import tempfile
import subprocess
from pathlib import Path

from ..config import Config
from ..llm.output_parsers import extract_first_json_object
from ..collectors import git_client


def _list_modified_files() -> list[str]:
    out = subprocess.check_output(["git", "diff", "--name-only"], stderr=subprocess.STDOUT)
    files = [l.strip() for l in out.decode("utf-8", errors="replace").splitlines() if l.strip()]
    return files


def _export_modified_files_to_artifacts(files: list[str], out_root: str = "artifacts/proposed_files"):
    out_dir = Path(out_root)
    out_dir.mkdir(parents=True, exist_ok=True)

    for fp in files:
        p = Path(fp)
        if not p.exists() or p.is_dir():
            continue

        dest = out_dir / fp.replace("\\", "/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(p.read_bytes())


def _git_apply(diff_text: str):
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".patch", encoding="utf-8") as f:
        f.write(diff_text)
        patch_path = f.name
    try:
        subprocess.check_call(["git", "apply", "--whitespace=fix", patch_path])
    finally:
        Path(patch_path).unlink(missing_ok=True)


def _rollback():
    subprocess.check_call(["git", "reset", "--hard", "HEAD"])
    subprocess.check_call(["git", "clean", "-fd"])


def apply_output_files_mode(cfg: Config, generated_tasks: list[dict], logger):
    """
    OUTPUT_MODE=FILES:
    - n'applique pas au repo
    - écrit les fichiers proposés dans artifacts/proposed_files/...
    """
    out_dir = Path("artifacts/proposed_files")
    out_dir.mkdir(parents=True, exist_ok=True)

    applied = []
    failed = []

    for t in generated_tasks:
        try:
            obj = extract_first_json_object(t["patch_output"])
            for f in obj.get("files", []):
                path = f["path"].replace("\\", "/")
                content = f["content"]
                dest = out_dir / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")
            applied.append({"task_id": t["id"], "file": t["file_path"], "mode": "FILES"})
        except Exception as e:
            failed.append({"task_id": t["id"], "file": t["file_path"], "reason": str(e)})

    return applied, failed


def apply_output_branch_mode(cfg: Config, generated_tasks: list[dict], logger):
    """
    OUTPUT_MODE=BRANCH:
    - crée/checkout une branche bot-review/...
    - applique les diffs
    - exporte aussi les fichiers modifiés dans artifacts/proposed_files (pour avoir les 2 formats)
    - commit + push
    """
    applied = []
    failed = []

    branch = cfg.output_branch
    try:
        git_client.create_branch(branch)
    except Exception:
        git_client.checkout(branch)

    # Apply patches
    for t in generated_tasks:
        try:
            _git_apply(t["patch_output"])
            applied.append({"task_id": t["id"], "file": t["file_path"], "mode": "BRANCH"})
        except Exception as e:
            _rollback()
            failed.append({"task_id": t["id"], "file": t["file_path"], "reason": f"apply_failed: {e}"})

    # ✅ Export ALSO as FILES (proposed_files) if anything applied
    if applied:
        try:
            modified = _list_modified_files()
            _export_modified_files_to_artifacts(modified)
            logger.info(f"Exported {len(modified)} modified files to artifacts/proposed_files")
        except Exception as e:
            failed.append({"task_id": "EXPORT_FILES", "file": "-", "reason": str(e)})

        # Commit + push
        try:
            git_client.add_all()
            git_client.commit("bot: sonar safe refactor (enterprise)")
            git_client.push(branch)
        except Exception as e:
            failed.append({"task_id": "COMMIT_PUSH", "file": "-", "reason": str(e)})

    return applied, failed

import json
import os
from pathlib import Path
import tempfile
import subprocess

from ..config import Config
from ..llm.output_parsers import extract_first_json_object
from ..exceptions import PatchError
from ..collectors import git_client

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
    applied = []
    failed = []

    # Create branch
    branch = cfg.output_branch
    try:
        git_client.create_branch(branch)
    except Exception:
        # If branch exists, checkout
        git_client.checkout(branch)

    for t in generated_tasks:
        try:
            _git_apply(t["patch_output"])
            applied.append({"task_id": t["id"], "file": t["file_path"], "mode": "BRANCH"})
        except Exception as e:
            _rollback()
            failed.append({"task_id": t["id"], "file": t["file_path"], "reason": f"apply_failed: {e}"})

    # Commit + push if at least 1 applied
    if applied:
        try:
            git_client.add_all()
            git_client.commit("bot: sonar safe refactor (enterprise v1)")
            git_client.push(branch)
        except Exception as e:
            failed.append({"task_id": "COMMIT_PUSH", "file": "-", "reason": str(e)})

    return applied, failed

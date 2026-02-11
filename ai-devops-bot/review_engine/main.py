from __future__ import annotations
import os, json
from pathlib import Path

from .config import Config
from .artifacts import run_id, ensure_dir, write_json, write_text, copy_files
from .utils import run_cmd, read_text
from .sonar_client import SonarClient, compact_issue
from .policy_internal import scan_internal
from .policy_strict import strict_checks
from .coherence import detect_coherence
from .prompting import build_fix_messages, attach_snippets
from .llm_client import call_llm
from .llm_parsing import parse_fix_response
from .patcher import apply_patch, apply_files_fallback
from .git_ops import changed_files, checkout_branch, commit_all, push
from .report_writer import build_report


def severity_rank(sev: str) -> int:
    order = {"BLOCKER": 0, "CRITICAL": 1, "MAJOR": 2, "MINOR": 3, "INFO": 4}
    return order.get((sev or "INFO").upper(), 9)

def select_sonar_batch(issues: list[dict], stage: int, max_n: int) -> list[dict]:
    # stage1: BLOCKER/CRITICAL ; stage2: MAJOR ; stage3: MINOR
    if stage == 1:
        scope = [i for i in issues if i.get("severity") in {"BLOCKER","CRITICAL"}]
    elif stage == 2:
        scope = [i for i in issues if i.get("severity") == "MAJOR"]
    else:
        scope = [i for i in issues if i.get("severity") == "MINOR"]

    # simple stable sort
    scope.sort(key=lambda x: (severity_rank(x.get("severity","INFO")), x.get("type",""), x.get("file",""), int(x.get("line") or 0)))
    return scope[:max_n]

def parse_compile_errors(output: str) -> list[dict]:
    # very simple, effective enough
    import re
    rx = re.compile(r"\[ERROR\]\s+(.+\.java):\[(\d+),(\d+)\]\s+(.*)")
    out = []
    for line in output.splitlines():
        m = rx.search(line)
        if m:
            out.append({
                "source": "compile",
                "severity": "BLOCKER",
                "type": "COMPILE",
                "rule": "JAVA_COMPILE_ERROR",
                "file": m.group(1).replace("\\","/"),
                "line": int(m.group(2)),
                "message": m.group(4)[:260],
            })
    return out

def build_payload(kind: str, batch: list[dict], cfg: Config) -> dict:
    # kind: "sonar" or "quality"
    return {
        "kind": kind,
        "constraints": {
            "max_batch": len(batch),
            "must_return_json_patch": True
        },
        "strict_policies": read_text(cfg.strict_policies_path, ""),
        "batch": attach_snippets(batch, max_lines=25, max_chars=1400),
    }

def run_fix_iteration(cfg: Config, system_prompt_path: str, batch: list[dict], iter_dir: Path) -> dict:
    payload = build_payload("fix", batch, cfg)
    msgs = build_fix_messages(system_prompt_path, payload, cfg.max_prompt_chars)
    write_json(iter_dir / "prompt_messages.json", msgs)
    write_text(iter_dir / "prompt_user.json", msgs[1]["content"])

    llm_text = call_llm(cfg, msgs)
    write_text(iter_dir / "llm_response.txt", llm_text)

    parsed = parse_fix_response(llm_text)
    write_json(iter_dir / "llm_parsed.json", parsed)

    ok, how_or_err = apply_patch(parsed.get("patch",""), str(iter_dir))
    if not ok:
        fb_ok = apply_files_fallback(parsed.get("files"))
        write_json(iter_dir / "apply_result.json", {"applied": fb_ok, "method": "files_fallback" if fb_ok else "failed", "error": how_or_err})
    else:
        write_json(iter_dir / "apply_result.json", {"applied": True, "method": how_or_err})

    ch = changed_files()
    write_json(iter_dir / "changed_files.json", ch)
    copy_files(ch, iter_dir / "changed_files")

    return {"parsed": parsed, "changed_files": ch}

def refresh_sonar_if_enabled(cfg: Config, out_dir: Path) -> None:
    if not cfg.sonar_refresh_enabled:
        return
    code, out = run_cmd(cfg.sonar_refresh_cmd, timeout=3600)
    write_text(out_dir / "sonar_refresh.log", out)
    write_json(out_dir / "sonar_refresh_result.json", {"code": code})

def main() -> int:
    cfg = Config()
    repo_root = os.getcwd()

    rid = run_id()
    base = ensure_dir(Path(cfg.artifacts_root) / rid)

    # init clients
    sonar = SonarClient(cfg.sonar_host_url, cfg.sonar_token)

    # initial compile
    c0, c0_out = run_cmd(cfg.mvn_compile_cmd, timeout=2400)
    write_text(base / "compile_before.log", c0_out)
    compile_issues = parse_compile_errors(c0_out)

    system_fix = cfg.system_fix_prompt_path

    sonar_md_lines = []
    tests_md_lines = []
    progress_guard = set()

    stages = [1, 2] + ([3] if cfg.fix_minor else [])
    for stage in stages:
        for it in range(1, cfg.max_iterations + 1):
            iter_dir = ensure_dir(base / f"sonar_stage{stage}_iter{it:02d}")

            # fetch sonar issues (API)
            raw = sonar.issues_all(cfg.sonar_project_key)
            write_json(iter_dir / "sonar_raw.json", raw)

            sonar_issues = [compact_issue(x) for x in (raw.get("issues") or [])]

            # Stage scope
            batch_sonar = select_sonar_batch(sonar_issues, stage, cfg.max_batch_size)

            # include compile issues only in stage 1
            if stage == 1:
                batch = (compile_issues + batch_sonar)[:cfg.max_batch_size]
            else:
                batch = batch_sonar[:cfg.max_batch_size]

            write_json(iter_dir / "selected_batch.json", batch)

            if not batch:
                sonar_md_lines.append(f"- Stage {stage} Iter {it}: no issues left.\n")
                break

            sig = (stage, tuple((b.get("rule"), b.get("file"), b.get("line")) for b in batch))
            if sig in progress_guard:
                sonar_md_lines.append(f"- Stage {stage} Iter {it}: STOP (repeated batch / no progress)\n")
                break
            progress_guard.add(sig)

            # LLM fix
            res = run_fix_iteration(cfg, system_fix, batch, Path(iter_dir))
            parsed = res["parsed"]
            ch = res["changed_files"]

            # compile + tests
            c1, c1_out = run_cmd(cfg.mvn_compile_cmd, timeout=2400)
            write_text(Path(iter_dir) / "compile_after.log", c1_out)
            compile_issues = parse_compile_errors(c1_out)

            t1, t1_out = run_cmd(cfg.mvn_test_cmd, timeout=3600)
            write_text(Path(iter_dir) / "tests.log", t1_out)

            sonar_md_lines.append(f"- Stage {stage} Iter {it}: changed={len(ch)}, compile={'OK' if c1==0 else 'FAIL'}, tests={'OK' if t1==0 else 'FAIL'}\n")

            # optional sonar refresh so API updates
            refresh_sonar_if_enabled(cfg, Path(iter_dir))

            # stop if tests fail (simple)
            if t1 != 0:
                tests_md_lines.append(f"- Tests failed at stage {stage} iter {it}\n")
                break

            # stage completion checks
            if stage == 1:
                if not compile_issues and not any(i.get("severity") in {"BLOCKER","CRITICAL"} for i in sonar_issues):
                    break
            elif stage == 2:
                if not any(i.get("severity") == "MAJOR" for i in sonar_issues):
                    break
            else:
                if not any(i.get("severity") == "MINOR" for i in sonar_issues):
                    break

    # -------------------------
    # POST-PASS QUALITE (ONE SHOT) => corriger seulement 5 issues detectées
    # -------------------------
    quality_dir = ensure_dir(base / "quality_postpass")

    # detect from current repo state
    internal = scan_internal(repo_root, cfg.internal_rules_path)
    write_json(quality_dir / "internal_detected.json", [i.__dict__ for i in internal])

    # use last changes list as a proxy for coherence detection scope
    ch_now = changed_files()
    coherence = detect_coherence(repo_root, ch_now)
    write_json(quality_dir / "coherence_detected.json", [i.__dict__ for i in coherence])

    # strict checks need the last patch (best effort) — if not available, scan only based on changed_files
    # Here we just pass empty patch (still does logic/tests and controller/repo checks)
    strict = strict_checks(repo_root, ch_now, patch_text="")
    write_json(quality_dir / "strict_detected.json", [i.__dict__ for i in strict])

    # Build quality issues list (NO PRIORITY), take only 5
    quality_all: list[dict] = []
    for i in internal:
        quality_all.append({
            "source": i.source, "severity": i.severity, "type": i.type, "rule": i.rule,
            "file": i.file, "line": i.line, "message": i.message, "hint": i.hint
        })
    for i in coherence:
        quality_all.append({
            "source": i.source, "severity": i.severity, "type": i.type, "rule": i.rule,
            "file": i.file, "line": i.line, "message": i.message, "hint": i.hint
        })
    for i in strict:
        quality_all.append({
            "source": i.source, "severity": i.severity, "type": i.type, "rule": i.rule,
            "file": i.file, "line": i.line, "message": i.message, "hint": i.hint
        })

    selected_quality = quality_all[:cfg.quality_max_issues]  # <= 5, sans priorité
    write_json(quality_dir / "selected_quality.json", selected_quality)

    quality_md = ""
    if selected_quality:
        resq = run_fix_iteration(cfg, system_fix, selected_quality, Path(quality_dir))
        # re-test
        c2, c2_out = run_cmd(cfg.mvn_compile_cmd, timeout=2400)
        write_text(Path(quality_dir) / "compile_after.log", c2_out)
        t2, t2_out = run_cmd(cfg.mvn_test_cmd, timeout=3600)
        write_text(Path(quality_dir) / "tests.log", t2_out)
        quality_md = f"- Corrected {len(selected_quality)} quality issues (one-shot). compile={'OK' if c2==0 else 'FAIL'}, tests={'OK' if t2==0 else 'FAIL'}\n"
    else:
        quality_md = "- No quality issues detected.\n"

    # -------------------------
    # Create & push bot/fix branch
    # -------------------------
    push_md = ""
    if cfg.create_fix_branch:
        checkout_branch(cfg.fix_branch_name)
        commit_all("chore(ai): auto-fix by AI DevOps Bot")
        ok, out = push(cfg.fix_branch_name, cfg.push_remote_url if cfg.push_remote_url else None)
        push_md = "OK\n" if ok else "FAIL\n"
        write_text(base / "push_output.txt", out)
    else:
        push_md = "disabled"

    # final report
    report = build_report({
        "summary": "Auto-fix completed (Sonar stages + quality post-pass).",
        "sonar_md": "".join(sonar_md_lines) or "_n/a_",
        "quality_md": quality_md,
        "tests_md": "".join(tests_md_lines) or "See iteration logs.",
        "push_md": push_md,
    })
    write_text(base / "final_report.md", report)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

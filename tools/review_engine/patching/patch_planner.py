from ..config import Config
from ..collectors.coverage_client import guess_file_coverage

def make_patch_tasks(cfg: Config, context: dict, triage: dict, logger) -> dict:
    selected = triage.get("selected_files", [])[: cfg.max_files_to_patch]
    issues_by_file = context.get("issues_by_file", {})
    jacoco = context.get("coverage", {})

    tasks = []
    for fp in selected:
        cov = guess_file_coverage(fp, jacoco)
        cov_val = cov if cov is not None else -1.0

        tasks.append({
            "id": f"T{len(tasks)+1:03d}",
            "file_path": fp,
            "coverage_percent": cov_val,
            "issues": issues_by_file.get(fp, []),
            "status": "PENDING",
            "max_change_lines": cfg.max_changed_lines_per_file,
        })

    return {"mode": cfg.output_mode, "tasks": tasks}

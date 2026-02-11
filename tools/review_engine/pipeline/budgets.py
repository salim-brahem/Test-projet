from dataclasses import dataclass

@dataclass(frozen=True)
class Budgets:
    max_files: int = 10
    max_iterations: int = 2
    max_changed_lines_per_file: int = 200

    # Optional enterprise knobs
    max_total_changed_lines: int = 500
    max_tasks: int = 10

def from_config(cfg) -> Budgets:
    return Budgets(
        max_files=cfg.max_files_to_patch,
        max_iterations=cfg.max_patch_iterations,
        max_changed_lines_per_file=cfg.max_changed_lines_per_file,
    )

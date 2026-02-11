from pathlib import Path

ANNOTATIONS = {
    "controllers": ["@RestController", "@Controller"],
    "services": ["@Service"],
    "repositories": ["@Repository"],
    "entities": ["@Entity"],
    "advice": ["@ControllerAdvice", "@RestControllerAdvice"],
}

def _scan_java_files(root: str = "src/main/java") -> list[str]:
    base = Path(root)
    if not base.exists():
        return []
    return [str(p).replace("\\", "/") for p in base.rglob("*.java")]

def index_spring_repo() -> dict:
    files = _scan_java_files()
    idx = {k: [] for k in ANNOTATIONS.keys()}
    idx["dtos"] = []
    idx["all_java"] = files

    for fp in files:
        text = Path(fp).read_text(encoding="utf-8", errors="replace")
        for bucket, anns in ANNOTATIONS.items():
            if any(a in text for a in anns):
                idx[bucket].append(fp)

        # DTO heuristic
        name = Path(fp).name
        if name.lower().endswith("dto.java") or "Dto" in name or "DTO" in name:
            idx["dtos"].append(fp)

    return idx

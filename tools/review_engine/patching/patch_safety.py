import re

REST_ANNOTATIONS = [
    "@RequestMapping", "@GetMapping", "@PostMapping", "@PutMapping", "@DeleteMapping", "@PatchMapping"
]

def touches_pom(file_path: str) -> bool:
    return file_path.replace("\\", "/").endswith("pom.xml")

def diff_touches_rest_mapping(diff_text: str) -> bool:
    return any(a in diff_text for a in REST_ANNOTATIONS)

def diff_changes_public_signature(diff_text: str) -> bool:
    # Heuristic: if diff contains lines adding/removing "public " or "protected "
    added_public = re.search(r"^\+.*\b(public|protected)\b", diff_text, re.MULTILINE)
    removed_public = re.search(r"^\-.*\b(public|protected)\b", diff_text, re.MULTILINE)
    return bool(added_public or removed_public)

def diff_too_large(diff_text: str, max_changed_lines: int) -> bool:
    added = sum(1 for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff_text.splitlines() if l.startswith("-") and not l.startswith("---"))
    return (added + removed) > max_changed_lines

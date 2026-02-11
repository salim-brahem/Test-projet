from pathlib import Path
import xml.etree.ElementTree as ET

def parse_jacoco(xml_path: str) -> dict:
    p = Path(xml_path)
    if not p.exists():
        return {"overall": None, "by_sourcefile": {}}

    root = ET.parse(p).getroot()

    overall = None
    for c in root.findall("counter"):
        if c.attrib.get("type") == "LINE":
            missed = int(c.attrib.get("missed", "0"))
            covered = int(c.attrib.get("covered", "0"))
            total = missed + covered
            overall = (covered / total * 100.0) if total else None
            break

    by_sourcefile = {}
    for pkg in root.findall("package"):
        pkg_name = pkg.attrib.get("name", "")
        for sf in pkg.findall("sourcefile"):
            name = sf.attrib.get("name", "")
            key = f"{pkg_name}/{name}" if pkg_name else name
            cov = None
            for c in sf.findall("counter"):
                if c.attrib.get("type") == "LINE":
                    missed = int(c.attrib.get("missed", "0"))
                    covered = int(c.attrib.get("covered", "0"))
                    total = missed + covered
                    cov = (covered / total * 100.0) if total else None
                    break
            by_sourcefile[key] = cov

    return {"overall": overall, "by_sourcefile": by_sourcefile}

def guess_file_coverage(java_path: str, jacoco: dict) -> float | None:
    name = Path(java_path).name
    for k, v in jacoco.get("by_sourcefile", {}).items():
        if k.endswith("/" + name) or k.endswith(name):
            return v
    return None

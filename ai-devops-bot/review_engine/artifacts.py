from __future__ import annotations
from pathlib import Path
import json, time, shutil
from typing import Any

def run_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S", time.gmtime())

def ensure_dir(p: str | Path) -> Path:
    pp = Path(p)
    pp.mkdir(parents=True, exist_ok=True)
    return pp

def write_text(path: str | Path, content: str) -> None:
    p = Path(path)
    ensure_dir(p.parent)
    p.write_text(content, encoding="utf-8")

def write_json(path: str | Path, obj: Any) -> None:
    p = Path(path)
    ensure_dir(p.parent)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def copy_files(rel_paths: list[str], dest_root: str | Path) -> None:
    dest = ensure_dir(dest_root)
    for rel in rel_paths:
        src = Path(rel)
        if not src.exists() or src.is_dir():
            continue
        tgt = dest / rel
        ensure_dir(tgt.parent)
        shutil.copy2(src, tgt)

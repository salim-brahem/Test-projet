from __future__ import annotations
import subprocess
from pathlib import Path

def run_cmd(cmd: str, timeout: int | None = None) -> tuple[int, str]:
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
        return 124, (out or "") + "\nTIMEOUT"
    return p.returncode, out or ""

def read_text(path: str, default: str = "") -> str:
    p = Path(path)
    if not p.exists():
        return default
    return p.read_text(encoding="utf-8", errors="replace")

def clamp(s: str, max_chars: int) -> str:
    return s if len(s) <= max_chars else s[:max_chars-1] + "…"

def extract_snippet(file_path: str, line: int | None, max_lines: int = 25, max_chars: int = 1400) -> str:
    p = Path(file_path)
    if not p.exists() or p.is_dir():
        return ""
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return ""
    if not line or line <= 0:
        start, end = 1, min(len(lines), max_lines)
    else:
        half = max_lines // 2
        start = max(1, line - half)
        end = min(len(lines), start + max_lines - 1)
    buf = [f"{i:>4}: {lines[i-1]}" for i in range(start, end+1)]
    s = "\n".join(buf)
    return s if len(s) <= max_chars else s[:max_chars-1] + "…"

import os
from pathlib import Path
import subprocess
from ..exceptions import GuardError

def ensure_file_exists(path: str, label: str):
    if not Path(path).exists():
        raise GuardError(f"Missing required file: {label} ({path})")

def ensure_sonar_env():
    required = ["SONAR_HOST_URL", "SONAR_TOKEN", "SONAR_PROJECT_KEY"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise GuardError(f"Missing env vars: {', '.join(missing)}")

def ensure_git_repo_cleanish():
    # In CI, workspace is usually clean. We'll just ensure git exists and repo initialized.
    try:
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        raise GuardError("Not a git repository (git rev-parse failed).")

def ensure_ollama_available():
    try:
        subprocess.check_output(["ollama", "--version"], stderr=subprocess.STDOUT)
    except Exception:
        raise GuardError("Ollama not available. Install ollama and ensure 'ollama' is in PATH.")

def run_guards(jacoco_xml_path: str):
    ensure_sonar_env()
    ensure_git_repo_cleanish()
    ensure_ollama_available()
    ensure_file_exists(jacoco_xml_path, "JaCoCo XML coverage report")

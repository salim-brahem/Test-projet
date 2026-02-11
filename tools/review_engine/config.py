import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    sonar_host_url: str
    sonar_token: str
    sonar_project_key: str
    sonar_branch: str | None

    git_base_ref: str

    ollama_model: str

    output_mode: str  # FILES | BRANCH
    output_branch: str

    max_files_to_patch: int
    max_patch_iterations: int
    max_changed_lines_per_file: int

    jacoco_xml_path: str

def load_config() -> Config:
    output_mode = os.environ.get("OUTPUT_MODE", "FILES").upper().strip()
    if output_mode not in ("FILES", "BRANCH"):
        output_mode = "FILES"

    return Config(
        sonar_host_url=os.environ["SONAR_HOST_URL"].rstrip("/"),
        sonar_token=os.environ["SONAR_TOKEN"],
        sonar_project_key=os.environ["SONAR_PROJECT_KEY"],
        sonar_branch=os.environ.get("SONAR_BRANCH"),

        git_base_ref=os.environ.get("GIT_BASE_REF", "origin/main"),

        ollama_model=os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b"),

        output_mode=output_mode,
        output_branch=os.environ.get("OUTPUT_BRANCH", "bot-review/v1"),

        max_files_to_patch=int(os.environ.get("MAX_FILES_TO_PATCH", "5")),
        max_patch_iterations=int(os.environ.get("MAX_PATCH_ITERATIONS", "2")),
        max_changed_lines_per_file=int(os.environ.get("MAX_CHANGED_LINES_PER_FILE", "120")),

        jacoco_xml_path=os.environ.get("JACOCO_XML_PATH", "target/site/jacoco/jacoco.xml"),
    )

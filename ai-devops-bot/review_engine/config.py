from __future__ import annotations
from dataclasses import dataclass
import os

def _env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    return v

def _env_bool(name: str, default: bool) -> bool:
    v = _env(name)
    if v is None:
        return default
    return v.strip().lower() in {"1","true","yes","y","on"}

def _env_int(name: str, default: int) -> int:
    v = _env(name)
    if v is None:
        return default
    try:
        return int(v)
    except ValueError:
        return default

@dataclass(frozen=True)
class Config:
    sonar_host_url: str = _env("SONAR_HOST_URL", "http://localhost:9000") or "http://localhost:9000"
    sonar_project_key: str = _env("SONAR_PROJECT_KEY", "nomDuProjet") or "nomDuProjet"
    sonar_token: str = _env("SONAR_TOKEN", "") or ""

    # optional: re-run sonar analysis after patch so API reflects fixes
    sonar_refresh_enabled: bool = _env_bool("SONAR_REFRESH_ENABLED", False)
    sonar_refresh_cmd: str = _env("SONAR_REFRESH_CMD", "mvn -B -ntp -DskipTests sonar:sonar") or "mvn -B -ntp -DskipTests sonar:sonar"

    # Maven
    mvn_compile_cmd: str = _env("MAVEN_COMPILE_CMD", "mvn -B -ntp -DskipTests compile") or "mvn -B -ntp -DskipTests compile"
    mvn_test_cmd: str = _env("MAVEN_TEST_CMD", "mvn -B -ntp test") or "mvn -B -ntp test"

    # loops
    max_batch_size: int = _env_int("MAX_BATCH_SIZE", 15)
    max_iterations: int = _env_int("MAX_ITERATIONS", 10)
    fix_minor: bool = _env_bool("FIX_MINOR", False)

    # post-pass quality
    quality_max_issues: int = _env_int("QUALITY_MAX_ISSUES", 5)

    # artifacts
    artifacts_root: str = _env("ARTIFACTS_ROOT", "artifacts/ai-devops") or "artifacts/ai-devops"

    # policies paths
    internal_rules_path: str = _env("INTERNAL_RULES_PATH", "policies/internal_rules.yml") or "policies/internal_rules.yml"
    strict_policies_path: str = _env("STRICT_POLICIES_PATH", "policies/strict_policies.yml") or "policies/strict_policies.yml"
    system_fix_prompt_path: str = _env("SYSTEM_FIX_PROMPT_PATH", "policies/prompt_system_fix.md") or "policies/prompt_system_fix.md"

    # LLM
    llm_provider: str = _env("LLM_PROVIDER", "openai_compatible") or "openai_compatible"
    llm_base_url: str = _env("LLM_BASE_URL", "") or ""
    llm_api_key: str = _env("LLM_API_KEY", "dummy") or "dummy"
    llm_model: str = _env("LLM_MODEL", "qwen2-coder-7b") or "qwen2-coder-7b"
    ollama_base_url: str = _env("OLLAMA_BASE_URL", "") or ""
    ollama_model: str = _env("OLLAMA_MODEL", "qwen2.5-coder:7b") or "qwen2.5-coder:7b"
    llm_temperature: float = float(_env("LLM_TEMPERATURE", "0.2") or "0.2")
    llm_max_tokens: int = _env_int("LLM_MAX_TOKENS", 2200)
    llm_timeout_sec: int = _env_int("LLM_TIMEOUT_SEC", 180)
    max_prompt_chars: int = _env_int("MAX_PROMPT_CHARS", 32000)

    # Git push
    create_fix_branch: bool = _env_bool("CREATE_FIX_BRANCH", True)
    fix_branch_name: str = _env("FIX_BRANCH_NAME", "bot/fix") or "bot/fix"
    push_remote_url: str = _env("PUSH_REMOTE_URL", "") or ""

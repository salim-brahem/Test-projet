from ..config import Config
from .sonar_client import SonarClient
from .git_client import changed_files, diff_text
from .coverage_client import parse_jacoco
from .repo_indexer import index_spring_repo
from .policy_loader import load_policy

def _group_issues_by_file(issues_json: dict) -> dict:
    out = {}
    for it in issues_json.get("issues", []):
        comp = it.get("component", "")
        if ":" in comp:
            _, path = comp.split(":", 1)
        else:
            path = comp
        out.setdefault(path, []).append(it)
    return out

def build_context(cfg: Config, logger) -> dict:
    sonar = SonarClient(cfg.sonar_host_url, cfg.sonar_token)

    qg = sonar.quality_gate(cfg.sonar_project_key, cfg.sonar_branch)
    measures = sonar.measures(
        cfg.sonar_project_key,
        cfg.sonar_branch,
        metric_keys=[
            "ncloc","complexity","cognitive_complexity","duplicated_lines_density",
            "code_smells","bugs","vulnerabilities","security_hotspots","coverage"
        ],
    )
    top_issues = sonar.issues(
        cfg.sonar_project_key,
        cfg.sonar_branch,
        severities=["BLOCKER","CRITICAL","MAJOR"],
        types=["BUG","VULNERABILITY","CODE_SMELL","SECURITY_HOTSPOT"],
        ps=300,
    )

    issues_by_file = _group_issues_by_file(top_issues)

    git = {
        "base_ref": cfg.git_base_ref,
        "changed_files": changed_files(cfg.git_base_ref),
        "diff": diff_text(cfg.git_base_ref),
    }

    coverage = parse_jacoco(cfg.jacoco_xml_path)
    repo_index = index_spring_repo()
    policy = load_policy("review-policy.yml")

    logger.info(f"Sonar issues fetched: {len(top_issues.get('issues', []))}")
    logger.info(f"Git changed files: {len(git['changed_files'])}")
    logger.info(f"Coverage overall: {coverage.get('overall')}")

    return {
        "project": {"key": cfg.sonar_project_key, "branch": cfg.sonar_branch},
        "quality_gate": qg,
        "metrics": measures,
        "issues": top_issues.get("issues", []),
        "issues_by_file": issues_by_file,
        "git": git,
        "coverage": coverage,
        "repo_index": repo_index,
        "policy": policy,
        "spring_assumptions": {
            "layering": "Controller -> Service -> Repository",
            "dto_boundary": "DTO at REST boundary, avoid exposing entities",
            "error_handling": "Prefer @ControllerAdvice or ResponseStatusException"
        }
    }

from .spring_analyzer import analyze_spring
from .rest_contract_checker import check_rest_contract
from .jpa_analyzer import analyze_jpa
from .exception_flow_analyzer import analyze_exception_flow

def run_risk_engine(context: dict) -> list[dict]:
    findings = []
    findings.extend(analyze_spring(context))
    findings.extend(check_rest_contract(context))
    findings.extend(analyze_jpa(context))
    findings.extend(analyze_exception_flow(context))
    return _dedupe(findings)

def _dedupe(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for it in items:
        k = (it.get("priority"), it.get("topic"), it.get("file"), it.get("message"))
        if k in seen:
            continue
        seen.add(k)
        out.append(it)
    return out

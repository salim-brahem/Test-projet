import json
from ..config import Config
from ..llm.llm_client import ollama_generate
from ..llm.prompt_router import load_prompt, render
from ..llm.output_parsers import extract_first_json_object

def run_triage(cfg: Config, context: dict, logger) -> dict:
    policy = load_prompt("policy.txt")
    tmpl = load_prompt("sonar_triage.txt")
    prompt = render(
        tmpl,
        {
            "policy": policy,
            "max_files": cfg.max_files_to_patch,
            "context_json": json.dumps(context, indent=2),
        },
    )
    out = ollama_generate(cfg.ollama_model, prompt)
    triage = extract_first_json_object(out)

    # Basic normalization
    if "selected_files" not in triage:
        triage["selected_files"] = []
    triage["selected_files"] = triage["selected_files"][: cfg.max_files_to_patch]
    return triage

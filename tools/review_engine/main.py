import uuid
from .config import load_config
from .logging_setup import setup_logging
from .pipeline.pipeline_runner import run_pipeline

def main():
    cfg = load_config()
    correlation_id = str(uuid.uuid4())[:8]
    logger = setup_logging(correlation_id, "artifacts")
    run_pipeline(cfg, logger)

if __name__ == "__main__":
    main()

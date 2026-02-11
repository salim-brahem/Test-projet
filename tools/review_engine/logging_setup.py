import json
import logging
import os
import sys
from datetime import datetime

def setup_logging(correlation_id: str, out_dir: str) -> logging.Logger:
    os.makedirs(out_dir, exist_ok=True)
    log_path = os.path.join(out_dir, "agent.log")

    logger = logging.getLogger("review_engine")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            payload = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "correlation_id": correlation_id,
                "msg": record.getMessage(),
                "logger": record.name,
            }
            return json.dumps(payload, ensure_ascii=False)

    fmt = JsonFormatter()

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)

    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger

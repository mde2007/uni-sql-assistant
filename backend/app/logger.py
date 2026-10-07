import json
import logging
import os
from datetime import datetime, timezone

LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("assistant")
logger.setLevel(logging.INFO)
if not logger.handlers:  # защита от дублей при повторном импорте/reload
    logger.addHandler(logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8"))
    logger.addHandler(logging.StreamHandler())


def log_event(event, **data):
    """Одна строка JSON на событие. Название и сигнатуру не менять."""
    record = {"time": datetime.now(timezone.utc).isoformat(), "event": event}
    record.update(data)
    logger.info(json.dumps(record, ensure_ascii=False, default=str))

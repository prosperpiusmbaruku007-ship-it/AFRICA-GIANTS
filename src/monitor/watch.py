import json
import os
from datetime import datetime, timezone
from typing import Dict

from src.common.storage import get_project_root


def metrics_path() -> str:
    root = get_project_root()
    path = os.path.join(root, "logs", "metrics.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def record_metric(event_type: str, payload: Dict) -> dict:
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **payload,
    }
    with open(metrics_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_metrics(limit: int = 50) -> list:
    path = metrics_path()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    return rows[-limit:]


import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional

from src.common.storage import get_project_root


def feedback_path() -> str:
    root = get_project_root()
    path = os.path.join(root, "data", "feedback", "feedback.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def save_feedback(
    question: str,
    answer: str,
    rating: Optional[int] = None,
    correction: str = "",
    model_name: str = "",
    metadata: Optional[Dict] = None,
) -> dict:
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "answer": answer,
        "rating": rating,
        "correction": correction,
        "model_name": model_name,
        "metadata": metadata or {},
    }
    with open(feedback_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


"""
Model registry — tracks every trained model version with eval scores,
dataset version, and deployment status. Enables promotion and rollback.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

from src.common.logging import get_logger
from src.common.storage import get_project_root

logger = get_logger("registry")

REGISTRY_PATH = os.path.join(get_project_root(), "models", "registry.json")


def _load() -> dict:
    if not os.path.exists(REGISTRY_PATH):
        return {"current": None, "models": []}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def register_model(
    model_id: str,
    base_model: str,
    training_method: str,
    dataset_version: str,
    hf_repo: str,
    eval_scores: Dict[str, float],
    passed_gate: bool,
) -> dict:
    """Register a newly trained model. Returns the model record."""
    data = _load()
    record = {
        "model_id": model_id,
        "base_model": base_model,
        "training_method": training_method,
        "dataset_version": dataset_version,
        "hf_repo": hf_repo,
        "accuracy_score": eval_scores.get("accuracy_score", 0.0),
        "hallucination_rate": eval_scores.get("hallucination_rate", 1.0),
        "p95_latency_ms": eval_scores.get("p95_latency_ms", 9999.0),
        "passed_gate": passed_gate,
        "status": "candidate",
        "created_at": datetime.utcnow().isoformat(),
        "deployed_at": None,
    }
    data["models"].append(record)
    _save(data)
    logger.info("Registered model %s (passed_gate=%s)", model_id, passed_gate)
    return record


def promote_model(model_id: str) -> bool:
    """Mark a model as the current production model. Returns True on success."""
    data = _load()
    found = False
    for record in data["models"]:
        if record["model_id"] == model_id:
            if not record.get("passed_gate"):
                logger.error("Cannot promote %s — eval gate not passed", model_id)
                return False
            record["status"] = "production"
            record["deployed_at"] = datetime.utcnow().isoformat()
            found = True
        elif record.get("status") == "production":
            record["status"] = "archived"

    if not found:
        logger.error("Model %s not found in registry", model_id)
        return False

    data["current"] = model_id
    _save(data)
    logger.info("Promoted %s to production", model_id)
    return True


def rollback(steps: int = 1) -> Optional[str]:
    """Revert to a previous production model. Returns the restored model_id or None."""
    data = _load()
    production_history = [
        r for r in data["models"] if r.get("status") in ("production", "archived")
    ]
    production_history.sort(key=lambda r: r.get("deployed_at") or "", reverse=True)

    if len(production_history) <= steps:
        logger.error("Not enough history to roll back %d step(s)", steps)
        return None

    target = production_history[steps]
    return promote_model(target["model_id"])


def get_current() -> Optional[dict]:
    """Return the current production model record, or None."""
    data = _load()
    current_id = data.get("current")
    if not current_id:
        return None
    for record in data["models"]:
        if record["model_id"] == current_id:
            return record
    return None


def list_models(status_filter: Optional[str] = None) -> List[dict]:
    """Return all registered models, optionally filtered by status."""
    data = _load()
    models = data.get("models", [])
    if status_filter:
        models = [m for m in models if m.get("status") == status_filter]
    return models


def get_model(model_id: str) -> Optional[dict]:
    """Return a specific model record by ID."""
    for record in list_models():
        if record["model_id"] == model_id:
            return record
    return None


if __name__ == "__main__":
    print(json.dumps({"current": get_current(), "all": list_models()}, indent=2))

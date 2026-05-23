"""
Evaluation gate — runs benchmarks and enforces promotion thresholds.
On pass, registers the model in the model registry.
"""
import json

from src.common.logging import get_logger
from src.common.storage import load_yaml_config
from src.evaluate.run_benchmarks import run_benchmarks

logger = get_logger("evaluate.gate")


def evaluate_gate(
    model_name: str = "",
    dataset_version: str = "unknown",
    hf_repo: str = "",
    base_model: str = "",
    training_method: str = "qlora",
    auto_register: bool = True,
) -> bool:
    """
    Run all benchmarks and check against promotion thresholds.

    If auto_register=True and model_name is given, the result is recorded
    in the model registry regardless of pass/fail, so every run is tracked.
    """
    config = load_yaml_config("eval")
    thresholds = config.get("evaluation", {}).get("thresholds", {})
    metrics = run_benchmarks(model_name=model_name)

    passed = (
        metrics["total"] > 0
        and metrics["accuracy_score"] >= thresholds.get("min_accuracy_score", 0.75)
        and metrics["hallucination_rate"] <= thresholds.get("max_hallucination_rate", 0.10)
        and metrics["p95_latency_ms"] <= thresholds.get("max_p95_latency_ms", 1500.0)
    )

    logger.info("Evaluation gate passed=%s metrics=%s", passed, metrics)

    if auto_register and model_name:
        try:
            from src.registry.model_registry import register_model, promote_model
            record = register_model(
                model_id=model_name,
                base_model=base_model or "McGill-NLP/AfriqueLlama-8B",
                training_method=training_method,
                dataset_version=dataset_version,
                hf_repo=hf_repo or f"prospaprospa/{model_name}",
                eval_scores=metrics,
                passed_gate=passed,
            )
            logger.info("Registered model in registry: %s", record["model_id"])

            if passed:
                promote_model(model_name)
                logger.info("Promoted %s to production", model_name)
        except Exception as e:
            logger.error("Failed to register model in registry: %s", e)

    print(json.dumps({"passed": passed, "metrics": metrics}, indent=2))
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if evaluate_gate() else 1)

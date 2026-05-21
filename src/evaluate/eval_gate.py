import json

from src.common.logging import get_logger
from src.common.storage import load_yaml_config
from src.evaluate.run_benchmarks import run_benchmarks

logger = get_logger("evaluate.gate")


def evaluate_gate(model_name: str = "") -> bool:
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
    print(json.dumps({"passed": passed, "metrics": metrics}, indent=2))
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if evaluate_gate() else 1)


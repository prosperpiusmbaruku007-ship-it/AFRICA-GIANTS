import json
import os
import time
from typing import Dict, List

from src.common.logging import get_logger
from src.common.storage import get_project_root, load_yaml_config
from src.serve.inference import InferenceEngine

logger = get_logger("evaluate.benchmarks")


def load_benchmark_rows() -> List[dict]:
    root = get_project_root()
    config = load_yaml_config("eval")
    benchmark_paths = config.get("evaluation", {}).get("benchmarks", {})

    rows = []
    for name, rel_path in benchmark_paths.items():
        path = os.path.join(root, rel_path)
        if not os.path.exists(path):
            logger.warning("Benchmark file missing: %s", path)
            continue
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                row["benchmark"] = name
                rows.append(row)
    return rows


def _expected_answer(row: dict) -> str:
    return row.get("expected") or row.get("output") or row.get("answer") or ""


def _question(row: dict) -> str:
    return row.get("question") or row.get("instruction") or row.get("input") or ""


def _score_answer(answer: str, expected: str, keywords: List[str]) -> float:
    answer_lower = answer.lower()
    expected_tokens = {token for token in expected.lower().split() if len(token) > 3}
    keyword_hits = sum(1 for keyword in keywords if keyword.lower() in answer_lower)

    if keywords:
        return keyword_hits / len(keywords)
    if not expected_tokens:
        return 1.0 if answer.strip() else 0.0

    overlap = sum(1 for token in expected_tokens if token in answer_lower)
    return overlap / max(len(expected_tokens), 1)


def run_benchmarks(model_name: str = "") -> Dict[str, float]:
    rows = load_benchmark_rows()
    engine = InferenceEngine()
    if model_name:
        engine.reload_model(model_name)

    if not rows:
        return {
            "total": 0,
            "accuracy_score": 0.0,
            "hallucination_rate": 1.0,
            "p95_latency_ms": 0.0,
        }

    scores = []
    latencies = []
    hallucination_flags = []

    for row in rows:
        question = _question(row)
        expected = _expected_answer(row)
        keywords = row.get("keywords", [])
        start = time.perf_counter()
        answer = engine.generate(question, max_tokens=160)
        latency_ms = (time.perf_counter() - start) * 1000

        score = _score_answer(answer, expected, keywords)
        scores.append(score)
        latencies.append(latency_ms)

        forbidden = row.get("forbidden", [])
        answer_lower = answer.lower()
        safe_negations = ("cannot guarantee", "can't guarantee", "do not guarantee", "not guarantee")
        has_forbidden = False
        for term in forbidden:
            term_lower = term.lower()
            if term_lower in answer_lower and not any(negation in answer_lower for negation in safe_negations):
                has_forbidden = True
                break
        hallucination_flags.append(has_forbidden)

    latencies_sorted = sorted(latencies)
    p95_index = int(0.95 * (len(latencies_sorted) - 1))
    result = {
        "total": len(rows),
        "accuracy_score": round(sum(scores) / len(scores), 4),
        "hallucination_rate": round(sum(hallucination_flags) / len(hallucination_flags), 4),
        "p95_latency_ms": round(latencies_sorted[p95_index], 2),
    }
    logger.info("Benchmark result: %s", result)
    return result


if __name__ == "__main__":
    print(json.dumps(run_benchmarks(), indent=2))

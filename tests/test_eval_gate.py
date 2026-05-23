"""Tests for the evaluation gate logic."""
import pytest


def test_gate_passes_good_metrics(monkeypatch):
    from src.evaluate import eval_gate

    monkeypatch.setattr(
        "src.evaluate.eval_gate.run_benchmarks",
        lambda model_name="": {
            "total": 50,
            "accuracy_score": 0.82,
            "hallucination_rate": 0.06,
            "p95_latency_ms": 900.0,
        },
    )
    monkeypatch.setattr("src.evaluate.eval_gate.load_yaml_config", lambda _: {
        "evaluation": {"thresholds": {
            "min_accuracy_score": 0.75,
            "max_hallucination_rate": 0.10,
            "max_p95_latency_ms": 1500.0,
        }}
    })

    result = eval_gate.evaluate_gate(auto_register=False)
    assert result is True


def test_gate_fails_low_accuracy(monkeypatch):
    from src.evaluate import eval_gate

    monkeypatch.setattr(
        "src.evaluate.eval_gate.run_benchmarks",
        lambda model_name="": {
            "total": 50,
            "accuracy_score": 0.60,
            "hallucination_rate": 0.06,
            "p95_latency_ms": 900.0,
        },
    )
    monkeypatch.setattr("src.evaluate.eval_gate.load_yaml_config", lambda _: {
        "evaluation": {"thresholds": {
            "min_accuracy_score": 0.75,
            "max_hallucination_rate": 0.10,
            "max_p95_latency_ms": 1500.0,
        }}
    })

    result = eval_gate.evaluate_gate(auto_register=False)
    assert result is False


def test_gate_fails_high_hallucination(monkeypatch):
    from src.evaluate import eval_gate

    monkeypatch.setattr(
        "src.evaluate.eval_gate.run_benchmarks",
        lambda model_name="": {
            "total": 50,
            "accuracy_score": 0.80,
            "hallucination_rate": 0.25,
            "p95_latency_ms": 900.0,
        },
    )
    monkeypatch.setattr("src.evaluate.eval_gate.load_yaml_config", lambda _: {
        "evaluation": {"thresholds": {
            "min_accuracy_score": 0.75,
            "max_hallucination_rate": 0.10,
            "max_p95_latency_ms": 1500.0,
        }}
    })

    result = eval_gate.evaluate_gate(auto_register=False)
    assert result is False


def test_gate_fails_high_latency(monkeypatch):
    from src.evaluate import eval_gate

    monkeypatch.setattr(
        "src.evaluate.eval_gate.run_benchmarks",
        lambda model_name="": {
            "total": 50,
            "accuracy_score": 0.80,
            "hallucination_rate": 0.06,
            "p95_latency_ms": 3000.0,
        },
    )
    monkeypatch.setattr("src.evaluate.eval_gate.load_yaml_config", lambda _: {
        "evaluation": {"thresholds": {
            "min_accuracy_score": 0.75,
            "max_hallucination_rate": 0.10,
            "max_p95_latency_ms": 1500.0,
        }}
    })

    result = eval_gate.evaluate_gate(auto_register=False)
    assert result is False


def test_gate_fails_zero_benchmarks(monkeypatch):
    from src.evaluate import eval_gate

    monkeypatch.setattr(
        "src.evaluate.eval_gate.run_benchmarks",
        lambda model_name="": {
            "total": 0,
            "accuracy_score": 0.0,
            "hallucination_rate": 1.0,
            "p95_latency_ms": 0.0,
        },
    )
    monkeypatch.setattr("src.evaluate.eval_gate.load_yaml_config", lambda _: {
        "evaluation": {"thresholds": {}}
    })

    result = eval_gate.evaluate_gate(auto_register=False)
    assert result is False

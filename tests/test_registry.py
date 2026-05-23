"""Tests for model registry — versioning, promotion, and rollback."""
import os
import json
import tempfile
import pytest

import src.registry.model_registry as registry_module


@pytest.fixture(autouse=True)
def isolated_registry(tmp_path, monkeypatch):
    """Redirect registry file to a temp dir for each test."""
    tmp_registry = str(tmp_path / "registry.json")
    monkeypatch.setattr(registry_module, "REGISTRY_PATH", tmp_registry)
    yield tmp_registry


def test_register_model():
    record = registry_module.register_model(
        model_id="africa-giants-v1",
        base_model="McGill-NLP/AfriqueLlama-8B",
        training_method="qlora",
        dataset_version="2026-01",
        hf_repo="prospaprospa/africa-giants-adapter-v1",
        eval_scores={"accuracy_score": 0.80, "hallucination_rate": 0.05, "p95_latency_ms": 900.0},
        passed_gate=True,
    )
    assert record["model_id"] == "africa-giants-v1"
    assert record["passed_gate"] is True
    assert record["status"] == "candidate"


def test_promote_model():
    registry_module.register_model(
        model_id="africa-giants-v1",
        base_model="McGill-NLP/AfriqueLlama-8B",
        training_method="qlora",
        dataset_version="2026-01",
        hf_repo="prospaprospa/africa-giants-adapter-v1",
        eval_scores={"accuracy_score": 0.80, "hallucination_rate": 0.05, "p95_latency_ms": 900.0},
        passed_gate=True,
    )
    result = registry_module.promote_model("africa-giants-v1")
    assert result is True

    current = registry_module.get_current()
    assert current is not None
    assert current["model_id"] == "africa-giants-v1"
    assert current["status"] == "production"


def test_promote_fails_if_gate_not_passed():
    registry_module.register_model(
        model_id="africa-giants-bad",
        base_model="McGill-NLP/AfriqueLlama-8B",
        training_method="qlora",
        dataset_version="2026-01",
        hf_repo="prospaprospa/africa-giants-bad",
        eval_scores={"accuracy_score": 0.50, "hallucination_rate": 0.30, "p95_latency_ms": 3000.0},
        passed_gate=False,
    )
    result = registry_module.promote_model("africa-giants-bad")
    assert result is False


def test_list_models():
    registry_module.register_model(
        model_id="v1",
        base_model="base",
        training_method="qlora",
        dataset_version="2026-01",
        hf_repo="hf/v1",
        eval_scores={"accuracy_score": 0.8, "hallucination_rate": 0.05, "p95_latency_ms": 800.0},
        passed_gate=True,
    )
    registry_module.register_model(
        model_id="v2",
        base_model="base",
        training_method="qlora",
        dataset_version="2026-02",
        hf_repo="hf/v2",
        eval_scores={"accuracy_score": 0.85, "hallucination_rate": 0.04, "p95_latency_ms": 750.0},
        passed_gate=True,
    )
    models = registry_module.list_models()
    assert len(models) == 2


def test_get_current_none_when_empty():
    assert registry_module.get_current() is None


def test_rollback():
    registry_module.register_model(
        model_id="v1",
        base_model="base",
        training_method="qlora",
        dataset_version="2026-01",
        hf_repo="hf/v1",
        eval_scores={"accuracy_score": 0.8, "hallucination_rate": 0.05, "p95_latency_ms": 800.0},
        passed_gate=True,
    )
    registry_module.promote_model("v1")

    registry_module.register_model(
        model_id="v2",
        base_model="base",
        training_method="qlora",
        dataset_version="2026-02",
        hf_repo="hf/v2",
        eval_scores={"accuracy_score": 0.85, "hallucination_rate": 0.04, "p95_latency_ms": 750.0},
        passed_gate=True,
    )
    registry_module.promote_model("v2")

    assert registry_module.get_current()["model_id"] == "v2"
    registry_module.rollback(steps=1)
    assert registry_module.get_current()["model_id"] == "v1"

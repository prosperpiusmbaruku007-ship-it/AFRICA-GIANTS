"""Tests for Pydantic schemas and common utilities."""
from src.common.schemas import ScrapedDocument, CleanedDocument, QAPair, EvaluationResult
from src.common.utils import generate_doc_id, get_current_timestamp, clean_whitespace, estimate_token_count


def test_scraped_document_valid():
    doc = ScrapedDocument(
        url="https://tra.go.tz/",
        source_name="TRA",
        title="TRA Home",
        raw_content="Tax information for Tanzania businesses.",
        scraped_at="2026-01-01T00:00:00",
    )
    assert doc.url == "https://tra.go.tz/"
    assert doc.metadata == {}


def test_cleaned_document_valid():
    doc = CleanedDocument(
        doc_id="doc_001",
        source_name="BRELA",
        url="https://brela.go.tz/",
        cleaned_content="Business registration in Tanzania.",
        language="en",
        cleaned_at="2026-01-01T00:00:00",
    )
    assert doc.language == "en"


def test_qa_pair_defaults():
    pair = QAPair(
        instruction="Ninaanzaje biashara?",
        output="Sajili BRELA.",
    )
    assert pair.input == ""
    assert pair.category == "general"
    assert pair.source_doc_id is None


def test_evaluation_result():
    result = EvaluationResult(
        model_name="africa-giants-v1",
        dataset_version="2026-01",
        timestamp="2026-01-01T00:00:00",
        loss=0.5,
        accuracy_score=0.82,
        hallucination_rate=0.05,
        p95_latency_ms=800.0,
        passed_gate=True,
    )
    assert result.passed_gate is True


def test_generate_doc_id_deterministic():
    assert generate_doc_id("hello") == generate_doc_id("hello")


def test_generate_doc_id_unique():
    assert generate_doc_id("hello") != generate_doc_id("world")


def test_get_timestamp_format():
    ts = get_current_timestamp()
    assert "T" in ts


def test_clean_whitespace():
    assert clean_whitespace("  hello   world  ") == "hello world"


def test_estimate_token_count():
    n = estimate_token_count("Hello world this is a test")
    assert n > 0

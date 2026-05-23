"""Tests for data cleaning and deduplication pipeline."""
import pytest
from src.common.schemas import ScrapedDocument, CleanedDocument
from src.process.clean import clean_documents
from src.process.deduplicate import deduplicate_documents


def _make_scraped(url: str, content: str, source: str = "TRA") -> ScrapedDocument:
    return ScrapedDocument(
        url=url,
        source_name=source,
        title="Test Doc",
        raw_content=content,
        scraped_at="2026-01-01T00:00:00",
    )


def test_clean_removes_html():
    doc = _make_scraped("https://tra.go.tz/", "<p>Tax <b>registration</b> in Tanzania.</p>")
    cleaned = clean_documents([doc])
    assert "<p>" not in cleaned[0].cleaned_content
    assert "Tax" in cleaned[0].cleaned_content


def test_clean_detects_swahili():
    content = "Usajili wa biashara nchini Tanzania ni muhimu kwa kodi na leseni."
    doc = _make_scraped("https://brela.go.tz/", content)
    cleaned = clean_documents([doc])
    assert cleaned[0].language == "sw"


def test_clean_detects_english():
    content = "Business registration in Tanzania requires a TIN number and a valid license."
    doc = _make_scraped("https://tra.go.tz/", content)
    cleaned = clean_documents([doc])
    assert cleaned[0].language == "en"


def test_clean_skips_empty_content():
    doc = _make_scraped("https://tra.go.tz/", "   ")
    cleaned = clean_documents([doc])
    assert len(cleaned) == 0


def test_clean_normalizes_whitespace():
    doc = _make_scraped("https://tra.go.tz/", "Hello   world.\n\nNext  line.")
    cleaned = clean_documents([doc])
    assert "  " not in cleaned[0].cleaned_content


def test_deduplicate_removes_exact_duplicates():
    base = "Business registration in Tanzania requires TIN and license documents."
    docs = [
        CleanedDocument(doc_id=f"doc_{i}", source_name="TRA", url="https://tra.go.tz/",
                        cleaned_content=base, language="en", cleaned_at="2026-01-01T00:00:00")
        for i in range(3)
    ]
    unique = deduplicate_documents(docs)
    assert len(unique) == 1


def test_deduplicate_keeps_different_docs():
    docs = [
        CleanedDocument(doc_id="doc_1", source_name="TRA", url="https://tra.go.tz/",
                        cleaned_content="Tax registration in Tanzania.", language="en",
                        cleaned_at="2026-01-01T00:00:00"),
        CleanedDocument(doc_id="doc_2", source_name="BRELA", url="https://brela.go.tz/",
                        cleaned_content="Company incorporation requirements at BRELA.", language="en",
                        cleaned_at="2026-01-01T00:00:00"),
    ]
    unique = deduplicate_documents(docs)
    assert len(unique) == 2

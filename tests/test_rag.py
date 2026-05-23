"""Tests for RAG vector store retrieval (BM25 fallback — no FAISS required)."""
import os
import json
import tempfile
import pytest
from src.rag.vector_store import LocalVectorStore, chunk_text, tokenize


def test_tokenize_basic():
    tokens = tokenize("Business registration in Tanzania")
    assert "business" in tokens
    assert "tanzania" in tokens


def test_tokenize_swahili():
    tokens = tokenize("Usajili wa biashara nchini Tanzania")
    assert "usajili" in tokens
    assert "biashara" in tokens


def test_chunk_text_splits():
    text = " ".join([f"word{i}" for i in range(2000)])
    chunks = list(chunk_text(text, chunk_size=100, overlap=20))
    assert len(chunks) > 1
    # Each chunk should not exceed chunk_size words
    for chunk in chunks:
        assert len(chunk.split()) <= 100


def test_chunk_text_empty():
    assert list(chunk_text("")) == []


def test_local_vector_store_build_and_search(tmp_path):
    index_path = str(tmp_path / "test_index.jsonl")
    store = LocalVectorStore(index_path=index_path)

    documents = [
        {"text": "Business registration in Tanzania requires a TIN number from TRA.", "source_name": "TRA", "url": "https://tra.go.tz/", "title": "TRA"},
        {"text": "Usajili wa biashara Tanzania unahitaji TIN kutoka TRA.", "source_name": "TRA-SW", "url": "https://tra.go.tz/sw/", "title": "TRA Swahili"},
        {"text": "BRELA handles company incorporation and business name registration.", "source_name": "BRELA", "url": "https://brela.go.tz/", "title": "BRELA"},
    ]
    count = store.build_from_documents(documents)
    assert count >= 3

    results = store.search("TIN number TRA", top_k=2)
    assert len(results) > 0
    assert results[0]["score"] > 0
    assert "chunk_id" in results[0]
    assert "text" in results[0]


def test_local_vector_store_empty_search(tmp_path):
    index_path = str(tmp_path / "empty_index.jsonl")
    store = LocalVectorStore(index_path=index_path)
    results = store.search("anything")
    assert results == []


def test_local_vector_store_persists(tmp_path):
    index_path = str(tmp_path / "persist_index.jsonl")
    store1 = LocalVectorStore(index_path=index_path)
    store1.build_from_documents([{"text": "Tanzania business tax registration TRA.", "source_name": "TRA", "url": "", "title": "TRA"}])

    # Load a new store from same path
    store2 = LocalVectorStore(index_path=index_path)
    assert len(store2.chunks) > 0


def test_search_returns_top_k(tmp_path):
    index_path = str(tmp_path / "topk_index.jsonl")
    store = LocalVectorStore(index_path=index_path)
    docs = [{"text": f"Tanzania business document number {i} about tax and registration.", "source_name": "src", "url": "", "title": f"doc{i}"} for i in range(20)]
    store.build_from_documents(docs)
    results = store.search("Tanzania tax registration", top_k=3)
    assert len(results) <= 3

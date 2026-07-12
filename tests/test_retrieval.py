"""Tests for chike.retrieval — the ported v15 RAG retrieval.

Two layers:
  1. Unit tests of the cosine-similarity + top-k scoring, exercised with fake
     numpy embeddings and a fake embedder. No GPU, no network, no index files.
  2. One integration test (skipped unless the real index files are present AND the
     e5 model can load) that runs the SAME critical-query list from
     kaggle/regenerate_rag_e5.py against the real 210-fact index.
"""
import os

import numpy as np
import pytest

import chike.retrieval as retrieval
from chike.retrieval import _score_and_rank, Retriever, EMB_PATH, TEXTS_PATH


# --- Unit: pure cosine + top-k scoring (fake embeddings) --------------------

def test_score_and_rank_returns_most_similar_fact_first():
    facts = np.array([
        [1.0, 0.0, 0.0],   # 0
        [0.0, 1.0, 0.0],   # 1
        [0.0, 0.0, 1.0],   # 2
    ])
    texts = ["fact-x", "fact-y", "fact-z"]
    query = np.array([0.0, 0.9, 0.1])  # closest to fact-y

    top = _score_and_rank(query, facts, texts, top_k=3)
    assert top[0] == "fact-y"


def test_score_and_rank_respects_top_k():
    facts = np.array([[1.0, 0.0], [0.9, 0.1], [0.0, 1.0], [0.1, 0.9]])
    texts = ["a", "b", "c", "d"]
    query = np.array([1.0, 0.0])

    top = _score_and_rank(query, facts, texts, top_k=2)
    assert len(top) == 2
    assert top[0] == "a"          # exact match ranks first
    assert top[1] == "b"          # next-closest second


def test_score_and_rank_is_scale_invariant_via_normalization():
    # A high-norm-but-wrong vector must NOT beat a unit-norm correct one — this is
    # the exact bug the cosine normalization fixed in v15.
    facts = np.array([
        [10.0, 10.0],   # high norm, 45 degrees off
        [1.0, 0.0],     # unit norm, exact direction
    ])
    texts = ["high-norm-wrong", "correct"]
    query = np.array([1.0, 0.0])

    top = _score_and_rank(query, facts, texts, top_k=1)
    assert top == ["correct"]


# --- Unit: Retriever with a fake embedder (no model download) ---------------

class _FakeEmbedder:
    """Stand-in for SentenceTransformer: records inputs, returns a fixed vector."""

    def __init__(self, vector):
        self._vector = np.array(vector)
        self.encoded = []

    def encode(self, inputs):
        self.encoded.append(inputs)
        return np.array([self._vector])


def _preloaded_retriever(facts, texts, query_vec):
    """Build a Retriever with index + embedder pre-injected, bypassing all I/O."""
    r = Retriever()
    r._index_loaded = True
    r.fact_embeddings = np.array(facts)
    r.fact_texts = list(texts)
    r.embed_model = _FakeEmbedder(query_vec)
    return r


def test_retriever_ranks_using_the_injected_embedder():
    r = _preloaded_retriever(
        facts=[[1.0, 0.0], [0.0, 1.0]],
        texts=["fact-a", "fact-b"],
        query_vec=[0.0, 1.0],
    )
    assert r.retrieve("swali lolote", top_k=1) == ["fact-b"]


def test_retriever_applies_the_e5_query_prefix():
    r = _preloaded_retriever(
        facts=[[1.0, 0.0]], texts=["fact-a"], query_vec=[1.0, 0.0],
    )
    r.retrieve("SDL ni asilimia ngapi", top_k=1)
    # e5 asymmetric retrieval: the query must carry the 'query: ' prefix.
    assert r.embed_model.encoded[0] == ["query: SDL ni asilimia ngapi"]


def test_retriever_returns_empty_when_index_absent():
    # Point at a non-existent index -> graceful RAG-disabled fallback, no embedder.
    r = Retriever(emb_path="/no/such/emb.npy", texts_path="/no/such/texts.json")
    assert r.retrieve("swali") == []
    assert r.embed_model is None      # embedder never imported/loaded


# --- Integration: real index + real e5 model (skipped if unavailable) -------

# Copied VERBATIM from kaggle/regenerate_rag_e5.py (critical_queries, lines ~132-151)
# — reused, not invented. The 'query: ' prefix is stripped here because
# chike.retrieval.retrieve re-adds it (matching modal_app.retrieve_facts).
_CRITICAL_QUERIES = [
    ('GN487A penalty', 'Faini kwa raia wa kigeni anayevunja GN487A ni kiasi gani hasa?', ['10,000,000', 'milioni kumi']),
    ('SDL rate', 'SDL rate Tanzania ni asilimia ngapi?', ['3.5']),
    ('NSSF employer', 'Mwajiri analipa asilimia ngapi NSSF kila mwezi?', ['10%', 'asilimia 10']),
    ('BRELA annual return', 'Ada ya annual return BRELA ni shilingi ngapi?', ['22,000', 'elfu 22']),
    ('VAT withholding services', 'VAT withholding kwenye huduma ni asilimia ngapi?', ['6%', 'services is 6']),
    ('Zero-rated input VAT', 'Naweza kudai input VAT kwenye bidhaa zilizo zero-rated?', ['ndiyo', 'input vat', 'can claim']),
    ('GN487A effective date', 'GN487A ilianza kutekelezwa tarehe gani?', ['28 july', '28 julai']),
    ('GN487A full name', 'Jina kamili la GN487A ni nini?', ['business licensing', 'prohibition']),
    ('Facilitator penalty', 'Adhabu ya raia wa Tanzania anayemsaidia mgeni ni nini?', ['5,000,000', 'milioni tano']),
    ('Phone repair activity', 'Mgeni anaweza kutengeneza simu?', ['phone', 'simu', 'activity 3']),
    ('PAYE 800K band', 'PAYE kwa mshahara wa TZS 800,000 ni kiasi gani?', ['760', '25%', '78,000']),
    ('SDL 12-employee calculation', 'Kwa wafanyakazi 12 wenye mshahara TZS 600,000, SDL jumla ni kiasi gani?', ['252,000']),
    ('NSSF 12-employee calculation', 'Kwa wafanyakazi 12 wenye mshahara TZS 600,000, NSSF jumla ni kiasi gani?', ['1,440,000']),
    ('NSSF compound (120k selection bug)', 'Kampuni ina wafanyakazi 12 wenye mshahara TZS 600,000 kila mmoja. NSSF jumla ya kampuni ni kiasi gani?', ['1,440,000']),
]


@pytest.mark.integration
@pytest.mark.skipif(
    not (os.path.exists(EMB_PATH) and os.path.exists(TEXTS_PATH)),
    reason="real RAG index files not present",
)
def test_real_index_retrieves_critical_queries_in_top3():
    pytest.importorskip("sentence_transformers")
    try:
        r = Retriever()
        r._ensure_index()  # loads the real 210-fact index (local file IO)
        # Force the embedder to load now; skip cleanly if the model can't download.
        from sentence_transformers import SentenceTransformer
        r.embed_model = SentenceTransformer(retrieval.EMBED_MODEL_NAME)
    except Exception as e:  # offline / model unavailable
        pytest.skip(f"e5 model unavailable: {e}")

    passed = 0
    for name, question, expected in _CRITICAL_QUERIES:
        top3 = r.retrieve(question, top_k=3)
        if any(kw.lower() in fact.lower() for fact in top3 for kw in expected):
            passed += 1

    # At least 3 of the known critical queries must hit their fact in the top-3.
    assert passed >= 3, f"only {passed}/{len(_CRITICAL_QUERIES)} critical queries hit top-3"

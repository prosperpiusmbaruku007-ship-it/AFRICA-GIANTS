"""RAG retrieval — ported verbatim from v15 production (chike-inference/modal_app.py).

This is the SAME retrieval that produced the v15 gate pass (87.9% in-corpus): the
intfloat/multilingual-e5-base embedder (768-dim), the pre-computed fact index
(rag_embeddings.npy + rag_facts_text.json), cosine similarity over L2-normalized
vectors, and top-k selection. It is NOT a reimplementation — the scoring math and
the e5 'query: ' prefix are copied from modal_app.retrieve_facts so the orchestrator
retrieves exactly what production does (R12: the eval must test the production system).

Index files: this reads the SINGLE tracked copy under kaggle/ — the same directory
LocalAdapter (item 1) reads chike_config.json from — so every local component reads
one canonical index, not a per-component copy. (Modal bakes its own copy into its
image at deploy time per R15; nothing here creates a third. When the index is
regenerated, update the kaggle/ copy and this picks it up automatically.)

Lazy loading mirrors LocalAdapter (item 1): the index and the embedding model load
on first retrieve(), never at import, so this module imports with no GPU and no
network (tests can import it and unit-test the scoring in isolation).

FAIL-LOUD INDEX CONTRACT (2026-08-06, pre-launch blocker): the module-level EMB_PATH /
TEXTS_PATH point at the repo-relative kaggle/ copy, which does NOT exist inside the Modal
image (production bakes its own copy into /root/assets per R15). Under the previous
graceful-disable behaviour a wiring mistake there returned [] from every retrieve() call —
the model would answer with NO facts at all, presenting as a total quality collapse rather
than a config error, with nothing in the logs saying so. A missing/corrupt index now RAISES
RetrievalIndexError by default; `require_index=False` restores the old silent fallback for
the rare caller that genuinely wants RAG-optional behaviour. Deployments should call
preflight() (or configure(..., expected_fact_count=N)) at startup so a bad index fails
before the first user question, not silently underneath it.
"""

import json
import os
import re
from typing import List, Optional

import numpy as np

# One canonical index, read from kaggle/ — the same directory LocalAdapter loads
# chike_config.json from (chike/model_abstraction/local_adapter.py). No per-component copy.
_HERE = os.path.dirname(__file__)
EMB_PATH = os.path.normpath(
    os.path.join(_HERE, "..", "kaggle", "rag_embeddings.npy")
)
TEXTS_PATH = os.path.normpath(
    os.path.join(_HERE, "..", "kaggle", "rag_facts_text.json")
)

EMBED_MODEL_NAME = "intfloat/multilingual-e5-base"


class RetrievalIndexError(RuntimeError):
    """The RAG index is missing, unreadable, or internally inconsistent.

    Raised instead of silently disabling retrieval, so a mis-wired index path or a
    half-written R15 regeneration fails loudly at startup rather than degrading every
    answer to a no-facts generation.
    """

# --- numeric-query hybrid retrieval (numeric-embedding-hijack fix) -----------
# A digit-bearing amount in the query dominates the e5 embedding and evicts the
# TOPIC fact from the top-k, surfacing numerically-similar-but-wrong facts instead
# (trademark fees, VAT deferment thresholds — all "X TZS" entries). Confirmed on
# eval_317/probe_01 (salon): "TZS 100,000,000" retrieved {fine-limit, trademark
# fee, vat-deferment} with zero GN487A facts, so the model fabricated a "<100M
# capital" exception. The fix retrieves a SECOND arm on a number-stripped query and
# appends the first recovered topic fact — append-only, so a baseline fact is never
# dropped (interleave dropped eval_331/eval_355's rank-3 EFD fact; append-only can't).
# See PROGRESS.md "Prohibition-inversion investigation" for the full evidence.

# Strip digit-bearing amounts (optional TZS prefix + comma/dot grouping) and bare
# standalone integers. Number-WORDS (milioni/elfu/kumi) are deliberately KEPT — they
# carry topic meaning without the hijacking magnitude.
_NUMERIC_AMOUNT = re.compile(r"\bTZS\s*[\d][\d.,]*|\b[\d][\d.,]*\b", re.IGNORECASE)

# The number-stripped arm retrieves a wider pool so the recovered topic fact is
# reachable even when it sits below the full-query top-3; only the first NEW fact is
# appended (final size = top_k + 1 on numeric queries).
_STRIPPED_POOL = 6


def strip_numeric_amounts(text: str) -> str:
    """Remove digit-bearing amounts, keep number-words. Validated in the retrieval
    prototype: recovers the salon GN487A fact and the EFD/OSHA topic facts without
    touching non-numeric queries."""
    s = _NUMERIC_AMOUNT.sub(" ", text)
    s = re.sub(r"\s+([,.?!])", r"\1", s)   # tidy space left before punctuation
    s = re.sub(r"\s{2,}", " ", s).strip()  # collapse doubled spaces
    return s


def _has_digit(text: str) -> bool:
    return any(ch.isdigit() for ch in text)


def _rank_indices(q_emb, fact_embeddings, top_k: int) -> List[int]:
    """Cosine similarity + top-k index selection, copied verbatim from
    modal_app.retrieve_facts. Normalize the query AND the fact vectors before the
    dot-product: raw dot-product favoured high-norm vectors and surfaced semantically-
    wrong facts in v15 (an SDL query once ranked GN487A penalties top). Pure function
    of numpy inputs — unit-testable with a fake embedding, no GPU or network."""
    q_norm = q_emb / (np.linalg.norm(q_emb) + 1e-10)
    norms = np.linalg.norm(fact_embeddings, axis=1, keepdims=True)
    normalized_facts = fact_embeddings / (norms + 1e-10)
    scores = np.dot(normalized_facts, q_norm)
    return list(np.argsort(scores)[-top_k:][::-1])


def _score_and_rank(q_emb, fact_embeddings, fact_texts, top_k: int) -> List[str]:
    """Index selection (above) mapped to fact texts. Signature/behaviour unchanged."""
    return [fact_texts[i] for i in _rank_indices(q_emb, fact_embeddings, top_k)]


class Retriever:
    """Holds the lazily-loaded e5 embedder + fact index; encodes then ranks.

    Loading is split to mirror production exactly: the index loads first and, if the
    files are absent, retrieval is gracefully disabled (returns []) WITHOUT importing
    the heavy embedder — the same RAG-disabled fallback as modal_app.
    """

    def __init__(
        self,
        emb_path: str = EMB_PATH,
        texts_path: str = TEXTS_PATH,
        require_index: bool = True,
        expected_fact_count: Optional[int] = None,
    ):
        """emb_path/texts_path: explicit index locations — ALWAYS pass these in a
        deployment whose index is not at the repo-relative kaggle/ default (e.g. Modal's
        baked /root/assets copy). require_index=True (default) raises RetrievalIndexError
        when the files are absent; False restores the legacy silent RAG-disabled fallback.
        expected_fact_count, when given, is asserted against the loaded index — the guard
        that catches a stale or half-regenerated index (R15) at startup."""
        self.emb_path = emb_path
        self.texts_path = texts_path
        self.require_index = require_index
        self.expected_fact_count = expected_fact_count
        self.embed_model = None
        self.fact_embeddings = None
        self.fact_texts: List[str] = []
        self._index_loaded = False

    def _ensure_index(self):
        if self._index_loaded:
            return
        if not (os.path.exists(self.emb_path) and os.path.exists(self.texts_path)):
            if self.require_index:
                raise RetrievalIndexError(
                    "RAG index not found — retrieval would silently return no facts. "
                    f"emb_path={self.emb_path!r} (exists={os.path.exists(self.emb_path)}), "
                    f"texts_path={self.texts_path!r} (exists={os.path.exists(self.texts_path)}). "
                    "Pass explicit paths (Retriever(emb_path=..., texts_path=...) or "
                    "chike.retrieval.configure(...)), or set require_index=False to allow "
                    "running without RAG."
                )
            # Legacy graceful fallback — opt-in only.
            self.fact_embeddings = None
            self.fact_texts = []
            self._index_loaded = True
            return

        self.fact_embeddings = np.load(self.emb_path)
        with open(self.texts_path, encoding="utf-8") as f:
            self.fact_texts = json.load(f)
        self._validate_index()
        self._index_loaded = True

    def _validate_index(self):
        """Structural checks on a LOADED index. These raise regardless of require_index —
        a present-but-inconsistent index is a corruption, never a 'RAG optional' case.
        Mirrors kaggle/eval.py's shape assertion, which production and this module lacked."""
        n_emb = int(self.fact_embeddings.shape[0])
        n_txt = len(self.fact_texts)
        if n_emb != n_txt:
            raise RetrievalIndexError(
                f"RAG index inconsistent: {n_emb} embeddings vs {n_txt} fact texts "
                f"({self.emb_path!r} / {self.texts_path!r}). Regenerate per R15."
            )
        if n_emb == 0:
            raise RetrievalIndexError(
                f"RAG index is empty (0 facts) at {self.emb_path!r} / {self.texts_path!r}."
            )
        if self.expected_fact_count is not None and n_emb != self.expected_fact_count:
            raise RetrievalIndexError(
                f"RAG index fact-count mismatch: loaded {n_emb}, expected "
                f"{self.expected_fact_count} ({self.texts_path!r}). Either the index is "
                "stale or the expectation was not updated after an R15 regeneration."
            )

    def preflight(self) -> int:
        """Force the index to load and validate NOW, returning the fact count.

        This is the startup assertion: call it once at deploy/boot so a missing, empty,
        inconsistent, or unexpected-size index fails immediately and visibly, instead of
        every answer quietly losing its facts. Does NOT load the embedding model (no
        network/GPU), so it is cheap enough to run unconditionally at startup."""
        self._ensure_index()
        return len(self.fact_texts)

    def _ensure_embed_model(self):
        if self.embed_model is None:
            # Imported and downloaded only here, matching modal_app's lazy
            # SentenceTransformer construction — never at import time.
            from sentence_transformers import SentenceTransformer

            self.embed_model = SentenceTransformer(EMBED_MODEL_NAME)

    def _encode_and_rank(self, text: str, top_k: int) -> List[int]:
        # e5 asymmetric retrieval: queries take the 'query: ' prefix (facts were
        # embedded with 'passage: ' at build time). Verbatim from production.
        q_emb = self.embed_model.encode([f"query: {text}"])[0]
        return _rank_indices(q_emb, self.fact_embeddings, top_k)

    def retrieve(self, question: str, top_k: int = 3) -> List[str]:
        self._ensure_index()
        if self.fact_embeddings is None or not self.fact_texts:
            return []
        self._ensure_embed_model()

        full_idx = self._encode_and_rank(question, top_k)

        # Non-numeric queries: single-arm retrieval, BYTE-IDENTICAL to production.
        # No second embed call, no merge — the numeric-hijack fix never touches them.
        if not _has_digit(question):
            return [self.fact_texts[i] for i in full_idx]

        # Numeric queries: add a number-stripped arm and append the first NEW fact it
        # surfaces (append-only — the baseline top-k is preserved verbatim, never
        # reordered or dropped). If stripping changes nothing, fall back to baseline.
        stripped = strip_numeric_amounts(question)
        if not stripped or stripped == question:
            return [self.fact_texts[i] for i in full_idx]

        stripped_idx = self._encode_and_rank(stripped, _STRIPPED_POOL)
        merged = list(full_idx)
        for i in stripped_idx:
            if i not in merged:
                merged.append(i)
                break
        return [self.fact_texts[i] for i in merged]


# Module-level singleton so repeated calls reuse one loaded model/index.
_DEFAULT_RETRIEVER: Optional[Retriever] = None


def configure(
    emb_path: str = EMB_PATH,
    texts_path: str = TEXTS_PATH,
    require_index: bool = True,
    expected_fact_count: Optional[int] = None,
) -> Retriever:
    """Point the module-level retrieve() at an EXPLICIT index and validate it now.

    This is the hook a deployment uses instead of inheriting the repo-relative kaggle/
    default — notably the Modal image, whose index lives at /root/assets and where the
    default path does not exist at all. Replaces the singleton, runs preflight(), and
    returns the Retriever so the caller can log the fact count.
    """
    global _DEFAULT_RETRIEVER
    retriever = Retriever(
        emb_path=emb_path,
        texts_path=texts_path,
        require_index=require_index,
        expected_fact_count=expected_fact_count,
    )
    retriever.preflight()
    _DEFAULT_RETRIEVER = retriever
    return retriever


def retrieve(question: str, top_k: int = 3) -> List[str]:
    """Orchestrator-facing interface: retrieve(question) -> list[str].

    Wraps a lazily-constructed singleton Retriever. The first call loads the e5
    model and the index; later calls reuse them. Matches the orchestrator's stub
    signature exactly, so it is a drop-in default retriever.

    The implicit singleton uses the repo-relative default paths and fails loudly if
    they are absent — use configure() to bind explicit paths in a deployment.
    """
    global _DEFAULT_RETRIEVER
    if _DEFAULT_RETRIEVER is None:
        _DEFAULT_RETRIEVER = Retriever()
    return _DEFAULT_RETRIEVER.retrieve(question, top_k)

"""
Vector store with two backends:
  - EmbeddingVectorStore  : sentence-transformers + FAISS (production)
  - LocalVectorStore      : BM25 JSON fallback (no GPU / no FAISS installed)

The retriever always uses EmbeddingVectorStore first and falls back to
LocalVectorStore if sentence-transformers or faiss are not installed.
"""
import json
import os
import re
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional

from src.common.logging import get_logger
from src.common.storage import get_project_root

logger = get_logger("rag.vector_store")

TOKEN_RE = re.compile(r"[A-Za-z0-9_'-]+")

EMBED_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# ---------------------------------------------------------------------------
# Shared data structures
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    chunk_id: str
    text: str
    source: str = "local"
    url: str = ""
    title: str = ""
    metadata: Dict[str, str] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["metadata"] = data["metadata"] or {}
        return data


def tokenize(text: str) -> List[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> Iterable[str]:
    words = text.split()
    if not words:
        return
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + chunk_size]).strip()
        if chunk:
            yield chunk


# ---------------------------------------------------------------------------
# FAISS + sentence-transformers backend
# ---------------------------------------------------------------------------

class EmbeddingVectorStore:
    """
    Dense retrieval using multilingual sentence-transformers + FAISS.

    Handles Swahili and English queries through the multilingual embedding
    model. Persists the index and metadata to disk.
    """

    def __init__(self, index_dir: Optional[str] = None):
        root = get_project_root()
        self.index_dir = index_dir or os.path.join(root, "vector_db", "faiss_index")
        self.meta_path = os.path.join(self.index_dir, "chunks.jsonl")
        self.faiss_path = os.path.join(self.index_dir, "index.faiss")
        self.chunks: List[Chunk] = []
        self._model = None
        self._index = None
        self._load_model()
        self._load()

    def _load_model(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(EMBED_MODEL_NAME)
            logger.info("Loaded embedding model: %s", EMBED_MODEL_NAME)
        except ImportError:
            logger.warning("sentence-transformers not installed — EmbeddingVectorStore unavailable")
            self._model = None

    def _embed(self, texts: List[str]):
        if self._model is None:
            return None
        return self._model.encode(texts, show_progress_bar=False, normalize_embeddings=True)

    def _load(self) -> None:
        if self._model is None:
            return
        try:
            import faiss
            import numpy as np
        except ImportError:
            logger.warning("faiss-cpu not installed — EmbeddingVectorStore unavailable")
            self._model = None
            return

        self.chunks = []
        if not os.path.exists(self.meta_path) or not os.path.exists(self.faiss_path):
            return

        with open(self.meta_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                self.chunks.append(Chunk(
                    chunk_id=row["chunk_id"],
                    text=row["text"],
                    source=row.get("source", "local"),
                    url=row.get("url", ""),
                    title=row.get("title", ""),
                    metadata=row.get("metadata", {}),
                ))

        self._index = faiss.read_index(self.faiss_path)
        logger.info("Loaded %d chunks and FAISS index from %s", len(self.chunks), self.index_dir)

    def _save(self) -> None:
        import faiss
        os.makedirs(self.index_dir, exist_ok=True)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            for chunk in self.chunks:
                f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
        faiss.write_index(self._index, self.faiss_path)

    def is_ready(self) -> bool:
        return self._model is not None

    def build_from_documents(self, documents: List[dict]) -> int:
        if not self.is_ready():
            return 0
        import faiss
        import numpy as np

        self.chunks = []
        texts_to_embed = []

        for doc_idx, doc in enumerate(documents):
            text = (
                doc.get("cleaned_content") or doc.get("raw_content")
                or doc.get("text") or doc.get("output") or doc.get("expected") or ""
            )
            if doc.get("question") and text:
                text = f"Question: {doc['question']}\nAnswer: {text}"
            title = doc.get("title") or doc.get("instruction") or doc.get("source_name") or "document"
            source = doc.get("source_name") or doc.get("source") or "local"
            url = doc.get("url") or ""

            for chunk_idx, chunk_body in enumerate(chunk_text(text)):
                chunk = Chunk(
                    chunk_id=f"doc_{doc_idx:05d}_chunk_{chunk_idx:03d}",
                    text=chunk_body,
                    source=source,
                    url=url,
                    title=title,
                    metadata={"document_index": str(doc_idx)},
                )
                self.chunks.append(chunk)
                texts_to_embed.append(chunk_body)

        if not texts_to_embed:
            return 0

        logger.info("Embedding %d chunks with %s ...", len(texts_to_embed), EMBED_MODEL_NAME)
        embeddings = self._embed(texts_to_embed).astype("float32")
        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)  # inner product on normalized vectors = cosine sim
        self._index.add(embeddings)
        self._save()
        logger.info("Built FAISS index with %d chunks", len(self.chunks))
        return len(self.chunks)

    def search(self, query: str, top_k: int = 4) -> List[dict]:
        if not self.is_ready() or self._index is None or self._index.ntotal == 0:
            return []
        import numpy as np

        q_emb = self._embed([query]).astype("float32")
        scores, indices = self._index.search(q_emb, min(top_k, self._index.ntotal))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            chunk = self.chunks[idx]
            results.append({**chunk.to_dict(), "score": round(float(score), 4)})
        return results


# ---------------------------------------------------------------------------
# BM25 JSON fallback backend (unchanged from original)
# ---------------------------------------------------------------------------

class LocalVectorStore:
    """
    BM25-style JSON vector store — fallback when FAISS is not available.
    Works without any ML dependencies but has weaker Swahili retrieval.
    """

    def __init__(self, index_path: Optional[str] = None):
        root = get_project_root()
        self.index_path = index_path or os.path.join(root, "vector_db", "rag_index.jsonl")
        self.chunks: List[Chunk] = []
        self._token_cache: Dict[str, set] = {}
        self.load()

    def load(self) -> None:
        self.chunks = []
        self._token_cache = {}
        if not os.path.exists(self.index_path):
            return
        with open(self.index_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                chunk = Chunk(
                    chunk_id=row["chunk_id"],
                    text=row["text"],
                    source=row.get("source", "local"),
                    url=row.get("url", ""),
                    title=row.get("title", ""),
                    metadata=row.get("metadata", {}),
                )
                self.chunks.append(chunk)
                self._token_cache[chunk.chunk_id] = set(tokenize(chunk.text))
        logger.info("Loaded %d BM25 chunks from %s", len(self.chunks), self.index_path)

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "w", encoding="utf-8") as f:
            for chunk in self.chunks:
                f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")

    def build_from_documents(self, documents: List[dict]) -> int:
        self.chunks = []
        self._token_cache = {}
        for doc_idx, doc in enumerate(documents):
            text = (
                doc.get("cleaned_content") or doc.get("raw_content")
                or doc.get("text") or doc.get("output") or doc.get("expected") or ""
            )
            if doc.get("question") and text:
                text = f"Question: {doc['question']}\nAnswer: {text}"
            title = doc.get("title") or doc.get("instruction") or doc.get("source_name") or "document"
            source = doc.get("source_name") or doc.get("source") or "local"
            url = doc.get("url") or ""
            for chunk_idx, chunk_body in enumerate(chunk_text(text)):
                chunk = Chunk(
                    chunk_id=f"doc_{doc_idx:05d}_chunk_{chunk_idx:03d}",
                    text=chunk_body,
                    source=source,
                    url=url,
                    title=title,
                    metadata={"document_index": str(doc_idx)},
                )
                self.chunks.append(chunk)
                self._token_cache[chunk.chunk_id] = set(tokenize(chunk.text))
        self.save()
        logger.info("Built BM25 index with %d chunks", len(self.chunks))
        return len(self.chunks)

    def search(self, query: str, top_k: int = 4) -> List[dict]:
        query_tokens = set(tokenize(query))
        if not query_tokens:
            return []
        scored = []
        for chunk in self.chunks:
            chunk_tokens = self._token_cache.get(chunk.chunk_id) or set(tokenize(chunk.text))
            overlap = query_tokens.intersection(chunk_tokens)
            if not overlap:
                continue
            score = len(overlap) / max(len(query_tokens), 1)
            scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {**chunk.to_dict(), "score": round(score, 4)}
            for score, chunk in scored[:top_k]
        ]


# ---------------------------------------------------------------------------
# Auto-select best available backend
# ---------------------------------------------------------------------------

def get_vector_store(index_dir: Optional[str] = None) -> "EmbeddingVectorStore | LocalVectorStore":
    """
    Return the best available vector store.
    Tries EmbeddingVectorStore first; falls back to LocalVectorStore.
    """
    store = EmbeddingVectorStore(index_dir)
    if store.is_ready():
        return store
    logger.warning("Falling back to BM25 LocalVectorStore (install sentence-transformers + faiss-cpu for better retrieval)")
    return LocalVectorStore()

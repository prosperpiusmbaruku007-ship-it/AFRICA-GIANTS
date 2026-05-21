import json
import os
import re
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional

from src.common.logging import get_logger
from src.common.storage import get_project_root

logger = get_logger("rag.vector_store")

TOKEN_RE = re.compile(r"[A-Za-z0-9_'-]+")


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


class LocalVectorStore:
    """Small JSON-backed retrieval store.

    This is intentionally simple for the first live version. It works without
    FAISS/Chroma, and can later be replaced by a real vector DB behind the same
    retriever interface.
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

        logger.info("Loaded %s RAG chunks from %s", len(self.chunks), self.index_path)

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
                doc.get("cleaned_content")
                or doc.get("raw_content")
                or doc.get("text")
                or doc.get("output")
                or doc.get("expected")
                or ""
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
        logger.info("Built RAG index with %s chunks", len(self.chunks))
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
            {
                **chunk.to_dict(),
                "score": round(score, 4),
            }
            for score, chunk in scored[:top_k]
        ]

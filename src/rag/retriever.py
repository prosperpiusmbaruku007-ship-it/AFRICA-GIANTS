import json
import os
from typing import List

from src.common.logging import get_logger
from src.common.storage import get_project_root
from src.rag.vector_store import get_vector_store

logger = get_logger("rag.retriever")


def _load_jsonl(path: str) -> List[dict]:
    rows = []
    if not os.path.exists(path):
        return rows

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def load_local_documents() -> List[dict]:
    root = get_project_root()
    candidates = [
        os.path.join(root, "data", "processed", "cleaned_documents.jsonl"),
        os.path.join(root, "data", "processed", "train_sft.jsonl"),
        os.path.join(root, "data", "processed", "val_sft.jsonl"),
        os.path.join(root, "data", "eval", "tanzania_business_qa.jsonl"),
        os.path.join(root, "data", "eval", "business_benchmarks.jsonl"),
    ]

    documents: List[dict] = []
    for path in candidates:
        documents.extend(_load_jsonl(path))
    return documents


class Retriever:
    def __init__(self):
        self.store = get_vector_store()
        if not self.store.chunks:
            self.rebuild()

    def rebuild(self) -> int:
        documents = load_local_documents()
        if not documents:
            logger.warning("No local documents found for RAG indexing.")
            return 0
        return self.store.build_from_documents(documents)

    def retrieve(self, query: str, top_k: int = 4) -> List[dict]:
        if not self.store.chunks:
            self.rebuild()
        return self.store.search(query, top_k=top_k)


from typing import List, Tuple

from src.rag.retriever import Retriever


SYSTEM_RAG_PROMPT = (
    "You are Africa Giants, a Tanzania business assistant. Answer using the "
    "provided context when it is relevant. If the context is not enough, say "
    "what is missing and recommend checking the official source."
)


class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()

    def build_prompt(self, question: str, chunks: List[dict]) -> str:
        if not chunks:
            return question

        context_blocks = []
        for idx, chunk in enumerate(chunks, start=1):
            source = chunk.get("source") or "local"
            url = chunk.get("url") or "no-url"
            context_blocks.append(
                f"[Source {idx}: {source} | {url}]\n{chunk.get('text', '')}"
            )

        context = "\n\n".join(context_blocks)
        return (
            "Use this verified context to answer the user.\n\n"
            f"{context}\n\n"
            f"User question: {question}\n\n"
            "Answer with practical next steps and mention sources when useful."
        )

    def prepare(self, question: str, top_k: int = 4) -> Tuple[str, List[dict]]:
        chunks = self.retriever.retrieve(question, top_k=top_k)
        return self.build_prompt(question, chunks), chunks


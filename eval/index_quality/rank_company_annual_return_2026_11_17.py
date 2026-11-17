# -*- coding: utf-8 -*-
"""STEP ZERO OF A WORDING JOB (CLAUDE.md R15): MEASURE THE NEW ROW'S RANK. `company_annual_return_deadline` (the prospective index's last row, 215) for the asker's phrasings, in the PROSPECTIVE 216-row index, built with the production
builder and the production embedder (intfloat/multilingual-e5-base, loaded OFFLINE from the local cache). Rank 1 is the ceiling: if the row is already rank 1 retrieval has nothing left to give and any remaining defect is generation.

    python eval/index_quality/rank_company_annual_return_2026_11_17.py  ->  eval/results/rank_company_annual_return_2026_11_17.json
"""
import importlib.util
import io
import json
import os
import sys

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(REPO, "scripts"))
os.chdir(REPO)                                         # precompute's FACTS_PATH is relative
import numpy as np                                     # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

spec = importlib.util.spec_from_file_location("precompute", os.path.join(REPO, "scripts", "precompute_rag_embeddings.py"))
pre = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pre)
KEY = "company_annual_return_deadline"
QUERIES = [
    "Annual return ya BRELA inapaswa kuwasilishwa lini?",
    "Mara ngapi kampuni iliyosajiliwa na BRELA inahitajika kuwasilisha annual return (ripoti ya kila mwaka)?",   # eval_072 verbatim
    "Annual return ya kampuni inatakiwa kuwasilishwa ndani ya muda gani?",
    "Kampuni yangu ilisajiliwa Machi, annual return ni lini?",
    "Nikichelewa kuwasilisha annual return BRELA nitatozwa nini?",
    "Je, annual return ya BRELA inawasilishwa ndani ya miezi 12 baada ya usajili?",
]


def main():
    texts, keys, _dropped = pre.build_fact_texts()
    row = keys.index(KEY)
    model = SentenceTransformer(pre.EMBED_MODEL)
    docs = model.encode([f"passage: {t}" for t in texts], normalize_embeddings=True, batch_size=32)
    out = {"rows": len(texts), "row": row, "key": KEY, "queries": []}
    for q in QUERIES:
        qv = model.encode([f"query: {q}"], normalize_embeddings=True)[0]
        order = np.argsort(-(docs @ qv))
        rank = int(np.where(order == row)[0][0]) + 1
        top3 = [(int(i), keys[i]) for i in order[:3]]
        out["queries"].append({"q": q, "rank": rank, "top3": top3})
        print(f"rank {rank:>3} | {q[:90]} | top3 {[k for _, k in top3]}")
    io.open(os.path.join(REPO, "eval", "results", "rank_company_annual_return_2026_11_17.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

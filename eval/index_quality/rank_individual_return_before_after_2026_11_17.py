# -*- coding: utf-8 -*-
"""READ-ONLY: did the 2026-11-17 index (215 rows) DISPLACE the individual income-tax-return row for the short question that was answered live with a tax RATE?
Compares the top-5 retrieved rows for each question over the PREVIOUS served index (211 rows, git 8452139) and the CURRENT one (215 rows). Offline: the e5 model loads from the local HF cache (HF_HUB_OFFLINE=1).
    python eval/index_quality/rank_individual_return_before_after_2026_11_17.py   ->  eval/results/rank_individual_return_before_after_2026_11_17.json"""
import io
import json
import os
import subprocess
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "rank_individual_return_before_after_2026_11_17.json")
QUESTIONS = [
    "Return ya kodi ya mapato ya mtu binafsi ni lini?",                                   # the live specimen (answered with a RATE)
    "Mwisho wa kuwasilisha return ya kodi ya mapato kwa mtu binafsi ni lini?",             # the committed regen guard's wording
    "Je, mtu binafsi mwenye biashara anatakiwa kuwasilisha return ya kodi ya mapato lini?",
    "Kampuni inawasilisha return ya kodi ya mapato lini?",
]
NEEDLE_IND = "Mkazi asiye na kodi ya kulipa"           # the individual-return row
NEEDLE_CORP = "kampuni ya kawaida (mwaka wa kalenda) kufikia 30 Juni"


def git_blob(rev, path):
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=REPO)


def load(rev):
    texts = json.loads(git_blob(rev, "chike-inference/rag_facts_text.json").decode("utf-8"))
    emb = np.load(io.BytesIO(git_blob(rev, "chike-inference/rag_embeddings.npy")))
    return texts, emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)


def main():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("intfloat/multilingual-e5-base")
    res = {}
    for label, rev in (("BEFORE (211 rows, 8452139)", "8452139"), ("AFTER (215 rows, a2e6611)", "a2e6611")):
        texts, emb = load(rev)
        res[label] = {}
        for q in QUESTIONS:
            v = model.encode(["query: " + q])[0]
            v = v / (np.linalg.norm(v) + 1e-10)
            order = np.argsort(emb @ v)[::-1]
            rank = lambda needle: next((r for r, i in enumerate(order, 1) if needle in texts[i]), None)
            res[label][q] = {"individual_row_rank": rank(NEEDLE_IND), "company_row_rank": rank(NEEDLE_CORP), "top5": [texts[i][:90] for i in order[:5]]}
            print(f"{label:<28} ind={res[label][q]['individual_row_rank']!s:>4} corp={res[label][q]['company_row_rank']!s:>4}  {q[:70]}")
            for t in res[label][q]["top5"][:3]:
                print("      ", t)
    json.dump(res, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

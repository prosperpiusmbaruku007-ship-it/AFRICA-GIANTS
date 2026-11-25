# -*- coding: utf-8 -*-
"""SEVERANCE ROW 188: MEASURE CANDIDATE REWRITES BEFORE QUEUEING ONE (R15 step zero, R22: the population is the six phrasings of measure_severance_rank_2026_11_25.py, two of which rank 4 and 5 today).
Only the LEAD and the length change; every claim is the current row's claim (7 days' basic wage per complete year, up to 10 years, 12 consecutive months, the exclusions, ELRA). No new fact. The candidate replaces row 188's embedding with a locally computed one
(local and Kaggle e5 agree to cosine >= 0.9999998, eval/results/regen_landing_verification_2026_11_24b.json); every other row is the served embedding. Nothing is encoded: this selects a candidate for the NEXT regen.

    python eval/index_quality/measure_severance_candidates_2026_11_25.py  ->  eval/results/severance_candidates_2026_11_25.json"""
import importlib.util
import io
import json
import os
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
spec = importlib.util.spec_from_file_location("_sev", os.path.join(REPO, "eval", "index_quality", "measure_severance_rank_2026_11_25.py"))
sev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sev)

CANDIDATES = {
    "current (served)": None,
    "A ask-led, same claims": "Severance pay (malipo ya kuachishwa kazi) ni kiasi gani? Mfanyakazi aliyetimiza miezi 12 mfululizo na akaachishwa anapata angalau mshahara wa msingi wa siku 7 kwa kila mwaka kamili, hadi miaka 10. Hayalipwi kwa utovu wa nidhamu, kukataa kazi mbadala bila sababu, kustaafu au mkataba kuisha (ELRA).",
    "B shorter": "Severance pay ni kiasi gani? Aliyetimiza miezi 12 mfululizo na akaachishwa: siku 7 za mshahara wa msingi kwa kila mwaka kamili, hadi miaka 10. Si kwa utovu wa nidhamu, kukataa kazi mbadala, kustaafu au mkataba kuisha (ELRA).",
    "C shortest": "Severance pay ni nini? Mfanyakazi aliyeachishwa baada ya miezi 12 mfululizo: siku 7 za mshahara wa msingi kwa kila mwaka kamili (hadi miaka 10), isipokuwa utovu wa nidhamu, kukataa kazi mbadala, kustaafu au mkataba kuisha (ELRA).",
}


def main():
    from sentence_transformers import SentenceTransformer
    texts = json.load(io.open(os.path.join(REPO, "kaggle", "rag_facts_text.json"), encoding="utf-8"))
    emb = np.load(os.path.join(REPO, "kaggle", "rag_embeddings.npy"))
    assert texts[188].startswith(sev.NEEDLE)
    model = SentenceTransformer("intfloat/multilingual-e5-base")

    def unit(v):
        return v / (np.linalg.norm(v) + 1e-10)
    out = {}
    for name, cand in CANDIDATES.items():
        e = emb.copy()
        if cand is not None:
            e[188] = unit(model.encode(["passage: " + cand], convert_to_numpy=True)[0])
        ranks = []
        for label, text in sev.PHRASINGS:
            s = e @ unit(model.encode(["query: " + text], convert_to_numpy=True)[0])
            ranks.append(int(np.where(np.argsort(s)[::-1] == 188)[0][0]) + 1)
        out[name] = {"chars": len(cand if cand else texts[188]), "ranks": ranks, "worst": max(ranks), "outside_top3": sum(r > 3 for r in ranks)}
        print(f"  {name:<26} chars={out[name]['chars']:>3} ranks={ranks}  outside top-3: {out[name]['outside_top3']}")
    json.dump({"phrasings": [p for _, p in sev.PHRASINGS], "candidates": out, "text": {k: v for k, v in CANDIDATES.items() if v}}, io.open(os.path.join(REPO, "eval", "results", "severance_candidates_2026_11_25.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""SEVERANCE FACT [188]: IS THE ONE KNOWN SELF-RETRIEVAL FAILURE A REAL RETRIEVAL PROBLEM? (founder, 2026-11-25; R18: committed with its result)
The Kaggle regen reports 223/224 self-retrieval: [188] (severance pay) retrieves 'duration of maternity cash benefit: 12 weeks' (0.898) as its own top match. It was the one unchanged failure in every regen since the 211-row index (PROGRESS 4aa onward).
This measures (1) whether it failed in the 220-row build too (the previously served index, from git), and (2) the severance fact's RANK for real phrasings, on BOTH indexes. Local e5 weights offline; the index embeddings are the SERVED files.
Phrasings: three are VERBATIM questions from the committed corpora (named), three are authored to carry the cues the founder named ("miezi 12", "mwaka mmoja", the day-count ask). Rank 1-3 = in the model's served context; the rule is: fix only if it falls out of the top 3.

    python eval/index_quality/measure_severance_rank_2026_11_25.py  ->  eval/results/severance_rank_2026_11_25.json"""
import io
import json
import os
import subprocess
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
NEEDLE = "Malipo ya kuachishwa kazi (severance pay)"
OLD_REF = "18f4f50"          # the commit whose kaggle/ index is the 220-row one that was live


def git_bytes(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=REPO, capture_output=True, check=True).stdout


PHRASINGS = [
    ("verbatim: eval corpus", "Naomba maelezo ya severance pay kwa mfanyakazi aliyeachishwa."),
    ("verbatim: eval corpus (miezi 8)", "Mfanyakazi wangu amefanya kazi miezi 8 tu. Nikisitisha ajira yake sasa, sihitajiki kumlipa severance pay, au siyo?"),
    ("verbatim: eval corpus (premise)", "Mfanyakazi aliyefanya kazi miezi 8 tu akiachishwa, hastahili malipo ya kuachishwa kazi, sivyo?"),
    ("authored: miezi 12", "Mfanyakazi amefanya kazi miezi 12 mfululizo, nikimwachisha nimlipe severance kiasi gani?"),
    ("authored: mwaka mmoja", "Nimefanya kazi mwaka mmoja na nimeachishwa kazi, nina haki ya malipo gani ya kuachishwa?"),
    ("authored: the day count", "Severance pay ni siku ngapi za mshahara kwa kila mwaka wa kazi?"),
]


def main():
    from sentence_transformers import SentenceTransformer
    new_t = json.load(io.open(os.path.join(REPO, "kaggle", "rag_facts_text.json"), encoding="utf-8"))
    new_e = np.load(os.path.join(REPO, "kaggle", "rag_embeddings.npy"))
    old_t = json.loads(git_bytes(OLD_REF, "kaggle/rag_facts_text.json").decode("utf-8"))
    old_e = np.load(io.BytesIO(git_bytes(OLD_REF, "kaggle/rag_embeddings.npy")))
    assert len(new_t) == 224 and len(old_t) == 220 and new_e.shape[0] == 224 and old_e.shape[0] == 220
    ni = [i for i, t in enumerate(new_t) if t.startswith(NEEDLE)]
    oi = [i for i, t in enumerate(old_t) if t.startswith(NEEDLE)]
    assert ni == [188] and oi == [188], (ni, oi)
    model = SentenceTransformer("intfloat/multilingual-e5-base")

    def q(text):
        v = model.encode([text], convert_to_numpy=True)[0]
        return v / (np.linalg.norm(v) + 1e-10)

    def rank_of(texts, emb, qv, idx):
        s = emb @ qv
        order = np.argsort(s)[::-1]
        return int(np.where(order == idx)[0][0]) + 1, [(int(i), round(float(s[i]), 3)) for i in order[:3]]

    res = {"self_retrieval": {}, "phrasings": []}
    for name, texts, emb in (("old_220", old_t, old_e), ("new_224", new_t, new_e)):
        qv = q("passage: " + texts[188])          # the regen's self-retrieval probe embeds the row text as the query side
        r, top = rank_of(texts, emb, qv, 188)
        res["self_retrieval"][name] = {"rank_of_row_188_for_its_own_text": r, "top3": [(i, s, texts[i][:60]) for i, s in top]}
    for label, text in PHRASINGS:
        qv = q("query: " + text)
        ro, to = rank_of(old_t, old_e, qv, 188)
        rn, tn = rank_of(new_t, new_e, qv, 188)
        res["phrasings"].append({"label": label, "question": text, "rank_old_220": ro, "rank_new_224": rn, "new_top3": [(i, s, new_t[i][:70]) for i, s in tn]})
    res["any_outside_top3_new"] = [p["label"] for p in res["phrasings"] if p["rank_new_224"] > 3]
    res["verdict"] = "FIX NEEDED" if res["any_outside_top3_new"] else "NO FIX: severance is in the top 3 for every phrasing; the self-retrieval miss is an artefact of the probe (a long text as its own query)"
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "severance_rank_2026_11_25.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res["self_retrieval"], ensure_ascii=False, indent=1))
    for p in res["phrasings"]:
        print(f"  old={p['rank_old_220']:>3} new={p['rank_new_224']:>3}  {p['label']:<34} | {p['question'][:80]}")
    print("VERDICT:", res["verdict"])


if __name__ == "__main__":
    main()

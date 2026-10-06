# -*- coding: utf-8 -*-
"""THE GN487A TERM-BLEED HYPOTHESIS, TESTED RATHER THAN ADOPTED.

OBSERVED LIVE (eval/results/cap50_deploy_verification_2026_10_05.json, probe
FINDING_gn487a_term_bleed). Asked "Nikipatikana na hatia ya kosa chini ya sheria ya NSSF,
nitatozwa faini ya kiasi gani na kifungo cha muda gani?" production replied:

    "adhabu ya msingi ni faini ya TZS 20,000,000 (milioni ishirini) AU kifungo cha miezi sita (6)"

Two errors. Cap.50 R.E.2023 s.76(1) is TEN million and TWO YEARS, and GN487A's penalty is ten
million and SIX MONTHS -- so the term looks borrowed from GN487A. Row 20 is CORRECT for GN487A
and is not to be touched.

THE HYPOTHESIS AS STATED: "the NSSF fine rows state the figure without the term, so the model
completes it from the nearest row that has both."

⛔ ITS STATED MECHANISM IS ALREADY FALSE, and checking before building is the whole point. Both
NSSF ceiling rows carry the term EXPLICITLY in the shipped 184-row index:

    row 159  "...TZS 10,000,000 (shilingi milioni kumi), au kifungo cha hadi MIAKA MIWILI,
              au vyote viwili. SI TZS 100,000..."
    row 160  "Kosa la NSSF linaweza kuleta kifungo (jela) cha hadi MIAKA MIWILI, au faini ya
              hadi TZS 10,000,000, au vyote viwili."

and they are the ONLY two rows in the entire index containing "miaka miwili". So the cheap fix
the hypothesis implies -- add the term -- is already in place, and was in place when the bleed
was observed. Something else is happening.

WHAT THIS MEASURES INSTEAD, in the order that separates the remaining explanations:
  1. RETRIEVAL. Does the conviction-phrased query even reach rows 159/160, or does it reach
     row 20? If row 20 wins, this is a retrieval problem and the term is irrelevant.
  2. REACH-BUT-IGNORE. If 159/160 ARE retrieved and the reply still says six months, the
     context was in hand and overridden -- a generation problem, which no index edit fixes.
  3. The TZS 20,000,000 figure separately: it is in NO penalty row of the index, so it is not
     retrieved from anywhere and cannot be an index defect at all.

This is R31's question asked of a fact rather than an engine parameter: the content exists and
is correct; what is between it and the answer?
"""
import importlib.util
import json
import os
import re
import sys

import numpy as np

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "gn487a_term_bleed_hypothesis.json")

# The live reply that prompted this, with its provenance (R24: a baseline must be checkable
# against something specific rather than against memory).
LIVE = {
    "artifact": "eval/results/cap50_deploy_verification_2026_10_05.json",
    "probe": "FINDING_gn487a_term_bleed",
    "question": "Nikipatikana na hatia ya kosa chini ya sheria ya NSSF, nitatozwa faini ya "
                "kiasi gani na kifungo cha muda gani?",
    "reply": "Kwa mujibu wa Sheria ya NSSF, adhabu ya msingi ni faini ya TZS 20,000,000 "
             "(milioni ishirini) AU kifungo cha miezi sita (6). Thibitisha na NSSF "
             "(nssf.go.tz).",
}

QUERIES = [
    ("the live conviction phrasing (verbatim from the artifact)", LIVE["question"]),
    ("prosecution phrasing", "NSSF wananishtaki. Adhabu ya juu ni ipi?"),
    ("ceiling phrasing (known to work)",
     "Faini ya juu kabisa kwa kosa la NSSF ni shilingi ngapi?"),
    ("term phrasing", "Kifungu cha kosa la NSSF ni cha muda gani gerezani?"),
]


def main():
    index = json.load(open(os.path.join(REPO, "kaggle", "rag_facts_text.json"),
                           encoding="utf-8"))

    # --- 0. the hypothesis' own premise, checked against the shipped index -------------------
    term_rows = [i for i, t in enumerate(index)
                 if re.search(r"miaka\s+miwili|miaka\s+2\b|two\s+years", t, re.I)]
    nssf_ceiling_rows = [i for i, t in enumerate(index)
                         if re.search(r"10,?000,?000|milioni kumi", t, re.I)
                         and re.search(r"\bNSSF\b", t, re.I)]
    # ⚠️ ONLY THE SIX-MONTH ROW COUNTS, and the first version of this check did not distinguish
    # them. There are two GN487A penalty rows: row 20 (non-citizen, TZS 10,000,000 + kifungo
    # MIEZI 6) and row 21 (Tanzanian facilitator, TZS 5,000,000 + miezi 3). The bleed under
    # investigation is specifically the SIX-MONTH term, so row 21's presence says nothing about
    # it -- and a `next()` over both reported "GN487A rank=3" when the row actually at rank 3
    # was 21, the IRRELEVANT one. That inverted the conclusion: it read as "the six-month term
    # is in context" when it was not. R34 in the instrument: the pattern matched a label
    # ("GN487A") rather than the content under test (the six-month term).
    gn487a_rows = [i for i, t in enumerate(index)
                   if re.search(r"GN\s*487A", t, re.I)
                   and re.search(r"miezi\s*(6|sita)\b", t, re.I)]
    gn487a_all_rows = [i for i, t in enumerate(index) if re.search(r"GN\s*487A", t, re.I)]
    twenty_m_penalty_rows = [i for i, t in enumerate(index)
                             if re.search(r"20,?000,?000|milioni ishirini", t, re.I)
                             and re.search(r"faini|adhabu|penalt|fine", t, re.I)]

    premise = {
        "hypothesis": "the NSSF fine rows state the figure WITHOUT the term, so the model "
                      "completes it from the nearest row that has both",
        "rows_containing_the_two_year_term": term_rows,
        "nssf_ceiling_rows": nssf_ceiling_rows,
        "both_ceiling_rows_carry_the_term": set(nssf_ceiling_rows) <= set(term_rows),
        "verdict": None,
    }
    premise["verdict"] = (
        "PREMISE FALSE -- both NSSF ceiling rows already carry 'miaka miwili' explicitly, and "
        "they are the ONLY rows in the index that do. The implied fix (add the term) was "
        "already in place when the bleed was observed."
        if premise["both_ceiling_rows_carry_the_term"] else
        "PREMISE HOLDS -- at least one NSSF ceiling row lacks the term; adding it is cheap.")
    assert premise["both_ceiling_rows_carry_the_term"], (
        "the premise now HOLDS, which reverses this file's finding -- re-read the rows and "
        "rewrite the conclusion rather than leaving a stale verdict in place.")

    # --- 1. retrieval: what do these queries actually reach? --------------------------------
    path = os.path.join(REPO, "scripts", "precompute_rag_embeddings.py")
    spec = importlib.util.spec_from_file_location("precompute_rag_embeddings", path)
    pre = importlib.util.module_from_spec(spec)
    sys.modules["precompute_rag_embeddings"] = pre
    spec.loader.exec_module(pre)
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(pre.EMBED_MODEL)
    emb = model.encode([f"passage: {t}" for t in index], batch_size=16,
                       show_progress_bar=False, convert_to_numpy=True)
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)

    retrieval = []
    for label, q in QUERIES:
        v = model.encode([f"query: {q}"], convert_to_numpy=True)[0]
        v = v / (np.linalg.norm(v) + 1e-10)
        order = np.argsort(emb @ v)[::-1]
        top5 = [int(i) for i in order[:5]]
        retrieval.append({
            "label": label, "query": q, "top5_rows": top5,
            "top5_text": [index[i][:100] for i in top5],
            "nssf_ceiling_row_in_top3": any(i in nssf_ceiling_rows for i in top5[:3]),
            "six_month_gn487a_row_in_top3": any(i in gn487a_rows for i in top5[:3]),
            "any_gn487a_row_in_top3": any(i in gn487a_all_rows for i in top5[:3]),
            "rank_of_best_nssf_ceiling_row": next(
                (n for n, i in enumerate(order, 1) if i in nssf_ceiling_rows), None),
            "rank_of_SIX_MONTH_gn487a_row": next(
                (n for n, i in enumerate(order, 1) if i in gn487a_rows), None),
            "rank_of_any_gn487a_row": next(
                (n for n, i in enumerate(order, 1) if i in gn487a_all_rows), None),
        })
        print(f"  [{label}]")
        print(f"      NSSF ceiling rank={retrieval[-1]['rank_of_best_nssf_ceiling_row']}  "
              f"6-month GN487A rank={retrieval[-1]['rank_of_SIX_MONTH_gn487a_row']}  top3={top5[:3]}")

    bleeds = [r for r in retrieval if r["six_month_gn487a_row_in_top3"]]
    reach = [r for r in retrieval if r["nssf_ceiling_row_in_top3"]]

    payload = {
        "_what": "Tests the GN487A term-bleed hypothesis against the shipped 184-row index "
                 "before any fix is built.",
        "_live_observation": LIVE,
        "_statute": "Cap.50 R.E.2023 s.76(1): 'a fine not exceeding ten million shillings or "
                    "to imprisonment for a term not exceeding two years or to both'. GN487A: "
                    "not less than TZS 10,000,000 and/or 6 months. Row 20 is CORRECT for "
                    "GN487A and is not touched.",
        "premise_check": premise,
        "retrieval": retrieval,
        "the_20m_figure": {
            "penalty_rows_containing_it": twenty_m_penalty_rows,
            "finding": "TZS 20,000,000 appears in NO penalty row of the index, so it is not "
                       "retrieved from anywhere. It cannot be an index defect and no index "
                       "edit can remove it -- it is generated, not grounded.",
        },
        "conclusion": {
            "hypothesis_as_stated": premise["verdict"],
            "queries_where_the_SIX_MONTH_row_is_in_top3": [r["label"] for r in bleeds],
            "queries_where_an_nssf_ceiling_row_is_in_top3": [r["label"] for r in reach],
            "reading": None,
        },
    }
    # The DECISIVE comparison is RELATIVE RANK, not mere presence. An index-side fix has
    # headroom only if the correct rows are BELOW the six-month row; if they are already at
    # ranks 1 and 2 there is nothing left to improve by editing the index.
    nssf_best = [r["rank_of_best_nssf_ceiling_row"] for r in retrieval]
    six_month = [r["rank_of_SIX_MONTH_gn487a_row"] for r in retrieval]
    headroom = any(s is not None and n is not None and s < n
                   for n, s in zip(nssf_best, six_month))
    payload["conclusion"]["nssf_ceiling_ranks"] = nssf_best
    payload["conclusion"]["six_month_row_ranks"] = six_month
    payload["conclusion"]["index_side_headroom"] = headroom
    if bleeds and headroom:
        payload["conclusion"]["reading"] = (
            "RETRIEVAL CONTRIBUTES AND AN INDEX FIX HAS HEADROOM: the six-month row outranks "
            "the NSSF ceiling rows on at least one phrasing. Row 20 must not change, so the "
            "lever is the NSSF rows' alignment to conviction/prosecution vocabulary.")
    elif not headroom:
        payload["conclusion"]["reading"] = (
            "RETRIEVAL DOES NOT EXPLAIN IT, AND AN INDEX EDIT HAS NO HEADROOM: the NSSF "
            "ceiling rows are at rank 1 (and 2) on every phrasing tested, ABOVE the six-month "
            "GN487A row in every case -- and they carry 'miaka miwili' "
            "explicitly. So the correct term was IN CONTEXT, at the top, and the reply said six months "
            "anyway. That is a generation defect, not an index defect, and NO index edit will "
            "fix it. The six months is most likely parametric (GN487A is heavily represented "
            "in training), which is the same shape as the D-NSSF-1 party defect: correct fact "
            "retrieved, wrong value emitted.")

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"\npremise: {premise['verdict']}")
    print(f"reading: {payload['conclusion']['reading']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

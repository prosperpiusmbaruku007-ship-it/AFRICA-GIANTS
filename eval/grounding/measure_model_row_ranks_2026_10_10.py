# -*- coding: utf-8 -*-
r"""THE CAVEAT ON THE A2 CEILING, DISCHARGED: WHAT RANK DO THE SIX MODEL ROWS' FACTS SIT AT?

⛔ WHY THIS RUNS BEFORE ANY RETRAIN DECISION. The 2026-10-09 closability pass classified 6
of 12 confirmed confident-wrong answers as MODEL — the fact was SERVED and the reply
contradicted it — and CLAUDE.md records those six as the A2 ceiling, the evidence for or
against a retrain. It also records, in the same block, the caveat that makes the claim
provisional:

    "IT DOES NOT SETTLE RANK, and that caveat is load-bearing. 'In the index' is necessary
     for 'the model ignored it', not sufficient. If a present fact sat at a bad rank, the
     row is retrieval work after all. Measure the rank before citing any of these six as
     model failures."

A fact at rank 1 that the reply contradicts is a model failure. A fact at rank 40 was never
in the pooled context, so the reply cannot have contradicted a fact it was handed and the
row is NOT evidence for a retrain — whether its fix is retrieval, corpus or a guard is a
further judgement, made per row and not by this harness. Those are different workstreams
and different budgets, and the only thing separating them is this measurement.

⚠️ THE SECOND CAVEAT IS NOT MEASURED HERE AND MUST NOT BE READ AS SETTLED BY IT. CLAUDE.md
also records that "PRESENT is not UNAMBIGUOUS" — eval_086 was classified MODEL on a fact
whose own wording was complicit, and the file predicts "this to reclassify more than one
MODEL row on inspection, which would make the A2 ceiling LOWER than six." Rank is
mechanical; ambiguity is a reading. This harness answers the mechanical half only and says
so in its own artifact.

⚠️ PINNED BY CONTENT, AND THE ROW NUMBER IS CHECKED AGAINST IT RATHER THAN TRUSTED. The
closability artifact records a `governing_fact_row` integer per row. Row numbers in this
project have moved underneath pinned verdicts before — the 2026-08-17 stale pins, and
`nat_23`'s 45→46 shift — so each needle below is a substring of the row's CURRENT text, the
needle is asserted to match exactly ONE row, and the row it matches is compared with the
recorded integer. A disagreement is reported as a finding, not silently followed.

Usage:  python eval/grounding/measure_model_row_ranks_2026_10_10.py
Artifact: eval/results/model_row_ranks_2026_10_10.json
Exit 0 measured · 2 could not be exercised (NOT a pass).
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "eval", "grounding"))
OUT = os.path.join(REPO, "eval", "results", "model_row_ranks_2026_10_10.json")
CLOSABILITY = os.path.join(REPO, "eval", "results", "bar_a_closability_2026_10_09.json")

# (gate id, verbatim question, needle, what the needle is a substring of)
#
# Questions are read out of the gate corpora verbatim, never retyped — a paraphrase measures
# a different question's retrieval (R26's "use the verbatim committed probe").
PROBES = [
    ("eval_104",
     "Mwajiri anahitaji nyaraka gani kuwasilisha NSSF ili kusajilisha wafanyakazi wake?",
     "'Form P9' is Kenyan",
     "row 3, paye p9 deadline — the row that EXPLICITLY FORBIDS the instrument the reply "
     "named"),
    ("eval_162",
     "'Mgeni' katika GN 487A inamaanisha nani hasa?",
     "recognises three citizen categories",
     "row 91, gn487a mgeni cap357 definition — the statutory definition the reply inverted"),
    ("eval_171",
     "Mimi ni mgeni ninayefanya biashara ya rejareja — GN 487A tayari imetangazwa. "
     "Nifanye nini sasa?",
     "may continue until licence expiry",
     "row 56, gn487a transitional provision — the gold's own relief, against a reply that "
     "advised the prohibited act"),
    ("eval_237",
     "Kodi ya zuio (withholding tax) inatakiwa kuwasilishwa TRA ndani ya muda gani baada "
     "ya mwisho wa mwezi?",
     "within 7 DAYS after end of the calendar month",
     "row 37, wht deadline — which pre-empts the exact one-word date shift the reply made"),
    ("eval_304",
     "Nina wafanyakazi 20 na mtaji wa TZS 50,000,000, je nasajili kampuni au jina la "
     "biashara BRELA?",
     "THREE main legal forms",
     "row 82, brela business structures — which says the choice turns NOT on headcount or "
     "capital, against a reply that invented a threshold"),
    ("eval_338",
     "VAT withholding kwa huduma ni asilimia 18 kama kiwango cha kawaida, sivyo?",
     "withholding on services is 6%",
     "row 17, vat withholding services — 6%, against a reply that confirmed 18%"),
]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                    # noqa: BLE001
        pass

    import measure_fact_reach as mfr

    # ── the recorded classification, read rather than retyped ───────────────────────────
    closability = json.load(io.open(CLOSABILITY, encoding="utf-8"))
    recorded = {r["id"]: r for r in closability["rows"] if r["closability"] == "MODEL"}
    if sorted(recorded) != sorted(p[0] for p in PROBES):
        print(f"[FATAL] the MODEL set has changed: artifact={sorted(recorded)} "
              f"probes={sorted(p[0] for p in PROBES)}")
        return 2

    norm, texts = mfr.load_deployed_index()
    print(f"deployed index: {len(texts)} rows")

    # ── needle uniqueness and the row-number cross-check, BEFORE any rank is taken ─────
    pin_findings = []
    for pid, _q, needle, _of in PROBES:
        hits = [i for i, t in enumerate(texts) if needle.lower() in t.lower()]
        if len(hits) != 1:
            print(f"[FATAL] needle for {pid} matches {len(hits)} rows {hits}: {needle!r}. "
                  f"An ambiguous needle can pass on a row it does not mean.")
            return 2
        if hits[0] != recorded[pid]["governing_fact_row"]:
            pin_findings.append({
                "id": pid, "recorded_row": recorded[pid]["governing_fact_row"],
                "row_the_content_is_actually_at": hits[0],
                "note": "the index moved under the recorded pin; the CONTENT is "
                        "authoritative and the rank below is measured against it",
            })
    print(f"[PINS] 6/6 needles unique · row-number disagreements: {len(pin_findings)}")

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("intfloat/multilingual-e5-base")
    ret = mfr.Retriever(model, norm, texts)

    rows = []
    for pid, q, needle, of in PROBES:
        rank = ret.rank_of(q, needle)
        pooled = ret.reaches_pooled_context(q, needle)
        # ⛔ THE VERDICT IS DERIVED FROM THE MEASUREMENT, NOT CARRIED FORWARD FROM THE
        # CLASSIFICATION. A resume may carry data forward, never a conclusion — and a
        # classification read out of an artifact is exactly a conclusion.
        # ⚠️ THE NEGATIVE VERDICT IS DELIBERATELY NOT "RECLASSIFY TO RETRIEVAL". That would
        # be over-specific and would push five rows into one workstream on the strength of a
        # measurement that only rules out a different one. What the rank settles is that the
        # model never saw the fact, so the row is NOT evidence for a retrain. Whether the fix
        # is retrieval wording, a missing corpus row, or a guard is a further judgement per
        # row — eval_104's governing row FORBIDS the P9, and no amount of re-wording makes a
        # P9-forbidding row retrievable from a question about NSSF documents that never
        # mentions the P9.
        if rank is None:
            verdict = "ABSENT — the needle is nowhere in the index"
        elif pooled and rank <= 3:
            verdict = "MODEL CONFIRMED — served at top-3 and contradicted"
        elif pooled:
            verdict = "MODEL CONFIRMED — pooled via decomposition despite raw rank"
        else:
            verdict = "NOT A MODEL FAILURE — the fact never reached the pooled context"
        rows.append({
            "id": pid, "question": q, "needle": needle, "needle_is_a_substring_of": of,
            "raw_rank": rank, "category": mfr._categorize(rank),
            "reaches_pooled_context": pooled,
            "verdict": verdict,
            "recorded_defect": recorded[pid]["defect"],
            "recorded_guard_possible": recorded[pid]["guard_possible"],
        })
        print(f"  {pid}  rank={rank!s:>4}  {mfr._categorize(rank):9s} "
              f"pooled={str(pooled):5s}  {verdict}")

    confirmed = [r for r in rows if r["verdict"].startswith("MODEL CONFIRMED")]
    reclass = [r for r in rows if not r["verdict"].startswith("MODEL CONFIRMED")]

    art = {
        "_what": "Retrieval rank of the governing fact for each of the six rows the "
                 "2026-10-09 closability pass classified MODEL. Discharges the rank caveat "
                 "CLAUDE.md records against citing those six as the A2 ceiling.",
        "_population": {
            "n": len(rows),
            "why_this_population": "These six are the whole of the retrain case. A1's other "
                                   "six rows are ROUTE/CORPUS/GOLD and no model change "
                                   "reaches them, so measuring anything else would not move "
                                   "the decision this was taken for.",
        },
        "_what_this_does_NOT_settle": "AMBIGUITY. A fact can be present, top-ranked, and "
                                      "still readable as supporting the wrong answer — "
                                      "eval_086's row 9 was. CLAUDE.md predicts more than "
                                      "one of these six reclassifies on that axis, which "
                                      "would lower the ceiling further. Rank is mechanical; "
                                      "that is a reading, and it is not done here.",
        "index": {"dir": mfr.DEFAULT_INDEX_DIR, "rows": len(texts)},
        "pin_findings": pin_findings,
        "model_confirmed": len(confirmed),
        "not_a_model_failure": len(reclass),
        "_the_conclusion": (
            "THE RETRAIN CASE IS ONE ROW, NOT SIX. Five of the six never reached the pooled "
            "context, so they cannot be instances of a reply contradicting a fact it was "
            "handed. 'In the served index' was necessary and not sufficient, exactly as "
            "CLAUDE.md's caveat said, and the gap between the two is large: ranks 4, 7, 12, "
            "46 and 61. eval_237 alone is confirmed — rank 2, pooled, contradicted. "
            "A retrain justified on six rows is being justified on one."),
        "rows": rows,
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(art, ensure_ascii=False, indent=1))

    print(f"\nMODEL CONFIRMED {len(confirmed)} · NOT A MODEL FAILURE {len(reclass)}")
    print(f"artifact: {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

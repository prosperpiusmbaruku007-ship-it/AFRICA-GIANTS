# -*- coding: utf-8 -*-
"""BUCKET-A RECOUNT: what the extended-078 failures actually are, re-derived from the committed
adjudication rather than recalled.

WHY. A figure of "8 bucket-A failures, 5 of them compute questions an engine already owns" drove
a work plan this session. It could not be re-derived from any committed artifact, and two of the
rows attributed to it turned out to be something else on inspection (ext_53 is a PASS; ext_51 is
the row that got its attribution RIGHT). R18's rule about provisional numbers applies: anything
scoped on a figure whose harness nobody can inspect is provisional too. So the census is rebuilt
from eval/results/extended_078_adjudication_2026_09_23.json, which is committed, per-row, and
carries both a verdict and a cause.

TWO LAYERS, KEPT SEPARATE ON PURPOSE.
  * `by_verdict` / `by_cause` are the ADJUDICATOR'S OWN fields, copied, not reinterpreted.
  * `remediation_class` is THIS FILE'S classification of what would have to change to fix each
    row. It is labelled as such because it is a judgement, and because one of its rows disagrees
    with the adjudicator's recorded cause -- ext_56, filed `model`, is proven this session to be
    a routing veto (eval/results/confirmation_tag_veto_2026_09_29.json). Recording the
    disagreement rather than silently overwriting the field is the point.

Usage:  python eval/results/bucket_a_recount_2026_09_29.py
"""
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "eval", "results", "extended_078_adjudication_2026_09_23.json")
OUT = os.path.join(REPO, "eval", "results", "bucket_a_recount_2026_09_29.json")

# What would have to CHANGE to fix each non-PASS row. My classification, not the adjudicator's.
# `route` = the engine exists and already answers correctly; only reachability is broken.
# `premise` = the reply asserts no figure of its own; it assents to a claim made in the QUESTION.
# `domain_unbuilt` = a coverage gap; there is no fact to retrieve because we never authored one.
# `fact_quality` = a locked fact is wrong, unverified, or a hedge the model overrode.
# `extraction` = routing worked, the engine was reachable, the input read failed.
# `generation` = the fact was available and the model still said something else.
REMEDIATION = {
    "route": ["ext_01", "ext_03", "ext_05", "ext_56"],
    "premise": ["ext_54", "ext_55", "ext_62"],
    "domain_unbuilt": ["ext_33", "ext_34", "ext_35", "ext_36", "ext_39", "ext_40",
                       "ext_42", "ext_43", "ext_44", "ext_46"],
    "fact_quality": ["ext_69", "ext_71", "ext_72", "ext_73", "ext_76"],
    "extraction": ["ext_58", "ext_59"],
    "generation": ["ext_08", "ext_09", "ext_14", "ext_22", "ext_25", "ext_27", "ext_29",
                   "ext_31", "ext_32", "ext_67"],
}
# Rows where my remediation class DISAGREES with the adjudicator's recorded `cause`. Listed, not
# resolved, so the disagreement is visible to whoever reads either field next.
DISAGREEMENTS = {
    "ext_56": "adjudication says cause=model. Proven routing this session: _THRESHOLD_ASK_VETO's "
              "`sivyo?` limb sends it to the fact path, and vat_registration(110_000_000, "
              "'six_month') returns the correct refutation. The model only had to answer "
              "because no engine ran.",
}


def main():
    rows = json.load(open(SRC, encoding="utf-8"))["rows"]
    assert len(rows) == 78, f"expected 78 adjudicated rows, got {len(rows)}"

    by_verdict = collections.Counter(r.get("verdict") for r in rows)
    non_pass = [r for r in rows if r.get("verdict") not in ("PASS", "PASS_BY_OUTCOME")]
    by_cause = collections.Counter(str(r.get("cause")) for r in non_pass)
    wrong = [r for r in rows if r.get("verdict") == "WRONG"]

    classified = {k: v for k, v in REMEDIATION.items()}
    all_classified = [i for v in classified.values() for i in v]
    wrong_ids = [r["id"] for r in wrong]
    # R20: this must be able to fail. If a row is classified twice, or a WRONG row is left out,
    # the census is incomplete and saying so is the whole value of running it.
    dupes = [i for i, c in collections.Counter(all_classified).items() if c > 1]
    missing = sorted(set(wrong_ids) - set(all_classified))
    extra = sorted(set(all_classified) - set(wrong_ids))
    assert not dupes, f"rows classified more than once: {dupes}"
    assert not missing, f"WRONG rows with no remediation class: {missing}"

    artifact = {
        "recounted": "2026-09-29",
        "harness": "eval/results/bucket_a_recount_2026_09_29.py",
        "source": "eval/results/extended_078_adjudication_2026_09_23.json",
        "why": ("A figure of '8 bucket-A failures, 5 of them compute questions an engine already "
                "owns' drove a work plan and could not be re-derived from any committed "
                "artifact. Two rows attributed to it are PASSes. Rebuilt from the committed "
                "per-row adjudication."),
        "adjudicators_own_fields": {
            "by_verdict": dict(by_verdict),
            "by_cause_among_non_pass": dict(by_cause),
        },
        "this_files_classification": {
            "note": ("remediation_class is a judgement about what would have to CHANGE, made by "
                     "this file and not by the adjudicator. Kept separate from `cause` above."),
            "counts": {k: len(v) for k, v in classified.items()},
            "rows": classified,
        },
        "disagreements_with_recorded_cause": DISAGREEMENTS,
        "rows_classified_but_not_WRONG": extra,
        "no_eight_anywhere": (
            "No grouping of this artifact yields 8. The nearest real figures are CLAUDE.md's "
            "'5 of 7 reaching-and-failing rows had no corpus defect behind them' (2026-09-24) "
            "and PROGRESS.md's '5 of 7 WRONG ... on the fact path'. Both are 5-of-7, and the "
            "first one's MEANING is the opposite of the plan it was cited for: it says a "
            "corpus/content fix does NOT close those rows."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, ensure_ascii=False, indent=2)

    print("verdicts over 78:", dict(by_verdict))
    print("causes among non-PASS:", dict(by_cause))
    print()
    print("WRONG rows by what would have to change:")
    for k, v in sorted(classified.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(v):>3}  {k:16} {', '.join(v)}")
    print()
    print(f"[saved] {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

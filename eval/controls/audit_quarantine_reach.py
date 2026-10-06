# -*- coding: utf-8 -*-
"""DID THE QUARANTINES ACTUALLY REMOVE ANYTHING FROM THE TRAINING SET?

WHY THIS EXISTS. The D-FIDELITY-7 pre-wiring sweep (eval/fidelity/price_threshold_guard_before_
wiring.py) flagged seven rows in datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_011.jsonl
and _012.jsonl asserting the fabricated TZS 11M EFD threshold. Five of their questions are
VERBATIM in datasets/tier1a/rejected/efd_threshold_fabrication_quarantine_2026_08_29.jsonl -- they
were adjudicated, recorded, and quarantined five and a half weeks ago, AND THEY ARE STILL IN THE
CORPUS.

THE SHAPE IS R26's, AND IT IS THE HARDER HALF OF R26: not "does the control fire?" but "WHERE does
it fire, and is that where the thing it protects actually lives?" The 2026-08-29 quarantine fired
correctly. It removed rows from `cleaned_pairs/`. The file that feeds training is
`datasets/tier1a/sft/train_sft.jsonl`, generated from `sft_shaped_pairs/` -- neither of which it
touched. So the quarantine record is accurate, the removal happened, a test would find the rows
absent from the directory it was pointed at, and the defect shipped anyway.

Exactly the two inert controls of 2026-08-24: `scan_for_keys.py` scanned correctly and was handed
no files; `chike/retrieval.py`'s index contract raises correctly and production never imports it.
Nothing is wrong with the logic in any of the three.

WHAT IT MEASURES. For every quarantine record in datasets/tier1a/rejected/*.jsonl, whether each
quarantined row's CONTENT still appears in any live corpus. Matching is on the ANSWER BODY, not
the question: a question may legitimately recur (a corrected pair answers the same question), so
matching on the question would report a false survival for every row that was correctly REPLACED.
Only a surviving answer body means the defective text is still there.

  LIVE CORPORA, in dependency order -- each generated from the one before it:
    datasets/tier1a/cleaned_pairs/       authored pairs            (the quarantines' target)
    datasets/tier1a/sft_shaped_pairs/    shaped copies
    datasets/tier1a/sft/                 train_sft.jsonl / val_sft.jsonl  <- WHAT TRAINS
    datasets/tier1a/eval_set/            held-out
    datasets/tier1a/adversarial/         refusal probes

A row surviving in a LATER stage than the one a quarantine cleaned is the defect class: the
quarantine was applied upstream of where the bytes actually are.

WHAT THIS CANNOT SHOW. It cannot tell a surviving row from a row DELIBERATELY retained -- an
adversarial pair that quotes the fabrication in order to refuse it is correct prose and must stay.
Polarity is not checked here; every survivor is printed with its body so it can be read (R26's
second half: a flag is a candidate, six of the first eight adverse verdicts in the 2026-08-24
audit were bad specimens). The quarantine FILES themselves are excluded from the live set -- a row
present in its own quarantine record is the record working.

R18: committed before the write-up that cites it.
Artifact: eval/results/quarantine_reach_audit_2026_10_06.json

Usage:  python eval/controls/audit_quarantine_reach.py
Exit 0 always -- this is a measurement, not a gate.
"""
import collections
import glob
import json
import os
import re
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "eval", "results", "quarantine_reach_audit_2026_10_06.json")

LIVE_DIRS = [
    ("cleaned_pairs", "datasets/tier1a/cleaned_pairs"),
    ("sft_shaped_pairs", "datasets/tier1a/sft_shaped_pairs"),
    ("sft_EXPORTED_TRAINING", "datasets/tier1a/sft"),
    ("eval_set", "datasets/tier1a/eval_set"),
    ("adversarial", "datasets/tier1a/adversarial"),
]
BODY_KEYS = ("output", "answer_sw", "response")
QKEYS = ("instruction", "question_sw", "question")


def norm(s):
    """Whitespace- and punctuation-dash-insensitive. The corpora carry mojibake em-dashes
    (cp1252 round-trips) and a byte-exact comparison would miss every row that has one."""
    s = re.sub(r"[—–�’‘“”-]+", " ", s or "")
    return " ".join(s.split()).lower()


def rows_of(path):
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield n, json.loads(line)
            except Exception:
                continue


def _unwrap(obj):
    """⛔ THE QUARANTINE RECORDS DO NOT SHARE A SHAPE, AND THE FIRST DRAFT OF THIS HARNESS
    REPORTED `0/0 survive` FOR FOUR OF THEM -- which reads exactly like a clean result.

    Two shapes are in use. The 2026-08 records are flat (`instruction`/`output` + `_quarantine`).
    Every record from 2026-09-02 onward nests the pair under a `row` key alongside provenance
    (`source_file`, `defect_class`, `row_sha256`). A reader that only looks at top level finds no
    body in the newer shape, counts zero rows with a body, and prints `0/0` -- R20's fourth
    arrival point (a fixture whose composition cannot exercise the category it claims to watch),
    in the auditor rather than in the thing audited. The four affected records include
    YESTERDAY'S, so the hole was in the newest evidence first.
    """
    if isinstance(obj.get("row"), dict):
        return obj["row"]
    return obj


def body_of(obj):
    obj = _unwrap(obj)
    return next((obj[k] for k in BODY_KEYS
                 if isinstance(obj.get(k), str) and obj[k].strip()), "")


def q_of(obj):
    obj = _unwrap(obj)
    return next((obj[k] for k in QKEYS
                 if isinstance(obj.get(k), str) and obj[k].strip()), "")


def main():
    # --- index every live corpus row by normalised ANSWER BODY ------------------------------
    live = collections.defaultdict(list)       # norm(body) -> [(stage, locator, question)]
    live_by_q = collections.defaultdict(list)  # norm(question) -> [(stage, locator, body)]
    live_rows = 0
    for stage, rel in LIVE_DIRS:
        for path in sorted(glob.glob(os.path.join(REPO, rel, "*.jsonl"))):
            loc_base = os.path.relpath(path, REPO).replace(os.sep, "/")
            for n, obj in rows_of(path):
                body = body_of(obj)
                if not body:
                    continue
                live_rows += 1
                live[norm(body)].append((stage, f"{loc_base}:{n}", q_of(obj)[:120]))
                if q_of(obj):
                    live_by_q[norm(q_of(obj))].append((stage, f"{loc_base}:{n}", body))

    # --- walk every quarantine record -------------------------------------------------------
    quarantines, survivors, edited_in_place = [], [], []
    q_rows_total = 0
    for path in sorted(glob.glob(os.path.join(
            REPO, "datasets", "tier1a", "rejected", "*.jsonl"))):
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        rec = {"record": rel, "rows": 0, "with_body": 0, "surviving": 0,
               "edited_in_place": 0, "stages": {}}
        for n, obj in rows_of(path):
            rec["rows"] += 1
            q_rows_total += 1
            body = body_of(obj)
            if not body:
                continue                       # a metadata/header row, not a quarantined pair
            rec["with_body"] += 1
            hits = live.get(norm(body)) or []
            if hits:
                rec["surviving"] += 1
                for stage, loc, question in hits:
                    rec["stages"][stage] = rec["stages"].get(stage, 0) + 1
                    survivors.append({
                        "quarantine_record": rel, "quarantine_line": n,
                        "survives_in_stage": stage, "survives_at": loc,
                        "question": question,
                        "body": body[:420],
                    })
                continue
            # ⛔ THE THIRD OUTCOME, AND IT IS THE ONE THAT MATTERS MOST HERE. A quarantined body
            # that is absent while its QUESTION is still live was not removed -- it was EDITED IN
            # PLACE. The quarantine record then holds the PRE-EDIT text, so a body match cannot
            # see it, and the audit would report the row as cleanly gone.
            #
            # That is R25's containment shape: the edit can repair the SENTENCE a sweep keys on
            # and leave the same claim standing in the body prose. Measured here on
            # efd_threshold_fabrication_quarantine_2026_08_29: the quarantined opener
            # "EFD inahitajika kwa biashara zenye mauzo ya TZS milioni 11 au zaidi" became
            # "...kulingana na kizingiti cha mauzo kilichowekwa na TRA", while the SAME ROW still
            # reads "haujafika kizingiti cha TZS 11M" three sentences later.
            #
            # It also explains a discrepancy that looked like two different defects: a sweep for
            # the spelled-out "milioni 11" found 3 rows and D-FIDELITY-7 found 7. The repair had
            # deleted the words and left the digits.
            qn = norm(q_of(obj))
            if qn and qn in live_by_q:
                rec["edited_in_place"] += 1
                for stage, loc, newbody in live_by_q[qn]:
                    edited_in_place.append({
                        "quarantine_record": rel, "quarantine_line": n,
                        "stage": stage, "at": loc,
                        "question": q_of(obj)[:140],
                        "quarantined_body": body[:360],
                        "live_body_now": newbody[:360],
                    })
        quarantines.append(rec)

    # R20 / the hole this harness shipped with: a record with a shape the reader does not
    # understand yields zero rows-with-body and prints "0/0 survive", which reads as clean.
    # Asserted so a future record in a third shape fails loudly instead of auditing nothing.
    empty = [r["record"] for r in quarantines if r["rows"] and not r["with_body"]]
    assert not empty, (
        f"{len(empty)} quarantine record(s) yielded NO readable pair body, so nothing in them "
        f"was audited and the report would read as clean: {empty}. Add their shape to _unwrap().")

    # R20: a matcher that normalises everything to nothing, or indexes no corpus, reports zero
    # survivors -- indistinguishable from clean. Both halves asserted.
    assert live_rows > 3000, f"only {live_rows} live corpus rows indexed"
    assert q_rows_total > 100, f"only {q_rows_total} quarantined rows read"
    assert len(live) > 1000, "normalisation collapsed the live corpus into too few keys"

    by_stage = collections.Counter(s["survives_in_stage"] for s in survivors)
    # The load-bearing subset: surviving in a stage DOWNSTREAM of the authored corpus, i.e. the
    # quarantine cleaned upstream of where the bytes that train the model actually live.
    in_training = [s for s in survivors
                   if s["survives_in_stage"] in ("sft_EXPORTED_TRAINING", "sft_shaped_pairs")]
    # Distinct quarantined rows (a row can survive in several stages at once).
    distinct = {(s["quarantine_record"], s["quarantine_line"]) for s in survivors}

    artifact = {
        "measured": str(date.today()),
        "harness": "eval/controls/audit_quarantine_reach.py",
        "question": ("For every quarantine this project has performed, does the quarantined TEXT "
                     "still exist in a live corpus -- and specifically in the exported SFT files "
                     "that actually train the model?"),
        "why_this_population": (
            "Every record in datasets/tier1a/rejected/ against every row of every live corpus. "
            "The quarantines are the only population where an adjudication was already made, so "
            "a survivor is a KNOWN defect still present rather than a new candidate -- no "
            "re-adjudication of the fact is needed, only of whether the row is a deliberate "
            "adversarial retention (R22: this is the population the question is about)."),
        "matched_on": ("the ANSWER BODY, not the question. A question legitimately recurs when a "
                       "defective pair is REPLACED by a corrected one; matching questions would "
                       "report a false survival for every correct replacement."),
        "what_this_cannot_show": (
            "A survivor may be a DELIBERATE adversarial retention -- a pair that quotes a "
            "fabrication in order to refuse it is correct prose. Polarity is not scored here; "
            "every survivor is printed with its body to be read individually (R26)."),
        "the_finding_that_prompted_it": (
            "D-FIDELITY-7's pre-wiring sweep flagged 7 rows asserting the fabricated TZS 11M EFD "
            "threshold in sft_shaped_pairs/batch_011 and _012. Five of their questions are "
            "verbatim in efd_threshold_fabrication_quarantine_2026_08_29.jsonl. The quarantine "
            "removed them from cleaned_pairs/ and never touched sft_shaped_pairs/ or sft/."),
        "totals": {
            "live_corpus_rows_indexed": live_rows,
            "quarantined_rows_read": q_rows_total,
            "distinct_quarantined_rows_still_live": len(distinct),
            "survivor_locations": len(survivors),
            "by_stage": dict(by_stage),
            "survivors_in_training_stages": len(in_training),
            "edited_in_place_not_removed": len(edited_in_place),
        },
        "the_third_outcome": (
            "A quarantined body that is ABSENT while its QUESTION is still live was EDITED IN "
            "PLACE, not removed. The record then holds the pre-edit text, so a body match reports "
            "the row as cleanly gone. R25's containment shape: the edit can repair the sentence a "
            "sweep keys on and leave the same claim standing later in the same row. It is also "
            "why a sweep for the spelled-out 'milioni 11' found 3 rows while D-FIDELITY-7 found "
            "7 -- the repair deleted the words and left the digits."),
        "per_quarantine_record": quarantines,
        "survivors": survivors,
        "edited_in_place": edited_in_place,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, ensure_ascii=False, indent=2)

    t = artifact["totals"]
    print(f"live corpus rows indexed:                 {t['live_corpus_rows_indexed']}")
    print(f"quarantined rows read:                    {t['quarantined_rows_read']}")
    print(f"DISTINCT quarantined rows STILL LIVE:     "
          f"{t['distinct_quarantined_rows_still_live']}")
    print(f"survivor locations:                       {t['survivor_locations']}")
    print(f"  by stage: {t['by_stage']}")
    print(f"EDITED IN PLACE (body gone, question live): {t['edited_in_place_not_removed']}")
    print()
    for rec in quarantines:
        mark = "⛔" if rec["surviving"] else ("~ " if rec["edited_in_place"] else "  ")
        print(f" {mark} {rec['surviving']:3d} survive / {rec['edited_in_place']:3d} edited "
              f"of {rec['with_body']:3d}  {os.path.basename(rec['record'])}  "
              f"{rec['stages'] or ''}")
    print(f"\n[saved] {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

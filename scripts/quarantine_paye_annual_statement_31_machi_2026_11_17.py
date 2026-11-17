# -*- coding: utf-8 -*-
"""QUARANTINE THE PAIR THAT STATES THE ANNUAL PAYE STATEMENT IS DUE "31 MACHI" (founder-approved 2026-11-17, stage 4 item 5: "read, verify, quarantine if wrong"; every copy including datasets/tier1a/sft/ -- R36).

THE DEFECT. `tier1a_paye_008_20260603` answers "Mwajiri anatoa taarifa ya kila mwaka ya PAYE TRA lini?" with "Taarifa ya Mwaka ya PAYE (Annual PAYE Statement) ifikapo tarehe 31 Machi ya mwaka unaofuata".
  * The only annual employer instrument with a date in the Income Tax Act Cap.332 R.E.2023 is the withholding certificate, served on the employee by 30 JANUARY (s.110(3)(b): "shall be served by 30th January after the end of
    the year"; locked fact paye_p9_deadline). Read directly 2026-11-17 in data/source_documents/tra/income_tax_act_cap332_re2023.pdf (R.E. 2023, edition asserted in the manifest).
  * The pair's cited page (tra.go.tz/page/pay-as-you-earn-paye, source_url on the row) is not the source of "31 Machi": the cached TRA PAYE pages contain no 31 March, 30 January or "taarifa ya mwaka" at all (read 2026-11-17).
  * The same claim -- P9 / the annual PAYE form due 31 March -- is ALREADY quarantined 30+ times as confirmed wrong (rejected/tier2_confirmed_wrong_quarantine_2026_08_31.jsonl, precondition_confirmed_wrong_quarantine_2026_10_08.jsonl);
    this row is the copy that survived because its question does not say "P9".
R37 (read before removing, in the OPPOSITE direction): the answer is a bare assertion of a date the Act does not state for any annual PAYE statement; it does not deny 31 March anywhere and contains no correct limb. Removed whole.
SCOPE (R36 -- the quarantine must reach the bytes that train): REMOVED from cleaned_pairs/batch_002_cleaned.jsonl:8, cleaned_pairs/batch_002a_cleaned.jsonl:8, sft/train_sft.jsonl:2238 and sft/val_sft.jsonl:417;
MARKED, NOT REMOVED: raw_sources/raw_pairs_batch_002.jsonl:8 and raw_pairs_batch_002a.jsonl:8 (pre-cleaning input, feed no training).

    python scripts/quarantine_paye_annual_statement_31_machi_2026_11_17.py [--dry-run]
"""
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUARANTINE = os.path.join(REPO, "datasets", "tier1a", "rejected", "paye_annual_statement_31_machi_quarantine_2026_11_17.jsonl")
OUT = os.path.join(REPO, "eval", "results", "paye_annual_statement_31_machi_quarantine_2026_11_17.json")
DEFECT = "PAYE_ANNUAL_STATEMENT_DATE_31_MACHI"
CORRECT = ("The Income Tax Act Cap.332 R.E.2023 s.110(3)(b) has the employer serve the annual withholding certificate by 30 January after the end of the year (locked fact paye_p9_deadline); "
           "it states no 31 March for any annual PAYE statement.")
T = "datasets/tier1a/"
HEAD = "Mwajiri anatoa taarifa ya kila mwaka ya PAYE TRA lini?"
SENTENCE = "ifikapo tarehe 31 Machi ya mwaka unaofuata"
ROWS = [
    (T + "cleaned_pairs/batch_002_cleaned.jsonl", 8, "remove"),
    (T + "cleaned_pairs/batch_002a_cleaned.jsonl", 8, "remove"),
    (T + "sft/train_sft.jsonl", 2238, "remove"),
    (T + "sft/val_sft.jsonl", 417, "remove"),
    (T + "raw_sources/raw_pairs_batch_002.jsonl", 8, "mark"),
    (T + "raw_sources/raw_pairs_batch_002a.jsonl", 8, "mark"),
]


def _head(o):
    return o.get("instruction") or o.get("question_sw") or ""


def main():
    dry = "--dry-run" in sys.argv
    files = {}
    for f, *_ in ROWS:
        files.setdefault(f, io.open(os.path.join(REPO, f), encoding="utf-8", newline="").read().splitlines())
    already = set()
    if os.path.exists(QUARANTINE):
        for ql in io.open(QUARANTINE, encoding="utf-8"):
            if ql.strip():
                already.add((json.loads(ql)["source_file"], json.loads(ql)["source_line_at_quarantine"]))
    planned = []
    for f, ln, action in ROWS:
        if (f, ln) in already:
            continue
        raw = files[f][ln - 1] if ln <= len(files[f]) else ""
        o = json.loads(raw) if raw.strip() else {}
        if not _head(o).startswith(HEAD) or SENTENCE not in raw:
            print(f"[ABORT] {f}:{ln} no longer holds the adjudicated row (head {_head(o)[:60]!r}). A line number pins a POSITION; re-adjudicate by content.")
            return 1
        planned.append((f, ln, action, hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode()).hexdigest(), o))
    print(f"planned {len(planned)} rows ({sum(1 for p in planned if p[2] == 'remove')} remove, {sum(1 for p in planned if p[2] == 'mark')} mark-only); already recorded {len(already)}")
    if dry or not planned:
        return 0
    os.makedirs(os.path.dirname(QUARANTINE), exist_ok=True)
    with io.open(QUARANTINE, "a", encoding="utf-8", newline="\n") as fh:               # record FIRST
        for f, ln, action, h, o in planned:
            fh.write(json.dumps({"source_file": f, "source_line_at_quarantine": ln, "action": "removed_from_live_corpus" if action == "remove" else "marked_raw_not_removed",
                                 "defect_class": DEFECT, "reason": f"states the annual PAYE statement is due 31 March: '...{SENTENCE}...'. {CORRECT}",
                                 "adjudicated": "individually, by reading the full row and the Act text (2026-11-17) -- not matched by pattern", "row_sha256": h, "row": o}, ensure_ascii=False) + "\n")
    removed = {}
    for f, ln, action, *_ in planned:
        if action == "remove":
            removed.setdefault(f, set()).add(ln)
    for f, lns in removed.items():                                                    # THEN the live files
        kept = [l for i, l in enumerate(files[f], 1) if i not in lns]
        with io.open(os.path.join(REPO, f), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(kept) + "\n")
    for f in removed:
        lines = io.open(os.path.join(REPO, f), encoding="utf-8").read().splitlines()
        assert not any(HEAD in l and SENTENCE in l for l in lines), f"the asserting row survives in {f}"
    rep = {"measured": "2026-11-17", "defect_class": DEFECT, "rows_removed_from_live": sum(len(v) for v in removed.values()), "rows_marked_raw": sum(1 for p in planned if p[2] == "mark"),
           "lines_removed": {k: sorted(v) for k, v in removed.items()}, "quarantine_file": os.path.relpath(QUARANTINE, REPO).replace("\\", "/")}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=2))
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

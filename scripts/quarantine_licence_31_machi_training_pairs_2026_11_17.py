# -*- coding: utf-8 -*-
"""QUARANTINE THE TRAINING PAIRS THAT STATE A BUSINESS LICENCE IS RENEWED BY "31 MACHI" (founder's decision, 2026-11-17: "mark, don't delete", every copy including datasets/tier1a/sft/ -- R36).

THE DEFECT. Every business licence in Tanzania expires on 30 JUNE (locked fact business_licence_expiry_30_june: Business Licensing Act s.3(4) as substituted by Finance Act 2014 s.5). Four distinct authored pairs say 31 March:
  batch_002 #145 "...lazima ihuishwe kila mwaka, kawaida ifikapo tarehe 31 Machi"            batch_005 #146 "...tarehe ya mwisho ni 31 Machi ya mwaka unaofuata"
  batch_005 #157 "Leseni ya biashara ya LGA (kila mwaka, 31 Machi)"                          batch_005 #193 "(10) Huisha leseni ya LGA kila mwaka (tarehe 31 Machi)"
The founder named TWO (the ones the D-FIDELITY-13 pricing flagged); reading the corpus for the same claim found FOUR (the pricing's question cue missed #157 and #193, which answer other questions). All four were READ IN FULL
(R37) before this script was written; each asserts the wrong date and is quarantined whole. #157 and #193 also carry correct content (the licence list, the ten steps); that loss is the cost of removing the wrong date,
and replacement pairs are a separate, authorable job. The probable origin of np_13's live "31 Machi" reply.

HOW (the 2026-11-16 pattern): rows NAMED by file:line AND by the start of their question, the record written FIRST and the live files second, idempotent, MOVED to datasets/tier1a/rejected/ with their reason.
SCOPE: REMOVED from cleaned_pairs (4) and sft/train_sft.jsonl (4); MARKED, NOT REMOVED: raw_sources/raw_pairs_batch_005.jsonl (3 rows; pre-cleaning input, feeds no training).

    python scripts/quarantine_licence_31_machi_training_pairs_2026_11_17.py [--dry-run]
"""
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUARANTINE = os.path.join(REPO, "datasets", "tier1a", "rejected", "licence_renewal_31_machi_quarantine_2026_11_17.jsonl")
OUT = os.path.join(REPO, "eval", "results", "licence_31_machi_training_quarantine_2026_11_17.json")
DEFECT = "BUSINESS_LICENCE_RENEWAL_DATE_31_MACHI"
CORRECT = "Every business licence expires on 30 June each year (locked fact business_licence_expiry_30_june; Business Licensing Act s.3(4) as substituted by Finance Act 2014 s.5). '31 Machi' is wrong."
T = "datasets/tier1a/"
Q145 = ("Leseni ya biashara ya LGA inahuishwa lini na ada yake", "ifikapo tarehe 31 Machi")
Q146 = ("Leseni ya biashara ya LGA inagharimu kiasi gani na inahuishwa lini?", "tarehe ya mwisho ni 31 Machi ya mwaka unaofuata")
Q157 = ("Biashara ya rejareja ndogo (duka) inahitaji leseni ngapi", "(kila mwaka, 31 Machi)")
Q193 = ("Muhtasari wa uzingatiaji wa msingi wa biashara ndogo Tanzania", "(tarehe 31 Machi)")
ROWS = [
    (T + "cleaned_pairs/batch_002_cleaned.jsonl", 145, "remove", Q145),
    (T + "cleaned_pairs/batch_005_cleaned.jsonl", 146, "remove", Q146),
    (T + "cleaned_pairs/batch_005_cleaned.jsonl", 157, "remove", Q157),
    (T + "cleaned_pairs/batch_005_cleaned.jsonl", 193, "remove", Q193),
    (T + "sft/train_sft.jsonl", 1208, "remove", Q145),
    (T + "sft/train_sft.jsonl", 1272, "remove", Q146),
    (T + "sft/train_sft.jsonl", 2428, "remove", Q193),
    (T + "sft/train_sft.jsonl", 2664, "remove", Q157),
    (T + "raw_sources/raw_pairs_batch_005.jsonl", 146, "mark", Q146),
    (T + "raw_sources/raw_pairs_batch_005.jsonl", 157, "mark", Q157),
    (T + "raw_sources/raw_pairs_batch_005.jsonl", 193, "mark", Q193),
]


def _head(o):
    return o.get("instruction") or o.get("question_sw") or ""


def main():
    dry = "--dry-run" in sys.argv
    files = {}
    for f, *_ in ROWS:
        files.setdefault(f, io.open(os.path.join(REPO, f), encoding="utf-8", newline="").read().splitlines())
    already_pos, already = set(), set()
    if os.path.exists(QUARANTINE):
        for ql in io.open(QUARANTINE, encoding="utf-8"):
            if ql.strip():
                rec = json.loads(ql)
                already.add(rec["row_sha256"])
                already_pos.add((rec["source_file"], rec["source_line_at_quarantine"]))
    planned, gone = [], 0
    for f, ln, action, (starts, sentence) in ROWS:
        if (f, ln) in already_pos:
            gone += 1
            continue
        raw = files[f][ln - 1] if ln <= len(files[f]) else ""
        o = json.loads(raw) if raw.strip() else {}
        h = hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if h in already:
            gone += 1
            continue
        if not _head(o).startswith(starts) or sentence not in raw:
            print(f"[ABORT] {f}:{ln} no longer holds the adjudicated row (head {_head(o)[:60]!r}). A line number pins a POSITION; re-adjudicate by content.")
            return 1
        planned.append((f, ln, action, h, o, sentence))
    if not planned:
        print(f"nothing to do: all {gone} rows already recorded (idempotent).")
        recs = [json.loads(l) for l in io.open(QUARANTINE, encoding="utf-8") if l.strip()]
        rem = {}
        for r in recs:
            if r["action"] == "removed_from_live_corpus":
                rem.setdefault(r["source_file"], []).append(r["source_line_at_quarantine"])
        rep = {"measured": "2026-11-17", "defect_class": DEFECT, "rows_removed_from_live": sum(len(v) for v in rem.values()), "rows_marked_raw": sum(1 for r in recs if r["action"] != "removed_from_live_corpus"),
               "lines_removed": {k: sorted(v) for k, v in rem.items()}, "quarantine_file": os.path.relpath(QUARANTINE, REPO).replace("\\", "/")}
        io.open(OUT, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=2))
        return 0
    print(f"planned {len(planned)} rows ({sum(1 for p in planned if p[2] == 'remove')} remove, {sum(1 for p in planned if p[2] == 'mark')} mark-only)")
    if dry:
        return 0
    os.makedirs(os.path.dirname(QUARANTINE), exist_ok=True)
    with io.open(QUARANTINE, "a", encoding="utf-8", newline="\n") as fh:               # record FIRST
        for f, ln, action, h, o, sentence in planned:
            fh.write(json.dumps({"source_file": f, "source_line_at_quarantine": ln, "action": "removed_from_live_corpus" if action == "remove" else "marked_raw_not_removed",
                                 "defect_class": DEFECT, "reason": f"states the business licence renewal date as 31 March: '...{sentence}...'. {CORRECT}",
                                 "adjudicated": "individually, by reading the full row (2026-11-17) -- not matched by pattern", "row_sha256": h, "row": o}, ensure_ascii=False) + "\n")
    removed = {}
    for f, ln, action, *_ in planned:
        if action == "remove":
            removed.setdefault(f, set()).add(ln)
    for f, lns in removed.items():                                                    # THEN the live files
        kept = [l for i, l in enumerate(files[f], 1) if i not in lns]
        with io.open(os.path.join(REPO, f), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(kept) + "\n")
    surv = {}
    for f in removed:
        lines = io.open(os.path.join(REPO, f), encoding="utf-8").read().splitlines()
        # a LICENCE row carrying the asserting phrase: the bare phrase also occurs in an unrelated PAYE row (annual statement), which is not this defect
        s = [x for x in {p[5] for p in planned} if any(x in l and "eseni" in l for l in lines)]
        if s:
            surv[f] = s
    assert not surv, f"an asserting sentence survives in a live file after quarantine: {surv}"
    rep = {"measured": "2026-11-17", "defect_class": DEFECT, "rows_removed_from_live": sum(len(v) for v in removed.values()), "rows_marked_raw": sum(1 for p in planned if p[2] == "mark"),
           "lines_removed": {k: sorted(v) for k, v in removed.items()}, "quarantine_file": os.path.relpath(QUARANTINE, REPO).replace("\\", "/")}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=2))
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

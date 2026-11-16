# -*- coding: utf-8 -*-
"""QUARANTINE THE 13 TRAINING-CORPUS ROWS THAT TEACH THE SUPERSEDED WCF ACCIDENT-REPORTING TRIGGER (founder's decision, 2026-11-16).

THE DEFECT. Workers Compensation Act Cap.263 R.E.2023 s.34(1) runs the EMPLOYER's reporting clock from RECEIPT of the employee's notice (or from learning of the
accident otherwise); GN 185/2016 Reg.15(4): "seven working days from the date of receipt of notification". These rows say the 7 days run FROM / AFTER THE ACCIDENT
("tangu tarehe ya ajali", "baada ya ajali kutokea", "tangu ajali itokee"). The live model reproduced exactly that on 2026-11-16 ("inaanza kuhesabiwa tangu siku ya ajali")
with the corrected row at rank 1 -- a training-prior defect no index edit reaches.

HOW (the 2026-10-05 NSSF-fine pattern, because that is what the project learned): every row is NAMED by file:line AND by the start of its instruction/question, read before it is
removed (R37: a presence-keyed sweep can delete correct rows), the adjudication travels with the row, the quarantine record is written FIRST and the live files second, and the
script is idempotent. Founder: "mark, don't delete" -- the rows are not destroyed, they move to datasets/tier1a/rejected/ (the audit trail) with their reason.

SCOPE, stated because R36 says a quarantine that does not reach datasets/tier1a/sft/ has removed nothing:
  REMOVED from the three LIVE stages (10 rows): cleaned_pairs (2), sft_shaped_pairs (3), sft/train_sft.jsonl (5).
  MARKED, NOT REMOVED (3 rows): datasets/tier1a/raw_sources/ (raw_pairs_batch_004 x2, _verify_batch004_pairs21_300 x1). Raw sources are the PRE-cleaning input and feed no
  training; they are recorded in the quarantine file with action=marked_raw so a re-clean from them cannot silently re-introduce the rows.

TWO ROWS (batch_004:295 and its shaped/train copy) are the OSHA-versus-WCF comparison: their OSHA half is correct and is lost with the row. Quarantining the row is the only
operation this convention has; repairing it in place would be a different decision (edited-in-place is R36's third outcome and leaves the record holding pre-edit text).

    python scripts/quarantine_wcf_accident_trigger_rows_2026_11_16.py [--dry-run]
"""
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUARANTINE = os.path.join(REPO, "datasets", "tier1a", "rejected", "wcf_accident_trigger_superseded_quarantine_2026_11_16.jsonl")
OUT = os.path.join(REPO, "eval", "results", "wcf_accident_trigger_quarantine_2026_11_16.json")
DEFECT = "WCF_ACCIDENT_TRIGGER_FROM_ACCIDENT_NOT_RECEIPT"
CORRECT = ("Cap.263 R.E.2023 s.34(1): the employer reports 'within seven days after receiving a notice of an accident from the employee or having learned in some other way "
           "that an accident has occurred'; GN 185/2016 Reg.15(4): 'seven working days from the date of receipt of notification'; the employee tells the employer within "
           "2 working days (Reg.15(1)). The Act says 'seven days' and the Regulation 'seven working days' -- an unresolved discrepancy recorded in locked_facts.json.")

T = "datasets/tier1a/"
# (file, 1-indexed line, how the file is treated, start of the question/instruction as adjudicated, the sentence that asserts the defect)
ROWS = [
    (T + "cleaned_pairs/batch_004_cleaned.jsonl", 179, "remove", "Ikiwa mfanyakazi ameumia kazini, mwajiri anamwarifu WCF ndan", "siku saba (7) ZA KAZI baada ya ajali kutokea"),
    (T + "cleaned_pairs/batch_004_cleaned.jsonl", 295, "remove", "Tofauti kati ya ripoti ya ajali ya OSHA na WCF ni ipi?", "siku 7 za kazi baada ya ajali"),
    (T + "sft_shaped_pairs/cleaned_pairs_batch_014.jsonl", 1018, "remove", "Vie, kama mfanyakazi wangu amepata ajali kazini, inabidi nii", "siku saba (7) tangu ajali itokee"),
    (T + "sft_shaped_pairs/cleaned_pairs_batch_015.jsonl", 214, "remove", "Ajali ya kazini inatakiwa kuripotiwa WCF ndani ya muda gani?", "siku 7 za kazi tangu tarehe ya ajali"),
    (T + "sft_shaped_pairs/cleaned_pairs_batch_015.jsonl", 233, "remove", "Mfanyakazi ameumia kazini", "siku 7 za kazi tangu tarehe ya ajali"),
    (T + "sft/train_sft.jsonl", 1280, "remove", "Vie, kama mfanyakazi wangu amepata ajali kazini, inabidi nii", "siku saba (7) tangu ajali itokee"),
    (T + "sft/train_sft.jsonl", 1944, "remove", "Ikiwa mfanyakazi ameumia kazini, mwajiri anamwarifu WCF ndan", "siku saba (7) ZA KAZI baada ya ajali kutokea"),
    (T + "sft/train_sft.jsonl", 2664, "remove", "Mfanyakazi ameumia kazini", "siku 7 za kazi tangu tarehe ya ajali"),
    (T + "sft/train_sft.jsonl", 2683, "remove", "Ajali ya kazini inatakiwa kuripotiwa WCF ndani ya muda gani?", "siku 7 za kazi tangu tarehe ya ajali"),
    (T + "sft/train_sft.jsonl", 3099, "remove", "Tofauti kati ya ripoti ya ajali ya OSHA na WCF ni ipi?", "siku 7 za kazi baada ya ajali"),
    (T + "raw_sources/raw_pairs_batch_004.jsonl", 179, "mark", "Ikiwa mfanyakazi ameumia kazini, mwajiri anamwarifu WCF ndan", "siku saba (7) ZA KAZI baada ya ajali kutokea"),
    (T + "raw_sources/raw_pairs_batch_004.jsonl", 295, "mark", "Tofauti kati ya ripoti ya ajali ya OSHA na WCF ni ipi?", "siku 7 za kazi baada ya ajali"),
    (T + "raw_sources/_verify_batch004_pairs21_300.jsonl", 160, "mark", "Ikiwa mfanyakazi ameumia kazini, mwajiri anamwarifu WCF ndan", "siku saba (7) ZA KAZI baada ya ajali kutokea"),
]


def _head(obj):
    return obj.get("instruction") or obj.get("question_sw") or ""


def main():
    dry = "--dry-run" in sys.argv
    files = {}
    for f, *_ in ROWS:
        files.setdefault(f, io.open(os.path.join(REPO, f), encoding="utf-8").read().splitlines())
    already, already_pos = set(), set()
    if os.path.exists(QUARANTINE):
        for ql in io.open(QUARANTINE, encoding="utf-8"):
            if ql.strip():
                rec = json.loads(ql)
                already.add(rec["row_sha256"])
                already_pos.add((rec["source_file"], rec["source_line_at_quarantine"]))   # removal SHIFTS later lines: a re-run must recognise a row by its recorded position too
    planned, gone = [], 0
    for f, ln, action, starts, sentence in ROWS:
        if (f, ln) in already_pos:
            gone += 1
            continue
        raw = files[f][ln - 1] if ln <= len(files[f]) else ""
        obj = json.loads(raw) if raw.strip() else {}
        h = hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if h in already:
            gone += 1
            continue
        if not _head(obj).startswith(starts) or sentence not in raw:
            # either already removed (positions shifted) or the line no longer holds the adjudicated row: both stop the run unless it is the idempotent case
            print(f"[ABORT] {f}:{ln} no longer holds the adjudicated row (head {_head(obj)[:60]!r}). A line number is a pin to a POSITION; re-adjudicate by content.")
            sys.exit(1)
        planned.append((f, ln, action, h, obj, sentence))
    if not planned:
        print(f"nothing to do: all {gone} rows already in the quarantine record (idempotent).")
        return 0
    print(f"planned {len(planned)} rows ({sum(1 for p in planned if p[2] == 'remove')} remove, {sum(1 for p in planned if p[2] == 'mark')} mark-only)")
    if dry:
        return 0
    os.makedirs(os.path.dirname(QUARANTINE), exist_ok=True)
    with io.open(QUARANTINE, "a", encoding="utf-8", newline="\n") as fh:                 # record FIRST
        for f, ln, action, h, obj, sentence in planned:
            fh.write(json.dumps({"source_file": f, "source_line_at_quarantine": ln, "action": "removed_from_live_corpus" if action == "remove" else "marked_raw_not_removed",
                                 "defect_class": DEFECT, "reason": f"asserts the 7 days run from / after THE ACCIDENT: '...{sentence}...'. {CORRECT}",
                                 "adjudicated": "individually, by reading the row -- not matched by pattern", "row_sha256": h, "row": obj}, ensure_ascii=False) + "\n")
    removed = {}
    for f, ln, action, *_ in planned:
        if action == "remove":
            removed.setdefault(f, set()).add(ln)
    for f, lns in removed.items():                                                      # THEN the live files
        kept = [l for i, l in enumerate(files[f], 1) if i not in lns]
        with io.open(os.path.join(REPO, f), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(kept) + "\n")
    survivors = {}
    for f in removed:
        txt = io.open(os.path.join(REPO, f), encoding="utf-8").read()
        s = [x for x in {p[5] for p in planned} if x in txt]
        if s:
            survivors[f] = s
    assert not survivors, f"the superseded trigger phrasing survives in a live file after quarantine: {survivors}"
    rep = {"measured": "2026-11-16", "defect_class": DEFECT, "rows_removed_from_live": sum(len(v) for v in removed.values()), "rows_marked_raw": sum(1 for p in planned if p[2] == "mark"),
           "lines_removed": {k: sorted(v) for k, v in removed.items()}, "quarantine_file": os.path.relpath(QUARANTINE, REPO).replace("\\", "/")}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=2))
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

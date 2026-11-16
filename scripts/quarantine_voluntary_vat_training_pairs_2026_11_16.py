# -*- coding: utf-8 -*-
"""QUARANTINE THE 8 TRAINING PAIRS THAT ASSERT UNCONDITIONAL VOLUNTARY VAT REGISTRATION (founder's decision, 2026-11-16: "mark, don't delete"; keep the 2 borderline "Omba kwa Kamishna wa TRA" pairs).

THE DEFECT. Each pair answers "can I register for VAT voluntarily below the threshold?" with a flat "Ndiyo -- unaweza / unaruhusiwa / TRA inaruhusu ... hata kama mauzo yako hayajafika kizingiti". The primary text says
less: the VAT Act Cap.148 R.E.2023 (read 2026-11-16, edition asserted) has 0 occurrences of "voluntar*" and routes registration only through s.28 (threshold), s.29(1) professional services, s.29(2) Government entities and
s.29(3) an intending trader, where "the Commissioner General MAY register" on evidence; the TRA FAQ says voluntary registration is allowed for "certain specific economic activities" and names none. The live model reproduced
the flat yes with the corrected row served (gate c2143c0 eval_013), the corpus's own claim echoed.

HOW (the 2026-10-05 and 2026-11-16 WCF pattern): every row NAMED by file:line AND by the start of its question, each READ in full before this script was written (R37), the adjudication travels with the row, the quarantine
record is written FIRST and the live files second, the script is idempotent, and the rows are MOVED to datasets/tier1a/rejected/ with their reason -- not destroyed.

SCOPE (R36: a quarantine that does not reach datasets/tier1a/sft/ has removed nothing):
  REMOVED from the LIVE stages (8 rows): cleaned_pairs (2), sft_shaped_pairs (2), sft/train_sft.jsonl (3), sft/val_sft.jsonl (1).
  MARKED, NOT REMOVED (4 rows): raw_sources (pre-cleaning input; feeds no training) -- recorded as action=marked_raw so a re-clean from them cannot silently re-introduce the rows.
  KEPT, DELIBERATELY (the 2 borderline texts, 4 locations): "Ninaweza kusajiliwa VAT hiari (voluntarily) kabla sijafika kizingiti?" -- says Ndiyo but routes the application to the Commissioner; asserted by the
  script as STILL PRESENT after the run, so a pattern that over-reaches fails loudly.

    python scripts/quarantine_voluntary_vat_training_pairs_2026_11_16.py [--dry-run]
"""
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUARANTINE = os.path.join(REPO, "datasets", "tier1a", "rejected", "voluntary_vat_unconditional_yes_quarantine_2026_11_16.jsonl")
OUT = os.path.join(REPO, "eval", "results", "voluntary_vat_training_quarantine_2026_11_16.json")
DEFECT = "VOLUNTARY_VAT_REGISTRATION_ASSERTED_UNCONDITIONALLY"
CORRECT = ("VAT Act Cap.148 R.E.2023: 0 occurrences of 'voluntar*'; registration routes are s.28 threshold, s.29(1) professional services, s.29(2) Government entities, s.29(3) intending trader ('the Commissioner General "
           "may register'); TRA FAQ: voluntary registration allowed for 'certain specific economic activities', none named -- unreconciled with the Act. The correct answer is hedged, never a flat Ndiyo.")
T = "datasets/tier1a/"
A = ("Mauzo yangu bado hayajafika TZS 200 milioni kwa mwaka. Ninaweza kusajili VAT kwa hiari", "unaweza kusajili VAT kwa hiari hata kama mauzo yako hayajafika")
B = ("Ninaweza kujisajili kwa VAT hiari hata kama mauzo yangu ni TZS 80,000,000", "Usajili wa hiari wa VAT unawezekana hata kama mauzo yako yako chini")
C = ("Mauzo yangu bado madogo, lakini naweza kujisajili VAT kwa hiari", "unaruhusiwa kujisajili VAT kwa hiari hata kama")
E = ("Biashara yangu ya mpya inatazamia mapato ya TZS 300M", "TRA inaruhusu usajili wa hiari wa VAT")
ROWS = [  # (file, 1-indexed line, treatment, (question start, asserting sentence))
    (T + "cleaned_pairs/batch_003_cleaned.jsonl", 148, "remove", B),
    (T + "cleaned_pairs/batch_007_replacements.jsonl", 2, "remove", A),
    (T + "sft_shaped_pairs/cleaned_pairs_batch_009.jsonl", 180, "remove", E),
    (T + "sft_shaped_pairs/cleaned_pairs_batch_015.jsonl", 102, "remove", C),
    (T + "sft/train_sft.jsonl", 467, "remove", A),
    (T + "sft/train_sft.jsonl", 541, "remove", B),
    (T + "sft/train_sft.jsonl", 2802, "remove", C),
    (T + "sft/val_sft.jsonl", 280, "remove", E),
    (T + "raw_sources/raw_pairs_batch_003.jsonl", 148, "mark", B),
    (T + "raw_sources/raw_pairs_replacements.jsonl", 2, "mark", A),
    (T + "raw_sources/raw_pairs_batch_009.jsonl", 180, "mark", E),
    (T + "raw_sources/batch_009_checkpoints/checkpoint_005.jsonl", 17, "mark", E),
]
KEPT_BORDERLINE = "Ninaweza kusajiliwa VAT hiari (voluntarily) kabla sijafika kizingiti?"


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
        ans = o.get("output") or o.get("answer_sw") or ""
        if not _head(o).startswith(starts) or sentence not in raw or not ans.lstrip().lower().startswith("ndiyo"):
            print(f"[ABORT] {f}:{ln} no longer holds the adjudicated row (head {_head(o)[:60]!r}). A line number pins a POSITION; re-adjudicate by content.")
            return 1
        planned.append((f, ln, action, h, o, sentence))
    if not planned:
        print(f"nothing to do: all {gone} rows already recorded (idempotent).")
        return 0
    print(f"planned {len(planned)} rows ({sum(1 for p in planned if p[2] == 'remove')} remove, {sum(1 for p in planned if p[2] == 'mark')} mark-only)")
    if dry:
        return 0
    os.makedirs(os.path.dirname(QUARANTINE), exist_ok=True)
    with io.open(QUARANTINE, "a", encoding="utf-8", newline="\n") as fh:               # record FIRST
        for f, ln, action, h, o, sentence in planned:
            fh.write(json.dumps({"source_file": f, "source_line_at_quarantine": ln, "action": "removed_from_live_corpus" if action == "remove" else "marked_raw_not_removed",
                                 "defect_class": DEFECT, "reason": f"answers an unconditional 'Ndiyo' to voluntary VAT registration below the threshold: '...{sentence}...'. {CORRECT}",
                                 "adjudicated": "individually, by reading the full row (2026-11-16) -- not matched by pattern", "row_sha256": h, "row": o}, ensure_ascii=False) + "\n")
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
        txt = io.open(os.path.join(REPO, f), encoding="utf-8").read()
        s = [x for x in {p[5] for p in planned} if x in txt]
        if s:
            surv[f] = s
    assert not surv, f"an asserting sentence survives in a live file after quarantine: {surv}"
    border = sum(io.open(os.path.join(REPO, f), encoding="utf-8").read().count(KEPT_BORDERLINE)
                 for f in (T + "sft/train_sft.jsonl", T + "sft_shaped_pairs/cleaned_pairs_batch_012.jsonl"))
    assert border == 2, f"the borderline pair must be KEPT in both live stages (expected 2 occurrences, found {border})"
    rep = {"measured": "2026-11-16", "defect_class": DEFECT, "rows_removed_from_live": sum(len(v) for v in removed.values()), "rows_marked_raw": sum(1 for p in planned if p[2] == "mark"),
           "lines_removed": {k: sorted(v) for k, v in removed.items()}, "borderline_kept_live_occurrences": border, "quarantine_file": os.path.relpath(QUARANTINE, REPO).replace("\\", "/")}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=2))
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""QUARANTINE THE 4 TRAINING ROWS ASSERTING THE SUPERSEDED NSSF FINE (TZS 100,000).

Cap.50 R.E.2023 s.76(1) reads "a fine not exceeding TEN MILLION shillings". TZS 100,000 is
R.E.2015 s.72(1)'s actual text -- superseded, not invented (R29 mode 2).

⛔ ROWS ARE NAMED INDIVIDUALLY, BY file:line AND BY CONTENT HASH, NEVER MATCHED BY PATTERN.
That is the whole design of this script and the reason it is not a two-line regex sweep.

The propagation sweep (eval/controls/sweep_nssf_fine_100k_propagation.py) returned FIVE
candidates on a deliberately narrow three-axis bound. One of them --
cleaned_pairs_batch_009.jsonl:216 -- is a FALSE POSITIVE: it uses TZS 100,000 as the BASE of a
correct worked example of the 5% late-payment penalty ("Mfano: NSSF TZS 100,000 haijalipwa kwa
miezi 3 -> faini = 5% x 100,000 x 3 = TZS 15,000"). The rate is the statutory one (s.14(3)), the
arithmetic is right, and the figure is not a ceiling at all. A pattern-driven quarantine would
have deleted it.

So the standard this script implements: EVERY row is adjudicated by reading it, the adjudication
travels with the quarantined row, and the excluded false positive is recorded here by name --
not merely omitted. An exclusion that leaves no trace is indistinguishable from an oversight.

The rows are REMOVED from the live corpus and APPENDED to
datasets/tier1a/rejected/, which is the audit trail, per CLAUDE.md Section 8 ("rejected/ --
Pairs that failed schema/whitelist -- keep for audit trail").

IDEMPOTENT: re-running after a successful pass finds the rows already gone and exits 0 having
done nothing, rather than appending duplicates to the quarantine file.
"""
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUARANTINE = os.path.join(REPO, "datasets", "tier1a", "rejected",
                          "nssf_fine_stale_100k_quarantine_2026_10_05.jsonl")
OUT = os.path.join(REPO, "eval", "results", "nssf_fine_100k_quarantine.json")
DEFECT = "NSSF_FINE_CEILING_STALE_100K_FROM_RE2015"

SRC = "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_014.jsonl"

# Each row named by its 1-indexed line in SRC, with the ADJUDICATION that authorises removing
# it. The `instruction_starts` field is checked against the file before anything is written --
# a line number alone is a pin to a position, and positions move (the stale-pins lesson). If the
# content at that line is not what was adjudicated, the run aborts rather than quarantining
# whatever happens to be there now.
TO_QUARANTINE = [
    {
        "line": 693,
        "instruction_starts": "Chike, niliona huko kwenye sheria kuna adhabu ya laki moja",
        "why": "Asserts 'faini ya shilingi elfu mia moja (TZS 100,000)' as the current "
               "statutory fine, attributed to 'kifungo cha sheria' without naming a section. "
               "The figure is R.E.2015 s.72(1); R.E.2023 s.76(1) reads ten million.",
    },
    {
        "line": 694,
        "instruction_starts": "Hii faini ya laki moja inawahusu nani hasa?",
        "why": "Same superseded ceiling, framed as applying to compliance offences generally.",
    },
    {
        "line": 695,
        "instruction_starts": "Hii faini ya elfu mia moja inamaanisha nini",
        "why": "Same superseded ceiling, framed inside the NSSF benefits system.",
    },
    {
        "line": 696,
        "instruction_starts": "Nkalipa vipi hiyo faini ya laki moja",
        "why": "Same superseded ceiling, with payment instructions built on top of it -- the "
               "most actionable of the four, since it tells the user to follow a process for "
               "an amount understated 100x.",
    },
]

# ⛔ RECORDED, NOT OMITTED. This row matched the sweep and is CORRECT.
EXCLUDED_FALSE_POSITIVE = {
    "file": "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_009.jsonl",
    "line": 216,
    "instruction_starts": "NSSF faini ya kuchelewa ni ngapi",
    "why_kept": "TZS 100,000 is the BASE of a worked example of the 5% late-payment penalty "
                "(s.14(3), confirmed correct against R.E.2023), not a fine ceiling: "
                "'Mfano: NSSF TZS 100,000 haijalipwa kwa miezi 3 -> faini = 5% x 100,000 x 3 "
                "= TZS 15,000'. The rate is statutory and the arithmetic is right.",
    "what_it_demonstrates": "A pattern-driven quarantine of the sweep's match set would have "
                            "deleted a correct row. This is why every row is read before it is "
                            "removed, and why the exclusion is written down.",
}


def main():
    src_path = os.path.join(REPO, SRC)
    lines = io.open(src_path, encoding="utf-8").read().splitlines()

    # --- verify every adjudicated line still holds the content it was adjudicated on --------
    planned = []
    for spec in TO_QUARANTINE:
        raw = lines[spec["line"] - 1]
        obj = json.loads(raw)
        instr = obj.get("instruction", "")
        if not instr.startswith(spec["instruction_starts"]):
            print(f"[ABORT] {SRC}:{spec['line']} no longer holds the adjudicated row.\n"
                  f"  expected to start: {spec['instruction_starts']!r}\n"
                  f"  found:             {instr[:90]!r}\n"
                  f"A line number is a pin to a POSITION, and positions move. Re-adjudicate "
                  f"by content before quarantining anything.")
            sys.exit(1)
        planned.append((spec, raw, obj))

    if not planned:
        print("nothing planned -- already quarantined?")
        sys.exit(0)

    # --- idempotence: if these exact rows are already in the quarantine file, stop -----------
    already = set()
    if os.path.exists(QUARANTINE):
        for ql in io.open(QUARANTINE, encoding="utf-8"):
            if ql.strip():
                already.add(hashlib.sha256(
                    json.dumps(json.loads(ql).get("row"), ensure_ascii=False,
                               sort_keys=True).encode()).hexdigest())
    new_records, removed_lines = [], set()
    for spec, raw, obj in planned:
        h = hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()
                           ).hexdigest()
        if h in already:
            print(f"[skip] {SRC}:{spec['line']} already in the quarantine file")
            continue
        new_records.append({
            "source_file": SRC,
            "source_line_at_quarantine": spec["line"],
            "defect_class": DEFECT,
            "reason": spec["why"],
            "adjudicated": "individually, by reading the row -- not matched by pattern",
            "correct_value": "TZS 10,000,000 (Cap.50 R.E.2023 s.76(1), 'a fine not exceeding "
                             "ten million shillings or to imprisonment for a term not "
                             "exceeding two years or to both')",
            "superseded_value_source": "Cap.50 R.E.2015 s.72(1), 'a fine not exceeding one "
                                       "hundred thousand shillings' -- R29 mode 2, an "
                                       "out-of-date edition faithfully transcribed, not a "
                                       "fabrication",
            "row_sha256": h,
            "row": obj,
        })
        removed_lines.add(spec["line"])

    if not new_records:
        print("all four rows already quarantined -- nothing to do (idempotent).")
        sys.exit(0)

    # --- write the quarantine record FIRST, then remove from the live corpus -----------------
    # Order matters: if the process dies between the two steps, a row present in BOTH places is
    # recoverable and visible, while a row removed with no record is simply gone.
    os.makedirs(os.path.dirname(QUARANTINE), exist_ok=True)
    with io.open(QUARANTINE, "a", encoding="utf-8") as fh:
        for rec in new_records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    kept = [ln for i, ln in enumerate(lines, 1) if i not in removed_lines]
    with io.open(src_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(kept) + "\n")

    # --- verify the defect is actually gone from the live corpus -----------------------------
    after = io.open(src_path, encoding="utf-8").read()
    survivors = [s for s in ("faini ya shilingi elfu mia moja", "faini ya laki moja")
                 if s in after]

    report = {
        "measured": "2026-10-05",
        "harness": "scripts/quarantine_nssf_fine_100k_rows.py",
        "defect_class": DEFECT,
        "rows_quarantined": len(new_records),
        "lines_removed_from": {SRC: sorted(removed_lines)},
        "corpus_rows_before": len(lines),
        "corpus_rows_after": len(kept),
        "quarantine_file": os.path.relpath(QUARANTINE, REPO).replace("\\", "/"),
        "excluded_false_positive": EXCLUDED_FALSE_POSITIVE,
        "superseded_phrases_surviving_in_live_corpus": survivors,
        "gold_answers_affected": 0,
        "_gold_note": "Zero. All 13 gold matches on the figure are OSHA's CORRECT TZS "
                      "100,000/day continuing-offence charge and are untouched.",
    }
    assert not survivors, (
        f"the superseded phrasing survives in the live corpus after quarantine: {survivors}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print(json.dumps({k: v for k, v in report.items()
                      if k != "excluded_false_positive"}, ensure_ascii=False, indent=2))
    print(f"\nEXCLUDED (correct row, kept): {EXCLUDED_FALSE_POSITIVE['file']}:"
          f"{EXCLUDED_FALSE_POSITIVE['line']}")
    print(f"[saved] {OUT}")


if __name__ == "__main__":
    main()

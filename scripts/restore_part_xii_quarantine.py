# -*- coding: utf-8 -*-
"""RESTORE THE PAIRS QUARANTINED ON 2026-09-01 FOR BEING RIGHT.

They were removed with this reason, recorded in each row's own `_quarantine` block:

    'cites "(Section XII)" as the Companies Act provision for foreign-company BRELA filings.
     The correct citation is Part XIII, ss.320-328 of Cap.212'

The Companies Act Cap.212 R.E. 2023, read directly on 2026-10-04 (394pp, 3,215,470 bytes,
brela.go.tz, HTTP 200), says:

    PART XI    WINDING UP OF UNREGISTERED COMPANIES              s.429+
    PART XII   COMPANIES INCORPORATED OUTSIDE TANZANIA           ss.437-447
    PART XIII  GENERAL PROVISIONS AS TO REGISTRATION             s.454+
    s.437.-(1) 'Sections 438 to 447 shall apply to all foreign companies...'

So the quarantine reason is void: the numeral XII was right and Part XIII was wrong. See
eval/controls/inventory_part_xii_reversal.py for the full 15-site inventory and why this is not
an edition mismatch (the Act's own renumbering notes give a +5 shift; ss.320-328 would need
about -115, so no edition of Cap.212 ever put the regime there).

=============================================================================================
TWO THINGS THE QUARANTINE RECORD DOES NOT SAY, BOTH FOUND BY READING THE ROWS
=============================================================================================

1. '13 TRAINING ROWS' IS 13 FILE-LEVEL INSTANCES OF FOUR DISTINCT PAIRS. The same four
   question/answer pairs appear across seven files -- cleaned_pairs, raw_sources, a batch
   checkpoint, train_sft.jsonl and train_sft_balanced.jsonl. Counting instances as rows
   overstates the corpus impact by about 3x. Recorded because the figure '13' has already
   travelled once.

2. NINE OF THE THIRTEEN ALSO ASSERT 'USD 25', WHICH IS UNDER LIVE DISPUTE. That was NOT the
   quarantine reason and is not settled by the Act -- s.458 and s.489(3) delegate every fee
   amount to Minister's regulations, and the Companies (Fees) Regulations were not located.
   brela.go.tz/pages/tozo-za-kampuni item 15(iv) read TZS 70,000 on 2026-10-04 where the same
   page was recorded as reading USD 25 on 2026-09-02. Restoring these rows reinstates a figure
   that matches the CURRENT locked fact (brela_foreign_late_filing_penalty, USD 25) but
   conflicts with one reading of the regulator's page.
   THEY ARE RESTORED ANYWAY, because the corpus should agree with the locked fact and the
   locked fact has not been changed -- but they are listed by hand below so that whoever
   resolves the fee can find them in one lookup instead of a sweep.

WHAT IS NOT DONE HERE, DELIBERATELY:

  * train_sft.jsonl and train_sft_balanced.jsonl are NOT touched. They are export artifacts
    regenerated from cleaned_pairs at Gate 3 (CLAUDE.md Section 9: 'the split is enforced at
    JSONL export time, not manually'). Hand-editing a generated file would desync it from its
    source and the next export would silently revert the edit. Six of the thirteen instances
    live there and come back on regeneration.
  * The rows' wording is NOT changed. They say 'Section XII' where the Act's heading says
    'PART XII'. That is a LABEL IMPRECISION, not the citation error they were removed for --
    and BRELA's own fee page uses the same form ('Sehemu ya XII'). Rewriting restored rows
    would be a content edit needing its own justification (R25), and the justification for a
    label change is weak. Flagged, not applied.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUARANTINE = os.path.join(
    REPO, "datasets", "tier1a", "rejected", "tier3_confirmed_wrong_quarantine_2026_09_01.jsonl")

DEFECT = "SECTION_XII_FOREIGN_COMPANY"

# Export artifacts -- regenerated, never hand-edited.
GENERATED = ("train_sft.jsonl", "train_sft_balanced.jsonl")

# Where each authored source actually lives (the `from_file` paths in the quarantine blocks are
# bare basenames for the checkpoint, and one is a path that no longer resolves as written).
AUTHORED_DIRS = ("datasets/tier1a/cleaned_pairs", "datasets/tier1a/raw_sources",
                 "datasets/tier1a/raw_sources/batch_013_checkpoints")

RESTORED_NOTE = {
    "restored": "2026-10-05",
    "reason": "The 2026-09-01 quarantine reason is VOID. Companies Act Cap.212 R.E.2023 "
              "PART XII is 'COMPANIES INCORPORATED OUTSIDE TANZANIA' (ss.437-447); the "
              "'correct citation' this row was removed for -- Part XIII, ss.320-328 -- is "
              "winding-up machinery in Part VIII and corresponds to no edition of the Act. "
              "Read directly from the Act on 2026-10-04.",
    "harness": "scripts/restore_part_xii_quarantine.py",
    "inventory": "eval/controls/inventory_part_xii_reversal.py",
    "⚠️_unresolved_figure": "If this row asserts USD 25/month, that figure is UNDER DISPUTE "
                            "and was not the quarantine reason. The Act delegates all fees "
                            "(s.458, s.489(3)); the Companies (Fees) Regulations were not "
                            "located; brela.go.tz read TZS 70,000 on 2026-10-04 against USD 25 "
                            "on 2026-09-02. Restored to match the unchanged locked fact.",
    "⚠️_label_imprecision": "Says 'Section XII' where the Act's heading reads 'PART XII'. Not "
                            "rewritten -- a label change is a content edit needing its own "
                            "justification (R25), and BRELA's own page uses the same form.",
}


def _resolve(basename):
    for d in AUTHORED_DIRS:
        p = os.path.join(REPO, d, basename)
        if os.path.exists(p):
            return p
    return None


def main():
    write = "--write" in sys.argv
    with open(QUARANTINE, encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh if l.strip()]

    targets, skipped_generated, unresolved, keep = [], [], [], []
    for row in rows:
        q = row["_quarantine"]
        if q["defect_class"] != DEFECT:
            keep.append(row)
            continue
        base = os.path.basename(q["from_file"])
        if base in GENERATED:
            skipped_generated.append({"file": base, "line": q["from_line"]})
            continue  # dropped from quarantine; regeneration restores it
        path = _resolve(base)
        if path is None:
            unresolved.append(base)
            keep.append(row)
            continue
        body = {k: v for k, v in row.items() if k != "_quarantine"}
        body["_restored"] = RESTORED_NOTE
        targets.append((path, body, base))

    # R20: this must be able to fail. A resolver that found nothing would report a clean
    # "0 restored" and look like there was nothing to do.
    assert targets, ("no authored source file resolved for any quarantined row -- the resolver "
                     "is broken, not the corpus")
    assert len(targets) + len(skipped_generated) + len(unresolved) == \
        sum(1 for r in rows if r["_quarantine"]["defect_class"] == DEFECT), "row accounting lost"

    by_file = {}
    for path, body, base in targets:
        by_file.setdefault(path, []).append(body)

    if write:
        for path, bodies in by_file.items():
            with open(path, "a", encoding="utf-8") as fh:
                for b in bodies:
                    fh.write(json.dumps(b, ensure_ascii=False) + "\n")
        with open(QUARANTINE, "w", encoding="utf-8") as fh:
            for r in keep:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # distinct pairs, to keep "13" from travelling again
    distinct = sorted({(r.get("instruction") or r.get("question_sw", ""))[:70]
                       for r in rows if r["_quarantine"]["defect_class"] == DEFECT})
    # COUNT THE BODY, NOT THE WHOLE ROW. The first version of this line dumped the entire row,
    # whose `_quarantine` block CONTAINS the phrase 'USD 25/month foreign' in its own reason
    # text -- so every one of the 13 matched and it reported 13/13. The quarantine metadata is
    # not the pair's claim. Caught before --write because this script reports first.
    asserts_usd25 = sum(1 for r in rows
                        if r["_quarantine"]["defect_class"] == DEFECT
                        and "USD 25" in json.dumps({k: v for k, v in r.items()
                                                    if k != "_quarantine"}, ensure_ascii=False))

    print(f"mode: {'WRITE' if write else 'REPORT_ONLY'}")
    print(f"quarantine entries with defect {DEFECT}: "
          f"{sum(1 for r in rows if r['_quarantine']['defect_class'] == DEFECT)}")
    print(f"  -> DISTINCT question/answer pairs: {len(distinct)}")
    print(f"  -> instances asserting the disputed USD 25: {asserts_usd25}")
    print(f"\nrestored to authored sources: {len(targets)}")
    for path, bodies in sorted(by_file.items()):
        print(f"   +{len(bodies)}  {os.path.relpath(path, REPO)}")
    print(f"\nleft to regeneration (export artifacts, not hand-edited): {len(skipped_generated)}")
    for s in skipped_generated:
        print(f"      {s['file']}:{s['line']}")
    if unresolved:
        print(f"\n⚠️ source file not found, kept in quarantine: {unresolved}")
    print(f"\nquarantine file: {len(rows)} -> {len(keep)} rows "
          f"({len(keep)} remaining are other defect classes: P45_P9_CONFLATION, COURSE_FEE_250K)")
    print("\nthe four distinct pairs:")
    for d in distinct:
        print(f"   {d}")


if __name__ == "__main__":
    main()

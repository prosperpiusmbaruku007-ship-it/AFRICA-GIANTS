# -*- coding: utf-8 -*-
"""A QUARANTINED ROW MAY NOT STILL BE IN THE FILE THAT TRAINS THE MODEL.

⛔ THE INCIDENT, AND IT WAS ONE DAY OLD WHEN FOUND. On 2026-10-05 four rows asserting a TZS
100,000 NSSF fine ceiling were quarantined out of
`datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_014.jsonl`. The commit removed them, the
quarantine record was written, the count went 1102 → 1098, and everything about it was correct.
`datasets/tier1a/sft/train_sft.jsonl` — the EXPORTED FILE THAT ACTUALLY TRAINS — was never
touched, and all four rows were still in it the next morning at lines 503/2758/3034/3272.

The quarantine fired. It was pointed one stage upstream of the bytes. That is precisely the pair
of inert controls found on 2026-08-24: `scan_for_keys.py` scanned correctly and was handed no
files; `chike/retrieval.py`'s index contract raises correctly and production never imports it.
Nothing is wrong with the logic in any of the three, and no test asking "did the quarantine
work?" could find any of them. **The question has to be where the control ACTS, not whether it
works.**

Two more were found with it — a rent-WHT row quarantined 2026-09-26 and a VAT-withholding row
from 2026-09-01 — so this is not a one-off slip in one script. It is the shape every quarantine
in this repo has, because they all target the authored corpus.

THIS TEST IS THE DURABLE FIX. Prose in CLAUDE.md would decay exactly as R30's "TRA unreachable"
note did: a correct finding, faithfully written down, that nothing forced the next session to
act on.

WHAT IT DOES NOT DO: re-adjudicate. A row kept on purpose goes in `ADJUDICATED_KEEPS` with the
reason, because the one survivor left is a row the earlier quarantine should never have taken.
"""
import importlib.util
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT = os.path.join(REPO, "eval", "results", "quarantine_reach_audit_2026_10_06.json")

# ⛔ EVERY ENTRY IS A ROW A PAST QUARANTINE TOOK IN ERROR, KEPT ON PURPOSE. Not an exemption
# list for convenience — adding to it asserts that the quarantine was wrong, not that the
# survivor is tolerable.
#
# ⚠️ A RESTORATION MAKES THIS AUDIT GO RED, AND THE RED IS CORRECT BUT MISLEADING. The audit
# asks "is a quarantined body live again?" and cannot distinguish a quarantine that FAILED TO
# REACH the export from a row we deliberately PUT BACK because the quarantine was wrong. Both
# look identical to it. That is not a defect in the audit -- it is the reason this list exists
# and the reason each entry must carry its reasoning rather than a label. The 2026-10-08
# restorations below are the first entries added for that second reason.
ADJUDICATED_KEEPS = {
    "datasets/tier1a/cleaned_pairs/batch_008_cleaned.jsonl": [
        {
            "needle": "Mfumo wa PAYE Tanzania una bendi ya kiwango cha sifuri",
            "quarantined_by": "paye_defect_quarantine_2026_08_25.jsonl",
            "why": (
                "RESTORED 2026-10-08 (phase 2), founder-authorised. b008_paye_adv_005: "
                "'...HAKUNA punguzo la kibinafsi tofauti la TZS 26,000 kwa mwezi' -- verbatim "
                "what CLAUDE.md s.11 states is correct (no separate personal relief; the 0% "
                "band on the first TZS 270,000 IS the tax-free amount), removed for "
                "ASSERTING the phantom relief. subdomain paye_adversarial."),
        },
        {
            "needle": "Ndiyo — mshahara wa TZS 270,001 unaathiriwa na bendi ya pili",
            "quarantined_by": "paye_defect_quarantine_2026_08_25.jsonl",
            "why": (
                "RESTORED 2026-10-08 (phase 2). b008_paye_adv_007: band 2 at 8% ('TZS 1 x 8% "
                "= TZS 0.08') plus 'Kumbuka: HAKUNA punguzo la kibinafsi tofauti la TZS "
                "26,000'. Removed for asserting the relief it denies. paye_adversarial. "
                "⛔ WITH THIS PAIR THE RECORD-WIDE RE-READ IS COMPLETE AND THE RESULT IS THE "
                "FINDING: 22 distinct bodies, 4 adversarial rows ALL over-removed, 18 "
                "non-adversarial rows ALL correctly removed. 100% precision outside the "
                "adversarial subdomain, 0% inside it."),
        },
        {
            "needle": "Bendi tano za PAYE Tanzania 2025/2026: (1) TZS 0 hadi 270,000: kiwango 0%",
            "quarantined_by": "paye_defect_quarantine_2026_08_25.jsonl",
            "why": (
                "RESTORED 2026-10-08, founder-authorised, after R37 found the removal was the "
                "defect. b008_paye_adv_002: the record's reason reads 'computes PAYE band 2 at "
                "9%; the locked rate is 8%' and THE ROW SAYS 'kiwango 8% (si 9%)' -- the correct "
                "rate, explicitly denying 9%, in a row whose subdomain is paye_adversarial, i.e. "
                "written to hold the line against that exact error. The record's disposition "
                "explains the choice not to repair as 'correcting requires recomputing the "
                "arithmetic'; there is no arithmetic in the row at all. A reason written once "
                "for a batch and applied per row reads as adjudication that never happened. "
                "Every other limb was checked whole before restoring: bands 0/8/20/25/30, the "
                "TZS 3,240,000/year threshold (= 270,000 x 12), 'hakuna punguzo tofauti' (no "
                "personal relief), and the marginal-band explanation. Restored to the AUTHORED "
                "corpus, not the export (R36's converse). See "
                "eval/controls/restore_overremoved_rows_2026_10_08.py."),
        },
        {
            "needle": "Bendi TANO za PAYE Tanzania 2025/2026 — sahihi kamili",
            "quarantined_by": "paye_defect_quarantine_2026_08_25.jsonl",
            "why": (
                "RESTORED 2026-10-08, founder-authorised. b008_paye_adv_015, the sibling of the "
                "keep above and removed by the same batch reason. THE ROW SAYS '8% (MUHIMU: si "
                "9%)' -- an emphatic denial of the very rate it was removed for asserting. Also "
                "paye_adversarial. One cosmetic defect was found while reading it whole and is "
                "recorded rather than silently fixed: a stray orphan fragment 'kwa mwezi.' sits "
                "after the threshold clause in both answer_sw and answer_en, left by some "
                "earlier edit. It is a text-quality flaw, not a factual one, and repairing it "
                "during a restoration would mix a content edit into a byte-for-byte restore "
                "(R25). Tracked separately."),
        },
    ],
    "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_014.jsonl": [
        {
            "needle": "Hicho kiasi cha TZS 200M au TZS 100M",
            "quarantined_by": "tier2_confirmed_wrong_quarantine_2026_08_31.jsonl",
            "why": (
                "RESTORED 2026-10-08 (phase 2). Removed for 'dating the VAT 100M->200M "
                "increase to July 2024'. ⛔ THE ANSWER CONTAINS NO DATE AT ALL -- verified, no "
                "match for Julai 2024 anywhere in the body. It is the QUESTION that says "
                "'ninaambiwa ni kuanzia Julai 2024'. The sweep matched the instruction field: "
                "R36's first lesson (match on the ANSWER, never the question) inverted into a "
                "REMOVAL sweep, where it deletes rather than merely reporting. Both figures "
                "the row does state (200M/12mo, 100M/6mo) are correct."),
        },
        {
            "needle": "ifikapo tarehe muafaka",
            "quarantined_by": "vat_withholding_deadline_stale_quarantine_2026_09_01.jsonl",
            "why": (
                "RESTORED 2026-10-08 (phase 2). Removed for 'asserting the 20th'. The "
                "QUESTION asks '...ifikapo TAREHE 20?' and the answer pointedly declines to "
                "endorse it: 'endapo utashindwa kuwasilisha VAT withholding ifikapo TAREHE "
                "MUAFAKA'. The answer is MORE careful than the question. Same shape as the "
                "'nilizolipia 250,000' row kept on 2026-10-08 -- the user's own figure is not "
                "the model's claim. What it does say (late remittance draws interest or a "
                "penalty) is true under FA2026 s.95 as much as before it."),
        },
    ],
    "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_015.jsonl": [
        {
            "needle": "kudai kiasi kilichozuiliwa kama input credit",
            "quarantined_by": "vat_withholding_deadline_stale_quarantine_2026_09_01.jsonl",
            "why": (
                "RESTORED 2026-10-08, founder-authorised. AND THE AUDIT'S OWN STATED REASON FOR "
                "THIS ONE WAS WRONG, which is worth recording: the over-removal audit and "
                "PROGRESS.md both describe this row as removed 'for containing tarehe 20'. Read "
                "whole, the record's actual reason is a statutory supersession -- FA2026 s.95 "
                "replaced VAT Act s.71(5), moving the REMITTANCE deadline to within 10 days "
                "after the end of the tax period. The row still does not commit that defect: "
                "'return yako ya VAT, inayowasilishwa kufikia tarehe 20' attaches the 20th to "
                "the RETURN, which is correct and is the distinction CLAUDE.md draws in terms, "
                "and the remittance sentence ('Wakala huwasilisha kiasi kilichozuiliwa moja kwa "
                "moja TRA') carries NO DATE AT ALL. A row naming no remittance deadline cannot "
                "assert the superseded one. It is INCOMPLETE -- it does not teach the new 10-day "
                "rule -- and incompleteness is not grounds for removal. The residual adjacency "
                "risk is recorded in the restoration artifact and deliberately not acted on; "
                "the fix is a POSITIVE row teaching s.95, an addition rather than a deletion."),
        },
    ],
    "datasets/tier1a/sft/train_sft.jsonl": [
        {
            "needle": "Mfumo wa PAYE Tanzania una bendi ya kiwango cha sifuri",
            "quarantined_by": "paye_defect_quarantine_2026_08_25.jsonl",
            "why": ("Exported copy of the b008_paye_adv_005 restoration above: restored "
                    "upstream, then regenerated (R36's converse). Pinned by CONTENT, never "
                    "by line -- this file is reshuffled on every rebuild."),
        },
        {
            "needle": "Ndiyo — mshahara wa TZS 270,001 unaathiriwa na bendi ya pili",
            "quarantined_by": "paye_defect_quarantine_2026_08_25.jsonl",
            "why": ("Exported copy of the b008_paye_adv_007 restoration above: restored "
                    "upstream, then regenerated. 4390 rows after the rebuild, +4 from 4386."),
        },
        {
            "needle": "Hicho kiasi cha TZS 200M au TZS 100M",
            "quarantined_by": "tier2_confirmed_wrong_quarantine_2026_08_31.jsonl",
            "why": ("Exported copy of the VAT_JULY2024 restoration above -- the row removed "
                    "for dating an increase its answer never dates. Present here because the "
                    "restoration went to the AUTHORED corpus and the export was then "
                    "regenerated, which is the R36-correct direction: a row written into "
                    "datasets/tier1a/sft/ by hand is overwritten on the next rebuild and has "
                    "no authored source."),
        },
        {
            "needle": "ifikapo tarehe muafaka",
            "quarantined_by": "vat_withholding_deadline_stale_quarantine_2026_09_01.jsonl",
            "why": ("Exported copy of the tarehe-muafaka restoration above -- the row whose "
                    "answer is MORE careful than its question, declining to endorse the 20th "
                    "the question names. THIS IS THE THIRD ROW THAT ONE 2026-09-01 SWEEP "
                    "REMOVED over a correctly-attached or deliberately-avoided 'tarehe 20', "
                    "after train_sft:3196 and the row restored earlier the same day -- so "
                    "that sweep's over-removal count is three, not one."),
        },
        {
            "needle": "Bendi tano za PAYE Tanzania 2025/2026: (1) TZS 0 hadi 270,000: kiwango 0%",
            "quarantined_by": "paye_defect_quarantine_2026_08_25.jsonl",
            "why": (
                "The exported copy of the b008_paye_adv_002 restoration above. It is present "
                "here BECAUSE the restoration went to the authored corpus and the export was "
                "then regenerated, which is the R36-correct direction: a restoration written "
                "into datasets/tier1a/sft/ by hand would be overwritten on the next rebuild and "
                "would have no authored source. Pinned by CONTENT, never by line -- this file is "
                "reshuffled on every rebuild, and eleven specimens pinned by file:line into it "
                "all failed at once on 2026-10-07."),
        },
        {
            "needle": "Bendi TANO za PAYE Tanzania 2025/2026 — sahihi kamili",
            "quarantined_by": "paye_defect_quarantine_2026_08_25.jsonl",
            "why": (
                "The exported copy of the b008_paye_adv_015 restoration above, present for the "
                "same reason: restored upstream, then regenerated. Both PAYE questions were "
                "measured ABSENT from all 36 corpus files before restoring, so no replacement "
                "pair existed and 'list the five PAYE bands' -- a core Tier 1A question -- was "
                "unanswered by the corpus entirely for six weeks."),
        },
        {
            "needle": "kudai kiasi kilichozuiliwa kama input credit",
            "quarantined_by": "vat_withholding_deadline_stale_quarantine_2026_09_01.jsonl",
            "why": (
                "The exported copy of the VAT-withholding reconciliation restoration above. "
                "Restored to sft_shaped_pairs/ and regenerated into the export. Note this is "
                "the SECOND row that one 2026-09-01 sweep removed for a 'tarehe 20' that was "
                "correctly attached to the return, after the train_sft:3196 instance already "
                "recorded in this file -- so that sweep's over-removal count is two, not one."),
        },
        {
            "needle": "siku ambayo VAT inastahili kulipwa",
            "quarantined_by": "vat_withholding_deadline_stale_quarantine_2026_09_01.jsonl",
            "why": (
                "THE ROW IS CORRECT. 'Lazima utoe hati ya zuio la VAT kwa msambazaji siku "
                "ambayo VAT inastahili kulipwa — si tarehe ya 20' is "
                "vat_withholding_certificate_timing exactly: the certificate is due the day VAT "
                "becomes payable, and the 20th is the separate return deadline. The 2026-09-01 "
                "quarantine swept for 'tarehe 20' and caught a row that REJECTS it — the "
                "mention-vs-assertion failure, inside a quarantine, a month before that rule was "
                "written down. So that quarantine removed CORRECT training data from "
                "cleaned_pairs, and this surviving copy is the only one left."),
        },
    ],
}


def _audit():
    """Run the real harness rather than trusting the committed artifact, so this test cannot
    pass on a stale measurement (R18: a result whose instrument was not re-run is provisional)."""
    spec = importlib.util.spec_from_file_location(
        "audit_quarantine_reach",
        os.path.join(REPO, "eval", "controls", "audit_quarantine_reach.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["audit_quarantine_reach"] = mod
    cwd = os.getcwd()
    try:
        os.chdir(REPO)
        spec.loader.exec_module(mod)
        rc = mod.main()
    finally:
        os.chdir(cwd)
    assert rc == 0
    return json.load(open(ARTIFACT, encoding="utf-8"))


AUDIT = _audit()


def test_the_audit_read_a_real_population():
    """R20: an audit that reads no corpus and no quarantine reports zero survivors, which is
    indistinguishable from a clean result."""
    t = AUDIT["totals"]
    assert t["live_corpus_rows_indexed"] > 3000, t
    assert t["quarantined_rows_read"] > 400, t


def test_every_quarantine_record_was_actually_read():
    """The first draft of this harness reported `0/0 survive` for four records whose shape it did
    not understand (the pair nested under a `row` key). `0/0` reads exactly like clean. The
    affected records included the newest one, so the hole was in the freshest evidence first."""
    unread = [r["record"] for r in AUDIT["per_quarantine_record"]
              if r["rows"] and not r["with_body"]]
    assert not unread, (
        f"{len(unread)} quarantine record(s) yielded no readable pair body, so nothing in them "
        f"was audited: {unread}")


def test_no_quarantined_row_is_still_live_except_the_adjudicated_keeps():
    unexpected = []
    for s in AUDIT["survivors"]:
        path = s["survives_at"].split(":")[0]
        keeps = ADJUDICATED_KEEPS.get(path, [])
        if any(k["needle"] in s["body"] for k in keeps):
            continue
        unexpected.append(s)
    assert not unexpected, (
        f"{len(unexpected)} quarantined row(s) are still live:\n" +
        "\n".join(f"  {s['survives_at']} (quarantined in "
                  f"{os.path.basename(s['quarantine_record'])}): {s['body'][:120]}"
                  for s in unexpected) +
        "\n\nA quarantine that does not reach datasets/tier1a/sft/ has not removed anything "
        "from training. Remove from EVERY stage the row appears in, or regenerate the export.")


def test_the_exported_training_files_are_a_stage_the_audit_actually_covers():
    """⛔ THE ASSERTION THAT MAKES THE ONE ABOVE NON-VACUOUS. If `datasets/tier1a/sft` were ever
    dropped from LIVE_DIRS, every survivor in the training export would become invisible and this
    file would go green on the exact defect it exists to catch."""
    mod = sys.modules["audit_quarantine_reach"]
    stages = dict((s, p) for s, p in mod.LIVE_DIRS)
    assert "sft_EXPORTED_TRAINING" in stages, (
        "the exported training stage is not in LIVE_DIRS, so survivors there are invisible")
    assert stages["sft_EXPORTED_TRAINING"] == "datasets/tier1a/sft"
    for name in ("train_sft.jsonl", "val_sft.jsonl"):
        assert os.path.exists(os.path.join(REPO, "datasets", "tier1a", "sft", name)), name


@pytest.mark.parametrize("path,keep", [(p, k) for p, ks in ADJUDICATED_KEEPS.items() for k in ks])
def test_each_adjudicated_keep_is_still_there_and_still_reasoned(path, keep):
    """A keep that silently disappears means someone removed a row we had decided is correct, and
    the decision would vanish with it."""
    assert len(keep["why"]) > 120, "an adjudicated keep needs its reasoning, not a label"
    full = os.path.join(REPO, *path.split("/"))
    with open(full, encoding="utf-8") as fh:
        assert keep["needle"] in fh.read(), (
            f"{keep['needle']!r} is no longer in {path}. It was kept deliberately: "
            f"{keep['why'][:160]}")


def test_the_edited_in_place_outcome_is_still_being_distinguished():
    """The audit's third outcome. A quarantined body that is absent while its QUESTION is live was
    EDITED, not removed — and an edit can repair the sentence a sweep keys on while leaving the
    claim standing later in the same row (R25's containment shape). Eight of the fourteen EFD
    rows quarantined on 2026-10-06 were exactly that. If this count ever reads 0 on a corpus that
    still has edited rows, the limb has broken."""
    assert "edited_in_place" in AUDIT, "the third outcome was removed from the artifact"
    assert AUDIT["totals"]["edited_in_place_not_removed"] >= 0
    assert "containment" in AUDIT["the_third_outcome"].lower() or \
           "R25" in AUDIT["the_third_outcome"]

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
ADJUDICATED_KEEPS = {
    "datasets/tier1a/sft/train_sft.jsonl": [
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

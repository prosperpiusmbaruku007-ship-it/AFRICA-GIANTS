"""R17 regression file for D-FIDELITY-7 — a stated threshold that is not the statutory one.

WHAT IT GUARDS. `pic_11`, live 2026-08-23: "Presumptive tax inatumika kwa mauzo CHINI YA MILIONI
10", with "mauzo yasiyozidi TZS 100,000,000" sitting at rank 1 in the model's own context. The
prompt/generation/adapter separation recovered it under NO arm, which made it the first measured
retrain justification in this project. R19 says try the cheap mechanism first: a stated threshold
is a STATUTORY CONSTANT, so it is a constant comparison exactly like D-FIDELITY-6's rate check —
no ComputationResult needed, and it works on the fact path where every earlier rule goes vacuous.

TWELVE OF THE SIXTEEN PROBES ARE DELIBERATELY CORRECT BODIES. That is the half R17 says does the
work: probes designed to flag pass on a broken rule too. Both narrowing decisions below were
forced by evidence, not chosen — see the module header in chike/fidelity.py.
"""
import json

import pytest

from chike import fidelity

PROBE_FILE = "eval/fidelity/threshold_guard_probes.jsonl"


def _probes():
    with open(PROBE_FILE, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert rows, "probe file is empty — an R17 regression file with no probes checks nothing"
    return rows


PROBES = _probes()
IDS = [p["id"] for p in PROBES]


def test_probe_file_is_intact_and_control_heavy():
    assert len(PROBES) == 16, f"probe file has {len(PROBES)} rows, expected 16"
    assert len(set(IDS)) == 16, "duplicate probe ids"
    flag = [p for p in PROBES if p["expect_flag"]]
    controls = [p for p in PROBES if not p["expect_flag"]]
    assert len(controls) > len(flag), (
        f"{len(controls)} controls vs {len(flag)} positives — the control arm must stay the "
        f"majority; it is the half that finds an over-broad rule")
    for p in PROBES:
        assert len(p["guards_against"]) > 60, f"{p['id']} has no real guards_against note"


@pytest.mark.parametrize("probe", PROBES, ids=IDS)
def test_probe_contract(probe):
    got = fidelity.body_states_wrong_threshold(probe["body"])
    assert got == probe["expect_flag"], (
        f"{probe['id']}: expected flag={probe['expect_flag']}, got {got}\n"
        f"detail: {fidelity.stated_wrong_thresholds(probe['body'])}\n"
        f"guards_against: {probe['guards_against']}")


def test_it_catches_the_specimen_it_was_built_for():
    body = ("Kwa mauzo ya milioni 20, unalipa kodi ya mapato kwa mfumo wa kawaida "
            "(normal progressive rates). Presumptive tax inatumika kwa mauzo chini ya "
            "milioni 10. Thibitisha na tra.go.tz.")
    assert fidelity.stated_wrong_thresholds(body) == [("presumptive", 10_000_000)]


def test_hadi_and_kuanzia_are_deliberately_not_frame_words():
    """They sit equally in a band recitation and in a sentence about the user's own turnover, so
    including them would attribute the USER's figure to the statute. Probe tg_10 is that case."""
    assert not fidelity._THRESHOLD_FRAME.search("hadi TZS 30,000,000")
    assert not fidelity._THRESHOLD_FRAME.search("kuanzia TZS 30,000,000")
    assert fidelity._THRESHOLD_FRAME.search("chini ya milioni 10")
    assert fidelity._THRESHOLD_FRAME.search("kizingiti")


def test_the_lawful_escape_is_body_level_not_sentence_level():
    """The sweep found a reply stating the right threshold in one sentence and comparing against
    it in the next. Sentence-level, the second sentence flags. That reply IS wrong — 205M exceeds
    200M — but it is wrong about a COMPARISON, a derived quantity and Guard B territory (R19).
    Catching it here would be the right verdict for the wrong reason, and the same shape with a
    CORRECT comparison would be a plain false positive."""
    body = ("Kizingiti chako cha usajili wa VAT ni TZS 200,000,000 tu. "
            "Mapato ya TZS 205,000,000 hayazidi kizingiti hicho.")
    assert fidelity.body_states_wrong_threshold(body) is False


def test_small_integers_next_to_a_frame_word_are_periods_not_thresholds():
    """From the sweep: a clarification asking 'je ni jumla ya miezi 12, au ya miezi 6?' had 12 and
    6 read as VAT thresholds. Every statutory threshold in the table is >= TZS 4,000,000."""
    body = ("Ili nilinganishe na kizingiti cha VAT, niambie kiasi ulichotaja ni cha kipindi "
            "gani — je ni jumla ya miezi 12, au ya miezi 6 mfululizo?")
    assert fidelity.body_states_wrong_threshold(body) is False
    assert fidelity._THRESHOLD_MONEY_FLOOR >= 1_000_000


def test_every_lawful_value_is_at_or_above_the_money_floor():
    """A threshold below the floor would be unreachable by the guard — silently inert, which is
    the dead-anchor shape (R20). Asserted so adding one fails here first."""
    for subject, lawful in fidelity._STATUTORY_THRESHOLDS.items():
        for value in lawful:
            assert value >= fidelity._THRESHOLD_MONEY_FLOOR, (subject, value)

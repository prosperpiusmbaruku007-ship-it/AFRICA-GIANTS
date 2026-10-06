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

⛔ tg_17–tg_24 WERE ADDED 2026-10-06, WHEN THE GUARD WAS PRICED BEFORE WIRING, AND THEY ARE THE
REASON THE FIRST SIXTEEN WERE NOT ENOUGH. Swept over 5,599 stored replies, gold answers and
training pairs, the rule as built flagged 45 rows — including THREE GOLD ANSWERS a human had
asserted correct, one of them `eval_347`, the row the wiring existed to fix. All 22 tests were
green while that was true. R33: a probe set validated against variants of its own design measures
the generator, not the phenomenon; the first sixteen probes were authored by whoever wrote the
rule, and every one of them agreed with it.

Every added probe is VERBATIM from a committed corpus, with its locator in `source` — never a
paraphrase (R26: a five-word paraphrase was once enough to flip a correct body into a flagged one).
Six are correct bodies, two are true positives that mention VAT, so N3b cannot be widened into a
blanket release without failing a test.
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
    assert len(PROBES) == 24, f"probe file has {len(PROBES)} rows, expected 24"
    assert len(set(IDS)) == 24, "duplicate probe ids"
    flag = [p for p in PROBES if p["expect_flag"]]
    controls = [p for p in PROBES if not p["expect_flag"]]
    assert len(controls) > len(flag), (
        f"{len(controls)} controls vs {len(flag)} positives — the control arm must stay the "
        f"majority; it is the half that finds an over-broad rule")
    for p in PROBES:
        assert len(p["guards_against"]) > 60, f"{p['id']} has no real guards_against note"


def test_the_probes_drawn_from_corpora_name_where_they_came_from():
    """A probe quoted from a corpus without its locator cannot be re-checked against the corpus,
    and a paraphrase is indistinguishable from a quote once it is in the fixture."""
    sourced = [p for p in PROBES if p.get("source")]
    assert len(sourced) >= 8, (
        f"only {len(sourced)} probes carry a `source` locator; the 2026-10-06 additions are all "
        f"verbatim corpus rows and must each say which file and line")
    for p in sourced:
        assert "verbatim" in p["source"], f"{p['id']}: source does not claim verbatim quotation"
        assert ":" in p["source"] or "eval_" in p["source"], (
            f"{p['id']}: source has no row locator, so nobody can re-read the original")


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


# --- each narrowing limb pinned directly, so a silent regression in one is visible -----------
#
# R20: the probes above exercise the limbs TOGETHER. If two limbs each independently clear the
# same probe, one can be removed without any test going red — which is how a narrowing becomes
# decoration. These pin the limbs themselves.

def test_N1_negation_is_word_bounded():
    r"""⛔ A LOOSE MENTION RULE DOES NOT ADD NOISE -- IT DELETES FINDINGS.

    A bare `si\s` matches inside the ordinary Swahili word `kiasi `, and in the NSSF-fine
    propagation sweep (2026-10-05) that one unbounded alternative reclassified the single real
    false positive as a mere mention, silently shrinking the adjudicated set. A shorter list of
    findings is indistinguishable from progress.
    """
    assert fidelity._negated_at("ni SI TZS 11,000,000", len("ni SI TZS "))
    # `kiasi` must NOT read as a negation
    s = "kiasi cha TZS 11,000,000"
    assert not fidelity._negated_at(s, s.index("TZS"))
    # a negative VERB form is not a negated claim -- it denies the USER reached the threshold,
    # while still asserting the threshold
    s2 = "haujafika kizingiti cha TZS 11,000,000"
    assert not fidelity._negated_at(s2, s2.index("TZS"))


def test_N2_a_frame_must_reach_the_amount_without_crossing_another():
    """The user's own turnover is not a threshold claim. This is the limb that knows it."""
    s = "Kwa mauzo ya TZS 250,000,000 (zaidi ya TZS 200,000,000)"
    pos = [m.start() for m in __import__("re").finditer(r"TZS", s)]
    assert not fidelity._frame_reaches(s, pos[0], pos), "250M has no frame before it"
    assert fidelity._frame_reaches(s, pos[1], pos), "200M has `zaidi ya` immediately before it"


def test_N3b_admits_only_the_vat_magnitudes_never_the_whole_table():
    """If N3b is ever widened to 'lawful anywhere', the guard loses its most important true
    positive: 11,000,000 is a lawful PRESUMPTIVE band edge and a fabricated EFD threshold."""
    assert fidelity.body_states_wrong_threshold(
        "Kizingiti cha EFD ni TZS 11,000,000, au usajili wa VAT.")
    assert not fidelity.body_states_wrong_threshold(
        "Lazima utumie EFD ukifikia kizingiti cha VAT cha TZS 200,000,000.")

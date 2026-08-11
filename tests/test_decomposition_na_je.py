"""R17 regression file for the `na je` split and the measure-matched preamble carry.

WHAT THIS FILE IS FOR. `eval/decomposition_gate/na_je_preamble_019.jsonl` was authored BEFORE
the rule, in both directions, because the corpus contains four `na je` questions and all four
want splitting — it cannot show a single question that merely CONTAINS the connector, and it
cannot show a second half that would be CORRUPTED by inheriting the first half's figure. Nine
of the nineteen probes fail on the pre-change decomposer; the other ten are the false-positive
direction and must keep passing forever.

WIRED TO FAIL ON ADDITIONS. Three pins below fail when someone widens this without probes:
  * the split-capable connector set is enumerated exactly — promoting another orphan (`pia`,
    `lakini pia`, `na aidha`, `pia ningependa`, `pia niambie`) fails here first;
  * the preamble measure map is pinned to its single entry (turnover -> VAT/EFD), so adding a
    second measure is a deliberate edit with a test to update;
  * every probe is asserted for content conservation, so no future split may drop a fragment.
IF YOU ADD A CONNECTOR OR A MEASURE: add probes in BOTH directions first, then update the pin
in the same commit. Do not relax the pin to make a change pass.

THE BOUND ON WHAT THIS FIXES, stated so nobody reads it as more than it is: four other
multi-domain corpus questions (eval_319/320/323/327) are not split either and are answered in
full anyway, because the rules engine enumerates the payroll levies independently. The drop
only happens when the two asks are in DIFFERENT routes — one compute, one threshold or
registration — which is the only case where decomposition is the mechanism that must separate
them. Cannot be asserted offline; it is measured in scratch/decomp_drop_live.json.
"""
import json
import re

import pytest

from chike import decomposition
from chike.decomposition import decompose_query

PROBE_FILE = "eval/decomposition_gate/na_je_preamble_019.jsonl"


def _probes():
    with open(PROBE_FILE, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


PROBES = _probes()
IDS = [p["id"] for p in PROBES]


# ── the probe file itself ────────────────────────────────────────────────────────

def test_probe_file_is_intact():
    assert len(PROBES) == 19, f"probe file has {len(PROBES)} rows, expected 19"
    assert len(set(IDS)) == 19, "duplicate probe ids"
    for p in PROBES:
        assert p["guards_against"].strip(), f"{p['id']} has no guards_against note"
        assert p["family"] in {
            "na_je_two_asks", "na_je_preamble_needed", "na_je_single_question",
            "substring_hazard", "preamble_must_not_carry", "preamble_needed",
            "control_existing_connector",
        }, p["family"]
    # Both directions must stay represented: a file of positives only is the failure mode R17
    # exists to prevent.
    must_split = [p for p in PROBES if p["expect_split"]]
    must_not = [p for p in PROBES if not p["expect_split"]]
    assert len(must_split) == 11 and len(must_not) == 8, (len(must_split), len(must_not))


# ── the contract, probe by probe ─────────────────────────────────────────────────

@pytest.mark.parametrize("probe", PROBES, ids=IDS)
def test_probe_contract(probe):
    parts = decompose_query(probe["question"])
    assert (len(parts) > 1) == probe["expect_split"], (
        f"{probe['id']}: expected split={probe['expect_split']}, got {len(parts)} parts "
        f"-> {parts}\nguards_against: {probe['guards_against']}")
    assert len(parts) == probe["expect_n_parts"], f"{probe['id']}: {parts}"

    for i, needles in enumerate(probe.get("expect_part_contains") or []):
        for needle in needles:
            assert needle.lower() in parts[i].lower(), (
                f"{probe['id']} part[{i}] is missing {needle!r}: {parts[i]!r}")
    for i, needles in enumerate(probe.get("expect_part_excludes") or []):
        for needle in needles:
            assert needle.lower() not in parts[i].lower(), (
                f"{probe['id']} part[{i}] must NOT contain {needle!r} — this is the "
                f"corruption direction: {parts[i]!r}\n{probe['guards_against']}")


_CONNECTOR_TEXT = re.compile(
    decomposition._SPLIT_PATTERN + r"|" + decomposition._NA_JE, re.IGNORECASE)


@pytest.mark.parametrize("probe", PROBES, ids=IDS)
def test_no_probe_loses_content(probe):
    """A split may consume the connector; it may never drop a word of the question.

    MODE B — split, fragment lost — is the failure the fragment floor used to cause: the old
    paths drop a short segment and split the rest. The `na je` path vetoes the whole split
    instead. Preamble carrying can only add text, never remove it.
    """
    parts = decompose_query(probe["question"])
    joined = " ".join(parts).lower()
    stripped = _CONNECTOR_TEXT.sub(" ", probe["question"])
    lost = [w for w in re.findall(r"\w+", stripped.lower()) if w not in joined]
    assert lost == [], f"{probe['id']} lost {lost} — parts: {parts}"


# ── pins that fail when the rule is widened without probes ───────────────────────

def test_only_na_je_was_promoted_out_of_the_orphan_set():
    """MULTI_PART_SIGNALS detects; _SPLIT_PATTERN + _NA_JE split. The gap between them is the
    orphan set, and it is deliberate: bare `pia` is adverbial (eval_180) and the other four
    appear in zero corpus questions. Promoting one is a behaviour change that needs its own
    probes in both directions — this pin fails first."""
    detect = [p.replace(r"\b", "") for p in decomposition.MULTI_PART_SIGNALS]
    splitter = re.compile(decomposition._SPLIT_PATTERN + r"|" + decomposition._NA_JE,
                          re.IGNORECASE)
    orphans = sorted(c for c in detect if not splitter.search(c))
    assert orphans == ["lakini pia", "na aidha", "pia", "pia niambie", "pia ningependa"], orphans


def test_the_preamble_carry_maps_exactly_one_measure():
    """Turnover -> VAT/EFD, and nothing else. pre_02 and pre_03 are the reason: a salary is a
    figure too, and a real turnover figure must not be offered to a headcount-triggered
    obligation. A second measure needs a probe in each direction before this pin moves."""
    assert decomposition._TURNOVER_CUE.search("mauzo yangu ni TZS 50,000,000")
    assert not decomposition._TURNOVER_CUE.search("mshahara wa mfanyakazi ni TZS 800,000")
    assert decomposition._TURNOVER_THRESHOLD_DOMAIN.search("nahitaji EFD?")
    assert decomposition._TURNOVER_THRESHOLD_DOMAIN.search("je nasajili VAT")
    for other in ("nahitaji kusajili NSSF?", "SDL ni kiasi gani", "kima cha chini cha mshahara",
                  "nahitaji kusajili OSHA?", "WCF ni kiasi gani"):
        assert not decomposition._TURNOVER_THRESHOLD_DOMAIN.search(other), other


def test_the_fragment_floor_is_a_veto_not_a_filter_on_the_na_je_path():
    """The shipped '?' and connector paths FILTER short segments — they split the rest and the
    dropped fragment is gone. On the `na je` path a short segment vetoes the split entirely, so
    a sub-question can never be silently discarded (naje_neg_04)."""
    q = "Mauzo yangu ni TZS 300,000,000 kwa mwaka na je VAT?"
    assert decompose_query(q) == [q]
    assert decomposition._split_na_je(q) == []


def test_word_boundaries_hold_against_the_substring_hazard():
    """`na jengo` / `na jenereta` contain the literal 'na je'. _SPLIT_PATTERN is applied with no
    boundaries, so this is the mistake a hurried edit makes."""
    for q in ["Nina duka na jengo langu mwenyewe — nahitaji leseni ya biashara ya aina gani?",
              "Nina duka na jenereta ya umeme — je nahitaji risiti ya EFD kwa mauzo yote?",
              "Kampuni yangu ina jengo na jenereta — nalipa kodi gani?"]:
        assert decompose_query(q) == [q], q

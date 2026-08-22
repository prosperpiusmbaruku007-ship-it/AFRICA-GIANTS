# -*- coding: utf-8 -*-
"""Swahili orthographic variants in the cue lists — presence, breadth, and the routing
case that motivated them.

WHY THESE EXIST (2026-08-14). A real user wrote "mfuko wa hifazi ya jamii". `hifazi` is
the ordinary dh->z spelling of `hifadhi`; it matched no cue, `detect_intent` returned
`none`, and an NSSF question fell to the fact path, which answered TZS 20,000 against a
stated salary of TZS 800,000. The correct employer share is TZS 80,000. Nothing else was
broken: `parse_amounts` read "laki nane" as 800000 and `nssf_party` read "employer".
ONE MISSPELLING was the whole blocker.

WHY HAND-WRITTEN AND NOT GENERATED. A character-collapsing normaliser was designed,
measured and REJECTED. Applied to user text it sits upstream of 52 compiled regexes,
40 of them in swahili_numbers.py, and Swahili numerals are the vocabulary richest in
`th`:

    laki thelathini            3,000,000  ->    100,000   (30x understatement)
    wafanyakazi thelathini na watano  35  ->          5
    themanini elfu                    80  ->      1,000

It does not fail loudly; it returns a different valid number, in the money direction —
the decimal-separator failure mode, reintroduced by the fix meant to prevent it. The
general form of the objection is in PROGRESS under the `waajiri` -> `wajiri` observation:
287 of 290 measured gains came from ONE substring collapse that was benign only because
the two words happened to be singular/plural of the same thing.

THE MAINTENANCE COST this file pays down: hand-written variants are O(new cues) forever
and invisible when forgotten, which is exactly how `hifadhi` got here. `test_every_
swahili_digraph_phrase_has_its_variant` converts "someone must remember" into "the suite
fails".
"""
import json
import os
import re

from chike import classification, routing, swahili_numbers as swn

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROBES = os.path.join(_ROOT, "eval", "refusal_gate",
                       "orthographic_variant_in_scope_012.jsonl")

# The dh->z / th->s / gh->g substitutions, as applied to whole words.
_SUBS = {"ardhi": "arzi", "bidhaa": "bizaa", "dhahabu": "zahabu", "thamani": "samani",
         "forodha": "foroza", "hifadhi": "hifazi", "gharama": "garama",
         "adhibiwa": "azibiwa", "dhamana": "zamana", "tathmini": "tasmini",
         "uthamini": "usamini"}

# ENGLISH PHRASES TAKE NO VARIANT. dh->z / th->s is a Swahili phonological process on
# Arabic-derived loanwords. "threshold" and "arm's length" are English embedded in
# code-switched Swahili; nobody writes "sreshold". This allowlist is a DECISION ON THE
# RECORD, not an omission — the presence test below would otherwise flag them forever.
_ENGLISH_NO_VARIANT = {"arm's length", "vat threshold"}

# WITHHELD DELIBERATELY: for each of these, the STANDARD spelling already refuses a
# realistic in-scope question TODAY (see the ov_02/ov_04/ov_08 probe rows). Mirroring
# them would have doubled a live defect rather than closed a gap. They are pre-existing
# over-breadth, logged as their own item, and their probes pin today's behaviour so a
# future narrowing pass has to change this file visibly.
_WITHHELD_PENDING_NARROWING = {"kipande cha ardhi", "naagiza bidhaa", "forodha"}


def _probes():
    with open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    # NON-EMPTY ASSERTION (2026-08-22, dead-anchor census) — see test_minimum_wage._probes.
    assert rows, f"{_PROBES} is empty — the tests looping over it would pass vacuously"
    return rows


def _all_phrases():
    """(list_name, phrase) for every cue list a variant could belong to."""
    out = []
    for mod in (routing, classification):
        for name in dir(mod):
            if not name.isupper() or name.startswith("__"):
                continue
            v = getattr(mod, name)
            if isinstance(v, (list, tuple)):
                for x in v:
                    if isinstance(x, str):
                        out.append((f"{mod.__name__}.{name}", x))
                    elif isinstance(x, (list, tuple)) and len(x) == 2 \
                            and isinstance(x[1], (list, tuple)):
                        for y in x[1]:
                            if isinstance(y, str):
                                out.append((f"{mod.__name__}.{name}", y))
    cfg = json.load(open(os.path.join(_ROOT, "kaggle", "chike_config.json"),
                         encoding="utf-8"))
    for key in ("ooc_phrases", "in_scope_phrases"):
        for p in cfg.get(key, []):
            out.append((f"config.{key}", p))
    return out


def _variant_of(phrase):
    out = phrase
    for std, var in _SUBS.items():
        out = out.replace(std, var)
    return out if out != phrase else None


# ---------------------------------------------------------------------------
# 1. the gap that let this through: a variant missing from a list
# ---------------------------------------------------------------------------

def test_every_swahili_digraph_phrase_has_its_variant():
    """THE SELF-ENFORCING CHECK. Add a cue containing dh/th/gh and forget its variant,
    and this fails — instead of a user finding it, which is how `hifadhi` was found."""
    missing = []
    by_list = {}
    for lst, p in _all_phrases():
        by_list.setdefault(lst, set()).add(p)
    for lst, p in _all_phrases():
        if p in _ENGLISH_NO_VARIANT or p in _WITHHELD_PENDING_NARROWING:
            continue
        var = _variant_of(p)
        if var and var not in by_list[lst]:
            missing.append((lst, p, var))
    assert not missing, (
        "cue phrases whose Swahili orthographic variant is missing from the same list:\n"
        + "\n".join(f"  {l}: {p!r} needs {v!r}" for l, p, v in missing))


def test_the_english_allowlist_is_actually_english():
    """A guard on the guard: the allowlist must not become a dumping ground for Swahili
    phrases someone did not want to write a variant for."""
    for p in _ENGLISH_NO_VARIANT:
        assert re.search(r"threshold|arm's|length|duty|pricing|market|stock", p), p


# ---------------------------------------------------------------------------
# 2. breadth — R17: the additions must not refuse an in-scope question
# ---------------------------------------------------------------------------

def test_the_variant_probe_file_is_present_and_intact():
    probes = _probes()
    assert len(probes) == 12, len(probes)
    for p in probes:
        assert p["guards_against"], p["id"]
        assert "question_standard" in p, p["id"]


def test_no_variant_refuses_an_in_scope_question():
    """R17's over-breadth gate, for the variant additions specifically.

    The corpus sweep found 0 false positives on all 27 candidates — which R17 says is
    weak evidence, and here it was provably weak: we measured 0 variant spellings across
    795 eval and 17,258 training questions. These probes are the only instrument that
    can see an over-broad variant."""
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    wrong = []
    for p in _probes():
        assert p["expected_refusal"] is False, p["id"]     # every probe is in-scope
        if not classification.classify(p["question"], ooc, in_scope):
            hits = [ph for ph in ooc if ph in p["question"].lower()]
            wrong.append((p["id"], hits, p["guards_against"]))
    assert not wrong, (
        "a variant addition refuses an IN-SCOPE question:\n"
        + "\n".join(f"  {i}: matched {h}\n     {g}" for i, h, g in wrong))


def test_withheld_variants_are_absent_and_their_defect_is_pinned():
    """The three phrases whose standard form ALREADY over-refuses.

    Not mirroring them is the decision; this test is what stops someone 'completing the
    set' later without noticing they are doubling a live wrong refusal. When the standard
    phrase is narrowed, this test and the ov_02/ov_04/ov_08 rows change together."""
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    for std in _WITHHELD_PENDING_NARROWING:
        var = _variant_of(std)
        assert var not in ooc, (
            f"{var!r} was added while its standard form {std!r} still over-refuses — "
            "narrow the standard phrase first, then add both together")
    # the pre-existing defect itself, so it cannot be quietly 'fixed' by deletion.
    # THIS TEST ASSERTS A WRONG ANSWER IS STILL WRONG. That is deliberate and it is the
    # R17 corollary in its intended form: the row is a pin, not an endorsement. When the
    # standard phrase is narrowed, this loop fails and the fixer must update the probe
    # rows in the same commit — which is the visibility the pin exists to buy.
    for p in _probes():
        if p["standard_refused_today"]:
            assert not classification.classify(p["question_standard"], ooc, in_scope), (
                f"{p['id']}: the standard spelling no longer over-refuses — if that was "
                "deliberate, add the withheld variant and flip standard_refused_today")


# ---------------------------------------------------------------------------
# 3. the routing case that motivated all of it
# ---------------------------------------------------------------------------

def test_the_hifazi_nssf_question_now_routes_to_compute():
    """The verbatim question from the 2026-08-14 transcript row."""
    q = ("Mshahara wa wafanyakazi wangu ni laki nane kwa mwezi mimi kama mwajiri "
         "nachangia shingapi kwenye mfuko wa hifazi ya jamii")
    # `shingapi` is a SEPARATE, still-open gap (the money-ask contraction) — so this
    # asserts the levy is now detected, which is what the dh->z variant fixes.
    assert routing._natural_levy(q.lower()) == "nssf", routing._natural_levy(q.lower())
    # and with the money-ask spelled the way the gate can currently see it, it routes:
    assert routing.detect_intent(q.replace("shingapi", "ngapi")) == "nssf"


def test_the_figures_were_never_the_problem():
    """Pins the finding that made this a routing fix and not an extraction one."""
    q = "Mshahara wa wafanyakazi wangu ni laki nane kwa mwezi"
    assert [str(x) for x in swn.parse_amounts(q)] == ["800000"]


def test_normaliser_would_have_corrupted_numerals():
    """The measurement that disqualified the rejected approach, kept executable.

    If anyone proposes a text normaliser again, this is the counter-example, and it runs."""
    def th_to_s(s):
        return s.lower().replace("th", "s")
    assert [str(x) for x in swn.parse_amounts("laki thelathini")] == ["3000000"]
    assert [str(x) for x in swn.parse_amounts(th_to_s("laki thelathini"))] != ["3000000"]

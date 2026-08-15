# -*- coding: utf-8 -*-
"""Swahili concord in the cue lists — CLASS COMPLETENESS, not a list of members.

WHY THIS FILE EXISTS (2026-08-15). Every cue list in routing.py grew one observed failure at
a time. For an open lexical set that is the only option — you cannot know the next word a
user will invent. For a CLOSED grammatical class it is a defect, because the class can be
written out from the grammar in one sitting. An audit found 11 of 37 members handled, and in
every class the pattern was the same: the high-frequency member present, the rest absent.
That is the signature of failure-driven growth, not of design.

WHAT THIS TEST ASSERTS, AND WHY IT IS SHAPED THIS WAY. It does not enumerate the members it
expects — an enumeration would be one more hand-maintained list, with the same failure mode
as the thing it is checking. It applies the PARADIGM to whatever is in the cue lists today
and demands that each derived counterpart be RECOGNISED. Add a cue tomorrow and forget its
counterpart, and this fails; the suite, not a user, finds it.

RECOGNISED, NOT PRESENT — the distinction is load-bearing. Cue lists match with
`phrase in text`, so 27 of the 58 derived counterparts were ALREADY matched via a shorter
existing cue: "tunauza" contains "nauza", "tumeuza ardhi" contains "uza ardhi". Requiring
literal membership would have added 27 lines that change no behaviour, and worse, would have
taught the next maintainer that this file wants list-stuffing rather than coverage.

THE LUCK IS TENSE-SHAPED, AND THAT IS THE FINDING. The colloquial 1sg present `na-` is a
substring of the 1pl `tuna-`, so present-tense 1pl worked by accident. `nime-`, `nili-` and
`nita-` are NOT substrings of `tume-`, `tuli-`, `tuta-`. The router understood "we pay" and
never understood "we PAID" or "we WILL pay" — a gap with a precise shape that no failure log
would ever have named, because it is a property of the paradigm and not of any one question.

CLOSURE IS LINEAR. Concord is functional: `mauzo` takes `yangu`/`yetu` and nothing else, so
each cue gains exactly one counterpart. The cross-product fear (10 nouns x 15 possessives)
is not a real cost, which is why this was affordable as a single item.
"""
import json
import os
import re

import pytest

from chike import classification, routing

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "concord_1pl_in_scope_020.jsonl")

# ---------------------------------------------------------------------------
# THE PARADIGMS — written from the grammar, once.
# ---------------------------------------------------------------------------
# Possessive: the STEM carries person (-angu = my, -etu = our); the PREFIX carries noun
# class and is identical in both. That is the whole reason closure is linear.
POSSESSIVE = {"wangu": "wetu", "yangu": "yetu", "langu": "letu", "changu": "chetu",
              "vyangu": "vyetu", "zangu": "zetu", "pangu": "petu", "kwangu": "kwetu",
              "mwangu": "mwetu"}

# Subject prefix fused with tense. Ordered longest-first; `na-` last, because it is the
# colloquial reduction of `nina-` and both therefore map onto the same 1pl form. That is a
# fact about the language, not an ambiguity to resolve.
SUBJECT = [("nime", "tume"), ("nili", "tuli"), ("nita", "tuta"), ("nina", "tuna"),
           ("niki", "tuki"), ("nika", "tuka"), ("na", "tuna")]

# Interrogative concord on `-ngapi`: FIVE members, one per countable noun class.
# `yangapi`/`zangapi`/`pangapi`/`kiangapi` are not Swahili — cl.4 and cl.6 take
# `mingapi`/`mangapi` and cl.10 takes the bare form. An earlier audit listed eight and was
# wrong; this table is the correction, kept executable so it cannot drift back.
NGAPI = {"ngapi": "cl.9/10", "wangapi": "cl.2", "mingapi": "cl.4",
         "mangapi": "cl.6", "vingapi": "cl.8"}

# ---------------------------------------------------------------------------
# EXEMPTIONS — every one a decision on the record, never a convenience.
# ---------------------------------------------------------------------------
# An English phrase has no Swahili concord. Same principle as the digraph work's
# `_ENGLISH_NO_VARIANT`: state it, so it is a decision rather than an omission.
_ENGLISH = {"my turnover", "my sales", "vat registered", "register for vat",
            "vat registration", "vat threshold", "efd machine", "arm's length",
            "minimum wage", "gn 605a", "gn605a"}

# WITHHELD, with the same rule the digraph work established: do not mirror a phrase whose
# 1sg form ALREADY over-refuses an in-scope question, because that doubles a live defect
# instead of closing a gap.
_WITHHELD = {
    "tukiagiza": (
        "`nikiagiza` refuses 'nikiagiza bidhaa kutoka nje je nasajili VAT lini' — an "
        "IN-SCOPE VAT-registration question. It is a fourth over-broad OOC phrase, found "
        "by this exercise and not by the digraph sweep (it has no digraph in it). Narrow "
        "`nikiagiza` first, then add both together."),
}

# NOT WITHHELD, and the reason is worth recording because it looks like an omission:
# `tunaagiza bidhaa` needs no exemption even though `naagiza bidhaa` is equally over-broad.
# It is already matched — `naagiza bidhaa` is a substring of `tu-naagiza bidhaa`. Withholding
# it would have bought nothing, which is a fact about the WITHHOLDING TOOL: it cannot protect
# 1pl speakers from an over-broad 1sg present-tense phrase, because substring matching has
# already leaked it. The over-refusal logged as ov_04 is therefore wider than ov_04 records.
_LEAKS_ANYWAY = "tunaagiza bidhaa"


def _cue_lists():
    """{qualified name: [phrases]} for every cue list concord could apply to."""
    out = {}
    for mod in (routing, classification):
        for name in dir(mod):
            if not name.isupper() or name.startswith("__"):
                continue
            v = getattr(mod, name)
            if not isinstance(v, (list, tuple)):
                continue
            phrases = []
            for x in v:
                if isinstance(x, str):
                    phrases.append(x)
                elif isinstance(x, (list, tuple)) and len(x) == 2 \
                        and isinstance(x[1], (list, tuple)):
                    phrases.extend(y for y in x[1] if isinstance(y, str))
            if phrases:
                out[f"{mod.__name__.split('.')[-1]}.{name}"] = phrases
    cfg = json.load(open(os.path.join(_ROOT, "kaggle", "chike_config.json"),
                         encoding="utf-8"))
    out["config.ooc_phrases"] = list(cfg["ooc_phrases"])
    out["config.in_scope_phrases"] = list(cfg["in_scope_phrases"])
    return out


def _possessive_counterparts(phrase):
    for a, b in POSSESSIVE.items():
        if re.search(rf"\b{a}\b", phrase):
            yield re.sub(rf"\b{a}\b", b, phrase)
        if re.search(rf"\b{b}\b", phrase):
            yield re.sub(rf"\b{b}\b", a, phrase)


def _subject_counterparts(phrase):
    head = phrase.split()[0]
    for a, b in SUBJECT:
        if head.startswith(a):
            yield phrase.replace(head, b + head[len(a):], 1)
            return


def _recognised(counterpart, phrases):
    """The property that matters: would this cue list MATCH a question containing it?

    Not 'is it in the list' — a shorter existing cue that is a substring of the counterpart
    already matches every text the counterpart would."""
    return any(p in counterpart for p in phrases)


# ---------------------------------------------------------------------------
# 1. THE SELF-ENFORCING CHECK
# ---------------------------------------------------------------------------

def test_every_cue_with_a_person_form_has_its_concord_counterpart():
    """Add a 1sg cue and forget the 1pl one, and this fails.

    This is the digraph test's shape applied to grammar instead of orthography, and it is
    the reason the concord classes were closed as ONE item rather than as four separate
    routing fixes: each of those fixes was one member of a class this test now holds shut."""
    missing = []
    for lname, phrases in _cue_lists().items():
        for p in phrases:
            if p in _ENGLISH:
                continue
            for kind, gen in (("possessive", _possessive_counterparts),
                              ("subject", _subject_counterparts)):
                for c in gen(p):
                    if c in _WITHHELD or c == _LEAKS_ANYWAY:
                        continue
                    if not _recognised(c, phrases):
                        missing.append((lname, kind, p, c))
    assert not missing, (
        "cue phrases whose concord counterpart is not recognised by the same list:\n"
        + "\n".join(f"  {l} [{k}]: {p!r} needs {c!r}" for l, k, p, c in missing))


def test_the_english_exemptions_are_actually_english():
    """A guard on the guard — the same one the digraph test carries, for the same reason:
    an exemption set is the obvious place to hide a phrase nobody wanted to think about."""
    for p in _ENGLISH:
        assert re.search(r"[a-z]", p) and not re.search(
            r"\b(?:yangu|yetu|wangu|wetu|langu|letu|zangu|zetu)\b", p), p
        assert re.search(r"my |vat|efd|arm's|minimum|gn ?605a", p), p


def test_the_withheld_counterpart_still_has_a_live_reason():
    """`tukiagiza` is withheld because `nikiagiza` over-refuses. If that stops being true,
    this fails and the withholding must be revisited in the same commit — the pin, not the
    endorsement. Same mechanism as test_withheld_variants_are_absent_and_their_defect_is_pinned.
    """
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    assert "tukiagiza" not in ooc
    q = "nikiagiza bidhaa kutoka nje je nasajili VAT lini"
    assert not classification.classify(q, ooc, in_scope), (
        "`nikiagiza` no longer over-refuses — if that was deliberate, add `tukiagiza` and "
        "delete this exemption together")


def test_the_withholding_tool_cannot_protect_present_tense_1pl():
    """The finding that made `tunaagiza bidhaa` need no exemption, kept executable.

    Substring matching means an over-broad colloquial 1sg present cue ALREADY refuses the
    1pl question. Withholding its counterpart buys nothing, and believing otherwise would
    have left a wrong refusal logged as narrower than it is."""
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    assert "tunaagiza bidhaa" not in ooc
    q = "Tunaagiza bidhaa kutoka Kenya chini ya USD 2,000 je tunatumia STR"
    assert not classification.classify(q, ooc, in_scope), (
        "if this now passes, the 1sg `naagiza bidhaa` was narrowed — update ov_04 too")


# ---------------------------------------------------------------------------
# 2. the interrogative class, whose members are gate-assigned by SEMANTICS
# ---------------------------------------------------------------------------

def test_the_ngapi_class_is_complete_and_correctly_split():
    """All five members known; and the money/non-money split is by MEANING, not by grammar.

    Money in Swahili is cl.9/10 (shilingi, fedha, pesa), so a money ask is always the bare
    `ngapi`. mingapi/mangapi/vingapi count periods and objects. Putting them in _MONEY_ASK
    'to complete the class' would be a category error wearing a grammar costume — the exact
    mistake a mechanical closure makes and a grammatical one does not."""
    for m in NGAPI:
        assert m == "ngapi" or any(m == x or x.endswith(" " + m)
                                   for x in routing._NONMONEY_ASK), m
    for m in ("mingapi", "mangapi", "vingapi", "wangapi"):
        assert m not in routing._MONEY_ASK, f"{m} counts things; it is not a money ask"


def test_the_contraction_is_an_explicit_money_ask():
    """`shingapi` = `shilingi ngapi`. It must survive a co-occurring count ask, which is
    what _EXPLICIT_MONEY_ASK is for — the override that would otherwise have made the fix
    silently conditional on no count word being present."""
    assert "shingapi" in routing._MONEY_ASK
    assert "shingapi" in routing._EXPLICIT_MONEY_ASK
    assert routing._has_money_ask("tunalipa shingapi kwa maduka mangapi")


# ---------------------------------------------------------------------------
# 3. R17 breadth — authored probes, because the corpus cannot supply them
# ---------------------------------------------------------------------------

def _probes():
    with open(_PROBES, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_the_probe_file_is_present_and_carries_both_polarities():
    probes = _probes()
    assert len(probes) == 20, len(probes)
    assert sum(1 for p in probes if p["kind"] == "pair") == 10
    assert sum(1 for p in probes if p["kind"] == "negative") == 10, (
        "the negatives are the point — R17 exists to police over-breadth, and a probe set "
        "of only positives cannot see it")
    for p in probes:
        assert p["guards_against"], p["id"]


@pytest.mark.parametrize("probe", [p for p in _probes() if p["kind"] == "pair"],
                         ids=lambda p: p["id"])
def test_a_1pl_question_routes_exactly_like_its_1sg_twin(probe):
    """The PAIRING assertion, which is stronger than 'it routes to X'.

    A question asked as 'we' must reach the same engine as the identical question asked as
    'I'. Pinning the expected route instead would pass by coincidence if both broke the same
    way; this cannot."""
    got = routing.detect_intent(probe["question"])
    twin = routing.detect_intent(probe["question_1sg"])
    assert got == twin, (
        f"{probe['id']}: 1pl -> {got!r} but 1sg -> {twin!r}\n"
        f"  1pl: {probe['question']}\n  1sg: {probe['question_1sg']}\n"
        f"  guards: {probe['guards_against']}")
    assert got == probe["expected_intent"], f"{probe['id']}: both twins moved to {got!r}"


@pytest.mark.parametrize("probe", [p for p in _probes() if p["kind"] == "negative"],
                         ids=lambda p: p["id"])
def test_the_negatives_are_unchanged_by_the_closure(probe):
    """Over-breadth, in the shapes the corpus never supplied. 38 of the additions have zero
    corpus occurrences, so the 5,510-row sweep could not have found a defect in them."""
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    assert routing.detect_intent(probe["question"]) == probe["expected_intent"], probe["id"]
    assert classification.classify(probe["question"], ooc, in_scope) is \
        probe["expected_in_scope"], f"{probe['id']}: {probe['guards_against']}"


# ---------------------------------------------------------------------------
# 4. the two live wrong answers this closure was ultimately for
# ---------------------------------------------------------------------------

def test_both_live_2026_08_14_questions_now_reach_their_engine():
    """`shingapi` was the last blocker on BOTH. The dh->z work fixed the levy detection on
    the NSSF one; this fixes the money-ask on both."""
    sdl = ("Nina wafanyakazi 14 mishahara yote kwa mwezi ni milioni 6 ile ya mafunzo ya "
           "ufundi nalipa shingapi")
    nssf = ("Mshahara wa wafanyakazi wangu ni laki nane kwa mwezi mimi kama mwajiri "
            "nachangia shingapi kwenye mfuko wa hifazi ya jamii")
    assert routing.detect_intent(sdl) == "sdl"
    assert routing.detect_intent(nssf) == "nssf"

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
import inspect
import json
import os
import re

import pytest

from chike import classification, routing

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "concord_1pl_in_scope_020.jsonl")
_OBJ_PROBES = os.path.join(_ROOT, "eval", "refusal_gate",
                           "object_concord_in_scope_022.jsonl")

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

# OBJECT INFIX — the THIRD person-marking paradigm, added 2026-08-15 after it produced two
# live wrong answers (nat_08, nat_04). It sits between the tense marker and the verb stem and
# the class is closed at five. `-m-` surfaces as `-mw-` before a vowel and is commonly written
# `-mu-` before a consonant; those are SPELLINGS of one member, not extra members.
OBJECT_INFIX = {"ni": "me (1sg)", "ku": "you (2sg)", "m": "him/her (cl.1)",
                "tu": "us (1pl)", "wa": "them (cl.2)"}

# Where a cue list has a compiled companion carrying the same class, RECOGNITION must consult
# it — a counterpart the regex matches needs no list entry, exactly as a counterpart covered by
# a shorter existing cue needs none.
_CONCORD_REGEXES = {
    "routing._APPLICABILITY_CUES": routing._APPLICABILITY_CONCORD,
    "routing._NSSF_EMPLOYEE_CUES": routing._NSSF_EMPLOYEE_CONCORD,
}

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

# WITHHELD FROM THE OBJECT PARADIGM — a MEASURED gap, deferred with its reason, not hidden.
#
# The object-concord derivation, on its first run, flagged ten counterparts in
# `_WAGE_PAY_CUES`. They are real: `nawalipa` (present) is in the list and `nimewalipa`
# (perfect) is not — the same tense gap the 2026-08-15 subject closure was about, arriving
# through the object paradigm instead. And the gap is LIVE, not theoretical:
#
#     "wananilipa laki mbili kwa mwezi je ni halali kisheria"   -> routes to fact/RAG
#     "mwajiri ananilipa 150000 kwa mwezi je nakiuka sheria"    -> routes to fact/RAG
#     "nimemlipa mfanyakazi wangu 150000 ... je ni halali"      -> minimum_wage  (control)
#
# An EMPLOYEE asking whether the wage they are paid is lawful is exactly the question the
# deterministic minimum_wage route was built for after th_16, and it does not reach it.
#
# THEY ARE WITHHELD ANYWAY, and the reason is scope discipline rather than doubt.
# `_WAGE_PAY_CUES` gates a DIFFERENT route from the one this item is closing, and it is the
# route with the worst history of over-broad additions in this file: the first version of that
# list included the noun `mshahara` and the blast-radius sweep caught it stealing FIVE real
# gate questions (eval_118/119/120/126/382). Widening it belongs in its own commit with its
# own sweep and its own probes, not folded silently into an NSSF/SDL fix.
#
# The pin below is what stops this becoming a forgotten TODO: it asserts the defect is still
# live, so whoever closes it will find this test failing and must remove the exemption in the
# same commit.
_WITHHELD_OBJECT = {
    "nimekulipa", "nimewalipa", "nimekulipia", "nimewalipia", "tunakulipa",
    "tumekulipa", "tumewalipa", "tumekulipia", "tumewalipia",
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


# Spellings, longest first — `mu`/`mw` must be tried before bare `m` or `nimeMUajiri` is
# mis-segmented as object `-m-` on a stem `uajiri`, and the derivation then demands words
# (`nimeniuajiri`) that are not Swahili. Same class of error as the audit that invented
# `yangapi`: a paradigm applied without its spelling rules produces confident nonsense.
_OBJ_SPELLINGS = ["mw", "mu", "ni", "ku", "tu", "wa", "m"]
_SPELLING_MEMBER = {"mw": "m", "mu": "m", "m": "m",
                    "ni": "ni", "ku": "ku", "tu": "tu", "wa": "wa"}
# SUBJECT AND OBJECT MAY NOT CO-REFER. Swahili has a dedicated reflexive infix `-ji-`
# (nimeJIlipa, "I paid myself"); `ni-...-ni-` and `tu-...-tu-` are not how the language says
# it. The overlap cases go with it — a 1sg subject does not take a 1pl object either, because
# 'us' contains 'me'. Without this rule the derivation demands `nimenilipa` and `tunatulipa`,
# and a test that demands non-words teaches the next maintainer to ignore it.
_PERSON_OVERLAP = {"ni": {"ni", "tu"}, "tu": {"ni", "tu"}, "u": {"ku"}, "m": {"ku"}}


def _object_counterparts(phrase):
    """Every other member of the object-infix class, for a cue that carries one.

    Derived the same way as the possessive and subject counterparts, and with the same limit:
    it reads an EXISTING member and produces its siblings. That limit is finding B and is why
    the census below exists — this function is the part that closes PARTIAL coverage."""
    for word in phrase.split():
        for spelling in _OBJ_SPELLINGS:
            m = re.fullmatch(rf"([a-z]{{1,2}})(na|me|li|ta|ki){spelling}([a-z]{{2,}})", word)
            if not m:
                continue
            subj, tense, stem = m.group(1), m.group(2), m.group(3)
            member = _SPELLING_MEMBER[spelling]
            for other in OBJECT_INFIX:
                if other == member or other in _PERSON_OVERLAP.get(subj, ()):
                    continue
                # -m- is -mw- before a vowel-initial stem.
                infix = "mw" if other == "m" and stem[0] in "aeiou" else other
                yield phrase.replace(word, f"{subj}{tense}{infix}{stem}", 1)
            return


def _recognised(counterpart, phrases, lname=None):
    """The property that matters: would this cue list MATCH a question containing it?

    Not 'is it in the list' — a shorter existing cue that is a substring of the counterpart
    already matches every text the counterpart would, and neither does a compiled companion
    pattern need a list entry to do its job."""
    if any(p in counterpart for p in phrases):
        return True
    rx = _CONCORD_REGEXES.get(lname)
    return bool(rx and rx.search(counterpart))


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
                              ("subject", _subject_counterparts),
                              ("object", _object_counterparts)):
                for c in gen(p):
                    if c in _WITHHELD or c in _WITHHELD_OBJECT or c == _LEAKS_ANYWAY:
                        continue
                    if not _recognised(c, phrases, lname):
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


def test_the_withheld_object_counterparts_still_name_a_live_defect():
    """The pin on `_WITHHELD_OBJECT`. Same mechanism as the `tukiagiza` pin above.

    An employee asking whether the wage they are PAID is lawful must reach the deterministic
    minimum_wage route, and does not — because `_WAGE_PAY_CUES` knows `namlipa` (I pay HIM)
    and not `wananilipa` (they pay ME). Ten counterparts are exempted from the generative
    check on the grounds that closing them widens a different route and needs its own sweep.
    When somebody does that work, this test fails and the exemption must go with it."""
    employee_side = "wananilipa laki mbili kwa mwezi je ni halali kisheria"
    employer_side = "nimemlipa mfanyakazi wangu 150000 kwa mwezi je ni halali"
    assert routing.detect_intent(employer_side) == "minimum_wage", (
        "the control moved — if the employer side no longer routes, this exemption is "
        "measuring the wrong thing")
    assert routing.detect_intent(employee_side) != "minimum_wage", (
        "the employee-side wage-floor gap is CLOSED — delete _WITHHELD_OBJECT and let the "
        "generative check hold the class shut")


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

# ---------------------------------------------------------------------------
# 5. THE ABSENT-CLASS CENSUS — finding B, made executable
# ---------------------------------------------------------------------------
# EVERYTHING ABOVE DERIVES A COUNTERPART FROM AN EXISTING MEMBER. That is a real property and
# it closed 31 real gaps — but it means a list with ZERO members of a class has nothing to
# derive from, so the class is not partially covered, it is ABSENT, and a generative check
# cannot see an absence. Measured on 2026-08-15:
#
#     _NSSF_EMPLOYEE_CUES    7 members, 0 person-marked      <- item C lived here
#     _NSSF_TOTAL_CUES      10 members, 0 person-marked
#     _APPLICABILITY_CUES   13 members, 5 person-marked      <- the test could see this one
#     _WAGE_PAY_CUES        19 members, 6 person-marked
#     _PAYROLL_CTX          28 members, 5 person-marked
#
# Every list the 2026-08-15 closure fixed was one somebody had already half-populated. C
# survived it because its class was at 0%, not at 30% — and C had then been live and wrong for
# weeks, answering TZS 130,000 where the employee share was TZS 65,000.
#
# THE FIX IS THAT THE REQUIREMENT MUST NOT COME FROM THE LIST. The table below states, from
# the grammar, what each person-resolving consumer has to be able to see, and builds one probe
# per class member by substitution. A list at 0% now fails, because nothing about the
# requirement depends on the list's contents. That is the whole difference, and it is worth
# more than the individual cues it was written to protect.
PERSON_COVERAGE = {
    "nssf_party": {
        "consumer": staticmethod(routing.nssf_party),
        "frame": "wana{OBJ}kata kiasi gani kwenye mshahara wa 650000 kwa ajili ya mfuko "
                 "wa uzeeni",
        "expected": "employee",
        "why": "the NSSF employee share is DEDUCTED FROM THE WAGE while the employer's 10% "
               "is paid by the employer and never deducted — so 'how much is taken out of "
               "<somebody>'s pay' is the employee share for every one of the five persons, "
               "whoever is asking.",
    },
    "asks_applicability": {
        "consumer": staticmethod(routing.asks_applicability),
        "frame": "nina wafanyakazi 12 je tozo ya mafunzo ina{OBJ}husu",
        "expected": True,
        "why": "'does it concern <person>' is the everyday applicability phrasing, and the "
               "list already carried three of the five members — a class the codebase had "
               "started enumerating and then stopped.",
    },
}

# Cue lists a person-resolving consumer reads that are NOT required to carry the class, each
# with the reason. An exemption is a decision on the record; silence is what produced C.
ZERO_PERSON_BY_DESIGN = {
    "_NSSF_TOTAL_CUES": (
        "a TOTAL question is party-NEUTRAL by definition — 'jumla ya michango', 'mwajiri na "
        "mfanyakazi'. Marking a person is precisely what a total question does not do, so "
        "zero person-marked members here is correct rather than missing."),
    "_NSSF_EMPLOYER_CUES": (
        "covered, not exempt in spirit: it already carries 'kama mwajiri nachangia' / "
        "'mwajiri nachangia'. It is listed here because the EMPLOYER share is not a "
        "deduction, so the object-infix frame above does not apply to it — the employer "
        "frame is nominal ('sehemu ya mwajiri'), not verbal."),
}


def _lists_read_by(fn):
    """The module-level cue lists a consumer function actually consults, read off its source.

    Discovery rather than declaration: add a fourth list to nssf_party tomorrow and the
    census demands a decision about it, without anyone remembering to update a table."""
    src = inspect.getsource(fn)
    return sorted({n for n in re.findall(r"\b_[A-Z][A-Z0-9_]*\b", src)
                   if isinstance(getattr(routing, n, None), (list, tuple))})


@pytest.mark.parametrize("name", sorted(PERSON_COVERAGE))
def test_a_person_resolving_consumer_sees_every_member_of_the_class(name):
    """The census. Fails when a class is ABSENT, which the generative test above cannot do."""
    spec = PERSON_COVERAGE[name]
    consumer = spec["consumer"].__func__
    missing = []
    for member in OBJECT_INFIX:
        q = spec["frame"].replace("{OBJ}", member)
        got = consumer(q)
        if got != spec["expected"]:
            missing.append((member, OBJECT_INFIX[member], q, got))
    assert not missing, (
        f"{name} is blind to {len(missing)} of the {len(OBJECT_INFIX)} object-infix members.\n"
        f"  WHY IT MUST SEE THEM: {spec['why']}\n"
        + "\n".join(f"  -{m}- ({gloss}): got {got!r}, expected "
                    f"{spec['expected']!r}\n      {q}" for m, gloss, q, got in missing))


@pytest.mark.parametrize("name", sorted(PERSON_COVERAGE))
def test_every_cue_list_a_person_resolving_consumer_reads_is_accounted_for(name):
    """A new cue list wired into a person-resolving consumer must be covered or exempted.

    This is the part that makes the census self-enforcing rather than a snapshot: the lists
    are discovered from the consumer's own source, so the table cannot quietly fall behind
    the code the way a hand-maintained enumeration does."""
    covered = set()
    for spec in PERSON_COVERAGE.values():
        covered |= set(_lists_read_by(spec["consumer"].__func__))
    undeclared = [n for n in _lists_read_by(PERSON_COVERAGE[name]["consumer"].__func__)
                  if n not in ZERO_PERSON_BY_DESIGN
                  and n not in {"_NSSF_EMPLOYEE_CUES", "_APPLICABILITY_CUES"}]
    assert not undeclared, (
        f"{name} reads cue lists nobody has decided about: {undeclared}. Either the "
        f"object-infix class must reach them (extend PERSON_COVERAGE) or their exemption "
        f"must be written down with its reason (ZERO_PERSON_BY_DESIGN). Do not leave it "
        f"silent — a silent zero is exactly how item C reached production twice.")
    assert covered, "the census discovered no cue lists at all — has a consumer been renamed?"


def test_the_census_is_not_satisfied_by_the_literal_cue_lists():
    """Proof the census tests something, and the record of what the fix actually is.

    `_NSSF_EMPLOYEE_CUES` still contains no person-marked phrase — deliberately, because a
    bare infix+stem cue is unsafe (`mkat` nests in `mkataba`, `wakat` in `wakati`). The class
    is carried by a host-qualified pattern instead. So this asserts BOTH halves: the literal
    list cannot see nat_08, and the party resolver can."""
    q = "wananikata kiasi gani kwenye mshahara wa 650000 kwa ajili ya mfuko wa uzeeni"
    assert not any(c in q for c in routing._NSSF_EMPLOYEE_CUES), (
        "if a person-marked literal was added, check it is not a bare infix+stem — "
        "`mkataba` and `wakati` are waiting for that mistake")
    assert routing.nssf_party(q) == "employee"


def test_the_object_infix_builder_emits_all_five_members_and_the_vowel_rule():
    """The builder is what makes half-enumeration impossible, so it is pinned directly.

    Includes the -m- -> -mw- alternation before a vowel-initial stem, which is the one part a
    hand-written list gets wrong every time (`inamwanza`, not `inamanza`)."""
    consonant = routing._object_concord("kat")
    for member in OBJECT_INFIX:
        assert member in consonant, member
    assert "mu" in consonant, "-m- is commonly written -mu- before a consonant"
    vowel = routing._object_concord("anza", vowel_initial=True)
    assert "mw" in vowel, "-m- must surface as -mw- before a vowel-initial stem"


def test_the_negative_host_cannot_spend_its_tense_marker_on_the_object():
    """`hakukata` is 'did NOT deduct' — the `ku` is the negative past marker, not the -ku-
    object infix. The first version of the pattern put the negative tense in an optional slot
    and the regex simply backtracked past it; the sweep caught it on 4 corpus rows.

    Both directions are asserted, because a fix that only kills the false positive would also
    kill `hakunihusu`, which is a real applicability question."""
    assert not routing._NSSF_EMPLOYEE_CONCORD.search("kama mwajiri hakukata paye")
    assert not routing._NSSF_EMPLOYEE_CONCORD.search("kampuni haikukata wht inayostahili")
    assert routing._APPLICABILITY_CONCORD.search("je tozo hiyo hakunihusu mwaka jana")
    assert routing._APPLICABILITY_CONCORD.search("je tozo ya mafunzo hainihusu")


# ---------------------------------------------------------------------------
# 6. R17 for the object class — authored probes, because the corpus is nearly blind
# ---------------------------------------------------------------------------
# The handover recorded "52 eval / 385 train rows exercise this, so a clean sweep means
# something". That figure came from a bare `(na|me|li|ta)(ni|ku|tu)` scan and does not survive
# contact with the words: `kaMPUNI`, `kiWAngo`, `kuTUmika`, `waKATi` and `inaMAANisha` all
# match it and none contains an object infix. Host-qualified, the corpus carries ~120 real
# occurrences and `-husu` alone is ~78 of them; `-ku-` and `-mw-` have ZERO on both stems.
# So the sweep is real evidence for one member and blind for the rest — the SAFETY-2 situation
# after all, and these probes are load-bearing rather than supplementary.

def _obj_probes():
    with open(_OBJ_PROBES, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_the_object_probe_file_carries_both_polarities_and_every_class_member():
    probes = _obj_probes()
    assert len(probes) == 22, len(probes)
    members = [p for p in probes if p["kind"] == "member"]
    negatives = [p for p in probes if p["kind"] == "negative"]
    assert len(members) == 12 and len(negatives) == 10
    covered = {p["member"] for p in members if p["paradigm"] == "object_infix"}
    assert {"-ni-", "-ku-", "-m-", "-tu-", "-wa-"} <= covered | {"-mu-"}, covered
    for p in probes:
        assert p["guards_against"], p["id"]


@pytest.mark.parametrize("probe", [p for p in _obj_probes() if p["kind"] == "member"],
                         ids=lambda p: p["id"])
def test_each_object_class_member_reaches_its_engine(probe):
    if "expected_intent" in probe:
        assert routing.detect_intent(probe["question"]) == probe["expected_intent"], \
            f"{probe['id']}: {probe['guards_against']}"
    if "expected_party" in probe:
        assert routing.nssf_party(probe["question"]) == probe["expected_party"], \
            f"{probe['id']}: {probe['guards_against']}"
    if "expected_applicability" in probe:
        assert routing.is_applicability_question(probe["question"]) is \
            probe["expected_applicability"], f"{probe['id']}: {probe['guards_against']}"


@pytest.mark.parametrize("probe", [p for p in _obj_probes() if p["kind"] == "negative"],
                         ids=lambda p: p["id"])
def test_the_nesting_words_do_not_read_as_object_concord(probe):
    """`wakati`, `mkataba`, `kukata`, `nikatae`, `kuhusu`, `linianza`, `hakukata` — every one
    proven on the corpus to nest inside the obvious bare cue, and two of them (`kuhusu` at 154
    rows, `wakati` at 116) would have been catastrophic. Also pins the two PRECEDENCE cases,
    since 'total wins, then employer' is the only thing keeping the widened employee pattern
    off a genuine total or employer question."""
    assert routing.nssf_party(probe["question"]) == probe["expected_party"], \
        f"{probe['id']}: {probe['guards_against']}"
    assert routing.is_applicability_question(probe["question"]) is \
        probe["expected_applicability"], f"{probe['id']}: {probe['guards_against']}"


def test_the_two_live_object_concord_wrong_answers_now_reach_their_engine():
    """nat_08 and nat_04 — the two rows this item exists for, both live and wrong today."""
    nat_08 = ("wananikata kiasi gani kwenye mshahara wangu wa 650000 kwa ajili ya mfuko "
              "wa uzeeni")
    nat_04 = "nimeongeza watu sasa tuko kumi na mmoja je ile ya mafunzo inanianza lini"
    assert routing.detect_intent(nat_08) == "nssf"
    assert routing.nssf_party(nat_08) == "employee", "20% of 650,000 is not what was asked"
    assert routing.detect_intent(nat_04) == "sdl"
    assert routing.is_applicability_question(nat_04)
    from chike import swahili_numbers as swn
    assert swn.parse_count(nat_04) == 11, (
        "the route alone is not the fix — without the copula headcount surface this asks "
        "for a count the question already states")


def test_both_live_2026_08_14_questions_now_reach_their_engine():
    """`shingapi` was the last blocker on BOTH. The dh->z work fixed the levy detection on
    the NSSF one; this fixes the money-ask on both."""
    sdl = ("Nina wafanyakazi 14 mishahara yote kwa mwezi ni milioni 6 ile ya mafunzo ya "
           "ufundi nalipa shingapi")
    nssf = ("Mshahara wa wafanyakazi wangu ni laki nane kwa mwezi mimi kama mwajiri "
            "nachangia shingapi kwenye mfuko wa hifazi ya jamii")
    assert routing.detect_intent(sdl) == "sdl"
    assert routing.detect_intent(nssf) == "nssf"

# -*- coding: utf-8 -*-
r"""THE PREMISE A QUESTION ASSERTS, AND WHETHER THE ENGINE'S YES/NO LEAD ANSWERS IT.

⛔⛔ THIS IS A CLASS FIX FOR A CLASS DEFECT, AND THE TWO PATCHES IT REPLACES ARE THE ARGUMENT
FOR IT. Every rules-engine verdict writes its yes/no lead for ONE implicit question — the
plain positive frame. `nssf_applies()` opens "Ndiyo."; `sdl_applies(9)` opens "Hapana.".
Route a question with any other premise to that verdict and the lead answers something
nobody asked, in the engine's deterministic voice.

Two rows had already been patched one at a time — eval_393 (`confirms_negated_premise`) and
eval_394 (the optionality branch). Then the mirror sweep asked the question of the whole
population: **37 of 65 polarity pairs received the SAME yes/no lead in both directions**, and
the only pair that flipped correctly was the one fixed by hand the day before. So it was
never 37 rows; it is one mechanism, patched twice.

    eval/controls/mirror_premise_sweep_2026_10_10.py
    eval/results/mirror_premise_sweep_2026_10_10.json

⛔ THE RESOLUTION IS TWO FACTS COMPARED, AND NEITHER IS GUESSED:

    1. what proposition the QUESTION asserts, and with what truth value  -> detect()
    2. what proposition the VERDICT's lead answers, and with what truth  -> result.lead_claim

A declared `lead_claim` is the whole reason this is not R34's metadata inference. Deriving
the proposition from `result.computation` would conflate distinct claims inside one
computation type — `sdl` carries BOTH "does the obligation apply" and "does the figure you
named count as the base" — so each verdict states its own claim at the site that writes the
lead, and this module never infers one.

⚠️ THE SCOPE IS DELIBERATELY THE NEGATED POPULATION ONLY, which is what makes the change
safe and measurable. A plain positive question is already answered correctly by the lead the
engine wrote for it, so `resolve()` returns the result UNTOUCHED unless the surface form is
negated or the propositions disagree. Every positive row stays byte-identical, and the blast
radius is the ~65 pairs the sweep enumerated rather than all 135 yes/no leads.

⚠️ FORMS ARE LISTED, NOT ASSEMBLED FROM OPTIONAL MORPHEMES (R37), and every pair was
harvested from the corpora rather than invented — a constructed `(?:ha)?(?:na)?lazimik\w*`
generates strings Swahili does not use and misses ones it does. This table is the SINGLE
OWNER: eval/controls/mirror_premise_sweep_2026_10_10.py imports it rather than keeping a
second copy, because two copies of one cue list is how the regex-in-two-rules defect of
2026-10-07 happened.
"""
import re
from typing import NamedTuple, Optional

from .results import ComputationResult, relead_for_premise, strip_lead_particle

# ── THE PROPOSITIONS ─────────────────────────────────────────────────────────────────────
OBLIGATION_APPLIES = "obligation_applies"
WAGE_IS_LAWFUL = "wage_is_lawful"
IS_VOLUNTARY = "is_voluntary"
BASE_COUNTS = "base_counts"
THRESHOLD_CROSSED = "threshold_crossed"

# ⚠️ COMPATIBILITY IS NARROW AND EACH ENTRY IS A SUBSTANTIVE CLAIM ABOUT THE LAW, NOT A
# CONVENIENCE. "Have I crossed the VAT threshold?" is answered by "you must register": for
# the registration engines, crossing the threshold is exactly the event that creates the
# obligation, so a verdict about the obligation does answer the question asked. eval_370 is
# the row — treating it as a mismatch would strip a CORRECT "Ndiyo, unatakiwa kujisajili
# VAT" of its lead.
#
# IS_VOLUNTARY is deliberately NOT compatible with OBLIGATION_APPLIES, and that
# non-compatibility is the entire eval_394 finding: a levy can apply to you and whether it is
# optional is a different claim. Conflating them is the R20 borrowed-detector error, and here
# it shipped a compulsory levy declared voluntary.
#
# BASE_COUNTS is likewise kept distinct from OBLIGATION_APPLIES: "does SDL apply to me" and
# "does the figure I named count as payroll" are different questions with different answers.
_COMPATIBLE = {
    THRESHOLD_CROSSED: {OBLIGATION_APPLIES},
}

# (positive surface form, negated surface form, frame, proposition, inverts)
#
# `inverts` means the POSITIVE surface form asserts the proposition is FALSE: "nakiuka
# sheria" (I am breaking the law) asserts wage_is_lawful = False. Without this flag the
# minimum-wage frames resolve backwards, and backwards is worse than unresolved.
FRAMES = [
    # applicability — 1sg/1pl/3pl object concord, the commonest frame in the corpora
    ("inanihusu", "hainihusu", "applies-to-me", OBLIGATION_APPLIES, False),
    ("inatuhusu", "haituhusu", "applies-to-us", OBLIGATION_APPLIES, False),
    ("inawahusu", "haiwahusu", "applies-to-them", OBLIGATION_APPLIES, False),
    ("inahusika", "haihusiki", "applies", OBLIGATION_APPLIES, False),
    # obligation / modality
    ("nalazimika", "silazimika", "i-am-obliged", OBLIGATION_APPLIES, False),
    ("tunalazimika", "hatulazimika", "we-are-obliged", OBLIGATION_APPLIES, False),
    ("natakiwa", "sitakiwi", "i-am-required", OBLIGATION_APPLIES, False),
    ("tunatakiwa", "hatutakiwi", "we-are-required", OBLIGATION_APPLIES, False),
    ("inatakiwa", "haitakiwi", "it-is-required", OBLIGATION_APPLIES, False),
    ("ana wajibu", "hana wajibu", "has-a-duty", OBLIGATION_APPLIES, False),
    # payment / contribution
    ("nalipa", "silipi", "i-pay", OBLIGATION_APPLIES, False),
    ("tunalipa", "hatulipi", "we-pay", OBLIGATION_APPLIES, False),
    ("nachangia", "sichangii", "i-contribute", OBLIGATION_APPLIES, False),
    ("nahitaji", "sihitaji", "i-need", OBLIGATION_APPLIES, False),
    # lawfulness — minimum_wage's two frames. The `violation` one INVERTS.
    ("ni halali", "si halali", "is-lawful", WAGE_IS_LAWFUL, False),
    ("nakiuka", "sikiuki", "i-am-breaking", WAGE_IS_LAWFUL, True),
    # compulsion. `ni lazima` lives HERE and not in the obligation family on purpose: it asks
    # whether the levy is mandatory, which is the IS_VOLUNTARY axis, and routing an
    # applicability verdict at it is extract_184's defect.
    #
    # ⚠️ THE `inverts` COLUMN ON THESE TWO WAS BACKWARDS IN MY FIRST DRAFT AND THE TABLE READ
    # PERFECTLY FINE. "ni ya hiari" (is it voluntary) asserts is_voluntary=TRUE, so it does NOT
    # invert; "ni lazima" (is it compulsory) asserts is_voluntary=FALSE, so it DOES. Swapping
    # them would have resolved every compulsion question to the opposite answer — in the
    # engine's voice, on the exact axis eval_394 was about. Found by printing detect()'s output
    # for all four surface forms instead of re-reading the table, which is the only thing that
    # distinguishes a correct polarity column from a plausible one.
    ("ni ya hiari", "si ya hiari", "is-voluntary", IS_VOLUNTARY, False),
    ("ni lazima", "si lazima", "is-compulsory", IS_VOLUNTARY, True),
    # threshold crossing
    ("nimevuka", "sijavuka", "i-have-crossed", THRESHOLD_CROSSED, False),
    ("yamefika", "hayajafika", "has-reached", THRESHOLD_CROSSED, False),
]

# ⛔ `ni kweli` / `si kweli` IS DELIBERATELY ABSENT, AND THE REASON IS WORTH RECORDING. It
# asserts no proposition of its own — it asks us to confirm whatever the user ALREADY stated,
# so the proposition lives in an embedded clause ("jamaa wamesema LAZIMA NIWE NA MASHINE YA
# RISITI, ni kweli?"). Mapping it to a fixed proposition would resolve the polarity of a claim
# this module never read. Left unresolved rather than resolved wrongly; edge_p08 is the row,
# and it stays in the mirror sweep's finding list as a known-open case.
_EXCLUDED_FRAMES = {"is-it-true": "asserts no proposition of its own — the claim being "
                                 "confirmed sits in an embedded clause this module does not "
                                 "parse"}

# ── THE ASK CLAUSE ───────────────────────────────────────────────────────────────────────
# ⛔ A FRAME MUST SIT IN THE CLAUSE THAT CARRIES THE ASK. Measured while building the mirror
# sweep: a whole-text match produced 46 findings of which TEN were specimens, not defects.
# `extract_087` — "Uzalishaji TUNALIPA jumla milioni nne, …, SDL ya kampuni nzima ni NGAPI?" —
# is an AMOUNT question whose lead comes from base_rejection; `tunalipa` in its first clause
# is a statement about production spending and asks nothing. Resolving on it would re-lead a
# correct answer.
#
# The digit guard `(?<!\d),(?!\d)` keeps "TZS 450,000" from splitting. The trailing
# confirmation tag is part of the ask, not a clause after it, so it is stripped and restored —
# without that, eval_393 ("… haitakiwi kulipa SDL, sivyo?") loses its frame entirely.
_SEP = re.compile(r"(?<!\d),(?!\d)|[;—–]|\.\s+|\?\s+")
_CONFIRMATION_TAG = re.compile(
    r"[,–—-]\s*(?:sivyo|si\s+ndivyo|siyo|sio\s+hivyo)\s*\??\s*$", re.IGNORECASE)


def ask_clause(question: str):
    """(ask clause, prefix, suffix) — the last clause, which is where the ask lives."""
    stripped = _CONFIRMATION_TAG.sub("", question.strip())
    tag = question.strip()[len(stripped):]
    parts = [p for p in _SEP.split(stripped) if p and p.strip()]
    if not parts:
        return stripped, "", tag
    last = parts[-1]
    cut = stripped.rfind(last)
    return last, stripped[:cut], stripped[cut + len(last):] + tag


class Premise(NamedTuple):
    frame: str
    proposition: str
    asserted_truth: bool      # what the question claims the proposition's value IS
    surface_negated: bool     # whether the question used the negated surface form
    form: str                 # the matched surface form, for the artifact


def detect(question: str) -> Optional[Premise]:
    """The premise the question's own ask asserts, or None.

    Longest-first and ONE frame per question: applying two would flip the polarity back.
    """
    ask, _prefix, _suffix = ask_clause(question)
    for pos, neg, frame, prop, inverts in sorted(FRAMES, key=lambda t: -len(t[0])):
        for form, negated in ((neg, True), (pos, False)):   # negated first: it is narrower
            if re.search(r"(?<![a-z])" + re.escape(form) + r"(?![a-z])", ask, re.IGNORECASE):
                # The positive form asserts the proposition unless the frame inverts;
                # negating the surface flips whichever that was.
                asserted = (not inverts) if not negated else inverts
                return Premise(frame, prop, asserted, negated, form)
    return None


def strip_lead(result: ComputationResult) -> ComputationResult:
    """Remove the yes/no particle, keeping the substantive verdict.

    ⚠️ THIS CONVERTS A WRONG ANSWER INTO A NON-ANSWER, WHICH IS THE SAFE DIRECTION AND NOT A
    WIN. Per CLAUDE.md's two-bar framing it moves A1 and never A2: the user no longer gets a
    confident wrong yes/no, and still does not get their yes/no. Used only where the verdict
    demonstrably answers a DIFFERENT proposition from the one asked, where the alternative is
    asserting a particle about a claim the engine never evaluated.
    """
    working = strip_lead_particle(result.working)
    return ComputationResult(
        computation=result.computation, applicable=result.applicable, amount=result.amount,
        working=working, inputs=result.inputs, note=result.note,
        lead_claim=result.lead_claim, premise_resolved=True)


class Resolution(NamedTuple):
    result: ComputationResult
    action: str               # 'untouched' | 'agreed' | 'denied' | 'lead_stripped'
    premise: Optional[Premise]
    why: str


def resolve(question: str, result: ComputationResult) -> Resolution:
    """Re-lead, strip, or leave alone — and say which, so a sweep can count the actions."""
    if result is None or result.lead_claim is None:
        return Resolution(result, "untouched", None,
                          "the verdict carries no yes/no lead to resolve")
    if result.premise_resolved:
        return Resolution(result, "untouched", None,
                          "a renderer already resolved this verdict's premise and passed a "
                          "restatement with it; re-resolving would strip a correct lead")
    premise = detect(question)
    if premise is None:
        return Resolution(result, "untouched", None,
                          "the question's ask asserts no listed premise")
    prop, truth = result.lead_claim
    if premise.proposition != prop and prop not in _COMPATIBLE.get(premise.proposition, ()):
        return Resolution(
            strip_lead(result), "lead_stripped", premise,
            f"the question asks about {premise.proposition} and the verdict answers "
            f"{prop}; a yes/no particle here would assert something the engine never "
            f"evaluated")
    if not premise.surface_negated:
        # The plain positive frame is what every engine lead is already written for, and for
        # an inverting frame the owning renderer (minimum_wage's lawful/violation table) has
        # already resolved it. Touching these would churn ~100 correct answers.
        return Resolution(result, "untouched", premise,
                          "positive surface form — the lead the engine wrote is the lead "
                          "this question wants")
    agrees = (premise.asserted_truth == truth)
    return Resolution(
        relead_for_premise(result, agrees=agrees), "agreed" if agrees else "denied", premise,
        f"premise asserts {premise.proposition}={premise.asserted_truth} and the verdict "
        f"holds it {truth}")

"""Shared result type and money helpers for the rules engine."""

import re
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


def to_shillings(amount: Decimal) -> Decimal:
    """Round to whole TZS (half-up). Compliance figures are stated in whole shillings."""
    return Decimal(amount).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def tzs(amount) -> str:
    """Format a number as 'TZS 1,440,000'."""
    return f"TZS {Decimal(amount):,.0f}"


@dataclass(frozen=True)
class ComputationResult:
    """The output contract of every rules-engine function.

    `working` is the calculation shown to the user (in Swahili) so the answer is
    auditable, not just a bare number. `applicable=False` means the obligation
    does not apply to these inputs (e.g. SDL below the 10-employee threshold) —
    that is a correct answer, not an error.
    """

    computation: str                      # 'sdl' | 'nssf' | 'paye' | 'wcf'
    applicable: bool
    amount: Optional[Decimal]             # None when not applicable
    working: str                          # human-readable calculation (Swahili)
    inputs: dict = field(default_factory=dict)
    note: str = ""
    # ⛔ WHAT THIS VERDICT'S YES/NO LEAD ACTUALLY CLAIMS: (proposition, truth), or None for
    # a verdict with no yes/no lead at all. DECLARED AT THE SITE THAT WRITES THE LEAD, never
    # inferred downstream — `computation` is not a substitute, because one computation type
    # carries several distinct claims ('sdl' leads BOTH "does the obligation apply" and "does
    # the figure you named count as the base", which have different answers to different
    # questions). See chike/rules_engine/premise.py for the resolver that consumes it, and
    # the mirror sweep for why it exists: 37 of 65 polarity pairs got the SAME lead in both
    # directions because nothing recorded which question the lead was answering.
    lead_claim: Optional[tuple] = None
    # ⛔ SET BY `relead_for_premise` AND CHECKED BY THE CENTRAL RESOLVER, so whichever layer
    # resolves the premise FIRST wins and the central one is a backstop rather than a second
    # pass. Without it the orchestrator's optionality branch — which re-leads for a premise
    # the generic resolver would call a MISMATCH — would have its correct answer stripped of
    # its lead immediately afterwards by the very mechanism meant to protect it.
    premise_resolved: bool = False


_NEGATIVE_LEAD = "Hapana."
_AFFIRMATIVE_LEAD = "Ndiyo."
_AGREEMENT_LEAD = "Ndiyo, ni kweli —"

# ⛔ ONE OWNER FOR "WHAT COUNTS AS A YES/NO LEAD PARTICLE", because two copies of a cue list
# is how a cue removed from one rule survives in the other (2026-10-07, four times in one
# afternoon). `premise.strip_lead` imports this rather than reimplementing the prefix walk my
# first draft duplicated.
#
# ⚠️ FOUR SURFACE FORMS, AND THE LAST TWO ARE WHY A `startswith("Hapana.")` CHECK IS NOT
# ENOUGH: the engines write "Hapana." (sdl), "Hapana," (corporate AMT, minimum wage), "Ndiyo,"
# (vat/efd/minimum wage) AND "Bado hapana." (corporate AMT below the loss-year count). A strip
# that only knew the period forms would leave "Bado hapana." in place and then prepend a
# second particle in front of it — two polarity markers in one sentence, which is the exact
# shape of the eval_393 defect this machinery exists to remove.
_LEAD_PARTICLE = re.compile(
    r"^\s*(?:Ndiyo,\s*ni\s*kweli\s*[—-]|Bado\s+hapana|Ndiyo|Hapana)\s*[.,]?\s*",
    re.IGNORECASE)


def strip_lead_particle(working: str) -> str:
    """The verdict's substance with its yes/no particle removed, re-capitalised.

    Re-capitalisation matters for the COMMA forms: minimum_wage writes "Ndiyo, ni halali.
    Mshahara …", so a bare strip leaves a lower-case "ni halali." to be prefixed with a new
    particle — "Hapana. ni halali." reads as a typo in the middle of a legal answer. With it:
    "Hapana. Ni halali. Mshahara …" — no, it IS lawful — which is both correct and readable.
    """
    out = _LEAD_PARTICLE.sub("", working or "", count=1).lstrip()
    return out[:1].upper() + out[1:] if out else out


# ⛔⛔ A YES/NO LEAD IS AN ANSWER TO ONE PARTICULAR QUESTION, AND THE ENGINE ONLY KNOWS ONE.
#
# Every applicability verdict writes its lead for the plain frame "does this levy apply?" —
# `nssf_applies()` opens "Ndiyo.", `sdl_applies(9)` opens "Hapana.". Route a question with a
# DIFFERENT premise to the same verdict and the lead answers a question nobody asked, carrying
# the engine's authority while doing it. Measured 2026-10-10 on the live code, both polarities:
#
#   "Je, NSSF SI ya hiari?"   premise: it is NOT voluntary. TRUE, and applicable=True confirms
#                             it. The engine leads "Ndiyo." -- accidentally right in substance,
#                             and it contradicted the model body's "Hapana, si ya hiari" in the
#                             next sentence. That is eval_394: the judge called the row WRONG
#                             for the contradiction, and the body was the CORRECT half.
#   "Je, NSSF NI ya hiari?"   premise: it IS voluntary. FALSE, and applicable=True contradicts
#                             it. The engine leads "Ndiyo." -- and that reads as YES, NSSF IS
#                             VOLUNTARY. **Flatly wrong, in the engine's own voice**, which is
#                             worse than eval_394 and was found in the same minute by asking
#                             the mirror question instead of only the one in the gate.
#
# So the lead is re-derived from TWO facts: does the verdict confirm the premise, and what was
# the premise. Only the lead and an optional restatement change; the substantive verdict is
# untouched and still governs, so this can never turn a correct verdict into a wrong one.
def relead_for_premise(result: ComputationResult, *, agrees: bool,
                       restate: str = None) -> ComputationResult:
    """Re-lead a verdict for a question whose premise is not the engine's plain frame.

    `agrees` is whether the verdict CONFIRMS the question's premise — a property of the
    premise, which only the caller can know. `restate` is the premise answered in the user's
    own terms, placed ahead of the engine's detail so the answer leads with what was asked.
    """
    working = strip_lead_particle(result.working)
    head = _AGREEMENT_LEAD if agrees else _NEGATIVE_LEAD
    parts = [head, restate.strip()] if restate else [head]
    if working:
        parts.append(working)
    return ComputationResult(
        computation=result.computation, applicable=result.applicable, amount=result.amount,
        working=" ".join(p for p in parts if p), inputs=result.inputs, note=result.note,
        # Carried through: the re-lead changes the PARTICLE, not what the verdict claims, so
        # dropping it here would make a re-led result look like one with no yes/no at all and
        # silently exempt it from every later check. R27's shape in a constructor.
        lead_claim=result.lead_claim, premise_resolved=True)


def agree_with_negated_premise(result: ComputationResult, *,
                               confirmed_when_applicable: bool = False,
                               restate: str = None) -> ComputationResult:
    """Re-lead a verdict as AGREEMENT with a negated premise the verdict confirms.

    Phase D re-run (030a5ff) finding, eval_393: "Kampuni yenye wafanyakazi 9 HAITAKIWI kulipa
    SDL, SIVYO?" The engine's lead is written for the plain frame ("does SDL apply?" -> No),
    so the reply opened "Hapana." while the model text had already opened "Sawa kabisa" —
    two opposite polarity markers agreeing with each other in one answer. It reads as a
    contradiction to a user, and the gold leads "Ndiyo, sivyo".

    A negated premise that the verdict CONFIRMS is agreed with, not denied. Callers must gate
    on routing.confirms_negated_premise(question) — the 17 confirmation-tag questions in the
    corpora are otherwise FALSE-premise traps whose correct lead really is "Hapana.".

    ⚠️ `confirmed_when_applicable` NAMES WHICH VERDICT CONFIRMS THE PREMISE, AND IT EXISTS
    BECAUSE THE OLD `applicable is False` GATE WAS NOT A STATEMENT ABOUT NEGATION AT ALL — it
    encoded eval_393's PREMISE SHAPE ("the levy does not apply"), which applicable=False
    confirms. eval_394's premise is "the levy is not optional", which applicable=**True**
    confirms, so the gate rejected the second real instance of the thing this function is for
    (R20's borrowed-detector question: whose words is the check written for, and is it the same
    population?). Default False, so every existing caller is byte-identical.
    """
    if result.applicable is not confirmed_when_applicable:
        raise ValueError(
            f"agree_with_negated_premise: applicable={result.applicable} does not CONFIRM this "
            f"premise (confirmed_when_applicable={confirmed_when_applicable}), so the premise "
            f"is WRONG and must be denied, not agreed with")
    return relead_for_premise(result, agrees=True, restate=restate)


def deny_positive_premise(result: ComputationResult, *, restate: str) -> ComputationResult:
    """Re-lead a verdict as DENIAL of a positive premise the verdict contradicts.

    The mirror of the above, and the half that was shipping a flatly wrong answer: "Je, NSSF NI
    ya hiari?" asserts the levy is voluntary, the verdict contradicts that, and the engine's
    plain-frame "Ndiyo." reads as agreeing with it. `restate` is REQUIRED here rather than
    optional — a bare "Hapana." in front of applicability detail denies something the user has
    to guess at, which is the ambiguity that produced eval_394 in the first place.
    """
    if not restate or not restate.strip():
        raise ValueError("deny_positive_premise: a denial needs the premise restated, or the "
                         "user cannot tell what was denied")
    return relead_for_premise(result, agrees=False, restate=restate)

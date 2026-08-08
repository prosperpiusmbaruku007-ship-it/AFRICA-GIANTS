"""Shared result type and money helpers for the rules engine."""

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


_NEGATIVE_LEAD = "Hapana."
_AGREEMENT_LEAD = "Ndiyo, ni kweli —"


def agree_with_negated_premise(result: ComputationResult) -> ComputationResult:
    """Re-lead a NOT-applicable verdict as agreement, for a negated confirmation-tag question.

    Phase D re-run (030a5ff) finding, eval_393: "Kampuni yenye wafanyakazi 9 HAITAKIWI kulipa
    SDL, SIVYO?" The engine's lead is written for the plain frame ("does SDL apply?" -> No),
    so the reply opened "Hapana." while the model text had already opened "Sawa kabisa" —
    two opposite polarity markers agreeing with each other in one answer. It reads as a
    contradiction to a user, and the gold leads "Ndiyo, sivyo".

    A negated premise that the verdict CONFIRMS is agreed with, not denied. Only the lead
    changes; the substantive verdict is untouched and still governs, so this can never turn
    a correct verdict into a wrong one. Callers must gate on `applicable is False` and on
    routing.confirms_negated_premise(question) — the 17 confirmation-tag questions in the
    corpora are otherwise FALSE-premise traps whose correct lead really is "Hapana.".
    """
    if result.applicable:
        raise ValueError("agree_with_negated_premise: the verdict is applicable=True, so the "
                         "negated premise is WRONG and must be denied, not agreed with")
    working = result.working
    if working.startswith(_NEGATIVE_LEAD):
        working = f"{_AGREEMENT_LEAD}{working[len(_NEGATIVE_LEAD):]}"
    else:
        working = f"{_AGREEMENT_LEAD} {working}"
    return ComputationResult(
        computation=result.computation, applicable=result.applicable, amount=result.amount,
        working=working, inputs=result.inputs, note=result.note)

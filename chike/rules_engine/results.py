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

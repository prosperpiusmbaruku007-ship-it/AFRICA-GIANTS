"""Deterministic compliance calculations — SDL, NSSF, PAYE, WCF.

No model dependency of any kind. Given the rates in rates.py (copied from the fact
DB) and structured inputs, every function is pure and unit-testable in isolation.

`SUPPORTED` is the set of computations that have a deterministic implementation.
The orchestrator uses it to decide the third routing outcome (Correction 2): a
computation request in a domain NOT in this set must return a template refusal,
never fall through to raw language-model generation.
"""

from .results import ComputationResult, agree_with_negated_premise
from .base_rejection import reject_base
from .sdl import (compute_sdl, sdl_applies, sdl_crosses_threshold,
                  sdl_zero_below_threshold)
from .nssf import compute_nssf, nssf_applies
from .periods import sdl_by_month
from .rate_statement import levy_rate_statement, supports as rate_statement_supports
from .paye import compute_paye, compute_paye_each
from .wcf import compute_wcf, wcf_applies
from .minimum_wage import compare_to_floor, sector_rates_statement
from .registration_thresholds import vat_registration, efd_required
from . import wage_schedule
from . import registration_thresholds

# 'minimum_wage' is deliberately ABSENT from SUPPORTED / _DISPATCH / _APPLICABILITY. It is not
# a levy: nothing is owed, there are no REQUIRED_FIELDS for the slot extractor to fill, and its
# inputs (the wage, the Schedule row, the period) are resolved deterministically without a
# model. The orchestrator answers it on its own branch, ahead of the levy machinery.
SUPPORTED = frozenset({"sdl", "nssf", "paye", "wcf"})

_DISPATCH = {
    "sdl": compute_sdl,
    "nssf": compute_nssf,
    "paye": compute_paye,
    "wcf": compute_wcf,
}

# Applicability-only ('does this levy apply?') answers — determined from headcount
# (SDL) or the flat no-threshold rule (NSSF/WCF), with no salary. PAYE is absent: its
# applicability depends on salary vs the 270k band, so PAYE stays on the amount path.
_APPLICABILITY = {
    "sdl": sdl_applies,
    "nssf": nssf_applies,
    "wcf": wcf_applies,
}


def is_supported(computation_type: str) -> bool:
    return computation_type in SUPPORTED


def supports_applicability(computation_type: str) -> bool:
    return computation_type in _APPLICABILITY


def compute(computation_type: str, **inputs) -> ComputationResult:
    """Dispatch to the right calculator. Raises KeyError for unsupported types —
    callers must gate on is_supported() first (see orchestrator refusal path)."""
    return _DISPATCH[computation_type](**inputs)


def applicability(computation_type: str, **inputs) -> ComputationResult:
    """Dispatch to the applicability-only answer (yes/no obligation) for a levy.
    Raises KeyError for types without applicability support (e.g. paye)."""
    return _APPLICABILITY[computation_type](**inputs)


__all__ = [
    "ComputationResult",
    "SUPPORTED",
    "is_supported",
    "supports_applicability",
    "compute",
    "applicability",
    "reject_base",
    "sdl_crosses_threshold",
    "sdl_zero_below_threshold",
    "agree_with_negated_premise",
    "compute_sdl",
    "compute_nssf",
    "compute_paye",
    "compute_paye_each",
    "compute_wcf",
    "sdl_applies",
    "nssf_applies",
    "wcf_applies",
    "compare_to_floor",
    "sector_rates_statement",
    "wage_schedule",
    "vat_registration",
    "efd_required",
    "registration_thresholds",
]

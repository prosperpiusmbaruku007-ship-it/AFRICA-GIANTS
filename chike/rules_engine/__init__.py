"""Deterministic compliance calculations — SDL, NSSF, PAYE, WCF.

No model dependency of any kind. Given the rates in rates.py (copied from the fact
DB) and structured inputs, every function is pure and unit-testable in isolation.

`SUPPORTED` is the set of computations that have a deterministic implementation.
The orchestrator uses it to decide the third routing outcome (Correction 2): a
computation request in a domain NOT in this set must return a template refusal,
never fall through to raw language-model generation.
"""

from .results import ComputationResult
from .sdl import compute_sdl, sdl_applies
from .nssf import compute_nssf, nssf_applies
from .paye import compute_paye
from .wcf import compute_wcf, wcf_applies

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
    "compute_sdl",
    "compute_nssf",
    "compute_paye",
    "compute_wcf",
    "sdl_applies",
    "nssf_applies",
    "wcf_applies",
]

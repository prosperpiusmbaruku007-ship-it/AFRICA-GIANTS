"""Deterministic compliance calculations — SDL, NSSF, PAYE, WCF.

No model dependency of any kind. Given the rates in rates.py (copied from the fact
DB) and structured inputs, every function is pure and unit-testable in isolation.

`SUPPORTED` is the set of computations that have a deterministic implementation.
The orchestrator uses it to decide the third routing outcome (Correction 2): a
computation request in a domain NOT in this set must return a template refusal,
never fall through to raw language-model generation.
"""

from .results import ComputationResult
from .sdl import compute_sdl
from .nssf import compute_nssf
from .paye import compute_paye
from .wcf import compute_wcf

SUPPORTED = frozenset({"sdl", "nssf", "paye", "wcf"})

_DISPATCH = {
    "sdl": compute_sdl,
    "nssf": compute_nssf,
    "paye": compute_paye,
    "wcf": compute_wcf,
}


def is_supported(computation_type: str) -> bool:
    return computation_type in SUPPORTED


def compute(computation_type: str, **inputs) -> ComputationResult:
    """Dispatch to the right calculator. Raises KeyError for unsupported types —
    callers must gate on is_supported() first (see orchestrator refusal path)."""
    return _DISPATCH[computation_type](**inputs)


__all__ = [
    "ComputationResult",
    "SUPPORTED",
    "is_supported",
    "compute",
    "compute_sdl",
    "compute_nssf",
    "compute_paye",
    "compute_wcf",
]

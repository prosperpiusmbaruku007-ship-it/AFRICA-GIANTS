"""D-FIDELITY-1 — compute-answer fidelity guard.

The compute path hands the model the authoritative `ComputationResult.working` as ground
truth and asks it only for Swahili persona around it. In a small but safety-relevant class
of cases the model IGNORES the working and re-derives a naive `rate x base` figure — exactly
the answer a gating/override rule (SDL <10 employees -> not applicable; PAYE non-resident ->
flat 15%) was built to correct. `_render` then appends the correct working AFTER that wrong
body, producing a self-contradictory reply that LEADS with the wrong number (eval_367/371/378).

This module detects that contradiction structurally from the model body + the ComputationResult
so the orchestrator can BLANK the body and emit the deterministic working alone — the clean
expression of the architecture's load-bearing invariant that arithmetic is never trusted to the
model (ADR 0001). It is a scorer/render-side guard, never on the arithmetic path.

Detector (validated EXACT over the afef9dd 400 sweep — flags only eval_367/371/378, zero
false-positives across all 13 body-vs-working candidates and the 10 benign breakdowns):

  * amount is None  (engine gave NO figure: not-applicable, or applicability-yes-no-amount)
        -> contradiction iff the body performs a naive levy compute (`rate% x TZS base`) AND
           asserts a `= TZS N` result. A faithful body states the verdict without computing one.
  * amount == 0     (within a 0% band)
        -> contradiction iff the body asserts a NONZERO `= TZS N` result.
  * amount > 0
        -> contradiction iff that authoritative amount is ABSENT from the body's `= TZS N`
           results while the body asserts some other result. (Robust: a faithful body always
           restates the correct figure amid any breakdown/net-pay steps, so presence-of-correct
           is immune to the intermediate band-base and net-pay extras a naive "extra number"
           rule would false-flag on eval_092/191/360/395.)
"""

import re
from typing import Optional

from .rules_engine.results import ComputationResult

# RHS of an '=' expressed in shillings — an asserted compute RESULT.
_RESULT = re.compile(r"=\s*TZS\s*([\d,]+)")
# A naive levy computation: 'TZS base x rate%' or 'rate% x TZS base' (x may be x, *, or the
# unicode multiplication sign). Presence means the body did its own arithmetic.
_NAIVE_LEVY = re.compile(
    r"(?:TZS\s*[\d,]+\s*[x*×]\s*\d+(?:\.\d+)?\s*%)"
    r"|(?:\d+(?:\.\d+)?\s*%\s*[x*×]\s*TZS\s*[\d,]+)",
    re.IGNORECASE,
)


def _asserted_results(text: str) -> set:
    """The set of figures asserted as compute RESULTS (RHS of '= TZS N') in the body."""
    return {int(m.replace(",", "")) for m in _RESULT.findall(text)}


def _has_naive_levy_compute(text: str) -> bool:
    return bool(_NAIVE_LEVY.search(text))


def body_contradicts_working(body: str, result: ComputationResult) -> bool:
    """True iff the model body numerically contradicts the authoritative ComputationResult.

    `body` is the isolated model generation for one compute sub-answer (post-clean_reply,
    pre-merge); `result` is the deterministic ComputationResult it was meant to render.
    """
    if body is None:
        return False
    results = _asserted_results(body)

    if result.amount is None:
        # Engine intentionally gave NO figure (not-applicable, or applicability-yes). A body that
        # computes one has ignored the verdict.
        return _has_naive_levy_compute(body) and bool(results)

    amount = int(result.amount)
    if amount == 0:
        # 0% band: a faithful body says 'hakuna PAYE' (no asserted result); any nonzero result contradicts.
        return any(r != 0 for r in results)

    # Definite positive amount: faithful bodies always restate it; its ABSENCE (while asserting some
    # other result) is the contradiction signal.
    return amount not in results and bool(results)

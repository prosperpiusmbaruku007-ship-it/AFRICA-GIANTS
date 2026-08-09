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

D-FIDELITY-2 (added 2026-08-08, from the 1476caa run) extends this to SIBLING levies. The
check above is per-levy: it validates a sub-answer body against ITS OWN ComputationResult only.
eval_320 ("SDL, NSSF, PAYE na WCF kwa mfanyakazi mmoja mwenye TZS 800,000") showed that is not
enough — the WCF sub-answer restated WCF 4,000 correctly, so it passed, while the SAME body
volunteered `SDL = 3.5% x TZS 800,000 = TZS 28,000` for a ONE-employee payroll (the engine says
TZS 0, below the 10-employee threshold) and `PAYE = 8% x TZS 800,000 - TZS 26,000 = TZS 64,000`
(the engine says 78,000, and the TZS 26,000 'personal relief' does not exist in Tanzania —
CLAUDE.md section 11). The regex scorer counted it a PASS; the judge called it wrong.

A body that volunteers a figure for a levy that is NOT its own is checked against that levy's
authoritative result, using the same per-levy semantics as above. Blanking stays whole-body: a
body proven to contradict the engine anywhere is discarded entirely, and the deterministic
working still carries the answer.

Scope is deliberately COMPUTE sub-answers only. A fact sub-answer has no ComputationResult to
fall back on, so blanking it would delete content rather than replace it with the truth.
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


# --- D-FIDELITY-2: sibling levies -------------------------------------------------------

# The four levies the rules engine computes. Matched case-insensitively as whole words so
# 'sdl' in prose and 'SDL' in a breakdown line are the same token.
_LEVY_TOKEN = re.compile(r"\b(sdl|nssf|paye|wcf)\b", re.IGNORECASE)

# An amount ATTRIBUTED to the label that precedes it — the RHS of either '=' or ':'. This is
# deliberately BROADER than _RESULT above, which stays '=' only: the enumeration shapes that
# motivated this check attribute with a colon ('PAYE (TZS 800,000, 8%): TZS 64,000') as often
# as with '='. _RESULT is left untouched so the validated own-levy detector is byte-identical.
_ATTRIBUTED = re.compile(r"[:=]\s*TZS\s*([\d,]+)")


def _levy_windows(body: str) -> dict:
    """{levy: [text from each mention up to the NEXT levy mention]}.

    Windowing on the next levy token is what makes attribution safe in a breakdown block:
    'SDL = ... = TZS 28,000\\nNSSF = ... = TZS 160,000' gives SDL only its own line, so a
    correct sibling figure can never be read as belonging to the wrong levy.
    """
    marks = [(m.start(), m.group(1).lower()) for m in _LEVY_TOKEN.finditer(body)]
    windows: dict = {}
    for idx, (pos, levy) in enumerate(marks):
        end = marks[idx + 1][0] if idx + 1 < len(marks) else len(body)
        windows.setdefault(levy, []).append(body[pos:end])
    return windows


# A TZS figure anywhere in the engine's own working.
_WORKING_FIGURE = re.compile(r"TZS\s*([\d,]+)")
# The working stating an employer/employee split, e.g. '(mwajiri TZS 80,000 + mfanyakazi
# TZS 80,000)'. Their SUM is as authoritative as the parts.
_SPLIT = re.compile(r"mwajiri\s+TZS\s*([\d,]+)\s*\+\s*mfanyakazi\s+TZS\s*([\d,]+)",
                    re.IGNORECASE)


def _acceptable(result: ComputationResult) -> set:
    """Figures that CANNOT contradict `result`, because the engine itself states them.

    NSSF is the reason this is not just {amount}: depending on how the question is framed the
    engine's `amount` is sometimes the employee share and sometimes the 20% total, while a
    faithful body may legitimately quote either. Anything the authoritative working already
    says — including the sum of an employer/employee split it spells out — is by definition
    not a contradiction of it.
    """
    ok = set()
    if result.amount is not None:
        ok.add(int(result.amount))
    else:
        ok.add(0)                             # not applicable: 'TZS 0' is the faithful figure
    working = result.working or ""
    ok |= {int(m.replace(",", "")) for m in _WORKING_FIGURE.findall(working)}
    for a, b in _SPLIT.findall(working):
        ok.add(int(a.replace(",", "")) + int(b.replace(",", "")))
    return ok


def body_contradicts_siblings(body: str, siblings: dict) -> bool:
    """True iff `body` volunteers a figure for a levy in `siblings` that contradicts it.

    `siblings` maps levy name -> the authoritative ComputationResult for the OTHER compute
    sub-answers of the same question. The per-levy semantics mirror body_contradicts_working,
    with one deliberate difference for the not-applicable case: there, an asserted NONZERO
    figure is a contradiction on its own, without also requiring the body to show the
    multiplication. 'SDL: TZS 28,000' for an employer below the 10-employee threshold is
    flatly wrong however it is punctuated, and the enumeration shapes routinely omit the
    working.
    """
    if not body or not siblings:
        return False
    windows = _levy_windows(body)
    for levy, result in siblings.items():
        ok = _acceptable(result)
        for window in windows.get(levy, ()):
            results = {int(m.replace(",", "")) for m in _ATTRIBUTED.findall(window)}
            if not results:
                continue                      # named the levy but volunteered no figure
            if result.amount is None or int(result.amount) == 0:
                # Not applicable, or a genuine zero: any NONZERO figure the engine does not
                # itself state is a contradiction of the verdict.
                if any(r != 0 and r not in ok for r in results):
                    return True
            elif not (results & ok):
                # Positive amount: faithful bodies restate an authoritative figure somewhere in
                # the levy's own window. NONE of them being authoritative is the signal — the
                # same presence-of-correct robustness the own-levy rule relies on.
                return True
    return False

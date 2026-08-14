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

# --- what counts as an ASSERTED RESULT (widened 2026-08-10, D-FIDELITY-1) ----------------
#
# This was `=\s*TZS\s*([\d,]+)` — an equals sign and nothing else. A body saying "SDL ... sawa
# na TZS 210,000" against a working of TZS 17,500 therefore produced an EMPTY asserted-set and
# `body_contradicts_working` returned False, so the guard has been partly blind since it
# shipped. "sawa na" is the ordinary Swahili way to state a result.
#
# Widened on ATTESTED constructions, not on symmetry. Every connector below was harvested by
# frequency from what actually precedes a `TZS` amount across 946 distinct stored model
# generations (scratch/dfid1_constructions.py); the count that justifies each is in the comment.
# Bare levy-scoped "ni" ("PAYE ni TZS 128,000") was a candidate on frequency and was REJECTED:
# the R17 probes show it reads a PAYE band boundary, an SDL applicability threshold and an NSSF
# exemption as computed results. Frequency argued for it; the adversarial probes settled it.
#
# The sweep over every recoverable stored body found the blindness is TWO-SIDED. Of the five
# bodies whose verdict changes, two are contradictions the guard was missing — including an
# NSSF answer claiming a 20% employee share AND a 20% employer share of TZS 800,000, which the
# regex scorer passed and the judge called correct — and THREE are the guard firing on CORRECT
# bodies and blanking them, because their total line was punctuated "Jumla ya mchango: TZS
# 200,000" and `=`-only matching could not see it. Widening fixes both directions.
_ASSERT_CONNECTORS = (
    r"=",                        # 703 — arithmetic result
    r":",                        # 198 — enumeration/total line; was in _ATTRIBUTED only
    r"(?:ni\s+)?sawa\s+na",      #  24 — the Swahili "equals"; the construction that exposed this
    r"itakuwa",                  #   5 — "PAYE itakuwa TZS 72,000"
    r"kitakuwa",                 #   4 — "VAT withholding kitakuwa TZS 180,000"
    r"→",                        #   8 — arrow used as an equals in breakdown lines
    r"ni\s+karibu",              #  11 — "PAYE ni karibu TZS 78,000"; hedged, still an assertion
)
# Pin the digit run to its full length BEFORE the operand test. Without this the operand
# lookahead is defeated by backtracking: on "TZS 250,000 × 8%" the engine gives back a digit and
# matches "250,00" instead, so the operand is not excluded but silently renumbered. (Found by a
# sanity check, after an R17 probe passed for exactly that wrong reason.)
_DIGIT_BOUNDARY = r"(?![\d,])"
# An asserted result is a TERMINAL figure. A number followed by an arithmetic operator is an
# OPERAND: the band base in "Band 2 (8%): TZS 250,000 × 8% = TZS 20,000", or the left side in
# "Band 1 (0%): TZS 270,000 = TZS 0". This also removes intermediate operands the OLD `=`
# pattern read as results, so the change is not purely additive — its effect on
# currently-correct rows is measured in eval/results/dfid1_stored_body_sweep.json.
_OPERAND = r"(?!\s*[-+*x×−=])"

_ASSERTED_SRC = (r"(?:" + "|".join(_ASSERT_CONNECTORS) + r")\s*TZS\s*([\d,]+)"
                 + _DIGIT_BOUNDARY + _OPERAND)

_RESULT = re.compile(_ASSERTED_SRC, re.IGNORECASE)
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


# --- D-FIDELITY-3: the levy reduced by a phantom deduction ------------------------------
#
# THIS GUARD IS DELIBERATELY PARTIAL. It closes ONE family and must never be described as
# closing the intermediate-figure hole. Read the misses below before extending it.
#
# THE HOLE. `body_contradicts_working` clears a positive-amount body when the authoritative
# figure appears ANYWHERE in its asserted results. That permissiveness is correct and was
# chosen on evidence — it is what stops band bases and net-pay tails false-flagging
# eval_092/191/360/395 — but it cannot tell "restates the correct figure and concludes with
# it" from "passes THROUGH the correct figure on the way to a wrong one":
#
#     "…Jumla kabla ya punguzo = TZS 78,000. Punguzo la kibinafsi = TZS 26,000.
#       PAYE inayolipwa = TZS 78,000 - TZS 26,000 = TZS 52,000."
#
# 78,000 is present, so the body passes — while its CONCLUSION is wrong and is rendered
# directly above the deterministic working, which lends it the engine's authority.
#
# WHY THIS IS NOT A LAST-ASSERTED-FIGURE RULE. That was the obvious candidate and it was
# measured and rejected (2026-08-11). Over 121 recovered bodies it newly flagged 9, of which
# 4 were already caught by D-FIDELITY-2 and 3 were false positives — including eval_191 and
# eval_395, TWO of the four rows the permissiveness above exists to protect. Four cue-based
# narrowings were then built and probed: each converted exactly one over-broad failure into
# exactly one escape, with the total pinned at 5 of 16 probes. See the PROGRESS entry
# "cue-based narrowing relocates the failure".
#
# The reason no positional rule can work is that the defect and its commonest false positive
# are STRUCTURALLY IDENTICAL:
#
#     DEFECT   "… = TZS  78,000 - TZS 26,000 = TZS  52,000"   (taken FROM the levy)
#     NET PAY  "… = TZS 800,000 - TZS 78,000 = TZS 722,000"   (the levy taken FROM the salary)
#
# Both assert the authoritative figure and then operate on it. They differ only in the LABEL
# the model puts on the result, which is model phrasing — so separating them needs a live
# conclusion-labelling check, not an offline string rule.
#
# WHAT THIS RULE USES INSTEAD. One structural difference a string CAN see: which side of the
# operator the authoritative amount is on. In the defect it is the minuend — the thing being
# reduced. In net pay it is the subtrahend — the thing taken away. Combined with the fact that
# the engine's `amount` IS the final payable figure, so a body deriving a SMALLER figure from
# it has contradicted the engine by construction, while a LARGER derived figure is usually a
# legitimate conversion (per-year, per-employer, plus-sibling).
#
# WHAT IT MISSES — named, because a partial guard whose misses are unstated will be mistaken
# for a complete one. Measured on the 18-probe regression set
# (eval/fidelity_gate/lastfig_conclusion_018.jsonl), 8 of which this rule does NOT catch:
#
#   * THE PARAPHRASE FAMILY — every wrong conclusion whose arithmetic is not WRITTEN OUT.
#     "Jumla ya bendi zote = TZS 78,000. PAYE ya kulipwa: TZS 52,000" has no expression for
#     this rule to read, and the same holds for the `sawa na`, `itakuwa` and add-instead-of-
#     subtract punctuations (probes pos_02..pos_05). THIS FAMILY IS STILL OPEN.
#   * A wrong conclusion behind a net-pay tail, an example frame, or a repeated figure
#     (probes adv_01..adv_04) — the escapes the rejected narrowings would have opened, which
#     this rule does not open but also does not close.
#
# What it costs: ZERO. 0 false positives over 121 recovered bodies and over all 9 negative
# probes, including all four protected rows. It adds exactly one catch — the live TZS 52,000
# PAYE answer — and that catch is unique to it.

# `TZS A <op> … = TZS C` — A is the FIRST operand, C the asserted result. The middle is
# bounded and may not cross a '=' or a newline, so one match cannot span two expressions and
# the subtrahend of an earlier expression can never be read as the minuend of a later one.
_FIRST_OPERAND_EXPR = re.compile(
    r"TZS\s*([\d,]+)\s*[-−+×x*/]\s*[^=\n]{0,80}?=\s*TZS\s*([\d,]+)" + _DIGIT_BOUNDARY + _OPERAND,
    re.IGNORECASE,
)


def body_reduces_authoritative_amount(body: str, result: ComputationResult) -> bool:
    """True iff `body` derives a SMALLER, non-authoritative figure FROM the engine's amount.

    Deliberately partial — see the block comment above for the family it closes, the family it
    leaves open, and why the last-asserted-figure rule was rejected in its favour.
    """
    if not body or result.amount is None:
        return False
    amount = int(result.amount)
    ok = _acceptable(result)
    for m in _FIRST_OPERAND_EXPR.finditer(body):
        first = int(m.group(1).replace(",", ""))
        asserted = int(m.group(2).replace(",", ""))
        if first == amount and asserted < amount and asserted not in ok:
            return True
    return False


# --- D-FIDELITY-2: sibling levies -------------------------------------------------------

# The four levies the rules engine computes. Matched case-insensitively as whole words so
# 'sdl' in prose and 'SDL' in a breakdown line are the same token.
_LEVY_TOKEN = re.compile(r"\b(sdl|nssf|paye|wcf)\b", re.IGNORECASE)

# An amount ATTRIBUTED to the label that precedes it. This used to be `[:=]` — broader than
# _RESULT, which was '=' only — precisely because the enumeration shapes attribute with a colon
# as often as with '='.
#
# THE TWO ARE NOW ONE PATTERN, because the sibling guard turned out to share the same blindness.
# Verified by direct call rather than inferred from the corpus (which does not contain the
# form): given a one-employee payroll where the engine says SDL does not apply, a body
# volunteering "SDL = TZS 28,000" is caught, and so is "SDL: TZS 28,000" — but "SDL ni sawa na
# TZS 28,000", "SDL ni TZS 28,000" and "SDL itakuwa TZS 28,000" all pass. Three of five
# punctuations of the same wrong figure. One gap, one fix.
_ATTRIBUTED = _RESULT


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


# ---------------------------------------------------------------------------
# GUARD A — the answer contradicts a headcount the USER STATED (2026-08-14)
# ---------------------------------------------------------------------------
# A different animal from everything above. D-FIDELITY-1/2/3 check the model body against
# the ENGINE's working; this checks it against the QUESTION, and it exists for the fact
# path, where there is no working to check against. The live case:
#
#     Q: "Nina wafanyakazi 14 mishahara yote kwa mwezi ni milioni 6 ... nalipa shingapi"
#     A: "bado una wafanyakazi CHINI YA 10, hivyo hakuna ulazima wa kulipa SDL"
#
# The engine would have said TZS 210,000. It was never invoked (a `shingapi` routing miss),
# so the fact path free-generated a claim contradicting a number in the same sentence.
#
# ⚠️ WHY THIS ONE IS SAFE AND ITS SIBLING (Guard B) IS IMPOSSIBLE. Guard B tried to catch
# a fabricated *amount* by asking whether it was derivable from the user's figures. It
# cannot work: a fabricated figure and a legitimate transformation are both just arithmetic
# relationships to the user's number (TZS 400,000 is exactly half of the stated TZS 800,000,
# and halving is what correct per-person answers do). THIS guard needs no derivation
# allowance at all, because the claim is a COMPARISON, not a quantity:
#
#     A STATED 14 IS NOT "FEWER THAN 10" UNDER ANY TRANSFORMATION.
#
# That property is the whole safety argument. It is why the rule may only ever compare a
# stated count against a `chini ya N` claim ABOUT THE USER.
#
# ⚠️ DO NOT WIDEN THIS TO "any headcount in the body differs from the stated one". That
# version was written first and measured: 10 flags on 400 real rows, NINE of them FALSE
# POSITIVES — every one a CORRECT answer citing the SDL threshold ("una wafanyakazi 9,
# chini ya kiwango cha 10"). Citing the threshold is exactly what a correct SDL answer
# does. The narrow comparative form flags 0 of those 400 and catches the live case.
#
# Evidence base is thin and that is on the record: the precondition (stated count + a
# `chini ya N` claim) occurs in only 7 of 400 real rows, and the one true positive came
# from a live user message, not the corpus. Hence authored probes, not a sweep — R17.

_STATED_COUNT = re.compile(
    r"\b(?:nina|tuna|ninao|tunao|ana|anao|wana|niliajiri|nimeajiri|nimewaajiri)\s+"
    r"(?:wafanyakazi|waajiriwa|watumishi|vibarua)?\s*(\d{1,3})\b"
    r"|\b(?:wafanyakazi|waajiriwa|watumishi|vibarua)\s+(\d{1,3})\b",
    re.IGNORECASE)

# 'chini ya N' asserted ABOUT THE USER. The subject markers are required: a bare
# 'chini ya 10' is the THRESHOLD being stated, which every correct SDL answer does.
_CLAIMS_BELOW = re.compile(
    r"(?:una|unao|wewe|biashara yako|kampuni yako|duka lako|bado una)"
    r"[^.!?]{0,40}?chini ya\s+(\d{1,3})\b",
    re.IGNORECASE)


def stated_headcount(question: str):
    """The employee count the user asserts, or None. Max when several are present —
    the largest stated count is the one a 'fewer than N' claim must not contradict."""
    if not question:
        return None
    counts = [int(g) for m in _STATED_COUNT.finditer(question)
              for g in m.groups() if g is not None]
    return max(counts) if counts else None


def body_contradicts_stated_headcount(body: str, question: str) -> bool:
    """True iff the body tells the user they have FEWER THAN N employees when the
    question states a count of N or more."""
    if not body or not question:
        return False
    stated = stated_headcount(question)
    if stated is None:
        return False
    return any(stated >= int(m.group(1)) for m in _CLAIMS_BELOW.finditer(body))

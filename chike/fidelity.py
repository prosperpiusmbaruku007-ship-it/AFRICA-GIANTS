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
from decimal import Decimal
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
# THE GAP THAT REMAINS, MEASURED AND DELIBERATELY LEFT OPEN (2026-08-15).
# Second-person obligation verbs govern a TZS amount directly — "unapaswa kulipa TZS 130,000",
# "utalipa TZS 50,000" — and nothing below can see a verb, so those bodies assert NOTHING and
# the guard is silent on them. Real, and one construction further out than the `=`-only
# blindness recorded above.
#
# IT WAS NOT CLOSED, ON EVIDENCE. Adding the obligation verbs here changes 3 verdicts over 186
# recoverable body<->working pairs: 1 true positive and 2 FALSE positives
# (scratch/dfid4_connector_sweep.json). Both false positives are `party=total` questions whose
# bodies state the per-party components — "kwa TZS 500,000 utalipa TZS 50,000 kwa upande wa
# mwajiri na TZS 50,000 kwa upande wa mfanyakazi" — which is CORRECT, and which the guard
# blanks because the positive-amount branch needs the authoritative figure to be PRESENT and
# cannot add 50,000 + 50,000. Same shape as the bare levy-scoped `ni` rejected on 2026-08-10:
# frequency argued for it, the probes settled it.
#
# THE HONEST CLOSURE, named so nobody re-derives it: `_asserted_results` must return a MULTISET
# (it returns a set today, so the two 50,000s collapse to one) and the positive-amount branch
# needs a COMPONENT-SUM acceptance — a body whose asserted figures sum to the authoritative
# amount is faithful. That is its own sweep and its own risk to the permissiveness this file
# depends on, and it must not be smuggled in as part of something else.
#
# The one case that mattered is handled instead by D-FIDELITY-4 below, where the
# `party != 'total'` precondition makes the same construction safe to read.
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


# --- D-FIDELITY-4: the cross-party total offered as the asker's own obligation -----------
#
# THE DEFECT (nat_08, live and wrong after the router was already fixed). The engine resolved
# `party='employee'` and computed TZS 65,000. The body said:
#
#     "unapaswa kulipa TZS 130,000 kwa NSSF (sehemu ya mwajiri ni TZS 65,000 na
#      sehemu ya mfanyakazi ni TZS 65,000)"
#
# Every figure in it is TRUE. 130,000 really is the NSSF total and the attribution is correct.
# It is wrong only relative to what was ASKED — "how much do they cut from ME" — and on
# WhatsApp the prose above the working IS the answer.
#
# WHY THE EXISTING GUARDS CANNOT SEE IT, which is the finding this rule exists to record:
# `body_contradicts_working` is a SET-MEMBERSHIP check, not a CONCLUSION check. It asks whether
# the authoritative figure is AMONG the figures the body asserts, never whether it is the one
# the body concludes with — so a body that states the correct share and leads with the wrong
# headline satisfies it. (Verified by direct call, not inferred: scratch/oc01_fidelity_probe.json
# shows the same claim rewritten with `=` asserts {65000, 130000} and STILL does not fire.)
# D-FIDELITY-3 declines this direction by design — its comment notes a LARGER derived figure is
# "usually a legitimate conversion (per-year, per-employer, plus-sibling)", and the cross-party
# total is exactly the plus-sibling case.
#
# THIS RULE IS DIFFERENT IN KIND, not a widening. It settles the question from information the
# BODY DOES NOT CONTAIN — `result.inputs['party']`, the party the engine actually resolved.
# Whether the total is a legitimate conversion or the wrong answer is a property of the
# QUESTION, so no amount of reading the body can decide it. That is why this is a new rule.
#
# WHY IT IS NOT KEYED ON THE TOTAL BEING PRESENT — the obvious form, measured and REJECTED.
# Swept over every stored generation (scratch/dfid4_party_sweep.json): 24 bodies pair with a
# PARTY-SPECIFIC working, 5 of them state the cross-party total, and only ONE is the defect.
# Of the other four, one is an instrument artefact and THREE ARE CORRECT BODIES that state the
# sum and the share side by side:
#
#     "Sehemu ya mfanyakazi: ... = TZS 250,000. Jumla ya michango: ... = TZS 500,000"
#     "Jumla ya NSSF: TZS 80,000 (mwajiri) + TZS 80,000 (mfanyakazi) = TZS 160,000"
#
# A presence rule is therefore 4-FOR-1 AGAINST — the same trade shape that disqualified the
# SAFETY-2 cue extension at 3-for-1. And ZERO stored bodies state the total WITHOUT the
# authoritative figure, so the crisp "leads with the total only" signal has no corpus support
# and would not have caught nat_08 either, which states both.
#
# WHAT SEPARATES THE DEFECT FROM THE THREE CORRECT BODIES is what the total is ATTACHED to:
# a neutral SUM label ("Jumla ya michango") versus a SECOND-PERSON OBLIGATION addressed to the
# asker ("unapaswa kulipa"). fidelity.py's D-FIDELITY-3 comment says separating a defect from
# its false positive on a LABEL needs a live conclusion-labelling check rather than an offline
# string rule — true there, where the label was arbitrary model phrasing. Here the class is
# second-person obligation, which is narrow and enumerable; the forms below were HARVESTED by
# frequency from stored generations (scratch/dfid4_constructions.py), not invented.
#
# FULL VERB FORMS, NEVER THE `u-` PREFIX. The harvester's own first pass matched `u\w*` and
# returned `usajili` (registration), `user` (a chat-template artefact), `umepita`, and `umla`
# from *Jumla* — the bare-cue nesting hazard again, this time inside the instrument.
_OBLIGATION_2SG = re.compile(
    r"\b(?:unapaswa|unatakiwa|unachotakiwa|unachokatwa|unakatwa|unalipa|utalipa|ulipe)\b"
    r"(?:\s+\w+){0,3}?\s*TZS\s*([\d,]+)" + _DIGIT_BOUNDARY,
    re.IGNORECASE,
)


def cross_party_total(result: ComputationResult):
    """The employer+employee total implied by the engine's own rates, or None.

    Computed from `inputs` rather than assumed to be 2x the amount: the rates are both 10% for
    NSSF today, but a rule that hard-codes the doubling would silently produce a wrong total
    the day they diverge. The sweep instrument DID assume 2x and immediately collided with a
    per-employee salary that happened to equal it (scratch/dfid4_party_sweep.json, hit 1).
    """
    inputs = result.inputs or {}
    party = inputs.get("party")
    if party not in ("employee", "employer"):
        return None
    employer_rate, employee_rate = inputs.get("employer_rate"), inputs.get("employee_rate")
    if not employer_rate or not employee_rate or result.amount is None:
        return None
    own = employer_rate if party == "employer" else employee_rate
    if not own:
        return None
    total = (Decimal(result.amount) / Decimal(own)) * (Decimal(employer_rate)
                                                       + Decimal(employee_rate))
    return int(total)


def body_offers_total_as_own_obligation(body: str, result: ComputationResult) -> bool:
    """True iff the body tells the ASKER they owe the CROSS-PARTY TOTAL, when the engine
    resolved one specific party's share.

    Fires only when `party` is employee or employer — never on a total question, which is what
    keeps it clear of the permissiveness `body_contradicts_working` is measured onto, and what
    excludes the two correct 'utalipa TZS 50,000' bodies a generic connector widening would
    have blanked (scratch/dfid4_connector_sweep.json).
    """
    if not body:
        return False
    total = cross_party_total(result)
    if total is None or total == int(result.amount):
        return False
    return any(int(m.replace(",", "")) == total for m in _OBLIGATION_2SG.findall(body))


# --- D-FIDELITY-5: the obligation denied without a figure --------------------------------
#
# THE DEFECT (nat_14, live after A2 routed it correctly). The engine computed TZS 6,400 and
# the body said:
#
#     "hakuna PAYE ya kulipa kwa sababu kiwango cha sifuri kinatumika hadi TZS 270,000"
#
# — the exact failure the row's own expected_behavior names ("WRONG = 'below the threshold,
# nothing due'"). An employer is told no PAYE is owed when TZS 6,400 is.
#
# WHY NO EXISTING GUARD SEES IT, and this is the finding rather than the fix:
#
#     _asserted_results(body)             -> []        the body asserts NO figure at all
#     body_contradicts_working            -> False
#     body_reduces_authoritative_amount   -> False
#     body_offers_total_as_own_obligation -> False
#
# A CONTRADICTION DOES NOT NEED A NUMBER. All three rules above compare FIGURES — which
# amounts the body asserts, and whether the authoritative one is among them. A body that
# asserts NOTHING and denies the obligation qualitatively contradicts a positive engine amount
# completely, and satisfies every one of them VACUOUSLY, because the set being checked is
# empty. That is presence-not-conclusion in its purest form: the instrument passes by having
# nothing to look at.
#
# THE FALSE-POSITIVE SURFACE IS REAL AND WAS MEASURED FIRST (scratch/dfid5_sweep.json), because
# a denial is the CORRECT body whenever the engine's own amount is zero:
#
#     `hakuna paye`   10 corpus bodies, ALL of them amount=0 and all of them RIGHT
#                     ("Kwa mshahara wa TZS 250,000/mwezi, hakuna PAYE inayokatwa")
#     `haikatwi`       2 corpus bodies with amount>0 — and BOTH ARE CORRECT:
#                     "Hii inalipwa na mwajiri peke yake — haikatwi kutoka mshahara wa
#                      mfanyakazi" denies the DEDUCTION LOCUS, not the liability
#
# So the phrase can never be the discriminator; the ENGINE AMOUNT is. This rule fires only on
# a definite POSITIVE amount, which excludes all ten legitimate `hakuna paye` bodies by
# construction — `body_contradicts_working` already owns the amount==0 case. And `haikatwi`
# is excluded from the phrase list entirely: "not deducted from the wage" is a true statement
# about who bears a levy, not a denial that it is owed.
#
# THE DENIAL MUST NAME THE COMPUTED LEVY. A PAYE answer may correctly say "hakuna SDL" (fewer
# than ten employees) in the same breath; keyed on any levy this rule would blank it. So the
# levy-specific form is built from `result.computation`, and only two levy-agnostic phrases —
# both unambiguous denials of liability — are matched regardless.
_DENIAL_ANY_LEVY = ("hakuna cha kulipa", "hakuna kinachotakiwa kulipwa")


def body_denies_a_positive_obligation(body: str, result: ComputationResult) -> bool:
    """True iff the body denies an obligation the engine computed as a positive amount.

    Deliberately silent when `result.amount` is 0 or None: a denial is then the FAITHFUL body,
    and ten corpus rows prove it.
    """
    if not body or result.amount is None or int(result.amount) <= 0:
        return False
    low = body.lower()
    levy = (result.computation or "").lower()
    if levy and re.search(rf"hakuna\s+(?:\w+\s+){{0,2}}?{re.escape(levy)}\b", low):
        return True
    return any(p in low for p in _DENIAL_ANY_LEVY)


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
# D-FIDELITY-6 — the body states a WRONG STATUTORY RATE for a levy (2026-08-22)
# ---------------------------------------------------------------------------
# Specified by one live row. nat_24's WCF body said "unatakiwa kulipa 10% ya jumla ya mishahara
# kwa ajili ya WCF" — 10% is NSSF's employer share — with the engine's correct 0.5% line
# immediately below it. Three separate mechanisms let it through, and this rule closes all
# three because they all sat in that one row:
#
#   1. DIRECTION. body_contradicts_siblings scans for OTHER levies' windows. Here the body
#      volunteered a SIBLING'S rate for its OWN levy — the inverse case, uncovered.
#   2. VACUITY. WCF's sub-answer was an APPLICABILITY verdict, so ComputationResult.amount is
#      None and every figure-comparing rule above is satisfied trivially. Same shape as
#      D-FIDELITY-5: there is nothing to compare against. THIS RULE NEEDS NO COMPUTATION AT
#      ALL — it compares against the statute, not against a working, which is exactly why it
#      reaches the case the others cannot.
#   3. WINDOW. _levy_windows runs FORWARD from a levy token, so a rate stated BEFORE its levy
#      ("kulipa 10% ... kwa ajili ya WCF") lands in no window. Attribution here is
#      bidirectional, and every one of the five real detections in the sweep depended on it.
#
# ⚠️ WHY THIS IS SAFE AND GUARD B IS NOT. Guard B (fabricated AMOUNTS) is impossible because a
# fabricated figure and a legitimate transformation are both just arithmetic relationships to
# the user's numbers. A STATUTORY RATE IS A CONSTANT, not a derived quantity:
#
#     3.5% IS NOT 0.5% UNDER ANY TRANSFORMATION.
#
# That is GUARD A's property — a comparison, not a quantity — and it is the whole safety
# argument. Zero is lawful for every levy (a non-liability claim), and denial against a
# positive engine amount is D-FIDELITY-5's job, not this one.
#
# ATTRIBUTION RULE, and the asymmetry is grammatical rather than a fudge:
#   * an EXPLICIT attachment wins first — "asilimia 10% kwa ajili ya NSSF" names its own
#     subject, which must beat a levy word left over from the previous clause. Found in real
#     output where a stray 'fidia' otherwise captured NSSF's correct 10%.
#   * otherwise a PRECEDING levy wins — in "X ni asilimia N" the subject comes first. R17 probe
#     rg_01 ("SDL ni 3.5..., NSSF ni 20, na WCF ni 0.5") broke a nearest-wins rule immediately,
#     attributing NSSF's rate to WCF and flagging a correct breakdown.
#   * a FOLLOWING levy is the fallback, which is the defect's own shape.
#
# MEASURED BEFORE IT WAS WRITTEN (eval/fidelity/sweep_rate_guard.py ->
# eval/results/rate_guard_sweep.json): 150 recorded model replies swept, 5 flagged, ALL FIVE
# true positives — nat_24 live, nat_24 historic, nat_01 and nat_04 (2026-08-11) and the ad-hoc
# probe, every one a real levy-rate conflation. Plus 16 authored R17 probes, 16/16 as expected,
# 12 of them correct bodies written specifically to break an over-broad version.
_LEVY_RATES = {
    "sdl": frozenset({Decimal("3.5"), Decimal(0)}),
    # All three lawful employer/employee split arrangements (locked fact: 10+10, 15+5, 20+0).
    "nssf": frozenset({Decimal(20), Decimal(15), Decimal(10), Decimal(5), Decimal(0)}),
    "wcf": frozenset({Decimal("0.5"), Decimal(0)}),
    "paye": frozenset({Decimal(0), Decimal(8), Decimal(15), Decimal(20), Decimal(25),
                       Decimal(30)}),
}
# Swahili nicknames, so "kwa ajili ya mafunzo" is attributable. Same words as
# routing._LEVY_CUES, restricted to the unambiguous ones: a nickname that also has an ordinary
# reading ('fidia' = compensation) is fine HERE because attribution still requires a rate
# adjacent to it, and a correct body naming that rate is allowed anyway.
_RATE_NICKNAME = {
    "mafunzo": "sdl", "ufundi": "sdl", "ujuzi": "sdl",
    "uzeeni": "nssf", "pensheni": "nssf", "hifadhi ya jamii": "nssf",
    "fidia": "wcf",
}
_RATE_NICK_TOKEN = re.compile(
    "|".join(re.escape(k) for k in sorted(_RATE_NICKNAME, key=len, reverse=True)),
    re.IGNORECASE)
_RATE_FIGURE = re.compile(
    r"(?:asilimia\s*([0-9]+(?:[.,][0-9]+)?)|([0-9]+(?:[.,][0-9]+)?)\s*%)", re.IGNORECASE)
# A contrast clause states a rate in order to DENY it: "si asilimia 4", "NOT 14%". The
# 18%-substring false-PASS proved these are real and must never be read as the body's claim.
_RATE_NEGATION = re.compile(r"\b(?:si|sio|siyo|not|never|badala\s+ya|tofauti\s+na)\s*$",
                            re.IGNORECASE)
_RATE_ATTACH = re.compile(r"[\s,]*%?[\s,]*(?:kwa\s+ajili\s+ya|kwa|ya|ni\s+ya)?\s*",
                          re.IGNORECASE)
_RATE_BACKWARD_CHARS = 60
_RATE_FORWARD_CHARS = 60


def _rate_levy_marks(body: str):
    marks = [(m.start(), m.group(1).lower()) for m in _LEVY_TOKEN.finditer(body)]
    marks += [(m.start(), _RATE_NICKNAME[m.group(0).lower()])
              for m in _RATE_NICK_TOKEN.finditer(body)]
    return sorted(marks)


def attributed_levy_rates(body: str):
    """[(levy, Decimal rate)] for every rate the body attaches to a levy subject."""
    marks = _rate_levy_marks(body)
    if not marks:
        return []
    out = []
    for m in _RATE_FIGURE.finditer(body):
        raw = (m.group(1) or m.group(2)).replace(",", ".")
        try:
            rate = Decimal(raw)
        except Exception:
            continue
        if _RATE_NEGATION.search(body[max(0, m.start() - 12):m.start()]):
            continue
        back = fwd = None
        for pos, levy in marks:
            if pos >= m.end():
                dist = pos - m.end()
                if dist <= _RATE_FORWARD_CHARS and (fwd is None or dist < fwd[0]):
                    fwd = (dist, levy)
            else:
                dist = m.start() - pos
                if dist <= _RATE_BACKWARD_CHARS and (back is None or dist < back[0]):
                    back = (dist, levy)
        attached = fwd is not None and _RATE_ATTACH.fullmatch(body[m.end():m.end() + fwd[0]])
        best = fwd if attached else (back or fwd)
        if best:
            out.append((best[1], rate))
    return out


def body_states_wrong_levy_rate(body: str) -> bool:
    """True iff the body attaches a rate to a levy that the statute does not give it.

    Needs no ComputationResult, by design — see the block comment above.
    """
    if not body:
        return False
    for levy, rate in attributed_levy_rates(body):
        allowed = _LEVY_RATES.get(levy)
        if allowed is not None and rate not in allowed:
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


# ─────────────────────────────────────────────────────────────────────────────────────────────
# D-FIDELITY-7 — A STATED THRESHOLD THAT IS NOT THE STATUTORY ONE
#
# WHY THIS EXISTS, AND WHY IT IS BUILDABLE WHEN SO LITTLE ELSE IS. `pic_11`, live 2026-08-23:
#
#     reply: "Presumptive tax inatumika kwa mauzo CHINI YA MILIONI 10."
#     fact in its own context, at rank 1: "mauzo yasiyozidi TZS 100,000,000"
#
# An order of magnitude wrong, with the correct figure at the top of the prompt. The
# prompt/generation/adapter separation could not recover it under ANY arm — the fact alone, an
# instruction to use only that fact, or the question rephrased — which made it the first
# measured justification for a retrain in this project.
#
# R19 SAYS TRY THE CHEAP MECHANISM FIRST, AND R19 IS WHY THIS ONE IS POSSIBLE. A stated
# threshold is a STATUTORY CONSTANT, not a quantity derived from the user's figures: no lawful
# transformation of anything the user typed makes "milioni 10" the presumptive ceiling. So this
# is a constant comparison exactly like D-FIDELITY-6's rate check, it needs no ComputationResult,
# and it works on the FACT path where every rule before the sixth goes vacuous.
#
# THE TWO NARROWING DECISIONS, both chosen as the smallest thing that closes the case (R17):
#
#   1. A THRESHOLD FRAME IS REQUIRED. A subject cue near a number is not enough — a correct
#      computation ("Kodi ya makadirio = 3.5% x TZS 30,000,000") carries both. Only
#      kizingiti / kikomo / yasiyozidi / chini ya / zaidi ya and their English forms count.
#      `hadi` and `kuanzia` are DELIBERATELY EXCLUDED: they are equally at home in a band
#      recitation and in a sentence about the user's own turnover, so including them would
#      attribute the user's figure to the statute.
#   2. IF ANY AMOUNT IN THE SENTENCE IS A LAWFUL THRESHOLD, THE SENTENCE PASSES. Probe tf_11 is
#      the reason: "Mauzo yako ya TZS 250,000,000 yamezidi kizingiti cha TZS 200,000,000" is
#      CORRECT and contains a non-statutory number (the user's own). A body that has stated the
#      right threshold is not making a wrong threshold claim.
#      THE COST OF THAT CHOICE, STATED: a body stating BOTH a correct and an incorrect threshold
#      escapes. Accepted — it errs toward silence, which is the only direction a guard that
#      blanks text may err in.
_STATUTORY_THRESHOLDS = {
    # presumptive: the First Schedule band edges AND the para 2(2) ceiling. Band edges belong
    # here because a correct answer may legitimately state one.
    "presumptive": frozenset({4_000_000, 7_000_000, 11_000_000, 100_000_000}),
    # VAT registration: both limbs — 200M/12mo OR 100M/6mo. RE-SOURCED 2026-08-31: found and
    # read directly — GN 448Y of 2023 s.4, amending Reg.14 of GN 225/2015 (VAT Act s.94) —
    # confirming both figures are real (unlike EFD, this constant was duplicated-but-not-
    # fabricated). Only the effective date was wrong everywhere it was duplicated: 1 July
    # 2023, not July 2024. See locked_facts.json's vat_threshold_200m_july2024_increase
    # correction_note for the full sweep.
    "vat_registration": frozenset({100_000_000, 200_000_000}),
    # EFD: EMPTY, not a typo (2026-08-29). This used to be frozenset({11_000_000}) -- the same
    # fabrication as locked_facts.json's efd_threshold_tzs_11m and rules_engine's now-removed
    # EFD_ANNUAL constant. Re-verified against TAA Cap.438 s.44 directly: NO turnover figure is
    # lawful for EFD, at any level -- fiscal-receipt issuance is the default for everyone, and
    # the only exemption is a Commissioner-General public notice naming a class, not a number.
    # An empty lawful set means ANY amount asserted as "the EFD threshold" is now correctly
    # flagged as wrong (see narrowing decision 2 above: `body_amounts & lawful` can never be
    # non-empty against an empty set, so the escape never fires for this subject) -- tg_08,
    # this project's own former example of a "correct" EFD-threshold statement, is the specimen
    # that proves it (see tests/test_threshold_guard.py).
    "efd": frozenset(),
}
_THRESHOLD_SUBJECT = {
    "makadirio": "presumptive", "makisio": "presumptive", "presumptive": "presumptive",
    "kusajili vat": "vat_registration", "kujisajili vat": "vat_registration",
    "usajili wa vat": "vat_registration", "kizingiti cha vat": "vat_registration",
    "vat registration": "vat_registration",
    "efd": "efd", "mashine ya risiti": "efd",
}
_THRESHOLD_SUBJECT_RE = re.compile(
    "|".join(re.escape(k) for k in sorted(_THRESHOLD_SUBJECT, key=len, reverse=True)),
    re.IGNORECASE)
_THRESHOLD_FRAME = re.compile(
    r"kizingiti|kikomo|yasiyozidi|isiyozidi|hayazidi|chini\s+ya|zaidi\s+ya|"
    r"\bthreshold\b|\bexceed", re.IGNORECASE)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


# Every statutory threshold in the table is >= TZS 4,000,000. A small integer next to a frame
# word is a PERIOD or a COUNT, not a threshold — the sweep caught a clarification reading
# "je ni jumla ya miezi 12, au ya miezi 6 mfululizo?" and attributed 12 and 6 as VAT thresholds.
_THRESHOLD_MONEY_FLOOR = 1_000_000

# ─────────────────────────────────────────────────────────────────────────────────────────────
# ⛔ THE THREE NARROWINGS, 2026-10-06 — MEASURED BEFORE WIRING, NOT AFTER
#
# This guard was built 2026-08-23 and held NOT_WIRED. Before wiring it, it was run over every
# stored reply, every gold answer and every training pair this project holds
# (eval/fidelity/price_threshold_guard_before_wiring.py → eval/results/
# threshold_guard_prewiring_2026_10_06.json). On 5,593 rows it flagged 45, and the flags were
# overwhelmingly FALSE POSITIVES — including THREE GOLD ANSWERS a human had asserted correct:
#
#   eval_347  "TZS 200,000,000 ni kizingiti cha usajili wa VAT, si EFD. EFD haina kizingiti…"
#   eval_355  "TZS 10,999,000 au TZS 11,000,000 hazibadilishi jibu … hakuna kizingiti…"
#   eval_331  "Hakuna kizingiti cha mauzo kwa EFD (TZS 9,000,000 haibadilishi jibu)."
#
# eval_347 is THE ROW THIS WIRING EXISTS TO FIX. Wired unnarrowed, the guard would have
# destroyed the correct answer to it — and because the fact path cannot be blanked (see
# orchestrator._validate_and_clean), destroying means an EMPTY REPLY. The 22 unit tests passed
# the whole time: R33 exactly, a probe set validated against variants of its own design.
#
# N1  POLARITY. A negated FRAME ("hakuna kizingiti", "haina kizingiti") DENIES that a threshold
#     exists — the opposite of claiming a wrong one — and a negated AMOUNT ("SI TZS 200,000,000")
#     is a MENTION, not an assertion. This is the mention-vs-assertion rule recorded in CLAUDE.md
#     on 2026-10-05, and the WORD-BOUNDING is the hard-won half: a bare `si\s` matches inside the
#     ordinary Swahili word `kiasi `, and in the NSSF-fine sweep that one unbounded alternative
#     silently DELETED the single real false positive from the adjudicated set. Every alternative
#     here is word-bounded.
#     Deliberately NOT included: negative VERB forms (`haujafika`, `hujafikia`). "haujafika
#     kizingiti cha TZS 11M" asserts the threshold and denies only that the user has reached it.
#
# N2  THE FRAME MUST REACH THE AMOUNT BACKWARD WITHOUT CROSSING ANOTHER AMOUNT. This is what
#     separates a threshold CLAIM from the user's own turnover, and it does the heavy lifting:
#     "Kwa mauzo ya TZS 250M (zaidi ya TZS 200M/miezi 12)" has no frame before 250M, so 250M is
#     not a threshold claim, while 200M has `zaidi ya` immediately before it and is. The old
#     sentence-level rule attributed EVERY amount in the sentence to EVERY subject in it.
#
# N3  LAWFUL FOR A CO-NAMED SUBJECT. If an amount is a statutory threshold for ANY subject named
#     in the same sentence, it is not a fabricated threshold. The old escape asked only about the
#     SUBJECT'S OWN lawful set, and for EFD that set is deliberately EMPTY — so the escape was
#     DEAD for EFD by construction, which is why 20-odd correct sentences of the form "…lazima
#     utumie EFD … kizingiti cha TZS 200M" were flagged: a real VAT threshold attributed to EFD.
#     Mis-attribution is D-FIDELITY-6's class, and in the bare-magnitude shape it was measured
#     UNBUILDABLE there. This guard's job is FABRICATED CONSTANTS (the 11M EFD threshold, pic_11's
#     milioni 10), and a global escape would not do: 11,000,000 IS a lawful presumptive band edge,
#     so "lawful anywhere in the table" would release the guard's single most important true
#     positive. Co-named is the line that keeps it.
#
# COST OF N3, STATED (the cost of narrowing decision 2 is already stated above): "kizingiti cha
# EFD ni TZS 200,000,000" escapes when VAT is also named. Accepted — it errs toward silence,
# the only direction a guard that removes text may err in, and the claim is near-true in effect
# (VAT registration does compel EFD) rather than fabricated.
_THRESHOLD_NEGATION = re.compile(
    r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bhakuna\b|\bhaina\b|\bhakina\b|\bhamna\b|"
    r"\bnot\b|\bno\b|\bnever\b)[\s:,—–-]*(?:tzs\s*)?$|"
    # 2026-11-16: `hapana` followed by a COMMA is the answer opener ("Hapana, kizingiti ni TZS 11,000,000") and does not negate the noun after it; only the comma-free "hapana kizingiti" does.
    # The comma form had exempted exactly the shape D-FIDELITY-7 exists for (found by a probe written for the subject fallback, sf_02).
    r"\bhapana\b[\s:—–-]*(?:tzs\s*)?$", re.IGNORECASE)
# How far back a negation may sit and still govern. 24 chars covers "SI TZS 200,000,000" and
# "haina kizingiti" without reaching across a clause boundary.
_THRESHOLD_NEGATION_CHARS = 24
_VAT_TOKEN = re.compile(r"\bvat\b", re.IGNORECASE)


def _negated_at(sentence: str, pos: int) -> bool:
    """True iff a word-bounded negation immediately precedes offset `pos`."""
    return bool(_THRESHOLD_NEGATION.search(
        sentence[max(0, pos - _THRESHOLD_NEGATION_CHARS):pos]))


def _frame_reaches(sentence: str, amount_pos: int, amount_positions) -> bool:
    """N2 — is there a frame word before `amount_pos` with no other amount in between?"""
    frames = [m for m in _THRESHOLD_FRAME.finditer(sentence) if m.end() <= amount_pos]
    if not frames:
        return False
    frame = frames[-1]                                 # the nearest one behind the amount
    if _negated_at(sentence, frame.start()):
        return False                                   # N1 — a negated frame denies a threshold
    return not any(frame.end() <= p < amount_pos for p in amount_positions)


def stated_wrong_thresholds(body: str, question: str = ""):
    """[(subject, stated_amount)] for every sentence making a non-statutory threshold claim.

    THE LAWFUL-AMOUNT ESCAPE IS BODY-LEVEL, NOT SENTENCE-LEVEL, and the sweep is why. A recorded
    reply stated the correct threshold in one sentence and compared against it in the next:

        "…kizingiti chako cha usajili wa VAT ni TZS 200,000,000 tu.
         Mapato ya TZS 205,000,000 hayazidi kizingiti hicho…"

    Sentence-level, the second sentence carries only 205,000,000 and flags. That reply IS wrong —
    205M plainly exceeds 200M — but it is wrong about a COMPARISON, which is a derived quantity
    and Guard B territory (R19), not a wrong constant. Catching it here would be the right verdict
    for the wrong reason, and the same shape with a CORRECT comparison ("TZS 150,000,000
    hayazidi…") would be a plain false positive. **A body that has stated the right threshold
    anywhere is not making a wrong threshold claim.**
    """
    if not body:
        return []
    from .swahili_numbers import parse_amounts, parse_amounts_located
    body_amounts = {int(a) for a in parse_amounts(body)}
    # 2026-11-16 (eval_355): the subject can live in the QUESTION only. "Mauzo yangu ni TZS 10,999,000, je EFD ni lazima?" was answered "Hapana, kwa sababu umefika chini ya kizingiti cha TZS 11M"
    # and the body never says EFD, so no sentence had a subject and the guard could not fire (the notation was never the problem: 11M, 11,000,000 and milioni 11 all flag once EFD is in the body).
    # A sentence that names NO subject of its own inherits the question's. Every other narrowing (lawful-amount escape, negation, frame reach, co-named lawful sets) applies unchanged.
    q_subjects = ({_THRESHOLD_SUBJECT[m.group(0).lower()] for m in _THRESHOLD_SUBJECT_RE.finditer(question)} if question else set())
    out = []
    for sentence in _SENTENCE_SPLIT.split(body):
        subjects = {_THRESHOLD_SUBJECT[m.group(0).lower()]
                    for m in _THRESHOLD_SUBJECT_RE.finditer(sentence)} or set(q_subjects)
        if not subjects or not _THRESHOLD_FRAME.search(sentence):
            continue
        located = [(p, int(a)) for p, a in parse_amounts_located(sentence)]
        positions = [p for p, _ in located]
        amounts = [(p, a) for p, a in located if a >= _THRESHOLD_MONEY_FLOOR]
        if not amounts:
            continue
        # N3 — every lawful threshold of every subject NAMED IN THIS SENTENCE.
        co_named_lawful = set().union(*(_STATUTORY_THRESHOLDS[s] for s in subjects))
        # N3b — A BARE MENTION OF VAT ADMITS THE VAT-REGISTRATION MAGNITUDES, and it is needed
        # because the subject map requires a REGISTRATION phrase (`kusajili vat`, `usajili wa
        # vat`) that correct prose routinely omits: "VAT 18% … (kizingiti TZS 200M/mwaka)",
        # "EFD ukifikia kizingiti", "zaidi ya TZS 200M … EFD nayo ni lazima". Seven training
        # rows stating the VAT threshold CORRECTLY were flagged as fabricated EFD thresholds on
        # the narrowed measurement, which is the shape N3 exists to stop and could not see.
        #
        # SAFE BECAUSE IT IS NOT A GLOBAL ESCAPE. Only 100M/200M are admitted, and only when the
        # sentence says "vat". The guard's own most important true positive — the fabricated
        # TZS 11,000,000 EFD threshold — is a lawful PRESUMPTIVE band edge, so admitting the
        # whole table would release it. Verified: batch_012:36/37 state "kizingiti cha EFD (TZS
        # 11M+ au zilizosajiliwa VAT)", mention VAT, and REMAIN flagged.
        if _VAT_TOKEN.search(sentence):
            co_named_lawful |= _STATUTORY_THRESHOLDS["vat_registration"]
        for subject in sorted(subjects):
            lawful = _STATUTORY_THRESHOLDS[subject]
            if body_amounts & lawful:
                continue                      # narrowing decision 2 — see the header
            for pos, a in amounts:
                if a in co_named_lawful:
                    continue                  # N3
                if _negated_at(sentence, pos):
                    continue                  # N1 — the amount is MENTIONED, not asserted
                if not _frame_reaches(sentence, pos, positions):
                    continue                  # N2
                out.append((subject, a))
    return out


def body_states_wrong_threshold(body: str, question: str = "") -> bool:
    """True iff the body claims a statutory threshold that is not the statutory threshold. `question` (optional) supplies the subject a body never names."""
    return bool(stated_wrong_thresholds(body, question))


# ─── D-FIDELITY-8 — A FEE STATED FOR THE WRONG BAND OF A PUBLISHED FEE TABLE ─────
# Built, priced and wired 2026-10-08. THE DEFECT, measured live against the deployed index:
#
#     Q: "Mtaji wa hisa wa kampuni yangu ni TZS 2,000,000,000. Ada ya kusajili ni ngapi?"
#     A: "Ada ya kusajili kampuni yenye mtaji wa hisa unaozidi TZS 5,000,000 ni TZS 290,000."
#
# TZS 2,000,000,000 is band 8 (>1bn-10bn) and the fee is TZS 600,000. The reply returned the
# >20M-50M band AND misstated its floor as 5,000,000.
#
# WHY A GUARD IS THE ONLY LAYER THAT REACHES IT. Row 181 measured at RANK 1 (0.9167) for that
# exact query, rank 3 on a paraphrase, rank 1 on the sibling ask -- the correct ladder was IN
# CONTEXT. CLAUDE.md's step-zero table: at rank 1-3 with a wrong answer the defect is in
# GENERATION, and every wording hour is spent on the wrong layer. Staleness is excluded from
# inside the live harness: the no-share-capital probe reads the SAME row 181 and returns the
# NEW TZS 500,000.
#
# R19 SAYS BUILDABLE, and the test is the one R19 prescribes: write the claim the guard would
# reject -- "the fee for TZS 2,000,000,000 of share capital is TZS 290,000" -- and ask whether
# it could be true under some lawful transformation of the user's own numbers. It could not:
# the fee is a LOOKUP against a fixed published table. A CONSTANT comparison, the same side of
# R19 as D-FIDELITY-7, and like it this needs no ComputationResult, so it reaches the FACT
# path where every pre-sixth D-FIDELITY rule goes vacuous.
#
# ⚠️ CONTAINMENT, NOT A FIX -- the same caveat eval_347 carries. This stops a confident wrong
# fee and hands over the table instead of the fee. It moves Bar A's A1 (confident wrong
# answers) and NOT A2 (answered correctly): the user still has to read off their own band.
# A2 needs band SELECTION to work, which is compute-path work. Do not read a falling
# wrong-answer count as a rising correct-answer count.
#
# FOUR NARROWINGS, each one a lesson already paid for, each pinned by a specimen in
# tests/test_fee_band_guard.py:
#   N1 SUBJECT GATE — share-capital registration only. Without it every BRELA fee is in
#      scope and the bare magnitudes collide (why bare 'TZS 70,000' and bare 'asilimia 10'
#      were both rejected as regen anchors).
#   N2 PROVENANCE — the user's amount comes from the QUESTION, the fee from the BODY.
#      Conflating them is D-FIDELITY-7's N2 failure in table form.
#   N3 FEE vs BAND EDGE, GRAMMATICALLY. In Swahili a fee follows the predicative `ni`; a band
#      edge follows a comparative (`unaozidi`, `zaidi ya`, `hadi`). The defective sentence
#      contains BOTH, so separating them is the whole job — and a proximity window cannot:
#      the first version of this rule used one and was INERT on its own founding specimen,
#      reporting 0 flags over 13,632 rows with a verdict of "SAFE TO PROPOSE".
#   N4 POLARITY — a fee named under a negation ("si TZS 290,000") is a mention. Correct rows
#      deliberately name wrong values to reject them.
# Plus a LADDER-RECITAL exclusion: a body listing the whole table is answering with the table,
# not with one fee, and must not be judged as if it had chosen.
_FEE_SUBJECT = re.compile(
    r"mtaji\s+wa\s+hisa|share\s+capital|ada\s+ya\s+kusajili\s+kampuni", re.I)
_FEE_NUM = re.compile(r"(?:TZS\s*)?([\d][\d,\.]{2,})", re.I)
_FEE_MARK = re.compile(r"(?:\bni\b|\bada\s+ni\b|\bgharama\s+ni\b|\bis\b|\bcosts?\b)"
                       r"[\s:]*(?:TZS\s*|Tsh\.?\s*)?$", re.I)
_FEE_EDGE = re.compile(r"(?:unaozidi|inazidi|zaidi\s+ya|hadi|kati\s+ya|chini\s+ya|juu\s+ya"
                       r"|above|over|up\s+to|exceed\w*|between)[\s:]*(?:TZS\s*)?$", re.I)
_FEE_NEG = re.compile(r"\b(?:si|sio|siyo|hakuna|not|no)\b[\s:,\-—]*(?:TZS\s*)?$", re.I)


def _fee_int(s: str):
    try:
        return int(s.replace(",", "").split(".")[0])
    except ValueError:
        return None


def expected_share_capital_fee(capital: int):
    """The published fee for this share capital, or None if it falls in no band.

    Reads the ladder from `chike.clarification`, which owns it as the replacement copy's
    single source. A second copy of a fee table in the guard layer is the dual-file
    divergence this project keeps paying for, and the copy is generated from the same tuple.
    """
    from chike import clarification
    for lo, hi, fee in clarification.BRELA_SHARE_CAPITAL_BANDS:
        if (lo is None or capital > lo) and (hi is None or capital <= hi):
            return fee
    return None


def stated_wrong_fee_band(question: str, body: str):
    """(capital, expected_fee, stated_fee) if the body states a fee that is wrong for the
    share capital the QUESTION states — otherwise None."""
    from chike import clarification
    if not _FEE_SUBJECT.search(f"{question} {body}"):
        return None                                                     # N1
    caps = [_fee_int(m.group(1)) for m in _FEE_NUM.finditer(question)]   # N2
    caps = [c for c in caps if c and c >= 100_000]
    if not caps:
        return None
    capital = max(caps)
    want = expected_share_capital_fee(capital)
    if want is None:
        return None
    if len(list(_FEE_NUM.finditer(body))) >= 7:
        return None                                      # the body recites the whole ladder
    lawful = {f for _, _, f in clarification.BRELA_SHARE_CAPITAL_BANDS}
    for m in _FEE_NUM.finditer(body):
        v = _fee_int(m.group(1))
        if v is None or v == capital:
            continue
        lead = body[max(0, m.start() - 24):m.start()]
        if _FEE_NEG.search(lead):
            continue                                                    # N4
        if _FEE_EDGE.search(lead):
            continue                                                    # N3, band edge
        if not _FEE_MARK.search(lead):
            continue                                                    # N3, not a fee
        if v == want:
            return None                                  # the right fee is stated: no defect
        if v in lawful or v > 10_000:
            return (capital, want, v)
    return None


def body_states_wrong_fee_band(question: str, body: str) -> bool:
    """True iff the body states a registration fee that is wrong for the stated share capital."""
    return bool(stated_wrong_fee_band(question, body))


# ─── D-FIDELITY-9 — A MONEY FIGURE THE QUESTION NEVER SUPPLIED AND THE ENGINE NEVER STATED ──
#
# ⛔ SCOPED BEFORE BUILT, AND THE SCOPING IS WHY THIS RULE IS THE NARROW ONE.
# eval/fidelity/scope_render_body_working_disagreement_2026_10_10.py measured the obvious form
# first — "flag any money figure in the body that is absent from the engine's working" — over
# every stored reply this project holds. 439 replies, 64 with a body AND a working, and that
# rule flags 14 at a precision of 1/14:
#
#   eval_092  "NSSF ya mwajiri = 10% x TZS 400,000 = TZS 40,000"   the per-head breakdown
#   eval_296  "TZS 18,000 x 26 = TZS 468,000/mwezi"                 the DAILY wage given
#   eval_395  "TZS 800,000 - TZS 78,000 = TZS 722,000"              NET PAY, which the question
#                                                                   EXPLICITLY ASKED FOR and the
#                                                                   working cannot contain
#   eval_360  "TZS 270,001 hadi 760,000"                            PAYE band edges
#   + 9 more, 11 of the 13 being CORRECT bodies
#
# Wiring that would be D-FIDELITY-7's unnarrowed shape: deleting the half of the answer the
# user asked for. THE ADJUDICATION PRODUCED THE DISCRIMINATOR, and it is R19's line exactly.
# All 13 false positives derive from a figure THE QUESTION SUPPLIED. th_22 — the one true
# positive, live, "Kwa mfanyakazi MMOJA: WCF = TZS 50,000 kwa mwaka" — differs in that its
# question ("Nina mfanyakazi mmoja tu — je nalipa WCF?") supplies NO FIGURE AT ALL.
#
# With no input amount, any money figure in the body is unsupported BY CONSTRUCTION: there is
# no lawful transformation of the user's numbers that reaches it, because there are no numbers.
# R19 calls that a CONSTANT comparison and buildable, as against the derived-quantity form
# (Guard B) which is impossible. Measured on the same 64 pairs the loose rule was priced on:
# 1 flag, 0 false positives, and the flag IS th_22.
#
# ⚠️ SOFT, DELIBERATELY, AND HERE IS WHAT SOFT MEANS. One true positive on 64 pairs is one row,
# not a measured rate, so the rule is held to the narrowest scope that still reaches the live
# defect:
#   * COMPUTE PATH ONLY. The fact path cannot be blanked (_render returns the body alone), so
#     there the remedy is silence or replacement copy — a separate decision with its own cost.
#     Excluded on measured harm, not on absence of defect.
#   * REQUIRES AN EMPTY QUESTION-SIDE FIGURE SET. One figure in the question and the rule stands
#     down entirely, which is what drops all 13.
#   * Widening it is a HOLD WITH AN EXPIRY in eval/controls/audit_control_fires.py, so "until it
#     has seen more" is a dated decision rather than a note that lapses (R35).
#
# ⚠️ BOTH NOTATIONS, because a figure sweep keyed on digits is blind to words by construction
# and this project has already paid for that once: R36's EFD count went 3 -> 7 -> 14 as the
# notation widened, and Swahili writes money both ways in one file. "TZS 50,000" and "milioni
# 11" are the same claim and are compared as integers.
_FIG_DIGITS = re.compile(r"(?:TZS|tsh|shilingi)\s*([\d][\d,\.]*)|\b(\d{6,})\b", re.I)
# ⛔ BOTH WORD ORDERS, AND THE SWAHILI ONE IS THE ONE THAT MATTERS. My first version was
# `(\d+)\s*(milioni|elfu)` — English order, "11 milioni" — and Swahili writes **"milioni 11"**,
# which is the form CLAUDE.md itself quotes from the worst row of the EFD quarantine ("Kizingiti
# sahihi ni TZS milioni 11"). The pattern matched NOTHING on the notation it was added for, and
# a cue that matches nothing is indistinguishable from a cue with nothing to match (R39). Caught
# by a probe written in the real word order, not by reading the pattern.
_FIG_WORDS = re.compile(
    r"\b(?:(?P<n1>\d+(?:\.\d+)?)\s*(?P<s1>milioni|bilioni|elfu)"
    r"|(?P<s2>milioni|bilioni|elfu)\s+(?P<n2>\d+(?:\.\d+)?))\b", re.I)
_FIG_SCALE = {"elfu": 1_000, "milioni": 1_000_000, "bilioni": 1_000_000_000}
# Below this a "figure" is a count, a year, a day-of-month or a percentage written oddly, not a
# money claim. The threshold guard uses the same reasoning with its own floor.
_FIG_FLOOR = 1_000


def _figures(text: str):
    """{int} — every money claim in `text`, in either notation, normalised to shillings."""
    out = set()
    for m in _FIG_DIGITS.finditer(text or ""):
        tok = (m.group(1) or m.group(2) or "").strip(".,")
        digits = tok.replace(",", "").split(".")[0]
        if digits.isdigit() and int(digits) >= _FIG_FLOOR:
            out.add(int(digits))
    for m in _FIG_WORDS.finditer(text or ""):
        number = m.group("n1") or m.group("n2")
        scale = m.group("s1") or m.group("s2")
        try:
            value = int(float(number) * _FIG_SCALE[scale.lower()])
        except (ValueError, KeyError, TypeError, AttributeError):
            continue
        if value >= _FIG_FLOOR:
            out.add(value)
    return out


def _asserted_figures(text: str):
    """[(amount, sentence)] for money claims the text ASSERTS — negated ones are MENTIONS.

    Reuses `_negated_at` and therefore `_THRESHOLD_NEGATION`, rather than restating the
    polarity rule: a cue list written twice has to be corrected twice, and CLAUDE.md records a
    cue surviving removal from one of two rules. Same reason the superseded-value sweep, the
    offline test and the pre-flight gate all import one `_asserted_spans`.
    """
    out = []
    for sentence in _SENTENCE_SPLIT.split(text or ""):
        for m in list(_FIG_DIGITS.finditer(sentence)) + list(_FIG_WORDS.finditer(sentence)):
            if _negated_at(sentence, m.start()):
                continue
            for amount in _figures(m.group(0)):
                out.append((amount, sentence.strip()))
    return out


def unsupported_body_figures(question: str, body: str, working: str):
    """[(amount, sentence)] for money the body asserts that neither the question nor the
    engine's working contains — and ONLY when the question supplies no figure at all."""
    if _figures(question):
        return []                     # the narrowing that drops all 13 false positives
    known = _figures(working) | _figures(question)
    return [(amount, sentence) for amount, sentence in _asserted_figures(body)
            if amount not in known]


# ---- D-FIDELITY-31 (2026-11-24, founder: build and price; wire ONLY with 0 gold flags and every flag read): A MONEY FIGURE IN A COMPUTE BODY THAT NO ENGINE PRODUCED AND NO ONE-STEP ARITHMETIC REACHES.
# Founding specimen (live, b96e8a8 and 84d8621, eval/results/sdl_three_routes_live_2026_11_23.json): the SDL+NSSF compute reply says "SDL ... TZS 210,000 (TZS 150,000 kwa mwajiri)"; the engine produced 210,000 and the NSSF figures, 150,000 is in neither the question
# nor any working, and `guards=[]`. D-FIDELITY-9 is off there (its gate is "the question supplies no figure at all") and its loose form is 1/14 precise because the user's own figures, per-head breakdowns and net pay are all LEGITIMATE derivations (eval_092, eval_296, eval_395).
# THE DIFFERENCE FROM THAT LOOSE RULE IS THE SUPPORT SET. A body amount is supported if it is (1) a figure in the question, (2) a figure in ANY engine working of the request (SIBLING levies included: a sibling's figure is not an invention), or (3) a ONE-STEP result of two supported
# amounts (x + y, x - y, x * y, x / y), of a supported amount and a RATE present in the question / the workings / the locked rate set (x * r), or of a supported amount and a COUNT the question states (x / n, x * n: a per-head share). 150,000 is 2.5% of 6,000,000 and 2.5% is
# in none of those sets, so it is unsupported; a two-step derivation by the model (x * r * 12) is flagged although correct: a KNOWN LIMIT, priced.
# R25. (1) Defect: a shilling figure the engine did not produce and no one-step arithmetic reaches (one live reply). (2) What CORRECT output could it damage: a per-head breakdown, a net pay, a daily-wage product, a rate-times-payroll figure and a figure the user supplied are all supported by rule (3);
#   a two-step annual figure is the exception, and the action (BODY BLANKED, the working still renders) costs one sentence, never the answer.
_D31_RATE = re.compile(r"(\d+(?:[.,]\d+)?)\s*%|asilimia\s+(\d+(?:[.,]\d+)?)", re.IGNORECASE)
_D31_COUNT = re.compile(r"(?<![\d.,])(\d{1,3})(?![\d%])(?![.,]\d)")   # "wafanyakazi 5," is a count; "1,500" and "3.5" are not (pricing: a trailing comma had hidden the headcount)
# RATES are only those PRESENT in the exchange (question + workings). A first draft added a broad locked-rate set and the founding specimen escaped: 150,000 = 0.25 x 600,000 (NSSF's employer half), a coincidence a wide rate set manufactures. STATUTORY CONSTANTS are a separate, derived set (the
# PAYE band edges, their +1 edges and base amounts, the presumptive ceilings), read from rates.py so they cannot drift: pricing found three stored replies and TWO GOLD answers flagged only for citing a band edge (270,000 / 270,001 / 760,001).
def _d31_constants():
    from .rules_engine import rates as _rates
    out = {int(_rates.PRESUMPTIVE_TURNOVER_CEILING), int(_rates.PRESUMPTIVE_NEW_BUSINESS_EXEMPT_UPPER)}
    for lower, _rate, base in _rates.PAYE_BANDS:
        for v in (int(lower), int(lower) + 1, int(base)):
            if v >= _FIG_FLOOR:
                out.add(v)
    return out


def _d31_rates(text: str):
    out = set()
    for m in _D31_RATE.finditer(text or ""):
        tok = (m.group(1) or m.group(2) or "").replace(",", ".")
        try:
            out.add(round(float(tok) / 100.0, 6))
        except ValueError:
            pass
    return out


def _d31_supported(amount: int, known, rates, counts) -> bool:
    if amount in known:
        return True
    base = sorted(known)[:40]
    cand = set()
    for x in base:
        for r in rates:
            cand.add(round(x * r))
        for n in counts:
            cand.add(round(x * n))
            if n:
                cand.add(round(x / n))
        for y in base:
            cand.add(x + y)
            cand.add(abs(x - y))
            if x * y < 10 ** 13:
                cand.add(x * y)
            if y:
                cand.add(round(x / y))
    return any(abs(amount - c) <= 1 for c in cand)


def unproduced_figures(question: str, body: str, workings: str):
    """[(amount, sentence)] for money the body asserts that is in no supported set (see D-FIDELITY-31). `workings` is EVERY engine working of the request, joined. Pure."""
    if not body or not workings:
        return []
    known = _figures(question) | _figures(workings) | _d31_constants()
    rates = _d31_rates((question or "") + " " + workings)
    counts = {int(m.group(1)) for m in _D31_COUNT.finditer(question or "") if 1 <= int(m.group(1)) <= 999}
    # A rate STATED IN THE SAME SENTENCE as the figure is part of the body's own derivation ("NSSF = 20% x TZS 4,800,000 = TZS 960,000"): priced on eval_324. A WRONG rate is D-FIDELITY-6's job; a figure with no rate and no derivation (the founding specimen) is not helped by this.
    return [(amount, sentence) for amount, sentence in _asserted_figures(body) if not _d31_supported(amount, known, rates | _d31_rates(sentence), counts)]


def body_states_unproduced_figure(question: str, body: str, workings: str) -> bool:
    return bool(unproduced_figures(question, body, workings))


def body_states_unsupported_figure(question: str, body: str, working: str) -> bool:
    """True iff the body asserts a money figure nothing in the exchange can support."""
    return bool(unsupported_body_figures(question, body, working))


# ─── D-FIDELITY-10 — A FIXED STATUTORY FIGURE CONTRADICTED ON THE MODEL PATH ─────────────────────
# Built 2026-11-16, from the five live answers of the 2026-11-13 coverage deploy, each wrong with the CORRECT fact at RANK 1:
#
#     notice         "Kwa mfanyakazi wa kila mwezi, notisi ni siku 4."            (monthly-paid: 28; 4 is the daily/weekly limb)
#     severance      "...mshahara wake wa mwisho + asilimia 25% ya mshahara..."   (7 days' basic wage per completed year)
#     overtime       "Kiwango cha chini cha overtime ni asilimia 25% ..."          (not less than 1.5 times basic wage)
#     annual leave   "Ndiyo, unatakiwa kulipa mshahara kamili wakati wa likizo."   (a non-answer: the figure is at least 28 days)
#     VAT credit     "...unaweza kuomba kulipa VAT kidogo kidogo..."               (earliest of invoice / payment / supply)
#
# R19 SAYS BUILDABLE, by the prescribed test: write the claim the guard would reject ("monthly notice is 4 days", "severance carries a
# percentage", "overtime is 25%") and ask whether a lawful transformation of the user's own numbers could make it true. None can: these are
# lookups against fixed statutory constants, and the question supplies at most the LIMB (pay period), never a figure to derive from. The same
# side of R19 as D-FIDELITY-7/8, and like them it needs no ComputationResult, so it reaches the FACT path.
#
# THE TOPIC COMES FROM THE QUESTION (D-FIDELITY-8's N2, provenance). Severance's live body never says "severance" ("Mfanyakazi aliyetimiza
# miezi 12+ anapata..."); only the question does. A question about ONE topic scans the whole body; a question about SEVERAL scans only the
# sentences that name the subject, so a correct overtime sentence is never judged by the severance rule.
#
# SIX RULES, one per failure shape, and each is a COMPARISON AGAINST A CONSTANT:
#   notice/limb     the question states the pay period and the body states a notice length for a DIFFERENT limb and never the right one
#   notice/value    a stated notice length that is no limb of the table and is under 28 (longer may be a contractual extension)
#   severance       a percentage; a 'siku N' per year with N != 7; a ceiling in years that is not 10; 'months of pay per year'
#   overtime        a percentage that is not >=150 (or >=50 with a premium word); a multiplier under 1.5
#   annual leave    a stated 'siku N' under 28 for leave of this kind; and (omission) asked how many days, the body never states 28
#   vat/time        'only when paid' / instalments / a due date other than the 20th, for a credit-sale VAT question
#
# REPLACEMENT, NOT BLANKING -- the fact path returns the body alone, so blanking ships silence. The replacement is the SAME whole statement
# the model-free route (`rules_engine.fixed_statements`) gives: all limbs, no limb selected, no amount computed. It is therefore safe by the
# argument D-FIDELITY-8's table copy makes: it performs no selection, so it cannot reproduce a wrong-limb error. UNLIKE D-FIDELITY-7 this one
# DOES hand the user the right answer, not only a withheld one -- so it moves A2 on these five topics as well as A1. It is still a reply a model
# path produced (model_calls > 0, guard 'replaced'), so it is never auto-send eligible and always reaches a reviewer.
#
# FAILS TOWARD SILENCE: each rule is word-bounded, a figure under a negation ('si 25%') is a MENTION, a sentence naming another levy is skipped
# (an NSSF "asilimia 10" in an overtime answer is not an overtime rate), and a rule with no clear subject does not fire.
_FD10_NEG = re.compile(r"(?<![a-z])(?:si|sio|siyo|not|never|badala\s+ya|tofauti\s+na|sivyo)\s*$", re.IGNORECASE)
_FD10_OTHER_LEVY = re.compile(r"(?<![a-z])(?:nssf|paye|sdl|wcf|zuio|kodi\s+ya\s+mapato|makadirio)", re.IGNORECASE)
_FD10_PERCENT = re.compile(r"(\d+(?:[.,]\d+)?)\s*%|asilimia\s+(\d+(?:[.,]\d+)?)", re.IGNORECASE)
_FD10_SIKU = re.compile(r"siku\s+(\d+)|(\d+)\s*(?:days?|siku)", re.IGNORECASE)
_FD10_PREMIUM = re.compile(r"zaidi|ziada|juu\s+ya|nyongeza|extra|premium|additional", re.IGNORECASE)
_FD10_TIMES = re.compile(r"mara\s+(\d+(?:[.,]\d+)?)|(\d+(?:[.,]\d+)?)\s*(?:x|×|times)(?![a-z])", re.IGNORECASE)
_FD10_MONTHLY = re.compile(r"kila\s+mwezi|wa\s+mwezi|mshahara\s+wa\s+mwezi|monthly", re.IGNORECASE)
_FD10_SHORT = re.compile(r"kila\s+wiki|wa\s+wiki|kila\s+siku|wa\s+siku|daily|weekly", re.IGNORECASE)
_FD10_FIRST_MONTH = re.compile(r"mwezi\s+wa\s+kwanza|first\s+month|miezi\s+ya\s+kwanza", re.IGNORECASE)
_FD10_OTHER_LEAVE = re.compile(r"uzazi|ugonjwa|baba|paternity|maternity|sick|msiba|compassionate|mafunzo|bila\s+malipo|unpaid",
                               re.IGNORECASE)
_FD10_ASK_COUNT = re.compile(r"ngapi|shingapi|how\s+many|muda\s+gani", re.IGNORECASE)
_FD10_VAT_ONLY_WHEN_PAID = re.compile(
    r"baada\s+ya\s+(?:kupokea\s+malipo|mteja\s+kulipa|malipo\s+kupokelewa)|mteja\s+akilipa|malipo\s+yakipokelewa|"
    r"pale\s+mteja\s+atakapolipa|only\s+(?:when|after)\s+(?:you\s+are\s+|the\s+customer\s+)?paid", re.IGNORECASE)
_FD10_VAT_INSTALMENT = re.compile(r"kidogo\s+kidogo|kwa\s+awamu|instal+ments?|awamu", re.IGNORECASE)
_FD10_VAT_EARLIEST = re.compile(r"mapema|earliest|invoice|ankara|usambazaji|supply", re.IGNORECASE)
_FD10_DATE = re.compile(r"tarehe\s+(\d+)", re.IGNORECASE)
_FD10_SUBJECT_WORDS = {
    "notice": re.compile(r"(?<![a-z])(?:notisi|notice)(?![a-z])", re.IGNORECASE),
    "severance": re.compile(r"severance|malipo\s+ya\s+kuachishwa", re.IGNORECASE),
    "overtime": re.compile(r"overtime|(?:saa|masaa)\s+(?:za|ya)\s+(?:ziada|nyongeza)", re.IGNORECASE),
    "annual_leave": re.compile(r"likizo|annual\s+leave", re.IGNORECASE),
    "vat_time_of_supply": re.compile(r"(?<![a-z])vat(?![a-z])", re.IGNORECASE),
}


def _fd10_num(s):
    return float(s.replace(",", "."))


def _fd10_negated(sentence, pos):
    return bool(_FD10_NEG.search(sentence[max(0, pos - 24):pos]))


def _fd10_scope(topic, question_topics, body):
    """The sentences of `body` the rule for `topic` may judge. One question topic -> the whole body; several -> only sentences naming the subject."""
    sentences = [s for s in _SENTENCE_SPLIT.split(body) if s and s.strip()]
    sentences = [s for s in sentences if not _FD10_OTHER_LEVY.search(s)]
    if len(question_topics) == 1:
        return sentences
    return [s for s in sentences if _FD10_SUBJECT_WORDS[topic].search(s)]


def _fd10_notice(question, scope):
    ql = question.lower()
    monthly, short, first = (bool(_FD10_MONTHLY.search(ql)), bool(_FD10_SHORT.search(ql)), bool(_FD10_FIRST_MONTH.search(ql)))
    expected = None
    if sum((monthly, short, first)) == 1:
        expected = 28 if monthly else (4 if short else 7)
    stated = []
    for s in scope:
        for m in _FD10_SIKU.finditer(s):
            if _fd10_negated(s, m.start()):
                continue
            stated.append(int(m.group(1) or m.group(2)))
    out = []
    for n in stated:
        if n not in (4, 7, 28) and n < 28:
            out.append(f"notice/value:{n}")
    if expected is not None and stated and expected not in stated and any(n in (4, 7, 28) for n in stated):
        out.append(f"notice/limb:expected {expected}, stated {sorted(set(stated))}")
    return out


_FD10_MONTHS = re.compile(r"(?:miezi|months)\s+(\d+)|(\d+)\s+(?:miezi|months)", re.IGNORECASE)
_FD10_QUALIFY = re.compile(r"angalau|at\s+least|kiwango\s+cha\s+chini|minimum|utumishi|huduma|kufanya\s+kazi|kufanyakazi|mfululizo|anastahili|hastahili|eligible|service|continuous", re.IGNORECASE)


def _fd10_severance(scope, question=""):
    out = []
    for s in scope:
        # 2026-11-16 (np_05 live: "angalau miezi 10 ... anastahili malipo ya kuachishwa kazi"): the qualifying service is 12 months. A months figure that is not 12, in a sentence about qualifying service, is
        # invented; one the QUESTION supplied (the asker's own "miezi 8") is a mention. Notice sentences and the per-year months rule below are not judged here.
        if _FD10_QUALIFY.search(s) and not re.search(r"notisi|notice|kwa\s+kila\s+mwaka|per\s+year", s, re.IGNORECASE):
            for m in _FD10_MONTHS.finditer(s):
                k = int(m.group(1) or m.group(2))
                if k != 12 and not _fd10_negated(s, m.start()) and not re.search(rf"(?<!\d){k}(?!\d)", question):
                    out.append(f"severance/qualifying-months:{k}")
        for m in _FD10_PERCENT.finditer(s):
            if not _fd10_negated(s, m.start()):
                out.append(f"severance/percent:{m.group(0).strip()}")
        for m in _FD10_SIKU.finditer(s):
            n = int(m.group(1) or m.group(2))
            if n != 7 and re.search(r"kila\s+mwaka|kwa\s+mwaka|per\s+year|each\s+year", s, re.IGNORECASE) \
                    and not _fd10_negated(s, m.start()):
                out.append(f"severance/days-per-year:{n}")
            elif n not in (4, 7, 28) and not _fd10_negated(s, m.start()):
                # live 2026-11-16: "yanatakiwa kulipwa ndani ya siku 30 baada ya kumaliza huduma" -- a payment deadline the fact does
                # not contain. 4/7/28 are the notice-table limbs and 7 is the severance figure; any other day count is invented.
                out.append(f"severance/days:{n}")
        for m in re.finditer(r"(?:hadi|isizidi|kikomo|max(?:imum)?|up\s+to)\s+(?:cha\s+)?(?:miaka\s+)?(\d+)\s*(?:miaka|years)?", s, re.IGNORECASE):
            if int(m.group(1)) != 10 and re.search(r"miaka|years", m.group(0), re.IGNORECASE) \
                    and not _fd10_negated(s, m.start()):
                out.append(f"severance/ceiling:{m.group(1)}")
        if re.search(r"(?:\d+|mmoja|miwili|mitatu)\s+(?:mwezi|miezi)\s+(?:wa\s+mshahara\s+)?kwa\s+kila\s+mwaka", s, re.IGNORECASE):
            out.append("severance/months-per-year")
    return out


def _fd10_overtime(scope):
    out = []
    for s in scope:
        premium = bool(_FD10_PREMIUM.search(s))
        for m in _FD10_PERCENT.finditer(s):
            p = _fd10_num(m.group(1) or m.group(2))
            lawful = p >= (50 if premium else 150)
            if not lawful and not _fd10_negated(s, m.start()):
                out.append(f"overtime/percent:{m.group(0).strip()}")
        for m in _FD10_TIMES.finditer(s):
            x = _fd10_num(m.group(1) or m.group(2))
            if x < 1.5 and not _fd10_negated(s, m.start()):
                out.append(f"overtime/multiplier:{m.group(0).strip()}")
    return out


def _fd10_annual_leave(question, scope, whole=()):
    out, stated_28 = [], False
    for s in list(scope) + [w for w in whole if w not in scope]:
        if _FD10_OTHER_LEAVE.search(s):
            continue
        for m in _FD10_SIKU.finditer(s):
            n = int(m.group(1) or m.group(2))
            if n >= 28:
                stated_28 = stated_28 or n == 28
                # 2026-11-16 (np_12 live: "Likizo ya mwaka ... ni siku 30"): the rule used to stop at "under 28" on the reasoning that more may be a contractual extension. A figure strictly between 28 and
                # 61 stated for annual leave is not that: the Act's figure is 28 consecutive days and nothing in the locked facts or the corpora states a 29-60 day annual leave. A figure the QUESTION supplied
                # is a mention (a reply denying the asker's "siku 30" must pass); 61+ stays unjudged (maternity/other leave counts).
                if 28 < n < 61 and re.search(r"likizo|leave", s, re.IGNORECASE) and not _fd10_negated(s, m.start()) \
                        and not re.search(rf"(?<!\d){n}(?!\d)", question):
                    out.append(f"annual_leave/value:{n}")
            elif re.search(r"likizo|leave", s, re.IGNORECASE) and not _fd10_negated(s, m.start()):
                out.append(f"annual_leave/value:{n}")
        if re.search(r"wiki\s+(?:4|nne)(?![\d])|(?<!\d)28(?!\d)", s):
            stated_28 = True
    if not out and not stated_28 and _FD10_ASK_COUNT.search(question) and not _FD10_OTHER_LEAVE.search(question):
        out.append("annual_leave/omission:28 not stated")
    return out


def _fd10_vat(scope):
    out = []
    for s in scope:
        if any(not _fd10_negated(s, m.start()) for m in _FD10_VAT_INSTALMENT.finditer(s)):
            out.append("vat/instalments")
        if any(not _fd10_negated(s, m.start()) for m in _FD10_VAT_ONLY_WHEN_PAID.finditer(s))                 and not _FD10_VAT_EARLIEST.search(s):
            out.append("vat/only-when-paid")
        for m in _FD10_DATE.finditer(s):
            if int(m.group(1)) != 20 and re.search(r"(?<![a-z])vat(?![a-z])", s, re.IGNORECASE) and not _fd10_negated(s, m.start()):
                out.append(f"vat/date:{m.group(1)}")
    return out


# ---- D-FIDELITY-10 EXTENSION (2026-11-16, founder): three more fixed statements, each founded on a LIVE wrong reply with the correct row at rank 1 -------------------------
#   voluntary VAT registration  the Act names no voluntary route and TRA's FAQ names no activities, so ANY substantive answer that does not carry the hedge is unsupported:
#                               live "Ndiyo, kwa mujibu wa sheria, unaweza kujisajili VAT kwa hiari hata ukiwa chini ya kiwango" and the garbled "lazima uwe umefikia kiwango ... ili
#                               usajiliwe kwa hiari". The rule is the ABSENCE of the hedge, which the statement itself always carries -- so a flag costs nothing: the replacement is the right answer.
#   WCF accident reporting      the employer's clock runs from RECEIPT of the employee's notice (Cap.263 R.E.2023 s.34(1); GN 185/2016 Reg.15(4)); live "inaanza kuhesabiwa tangu siku ya
#                               ajali au siku ambayo mwajiri alipata habari". A sentence tying the period to the accident date is flagged UNLESS it is about the employee (the employee's own 2-working-day
#                               and direct 7-working-day legs genuinely run from the accident, Reg.15(1),(2)) or negates it ("si tangu tarehe ya ajali" is the statement's own wording).
#   VAT withholding, mixed      the VALUE subject to withholding is apportioned 3:2 goods:services (FA2026 s.91(b) -> VAT Act s.5(7)); live "kiwango kinagawanywa 3:2" apportions the RATE. A sentence
#                               with 3:2 and a rate subject and no mention of the value is flagged, as is a rate applied to "thamani yote".
# These topics are ABOUT a levy by name (WCF, "zuio"), so the "another levy is named" early return does not apply to them (each has its own veto in routing._FS_TOPICS).
_FD10_LEVY_EXEMPT = frozenset({"wcf_accident_reporting", "vat_withholding_mixed_supply", "wcf_disease_reporting", "nssf_split", "paye_band_table"})
_FD10_VOL_HEDGE = re.compile(
    r"hayataji|haitaji|hazitaji|haijatajwa|hakuna\s+njia|si\s+wazi|siyo\s+wazi|haiko\s+wazi|bila\s+(?:kuzitaja|kutaja)|anayetarajia|intending|Kamishna\s+ndiye|njia\s+zilizotajwa",
    re.IGNORECASE)
_FD10_ACCIDENT_TRIGGER = re.compile(
    r"(?<![a-z])(?:tangu|kutoka|toka|baada\s+ya)\s+(?:siku|tarehe)\s+ya\s+ajali|tangu\s+ajali\s+(?:itokee|ilipotokea|kutokea)|baada\s+ya\s+ajali\s+kutokea|"
    r"siku\s+(?:7|saba)(?:\s*\(7\))?(?:\s+za\s+kazi)?\s+(?:tangu|baada\s+ya|toka)\s+(?:tarehe\s+ya\s+|siku\s+ya\s+)?ajali|"
    r"(?:from|since|after)\s+the\s+(?:date|day)\s+of\s+the\s+accident", re.IGNORECASE)
_FD10_EMPLOYEE_LEG = re.compile(r"mfanyakazi|employee", re.IGNORECASE)
_FD10_RATIO_32 = re.compile(r"3\s*:\s*2")
_FD10_RATE_SUBJECT = re.compile(r"kiwango|asilimia|\brate\b", re.IGNORECASE)
_FD10_VALUE_WORD = re.compile(r"thamani|value|consideration|bei\s+ya", re.IGNORECASE)
_FD10_WHOLE_VALUE = re.compile(r"thamani\s+yote|full\s+value|whole\s+value|jumla\s+ya\s+thamani|kiasi\s+chote", re.IGNORECASE)


def _fd10_voluntary(body):
    if _FD10_VOL_HEDGE.search(body):
        return []
    return ["voluntary VAT registration answered without the hedge: the Act names no voluntary route and TRA names no activities, so a categorical answer is unsupported"]


def _fd10_wcf_accident(body):
    out = []
    for sent in [x for x in _SENTENCE_SPLIT.split(body) if x and x.strip()]:
        for m in _FD10_ACCIDENT_TRIGGER.finditer(sent):
            if _fd10_negated(sent, m.start()) or _FD10_EMPLOYEE_LEG.search(sent):
                continue
            out.append("the employer's reporting period is tied to the date of the accident; it runs from RECEIPT of the employee's notice")
            break
    return out


def _fd10_vat_mixed(body):
    out = []
    for sent in [x for x in _SENTENCE_SPLIT.split(body) if x and x.strip()]:
        if _FD10_RATIO_32.search(sent) and _FD10_RATE_SUBJECT.search(sent) and not _FD10_VALUE_WORD.search(sent):
            out.append("3:2 is applied to the RATE; the Act apportions the VALUE subject to withholding")
        for m in _FD10_WHOLE_VALUE.finditer(sent):
            if not _fd10_negated(sent, m.start()) and re.search(r"\d\s*%|asilimia", sent, re.IGNORECASE):
                out.append("a single withholding rate applied to the whole value of a mixed supply")
                break
    return out



def _fd10_wcf_disease(body):
    """2026-11-16 (eval_239): occupational-disease reporting is a TWO-stage chain (employee -> employer 14 working days; employer -> WCF 7 working days from RECEIPT). A body that names a day count for disease
    reporting and does not carry BOTH stages collapses it ("siku 14 za kazi tangu kugunduliwa" as the whole deadline). A body naming no day count is not judged."""
    if not (re.search(r"ugonjwa|magonjwa|disease", body, re.IGNORECASE) and re.search(r"wcf", body, re.IGNORECASE)):
        return []
    if not re.search(r"siku\s+(?:7|14|21)|(?:7|14|21)\s+(?:working\s+)?days|siku\s+saba", body, re.IGNORECASE):
        return []
    if re.search(r"\b14\b", body) and re.search(r"\b7\b|saba", body):
        return []
    return ["occupational-disease reporting is a two-stage chain (employee to employer 14 working days, then employer to WCF 7 working days from receipt), not one deadline"]


_FD10_SPLIT_DENIAL = re.compile(r"hakuna\s+mgawanyo\s+mwingine|mgawanyo\s+mmoja\s+tu|mgawanyo\s+huo\s+pekee|10\s*%?\s*kwa\s*10\s*(?:tu|pekee)|hakuna\s+migawanyo\s+mingine", re.IGNORECASE)


def _fd10_nssf_split(body):
    """2026-11-16 (eval_348): the Act lets the employer opt to contribute more than its 10% share (15+5, 20+0 are examples) and enumerates no list of permitted splits. A body that says no other split exists is wrong."""
    if re.search(r"\b15\b|20\s*%?\s*\+\s*0|anaweza\s+kuchagua|kikubwa\s+zaidi", body, re.IGNORECASE):
        return []
    for m in _FD10_SPLIT_DENIAL.finditer(body):
        sent = next((x for x in _SENTENCE_SPLIT.split(body) if m.group(0) in x), body)
        if not _fd10_negated(sent, sent.lower().find(m.group(0).lower())):
            return ["the body says the 10/10 NSSF split is the only one; the employer may opt to contribute a greater share (15+5, 20+0) and the Act lists no exhaustive set"]
    return []


def fixed_figure_violations(question: str, body: str):
    """[(topic, reason)] for every fixed statutory figure the body contradicts. Empty when the question is not about a fixed-statement topic."""
    if not body or not question:
        return []
    from .routing import fixed_statement_topics
    topics = fixed_statement_topics(question)
    levy_named = bool(_FD10_OTHER_LEVY.search(question))   # another levy is named: a different question (priced: an NSSF-on-overtime answer was flagged on its "10%")
    out = []
    for topic in topics:
        if levy_named and topic not in _FD10_LEVY_EXEMPT:
            continue
        if topic == "vat_voluntary_registration":
            out += [(topic, r) for r in _fd10_voluntary(body)]
            continue
        if topic == "wcf_accident_reporting":
            out += [(topic, r) for r in _fd10_wcf_accident(body)]
            continue
        if topic == "vat_withholding_mixed_supply":
            out += [(topic, r) for r in _fd10_vat_mixed(body)]
            continue
        if topic == "wcf_disease_reporting":
            out += [(topic, r) for r in _fd10_wcf_disease(body)]
            continue
        if topic == "nssf_split":
            out += [(topic, r) for r in _fd10_nssf_split(body)]
            continue
        if topic in ("future_year_rate", "sector_minimum_wage", "sdl_exemptions", "sdl_payer", "sdl_employee_premise", "sdl_how_to_file_pay", "sdl_nssf_party",
                     "sdl_nssf_paye_party", "nssf_party", "brela_three_forms", "brela_fee_no_share_capital", "gn487a_penalties", "vat_withholding_rates", "vat_professional_services", "brela_late_annual_return", "sdl_paye_deadline", "sdl_audit_hedge", "vat_medicines", "paye_base", "paye_rate", "vat_health_and_medicines", "wcf_base", "paye_residency", "director_fees_wht", "sdl_base", "levy_rates_three", "levy_deadlines_three", "vat_medical_services"):
            continue                # a model-free statement route with no figure-scope rule (the model answers this question only when the route is missed); without this the loop falls to the VAT scope rule below
        if topic == "brela_annual_return_deadline":
            continue                # guarded by D-FIDELITY-20 (body_contradicts_d16); this route is model-free, and no figure-scope rule applies here
        if topic == "paye_band_table":
            continue                # no ordinal guard by decision (tests/test_fixed_statements.py PAYE_NO_GUARD); D-FIDELITY-11 guards band edges on the compute path
        scope = _fd10_scope(topic, topics, body)
        if not scope and topic != "annual_leave":
            continue                # annual leave's OMISSION rule must still run on a body that never mentions leave at all
        if topic == "notice":
            reasons = _fd10_notice(question, scope)
        elif topic == "severance":
            reasons = _fd10_severance(scope, question)
        elif topic == "overtime":
            reasons = _fd10_overtime(scope)
        elif topic == "annual_leave":
            reasons = _fd10_annual_leave(question, scope, [x for x in _SENTENCE_SPLIT.split(body) if x and x.strip()
                                                           and not _FD10_OTHER_LEVY.search(x)])
        else:
            reasons = _fd10_vat(scope)
        out += [(topic, r) for r in reasons]
    return out


def body_contradicts_fixed_figure(question: str, body: str) -> bool:
    """True iff the body contradicts a fixed statutory figure for a topic the QUESTION is about."""
    return bool(fixed_figure_violations(question, body))

# ---- D-FIDELITY-11 (2026-11-16, founder): THE PAYE BAND NARRATION. A compute reply is a model-written body with the engine's working appended; the working was right and the narration
# around it said "TZS 760,000 ni kiwango cha pili cha PAYE (8%)". 760,000 is the TOP of the 20% band (TZS 520,001-760,000), and the BASE of the 25% band's excess. A CONSTANT comparison
# (R19: the band edges are statute, no transformation of the user's numbers can make "760,000 is in the 8% band" true), so it needs no engine result and judges any body.
# An edge figure may be named as the END of band k or the START of band k+1; anything else is a misnaming. Only the strict "TZS <edge> ... kiwango cha <ordinal> | (<rate>%)" form is read:
# a figure followed by "juu ya", "zaidi ya", or an excess is not an assignment to a band.
_PAYE_EDGE_BAND = {270000: 1, 520000: 2, 760000: 3, 1000000: 4}
_PAYE_ORDINAL = {"kwanza": 1, "pili": 2, "tatu": 3, "nne": 4, "tano": 5}
_PAYE_RATE_BAND = {0: 1, 8: 2, 20: 3, 25: 4, 30: 5}
_PAYE_CLAIM = re.compile(
    r"TZS\s*(270,000|520,000|760,000|1,000,000)(?![\d,])[^.;\n]{0,50}?(?:(?:kiwango|band|bendi|daraja)\s+cha\s+(kwanza|pili|tatu|nne|tano)|\((\d+)\s*%\))", re.IGNORECASE)


def paye_band_misnamings(body):
    """[(edge, claimed_band)] where the body assigns a PAYE band edge to a band it is neither the end of nor the start of."""
    out = []
    for m in _PAYE_CLAIM.finditer(body or ""):
        edge = int(m.group(1).replace(",", ""))
        claimed = _PAYE_ORDINAL.get((m.group(2) or "").lower()) or _PAYE_RATE_BAND.get(int(m.group(3))) if (m.group(2) or m.group(3)) else None
        if claimed is None:
            continue
        end = _PAYE_EDGE_BAND[edge]
        if claimed not in (end, end + 1):
            out.append((edge, claimed))
    return out


def body_misnames_paye_band(body: str) -> bool:
    return bool(paye_band_misnamings(body))


# ---- D-FIDELITY-12 (2026-11-16, founder): A TURNOVER ABOVE THE VAT THRESHOLD IS TOLD IT NEED NOT REGISTER. The founding specimen is eval_318's VAT limb: "Mapato ya TZS 205,000,000 hayazidi kizingiti
# hicho, hivyo huhitajiwi kusajili VAT" -- 205M > 200M. ``stated_wrong_thresholds``' own docstring says this exact reply is OUT of its scope ("wrong about a COMPARISON ... Guard B territory"), and that
# was right about THAT guard. What makes this one buildable (R19's test, applied honestly): the claim compared is the user's ONE figure against a CONSTANT, and the verdict has a single lawful
# value. "TZS 205,000,000 does not reach TZS 200,000,000" is not true under ANY transformation of the user's own number -- there is no halving, annualising or netting that makes 205M smaller than
# 200M -- unless the figure is a different PERIOD (a 24-month total) or a BOUND ("bado hayajafika 205M"), both of which are excluded from the trigger rather than argued about afterwards.
# NARROW BY CONSTRUCTION (R17): exactly ONE money figure in the question, STRICTLY above 200,000,000 (either limb is then met for any period up to 12 months), no foreign currency, no bound/period
# vocabulary, and the question must be about VAT registration. The body must DENY an obligation (a registration-specific denial or "hayazidi kizingiti") in a sentence that is NOT conditional, and must
# not also AFFIRM one -- a body that states both errs toward silence, the only direction a guard that replaces text may err in (D-FIDELITY-7's N3, same trade, same stated cost).
# Replaced, not blanked, on the FACT path: _render returns the body alone there, so blanking ships silence.
_VAT_REG_ASK = re.compile(r"sajili|jisajili|usajili|usajilishaji|register|jiandikish|andikish|ni\s+lazima|lazima\s+(?:ni|tu)", re.IGNORECASE)
_VAT_NOT_A_TURNOVER = re.compile(
    r"hayajafika|haijafika|hajafika|hatujafika|sijafikia|hatujafikia|\bbado\b|chini\s+ya|isiyozidi|yasiyozidi|kabla\s+ya|ukiwa|\bmiaka\b|miezi\s+(?:1[3-9]|[2-9]\d)\b|\byears?\b|\bsivyo\b|"
    # a trader whose supplies are all EXEMPT genuinely need not register, so exemption vocabulary vetoes the trigger rather than letting the guard contradict a correct answer.
    r"sameh|msamaha|exempt", re.IGNORECASE)
_VAT_FOREIGN = re.compile(r"shilingi\s+za\s+kenya|kenyan?\s+shilling|\bkes\b|\bugx\b|\busd\b|dola|dollar|\beur\b|euro|\bgbp\b|paundi|\brand\b", re.IGNORECASE)
_VAT_DENIAL = re.compile(
    r"huhitajiwi\s+(?:kusajili|kujisajili|kujiandikisha|usajili)|hutahitaji\s+(?:kusajili|kujisajili)|hauhitajiki|haulazimiki|"
    r"huna\s+(?:haja|lazima|wajibu)\s+(?:ya\s+)?(?:kusajili|kujisajili|usajili|kujiandikisha)|"
    r"(?:si|sio)\s+lazima\s+(?:kusajili|kujisajili|usajili|ujisajili|usajiliwe|ujiandikishe)|hakuna\s+ulazima|"
    r"hayazidi\s+kizingiti|haijazidi\s+kizingiti|hayajazidi\s+kizingiti|haujazidi\s+kizingiti|hujazidi\s+kizingiti|"
    r"hayajafika\s+kizingiti|haujafika\s+kizingiti|hujafika\s+kizingiti|haijafika\s+kizingiti|"
    r"(?:do\s+not|don't|need\s+not|not\s+required\s+to)\s+(?:need\s+to\s+)?register", re.IGNORECASE)
_VAT_AFFIRM = re.compile(
    r"(?<!si )(?<!sio )lazima\s+(?:ujisajili|usajili|usajiliwe|ujiandikishe|kusajili|kujisajili)|unatakiwa\s+(?:kusajili|kujisajili|kujiandikisha|ujisajili)|inakulazimu|"
    r"(?:umezidi|yamezidi|umevuka|yamevuka|umefika|yamefika)\s+kizingiti|must\s+register", re.IGNORECASE)
_VAT_CONDITIONAL = re.compile(r"\b(?:ikiwa|kama|ukiwa|ukipata|ukifikia|usipofika|endapo|isipozidi|chini\s+ya)\b", re.IGNORECASE)
_VAT_REG_TOP_LIMB = 200_000_000


def vat_denial_above_threshold(question: str, body: str):
    """The question's single figure when the body denies a VAT registration obligation that figure triggers, else None."""
    if not question or not body:
        return None
    ql = question.lower()
    if not (_VAT_TOKEN.search(ql) and _VAT_REG_ASK.search(ql)) or _VAT_NOT_A_TURNOVER.search(ql) or _VAT_FOREIGN.search(ql):
        return None
    from .swahili_numbers import parse_amounts
    figures = [int(a) for a in parse_amounts(question) if int(a) >= _THRESHOLD_MONEY_FLOOR]
    if len(figures) != 1 or figures[0] <= _VAT_REG_TOP_LIMB:
        return None
    if _VAT_AFFIRM.search(body) or not (_VAT_TOKEN.search(body) or re.search(r"kizingiti|usajili|sajili", body, re.IGNORECASE)):
        return None
    for sentence in _SENTENCE_SPLIT.split(body):
        if _VAT_DENIAL.search(sentence) and not _VAT_CONDITIONAL.search(sentence):
            return figures[0]
    return None


def body_denies_vat_registration_above_threshold(question: str, body: str) -> bool:
    return vat_denial_above_threshold(question, body) is not None


# ---- D-FIDELITY-13 (2026-11-16, founder, from the live np_ replies): THREE CONSTANTS THE MODEL CONTRADICTED ON THE FACT PATH WITH THE CORRECT ROW AT HAND, AND A DERIVED AMOUNT NOBODY COULD HAVE SUPPLIED.
#   licence    np_13  "leseni ya biashara inatakiwa kuwa updated kila mwaka ifikapo tarehe 31 Machi"   (every business licence expires 30 June)
#   records    np_20  "kuhifadhiwa kwa angalau miaka mitatu (3)"                                        (five years from the relevant date)
#   TIN        np_26  "Hakuna siku maalum za 15 za kuomba TIN"                                          (apply within 15 days of starting business)
#   WCF amount np_28  "Kwa wafanyakazi 6, hesabu hiyo itakuwa ni TZS 30,000 kwa mwezi"                  (no wage was given; th_22's shape, on the FACT path)
# R19: each of the first three is a lookup against a statutory CONSTANT -- no transformation of the user's numbers makes "licences expire 31 March" or "keep records three years" true -- so no engine result is
# needed and the guard reaches the fact path. The fourth is D-FIDELITY-9's loose form restricted to the fact path and to a sentence that DERIVES an amount (per month / per year / per employee / "hesabu"), for a
# question that names one payroll levy and supplies no figure: with no input there is no lawful transformation to reach it.
# A figure the QUESTION itself carries (the asker's "miaka mitatu", "siku 15") is a MENTION: a reply that corrects it must pass. Word numbers are read (Swahili writes "tatu" as often as "3").
_WORD_NUM = {"moja": 1, "mmoja": 1, "mbili": 2, "miwili": 2, "tatu": 3, "mitatu": 3, "nne": 4, "minne": 4, "tano": 5, "mitano": 5, "sita": 6, "saba": 7, "nane": 8, "tisa": 9, "kumi": 10}
_MONTH_NAMES = r"januari|februari|machi|aprili|mei|juni|julai|agosti|septemba|oktoba|novemba|desemba|january|february|march|april|june|july|august|september|october|november|december"
_C13_LICENCE_Q = re.compile(r"leseni\s+(?:ya|yangu|za)\s*(?:biashara|duka)?|business\s+licen[cs]e", re.IGNORECASE)
_C13_LICENCE_Q_NEED = re.compile(r"isha|huisha|ish[ae]|upya|hui?sh|renew|expir|dumu|muda|lini|tarehe|kila\s+mwaka|mwisho", re.IGNORECASE)
_C13_LICENCE_S = re.compile(r"leseni|licen[cs]e", re.IGNORECASE)
_C13_EXPIRY_S = re.compile(r"isha|huish|upya|renew|expir|ifikapo|kabla\s+ya|updated|mwisho|tarehe", re.IGNORECASE)
_C13_LIC_NEG = re.compile(r"(?<![a-z])(?:si|sio|siyo|not|never|badala\s+ya|tofauti\s+na|wala)\s+(?:tarehe\s+|siku\s+ya\s+|ya\s+)?$", re.IGNORECASE)   # "si tarehe 30 Juni", "wala 31 Machi"
_C13_DATE = re.compile(rf"(?<!\d)(\d{{1,2}})\s+({_MONTH_NAMES})\b|\b({_MONTH_NAMES})\s+(\d{{1,2}})(?!\d)", re.IGNORECASE)
_C13_RECORDS_Q = re.compile(r"kumbukumbu|rekodi|vitabu\s+vya|records|books\s+of\s+account", re.IGNORECASE)
_C13_RECORDS_Q_NEED = re.compile(r"hifadhi|hifadh|keep|retain|muda|miaka|tupa|kuhifadhi", re.IGNORECASE)
_C13_RECORDS_S = re.compile(r"hifadhi|hifadh|kumbukumbu|rekodi|vitabu|records|keep|retain", re.IGNORECASE)
_C13_YEARS = re.compile(r"miaka\s+(\d+|%s)\b|(\d+)\s*(?:miaka|years?)\b" % "|".join(_WORD_NUM), re.IGNORECASE)
_C13_TIN_Q = re.compile(r"(?<![a-z])tin(?![a-z])", re.IGNORECASE)
_C13_TIN_Q_NEED = re.compile(r"siku|muda|lini|deadline|kuomba|omba|apply|baada|ndani|kuanza|anza|biashara|haraka", re.IGNORECASE)
_C13_TIN_S = re.compile(r"(?<![a-z])tin(?![a-z])|kuomba|omba|apply|maombi", re.IGNORECASE)
_C13_TIN_ISSUE = re.compile(r"toa|hutoa|itatoa|kutolewa|itatolewa|issue|kupewa|kupatiwa", re.IGNORECASE)
_C13_TIN_DENY = re.compile(r"hakuna\s+(?:siku|muda|kikomo|mwisho|deadline|tarehe)(?:\s+(?:maalum|ya\s+mwisho))?", re.IGNORECASE)
# priced: "kwa mwezi/mwaka" alone, "=" and "jumla" also match thresholds and band tables ("zaidi ya TZS 270,000 kwa mwezi"); only a per-employee / headcount / "hesabu" derivation is the defect.
_C13_DERIVED = re.compile(r"kwa\s+(?:mfanyakazi|wafanyakazi)|wafanyakazi\s+\d|hesabu|itakuwa", re.IGNORECASE)
_C13_NOT_AMOUNT = re.compile(r"faini|adhabu|ada\b|kikomo|ceiling|kiwango\s+cha\s+juu|kima\s+cha\s+chini|mshahara\s+wa\s+chini|minimum\s+wage|threshold|kizingiti|riba|penalty|fine\b|mfano|example|ukomo|kiwango\s+cha\s+chini|gn\s*605a", re.IGNORECASE)
# The PAYE band edges and bases are statute, stated legitimately in answers to SDL/NSSF/WCF questions that also touch PAYE ("PAYE hukatwa kwa wafanyakazi wanaopata zaidi ya TZS 270,000"); priced as false positives.
_C13_STATUTORY_AMOUNTS = frozenset({270_000, 270_001, 520_000, 520_001, 760_000, 760_001, 1_000_000, 1_000_001, 20_000, 68_000, 128_000})
_C13_LEVY_Q = re.compile(r"(?<![a-z])(?:wcf|nssf|sdl|fidia)(?![a-z])", re.IGNORECASE)


def _c13_numbers(text):
    """{int} every plain count in `text`, digits and Swahili number words."""
    out = {int(x) for x in re.findall(r"(?<![\d,.])(\d{1,3})(?![\d,.])", text or "")}
    for w, n in _WORD_NUM.items():
        if re.search(rf"\b{w}\b", text or "", re.IGNORECASE):
            out.add(n)
    return out


def _c13_licence(question, body):
    if not (_C13_LICENCE_Q.search(question) and _C13_LICENCE_Q_NEED.search(question)):
        return []
    qn = _c13_numbers(question)
    out = []
    for s in _SENTENCE_SPLIT.split(body):
        if not (s and _C13_LICENCE_S.search(s) and _C13_EXPIRY_S.search(s)):
            continue
        for m in _C13_DATE.finditer(s):
            day = int(m.group(1) or m.group(4))
            month = (m.group(2) or m.group(3)).lower()
            if re.match(r"\s*,?\s*\d{4}", s[m.end():]):
                continue                 # a FULL date with a year ("GN 487A ya 28 Julai 2025") is a dated instrument, not a recurring licence expiry (priced: 3 training rows)
            # 2026-11-17 FLIPPED. The Business Licensing Act (Cap.101 R.E.2023 s.7(1)) makes a licence valid TWELVE MONTHS FROM ISSUANCE: NO fixed calendar date is right, and 30 June (the pre-2014 rule, Cap.208 R.E.2002 s.7)
            # is the stale one. The old exemption for (30, juni) is gone, and so is the old "a date the ASKER named is a mention" exemption: under the old constant a reply that
            # repeated the asker's 30 June was right; now it is the premise to deny (s2_07). A bare "Hapana," opener does NOT excuse a sentence that still asserts the date -- only a negation attached to the date does.
            if _fd10_negated(s, m.start()) or _C13_LIC_NEG.search(s[max(0, m.start() - 32):m.start()]):
                continue
            out.append(f"licence/expiry-date:{day} {month}")
    return out


def _c13_records(question, body):
    if not (_C13_RECORDS_Q.search(question) and _C13_RECORDS_Q_NEED.search(question)):
        return []
    qn = _c13_numbers(question)
    out = []
    for s in _SENTENCE_SPLIT.split(body):
        if not (s and _C13_RECORDS_S.search(s)):
            continue
        for m in _C13_YEARS.finditer(s):
            tok = (m.group(1) or m.group(2) or "").lower()
            n = int(tok) if tok.isdigit() else _WORD_NUM.get(tok)
            if n is None or n == 5 or n in qn or _fd10_negated(s, m.start()):
                continue
            out.append(f"records/years:{n}")
    return out


def _c13_tin(question, body):
    if not (_C13_TIN_Q.search(question) and _C13_TIN_Q_NEED.search(question)):
        return []
    qn = _c13_numbers(question)
    out = []
    for s in _SENTENCE_SPLIT.split(body):
        if not (s and _C13_TIN_S.search(s)):
            continue
        d = _C13_TIN_DENY.search(s)
        if d and not _fd10_negated(s, d.start()):
            out.append("tin/deadline-denied")
            continue
        if _C13_TIN_ISSUE.search(s):
            continue                     # "TRA can issue a TIN within 7 days" is the issuance limb, not the application deadline
        for m in _FD10_SIKU.finditer(s):
            n = int(m.group(1) or m.group(2))
            if n != 15 and n not in qn and not _fd10_negated(s, m.start()):
                out.append(f"tin/days:{n}")
    return out


def constant_violations(question: str, body: str):
    """[(topic, reason)] for a licence-expiry / record-keeping / TIN-deadline constant the body contradicts. Empty when the question is not about one."""
    if not body or not question:
        return []
    out = [("business_licence_expiry", r) for r in _c13_licence(question, body)]
    out += [("business_licence_expiry", r) for r in licence_validity_period_violations(question, body)]
    out += [("record_keeping_period", r) for r in _c13_records(question, body)]
    out += [("tin_apply_deadline", r) for r in _c13_tin(question, body)]
    return out


def body_contradicts_constant(question: str, body: str) -> bool:
    return bool(constant_violations(question, body))


_C13_ANY_MONEY = re.compile(r"\d{1,3}(?:[,.]\d{3})+|\d{4,}|(?<![a-z])(?:laki|elfu|milioni|bilioni|mia|shilingi|tsh|tzs)(?![a-z])|(?<![a-z])sh\.?\s*\d", re.IGNORECASE)


def _question_has_money(question):
    """ANY money notation in the question: digits with separators ("800,000"), plain 4+ digit numbers, and the Swahili words (laki, elfu, milioni ...). `_figures` alone misses "800,000"; a question that supplies a wage is the COMPUTE path's business, never this rule's."""
    return bool(_figures(question) or _C13_ANY_MONEY.search(question or ""))


def derived_levy_amount(question: str, body: str):
    """[(amount, sentence)] -- a shilling amount the FACT-PATH body DERIVES (per month / per year / per employee / "hesabu") for a question that names a payroll levy and supplies no figure at all. np_28, th_22."""
    if not body or not question or not _C13_LEVY_Q.search(question) or _question_has_money(question):
        return []
    # PRICED over 2,244 stored replies, 562 gold answers and 8,772 training pairs (eval/fidelity/price_np_guards_2026_11_16.py): the first form flagged PAYE band tables (statutory constants with '=' in them) and every
    # worked example that states its own base ("10% × TZS 700,000 = TZS 70,000"). The defect is an amount with NO base anywhere in the exchange, so (1) PAYE is out (banded: every body states fixed edges),
    # and (2) the amount must be the ONLY money figure in its sentence -- np_28 and th_22 each carry exactly one. An invented base AND result in one sentence is therefore not caught: the safe direction for a
    # guard that REPLACES text (precision over recall).
    return [(a, s) for a, s in _asserted_figures(body)
            if a not in _C13_STATUTORY_AMOUNTS and _C13_DERIVED.search(s) and not _C13_NOT_AMOUNT.search(s) and len(_figures(s)) == 1]


def body_states_derived_levy_amount(question: str, body: str) -> bool:
    return bool(derived_levy_amount(question, body))


# ---- D-FIDELITY-14 (2026-11-16, founder-approved): WRONG AUTHORITY. A reply that tells the asker to "Thibitisha na <authority>" and names the WRONG authority for the question's topic: np_19 (maternity leave -> immigration.go.tz),
# np_12 (annual leave -> osha.go.tz), an overtime answer -> mlywf.go.tz (a domain with NO DNS record), a GN 605A answer -> "Ofisi ya Kazi (wcf.go.tz)" or PKF Eastern Africa. REPAIRED, never withheld: the citation tail is a formulaic
# constant per topic, so replacing a wrong host with the topic's host changes one clause and cannot block a user.
#
# R25 -- THE TWO QUESTIONS, ANSWERED AT THE SITE (a content rewrite in the cleanup layer needs its justification in writing here):
#   1. What corpus/system defect does this repair?  Measured over 2,244 stored replies (eval/fidelity/measure_authority_by_topic_2026_11_16.py): 1,132 carry a citation on a single-topic question; 27 distinct pairs flagged by a
#      naive table, ~9 real (osha/immigration/mlywf/wcf/brela/PKF hosts on the wrong topic). The model learns the formulaic tail, not the authority, so the wrong host is emitted with the right fact at rank 1 (the
#      D-FIDELITY class: no index edit reaches it). One cause is in the corpus itself: 43 pairs were once sourced to mlywf.go.tz (CLAUDE.md Section 4).
#   2. What CORRECT output could it damage?  (a) a body citing TWO authorities (an NSSF-vs-SDL comparison legitimately cites nssf.go.tz AND tra.go.tz): the rule judges a body ONLY when it names exactly ONE distinct judged host;
#      (b) TanzLII (a whitelisted legal database) on an instrument question: never judged, never replaced; (c) an out-of-scope refusal naming a foreign regulator (kra.go.ke): foreign hosts are not judged, and a body
#      carrying a refusal phrase is skipped; (d) a question about SEVERAL topics: not judged (the topic is then ambiguous, as in the fixed-statement route). The probes in eval/fidelity/authority_repair_probes_2026_11_16.jsonl
#      hold each of these and the planted tests watch them stay clean.
# DUAL-FILE SYNC (CLAUDE.md): this lives in chike/, which production (chike-inference/modal_app.py) imports and which the Kaggle gate fetches from GitHub at runtime (kaggle/eval_gate_production_*.py runs the same
# Orchestrator); there is no second copy of the rule to keep in step. kaggle/eval.py itself runs none of the orchestrator guards and is unchanged.
_AUTH_TOPICS = (
    # name, question cue, allowed host suffixes, label, primary host
    ("labour", re.compile(r"likizo|notisi|(?<![a-z])notice(?![a-z])|severance|kuachishwa|overtime|mshahara\s+wa\s+chini|gn\s*605a|ajira|mkataba\s+wa\s+kazi|(?<![a-z])elra(?![a-z])|uzazi|paternity|maternity", re.IGNORECASE),
     ("kazi.go.tz",), "Ofisi ya Kazi", "kazi.go.tz"),
    ("nssf", re.compile(r"(?<![a-z])nssf(?![a-z])|pensheni|mfuko\s+wa\s+hifadhi|uzeeni|uzee(?![a-z])", re.IGNORECASE), ("nssf.go.tz", "kazi.go.tz"), "NSSF", "nssf.go.tz"),
    ("wcf", re.compile(r"(?<![a-z])wcf(?![a-z])|workers\s+compensation|ajali\s+kazini|fidia", re.IGNORECASE), ("wcf.go.tz",), "WCF", "wcf.go.tz"),
    ("osha", re.compile(r"(?<![a-z])osha(?![a-z])|usalama\s+kazini|afya\s+na\s+usalama", re.IGNORECASE), ("osha.go.tz", "kazi.go.tz"), "OSHA", "osha.go.tz"),
    ("brela", re.compile(r"(?<![a-z])brela(?![a-z])|usajili\s+wa\s+kampuni|jina\s+la\s+biashara|annual\s+return", re.IGNORECASE), ("brela.go.tz",), "BRELA", "brela.go.tz"),
    ("immigration", re.compile(r"gn\s*487a|non-?citizen|wageni|mgeni|foreigner|uhamiaji|(?<![a-z])visa(?![a-z])|kibali\s+cha\s+kazi", re.IGNORECASE), ("immigration.go.tz", "brela.go.tz", "tra.go.tz", "kazi.go.tz"), "Idara ya Uhamiaji", "immigration.go.tz"),
    ("tax", re.compile(r"(?<![a-z])(?:vat|paye|sdl|efd|tin|tra|withholding|zuio|risiti)(?![a-z])|kodi\s+ya|mafunzo|skills\s+development", re.IGNORECASE), ("tra.go.tz",), "TRA", "tra.go.tz"),
)
# Hosts judged: Tanzanian government hosts, plus practitioner firms whose pages are the EVAL family (R6) and are never a "Thibitisha na" authority.
_AUTH_HOST = re.compile(r"(?<![a-z0-9.-])((?:[a-z0-9-]+\.)*(?:go\.tz|pkfeastafrica\.com|pkfea\.com|velmalaw\.co\.tz|velmalaw\.com|bowmanslaw\.com|clydeco\.com))(?![a-z0-9-])", re.IGNORECASE)
_AUTH_REFUSAL = re.compile(r"samahani|sijui|siwezi\s+kusaidia|nje\s+ya\s+(?:uwezo|wigo)|masuala\s+ya\s+tanzania\s+bara\s+pekee|sina\s+uhakika", re.IGNORECASE)


# 2026-11-17: "Nikiachishwa kazi nitakatwa kodi gani kwenye malipo ya severance?" has a LABOUR cue (severance) and NO tax cue ("kodi gani" does not match `kodi ya`), so it was judged single-topic labour and a correct
# "Thibitisha na TRA" was rewritten to "Ofisi ya Kazi (kazi.go.tz)". A TAX-ASK ("kodi gani / ngapi", "inakatwa / inatozwa kodi", PAYE, zuio ...) on a question whose only other topic is labour makes TAX the topic. The mirror
# question ("severance ni siku ngapi?") has no tax-ask and stays labour. A third topic present (NSSF, WCF ...) still leaves the question unjudged.
_AUTH_TAX_ASK = re.compile(r"kodi\s+(?:gani|ngapi|kiasi)|(?:kukatwa|kukatwaje|inakatwa|hukatwa|inatozwa|hutozwa|inapigwa|hupigwa|itakatwa|nitakatwa|nitatozwa)\s+kodi|kodi\s+inayo(?:katwa|tozwa)|"
                           r"(?<![a-z])(?:paye|zuio|withholding|tax)(?![a-z])", re.IGNORECASE)


def authority_topic(question: str):
    """The ONE topic row the question is about, or None (no topic, or several: not judged). Tax wins over labour on a tax-ASK."""
    hits = [t for t in _AUTH_TOPICS if t[1].search(question or "")]
    names = {t[0] for t in hits}
    if "labour" in names and names <= {"labour", "tax"} and _AUTH_TAX_ASK.search(question or ""):
        return [t for t in _AUTH_TOPICS if t[0] == "tax"][0]
    return hits[0] if len(hits) == 1 else None


def repair_authority(question: str, body: str) -> str:
    """The body with a WRONG-authority host replaced by the topic's authority; the body unchanged when nothing is wrong or when the rule does not apply (see the R25 block above for every exclusion)."""
    if not question or not body or _AUTH_REFUSAL.search(body):
        return body
    topic = authority_topic(question)
    if topic is None:
        return body
    _, _, allowed, label, primary = topic
    hosts = {m.group(1).lower() for m in _AUTH_HOST.finditer(body)}
    if len(hosts) != 1:
        return body                                       # none cited, or a multi-authority answer: not judged
    host = next(iter(hosts))
    if any(host == a or host.endswith("." + a) for a in allowed):
        return body
    esc = re.escape(host)
    labelled = re.compile(r"(thibitisha\s+na\s+)([^().\n]{0,60}?)\(\s*(?:https?://)?(?:www\.)?" + esc + r"\s*\)", re.IGNORECASE)
    fixed, n = labelled.subn(lambda m: f"{m.group(1)}{label} ({primary})", body)
    if n:
        return fixed
    return re.sub(r"(?<![a-z0-9.-])" + esc + r"(?![a-z0-9-])", primary, body, flags=re.IGNORECASE)


# ---- D-FIDELITY-15 (2026-11-17, founder, from set #2): TWO MORE CONSTANTS, FACT PATH.
#   WCF deducted from wages   s2_04  "Ndiyo, hiyo 0.5% unapaswa kuikata kutoka kwa mishahara ya wafanyakazi wako ..."   (the employee does NOT contribute; deducting is a criminal offence: locked wcf_paid_to_fund_not_tra)
#   input VAT on a car        s2_17  "unaweza kudai input VAT ya manunuzi ya magari ... ikiwa umesajiliwa VAT"            (no input credit for a passenger vehicle unless the business deals in/hires/transports passengers)
# R19: each is a lookup against a statutory constant -- no transformation of the user's numbers makes "WCF is deducted from the employee" true -- so no engine result is needed and the guard reaches the fact path.
# OPENER-RIGHT IS NOT CONTENT-RIGHT: s2_04's opener (Ndiyo) was correct for the premise and its content was the offence; no opener metric can see it. NARROW BY CONSTRUCTION (R17): the WCF rule needs WCF named in the
# SENTENCE and an affirmative deduction verb on the wage, with every negation cue vetoing; the VAT rule needs a PASSENGER-car question (the locked fact says which other vehicles count is NOT stated, so pickups and
# lorries are never judged), an affirmative "you can claim" with no negation and no passenger-business exception.
_D15_WCF_SENT = re.compile(r"(?<![a-z])(?:wcf|fidia\s+ya\s+wafanyakazi|mfuko\s+wa\s+fidia)(?![a-z])|0\.5\s*%", re.IGNORECASE)
_D15_DEDUCT = re.compile(r"(?<![a-z])(?:kuikata|kuzikata|ukate|ukatie|inakatwa|hukatwa|ikatwe|inatakiwa\s+kukatwa|unakata|nakata|mnakata|kukata)(?![a-z])", re.IGNORECASE)
_D15_OTHER_LEVY = re.compile(r"(?<![a-z])(?:paye|nssf|sdl|osha|vat|tra)(?![a-z])", re.IGNORECASE)
_D15_WAGE = re.compile(r"mshahara|mishahara|wafanyakazi\s+wako|mfanyakazi", re.IGNORECASE)
_D15_NEG = re.compile(r"haikatwi|hukatwi|hakatwi|hazikatwi|usikate|usiikate|usimkate|hutakiwi|hupaswi|haupaswi|haitakiwi|haikatwe|bila\s+kukata|si\s+(?:ya|sehemu|kwa)|hakikatwi|hulipwa\s+na\s+mwajiri\s+pekee|mwajiri\s+pekee|kosa|marufuku|haihusu|sihitaji|hahitaji|hatakiwi", re.IGNORECASE)
_D15_CAR_Q = re.compile(r"gari\s+la\s+(?:kutembelea|abiria|kampuni|kibinafsi|familia)|magari\s+ya\s+abiria|passenger\s+(?:car|vehicle)|saloon|salon|company\s+car", re.IGNORECASE)
_D15_VAT_Q = re.compile(r"(?<![a-z])vat(?![a-z])|pembejeo|input", re.IGNORECASE)
_D15_CLAIM = re.compile(r"unaweza\s+kudai|unaruhusiwa\s+kudai|unadai|unastahili\s+kudai|inaruhusiwa\s+kudai|unaweza\s+kurejeshewa|inadaiwa|can\s+claim", re.IGNORECASE)
_D15_VAT_SAFE = re.compile(r"hapana|huwezi|hairuhusiwi|haidaiwi|hudai|isipokuwa|except|kusafirisha|kukodisha|kuuza\s+magari|abiria|mizigo|lori|pickup|trekta|basi|teksi|taxi|siyo|si\s+", re.IGNORECASE)


def wcf_deduction_asserted(body: str, question: str = ""):
    """[sentence] stating that WCF is deducted from the employee's wage. A sentence with ANY negation/offence cue is a mention, never judged."""
    # a pronoun reply ("unapaswa kuikata ...") names no levy in the sentence: the QUESTION supplies it, but only when it names WCF and NO other levy
    wcf_only = bool(_D15_WCF_SENT.search(question or "") and not re.search(r"(?<![a-z])(?:nssf|paye|sdl)(?![a-z])", question or "", re.IGNORECASE))
    out = []
    for s in _SENTENCE_SPLIT.split(body or ""):
        if s and (_D15_WCF_SENT.search(s) or wcf_only) and not _D15_OTHER_LEVY.search(s) and _D15_DEDUCT.search(s) and _D15_WAGE.search(s) and not _D15_NEG.search(s):
            out.append(s.strip())
    return out


def input_vat_car_claim_asserted(question: str, body: str):
    """[sentence] affirming that input VAT on a PASSENGER car is claimable (no negation, no passenger-business exception), for a question about a passenger/company car."""
    if not (_D15_CAR_Q.search(question or "") and _D15_VAT_Q.search(question or "")):
        return []
    out = []
    for s in _SENTENCE_SPLIT.split(body or ""):
        if s and _D15_CLAIM.search(s) and not _D15_VAT_SAFE.search(s):
            out.append(s.strip())
    return out


def body_contradicts_d15(question: str, body: str):
    """[(topic, sentence)] -- empty when neither rule applies."""
    out = [("wcf_not_deducted", s) for s in wcf_deduction_asserted(body, question)]
    out += [("input_vat_passenger_vehicle", s) for s in input_vat_car_claim_asserted(question, body)]
    return out


# ---- D-FIDELITY-16 (2026-11-17, founder-approved, from the unsourced-figure check of the 2026-11-17 live replies): THREE MORE CONSTANTS, FACT PATH, plus TWO REPAIRS.
#   dividend to a non-resident at 15%   "10% kwa wakazi na 15% kwa wasio wakazi"   (First Schedule para 4(b)(i): 5% / 10% whatever the payee's residence; the 15% in para 4(b) is 'other payments')
#   company income-tax return deadline  "miezi 12 ... 30 Septemba"                  (six months after the year of income, 30 June for a calendar-year company; 30 September is a PROVISIONAL TAX instalment date)
#   a flat 15% on severance             "inatozwa kodi ya asilimia 15 (PAYE)"      (employment income through the ordinary bands; the 15% limbs are a non-resident payee and director's fees)
# R19: each is a lookup against a statutory constant, so no engine result is needed and the guard reaches the fact path. NARROW BY CONSTRUCTION (R17): each needs its OWN subject in the sentence AND the figure in the
# SAME sentence, and every negation, every neighbouring payment type and every neighbouring obligation vetoes it. The must-pass probes the founder named are the veto lists: non-resident SERVICE FEES at 15%, "other
# payments" at 15%, provisional-tax dates (including 30 September), the VAT 12-month threshold, severance's 12 months, a non-resident's 15% and a director's fee 15%.
_D16_NONRES = re.compile(r"asiye\s+mkazi|wasio\s+wakazi|wasiokuwa\s+wakazi|non-?\s?residents?|nje\s+ya\s+nchi|(?<![a-z])wageni(?![a-z])|(?<![a-z])mgeni(?![a-z])|foreign(?:er)?s?", re.IGNORECASE)
_D16_DIV = re.compile(r"gawio|magawio|dividend", re.IGNORECASE)
_D16_15 = re.compile(r"(?<![\d.,])(?:asilimia\s+15|15\s*%|15\s*percent)(?![\d])", re.IGNORECASE)
_D16_OTHER_PAYMENT = re.compile(r"huduma|service|riba|interest|mrabaha|royalt|pango|(?<![a-z])rent(?![a-z])|kamisheni|commission|ushauri|consult|ada\s+ya|malipo\s+mengine|other\s+payments|mkurugenzi|director|usafirishaji|bima|insurance|mshahara|ajira|employ|ukodishaji", re.IGNORECASE)
_D16_NEG = re.compile(r"(?<![a-z])(?:si|sio|siyo|sivyo|hakuna|haikatwi|hakitumiki|haihusu|not|no|never)(?![a-z])", re.IGNORECASE)
_D16_RETURN = re.compile(r"(?<![a-z])(?:returns?|tamko|ritani)(?![a-z])", re.IGNORECASE)
_D16_12M = re.compile(r"miezi\s+(?:12|kumi\s+na\s+mbili)|12\s+months?", re.IGNORECASE)
_D16_SEP30 = re.compile(r"30\s+septemba|30(?:th)?\s+september|september\s+30|septemba\s+30", re.IGNORECASE)
_D16_NOT_RETURN_DEADLINE = re.compile(r"awamu|instal?l?ment|provisional|vat|thamani\s+iliyoongezwa|severance|kuachishwa|likizo|leave|usajili|sajili|threshold|kizingiti|mauzo|turnover|kodi\s+ya\s+zuio|withholding|paye|nssf|sdl|wcf", re.IGNORECASE)
_D16_DEADLINE_WORDS = re.compile(r"muda\s+wa\s+mwisho|tarehe\s+ya\s+mwisho|mwisho\s+wa\s+kuwasilisha|deadline|due\s+date|ifikapo", re.IGNORECASE)
_D16_INCOME_TAX_Q = re.compile(r"kodi\s+ya\s+mapato|income\s+tax|corporate|(?<![a-z])kampuni|(?<![a-z])company", re.IGNORECASE)
_D16_SEV_Q = re.compile(r"severance|kuachishwa\s+kazi|malipo\s+ya\s+kuachishwa|redundan|retrench|kupunguzwa\s+kazi", re.IGNORECASE)
_D16_SEV_EXCLUDED = re.compile(r"asiye\s+mkazi|wasio\s+wakazi|non-?resident|mkurugenzi|director", re.IGNORECASE)
_D16_SEV_TAX = re.compile(r"kodi|paye|(?<![a-z])tax|zuio|hukatwa|inatozwa|inakatwa|kukatwa", re.IGNORECASE)
_D16_SEV_OTHER_LEVY = re.compile(r"(?<![a-z])(?:nssf|sdl|wcf|osha|vat|tin)(?![a-z])", re.IGNORECASE)


def dividend_nonresident_15_asserted(question: str, body: str):
    """[sentence] attaching 15% to a DIVIDEND for a NON-RESIDENT. The sentence names a non-resident with the 15% within 50 characters; the dividend subject is in the sentence OR the question; any neighbouring
    payment type (service fees, interest, royalty, rent, commission, director's fee ...) or any negation vetoes it."""
    out = []
    for s in _SENTENCE_SPLIT.split(body or ""):
        if not s or not _D16_15.search(s) or _D16_OTHER_PAYMENT.search(s) or _D16_NEG.search(s):
            continue
        if not (_D16_DIV.search(s) or _D16_DIV.search(question or "")):
            continue
        if any(abs(a.start() - b.start()) <= 50 for a in _D16_15.finditer(s) for b in _D16_NONRES.finditer(s)):
            out.append(s.strip())
    return out


def corporate_return_deadline_misstated(question: str, body: str):
    """[sentence] stating 12 months or 30 September as the INCOME TAX RETURN deadline. The sentence names a return AND one of the two; the question is about an income-tax / company return. Provisional-tax
    instalments, VAT, severance, registration thresholds and withholding all veto, as does any negation."""
    if not (_D16_RETURN.search(question or "") and _D16_INCOME_TAX_Q.search(question or "")) or re.search(r"(?<![a-z])vat(?![a-z])", question or "", re.IGNORECASE):
        return []
    # a sentence naming the return states the figure; a sentence that only gives a DEADLINE ("muda wa mwisho ni 30 Septemba ya mwaka unaofuata", the live specimen's second sentence) states it for the
    # return the QUESTION is about -- but only the 30 September limb, since "12 months" with no subject is too common a phrase to attach to a return.
    return [s.strip() for s in _SENTENCE_SPLIT.split(body or "")
            if s and ((_D16_RETURN.search(s) and (_D16_12M.search(s) or _D16_SEP30.search(s))) or (_D16_SEP30.search(s) and _D16_DEADLINE_WORDS.search(s)))
            and not _D16_NOT_RETURN_DEADLINE.search(s) and not _D16_NEG.search(s)]


def severance_flat_15_asserted(question: str, body: str):
    """[sentence] putting a flat 15% tax on severance. The QUESTION is about severance and names no non-resident or director; the sentence carries the 15% and a tax word, and no other levy, no non-resident /
    director cue and no negation."""
    if not _D16_SEV_Q.search(question or "") or _D16_SEV_EXCLUDED.search(question or ""):
        return []
    return [s.strip() for s in _SENTENCE_SPLIT.split(body or "")
            if s and _D16_15.search(s) and _D16_SEV_TAX.search(s) and not _D16_SEV_OTHER_LEVY.search(s)
            and not _D16_SEV_EXCLUDED.search(s) and not _D16_NEG.search(s)]


# ---- D-FIDELITY-20 (2026-11-17, founder-approved after the BRELA verification of PROGRESS 4aw): THE COMPANY ANNUAL-RETURN DEADLINE. A CONSTANT (R19), FACT PATH.
#   specimen (gate c2143c0 and 0e11c3d, eval_072): "annual return kila mwaka -- hasa ndani ya miezi 12 kutoka tarehe ya usajili wake"
#   the Act (Companies Act Cap.212 R.E.2023, edition asserted from the running header, read 2026-11-17): each annual return is made up to the "return date" = the ANNIVERSARY of incorporation (or of the last return's date) and is
#   delivered within TWENTY-EIGHT DAYS of it; failing that, the company and every officer in default are liable to a fine. "12 months from registration" is not the rule.
# R25 (the two questions, answered at the site). (1) Defect: a confident wrong deadline on a stored gate reply; no served index row states the 28-day rule in the asker's vocabulary (it sits only inside the legacy form-number label of
#   `annual_return_form_number`), so the model fills the gap; the index row is QUEUED for the next regen (kaggle/NEXT_REGEN_QUEUE.md) and this guard is the layer that reaches it meanwhile. (2) What CORRECT output could it damage: a sentence
#   that NEGATES the date ("Hakuna tarehe maalum ya 30 Septemba kwa annual returns za BRELA" -- a training pair that denies it), one that states the right frame (anniversary / "tarehe ya kumbukumbu" / "siku 28"), a TAX return question
#   (the corporate-return guard owns income-tax returns), and any sentence that does not carry an annual-return subject AND a 12-month / 30-September figure. NARROW BY CONSTRUCTION (R17): the QUESTION is about a company's annual return
#   (BRELA / kampuni / Msajili) and about no tax; the sentence names the return AND the figure.
_D20_RETURN = re.compile(r"annual\s+returns?|ritani(?:\s+ya\s+mwaka)?|ripoti\s+ya\s+kila\s+mwaka|tamko\s+la\s+mwaka", re.IGNORECASE)
_D20_Q_COMPANY = re.compile(r"brela|kampuni|company|msajili|registrar|companies\s+act|sheria\s+ya\s+makampuni", re.IGNORECASE)
_D20_Q_TAX = re.compile(r"kodi|income\s+tax|(?<![a-z])tra(?![a-z])|(?<![a-z])paye(?![a-z])|(?<![a-z])vat(?![a-z])|tax", re.IGNORECASE)
# its OWN veto list: the D-FIDELITY-16 one contains "usajili" (registration thresholds) and would veto the very specimen ("... kutoka tarehe ya usajili wake")
_D20_NOT_THIS_OBLIGATION = re.compile(r"awamu|instal?l?ment|provisional|(?<![a-z])vat(?![a-z])|severance|kuachishwa|likizo|leave|threshold|kizingiti|mauzo|turnover|withholding|kodi\s+ya\s+zuio|(?<![a-z])paye(?![a-z])|nssf|sdl|wcf|leseni|licen[cs]e", re.IGNORECASE)
_D20_RIGHT_FRAME = re.compile(r"anniversary|maadhimisho|kumbukumbu|siku\s+28|28\s+days|return\s+date|tarehe\s+ya\s+return", re.IGNORECASE)


def brela_annual_return_deadline_misstated(question: str, body: str):
    """[sentence] stating 12 months or 30 September as the deadline for a COMPANY's annual return, for a question about a company's annual return. Negations, the correct anniversary / 28-day frame and any tax cue veto."""
    q = question or ""
    if not (_D20_RETURN.search(q) and _D20_Q_COMPANY.search(q)) or _D20_Q_TAX.search(q):
        return []
    return [s.strip() for s in _SENTENCE_SPLIT.split(body or "")
            if s and _D20_RETURN.search(s) and (_D16_12M.search(s) or _D16_SEP30.search(s))
            and not _D16_NEG.search(s) and not _D20_RIGHT_FRAME.search(s) and not _D20_NOT_THIS_OBLIGATION.search(s)]


# ---- D-FIDELITY-22 (2026-11-17, founder-approved, item 6 of batch 3): THE VAT-WITHHOLDING START DATE. A CONSTANT (R19), FACT PATH.
#   specimen (live, build e9e429e, eval_041): "Finance Act 2025 ilipanga mabadiliko hayo kuanzia 1 Julai 2025, lakini utekelezaji wake ulicheleweshwa hadi 1 Septemba 2025."
#   the Act (Finance Act 2025 (No. 11), edition asserted, read 2026-11-17): s.2 commences the Act on 1 JULY 2025; s.124 inserts VAT Act s.5(5) (the 3% / 6% withholding) with NO separate commencement clause; the "1st September, 2025" proviso
#   is attached to s.5(6) -- the 16% rate for an UNREGISTERED person who pays through a bank / approved electronic system -- a different rule. The reply put that date on the withholding rule.
# R25. (1) Defect: a confident wrong start/deferral date on the fact path. (2) What CORRECT output could it damage: a sentence about the B2C e-payment 16% rule (names e-payment / digital / B2C / 16%), a negation ("si 1 Septemba"), a correct
#   1 July statement (no September), an UNRELATED 1 September date (the subject must be VAT WITHHOLDING, from the question or the sentence), and any sentence that gives September no start / delay word. The replacement states the fixed rule.
_D22_WH = re.compile(r"vat\s+withholding|vat\s+ya\s+zuio|zuio\s+la\s+vat|zuio\s+wa\s+vat|utaratibu\s+wa\s+zuio|withholding\s+(?:vat|agent)", re.IGNORECASE)
_D22_SEP = re.compile(r"1\s+septemba(?:\s+2025)?|septemba\s+1|1(?:st)?\s+september(?:\s+2025)?|september\s+1", re.IGNORECASE)
_D22_B2C = re.compile(r"e-?payment|kidijitali|digital|b2c|mteja\s+wa\s+mwisho|16\s*%|asilimia\s+16|malipo\s+ya\s+kielektroniki|kielektroniki|electronic", re.IGNORECASE)
_D22_START = re.compile(r"cheleweshw|ulianza|ilianza|kuanza|kuanzia|ulipoanza|utekelezaji|implementation|effective|delayed|postponed|deferred|hadi", re.IGNORECASE)


def vat_withholding_start_misstated(question: str, body: str):
    """[sentence] putting 1 September on the START (or a deferral) of VAT WITHHOLDING. The subject comes from the question OR the sentence; the B2C e-payment rule and any negation veto."""
    subject_q = bool(_D22_WH.search(question or ""))
    return [s.strip() for s in _SENTENCE_SPLIT.split(body or "")
            if s and (subject_q or _D22_WH.search(s)) and _D22_SEP.search(s) and _D22_START.search(s)
            and not _D22_B2C.search(s) and not _D16_NEG.search(s)]


# ---- D-FIDELITY-23 (2026-11-18, founder-approved, batch 4 item b): "46" AS THE SUB-SECTOR COUNT OF A SINGLE SECTOR. A CONSTANT (R19), FACT PATH.
#   specimen (live, build 7b94236, PROGRESS 4az): "Kulingana na GN 605A, kuna sekta ndogo 46 katika sekta ya madini peke yake."
#   the Order (kazi.go.tz official copy, GN No. 605A, 13/10/2025, edition asserted, read 2026-11-18): First Schedule item 10 "Mining Sector" has FOUR rows, (a)-(d). 46 is the claimed TOTAL across all sectors (PKF), which the Order does not settle.
# R25. (1) Defect: a confident wrong sub-count for ONE sector on the fact path. (2) What CORRECT output could it damage: "46" stated as the OVERALL total (with or without its PKF source caveat: "kwa ujumla", "jumla", "zote", "sekta 16", "PKF", "total"),
#   a negation ("si 46"), any sentence that does not carry the 46 as a sub-sector count, and any text not about the minimum-wage Order (the context must be GN 605A / kima cha chini / minimum wage, in the question OR the sentence).
#   Names no single sector in particular: the claim is "this one sector has 46 sub-sectors", which no sector of the Order does (the largest has well under ten rows).
_D23_COUNT = re.compile(r"sekta\s+ndogo\s+(?:za\s+)?46(?!\d|[,.]\d)|(?<![\d,.])46\s+(?:sekta\s+ndogo|sub-?sectors?)|(?<![\d,.])46\s+(?:za\s+)?(?:vipengele|aina\s+ndogo)", re.IGNORECASE)
_D23_CTX = re.compile(r"605\s*a|kima\s+cha\s+chini|mshahara\s+wa\s+chini|minimum\s+wage", re.IGNORECASE)
_D23_SINGLE = re.compile(r"(?:katika|ndani\s+ya|kwenye)\s+sekta\s+ya\s+[a-z]+|sekta\s+hiyo|sekta\s+hii|peke\s+yake|pekee|(?:in|within)\s+the\s+[a-z]+\s+sector|[a-z]+\s+sector\s+(?:alone|has|contains)", re.IGNORECASE)
_D23_Q_SINGLE = re.compile(r"sekta\s+ya\s+[a-z]+\s+ina", re.IGNORECASE)
_D23_TOTAL = re.compile(r"kwa\s+ujumla|(?<![a-z])jumla|(?<![a-z])zote|sekta\s+zote|kwa\s+pamoja|(?<![a-z])across|in\s+total|(?<![a-z])total|overall|(?<![a-z])pkf|sekta\s+16|16\s+sectors", re.IGNORECASE)


def gn605a_subsector_count_misstated(question: str, body: str):
    """[sentence] giving 46 as the sub-sector count of ONE sector of GN 605A. The overall total, a negation and any non-minimum-wage text are left alone."""
    q = question or ""
    return [s.strip() for s in _SENTENCE_SPLIT.split(body or "")
            if s and _D23_COUNT.search(s) and (_D23_CTX.search(q) or _D23_CTX.search(s))
            and (_D23_SINGLE.search(s) or (_D23_Q_SINGLE.search(q) and not _D23_TOTAL.search(s)))
            and not _D23_TOTAL.search(s) and not _D16_NEG.search(s)]


# ---- D-FIDELITY-24 (2026-11-22, founder-approved, option A of the mining-vs-energy miss): ANOTHER SECTOR'S MINIMUM WAGE STATED AS A MINING RATE. A CONSTANT (R19), FACT PATH.
#   specimen (live, build 1c7582c, eval/results/batch4_deploy_live_2026_11_18.json): "Kulingana na GN 605A, viwango vilivyothibitishwa kwa sekta ya madini na nishati ni karibu TZS 765,900 kwa mwezi. Thibitisha kiwango halisi cha sekta yako na MLYWF."
#   the Order (kazi.go.tz official copy, GN No. 605A, edition asserted; transcription in rules_engine.wage_schedule, asserted against the gazette extract): the MINING sector (item 10) has FOUR monthly rates -- brokers 333,500; primary
#   mining licence 397,600; dealer 595,000; mining and prospecting minerals 695,000. 765,900 is the ENERGY sector, international companies (item 7(a)); domestic energy is 297,000.
# R25. (1) Defect: a confident wrong rate on the fact path for a sector the Order lists, with the right rows served. (2) What CORRECT output could it damage: any of the four mining rates stated for mining; a correct energy answer (765,900 or
#   297,000 attributed to energy); a sentence naming BOTH sectors with each figure after its own subject ("Madini: 695,000; nishati: 765,900"); a negation ("si 765,900"); and any text not about the minimum wage (context from the question or the
#   sentence). ATTRIBUTION is by the nearest preceding subject cue, never by a window (D-FIDELITY-6's two failed designs): the figure belongs to the last sector word before it, EXCEPT a bare coordination of mining with another sector
#   ("madini na nishati ... 765,900") which attributes ONE figure to BOTH and is the founding specimen. NARROW: only figures the schedule assigns to a sector other than mining are judged; the mining rates are never flagged.
_D24_CTX = re.compile(r"605\s*a|kima\s+cha\s+chini|mshahara\s+wa\s+chini|kiwango\s+cha\s+chini|minimum\s+wage", re.IGNORECASE)
_D24_MINING = r"madini|mgodi|migodi|uchimbaji|mchimbaji|wachimbaji|mining|(?<![a-z])miners?(?![a-z])"
_D24_OTHER = (r"nishati|(?<![a-z])energy|kilimo|agricultur|afya|(?<![a-z])health|ujenzi|construction|hoteli|(?<![a-z])hotel|ulinzi|(?<![a-z])security|usafirishaji|transport|viwanda|manufactur|mawasiliano|telecom|benki|"
              r"(?<![a-z])bank|shule|(?<![a-z])school|biashara|(?<![a-z])business|kazi\s+za\s+nyumbani|domestic|taka|waste|burudani|michezo|sanaa")
_D24_SUBJECT = re.compile(r"(?P<mining>" + _D24_MINING + r")|(?P<other>" + _D24_OTHER + r")", re.IGNORECASE)
_D24_FIGURE = re.compile(r"(?<![\d,.])(\d{1,3}(?:,\d{3})+|\d{6})(?![\d])")
_D24_COORD = re.compile(r"^\s*(?:na|and|pamoja\s+na|au|or|&|/|,)?\s*$", re.IGNORECASE)
_D24_OWNERS = None


def _d24_non_mining_figures():
    """The set of monthly figures the schedule assigns ONLY to sectors other than mining. Lazy: wage_schedule is pure data and fidelity must stay importable without it."""
    global _D24_OWNERS
    if _D24_OWNERS is None:
        from .rules_engine import wage_schedule as ws
        owners = {}
        for row in ws.SCHEDULE:
            owners.setdefault(int(row[-1]), set()).add(row[0])
        _D24_OWNERS = {f for f, secs in owners.items() if 10 not in secs}
    return _D24_OWNERS


def mining_wage_misattributed(question: str, body: str):
    """[sentence] stating another sector's monthly minimum wage as a MINING rate (alone, or in a bare coordination with another sector). The four mining rates, a correct energy figure, per-subject lists and negations are left alone."""
    q = question or ""
    foreign = _d24_non_mining_figures()
    out = []
    for s in _SENTENCE_SPLIT.split(body or ""):
        if not s or not _D24_SUBJECT.search(s) or not (_D24_CTX.search(q) or _D24_CTX.search(s)) or _D16_NEG.search(s):
            continue
        cues = [(m.start(), m.end(), "mining" if m.group("mining") else "other") for m in _D24_SUBJECT.finditer(s)]
        for fm in _D24_FIGURE.finditer(s):
            if int(fm.group(1).replace(",", "")) not in foreign:
                continue
            before = [c for c in cues if c[1] <= fm.start()]
            if not before:
                continue
            last = before[-1]
            conflated = (last[2] == "other" and len(before) >= 2 and before[-2][2] == "mining" and bool(_D24_COORD.match(s[before[-2][1]:last[0]])))
            if last[2] == "mining" or conflated:
                out.append(s.strip())
                break
    return out


# ---- D-FIDELITY-25 (2026-11-22, from preliminary Gate 2 control #24): "SDL NOT PAYABLE" STATED TO AN EMPLOYER WHOSE OWN STATED HEADCOUNT IS AT OR ABOVE THE THRESHOLD. A CONSTANT COMPARISON (R19), FACT PATH.
#   specimen (live, build 7643e18, eval/results/gate2_prelim_live_2026_11_22.json gp_24): "...ununuzi wa bidhaa kutoka nje ya nchi (imports) haupaswi kutozwa SDL. Hivyo, kwa sasa, idadi ya wafanyakazi wako 12 haihitaji malipo ya SDL."
#   the facts served at rank 1 said the opposite ("Kizingiti cha SDL ni wafanyakazi 10 au zaidi", plus a worked example for 12 employees); the model contradicted them.
#   the constant (locked facts sdl_threshold, sdl_exemption_categories; VETA Act Cap.82 s.19(1), nine categories): SDL applies to Mainland employers with 10 OR MORE employees, EXCEPT the nine statutory exemption categories.
# R19: this compares the USER'S OWN stated count to a fixed threshold. It is NOT a derived-amount check (Guard B): no lawful transformation of "12 employees" makes "you need not pay SDL" true unless the employer is in an exempt category,
#   and the exemption vocabulary is a VETO in the question AND in the sentence.
# R25. (1) Defect: a confident wrong applicability verdict (a 12-employee employer told it owes no SDL). (2) What CORRECT output could it damage: the engine's own statement ("Mwenye wafanyakazi chini ya 10 hana wajibu ..."), an exempt employer
#   (government, local authority, embassy, UN, aid body, religious body, school, charity, farm: any of those words in the question or the sentence vetoes), a negated denial ("si kweli kwamba haulipi"), a count below 10, a count the extractor
#   does not read (sole_headcount returns None for two counts -- the safe direction), and any sentence that does not name SDL. NARROW: the question names SDL, states ONE headcount of 10 or more, and names no exempt category.
_D25_Q_SDL = re.compile(r"(?<![a-z])sdl(?![a-z])|skills\s+development\s+levy|tozo\s+la\s+mafunzo", re.IGNORECASE)
_D25_EXEMPT = re.compile(
    r"serikali|halmashauri|manispaa|ubalozi|balozi|diplomat|umoja\s+wa\s+mataifa|(?<![a-z])un(?![a-z])|kimataifa|misaada|msaada|dini|kanisa|msikiti|shule|chuo|elimu|hisani|charit|mkulima|kilimo|shamba|farm|isipokuwa|msamaha|exempt|"
    r"taasisi\s+ya|sheria\s+ya\s+elimu|"
    r"mamlaka\s+ya\s+maji|usafi\s+wa\s+mazingira|water\s+supply|taesa|intern|wanafunzi", re.IGNORECASE)   # 2026-11-22: the two categories the R.E.2023 list and Finance Act 2024 s.112 add (TaESA interns, (k) water authorities) -- vetoes only, so it can only flag LESS
_D25_DENY = re.compile(
    r"haihitaji\s+(?:kulipa|malipo)|hauhitaji\s+(?:kulipa|malipo)|haulipi|hulipi|huna\s+wajibu|hana\s+wajibu|haupaswi\s+kulipa|haupaswi\s+kutozwa|hautakiwi\s+kulipa|haitakiwi\s+kulipa|"
    r"haitozwi|hautozwi|haihusiki|haikuhusu|hakuna\s+(?:wajibu|malipo\s+ya\s+sdl)|haipaswi\s+kutozwa|not\s+(?:payable|required\s+to\s+pay)|no\s+obligation", re.IGNORECASE)
_D25_BELOW = re.compile(r"chini\s+ya\s+(?:10|kumi)|pungufu\s+ya\s+10|less\s+than\s+10|fewer\s+than\s+10|hajafikisha|haijafikia|hawajafikisha|haujafikisha", re.IGNORECASE)
# added after the FIRST pricing (13,449 texts, 5 flags, 3 of them false): (a) a question ABOUT the threshold ("Kizingiti cha SDL ni wafanyakazi 10 au ...") states "10" as the RULE, not as the user's headcount; (b) a second, SMALLER count in
# the question ("wafanyakazi 12, msimu mwingine 6") or in the sentence ("miezi yenye 6 huna wajibu", "only 9 employees") means the sentence is discussing the below-threshold case, which is correct.
_D25_THRESHOLD_Q = re.compile(r"kizingiti|kikomo|threshold|kiwango\s+cha\s+chini", re.IGNORECASE)   # NOT "wangapi": the founding specimen asks the threshold AND states its own headcount
_D25_SMALL_NUMBER = re.compile(r"(?<![\d,.])[1-9](?![\d,.])")
_D25_NEGATED_DENIAL = re.compile(r"si\s+kweli|sivyo|siyo\s+kweli|ni\s+makosa|hapana,?\s+(?:unatakiwa|unapaswa|inatozwa|unalipa)", re.IGNORECASE)


def sdl_denied_above_threshold(question: str, body: str):
    """[sentence] telling an employer whose OWN stated headcount is 10 or more that SDL is not payable, when the question names no exempt category. The engine's below-threshold statement, exempt-category talk and negated denials are left alone."""
    q = question or ""
    if not _D25_Q_SDL.search(q) or _D25_EXEMPT.search(q) or _D25_THRESHOLD_Q.search(q) or _D25_SMALL_NUMBER.search(q):
        return []
    from .swahili_numbers import sole_headcount
    n = sole_headcount(q)
    if n is None or n < 10:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT.split(body or "")
            if s and _D25_Q_SDL.search(s) and _D25_DENY.search(s) and not _D25_BELOW.search(s) and not _D25_EXEMPT.search(s) and not _D25_NEGATED_DENIAL.search(s)
            and not _D25_SMALL_NUMBER.search(s)]


# ---- D-FIDELITY-25b (2026-11-22, founder-approved with THREE CONDITIONS): D-FIDELITY-25 EXTENDED TO THE SDL COMPUTE PATH. A compute-path reply is `model body + engine working`, so a model-written sentence can contradict the engine's SDL
#   verdict. The three conditions, each load-bearing and each pinned by a plant: (1) UNNEGATED applicability questions only -- eval_394 showed the engine's own verdict LEAD can be the wrong half on a negated premise ("Je, NSSF si ya hiari?"
#   answered "Ndiyo." to a question nobody asked), so a negated question is never judged; (2) the body's polarity is compared with the engine's `applicable` BOOLEAN, never with its lead word; (3) BLANK THE BODY ONLY -- the working still
#   renders, so the user loses a sentence and keeps the answer.
# R25. (1) Defect: a model sentence telling an employer SDL does not apply when the engine computed that it does (or the reverse). (2) What CORRECT output could it damage: an exempt employer (any exempt-category word in the question or the
#   sentence vetoes: the engine knows only the headcount, so its boolean can be the wrong half there), a below-threshold sentence, a negated denial, any sentence not naming SDL, a negated question. Narrow: SDL named, an engine SDL verdict
#   with a boolean, a plain applicability question.
_D25B_NEGATED_Q = re.compile(r"(?<![a-z])(?:si|siyo|sivyo|haihitaji|hahitaji|hauhitaji|hailipwi|halipwi|haitozwi|sihitaji|sitakiwi|hatakiwi|hautakiwi|haulipi|hawalipi|hakuna|hamna)(?![a-z])|ni\s+kweli", re.IGNORECASE)
_D25B_AFFIRM = re.compile(r"unalazimika\s+kulipa|unatakiwa\s+kulipa|unapaswa\s+kulipa|lazima\s+ulipe|inakuhusu|utalipa|inatozwa|ndiyo", re.IGNORECASE)
_D25B_NEG_IN_SENTENCE = re.compile(r"(?<![a-z])(?:hapana|huna|hana|hutakiwi|haulazimiki|haupaswi|hautozwi|haitozwi|haikuhusu|si)(?![a-z])|chini\s+ya\s+(?:10|kumi)", re.IGNORECASE)


def sdl_body_contradicts_verdict(question: str, body: str, computation):
    """[sentence] whose SDL polarity contradicts the engine's boolean on an unnegated applicability question. [] otherwise. Pure."""
    if computation is None or getattr(computation, "computation", None) != "sdl" or not isinstance(getattr(computation, "applicable", None), bool):
        return []
    q = question or ""
    if not _D25_Q_SDL.search(q) or _D25_EXEMPT.search(q) or _D25B_NEGATED_Q.search(q):
        return []
    from .routing import is_applicability_question
    if not is_applicability_question(q):
        return []
    out = []
    for s in _SENTENCE_SPLIT.split(body or ""):
        if not s or not _D25_Q_SDL.search(s) or _D25_EXEMPT.search(s) or _D25_NEGATED_DENIAL.search(s):
            continue
        if computation.applicable and _D25_DENY.search(s) and not _D25_BELOW.search(s):
            out.append(s.strip())
        elif (not computation.applicable) and _D25B_AFFIRM.search(s) and not _D25B_NEG_IN_SENTENCE.search(s):
            out.append(s.strip())
    return out


# ---- D-FIDELITY-27 / 28 (2026-11-22, founder decision 3): TWO UNSUPPORTED SCOPE CLAIMS, FACT PATH. Constants about what a LAW SAYS (R19), so no engine result is needed. Both REPLACED (the fact path cannot be blanked) with the proposed fact text.
# D-FIDELITY-27 -- SDL scope stated by PREMISES. Specimen (live, build a78f5d0, d25_deploy_live_2026_11_22.json): "SDL inalenga waajiri wenye wafanyakazi 10+ katika MAENEO YA BIASHARA (commercial premises) ... Wafanyakazi wa nyumbani ... hawaingii kwenye
#   kizingiti cha SDL." Primary text read 2026-11-22 (VETA Act Cap.82 R.E.2023, TRA-hosted, sha256 eac6e92d...): the levy is charged on "every employer who has in his employment ten or more employees"; the words "domestic" and "premises" appear NOWHERE in the Act.
# D-FIDELITY-28 -- NSSF contributions tied to AGE 60. Specimen (live, same run): "michango ya NSSF huendelea hadi umri wa miaka 60". NSSF Act Cap.50 R.E.2023 (sha256 2a820e67...): age 60 is "pensionable age" and appears only in BENEFIT provisions; Parts III-IV set no age at which
#   contributions start or stop; s.20 does not relieve the employer for an employee in receipt of or entitled to a benefit. So a claim that contributions stop at 60 OR continue until 60 is unsupported either way.
# R25. (1) Defect: an invented SDL scope rule (one live reply) and an invented NSSF age cut-off (one live reply). (2) What CORRECT output could they damage: a sentence that DENIES the premises rule ("SDL haitegemei maeneo ya biashara"), a pension-eligibility sentence
#   about age 60 that does not speak of contributions, an early-retirement sentence (55), and a sentence that says contributions are NOT tied to age. Each is vetoed by a negation cue or by requiring the word for contributions beside the age.
_D27_SDL = re.compile(r"(?<![a-z])sdl(?![a-z])|tozo\s+la\s+mafunzo|skills\s+development\s+levy", re.IGNORECASE)
_D27_PREMISES = re.compile(r"maeneo\s+ya\s+biashara|commercial\s+premises|business\s+premises|mahali\s+pa\s+biashara|ofisi\s+ya\s+biashara|biashara\s+pekee|ene(?:o|no)\s+la\s+biashara|premises", re.IGNORECASE)
_D27_NEG = re.compile(r"(?<![a-z])(?:si|siyo|sio|haitegemei|haihusu|haihusiani|haina|hakuna|not|no)(?![a-z])", re.IGNORECASE)
_D28_CONTRIB = re.compile(r"michango|mchango|contribution|kuchangia|inachangiwa|huchangiwa|hulipwa\s+michango", re.IGNORECASE)
_D28_AGE60_CLAIM = re.compile(
    r"(?:huendelea|hudumu|zinaendelea|inaendelea|huisha|zinaisha|inaisha|hukoma|zinakoma|inakoma|hukatwa|huchangiwa|hulipwa|inalipwa)[^.]{0,70}(?:hadi|mpaka|until|till|baada\s+ya)\s+(?:umri\s+wa\s+)?(?:miaka\s+)?60(?![0-9])"
    r"|(?:ukifikisha|ukifika|akifikisha|akifika|anapofikisha|unapofikisha|baada\s+ya\s+kufikisha)\s+(?:umri\s+wa\s+)?(?:miaka\s+)?60(?![0-9])[^.]{0,70}(?:hahitaji|huhitaji|hauhitaji|hakuna\s+michango|haulipi|huacha|hukoma|hawajibiki|haitajiki|hahitajiki)",
    re.IGNORECASE)
# 2026-11-23, FROM THE LIVE CHECK (eval/results/sdl_nssf_deploy_live_2026_11_23.json): the first D-28 pattern wanted "hadi/mpaka 60" and so missed the live reply "michango huisha pale mfanyakazi anapofikia umri wa miaka 60"; a THIRD reply invented a
# different cut-off, "michango huisha ukifikia miezi 180" (180 months is the MINIMUM for a pension, not an end to contributions). A denial of the 180 claim ("... kwamba michango huisha ...") is left alone.
_D28_STOP_AT_60 = re.compile(r"(?:huisha|zinaisha|inaisha|hukoma|zinakoma|inakoma|huacha|zinaacha)[^.?!]{0,60}(?:anapofikia|anapofikisha|ukifikia|ukifikisha|ukifika|akifika|akifikisha|anapofika|unapofikia)[^.?!]{0,30}60(?![0-9])", re.IGNORECASE)
_D28_STOP_AT_180 = re.compile(r"michango[^.?!]{0,60}(?:huisha|zinaisha|inaisha|hukoma|zinakoma|inakoma)[^.?!]{0,40}(?:miezi\s+180|(?<![0-9])180(?![0-9])|miaka\s+15(?![0-9]))", re.IGNORECASE)
_D28_DENIAL_OF_CLAIM = re.compile(r"kwamba|haisemi|haikomi|hazikomi|haziishi", re.IGNORECASE)
_D28_NEG = re.compile(r"(?<![a-z])(?:si|siyo|sio|haikomi|hazikomi|haziishi|haitegemei|haihusiani)(?![a-z])|haijafungwa|haijafungamana", re.IGNORECASE)


def sdl_scope_by_premises(question: str, body: str):
    """[sentence] stating that SDL turns on commercial premises / places of business. A sentence that DENIES the rule is left alone."""
    if not body or not _D27_SDL.search((question or "") + " " + body):
        return []
    return [s.strip() for s in _SENTENCE_SPLIT.split(body)
            if s and _D27_PREMISES.search(s) and (_D27_SDL.search(s) or _D27_SDL.search(question or "")) and not _D27_NEG.search(s)]


def nssf_contributions_tied_to_age_60(question: str, body: str):
    """[sentence] stating that NSSF contributions continue until, or stop at, age 60. Pension-eligibility and early-retirement sentences (no word for contributions) and sentences that deny the tie are left alone."""
    if not body:
        return []
    out = []
    for s in _SENTENCE_SPLIT.split(body):
        if not s or not _D28_CONTRIB.search(s):
            continue
        if _D28_AGE60_CLAIM.search(s) and not _D28_NEG.search(s):
            out.append(s.strip())
        elif _D28_STOP_AT_60.search(s) and not _D28_NEG.search(s):
            out.append(s.strip())
        elif _D28_STOP_AT_180.search(s) and not _D28_DENIAL_OF_CLAIM.search(s):
            out.append(s.strip())
    return out


# ---- D-FIDELITY-29 (2026-11-23, founder): NSSF STATED AS DUE BY THE 7TH. A CONSTANT (R19), so no engine result is needed. Locked fact nssf_payment_deadline (NSSF Act Cap.50 R.E.2023 s.14(1), direct read): contributions are due WITHIN ONE MONTH after the
# end of the month; the 7th is SDL's (VETA Act s.16) and PAYE's (Income Tax Act s.109). Founding specimen (live, build b96e8a8, eval/results/sdl_three_routes_live_2026_11_23.json, the compute reply to "SDL na NSSF ni kiasi gani?"): "... NSSF: 20% ya TZS
# 6,000,000 = TZS 1,200,000 ... Zote mbili zinalipwa ndani ya siku 7 za kwanza za mwezi unaofuata." -- NSSF is named in the sentence BEFORE; the sentence that states the 7 days names no levy, so a same-clause rule is blind to it (R39: the anaphoric-transfer
# blind spot) and an ANAPHOR limb is part of the rule.
# R25. (1) Defect: the NSSF deadline stated as the 7th / 7 days (one live reply; the locked fact exists because the same error was found before). (2) What CORRECT output could it damage: a clause naming NSSF AND a one-month deadline ("NSSF ni ndani ya mwezi mmoja;
#   SDL na PAYE tarehe 7"), a clause that DENIES the tie ("NSSF si tarehe 7"), a sentence that gives the 7th to SDL/PAYE with NSSF in a different clause (split on ; : lakini ila wakati), and a sentence whose levies are all explicit and exclude NSSF.
#   The anaphor limb fires only on a sentence naming NO levy (zote / both / all) directly after a sentence naming NSSF.
_D29_NSSF = re.compile(r"(?<![a-z])nssf(?![a-z]|\.go\.tz)", re.IGNORECASE)
_D29_LEVY = re.compile(r"(?<![a-z])(?:nssf|sdl|paye|wcf|vat|wht|osha|nhif)(?![a-z]|\.go\.tz)|tozo\s+la\s+mafunzo", re.IGNORECASE)
_D29_SEVEN = re.compile(r"(?:siku|tarehe)\s+(?:ya\s+)?(?:7|saba)(?![0-9])|(?<![0-9])7(?:th)?\s+days?(?![a-z])|seven\s+days|(?:by|on)\s+the\s+7th|(?:ndani\s+ya|kufikia|ifikapo|kabla\s+ya)\s+(?:siku\s+)?(?:ya\s+)?7(?![0-9])", re.IGNORECASE)
_D29_MONTH = re.compile(r"mwezi\s+mmoja|one\s+month|calendar\s+month|siku\s+30(?![0-9])|30\s+days", re.IGNORECASE)
_D29_NEG = re.compile(r"(?<![a-z])(?:si|siyo|sio|not|wala|tofauti)(?![a-z])", re.IGNORECASE)
_D29_ANAPHOR = re.compile(r"zote\s+mbili|(?<![a-z])zote(?![a-z])|hizi\s+zote|(?<![a-z])both(?![a-z])|all\s+(?:three|of\s+them)", re.IGNORECASE)
# the live replies run sentences together with NO space after the full stop ("...tra.go.tz).NSSF inalipwa ... (nssf.go.tz).PAYE inalipwa ..."), so a split on punctuation + whitespace merged the NSSF one-month clause with the PAYE 7th clause and the month guard excused the error:
_D29_SENT = re.compile(r"(?<=[.!?])\s+|(?<=[.!?])(?=[A-Z])|\n+")
_D29_CLAUSE = re.compile(r"[;:|]|\s+(?:lakini|ila|wakati|while|but|whereas)\s+", re.IGNORECASE)
# A LIST of levies ("SDL na NSSF", "PAYE, NSSF, WCF na kodi", "SDL + PAYE"): the unit a deadline attaches to. Priced over the corpus (eval/results/price_d29_d30_2026_11_23.json): the first draft asked only "is NSSF in the same clause as a 7th" and flagged four
# CORRECT training rows (a `|`-separated table, the nssf.go.tz DOMAIN read as a levy, "PAYE kufikia tarehe 7" where the 7th belongs to PAYE, a sentence the splitter could not break at ".)"). The deadline belongs to the list directly BEFORE it (or, when none, directly after).
_D29_LEVY_LIST = re.compile(r"(?:nssf|sdl|paye|wcf|vat|wht|osha|nhif)(?![a-z]|\.go\.tz)(?:\s*(?:,|\+|&|na|and|au|pamoja\s+na|sambamba\s+na)\s*(?:michango\s+ya\s+|mchango\s+wa\s+|malipo\s+ya\s+|contributions?\s+(?:of\s+|to\s+)?)?(?:nssf|sdl|paye|wcf|vat|wht|osha|nhif)(?![a-z]|\.go\.tz))*", re.IGNORECASE)


def _d29_list_for_deadline(clause, m7):
    """The levy list the 7th attaches to: the last list before it, else a list within 25 characters after it. '' when there is none."""
    before = [m for m in _D29_LEVY_LIST.finditer(clause[:m7.start()])
              if not re.search(r"(?<![a-z])(?:nssf|sdl|paye|wcf|vat|wht|osha|nhif)(?![a-z])", clause[m.end():m7.start()], re.IGNORECASE)]
    if before:
        return before[-1].group(0)
    after = _D29_LEVY_LIST.search(clause[m7.end():m7.end() + 25])
    return after.group(0) if after else ""


def nssf_deadline_misstated(question: str, body: str):
    """[clause] stating that NSSF is due by the 7th / within 7 days: NSSF is in the levy list the 7th attaches to, or the sentence says 'zote mbili' / 'both' (no levy named) directly after a sentence naming NSSF. A clause that also states a one-month
    deadline, or denies the tie, is left alone. Pure."""
    if not body or not _D29_NSSF.search(body):
        return []
    out, prev_named_nssf = [], False
    for s in _D29_SENT.split(body):
        if not s or not s.strip():
            continue
        for clause in _D29_CLAUSE.split(s):
            m7 = _D29_SEVEN.search(clause) if clause else None
            if not m7 or _D29_NEG.search(clause) or _D29_MONTH.search(clause):
                continue
            lst = _d29_list_for_deadline(clause, m7)
            if lst and _D29_NSSF.search(lst):
                out.append(clause.strip())
            elif not _D29_LEVY.search(clause) and prev_named_nssf and _D29_ANAPHOR.search(clause):
                out.append(clause.strip())
        prev_named_nssf = bool(_D29_NSSF.search(s))
    return out


# ---- D-FIDELITY-30 (2026-11-23, founder): "P9" IN AN ANSWER IS KENYAN (KRA) TERMINOLOGY -- TANZANIA'S TRA HAS NO FORM BY THAT NAME. A REPAIR (one clause changes, nothing is blocked; the D-FIDELITY-14 posture). Locked fact paye_p9_deadline (Income Tax Act Cap.332
# R.E.2023 s.110(3)(b); CLAUDE.md Section 11): the annual employment-income document is the WITHHOLDING CERTIFICATE, served by 30 January. Founding specimen (live, build b96e8a8): the SDL-audit reply "The auditor will ask to see: payslips, P9 forms, SDL returns ...".
# R25. (1) Defect: a Kenyan form name asserted as a Tanzanian document (one live reply). (2) What CORRECT output could it damage: a sentence that SAYS P9 is Kenyan / not Tanzanian ("P9 ni neno la Kenya; TRA haina fomu hiyo"), which carries a negation or a Kenya / KRA / term cue and is left untouched. The replacement is
#   the document the locked fact names, so a repaired sentence stays true.
_D30_P9 = re.compile(r"(?<![A-Za-z0-9])((?:fomu|form|forms|vyeti)\s+(?:ya|za|of)\s+)?P\s?9(?![A-Za-z0-9])(\s+forms?|\s+fomu)?", re.IGNORECASE)
_D30_SAYS_NOT_TZ = re.compile(r"kenya|(?<![a-z])kra(?![a-z])|haina|hakuna|haitumii|haipo|(?<![a-z])si(?![a-z])|siyo|(?<![a-z])not(?![a-z])|isn'?t|usitumie|(?<![a-z])neno|(?<![a-z])term|terminolog", re.IGNORECASE)


def p9_asserted(body: str):
    """[sentence] that uses 'P9' as if it were a Tanzanian document. A sentence that says it is Kenyan / not Tanzanian is left alone. Pure."""
    if not body:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT.split(body) if s and _D30_P9.search(s) and not _D30_SAYS_NOT_TZ.search(s)]


# The replacement is the withholding certificate ONLY where the sentence is about PAYE / the employee's annual tax document (the context that locked fact paye_p9_deadline answers). Priced over the corpus: a gate reply listed "fomu ya NSSF P9" among NSSF
# REGISTRATION documents, and substituting "cheti cha zuio" there would keep a false claim (registration needs no withholding certificate). Outside that context the Kenyan token is DROPPED instead, so no sentence is made false by the repair.
_D30_PAYE_CONTEXT = re.compile(r"paye|payslip|ukaguzi|audit|zuio|withhold|kodi\s+ya\s+mapato|taarifa\s+ya\s+mwaka|annual|mshahara|payroll|(?<![a-z])tra(?![a-z])", re.IGNORECASE)
_D30_OTHER_AUTHORITY = re.compile(r"(?<![a-z])(?:nssf|wcf|osha|brela)(?![a-z])", re.IGNORECASE)


def repair_p9(body: str) -> str:
    """The body with 'P9' / 'P9 forms' replaced by the withholding certificate (cheti / vyeti vya zuio) in a PAYE-context sentence that asserts it, and simply dropped in any other context; a sentence that says P9 is Kenyan / not Tanzanian is untouched. Idempotent."""
    if not body or not _D30_P9.search(body):
        return body
    out = []
    for part in re.split(r"(?<=[.!?\n])", body):
        if _D30_P9.search(part) and not _D30_SAYS_NOT_TZ.search(part):
            if _D30_PAYE_CONTEXT.search(part) and not _D30_OTHER_AUTHORITY.search(part):
                part = _D30_P9.sub(_p9_replacement, part)
            else:
                part = re.sub(r"\s{2,}", " ", _D30_P9.sub("", part)).replace(" ,", ",").replace(" .", ".")
        out.append(part)
    return "".join(out)


def _p9_replacement(m) -> str:
    """Plural when the match is 'P9 forms', 'forms of P9', 'fomu za P9' or 'vyeti vya P9'; singular otherwise ('P9', 'form P9', 'fomu ya P9')."""
    pre, post = (m.group(1) or "").strip().lower(), (m.group(2) or "").strip().lower()
    plural = post == "forms" or pre.startswith("forms") or pre.endswith(("za", "vya"))
    return "vyeti vya zuio (withholding certificates)" if plural else "cheti cha zuio (withholding certificate)"


# ---- D-FIDELITY-32 (2026-11-24, founder: APPROVED IN DESIGN; wire ONLY if pricing shows 0 gold flags and exports still pass -- eval/fidelity/price_d32_2026_11_24.py): MEDICINES / MEDICAL EQUIPMENT CALLED ZERO-RATED. A CONSTANT (R19), FACT PATH. WIRED 2026-11-24 (founder approved the replacement copy, CONSTANT_RESTATEMENTS["medicines_zero_rated"] = the locked fact medicines_vat_exempt).
# Specimen (live, build 37cdf9d, eval/results/followup_deploy_live_2026_11_24.json): "Dawa nyingi za binadamu ziko katika daraja la zero-rated (tozo 0%)"; "vifaa tiba (zero-rated)". VAT Act Cap.148 R.E.2023, Schedule Part I "SUPPLIES AND IMPORTS EXEMPT FROM VALUE ADDED TAX", item 7: essential human and
#   veterinary medicine, drugs, medical equipment and packaging approved by the Minister are EXEMPT. s.5(3): a supply both exempt and zero-rated is zero-rated (so exported medicines ARE zero-rated: that sentence is lawful).
# R25. (1) Defect: one live question, three live replies. (2) What CORRECT output could it damage: "dawa si zero-rated" (negation); "mauzo ya nje ni zero-rated; dawa ni msamaha" (the two words sit in DIFFERENT clauses); any sentence about exported/export medicines (zero-rated by s.5(3)+s.55). Vetoed by a negation cue in the clause, by clause scope, and by an export cue.
_D32_MED = re.compile(r"(?<![a-z])(?:dawa|madawa|medicines?|drugs?|pharmaceuticals?|vifaa\s+tiba|medical\s+(?:equipment|supplies|devices))(?![a-z])", re.IGNORECASE)
_D32_ZERO = re.compile(r"zero[\s-]*rat(?:ed|ing|e)|daraja\s+la\s+(?:zero|0)|tozo\s+(?:la\s+)?(?:0|sifuri)\s*%|(?<![\d.,])0\s*%|asilimia\s+(?:0|sifuri)(?![\d.,])", re.IGNORECASE)
_D32_CLAUSE = re.compile(r"[;:]|\s+(?:wakati|ilhali|lakini|ila|while|but|whereas)\s+")   # NOT brackets: "vifaa tiba (zero-rated)" is the live form, an apposition inside one clause
_D32_NEG = re.compile(r"(?<![a-z])(?:si|siyo|sio|haziko|haiko|hazina|haina|hakuna|not|no|never|isipokuwa)(?![a-z])|haziwi|hazitozwi\s+0|sivyo", re.IGNORECASE)
_D32_EXPORT = re.compile(r"nje\s+ya\s+nchi|zinazouzwa\s+nje|zinazosafirishwa|usafirishaji|export|mauzo\s+ya\s+nje|kuuza\s+nje", re.IGNORECASE)


# 2026-11-25 (founder, queued from the live miss of build ff68073): THE NEGATION MUST GOVERN THE ZERO-RATED TOKEN, NOT THE WHOLE CLAUSE. The live reply "Dawa zinaweza kuwa zero-rated (msamaha wa VAT) au exempt (si zero-rated)." carries a NEGATED zero-rated ("(si zero-rated)") AND an ASSERTED one
# ("kuwa zero-rated"); the old rule vetoed the clause on any negation cue and let the wrong half through (eval/results/two_routes_deploy_live_2026_11_25.json). Now: every zero-rate token in the clause is judged on its OWN preceding 28 characters, and the clause is flagged if ANY token lacks an adjacent negation.
# R25 (2): what correct output could it damage: "dawa si zero-rated", "dawa si za zero-rated", "Medicine is exempt, not zero-rated", "dawa hazitozwi 0%" (each token negated ADJACENTLY), the contrast and export sentences (unchanged vetoes). "sivyo" / "isipokuwa" still veto the clause (a premise or an exception, not an assertion).
_D32_NEG_ADJ = re.compile(r"(?<![a-z])(?:si|siyo|sio|not|no|never|wala|nor|haiko|haziko|hazina|haina|hakuna|haziwi|hazitozwi|haitozwi)(?![a-z])(?:\s+(?:ni|za|kwa|kuwa|katika|a|an|the|daraja|la))*[\s,(\-]*$", re.IGNORECASE)
_D32_CLAUSE_VETO = re.compile(r"sivyo|isipokuwa", re.IGNORECASE)


def _d32_asserted_zero(clause: str):
    return [m for m in _D32_ZERO.finditer(clause) if not _D32_NEG_ADJ.search(clause[max(0, m.start() - 28):m.start()])]


def medicines_called_zero_rated(question: str, body: str):
    """[sentence] in which a medicine/medical-equipment word and an UNNEGATED zero-rate token share one CLAUSE (negation is judged per token, adjacent), with no export cue in that clause."""
    out = []
    for s in _SENTENCE_SPLIT.split(body or ""):
        if not s:
            continue
        for clause in _D32_CLAUSE.split(s):
            if clause and _D32_MED.search(clause) and not _D32_CLAUSE_VETO.search(clause) and not _D32_EXPORT.search(clause) and _d32_asserted_zero(clause):
                out.append(s.strip())
                break
    return out


# ---- D-FIDELITY-33 (2026-11-25, founder, queued from the live reply "Dawa za TZS 5,000,000 nimeuza, VAT ni ngapi?" -> "kiwango cha VAT ni 18%"): MEDICINES TAXED AT THE STANDARD RATE, OR A VAT AMOUNT COMPUTED ON A MEDICINES AMOUNT. A CONSTANT (R19), FACT PATH.
# VAT Act Cap.148 R.E.2023 Schedule Part I item 7: approved medicine, drugs and medical equipment are EXEMPT: no VAT is charged, so neither "18%" nor a shillings VAT amount is ever the answer. REPLACED by the medicines statement (the D-FIDELITY-32 copy).
# A sentence is flagged when it states the STANDARD RATE (18% / "asilimia 18" / "kiwango cha kawaida") or, where the QUESTION names a medicine and VAT, a shillings figure attached to VAT, AND the medicines are the subject (a medicine word in the sentence, or in the question), AND the sentence carries no exemption / contrast / negation / export cue.
# R25 (2): what correct output could it damage: "VAT ya kawaida ni 18%, lakini dawa ni msamaha" (contrast), "dawa hazitozwi VAT" (exempt), "dawa si 18%", an export sentence, and an 18% sentence in a reply to a question that is NOT about medicines (the question context is required).
_D33_STD = re.compile(r"(?<![\d.,])18\s*%|asilimia\s+(?:ya\s+)?18(?![\d,]|\.\d)|(?<![\d.,])18\s+percent|standard\s+rate|kiwango\s+cha\s+kawaida", re.IGNORECASE)
_D33_VAT_AMOUNT = re.compile(r"(?<![a-z])vat(?![a-z])\s*(?:yote|yake|yako|ya\s+dawa|hiyo)?\s*(?:itakuwa|inakuwa|inayolipwa|inatozwa|ni|ya|=|:)\s*(?:tzs|shilingi)\s*\d[\d,.]*", re.IGNORECASE)   # a VAT figure STATED AS CHARGED; a registration threshold ("mauzo ya TZS 200M ... linasajili VAT", the live pharmacy reply's first sentence) is NOT an amount of VAT (the plant that found this overbreadth: tests/test_medicines_guards_2026_11_25.py)
_D33_SAFE = re.compile(r"msamaha|exempt|zimesamehewa|isipokuwa|lakini|ila(?![a-z])|but(?![a-z])|sajili|usajili|register|kizingiti|threshold|(?<![a-z])(?:si|siyo|sio|not|no|never|hakuna|hazitozwi|haitozwi|haziwi)(?![a-z])|wala|bila", re.IGNORECASE)
_D33_VAT = re.compile(r"(?<![a-z])vat(?![a-z])|ongezeko\s+la\s+thamani", re.IGNORECASE)


def medicines_taxed_at_standard_rate(question: str, body: str):
    """[sentence] that taxes medicines at the standard rate or computes a VAT amount on them. Needs the QUESTION (an 18% sentence about another good is correct)."""
    q_meds = bool(_D32_MED.search(question or "") and _D33_VAT.search(question or ""))
    out = []
    for s in _SENTENCE_SPLIT.split(body or ""):
        if not s or _D33_SAFE.search(s) or _D32_EXPORT.search(s):
            continue
        subject = bool(_D32_MED.search(s)) or q_meds
        if not subject or not (_D33_VAT.search(s) or q_meds):
            continue
        if _D33_STD.search(s) or (q_meds and _D33_VAT_AMOUNT.search(s)):
            out.append(s.strip())
    return out



# ---- D-FIDELITY-34 (2026-11-25, founder: INTERIM, ship first): A FOREIGN / EXPATRIATE EMPLOYEE TIED TO THE 15% RATE. A CONSTANT (R19), FACT PATH. REPLACED by a short HOLDING LINE (the cohort is supervised).
# Specimen (live, build 16f0a43, eval/results/five_fixes_deploy_live_2026_11_25.json): "A foreigner working as an employee pays a flat rate of 15% on their gross employment income. This is because they don't have residence status for progressive taxation."
# Income Tax Act Cap.332 R.E.2023, read directly 2026-11-25 (assert_edition): residence of an individual (s.86(1), [s.66] in R.E.2015) is a test of a PERMANENT HOME, PRESENCE (183 days, or an average of more than 122 days over three years) or Government posting abroad: citizenship and being a foreigner appear NOWHERE in it;
#   the 15% is the rate for a NON-RESIDENT withholdee (First Schedule para 4(a)(ii)). So foreign != non-resident, and a foreigner resident in Tanzania is taxed on the bands.
# R25. (1) Defect: one live reply (the question is the model path's, because the paye_rate route correctly vetoes foreign/citizen questions: the statement cannot answer residency). (2) What CORRECT output could it damage: any sentence that names a residency word (mkazi, asiye mkazi, non-resident, resident, ukazi, 183 days) is a correct tie of 15% to RESIDENCY and is never flagged;
#   a negated 15% ("hawalipi 15%") is a mention; a 15% sentence in a reply to a question that does not name a foreign status; a 15% sentence with no PAYE / employment word in a reply to a foreign question (e.g. a dividend rate).
_D34_FOREIGN = re.compile(r"(?<![a-z])(?:foreign(?:er|ers)?|expat(?:riate)?s?|mgeni|wageni|kigeni|raia\s+wa\s+kigeni|non-?citizens?)(?![a-z])", re.IGNORECASE)
_D34_RESIDENCY = re.compile(r"asiye\s+mkazi|asiye\s+mkaazi|wasio\s+wakazi|non-?resident|(?<![a-z])mkazi|(?<![a-z])mkaazi|wakazi|(?<![a-z])resident|ukazi|ukaazi|kikodi|residen(?:ce|cy)|makazi|siku\s+183|183\s+days", re.IGNORECASE)
_D34_FIFTEEN = re.compile(r"(?<![\d.,])15\s*%|asilimia\s+(?:ya\s+)?15(?![\d,]|\.\d)|fifteen\s+percent|(?<![a-z])flat(?:\s+rate)?(?![a-z])|tambarare", re.IGNORECASE)
_D34_PAYE_Q = re.compile(r"(?<![a-z])paye(?![a-z])|kodi\s+ya\s+mapato|income\s+tax|mshahara|salary|employee|mfanyakazi|ajira|employment", re.IGNORECASE)


_D34_NEG = re.compile(r"(?<![a-z])(?:hawalipi|halipi|hailipi|hawatozwi|hatozwi|hawana|hana|do(?:es)?\s+not|don't|doesn't|never)(?![a-z])(?:\s+[a-z']+){0,3}[\s,(\-]*(?:kiwango\s+cha\s+)?$", re.IGNORECASE)   # the Swahili / English negative VERB forms the shared adjacency cue (si, not, wala ...) does not carry


# NARROWED 2026-11-25 BY THE PRICING (every flag was read): (a) a sentence about ANOTHER 15% withholding (director's fees, dividends, royalties, software, service fees: ITA First Schedule para 4) is not the employment rate; (b) a QUESTION that already carries a residency word ("mgeni (non-resident)") has framed residency itself;
# (c) a sentence whose NEIGHBOUR (the one before it) carries the residency word is the continuation of a residency-tied answer ("Mfanyakazi asiye mkazi ... analipa PAYE tofauti: Kiwango: asilimia 15 ..."). The live specimen has none of the three.
_D34_OTHER_WHT = re.compile(r"director|mkurugenzi|ada\s+ya|(?<![a-z])fees?(?![a-z])|gawio|dividend|royalt|software|service\s+fee|(?<![a-z])wht(?![a-z])|zuio|withholding|riba|interest|rent|kodi\s+ya\s+pango", re.IGNORECASE)


def foreign_status_tied_to_15pct(question: str, body: str):
    """[sentence] that ties a foreign / expatriate status to the 15% (or 'flat') rate without a residency word."""
    if _D34_RESIDENCY.search(question or ""):
        return []
    q_foreign = bool(_D34_FOREIGN.search(question or "") and _D34_PAYE_Q.search(question or ""))
    out, prev = [], ""
    for s in _SENTENCE_SPLIT.split(body or ""):
        if not s:
            continue
        before, prev = prev, s
        if _D34_RESIDENCY.search(s) or _D34_RESIDENCY.search(before) or _D34_OTHER_WHT.search(s):
            continue
        neg = lambda m: bool(_D32_NEG_ADJ.search(s[max(0, m.start() - 28):m.start()]) or _D34_NEG.search(s[max(0, m.start() - 28):m.start()]))   # noqa: E731
        allm = list(_D34_FIFTEEN.finditer(s))
        figs = [m for m in allm if not re.match(r"(?i)flat|tambarare", m.group(0))]
        toks = [m for m in (figs or allm) if not neg(m)]      # the FIGURE is judged when there is one; "flat" / "tambarare" are only its qualifiers
        if not toks:
            continue
        if _D34_FOREIGN.search(s) or (q_foreign and _D34_PAYE_Q.search(s)):
            out.append(s.strip())
    return out


# ---- OUT-OF-COUNTRY QUESTIONS NEVER NAME A FOREIGN AUTHORITY OR URL (2026-11-25, founder). A REPAIR: ONE SENTENCE is replaced, nothing else changes. R25.
# Specimen (live, build 16f0a43): the right refusal about Kenya, then "Kwa taarifa za kodi za Kenya, thibitisha na TRA (tra.go.ke) au mshauri wa kodi wa Kenya." TRA is TANZANIA's authority and tra.go.ke does not exist; Kenya's is the KRA. (CLAUDE.md R25 already records the .go.ke lesson.)
# Replaced sentence: any sentence that carries a FOREIGN DOMAIN (always), or, when the QUESTION names another country, a foreign authority NAME or a "confirm with TRA" tied to that country. The replacement names nobody: "wasiliana na mamlaka ya kodi ya nchi husika."
# (2) What CORRECT output could it damage: Tanzanian questions (no foreign country in the question) keep naming TRA and every Tanzanian URL; "Kenyan (KRA)" in the P9 explanation (D-FIDELITY-30's own copy) has NO foreign country in the question and no foreign domain, so it stays; a sentence that names Tanzania / Bara is a comparison and is left alone.
_FA_COUNTRY = re.compile(r"(?<![a-z])(?:kenya|uganda|rwanda|burundi|zambia|malawi|msumbiji|mozambique|nigeria|ghana|ethiopia|afrika\s+kusini|south\s+africa|uingereza|marekani)(?![a-z])", re.IGNORECASE)
_FA_DOMAIN = re.compile(r"[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:go\.(?:ke|ug|rw|zm|mw|mz)|gov\.(?:za|rw|zm|ng|gh|uk|in|et))(?![a-z])", re.IGNORECASE)
_FA_NAME = re.compile(r"(?<![a-z])(?:kra|ura|rra|sars|zra|hmrc|irs|kenya\s+revenue\s+authority|uganda\s+revenue\s+authority|rwanda\s+revenue\s+authority|south\s+african\s+revenue\s+service|zambia\s+revenue\s+authority)(?![a-z])", re.IGNORECASE)
_FA_CONFIRM_TRA = re.compile(r"(?:thibitisha|wasiliana|angalia|uliza|confirm|contact|check)[^.?!]{0,60}(?<![a-z])tra(?![a-z])|(?<![a-z])tra(?![a-z])[^.?!]{0,30}\(?\s*tra\.go", re.IGNORECASE)
_FA_TANZANIA = re.compile(r"tanzania|(?<![a-z])bara(?![a-z])|tra\.go\.tz", re.IGNORECASE)
FOREIGN_AUTHORITY_LINE = "Kwa taarifa hizo, wasiliana na mamlaka ya kodi ya nchi husika."


def foreign_authority_sentences(question: str, body: str):
    q_country = bool(_FA_COUNTRY.search(question or ""))
    out = []
    for s in _SENTENCE_SPLIT.split(body or ""):
        if not s:
            continue
        s_country = bool(_FA_COUNTRY.search(s))
        # NARROWED 2026-11-25 BY THE PRICING: four GOLD answers ("Thibitisha na TRA.") answer questions that mention Kenya only incidentally (Kenyan shillings, a P9 comparison) about a TANZANIAN obligation. "Confirm with TRA" is wrong only when the SAME SENTENCE names the foreign country.
        if _FA_DOMAIN.search(s) or (not _FA_TANZANIA.search(s) and ((_FA_NAME.search(s) and (q_country or s_country)) or (_FA_CONFIRM_TRA.search(s) and s_country))):
            out.append(s)
    return out


def repair_foreign_authority(question: str, body: str) -> str:
    """Each sentence that names a foreign authority / URL (see the R25 block above) is replaced by FOREIGN_AUTHORITY_LINE, once."""
    bad = foreign_authority_sentences(question, body)
    if not bad:
        return body
    out, seen = body, False
    for s in bad:
        out = out.replace(s, FOREIGN_AUTHORITY_LINE if not seen else "", 1)
        seen = True
    return re.sub(r"[ \t]{2,}", " ", out).strip()


def body_contradicts_d16(question: str, body: str):
    """[(topic, sentence)] -- empty when none of the three rules applies."""
    out = [("dividend_nonresident_rate", s) for s in dividend_nonresident_15_asserted(question, body)]
    out += [("corporate_return_deadline", s) for s in corporate_return_deadline_misstated(question, body)]
    out += [("severance_flat_15", s) for s in severance_flat_15_asserted(question, body)]
    out += [("brela_annual_return_deadline", s) for s in brela_annual_return_deadline_misstated(question, body)]   # D-FIDELITY-20
    out += [("vat_withholding_start_date", s) for s in vat_withholding_start_misstated(question, body)]   # D-FIDELITY-22
    out += [("gn605a_mining_subsector_count", s) for s in gn605a_subsector_count_misstated(question, body)]   # D-FIDELITY-23
    out += [("gn605a_mining_wage", s) for s in mining_wage_misattributed(question, body)]   # D-FIDELITY-24
    out += [("sdl_applies_at_threshold", s) for s in sdl_denied_above_threshold(question, body)]   # D-FIDELITY-25
    out += [("sdl_scope_by_premises", s) for s in sdl_scope_by_premises(question, body)]   # D-FIDELITY-27
    out += [("nssf_contributions_age_60", s) for s in nssf_contributions_tied_to_age_60(question, body)]   # D-FIDELITY-28
    out += [("nssf_payment_deadline", s) for s in nssf_deadline_misstated(question, body)]   # D-FIDELITY-29
    out += [("medicines_zero_rated", s) for s in medicines_called_zero_rated(question, body)]   # D-FIDELITY-32 (WIRED 2026-11-24 after pricing: 0 gold flags, 0 index flags)
    out += [("medicines_taxed", s) for s in medicines_taxed_at_standard_rate(question, body)]   # D-FIDELITY-33 (2026-11-25): medicines at 18% / a VAT amount on a medicines amount
    out += [("foreign_15pct", s) for s in foreign_status_tied_to_15pct(question, body)]   # D-FIDELITY-34 (2026-11-25, interim): a foreign / expatriate status tied to the 15% rate
    return out


# ---- TWO REPAIRS (one clause changes, nothing is blocked; the D-FIDELITY-14 posture). R25's two questions, answered at the site:
# GN 605A ISSUER.  1. Defect: a live reply said the table was "lililotolewa na PKF Eastern Africa" (eval/results/np_batch_deploy_live_2026_11_17.json). GN 605A is the Labour Institutions (Minimum Wage for Private
#   Sector) Order, 2025 -- published in Special Supplement 9, 13 Oct 2025; it names no consultancy. "PKF" appears in NO served index row, so no index edit reaches it. 2. What correct output could it damage? Only a sentence
#   that says PKF ISSUED/PUBLISHED/PREPARED something about GN 605A; "kulingana na uchambuzi wa PKF" (an analysis cited as such) is not an issuer verb and is untouched, as is any sentence not about GN 605A.
# LICENCE AUTHORITY.  1. Defect: s2_07 told an ordinary trader to "Thibitisha na BRELA (brela.go.tz)" for a business licence. The Act delegates the choice of licensing authority to a Gazette order (not located); BRELA's
#   own newsletter says BRELA issues Category A licences (national / international businesses, since 1 July 2017) and councils issue Category B. So a lone BRELA citation is right for one class and wrong for the ordinary
#   trader, and a lone TRA / labour / OSHA / NSSF / WCF / immigration host is wrong for both. 2. Damage: a body naming two authorities, a body that already says "halmashauri", a refusal, and a licence question that also
#   carries another topic cue are all left alone, and the rewrite is idempotent.
_D16_PKF_ISSUER_AFTER = re.compile(r"((?:lililotolewa|iliyotolewa|limetolewa|imetolewa|lilitolewa|ilitolewa|lililochapishwa|iliyochapishwa|limechapishwa|lililoandaliwa|iliyoandaliwa|issued|published|prepared)\s+(?:na|kutoka|by)\s+)PKF(?:\s+East(?:ern)?\s+Africa)?(?![a-z])", re.IGNORECASE)
_D16_PKF_ISSUER_BEFORE = re.compile(r"(?<![a-z])PKF(?:\s+East(?:ern)?\s+Africa)?(\s+(?:ilitoa|inatoa|ilichapisha|iliandaa|issued|published|prepared))", re.IGNORECASE)
# 2026-11-17: the live reply said "ilitolewa na Waziri wa Kazi, Mawasiliano na Uchukuzi (MHE. ...)": an issuer verb followed by "Waziri ..." with an office the Order does not carry. The Order's own gazette copy (kazi.go.tz, "GOVERNMENT NOTICE
# No. 605A published on 13/10/2025") is signed by "Minister of State, Prime Minister's Office - Labour, Youth, Employment and Persons with Disability" and Labour Institutions Act s.39(1) has "the Minister" make the order, so a Waziri
# phrase after an issuer verb on a GN 605A sentence is replaced by THAT office, by title only (no personal name anywhere).
_D17_GN605A_OFFICE = "Waziri wa Nchi, Ofisi ya Waziri Mkuu (Kazi, Vijana, Ajira na Watu Wenye Ulemavu)"
_D16_GN605A_MINISTER = re.compile(r"((?:lililotolewa|iliyotolewa|limetolewa|imetolewa|lilitolewa|ilitolewa|lililochapishwa|iliyochapishwa|ilitoa|inatoa|ilichapisha)\s+(?:na|kutoka)\s+)Waziri(?!\s+wa\s+Nchi,\s+Ofisi|\s+anayehusika)(?:\s+wa\s+[A-Z][a-z]+(?:(?:,|\s+na)\s+[A-Z][a-z]+)*)?(?:\s+Mkuu)?", re.IGNORECASE)
_D16_GN605A_CUE = re.compile(r"605\s*a|kima\s+cha\s+chini|minimum\s+wage", re.IGNORECASE)


def repair_gn605a_issuer(question: str, body: str) -> str:
    """The body with 'PKF' replaced by 'Serikali' where a sentence about GN 605A says PKF issued/published/prepared it; unchanged otherwise."""
    if not body:
        return body
    out = []
    for part in re.split(r"(?<=[.!?\n])", body):
        if _D16_GN605A_CUE.search(part):
            part = _D16_PKF_ISSUER_AFTER.sub(lambda m: m.group(1) + "Serikali", part)
            part = _D16_PKF_ISSUER_BEFORE.sub(lambda m: "Serikali" + m.group(1), part)
            part = _D16_GN605A_MINISTER.sub(lambda m: m.group(1) + _D17_GN605A_OFFICE, part)
        out.append(part)
    return "".join(out)


_D16_LICENCE_Q = re.compile(r"leseni\s+(?:(?:yangu|yetu|yako|yake|yao|ya|za)\s+)*(?:biashara|duka|maduka|mgahawa|saluni|kioski|genge|frem|banda|hoteli|baa)|licen[cs]e\s+ya\s+(?:biashara|duka)|business\s+licen[cs]e", re.IGNORECASE)
# 2026-11-17: the first form needed "biashara"/"duka" IMMEDIATELY after ya|yangu|za, so "Leseni yangu ya biashara" (live np_13) escaped the repair; the repeated (yangu|ya ...) group fixes it and the trade words
# a participant actually uses (mgahawa, saluni, kioski ...) are listed. A bare "leseni" stays unjudged: it is also a driving, mining or fishing licence.
_D16_LICENCE_LABEL = "halmashauri yako, au BRELA kwa kundi A"
_D16_NO_DNS_HOSTS = ("lga.go.tz", "mlywf.go.tz")
_D16_NON_LICENCE_HOSTS = ("tra.go.tz", "kazi.go.tz", "osha.go.tz", "nssf.go.tz", "wcf.go.tz", "immigration.go.tz", "lga.go.tz", "mlywf.go.tz")
# lga.go.tz and mlywf.go.tz: NO DNS RECORD (NXDOMAIN via the local resolver and 8.8.8.8 on 2026-11-17; tra.go.tz, brela.go.tz, tamisemi.go.tz resolved as controls). The model cites lga.go.tz as a licence authority in live replies.


def repair_licence_authority(question: str, body: str) -> str:
    """For a business-LICENCE question, the one citation host rewritten to 'halmashauri yako, au BRELA kwa kundi A (brela.go.tz)' when it is BRELA alone or a non-licence authority; unchanged otherwise (R25 block above)."""
    if not question or not body or not _D16_LICENCE_Q.search(question) or _AUTH_REFUSAL.search(body):
        return body
    if re.search(r"halmashauri", body, re.IGNORECASE):
        # 2026-11-17 live (build 36a5144): "Thibitisha na halmashauri husika (lga.go.tz)" kept the host that has NO DNS record, because a body that already names the council was skipped as already right. It is only already
        # right when it cites no dead host: for lga.go.tz / mlywf.go.tz the host (and its parenthesis) is removed and the council wording is left as the model wrote it.
        dead = "|".join(re.escape(h) for h in _D16_NO_DNS_HOSTS)
        fixed = re.sub(r"\s*\(\s*(?:https?://)?(?:www\.)?(?:%s)\s*\)" % dead, "", body, flags=re.IGNORECASE)
        return _drop_redundant_confirm_tail(re.sub(r"(?<![a-z0-9.-])(?:%s)(?![a-z0-9-])" % dead, "halmashauri yako", fixed, flags=re.IGNORECASE))
    if any(t[1].search(question) for t in _AUTH_TOPICS):
        return body                                       # the question carries another topic cue: ambiguous, not judged
    hosts = {m.group(1).lower() for m in _AUTH_HOST.finditer(body)}
    if len(hosts) != 1:
        return body
    host = next(iter(hosts))
    if not (host == "brela.go.tz" or host.endswith(".brela.go.tz") or any(host == h or host.endswith("." + h) for h in _D16_NON_LICENCE_HOSTS)):
        return body
    esc = re.escape(host)
    labelled = re.compile(r"(thibitisha\s+na\s+)([^().\n]{0,60}?)\(\s*(?:https?://)?(?:www\.)?" + esc + r"\s*\)", re.IGNORECASE)
    fixed, n = labelled.subn(lambda m: f"{m.group(1)}{_D16_LICENCE_LABEL} (brela.go.tz)", body)
    if n:
        return fixed
    return re.sub(r"(?<![a-z0-9.-])" + esc + r"(?![a-z0-9-])", f"{_D16_LICENCE_LABEL} (brela.go.tz)", body, flags=re.IGNORECASE)


# ---- D-FIDELITY-17 (2026-11-17, founder-approved batch from the live check of build a2e6611). TWO MORE FACT-PATH CONSTANTS/REPAIRS, plus the shared cues they need.
#
# (1) UNSUPPORTED PERSONAL NAMES. Live: "GN 605A ilitolewa na Waziri wa Kazi, Mawasiliano na Uchukuzi (MHE. George Simbachawene)" -- a minister, a ministry and a name, none in any served row (the served row says "Serikali"/an office).
#     GENERAL RULE: a personal name introduced by an honorific (MHE., Mheshimiwa, Dkt., Prof., Mr, Bw., Bi ...), or following an office-holder title (Waziri, Katibu Mkuu, Kamishna ...), or standing in a parenthesis directly after such a
#     title, is REMOVED unless that name appears in the QUESTION or in a served fact. The OFFICE stays ("Waziri wa Fedha", "Kamishna Mkuu wa TRA"): institutions, Acts and offices are never judged, only a person.
#     R25 -- the two questions at the site: (a) the defect is a fabricated, confidently stated human being in a compliance answer; no index edit reaches it (the row names no person). (b) What CORRECT output could it damage? A person the
#     asker named (kept: the question is in the supported text); a person a served fact names (kept); an institution or Act whose name is capitalised ("Mamlaka ya Mapato Tanzania", "Sheria ya Kodi ya Mapato"); an office by title
#     ("Kamishna Mkuu wa TRA", "Waziri wa Fedha", "Rais wa Jamhuri"): none carries an honorific+name or a title followed by a capitalised given name, so none is touched. The probes hold each.
_NAME_WORD = r"[A-Z][a-z]{1,}(?:['’-][A-Za-z]+)*"
_HONORIFIC = r"(?:MHE\.?|Mhe\.?|Mheshimiwa|Dkt\.?|Dr\.?|Prof\.?|Mr\.?|Mrs\.?|Ms\.?|Bw\.?|Bwana|Bi\.?|Bibi|Ndugu|Mzee)"
_OFFICE_ONLY = (r"(?:Waziri\s+Mkuu|Naibu\s+Waziri(?:\s+wa\s+[A-Z][a-z]+(?:\s+na\s+[A-Z][a-z]+)*)?|Waziri(?:\s+wa\s+[A-Z][a-z]+(?:\s+na\s+[A-Z][a-z]+)*)?|Katibu\s+Mkuu|Kamishna\s+Mkuu|Kamishna|"
                r"Mkurugenzi\s+Mkuu|Mkurugenzi|Rais|Gavana|Mwenyekiti)")
_NAME_AFTER_HONORIFIC = re.compile(rf"(?<![A-Za-z])({_HONORIFIC})\s+({_NAME_WORD}(?:\s+{_NAME_WORD}){{0,2}})")
_NAME_AFTER_OFFICE = re.compile(rf"(?<![A-Za-z])({_OFFICE_ONLY})(\s+wa\s+[A-Z]{{2,6}})?\s+({_NAME_WORD}(?:\s+{_NAME_WORD}){{1,2}})(?![a-z])")
_NAME_PAREN = re.compile(rf"\s*\(\s*(?:{_HONORIFIC}\s*)?({_NAME_WORD}(?:\s+{_NAME_WORD}){{1,2}})\s*\)")
_OFFICE_WORD = re.compile(r"(?:Waziri|Katibu|Kamishna|Mkurugenzi|Rais|Gavana|Mwenyekiti|Naibu)")


# Capitalised words that are PART OF AN OFFICE OR INSTITUTION, never of a person: "Mkurugenzi Mtendaji Mkuu wa WCF", "Mkaguzi Mkuu", "Mamlaka ya Mapato" must not be read as an office followed by a given name (priced on 8,758
# training pairs: "Mkurugenzi Mtendaji Mkuu" was the one false positive of the first form).
_NAME_STOP = frozenset(w.casefold() for w in (
    "Mkuu", "Mtendaji", "Msaidizi", "Mkaguzi", "Msimamizi", "Mkurugenzi", "Mwandamizi", "Mdhibiti", "Naibu", "Katibu", "Waziri", "Rais", "Mwenyekiti", "Kamishna", "Gavana", "Mamlaka", "Wakala", "Ofisi", "Idara", "Wizara",
    "Bodi", "Mfuko", "Benki", "Tume", "Serikali", "Jamhuri", "Muungano", "Tanzania", "Afrika", "Mashariki", "Kuu", "Taifa", "Bunge", "Mahakama", "Halmashauri", "Manispaa", "Jiji", "Wilaya", "Mkoa", "Kazi", "Fedha", "Mipango",
    "Mapato", "Biashara", "Viwanda", "Uwekezaji", "Sheria", "Kodi", "Usajili", "Leseni", "Hifadhi", "Jamii", "Fidia", "Wafanyakazi", "Usalama", "Afya", "Ajira", "Vijana", "Ulemavu", "Wenye", "Watu", "Dar", "Salaam", "Dodoma",
    "Arusha", "Mwanza", "Zanzibar", "Tunduma", "Moshi", "Mbeya", "Tanga", "Mtwara", "Kampuni", "Shirika", "Chama", "Baraza", "Kamati", "Kitengo", "Kurugenzi", "Sekretarieti"))


def _looks_like_a_person(name):
    """False when any word of `name` is an office/institution/place word (the stoplist above)."""
    return not any(w.casefold() in _NAME_STOP for w in re.findall(r"[A-Za-z]+", name))


def _name_supported(name, supported):
    return name.casefold() in (supported or "").casefold()


def strip_unsupported_names(body, question="", supported=""):
    """(new_body, [removed names]): every personal name in `body` that is NOT in `question` / `supported` (the served facts) removed; offices, institutions and Acts untouched. Idempotent."""
    if not body:
        return body, []
    ctx = f"{question or ''} {supported or ''}"
    removed = []

    def drop_honorific(m):
        if not _looks_like_a_person(m.group(2)) or _name_supported(m.group(2), ctx):
            return m.group(0)
        removed.append(m.group(2))
        return ""

    def drop_after_office(m):
        if not _looks_like_a_person(m.group(3)) or _name_supported(m.group(3), ctx):
            return m.group(0)
        removed.append(m.group(3))
        return m.group(1) + (m.group(2) or "")

    out = _NAME_AFTER_HONORIFIC.sub(drop_honorific, body)

    def drop_paren(m):
        if not _OFFICE_WORD.search(out_before(m)) or not _looks_like_a_person(m.group(1)) or _name_supported(m.group(1), ctx):
            return m.group(0)
        removed.append(m.group(1))
        return ""

    def out_before(m):
        return cur[max(0, m.start() - 90):m.start()].split(".")[-1]

    out = _NAME_AFTER_OFFICE.sub(drop_after_office, out)
    cur = out
    out = _NAME_PAREN.sub(drop_paren, out)
    if removed:
        out = re.sub(r"\(\s*\)", "", out)
        out = re.sub(r"[ \t]{2,}", " ", out)
        out = re.sub(r"\s+([,.;:])", r"\1", out)
        # 2026-11-17 live (build 36a5144): "Waziri wa Kazi, <name>." became "Waziri wa Kazi,." and "..., <name>, katika" became "Waziri wa Kazi,, katika". The comma that introduced the name goes with it.
        out = re.sub(r",\s*(?=[.;:!?])", "", out)
        out = re.sub(r",(\s*,)+", ",", out)
    return out, removed


# (2) A LICENCE VALIDITY PERIOD other than twelve months from issuance (or the up-to-three-years prepayment option). Live: "huisha ... ndani ya siku 90 tangu tarehe ya kuomba upya". The 2026-11-17 flip of the licence rule judged
# CALENDAR DATES only; a numeric period slipped past. R19: a constant. A period is judged only in a sentence about the licence's VALIDITY (expiry / halali / dumu) -- a late-renewal PENALTY, a fee, a grace window or an application
# process is a different question and is skipped by its own cue words. Periods are normalised to months; 12 and 36 are lawful (s.7(1), s.7(2)); the asker's own numbers are mentions.
_C17_VALIDITY_S = re.compile(r"huisha|inaisha|(?<![a-z])isha(?![a-z])|halali|dumu|inadumu|validity|(?<![a-z])valid(?![a-z])|expire|muda\s+wa\s+leseni", re.IGNORECASE)
_C17_SKIP_S = re.compile(r"adhabu|faini|(?<![a-z])ada(?![a-z])|kuchelewa|kuchelewesha|penalty|(?<![a-z])fee(?![a-z])|gharama|riba|mchakato|maombi\s+yanachukua|inachukua\s+muda|kupata\s+leseni", re.IGNORECASE)
_C17_NUM = {**_WORD_NUM, "thelathini": 30, "sitini": 60, "tisini": 90, "ishirini": 20}
_C17_NUMRE = r"\d{1,3}|kumi\s+na\s+(?:moja|mbili)|" + "|".join(sorted(_C17_NUM, key=len, reverse=True))
_C17_PERIOD = re.compile(rf"(?<![\d.,])({_C17_NUMRE})\s+(siku|wiki|miezi|miaka|mwezi|mwaka|days?|weeks?|months?|years?)(?![a-z])|(?<![a-z])(siku|wiki|miezi|miaka)\s+({_C17_NUMRE})(?![\d])", re.IGNORECASE)
_C17_UNIT_MONTHS = {"siku": 1 / 30, "day": 1 / 30, "days": 1 / 30, "wiki": 1 / 4.345, "week": 1 / 4.345, "weeks": 1 / 4.345, "mwezi": 1, "miezi": 1, "month": 1, "months": 1, "mwaka": 12, "miaka": 12, "year": 12, "years": 12}
_C17_LAWFUL_MONTHS = (12, 36)


def _c17_to_number(tok):
    t = re.sub(r"\s+", " ", tok.lower().strip())
    if t.isdigit():
        return int(t)
    if t.startswith("kumi na "):
        return 10 + _C17_NUM[t.split()[-1]]
    return _C17_NUM.get(t)


def licence_validity_period_violations(question, body):
    """[reason] for a licence-validity sentence stating a period that is not twelve months (or the three-year prepayment). Empty when the question is not about a licence's expiry."""
    if not (_C13_LICENCE_Q.search(question or "") and _C13_LICENCE_Q_NEED.search(question or "")):
        return []
    qn = _c13_numbers(question)
    out = []
    for s in _SENTENCE_SPLIT.split(body or ""):
        if not (s and _C13_LICENCE_S.search(s) and _C17_VALIDITY_S.search(s)) or _C17_SKIP_S.search(s):
            continue
        for m in _C17_PERIOD.finditer(s):
            num_tok, unit = (m.group(1), m.group(2)) if m.group(1) else (m.group(4), m.group(3))
            n = _c17_to_number(num_tok)
            if n is None or n in qn or _fd10_negated(s, m.start()) or _C13_LIC_NEG.search(s[max(0, m.start() - 32):m.start()]):
                continue
            months = n * _C17_UNIT_MONTHS[unit.lower()]
            if any(abs(months - ok) < 0.5 for ok in _C17_LAWFUL_MONTHS):
                continue
            out.append(f"licence/validity-period:{n} {unit.lower()}")
    return out


# ---- D-FIDELITY-18 (2026-11-17, founder's next small batch). TWO MORE SINGLE-CLAUSE REPAIRS.
#
# (3) A PRACTITIONER FIRM NAMED AS THE AUTHORITY TO CONFIRM WITH. Live (build a2e6611 and 36a5144): "Nani alisaini GN 605A?" -> "... Thibitisha na VELMA Law au PKF Eastern Africa." D-FIDELITY-14 judges HOSTS (a *.go.tz or a firm's
#     domain written out); a firm named in WORDS, with no host, was never judged. The firms below are the practitioner-advisory family (CLAUDE.md R6 / Section 4: they are EVAL sources and cited as such, never an authority to "confirm with").
#     R25 -- the two questions at the site: (a) the defect: a consultancy offered to a Tanzanian employer as the place to verify a statutory figure -- the model learned the formulaic "Thibitisha na ..." tail from corpus rows that end that way
#     (the sibling GN 605A pairs, PROGRESS section 5). No index edit reaches it. (b) What CORRECT output could it damage? ONLY a "Thibitisha na ..." (or "kwa ...") TAIL that names a firm: an analysis cited as an analysis ("Kulingana na uchambuzi wa
#     PKF Eastern Africa, wastani ni 33.4%") is not a tail and is untouched; a tail naming a whitelisted source (TanzLII) keeps it; a tail naming a real authority (TRA, kazi.go.tz) is untouched. Only the firm items are removed from a tail;
#     what is left stays; if nothing is left the topic's authority replaces them (the D-FIDELITY-14 table), or "mamlaka husika" when the question has no single topic.
_FIRM_NAMES_CI = re.compile(r"velma(?:\s+law)?|clydeco|ey\.com|pkf(?:\s+east(?:ern)?\s+africa)?|bowmans?|clyde\s*(?:&|and)\s*co\.?|kpmg|ernst\s*(?:&|and)\s*young|pwc|pricewaterhouse\s*coopers|deloitte|dentons|dla\s+piper|habib\s+advisory", re.IGNORECASE)
_FIRM_EY = re.compile(r"(?<![A-Za-z])EY(?![A-Za-z])")
# the tail consumes a parenthesis whole and a dotted host whole ("bowmanslaw.com"), so a full stop INSIDE a host does not end it early (the first form left ".com)." behind)
_CONFIRM_TAIL = re.compile(r"(?P<lead>thibitisha\s+(?:na|kwa)\s+)(?P<tail>(?:\([^)\n]*\)|[\w-]+(?:\.[\w-]+)+|[^.\n(])*)", re.IGNORECASE)
_TAIL_SPLIT = re.compile(r"\s+(?:au|na|and|or)\s+|\s*[,/]\s*", re.IGNORECASE)


def _names_a_firm(text):
    return bool(_FIRM_NAMES_CI.search(text) or _FIRM_EY.search(text))


def repair_firm_authority(question: str, body: str) -> str:
    """The body with a practitioner firm removed from every 'Thibitisha na ...' tail; the topic's authority (or 'mamlaka husika') when nothing legitimate is left; unchanged otherwise. Idempotent."""
    if not body or not _names_a_firm(body):
        return body
    topic = authority_topic(question)
    replacement = f"{topic[3]} ({topic[4]})" if topic else "mamlaka husika"

    def fix(m):
        tail = m.group("tail")
        if not _names_a_firm(tail):
            return m.group(0)
        items = [x.strip() for x in _TAIL_SPLIT.split(re.sub(r"\([^)]*\)", lambda g: g.group(0).replace(",", ";"), tail)) if x and x.strip()]
        kept = [x for x in items if not _names_a_firm(x)]
        kept = [x for x in kept if re.sub(r"[\s()]", "", x)]
        return m.group("lead") + (" au ".join(kept) if kept else replacement)

    return _drop_redundant_confirm_tail(_CONFIRM_TAIL.sub(fix, body))


# (4) A REPEATED "Thibitisha na X." SENTENCE. Live (build 36a5144 -> 911948b): after the dead-host repair removed "(lga.go.tz)" the reply read "Thibitisha na halmashauri husika ili kujua utaratibu sahihi wa kuitafuta upya. Thibitisha na
#     halmashauri husika." -- the model wrote one clause, the repair left it beside the formulaic tail. The LAST sentence is dropped when it is only a shorter restatement of "Thibitisha na <same target>" that an earlier sentence already carries.
def _drop_redundant_confirm_tail(body):
    parts = re.split(r"(?<=[.!?])\s+", (body or "").strip())
    if len(parts) < 2:
        return body
    last = parts[-1].strip()
    m = re.match(r"^thibitisha\s+(?:na|kwa)\s+(.+?)\s*\.?$", last, re.IGNORECASE)
    if not m:
        return body
    target = re.sub(r"\s+", " ", m.group(1).lower()).strip()
    for earlier in parts[:-1]:
        e = re.sub(r"\s+", " ", earlier.lower())
        if re.search(r"thibitisha\s+(?:na|kwa)\s+" + re.escape(target), e):
            return " ".join(parts[:-1])
    return body


# ══════════════════════════════════════════════════════════════════════════════════════════════
# D-FIDELITY-19 (2026-11-17, founder-approved): COMPARISON FIDELITY -- "A ni chini ya B" when A > B, "A ni zaidi ya B" when A < B.
#
# Founding specimen, LIVE build d644c71 (eval/results/batch3_deploy_live_2026_11_17.json): "...ni sawa na mauzo ya TZS 216,000,000 kwa mwaka. Hii ni chini ya kiwango cha milioni 200 kinachohitajika ili kusajiliwa kwa VAT."
# 216,000,000 is ABOVE 200,000,000; the model states both figures and then compares them backwards, which tells a liable business it is below the VAT threshold.
#
# R19 (constant vs derived): BOTH numbers are in the text, so this is a comparison of two stated constants -- buildable. It needs no engine result, so it works on the fact path too, where the other D-FIDELITY rules are
# vacuous. It REPAIRS (flips the comparator so the sentence is true of its own figures) and never withholds: blanking would ship silence on the fact path.
#
# R25 (written before it was wired): (1) the corpus defect repaired: one confident backwards comparison in production; priced on every stored reply, gold answer and training pair (eval/results/price_d19_2026_11_17.json).
# (2) the CORRECT output it could damage: any sentence whose comparison is TRUE is untouched by construction (it fires only when the words contradict the two stated figures). The shapes at risk are ranges and bands, which
# contain comparator words but no "A ni <comparator> B" predicate: "TZS 270,001 hadi 520,000: 8%", "zaidi ya TZS 270,000 lakini chini ya TZS 520,000", "chini ya TZS 270,000: 0%". The predicate (A, optionally a sentence break and a
# demonstrative bridge "Hii ni", then ni/iko/ipo) is REQUIRED, A must be the nearest figure before the comparator, B the first after it within five filler words, both >= TZS 10,000 (so a percentage, a count or a date is never
# compared). EQUAL figures are never flagged (the boundary is the statute's, not the model's). LIMITATION, stated: flipping the comparator makes the sentence true; a CONCLUSION elsewhere in the body that followed the wrong
# comparison ("kwa hiyo hauhitaji kusajili") is not rewritten -- the review card shows guard 'repaired'.
# ══════════════════════════════════════════════════════════════════════════════════════════════
_D19_LT = r"chini\s+ya|pungufu\s+ya|ndogo\s+kuliko|chini\s+kuliko|less\s+than|lower\s+than|below"
_D19_GT = r"zaidi\s+ya|juu\s+ya|kubwa\s+kuliko|juu\s+kuliko|more\s+than|higher\s+than|above"
_D19_CMP = re.compile(rf"(?<![A-Za-z])(?P<lt>{_D19_LT})(?![A-Za-z])|(?<![A-Za-z])(?P<gt>{_D19_GT})(?![A-Za-z])", re.IGNORECASE)
_D19_FLIP = {"chini ya": "zaidi ya", "pungufu ya": "zaidi ya", "ndogo kuliko": "kubwa kuliko", "chini kuliko": "juu kuliko", "less than": "more than", "lower than": "higher than", "below": "above",
             "zaidi ya": "chini ya", "juu ya": "chini ya", "kubwa kuliko": "ndogo kuliko", "juu kuliko": "chini kuliko", "more than": "less than", "higher than": "lower than", "above": "below"}
_D19_MONEY_FLOOR = 10_000
_D19_LEAD_TOKEN = re.compile(r"^(?:(?:milioni|bilioni|elfu|laki)\s*)?\d[\d,.]*\s*(?:milioni|bilioni|elfu|m\b|bn\b|k\b)?", re.IGNORECASE)
_D19_BRIDGE = re.compile(r"[.!?]\s+(?:Hii|Hiyo|Hiki|Hicho|Hizo|Hivyo|Kiasi\s+hiki|Kiasi\s+hicho|Jumla\s+hii)\s+(?:ni\s+|iko\s+|ipo\s+)?$", re.IGNORECASE)
_D19_PREDICATE = re.compile(r"(?:^|\s)(?:ni|iko|ipo|ziko|yako|is|are)\s+(?:bado\s+|pia\s+|tu\s+)?$", re.IGNORECASE)


def _d19_pairs(body):
    """[(cmp_match, A, B, kind)] for every 'A ni <comparator> B' whose words contradict its own figures."""
    from . import swahili_numbers as swn
    located = [(p, a) for p, a in swn.parse_amounts_located(body) if a >= _D19_MONEY_FLOOR]
    out = []
    for m in _D19_CMP.finditer(body):
        before = [(p, a) for p, a in located if p < m.start()]
        after = [(p, a) for p, a in located if p >= m.end()]
        if not before or not after:
            continue
        pa, a = before[-1]
        pb, b = after[0]
        lead = _D19_LEAD_TOKEN.match(body[pa:m.start()])
        gap = body[pa + (lead.end() if lead else 0):m.start()]
        if len(gap) > 90 or re.search(r"\d", gap):
            continue
        if not (_D19_PREDICATE.search(gap) or (_D19_BRIDGE.search(gap) and not re.search(r"[.!?;:]\s", gap[: _D19_BRIDGE.search(gap).start()] + " "))):
            continue
        mid = body[m.end():pb]
        if len(mid.split()) > 5 or re.search(r"[\d.;:?!]", mid):
            continue
        kind = "lt" if m.group("lt") else "gt"
        if (kind == "lt" and a > b) or (kind == "gt" and a < b):
            out.append((m, a, b, kind))
    return out


def comparison_violations(body: str):
    """[(A, B, comparator_text)] for each backwards comparison between two stated figures; [] when none. Pure, idempotent after repair."""
    return [(a, b, m.group(0)) for m, a, b, _ in _d19_pairs(body or "")]


def repair_comparisons(body: str) -> str:
    """The body with each backwards comparator flipped so the sentence is true of its own two figures; unchanged when there is none."""
    if not body:
        return body
    hits = _d19_pairs(body)
    for m, _a, _b, _k in sorted(hits, key=lambda h: -h[0].start()):
        word = m.group(0)
        flipped = _D19_FLIP[re.sub(r"\s+", " ", word.lower())]
        if word[:1].isupper():
            flipped = flipped[:1].upper() + flipped[1:]
        body = body[:m.start()] + flipped + body[m.end():]
    return body


# ---- D-FIDELITY-21 (2026-11-17, founder-approved, item 5 of the batch after the targeted verification): THE GN 605A SECTOR COUNT. A CONSTANT (R19), A ONE-TOKEN REPAIR.
#   specimen (live, build e9e429e, eval_117): "GN 605A inashughulikia sekta 15 na sekta ndogo 46 za mishahara ya chini."   (judge wrong 5/5; the baseline said 16)
#   the Order (kazi.go.tz official copy, GN No. 605A, 13/10/2025, edition asserted, read 2026-11-17): the FIRST SCHEDULE lists exactly SIXTEEN sectors and areas, the sixteenth being "Other sectors or areas not specified in this Order".
#   NOT guarded: the "46 sub-sectors". It is PKF's figure and the Order does not settle it mechanically: counting its lettered rows gives 44, or 48 if a sector with a single row counts once, depending on what a "sub-sector" is.
# R25. (1) Defect: a confident wrong count on the model path (the fact "16 sectors" is served; the model's reply still said 15). (2) What CORRECT output could it damage: only a sentence that carries "sekta N" / "N sectors" with N != 16
#   for a question that asks how many sectors GN 605A covers; a NEGATION ("si sekta 15") is left alone (rewriting its number would turn a denial into a falsehood), a sentence that already says 16 is untouched, "sekta ndogo N" (sub-sectors)
#   is never matched, and any question that is not about the GN 605A sector count is untouched. The repair changes ONE number and blocks nothing; idempotent.
_D21_Q = re.compile(r"(?=.*(?:605\s*a|mshahara\s+wa\s+chini|minimum\s+wage))(?=.*(?:sekta\s+ngapi|ngapi\s+za\s+sekta|idadi\s+ya\s+sekta|sekta\s+zote\s+ni\s+ngapi|sekta\s+zipi\s+na\s+ngapi|how\s+many\s+(?:main\s+)?sectors|number\s+of\s+sectors))", re.IGNORECASE | re.DOTALL)   # the QUESTION must ask for the NUMBER OF SECTORS: "mshahara wa chini wa sekta ya madini ni ngapi?" asks for a wage and a reply's "sekta 10" there is the mining sector's NUMBER
_D21_COUNT = re.compile(r"(?<![a-z])(sekta\s+)(\d{1,2})(?![\d,.]|\s+ndogo)|(?<![\d,.])(\d{1,2})(\s+(?:sekta|sectors?)(?![a-z]*\s+ndogo))", re.IGNORECASE)
_D21_SECTORS = 16


def repair_gn605a_sector_count(question: str, body: str) -> str:
    """The body with a wrong GN 605A SECTOR count corrected to 16 where the question asks for it; unchanged otherwise."""
    if not body or not _D21_Q.search(question or ""):
        return body

    def fix(m):
        n = int(m.group(2) or m.group(3))
        if n == _D21_SECTORS or n < 1 or n > 40:
            return m.group(0)
        return (m.group(1) + str(_D21_SECTORS)) if m.group(2) else (str(_D21_SECTORS) + m.group(4))
    out = []
    for part in re.split(r"(?<=[.!?\n])", body):
        out.append(part if _D16_NEG.search(part) else _D21_COUNT.sub(fix, part))
    return "".join(out)



# ── D-FIDELITY-26 (2026-11-22, founder): A FIGURE ATTACHED TO NHIF IS REMOVED -- WE HOLD NO NHIF RATE ────────────────────────────────────────────────────────────────────
# NHIF (the National Health Insurance Fund) is OUT OF SCOPE (the 2026-11-22 OOC additions refuse the verb-qualified forms) and NO locked fact holds an NHIF rate or amount. So ANY percentage or amount a reply attaches to NHIF is unsupported by
# construction -- there is no served fact it could be copied from. Founding specimen, LIVE: the mixed question "NSSF na NHIF -- ni mifumo tofauti au moja?" (correctly NOT refused: it compares two schemes) was answered "NHIF: ... (asilimia 0.5
# mwajiri + asilimia 10 mfanyakazi)" -- WCF's 0.5 and NSSF's 10 attributed to NHIF. The unsupported-figure FLAG cannot see it (both numbers are served, for OTHER subjects: its recorded subject-blindness), so this is a constant rule about a SUBJECT.
#
# R25, in writing at the site. (1) WHAT DEFECT DOES IT REPAIR: an invented rate attributed to a scheme we do not cover; one live instance, no corpus count (the corpus holds 3 NHIF questions, none answered with a rate). (2) WHAT CORRECT OUTPUT COULD IT
# DAMAGE: any sentence that states a figure beside NHIF that is nevertheless true -- e.g. a member COUNT or a founding year written with a thousands separator. We hold no NHIF fact to say such a figure is right, and the decision is that an
# unsupported figure on an uncovered scheme is removed, not judged. A reply that mentions NHIF WITHOUT a figure is untouched, and so is every figure that belongs to ANOTHER levy in the same sentence (the unit of removal is the CLAUSE).
#
# REPAIRED, never withheld, and only the offending clause goes: the correct NSSF part of the founding reply is kept, and one sentence is appended saying NHIF is not covered. Applies to every model-written body that reaches the repair chain.
_NHIF = re.compile(r"(?<![a-z])nhif(?![a-z])", re.IGNORECASE)
_NHIF_OTHER = re.compile(r"(?<![a-z])(?:nssf|wcf|sdl|paye|vat|efd|osha|brela|tra)(?![a-z])", re.IGNORECASE)
_NHIF_FIG = re.compile(r"\d+(?:[.,]\d+)?\s*(?:%|asilimia|percent|per\s*cent)|(?:asilimia|percent)\s*\d+(?:[.,]\d+)?|(?:tzs|tsh|sh\.?|shilingi)\s*\d[\d,.]*|\d{1,3}(?:,\d{3})+|\d+\s*(?:elfu|laki|milioni)", re.IGNORECASE)
_NHIF_CLAUSE = re.compile(r"((?<=[.!?])\s+|\n+|;\s*|\s+na\s+(?=nhif|nssf|wcf|sdl|paye|vat|efd|osha|brela|tra(?![a-z]))|,\s+(?=nhif|nssf|wcf|sdl|paye|vat|efd|osha|brela|tra(?![a-z])))", re.IGNORECASE)
_NHIF_BACK = re.compile(r"(?:ya|kwa|za|wa|cha)\s*$", re.IGNORECASE)
NHIF_NOT_COVERED_NOTE = "Kuhusu NHIF: Chike haijafunika NHIF, kwa hiyo sina kiwango au kiasi chake; thibitisha moja kwa moja na NHIF."


def _nhif_figure_attached(clause: str) -> bool:
    """True when `clause` attaches a figure to NHIF: a figure AFTER the name (before any other levy's name), or one directly before it in 'figure ... ya NHIF'."""
    for m in _NHIF.finditer(clause):
        after = clause[m.end():m.end() + 100]
        other = _NHIF_OTHER.search(after)
        if _NHIF_FIG.search(after[:other.start()] if other else after):
            return True
        before = clause[max(0, m.start() - 45):m.start()]
        last = None
        for last in _NHIF_OTHER.finditer(before):
            pass
        before = before[last.end():] if last else before
        if _NHIF_BACK.search(before) and _NHIF_FIG.search(before):
            return True
    return False


def repair_nhif_figures(body: str):
    """(repaired body, [removed clauses]). Unchanged, with [], when no clause attaches a figure to NHIF."""
    if not body or not _NHIF.search(body):
        return body, []
    parts = _NHIF_CLAUSE.split(body)                       # clause, separator, clause, ... (the separator is captured)
    items = [(parts[k], parts[k + 1] if k + 1 < len(parts) else "") for k in range(0, len(parts), 2)]
    flagged = [bool(c.strip()) and _nhif_figure_attached(c) for c, _ in items]
    removed = [c.strip() for (c, _), f in zip(items, flagged) if f]
    if not removed:
        return body, []
    text, prev = "", None
    for k, ((clause, sep), f) in enumerate(zip(items, flagged)):
        if f or not clause.strip():
            continue
        if prev is not None:
            # adjacent in the original: keep ITS separator; something was removed between them: a full stop, never a dangling connector ("na", ",", ";")
            text += items[prev][1] if prev == k - 1 else (" " if text[-1:] in ".!?" else ". ")
        text += clause
        prev = k
    text = text.rstrip(" ;,\n")
    if text and text[-1] not in ".!?":
        text += "."
    if NHIF_NOT_COVERED_NOTE not in text:
        text = (text + " " if text else "") + NHIF_NOT_COVERED_NOTE
    return text, removed



# ── NHIF NAMED IN THE QUESTION: APPEND ONE LINE, NEVER REFUSE THE REST (2026-11-23, founder's decision 3) ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# Live (build d997d4d): "NHIF inakatwa asilimia ngapi pamoja na NSSF kwenye mshahara?" was answered by the NSSF engine with NSSF's employee share and NOT A WORD about NHIF -- a reader can take 10% as the NHIF rate. The NSSF part is correct and stays; the reply
# gains one line saying NHIF is not covered. Applies whenever the QUESTION names NHIF and the reply is not already a refusal (the verb-qualified NHIF forms are refused by the OOC list before this runs, unchanged). R25. (1) Defect: a silent partial answer to a
# two-scheme question. (2) What CORRECT output could it damage: none removed -- it only appends; a reply that already says NHIF is not covered (D-FIDELITY-26's note, or this line) gets no second copy; an NSSF-only question gets nothing.
NHIF_APPEND = "NHIF haijafunikwa na Chike — thibitisha na NHIF."
_NHIF_ALREADY = re.compile(r"haijafunikwa\s+na\s+chike|haijafunika\s+nhif", re.IGNORECASE)


def question_names_nhif(question: str) -> bool:
    return bool(question) and bool(_NHIF.search(question))


def append_nhif_note(question: str, text: str) -> str:
    """`text` with the NHIF-not-covered line appended when the question names NHIF and the text does not already say so; otherwise unchanged."""
    if not text or not question_names_nhif(question) or _NHIF_ALREADY.search(text):
        return text
    return text.rstrip() + "\n\n" + NHIF_APPEND

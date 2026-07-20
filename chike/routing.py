"""Router — decide COMPUTE (rules engine) vs FACT (RAG) for one sub-question, and, for
compute, WHICH levy.

Adopted from ADR 0001 Phase 0 (docs/decisions/0001-...): the embedding and broad-keyword
routers were rejected (embedding misrouted OOC questions into compute with false confidence
and was boundary-blind; broad keyword had poor precision). The validated design is
Candidate C — a deterministic lexical router that separates compute-INTENT from topic by
requiring a money 'how-much' cue together with payroll context, NOT topic words alone.

This module is the deterministic routing layer. It is a UNION of two paths:

  1. EXPLICIT path — an explicit levy identifier (sdl/nssf/paye/wcf) + a number. Preserves the
     v15/stub behaviour for tax-named questions and the 400-gate control recall (those questions
     all name their levy). High precision on named questions.

  2. NATURAL path (Candidate C) — no levy is named, so intent is inferred from the combination
     {a number} + {payroll context} + {a money 'how-much' cue}. The levy is then read off the
     generic obligation words (pensheni->nssf, ufundi->sdl, kodi ya mapato->paye, fidia->wcf);
     if the cue is generic/multi ('makato yote') the intent is 'ambiguous_multi' (compute-intent,
     specific levy unresolved -> the compute path clarifies which one).

Everything here is pure string logic — no model call, no network, no GPU — so routing is free
and fully offline-testable. The model (SlotExtractor) is consulted only AFTER a compute route,
to extract field values (unchanged). The two natural questions this deterministic layer cannot
catch (net-take-home phrasing without an explicit 'kiasi gani'; a compute question whose only
number is a Swahili number-word) are the documented residual that the extractor-emitted-intent
backstop (ADR Phase A, needs GPU) is intended to close; they are NOT silently mis-answered — they
fall through to the fact/RAG path, the same honest failure as the current stub.
"""

import re

# The four rules-engine computation types. 'ambiguous_multi' is compute-intent with an
# unresolved specific levy; 'none' means fact/RAG.
COMPUTE_TYPES = ("sdl", "nssf", "paye", "wcf")

# --- explicit identifiers (path 1) ------------------------------------------
_EXPLICIT = {
    "sdl": [r"\bsdl\b", r"skills development"],
    "nssf": [r"\bnssf\b"],
    "paye": [r"\bpaye\b", r"\bp\.?a\.?y\.?e\b"],
    "wcf": [r"\bwcf\b"],
}

# --- natural-path cues (path 2, Candidate C) --------------------------------
# Generic obligation words -> levy. Ordered so a more specific cue wins; generic
# deduction words ('makato','michango') map to ambiguous_multi, not a single levy.
_LEVY_CUES = [
    ("nssf", ["pensheni", "uzeeni", "hifadhi ya jamii", "mchango wa hifadhi",
              "mfuko wa hifadhi", "akiba ya baadaye"]),
    ("sdl", ["ufundi", "ujuzi", "mafunzo", "maendeleo ya ujuzi", "kuendeleza wafanyakazi"]),
    ("wcf", ["fidia", "bima ya ajali", "bima ya majeraha", "majeraha kazini", "ajali kazini"]),
    ("paye", ["kodi ya mapato", "kodi ya mshahara", "mapato ya ajira"]),
]
_GENERIC_LEVY = ["makato", "michango", "tozo", "malipo kwa serikali", "kulipa serikali",
                 "kwa serikali"]

# Payroll context: the question is about wages/employees (needed for a payroll levy).
_PAYROLL_CTX = ["mshahara", "mishahara", "mfanyakazi", "wafanyakazi", "waajiriwa",
                "watumishi", "analipwa", "ninalipa", "kumlipa", "ajira", "payroll", "mlipwa"]

# Money 'how-much' cue: a request for a shilling QUANTITY.
_MONEY_ASK = ["kiasi gani", "shilingi ngapi", "kinakatwa kiasi", "ni ngapi", "gharama gani"]
# Non-money quantity asks (rate / time / count) that must NOT count as a money ask.
_NONMONEY_ASK = ["asilimia ngapi", "siku ngapi", "muda gani", "miaka mingapi", "idadi gani",
                 "wangapi", "mara ngapi"]

# Swahili number words (so a compute question with no ASCII digit still counts as numeric).
_SWA_NUM = (r"\b(moja|mbili|tatu|nne|tano|sita|saba|nane|tisa|kumi|ishirini|thelathini|"
            r"arobaini|hamsini|sitini|sabini|themanini|tisini|laki|elfu|milioni|mia|robo|"
            r"nusu)\b")


# 'moja kwa moja' is the idiom "directly", not the quantity "one" — strip it before the
# number-word scan so it does not spuriously mark a question as numeric (eval_128).
_NUM_IDIOMS = re.compile(r"moja\s+kwa\s+moja", re.IGNORECASE)


def _has_number(ql: str) -> bool:
    ql = _NUM_IDIOMS.sub(" ", ql)
    return bool(re.search(r"\d", ql)) or bool(re.search(_SWA_NUM, ql))


def _has_money_ask(ql: str) -> bool:
    ask = any(c in ql for c in _MONEY_ASK)
    # A bare 'ni ngapi'/'... ngapi' that is actually a rate/time/count ask does not count,
    # unless an explicit money phrase ('kiasi gani'/'shilingi ngapi') is also present.
    if any(nm in ql for nm in _NONMONEY_ASK) and not (
            "kiasi gani" in ql or "shilingi ngapi" in ql):
        ask = False
    return ask


def _explicit_levy(ql: str):
    for levy, pats in _EXPLICIT.items():
        if any(re.search(p, ql) for p in pats):
            return levy
    return None


def _natural_levy(ql: str):
    for levy, cues in _LEVY_CUES:
        if any(c in ql for c in cues):
            return levy
    if any(g in ql for g in _GENERIC_LEVY):
        return "ambiguous_multi"
    return None


def detect_intent(text: str) -> str:
    """Return the routing intent: one of COMPUTE_TYPES, 'ambiguous_multi', or 'none'.

    'none' means route to fact/RAG. Deterministic; no model call.
    """
    ql = text.lower()

    # Path 1 — explicit levy named + a number -> that levy (preserves stub / 400 control).
    explicit = _explicit_levy(ql)
    if explicit and _has_number(ql):
        return explicit

    # Path 2 — Candidate C: number + payroll context + a money 'how-much' cue.
    if _has_number(ql) and any(c in ql for c in _PAYROLL_CTX) and _has_money_ask(ql):
        return _natural_levy(ql) or "ambiguous_multi"

    return "none"


def invoke_extractor(text: str) -> bool:
    """Recall-biased gate (ADR Phase A): should the extractor-intent backstop be consulted
    when the deterministic router abstained (detect_intent == 'none')?

    True when the question carries a PAYROLL compute signal — a number OR payroll context.
    A money 'how-much' cue is deliberately NOT sufficient on its own: a money question with
    no payroll context (e.g. 'BRELA ada ni ngapi' — a fixed-fee lookup) can never be a
    payroll-levy computation, so escalating it would spend a model call that always returns
    'none'. Number-or-payroll still catches the deterministic layer's residual misses
    (rc_11: payroll+number; rc_22: payroll) while skipping non-payroll fee/definition
    questions. (Refinement found during Phase A wiring; see ADR 0001 s8.)"""
    ql = text.lower()
    return _has_number(ql) or any(c in ql for c in _PAYROLL_CTX)

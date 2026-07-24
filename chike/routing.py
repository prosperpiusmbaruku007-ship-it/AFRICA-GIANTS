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
     specific levy unresolved -> the compute path clarifies which one). If NO levy/obligation
     word is present at all, the {number + payroll + money-ask} combination is not treated as
     compute-intent (the number may be incidental, e.g. a gazette 'GN 605A') -> fact/RAG.

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
# Net-take-home phrasing ("what remains in hand after tax") — a money 'how-much' request
# that never uses an explicit 'kiasi gani'. rc_11's phrasing; caught here so a net-of-PAYE
# question routes to compute deterministically (this is the residual the retired
# extractor-emitted-intent backstop unreliably targeted — now a fixed lexical rule).
_TAKEHOME_ASK = ["kitakachobaki", "kinachobaki", "mkononi", "baada ya kodi", "nitabaki na"]

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
    # Net-take-home phrasing is a money 'how-much' request even with no explicit 'kiasi gani'.
    if any(t in ql for t in _TAKEHOME_ASK):
        ask = True
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
    # Only a compute route when _natural_levy actually resolves a levy — a specific one,
    # OR 'ambiguous_multi' via a generic obligation word ('makato yote'/'michango'). A bare
    # {digit + payroll word + money-ask} with NO levy/obligation word is NOT compute-intent:
    # the digit may be incidental (e.g. '605' in 'GN 605A', a pure fact lookup) or the ask a
    # non-levy custom split ('mgao wa 15%'). Those fall through to fact/RAG rather than emitting
    # a spurious 'which levy?' clarification.
    if _has_number(ql) and any(c in ql for c in _PAYROLL_CTX) and _has_money_ask(ql):
        natural = _natural_levy(ql)
        if natural:
            return natural

    return "none"


# Obligation/threshold cues: the question asks WHETHER a levy applies (am I obligated /
# do I reach the threshold), not HOW MUCH. Multi-word to avoid matching bare 'kulipa' in
# deadline/mechanism facts ('deadline ya kulipa michango', 'zinalipwa TRA siku ya 7').
_APPLICABILITY_CUES = [
    "wajibu wa kulipa", "nawajibika kulipa", "nalazimika kulipa", "lazima nilipe",
    "lazima kulipa", "inatakiwa kulipwa", "nafikia kizingiti", "fikia kizingiti",
    "haitakiwi kulipa", "nachangia",
]


# Ordinal-hire / threshold-crossing phrasing ('ninaajiri mfanyakazi wa 10 katikati ya
# mwezi') — the headcount CHANGES over the period, so a static count-vs-threshold check
# would assert a possibly-wrong verdict (eval_124: reads '9', but hiring the 10th makes SDL
# due). Never-guess (R8): decline the deterministic shortcut here and let the amount path
# clarify, rather than assert 'haihusiki' on a count that is actually crossing the threshold.
_COUNT_TRANSITION = re.compile(r"mfanyakazi\s+wa\s+\d+")


def is_applicability_question(text: str) -> bool:
    """True when a levy question asks WHETHER the obligation applies (yes/no) AND a static
    headcount/flat-rule check can answer it — an obligation/threshold cue is present, there
    is NO money 'how-much' ask, and the count is not mid-transition (Finding 1). The
    orchestrator gates the levy type (sdl/nssf/wcf) separately; PAYE applicability needs a
    salary, so it stays on the amount path. Pure string logic."""
    ql = text.lower()
    if _has_money_ask(ql):
        return False
    if _COUNT_TRANSITION.search(ql):
        return False
    return any(cue in ql for cue in _APPLICABILITY_CUES)


def is_uncomputable_payroll_amount(text: str) -> bool:
    """Never-guess (R8) fabrication guard for the FACT/RAG path.

    True when a question asks for a SPECIFIC payroll-levy shilling amount, in a
    situation-specific context (a workplace / employees / salary is referenced), but gives
    NO monetary figure to compute from — the case where the fact/RAG model otherwise
    invents a number (rc_22: 'wafanyakazi wanne ... makato ya mshahara ... kiasi gani?'
    -> the model fabricated 'PAYE TZS 4,000' with no salary ever given).

    Fires only when the deterministic router found no computable intent (detect_intent ==
    'none' -> no usable amount is present); a question with a computable amount routes to
    compute and never reaches this guard. Precision-first: requires payroll context AND a
    levy/deduction cue AND a money 'how-much' ask, so it never touches fixed-fee lookups
    ('BRELA ada ni ngapi' — no payroll context) or rate/definition questions ('kodi ni
    asilimia ngapi' — _has_money_ask rejects 'asilimia ngapi').

    Pure string logic, no model call. Applied in the fact path of BOTH the orchestrator and
    production run() (modal_app.py) as a shared predicate, so they cannot diverge."""
    ql = text.lower()
    if detect_intent(text) != "none":
        return False                                  # a computable route exists — not this guard's job
    has_payroll = any(c in ql for c in _PAYROLL_CTX)
    has_levy = bool(_explicit_levy(ql) or _natural_levy(ql))   # named levy OR generic 'makato'
    return has_payroll and has_levy and _has_money_ask(ql)

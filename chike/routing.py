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

from . import swahili_numbers as swn

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
    # ROUTING-GAP-PAYE: PAYE's everyday word is 'kodi' (tax), which is in neither the original
    # PAYE cues nor _GENERIC_LEVY, so ordinary "tax deducted from salary" phrasings mis-routed to
    # fact and the model free-computed a wrong figure (edge_04 "kodi ya serikali inayokatwa";
    # edge_05 "kodi yake"). These everyday phrasings are added so such questions reach paye compute
    # (and thus the D-PAYE-1 non-resident branch + the D-FIDELITY-1 guard). They only participate in
    # path 2, which already requires {number + payroll context + money-ask}, and the OOC classifier
    # runs BEFORE routing (so property/capital-gains/etc. 'kodi' questions are intercepted first) —
    # so these can only fire on an in-scope salary-context money-ask, which is PAYE. Offline sweep
    # over 400+20: routes exactly edge_04/edge_05 -> paye, zero other routing changes on the 400.
    # PREREQ-2 follow-up: 'kodi ya MISHAHARA' (plural) was missing while the singular 'kodi ya
    # mshahara' was present — the same singular/plural inflection gap Run 3 identified in the
    # levy cues. nat_18 ("...kodi ya mishahara yao ni ngapi") therefore routed to fact and
    # never reached the per-individual PAYE shape that pattern B had just built to answer it.
    # Sweep over 532: matches nat_18 (and its gp_05 probe twin) only. The OOC classifier runs
    # BEFORE routing, so a property/capital-gains 'kodi' is intercepted upstream and cannot
    # reach this cue.
    ("paye", ["kodi ya mapato", "kodi ya mshahara", "kodi ya mishahara", "mapato ya ajira",
              "kodi ya serikali", "kodi ya kipato", "kodi ya ajira",
              "kodi inayokatwa", "kodi ya mfanyakazi", "kodi yake"]),
]
_GENERIC_LEVY = ["makato", "michango", "tozo", "malipo kwa serikali", "kulipa serikali",
                 "kwa serikali"]

# Payroll context: the question is about wages/employees (needed for a payroll levy).
_PAYROLL_CTX = ["mshahara", "mishahara", "mfanyakazi", "wafanyakazi", "waajiriwa",
                "watumishi", "analipwa", "ninalipa", "kumlipa", "ajira", "payroll", "mlipwa",
                # Informal employment phrasing (item 3 / edge_p02): real users describe
                # employing/paying staff without a formal payroll word ("nimemuajiri msichana
                # wa kazi", "nina vibarua", "namlipa fundi"). Extends the ROUTING-GAP-PAYE class
                # (3144a98 added levy cues; this closes the payroll-context gate). Blast-radius
                # sweep over 400 gate + 15 probe: routes edge_p02 none->paye (correct compute
                # = TZS 78,000), ZERO other routing changes.
                "kuajiri", "niliajiri", "nimeajiri", "nimemuajiri", "nimemwajiri", "kumuajiri",
                "kumwajiri", "muajiri", "mwajiri", "waajiri", "kibarua", "vibarua", "mtumishi"]

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


# Payroll MONEY MAGNITUDE: a figure that could serve as a computation base. This separates a
# genuine compute question ("mishahara TZS 1,500,000 -> SDL yake?", "mshahara 6,750,000") from
# a rate/deadline/confirmation whose only number is incidental ("asilimia 3.5", "siku 30",
# "tarehe 20", "wafanyakazi 4"). Two signals: a currency/magnitude token, OR a parsed amount
# at/above the extraction layer's own payroll-plausibility floor (swn.MIN_PLAUSIBLE_AMOUNT),
# so a bare large number like 6,750,000 counts while a small rate/day/count does not — keeping
# routing consistent with how extraction itself decides a figure is a real payroll amount.
# Present -> the question may need computing, keep it on the compute path; absent (and no
# money-ask/applicability/derive cue) -> the number is incidental, route to fact/RAG.
_MONEY_MAGNITUDE = re.compile(
    r"\b(tzs|tsh|sh|shilingi|milioni|elfu|laki|dola|dollar|usd|euro|eur|kes|pound|paundi)\b")


def _has_money_magnitude(ql: str) -> bool:
    if _MONEY_MAGNITUDE.search(ql):
        return True
    return any(a >= swn.MIN_PLAUSIBLE_AMOUNT for a in swn.parse_amounts(ql))


# Compute-DERIVATION cue: the question actively asks to derive/compute the levy ("how will my
# X be?", "how do I get X?", "how is X computed?") — compute-intent even when the only number
# offered is a wrong base (a non-payroll count). Such a question belongs on the compute path,
# where the wrong-base / too-small-amount extraction guards clarify SAFELY (never-guess, R8);
# flipping it to fact/RAG would risk fabricating a levy from the wrong base — the separately-
# tracked extraction:small_int_as_money class (eval_263/265/266), deliberately NOT absorbed
# into this money-ask guard.
_DERIVE_CUE = re.compile(
    r"itakuwaje|itakuwa\s+ngapi|naipataje|naichangiaje|naikadiriaje|naihesabuje|"
    r"inahesabuje|inahesabiwa|inakatwa\s+vipi")


def _explicit_levy(ql: str):
    for levy, pats in _EXPLICIT.items():
        if any(re.search(p, ql) for p in pats):
            return levy
    return None


def all_explicit_levies(text: str):
    """Every explicitly-named compute levy in the text, in canonical order (sdl, nssf,
    paye, wcf). D-DECOMP-1: a compute sub-question can name MORE THAN ONE levy
    ("...SDL na NSSF...", "SDL, NSSF, PAYE na WCF"); detect_intent returns only the first
    (_explicit_levy), so the orchestrator used to compute one levy and silently drop the
    rest (eval_318 dropped NSSF). The orchestrator fans a multi-levy compute part out into
    one compute per levy using this list. Bounded to the four explicit levy tokens, so it
    never over-splits ordinary prose. Pure string logic, no model call."""
    ql = text.lower()
    return [levy for levy, pats in _EXPLICIT.items()
            if any(re.search(p, ql) for p in pats)]


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

    # Path 1 — explicit levy named + a number. GUARD (mirrors the natural-path money-ask
    # guard and the applicability-vs-amount guard): only COMMIT to compute when a computation
    # is actually needed. A bare incidental number — a rate ('asilimia 3.5'), a day ('siku
    # 30'/'tarehe 20'), a threshold headcount in a confirmation ('wafanyakazi 4, sivyo?') —
    # in a yes_no/definition/deadline question that merely NAMES the levy is NOT compute-
    # intent; without this guard it hit the compute path and asked for a salary the answer
    # never uses (eval_099/102/127/335/342/343/344/345). Commit to compute when ANY of:
    #   - a money 'how-much' ask (_has_money_ask), OR
    #   - an obligation/applicability cue (is_applicability_question), OR
    #   - a payroll money magnitude to compute from (_has_money_magnitude), OR
    #   - a threshold-crossing count (_COUNT_TRANSITION — eval_124's dedicated never-guess
    #     case from the applicability fix; kept on its own path, not flipped here), OR
    #   - a compute-derivation cue on a wrong base (_DERIVE_CUE — the extraction wrong-base
    #     small_int_as_money cases eval_263/265/266, where extraction clarifies safely).
    # The last two are explicit carve-outs so this guard stays surgical to the rate/deadline/
    # confirmation class and does not disturb mechanisms built/tracked on other lines.
    explicit = _explicit_levy(ql)
    if explicit and _has_number(ql) and (
            _has_money_ask(ql) or is_applicability_question(text)
            or _has_money_magnitude(ql)
            or _COUNT_TRANSITION.search(ql) or _DERIVE_CUE.search(ql)):
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

    # Path 2b — NATURAL APPLICABILITY (PREREQ-1 M5 / edge_p04). Path 2 above requires a money
    # 'how-much' ask, so an APPLICABILITY question on a levy that is only named naturally
    # ("...ile tozo ya mafunzo kwa waajiri inanihusu") could never reach compute — there was
    # no applicability arm on the natural path at all, which is why cue additions alone could
    # not fix p04. Same {number + payroll context + resolved levy} evidence as path 2, with
    # the money-ask swapped for an applicability cue.
    #
    # NARROWEST FORM: a number is REQUIRED, mirroring both paths above. The number-free form
    # also diverts adv_06 ("mfanyakazi wangu ameumia je bima ya ajali inatosha au nachangia
    # WCF") to a correct-but-partial deterministic yes that ignores the insurance half of the
    # question — not worth widening for. Limited to the three levies with a deterministic
    # applicability answer; 'ambiguous_multi' is excluded, since "does SOME levy apply?" has
    # no single yes/no.
    if _has_number(ql) and any(c in ql for c in _PAYROLL_CTX) and is_applicability_question(text):
        natural = _natural_levy(ql)
        if natural in ("sdl", "nssf", "wcf"):
            return natural

    return "none"


# Obligation/threshold cues: the question asks WHETHER a levy applies (am I obligated /
# do I reach the threshold), not HOW MUCH. Multi-word to avoid matching bare 'kulipa' in
# deadline/mechanism facts ('deadline ya kulipa michango', 'zinalipwa TRA siku ya 7').
_APPLICABILITY_CUES = [
    "wajibu wa kulipa", "nawajibika kulipa", "nalazimika kulipa", "lazima nilipe",
    "lazima kulipa", "inatakiwa kulipwa", "nafikia kizingiti", "fikia kizingiti",
    "haitakiwi kulipa", "nachangia",
    # PREREQ-1: the everyday "does it concern me?" phrasing. Its absence meant even an
    # EXPLICIT-levy applicability question missed path 1's guard ("nina wafanyakazi 15 je
    # SDL inanihusu" routed to fact — probe ap_13), as well as blocking the natural path
    # (edge_p04). DROPPED after the 483-sweep: "nahusika na", because it substring-matches
    # "i-nahusika na" in eval_100 ("je, NSSF inahusika na mshahara wote?") — a base-SCOPE
    # question that currently passes, which nssf_applies() would answer with the wrong
    # question's answer. The three '-nihusu/-kuhusu/-tuhusu' object forms carry the
    # applicability sense unambiguously.
    "inanihusu", "inakuhusu", "inatuhusu",
]


# Ordinal-hire / threshold-crossing phrasing ('ninaajiri mfanyakazi wa 10 katikati ya
# mwezi') — the headcount CHANGES over the period, so a static count-vs-threshold check
# would assert a possibly-wrong verdict (eval_124: reads '9', but hiring the 10th makes SDL
# due). Never-guess (R8): decline the deterministic shortcut here and let the amount path
# clarify, rather than assert 'haihusiki' on a count that is actually crossing the threshold.
# A headcount that CHANGES during the period. 'mfanyakazi wa 10' (the ordinal hire) was the
# only surface covered until 2026-08-08; 'kufikia 10' / 'nikafikia watu 12' are the same event
# stated as a destination and appear in eval_323 / eval_329 / ex_09. Widening this MATTERS for
# safety, not only for pattern F: parse_count's new singular and pay-verb surfaces make more
# questions yield a static headcount, and this veto is what stops that static count being
# treated as the whole story at the consumer (the SDL-zero branch gates on it). Narrowing a
# parser while leaving its safety net at one surface form is how a nat_07 gets made.
_COUNT_TRANSITION = re.compile(
    r"mfanyakazi\s+wa\s+(\d+)"
    r"|\b(?:kufikia|nikafikia|tukafikia|kufika)\s+"
    r"(?:watu\s+|wafanyakazi\s+|watumishi\s+|waajiriwa\s+)?(\d+)")

# Confirmation tag ("..., sivyo?") — the questioner states a premise and asks us to confirm
# it. There are 17 across the corpora and 16 are FALSE-premise traps whose correct lead is
# "Hapana."; only a premise that is both NEGATED and TRUE is agreed with. See
# rules_engine.results.agree_with_negated_premise for the eval_393 history.
_CONFIRMATION_TAG = re.compile(
    r"[,–—-]\s*(?:sivyo|si\s+ndivyo|siyo|sio\s+hivyo)\s*\??\s*$", re.IGNORECASE)
# Swahili negative concord in the premise clause: hai-/hawa-/ha- verb prefixes, 'si',
# 'hakuna'. Deliberately NOT matching bare 'si' inside a word (hivyo, sisi, kisicho...).
_NEGATED_PREMISE = re.compile(
    r"\bha(?:i|wa|tu|u|ki|ya|zi|li)?[a-z]*(?:takiwi|paswi|husiki|na\b|kuna\b)|"
    r"\bsi\s+lazima\b|\bsi\s+sharti\b|\bhakuna\b", re.IGNORECASE)


def confirms_negated_premise(text: str) -> bool:
    """True for a confirmation-tag question whose premise is NEGATED ('X haitakiwi ..., sivyo?').

    Agreeing with such a premise means leading 'Ndiyo', not 'Hapana' — the opposite of the
    plain frame the rules engine writes its verdict for. Gate the re-lead on this AND on the
    verdict actually confirming the premise (applicable is False); a negated premise the
    verdict CONTRADICTS must still be denied."""
    stripped = text.strip()
    if not _CONFIRMATION_TAG.search(stripped):
        return False
    premise = _CONFIRMATION_TAG.sub("", stripped)
    return bool(_NEGATED_PREMISE.search(premise))


def asks_applicability(text: str) -> bool:
    """True when the question asks WHETHER the obligation applies (yes/no) rather than HOW
    MUCH — an obligation/threshold cue with no money 'how-much' ask.

    This is is_applicability_question WITHOUT the mid-transition veto, so the transition
    branch (see count_transition_ordinal) can tell "an applicability question whose count is
    crossing" apart from "not an applicability question at all". Splitting the predicate does
    not weaken the veto: is_applicability_question still applies it, and the transition branch
    answers only at/above the threshold."""
    ql = text.lower()
    if _has_money_ask(ql):
        return False
    return any(cue in ql for cue in _APPLICABILITY_CUES)


def count_transition_ordinal(text: str):
    """The ordinal in a threshold-crossing hire phrase ('...mfanyakazi wa 10...'), else None.

    PREREQ-1 M4. _COUNT_TRANSITION already detected this shape in order to VETO the static
    headcount shortcut (eval_124: reads '9', but hiring the 10th makes SDL due). The veto was
    right and stays; what was missing is the ordinal itself, without which the question fell
    through to the amount path and demanded a salary its yes/no never needed. Callers must
    still gate on ordinal >= the levy threshold — below it, the crossing settles nothing and
    the never-guess refusal stands (probe ap_15)."""
    m = _COUNT_TRANSITION.search(text.lower())
    return int(next(g for g in m.groups() if g)) if m else None


def is_applicability_question(text: str) -> bool:
    """True when a levy question asks WHETHER the obligation applies (yes/no) AND a static
    headcount/flat-rule check can answer it — an obligation/threshold cue is present, there
    is NO money 'how-much' ask, and the count is not mid-transition (Finding 1). The
    orchestrator gates the levy type (sdl/nssf/wcf) separately; PAYE applicability needs a
    salary, so it stays on the amount path. Pure string logic."""
    if _COUNT_TRANSITION.search(text.lower()):
        return False
    return asks_applicability(text)


# NSSF party framing (D-NSSF-1): an NSSF amount question can ask for the EMPLOYEE's 10%
# share, the EMPLOYER's 10% share, or the 20% TOTAL. The rules engine used to always return
# the total, doubling the answer for single-party questions. This picks the party so
# compute_nssf returns the right headline. Pure string logic; default 'total' preserves the
# prior behaviour for anything unmatched.
#
# TOTAL cues are DELIBERATELY PRECISE — never bare 'jumla', because "mshahara wa jumla" /
# "jumla ya mshahara" means GROSS SALARY (not total contribution) and appears in employer
# questions (eval_090: "mshahara wa jumla ... mwajiri anachangia ... sehemu yake"). A bare
# 'jumla' rule misroutes that to total. Employer cues WIN over an incidental 'mfanyakazi'
# (the salary owner is named even in an employer-share question).
_NSSF_TOTAL_CUES = [
    "jumla ya mchango", "jumla ya michango", "michango yote", "yote miwili",
    "mwajiri pamoja na mfanyakazi", "mwajiri na mfanyakazi", "kiwango cha jumla",
    "jumla ya nssf", "nssf ya jumla", "umegawanywa",
]
_NSSF_EMPLOYER_CUES = [
    "sehemu ya mwajiri", "mwajiri anachangia", "upande wa mwajiri", "mchango wa mwajiri",
    # PREREQ-2: the FIRST-PERSON employer phrasing ("mimi KAMA MWAJIRI NACHANGIA kiasi gani")
    # matched none of the third-person cues above, so nat_07 fell to the 'total' default and
    # would answer 20% (TZS 160,000) where the employer share is 10% (TZS 80,000). Latent
    # until now — the question used to clarify; the Tier-1 'kama' fix makes it computable, so
    # the D-NSSF-1 party gap underneath became reachable and had to be closed with it.
    # Sweep over 500: matches nat_07 only (edge_p03 already resolves 'employee' on an
    # earlier cue and is unchanged).
    "kama mwajiri nachangia", "mwajiri nachangia",
]
_NSSF_EMPLOYEE_CUES = [
    "ya mfanyakazi", "wa mfanyakazi", "anayokatwa", "kinakatwa mshahara",
    "wake wa nssf", "nssf yake", "mchango wake",
]


def nssf_party(text: str) -> str:
    """Which NSSF figure the question asks for: 'employee' | 'employer' | 'total'.

    Precedence: an explicit TOTAL cue wins first (a 'jumla ya mchango' / 'mwajiri na
    mfanyakazi' question wants the 20% total even though it names both parties); then an
    EMPLOYER cue (wins over the incidental 'mfanyakazi' that names the salary owner); then an
    EMPLOYEE cue. Default 'total' — byte-identical to the engine's prior single-behaviour, so
    an unmatched question is unchanged. Pure string logic, no model call."""
    ql = text.lower()
    if any(cue in ql for cue in _NSSF_TOTAL_CUES):
        return "total"
    if any(cue in ql for cue in _NSSF_EMPLOYER_CUES):
        return "employer"
    if any(cue in ql for cue in _NSSF_EMPLOYEE_CUES):
        return "employee"
    return "total"


# D-PAYE-1. Non-resident employees pay a flat 15% final withholding, NOT the resident
# progressive bands. The engine (compute_paye) already expresses this via resident=False;
# it was never told, so every PAYE compute got resident bands (eval_367: a non-resident on
# TZS 5,000,000 was billed 1,328,000 progressive instead of the flat 750,000).
# NON-RESIDENT cues are negated-residency phrases; each CONTAINS 'mkazi', so a bare 'mkazi'
# resident test would misfire — the resident-affirmation cue is the precise 'ni mkazi'.
_PAYE_NONRESIDENT_CUES = [
    "asiye mkazi", "si mkazi", "sio mkazi", "wasio wakazi", "asiyekuwa mkazi",
    "non-resident", "nonresident",
]
# A DISTINCT resident is also named -> a two-person, mixed-residency question that a single
# scalar flag cannot express (eval_326: "ni mkazi ... na mwenzake si mkazi"). Guard: do NOT
# flip; leave the default resident path and defer to the multi-part decompose/merge item.
# Cues are the PRECISE 'ni mkazi' — a greedy 'mkazi analipwa' would match inside the
# non-resident 'asiye mkazi analipwa' and wrongly guard eval_367 back to resident.
_PAYE_RESIDENT_CUES = ["ni mkazi", "ni wakazi"]


def paye_resident(text: str) -> bool:
    """True = resident (progressive bands, the default); False = non-resident (flat 15%).

    Only a negated-residency cue flips to non-resident. If a resident is ALSO named
    (mixed-residency, two people), the scalar can't represent both — stay resident-default
    and let the decompose/merge path handle it (eval_326). Default True is byte-identical to
    the engine's prior single behaviour, so unmatched questions are unchanged. Pure string
    logic, no model call."""
    ql = text.lower()
    if not any(cue in ql for cue in _PAYE_NONRESIDENT_CUES):
        return True
    if any(cue in ql for cue in _PAYE_RESIDENT_CUES):  # mixed -> defer to decomposition
        return True
    return False


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

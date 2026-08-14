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

# The rules-engine computation types. 'ambiguous_multi' is compute-intent with an
# unresolved specific levy; 'none' means fact/RAG. 'minimum_wage' is not a levy — see path 3
# in detect_intent and chike/rules_engine/minimum_wage.py.
COMPUTE_TYPES = ("sdl", "nssf", "paye", "wcf", "minimum_wage")

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

# --- minimum wage (GN 605A), path 3 -----------------------------------------
# The figure must be presented as PAY, and specifically as pay SOMEONE IS BEING PAID —
# a pay VERB, not the noun 'mshahara'. Two narrowings, both forced by evidence:
#
#   * Narrower than _PAYROLL_CTX: a bare 'mfanyakazi' plus a lawfulness word is a question
#     about employment generally, not about the wage floor (mw_18).
#   * Narrower than the noun 'mshahara': the first version of this list included it, and the
#     blast-radius sweep caught it stealing FIVE real gate questions — eval_118/119/120/126/382,
#     all GN 605A LOOKUPS ("wastani wa mshahara wa chini ... ulikuwa TZS ngapi?", "kima cha juu
#     kabisa ... ni TZS ngapi?"). Every one of them says 'mshahara wa chini' and carries a 'TZS'
#     token, so cue + magnitude were both satisfied while nobody was being paid anything. They
#     would have been answered with "tell me what work your employee does", which is not an
#     answer to any of them. A pay verb is the thing that distinguishes "I pay X" from "what is
#     X" — the narrowest form that closes the case, per R17.
#
# 'analipa' (he PAYS) is excluded and only 'analipwa' (he IS PAID) kept: the active form
# appears in "mfanyakazi analipa kodi", which is a levy question. Bare 'nalipa' is excluded
# for the same reason — it is a substring of 'analipa'.
_WAGE_PAY_CUES = ["namlipa", "ninalipa", "nawalipa", "namlipia", "nimemlipa", "nimemlipia",
                  "tunamlipa", "tunawalipa", "kumlipa", "kuwalipa", "humlipa",
                  "analipwa", "wanalipwa", "analipwaga", "hulipwa", "walipwa"]
# Explicit floor vocabulary — enough on its own, with a pay cue and a magnitude.
_MIN_WAGE_CUES = ["kima cha chini", "mshahara wa chini", "kiwango cha chini cha mshahara",
                  "kima kidogo cha mshahara", "gn 605a", "gn605a", "minimum wage"]

# The question's FRAME decides which lead word is correct for the SAME verdict:
#   "…je ni halali?"      -> compliant = "Ndiyo"
#   "…nakiuka sheria?"    -> compliant = "Hapana"
# The yes/no scorer reads the polarity of the first paragraph, so getting this backwards is
# the th_16 inversion arriving from the QUESTION side rather than the model side — a source
# that blanking the model body does nothing about. Violation cues are tested FIRST, and a
# question carrying BOTH frames resolves to 'unknown', which leads substantively instead.
_WAGE_VIOLATION_CUES = ["nakiuka", "ninakiuka", "unakiuka", "tunakiuka", "navunja sheria",
                        "ninavunja sheria", "ni kosa", "ni kinyume cha sheria",
                        "nitaadhibiwa", "nitatozwa faini", "nitafungwa", "nakosea kisheria"]
_WAGE_LAWFUL_CUES = ["ni halali", "si halali", "ni sawa", "iko sawa", "inaruhusiwa",
                     "naruhusiwa", "ni sahihi kisheria", "nafuata sheria", "ni kihalali"]


def wage_question_frame(text: str) -> str:
    """'lawful' | 'violation' | 'unknown' — which way round a yes/no answer reads.

    'unknown' is a first-class outcome, not a failure: the caller then leads with the
    substantive comparison ("Mshahara wa TZS X uko CHINI ya kima cha chini cha TZS Y"), which
    is correct under either frame and does not depend on this detector being right."""
    ql = text.lower()
    violation = any(c in ql for c in _WAGE_VIOLATION_CUES)
    lawful = any(c in ql for c in _WAGE_LAWFUL_CUES)
    if violation and lawful:
        return "unknown"                       # both framings in one question — lead neutrally
    if violation:
        return "violation"
    if lawful:
        return "lawful"
    return "unknown"


# Pay quoted PER UNIT. The Order prescribes a rate for every one of these periods, so the
# comparison is column-to-column and nothing is ever converted. Fortnight patterns are tested
# BEFORE weekly ('kwa wiki mbili' contains 'kwa wiki').
_WAGE_PERIOD_CUES = [
    ("fortnightly", r"kwa\s+wiki\s+mbili|kila\s+wiki\s+mbili|kwa\s+siku\s+kumi\s+na\s+nne|"
                    r"fortnight|bi-?weekly"),
    ("hourly", r"kwa\s+saa\b|kila\s+saa\b|per\s+hour"),
    ("daily", r"kwa\s+siku\b|kila\s+siku\b|per\s+day|kwa\s+kutwa\b"),
    ("weekly", r"kwa\s+wiki\b|kila\s+wiki\b|per\s+week"),
    ("monthly", r"kwa\s+mwezi\b|kila\s+mwezi\b|kwa\s+mwezi\s+mmoja|per\s+month"),
]


# Work arrangements whose EMPLOYMENT STATUS is unsettled. GN 605A applies to "employees",
# and para 3 gives that word the meaning it has under the Employment and Labour Relations Act
# Cap. 366 — so whether a bodaboda rider is covered at all is a labour-law determination, not
# a wage question. Unverified against a primary source here, and wrong in either direction if
# guessed, so it is routed to a clarification and logged as its own item rather than resolved
# implicitly by a sector cue.
_WAGE_STATUS_UNCLEAR_CUES = ["bodaboda", "boda boda", "boda-boda", "bajaji", "guta",
                             "kujitegemea", "anajitegemea", "freelance", "gig",
                             "kwa makubaliano ya kazi"]


def wage_status_unclear(text: str) -> bool:
    """True when the worker's status as an 'employee' under Cap. 366 is itself in question."""
    ql = text.lower()
    return any(c in ql for c in _WAGE_STATUS_UNCLEAR_CUES)


def wage_period(text: str):
    """The period a wage is quoted in, or None when the question does not say.

    None is NOT 'monthly'. The caller decides whether the monthly reading is safe: a figure
    below the Order's lowest monthly rate with no period stated is genuinely ambiguous
    (TZS 10,000 is an unlawful month and a lawful day), and is clarified rather than judged."""
    ql = text.lower()
    for period, pattern in _WAGE_PERIOD_CUES:
        if re.search(pattern, ql):
            return period
    return None

# --- VAT registration / EFD thresholds, path 4 ------------------------------
# Registration is not a levy: nothing is deducted and nothing is owed, so no levy path can
# reach these. "Je nahitajika kusajili VAT?" asks for a VERDICT, which _has_money_ask rejects.
#
# The vocabulary is deliberately split into WHICH-OBLIGATION and IS-IT-REQUIRED, and BOTH are
# required, because either alone is far too broad: 'mauzo' appears in 178 corpus rows, most of
# them VAT rate/withholding/definition questions that must keep their fact route.
_VAT_REG_CUES = ["kusajili vat", "kujisajili vat", "kusajilisha vat", "kujisajilisha vat",
                 "usajili wa vat", "usajilishaji wa vat", "nasajiliwa vat", "kusajiliwa vat",
                 "kizingiti cha vat", "kufika kiwango cha vat", "nimefika kiwango cha vat",
                 "register for vat", "vat registration", "vat threshold"]
_EFD_CUES = ["mashine ya risiti", "mashine ya efd", "risiti ya mashine", "kuwa na efd",
             "nahitaji efd", "lazima niwe na efd", "efd machine", "kutumia efd"]

# THE FIGURE MUST BE THE TRADER'S OWN TURNOVER. This is the `mshahara` narrowing from the
# minimum-wage arm, in its second domain and forced by the same instrument: the first version
# required only {obligation cue + magnitude} and the sweep diverted 18 corpus rows, of which
# most were wrong — threshold LOOKUPS ("kizingiti cha mauzo cha miezi 12 ... ni TZS ngapi?"),
# false-premise confirmations ("kizingiti ... ni TZS 200,000,000, sivyo?"), and projections.
# Every one of them contains a threshold, a period and VAT registration vocabulary while
# nobody is stating their own sales. A possessive/first-person turnover claim is what
# separates "my sales are X" from "what is X".
_OWN_TURNOVER_CUES = ["mauzo yangu", "mauzo ya biashara yangu", "mauzo ya duka langu",
                      "mapato yangu", "mzunguko wangu", "biashara yangu ina mauzo",
                      "biashara yangu imepata", "biashara yangu inaingiza", "duka langu lina",
                      "duka langu linaingiza", "nimeuza", "ninauza", "nauza", "naingiza",
                      "ninaingiza", "nimepata mauzo", "tumeuza", "mauzo yetu", "mapato yetu",
                      "my turnover", "my sales"]

# Asks that are NOT "am I over the threshold?", even when every other cue is present. Each is
# a question the comparison cannot answer, and answering it with a comparison is worse than
# leaving it on the fact path:
#   * a LOOKUP of the threshold itself ("ni TZS ngapi")
#   * a PROJECTION ("after how many months", "how much MORE do I need")
#   * a false-premise CONFIRMATION ("sivyo?"), which has its own machinery and whose correct
#     answer is a correction, not a verdict
_THRESHOLD_ASK_VETO = re.compile(
    r"ni\s+tzs\s+ngapi|ni\s+kiasi\s+gani\s*\?|\bsivyo\s*\?|baada\s+ya\s+miezi\s+mingapi|"
    r"mauzo\s+ya\s+ziada|kiasi\s+gani\s+zaidi|ngapi\s+kabla|vizingiti\s+viwili|"
    r"kizingiti\s+cha\s+mauzo\s+cha|asilimia\s+ngapi")

# A figure quoted in a FOREIGN currency is not TZS turnover and must never be compared against
# a TZS threshold (eval_278 states Kenyan shillings). The existing money-magnitude test counts
# them as money, correctly; they are simply not this comparison's operand.
_FOREIGN_CURRENCY = re.compile(
    r"shilingi\s+za\s+kenya|kenyan?\s+shilling|\bkes\b|\bugx\b|shilingi\s+za\s+uganda|"
    r"\busd\b|dola|dollar|\beur\b|euro|\bgbp\b|paundi|rand")

# Already-registered statements. EFD is required on VAT registration alone, so this is not a
# nicety: it short-circuits the turnover test entirely.
_VAT_REGISTERED_CUES = ["nimeshasajili vat", "nimesajili vat", "nimejisajili vat",
                        "nimesajiliwa vat", "nimeshajisajili vat", "niko kwenye vat",
                        "nina namba ya vat", "vat registered", "nimesajiliwa kwa vat"]

# Turnover PERIOD. This is the crux: the two VAT limbs are separate tests, and a figure only
# addresses the limb its period names. 'monthly' is recognised precisely so it can be REFUSED
# — a monthly rate is not a period total and is never annualised (see registration_thresholds).
# Six-month patterns are tested BEFORE annual ones ('miezi 6 ya mwaka' contains neither, but
# 'nusu mwaka' contains 'mwaka').
_TURNOVER_PERIOD_CUES = [
    ("six_month", r"miezi\s+(?:6|sita)|nusu\s+mwaka|miezi\s+sita|half\s*-?\s*year|"
                  r"robo\s+mbili"),
    # 'ya/za/la mwaka' — the GENITIVE — is how annual turnover is actually said ("mauzo yangu
    # YA MWAKA ni milioni 15"), and the first version matched only 'kwa mwaka'. The routing
    # sweep could not see the gap because those rows route here correctly; they then failed at
    # the PERIOD step and came back as clarifications. Caught by the offline orchestrator run
    # asserting each probe's `truth`, not by the router sweep — the same lesson as instrument
    # #2: a check that compares one stage cannot see a defect in the next.
    ("annual", r"kwa\s+mwaka|(?:ya|za|la)\s+mwaka|kila\s+mwaka|mwaka\s+huu|mwaka\s+mmoja|"
               r"miezi\s+(?:12|kumi\s+na\s+miwili)|per\s+year|annual|kwa\s+mwaka\s+mzima"),
    ("monthly", r"kwa\s+mwezi|kila\s+mwezi|mwezi\s+huu|per\s+month|monthly|kwa\s+wiki|"
                r"kila\s+wiki"),
]


def turnover_period(text: str):
    """'annual' | 'six_month' | 'monthly' | None — the period a turnover figure is stated for.

    None is NOT annual, and 'monthly' is NOT a twelfth of annual. Both are refusals at the
    caller: the first because no limb is addressed, the second because annualising a rate
    assumes the trader's turnover is flat, which for a seasonal market trader is a guess about
    the future dressed up as arithmetic."""
    ql = text.lower()
    for period, pattern in _TURNOVER_PERIOD_CUES:
        if re.search(pattern, ql):
            return period
    return None


def states_vat_registered(text: str) -> bool:
    """True when the trader says they are ALREADY VAT-registered."""
    ql = text.lower()
    return any(c in ql for c in _VAT_REGISTERED_CUES)


# --- the polarity reader, asserted over our OWN threshold copy ---------------
# A two-part answer ("no on the limb I tested, BUT the other limb is open") must not scan as a
# flat no. This is the minimum-wage `ni halali` lesson applied before shipping rather than
# after: a refusal that reads as a verdict is the failure this copy is most prone to, and the
# copy is the thing under test, not the question.
_VERDICT_NEG = ["hapana", "hutakiwi", "hauhitajiki", "huhitaji", "sio lazima", "si lazima"]
_VERDICT_POS = ["ndiyo", "unatakiwa", "ni lazima", "unahitajika", "inatakiwa"]
# A condition left OPEN — the marker that makes a negative partial rather than final.
_CONDITIONAL_MARKERS = ["ikiwa", "endapo", "kama yamezidi", "kama umesajiliwa",
                        "halijamalizika", "lakini hili", "niambie mauzo", "niambie kama"]


def reads_as_unconditional(text: str) -> bool:
    """True when an answer states a verdict with NO condition left open beside it.

    Used as a TEST INSTRUMENT over our own generated copy, not over user questions. The
    assertion it supports: every below-threshold answer must read as CONDITIONAL (this
    returns False), and every above-threshold answer must read as final (returns True). A
    future edit that drops the conditional clause, or that softens an unconditional verdict
    into mush, fails on one side or the other.
    """
    tl = text.lower()
    has_verdict = any(c in tl for c in _VERDICT_NEG + _VERDICT_POS)
    has_condition = any(c in tl for c in _CONDITIONAL_MARKERS)
    return has_verdict and not has_condition


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


# ROUTING-GAP-NGAPI (A1). `ngapi` IS the Swahili "how much" — and _MONEY_ASK only carried
# it in the fixed phrases "ni ngapi" / "shilingi ngapi". An inflected verb before it
# ("nitalipa ngapi", "nichangie ngapi", "nakatwa ngapi") matched nothing, so the question
# never reached the compute path and the MODEL free-computed the figure: nat_01 answered SDL
# at 0.5% with no amount at all, nat_19 answered WCF as TZS 300,000 on a 3,000,000 payroll
# (10%, against the real 0.5%). Neither reply carried a deterministic working, which is the
# observable signature of the engine never having run.
#
# VERB-QUALIFIED, NEVER A BARE `ngapi` (R17: prefer the narrowest form that closes the case,
# chosen so one substring covers a whole inflection family). Two noun collisions exist and
# only an AUTHORED probe could find them — the corpus contains neither:
#   kata       = WARD (an administrative area), not only the deduct stem. Hence \w+kata with
#                a REQUIRED prefix, so "kata ngapi zina ofisi za TRA" cannot match while
#                "wananikata ngapi" does.
#   changamoto = CHALLENGE, and it opens with the chang- contribute stem. Safe because the
#                stem must sit immediately before the space: "changamoto ngapi" cannot match.
# The _NONMONEY_ASK guard below still runs afterwards, so "asilimia/siku/mara ngapi" remain
# non-money asks even when a verb form is also present — two independent layers, deliberately.
_VERB_MONEY_ASK = re.compile(
    r"\b(?:\w*lipa|\w*lipe|\w*lipwa|\w*changia|\w*changie|\w*changa|\w+katwa|\w+kata)"
    r"\s+ngapi\b")


def _has_money_ask(ql: str) -> bool:
    ask = any(c in ql for c in _MONEY_ASK) or bool(_VERB_MONEY_ASK.search(ql))
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

    # Path 3 — MINIMUM WAGE (GN 605A). Not a levy: nothing is deducted and nothing is owed,
    # so neither path above can reach it. "Je ni halali kisheria?" asks for a VERDICT, which
    # _has_money_ask rejects (correctly — it is not a request for a shilling quantity), and no
    # levy word is present, so these questions have always fallen through to fact/RAG. That is
    # how th_16 came to be answered wrong in production.
    #
    # PLACED LAST, immediately before the fact fallthrough, so BY CONSTRUCTION this arm can
    # only capture questions that route to fact today: every levy route above wins first, and
    # the blast radius is bounded before the sweep runs rather than by it. A question naming
    # both a levy and a wage ("...TZS 800,000 — je ni halali kukata NSSF?") keeps its levy
    # route on path 1.
    #
    # Evidence required: a payroll MAGNITUDE (a real wage figure, not an incidental number),
    # a PAY cue, and either an explicit floor term or a lawfulness/violation frame. The pay
    # cue is deliberately NARROWER than _PAYROLL_CTX — the figure has to be presented as pay,
    # so "je ni halali kulipa mfanyakazi bila mkataba" (a contract question that merely
    # mentions an employee) is not diverted here.
    if (_has_money_magnitude(ql) and any(c in ql for c in _WAGE_PAY_CUES)
            and (any(c in ql for c in _MIN_WAGE_CUES)
                 or wage_question_frame(text) != "unknown")):
        return "minimum_wage"

    # Path 4 — VAT REGISTRATION / EFD THRESHOLDS. Also not a levy: registering costs nothing
    # and deducts nothing, so no path above can reach these, and they have always fallen
    # through to fact/RAG. SAFETY-3 is what that produced — the threshold recited correctly in
    # the sentence where it was misapplied.
    #
    # PLACED LAST, after minimum_wage and immediately before the fact fallthrough, for the same
    # constructional reason: every levy and wage route wins first, so the blast radius is
    # bounded before the sweep runs. A question mixing a levy with a threshold
    # ("...mauzo milioni 300, SDL yangu ni ngapi?") keeps its levy route on path 1.
    #
    # Evidence required: an OBLIGATION cue (VAT-registration or EFD vocabulary, both narrow
    # multi-word forms) AND a money magnitude, OR an already-registered statement with an EFD
    # cue (which needs no figure at all — registration alone settles it). 'mauzo' on its own is
    # NOT evidence: it appears in 178 corpus rows, nearly all of them rate, withholding and
    # definition questions that must keep their fact route.
    # EFD WINS WHEN THE ASK IS EFD. th_09/th_10 ("mauzo yangu ni TZS 15,000,000 kwa mwaka na
    # SINA USAJILI WA VAT — je nahitaji EFD?") mention VAT registration only to say they do not
    # have it; the question is the EFD one. First-version precedence gave VAT the row and
    # answered the wrong obligation. The EFD cues are all forms of "do I need the machine",
    # so their presence identifies the ask regardless of what else is named.
    vat_reg = any(c in ql for c in _VAT_REG_CUES)
    efd = any(c in ql for c in _EFD_CUES)
    if (vat_reg or efd) and not _THRESHOLD_ASK_VETO.search(ql) \
            and not _FOREIGN_CURRENCY.search(ql):
        own = any(c in ql for c in _OWN_TURNOVER_CUES)
        # EFD needs no figure when registration alone settles it; VAT always needs one.
        if (own and _has_money_magnitude(ql)) or (efd and states_vat_registered(text)):
            return "efd_requirement" if efd else "vat_registration"

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
# safety, not only for pattern F: parse_count's singular and pay-verb surfaces make more
# questions yield a static headcount, and this veto is what stops that static count being
# treated as the whole story at the consumer (the SDL-zero branch gates on it). Narrowing a
# parser while leaving its safety net at one surface form is how a nat_07 gets made.
#
# THE SURFACE ITSELF LIVES IN swahili_numbers._CROSSING and is not duplicated here. The same
# phrase drives this veto, the per-month split (F2) and F1's SDL headcount; three copies of one
# safety predicate is precisely the dual-file divergence CLAUDE.md warns about, so there is one
# owner and every consumer delegates to it.
_COUNT_TRANSITION = swn._CROSSING

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


# "Kiwango cha SDL ni (asilimia) ngapi ...?" — the RATE is what is being asked for, and it does
# not depend on the figure the question also carries. Requires 'kiwango'/'asilimia ngapi'
# phrasing; a plain "SDL yangu ni ngapi" is an AMOUNT question and must not land here.
_RATE_QUESTION = re.compile(
    r"\bkiwango\s+(?:cha|kwa)\b[^.?!]{0,60}?\bngapi\b"
    r"|\b(?:paye|sdl|nssf|wcf)\s+ni\s+asilimia\s+ngapi\b", re.IGNORECASE)


def asks_rate(text: str) -> bool:
    """True when the question asks for a levy's RATE rather than an amount owed."""
    return bool(_RATE_QUESTION.search(text))


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
    return swn.crossing_headcount(text)


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

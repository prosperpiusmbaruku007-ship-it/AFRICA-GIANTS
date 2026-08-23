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
# ORTHOGRAPHIC VARIANTS (2026-08-14, dh->z). THE OBSERVED MISS: a real user wrote "mfuko wa
# hifazi ya jamii". No cue matched, detect_intent returned none, and the question fell to the
# fact path, which answered "TZS 20,000" against a stated salary of TZS 800,000 — the correct
# employer share was TZS 80,000. The figure was extracted correctly (parse_amounts read "laki
# nane" as 800000) and nssf_party read "employer"; ONE MISSPELLING was the entire blocker.
# Hand-written per phrase, never generated — see tests/test_orthographic_variants.py.
_LEVY_CUES = [
    # A2 (2026-08-15): `kwenye mfuko` — money going INTO the fund. Bare `mfuko` was measured
    # and rejected: it is 29 corpus rows (pocket/bag/any fund) against the SAME 2 route
    # changes, so the narrowing costs nothing in coverage and removes 20 rows of surface.
    ("nssf", ["pensheni", "uzeeni", "hifadhi ya jamii", "mchango wa hifadhi",
              "mfuko wa hifadhi", "akiba ya baadaye",
              "hifazi ya jamii", "mchango wa hifazi", "mfuko wa hifazi",
              "kwenye mfuko"]),
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
    # A2 (2026-08-15): what the GOVERNMENT takes from a wage, and what is SENT to TRA on a
    # wage — the everyday phrasings for PAYE that name no tax at all. Each is one observed
    # failure; see the A2 note below on why that is the honest ceiling here.
    #
    # `serikali` bare is 80 corpus rows and `kwa tra` is 34; verb-qualified they are ONE row
    # each, with identical route coverage. The levy is PAYE and not `ambiguous_multi` because
    # what the government takes FROM a salary is income tax: NSSF goes to a fund rather than
    # to the state, and SDL is paid by the employer rather than deducted from the wage.
    ("paye", ["kodi ya mapato", "kodi ya mshahara", "kodi ya mishahara", "mapato ya ajira",
              "kodi ya serikali", "kodi ya kipato", "kodi ya ajira",
              "kodi inayokatwa", "kodi ya mfanyakazi", "kodi yake",
              "serikali inachukua", "peleka kwa tra"]),
# WITHHELD: `serikali inakata`. It is the exact sibling of `serikali inachukua` above, it is
# corpus-attested (rc_10), and it is NOT ADDED — because routing that row to compute would be
# WORSE than leaving it on the fact path.
#
#   rc_10  "Ninalipwa laki mbili na hamsini kwa mwezi. Je serikali inakata kiasi gani...?"
#          gold: PAYE on 250,000 -> ZERO, below the 270,000 band.
#          sole_plausible_amount("laki mbili na hamsini") -> 5,200,000
#
# The parser reads `mbili na hamsini` as 52 and multiplies by laki. Even the unambiguous
# "laki mbili na hamsini ELFU" parses to 5,200,000. Routed to PAYE that yields roughly
# TZS 1,388,000 — served WITH A DETERMINISTIC WORKING to somebody who owes nothing. A wrong
# number on the fact path is bad; the same wrong number carrying the engine's authority is
# worse, so the cue waits for the parse.
#
# This is a PRE-EXISTING parser defect that the A2 cue merely UNMASKS, and it is its own item:
# `laki <n> na <m>` affects every money extraction in the product, so it needs its own sweep
# and cannot ride along here. test_the_withheld_serikali_inakata_cue_still_names_a_live_defect
# fails the moment the parse is fixed, which is when this line should be deleted.
]
_GENERIC_LEVY = ["makato", "michango", "tozo", "malipo kwa serikali", "kulipa serikali",
                 "kwa serikali"]

# ===========================================================================
# CONCORD CLOSURE (2026-08-15) — the classes below are CLOSED, so they are closed here.
# ===========================================================================
# Every cue list in this file grew one observed failure at a time. That is fine for open
# lexical sets, where you cannot know the next word a user will invent. It is a defect for
# CLOSED grammatical classes, which can be enumerated from the grammar in one sitting — and
# Swahili concord is exactly such a class. An audit found 11 of 37 members handled: the
# high-frequency member of each class present, the rest absent, which is the signature of
# failure-driven growth rather than of design.
#
# TWO PARADIGMS ARE CLOSED HERE:
#   possessive  -angu (my) <-> -etu (our), agreeing in noun class:
#               wangu/wetu, yangu/yetu, langu/letu, changu/chetu, vyangu/vyetu, zangu/zetu
#   subject     ni- (I) <-> tu- (we), fused with tense:
#               nina-/tuna-, nime-/tume-, nili-/tuli-, nita-/tuta-
#
# CLOSURE IS LINEAR, NOT QUADRATIC — the reason this was affordable. Concord is FUNCTIONAL:
# `mauzo` takes `yangu`/`yetu` and nothing else; `mauzo langu` is ungrammatical, not an
# unhandled variant. So each cue gains exactly ONE counterpart. The cross-product fear
# (10 nouns x 15 possessives = 150) is not a real cost.
#
# 27 OF 58 DERIVED COUNTERPARTS WERE ALREADY MATCHED, AND ONLY BY LUCK. Cue lists match with
# `phrase in text`, and the colloquial 1sg present `na-` is a substring of the 1pl `tuna-`:
# "tunauza" already matched "nauza", "tunachangia" already matched "nachangia". The luck
# runs out at every other tense — `nime-`/`nili-`/`nita-` are NOT substrings of
# `tume-`/`tuli-`/`tuta-`. So the router understood "we pay" and never understood "we PAID"
# or "we WILL pay", and no failure log would have named that pattern. Only the paradigm does.
# The additions below are the 29 that are NOT already matched; the test asserts RECOGNITION,
# not list membership, so the 27 free ones do not become 27 lines of noise.
# (`tumemuajiri` was in the lucky set via the NOUN `muajiri` = employer — coincidence, not
# morphology. It is the fragile kind and the test's recognition check is what holds it.)
#
# Blast radius over 5,510 corpus questions: ONE route change, and it is the live SDL wrong
# answer moving none -> sdl. 38 of the additions have zero corpus occurrences, which is why
# eval/refusal_gate/concord_1pl_in_scope_020.jsonl exists (R17: a clean sweep over a corpus
# that lacks the vocabulary is not evidence).
# ===========================================================================

# ===========================================================================
# OBJECT CONCORD (2026-08-15) — the THIRD person-marking paradigm, and the one the
# 2026-08-15 audit did not enumerate.
# ===========================================================================
# Swahili marks the OBJECT with an infix between the tense marker and the verb stem, and the
# class is CLOSED — exactly five members:
#
#     wa-na-NI-kata     they deduct from ME        -ni-  1sg   <- nat_08, live and wrong
#     wa-na-KU-kata     they deduct from YOU       -ku-  2sg
#     wa-na-M-kata      they deduct from HIM/HER   -m-   cl.1  (-mw- before a vowel)
#     wa-na-TU-kata     they deduct from US        -tu-  1pl
#     wa-na-WA-kata     they deduct from THEM      -wa-  cl.2
#     i-na-NI-anza      it starts on ME                        <- nat_04, live and wrong
#
# `_APPLICABILITY_CUES` already closed it for ONE verb (`-nihusu`/`-kuhusu`/`-tuhusu`), so the
# discipline existed in this file and had been applied in exactly one place — and even there
# only three of the five members were present.
#
# WHY THIS IS A REGEX AND NOT A CUE LIST, WHICH IS THE WHOLE SAFETY ARGUMENT.
# The obvious closure — put the bare infix+stem in the list, so one substring covers the
# inflection family (R17 step 4) — is UNSAFE HERE, and measurably so. Swept over 5,549 corpus
# questions, four of the five bare forms nest inside ordinary Swahili words:
#
#     `wakat`  ->  116 hits, ALL of them `waKATi` (time/when)
#     `mkat`   ->   36 hits, ALL of them `MKATaba` (employment contract)
#     `kukat`  ->   48 hits, ALL of them `kukata` (the infinitive, no object at all)
#     `nikat`  ->   12 hits, 6 of them `nikatae` (if I refuse)
#     `kuhusu` ->  154 hits, ALL of them the PREPOSITION "about"
#
# and a fifth trap has nothing to do with morphology: `lini anza` ("WHEN does it start")
# written as one word is `linianza`, which any `-ni-anza` substring cue reads as object
# concord. This is the FOURTH instance of the substring-nesting hazard CLAUDE.md records
# (`waajiri`/`wajiri`, `naagiza`/`tunaagiza`, `si mkazi`/`si mkazi wa kudumu`) and the first
# where it was found BEFORE shipping rather than after.
#
# Requiring the HOST — a subject prefix fused with a tense marker, or the tenseless habitual
# `hu-`/infinitive `ku-`/negative `ha-` — kills every one of those. `wakati` has no tense
# marker after `wa`; `mkataba` has no host at all; `kukata` has no infix between `ku` and the
# stem; `linianza` has `ni` where a tense marker must be. The host is not decoration, it is
# the discriminator.
#
# THE HONEST LIMIT, stated because the handover overstated it. The INFIX class is closed; the
# VERB it attaches to is not. So this cannot be a generic object-concord detector — each stem
# is named. The handover's "52 eval / 385 train rows exercise this" came from a bare
# `(na|me|li|ta)(ni|ku|tu)` scan and is noise: `kaMPUNI`, `kiWAngo`, `kuTUmika`, `waKATi`,
# `inaMAANisha` all match it and none contains an object infix. Host-qualified, the corpus
# carries ~120 real occurrences and `-husu` alone is ~78 of them. The sweep below is
# therefore real evidence for `-husu` and NEARLY BLIND for `-kata` and `-anza` — which is the
# SAFETY-2 situation after all, and why the authored probes are load-bearing, not a ritual.
_OBJECT_INFIX = ("ni", "ku", "m", "tu", "wa")
# `-m-` is `-mw-` before a vowel-initial stem (inamwanza) and is commonly written `-mu-`
# before a consonant (inamuhusu). Both are the SAME class member, not extra ones.
_OBJECT_INFIX_ALT = {"m": ("m", "mu", "mw")}
# HOSTS — what must sit in front of the infix for it to BE an infix. Three shapes, kept
# SEPARATE rather than folded into one alternation, and the separation is the safety property:
#
#   affirmative  subject prefix + tense marker        wa+na+NI+kata, i+ta+NI+anza
#   negative     ha- + optional subject + neg tense   ha+i+NI+husu, ha+ku+NI+husu
#   tenseless    hu- (habitual), ku- (infinitive)     hu+NI+kata, ku+NI+husu
#
# THE NEGATIVE BRANCH EXCLUDES `-ku-` AS AN OBJECT, AND THE SWEEP IS WHY. The first version
# put the negative tense in an OPTIONAL slot inside one shared host, and `haKUkata` /
# `haiKUkata` ("did NOT deduct", 4 corpus rows) matched anyway — the regex simply backtracked,
# declined to spend `ku` on the tense slot, and spent it on the object slot instead. An
# optional group cannot forbid anything. The `ku` in `hakukata` is the negative PAST MARKER
# and the word contains no object at all.
#
# The cost of the exclusion is `hakukuhusu` ("it did not concern YOU"), which is now unmatched.
# That is a deliberate trade: the form is vanishingly rare, and it is genuinely ambiguous with
# the tense reading even to a human reader, whereas `hakukata` is common and unambiguously not
# object concord. Narrowest form that closes the case, per R17.
_OC_AFFIRMATIVE = r"(?:ni|u|a|tu|m|wa|i|zi|li|ya|ki|vi)(?:na|me|li|ta|ki)"
_OC_NEGATIVE = r"ha(?:tu|wa|ni|u|i|zi|li|ya|ki|vi)?(?:ku|ta|ja|li)?"
_OC_TENSELESS = r"(?:hu|ku)"


def _object_concord(stem: str, vowel_initial: bool = False) -> str:
    """Regex source matching every object-concord form of one verb stem.

    ALL FIVE MEMBERS, ALWAYS — the point of writing the class out is that it cannot be
    half-populated by accident, which is how `_APPLICABILITY_CUES` came to hold three of five
    and how `_NSSF_EMPLOYEE_CUES` came to hold none."""
    infixes = []
    for member in _OBJECT_INFIX:
        for form in _OBJECT_INFIX_ALT.get(member, (member,)):
            # -m- surfaces as -mw- before a vowel and as bare -m-/-mu- before a consonant.
            if vowel_initial and member == "m" and form == "m":
                continue
            if not vowel_initial and form == "mw":
                continue
            infixes.append(form)
    alt = "|".join(sorted(set(infixes), key=len, reverse=True))
    # `ku` is dropped from the negative branch only — see the _OC_NEGATIVE note above.
    alt_no_ku = "|".join(sorted(set(infixes) - {"ku"}, key=len, reverse=True))
    return "|".join((
        rf"\b{_OC_AFFIRMATIVE}(?:{alt}){stem}",
        rf"\b{_OC_NEGATIVE}(?:{alt_no_ku}){stem}",
        rf"\b{_OC_TENSELESS}(?:{alt}){stem}",
    ))


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
                "kumwajiri", "muajiri", "mwajiri", "waajiri", "kibarua", "vibarua", "mtumishi",
                # CONCORD: 1pl counterparts. `tunalipa` is the one with corpus presence
                # (17 rows); the past/perfect pair is the tense gap substring luck misses.
                "tunalipa", "tuliajiri", "tumeajiri",
                # OBJECT CONCORD (nat_04): headcount GROWTH is a payroll statement even when
                # no payroll word is used — "nimeongeza watu sasa tuko kumi na mmoja" names
                # neither mshahara nor mfanyakazi, so this gate rejected it and the SDL levy
                # (already resolved from 'mafunzo') could never reach compute. ONE cue covers
                # the whole inflection family, which is what R17 asks for: `ongeza watu` is a
                # substring of nime-/nili-/nita-/nika-/tume-/tuli-/ku-ongeza watu. Kept as the
                # verb+object pair, never bare `watu` — that word is in 178 corpus rows and
                # most of them are not about employees.
                "ongeza watu"]

# Money 'how-much' cue: a request for a shilling QUANTITY.
#
# CONCORD-1. `shingapi` is the spoken contraction of `shilingi ngapi`, and it was the last
# blocker on BOTH live wrong answers of 2026-08-14: the SDL question that was told "bado una
# wafanyakazi chini ya 10" against a stated 14, and the NSSF question answered TZS 20,000
# against a stated TZS 800,000. `_VERB_MONEY_ASK` cannot reach it — that regex requires
# `<verb> ngapi` with a SPACE, and the contraction removes exactly that space.
#
# Added BARE, unlike `ngapi`, and the difference is not a relaxation of R17. Bare `ngapi` is
# ambiguous (asilimia ngapi, siku ngapi, mara ngapi) which is why it is verb-qualified;
# `shingapi` carries `shilingi` inside it and is money-marked on its own. There is no
# non-money reading of it to guard against.
# A2 (2026-08-15): `jumla inayoenda` — "the total that GOES [to]". nat_09 needed BOTH a levy
# cue and this: it is the one A2 row where the levy word was not the only thing missing, and a
# cue addition alone would have left it on the fact path still answering wrongly.
_MONEY_ASK = ["kiasi gani", "shilingi ngapi", "shingapi", "kinakatwa kiasi", "ni ngapi",
              "gharama gani", "garama gani",       # gh->g variant
              "jumla inayoenda"]
# An EXPLICIT money ask — strong enough to survive a co-occurring rate/time/count ask below.
# `shingapi` belongs here for the same reason it is bare above: it names the currency.
_EXPLICIT_MONEY_ASK = ["kiasi gani", "shilingi ngapi", "shingapi"]
# Non-money quantity asks (rate / time / count) that must NOT count as a money ask.
#
# CONCORD-2. `-ngapi` takes the noun-class prefix of the thing counted, and the class is
# CLOSED: ngapi (cl.9/10), wangapi (cl.2), mingapi (cl.4), mangapi (cl.6), vingapi (cl.8).
# That is the whole set — `yangapi`/`zangapi`/`pangapi` are not Swahili, and an earlier audit
# that listed them was over-enumerating.
#
# WHICH GATE each member belongs to is decided by SEMANTICS, not by the class system. Money
# in Swahili is cl.9/10 (shilingi, fedha, pesa), so a money ask is ALWAYS the bare `ngapi`.
# mingapi/mangapi/vingapi count periods and objects — they are non-money asks, and putting
# them in _MONEY_ASK "for completeness" would be a category error wearing a grammar costume.
# `miaka mingapi` was already here; the bare form generalises it to `miezi mingapi` etc.
_NONMONEY_ASK = ["asilimia ngapi", "siku ngapi", "muda gani", "miaka mingapi", "idadi gani",
                 "wangapi", "mangapi", "mingapi", "vingapi", "mara ngapi"]
# Net-take-home phrasing ("what remains in hand after tax") — a money 'how-much' request
# that never uses an explicit 'kiasi gani'. rc_11's phrasing; caught here so a net-of-PAYE
# question routes to compute deterministically (this is the residual the retired
# extractor-emitted-intent backstop unreliably targeted — now a fixed lexical rule).
_TAKEHOME_ASK = ["kitakachobaki", "kinachobaki", "mkononi", "baada ya kodi", "nitabaki na",
                 "tutabaki na"]                    # CONCORD-3: 1pl counterpart

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
                  # CONCORD: `tunamlipa`/`tunawalipa` were here and their perfect-tense
                  # siblings were not — one class, half enumerated, exactly the pattern.
                  "tunalipa", "tumemlipa", "tumemlipia",
                  "analipwa", "wanalipwa", "analipwaga", "hulipwa", "walipwa"]

# THE EMPLOYEE'S OWN SIDE — the th_16 class asked from the other direction.
#
# Every literal above is the EMPLOYER speaking ("I pay him", "we pay them") or a THIRD PERSON
# being paid ("analipwa", "wanalipwa"). Not one is a worker asking about their OWN wage. So
# "wananilipa laki mbili kwa mwezi je ni halali kisheria" — they pay ME 200,000, is that
# lawful — matched nothing and fell through to fact/RAG, while the employer-side twin
# "namlipa mlinzi wangu 200000 je ni halali" routes to the deterministic minimum_wage answer.
# Measured before it was fixed: scratch/oc_wage_gap.json.
#
# ARGUABLY THE HIGHEST-STAKES QUESTION THIS PRODUCT GETS. th_16's own history says what the
# generative path does with it: of six candidate wordings tried in 2026-08-10, FOUR fabricated
# TZS 765,900 as a legal MAXIMUM wage, and one of the "before" answers instructed an employer
# to claw back lawfully paid wages. A worker asking whether they are being underpaid is exactly
# the person who cannot afford a fabricated number.
#
# TWO PARADIGMS, and both were at ZERO for first person — finding B a third time, in the list
# where it costs the most:
#
#   ACTIVE + object infix   wana-NI-lipa, ana-NI-lipa, wana-TU-lipa, hu-NI-lipa
#   PASSIVE + subject       ni-na-LIPWA, tu-na-LIPWA, u-na-LIPWA   (the list had only the
#                           3sg/3pl `analipwa`/`wanalipwa`/`walipwa`)
#
# HOST-QUALIFIED, for the reason the object-concord commit records: the bare infix+stem nests.
# `_object_concord` requires a subject+tense host, so `analipa` (he PAYS — a levy question,
# deliberately excluded above), `kulipa` (the infinitive), `nilipa`/`walipa`/`tulipa` (I/they/we
# PAID) and `wanalipa` all fail to match, because in every one of them the slot where an object
# infix must sit holds nothing at all.
#
# `-lipia` (the applicative) is NOT generated here: `_object_concord('lipa')` will not match
# `anamlipia`, and the applicative forms that matter are already literals above. Naming the
# stem rather than inferring it is the honest limit recorded in the builder's docstring.
_WAGE_PAY_CONCORD = re.compile(
    _object_concord("lipa")                                   # active + object infix
    + r"|\b(?:ni|tu|u)(?:na|me|li|ta|ki)lipwa"                 # passive + 1st/2nd person subject
    + r"|\bnalipwa|\bnimelipwa")                               # colloquial 1sg present/perfect


def _has_wage_pay_cue(ql: str) -> bool:
    """A pay cue in either direction — the employer paying, or the worker being paid."""
    return any(c in ql for c in _WAGE_PAY_CUES) or bool(_WAGE_PAY_CONCORD.search(ql))


# WHO IS ASKING — needed because the clarification copy addresses somebody, and until the
# concord fix above only employers ever reached it.
#
# Live, straight after that fix shipped: an employee asking "ninalipwa laki moja na nusu je ni
# halali" was answered "niambie MFANYAKAZI WAKO anafanya kazi ya aina gani" — tell me what YOUR
# EMPLOYEE does. The route was right and the audience was wrong, which on this question is its
# own kind of wrong answer: a worker told to describe "your employee" may reasonably conclude
# the service is not for them, at the exact moment they are asking whether they are underpaid.
#
# ASYMMETRIC BY DESIGN. Employer cues WIN. The employer wording is the existing, well-tested
# default, so this flips only on positive worker evidence and never on the absence of employer
# evidence — an ambiguous question keeps the behaviour it has today.
#
# `wangu` ALONE IS NOT WORKER EVIDENCE, and this is the trap in the whole predicate:
# "namlipa mlinzi WANGU 200000" is an EMPLOYER saying "my guard". Only the possessive bound to
# the speaker's OWN wage or OWN employer counts — `mshahara wangu`, `mwajiri wangu`.
_WAGE_WORKER_POSSESSIVE = ["mshahara wangu", "mshahara wetu", "mwajiri wangu", "mwajiri wetu",
                           "ujira wangu", "ujira wetu"]
# The employer's own side, stated explicitly rather than inferred from the absence of the above.
_WAGE_EMPLOYER_CUES = ["mfanyakazi wangu", "wafanyakazi wangu", "mfanyakazi wetu",
                       "wafanyakazi wetu", "namlipa", "ninalipa", "nawalipa", "namlipia",
                       "nimemlipa", "nimemlipia", "tunamlipa", "tunawalipa", "kumlipa",
                       "kuwalipa", "humlipa", "tumemlipa", "tumemlipia", "nimemwajiri",
                       "mwajiri, ", "kama mwajiri", "mimi ni mwajiri",
                       # CONCORD counterparts, added because the generative test demanded
                       # them and was RIGHT to: every one is still the speaker doing the
                       # paying, which is what makes this list employer-side.
                       "tunalipa", "nimekulipa", "nimewalipa", "tunakulipa", "tumekulipa",
                       "tumewalipa", "tumemwajiri", "nimekuajiri", "nimewaajiri",
                       "tumekuajiri", "tumewaajiri"]
# THE OBJECT INFIX ALONE DOES NOT SAY WHO IS ASKING — subject and object together do, and the
# first version of this regex got it wrong in a way the generative concord test caught:
#
#   wana-NI-lipa   they pay ME     -> the speaker is PAID      worker
#   wana-TU-lipa   they pay US     -> the speaker is PAID      worker
#   nime-KU-lipa   I have paid YOU -> the speaker PAYS         EMPLOYER  <- was flagged worker
#   wana-KU-lipa   they pay YOU    -> the addressee is paid    worker (asking on their behalf)
#
# `-ni-` and `-tu-` are unambiguous: nobody pays themselves, so whoever the subject is, the
# speaker is on the receiving end. `-ku-` is ambiguous and resolves on the SUBJECT — so its
# branch takes third-person subjects only. `-m-`/`-wa-` are the employer paying somebody else
# and are excluded entirely, even though `_WAGE_PAY_CONCORD` matches them for ROUTING.
_OC_SUBJ_3RD = r"(?:a|wa|i|zi|li|ya|ki|vi)(?:na|me|li|ta|ki)"
_WAGE_WORKER_CONCORD = re.compile(
    "|".join((
        rf"\b{_OC_AFFIRMATIVE}(?:ni|tu)lipa",        # -ni-/-tu-: any subject
        rf"\b{_OC_SUBJ_3RD}kulipa",                  # -ku-: third-person subject only
        rf"\b{_OC_TENSELESS}(?:ni|tu)lipa",
        # PASSIVE, 1sg/1pl ONLY. Bare `u-` was here and the sweep killed it: `u-` is also the
        # class 3/11 subject agreement, so `ushuru unalipwa lini`, `mchango unalipwa TRA`,
        # `umeme unalipwa VAT` all read as "YOU are paid". 28 corpus rows, none of them a
        # person. Harmless today because this predicate is only consulted on the wage route,
        # but a wage question mentioning `ushuru` would have picked up worker copy.
        # The cost is the genuine 2sg "unalipwa 190000" — which stays on the EMPLOYER copy,
        # the safe default, and is ambiguous anyway (an employer may equally be checking).
        r"\b(?:ni|tu)(?:na|me|li|ta|ki)lipwa",
        r"\bnalipwa|\bnimelipwa",                    # colloquial 1sg present/perfect
    )))


def wage_asker_is_worker(text: str) -> bool:
    """True iff the minimum-wage question is asked BY the person whose wage it is."""
    ql = text.lower()
    if any(c in ql for c in _WAGE_EMPLOYER_CUES):
        return False
    return (bool(_WAGE_WORKER_CONCORD.search(ql))
            or any(c in ql for c in _WAGE_WORKER_POSSESSIVE))
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
                        "nitaadhibiwa", "nitaazibiwa",          # dh->z variant
                        "nitatozwa faini", "nitafungwa", "nakosea kisheria",
                        # CONCORD: `tunakiuka` was added by hand at some point and its four
                        # future-tense siblings were not — the same class, half closed.
                        "tutaadhibiwa", "tutaazibiwa", "tutatozwa faini", "tutafungwa"]
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
                 "tumefika kiwango cha vat",            # CONCORD: 1pl counterpart
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
#
# CONCORD. `mauzo yetu`/`mapato yetu`/`tumeuza` were here; the other eight 1pl forms were
# not. This is the list where the omission cost the most, because the ownership gate is what
# makes the VAT comparison run at all: a trader writing "biashara YETU ina mauzo ya TZS
# 250,000,000" stated their own turnover in plain Swahili and got the fact path.
_OWN_TURNOVER_CUES = ["mauzo yangu", "mauzo ya biashara yangu", "mauzo ya duka langu",
                      "mapato yangu", "mzunguko wangu", "biashara yangu ina mauzo",
                      "biashara yangu imepata", "biashara yangu inaingiza", "duka langu lina",
                      "duka langu linaingiza", "nimeuza", "ninauza", "nauza", "naingiza",
                      "ninaingiza", "nimepata mauzo", "tumeuza", "mauzo yetu", "mapato yetu",
                      "mauzo ya biashara yetu", "mauzo ya duka letu", "mzunguko wetu",
                      "biashara yetu ina mauzo", "biashara yetu imepata", "duka letu lina",
                      "tumepata mauzo",
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
# CONCORD: every member here is a perfect-tense `nime-` statement, and a company says
# `tume-`. Not one 1pl form was present, and the substring luck does not reach the perfect.
_VAT_REGISTERED_CUES = ["nimeshasajili vat", "nimesajili vat", "nimejisajili vat",
                        "nimesajiliwa vat", "nimeshajisajili vat", "niko kwenye vat",
                        "nina namba ya vat", "tuna namba ya vat",
                        "vat registered", "nimesajiliwa kwa vat",
                        "tumeshasajili vat", "tumesajili vat", "tumejisajili vat",
                        "tumesajiliwa vat", "tumeshajisajili vat", "tumesajiliwa kwa vat"]

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


# === PRESUMPTIVE INCOME TAX — the tax a duka owner actually pays ==========================
# Coverage item, not a defect fix: the 2026-08-16 coverage measurement found 12 of 12
# questions from an ordinary trader's month reaching NO deterministic route and having NO
# fact behind them, and presumptive tax is the most common of those. It is the first route
# added to close a coverage gap rather than a wrong answer.
#
# NARROW BY CONSTRUCTION (R17 step 4). Named presumptive vocabulary only, plus one
# context-gated second path. `makadirio` alone is NOT here: it is the ordinary word for
# "estimate" and appears in budget/valuation senses; `kodi ya mapato` alone is NOT here
# either — it covers employment and corporate income tax, neither of which this engine can
# answer. The second path therefore demands BOTH a business-income-tax phrase AND the
# trader's own-turnover claim, the same ownership gate the VAT arm needed.
_PRESUMPTIVE_CUES = ["kodi ya makadirio", "kodi ya makisio", "makadirio ya kodi ya mapato",
                     "kodi ya kadirio", "presumptive tax", "presumptive income tax"]
_BUSINESS_INCOME_TAX_CUES = ["kodi ya mapato ya biashara", "kodi ya mapato ya duka",
                             "kodi ya biashara yangu", "kodi ya biashara yetu",
                             "business income tax",
                             # BARE `kodi ya mapato` (added 2026-08-23). The qualified forms
                             # above require the user to say "...YA BIASHARA / YA DUKA", so the
                             # commonest phrasing of the commonest duka tax question —
                             # "mauzo yangu ni milioni 30... nalipa KODI YA MAPATO kiasi gani?"
                             # — fell to the fact path while the technical term `makadirio`
                             # reached the engine. AN ENGINE REACHABLE ONLY BY THE TECHNICAL
                             # TERM SERVES THE USERS WHO LEAST NEED IT.
                             #
                             # It is broad on its own, which is why it is safe only in the
                             # conjunction it sits in: a turnover cue AND a money magnitude AND
                             # no veto. Sweep of 475 corpus rows: ZERO moved. The one hazard the
                             # corpus could not show was found by an authored probe — see
                             # _PRESUMPTIVE_VETO's entity arm.
                             "kodi ya mapato"]

# THE OWNERSHIP GATE, AND IT IS NOT A COPY OF THE VAT ONE. The first version of this route
# required only {presumptive cue + magnitude} and the 5,595-row sweep diverted FOUR corpus
# rows, THREE of which would have been answered wrongly:
#   * "...ina mapato ya TZS 40,000,000 ... Ninatumia mfumo wa kodi ya makisio?" — asks WHICH
#     REGIME applies, and states `mapato` (income), not `mauzo` (turnover)
#   * "...nitajua vipi ikiwa ninapaswa kutumia presumptive tax AU MFUMO WA KAWAIDA?" — the
#     ELECTION question of para 2(1)(c), which no amount answers
#   * "'presumptive tax rate class a' kwa magari ya abiria ... TZS 250,000" — the TRANSPORT
#     schedule (para 2(5)), which this engine does not implement; the 250,000 is a TAX figure,
#     and computing on it returns "TZS 0" to a daladala owner
# Hence: turnover vocabulary only. `mapato yangu` is deliberately ABSENT even though the VAT
# arm carries it — `mapato` can mean profit, and 3.5% of profit is not 3.5% of turnover. The
# narrower list is the cost of the engine's authority.
_PRESUMPTIVE_TURNOVER_CUES = ["mauzo yangu", "mauzo yetu", "mauzo ya biashara yangu",
                              "mauzo ya biashara yetu", "mauzo ya duka langu",
                              "mauzo ya duka letu", "biashara yangu ina mauzo",
                              "biashara yetu ina mauzo", "duka langu lina",
                              "duka letu lina", "nauza", "ninauza", "tunauza",
                              "nimeuza", "tumeuza", "mzunguko wangu", "mzunguko wetu",
                              "my turnover", "my sales"]

# Other schedules under the SAME paragraph that this engine does not implement, and the
# regime-choice question that no figure answers. Vetoing is the honest behaviour: para 2(5)'s
# per-vehicle table is a different computation, and returning the turnover table's answer for
# it is a wrong number with the engine's authority behind it.
_PRESUMPTIVE_SCHEDULE_VETO_PATTERN = (
    r"daladala|abiria|magari|gari\s+la\s+biashara|bodaboda|bajaji|teksi|\btaxi\b|"
    r"class\s+[abcd]\b|tour\s+service|kubeba\s+mizigo|\btani\b|tonne|"
    r"au\s+mfumo\s+wa\s+kawaida|nitajua\s+vipi")

# ENTITY ARM (2026-08-23), required by the bare `kodi ya mapato` cue and found by an AUTHORED
# PROBE after a completely clean 475-row corpus sweep — R17 exactly.
#
# Presumptive is First Schedule para 2's regime for a resident INDIVIDUAL. A company pays 30% on
# PROFIT. And `_PRESUMPTIVE_TURNOVER_CUES` contains "nauza", which is a SUBSTRING of "i-nauza" —
# so "Kampuni yangu INAUZA bidhaa za milioni 50" already satisfied the turnover gate before this
# cue existed. With the bare cue and without this arm, probe pic_04 routed a company to the
# individual turnover table: a wrong figure carrying the engine's authority. No corpus row has
# that shape, so nothing but the probe could have found it.
#
# KEPT AS ITS OWN NAMED PATTERN, and composed below, for the same reason ROUTING-GAP-B's cues
# are: a blast-radius sweep must be able to subtract exactly this arm to reconstruct the
# before-state. An earlier sweep inlined a mechanism it could not turn off and reported a false
# zero radius for it.
_PRESUMPTIVE_ENTITY_VETO_PATTERN = (
    r"kampuni|shirika|\bcompany\b|\bltd\b|\bplc\b|ubia|ushirikiano\s+wa\s+kibiashara|"
    r"partnership")

_PRESUMPTIVE_VETO = re.compile(
    _PRESUMPTIVE_SCHEDULE_VETO_PATTERN + r"|" + _PRESUMPTIVE_ENTITY_VETO_PATTERN)

# RECORD-KEEPING, the categorical axis of the statutory table. Consulted ONLY inside the
# presumptive branch, so a false positive cannot leak into another route — but it CAN change
# a figure, so both polarities are explicit and neither is a default: absent evidence returns
# None and the caller clarifies (and only where the answer would differ — see
# rules_engine.presumptive.records_status_matters).
_KEEPS_RECORDS_CUES = ["natunza kumbukumbu", "ninatunza kumbukumbu", "tunatunza kumbukumbu",
                       "naweka kumbukumbu", "ninaweka kumbukumbu", "tunaweka kumbukumbu",
                       "nina vitabu vya mahesabu", "tuna vitabu vya mahesabu",
                       "nina kumbukumbu za mauzo", "tuna kumbukumbu za mauzo",
                       "natunza hesabu", "tunatunza hesabu",
                       "i keep records", "keeping records", "keep proper records"]
_NO_RECORDS_CUES = ["situnzi kumbukumbu", "hatutunzi kumbukumbu", "siwezi kutunza kumbukumbu",
                    "sina kumbukumbu", "hatuna kumbukumbu", "sina vitabu vya mahesabu",
                    "hatuna vitabu vya mahesabu", "siweki kumbukumbu", "hatuweki kumbukumbu",
                    "situnzi hesabu", "sina hesabu za maandishi",
                    "i do not keep records", "i don't keep records", "no records"]

# EXCLUDED SERVICES — para 2(1)(a) as amended by FA2022 s.72(a)(i). A FIRST-PERSON
# self-description only. The cost of a false positive here is telling a trader the regime
# does not apply to them, which is a wrong answer carrying the engine's authority, so the
# list refuses anything that could describe a customer, a supplier or a third party.
_EXCLUDED_SERVICE_CUES = ["mimi ni mshauri", "mimi ni wakili", "mimi ni daktari",
                          "mimi ni mhandisi", "mimi ni mkandarasi", "mimi ni mkufunzi",
                          "mimi ni mtaalamu", "mimi ni mhasibu",
                          "biashara yangu ni ushauri", "biashara yetu ni ushauri",
                          "natoa huduma za ushauri",
                          "natoa huduma za kitaalamu", "natoa mafunzo",
                          "kampuni yangu ya ujenzi", "kampuni yetu ya ujenzi",
                          "biashara yangu ya ujenzi", "biashara yetu ya ujenzi",
                          "i am a consultant", "independent professional"]


def keeps_records(text: str):
    """True | False | None — whether the trader states they keep books of account.

    None means UNSTATED and is never treated as False: the no-records column is the more
    expensive one at low turnover (TZS 100,000 against TZS 30,000 at a turnover of 5M), so
    defaulting would overstate the bill for exactly the trader least able to check it."""
    ql = text.lower()
    if any(c in ql for c in _NO_RECORDS_CUES):
        return False
    if any(c in ql for c in _KEEPS_RECORDS_CUES):
        return True
    return None


def states_excluded_service(text: str) -> bool:
    """True when the asker describes THEMSELVES as outside the presumptive regime."""
    ql = text.lower()
    return any(c in ql for c in _EXCLUDED_SERVICE_CUES)


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
    # unless an explicit money phrase is also present. The override list is named rather
    # than spelled inline because CONCORD-1 added a third member to it: a question can
    # legitimately carry both a count ask and a money ask ("maduka mangapi ... tunalipa
    # shingapi"), and forgetting to widen this test alongside _MONEY_ASK would have made
    # the contraction fix silently conditional on no count word being present.
    if any(nm in ql for nm in _NONMONEY_ASK) and not any(
            m in ql for m in _EXPLICIT_MONEY_ASK):
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


def all_natural_levies(text: str):
    """Every levy resolved by NATURAL CUE, in canonical _LEVY_CUES order.

    ROUTING-GAP-A (2026-08-22). `all_explicit_levies` had no natural-cue counterpart, so
    `Orchestrator._fan_out_multi_levy` — which fans a multi-levy compute part into one compute
    per levy — was structurally blind to nicknamed levies. `_natural_levy` returns the FIRST
    cue match and nothing records the rest.

    THE MEASURED CONSEQUENCE: nat_23 ("...ile ya mafunzo na ile ya uzeeni") routes to compute
    as `nssf` because 'uzeeni' precedes 'mafunzo' in _LEVY_CUES order, the NSSF engine computes
    correctly, and SDL is silently dropped. Confirmed on the live v16 pipeline, not inferred —
    the reply carried NSSF's deterministic working and no SDL at all
    (eval/results/ss8_forced_facts_v16_2026_08_22.json).

    Deliberately NOT a change to `_natural_levy` itself: detect_intent must keep returning ONE
    intent, because every caller downstream assumes a single computation_type. This is the
    enumeration the fan-out needs, exposed alongside it, exactly as all_explicit_levies sits
    alongside _explicit_levy. Pure string logic, no model call.
    """
    ql = text.lower()
    out = []
    for levy, cues in _LEVY_CUES:
        if levy not in out and any(c in ql for c in cues):
            out.append(levy)
    return out


def all_compute_levies(text: str):
    """Every levy named in the text, explicit first then natural, no duplicates.

    What `_fan_out_multi_levy` fans out on. Explicit names lead so the ordering the
    D-DECOMP-1 fan-out already relied on is preserved byte-for-byte for questions that name
    their levies outright — a question with >=2 explicit levies produces the identical list it
    did before this function existed.
    """
    explicit = all_explicit_levies(text)
    return explicit + [lv for lv in all_natural_levies(text) if lv not in explicit]


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
    if (_has_money_magnitude(ql) and _has_wage_pay_cue(ql)
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
    # PRESUMPTIVE INCOME TAX. Placed AHEAD of the VAT/EFD block deliberately: its vocabulary
    # is named and specific ("kodi ya makadirio"), while the VAT/EFD block can be entered by a
    # question that merely mentions sales. A message asking both ("mauzo yangu ni milioni 30 —
    # nahitaji EFD, na kodi ya makadirio ni ngapi?") is a decomposition case, and if it is not
    # split the amount-ask is the one with a figure attached. Requires a money magnitude: a
    # definition question ("kodi ya makadirio ni nini?") has nothing to compute and keeps its
    # fact route.
    if (_has_money_magnitude(ql)
            and any(c in ql for c in _PRESUMPTIVE_TURNOVER_CUES)
            and not _PRESUMPTIVE_VETO.search(ql)
            and (any(c in ql for c in _PRESUMPTIVE_CUES)
                 or any(c in ql for c in _BUSINESS_INCOME_TAX_CUES))):
        return "presumptive"

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

# ROUTING-GAP-B (2026-08-22), first form. Kept as its OWN named list, appended below, so a
# blast-radius sweep can subtract exactly this set to reconstruct the before-state. An
# earlier version of the sweep inlined these into _APPLICABILITY_CUES and could not turn
# them off, so it reported a zero blast radius for this form — a false clean sweep, which is
# the one result R17 says never to trust.
_GAP_B_APPLICABILITY_CUES = [
    # The everyday yes/no form "je nalipa X" — "do I pay X" — matched NOTHING, so an
    # applicability question fell to the fact path and the model free-generated the answer.
    #
    # THIS IS NOT A NICKNAME GAP, which is why it is here rather than in _LEVY_CUES. Probe
    # nick_03 names the levy OUTRIGHT — "nimeajiri watu 5 tu je nalipa SDL" — and still routed
    # to fact, blocked in path 1 for carrying no compute-intent cue. Framing this workstream as
    # "nicknamed multi-levy decomposition" would have fixed the fan-out and left this untouched.
    # Measured: eval/results/nickname_routing_measurement.json.
    #
    # QUESTION-PARTICLE QUALIFIED, never a bare "nalipa"/"nilipe". Bare forms appear in
    # deadline and mechanism facts ("deadline ya kulipa michango"), which is the same reason
    # the cues above are all multi-word. "je " anchors it to an actual yes/no question.
    "je nalipa", "je nilipe", "je tunalipa", "je tulipe",
    "je nachangia", "je tunachangia", "je nalazimika", "je tunalazimika",
]

_APPLICABILITY_CUES = _APPLICABILITY_CUES + _GAP_B_APPLICABILITY_CUES

# ROUTING-GAP-B, second form: "nilipe nini kati ya A na B" — WHICH of these do I pay.
# nat_24's shape. Not a money 'how-much' ask (no shilling quantity is requested) and not an
# applicability cue above (it presupposes SOME obligation and asks which), so it satisfied
# neither gate and fell to fact, where it produced a bare "Thibitisha na TRA" with all three
# correct facts forced into context.
#
# Requires the CHOICE frame ("kati ya" / "au"), never a bare "nilipe nini" — without the
# choice frame the question is an open-ended "what do I pay", which has no single deterministic
# answer and belongs on the fact path.
_WHICH_LEVY_ASK = re.compile(
    r"\b(?:ni|tu)(?:lipe|nalipa|talipa|takiwa\s+kulipa)\s+(?:nini|kipi|gani)\b"
    r"[^?]{0,60}?\b(?:kati\s+ya|au)\b")

# ROUTING-GAP-B, third form: "asilimia tatu na nusu ya nini" — a stated RATE whose BASE is
# being asked for. nat_05's shape, and the wrong-base trap: the question states a machine
# purchase and a headcount, and the rubric wants the answer to name gross payroll as the base
# and ask for it. `asilimia ngapi` sits in _NONMONEY_ASK so this could never be a money ask,
# and it carries no applicability cue, so it fell to fact.
#
# Narrow by construction: a percentage token, then 'ya nini' within a short window. "asilimia
# ngapi ya mshahara" cannot match (no 'nini'), and a bare 'ya nini' cannot match either.
_RATE_BASE_ASK = re.compile(r"asilimia\b[^?]{0,40}?\bya\s+nini\b")

# OBJECT CONCORD on the applicability verbs. The three literals above are the `ina-` present
# tense of THREE of the five class members on ONE verb — the signature of failure-driven
# growth, in the one list that had already applied the paradigm once. Two independent gaps:
#
#   MEMBERS.  `-m-` ("inamhusu") and `-wa-` ("inawahusu") were absent, as were the `mu`/`mw`
#             spellings of `-m-`, which are the commoner ones in this corpus.
#   HOSTS.    Only `ina-` was covered. `itanihusu` (future), `hainihusu` (negative — "does it
#             NOT concern me" is an applicability question), `zinanihusu` (cl.10 levies) and
#             the attested infinitive `kunihusu` / `kuwahusu` ("SDL inaanza KUNIHUSU") all
#             missed. Corpus-attested, not hypothetical.
#
# -ANZA is the SECOND VERB, and it is here because nat_04 says `inaNIanza` — "when does it
# START on me". The verb axis is open (see the _object_concord docstring), so this is two
# named stems and not a general mechanism; `-anza` is vowel-initial, so `-m-` surfaces as
# `-mw-` and the builder handles it rather than the author remembering to.
#
# WHY A `lini` QUESTION IS AN APPLICABILITY QUESTION. "inanianza lini" presupposes the levy
# applies and asks from when. The deterministic applicability answer ("SDL applies — you have
# 11 employees, the threshold is 10") is correct and is what the probe expects; the amount
# path, where this lands today, demands a salary that no answer to it needs.
_APPLICABILITY_CONCORD = re.compile(
    "|".join((_object_concord("husu"), _object_concord("anza", vowel_initial=True))))


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
    return (any(cue in ql for cue in _APPLICABILITY_CUES)
            or bool(_APPLICABILITY_CONCORD.search(ql))
            # ROUTING-GAP-B: the which-of-these and rate-base forms. Both sit behind the
            # money-ask veto above, exactly like every other cue here, so a question that
            # does ask for a shilling quantity keeps the amount path.
            or bool(_WHICH_LEVY_ASK.search(ql))
            or bool(_RATE_BASE_ASK.search(ql)))


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

# OBJECT CONCORD — item C, the wrong number this closes.
#
# Every literal above is THIRD PERSON. The list had SEVEN members and ZERO first-person ones,
# so nat_08 — "wanaNIkata kiasi gani kwenye mshahara WANGU" — matched nothing, fell to the
# `total` default and was answered TZS 130,000 where the employee share is TZS 65,000. It has
# been live and wrong since the party resolver shipped.
#
# THIS IS WHY IT SURVIVED THE 2026-08-15 CONCORD CLOSURE, and the reason generalises:
# `test_every_cue_with_a_person_form_has_its_concord_counterpart` derives a counterpart FROM
# AN EXISTING MEMBER. A list at 0% has nothing to derive from, so a generative completeness
# test closes PARTIAL coverage and is structurally blind to ABSENT coverage. Every list that
# closure fixed was one somebody had already half-populated. The census test added in
# tests/test_concord_closure.py is the fix for that, and it matters more than these cues.
#
# TWO PARADIGMS, ONE MEANING — "money taken out of somebody's pay".
#   ACTIVE, object infix:   wana-NI-kata / ana-M-kata / wana-TU-kata / ...
#   PASSIVE, subject prefix: ni-na-KATWA / tu-na-KATWA / a-na-KATWA / u-na-KATWA
# The passive family is the same absence seen from the other side: `anayokatwa` was present
# (3sg relative) and not one of the person-marked forms was.
#
# THE SEMANTIC WARRANT, which is what makes this safe rather than merely grammatical:
# under the NSSF Act the employee's 10% is DEDUCTED FROM THE WAGE and the employer's 10% is
# PAID BY THE EMPLOYER — it is not a deduction at all. So "how much is deducted from <a
# person>'s pay" is ALWAYS the employee share, whoever is asking. That is why a `-wa-`/`-m-`
# form (an EMPLOYER asking about their staff) still resolves to 'employee' and is not a bug.
#
# PRECEDENCE PROTECTS THE TOTAL. nssf_party tests TOTAL first and EMPLOYER second, so a
# "jumla ya michango" or "mwajiri anachangia" question never reaches this branch.
_NSSF_EMPLOYEE_CONCORD = re.compile(
    _object_concord("kat")                                  # active + object infix
    + r"|\b(?:ni|tu|u|a|wa|m|i|ki|zi)(?:na|me|li|ta|ki)katwa"   # passive + personal subject
    + r"|\bnakatwa|\btunakatwa")                            # colloquial 1sg present, and 1pl


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
    if any(cue in ql for cue in _NSSF_EMPLOYEE_CUES) or _NSSF_EMPLOYEE_CONCORD.search(ql):
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

# ===========================================================================
# SAFETY-2 / D-RESIDENCY-1 (2026-08-15) — WHY THIS IS A CLARIFICATION AND NOT A CUE.
# ===========================================================================
# The tracked entry (2026-08-06) proposed extending _PAYE_NONRESIDENT_CUES with permit and
# foreignness phrasings — "hana residence permit", "mfanyakazi wa kigeni", "amekuja kutoka",
# "yuko kwa muda". Measurement disqualified that plan on three independent grounds.
#
# 1. CITIZENSHIP IS NOT RESIDENCY, and the proposed cues confuse them. Tanzanian tax
#    residency is decided by PRESENCE (a permanent home plus presence in the year, or 183
#    days, or an average 122 days over three years), never by nationality. A Kenyan who has
#    lived in Dar for five years is a RESIDENT and pays progressive bands; a Tanzanian
#    citizen living abroad may be non-resident. So `si raia wa tanzania`, `mfanyakazi wa
#    kigeni`, `mgeni` and `expatriate` are not evidence of non-residency at all — they are a
#    category error, and shipping them would create wrong numbers with the engine's authority
#    behind them, which is exactly the defect being fixed.
#
# 2. WE DO NOT OWN THE TEST. scripts/locked_facts.json carries the non-resident RATE
#    (`paye_nonresident_flat_rate`, 15% final withholding) and no definition of who is a
#    non-resident. There are ZERO corpus occurrences of the 183-day test. A cue list cannot
#    encode a rule the corpus has never verified, and R2/R4 discipline says do not invent one.
#
# 3. THE CORPUS SAYS THE TRADE IS BAD. 144 corpus rows route to `paye`; 8 mention
#    foreignness. Three already resolve correctly through the explicit `asiye mkazi` cue, one
#    is the deferred mixed-residency case, one is the nat_16 defect — and THREE would be
#    BROKEN by the proposed cues:
#      * "Mfanyakazi mgeni anapata mshahara wa USD 5,000" — foreign, residency never stated
#      * "...analipwa laki sita kwa mwezi, PAYE ni ngapi, na kama MGENI angependa..." — the
#        foreigner is a hypothetical aside, not the taxpayer
#      * "Mshahara ... unapoingia kwenye KIBALI kikubwa cha PAYE" — here `kibali` means
#        BRACKET, not permit. A bare `kibali` cue reads a tax band as an immigration document.
#    A fix that breaks three correct answers to fix one wrong one is not a fix.
#
# AND THE COST IS ASYMMETRIC IN THE DIRECTION THAT MATTERS. A false NON-resident detection
# applies flat 15% to a resident, and at the salaries our users actually have that is far
# worse than the bug it would fix:
#      TZS   300,000   resident 2,400   -> flat 45,000   = 18.75x OVERCHARGE
#      TZS 4,000,000   resident 1,028,000 -> flat 600,000 = the tracked defect (0.58x)
# The bug overcharges one high earner. The proposed fix would overcharge many low ones.
#
# SO THIS DETECTS ONLY *AMBIGUITY*, AND DECLINES. It fires on residency-ADJACENT permit
# language — never on nationality, never on bare `kibali` — and routes to a clarification
# instead of computing either figure. That is honest for nat_16 specifically: "hana residence
# permit YA KUDUMU" says the engineer lacks PERMANENT residency and says nothing about days
# present, so it does not establish non-residency either. TZS 600,000 would also be a guess.
# Asking is the only answer the facts support.
_PAYE_RESIDENCY_UNCLEAR_CUES = [
    "hana residence permit", "hana kibali cha ukaazi", "hana kibali cha ukazi",
    "hana kibali cha kuishi", "hana kibali cha makazi", "hana ukaazi", "hana ukazi",
    "hana makazi ya kudumu", "si mkazi wa kudumu", "siyo mkazi wa kudumu",
    "sio mkazi wa kudumu", "hana ukaazi wa kudumu", "no residence permit",
]


def _strip_unclear_spans(ql: str) -> str:
    """Blank out the residency-AMBIGUOUS phrases before any explicit cue is tested.

    ⚠️ THIS EXISTS BECAUSE `si mkazi wa kudumu` CONTAINS `si mkazi`, AND THEY ARE DIFFERENT
    CLAIMS. "Not a PERMANENT resident" is an immigration status; "not a resident" is a tax
    determination. Substring matching collapses the narrow claim into the broad one, so
    before this the engine read a permanent-permit statement as a settled non-residency
    finding and applied flat 15% — a wrong number with the engine's authority on it, from
    the same family as the defect this whole item is about, and pre-existing.

    Third instance today of the same hazard (`naagiza bidhaa` inside `tunaagiza bidhaa`;
    `nauza` inside `tunauza`). Substring matching over a hand-written cue list is convenient
    exactly until two phrases in the language nest, and then it is silent."""
    for c in _PAYE_RESIDENCY_UNCLEAR_CUES:
        ql = ql.replace(c, " ")
    return ql


def paye_residency_unclear(text: str) -> bool:
    """True when the question raises residency WITHOUT settling it.

    Suppressed when an explicit residency cue survives `_strip_unclear_spans` — i.e. the user
    settled it somewhere OTHER than inside the ambiguous phrase itself. If they already said
    `asiye mkazi` or `ni mkazi`, there is nothing to ask. Pure string logic."""
    ql = text.lower()
    if not any(c in ql for c in _PAYE_RESIDENCY_UNCLEAR_CUES):
        return False
    rest = _strip_unclear_spans(ql)
    if any(c in rest for c in _PAYE_NONRESIDENT_CUES):
        return False
    if any(c in rest for c in _PAYE_RESIDENT_CUES):
        return False
    return True


def paye_resident(text: str) -> bool:
    """True = resident (progressive bands, the default); False = non-resident (flat 15%).

    Only a negated-residency cue flips to non-resident. If a resident is ALSO named
    (mixed-residency, two people), the scalar can't represent both — stay resident-default
    and let the decompose/merge path handle it (eval_326). Default True is byte-identical to
    the engine's prior single behaviour, so unmatched questions are unchanged. Pure string
    logic, no model call.

    SAFETY-2: the ambiguous spans are blanked FIRST, so `si mkazi wa kudumu` no longer reads
    as `si mkazi`. This call site is reached only after the orchestrator's clarification exit
    has declined the ambiguous case, but `compute_paye_each` also calls this and must not
    keep the substring bug."""
    ql = _strip_unclear_spans(text.lower())
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

"""Unit tests for chike.routing — the deterministic Candidate-C router (ADR 0001 Phase A).

Fully offline (pure string logic). Covers the two paths (explicit levy + natural inference),
the boundary discriminators that defeated the keyword/embedding candidates, and the OOC
controls that must never route to compute.
"""

from chike import routing


# --- explicit path (named levy + number) -----------------------------------

def test_explicit_levy_with_number_routes_to_that_type():
    assert routing.detect_intent("SDL kwa wafanyakazi 15 wenye jumla ya mshahara 6,750,000") == "sdl"
    assert routing.detect_intent("NSSF ya mshahara wa 800,000 ni ngapi") == "nssf"


def test_explicit_levy_without_number_does_not_force_compute():
    # A named levy but no figure is a definition/rate question -> fact.
    assert routing.detect_intent("SDL ni ngapi") == "none"


# --- natural path (Candidate C: number + payroll + money-ask) ---------------

def test_natural_compute_infers_levy_from_generic_cue():
    assert routing.detect_intent(
        "Jumla ya mishahara milioni nne, bima ya ajali kazini ninalipa kiasi gani?") == "wcf"
    assert routing.detect_intent(
        "Mshahara ni laki tano, kodi ya mapato inayokatwa ni kiasi gani?") == "paye"


def test_generic_deductions_route_ambiguous_multi():
    # 'makato yote' is compute-intent but the specific levy is unresolved.
    assert routing.detect_intent(
        "Wafanyakazi kumi na mmoja, mishahara milioni saba, makato yote ni kiasi gani?"
    ) == "ambiguous_multi"


def test_incidental_digit_with_no_levy_word_is_fact_not_ambiguous_multi():
    # eval_240 shape: a pure fact lookup whose only digit is an incidental gazette number
    # ('GN 605A') plus a payroll word + 'kiasi gani' must NOT be pulled into compute — it has
    # no levy/obligation word, so it routes to fact/RAG, never a spurious 'which levy?' clarify.
    assert routing.detect_intent(
        "GN 605A ilibadilisha kima cha chini cha mshahara wa sekta binafsi kwa wastani wa kiasi gani?"
    ) == "none"


def test_custom_split_with_no_levy_word_is_fact_not_ambiguous_multi():
    # eval_398 shape: self-contained arithmetic with an explicit non-levy custom split
    # ('mgao wa 15% mwajiri na 5%') and no levy/obligation word -> fact/RAG, not ambiguous_multi.
    # (The fixed-rate rules engine cannot produce a custom split anyway.)
    assert routing.detect_intent(
        "Mshahara ni TZS 700,000 na tumekubaliana mgao wa 15% mwajiri na 5% mfanyakazi — "
        "kila upande ni ngapi?"
    ) == "none"


# --- boundary discriminators (same topic, opposite route) -------------------

def test_boundary_amount_vs_threshold():
    # amount asked -> compute; yes/no threshold -> fact
    assert routing.detect_intent(
        "Nina wafanyakazi wanane, mishahara milioni tatu, nalipa kiasi gani kwa tozo la ujuzi?"
    ) == "sdl"
    assert routing.detect_intent(
        "Nina wafanyakazi tisa tu — je bado nawajibika kulipa tozo la mafunzo?") == "none"


def test_boundary_rate_only_is_fact():
    # 'asilimia ngapi' (rate only) must NOT count as a money 'how-much' ask.
    assert routing.detect_intent("Je, mchango wa mwajiri kwenye pensheni ni asilimia ngapi?") == "none"


def test_fixed_fee_decoy_is_not_compute():
    # A published fee lookup ('kiasi gani kwa kila mwezi') with no payroll context -> fact.
    assert routing.detect_intent(
        "Baada ya faili la mwaka la kampuni, tozo la kuchelewa ni kiasi gani kwa kila mwezi?"
    ) == "none"


# --- OOC controls: numeric-looking but must never route to compute ----------

def test_ooc_questions_never_route_to_compute():
    for q in [
        "Niliuza kiwanja changu kwa faida — nalipa kodi kiasi gani kwa faida hiyo?",
        "Naagiza bidhaa kutoka nje — ushuru wa forodha ni kiasi gani?",
        "Nina mgodi mdogo wa dhahabu — mrabaha wa madini ninalipa kiasi gani?",
    ]:
        assert routing.detect_intent(q) == "none"


def test_moja_kwa_moja_idiom_not_a_number():
    # 'moja kwa moja' = 'directly', not the quantity 'one'.
    assert routing._has_number("mwajiri anaweza kulipa moja kwa moja") is False


# --- net-take-home router extension (rc_11: replaces the retired LLM backstop) ---------

def test_net_take_home_phrasing_routes_to_paye_deterministically():
    # rc_11: number + payroll + a PAYE cue, but NO explicit 'kiasi gani' — the money ask is
    # the net-take-home phrasing ('kitakachobaki mkononi baada ya kodi ya mshahara'). This is
    # the case the extractor-emitted-intent backstop targeted and failed on real weights; the
    # deterministic router now handles it, no model call.
    q = ("Mshahara wangu wa mwezi ni milioni moja na nusu. Nataka kujua kitakachobaki "
         "mkononi baada ya kodi ya mshahara.")
    assert routing.detect_intent(q) == "paye"


def test_take_home_cue_needs_payroll_and_number_to_route_compute():
    # 'baada ya kodi' alone, with no payroll context or number, is not a compute route.
    assert routing.detect_intent("Bei ya bidhaa baada ya kodi ni ipi?") == "none"


# --- fabrication guard: is_uncomputable_payroll_amount --------------------------------

def test_guard_fires_on_payroll_amount_ask_with_no_salary():
    # rc_22: payroll context + generic levy ('makato ya mshahara') + money ask ('kiasi gani')
    # but no monetary figure -> guard True (clarify, never fabricate).
    q = ("Nina duka lenye wafanyakazi wanne. Makato ya mshahara ninayotakiwa kulipa "
         "kila mwezi ni kiasi gani?")
    assert routing.detect_intent(q) == "none"          # router abstains (no amount)
    assert routing.is_uncomputable_payroll_amount(q) is True


def test_guard_does_not_fire_on_fee_lookup_or_rate_or_computable_question():
    # Fixed-fee lookup (no payroll context) -> not the guard's business.
    assert routing.is_uncomputable_payroll_amount("BRELA ada ya mwaka ni ngapi?") is False
    # Rate/definition question ('asilimia ngapi' is a non-money ask) stays on the fact path.
    assert routing.is_uncomputable_payroll_amount(
        "Kodi ya mapato kwa mshahara ni asilimia ngapi?") is False
    # A computable payroll question (amount present) routes to compute, never reaches the guard.
    assert routing.is_uncomputable_payroll_amount(
        "Nihesabie SDL kwa wafanyakazi 15 wenye jumla ya mshahara 6,750,000?") is False


# --- applicability-vs-amount predicate (Finding 1) ------------------------------------

def test_is_applicability_question_fires_on_obligation_and_threshold_asks():
    # The six recovery shapes: obligation/threshold phrasing, NO amount ask.
    for q in [
        "Je, mwajiri mwenye wafanyakazi 8 ana wajibu wa kulipa SDL?",                   # eval_121
        "Je, kama nina wafanyakazi 8 tu, bado nalazimika kulipa NSSF?",                 # eval_308
        "Nina mfanyakazi mmoja tu anayelipwa TZS 500,000, je bado nachangia WCF?",      # eval_311
        "Nina wafanyakazi 12 lakini wote ni wa muda (part-time), je bado nafikia "
        "kizingiti cha SDL?",                                                           # eval_368
        "Kampuni yenye wafanyakazi 9 haitakiwi kulipa SDL, sivyo?",                     # eval_393
    ]:
        assert routing.is_applicability_question(q) is True


def test_is_applicability_question_excludes_count_transition_never_guess():
    # eval_124: 'ninaajiri mfanyakazi wa 10 katikati ya mwezi' — the count is CROSSING the
    # threshold, so a static count check would assert a wrong 'haihusiki'. Never-guess: this
    # must NOT take the deterministic applicability path (falls back to a safe clarification).
    assert routing.is_applicability_question(
        "Biashara yangu ina wafanyakazi 9 na ninaajiri mfanyakazi wa 10 katikati "
        "ya mwezi — je, SDL inatakiwa kulipwa mwezi huo huo?") is False


def test_is_applicability_question_excludes_amount_distractor_and_fact_questions():
    # An AMOUNT ask ('kiasi gani') is not applicability — must stay on the amount path.
    assert routing.is_applicability_question(
        "Kampuni ina waajiriwa 9 na mishahara ya TZS 4,000,000 — SDL "
        "inayostahili kulipwa ni kiasi gani?") is False                                 # eval_247
    # A distractor question ('per car') has no obligation cue.
    assert routing.is_applicability_question(
        "Kampuni yangu ina magari 14, WCF inahesabiwa kwa kila gari?") is False         # eval_266
    # Deadline / mechanism FACT questions naming a levy — no obligation-to-pay cue.
    assert routing.is_applicability_question(
        "Je, mchango wa NSSF wa mwajiri (asilimia 10) unakatwa kutoka mshahara "
        "wa mfanyakazi?") is False                                                      # eval_099
    assert routing.is_applicability_question(
        "Je, deadline ya kulipa michango ya NSSF kila mwezi ni siku ya 20 ya "
        "mwezi unaofuata?") is False                                                    # eval_102
    assert routing.is_applicability_question(
        "Je, SDL na PAYE zinalipwa TRA kwa wakati mmoja — siku ya 7 ya mwezi "
        "unaofuata?") is False                                                          # eval_127


# --- explicit-levy money-ask guard (the generic guard on Path 1) ----------------------
# A yes_no/definition/deadline question that merely NAMES a levy and carries an INCIDENTAL
# number (a rate 'asilimia 3.5', a day 'siku 30'/'tarehe 20', a threshold headcount in a
# confirmation 'wafanyakazi 4, sivyo?') must NOT be forced to the compute path (which then
# asks for a salary the answer never uses). It routes to fact/RAG. Mirrors the natural-path
# money-ask guard and the applicability-vs-amount guard.

# A1 — the eight originally-named affected questions now route to fact.
def test_explicit_guard_named_eight_route_to_fact():
    for q in [
        "Je, mchango wa NSSF wa mwajiri (asilimia 10) unakatwa kutoka mshahara wa mfanyakazi?",   # eval_099
        "Je, deadline ya kulipa michango ya NSSF kila mwezi ni siku ya 20 ya mwezi unaofuata?",   # eval_102
        "Je, SDL na PAYE zinalipwa TRA kwa wakati mmoja — siku ya 7 ya mwezi unaofuata?",          # eval_127
        "Kiwango cha WCF ni asilimia 3.5 ya mishahara, sivyo?",                                    # eval_335
        "Kiwango cha juu kabisa cha PAYE ni asilimia 25, sivyo?",                                  # eval_342
        "Ajali ya kazini WCF lazima itolewe taarifa ndani ya siku 30, sivyo?",                     # eval_343
        "PAYE ya mfanyakazi asiye mkazi ni asilimia 30, sivyo?",                                   # eval_344
        "SDL inalipwa ifikapo tarehe 20 ya mwezi kama VAT withholding, sivyo?",                    # eval_345
    ]:
        assert routing.detect_intent(q) == "none"


# A2 — the four additional same-class questions surfaced by the 400 sweep also route to fact.
def test_explicit_guard_additional_rate_and_threshold_confirmations_route_to_fact():
    for q in [
        "Mfanyabiashara anayejitegemea (self-employed) anapojiunga NSSF kwa hiari — "
        "analipa asilimia ngapi ya mchango wake wote (sehemu zote mbili)?",                        # eval_095
        "Kiwango cha mchango wa NSSF ni asilimia 3.5, au ni 0.5?",                                 # eval_337
        "Kizingiti cha SDL ni wafanyakazi 4, sivyo?",                                              # eval_341
        "NSSF ina mgawanyo mmoja tu wa 10 kwa 10 kati ya mwajiri na mfanyakazi, sivyo?",           # eval_348
    ]:
        assert routing.detect_intent(q) == "none"


# A3 — regression locks: genuine compute (a payroll money magnitude, a money-ask, or an
# applicability cue present) MUST still route to its levy, not be hijacked to fact.
def test_explicit_guard_preserves_genuine_compute_questions():
    checks = [
        ("Nina wafanyakazi 11 na mishahara TZS 5,500,000 na nataka kujua SDL na NSSF na "
         "pia je nasajili VAT kama mapato ni TZS 205,000,000?", "sdl"),                           # eval_318
        ("Duka dogo lina wafanyakazi 5, mishahara TZS 1,500,000 — SDL yake?", "sdl"),             # eval_372
        ("Mzee faida ya duka mwezi huu imefika TZS 8,400,000, sasa SDL yangu itakuwa ngapi?",
         "sdl"),                                                                                   # eval_251 (wrong-base, still compute -> clarifies)
        ("Mfanyakazi anapata mshahara wa jumla wa TZS milioni 2 kwa mwezi — je, NSSF "
         "inahusika na mshahara wote?", "nssf"),                                                   # eval_100
        ("Nilipe SDL, NSSF, PAYE na WCF kwa mfanyakazi mmoja mwenye TZS 800,000 — "
         "nionyeshe vyote.", "sdl"),                                                               # eval_320
        ("Nina wafanyakazi 9 na mishahara TZS 3,600,000 — je SDL inanihusu?", "sdl"),             # eval_363 (applicability)
        ("Mshahara wa mfanyakazi ni TZS 300,000, je kujiunga na NSSF ni hiari au lazima?",
         "nssf"),                                                                                  # eval_309
    ]
    for q, expected in checks:
        assert routing.detect_intent(q) == expected


# A4 — _has_money_magnitude truth table: currency/magnitude tokens are a base to compute
# from; a bare rate/day/percentage number is not.
def test_has_money_magnitude_truth_table():
    for pos in ["mishahara TZS 1,500,000", "milioni 2", "laki tano", "elfu hamsini",
                "analipwa dola 1,200", "euro 400", "KES 90,000"]:
        assert routing._has_money_magnitude(pos.lower()) is True
    for neg in ["asilimia 3.5", "asilimia 25", "siku 30", "tarehe 20", "wafanyakazi 4",
                "kwa wakati mmoja siku ya 7"]:
        assert routing._has_money_magnitude(neg.lower()) is False


# A5 — explicit carve-outs: these belong to OTHER, already-built mechanisms and must stay on
# the compute path, NOT be flipped by this guard.
def test_explicit_guard_carve_outs_stay_on_compute():
    # eval_124 — count-transition never-guess (_COUNT_TRANSITION, applicability fix). Stays on
    # compute so its own never-guess clarification (not a fact answer) still fires.
    assert routing.detect_intent(
        "Biashara yangu ina wafanyakazi 9 na ninaajiri mfanyakazi wa 10 katikati ya mwezi — "
        "je, SDL inatakiwa kulipwa mwezi huo huo?") == "sdl"                                       # eval_124
    # eval_263/265/266 — wrong-base (extraction:small_int_as_money). A compute-derivation cue
    # keeps them on compute, where extraction clarifies for the right input (never-guess R8);
    # flipping to fact/RAG would risk fabricating a levy from the wrong base.
    assert routing.detect_intent(
        "Nimetoa invoice 450 mwezi huu, sasa NSSF yangu itakuwaje?") == "nssf"                    # eval_263
    assert routing.detect_intent(
        "Nina matawi 6 nchini kote, PAYE ya wafanyakazi wangu naipataje kutoka idadi hiyo?"
    ) == "paye"                                                                                    # eval_265
    assert routing.detect_intent(
        "Kampuni yangu ina magari 14, WCF inahesabiwa kwa kila gari?") == "wcf"                    # eval_266


# --- NSSF party detection (D-NSSF-1) ----------------------------------------
# nssf_party picks which figure an NSSF amount question asks for: the employee's 10% share,
# the employer's 10% share, or the 20% total. Precise total cues (never bare 'jumla') so the
# gross-salary phrase "mshahara wa jumla" does not misroute a single-party question to total.

def test_nssf_party_employee_framings():
    for q in [
        "Mfanyakazi anapata mshahara wa jumla wa TZS 800,000 — kiasi gani kinakatwa mshahara wake kwa ajili ya NSSF?",  # eval_091
        "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi — mchango wa NSSF wa mfanyakazi ni kiasi gani?",              # eval_241
        "Mfanyakazi mpya analipwa TZS 350,000 kwa mwezi — mchango wake wa NSSF ni kiasi gani?",                        # eval_248
        "Mfanyakazi analipwa laki saba na nusu tu, NSSF anayokatwa ni ngapi?",                                         # eval_274
        "Analipwa mshahara wa wastani, yaani TZS 640,000 — NSSF yake anayokatwa ni ngapi?",                            # eval_282
        "Nataka jibu la haraka: NSSF ya mfanyakazi wa TZS 450,000, na pia deadline ya kuwasilisha",                    # eval_330
        "Mshahara wa meneja ni TZS 2,500,000 kwa mwezi — mchango wake wa NSSF ni ngapi?",                              # eval_386
    ]:
        assert routing.nssf_party(q) == "employee", q


def test_nssf_party_employer_framings():
    for q in [
        "Mfanyakazi ana mshahara wa jumla wa TZS 500,000 kwa mwezi — mwajiri anachangia kiasi gani NSSF kwa sehemu yake",   # eval_090
        "Wafanyakazi 5 kila mmoja anapata TZS 400,000 kwa mwezi — mwajiri anachangia kiasi gani NSSF kwa sehemu yake peke", # eval_092
        "Mfanyakazi analipwa TZS 1,200,000 kwa mwezi — sehemu ya mwajiri ya NSSF ni kiasi gani?",                           # eval_243
        "Nusu ya wafanyakazi 14 wanapata TZS 620,000, nusu wanapata TZS 380,000 — sehemu ya mwajiri ya NSSF?",              # eval_289
    ]:
        assert routing.nssf_party(q) == "employer", q


def test_nssf_party_total_framings():
    for q in [
        "Mshahara ni TZS 800,000 — jumla ya mchango wa NSSF (mwajiri pamoja na mfanyakazi) ni kiasi gani?",  # eval_242
        "Mshahara ni TZS 500,000 — jumla ya michango yote miwili ya NSSF ni kiasi gani?",                    # eval_244
        "Mshahara ni TZS 1,000,000 kwa mwezi — jumla ya mchango wa NSSF ni kiasi gani na umegawanywaje?",    # eval_250
    ]:
        assert routing.nssf_party(q) == "total", q


def test_nssf_party_gross_salary_trap_is_employer_not_total():
    # eval_090: "mshahara wa jumla" (= GROSS salary) contains 'jumla' but the question asks the
    # EMPLOYER's share. A bare-'jumla' total cue would misroute this to total; precise cues +
    # employer precedence keep it 'employer'.
    q = ("Mfanyakazi ana mshahara wa jumla wa TZS 500,000 kwa mwezi — "
         "mwajiri anachangia kiasi gani NSSF kwa sehemu yake")
    assert routing.nssf_party(q) == "employer"


def test_nssf_party_total_rate_with_named_employee_is_total():
    # eval_314: "kiwango cha jumla cha NSSF ... kwa mfanyakazi mwenye mshahara" — names the
    # employee (salary owner) but asks the TOTAL rate. The explicit total cue must win.
    q = "Kiwango cha jumla cha NSSF ni asilimia ngapi kwa mfanyakazi mwenye mshahara wa TZS 950,000?"
    assert routing.nssf_party(q) == "total"


def test_nssf_party_defaults_to_total_when_unmatched():
    # No single-party or total cue -> default 'total' (byte-identical to the engine's prior
    # single behaviour, so unmatched questions are unchanged).
    assert routing.nssf_party("NSSF ya mshahara wa 800,000 ni ngapi") == "total"


# --- PAYE residency detection (D-PAYE-1) ------------------------------------
# paye_resident decides whether a PAYE compute uses resident progressive bands (True) or the
# non-resident flat 15% (False). Only a negated-residency cue flips it; a mixed two-person
# question stays resident-default and defers to decompose/merge.

def test_paye_resident_nonresident_framings():
    for q in [
        "Mfanyakazi asiye mkazi analipwa TZS 5,000,000 kwa mwezi — PAYE yake ni ngapi?",   # eval_367
        "PAYE ya mfanyakazi asiye mkazi ni asilimia 30, sivyo?",                            # eval_344
        "Mtu si mkazi wa Tanzania analipwa TZS 2,000,000 — PAYE yake ni ngapi?",
        "Wasio wakazi wanalipwaje PAYE?",
    ]:
        assert routing.paye_resident(q) is False, q


def test_paye_resident_resident_framings_default_true():
    for q in [
        "Mshahara ni TZS 800,000 — PAYE ni ngapi?",                    # eval_395 family
        "Mfanyakazi analipwa TZS 250,000 kwa mwezi — PAYE inayokatwa ni ngapi?",  # eval_373
        "Meneja wangu analipwa dola 1,200 kwa mwezi, yuko kwenye kundi gani la PAYE?",  # eval_276
    ]:
        assert routing.paye_resident(q) is True, q


def test_paye_resident_mixed_two_person_is_guarded_to_resident_default():
    # eval_326: one resident + one non-resident in the same question. A scalar flag cannot
    # express both — the 'ni mkazi' guard keeps it resident-default (no wrong 15% on the
    # resident half), deferring the two-answer split to the multi-part decompose/merge item.
    q = ("Mfanyakazi ni mkazi analipwa TZS 1,100,000 na mwenzake si mkazi analipwa "
         "TZS 1,100,000 — PAYE ya kila mmoja ni ngapi?")
    assert routing.paye_resident(q) is True


def test_paye_resident_nonresident_cue_does_not_falsely_trip_on_bare_mkazi():
    # 'asiye mkazi' / 'si mkazi' both CONTAIN 'mkazi'; the resident guard uses the precise
    # 'ni mkazi', so a pure non-resident question is NOT mis-guarded back to resident.
    assert routing.paye_resident("mfanyakazi asiye mkazi, PAYE yake?") is False

"""Clarification copy — the user-facing Swahili shown when the never-guess contract fires.

The orchestrator's compute path and the fact-path fabrication guard refuse to invent a number
when a required input is missing or ambiguous (R8). Instead of a bare '<CLARIFICATION_NEEDED>'
placeholder, they render a real, actionable Swahili question that names exactly what is missing,
using the reason the deterministic extractor already recorded per field
(Extraction.clarification_reasons).

Leaf module (stdlib-only) so it stays shareable. PAYROLL_AMOUNT is kept IDENTICAL to
chike-inference/modal_app.py::PAYROLL_CLARIFICATION (production's fabrication-guard reply) —
if you change one, change the other (the dual-file parity rule; they fire on the same
routing.is_uncomputable_payroll_amount predicate).
"""

import re

# Fabrication guard / generic 'no salary figure was given'.
# MUST stay identical to modal_app.PAYROLL_CLARIFICATION.
PAYROLL_AMOUNT = (
    "Ili nikuhesabie makato ya mshahara (kama PAYE, NSSF, SDL) kwa usahihi, nahitaji "
    "kiasi cha mshahara au jumla ya mishahara kwa mwezi. Tafadhali niambie mshahara ni "
    "shilingi ngapi, kisha nitakuletea hesabu kamili."
)

# Compute-intent but the specific levy is unresolved ('ambiguous_multi').
AMBIGUOUS_LEVY = (
    "Naweza kukusaidia kuhesabu makato ya mshahara, lakini niambie unahitaji hesabu ya "
    "tozo gani hasa — PAYE, NSSF, SDL, au WCF — pamoja na kiasi cha mshahara kwa mwezi."
)

FIXED_STATEMENT_NO_TOPIC = (
    "Sijaelewa swali lako linahusu jambo gani hasa. Niambie kama ni notisi ya kuachishwa kazi, malipo ya kuachishwa kazi, "
    "overtime, likizo ya mwaka, au VAT kwa mauzo ya mkopo."
)

_LEVY_NAME = {"paye": "PAYE", "sdl": "SDL", "nssf": "NSSF", "wcf": "WCF"}


def ambiguous_figure(raw: str) -> str:
    """A figure written with a separator that both conventions claim, e.g. 'milioni 1,500'.

    QUOTES THE USER'S OWN TEXT BACK. The two readings are a THOUSAND apart, so a generic
    "niambie mshahara" would look like we ignored the number they plainly wrote, and the
    user would very likely retype it in exactly the same form. Naming both readings is what
    makes the next message resolve it.

    Deliberately does NOT pick the "more likely" one. Comma-decimals are ordinary in
    Swahili writing and grouped thousands are ordinary in TRA documents; the same trader
    may use both in one conversation.
    """
    return (
        f"Sijaelewa vizuri kiasi ulichoandika — \"{raw}\". Kinaweza kumaanisha mambo "
        f"mawili tofauti kabisa, na tofauti yake ni mara elfu moja. Tafadhali niandikie "
        f"kwa tarakimu kamili (mfano: 1,500,000 au 1,500,000,000) ili nisikukosee "
        f"katika hesabu."
    )

# --- minimum wage (GN 605A) -------------------------------------------------
# NEVER-GUESS COPY LIVES HERE AND IS RETURNED BY THE DETERMINISTIC PATH — it is never an
# instruction written into a fact and handed to the model. C4, measured: a locked fact
# containing "usikisie, uliza" did NOT produce a refusal; the model answered anyway. A
# never-guess contract has to be infrastructure, not a sentence in the index.

# No occupation named at all. TZS 175,000 (First Schedule item 16) is NOT the answer here:
# item 16 is the rate for a sector the ORDER does not list, not for a question the USER did
# not answer, and it under-states for a hotel, bank or mine worker.
MIN_WAGE_NO_SECTOR = (
    "Kima cha chini cha mshahara kinatofautiana kwa sekta — GN 605A ina viwango 50, kuanzia "
    "TZS 80,000 hadi TZS 765,900 kwa mwezi. Ili nikupe jibu sahihi la kisheria, niambie "
    "mfanyakazi wako anafanya kazi ya aina gani (mfano: shamba, hoteli, ulinzi, duka, ujenzi)."
)

# The wage figure itself is not identifiable — no figure, or more than one and no way to tell
# which is the wage.
MIN_WAGE_NO_AMOUNT = (
    "Ili nilinganishe na kima cha chini cha GN 605A, niambie mshahara unaomlipa mfanyakazi ni "
    "shilingi ngapi, na kama ni kwa mwezi, kwa wiki au kwa siku."
)

# WORKER-FACING TWINS. Until `_WAGE_PAY_CONCORD` shipped, only employers could reach this
# route, so both strings above address one — "mfanyakazi WAKO", "mshahara UNAOMLIPA mfanyakazi".
# The first live run after that fix answered an employee's "ninalipwa laki moja na nusu je ni
# halali" with "tell me what YOUR EMPLOYEE does".
#
# Same facts, same never-guess contract, same question asked — only the addressee changes. The
# figures are deliberately identical strings to the employer copy so the two cannot drift: if
# the range is corrected, it must be corrected in both, and a test asserts they agree.
MIN_WAGE_NO_SECTOR_WORKER = (
    "Kima cha chini cha mshahara kinatofautiana kwa sekta — GN 605A ina viwango 50, kuanzia "
    "TZS 80,000 hadi TZS 765,900 kwa mwezi. Ili nikupe jibu sahihi la kisheria, niambie "
    "unafanya kazi ya aina gani (mfano: shamba, hoteli, ulinzi, duka, ujenzi)."
)

MIN_WAGE_NO_AMOUNT_WORKER = (
    "Ili nilinganishe na kima cha chini cha GN 605A, niambie unalipwa shilingi ngapi, na kama "
    "ni kwa mwezi, kwa wiki au kwa siku."
)


def min_wage_no_sector(asker_is_worker: bool) -> str:
    return MIN_WAGE_NO_SECTOR_WORKER if asker_is_worker else MIN_WAGE_NO_SECTOR


def min_wage_no_amount(asker_is_worker: bool) -> str:
    return MIN_WAGE_NO_AMOUNT_WORKER if asker_is_worker else MIN_WAGE_NO_AMOUNT

# A figure with no period stated that is too small to be a plausible MONTHLY wage. Comparing
# it against the monthly column would call a lawful daily wage unlawful.
MIN_WAGE_PERIOD_UNCLEAR = (
    "Sijaelewa kama kiasi ulichotaja ni cha mwezi, cha wiki au cha siku — GN 605A ina kiwango "
    "tofauti kwa kila kipindi, hivyo jibu linabadilika kabisa. Tafadhali niambie kiasi hicho "
    "ni cha kipindi gani."
)

# Employment STATUS is unsettled (bodaboda riders, gig work). Whether such a person is an
# "employee" is decided by the Employment and Labour Relations Act Cap. 366, which GN 605A
# para 3 defers to — a labour-law determination this project has not verified against a
# primary source, and one whose answer is wrong in both directions if guessed. Deliberately
# NOT resolved by a cue table.
MIN_WAGE_STATUS_UNCLEAR = (
    "Kima cha chini cha GN 605A kinawahusu WAAJIRIWA. Kama mtu huyu ni bodaboda au anafanya "
    "kazi kwa makubaliano ya kujitegemea, kwanza inabidi ijulikane kama kisheria ni mwajiriwa "
    "au la — hilo linaamuliwa chini ya Sheria ya Ajira na Mahusiano Kazini (Sura 366), na "
    "sina uhakika nalo. Thibitisha na Ofisi ya Kazi (kazi.go.tz)."
)

# --- VAT registration / EFD thresholds --------------------------------------
# Same contract as the minimum-wage copy: returned BY THE DETERMINISTIC PATH, never written
# into a fact and handed to the model (C4). Each states the thresholds — which are locked,
# public and useful — while declining the comparison the question actually asked, because the
# input needed to make it honestly is missing.

# A MONTHLY (or weekly) rate. Deliberately NOT annualised: "milioni 25 kila mwezi" implies
# 300M/year only if the rate holds all twelve months, which is an assumption about a seasonal
# trader's future, not an arithmetic step. Both limbs are stated so the trader can check
# themselves against whichever period they actually know.
VAT_PERIOD_IS_A_RATE = (
    "Kizingiti cha VAT kinapimwa kwa jumla ya mauzo ya kipindi, si kwa mauzo ya mwezi mmoja: "
    "usajili ni wa lazima IKIWA mauzo yamefikia TZS 200,000,000 katika miezi 12, AU TZS "
    "100,000,000 katika miezi 6 mfululizo. Sitakisii mauzo ya mwaka kwa kuzidisha ya mwezi "
    "mara 12 — mauzo hupanda na kushuka. Niambie jumla ya mauzo yako ya miezi 12 iliyopita, "
    "au ya miezi 6 mfululizo, nami nitalinganisha na kizingiti."
)

# A figure with no period at all.
VAT_NO_PERIOD = (
    "Ili nilinganishe na kizingiti cha VAT, niambie kiasi ulichotaja ni cha kipindi gani — "
    "je ni jumla ya miezi 12, au ya miezi 6 mfululizo? Vizingiti ni viwili tofauti: TZS "
    "200,000,000 kwa miezi 12, na TZS 100,000,000 kwa miezi 6 mfululizo, hivyo jibu "
    "linategemea kipindi."
)

def _tzs(amount) -> str:
    return f"TZS {int(amount):,}"


def vat_upper_bound(bound, period, asks_voluntary, annual, six_month) -> str:
    """The user said turnover has NOT REACHED `bound`. That is a bound, not their turnover, and it is
    NEVER reused as one. What follows is derived only from "turnover < bound":
      * annual premise and bound <= the 12-month threshold  -> limb A is demonstrably not met;
      * six-month premise and bound <= the 6-month threshold -> limb B is demonstrably not met;
      * anything else (bound above the threshold, no period) -> nothing is established; ask.
    Voluntary registration: the index holds no fact on it, so the reply SAYS it has none rather than
    letting the model improvise one."""
    head = (f"Umesema mauzo yako hayajafika {_tzs(bound)} — hicho ni kikomo, si mauzo yako halisi, "
            f"kwa hiyo sikitumii kama mauzo yako.")
    if period == "annual" and bound <= annual:
        body = (f" Kwa kizingiti cha miezi 12 ({_tzs(annual)}): hapana, hujakifikia. LAKINI usajili wa VAT "
                f"ni wa lazima pia IKIWA mauzo yamefikia {_tzs(six_month)} katika miezi 6 mfululizo. "
                f"Sijui mauzo yako ya miezi 6 mfululizo — niambie nami nitathibitisha.")
    elif period == "six_month" and bound <= six_month:
        body = (f" Kwa kizingiti cha miezi 6 mfululizo ({_tzs(six_month)}): hapana, hujakifikia. LAKINI "
                f"usajili wa VAT ni wa lazima pia IKIWA mauzo ya miezi 12 yamefikia {_tzs(annual)}. "
                f"Niambie mauzo yako ya miezi 12 nami nitathibitisha.")
    else:
        body = (f" Hilo halitoshi kujua kama umefikia kizingiti ({_tzs(annual)} kwa miezi 12, au "
                f"{_tzs(six_month)} kwa miezi 6 mfululizo). Niambie mauzo yako halisi na kipindi chake.")
    voluntary = (" Kuhusu kujisajili kwa hiari: sina taarifa iliyothibitishwa hapa; thibitisha na TRA "
                 "(tra.go.tz).") if asks_voluntary else ""
    return head + body + voluntary + " Thibitisha na TRA (tra.go.tz)."


def vat_lower_bound(bound, period, annual, six_month):
    """The user said turnover has EXCEEDED `bound`: "at least B", never "B". Returns (text, settled).
    Settled ONLY when the stated period's threshold is at or below B -- then turnover is over it whatever
    the true figure is, and registration is compulsory. Below the threshold (or with no period, or a
    period that is not a total) nothing is established and the figure is asked for; the answer must
    never be 'hapana' on the strength of a floor."""
    head = (f"Umesema mauzo yako yamezidi {_tzs(bound)} — hicho ni kiwango cha chini, si mauzo yako kamili.")
    if period == "annual" and bound >= annual:
        return ("Ndiyo, unatakiwa kujisajili VAT. " + head + f" Kwa kizingiti cha miezi 12 ({_tzs(annual)}): "
                f"umekizidi, hivyo usajili ni wa LAZIMA. Hatua ya kwanza ni kuomba usajili wa VAT TRA. "
                f"Thibitisha na TRA (tra.go.tz)."), True
    if period == "six_month" and bound >= six_month:
        return ("Ndiyo, unatakiwa kujisajili VAT. " + head + f" Kwa kizingiti cha miezi 6 mfululizo "
                f"({_tzs(six_month)}): umekizidi, hivyo usajili ni wa LAZIMA. Hatua ya kwanza ni kuomba "
                f"usajili wa VAT TRA. Thibitisha na TRA (tra.go.tz)."), True
    return (head + f" Hilo halitoshi kujua kama umefikia kizingiti ({_tzs(annual)} kwa miezi 12, au "
            f"{_tzs(six_month)} kwa miezi 6 mfululizo), wala kwa kipindi gani. Niambie mauzo yako halisi na "
            f"kipindi chake nami nitathibitisha. Thibitisha na TRA (tra.go.tz)."), False


def presumptive_lower_bound(bound) -> str:
    """Annual turnover is ABOVE `bound`. That settles nothing about the tax -- the figure is asked for,
    and B is never used as turnover (it would put a trader above the zero band on the zero band)."""
    return (f"Umesema mauzo yako ya mwaka yamezidi {_tzs(bound)} — hicho ni kiwango cha chini, si mauzo yako "
            f"kamili, kwa hiyo sikitumii kama mauzo yako. Kodi ya makadirio inategemea kiasi halisi cha mauzo "
            f"ya mwaka: niambie mauzo yako ya miezi 12 nami nitahesabu. Thibitisha na TRA (tra.go.tz).")


def presumptive_upper_bound(bound, zero_band_top) -> str:
    """Annual turnover is BELOW `bound`. At or under the top of the zero band that settles the tax
    (TZS 0 for any turnover in the band); above it, nothing is settled and the figure is asked for."""
    if bound <= zero_band_top:
        return (f"Kwa kuwa mauzo yako ya mwaka hayajafika {_tzs(bound)}, uko ndani ya kiwango cha sifuri "
                f"(TZS 0 hadi {_tzs(zero_band_top)}): kodi ya makadirio = TZS 0. "
                f"Thibitisha na TRA (tra.go.tz).")
    return (f"Umesema mauzo yako hayajafika {_tzs(bound)} — hicho ni kikomo, si mauzo yako halisi, kwa "
            f"hiyo sikitumii kama mauzo yako. Kodi ya makadirio inategemea kiasi halisi cha mauzo ya "
            f"mwaka: niambie mauzo yako ya miezi 12 nami nitahesabu. Thibitisha na TRA (tra.go.tz).")


# No turnover figure that can be identified.
VAT_NO_TURNOVER = (
    "Ili nikwambie kama usajili wa VAT ni wa lazima kwako, niambie jumla ya mauzo ya biashara "
    "yako — ya miezi 12 iliyopita, au ya miezi 6 mfululizo. Vizingiti ni TZS 200,000,000 kwa "
    "miezi 12 na TZS 100,000,000 kwa miezi 6 mfululizo."
)

# REMOVED 2026-08-29 (EFD_PERIOD_IS_A_RATE, EFD_NO_BASIS): both asked the trader for a turnover
# figure or period before answering the EFD question, and both asserted the TZS 11,000,000
# figure as the threshold their answer would depend on. TAA Cap.438 s.44 has no turnover
# threshold at all -- fiscal-receipt issuance is the default for everyone -- so there is no
# figure or period that could change the verdict, and no clarification to ask for. See
# chike/rules_engine/registration_thresholds.py:efd_required(), which now takes no turnover
# argument at all.

# === PRESUMPTIVE INCOME TAX (Cap 332 First Schedule para 2, as amended by FA2022 s.72,
# further amended by FA2026 s.27(a), WEF 2026-07-01) ===
# Three exits, and only three. The records question is asked ONLY where the two columns of the
# statutory table differ (turnover 4,000,001–11,000,000) — below and above that window the
# figure is identical either way, and asking for an input that cannot change the answer is the
# defect that put five of six CLARIFY rows in the 48-question set (see
# presumptive.records_status_matters).

# No turnover figure at all.
PRESUMPTIVE_NO_TURNOVER = (
    "Ili nikuhesabie kodi ya makadirio, niambie jumla ya MAUZO ya biashara yako kwa mwaka — "
    "si faida, bali mauzo yote. Kodi ya makadirio hupigwa kwa mauzo ya mwaka, na hutumika tu "
    "kwa mauzo yasiyozidi TZS 200,000,000."
)

# A figure whose period is monthly/weekly, or absent. NOT annualised: multiplying one month by
# twelve is an assumption about the rest of the trader's year, not an arithmetic step — the
# same reasoning as VAT_PERIOD_IS_A_RATE.
PRESUMPTIVE_PERIOD_IS_A_RATE = (
    "Kodi ya makadirio hupigwa kwa MAUZO YA MWAKA mzima, si ya mwezi mmoja. Sitakisii mauzo "
    "ya mwaka kwa kuzidisha ya mwezi mara 12 — mauzo hupanda na kushuka. Niambie jumla ya "
    "mauzo yako ya mwaka, nami nitakuhesabia."
)

# Turnover is inside the window where record-keeping changes the figure.
PRESUMPTIVE_NO_RECORDS_STATUS = (
    "Kwa mauzo ya kiwango hicho, kodi inategemea jambo moja zaidi: je unatunza kumbukumbu za "
    "mahesabu ya biashara (vitabu vya mauzo na manunuzi) kama sheria inavyotaka? Anayetunza "
    "kumbukumbu hulipa kwa asilimia ya mauzo yaliyozidi kiwango, na asiyetunza hulipa kiasi "
    "kilichopangwa. Niambie, nami nitakupa kiasi kamili."
)

# Pay quoted PER UNIT rather than per month: per day/week/hour/shift, per trip/piece/job, or
# fortnightly. Used only to pick which question to ask back — it never unlocks a computation
# (turning a rate into a monthly figure is pattern D, still deferred), so a false positive
# costs a differently-worded clarification, never a wrong number.
_PER_UNIT_PAY = re.compile(
    r"kwa\s+(?:siku|wiki|saa|safari|kipande|zamu|mzigo|mteja|kazi\s+moja)\b|"
    r"kila\s+(?:siku|wiki|saa|safari|zamu)\b|bi-?weekly|part-?time\s+kwa\s+saa")

# The question asks about the WHOLE payroll ("NSSF ya JUMLA", "SDL ya WOTE"), not one
# person's. Used only to pick the wording of the question asked back — see the eval_270
# note on the 'needs days/weeks' branch. Kept identical in spirit to extraction._AGGREGATE;
# it is a copy signal here, never an extraction decision.
_AGGREGATE_ASK = re.compile(r"\bjumla\b|\byote\b|\bwote\b|kwa\s+pamoja")


def applicability_clarification(computation_type):
    """Clarification for an applicability-only question that still lacks the one field its
    yes/no needs — currently only SDL, which needs the headcount (vs the 10-employee
    threshold). Asks for the COUNT, not a salary. Pure string logic."""
    levy = _LEVY_NAME.get(computation_type, "makato ya mshahara")
    return (f"Ili nijue kama {levy} inakuhusu, niambie una wafanyakazi wangapi "
            "(kizingiti ni wafanyakazi 10).")


def compute_clarification(computation_type, reasons, question=""):
    """Reason-aware clarification for a compute question whose extraction was UNUSABLE.

    `reasons` is Extraction.clarification_reasons(required) — a list such as
    ['monthly_salary: missing'] or
    ['gross_monthly_payroll: low (amount in foreign currency (not TZS) — needs conversion)'].
    The copy names the specific levy and the specific blocker; a generic 'give me the monthly
    salary' (PAYROLL_AMOUNT) is the fallback when the blocker is vague. Pure string logic.

    `question` is optional and used only to tell a PER-UNIT rate apart from a per-person
    salary. Both reach the extractor as 'role ambiguous' (two figures, neither anchored), but
    they need opposite questions asked back — see _PER_UNIT_PAY."""
    levy = _LEVY_NAME.get(computation_type, "makato ya mshahara")
    blob = " ".join(reasons).lower()
    missing = [r.split(":", 1)[0].strip() for r in reasons if r.strip().endswith("missing")]

    if "foreign currency" in blob or "not tzs" in blob:
        return (f"Ili nihesabu {levy}, tafadhali badilisha kiasi kuwa shilingi za Tanzania "
                "(TZS) — kiasi ulichotaja kiko katika sarafu ya kigeni. Kisha nitahesabu.")
    if "unanchored_base" in blob:
        # 2026-11-16: the question names a levy and one figure but nothing says the figure is a wage ("Mapato yangu ni TZS ..."). ASK; do not assert it is not a salary --
        # an employee's own pay can be phrased that way, which is why this is not the base-rejection answer.
        return (f"Ili nihesabu {levy}, nahitaji kuthibitisha kwamba kiasi ulichotaja ni MSHAHARA (wa mfanyakazi, kwa mwezi) — "
                "si mapato ya biashara, faida, mkopo au kiasi kingine. Kama ni mshahara niambie, au nipe mshahara halisi.")
    if "gross-net" in blob or "allowance" in blob:
        return (f"Ili nihesabu {levy}, thibitisha kama kiasi ulichotaja ni mshahara ghafi "
                "(kabla ya makato) au wa mkononi (baada ya makato).")
    if "needs days" in blob or "needs weeks" in blob:
        # eval_270 ("Tunaendesha zamu 3 kwa siku kiwandani, NSSF ya JUMLA kwa zamu hizo ni
        # ngapi?") asks about a whole factory's payroll, and was answered with a question
        # about one worker's month — the gold asks for the headcount AND their pay. A shift
        # COUNT is not a payroll, so the input actually needed is the total monthly payroll
        # across every worker. Copy only: the verdict (decline to compute) is unchanged, and
        # a false positive costs a differently worded clarification, never a wrong number.
        if question and _AGGREGATE_ASK.search(question.lower()):
            return (f"Ili nihesabu {levy}, niambie JUMLA ya mishahara ya wafanyakazi wote kwa "
                    "mwezi — idadi ya zamu au siku peke yake hainitoshi. Kama unalipa kwa siku "
                    "au kwa zamu, nipe idadi ya wafanyakazi na kiasi wanacholipwa kwa mwezi.")
        return (f"Ili nihesabu {levy}, niambie mshahara wa mwezi ni kiasi gani (au mfanyakazi "
                "anafanya kazi siku/wiki ngapi kwa mwezi) ili nibadilishe kuwa mshahara wa mwezi.")
    # Phase D re-run, eval_291 / eval_294. A PER-UNIT rate ("TZS 320,000 kila wiki mbili",
    # "TZS 80,000 kwa safari, safari 15 kwa mwezi") reaches the extractor as the same
    # 'role ambiguous' two-figure state as a per-person salary, but the question to ask back
    # is the opposite one. Asking "is that per employee or the total?" about a fortnightly
    # wage reads as broken even though declining to compute is right: the missing input is
    # the MONTHLY figure, not the split. The verdict is unchanged — only the copy.
    if question and _PER_UNIT_PAY.search(question.lower()):
        ask = ("niambie mshahara wa MWEZI ni kiasi gani — kiasi ulichotaja ni cha kipindi au "
               "kazi moja, si cha mwezi mzima")
        if "employee_count" in missing:
            ask += (", na idadi ya wafanyakazi wote walio kwenye orodha ya mishahara "
                    "(kizingiti cha SDL ni wafanyakazi 10)" if computation_type == "sdl"
                    else ", na idadi ya wafanyakazi")
        return f"Ili nihesabu {levy}, {ask}. Kisha nitahesabu."
    if ("role ambiguous" in blob or "base ambiguous" in blob
            or "per-person" in blob or "per person" in blob):
        return (f"Ili nihesabu {levy}, niambie kama kiasi ni kwa kila mfanyakazi au ni jumla "
                "ya wote, pamoja na idadi ya wafanyakazi.")

    amount_missing = any(m in ("gross_monthly_payroll", "monthly_salary") for m in missing)
    if missing == ["employee_count"]:
        return (f"Ili nihesabu {levy}, niambie idadi ya wafanyakazi walio kwenye orodha ya "
                "mishahara.")
    if "employee_count" in missing and amount_missing:
        return (f"Ili nihesabu {levy}, nahitaji jumla ya mishahara kwa mwezi NA idadi ya "
                "wafanyakazi. Tafadhali nipe namba hizo mbili.")
    # Missing/vague amount, wrong-base, too-small, or any other blocker -> ask for the salary.
    return PAYROLL_AMOUNT


# --- PAYE residency unclear (SAFETY-2 / D-RESIDENCY-1, 2026-08-15) ----------
# The engine's two PAYE answers are FIVE TIMES apart at TZS 4,000,000 and nearly nineteen
# times apart at TZS 300,000, and which one is right turns on a fact the question does not
# contain. Tanzanian tax residency is decided by PRESENCE, not nationality or permit class —
# so "hana residence permit ya kudumu" narrows nothing: an engineer on a one-year work permit
# who is here 200 days IS tax-resident.
#
# NAMES THE TEST, because it is the one thing that lets the user answer in one message. A
# generic "niambie kama ni mkazi" invites the answer "he's Indian", which is the confusion
# that produced this defect. Days-present is a fact an employer actually knows.
#
# DELIBERATELY STATES NEITHER FIGURE. Offering "TZS 1,028,000 au TZS 600,000" would hand over
# both numbers with our authority attached and let the user pick the smaller one — which is
# the fabrication risk wearing a clarification costume.
PAYE_RESIDENCY_UNCLEAR = (
    "Kabla sijahesabu PAYE, nahitaji kujua kitu kimoja: kwa kodi ya Tanzania, mfanyakazi ni "
    "MKAZI au SI MKAZI, na hili haliamuliwi na uraia wala aina ya kibali — linaamuliwa na "
    "muda anaokaa nchini. Mtu anayekaa Tanzania siku 183 au zaidi katika mwaka wa kodi "
    "huhesabiwa kama mkazi, hata kama ni raia wa nchi nyingine. Tafadhali niambie mfanyakazi "
    "huyu anakaa Tanzania takriban siku ngapi kwa mwaka, kisha nitahesabu PAYE yake kwa "
    "usahihi. Kwa uhakika zaidi, thibitisha na TRA (tra.go.tz)."
)


# --- stated-headcount contradiction (Guard A, 2026-08-14) -------------------

def headcount_contradiction(stated: int) -> str:
    """The fact path told the user they have fewer employees than they just said they have.

    QUOTES THE COUNT BACK, like ambiguous_figure does. The user wrote the number in the
    same sentence, so a generic "niambie idadi ya wafanyakazi" would read as though we had
    not been listening — and they would very likely retype the same figure.

    DELIBERATELY DOES NOT ANSWER. The reason the body was wrong is that the question never
    reached the rules engine, so we do not have an authoritative figure to substitute; and
    the whole point of the guard is that this system had just asserted something false
    about the user's own business. Asking them to confirm is the honest move, and it
    routes the next message into the compute path where a real answer exists.
    """
    return (
        f"Samahani — nimeona umeandika wafanyakazi {stated}, lakini jibu langu la awali "
        f"halikuendana na idadi hiyo, hivyo sitalitumia. Tafadhali nithibitishie: una "
        f"wafanyakazi {stated} na unataka hesabu ya tozo gani (SDL, NSSF, PAYE au WCF), "
        f"pamoja na jumla ya mishahara kwa mwezi? Nitakuletea hesabu kamili."
    )


# --- wrong stated threshold withheld (D-FIDELITY-7, wired 2026-10-06) -------

_THRESHOLD_TOPIC = {
    "efd": "mashine ya risiti (EFD)",
    "vat_registration": "usajili wa VAT",
    "presumptive": "kodi ya makadirio",
}

# ⛔ THE STATUTORY POSITION, FOR THE SUBJECTS WHERE IT IS *THAT THERE IS NO THRESHOLD*.
# (added 2026-10-09, with the apology removal)
#
# WHAT THIS REPAIRS, AND IT IS A2 WORK, NOT A1 WORK. D-FIDELITY-7 converted eval_347 from a
# confident fabricated TZS 11,000,000 EFD threshold into a non-answer. That is the safe
# direction and it still scores as a gate miss, because the user did not get their answer —
# the debt the two-bar framing names explicitly: a guard stops a wrong answer, it cannot
# produce a right one. For EFD the right answer is available and is not a second guess: the
# statutory position is that NO threshold exists.
#
# ⚠️ WHY THIS DOES NOT BREAK THE NO-FIGURE CONTRACT, which is the obvious objection. That
# contract exists because following a caught fabrication with a different NUMBER from the same
# generation is a second guess. "There is no threshold" is the ABSENCE of a number, it is not
# drawn from the generation at all, and it is the same provenance as D-FIDELITY-8's ladder:
# ITA s.44(1) (s.36(1) renumbered, Finance Act 2023 s.54), already served verbatim by index
# row 57 and its sibling `efd_not_every_business`. The copy still states no figure, and
# tests/test_threshold_guard_wiring.py still asserts that for every subject.
#
# ⚠️ AND IT IS PER-SUBJECT FOR A REASON. `vat_registration` and `presumptive` DO have
# statutory thresholds, so "there is no threshold" would be false for them — they keep the
# withhold-only copy. A generic rule sentence here would have been a worse defect than the
# apology it replaced.
_THRESHOLD_RULE = {
    "efd": ("Mashine ya risiti (EFD) haina kizingiti cha mauzo — inahitajika bila kujali "
            "kiwango cha mauzo ya mwaka. Msamaha hutolewa tu kwa tangazo la Kamishna Mkuu "
            "wa TRA."),
}


def wrong_threshold_withheld(subject: str) -> str:
    """The fact path stated a turnover threshold that is not the statutory one.

    WHY THIS IS REPLACEMENT COPY AND NOT A BLANK. On the compute path a flagged body is blanked
    and `_render` still emits the engine's authoritative working, so the user loses a wrong
    sentence and keeps the right figure. On the FACT path there is no working: `_render` returns
    the body alone, so blanking returns an EMPTY REPLY. GUARD A's note governs — silence is worse
    than a wrong answer — so the wrong sentence is REPLACED, exactly as a headcount contradiction
    is.

    DELIBERATELY STATES NO FIGURE, not even a correct one. The system has just been caught
    asserting a fabricated constant about this very subject; following that with a different
    number from the same generation is not a correction, it is a second guess. Naming the subject
    and the authority is the whole of what can be said honestly here.

    ⛔ NO APOLOGY, AS OF 2026-10-09 — the same correction already applied to
    `wrong_fee_band_withheld` on 2026-10-08, and the earlier note claiming the two copies
    DIVERGE on this point was wrong. It read: "D-FIDELITY-7 fires where there is no rule to
    state, so withdrawal is the whole of its message." The first clause is subject-dependent and
    the second does not follow from it. On the fact path the user NEVER SEES THE ORIGINAL REPLY —
    the guard replaces it before `_render` returns — so "Samahani — jibu langu la awali lilitoa
    kiwango..." apologised for a reply they never received and manufactured anxiety about an error
    the system successfully prevented. That reasoning is a property of the FACT PATH, not of
    either guard, so it was never a legitimate difference between them. eval_347 served the
    apology live in this run.

    AND WHERE A RULE EXISTS, IT IS NOW STATED (`_THRESHOLD_RULE`). For EFD the statutory position
    is that there IS no threshold, which is the absence of a figure rather than a second guess,
    so the reply can answer instead of only withdrawing — A2 work, not A1 work. Subjects with a
    real threshold (`vat_registration`, `presumptive`) keep the withhold-only form, because for
    them "there is no threshold" would be false.

    ⛔ AND IT IS NOT A FIX, ONLY A STOP. Wiring the guard turns a confident wrong answer into a
    non-answer. On an IN-CORPUS question (eval_347 is one) that still scores as a miss on the
    accuracy gate — correctly, because the user did not get their answer. It closes R7's Bar A
    (no known class of confident wrong answer) and does nothing for the retrieval or generation
    defect underneath. Anyone reading a gate score after this lands should expect the wrong-answer
    class to become a no-answer class, not to disappear.
    """
    topic = _THRESHOLD_TOPIC.get(subject, "kiwango hiki")
    rule = _THRESHOLD_RULE.get(subject)
    if rule:
        return f"{rule} Sitatoa kiwango chochote cha mauzo hapa. Thibitisha na TRA (tra.go.tz)."
    return (
        f"Siwezi kuthibitisha kiwango cha mauzo kwa {topic}, hivyo sitakitaja na sitakisii "
        f"kingine. Thibitisha na TRA (tra.go.tz) — au niulize utaratibu bila kiasi, "
        f"nikueleze hatua."
    )


NSSF_SPLIT_INVALID = ("Jumla ya NSSF ni asilimia 20 ya mshahara ghafi daima, na mgao wa mwajiri na mfanyakazi lazima ujumlishe asilimia 20 "
                      "(kwa mfano 10 + 10, 15 + 5, au 20 + 0). Mgao uliotaja haujumlishi asilimia 20 — niambie mgao unaokusudia, kisha nitahesabu.")


def vat_registration_verdict_withheld() -> str:
    """D-FIDELITY-12 replacement copy (2026-11-16): the fact path told a turnover ABOVE the VAT threshold that it need not register.

    States the RULE from the served rows (the two limbs, and that reaching either one is what obliges registration) and passes NO verdict on the user's figure: the system has just been caught
    asserting a wrong verdict about this very comparison, so a replacement verdict from the same generation would be a second guess. The user can read their own figure against the rule in one line.
    No apology (the user never sees the original reply on the fact path) and no days figure (not stated here as a positive fact)."""
    return ("Kizingiti cha kusajili VAT ni mauzo ya TZS 200,000,000 ndani ya miezi 12 AU TZS 100,000,000 ndani ya miezi 6. "
            "Ukifikia au ukizidi mojawapo ya viwango hivi, ni lazima ujisajili VAT. Linganisha mauzo yako ya kipindi husika na kiwango hiki, "
            "kisha thibitisha na TRA (tra.go.tz).")


# ─── D-FIDELITY-8 REPLACEMENT COPY: THE BRELA SHARE-CAPITAL FEE LADDER ───────────
# ⛔ THE ONE OWNER OF THESE NINE BANDS IN PRODUCTION CODE. The copy below is GENERATED from
# this tuple, never hand-typed, so the sentence a user reads cannot drift from the table --
# and tests/test_fee_band_copy.py asserts every figure here appears in the SERVED index row
# 181. A second hand-written copy of a fee table is the dual-file divergence this project
# keeps paying for.
#
# Source: BRELA's published schedule, item 1, captured 2026-10-06T14:04:42Z, sha256
# 8d5543ac… (data/source_documents/brela/brela_ada_kampuni_20261006T140442Z.html).
#
# ⚠️ THE DATE BELOW IS AN OBSERVATION DATE, NOT AN EFFECTIVE DATE, and the copy says
# "kama ilivyochapishwa … tarehe" (as published on) for exactly that reason. CLAUDE.md is
# explicit: `effective_date` is UNKNOWN for every figure on this schedule, the change landed
# somewhere inside 2026-06-30 → 2026-10-06, and the Companies (Fees) Regulations have not
# been located. Writing the capture date as an effective date would manufacture R29 mode 3 --
# a correctly-cited figure carrying an unsourced currency date.
BRELA_CAPTURE_DATE = "2026-10-06"
BRELA_SHARE_CAPITAL_BANDS = (
    (None,             1_000_000,        95_000),
    (1_000_000,        5_000_000,       175_000),
    (5_000_000,        20_000_000,      260_000),
    (20_000_000,       50_000_000,      290_000),
    (50_000_000,       100_000_000,     400_000),
    (100_000_000,      500_000_000,     450_000),
    (500_000_000,      1_000_000_000,   500_000),
    (1_000_000_000,    10_000_000_000,  600_000),
    (10_000_000_000,   None,          1_000_000),
)


def _tzs(n):
    return f"TZS {n:,}"


def _band_phrase(lo, hi, fee):
    if lo is None:
        return f"hadi {_tzs(hi)} ni {_tzs(fee)}"
    if hi is None:
        return f"zaidi ya {_tzs(lo)} ni {_tzs(fee)}"
    return f"zaidi ya {_tzs(lo)} hadi {_tzs(hi)} ni {_tzs(fee)}"


def wrong_fee_band_withheld() -> str:
    """The fact path stated a company-registration fee that is wrong for the share capital.

    WHY THIS COPY STATES THE RULE AND THE WHOLE LADDER, where `wrong_threshold_withheld`
    deliberately states NO figure. The two defects are not the same shape and the difference
    decides the copy:

      D-FIDELITY-7 caught a FABRICATED constant -- there IS no statutory EFD turnover
      threshold, so there is no rule to state, and following a fabrication with a different
      number from the same generation would be a second guess.

      D-FIDELITY-8 catches a MISAPPLIED LOOKUP. The table is real, published, sha256-pinned,
      and ALREADY SERVED VERBATIM as index row 181. Nothing about the facts failed; BAND
      SELECTION failed -- picking a row from nine closed bands means comparing the user's
      figure against band edges, which is arithmetic the fact path does not do. The measured
      live reply gave TZS 290,000 for TZS 2,000,000,000 of share capital (the >20M-50M band,
      with its floor misstated as 5,000,000) where the ladder gives TZS 600,000.

    SO THE COPY ANSWERS BY HANDING OVER THE RULE AND REFUSING THE SELECTION:
      * it withdraws the figure it just gave;
      * it states the RULE -- the fee depends on share capital and is a ladder, not one rate;
      * it lists all nine bands, generated from BRELA_SHARE_CAPITAL_BANDS;
      * it asks the user to read off their own band, which is the step that failed;
      * it names the authority and the CAPTURE date, and asks them to confirm the current
        schedule, because `effective_date` is genuinely unknown.

    ⛔ IT CANNOT REPRODUCE THE 290,000 ERROR, and that is the structural property rather than
    a hope: the copy performs no band selection at all. Every figure in it comes from the
    pinned capture via the constant above, so there is no step at which a wrong band can be
    chosen. That is what makes stating figures safe HERE and unsafe in D-FIDELITY-7's case.

    ⚠️ AND IT IS STILL NOT A FIX. Like every guard, this stops a wrong answer and does not
    produce the right one: the user is handed the table instead of their fee. It moves Bar
    A's A1 (confident wrong answers) and NOT A2 (answered correctly). A2 needs the band
    SELECTION to work, which is a compute-path job, not a copy job.
    """
    # ⛔ NO APOLOGY, AND NO REFERENCE TO A PREVIOUS ANSWER. Founder edit, 2026-10-08, and the
    # reasoning generalises to every fact-path replacement: ON THE FACT PATH THE USER NEVER
    # SEES THE ORIGINAL REPLY -- the guard REPLACES it before `_render` returns. So an opener
    # like "jibu langu la awali lilitoa ada..." apologises for a reply they never received and
    # reads as though something went wrong that they should worry about. It manufactures
    # anxiety about an error the system successfully prevented.
    #
    # This is the one place this copy DIVERGES from `wrong_threshold_withheld` above, which
    # does open by withdrawing. That difference is deliberate and not an inconsistency to
    # tidy: D-FIDELITY-7 fires where there is no rule to state, so withdrawal is the whole of
    # its message. Here the rule IS the message, so the reply simply answers.
    ladder = "; ".join(_band_phrase(lo, hi, fee)
                       for lo, hi, fee in BRELA_SHARE_CAPITAL_BANDS)
    return (
        "Ada ya kusajili kampuni BRELA inategemea mtaji wa hisa (share capital), na ni "
        "ngazi — si kiwango kimoja. "
        f"Ngazi za ada: {ladder}. "
        "Angalia ngazi inayolingana na mtaji wa hisa wa kampuni yako. "
        "Kampuni isiyo na mtaji wa hisa ni TZS 500,000. "
        f"Ratiba hii ni kama ilivyochapishwa na BRELA (brela.go.tz) tarehe "
        f"{BRELA_CAPTURE_DATE}; thibitisha ratiba inayotumika sasa na BRELA kabla ya kulipa."
    )


# --- D-FIDELITY-13 replacement copy (2026-11-16): a licence / record-keeping / TIN constant the fact path contradicted -------------------------------------------------------------------------
# Unlike D-FIDELITY-7 (which states no figure after being caught inventing one), these three are lookups against statutory constants that the SAME session's locked facts hold verbatim, so the replacement is the
# right answer, not a second guess. Each sentence is lifted from the locked fact of that name (tests/test_constant_guards.py asserts the figure is in the fact's own text). R44: the Act is named, no section number.
CONSTANT_RESTATEMENTS = {
    "business_licence_expiry": ("Leseni ya biashara ni halali kwa miezi 12 tangu tarehe ilipotolewa; si tarehe maalum ya kalenda (si 30 Juni, si 31 Machi: sheria ya zamani ilibadilishwa). "
                                "Unaweza kulipia ada ya hadi miaka 3 mfululizo (Sheria ya Leseni za Biashara). Thibitisha na mamlaka yako ya leseni: halmashauri yako, au BRELA kwa leseni za kundi A (brela.go.tz)."),
    "record_keeping_period": ("Rekodi za biashara zihifadhiwe kwa miaka 5 tangu tarehe husika (kodi ya mapato: mwisho wa mwaka wa mapato; VAT: mwisho wa kipindi cha kodi), ndani ya Tanzania. "
                              "Muda ni mrefu zaidi ikiwa kuna pingamizi, ukaguzi au ombi la marejesho (Sheria ya Usimamizi wa Kodi). Thibitisha na TRA (tra.go.tz)."),
    # D-FIDELITY-15 (2026-11-17): WCF is never deducted from the employee; input VAT on a passenger car. Sentences lifted from wcf_paid_to_fund_not_tra / input_vat_passenger_vehicle.
    "wcf_not_deducted": ("WCF inalipwa na mwajiri peke yake: mfanyakazi hachangii WCF, kwa hiyo HAIKATWI kwenye mshahara wake, na ni kosa kwa mwajiri kukata mchango wa WCF kwa mfanyakazi. "
                         "Kiwango ni asilimia 0.5 ya jumla ya mishahara ghafi ya wafanyakazi wote, na hulipwa kwa Mfuko wa WCF (wcf.go.tz), si TRA."),
    "input_vat_passenger_vehicle": ("Hapana: VAT ya pembejeo haidaiwi kwa gari la abiria, vipuri au matengenezo yake, isipokuwa biashara yako ni kuuza, kukodisha au kusafirisha abiria na gari lilinunuliwa kwa kusudi hilo "
                                    "(Sheria ya VAT). Thibitisha na TRA (tra.go.tz)."),
    # D-FIDELITY-16 (2026-11-17): a non-resident dividend at 15%, a company return deadline of 12 months / 30 September, a flat 15% on severance. Sentences lifted from dividend_withholding_rate / corporate_income_tax_return /
    # severance_pay_income_tax (tests/test_d16_followup_guards.py asserts the figures are in each fact's own text). R44: the Act is named, no section number.
    "dividend_nonresident_rate": ("Gawio linakatwa kodi ya zuio ya 5% (kampuni iliyoorodheshwa Soko la Hisa la Dar es Salaam, au kampuni mkazi inayomiliki 25% au zaidi) au 10% (kampuni nyingine). "
                                  "15% si kiwango cha gawio; viwango hivi ni vilevile kwa mpokeaji asiye mkazi. Mkataba wa kodi mara mbili unaweza kuweka kiwango tofauti (Sheria ya Kodi ya Mapato). Thibitisha na TRA (tra.go.tz)."),
    "corporate_return_deadline": ("Return ya kodi ya mapato ya kampuni iwasilishwe ndani ya miezi 6 baada ya mwisho wa mwaka wa mapato: kampuni ya kawaida (mwaka wa kalenda) kufikia 30 Juni ya mwaka unaofuata; "
                                  "mwaka tofauti ulioidhinishwa na Kamishna unahamisha tarehe, na anayekaguliwa na CAG ana miezi 9. Mapato jumla zaidi ya TZS 100,000,000: return ipitiwe au kuthibitishwa na CPA "
                                  "(Sheria ya Kodi ya Mapato). Thibitisha na TRA (tra.go.tz)."),
    "severance_flat_15": ("Malipo ya kuachishwa kazi (severance) ni mapato ya ajira: yanajumuishwa kwenye mapato yako na PAYE hukokotolewa kwa viwango vya kawaida vya mshahara kwa mkazi; hakuna kiwango maalum cha asilimia 15. "
                          "Kuna kanuni za kugawa malipo ya miaka ya nyuma (Sheria ya Kodi ya Mapato). Thibitisha kiasi chako na TRA (tra.go.tz)."),
    # D-FIDELITY-20 (2026-11-17): the company annual-return deadline (Companies Act Cap.212 R.E.2023: each return is made up to the anniversary of incorporation; 28 days from that return date). R44: the Act is named, no section number.
    "brela_annual_return_deadline": ("Annual return ya kampuni hufanywa kila mwaka: kila return hutayarishwa hadi tarehe ya maadhimisho ya kuanzishwa kwa kampuni (au ya tarehe ya return iliyotangulia). "
                                     "Ukichelewa zaidi ya siku 28 baada ya tarehe hiyo, kampuni na kila afisa aliyehusika wanaweza kutozwa faini (Sheria ya Makampuni). Thibitisha na BRELA (brela.go.tz)."),
    # D-FIDELITY-22 (2026-11-17): the VAT-withholding start date (Finance Act 2025 (No. 11), read with edition asserted: the Act commences 1 July 2025; the 3% / 6% rule carries no separate commencement; the 1 September 2025 proviso belongs to the 16% e-payment rate). R44: the Act is named, no section number.
    "vat_withholding_start_date": ("VAT ya zuio (3% kwa bidhaa, 6% kwa huduma) ilianza kutumika tarehe 1 Julai 2025 pamoja na Sheria ya Fedha 2025; sheria haina kuahirishwa kwa kifungu hicho. "
                                   "Tarehe 1 Septemba 2025 ni ya kifungu kingine cha sheria hiyo hiyo (VAT ya 16% kwa malipo kupitia benki au mfumo wa kielektroniki), si ya VAT ya zuio. "
                                   "Anayezuia VAT ni wakala wa zuio: wizara ya fedha, taasisi ya Serikali inayobakiza mapato yake, au mtu aliyesajiliwa anayeteuliwa na Kamishna Mkuu kwa taarifa. Thibitisha na TRA (tra.go.tz)."),
    "tin_apply_deadline": ("Anayeanza biashara aombe Namba ya Mlipakodi (TIN) kwa TRA ndani ya siku 15 tangu aanze biashara, akiwa na ushahidi wa utambulisho. "
                           "TRA inaweza kutoa TIN ndani ya siku 7 tangu ombi (Sheria ya Usimamizi wa Kodi). Thibitisha na TRA (tra.go.tz)."),
    # D-FIDELITY-23 (2026-11-18): "46" stated as the sub-sector count of the MINING sector alone. GN 605A (kazi.go.tz official copy, edition asserted in the manifest): the First Schedule lists sixteen sectors; item 10, Mining Sector, has FOUR rows
    # ((a) mining and prospecting minerals, (b) primary mining licence, (c) dealer licence, (d) brokers licences). The 46 is PKF's figure for the sub-sectors across ALL sectors, and the Order does not settle it mechanically.
    "gn605a_mining_subsector_count": ("Agizo la Kima cha Chini cha Mshahara kwa Sekta Binafsi (GN 605A) lina sekta 16 katika Ratiba yake ya Kwanza. Sekta ya Madini (kipengele cha 10) ina vipengele vinne tu, kila kimoja na kiwango chake: "
                                      "uchimbaji na utafutaji wa madini, leseni ya msingi ya uchimbaji, leseni ya wauzaji (dealer), na leseni za madalali (brokers). "
                                      "Idadi ya 46 ni takwimu ya sekta ndogo kwa sekta zote kwa pamoja (kutoka PKF), si ya sekta ya madini peke yake, na Agizo lenyewe halitaji idadi hiyo: thibitisha na kazi.go.tz."),
}


def _mining_wage_restatement() -> str:
    """D-FIDELITY-24 replacement text: the four mining rates GENERATED from the transcribed schedule (wage_schedule.SCHEDULE), so the figures a user reads cannot drift from the engine's table. Labels follow the Order's own row names."""
    from .rules_engine import wage_schedule as ws
    labels = {"a": "uchimbaji na utafutaji wa madini (mining and prospecting minerals)", "b": "leseni ya msingi ya uchimbaji (primary mining licence)",
              "c": "leseni ya wauzaji (dealer licence)", "d": "leseni za madalali (brokers licences)"}
    rows = sorted(((int(r[-1]), r[1]) for r in ws.SCHEDULE if r[0] == 10), reverse=True)
    parts = "; ".join(f"{labels[letter]}: TZS {amount:,}" for amount, letter in rows)
    energy = {r[1]: int(r[-1]) for r in ws.SCHEDULE if r[0] == 7}
    return ("Sekta ya Madini katika GN 605A (kipengele cha 10) ina viwango vinne vya kima cha chini kwa mwezi, kulingana na aina ya leseni au shughuli: " + parts + ". "
            f"Kiwango cha TZS {energy['a']:,} ni cha sekta ya nishati (kampuni za kimataifa), si cha madini. Thibitisha kiwango cha aina yako ya leseni na kazi.go.tz.")


CONSTANT_RESTATEMENTS["gn605a_mining_wage"] = _mining_wage_restatement()


CONSTANT_RESTATEMENTS["sdl_applies_at_threshold"] = (
    "Mwajiri mwenye wafanyakazi 10 au zaidi (Tanzania Bara) ana wajibu wa kulipa SDL, asilimia 3.5 ya jumla ya mishahara. Wanaosamehewa na sheria ni makundi maalum tu (taasisi za Serikali, mamlaka za serikali za mitaa, "
    "balozi, Umoja wa Mataifa na mashirika ya kimataifa, taasisi za dini, shule zilizosajiliwa, mashirika ya hisani, na waajiri wa mashamba kwa wafanyakazi wa kilimo tu). Biashara ya kawaida yenye wafanyakazi 10 au zaidi hulipa SDL. "
    "Thibitisha na TRA (tra.go.tz).")


# D-FIDELITY-27 / 28 (2026-11-22): replacement copy for two unsupported scope claims. These are the PROPOSED fact texts (founder to approve before the regen); R44: the Act is named, no section number (it lives in the fact's metadata).
CONSTANT_RESTATEMENTS["sdl_scope_by_premises"] = (
    "SDL hutozwa kwa kila mwajiri mwenye wafanyakazi 10 au zaidi (Sheria ya Elimu na Mafunzo ya Ufundi); Sheria haisemi kwamba inahusu 'maeneo ya biashara' pekee. "
    "Wasiotozwa ni makundi yaliyoorodheshwa kisheria: taasisi za Serikali zinazofadhiliwa kikamilifu kupitia ruzuku ya Serikali, balozi, Umoja wa Mataifa, taasisi za misaada za kimataifa au za kigeni, taasisi za dini, mashirika ya hisani, "
    "taasisi za elimu zilizosajiliwa, halmashauri, wanafunzi wa mafunzo kwa vitendo chini ya TaESA, waajiri wa mashambani kwa wafanyakazi wa kilimo, na mamlaka ya maji na usafi wa mazingira kwa vibarua wa miradi ya maji; Waziri wa Fedha pia anaweza kusamehe kwa tangazo la Gazeti. "
    "Orodha hiyo haina mwajiri wa nyumbani; kama wafanyakazi wa nyumbani wanahesabiwa kwenye idadi ya 10, hakuna kinachotuonyesha kwa uhakika; thibitisha na TRA (tra.go.tz) kabla ya kuamua.")
CONSTANT_RESTATEMENTS["nssf_contributions_age_60"] = (
    "Umri wa miaka 60 ni umri wa pensheni wa NSSF: ndio unaoamua lini pensheni ya uzee inapatikana (michango isiyopungua miezi 180; kustaafu mapema kunawezekana ndani ya miaka 5 kabla yake). "
    "Sheria haisemi kwamba michango inakoma wala inaendelea kwa sababu ya umri wa 60, na haimwondolei mwajiri wajibu wa michango kwa mfanyakazi anayepokea au anayestahili manufaa. "
    "Kwa mfanyakazi aliyefika 60 au anayepokea pensheni na bado ameajiriwa, thibitisha na NSSF (nssf.go.tz).")


def constants_restated(topics) -> str:
    """The whole statement for every violated constant topic, in the order given, each once."""
    seen, out = set(), []
    for t in topics:
        if t not in seen:
            seen.add(t)
            out.append(CONSTANT_RESTATEMENTS[t])
    return "\n\n".join(out)


def derived_amount_withheld(rate_text: str = "") -> str:
    """D-FIDELITY-13 (np_28, th_22): the fact path stated a shilling amount for a payroll levy although the question gave no wage or payroll. No amount can be derived from nothing, so the sentence is REPLACED
    (the fact path cannot be blanked: `_render` returns the body alone) by the rate, when one is known, and a request for the one input that is missing."""
    ask = "Ili nikokotoe kiasi cha shilingi, nipe jumla ya mishahara ya mwezi (na idadi ya wafanyakazi ikihitajika)."
    return (rate_text.strip() if "nipe jumla" in rate_text else (rate_text.strip() + " " + ask).strip()) if rate_text else ("Siwezi kutaja kiasi cha shilingi bila mshahara au jumla ya mishahara. " + ask)

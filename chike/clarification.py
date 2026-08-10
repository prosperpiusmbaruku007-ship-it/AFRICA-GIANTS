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

_LEVY_NAME = {"paye": "PAYE", "sdl": "SDL", "nssf": "NSSF", "wcf": "WCF"}

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
    "TZS 80,000 hadi TZS 765,900 kwa mwezi. Ili nikwambie kama unacholipa ni halali, niambie "
    "mfanyakazi wako anafanya kazi ya aina gani (mfano: shamba, hoteli, ulinzi, duka, ujenzi)."
)

# The wage figure itself is not identifiable — no figure, or more than one and no way to tell
# which is the wage.
MIN_WAGE_NO_AMOUNT = (
    "Ili nilinganishe na kima cha chini cha GN 605A, niambie mshahara unaomlipa mfanyakazi ni "
    "shilingi ngapi, na kama ni kwa mwezi, kwa wiki au kwa siku."
)

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

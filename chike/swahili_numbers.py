"""Deterministic Swahili numeral parsing + ambiguity detection for slot extraction.

WHY THIS IS DETERMINISTIC AND NOT MODEL-BASED
This session proved (qwen3-32b judge non-determinism finding, PROGRESS.md 2026-07-16)
that even a 32B model misreads Swahili compound numerals — "laki tano" as 5,000 instead
of 500,000, "milioni mbili na robo" as 2.5M instead of 2.25M. The 8B production model is
weaker still. So the confidence-assignment and clarification-triggering layer of slot
extraction — the part that must be trustworthy and inspectable — is implemented here as
pure, unit-tested Python, NOT delegated to a language model. The model is used only for
free-text role assignment (which number is the payroll vs the headcount); every numeric
value and every ambiguity verdict it produces is validated against this module.

Swahili numeral grammar is SCALE-FIRST (big-endian): the scale word precedes its
multiplier — "laki tano" = 100,000 x 5, "milioni sabini na mbili" = 1e6 x 72,
"milioni mia mbili na hamsini" = 1e6 x 250. This is the opposite of English and the
exact place the models fail; parse_amount() implements it explicitly.
"""

import re
from decimal import Decimal, InvalidOperation

# --- cardinal words (incl. the wa-/w- noun-class forms used for counting people) ---
UNITS = {
    "sifuri": 0, "moja": 1, "mmoja": 1, "mbili": 2, "wawili": 2, "mbaya": None,
    "tatu": 3, "watatu": 3, "nne": 4, "wanne": 4, "tano": 5, "watano": 5,
    "sita": 6, "wasita": 6, "saba": 7, "nane": 8, "wanane": 8, "tisa": 9, "tisatisa": 9,
    "kumi": 10, "ishirini": 20, "thelathini": 30, "arobaini": 40, "hamsini": 50,
    "sitini": 60, "sabini": 70, "themanini": 80, "tisini": 90,
}
UNITS = {k: v for k, v in UNITS.items() if v is not None}
BIG_SCALE = {"elfu": 1000, "laki": 100000, "milioni": 1000000, "bilioni": 1000000000}
FRACTION = {"nusu": Decimal("0.5"), "robo": Decimal("0.25"), "theluthi": Decimal("1") / 3}
NUMBER_TOKENS = set(UNITS) | set(BIG_SCALE) | set(FRACTION) | {"mia", "na"}

# RC-2: a monthly payroll/salary below this is not a real TZS figure — the 2026 minimum
# wage floor is ~175,000/month, so a "payroll" of 2 / 5 / 8 is a miscounted quantity
# (branches, employees, shares), not money. Used to veto small-int-as-money AND to stop a
# spelled small count ("wawili" = 2) from masking a missing antecedent.
MIN_PLAUSIBLE_AMOUNT = Decimal(10000)


def _value_small(tokens):
    """Value of a number phrase with no leading big-scale: mia/tens/units/fraction."""
    total = Decimal(0)
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "na":
            i += 1
            continue
        if t in FRACTION:
            total += FRACTION[t]
            i += 1
            continue
        if t == "mia":                                   # "mia mbili" = 100 x 2 = 200
            mult = 1
            if i + 1 < len(tokens) and UNITS.get(tokens[i + 1], 99) < 10:
                mult = UNITS[tokens[i + 1]]
                i += 1
            total += 100 * mult
            i += 1
            continue
        if t in UNITS:
            total += UNITS[t]
            i += 1
            continue
        i += 1
    return total


def _value(tokens):
    """Value of a full Swahili number phrase (scale-first, big-endian)."""
    if not tokens:
        return Decimal(0)
    if tokens[0] in BIG_SCALE:                           # "milioni <sub-number>"
        rest = _value(tokens[1:])
        return Decimal(BIG_SCALE[tokens[0]]) * (rest if rest else Decimal(1))
    return _value_small(tokens)


_DIGIT_M = re.compile(r"(\d+(?:\.\d+)?)\s*m\b", re.IGNORECASE)          # "20m", "2.5m"
_DIGITS = re.compile(r"\d[\d,\.]*")
_SCALE_DIGIT = re.compile(r"\b(elfu|laki|milioni|bilioni)\s+(\d[\d,]*)", re.IGNORECASE)


def parse_amounts(text):
    """All monetary amounts found in `text`, as a list of Decimal (best-effort).

    Handles digit forms ("TZS 500,000", "milioni 190"), the "20m" slang, and
    scale-first Swahili word numbers ("laki tano", "milioni moja na nusu").
    Deliberately over-collects candidates; the caller decides which role each fills.
    """
    text_l = text.lower()
    found = []

    for m in _SCALE_DIGIT.finditer(text_l):              # "milioni 190" -> 190e6
        scale = BIG_SCALE[m.group(1)]
        digits = Decimal(m.group(2).replace(",", ""))
        found.append((m.start(), Decimal(scale) * digits))

    for m in _DIGIT_M.finditer(text_l):                  # "20m" -> 20,000,000
        found.append((m.start(), Decimal(m.group(1)) * 1000000))

    # word-number runs (skip any that were already consumed by a scale+digit match)
    consumed = {i for m in _SCALE_DIGIT.finditer(text_l) for i in range(m.start(), m.end())}
    for m in re.finditer(r"[a-z]+", text_l):
        if m.group(0) in NUMBER_TOKENS and m.start() not in consumed:
            # extend to the maximal run of number tokens
            start = m.start()
            run = []
            for w in re.finditer(r"[a-z]+", text_l[start:]):
                if w.group(0) in NUMBER_TOKENS:
                    run.append(w.group(0))
                else:
                    break
            if run and any(t in BIG_SCALE or t == "mia" or t in UNITS for t in run):
                # PREREQ-2 pattern C-1. A run BEGINNING with a fraction word is a QUANTIFIER
                # ("theluthi mbili ya watu 30" = two-thirds OF thirty), not an amount. Swahili
                # has two fraction constructions and _value_small implements only one:
                #   additive       "<scale> <n> NA <frac>"  laki saba na nusu = 750,000   ✅
                #   multiplicative "<frac> [<mult>] YA <N>" theluthi mbili ya 30 = 20      ❌
                # The multiplier is a NUMERATOR, not an addend, so the additive path yields
                # 1/3 + 2 = 2.333 and 1/4 + 3 = 3.25 — junk in the amount list.
                #
                # This SUPPRESSES rather than computes: resolving the quantifier needs the
                # group it modifies, which is pattern B. parse_fraction_of_count() below
                # exposes the resolved split for B to consume.
                #
                # Applied to ANY fraction-initial run, not only 'ya'-gated ones, on evidence:
                # _value produces junk for every fraction-initial run (nusu milioni -> 0.5,
                # robo milioni -> 0.25, theluthi elfu -> 0.33), so there is no correct figure
                # to lose. The 516-sweep could NOT distinguish the two variants — both change
                # the same 2 questions — so the choice rests on the probes.
                #
                # DEFINED ON THE PARSED RUN, NOT BY REGEX. A '\b(nusu|robo|theluthi)\s+ya'
                # regex wrongly suppresses nat_05 ("asilimia tatu na nusu YA nini" = 3.5%):
                # it matches 'nusu ya' while the actual run starts at 'tatu'. Run-initial is
                # the only formulation that separates the two constructions.
                if run[0] not in FRACTION:
                    val = _value(run)
                    if val > 0:
                        found.append((start, val))
            # advance past this run by marking consumed
            consumed.update(range(start, start + len(" ".join(run))))

    # bare digit amounts not attached to a scale word (e.g. "250000", "500,000")
    for m in _DIGITS.finditer(text_l):
        if m.start() in consumed:
            continue
        # A run of digits touching a letter on either side is part of an alphanumeric
        # code, not a currency figure — the "487" in "GN487A", the "605" in "GN605A".
        # Extracting it as money is the exact DANGEROUS misread the parser must avoid.
        before = text_l[m.start() - 1] if m.start() > 0 else ""
        after = text_l[m.end()] if m.end() < len(text_l) else ""
        if before.isalpha() or after.isalpha():
            continue
        raw = m.group(0).rstrip(".,").replace(",", "")
        if raw.isdigit():
            found.append((m.start(), Decimal(raw)))

    found.sort(key=lambda x: x[0])
    # de-dup by (position) keeping order
    return [v for _, v in found]


# ── PREREQ-2 pattern C-2: resolve a fraction-of-headcount into group sizes ──────────
#
# UNUSED BY DEFAULT. Nothing in the pipeline calls this yet: C-1 only removes junk, and no
# gate question becomes answerable from it. It exists so pattern B (multi-group payroll) can
# consume the split instead of re-deriving it — which is what makes C a prerequisite for 4 of
# B's 9 instances (eval_285/287/288/289).
#
# Requires a PEOPLE noun. "nusu ya MSHAHARA wake" is a proportion of MONEY, not a headcount,
# and must never be read as a group size — the corpus contains no such case, so the probes
# (extraction_fraction_probes_008.jsonl) are the only thing testing it.
_FRACTION_DENOM = {"nusu": 2, "robo": 4, "theluthi": 3}
# The word after a fraction is its NUMERATOR: "theluthi MBILI" = TWO thirds, "robo TATU" =
# THREE quarters. This is the exact place _value_small went wrong by adding instead.
_FRACTION_NUMERATOR = {
    "moja": 1, "mmoja": 1, "mbili": 2, "wawili": 2, "tatu": 3, "watatu": 3,
    "nne": 4, "wanne": 4, "tano": 5, "watano": 5, "sita": 6, "saba": 7, "nane": 8, "tisa": 9,
}
_FRACTION_PEOPLE = r"wafanyakazi|watu|wafanyikazi|waajiriwa|vibarua|watumishi"
_FRACTION_OF = re.compile(
    rf"\b(nusu|robo|theluthi)(?:\s+({'|'.join(_FRACTION_NUMERATOR)}))?\s+ya\s+"
    rf"(?:{_FRACTION_PEOPLE})\s+(\d{{1,4}})")
# The SECOND group is often elliptical — the fraction repeats with no 'ya' and no base
# ("robo tatu ya wafanyakazi 16 wanapata X, ROBO wanapata Y") — or is named as the remainder
# ("wengine wote").
_FRACTION_ELLIPTIC = re.compile(
    rf"\b(nusu|robo|theluthi)(?:\s+({'|'.join(_FRACTION_NUMERATOR)}))?\s+"
    r"(?:wanapata|wanalipwa|wana\b|wenye)")
_FRACTION_REMAINDER = re.compile(r"\bwengine\w*\b")


def parse_fraction_of_count(text):
    """Resolve "<fraction> [<numerator>] ya <people-noun> <N>" into group sizes.

    Returns {'base': N, 'groups': [...]} , or {'base': N, 'groups': None, 'reason': ...} when
    the split is not a whole number, or None when the construction is absent.

    NEVER ROUNDS. "theluthi ya watu 10" is 3.33 people; rounding it would assert a headcount
    the user never gave, which is the never-guess contract's whole point. Declines instead.
    """
    text_l = text.lower()
    match = _FRACTION_OF.search(text_l)
    if not match:
        return None
    fraction, numerator_word, base_raw = match.groups()
    base = int(base_raw)
    first = (Decimal(base) * _FRACTION_NUMERATOR.get(numerator_word, 1)
             / _FRACTION_DENOM[fraction])
    if first != first.to_integral_value():
        return {"base": base, "groups": None,
                "reason": f"fraction of {base} is not a whole number of people ({first})"}

    groups = [int(first)]
    tail = text_l[match.end():]
    elliptic = _FRACTION_ELLIPTIC.search(tail)
    if elliptic:
        second = (Decimal(base) * _FRACTION_NUMERATOR.get(elliptic.group(2), 1)
                  / _FRACTION_DENOM[elliptic.group(1)])
        if second != second.to_integral_value():
            return {"base": base, "groups": None,
                    "reason": f"second group of {base} is not a whole number ({second})"}
        groups.append(int(second))
    elif _FRACTION_REMAINDER.search(tail):
        groups.append(base - groups[0])
    return {"base": base, "groups": groups}


# ── PREREQ-2 pattern B: multi-group payroll, Σ(countᵢ × salaryᵢ) ─────────────────────
#
# ALL-OR-NOTHING BY CONSTRUCTION. A prototype of the obvious structural template
# ("<count> <pay-verb> <amount>") was swept over 524 questions: it matched 12 and MIS-PARSED
# SIX of them, two catastrophically —
#   eval_304  "wafanyakazi 20 na MTAJI wa TZS 50,000,000"  -> 20 x 50M = TZS 1 BILLION payroll
#   nat_18    "wafanyakazi wawili mmoja 400000 mwingine 1100000" -> 2 x 400k, not 400k + 1.1M
#   eval_285  "ROBO YA wafanyakazi 24 wanapata 800,000"    -> 24 x 800k; the group is SIX
#   ex_08     two branches stated                          -> caught only the second
# Every one of those replaces an honest clarification with a confident wrong number. So this
# parser never returns a partial result: four validations must ALL pass, or it declines and
# the existing clarification stands.
#
# Magnitude cannot be the count-vs-salary discriminator: MIN_PLAUSIBLE_AMOUNT is 10,000, but
# real rates in this corpus are 1,500/piece and 18,000/day, so a magnitude rule reads 1,500 as
# "a count of 1,500 people". Counts are identified STRUCTURALLY — adjacent to a people-noun or
# carrying the wa- people-class prefix — never by size.
_GROUP_PAY_VERB = r"wanapata|wanalipwa|wana|wenye|wa|analipwa|anapata|lenye"
# wa-prefixed spelled counts stand alone ("WANNE wanaofuata"), bare ones need a people-noun.
_WA_SPELLED = {"mmoja": 1, "wawili": 2, "watatu": 3, "wanne": 4, "watano": 5,
               "wasita": 6, "wanane": 8}
_BARE_SPELLED = {"moja": 1, "mbili": 2, "tatu": 3, "nne": 4, "tano": 5, "sita": 6,
                 "saba": 7, "nane": 8, "tisa": 9, "kumi": 10}
_COUNT_TOKEN = re.compile(
    rf"(?:(?:{_FRACTION_PEOPLE})\s+(\d{{1,4}}|{'|'.join(_BARE_SPELLED)}|{'|'.join(_WA_SPELLED)}))"
    rf"|(?:(\d{{1,4}})\s+(?:{_FRACTION_PEOPLE}))"
    # A bare count directly governing a pay verb ("KATI YAO 4 WANA mishahara ya TZS 700,000",
    # eval_327). The pay verb is what makes it a headcount rather than a loose number; without
    # this the groups are invisible and the whole parse declines.
    rf"|(?:(\d{{1,4}})\s+(?:wana|wanapata|wanalipwa|wenye)\b)"
    rf"|\b({'|'.join(_WA_SPELLED)})\b")
_MONEY_TOKEN = re.compile(
    r"(?:tzs|tsh|sh|shilingi)\s*(\d[\d,]*)|(\d[\d,]{4,})(?!\s*%)", re.IGNORECASE)
_STATED_TOTAL = re.compile(rf"(?:{_FRACTION_PEOPLE})\s+(\d{{1,4}})\s*,?\s*(?:kati\s+ya|ambao)")


def _count_value(match):
    for group in match.groups():
        if group is None:
            continue
        if group.isdigit():
            return int(group)
        return _WA_SPELLED.get(group) or _BARE_SPELLED.get(group)
    return None


def parse_payroll_groups(text):
    """Resolve a multi-group payroll into {'groups': [(count, salary), ...],
    'payroll': Decimal, 'headcount': int}, or {'groups': None, 'reason': ...} when any
    validation fails, or None when no group construction is present.

    VALIDATIONS (all must pass — see the module comment for what each one caught):
      1. every plausible money figure in the question is assigned to a group;
      2. a separately stated total headcount equals the sum of the group counts;
      3. fraction forms take their counts from parse_fraction_of_count, NEVER from the
         number adjacent to the salary (that number is the fraction's BASE);
      4. no wrong-base word is present (mtaji/mauzo/faida/... are not payroll).
    """
    text_l = _PER_PERSON.sub(" ", text.lower()) if False else text.lower()
    salaries = [a for a in parse_amounts(text) if a >= MIN_PLAUSIBLE_AMOUNT]
    if len(salaries) < 2:
        return None                                   # not a multi-group construction

    if not re.search(rf"(?:{_FRACTION_PEOPLE})|(?:{'|'.join(_WA_SPELLED)})", text_l):
        return None
    if not re.search(rf"\b(?:{_GROUP_PAY_VERB})\b", text_l):
        return None

    # (4) a non-payroll base anywhere disqualifies the whole parse.
    if detect_wrong_base(text, None):
        return {"groups": None, "reason": "non-payroll figure present (wrong base)"}

    # INDIVIDUALS, NOT GROUPS. nat_18 ("wafanyakazi WAWILI, MMOJA anapata 400000, MWINGINE
    # 1100000") reads as a group parse of (2 x 400,000) + (1 x 1,100,000) = 1,900,000 when the
    # truth is 400,000 + 1,100,000 = 1,500,000. Found by the 524-sweep, not by a probe. An
    # explicit individual enumeration is never a group construction — hand it to
    # parse_individual_salaries instead.
    if _INDIVIDUAL.search(text_l):
        return None

    # (3) fraction forms: counts come only from C-2.
    fraction = parse_fraction_of_count(text)
    if fraction is not None:
        if fraction.get("groups") is None:
            return {"groups": None, "reason": fraction.get("reason", "unresolved fraction")}
        counts = list(fraction["groups"])
        stated_total = fraction["base"]
    else:
        counts = [c for c in (_count_value(m) for m in _COUNT_TOKEN.finditer(text_l))
                  if c is not None]
        stated = _STATED_TOTAL.search(text_l)
        stated_total = int(stated.group(1)) if stated else None
        if stated_total is not None and counts and counts[0] == stated_total:
            counts = counts[1:]                       # the leading figure is the total
    if not counts:
        return {"groups": None, "reason": "no group headcounts found"}

    # (1) one salary per group, none left over.
    if len(counts) != len(salaries):
        return {"groups": None,
                "reason": f"{len(counts)} groups but {len(salaries)} salaries — "
                          "not every figure is accounted for"}

    groups = list(zip(counts, salaries))
    headcount = sum(counts)
    # (2) a stated total must agree with the groups.
    if stated_total is not None and headcount != stated_total:
        return {"groups": None,
                "reason": f"group counts sum to {headcount} but {stated_total} was stated"}
    payroll = sum(Decimal(c) * s for c, s in groups)
    return {"groups": groups, "payroll": payroll, "headcount": headcount}


# eval_399 shape: INDIVIDUALS enumerated, not a group. PAYE is progressive, so summing two
# salaries into one payroll is not a presentation choice — it is arithmetically wrong
# (400,000 + 1,200,000 answered as one 1,600,000 salary gives TZS 308,000 against a true
# 10,400 + 188,000 = 198,400). Kept deliberately separate from parse_payroll_groups.
_INDIVIDUAL = re.compile(r"\b(mmoja|wa kwanza)\b.{0,40}?\b(?:mwingine|wa pili|mwenzake)\b",
                         re.IGNORECASE | re.DOTALL)


def parse_individual_salaries(text):
    """The distinct per-person salaries in an 'X gets A, the other gets B' question, or None.

    Requires an explicit two-person enumeration AND a matching people count, so a group
    question never lands here."""
    text_l = text.lower()
    if not _INDIVIDUAL.search(text_l):
        return None
    # A two-person enumeration: the stated headcount must be 2, so a group question with an
    # incidental 'mmoja' never lands here. eval_326 (mixed residency, "mwenzake" with no
    # leading 'mmoja') is untouched — it stays on its deferred D-PAYE-1 path.
    if not re.search(rf"(?:{_FRACTION_PEOPLE})\s+(?:2|wawili|mbili)\b", text_l):
        return None
    salaries = [a for a in parse_amounts(text) if a >= MIN_PLAUSIBLE_AMOUNT]
    return salaries if len(salaries) == 2 else None


# PREREQ-2 pattern I. People-nouns parse_count recognises. 'vibarua/kibarua/watumishi' are
# the INFORMAL employment words PREREQ-1 added to routing._PAYROLL_CTX; they were never added
# here, so a question could route to a levy and then be told its headcount was missing.
_PEOPLE_NOUN = r"wafanyakazi|watu|wafanyikazi|waajiriwa|vibarua|kibarua|watumishi|wafanyabiashara"
# Spelled small counts ("wafanyakazi tisa"), on top of the existing tens.
_SPELLED_COUNT = (r"moja|mmoja|wawili|mbili|watatu|tatu|wanne|nne|watano|tano|sita|saba|"
                  r"nane|tisa|kumi|ishirini|thelathini|arobaini|hamsini")
# A SECOND people-quantity anywhere else in the question means the headcount is a SUM, not the
# first number found. Without this guard, edge_p04 ("vibarua 8 wa kudumu na WAWILI wa muda")
# would return 8 and the SDL applicability answer would flip from an honest clarification to a
# confident "Hapana" — when 8 + 2 = 10 means SDL DOES apply. Aggregating the groups is
# PREREQ-2 pattern B; until it lands, decline and keep clarifying. Same guard covers
# edge_p14 / eval_399 / nat_18, which are all B-shaped.
_SECOND_GROUP = re.compile(
    rf"(\w+)\s+(?:na|kati|wengine|wengineo)\s+(?:{_SPELLED_COUNT})\b"
    # headcount CHANGES during the period ("nikaongeza mmoja KUFIKIA 10" — eval_329): the
    # single count is not the whole answer, so decline rather than answer for one period.
    rf"|(\bkufikia\s+\d+|\bnikaongeza\b|\bnikapunguza\b)")
# Swahili compounds numerals with 'na' — "kumi NA WAWILI" is TWELVE, one group, not a second
# one. Caught by test_spelled_and_digit_counts, which this guard broke on its first version.
_COMPOUND_HEAD = re.compile(rf"^(?:{_SPELLED_COUNT}|mia|elfu|laki|milioni)$")


def _has_second_group(text_l):
    for m in _SECOND_GROUP.finditer(text_l):
        if m.group(2):                       # the headcount-changes alternative
            return True
        if not _COMPOUND_HEAD.match(m.group(1) or ""):
            return True
    return False


def parse_count(text):
    """Best-effort employee/people count (small integer), or None.

    Looks for '<people-noun> <N>' or a spelled count ('kumi na wawili'). Returns None when a
    SECOND people-group is mentioned (see _SECOND_GROUP) — a partial headcount asserted as the
    whole is a confident wrong answer, which is exactly what never-guess exists to prevent.
    """
    text_l = text.lower()
    # 'kila mmoja' is the per-person MARKER, not a second group — strip before that check.
    if _has_second_group(re.sub(r"kila\s+(?:mmoja|mfanyakazi|mtu)", " ", text_l)):
        return None
    if has_multiple_groups(text):
        return None
    m = re.search(rf"(?:{_PEOPLE_NOUN})\s+(\d{{1,4}})", text_l)
    if m:
        return int(m.group(1))
    m = re.search(rf"\b(\d{{1,4}})\s+(?:{_PEOPLE_NOUN})", text_l)
    if m:
        return int(m.group(1))
    # spelled count near a people-noun
    m = re.search(rf"(?:{_PEOPLE_NOUN})\s+((?:{_SPELLED_COUNT})(?:\s+na\s+\w+)?)", text_l)
    if m:
        v = _value_small(m.group(1).split())
        if v > 0:
            return int(v)
    return None


# An explicitly stated headcount of ZERO ("sina wafanyakazi kabisa", "nafanya kazi peke
# yangu"). parse_count cannot express this — it looks for a digit or a spelled numeral and
# there is neither — so eval_376 fell through to a clarification asking for a payroll that
# cannot change the answer. Requires an explicit negation or a solo-trader phrase, never the
# mere ABSENCE of a count, so a question that simply omits the headcount still clarifies.
_NO_EMPLOYEES = re.compile(
    rf"\b(?:sina|hakuna|hatuna|sio?\s+na)\s+(?:{_PEOPLE_NOUN})|"
    r"\b(?:peke\s+yangu|mimi\s+pekee|mwenyewe\s+pekee)\b|"
    rf"\b(?:{_PEOPLE_NOUN})\s+(?:sifuri|hakuna)\b")


def states_no_employees(text):
    """True when the question explicitly states there are NO employees (a headcount of 0)."""
    return bool(_NO_EMPLOYEES.search(text.lower()))


# A count is only the WHOLE headcount when it is the only one in the sentence. parse_count
# returns the first match and _SECOND_GROUP only catches a SPELLED second count, so
# "vibarua 8 wanalipwa ... na 4 wanalipwa ..." (gp_02) yields 8 for a 12-person employer.
# That was harmless while nothing asserted on a sub-threshold count; the SDL-zero branch made
# it reachable and it immediately produced "SDL ni TZS 0" for an employer over the threshold —
# the eval_327 class again, caught by the 569-question sweep rather than by a probe.
_ANY_HEADCOUNT = None                       # built lazily; _PEOPLE_NOUN is defined above


def sole_headcount(text):
    """parse_count's value, but ONLY when the sentence states exactly one people-count.

    Returns None when a second count is present, whatever form it takes — the safe direction,
    since a partial headcount asserted as the whole is a confident wrong answer."""
    global _ANY_HEADCOUNT
    if _ANY_HEADCOUNT is None:
        _ANY_HEADCOUNT = re.compile(
            rf"(?:{_PEOPLE_NOUN})\s+(\d{{1,4}})|\b(\d{{1,4}})\s+(?:{_PEOPLE_NOUN})|"
            rf"\b(\d{{1,4}})\s+wana(?:lipwa|pata)\b")
    count = parse_count(text)
    if count is None:
        return None
    hits = {int(next(g for g in m if g)) for m in _ANY_HEADCOUNT.findall(text.lower())}
    return count if len(hits) <= 1 else None


# ============================ AMBIGUITY DETECTORS ============================
# Each returns True when the named ambiguity is present. These are the EXPLICIT,
# inspectable clarification triggers — the never-guess guardrail. A True from any
# relevant detector forces the affected field to LOW confidence regardless of what
# the model claimed, so the orchestrator asks for clarification instead of guessing.

_VAGUE = [
    r"\bwachache\b", r"\bwengi\b", r"\bkadhaa\b", r"\bchache\b", r"\bmdogo\b",
    r"\bmidogo\b", r"\bndogo\b", r"\bkubwa\b", r"\bmengi\b", r"\bwingi\b",
    # PREREQ-2 pattern K: 'kiasi CHA <X>' is "the AMOUNT OF X" — a definite reference, not a
    # vague quantity ("zinabadilisha kiasi cha SDL ninachodaiwa", eval_261). The genuinely
    # vague uses ('mingi kiasi', 'kiasi kidogo') are unaffected, so only 'cha' is excluded
    # alongside the existing 'gani'. Sweep over 500: 2 questions, 0 of them currently computing.
    r"\bkutosha\b", r"\bflani\b", r"\bfulani\b", r"\bkiasi\b(?!\s+(?:gani|cha))",
    r"\bsi wengi\b", r"\bsi chache\b",
]
_APPROX = [
    # PREREQ-2 pattern A1: bare '\bkama\b' fired on the CONDITIONAL/COMPARATIVE "if"/"as"
    # ("KAMA kawaida mishahara inabadilika" = as usual; "KAMA nikizingatia" = if I consider;
    # "na KAMA nikiongeza" = and if I add — eval_283/319/323), vetoing an exact figure that was
    # never approximate. Approximative 'kama' is always followed by a QUANTITY ("kama laki
    # sita", "kama TZS 500,000"), so requiring one keeps eval_284's real hedge while dropping
    # the false ones. Sweep over 500: bare form 39 hits, this form 3 — 0 currently computing.
    r"\bkama\s+(?=\d|laki\b|elfu\b|milioni\b|mia\b|nusu\b|robo\b|shilingi\b|tzs\b)",
    r"\bhivi\b", r"\bka-?\d", r"\baround\b", r"\bna kitu\b", r"\bplus kitu\b",
    r"\bkasoro\b", r"\bushee\b", r"\bushe\b", r"\bnegotiable\b", r"\btakriban[a-z]*",
    r"\bkaribu\b", r"\bhivyo hivyo\b", r"\bna ushee\b", r"\bna kitu kidogo\b",
]
_ANTECEDENT = [
    r"\bhao\b", r"\bwale\b", r"\bile\b", r"\bhiyo\b", r"\bhivyo\b", r"\bhuyo\b",
    r"\bhicho\b", r"\bwao\b", r"\byao\b", r"\bule\b", r"\bhayo\b", r"\bhii\b",
    r"niliokwambia", r"tuliozungumzia", r"niliyokueleza", r"niliosema",
    r"tuliouongea", r"nilichokwambia", r"waliobaki", r"niliyokupa", r"tuliozungumza",
]
_WRONG_BASE = [
    r"\bmauzo\b", r"\brevenue\b", r"\bturnover\b", r"\bfaida\b", r"\bmtaji\b",
    r"\btin\b", r"namba ya simu", r"\bphone\b", r"\befd\b", r"namba ya mashine",
    r"tumesajiliwa brela", r"miaka \d+", r"\bcompany ina mtaji\b",
    # RC-1b: phrasings that slipped through the full-205 run — sales given as a verb
    # ("tunauza"/"kuuza"), a VAT-threshold figure, and a share count/holding.
    r"\btunauza\b", r"\bkuuza\b", r"\btunanunua\b", r"kizingiti cha vat", r"\bhisa\b",
    r"soko la hisa",
    # D-WCF-1: an ASSET / VEHICLE value ("magari ... yana thamani ya TZS 40,000,000") is not a
    # payroll base — WCF/NSSF/SDL are computed on gross payroll, not on the worth of vehicles or
    # assets. eval_259 slipped through (the extractor read the 40M vehicle value as gross payroll
    # and computed WCF on it) because _WRONG_BASE had no asset-value pattern. The specific asset
    # words keep the intent auditable; the general "thamani ya <asset>" prefix catches the class.
    # A payroll figure is never phrased "thamani ya ..." (it is "mshahara wa"/"analipwa"), so this
    # does not touch legitimate payroll questions.
    r"thamani ya magari", r"thamani ya gari", r"thamani ya mali", r"thamani ya vifaa",
    r"thamani ya mtambo", r"thamani ya \w+",
    # D-WCF-2: further non-payroll bases offered for a payroll levy — same class as the
    # D-WCF-1 asset value. A market value, rent, savings, utility cost, bank loan, or business
    # cash flow is not gross payroll; WCF/SDL/NSSF/PAYE are computed on wages only. Full-400
    # sweep: these 6 (eval_253/254/255/258/260/261) offered such a figure as the base, and
    # eval_254 was mis-computed (WCF = 0.5% x 25,000,000 shop value). Two precision choices:
    # 'gharama za umeme'/'maji' (NOT a broad 'gharama za \w+', which would hit 'gharama za
    # mishahara'), and '\bdeni\b' (its boundary catches 'deni la benki' but NOT 'madeni' in
    # eval_324 — that is D-WCF-3's distinct inverse problem, kept out of this additive scope).
    r"bei ya soko",                            # eval_254 shop market value
    r"kodi ya pango", r"\bpango\b",            # eval_258 office rent
    r"\bakiba\b",                              # eval_260 bank savings
    r"gharama za umeme", r"gharama za maji",   # eval_261 utility cost
    r"\bdeni\b",                               # eval_253 bank loan
    r"mzunguko wa fedha", r"cash ?flow",       # eval_255 business cash flow
]
_ALLOWANCE = [
    r"\bposho\b", r"\bbonasi\b", r"\ballowance\b", r"\bgross\b", r"\bnet\b",
    r"take home", r"baada ya kukatwa", r"bila posho", r"\bbima\b", r"\bovertime\b",
    r"\blikizo\b", r"malipo ya likizo", r"commission",
    # PREREQ-2 pattern G: 'pamoja na' meant "salary INCLUDING <component>" — but bare, it also
    # matched "mwajiri PAMOJA NA mfanyakazi" (employer TOGETHER WITH employee), which names the
    # NSSF PARTY, not a pay component. eval_242 states its salary plainly (TZS 800,000) and was
    # asked whether that figure was gross or net. Requiring an actual pay-component object keeps
    # the intended sense. Sweep over 500: 3 'pamoja na' occurrences, only eval_242 changes;
    # eval_114 (a deadline fact) and ap_07 never reached this detector.
    r"pamoja na\s+(?:posho|bonasi|allowance|marupurupu|malazi|chakula|usafiri|likizo|"
    r"overtime|commission|kodi|vat)",
    # VAT-inclusive vs exclusive is the same gross/net base ambiguity for a money
    # figure — "is this 180M with or without VAT?" must be clarified, not assumed.
    r"jumuisha vat", r"vat au la", r"pamoja na vat", r"bila vat", r"ikiwa na vat",
    # RC-3: net/take-home in noun form ("baada ya makato", "mkononi"), and a per-diem
    # figure explicitly flagged as NOT salary ("siyo mshahara", "malazi na chakula").
    r"baada ya makato", r"\bmkononi\b", r"siyo mshahara", r"\bsio mshahara\b",
    r"si mshahara", r"\bmalazi\b", r"posho ya safari",
]

# RC-3: a figure quoted in a foreign currency is not a TZS payroll base — it needs
# conversion before use, so the extractor must clarify rather than read "dola 300" as 300.
_CURRENCY = [
    r"\bdola\b", r"\busd\b", r"\bdollar", r"\$", r"\beuro\b", r"\bpauni\b",
    r"\bpound", r"\bksh\b", r"shilingi za kenya", r"\bgbp\b",
]


def _any(patterns, text_l):
    return any(re.search(p, text_l) for p in patterns)


def detect_vague_quantity(text):
    return _any(_VAGUE, text.lower())


def detect_approximation(text):
    return _any(_APPROX, text.lower())


# PREREQ-2 pattern H. A demonstrative that MODIFIES a named noun is not a dangling
# reference: "je ILE TOZO ya mafunzo" is "that training levy" — the referent is right there
# (edge_p04). Only the DEFINITE nouns below count, deliberately not any following word: the
# documented RC-2 case "wale WAWILI waliobaki" (extract_153) is a demonstrative followed by a
# pronoun-count and MUST keep firing, which a general '\w+' suppression would break.
# NOT 'hesabu'/'fedha'/'deni': "ILE HESABU ya wiki iliyopita" (eval_299) is a genuine dangling
# reference — the calculation itself is the unresolved thing. Only nouns naming a levy, a pay
# component, or an institution, where the demonstrative is doing ordinary definite reference.
_ANTECEDENT_NOUNS = (r"tozo|kodi|mshahara|mishahara|malipo|makato|mchango|michango|ada|"
                     r"faini|sheria|kampuni|biashara|leseni")
_ANTECEDENT_MODIFIED = re.compile(
    r"\b(?:ile|hiyo|hii|hayo|hicho|huyo|ule|wale|hao|yao|wao)\s+(?:ya\s+|wa\s+)?"
    rf"(?:{_ANTECEDENT_NOUNS})\b")


def detect_missing_antecedent(text):
    """Antecedent pronoun present AND no explicit number to anchor on.

    RC-2: 'no number' means no PLAUSIBLE amount — a spelled small count like 'wawili'
    (2) in "wale wawili waliobaki" is a pronoun-count, not a figure, and must not mask
    the missing antecedent (extract_153).

    PREREQ-2 (H): demonstratives modifying a named compliance noun are stripped first, so
    "ile tozo ya mafunzo" no longer reads as a dangling reference."""
    text_l = _ANTECEDENT_MODIFIED.sub(" ", text.lower())
    if not _any(_ANTECEDENT, text_l):
        return False
    plausible = [a for a in parse_amounts(text) if a >= MIN_PLAUSIBLE_AMOUNT]
    return not plausible and parse_count(text) is None


# PREREQ-2 patterns A2 + J — ANCHORED FIGURE SELECTION.
#
# _amount_field gives up whenever it parses more than one figure ("role ambiguous") — the
# single biggest blocker in the Class-A set. This does NOT relax that rule: it engages ONLY
# where the parser has already given up, and only when exactly ONE figure carries an
# unambiguous anchor naming it as the intended amount:
#   J  — a payroll word:      "ina MISHAHARA TZS 4,800,000 kwa watu 13, na madeni TZS 2,000,000"
#   A2 — a precision marker:  "kama laki sita hivi, sawa TZS 610,000 KAMILI"
# Two anchored figures, or none, means the ambiguity is real and the clarification stands.
# Measured over 500 questions: J engages on 2, A2 on 3, none currently computing.
_PRECISION = r"hasa|haswa|kamili|sawasawa|kabisa"
_ANCHORED = [
    ("payroll", re.compile(r"(?:mshahara|mishahara)\w*\s+(?:wa\s+|ya\s+|ni\s+|za\s+)*"
                           r"(?:tzs\s*|tsh\s*|sh\s*)?(\d[\d,\.]*)", re.IGNORECASE)),
    ("precision", re.compile(rf"(?:{_PRECISION})\s+(?:ni\s+|ya\s+|kwa\s+)*"
                             r"(?:tzs\s*|tsh\s*|sh\s*)?(\d[\d,\.]*)", re.IGNORECASE)),
    ("precision", re.compile(r"(?:tzs\s*|tsh\s*|sh\s*)(\d[\d,\.]*)\s+(?:" + _PRECISION + r")",
                             re.IGNORECASE)),
]


def _to_decimal_amount(raw):
    try:
        return Decimal(str(raw).replace(",", "").rstrip("."))
    except (InvalidOperation, ValueError):
        return None


# MULTI-GROUP / MULTI-PERIOD BLOCK — the most important guard in this module.
#
# Found by the 500-question sweep, not by a probe: without it, eval_327 ("Nina wafanyakazi 10,
# KATI YAO 4 wana MISHAHARA YA TZS 700,000 na 6 wana TZS 300,000") anchors on the FIRST group's
# salary and computes WCF on 700,000 instead of the real 4,600,000 payroll — 0.5% x 700,000 =
# TZS 3,500 asserted confidently in place of TZS 23,000. That is precisely the confident-wrong-
# number failure never-guess exists to prevent, and it is worse than the clarification it
# replaces. When the question describes SEVERAL pay groups or SEVERAL periods, no single figure
# is "the" payroll, so anchoring must not run at all; summing the groups is pattern B.
_GROUP_MARKERS = re.compile(
    r"kati\s+ya(?:o|nu|ke|tu)\b|\bwengine\w*\b|wanaofuata|wa\s+mwisho|wa\s+kwanza|"
    r"\btawi\b|\bmatawi\b|\bkundi\b|\bmakundi\b")
# EMPLOYMENT-TYPE split, held SEPARATE from the markers above because it is only a split when
# BOTH sides are named. The Phase D re-run (030a5ff) caught this: as a bare alternative,
# `wa muda` fired on eval_368 ("wafanyakazi 12 lakini WOTE ni WA MUDA") — one group described
# as part-time, not two groups — which made has_multiple_groups True, parse_count None, and the
# applicability route ask for a headcount that was in the question. It also fired on eval_377
# ("MFANYAKAZI WA MUDA analipwa...", a single employee) and on eval_225 ("muda wa siku 30"),
# a time period with no employment sense at all. Requiring both sides keeps the two genuine
# splits — edge_p04 and ex_10, both "<n> wa kudumu na <n> wa muda" — and drops all three.
_PART_TIME = re.compile(r"wa\s+muda\b")
_PERMANENT = re.compile(r"wa\s+kudumu\b")
_MONTHS = re.compile(r"\b(januari|februari|machi|aprili|mei|juni|julai|agosti|septemba|"
                     r"oktoba|novemba|desemba)\b")


def has_multiple_groups(text):
    """True when the question describes more than one pay group or more than one period, so
    no single parsed figure can be the whole payroll."""
    text_l = text.lower()
    if _GROUP_MARKERS.search(text_l):
        return True
    if _PART_TIME.search(text_l) and _PERMANENT.search(text_l):
        return True
    return len(set(_MONTHS.findall(text_l))) >= 2


def select_anchored_amount(text, amounts):
    """The one figure explicitly named as the amount, or None when the question is genuinely
    ambiguous.

    `amounts` is the already-parsed candidate list; only a value present there can be
    returned, so this can never introduce a figure the parser did not itself see.

    Returns (value, kind) where kind is 'payroll' or 'precision', or (None, None)."""
    if len(amounts) < 2 or has_multiple_groups(text):
        return None, None
    pool = {Decimal(a) for a in amounts}
    found = {}
    for kind, pattern in _ANCHORED:
        for raw in pattern.findall(text):
            value = _to_decimal_amount(raw)
            if value is not None and value in pool:
                found[value] = kind
    if len(found) != 1:
        return None, None
    value, kind = next(iter(found.items()))
    return value, kind


def has_precision_override(text):
    """A hedge word is present, but the SAME sentence supplies an exact figure and marks it as
    exact ("wengi sana karibu, LAKINI HASA NI 18"; "sawa TZS 610,000 KAMILI"). The hedge then
    describes what the speaker first said, not the figure they went on to give, so the global
    vague/approximation veto must not discard it.

    Deliberately requires an explicit precision MARKER. eval_281 ("unafika TZS 920,000 hivi")
    has none — a bare 'hivi' after a figure really does mean "about", and treating it as exact
    would loosen never-guess for a single row. Permanent won't-fix, not a deferred item."""
    if not re.search(rf"\b(?:{_PRECISION})\b", text.lower()):
        return False
    return any(a >= MIN_PLAUSIBLE_AMOUNT for a in parse_amounts(text))


def detect_foreign_currency(text):
    """A figure quoted in a non-TZS currency (dola/USD/euro/...) — needs conversion."""
    return _any(_CURRENCY, text.lower())


def detect_wrong_base(text, computation_type):
    """The slot wants a PAYROLL figure but the number offered is a non-payroll base
    (sales/turnover/capital/threshold/registration id/share count).

    RC-1a: this must run for the payroll levies AND for the generic payroll slot
    (computation_type is None — the path vat/brela/osha/gn487a questions take, exactly
    where sales/capital figures get misread as payroll). It is NOT run for a genuinely
    turnover-based computation type (e.g. 'vat'), where sales IS the right base."""
    if computation_type not in ("sdl", "nssf", "wcf", "paye", None):
        return False
    return _any(_WRONG_BASE, text.lower())


# PREREQ-1. A COUNT of non-payroll objects offered as a levy base ("mashine 9",
# "invoice 450", "matawi 6", "magari 14" — eval_263/265/266/269). _WRONG_BASE has no
# pattern for these, so detect_wrong_base misses them entirely and the small-int guard
# catches them instead: a true observation ("implausibly small for a payroll") with the
# wrong consequence (SDL then asks for a headcount).
#
# NARROWEST FORM (R17): noun + digit, never a bare noun. A bare 'magari'/'matawi' would
# fire on legitimate compute questions that merely mention company assets — see the
# ap_01..ap_05 probes in eval/accuracy_gate/applicability_adversarial_in_scope_017.jsonl.
_OBJECT_COUNT = re.compile(
    r"\b(mashine|magari|gari|invoice|ankara|matawi|tawi|vifaa|mitambo|mtambo|"
    r"kompyuta|pikipiki)\s+\d+"
    r"|\bidadi ya (mashine|magari|invoice|ankara|matawi|vifaa|mitambo)\b")

# A payroll figure IS on the table -> never reject the base. Found by the R17 adversarial
# probes (ap_07..ap_10), NOT by the corpus: a wrong-base WORD can sit in a question whose
# only FIGURE is a legitimate payroll ("pamoja na kodi ya pango, nalipa mishahara TZS
# 3,600,000 kwa wafanyakazi 11"). A figure count alone does not separate those cases — the
# count is 1 and the figure is the RIGHT base. None of the 11 wrong-base gate questions
# contains 'mshahara'/'mishahara' at all, so requiring its ABSENCE separates the two classes
# exactly. It fails SAFE: a question that mentions payroll falls back to the existing
# clarification, never to a wrong assertion.
_PAYROLL_WORD = re.compile(r"\bmshahara\w*|\bmishahara\w*")


def detect_rejectable_base(text, computation_type):
    """Return 'wrong_base' | 'object_count' | None — is the ONLY base on offer a
    non-payroll figure, such that the correct reply names the real base instead of asking
    for a salary? (PREREQ-1; consumed by the orchestrator's compute path.)

    Structural by design: it keys off detect_wrong_base() and the parsed amounts rather
    than off Extraction's reason STRING. eval_261's wrong_base reason is overwritten by a
    (false) vague_quantity global veto — '_VAGUE' matches 'kiasi cha SDL ninachodaiwa', a
    definite reference, not a vague quantity — so a reason-string check would miss it. The
    _VAGUE over-match itself is logged for PREREQ-2 and deliberately not touched here.

    Never fires when a payroll word is present (see _PAYROLL_WORD), and 'wrong_base'
    additionally requires the non-payroll figure to be the ONLY plausible amount — which is
    what keeps eval_324 / nat_21 (a real payroll figure IS present, merely unparsed among
    several) on the existing clarification path, where PREREQ-2 owns them."""
    if computation_type not in ("sdl", "nssf", "wcf", "paye"):
        return None
    text_l = text.lower()
    if _PAYROLL_WORD.search(text_l):
        return None
    plausible = [a for a in parse_amounts(text) if a >= MIN_PLAUSIBLE_AMOUNT]
    if _OBJECT_COUNT.search(text_l) and not plausible:
        return "object_count"
    if detect_wrong_base(text, computation_type) and len(plausible) == 1:
        return "wrong_base"
    return None


def rejectable_base_amount(text):
    """The single non-payroll figure to echo back in a base rejection, or None when what
    was offered was a COUNT of objects rather than a money figure."""
    plausible = [a for a in parse_amounts(text) if a >= MIN_PLAUSIBLE_AMOUNT]
    return plausible[0] if len(plausible) == 1 else None


def detect_allowance_ambiguity(text):
    return _any(_ALLOWANCE, text.lower())


# period markers -> monthly-conversion divisor (payroll/salary are assessed monthly)
_PERIOD = [
    (re.compile(r"\bkwa mwaka\b|\bya mwaka\b|\bmwaka jana\b|\bmwaka uliopita\b|\bkwa mwaka huu\b|\bkila mwaka\b"), 12, "annual"),
    (re.compile(r"\brobo mwaka\b|\bkwa robo\b|\bkila robo\b"), 3, "quarter"),
    (re.compile(r"\bnusu mwaka\b"), 6, "half_year"),
    (re.compile(r"\bkila wiki\b|\bkwa wiki\b(?!\s+mbili)"), None, "week"),
    (re.compile(r"\bwiki mbili\b|\bkila wiki mbili\b"), None, "biweekly"),
    (re.compile(r"\bkwa siku\b|\bkila siku\b"), None, "daily"),
]


def detect_period(text):
    """Return (divisor_or_None, label) for a non-monthly period marker, else (1,'monthly').

    A numeric divisor (12/3/6) means the amount can be converted to monthly
    deterministically. None means the conversion needs extra info (days/weeks worked)
    -> the caller should treat it as needing clarification, not silently convert.
    """
    text_l = text.lower()
    for rx, divisor, label in _PERIOD:
        if rx.search(text_l):
            return divisor, label
    return 1, "monthly"

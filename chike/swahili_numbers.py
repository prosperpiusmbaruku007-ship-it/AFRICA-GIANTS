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
from decimal import Decimal

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


def parse_count(text):
    """Best-effort employee/people count (small integer), or None.

    Looks for 'wafanyakazi/watu/wafanyikazi <N>' or a spelled count ('kumi na wawili').
    """
    text_l = text.lower()
    m = re.search(r"(?:wafanyakazi|watu|wafanyikazi|waajiriwa)\s+(\d{1,4})", text_l)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(\d{1,4})\s+(?:wafanyakazi|watu)", text_l)
    if m:
        return int(m.group(1))
    # spelled count near a people-noun
    m = re.search(r"(?:wafanyakazi|watu)\s+((?:kumi|ishirini|thelathini|arobaini|hamsini)"
                  r"(?:\s+na\s+\w+)?)", text_l)
    if m:
        v = _value_small(m.group(1).split())
        if v > 0:
            return int(v)
    return None


# ============================ AMBIGUITY DETECTORS ============================
# Each returns True when the named ambiguity is present. These are the EXPLICIT,
# inspectable clarification triggers — the never-guess guardrail. A True from any
# relevant detector forces the affected field to LOW confidence regardless of what
# the model claimed, so the orchestrator asks for clarification instead of guessing.

_VAGUE = [
    r"\bwachache\b", r"\bwengi\b", r"\bkadhaa\b", r"\bchache\b", r"\bmdogo\b",
    r"\bmidogo\b", r"\bndogo\b", r"\bkubwa\b", r"\bmengi\b", r"\bwingi\b",
    r"\bkutosha\b", r"\bflani\b", r"\bfulani\b", r"\bkiasi\b(?!\s+gani)",
    r"\bsi wengi\b", r"\bsi chache\b",
]
_APPROX = [
    r"\bkama\b", r"\bhivi\b", r"\bka-?\d", r"\baround\b", r"\bna kitu\b", r"\bplus kitu\b",
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
]
_ALLOWANCE = [
    r"\bposho\b", r"\bbonasi\b", r"\ballowance\b", r"\bgross\b", r"\bnet\b",
    r"take home", r"baada ya kukatwa", r"bila posho", r"\bbima\b", r"\bovertime\b",
    r"\blikizo\b", r"malipo ya likizo", r"pamoja na", r"commission",
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


def detect_missing_antecedent(text):
    """Antecedent pronoun present AND no explicit number to anchor on.

    RC-2: 'no number' means no PLAUSIBLE amount — a spelled small count like 'wawili'
    (2) in "wale wawili waliobaki" is a pronoun-count, not a figure, and must not mask
    the missing antecedent (extract_153)."""
    text_l = text.lower()
    if not _any(_ANTECEDENT, text_l):
        return False
    plausible = [a for a in parse_amounts(text) if a >= MIN_PLAUSIBLE_AMOUNT]
    return not plausible and parse_count(text) is None


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

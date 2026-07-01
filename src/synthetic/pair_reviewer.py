import json
import os
import re

VALID_GN_NUMBERS  = {'GN487A', 'GN605A'}
# Genuine Tanzanian rates that appear in primary TRA sources (transport/film WHT 5%,
# certain levies 1%/2%, presumptive 2.5%, mineral royalty 17%) were previously rejected
# by CHECK 6 even though they are real. Extended to cover the published rate set.
VALID_PERCENTAGES = {
    0.0, 0.5, 1.0, 2.0, 2.5, 3.0, 3.5, 5.0, 6.0, 8.0, 10.0,
    15.0, 16.0, 17.0, 18.0, 20.0, 25.0, 30.0, 33.4,
}

VALID_SUBDOMAINS = {
    'vat_registration', 'paye', 'sdl_compliance', 'gn487a',
    'brela_registration', 'nssf_contributions', 'osha_registration',
    'efd_compliance', 'vat_withholding', 'out_of_corpus', 'wcf_compliance',
}
VALID_ANSWER_TYPES = {
    'yes_no', 'number', 'definition', 'procedure', 'penalty', 'out_of_corpus_refusal',
}
VALID_SOURCE_DOMAINS = {
    'tra.go.tz', 'brela.go.tz', 'osha.go.tz', 'nssf.or.tz',
    'wcf.go.tz', 'immigration.go.tz', 'labour.go.tz', 'ppra.go.tz', 'tanzlii.org',
}

# Each subdomain must cite its OWN authority. Prevents e.g. a WCF pair citing tra.go.tz
# (the WCF->TRA misattribution observed in the wcf_michango run).
SUBDOMAIN_DOMAIN_MAP = {
    'vat_registration':   ['tra.go.tz'],
    'paye':               ['tra.go.tz'],
    'sdl_compliance':     ['tra.go.tz'],
    'gn487a':             ['immigration.go.tz'],
    'brela_registration': ['brela.go.tz'],
    'nssf_contributions': ['nssf.or.tz'],
    'osha_registration':  ['osha.go.tz'],
    'efd_compliance':     ['tra.go.tz'],
    'vat_withholding':    ['tra.go.tz'],
    'wcf_compliance':     ['wcf.go.tz'],
    'out_of_corpus':      [],  # refusals need no domain citation
}

RAW_REVIEWED_DIR = 'data/raw/reviewed'


def _check1_numerical_accuracy(pair: dict, locked_facts: dict) -> list:
    output = pair.get('output', '')
    nums   = re.findall(r'(\d[\d,\.]*)\s*(%|TZS|milioni|asilimia)', output, re.IGNORECASE)
    failures = []
    for num, unit in nums:
        found = any(
            num in (fact.get('correct_value', str(fact)) if isinstance(fact, dict) else str(fact))
            for key, fact in locked_facts.items() if key != '_meta'
        )
        if not found:
            failures.append(f"CHECK1: unverified number {num}{unit} not in locked_facts")
    return failures


def _check2_schema(pair: dict) -> list:
    failures = []
    for field in ('instruction', 'input', 'output', 'system', 'subdomain', 'answer_type'):
        if field not in pair:
            failures.append(f"CHECK2: missing field '{field}'")
    instr_len  = len(pair.get('instruction', ''))
    output_len = len(pair.get('output', ''))
    if not (10 <= instr_len <= 200):
        failures.append(f"CHECK2: instruction length {instr_len} not in [10,200]")
    if not (20 <= output_len <= 500):
        failures.append(f"CHECK2: output length {output_len} not in [20,500]")
    if pair.get('subdomain') not in VALID_SUBDOMAINS:
        failures.append(f"CHECK2: invalid subdomain '{pair.get('subdomain')}'")
    if pair.get('answer_type') not in VALID_ANSWER_TYPES:
        failures.append(f"CHECK2: invalid answer_type '{pair.get('answer_type')}'")
    return failures


def _check3_refusal_discipline(pair: dict) -> list:
    if pair.get('answer_type') != 'out_of_corpus_refusal':
        return []
    output    = pair.get('output', '')
    sentences = [s.strip() for s in re.split(r'[.!?]', output) if s.strip()]
    if len(sentences) > 2:
        return [f"CHECK3: refusal too verbose ({len(sentences)} sentences, max 2)"]
    return []


def _check4_source_citation(pair: dict) -> list:
    output    = pair.get('output', '')
    subdomain = pair.get('subdomain', '')

    if subdomain == 'out_of_corpus':
        return []  # refusals don't need a domain citation

    allowed = SUBDOMAIN_DOMAIN_MAP.get(subdomain)
    if not allowed:
        # Unknown subdomain, or one with no mapped authority -> fail safe.
        return [f"CHECK4: subdomain '{subdomain}' has no mapped citation domain"]

    out_low = output.lower()

    # 1) some valid authority domain must be present at all
    if not any(d in out_low for d in VALID_SOURCE_DOMAINS):
        return ["CHECK4: no valid .go.tz domain found in output"]

    # 2) and it must be the CORRECT authority for this subdomain
    if not any(d in out_low for d in allowed):
        return [f"CHECK4: subdomain '{subdomain}' requires {allowed} "
                f"but output cites a different authority"]

    return []


def _check5_completeness(pair: dict) -> list:
    failures = []
    output   = pair.get('output', '')
    if output and output[-1] not in '.!?':
        failures.append("CHECK5: output does not end with sentence-ending punctuation")
    for placeholder in ('TODO', 'PLACEHOLDER', 'INSERT', '...'):
        if placeholder in output:
            failures.append(f"CHECK5: placeholder '{placeholder}' in output")
    if len(output.split()) < 15:
        failures.append(f"CHECK5: output too short ({len(output.split())} words, min 15)")
    return failures


def _check6_hallucination_guard(pair: dict) -> list:
    failures = []
    output   = pair.get('output', '')

    for gn in re.findall(r'GN\s*(\d+[A-Z]*)', output, re.IGNORECASE):
        canonical = f"GN{gn.upper().replace(' ', '')}"
        if canonical not in VALID_GN_NUMBERS:
            failures.append(f"CHECK6: invalid GN number '{canonical}' (valid: {sorted(VALID_GN_NUMBERS)})")

    for pct in re.findall(r'(\d+\.?\d*)\s*%', output):
        try:
            val = float(pct)
            if val not in VALID_PERCENTAGES:
                failures.append(f"CHECK6: unexpected percentage {val}% "
                                 f"(valid: {sorted(VALID_PERCENTAGES)})")
        except ValueError:
            pass

    return failures


# ---- CHECK 7: GN487A activity-accuracy guard -------------------------------
# The exact Schedule from the GN487A Official Gazette, 28 July 2025 (verified
# verbatim from the primary PDF). Keyword sets used to sanity-check any pair that
# names a specific Schedule number against the real activity for that number.
GN487A_SCHEDULE = {
    1:  ['wholesale', 'retail', 'sale of goods', 'uuzaji wa bidhaa', 'jumla', 'rejareja'],
    2:  ['mobile money', 'uhamisho wa pesa', 'pesa za simu'],
    3:  ['repair', 'mobile phone', 'electronic', 'ukarabati', 'simu', 'vifaa vya elektroniki'],
    4:  ['salon', 'saluni', 'nywele', 'hair'],
    5:  ['cleanliness', 'cleaning', 'usafi', 'ofisi', 'mazingira'],
    6:  ['mining', 'madini', 'small-scale', 'uchimbaji'],
    7:  ['postal', 'parcel', 'delivery', 'posta', 'vifurushi'],
    8:  ['tour', 'guiding', 'utalii', 'uongozaji'],
    9:  ['radio', 'television', 'redio', 'televisheni', 'runinga'],
    10: ['museum', 'curio', 'jumba la kumbukumbu', 'sanaa'],
    11: ['brokerage', 'agency', 'real estate', 'wakala', 'ardhi', 'dalali'],
    12: ['clearing', 'forwarding', 'forodha'],
    13: ['crop', 'mazao', 'shamba', 'kilimo'],
    14: ['gambling', 'casino', 'kamari', 'bahati nasibu'],
    15: ['micro', 'small industries', 'viwanda vidogo'],
}

# Activities the model has hallucinated as "prohibited" but which are NOT in the
# GN487A Schedule. A gn487a pair mentioning any of these is almost always fabricating
# a restriction that does not exist -> reject.
NOT_IN_GN487A_SCHEDULE = [
    'ushonaji', 'tailoring', 'uvuvi', 'fishing', 'dagaa', 'ujenzi', 'construction',
    'usafirishaji wa abiria', 'passenger transport', 'bodaboda', 'chakula',
    'mgahawa', 'restaurant', 'benki', 'banking', 'bima', 'insurance',
    'dawa', 'pharmacy', 'shule', 'school', 'hospitali', 'hospital',
]


def _check7_gn487a_accuracy(pair: dict) -> list:
    """CHECK 7 -- fires only for gn487a pairs. Rejects pairs that (a) claim a
    non-listed activity is prohibited, or (b) cite a Schedule number outside 1-15,
    or (c) name a Schedule number whose real activity keywords are absent (a
    wrong number<->activity mapping). Backstop for the seed generator, which was
    observed inventing 'activity 14 = tailoring' etc."""
    if pair.get('subdomain') != 'gn487a':
        return []
    combined = (pair.get('instruction', '') + ' ' + pair.get('output', '')).lower()
    failures = []
    for term in NOT_IN_GN487A_SCHEDULE:
        if term in combined:
            failures.append(f"CHECK7: names non-listed activity '{term}' as GN487A-restricted")
            break
    # A specific Schedule claim: English "activity N" (bare N ok -- the generator
    # writes "(activity 14 in the Schedule)"), or Swahili "shughuli namba N" (require
    # the namba/no/number qualifier so a bare count like "shughuli 15 zilizoorodheshwa"
    # is NOT mistaken for a claim about activity #15).
    claims = re.findall(r'activity\s*(?:no\.?|number)?\s*(\d{1,2})'
                        r'|shughuli\s*(?:namba|no\.?|number)\s*(\d{1,2})', combined)
    for a, b in claims:
        n = int(a or b)
        if n < 1 or n > 15:
            failures.append(f"CHECK7: Schedule number {n} out of range 1-15")
        elif not any(kw in combined for kw in GN487A_SCHEDULE[n]):
            failures.append(f"CHECK7: activity #{n} cited but no matching Schedule keyword (wrong number<->activity)")
    return failures


def review_pairs(pairs: list, batch_num: str = None,
                 locked_facts: dict = None) -> tuple:
    if locked_facts is None:
        try:
            with open('scripts/locked_facts.json', encoding='utf-8') as f:
                locked_facts = json.load(f)
        except Exception:
            locked_facts = {}

    approved = []
    flagged  = []
    rejected = []
    results  = []

    for pair in pairs:
        failures  = []
        failures += _check1_numerical_accuracy(pair, locked_facts)
        failures += _check2_schema(pair)
        failures += _check3_refusal_discipline(pair)
        failures += _check4_source_citation(pair)
        failures += _check5_completeness(pair)
        failures += _check6_hallucination_guard(pair)
        failures += _check7_gn487a_accuracy(pair)

        n = len(failures)
        if n == 0:
            approved.append(pair)
            status = 'APPROVED'
        elif n <= 2:
            p_copy = dict(pair)
            p_copy['_failed_checks'] = failures
            flagged.append(p_copy)
            status = 'FLAGGED'
        else:
            rejected.append(pair)
            status = 'REJECTED'

        results.append({
            'instruction': pair.get('instruction', '')[:80],
            'status':   status,
            'failures': failures,
        })

    if batch_num is not None:
        out_path = os.path.join(RAW_REVIEWED_DIR, f'batch_{batch_num}_results.json')
        os.makedirs(RAW_REVIEWED_DIR, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({
                'batch':    batch_num,
                'total':    len(pairs),
                'approved': len(approved),
                'flagged':  len(flagged),
                'rejected': len(rejected),
                'results':  results,
            }, f, indent=2, ensure_ascii=False)

    print(f"[reviewer] {len(pairs)} pairs: "
          f"{len(approved)} approved, {len(flagged)} flagged, {len(rejected)} rejected")
    return approved, flagged, rejected

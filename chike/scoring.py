"""Shared gate scorer — the single definition of score_question and its helpers.

Extracted from kaggle/eval.py (and its copy in kaggle/eval_orchestrator.py) so both
gate runners score identically from one source, following the same pattern as
chike/prompting.py and chike/generation_cleanup.py. Leaf module: imports only `re`,
no chike-internal or __file__ dependencies, so it works both as a normal import
(eval_orchestrator.py git-clones the package) and via fetch-and-exec (eval.py).

REFUSAL_PHRASES is passed in as a parameter (each runner loads it from chike_config).
"""

import re

SWAHILI_NUMBERS = {
    'moja': 1, 'mbili': 2, 'tatu': 3, 'nne': 4, 'tano': 5,
    'sita': 6, 'saba': 7, 'nane': 8, 'tisa': 9, 'kumi': 10,
    'ishirini': 20, 'thelathini': 30, 'arobaini': 40,
    'hamsini': 50, 'sitini': 60, 'sabini': 70,
    'themanini': 80, 'tisini': 90, 'mia': 100,
    'elfu': 1_000, 'milioni': 1_000_000,
}


def extract_numbers(text):
    text_lower = text.lower()
    nums = set()
    for m in re.findall(r'asilimia\s*(\d+(?:\.\d+)?)', text_lower):
        nums.add(m)
    for m in re.findall(r'(\d+(?:\.\d+)?)\s*%', text_lower):
        nums.add(m)
    for m in re.findall(r'tzs\s*([\d,]+)', text_lower):
        nums.add(m.replace(',', ''))
    # Comma-grouped numbers must be captured as ONE token. The old pattern
    # r'\b(\d{3,}(?:,\d+)*)\b' anchored on a 3+-digit FIRST group, so any figure
    # whose leading group is 1-2 digits ('40,000', '1,000,000', '36,000,000')
    # failed at the start; the engine then re-anchored after a comma and captured
    # a garbage fragment ('000' / '000000'), dropping the real value. A shared
    # bare '000' then satisfied number-type scoring for almost any comma-formatted
    # payroll answer regardless of the actual figures. Fix: match either a proper
    # thousands-grouped number (1-3 digits + one-or-more exactly-3-digit groups)
    # OR a bare 3+-digit run. The comma form is the first alternative so it wins
    # the anchor; no fragment is ever emitted. (3-digit-lead cases like '100,000'
    # that already worked canonicalize to the same value, so they do not regress.)
    for m in re.findall(r'\b(\d{1,3}(?:,\d{3})+|\d{3,})\b', text_lower):
        nums.add(m.replace(',', ''))
    for word, val in SWAHILI_NUMBERS.items():
        if re.search(r'\b' + word + r'\b', text_lower):
            nums.add(str(int(val)))
    # BUG 3 fix — multiplier composition. Without this, 'milioni 5' contributed only
    # the bare word-value 1_000_000 (from SWAHILI_NUMBERS) and dropped the '5', so it
    # never matched '5,000,000' (a correct answer scored WRONG — e.g. eval_165). Compose
    # each multiplier word with its adjacent number so both spellings canonicalize equally.
    _MULT = {'bilioni': 1_000_000_000, 'billion': 1_000_000_000,
             'milioni': 1_000_000, 'million': 1_000_000,
             'laki': 100_000, 'elfu': 1_000, 'thousand': 1_000}
    for word, mult in _MULT.items():
        for m in re.findall(r'(\d+(?:\.\d+)?)\s*' + word + r'\b', text_lower):
            nums.add(str(int(float(m) * mult)))
        for m in re.findall(r'\b' + word + r'\s*(\d+(?:\.\d+)?)', text_lower):
            nums.add(str(int(float(m) * mult)))
    # 'M' / 'bn' shorthand on a bare figure: '200M' -> 200000000, '1.5bn' -> 1500000000.
    for m in re.findall(r'(\d+(?:\.\d+)?)\s*m\b', text_lower):
        nums.add(str(int(float(m) * 1_000_000)))
    for m in re.findall(r'(\d+(?:\.\d+)?)\s*bn\b', text_lower):
        nums.add(str(int(float(m) * 1_000_000_000)))
    return nums


def normalize(text):
    return ' '.join(text.lower().split())


# NOTE: known-fragile heuristic fix for the ramble-credits-wrong-answer bug found in
# v16 orchestrator testing (eval_045, eval_101 — see PROGRESS.md). It scores the polarity
# of the SUBSTANTIVE answer (the first block, before any trailing fabricated ramble) via
# the leading yes/no word + Swahili negation markers, NOT a substring scan of the full
# text. It is NOT a robust yes/no classifier — a differently-shaped answer (an implicit
# yes/no with no leading word and no negation marker) can still be misclassified.
# Future improvement: score only the first sentence / first N chars, not the full text,
# so trailing content (ramble or otherwise) cannot influence the score at all.
_YN_NEG = re.compile(r'\b(hakuna|haiwezi|hairuhusiwi|haiondoi|haipatikani|hawezi|'
                     r'haihusiki|haistahili|hairuhusu|haitakiwi|haina|haiathiri)\b')
_YN_YES = re.compile(r'\b(ndiyo|ndio)\b')


def _yn_leading(text):
    w = text.strip().lower().split()
    return w[0].strip('.,—-:()"') if w else ''


def _yn_polarity(text):
    substantive = text.split('\n\n')[0]           # ignore trailing ramble entirely
    lead = _yn_leading(substantive); low = substantive.lower()
    if lead in ('hapana', 'la', 'siyo', 'sivyo', 'no'):   # 'la' = No ONLY as a leading word
        return 'no'
    if lead in ('ndiyo', 'ndio', 'yes'):
        return 'yes'
    if re.search(r'\bhapana\b', low) or _YN_NEG.search(low):
        return 'no'
    if _YN_YES.search(low):
        return 'yes'
    return 'yes'                                   # affirmative default


def score_question(q, generated, refusal_phrases):
    gen_lower  = normalize(generated)
    atype      = q.get('answer_type', '')
    correct_sw = q.get('correct_answer_sw', '').lower()
    correct_en = q.get('correct_answer_en', '').lower()

    if atype == 'out_of_corpus_refusal':
        return any(p in gen_lower for p in [normalize(p) for p in refusal_phrases])

    if atype in ('number', 'penalty'):
        correct_nums = extract_numbers(correct_sw) | extract_numbers(correct_en)
        gen_nums = extract_numbers(generated)
        if correct_nums and len(correct_nums & gen_nums) >= 1:
            return True
        # Fallback for frequency answers like 'mara moja kwa mwaka'
        frequency_words = {'mara', 'kila', 'mwaka', 'wiki', 'mwezi', 'siku', 'once', 'annually'}
        if any(w in gen_lower for w in frequency_words) and any(w in correct_sw for w in frequency_words):
            if len(gen_lower) > 15:
                return True
        if not correct_nums:
            return len(gen_lower) > 10
        return False

    if atype == 'yes_no':
        # Compare the model's stated polarity to the expected polarity (see _yn_polarity
        # NOTE above). Correct answers reliably lead with Ndiyo/Hapana/La.
        return _yn_polarity(generated) == _yn_polarity(q.get('correct_answer_sw', ''))

    if atype in ('definition', 'procedure'):
        correct_sw = re.sub(r'thibitisha na.*$', '', correct_sw, flags=re.IGNORECASE|re.DOTALL).strip()
        correct_en = re.sub(r'confirm with.*$',  '', correct_en, flags=re.IGNORECASE|re.DOTALL).strip()
        # Lowered from 6→5 chars and 4→3 words to handle Swahili synonym variation
        words = {w for w in (correct_sw + ' ' + correct_en).split() if len(w) >= 5}
        if not words: return len(gen_lower) > 20
        return len(words & set(gen_lower.split())) >= 3

    # BUG 6 fix — an unrecognized answer_type previously fell through to a silent
    # 'pass if >20 chars'. That masks a data/config error (a typo'd or new answer_type
    # would be scored PASS without any real check). Fail loudly instead of silently pass.
    raise ValueError(f"score_question: unrecognized answer_type {atype!r} (id={q.get('id')})")


# ── SCORER RELIABILITY (BUGs 1/2/4/5 — flag, do NOT regex-patch) ───────────────
# The audit proved these categories cannot be scored robustly by regex without trading
# false-passes for false-fails. Rather than pretend otherwise, a question in one of
# these categories is marked scorer_unreliable and EXCLUDED from the scored denominator
# (reported separately as 'unscored, pending semantic judge'), never silently passed or
# failed. The check is deterministic from the question record + the model's output, so
# both the v15 and orchestrator runs exclude the same set. The real long-term fix is a
# semantic judge (LLM-as-judge / frontier-model scoring), not more regex here.

_ARITH_RE = re.compile(r'[−–—]\s*\d|\d\s*[−–—]|[x×*]\s*\d|=\s*\d|\d\s*\+\s*\d')


def _is_year(s):
    return bool(re.fullmatch(r'(19|20)\d\d', s))


def _polarity_conf(text):
    """Return (polarity, confident). Confident only when the stance is unambiguous:
    an explicit leading Ndiyo/Hapana/La, or a single-polarity marker sitting in the
    LEADING clause with no contradicting marker later. Not confident when there is no
    marker (pure affirmative default), when a marker appears only in a subordinate
    clause (the eval_182/eval_153 flip risk), or when both polarities appear."""
    substantive = text.split('\n\n')[0]
    low = substantive.lower()
    w = low.split()
    lead = w[0].strip('.,—-:()"') if w else ''
    if lead in ('hapana', 'la', 'siyo', 'sivyo', 'no'):
        return 'no', True
    if lead in ('ndiyo', 'ndio', 'yes'):
        return 'yes', True
    head = re.split(r'[.,—]', low, 1)[0]

    def pol(seg):
        neg = bool(re.search(r'\bhapana\b', seg) or _YN_NEG.search(seg))
        pos = bool(_YN_YES.search(seg) or re.search(r'\blazima\b', seg))
        if neg and pos:
            return 'both'
        if neg:
            return 'no'
        if pos:
            return 'yes'
        return None

    ph, pf = pol(head), pol(low)
    if ph in ('no', 'yes') and (pf is None or pf == ph):
        return ph, True                     # decisive marker in the leading clause
    if ph is None and pf in ('no', 'yes'):
        return pf, False                    # marker only in a later clause -> flip risk
    if ph == 'both' or pf == 'both' or (ph and pf and ph != pf):
        return (pf or 'yes'), False         # conflicting markers -> ambiguous
    return 'yes', False                     # nothing found -> affirmative default, not confident


def _defproc_words(correct_sw, correct_en, stem):
    csw = re.sub(r'thibitisha na.*$', '', correct_sw.lower(), flags=re.IGNORECASE | re.DOTALL).strip()
    cen = re.sub(r'confirm with.*$', '', correct_en.lower(), flags=re.IGNORECASE | re.DOTALL).strip()
    ws = {w for w in (csw + ' ' + cen).split() if len(w) >= 5}
    return {w[:5] for w in ws} if stem else ws


def _defproc_pass(correct_sw, correct_en, generated, stem):
    words = _defproc_words(correct_sw, correct_en, stem)
    if not words:
        return len(normalize(generated)) > 20
    g = set(normalize(generated).split())
    if stem:
        g = {w[:5] for w in g}
    return len(words & g) >= 3


def scorer_reliability(q, generated):
    """Return (reliable: bool, reason: str). reliable=False marks a question the regex
    scorer cannot verify robustly (BUGs 1/2/4/5) — exclude it from the scored total."""
    atype = q.get('answer_type', '')
    csw = q.get('correct_answer_sw', '') or ''
    cen = q.get('correct_answer_en', '') or ''

    if atype in ('number', 'penalty'):
        if _ARITH_RE.search(csw) or _ARITH_RE.search(cen):
            return False, 'compute_derived_number'      # answer is a computed delta; context figures leak in
        nums = extract_numbers(csw) | extract_numbers(cen)
        nonyear = {n for n in nums if not _is_year(n)}
        if not nums:
            return False, 'qualitative_number_no_numeric_key'   # BUG 1
        if not nonyear:
            return False, 'year_only_numeric_key'               # BUG 2
        # BUG 7 — zero / "does not apply" conclusion. When the reference answer's only
        # non-year figure is 0 (e.g. eval_247 "TZS 0. SDL inatozwa tu ... 10 au zaidi"),
        # the answer is a below-threshold / not-applicable conclusion, not a computed
        # amount. Number-overlap scoring cannot verify it either way: a wrong answer that
        # states any nonzero figure never shares the bare '0' (spurious FAIL), and a
        # rambling answer that happens to print '0' passes without establishing the
        # not-applicable reasoning (spurious PASS). Flag unreliable — the verdict is a
        # coin-flip on phrasing, not a real check. (Scope: numeric zero only. "No minimum
        # threshold" answers carrying illustrative nonzero figures, e.g. eval_051, are a
        # separate leniency pattern not addressed here.)
        if all(float(n) == 0 for n in nonyear):
            return False, 'zero_or_not_applicable_answer'       # BUG 7
        # BUG 2 residual: even when the reference answer carries other (non-year) figures,
        # a pass can still hinge ENTIRELY on a shared calendar year ('Finance Act 2025'
        # boilerplate) when the model reproduced only the year and none of the real figures
        # (e.g. eval_033). If the sole overlap with the output is a year, we cannot verify
        # substantive correctness either way -> unreliable.
        matched = nums & extract_numbers(generated)
        if matched and all(_is_year(n) for n in matched):
            return False, 'year_collision_match'
        return True, ''

    if atype == 'yes_no':                                        # BUG 4
        _, cconf = _polarity_conf(csw)
        _, gconf = _polarity_conf(generated)
        if not cconf:
            return False, 'yes_no_ground_truth_ambiguous'
        if not gconf:
            return False, 'yes_no_polarity_unverifiable'
        return True, ''

    if atype in ('definition', 'procedure'):                    # BUG 5
        if not _defproc_words(csw, cen, stem=False):
            return False, 'no_distinctive_vocabulary'
        if _defproc_pass(csw, cen, generated, stem=False) != _defproc_pass(csw, cen, generated, stem=True):
            return False, 'morphological_overlap_gap'
        return True, ''

    if atype == 'out_of_corpus_refusal':
        return True, ''
    return False, 'unknown_answer_type'


# ── HIGH-STAKES PROHIBITION SAFETY FLAG (reporting-only; never touches denominators) ──
# A hard-prohibition / absolute-obligation yes-no answer must NEVER be allowed to hide a
# polarity inversion inside the scorer_reliability 'unverifiable' bucket. In the 400-run,
# eval_317 (salon) and eval_332 (wholesale) were BOTH excluded as
# yes_no_polarity_unverifiable, so the reliable-subset headline was blind to two dangerous
# inversions (a non-citizen told a prohibited activity is permitted). These questions are
# tagged deterministically from the question record and ALWAYS polarity-reviewed against
# the reference answer, regardless of scorer_reliability. This is OBSERVABILITY ONLY: it
# adds a separate report section; it changes no pass verdict and no scored denominator.
#
# The trigger list is a small, auditable mirror of the absolutes locked in
# CLAUDE.md section 11 / locked_facts.json — not a heuristic. Keep it that way: add a
# subdomain/marker here only when the rule is a genuine hard prohibition or a
# no-exception obligation whose polarity is unambiguous ground truth.
_HIGH_STAKES_SUBDOMAINS = {
    'gn487a',             # GN487A: 15 activities absolutely prohibited for non-citizens
    'nssf_contributions', # mandatory from the first employee (no minimum headcount)
    'wcf_compliance',     # mandatory from the first employee (no minimum headcount)
    'osha_registration',  # registration required regardless of headcount
    'efd_compliance',     # EFD receipt on every transaction regardless of amount
}
# Minimum-wage floor (GN605A) may appear under a labour/sdl subdomain -> catch by marker.
_MINWAGE_MARKERS = ('mshahara wa chini', 'kima cha chini', 'gn 605', 'gn605')
# Substring identifying the orchestrator's in-scope refusal (chike.orchestrator.REFUSAL_TEXT).
# A refusal states no yes/no polarity, so it must not be scored as a candidate inversion.
REFUSAL_MARKER = 'nje ya maarifa yangu'
# Permission / obligation markers. For the OBLIGATION subdomains (nssf/wcf/osha/efd) a
# neutral factual yes-no (e.g. "is the NSSF rate 20%?") is NOT a prohibition question, so
# one of these must be present. GN487A is exempt from this gate: every non-citizen yes-no
# there is prohibition-relevant.
_PROHIBITION_MARKERS = (
    'mgeni', 'wageni', 'wasio raia', 'raia wa kigeni',   # non-citizen framing
    'ruhusiwa', 'naweza', 'kuruhusu', 'marufuku', 'katazo', 'kataz', 'zuili',
    'nalazimika', 'lazima', 'nawajibika', 'nahitaji', 'nasajili', 'kizingiti',
)


def high_stakes_prohibition(q):
    """Deterministic tag (reporting-only). Return (bool, reason).

    True when the question is a hard-prohibition / absolute-obligation yes-no whose
    polarity is unambiguous ground truth and must always be safety-reviewed, regardless
    of scorer_reliability. `reason` names the matched subdomain / rule for the report.
    """
    if q.get('answer_type', '') != 'yes_no':
        return False, ''
    sub = q.get('subdomain', '')
    low = (q.get('question_sw', '') or '').lower()
    if sub == 'gn487a':
        return True, 'gn487a'
    if sub in _HIGH_STAKES_SUBDOMAINS and any(m in low for m in _PROHIBITION_MARKERS):
        return True, sub
    if any(m in low for m in _MINWAGE_MARKERS):
        return True, 'min_wage_floor'
    return False, ''


def prohibition_polarity_review(q, generated):
    """Reporting-only safety review for one question. Return a dict when the question is
    high-stakes-prohibition, else None. `candidate_inversion` is True when the model's
    stated polarity disagrees with the reference answer's polarity — a possible dangerous
    flip — and is surfaced ALWAYS, independent of scorer_reliability. Uses the reference
    answer (well-formed, leads with Ndiyo/Hapana) as the polarity ground truth; the model
    polarity value is compared regardless of its own confidence, since a discursively
    worded inversion (no leading yes/no word) is exactly the case scorer_reliability
    excludes and this section exists to catch.
    """
    hs, reason = high_stakes_prohibition(q)
    if not hs:
        return None
    gen = generated or ''
    gold_pol, gold_conf = _polarity_conf(q.get('correct_answer_sw', '') or '')
    # A clarification sentinel / empty / refusal is a SAFE non-answer, not an inversion —
    # it states no polarity, so it must never be counted as a dangerous flip (eval_343 was
    # a false alarm from the sentinel's affirmative-default polarity).
    if ('<CLARIFICATION' in gen) or (not gen.strip()) or (REFUSAL_MARKER in gen.lower()):
        return {
            'id': q.get('id'), 'reason': reason,
            'gold_polarity': gold_pol, 'gold_confident': gold_conf,
            'model_polarity': 'none', 'model_confident': False,
            'candidate_inversion': False, 'status': 'clarified_or_refused',
        }
    model_pol, model_conf = _polarity_conf(gen)
    # candidate_inversion fires ONLY when both sides give a clear, opposite yes/no. A
    # 'both' (conflicting markers, e.g. "mandatory; there is no OPTIONAL version" —
    # eval_182) is ambiguous, not an inversion: surface it for review under its own
    # status rather than raising a false alarm on a correct answer.
    if model_pol == 'both':
        status = 'polarity_ambiguous'
        inversion = False
    else:
        inversion = gold_pol != model_pol
        status = 'candidate_inversion' if inversion else 'consistent'
    return {
        'id': q.get('id'), 'reason': reason,
        'gold_polarity': gold_pol, 'gold_confident': gold_conf,
        'model_polarity': model_pol, 'model_confident': model_conf,
        'candidate_inversion': inversion, 'status': status,
    }

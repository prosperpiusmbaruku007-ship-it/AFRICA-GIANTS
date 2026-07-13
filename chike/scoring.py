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
    for m in re.findall(r'\b(\d{3,}(?:,\d+)*)\b', text_lower):
        nums.add(m.replace(',', ''))
    for word, val in SWAHILI_NUMBERS.items():
        if re.search(r'\b' + word + r'\b', text_lower):
            nums.add(str(int(val)))
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

    return len(gen_lower) > 20

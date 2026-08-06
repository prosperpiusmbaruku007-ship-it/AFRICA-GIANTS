"""Production's query decomposition — the v15 shape, extracted verbatim.

THIS IS NOT chike/decomposition.py. Read this before touching either.

  chike/decomposition.py      = the v16 decomposer. Production's logic PLUS
                                _split_ordinal_enumeration (the eval_322 'mambo matatu:
                                kwanza… pili… tatu…' split, shipped 2026-07-24).
  chike/decomposition_v15.py  = THIS module. Exactly what production
                                (chike-inference/modal_app.py) and the live gate
                                (kaggle/eval.py) run today: '?'-splitting, Swahili
                                connectors, and the 'A, B, na C' enumeration. NO ordinal
                                split.

Why the duplication is deliberate rather than sloppy: the Phase D paired run compares v15
against v16, and the v15 arm must NOT inherit a v16 capability. If the v15 arm imported
chike/decomposition.py it would gain eval_322's 3-way split — flattering v15 with something
production does not have and quietly corrupting the very comparison the run exists to make.
The two modules encode two real, currently-deployed behaviours; they are not two copies of
one behaviour. tests/test_pipeline_v15.py asserts they differ on exactly eval_322 and agree
everywhere else across the 400.

LEAF MODULE CONTRACT: stdlib-only (re), no chike-internal imports, so kaggle/eval.py can
fetch and exec() it standalone the way it already does for prompting / generation_cleanup /
classification. Do not add a `from . import ...` here without updating eval.py's fetch list.

Only the two debug print loops from modal_app's copy are dropped (a library should not
print); the splitting logic is byte-for-byte the same.
"""

import re
from typing import List

# Swahili connectors that signal a second question inside one message.
MULTI_PART_SIGNALS = [
    r'\bna pia\b', r'\bpia\b', r'\bvilevile\b', r'\bzaidi ya hayo\b',
    r'\blakini pia\b', r'\bna aidha\b', r'\bpia ningependa\b',
    r'\bswali lingine\b', r'\bpia niambie\b', r'\bna je\b',
]

# Strong, unambiguous split points (never split on a bare "pia").
_SPLIT_PATTERN = r'(?:na pia|pia pia|vilevile|zaidi ya hayo|swali lingine)'

# Enumeration: a single clause listing several obligations to compute in one breath,
# e.g. "Nihesabie PAYE, SDL, na NSSF zote tatu". Such a message has no '?' and no
# multi-part connector, so the '?'/connector paths below never fire and a single
# whole-message top-3 retrieval covers only ONE domain (observed: PAYE dropped
# entirely, model looped on 'Thibitisha na TRA'). We detect the "A, B, na C" list
# and give each item its own context-carrying sub-query so each domain is retrieved.
_ENUMERATION_CLAUSE = re.compile(
    r'([^\s,.?!][\w/]*(?:\s*,\s*[\w/]+)+\s*,?\s*na\s+[\w/]+)', re.IGNORECASE)
# Require a calculate/list verb so ordinary prose ("inalipa BRELA, TRA na NSSF") is
# never over-split. \w* on both sides matches the Swahili object prefix so the verb
# in "Nihesabie" / "Nielezee" / "Niambie" is caught, not skipped by a word boundary.
_ENUMERATION_VERB = re.compile(r'\w*(?:hesab|elez|ambi|orodh|taj)\w*', re.IGNORECASE)


def _split_enumeration(message: str) -> list:
    """Sub-queries for an 'A, B, na C' compute list, else [] (not an enumeration).

    Each sub-query carries the context preceding the list (salary, employee count,
    verb) so it retrieves the calc example, not just the bare domain keyword.
    """
    if not _ENUMERATION_VERB.search(message):
        return []
    m = _ENUMERATION_CLAUSE.search(message)
    if not m:
        return []
    raw = re.split(r'\s*,\s*(?:na\s+)?|\s+na\s+', m.group(1), flags=re.IGNORECASE)
    items = [re.sub(r'^na\s+', '', it.strip(), flags=re.IGNORECASE)
             for it in raw if it.strip()]
    if len(items) < 2:
        return []
    preamble = message[:m.start()].strip()
    return [f'{preamble} {item}'.strip() for item in items]


def decompose_query(message: str) -> List[str]:
    """Split a multi-part message into sub-queries for separate RAG retrieval.

    Returns a list of sub-query strings — a single-item list for single-part
    messages. Conservative: if a split produces unusable fragments it falls back
    to the original message so single questions are never over-decomposed.
    """
    message_lower = message.lower()
    question_marks = message.count('?')
    has_connector = any(re.search(p, message_lower) for p in MULTI_PART_SIGNALS)
    enum_parts = _split_enumeration(message)

    if question_marks <= 1 and not has_connector and not enum_parts:
        return [message]  # single question — no decomposition needed

    parts = []

    # Prefer splitting on '?' boundaries when the message has several questions.
    # Fragment floor of 8 chars drops junk remnants ("Sawa?") while keeping real
    # short Swahili sub-queries ("EFD ninahitaji?" is 15 chars).
    if question_marks > 1:
        segments = [s.strip() for s in re.split(r'\?', message) if len(s.strip()) > 8]
        if len(segments) > 1:
            parts = [s + '?' for s in segments]

    # Otherwise split on strong Swahili connectors (case-insensitive on original).
    if not parts and has_connector:
        segments = re.split(_SPLIT_PATTERN, message, flags=re.IGNORECASE)
        parts = [s.strip() for s in segments if len(s.strip()) > 8]

    # Enumeration list ("Nihesabie A, B, na C") — use when the '?'/connector paths
    # above produced nothing usable (no '?', no connector).
    if (not parts or len(parts) == 1) and enum_parts:
        parts = enum_parts

    # Fallback: unusable fragments -> treat as single query.
    if not parts or len(parts) == 1:
        return [message]

    return parts

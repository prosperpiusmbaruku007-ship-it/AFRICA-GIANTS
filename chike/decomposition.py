"""Query decomposition — split a multi-part message into per-topic sub-queries.

Ported VERBATIM from production (chike-inference/modal_app.py:192-284), the logic
that produced the measured 87.9%->91.1% gate improvement. A single WhatsApp message
often covers two subdomains; whole-message top-3 RAG retrieval returns facts for one
subdomain only, so the model answers half the question. This splits multi-part
messages so each part gets its own retrieval.

Only the two debug print loops at the end of decompose_query are dropped (a library
should not print); the splitting logic is identical to modal_app.py and kaggle/eval.py.

DIVERGENCE-RISK FOLLOW-UP (same as chike/prompting.py and chike/generation_cleanup.py):
this exact block is duplicated identically in modal_app.py AND eval.py. Extracting all
three to import this module is the right end state but a cross-deployment change (modal
bakes chike-inference/; eval fetches from GitHub) — tracked as a follow-up.
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


# Announce-then-ordinal enumeration: "...mambo matatu: kwanza A, pili B, tatu C" — a single
# message that announces N things then lists them with ORDINAL delimiters (firstly/secondly/
# thirdly). It has one '?' and no multi-part connector, so the '?'/connector/enum paths never
# fire and whole-message top-3 retrieval covers only one part (eval_322: the SDL fragment
# mis-routes to compute and the VAT/EFD parts are dropped). Detected ONLY when BOTH signals are
# present — the announce phrase AND >=2 sequential ordinals — so a bare "kwanza" meaning "the
# first [group]" (eval_290's tiered payroll: "watu 3 wa kwanza... wanne wanaofuata...") is
# never split. The adverbial "pia" (also/too) has no announce phrase and is likewise untouched.
_ORDINAL_ANNOUNCE = re.compile(
    r'\b(mambo|maswali|masuala|vitu|mengi)\s+'
    r'(mawili|matatu|manne|matano|sita|saba|kadhaa)\b', re.IGNORECASE)
# Ordinal words in canonical sequence. Used as clause delimiters, matched as whole words so
# they are not found inside "matatu"/"wanne"/"watano".
_ORDINAL_SEQUENCE = ['kwanza', 'pili', 'tatu', 'nne', 'tano']


def _split_ordinal_enumeration(message: str) -> list:
    """Sub-queries for an announce-then-ordinal list ("mambo matatu: kwanza A, pili B, tatu C"),
    else [] (not this shape). Requires the announce phrase AND a sequential ordinal run starting
    at 'kwanza' then 'pili' (>=2), each appearing after the previous in text order. Splits on the
    ordinal delimiters; the announce preamble before the first ordinal is dropped (it carries no
    per-item context — each listed item is self-contained)."""
    if not _ORDINAL_ANNOUNCE.search(message):
        return []
    # First whole-word position of each ordinal.
    firsts = {}
    for ordw in _ORDINAL_SEQUENCE:
        mo = re.search(r'\b' + ordw + r'\b', message, flags=re.IGNORECASE)
        if mo:
            firsts[ordw] = mo.start()
    # Build the sequential run: kwanza, then pili, then tatu... each present and strictly after
    # the previous. Stop at the first missing/out-of-order ordinal (never a bare 'kwanza' alone).
    run = []
    prev = -1
    for ordw in _ORDINAL_SEQUENCE:
        pos = firsts.get(ordw, -1)
        if pos > prev:
            run.append((pos, ordw))
            prev = pos
        else:
            break
    if len(run) < 2:
        return []
    items = []
    for i, (pos, ordw) in enumerate(run):
        start = pos + len(ordw)
        end = run[i + 1][0] if i + 1 < len(run) else len(message)
        item = message[start:end].strip(' ,:;.-')
        if item:
            items.append(item)
    return items if len(items) >= 2 else []


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
    ordinal_parts = _split_ordinal_enumeration(message)

    if question_marks <= 1 and not has_connector and not enum_parts and not ordinal_parts:
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

    # Announce-then-ordinal list ("...mambo matatu: kwanza A, pili B, tatu C") — used when the
    # '?'/connector/enum paths above produced nothing usable. Tightly scoped (announce phrase +
    # >=2 sequential ordinals); see _split_ordinal_enumeration.
    if (not parts or len(parts) == 1) and ordinal_parts:
        parts = ordinal_parts

    # Fallback: unusable fragments -> treat as single query.
    if not parts or len(parts) == 1:
        return [message]

    return parts

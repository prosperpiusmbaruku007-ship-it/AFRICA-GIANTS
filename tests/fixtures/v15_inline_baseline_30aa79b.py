"""FROZEN BASELINE — the inline v15 logic as it existed at commit 30aa79b.

Captured from `git show 30aa79b:chike-inference/modal_app.py` and `:kaggle/eval.py`, i.e.
the last commit BEFORE chike/pipeline_v15.py + chike/decomposition_v15.py were extracted.
tests/test_pipeline_v15.py diffs the extracted modules against this, so "behaviour
preserving" is proved against the code production actually ran, not against a restatement
of it. DO NOT EDIT to make a test pass — a diff here means the extraction changed behaviour.
"""
import re


# ─── modal_app.py @ 30aa79b — inline decompose (production) ───────────────────────
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


def decompose_query(message: str) -> list:
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

    print(f'[decompose] split into {len(parts)} sub-queries:')
    for i, p in enumerate(parts):
        print(f'[decompose]   {i+1}. {p[:80]}')
    return parts


# ─── kaggle/eval.py @ 30aa79b — inline decompose (the live gate's copy) ───────────
def _eval_py_namespace():
    """eval.py's copy, exec'd in isolation (it shadows the same names as modal_app's)."""
    ns = {'re': re}
    exec(_EVAL_DECOMPOSE_SRC, ns)
    return ns


_EVAL_DECOMPOSE_SRC = '# Swahili connectors that signal a second question inside one message.\nMULTI_PART_SIGNALS = [\n    r\'\\bna pia\\b\', r\'\\bpia\\b\', r\'\\bvilevile\\b\', r\'\\bzaidi ya hayo\\b\',\n    r\'\\blakini pia\\b\', r\'\\bna aidha\\b\', r\'\\bpia ningependa\\b\',\n    r\'\\bswali lingine\\b\', r\'\\bpia niambie\\b\', r\'\\bna je\\b\',\n]\n\n# Strong, unambiguous split points (never split on a bare "pia").\n_SPLIT_PATTERN = r\'(?:na pia|pia pia|vilevile|zaidi ya hayo|swali lingine)\'\n\n# Enumeration: a single clause listing several obligations to compute in one breath,\n# e.g. "Nihesabie PAYE, SDL, na NSSF zote tatu". Such a message has no \'?\' and no\n# multi-part connector, so the \'?\'/connector paths below never fire and a single\n# whole-message top-3 retrieval covers only ONE domain (observed: PAYE dropped\n# entirely, model looped on \'Thibitisha na TRA\'). We detect the "A, B, na C" list\n# and give each item its own context-carrying sub-query so each domain is retrieved.\n_ENUMERATION_CLAUSE = re.compile(\n    r\'([^\\s,.?!][\\w/]*(?:\\s*,\\s*[\\w/]+)+\\s*,?\\s*na\\s+[\\w/]+)\', re.IGNORECASE)\n# Require a calculate/list verb so ordinary prose ("inalipa BRELA, TRA na NSSF") is\n# never over-split. \\w* on both sides matches the Swahili object prefix so the verb\n# in "Nihesabie" / "Nielezee" / "Niambie" is caught, not skipped by a word boundary.\n_ENUMERATION_VERB = re.compile(r\'\\w*(?:hesab|elez|ambi|orodh|taj)\\w*\', re.IGNORECASE)\n\n\ndef _split_enumeration(message: str) -> list:\n    """Sub-queries for an \'A, B, na C\' compute list, else [] (not an enumeration).\n\n    Each sub-query carries the context preceding the list (salary, employee count,\n    verb) so it retrieves the calc example, not just the bare domain keyword.\n    """\n    if not _ENUMERATION_VERB.search(message):\n        return []\n    m = _ENUMERATION_CLAUSE.search(message)\n    if not m:\n        return []\n    raw = re.split(r\'\\s*,\\s*(?:na\\s+)?|\\s+na\\s+\', m.group(1), flags=re.IGNORECASE)\n    items = [re.sub(r\'^na\\s+\', \'\', it.strip(), flags=re.IGNORECASE)\n             for it in raw if it.strip()]\n    if len(items) < 2:\n        return []\n    preamble = message[:m.start()].strip()\n    return [f\'{preamble} {item}\'.strip() for item in items]\n\n\ndef decompose_query(message: str) -> list:\n    """Split a multi-part message into sub-queries for separate RAG retrieval.\n\n    Returns a list of sub-query strings — a single-item list for single-part\n    messages. Conservative: if a split produces unusable fragments it falls back\n    to the original message so single questions are never over-decomposed.\n    """\n    message_lower = message.lower()\n    question_marks = message.count(\'?\')\n    has_connector = any(re.search(p, message_lower) for p in MULTI_PART_SIGNALS)\n    enum_parts = _split_enumeration(message)\n\n    if question_marks <= 1 and not has_connector and not enum_parts:\n        return [message]  # single question — no decomposition needed\n\n    parts = []\n\n    # Prefer splitting on \'?\' boundaries when the message has several questions.\n    # Fragment floor of 8 chars drops junk remnants ("Sawa?") while keeping real\n    # short Swahili sub-queries ("EFD ninahitaji?" is 15 chars).\n    if question_marks > 1:\n        segments = [s.strip() for s in re.split(r\'\\?\', message) if len(s.strip()) > 8]\n        if len(segments) > 1:\n            parts = [s + \'?\' for s in segments]\n\n    # Otherwise split on strong Swahili connectors (case-insensitive on original).\n    if not parts and has_connector:\n        segments = re.split(_SPLIT_PATTERN, message, flags=re.IGNORECASE)\n        parts = [s.strip() for s in segments if len(s.strip()) > 8]\n\n    # Enumeration list ("Nihesabie A, B, na C") — use when the \'?\'/connector paths\n    # above produced nothing usable (no \'?\', no connector).\n    if (not parts or len(parts) == 1) and enum_parts:\n        parts = enum_parts\n\n    # Fallback: unusable fragments -> treat as single query.\n    if not parts or len(parts) == 1:\n        return [message]\n\n    print(f\'[decompose] split into {len(parts)} sub-queries:\')\n    for i, p in enumerate(parts):\n        print(f\'[decompose]   {i+1}. {p[:80]}\')\n    return parts\n'


# ─── modal_app.py @ 30aa79b — inline messages build + post-generation sequence ────
def baseline_build_messages(message, relevant_facts, base_system_prompt,
                            build_enriched_system, ensure_terminal_punct):
    enriched_system = build_enriched_system(base_system_prompt, relevant_facts)
    user_msg = ensure_terminal_punct(message)
    return [
        {'role': 'system', 'content': enriched_system},
        {'role': 'user',   'content': user_msg},
    ]


def baseline_postprocess(reply, stop_strings, clean_reply):
    for stop in ['<|start_header_id|>', 'User:', 'Mtumiaji:'] + list(stop_strings):
        if stop in reply:
            reply = reply.split(stop)[0].strip()
    return clean_reply(reply, stop_strings)


def baseline_pool_facts(retrieve_facts, sub_queries):
    relevant_facts = []
    seen_facts = set()
    for sub_query in sub_queries:
        for fact in retrieve_facts(sub_query):
            if fact not in seen_facts:
                relevant_facts.append(fact)
                seen_facts.add(fact)
    return relevant_facts[:9]

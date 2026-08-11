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

NO DUAL-FILE SYNC IS NEEDED FOR CHANGES MADE HERE. Since the v16 cutover, production runs
this module through chike.orchestrator (modal_app.py imports Orchestrator; it carries no
decompose copy of its own), so this file has exactly one definition on the live path.
kaggle/eval.py fetches chike/decomposition_v15.py — the FROZEN v15 arm — which must not
gain v16 capabilities; tests/test_pipeline_v15.py enumerates the intended divergences.
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

# --- `na je`: the orphan connector -----------------------------------------------------------
#
# THE DEFECT THIS CLOSES. MULTI_PART_SIGNALS (which DECIDES a message is multi-part) has ten
# entries; _SPLIT_PATTERN (which actually SPLITS one) has five. Six connectors therefore detect
# and never split, and a message whose only connector is one of them is recognised as multi-part
# and then returned WHOLE by the `len(parts) == 1` fallback below. Silently: nothing in any
# artifact records that half a question went unanswered, and the regex scorer credits the half
# that was answered. Live-confirmed on three of them (th_19 SDL answered/EFD dropped, th_20 NSSF
# answered/VAT dropped, th_24 EFD answered/VAT dropped) — all three carrying `na je`.
#
# THE BOUND, worth knowing before anyone widens this further. Four other multi-domain corpus
# questions (eval_319/320/323/327) are NOT split and are answered in FULL anyway, because the
# rules engine enumerates the payroll levies (PAYE/SDL/NSSF/WCF) independently of decomposition.
# The drop happens only when the two asks live in DIFFERENT routes — one compute, one
# threshold/registration — where decomposition is the only mechanism that could have separated
# them. Decomposition is less load-bearing than it looks; this is the part of it that is.
#
# ONLY `na je` IS PROMOTED. The other five orphans appear in zero corpus questions, and bare
# `pia` is adverbial ("also/too", eval_180) — deliberately left detecting-but-not-splitting.
#
# THREE ADMISSION TESTS, one per authored false positive (eval/decomposition_gate/
# na_je_preamble_019.jsonl). The corpus cannot show any of them: all four of its `na je`
# questions want splitting.
#   \b boundaries   "na jengo" / "na jenereta" CONTAIN the literal "na je"; _SPLIT_PATTERN is
#                   applied with no boundaries, so a bare alternative would cut a single
#                   question mid-word.
#   fragment floor  applied as a VETO, not a filter: if any segment falls under the floor the
#                   message stays whole. The existing paths drop the short segment and split the
#                   rest, which loses a sub-question — the failure this change exists to fix.
#   ask marker      every segment must ask something. "Nimesajili biashara BRELA mwezi uliopita"
#                   is context, not a sub-question, and must not get its own retrieval and its
#                   own paragraph in the answer.
#   anaphora        a segment opening with a back-reference ("na je hiyo inategemea mauzo?")
#                   is not a standalone ask; split out it retrieves on nothing.
_NA_JE = r'\bna\s+je\b'
_FRAGMENT_FLOOR = 8
_ASK_MARKER = re.compile(
    r'\?|\bje\b|\bngapi\b|\bkiasi gani\b|\bnini\b|\blini\b|\bvipi\b|\bgani\b'
    r'|\bnahitaji\b|\bnasajili\b|\bnaweza\b|\bnilazimika\b|\bnatakiwa\b|\bnastahili\b',
    re.IGNORECASE)
_ANAPHORIC_OPENER = re.compile(r'^(hiyo|hilo|hicho|hii|huo|hizo|hao|hivyo|ndiyo)\b',
                               re.IGNORECASE)

# --- preamble carrying, MEASURE-MATCHED ------------------------------------------------------
#
# Splitting alone trades one silent failure for another: th_24 splits into "…mauzo TZS
# 50,000,000…" and "nahitaji EFD?" — self-contained by length, stripped of the turnover figure
# the EFD threshold is tested against. _split_enumeration already carries its preamble for this
# reason; the connector path never has.
#
# The carry is matched on the MEASURE, not on the presence of a figure, because "has a figure"
# admits two corruptions the corpus cannot show:
#   pre_02  "Mshahara … TZS 800,000 — PAYE ni kiasi gani, na je kima cha chini … ni kiasi gani?"
#           A salary is a figure too. Carrying it into a question that asks only what the
#           agricultural floor IS would hand the DETERMINISTIC minimum-wage route a wage to
#           adjudicate, manufacturing a halali / si halali verdict about a wage nobody asked
#           about.
#   pre_03  "Mauzo … TZS 50,000,000 — VAT ni asilimia ngapi, na je nahitaji kusajili NSSF?"
#           A real turnover figure, a real applicability ask with no figure of its own — every
#           precondition of a naive rule is met, and NSSF registration is triggered by employing
#           someone, not by turnover.
# So: the preamble must name turnover, must carry a figure, must name no domain of its own, and
# is carried only into a segment that has no figure AND belongs to a turnover-threshold domain.
# One measure is mapped today (turnover -> VAT/EFD). Adding a second is a data change that needs
# its own probes in both directions — see R17 and the probe file.
_PREAMBLE_DELIM = re.compile(r'\s*[—–:]\s+|\s+-\s+')
_TURNOVER_CUE = re.compile(r'\b(mauzo|mapato|mzunguko|turnover)\b', re.IGNORECASE)
_TURNOVER_THRESHOLD_DOMAIN = re.compile(r'\bVAT\b|\bEFD\b|risiti|kodi ya ongezeko',
                                        re.IGNORECASE)
_ANY_DOMAIN = re.compile(r'\b(VAT|EFD|PAYE|SDL|NSSF|WCF|OSHA|BRELA|TIN|GN)\b', re.IGNORECASE)
_HAS_FIGURE = re.compile(r'\d')


def _measure_preamble(message: str) -> str:
    """The message's leading context clause when it carries a TURNOVER figure, else ''.

    Requires a delimiter ("— ", "- ", ": ") so the preamble is a clause the writer marked off,
    not a guess at where the context ends; requires a figure and a turnover cue; and refuses
    any head that names a domain, which would import one obligation into another's sub-query.
    """
    m = _PREAMBLE_DELIM.search(message)
    if not m:
        return ''
    head = message[:m.start()].strip()
    if not head or not _HAS_FIGURE.search(head) or not _TURNOVER_CUE.search(head):
        return ''
    if _ANY_DOMAIN.search(head):
        return ''
    return head


def _split_na_je(message: str) -> list:
    """Sub-queries for a message joined by `na je`, else [] (not this shape, or vetoed).

    Returns segments in order, with the turnover preamble carried into any segment that lacks
    a figure and asks about a turnover-threshold obligation. See the block comment above for
    why each veto exists and which probe holds it.
    """
    if not re.search(_NA_JE, message, re.IGNORECASE):
        return []
    segments = [s.strip(' ,;:—–-')
                for s in re.split(_NA_JE, message, flags=re.IGNORECASE)]
    if len(segments) < 2:
        return []
    if any(len(s) <= _FRAGMENT_FLOOR for s in segments):
        return []                      # veto, never split-and-discard
    if not all(_ASK_MARKER.search(s) for s in segments):
        return []
    if any(_ANAPHORIC_OPENER.match(s) for s in segments[1:]):
        return []
    preamble = _measure_preamble(message)
    if not preamble:
        return segments
    return [f'{preamble} {s}'
            if not _HAS_FIGURE.search(s) and _TURNOVER_THRESHOLD_DOMAIN.search(s)
            else s
            for s in segments]

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

    # `na je` — the orphan connector, with its own admission tests and preamble carry.
    # Placed after the '?' and _SPLIT_PATTERN paths so neither shipped behaviour moves.
    if not parts or len(parts) == 1:
        na_je_parts = _split_na_je(message)
        if na_je_parts:
            parts = na_je_parts

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

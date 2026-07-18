"""Canonical post-generation stop/clean logic for Chike replies.

Two responsibilities, both ported from production (chike-inference/modal_app.py) and
kept identical to it and kaggle/eval.py:

1. Stop the reply from running into fabricated follow-up turns. StoppingCriteria is
   a GENERATION-time mechanism and cannot run post-hoc, so the portable equivalent is
   production's post-generation substring truncation (modal_app.py:524): cut the text
   at the first chat-turn boundary / stop string. This works on the orchestrator side
   because the raw endpoint now returns text WITH special tokens (skip_special_tokens
   =False), so the '<|eot_id|>' / '<|start_header_id|>' turn markers are present to
   split on — reliably, without truncating a legitimate multi-paragraph single turn.

2. clean_generated_reply — the exact post-generation corrections: strip leading
   fabricated '(N) …?' questions (loop), and the domain fixes RAG can't override
   (nssf.or.tz -> nssf.go.tz, .go.ke -> .go.tz).

DIVERGENCE-RISK FOLLOW-UP (same as chike/prompting.py): clean_generated_reply and
STOP_STRINGS live inline in BOTH modal_app.py and eval.py. This module is written to
become the single shared home; wiring those two to import it is a cross-deployment
change (modal bakes chike-inference/; eval fetches from GitHub) tracked as a follow-up.
Kept byte-for-byte identical to both for now.
"""

import json
import os
import re
from typing import Optional, Sequence

_CONFIG_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "kaggle", "chike_config.json")
)

# Default matches modal_app.py / eval.py's _GEN.get('stop_strings', [...]) fallback.
_DEFAULT_STOP_STRINGS = ["\n\nQ:", "\n\nSwali:", "<|start_header_id|>", "\n\n---"]

# Chat-turn boundaries. The first three are the special tokens that bound the
# assistant turn (present because generate_raw decodes skip_special_tokens=False);
# 'User:' / 'Mtumiaji:' match production's post-split list (modal_app.py:524).
_TURN_MARKERS = [
    "<|eot_id|>", "<|end_of_text|>", "<|start_header_id|>", "User:", "Mtumiaji:",
]

_SPECIAL_TOKEN_RE = re.compile(r"<\|[^|]*\|>")

# The fine-tuned model, driven by a manual Llama chat template, does NOT emit the
# real turn tokens — it appends fabricated follow-up turns as PLAIN TEXT separated by
# a blank line, each glued to the prior answer by a leaked role word ('user') or a
# fact-key-like run ('understand...'). So the reliable turn boundary is the first
# '\n\n', and the trailing glued junk is stripped after it. (Proper server-side fix:
# use the tokenizer's real chat template so generation stops at EOS — tracked separately.)
_TURN_SEPARATOR = "\n\n"
_ROLE_JUNK_RE = re.compile(r"(?i)(user|assistant|system|understand)[a-z0-9_]*\s*$")
# A '\n\n'-separated block is a fabricated follow-up turn (not part of the answer) if it
# starts with a leaked role header, repeats an earlier block (repeated disclaimer), or is a
# question immediately followed by its own answer. Blindly cutting at the first '\n\n' threw
# away legitimately-structured answers (intro line + steps/rates/definition); this keeps
# answer blocks and stops only at the first fabricated one.
_ROLE_START_RE = re.compile(r"(?i)^\s*(user|assistant|system|understand[a-z0-9_]*)\b")
# A block that ENDS with a question glued straight onto a leaked role/junk token
# ('...?user_0x01', '...?become', '...?understander', '...OSHA?nssm') — the model's
# fabricated-Q&A boundary. Two branches:
#   (1) a known role word after '? ' (optionally spaced) — the original leaks;
#   (2) GENERAL: any short token glued DIRECTLY to '?' with NO space ('?nssm'). A real
#       question ends with '?' then either end-of-block or a SPACE + capital next sentence;
#       '?'+lowercase-with-no-space is never natural Swahili/English — it is a leaked turn
#       token. Generalized (2) so a new glued-token variant needs no further hardcoding
#       (the eval_183 'nssm' leak was invisible to the whitelist-only rule).
_GLUED_TURN_RE = re.compile(
    r"(?i)\?\s*(?:user|assistant|system|become|understand)[a-z0-9_]*\s*$"
    r"|\?[a-z][a-z0-9_.:/-]{0,25}\s*$"
)


# --- degradation-tail cuts (2026-07-18) --------------------------------------
# All three target the SAME upstream defect — the model rarely emits EOS, so ~79% of
# generations overrun the answer into a degradation tail (repetition / fabricated turns /
# script leak) until max_new_tokens truncates mid-word. clean_reply already trims most;
# these close the enumerated gaps that left eval_317 (intra-block repetition) and eval_183
# (glued 'nssm' turn) — and the Arabic / domain-loop leaks — degraded. The proper fix is
# server-side EOS (PROGRESS.md, HIGH-PRIORITY follow-up); these are post-hoc, byte-exact on
# a clean reply (they fire only when the specific garbage signature is present).

# Any character in a foreign SCRIPT is never part of a legitimate Swahili/English Chike
# reply -- it is always leaked fabricated-turn content (observed: Arabic 'yes'/'no' glued
# after a fabricated '?'). Allowed = Latin+diacritics (U+0000-036F) and shared punctuation
# / symbols incl. Mathematical Operators (U+2000-22FF) -- the em/en dash AND the arithmetic
# MINUS SIGN U+2212 that PAYE/SDL sums use (dropping it truncated eval_191 mid-sum). Foreign
# scripts (Arabic 06xx, Hebrew 05xx, Greek/Cyrillic 037x-04xx, CJK 3000+) fall outside and
# are still cut at the first character.
_NONLATIN_RE = re.compile(r"[^\x00-ͯ -⋿\s]")

# A domain glued straight onto another domain ('tra.go.tz.understandthis.com', or the
# '...understandthis.com.understandthis.com...' decode loop) is never legitimate — a real
# citation is a SINGLE 'word.tld'. Group 1 is the first (legitimate) domain; group 2 is the
# glued junk domain(s). Cutting at group 2's start KEEPS the real citation and drops only the
# leaked/looped fragment(s). Separators between fragments are '.', ')', '/' (no whitespace),
# so the match never crosses into the next sentence.
_DOMAIN_LOOP_RE = re.compile(
    r"(?i)\b([a-z0-9_-]+\.(?:com|go\.tz|co\.tz|or\.tz|org|net))"
    r"((?:[.)/][a-z0-9_/-]*\.(?:com|go\.tz|co\.tz|or\.tz|org|net))+[a-z0-9_/-]*)"
)

# Sentence boundary that KEEPS the separator (capturing group) so a non-repeating reply
# re-joins byte-for-byte identical.
_SENT_SPLIT_RE = re.compile(r"((?<=[.)])\s+)")


def _cut_at_first(text: str, match) -> str:
    return text[: match.start()].rstrip() if match else text


def _cut_nonlatin_and_domain_loops(text: str) -> str:
    """Truncate at the first non-Latin-script char, and drop a glued/looped junk domain
    while KEEPING the first legitimate citation. Byte-identical when neither is present."""
    text = _cut_at_first(text, _NONLATIN_RE.search(text))
    m = _DOMAIN_LOOP_RE.search(text)
    if m:
        text = text[: m.start(2)].rstrip()   # keep group 1 (real domain), drop group 2 junk
    return text


def _truncate_repeated_sentences(text: str) -> str:
    """Cut at the first sentence that exactly repeats an earlier sentence in the reply
    (the eval_317 '…Thibitisha na Idara ya Uhamiaji (immigration.go.tz).' ×13 loop).

    Only sentences >=12 chars count, so a short legitimately-restated clause is never a
    trigger; the first occurrence is always kept. Re-joins via the captured separators, so
    a reply with no repeat is returned byte-for-byte unchanged."""
    parts = _SENT_SPLIT_RE.split(text)      # [sent, sep, sent, sep, ..., sent]
    kept, seen = [], set()
    i = 0
    while i < len(parts):
        sent = parts[i]
        key = sent.strip().lower()
        if len(key) >= 12 and key in seen:
            break                            # loop start — drop this sentence and the rest
        kept.append(sent)
        if i + 1 < len(parts):
            kept.append(parts[i + 1])        # its trailing separator (verbatim)
        if len(key) >= 12:
            seen.add(key)
        i += 2
    return "".join(kept).rstrip()


def _is_fabricated_block(block: str, seen: set) -> bool:
    b = block.strip()
    if not b:
        return True
    if _ROLE_START_RE.match(b):                 # leaked chat-turn header
        return True
    if b.lower()[:50] in seen:                  # repeated disclaimer / duplicate block
        return True
    m = re.search(r"\?\s*[A-Za-z]", b)          # a question followed by its own answer = fabricated Q&A turn
    if m and len(b) - m.end() > 15:
        return True
    # A question glued directly to a leaked role/junk token at the block's END — the boundary
    # where the model begins fabricating Q&A turns (e.g. '...withholding?user_0x01', '...hiari?become',
    # '...ni ngapi?understander'). The rule above misses these because the glued token is short
    # (<=15 chars). Anchored to end-of-block and restricted to known leak tokens, so a legitimate
    # rhetorical question in a real answer — and legit 'intro:\n\n(1)(2)(3)' structure — is never
    # caught (verified: strips eval_048/107 ramble, zero content loss across all 190 gate outputs).
    if _GLUED_TURN_RE.search(b):
        return True
    return False


def _load_stop_strings() -> list:
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as fh:
            cfg = json.load(fh)
        return cfg.get("generation_params", {}).get("stop_strings", _DEFAULT_STOP_STRINGS)
    except (FileNotFoundError, json.JSONDecodeError):
        return _DEFAULT_STOP_STRINGS


STOP_STRINGS = _load_stop_strings()


def clean_generated_reply(text: str) -> str:
    """Thin cleanup: strip leading (N)? enumerations + domain fixes only. Does NOT
    truncate fabricated follow-up turns.

    DEPRECATED as a public entry point — kept ONLY as the final building block inside
    clean_reply (step 5). All consumers (eval.py, modal_app.py, orchestrator) now call
    clean_reply, which strips ramble first. Do not wire this in directly: on its own it
    leaves fabricated Q&A ramble in the reply, which fed the scorer false-credit keywords
    (eval_029/132/163). Use clean_reply."""
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"^\(\d+\)\s*[^.!?]*\?\s*", "", text.strip())
    text = re.sub(r"nssf\.or\.tz", "nssf.go.tz", text, flags=re.IGNORECASE)
    text = re.sub(r"\.go\.ke\b", ".go.tz", text, flags=re.IGNORECASE)
    return text.strip()


def truncate_at_stops(text: str, stop_strings: Optional[Sequence[str]] = None) -> str:
    """Cut the reply at the first chat-turn boundary or stop string — the post-hoc
    equivalent of production's StoppingCriteria (modal_app.py:524 post-split)."""
    if stop_strings is None:
        stop_strings = STOP_STRINGS
    for stop in _TURN_MARKERS + list(stop_strings):
        if stop in text:
            text = text.split(stop)[0]
    return text.strip()


def clean_reply(text: str, stop_strings: Optional[Sequence[str]] = None) -> str:
    """Full stop/clean stage: cut the reply at the first fabricated follow-up turn,
    drop residual special tokens and glued role junk, then apply clean_generated_reply.

    Order: (1) truncate at any real turn/stop marker; (2) cut a leaked non-Latin-script
    tail / domain-fragment loop; (3) keep '\\n\\n'-separated blocks until the first
    fabricated follow-up turn (a legitimately-structured answer — intro line + steps/rates/
    definition — is kept whole; only the appended ramble is dropped); (4) cut an intra-block
    repeated-sentence loop; (5) strip a trailing leaked role word / fact-key run glued to
    the answer; (6) strip residual special tokens; (7) domain fixes.

    Steps (2) and (4) are byte-exact no-ops on a clean reply — they fire only when the
    specific degradation-tail signature (non-Latin char, domain loop, repeated sentence)
    is actually present.
    """
    text = truncate_at_stops(text, stop_strings)
    text = _cut_nonlatin_and_domain_loops(text)
    kept, seen = [], set()
    for block in text.split(_TURN_SEPARATOR):
        if _is_fabricated_block(block, seen):
            break
        kept.append(block)
        seen.add(block.strip().lower()[:50])
    text = _TURN_SEPARATOR.join(kept).strip()
    # Strip a trailing glued role token BEFORE the repetition cut, so a duplicate closing
    # line that differs only by a leaked suffix ('…(tra.go.tz).user' vs '…(tra.go.tz).')
    # still matches and de-duplicates (eval_111). Re-strip afterwards in case the cut
    # exposed another. Both are no-ops on a clean reply.
    text = _ROLE_JUNK_RE.sub("", text).strip()
    text = _truncate_repeated_sentences(text)
    text = _ROLE_JUNK_RE.sub("", text).strip()
    text = _SPECIAL_TOKEN_RE.sub("", text).strip()
    return clean_generated_reply(text)

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
# ('...?user_0x01', '...?become', '...?understander') — the model's fabricated-Q&A
# boundary. Anchored to end + limited to leak tokens so real questions are untouched.
_GLUED_TURN_RE = re.compile(r"(?i)\?\s*(?:user|assistant|system|become|understand)[a-z0-9_]*\s*$")


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

    Order: (1) truncate at any real turn/stop marker; (2) keep '\\n\\n'-separated blocks
    until the first fabricated follow-up turn (a legitimately-structured answer — intro
    line + steps/rates/definition — is kept whole; only the appended ramble is dropped);
    (3) strip a trailing leaked role word / fact-key run glued to the answer; (4) strip
    residual special tokens; (5) domain fixes.
    """
    text = truncate_at_stops(text, stop_strings)
    kept, seen = [], set()
    for block in text.split(_TURN_SEPARATOR):
        if _is_fabricated_block(block, seen):
            break
        kept.append(block)
        seen.add(block.strip().lower()[:50])
    text = _TURN_SEPARATOR.join(kept).strip()
    text = _ROLE_JUNK_RE.sub("", text).strip()
    text = _SPECIAL_TOKEN_RE.sub("", text).strip()
    return clean_generated_reply(text)

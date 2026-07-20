"""Canonical Chike OOC (out-of-corpus) classifier — the R11 inference-time gate.

Single source of truth for the classify logic shared by ALL THREE code paths that must
behave identically (R12): chike-inference/modal_app.py (the Modal edge), kaggle/eval.py
(the gate), and chike/orchestrator.py (the v16 pipeline). Each previously carried its own
inline copy of the phrase lists + classify function — three copies that happened to match
today but could silently diverge. They already diverged in ONE dimension: modal_app UNIONed
its hardcoded list with config ooc_phrases, while eval.py REPLACED hardcoded with config
(CONFIG.get('ooc_phrases', [fallback])). That was benign only because the config lists are
currently supersets of the hardcoded ones; add a phrase to a hardcoded list without adding it
to config and the gate would silently stop testing the production classifier. This module
makes that class of divergence structurally impossible: one classify(), one resolve_phrases(),
one set of canonical fallback lists, imported by all three.

DELIBERATE BOUNDARY (flagged): the config-FILE loader is NOT shared, and legitimately cannot
be. modal_app reads the baked /root/assets/chike_config.json; the orchestrator/local path
reads repo-relative kaggle/chike_config.json (as chike/prompting.py does); eval.py fetches
chike_config.json over HTTP from GitHub. Each environment locates the file its own way — that
step cannot be unified — but all feed the SAME resolve_phrases()/classify() here, so the
resolved phrase SET and the decision LOGIC are single-source. R14 governs the config file as
the single source for phrase additions.

LEAF MODULE CONTRACT: stdlib-only, no chike-internal imports, so kaggle/eval.py can fetch and
exec() it standalone (the same pattern it uses for chike/prompting.py and generation_cleanup.py).
Do not add a `from . import ...` here without also updating eval.py's fetch mechanism.
"""

import json
import os
from typing import Sequence, Tuple

# Canonical hardcoded fallback lists — moved verbatim out of chike-inference/modal_app.py so
# there is exactly one copy. In production these are UNIONed with chike_config.json's
# ooc_phrases / in_scope_phrases (R14 additions). The config lists are currently supersets, so
# the resolved set equals the config lists in production; these fallbacks apply when no config
# is available (e.g. modal_app's web container, which has no baked config file).
HARDCODED_OOC_PHRASES = [
    # Capital gains
    "capital gain", "faida ya mtaji", "kodi ya faida ya mtaji",
    "nilinunua ardhi", "nilinunua nyumba", "niliuza ardhi", "niliuza nyumba",
    # Import / customs duty
    "import duty", "customs duty", "ushuru wa forodha", "ushuru wa uagizaji",
    "kodi ya uagizaji", "kuagiza bidhaa", "duty ya kuagiza",
    # Transfer pricing
    "transfer pricing", "bei ya uhamisho", "arm's length",
    # Stamp duty and land valuation
    "stamp duty", "ushuru wa stempu", "tathmini ya ardhi", "land valuation",
    # Mining royalties
    "mining royalt", "mrabaha wa madini", "royalty ya madini", "ya royalty",
    # EPZ / special economic zones
    "export processing zone", "epz tax", "kodi ya epz", "(epz)",
    # Insurance premium levy
    "insurance premium levy", "ushuru wa bima",
    # Zanzibar tax system (not general Zanzibar mention)
    "zanzibar tax", "kodi ya zanzibar", "kodi za zanzibar", "vat zanzibar",
    # Crypto / investment
    "bitcoin", "cryptocurrency", "hisa za soko", "stock market",
]

HARDCODED_IN_SCOPE_PHRASES = [
    "brela", "vat", "ongezeko la thamani", "paye", "mapato ya ajira",
    "sdl", "ufundi stadi", "nssf", "hifadhi ya jamii", "osha", "usalama kazini",
    "efd", "mashine ya kodi", "wcf", "fidia ya wafanyakazi",
    "gn487a", "gn 487", "wageni", "wasio raia",
    "kampuni", "usajili", "leseni ya biashara", "tin", "taxpayer",
]

# The per-environment config-file loader for the LOCAL / orchestrator path (the boundary
# flagged in the module docstring). Mirrors chike/prompting.py's repo-relative path exactly.
_LOCAL_CONFIG_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "kaggle", "chike_config.json")
)


def load_local_config() -> dict:
    """Read repo-relative kaggle/chike_config.json — the LOCAL/orchestrator config loader.
    Returns {} on failure (-> hardcoded fallbacks). This is the deliberately-unshared,
    environment-specific step; modal_app and eval.py locate the same file their own way."""
    try:
        with open(_LOCAL_CONFIG_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def resolve_phrases(config) -> Tuple[list, list]:
    """Union the canonical hardcoded lists with config's ooc_phrases / in_scope_phrases (R14).

    Byte-for-byte the union logic from modal_app.py:154-157 (hardcoded first, then any config
    phrase not already present). config may be {} / None (no file available) -> the hardcoded
    fallbacks. Returns (ooc_phrases, in_scope_phrases)."""
    cfg = config or {}
    ooc = list(HARDCODED_OOC_PHRASES)
    ooc += [p for p in cfg.get("ooc_phrases", []) if p and p not in ooc]
    in_scope = list(HARDCODED_IN_SCOPE_PHRASES)
    in_scope += [p for p in cfg.get("in_scope_phrases", []) if p and p not in in_scope]
    return ooc, in_scope


def classify(message: str, ooc_phrases: Sequence[str],
             in_scope_phrases: Sequence[str]) -> bool:
    """Return True if in scope (pass to the model), False if explicitly OOC (intercept/refuse).

    Exact 3-step precedence, ported byte-for-byte from modal_app.py:173-182 and eval.py:
    explicit-OOC wins -> in-scope short-circuits -> else pass to the model. When a question
    matches BOTH an OOC phrase and an in-scope phrase, OOC wins because the OOC loop runs first
    and returns before the in-scope loop is reached."""
    msg = message.lower()
    for phrase in ooc_phrases:
        if phrase in msg:
            return False                 # OOC — intercept (checked FIRST: OOC always wins)
    # NOTE: the in-scope loop is currently a no-op in the original logic — both this branch and
    # the final `return True` return True, so IN_SCOPE_PHRASES has zero effect on the output.
    # Mirrored exactly for behavioral parity; do NOT 'simplify' this away without confirming
    # that is intentional (a future non-trivial in-scope decision is a separate, deliberate
    # change, not a cleanup).
    for phrase in in_scope_phrases:
        if phrase in msg:
            return True                  # clearly in-scope
    return True                          # ambiguous — let the model handle it

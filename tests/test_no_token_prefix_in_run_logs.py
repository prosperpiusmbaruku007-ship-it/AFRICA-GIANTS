"""No secret value in a log (founder, 2026-11-16): the Kaggle regen and the production gate print a token LENGTH and a hash FINGERPRINT, never a prefix.

Planted (R26): the checker must flag the old print form and pass the new one. Scoped to the two scripts the founder runs next; the same pattern still
exists in other kaggle/ scripts (listed in PROGRESS 4x) and is NOT silently included here -- widening it is a decision, not a side effect.
"""
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PREFIX = re.compile(r"hf_token\[\s*:\s*\d+\s*\]|HF_TOKEN\[\s*:\s*\d+\s*\]")


def _code_lines(path):
    return [l for l in open(os.path.join(REPO, path), encoding="utf-8").read().splitlines() if not l.lstrip().startswith("#")]


def test_plant_the_old_form_is_flagged_and_the_new_form_passes():
    assert _PREFIX.search("print(f'[auth] HF token from Kaggle secret ({hf_token[:8]}...)')")
    assert not _PREFIX.search("print('[auth] len=%d' % len(hf_token))")


def test_the_regen_and_the_gate_print_no_token_prefix():
    for rel in ("kaggle/regenerate_rag_e5.py", "kaggle/eval_gate_production_2026_10_09.py"):
        bad = [l for l in _code_lines(rel) if _PREFIX.search(l)]
        assert not bad, (rel, bad)
        assert any("fingerprint" in l for l in _code_lines(rel)), f"{rel} no longer prints the length+fingerprint form"

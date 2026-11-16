"""No secret value in a log (founder, 2026-11-16): the Kaggle regen and the production gate print a token LENGTH and a hash FINGERPRINT, never a prefix.

Planted (R26): the checker must flag the old print form and pass the new one. Covers the regen, the production gate and the 11 eval/probe scripts the founder approved on 2026-11-16 (print-only change).
`kaggle/train_ddp.py` is DELIBERATELY excluded -- the founder said to leave it untouched until the next retrain (it prints 8 characters); it is the one known
remaining instance, recorded in PROGRESS, and this list is the only place the exclusion lives.
"""
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PREFIX = re.compile(r"hf_token\[\s*:\s*\d+\s*\]|HF_TOKEN\[\s*:\s*\d+\s*\]")
COVERED = ("kaggle/regenerate_rag_e5.py", "kaggle/eval_gate_production_2026_10_09.py", "kaggle/eos_production_probe.py", "kaggle/eval.py", "kaggle/eval_orchestrator.py",
           "kaggle/eval_orchestrator_combined.py", "kaggle/eval_phase_d_paired.py", "kaggle/extraction_raw_debug.py", "kaggle/extraction_stress_test.py",
           "kaggle/faithfulness_probe.py", "kaggle/gn487a_inversion_probe.py", "kaggle/nli_regression.py", "scripts/build_eval_notebook.py")


def _code_lines(path):
    return [l for l in open(os.path.join(REPO, path), encoding="utf-8").read().splitlines() if not l.lstrip().startswith("#")]


def test_plant_the_old_form_is_flagged_and_the_new_form_passes():
    assert _PREFIX.search("print(f'[auth] HF token from Kaggle secret ({hf_token[:8]}...)')")
    assert not _PREFIX.search("print('[auth] len=%d' % len(hf_token))")


def test_the_regen_and_the_gate_print_no_token_prefix():
    for rel in COVERED:
        bad = [l for l in _code_lines(rel) if _PREFIX.search(l)]
        assert not bad, (rel, bad)
        assert any("fingerprint" in l or "_fp" in l for l in _code_lines(rel)), f"{rel} no longer prints the length+fingerprint form"


def test_train_ddp_exclusion_is_explicit_and_still_the_only_known_instance():
    import glob
    offenders = sorted(os.path.relpath(p, REPO).replace(os.sep, "/") for p in glob.glob(os.path.join(REPO, "kaggle", "*.py")) + glob.glob(os.path.join(REPO, "scripts", "*.py"))
                       if any(_PREFIX.search(l) for l in open(p, encoding="utf-8", errors="replace").read().splitlines() if not l.lstrip().startswith("#")))
    assert offenders == ["kaggle/train_ddp.py"], offenders

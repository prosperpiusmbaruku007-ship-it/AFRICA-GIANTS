# -*- coding: utf-8 -*-
"""THE THREE PREVIOUSLY-UNENFORCED CORPUS GATES, NOW WIRED (2026-10-08).

Measured 2026-10-08, and this file is the fix:

    validate_dataset.py   ENFORCED  — a test asserted the real corpus passes it, and
                                      pre-push runs pytest. Corpus clean: 1714 / 0.
    check_locked_facts.py NOT       — imported by two tests, NEITHER running it over the
                                      corpus. 48 flag lines live at HEAD.
    check_sources.py      NOT       — ZERO test references.
    check_eval_split.py   NOT       — ZERO test references.

`.githooks/` held ONLY pre-push. There was NO pre-commit hook. "Only commit if all 4 return
exit code 0" was an instruction to a reader, enforced by nothing — so the clean gate and the
dirty ones differed in WIRING, not diligence.

⛔ THIS FILE IS NOT "ASSERT THE CORPUS IS CLEAN". It is not, 18 pairs still flag, and
asserting zero would be a test that instructs maintainers to ignore real defects (R17's
corollary — the inverse of which already produced a test asserting a known OOC leak should
pass). It asserts SHRINK-ONLY per file against a committed baseline, so every one of those 18
is visible, counted, and impossible to add to.

AND IT ASSERTS THE WIRING ITSELF, which is the part R26 says is actually load-bearing:
`scan_for_keys.py` scanned correctly for the whole life of the project while being handed
zero files, and `chike/retrieval.py`'s index contract raised correctly while production never
imported it. Both were perfect and both protected nothing. So: does the hook exist, does it
call this runner, and does the runner BLOCK a planted regression?
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(REPO, "scripts", "check_corpus_gates.py")
BASELINE = os.path.join(REPO, "scripts", "corpus_gate_baseline.json")
HOOK = os.path.join(REPO, ".githooks", "pre-commit")


def _run(*args, cwd=REPO):
    return subprocess.run([sys.executable, RUNNER, *args], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


# ── THE GATES ACTUALLY RUN OVER THE CORPUS NOW ───────────────────────────────────
def test_the_whole_corpus_is_no_worse_than_its_baseline():
    """The assertion that was missing entirely. Slow-ish by necessity: it is the only thing
    that reads every corpus file through the locked-fact patterns. A compile cache took this
    from ~40s per file to seconds, which is what made wiring it affordable at all — expense
    is how a check ends up not being run."""
    r = _run("--quiet")
    assert r.returncode == 0, (
        f"the corpus got worse against scripts/corpus_gate_baseline.json:\n{r.stdout}\n"
        f"{r.stderr}")


def test_the_baseline_covers_every_corpus_file():
    """A file absent from the baseline is a file the ratchet cannot judge, and the runner
    treats that as a failure rather than a pass — but only if the baseline is actually
    complete, so that is asserted here rather than assumed."""
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import check_corpus_gates as cg
    with open(BASELINE, encoding="utf-8") as fh:
        base = json.load(fh)
    files = set(cg.corpus_files())
    assert files, "no corpus files found — the globs have broken, and an empty population " \
                  "reports clean"
    missing = sorted(files - set(base["locked_facts"]))
    assert not missing, f"corpus files with no locked_facts ceiling: {missing}"
    missing_s = sorted(files - set(base["sources"]))
    assert not missing_s, f"corpus files with no sources ceiling: {missing_s}"


def test_the_baseline_is_a_ratchet_not_a_target():
    """Every non-zero ceiling is a real defect awaiting adjudication, and the file must say
    so. A baseline that reads as a target is how 18 known defects become permanent."""
    with open(BASELINE, encoding="utf-8") as fh:
        base = json.load(fh)
    assert "SHRINK-ONLY" in base["_what"]
    assert "not targets" in base["_what"] or "not targets" in base["_what"].lower()
    assert base.get("_why_not_zero"), "the reason zero is not demanded must be stated"
    total = sum(base["locked_facts"].values())
    assert total <= 18, (
        f"the locked-fact backlog has grown to {total} (was 18 on 2026-10-08). The per-file "
        f"ratchet allows a file to stay the same; this total catches a NEW file arriving "
        f"already dirty, which the per-file check would wave through on its first run.")


def test_check_eval_split_is_now_exercised():
    """R6's invariant: eval pairs must not reach training. Zero test references before today.
    No ratchet — unlike the other two it has no legacy backlog, so a ceiling would invent
    slack that does not exist."""
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import check_corpus_gates as cg
    ok, tail = cg.eval_split_ok()
    assert ok, f"check_eval_split failed:\n{tail}"


# ── THE WIRING, WHICH IS THE PART THAT HAS FAILED BEFORE ─────────────────────────
def test_a_pre_commit_hook_exists_and_calls_the_runner():
    assert os.path.exists(HOOK), (
        "there is no pre-commit hook. This is the gap measured on 2026-10-08: `.githooks/` "
        "held only pre-push, so the corpus gates were enforced by nothing.")
    src = open(HOOK, encoding="utf-8").read()
    assert "check_corpus_gates.py" in src, (
        "the hook no longer calls the shared runner. If it has grown its own copy of the "
        "checks, that copy will drift from this suite and the drift will be invisible "
        "because both will be green.")
    assert "scan_for_keys.py" in src, (
        "scan_for_keys is not run at commit time. Invoked bare it reads `git diff --cached`, "
        "and at PUSH time nothing is staged — pre-commit is the point where it has files.")
    assert "--files" in src, "the hook checks the whole corpus instead of the staged set"


def test_the_hook_is_on_the_configured_hooks_path():
    """A hook in a directory git is not looking at is the purest form of an inert control."""
    p = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=REPO,
                       capture_output=True, text=True)
    configured = (p.stdout or "").strip()
    assert configured == ".githooks", (
        f"core.hooksPath is {configured!r}, so .githooks/pre-commit is not being run by git. "
        f"Set it with: git config core.hooksPath .githooks")


def test_the_runner_BLOCKS_a_planted_regression():
    """⛔ R26: watch it block the thing it exists to block. Plants a row asserting a locked
    fact's wrong value into a corpus file in a scratch copy of the repo, and requires a
    non-zero exit. Without this the ratchet could be satisfied by a runner that counts
    nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, "repo")
        os.makedirs(work)
        for sub in ("scripts", "datasets/tier1a/cleaned_pairs",
                    "datasets/tier1a/sft_shaped_pairs", "sources", "schema"):
            os.makedirs(os.path.join(work, *sub.split("/")), exist_ok=True)
        for f in ("check_corpus_gates.py", "check_locked_facts.py", "check_sources.py",
                  "check_eval_split.py", "locked_facts.json", "corpus_gate_baseline.json"):
            src = os.path.join(REPO, "scripts", f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(work, "scripts", f))
        target = "datasets/tier1a/cleaned_pairs/batch_008_cleaned.jsonl"
        shutil.copy2(os.path.join(REPO, *target.split("/")),
                     os.path.join(work, *target.split("/")))
        # Baseline for batch_008 is 0, so ONE planted violation must break it.
        base = json.load(open(os.path.join(work, "scripts", "corpus_gate_baseline.json"),
                              encoding="utf-8"))
        assert base["locked_facts"].get(target) == 0, (
            f"this specimen assumes a 0 ceiling for {target}; it is "
            f"{base['locked_facts'].get(target)} — re-point it at a clean file")
        planted = {
            "id": "planted_regression_specimen",
            "question_sw": "Bendi ya pili ya PAYE ni asilimia ngapi?",
            # A compact, unnegated assertion of band 2 at 9% when the locked rate is 8% --
            # the same specimen as lfp_01 in the polarity probe set.
            "answer_sw": "Bendi ya pili ya PAYE Tanzania ni asilimia 9 kwenye sehemu "
                         "inayozidi TZS 270,000.",
            "answer_en": "The second PAYE band in Tanzania is 9% on the excess over TZS "
                         "270,000.",
        }
        with open(os.path.join(work, *target.split("/")), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(planted, ensure_ascii=False) + "\n")

        r = subprocess.run(
            [sys.executable, os.path.join(work, "scripts", "check_corpus_gates.py"),
             "--files", target],
            cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert r.returncode == 1, (
            "a planted locked-fact violation did NOT block — the runner is INERT.\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}")
        assert "WORSE" in r.stdout or "rose to" in r.stdout, r.stdout


def test_the_runner_PASSES_the_same_file_unplanted():
    """The clean arm. Positive-only certifies a gate that blocks everything, and
    negative-only is what the secret scan had."""
    r = _run("--files", "datasets/tier1a/cleaned_pairs/batch_008_cleaned.jsonl")
    assert r.returncode == 0, r.stdout + r.stderr


def test_a_missing_baseline_is_cannot_evaluate_not_a_pass():
    """Exit 2, distinct from both 0 and 1, so an `&&` chain cannot read it as success — the
    same fix already applied to run_eval.py's empty-corpus path and validate_dataset's."""
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, "repo")
        os.makedirs(os.path.join(work, "scripts"))
        for f in ("check_corpus_gates.py", "check_locked_facts.py", "check_sources.py",
                  "check_eval_split.py", "locked_facts.json"):
            src = os.path.join(REPO, "scripts", f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(work, "scripts", f))
        r = subprocess.run(
            [sys.executable, os.path.join(work, "scripts", "check_corpus_gates.py")],
            cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert r.returncode == 2, (
            f"a missing baseline exited {r.returncode}; it must be 2 — cannot-evaluate is "
            f"not a pass.\n{r.stdout}")

# -*- coding: utf-8 -*-
"""THE DEPLOY PRE-FLIGHT, PLANTED IN BOTH DIRECTIONS (2026-10-08).

⛔ THE REORDERING IS THE FIX, NOT THE CHECKS. R16 step 1 is `modal app stop` then redeploy.
The stop is INSTANT AND IRREVERSIBLE; the deploy is neither. Twice the stop succeeded and the
replacing deploy failed for an unrelated reason:

  2026-08-10  the CLI aborted on its own `✓` glyph, unprintable on a cp1252 console. ~2 min down.
  2026-10-08  `.env()` chained AFTER `add_local_file`, which Modal forbids. ~3 min down.

Two unrelated causes, one window — so enumerating causes is the wrong defence. Build first,
then open the window. After this, the outage window can only be opened by a deploy that has
already built once.

⚠️ AND THE OBVIOUS PRE-FLIGHT DOES NOT WORK. "Import modal_app.py and construct the image"
does NOT catch the 2026-10-08 bug: measured on modal 1.5.1, chaining `.env()` after
`add_local_file()` CONSTRUCTS FINE and raises only at BUILD time. An import-based pre-flight
would have passed and the outage would have happened anyway. That is why there are two
separate gates — a static lint for the known class, and a REAL BUILD for the class nobody has
thought of, which is the category both outages came from.
"""
import io
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import preflight_deploy as pf  # noqa: E402

LIVE_APP = "chike-inference/modal_app.py"


# ── GATE 2: THE STATIC LINT, BOTH DIRECTIONS ─────────────────────────────────────
def test_the_lint_PASSES_the_real_current_app_file():
    """The clean arm. A lint that flags everything is as useless as one that flags nothing,
    and this file is the one that must keep deploying."""
    assert pf.gate_chain_lint(LIVE_APP) == [], (
        "the live app file now trips the chain lint — either it has regressed, or the lint "
        "has become over-broad. Both block deploys, so find out which.")


def test_the_lint_BLOCKS_the_exact_2026_10_08_bug(tmp_path):
    """⛔ THE PLANTED SPECIMEN: the outage reinstated, verbatim in shape — `.env()` moved back
    after the local-adds. If this stops firing, the lint is inert on the only bug it was
    written for, which is the state the first fee-band rule shipped in."""
    src = io.open(os.path.join(REPO, *LIVE_APP.split("/")), encoding="utf-8").read()
    bad = src.replace(
        "    .env({'CHIKE_BUILD': BUILD})\n"
        "    .add_local_file(os.path.join(_HERE, 'rag_embeddings.npy')",
        "    .add_local_file(os.path.join(_HERE, 'rag_embeddings.npy')")
    bad = bad.replace(
        "    .add_local_dir(os.path.join(_HERE, '..', 'chike'), '/root/chike')\n)",
        "    .add_local_dir(os.path.join(_HERE, '..', 'chike'), '/root/chike')\n"
        "    .env({'CHIKE_BUILD': BUILD})\n)")
    assert bad != src, (
        "the plant changed nothing — the anchors have moved and this specimen is no longer "
        "the 2026-10-08 bug. Re-derive it from modal_app.py rather than trusting this test.")
    p = tmp_path / "planted_modal_app.py"
    io.open(p, "w", encoding="utf-8", newline="\n").write(bad)
    rel = os.path.relpath(str(p), REPO)
    fails = pf.gate_chain_lint(rel)
    assert fails, "the planted outage did not fire — the lint is INERT"
    assert "add_local_dir" in fails[0] and "env" in fails[0]


def test_the_lint_ACCEPTS_copy_true(tmp_path):
    """`copy=True` is Modal's own escape hatch, so the lint must not forbid it — otherwise it
    blocks a legitimate pattern and gets disabled, which is how a gate stops being run."""
    p = tmp_path / "copyok.py"
    io.open(p, "w", encoding="utf-8", newline="\n").write(
        "import modal\n"
        "app = modal.App('x')\n"
        "image = (modal.Image.debian_slim()\n"
        "         .add_local_file('a.json', '/a.json', copy=True)\n"
        "         .env({'A': 'B'}))\n")
    assert pf.gate_chain_lint(os.path.relpath(str(p), REPO)) == []


def test_a_local_add_following_a_local_add_is_fine(tmp_path):
    """Several local-adds in a row is the normal pattern and must not be flagged."""
    p = tmp_path / "chain.py"
    io.open(p, "w", encoding="utf-8", newline="\n").write(
        "import modal\n"
        "app = modal.App('x')\n"
        "image = (modal.Image.debian_slim()\n"
        "         .env({'A': 'B'})\n"
        "         .add_local_file('a.json', '/a.json')\n"
        "         .add_local_dir('d', '/d'))\n")
    assert pf.gate_chain_lint(os.path.relpath(str(p), REPO)) == []


# ── GATE 1: PROVENANCE ───────────────────────────────────────────────────────────
def test_the_provenance_gate_exists_and_checks_both_things():
    """A dirty tree makes /health lie, and an unpushed HEAD makes its label unresolvable by
    anyone else. On 2026-10-08 the first happened: /health reported `build 5d1ed71` while the
    running image carried an uncommitted fix, so the label named a commit whose own
    modal_app.py cannot deploy at all."""
    import inspect
    src = inspect.getsource(pf.gate_provenance)
    assert "status" in src and "--porcelain" in src, "the dirty-tree check is gone"
    assert "is-ancestor" in src and "origin/main" in src, "the on-origin check is gone"


def test_the_provenance_gate_reports_a_dirty_tree_on_the_real_repo_when_dirty():
    """Run against the live repo: it must agree with `git status`, in whichever state the repo
    happens to be in. Asserting one direction only would pass on a repo that is always clean
    and never exercise the limb."""
    st = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                        capture_output=True, text=True)
    dirty = bool(st.stdout.strip())
    fails, head = pf.gate_provenance()
    assert head, "no HEAD resolved — cannot evaluate"
    says_dirty = any("DIRTY" in f for f in fails)
    assert says_dirty == dirty, (
        f"the gate says dirty={says_dirty} while git says dirty={dirty}")


# ── THE ORDER, WHICH IS THE ACTUAL FIX ───────────────────────────────────────────
def test_the_preflight_tells_the_operator_to_STOP_ONLY_AFTER_it_passes():
    """The reordering has to be readable in the output, not just intended. The success path
    must print the stop-then-deploy sequence; the failure path must say DO NOT STOP."""
    import inspect
    src = inspect.getsource(pf.main)
    assert "DO NOT STOP THE LIVE APP" in src, (
        "the failure path no longer tells the operator not to stop — which is the entire "
        "point of running this before the stop")
    assert "SAFE TO DEPLOY" in src
    ok_path = src.split("SAFE TO DEPLOY")[1]
    assert "app stop" in ok_path and "modal deploy" in ok_path, (
        "the success path does not print the ordered sequence")


def test_gate_3_builds_under_a_DIFFERENT_app_name():
    """⛔ THE ISOLATION PROPERTY. Gate 3 is the only gate that catches an unanticipated build
    failure, and it is only safe to run before the stop because it deploys under a throwaway
    name. If it ever deploys under the live name, the pre-flight becomes the thing it was
    protecting against."""
    import inspect
    src = inspect.getsource(pf.gate_real_build)
    assert '"--name"' in src or "'--name'" in src, "gate 3 no longer isolates by app name"
    assert "preflight" in src, "the throwaway name is gone"
    assert "app" in src and "stop" in src, (
        "gate 3 no longer stops the preflight app, so a failed run leaves one behind")


def test_cannot_evaluate_exits_2_not_0():
    """A missing app file must not read as a pass — the same rule applied to run_eval.py's
    empty corpus and validate_dataset's."""
    r = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "preflight_deploy.py"),
                        "chike-inference/does_not_exist.py", "--no-build"],
                       cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert r.returncode == 2, f"exited {r.returncode}, expected 2:\n{r.stdout}"

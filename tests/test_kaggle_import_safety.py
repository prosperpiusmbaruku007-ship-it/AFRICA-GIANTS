# -*- coding: utf-8 -*-
"""NO MODULE A KAGGLE SCRIPT IMPORTS MAY CONFIGURE GLOBAL I/O AT IMPORT TIME.

⛔ THIS TEST EXISTS BECAUSE THE SAME DEFECT LANDED TWICE, IN TWO FILES, FIFTEEN DAYS APART,
AND THE FIRST FIX COULD NOT HAVE PREVENTED THE SECOND.

  2026-09-24  scripts/check_correction_sync.py — module-level `sys.stdout.reconfigure()`
              killed a Kaggle RAG regen AFTER every blocking check passed and BEFORE anything
              was uploaded. The whole run.
  2026-10-09  eval/index_quality/sweep_superseded_values_in_built_index.py — the same line,
              in a module-level loader written the day before, killed the full production gate
              at SECOND 13.

The 2026-09-24 remedy was a guard plus "AST-sweep the other two modules the regen imports
in-process for module-level I/O configuration of any kind". That was a ONE-TIME act over a
TWO-MODULE population, so it could not protect a file that did not exist yet — the
remembered-rule failure (R30, R35). The population is therefore re-derived on every run here.

⛔⛔ WHY NO OTHER TEST IN THIS SUITE CAN COVER THIS CLASS — the thing to remember.
`sys.stdout.reconfigure` exists on a real `TextIOWrapper` and NOT on Jupyter's
`ipykernel.iostream.OutStream`. Under pytest, `sys.stdout` is a `TextIOWrapper` — or pytest's
own `CaptureIO`, which subclasses it — so it ALWAYS has `reconfigure`. Every local test of a
Kaggle-imported module therefore runs in an environment where this failure mode cannot occur.
The gate package's 23 offline tests included two that LOAD the offending module and run its
self-test, and they passed while the gate was unrunnable. **LOCAL GREEN SAYS NOTHING ABOUT
JUPYTER'S STREAM OBJECTS.** The only reachable check is STATIC: read the source, never run it.
That asymmetry is the reason this file is an AST test and not an import probe, and it is why
"the suite is green" must never be offered as evidence that a Kaggle script will start.
"""
import importlib.util
import io
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCANNER = os.path.join(REPO, "scripts", "check_kaggle_import_safety.py")


def _scanner():
    """Fresh module each time — the tests rebind REPO, so they must not share state."""
    spec = importlib.util.spec_from_file_location("kaggle_import_safety_under_test", SCANNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _w(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return rel.replace("\\", "/")


# ── THE LIVE REPO ───────────────────────────────────────────────────────────────────────
def test_the_real_repo_is_clean():
    mod = _scanner()
    findings, population, _edges = mod.scan()
    assert findings == [], (
        "a module the kaggle/ scripts import configures global I/O at import time. On Kaggle "
        "this raises before the caller's first line:\n" +
        "\n".join(f"  {f['module']}:{f['line']}  {f['rule']}  {f['detail']}" for f in findings))
    assert population, "empty population — see the non-vacuity test"


def test_the_population_contains_the_modules_it_MUST_contain():
    """⛔ A POPULATION IS CHECKED BY ITS POSITIVE LIMB, NOT BY ITS FINDINGS, AND THIS TEST IS
    HERE BECAUSE THE SCANNER ALREADY FAILED THAT WAY TWICE WHILE BEING WRITTEN.

    1. The first draft resolved dotted names against the repo root only. The regen reaches its
       checker as `sys.path.insert(0, 'scripts')` + `from check_correction_sync import ...`, a
       BARE name — so `scripts/check_correction_sync.py`, THE 2026-09-24 OFFENDER ITSELF, was
       not in the audited population at all, while the scan reported findings and looked like
       it worked.
    2. Adding a constant table so `_gates_path` would resolve then made `_CLONE` resolve too
       (it is also a module-level literal), turning the sweep's path into
       `/kaggle/working/AFRICA-GIANTS/eval/...`. The sweep FELL OUT of the population and the
       scan went from 2 findings to CLEAN while the closure grew 58 -> 60. A strictly more
       capable resolver that deleted the only finding it existed to report — R39's direction,
       where a falling count reads as progress.

    Both were invisible to the findings list. Only naming required members catches them.
    """
    mod = _scanner()
    _f, population, edges = mod.scan()
    must = {
        # the 2026-09-24 instance's file, reached by a bare name via sys.path.insert
        "scripts/check_correction_sync.py",
        "scripts/check_facts_index_sync.py",
        # the 2026-10-09 instance's file, reached by spec_from_file_location + os.path.join
        "eval/index_quality/sweep_superseded_values_in_built_index.py",
        # reached only through a path held in a variable
        "scripts/rag_payload_gates.py",
        # reached by a bare literal spec_from_file_location
        "scripts/precompute_rag_embeddings.py",
        # the answer-producing package, reached by ordinary imports
        "chike/fidelity.py", "chike/scoring.py", "chike/orchestrator.py", "chike/judge.py",
        "chike/clarification.py", "chike/retrieval.py",
    }
    missing = sorted(m for m in must if m not in population)
    assert not missing, (
        f"these modules ARE imported by kaggle/ scripts and are NOT in the audited "
        f"population, so the scan cannot see a defect in them: {missing}")
    assert len(population) >= 61, (
        f"the closure SHRANK to {len(population)} (was 61 at 2026-10-09). A population that "
        f"quietly gets smaller reports a cleaner result than it earned — bump this number "
        f"deliberately, with the reason, or find the resolver edge that broke")
    assert (edges["kaggle/eval_gate_production_2026_10_09.py"]
            and "eval/index_quality/sweep_superseded_values_in_built_index.py"
            in edges["kaggle/eval_gate_production_2026_10_09.py"]), (
        "the dynamic edge the 2026-10-09 crash arrived on is gone from the graph")


# ── THE PLANTS — BOTH HISTORICAL INSTANCES, AND BOTH RESOLVER EDGES (R26) ───────────────
_UNGUARDED = ("import sys\n"
              "sys.stdout.reconfigure(encoding='utf-8', errors='replace')\n"
              "def f():\n    return 1\n")

_GUARDED_TRY = ("import sys\n"
                "try:\n"
                "    sys.stdout.reconfigure(encoding='utf-8', errors='replace')\n"
                "except Exception:\n"
                "    pass\n"
                "def f():\n    return 1\n")

_GUARDED_IN_MAIN = ("import sys\n"
                    "def _safe():\n"
                    "    try:\n"
                    "        sys.stdout.reconfigure(encoding='utf-8')\n"
                    "    except Exception:\n"
                    "        pass\n"
                    "def main():\n"
                    "    _safe()\n"
                    "    sys.stdout.reconfigure(encoding='utf-8')\n")


@pytest.fixture
def fake_repo(tmp_path):
    """A miniature repo whose edges are the three the real one uses."""
    root = str(tmp_path)
    # EDGE 1 — ordinary import
    _w(root, "kaggle/seed_static.py", "from chike import helper_unguarded\n")
    _w(root, "chike/__init__.py", "")
    _w(root, "chike/helper_unguarded.py", _UNGUARDED)
    # EDGE 2 — spec_from_file_location + os.path.join(_CLONE, ...), the 2026-10-09 shape,
    # including the literal _CLONE that broke the resolver's second draft
    _w(root, "kaggle/seed_dynamic.py",
       "import importlib.util, os\n"
       "_CLONE = '/kaggle/working/AFRICA-GIANTS'\n"
       "_s = importlib.util.spec_from_file_location(\n"
       "    'dyn', os.path.join(_CLONE, 'eval', 'ix', 'dyn_unguarded.py'))\n")
    _w(root, "eval/ix/dyn_unguarded.py", _UNGUARDED)
    # EDGE 3 — sys.path.insert + bare name, the 2026-09-24 shape
    _w(root, "kaggle/seed_syspath.py",
       "import sys\n"
       "def go():\n"
       "    sys.path.insert(0, 'scripts')\n"
       "    from bare_unguarded import f\n"
       "    return f()\n")
    _w(root, "scripts/bare_unguarded.py", _UNGUARDED)
    # EDGE 4 — a declared dependency manifest, how the regen fetches its checkers
    _w(root, "kaggle/seed_manifest.py",
       "SOURCE_FILES = ['scripts/manifest_unguarded.py']\n")
    _w(root, "scripts/manifest_unguarded.py", _UNGUARDED)
    return root


def test_every_edge_FINDS_an_unguarded_reconfigure(fake_repo):
    """⛔ THE NEGATIVE LIMB, ONE PLANT PER RESOLVER EDGE. Three of these four edges each had a
    real bug in this scanner, so a single plant through one edge would have certified it."""
    mod = _scanner()
    mod.REPO = fake_repo
    findings, population, _ = mod.scan()
    flagged = {(f["module"], f["rule"]) for f in findings}
    for victim in ("chike/helper_unguarded.py", "eval/ix/dyn_unguarded.py",
                   "scripts/bare_unguarded.py", "scripts/manifest_unguarded.py"):
        assert victim in population, (
            f"{victim} is not reachable by the resolver, so the scan is blind to it — this is "
            f"the population defect, not a missing rule")
        assert (victim, "stdout_reconfigure") in flagged, (
            f"{victim} is in the population and its unguarded reconfigure was NOT flagged — "
            f"the rule is INERT, and an inert rule's clean sweep is byte-identical to a sound "
            f"one's")


def test_the_guarded_forms_are_NOT_flagged(fake_repo):
    """⛔ THE POSITIVE LIMB. A rule that flags both accepted fixes blocks every correct file,
    and the repo has ~70 scripts that legitimately reconfigure their own stdout. Both forms
    are the ones actually used in this repo: a module-level try/except
    (scripts/check_anchor_provenance.py) and a call inside main()
    (scripts/check_correction_sync.py, and now the sweep)."""
    mod = _scanner()
    mod.REPO = fake_repo
    _w(fake_repo, "chike/helper_try.py", _GUARDED_TRY)
    _w(fake_repo, "chike/helper_main.py", _GUARDED_IN_MAIN)
    _w(fake_repo, "kaggle/seed_clean.py",
       "from chike import helper_try\nfrom chike import helper_main\n")
    findings, population, _ = mod.scan()
    assert "chike/helper_try.py" in population and "chike/helper_main.py" in population
    for clean in ("chike/helper_try.py", "chike/helper_main.py"):
        assert not [f for f in findings if f["module"] == clean], (
            f"{clean} is a CORRECTLY guarded module and was flagged. This rule would send "
            f"someone to 'fix' a working file — the expensive direction, because only a false "
            f"positive generates an edit")


def test_a_seed_script_is_judged_for_reconfigure_but_not_for_chdir(tmp_path):
    """The asymmetry is deliberate and it is not a loophole.

    A kaggle/ seed runs as `__main__` INSIDE the notebook kernel, so it owns its cwd and may
    set it — but it does NOT own a stream object that implements `reconfigure`. The kernel's
    stdout is an OutStream either way, so an unguarded reconfigure crashes whether it is in a
    library or in the script itself. chdir is about whose state is being mutated; reconfigure
    is about whether the method exists at all.
    """
    root = str(tmp_path)
    _w(root, "kaggle/seed_chdir.py", "import os\nos.chdir('/tmp')\n")
    _w(root, "kaggle/seed_reconf.py",
       "import sys\nsys.stdout.reconfigure(encoding='utf-8')\n")
    mod = _scanner()
    mod.REPO = root
    findings, _pop, _ = mod.scan()
    rules = {(f["module"], f["rule"]) for f in findings}
    assert ("kaggle/seed_chdir.py", "chdir") not in rules, (
        "a top-level notebook script was flagged for setting its own cwd")
    assert ("kaggle/seed_reconf.py", "stdout_reconfigure") in rules, (
        "a seed script's own unguarded reconfigure was excused. It crashes on Kaggle exactly "
        "as a library's does — the kernel's stdout has no reconfigure regardless of who calls")


def test_a_module_level_chdir_in_a_LIBRARY_is_flagged(tmp_path):
    """The second rule, and the live instance it was found by: the sweep carried
    `os.chdir(REPO)` next to the reconfigure, so importing it relocated the notebook's cwd.
    It is now inside main() — moved, not removed, because it is load-bearing
    (precompute_rag_embeddings.FACTS_PATH is relative)."""
    root = str(tmp_path)
    _w(root, "kaggle/seed.py", "from chike import lib_chdir\n")
    _w(root, "chike/__init__.py", "")
    _w(root, "chike/lib_chdir.py", "import os\nos.chdir(os.path.dirname(__file__))\n")
    mod = _scanner()
    mod.REPO = root
    findings, _pop, _ = mod.scan()
    assert ("chike/lib_chdir.py", "chdir") in {(f["module"], f["rule"]) for f in findings}


def test_the_historical_2026_09_24_form_would_have_been_CAUGHT(tmp_path):
    """⛔ THE SPECIMEN THAT MATTERS MOST: the actual pre-fix shape of the file that cost a
    regen, reached by the actual edge it was reached by. Verbatim line, verbatim import form.

    Without this, the scanner's clean verdict on today's repo is only evidence that today's
    repo is clean — not that the instrument can see the defect that motivated it.
    """
    root = str(tmp_path)
    _w(root, "kaggle/regen_like.py",
       "import sys\n"
       "def run():\n"
       "    sys.path.insert(0, 'scripts')\n"
       "    from check_correction_sync import check_facts_and_index\n"
       "    return check_facts_and_index()\n")
    _w(root, "scripts/check_correction_sync.py",
       "import json, os, re, sys\n"
       "sys.stdout.reconfigure(encoding='utf-8', errors='replace')\n"
       "def check_facts_and_index():\n    return True\n")
    mod = _scanner()
    mod.REPO = root
    findings, population, _ = mod.scan()
    assert "scripts/check_correction_sync.py" in population
    assert [f for f in findings if f["module"] == "scripts/check_correction_sync.py"
            and f["rule"] == "stdout_reconfigure"]
    # and the fixed form of the same file must come back clean
    _w(root, "scripts/check_correction_sync.py",
       "import json, os, re, sys\n"
       "def _safe_stdout_utf8():\n"
       "    try:\n"
       "        sys.stdout.reconfigure(encoding='utf-8', errors='replace')\n"
       "    except Exception:\n"
       "        pass\n"
       "def check_facts_and_index():\n    return True\n")
    mod2 = _scanner()
    mod2.REPO = root
    findings2, _p2, _ = mod2.scan()
    assert not [f for f in findings2
                if f["module"] == "scripts/check_correction_sync.py"], (
        "the real 2026-09-24 FIX is reported as a defect — the rule cannot tell the repaired "
        "file from the broken one")


def test_the_scanner_REFUSES_to_report_clean_with_no_population(tmp_path):
    """R26: cannot evaluate is not passed. An empty seed directory must raise, not return
    CLEAN — a scan of nothing is the inert-control shape in its purest form."""
    mod = _scanner()
    mod.REPO = str(tmp_path)
    os.makedirs(os.path.join(str(tmp_path), "kaggle"), exist_ok=True)
    with pytest.raises(RuntimeError, match="no seeds"):
        mod.scan()


_RULE_SPECIMENS = {
    "stdout_reconfigure": "import sys\nsys.stdout.reconfigure(encoding='utf-8')\n",
    "chdir": "import os\nos.chdir('/tmp')\n",
    "setlocale": "import locale\nlocale.setlocale(locale.LC_ALL, 'C')\n",
    "logging_basicConfig": "import logging\nlogging.basicConfig(level=logging.INFO)\n",
    "filterwarnings": "import warnings\nwarnings.filterwarnings('ignore')\n",
    "environ_assign": "import os\nos.environ['HF_TOKEN'] = 'x'\n",
}


@pytest.mark.parametrize("rule", sorted(_RULE_SPECIMENS))
def test_every_rule_FIRES_on_its_own_specimen(rule, tmp_path):
    """⛔ EVERY RULE, NOT JUST THE TWO WITH LIVE INSTANCES.

    Four of these six currently match nothing in the repo — setlocale, basicConfig,
    filterwarnings, environ_assign — and that is precisely why they are planted. A rule with
    no current violation is indistinguishable, from the outside, from a rule that cannot
    match anything at all; the first is protection and the second is decoration, and the
    2026-10-09 fee-band guard shipped inert with "0 flags over 13,632 rows, verdict SAFE".
    """
    root = str(tmp_path)
    _w(root, "kaggle/seed.py", "from chike import victim\n")
    _w(root, "chike/__init__.py", "")
    _w(root, "chike/victim.py", _RULE_SPECIMENS[rule])
    mod = _scanner()
    mod.REPO = root
    findings, pop, _ = mod.scan()
    assert "chike/victim.py" in pop
    assert ("chike/victim.py", rule) in {(f["module"], f["rule"]) for f in findings}, (
        f"rule {rule!r} did not fire on its own specimen — it is INERT, and its silence on "
        f"the real repo means nothing")


@pytest.mark.parametrize("rule", sorted(_RULE_SPECIMENS))
def test_every_rule_is_SATISFIED_by_the_same_call_inside_a_function(rule, tmp_path):
    """The positive limb for all six: at CALL time the caller decides, so it is allowed.
    A rule that cannot tell import time from call time would flag main() and every helper."""
    root = str(tmp_path)
    body = "\n".join("    " + ln for ln in _RULE_SPECIMENS[rule].splitlines()[1:] if ln)
    src = _RULE_SPECIMENS[rule].splitlines()[0] + "\n\n\ndef main():\n" + body + "\n"
    _w(root, "kaggle/seed.py", "from chike import ok\n")
    _w(root, "chike/__init__.py", "")
    _w(root, "chike/ok.py", src)
    mod = _scanner()
    mod.REPO = root
    findings, pop, _ = mod.scan()
    assert "chike/ok.py" in pop
    assert not [f for f in findings if f["module"] == "chike/ok.py"], (
        f"rule {rule!r} flagged the call inside main(), which is the accepted fix — it would "
        f"block every correctly written script in the repo")


class _OutStreamLike:
    """The one part of `ipykernel.iostream.OutStream` that matters here: NO `reconfigure`.

    Not a mock of the whole class — a minimal stand-in with the single property that caused
    both outages. `__getattr__` raising AttributeError for anything undefined is the point.
    """

    encoding = "utf-8"

    def __init__(self):
        self.buf = []

    def write(self, s):
        self.buf.append(s)
        return len(s)

    def flush(self):
        pass

    def isatty(self):
        return False


@pytest.mark.parametrize("rel", [
    "eval/index_quality/sweep_superseded_values_in_built_index.py",   # the 2026-10-09 file
    "scripts/check_correction_sync.py",                              # the 2026-09-24 file
])
def test_the_two_historical_modules_IMPORT_under_a_reconfigure_less_stdout(rel, monkeypatch):
    """⛔ THE DYNAMIC PROOF, AND IT IS NARROW ON PURPOSE.

    The static scan is the durable, general check; this is direct evidence that these two
    specific modules — the only two that have ever broken a Kaggle run this way — now import
    when `sys.stdout` has no `reconfigure`. It is the Kaggle condition, reproduced locally in
    the only way it can be: by substituting the stream, since pytest's own stdout always has
    the method.

    Scoped to two known-pure modules rather than the whole 61-module closure, because loading
    the closure would import torch and the e5 model — the segfault risk that put `integration`
    behind a marker in the first place. A probe that cannot run safely is not a probe.
    """
    fake = _OutStreamLike()
    monkeypatch.setattr(sys, "stdout", fake)
    assert not hasattr(sys.stdout, "reconfigure"), "the stand-in is wrong, not the module"
    spec = importlib.util.spec_from_file_location(
        f"under_outstream_{os.path.basename(rel)[:-3]}", os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # the line that raised AttributeError, twice
    assert mod is not None
    # and the guarded helper must still be CALLABLE without raising on this stream — a guard
    # that only works by never being called is not a guard
    for fn in ("_safe_stdout_utf8",):
        if hasattr(mod, fn):
            getattr(mod, fn)()


def test_pytest_itself_proves_why_this_must_be_static():
    """⛔ THE CLAIM IN THIS FILE'S HEADER, ASSERTED RATHER THAN STATED.

    If this ever fails, the premise has changed and the reasoning above needs re-reading: it
    would mean the local environment CAN reach the failure mode, and a dynamic probe would
    become possible. Until then, a green suite is not evidence about Kaggle.
    """
    assert hasattr(sys.stdout, "reconfigure"), (
        "sys.stdout has no reconfigure under pytest — that is the Kaggle condition, locally. "
        "Re-read this file's header: a dynamic import probe may now be feasible")

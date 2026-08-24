"""The pre-push gate exists and refuses a red build — pinned, because remembering did not work.

THREE TIMES a console operation has stood between a measurement and its verdict: a PowerShell
`Select-Object` killed a run before it wrote its artifact (twice, silently, exit 0); a cp1252
console encoding aborted a deploy and truncated a live canary; and on 2026-08-24 a
`pytest ... | tail -2` consumed pytest's exit status so an `&&` chain committed and PUSHED with a
failing test. The first two were written up as lessons. The third happened anyway.

**A rule you have to recall is not a fix.** These assertions fail if the mechanical fix is
removed or weakened.
"""
import os
import re
import subprocess

HOOK = os.path.join('.githooks', 'pre-push')


def test_the_pre_push_hook_is_versioned_in_the_repo():
    """In .githooks/, not .git/hooks/. A hook in .git/hooks protects exactly one machine and
    does not survive a clone; core.hooksPath is what makes the gate travel."""
    assert os.path.isfile(HOOK), (
        f'{HOOK} is missing — the push gate is gone. Restore it and run '
        f'python scripts/install_hooks.py')


def test_the_hook_runs_pytest_without_a_pipe_and_refuses_on_failure():
    """The specific defect was a PIPE eating the exit status, so the absence of one is the
    thing worth asserting, not merely that pytest is mentioned."""
    src = open(HOOK, encoding='utf-8').read()
    pytest_lines = [ln for ln in src.splitlines()
                    if 'pytest' in ln and not ln.strip().startswith('#')]
    assert pytest_lines, 'the hook no longer runs pytest'
    for ln in pytest_lines:
        assert '|' not in ln, (
            f'the hook pipes pytest, which is the exact defect it exists to prevent: {ln!r}')
    assert re.search(r'STATUS=\$\?', src), 'the hook does not capture pytest\'s exit status'
    assert re.search(r'if \[ \$STATUS -ne 0 \]', src), 'the hook does not branch on failure'
    assert re.search(r'exit 1', src), 'the hook never refuses'


def test_the_hook_also_gates_the_secret_scan():
    """scan_for_keys.py before every commit is a standing rule in CLAUDE.md; the gate is where
    it stops depending on anyone remembering."""
    src = open(HOOK, encoding='utf-8').read()
    assert 'scan_for_keys.py' in src
    assert re.search(r'if \[ \$SCAN -ne 0 \]', src)


def test_the_secret_scan_is_not_invoked_with_no_target():
    """⚠️ THE ORIGINAL VERSION OF THIS GATE COULD NOT FAIL — and the two assertions above both
    passed while it couldn't.

    The hook called `scan_for_keys.py` bare. Bare means `git diff --cached`, and AT PUSH TIME
    NOTHING IS STAGED: it printed 'No files to scan' and exited 0 on every push, whatever the
    push contained. 'The hook mentions the script' and 'the hook branches on its status' are
    statements about wiring, not about whether the check can fire — which is R20 exactly, found
    one day after this gate shipped, inside the gate built to enforce that family of discipline.

    So this asserts the invocation has a TARGET: a commit range (what is actually being pushed)
    or --all-tracked (the fallback when the remote has never seen the branch)."""
    src = open(HOOK, encoding='utf-8').read()
    invocations = [ln for ln in src.splitlines()
                   if 'scan_for_keys.py' in ln and not ln.strip().startswith('#')
                   and 'python' in ln]          # the call, not the echo that names it
    assert invocations, 'the hook no longer runs the secret scan'
    for ln in invocations:
        assert ('--range' in ln or '--all-tracked' in ln or ln.rstrip().endswith('\\')), (
            f'the secret scan is invoked with no target, so it scans nothing at push time: {ln!r}')
    assert '--range' in src and '--all-tracked' in src, (
        'the hook must scan the pushed range, and fall back to all tracked files when the '
        'remote has no baseline for the branch')


def test_the_secret_scan_actually_FAILS_on_a_key():
    """Watch the check fail before trusting it (R20). Everything else here inspects text; this
    runs the scanner against a crafted key and asserts a non-zero exit.

    The key below is fabricated — it matches the OpenRouter pattern and is not a credential."""
    import subprocess
    import sys
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        planted = os.path.join(d, 'leak.py')
        with open(planted, 'w', encoding='utf-8') as f:
            f.write('KEY = "sk-or-' + 'v1abcdefghijklmnopqrstuvwxyz0123456789' + '"\n')
        out = subprocess.run(
            [sys.executable, os.path.join('scripts', 'scan_for_keys.py'), '--files', planted],
            capture_output=True, text=True, timeout=60)
    assert out.returncode == 1, (
        f'scan_for_keys.py did NOT flag a planted key (exit {out.returncode}). '
        f'stdout: {out.stdout!r}')
    assert 'BLOCKED' in out.stdout


def test_the_secret_scan_passes_a_clean_file():
    """The negative case, per R17: a change that only proves the new behaviour can be silently
    over-broad. A scanner that flags everything is as useless as one that flags nothing."""
    import subprocess
    import sys
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        clean = os.path.join(d, 'ok.py')
        with open(clean, 'w', encoding='utf-8') as f:
            f.write('import os\nKEY = os.environ.get("OPENROUTER_API_KEY", "")\n')
        out = subprocess.run(
            [sys.executable, os.path.join('scripts', 'scan_for_keys.py'), '--files', clean],
            capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, f'clean file was flagged: {out.stdout!r}'


def test_the_bypass_exists_and_is_loud():
    """A gate with no escape hatch gets disabled wholesale the first time it is inconvenient.
    A LOUD one is the compromise — and it must not be the default."""
    src = open(HOOK, encoding='utf-8').read()
    assert 'CHIKE_SKIP_PREPUSH' in src
    assert re.search(r'CHIKE_SKIP_PREPUSH:-0', src), 'bypass must default to OFF'
    assert 'WITHOUT running the suite' in src, 'the bypass must warn in plain words'


def test_hooks_path_is_configured_in_this_working_copy():
    """Not a property of the code — a property of THIS clone. Skipped rather than failed when
    git is unavailable, but a wrong value is a real finding: the hook file can be present and
    completely inert."""
    try:
        out = subprocess.run(['git', 'config', '--get', 'core.hooksPath'],
                             capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        import pytest
        pytest.skip('git unavailable')
    configured = out.stdout.strip()
    assert configured == '.githooks', (
        f'core.hooksPath is {configured!r}, so {HOOK} is INERT in this clone. '
        f'Run python scripts/install_hooks.py')

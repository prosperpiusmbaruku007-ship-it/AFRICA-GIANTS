# -*- coding: utf-8 -*-
"""Bridge outbound pacing (item G). The node tests in chike-whatsapp/bridge/pacer.test.mjs are run here, and each limb is PLANTED (R26): a
broken copy of pacer.mjs must make the node tests FAIL, so a green run cannot be a suite that cannot fail. Plus the wiring check (R26, "what does
production call"): server.mjs must acquire a slot BEFORE it calls sock.sendMessage, and a refusal must be a 429 that sends nothing.
"""
import os
import re
import shutil
import subprocess
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BRIDGE = os.path.join(_ROOT, "chike-whatsapp", "bridge")
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not installed")


def _node_tests(pacer_path=None):
    env = dict(os.environ)
    if pacer_path:
        env["PACER_PATH"] = pacer_path
    return subprocess.run([NODE, "--test", "pacer.test.mjs"], cwd=_BRIDGE, env=env, capture_output=True, text=True, timeout=120)


def test_node_pacer_tests_pass():
    r = _node_tests()
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-500:]


_SRC = open(os.path.join(_BRIDGE, "pacer.mjs"), encoding="utf-8").read()
_MUTANTS = {
    "no_spacing":   ("nextFree = start + minGapMs + Math.floor(rand() * (jitterMs + 1));", "nextFree = start;"),
    "no_jitter":    ("nextFree = start + minGapMs + Math.floor(rand() * (jitterMs + 1));", "nextFree = start + minGapMs;"),
    "unbounded":    ("if (wait > maxWaitMs)", "if (false)"),
    "gap_floor_off": ("minGapMs: gap >= FLOOR_GAP_MS ? gap : DEFAULTS.minGapMs,", "minGapMs: gap,"),
}


@pytest.mark.parametrize("name", sorted(_MUTANTS))
def test_plant_each_limb_is_caught(name, tmp_path):
    old, new = _MUTANTS[name]
    assert _SRC.count(old) == 1, f"mutation target for {name} not found: the plant would be inert (R20)"
    p = tmp_path / "pacer_mutant.mjs"
    p.write_text(_SRC.replace(old, new), encoding="utf-8")
    r = _node_tests(str(p))
    assert r.returncode != 0, f"the node tests did NOT notice the '{name}' defect: that limb is not actually tested"


def _code_lines(path):
    return [ln for ln in open(path, encoding="utf-8").read().splitlines() if not ln.strip().startswith("//")]


def test_server_acquires_a_slot_before_sending():
    code = "\n".join(_code_lines(os.path.join(_BRIDGE, "server.mjs")))
    body = code[code.index("async function send("):]
    body = body[:body.index("function ledgerSummary")]
    assert "pacer.acquire()" in body and "sock.sendMessage(" in body
    assert body.index("pacer.acquire()") < body.index("sock.sendMessage("), "a send reaches WhatsApp before it is paced"
    assert "code: 429" in body and "pacing_backlog" in body
    assert re.search(r"import \{[^}]*createPacer[^}]*\} from \"\./pacer\.mjs\"", code)


def test_a_pacing_refusal_is_retryable_not_a_phantom_pending():
    ok, detail = core.bridge_send_result(429, {"ok": False, "error": "pacing_backlog", "retry_after_s": 3})
    assert ok is False and not core.is_pending_receipt(detail)        # nothing was sent, so the retry layer may retry
    ok2, detail2 = core.bridge_send_result(200, {"ok": False, "pending": True, "id": "x", "status": "sent"})
    assert core.is_pending_receipt(detail2)                          # positive control: a REAL pending is still never retried

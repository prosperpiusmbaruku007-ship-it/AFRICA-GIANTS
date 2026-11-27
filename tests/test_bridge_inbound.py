# -*- coding: utf-8 -*-
"""Bridge inbound extraction and the no-receipt-wait hint (founder amendment, 2026-11-28: reply-to-approve + parallel card pushes).

The node tests in chike-whatsapp/bridge/inbound.test.mjs run here, and each limb is PLANTED (R26): a deliberately broken copy of inbound.mjs must make them FAIL, so a green run cannot be a suite that cannot
fail. Plus the wiring (what does the DEPLOYED server actually call), the cross-language field-name contract with handler_core.parse_webhook, and the image check: the new module must ship in the bridge image,
because a missing module makes server.mjs crash at import and takes the WhatsApp front door down."""
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BRIDGE = os.path.join(_ROOT, "chike-whatsapp", "bridge")
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not installed")

_SRC = open(os.path.join(_BRIDGE, "inbound.mjs"), encoding="utf-8").read()
_SERVER = open(os.path.join(_BRIDGE, "server.mjs"), encoding="utf-8").read()


def _node_tests(inbound_path=None):
    env = dict(os.environ)
    if inbound_path:
        env["INBOUND_PATH"] = inbound_path
    return subprocess.run([NODE, "--test", "inbound.test.mjs"], cwd=_BRIDGE, env=env, capture_output=True, text=True, timeout=120)


def test_node_inbound_tests_pass():
    r = _node_tests()
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-500:]


_MUTANTS = {
    "drops_the_quoted_id": ('quotedId: typeof q === "string" ? q : ""', 'quotedId: ""'),
    "coerces_a_non_string_id": ('quotedId: typeof q === "string" ? q : ""', 'quotedId: q ? String(q) : ""'),
    "text_rule_changed_extended_first": ('m.conversation || m.extendedTextMessage?.text || ""', 'm.extendedTextMessage?.text || m.conversation || ""'),
    "no_wait_on_anything_falsy": ("payload.wait_receipt === false", "!payload.wait_receipt"),
    "never_waits": ("return !(payload && payload.wait_receipt === false);", "return false;"),
    "always_waits": ("return !(payload && payload.wait_receipt === false);", "return true;"),
}


@pytest.mark.parametrize("name", sorted(_MUTANTS))
def test_PLANT_each_limb_can_fail(name, tmp_path):
    a, b = _MUTANTS[name]
    assert _SRC.count(a) == 1, f"the plant for {name} no longer matches the source: update it, do not delete it"
    broken = tmp_path / "inbound_broken.mjs"
    broken.write_text(_SRC.replace(a, b), encoding="utf-8")
    r = _node_tests(str(broken))
    assert r.returncode != 0, f"the node tests PASSED against a broken copy ({name}): they cannot fail on this limb"


# ── wiring: what the deployed server calls ────────────────────────────────────────────────────────────────
def test_the_server_uses_the_module_for_inbound_and_forwards_the_quoted_id():
    assert 'from "./inbound.mjs"' in _SERVER
    assert "extractInbound(m.message)" in _SERVER, "inbound text must come from the tested function, not an inline copy"
    assert "m.message.conversation ||" not in _SERVER, "the old inline text rule must be gone (two copies would drift)"
    assert re.search(r"\.\.\.\(quotedId \? \{ quotedId \} : \{\}\)", _SERVER), "the quoted id is forwarded, and only when present"


def test_the_field_name_matches_what_the_webhook_parser_reads():
    assert "quotedId" in open(os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"), encoding="utf-8").read()
    body = {"event": "messages.received", "data": {"messages": {"key": {"remoteJid": "255700000011@s.whatsapp.net", "fromMe": False}, "conversation": "TUMA", "quotedId": "3EB0ABC"}}}
    assert core.parse_webhook(body)["quoted_id"] == "3EB0ABC"


def test_a_send_that_does_not_wait_returns_after_the_ledger_row_exists_and_before_the_polling_loop():
    i = _SERVER.index("async function send(")
    seg = _SERVER[i:_SERVER.index("function ledgerSummary")]
    assert "wait_receipt" in seg.split(")")[0], "send() accepts the hint"
    pace, sendmsg, ledger, hint, loop = (seg.index(x) for x in ("pacer.acquire()", "sock.sendMessage", "LEDGER.set(id, row)", "wantsReceiptWait", "while (Date.now() - t0 < RECEIPT_WAIT_MS"))
    assert pace < sendmsg < ledger < hint < loop, "paced, sent, TRACKED in the ledger, and only then may it skip the wait: a no-wait send must still be receipt-tracked"
    assert "pending: true" in seg[hint:loop], "and it is reported as accepted-but-pending, so the caller never treats it as delivered and never resends"


def test_the_new_module_ships_in_the_bridge_image():
    assert os.path.exists(os.path.join(_BRIDGE, "inbound.mjs"))
    mb = open(os.path.join(_BRIDGE, "modal_bridge.py"), encoding="utf-8").read()
    assert 'add_local_dir(_HERE, "/app"' in mb and "inbound" not in mb.split("ignore=")[1].split(")")[0], "the whole bridge directory is baked, and inbound.mjs is not ignored: server.mjs imports it at start-up"


def test_server_mjs_still_parses():
    r = subprocess.run([NODE, "--check", "server.mjs"], cwd=_BRIDGE, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-600:]

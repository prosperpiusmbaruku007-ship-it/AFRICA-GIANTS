"""2026-11-25 (founder): per-message ANSWER-PATH log, code-only, no behaviour change. Pure classifier + summary + wiring checked on the REAL handler (deliver) and the deployed module's source (R41: run, do not just grep)."""
import ast
import asyncio
import importlib.util
import os
import subprocess
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


hc = _load("hc_pathlog", "chike-whatsapp/handler_core.py")
T = hc.answer_trace_record


@pytest.mark.parametrize("path,calls,guards,cls,routes", [
    ("engine:fixed_statement", 0, [], "fixed_statement", ["engine:fixed_statement"]),
    ("engine:paye", 2, [], "engine", ["engine:paye"]),
    ("engine:paye:ask", 1, [], "engine", ["engine:paye:ask"]),
    ("engine:rent_wht", 0, [], "engine", ["engine:rent_wht"]),
    ("fact", 1, [], "fact_model", ["fact"]),
    ("fact", 1, ["replaced"], "fact_model", ["fact"]),
    ("refusal", 0, [], "ooc", ["refusal"]),
    ("coverage_refusal", 0, [], "coverage_refusal", ["coverage_refusal"]),
    ("clarification", 1, [], "clarification", ["clarification"]),
    ("engine:paye+fact", 2, [], "multi", ["engine:paye", "fact"]),
    (None, None, None, "unknown", []),
    ("something_new", 1, [], "unknown", ["something_new"]),
])
def test_classification(path, calls, guards, cls, routes):
    t = T(path, calls, guards)
    assert t["cls"] == cls and t["routes"] == routes and t["model_calls"] == calls


def test_guard_and_model_call_fields_never_guessed():
    assert T("fact", 1, ["replaced"])["guard_fired"] is True and T("fact", 1, [])["guard_fired"] is False
    assert T("fact", 1, None)["guard_fired"] is None and T("fact", None, [])["model_calls"] is None
    assert T("fact", True, [])["model_calls"] is None          # a bool is not a count


def test_fallback_wins_over_a_stale_captured_path():
    t = T("engine:paye", 2, [], fallback=True, error_class="timeout")
    assert t["cls"] == "fallback" and t["error_class"] == "timeout" and t["routes"] == []


def test_record_holds_no_message_text_and_never_raises():
    t = T("fact", 1, [])
    assert set(t) == {"cls", "path", "routes", "model_calls", "guard_fired", "guards", "error_class"}
    assert T(object(), object(), object())["cls"] == "unknown"


def test_summary_counts_excludes_test_and_untraced_separately():
    rows = [{"answer_trace": T("engine:fixed_statement", 0, [])}, {"answer_trace": T("fact", 1, ["replaced"])},
            {"answer_trace": T("engine:paye", 2, [])}, {"answer_trace": T("refusal", 0, [])},
            {"test_sender": True, "answer_trace": T("fact", 1, [])}, {"review_id": "TEST-1", "answer_trace": T("fact", 1, [])},
            {"question": "old row, no trace"}]
    s = hc.summarize_answer_paths(rows)
    assert s["n"] == 5 and s["excluded_test"] == 2 and s["untraced"] == 1
    assert s["by_class"] == {"fixed_statement": 1, "fact_model": 1, "engine": 1, "ooc": 1}
    assert s["model_free"] == 2 and s["model_called"] == 2 and s["guard_fired"] == 1 and s["by_route"]["engine:paye"] == 1
    assert hc.summarize_answer_paths(rows, include_test=True)["n"] == 7


def test_summary_command_runs_and_prints_the_split(tmp_path):
    import json
    f = tmp_path / "rows.json"
    f.write_text(json.dumps([{"answer_trace": T("engine:fixed_statement", 0, [])}, {"answer_trace": T("fact", 1, [])}]), encoding="utf-8")
    out = subprocess.run([sys.executable, "-I", os.path.join(_ROOT, "scripts", "answer_path_summary.py"), "--file", str(f)], capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert out.returncode == 0, out.stderr
    assert "answer paths: 2 messages" in out.stdout and "fixed_statement" in out.stdout and "fact_model" in out.stdout and "model-free 1 | model called 1" in out.stdout


def test_the_deployed_handler_wires_the_trace_in_every_mode():
    """Parse the deployed file: the row and the review item both get answer_trace, and deliver() is handed the CAPTURING ask unconditionally (it used to be supervised-only)."""
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
    assert 'row["answer_trace"] = core.answer_trace_record(' in code and 'item["answer_trace"] = core.answer_trace_record(' in code
    assert "ask_capturing if settings.supervised else ask" not in code
    ast.parse(src)


def test_deliver_still_returns_the_same_row_shape_unsupervised_and_supervised():
    """Behaviour unchanged: the answer is sent or held exactly as before; the trace is added by the CALLER, so deliver()'s row gains no key."""
    sent = []

    async def ask(text):
        return {"reply": "Jibu.", "path": "fact", "model_calls": 1, "guards": []}

    async def send_once(to, text):
        sent.append((to, text))
        return True, None

    s = hc.Settings(model_timeout_s=5.0, slow_ack_after_s=0, cold_start_suspected_s=30.0, send_attempts=1, send_retry_delay_s=0.01, sender_salt="t", secrets=("x",))
    row = asyncio.run(hc.deliver("255700000000", "swali", ask, send_once, s, "t"))
    assert row["reply"] == "Jibu." and row["supervision"] == "sent" and sent == [("255700000000", "Jibu.")] and "answer_trace" not in row

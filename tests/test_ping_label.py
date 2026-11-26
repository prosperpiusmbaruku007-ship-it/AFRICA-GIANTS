# -*- coding: utf-8 -*-
"""The label healthchecks.io shows beside a ping (the User-Agent). The archiver's pings were arriving on ITS OWN check labelled "chike-bridge-watch", because the
shared `_ping_healthcheck` hard-coded that string (seen live 2026-11-26 on the archive check). Fixed: a `user_agent` parameter, defaulting to the old label so
every other caller is unchanged, and the archiver passes "chike-archive".

Plants: the pre-fix call shape (no label from the archiver) fails the structural check; the real run_archive is driven end to end and its actual ping request is read."""
import ast
import os
import sys
import urllib.request

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
from test_evidence_guard import _load_mw as _load_mw_real  # noqa: E402
from test_archive_core import item, Spy  # noqa: E402

SRC = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
URL = "https://hc-ping.example/SECRET-ARCHIVE-UUID"


class _Resp:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _capture(monkeypatch):
    seen = []

    def fake(req, timeout=None):
        seen.append({"url": req.full_url, "ua": req.get_header("User-agent"), "body": (req.data or b"").decode("utf-8")})
        return _Resp()
    monkeypatch.setattr(urllib.request, "urlopen", fake)
    return seen


def _archiver_ping_calls(source):
    """Every call to _ping_healthcheck inside run_archive, as {keyword: constant value or None}."""
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_archive")
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "_ping_healthcheck":
            out.append({k.arg: (k.value.value if isinstance(k.value, ast.Constant) else None) for k in n.keywords})
    return out


def test_every_archiver_ping_passes_its_own_label_and_its_own_check():
    calls = _archiver_ping_calls(SRC)
    assert len(calls) == 2, "the success ping and the failure ping"
    for kw in calls:
        assert kw.get("user_agent") == "chike-archive" and kw.get("url_env") == "HEALTHCHECK_ARCHIVE_URL", kw


def test_PLANT_the_pre_fix_call_shape_is_caught_by_the_same_check():
    pre_fix = SRC.replace(', user_agent="chike-archive"', "")
    assert pre_fix != SRC and all(kw.get("user_agent") is None for kw in _archiver_ping_calls(pre_fix)), "without the keyword the label silently falls back to the watcher's"


def test_the_default_label_is_unchanged_for_every_other_caller(monkeypatch):
    monkeypatch.setenv("HEALTHCHECK_PING_URL", URL)
    monkeypatch.setenv("HEALTHCHECK_CANARY_URL", URL)
    mw = _load_mw_real(monkeypatch)
    seen = _capture(monkeypatch)
    assert mw._ping_healthcheck("ok", "watch") == (True, None) and mw._ping_healthcheck("ok", "canary", url_env="HEALTHCHECK_CANARY_URL") == (True, None)
    assert [c["ua"] for c in seen] == ["chike-bridge-watch", "chike-bridge-watch"], "the watcher, the canary and the alerts keep the original label"


def test_a_custom_label_is_sent_as_given(monkeypatch):
    monkeypatch.setenv("HEALTHCHECK_ARCHIVE_URL", URL)
    mw = _load_mw_real(monkeypatch)
    seen = _capture(monkeypatch)
    mw._ping_healthcheck("ok", "x", url_env="HEALTHCHECK_ARCHIVE_URL", user_agent="chike-archive")
    assert seen[0]["ua"] == "chike-archive" and seen[0]["url"] == URL


def test_the_REAL_run_archive_sends_its_label_on_the_wire_for_success_and_for_failure(monkeypatch, tmp_path):
    monkeypatch.setenv("HEALTHCHECK_ARCHIVE_URL", URL)
    mw = _load_mw_real(monkeypatch)
    store = Spy(tmp_path / "vol")
    monkeypatch.setattr(mw, "_archive_store", lambda: store)
    seen = _capture(monkeypatch)
    mw.run_archive.get_raw_f()()
    assert [(c["ua"], c["url"]) for c in seen] == [("chike-archive", URL)] and seen[0]["body"].startswith("archive ok")
    store.fail_commit = True
    mw.REVIEW_QUEUE["r1"] = item(1, "sent", days_ago=9)
    # rebase the item onto the real clock so it is archivable today
    import datetime as dt
    it = mw.REVIEW_QUEUE["r1"]
    shift = dt.datetime.now(dt.timezone.utc) - dt.datetime(2026, 11, 26, 12, 0, tzinfo=dt.timezone.utc)
    for k in ("decided_ts", "ts_held"):
        it[k] = (dt.datetime.fromisoformat(it[k]) + shift).isoformat(timespec="seconds")
    with pytest.raises(OSError):
        mw.run_archive.get_raw_f()()
    assert seen[-1]["ua"] == "chike-archive" and seen[-1]["url"] == URL + "/fail" and seen[-1]["body"].startswith("archive FAILED")

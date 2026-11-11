"""R26 for the offline-suite guard (tests/conftest.py): plant each violation, watch it BLOCK; give
it a clean case, watch it PASS. Positive-only certifies a guard that blocks everything.

Nothing here leaves the machine: 203.0.113.1 is TEST-NET-3 and the guard refuses before connect().
"""
import os
import shutil
import socket
import subprocess
import sys
import textwrap

import pytest

_HERE = os.path.dirname(__file__)


_NODE = []


@pytest.fixture(autouse=True)
def _remember_node(request, _offline_guard):
    _NODE[:] = [request.node]
    yield


def _forgive():
    """These tests PROVOKE violations on purpose; the makereport hook would otherwise (correctly)
    fail them for it. Clear the record INSIDE the test body -- a teardown is too late, the report
    is already built. The decisive end-to-end proof is the subprocess tests below, where nothing
    is forgiven."""
    getattr(_NODE[0], "_offline_guard_violations", []).clear()


def _guard_raises(fn):
    # BaseException on purpose: the guard's exception is a BaseException so that retry loops
    # written as `except Exception` (Modal's client retried a refused DNS lookup 17 times, ~2 min)
    # cannot absorb it. The swallow case that REMAINS (`except BaseException`) is covered by the
    # recorded-violation path, tested below.
    with pytest.raises(BaseException) as ei:
        fn()
    assert "OFFLINE SUITE VIOLATION" in str(ei.value)
    _forgive()


def test_outbound_connect_is_blocked():
    s = socket.socket()
    try:
        _guard_raises(lambda: s.connect(("203.0.113.1", 443)))
    finally:
        s.close()


def test_connect_ex_create_connection_and_dns_are_blocked():
    s = socket.socket()
    try:
        _guard_raises(lambda: s.connect_ex(("203.0.113.1", 443)))
    finally:
        s.close()
    _guard_raises(lambda: socket.create_connection(("203.0.113.1", 443), timeout=1))
    _guard_raises(lambda: socket.getaddrinfo("api.modal.com", 443))


def test_loopback_still_works_the_negative_case():
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    c = socket.create_connection(srv.getsockname(), timeout=2)
    c.close()
    srv.close()
    socket.getaddrinfo("localhost", 80)


def test_a_modal_dict_read_is_blocked_not_just_a_raw_socket():
    """The founding route: modal.Dict -> gRPC -> getaddrinfo. NB `.keys()` is a LAZY GENERATOR --
    a plant that does not consume it never touches the network and 'passes', which is exactly how
    my first version of this test certified nothing. Consume it, as health() does."""
    modal = pytest.importorskip("modal")
    _guard_raises(lambda: list(
        modal.Dict.from_name("chike-transcripts-kv", create_if_missing=True).keys()))


def _run_pytester(tmp_path, body: str, extra=()):
    shutil.copy(os.path.join(_HERE, "conftest.py"), tmp_path / "conftest.py")
    (tmp_path / "test_planted.py").write_text(textwrap.dedent(body), encoding="utf-8")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, "-m", "pytest", str(tmp_path), "-q", "-p", "no:cacheprovider",
         "--rootdir", str(tmp_path), "-c", os.devnull, *extra],
        capture_output=True, text=True, env=env, timeout=180)


def test_a_swallowed_violation_still_fails_the_test(tmp_path):
    """health() wraps I/O in `except Exception`. A guard that only raised would let that test
    pass having tried to connect -- the exact shape of the founding defect."""
    r = _run_pytester(tmp_path, """
        import socket
        def test_swallows():
            try:
                socket.create_connection(("203.0.113.1", 443), timeout=1)
            except Exception:
                pass
        """)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "OFFLINE SUITE VIOLATION" in r.stdout and "1 failed" in r.stdout


def test_a_modal_dict_read_fails_a_planted_test_even_when_wrapped(tmp_path):
    pytest.importorskip("modal")
    r = _run_pytester(tmp_path, """
        def test_modal_dict():
            import modal
            try:
                d = modal.Dict.from_name("chike-transcripts-kv", create_if_missing=True).keys()
                list(d)
            except Exception:
                pass
        """)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "OFFLINE SUITE VIOLATION" in r.stdout


def test_network_marked_tests_are_exempt_the_negative_case(tmp_path):
    r = _run_pytester(tmp_path, """
        import socket, pytest
        @pytest.mark.network
        def test_live():
            # exempt: this must NOT be recorded as a violation (loopback refused is fine)
            try:
                socket.create_connection(("127.0.0.1", 1), timeout=1)
            except OSError:
                pass
        """, extra=("-m", "network"))
    assert r.returncode == 0, r.stdout + r.stderr


def test_a_clean_offline_test_passes(tmp_path):
    r = _run_pytester(tmp_path, "def test_ok():\n    assert 1 + 1 == 2\n")
    assert r.returncode == 0, r.stdout + r.stderr


def test_isolate_modal_stores_leaves_no_live_dict(monkeypatch):
    """The helper's population is enumerated from the module, so a store added later is covered.
    Assert both that it found the known stores and that NONE remains a modal.Dict -- the 46
    test rows found in the production transcript store came from one Dict left un-stubbed."""
    import importlib.util
    modal = pytest.importorskip("modal")
    import types
    from conftest import isolate_modal_stores
    sys.path.insert(0, os.path.join(_HERE, "..", "chike-whatsapp"))
    try:
        import handler_core as hc
    finally:
        sys.path.pop(0)
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = hc
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", hc)
    spec = importlib.util.spec_from_file_location(
        "chike_mw_isolation_probe", os.path.join(_HERE, "..", "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    assert isinstance(mw.TRANSCRIPTS, modal.Dict)            # live before: the founding hazard
    names = isolate_modal_stores(mw, monkeypatch)
    assert {"TRANSCRIPTS", "REVIEW_QUEUE", "PENDING_ROWS"} <= set(names)
    assert not [n for n, v in vars(mw).items() if isinstance(v, modal.Dict)]
    mw._write_row({"question": "probe", "sender": "x", "ts": "2026-11-11T00:00:00+00:00"})
    assert len(mw.TRANSCRIPTS) == 1                          # landed in the stub, not production

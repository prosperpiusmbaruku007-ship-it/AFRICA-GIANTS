"""OFFLINE-SUITE GUARD: the default test run may not leave this machine.

WHY THIS EXISTS (2026-11-11). pyproject deselects tests marked `network`, and the pre-push hook
documents the suite as ~90s and offline. In fact `test_health_reports_supervised_beside_declared_
size_and_participants_seen` called the real `health()`, which does `TRANSCRIPTS.keys()` on the
PRODUCTION `chike-transcripts-kv` modal.Dict. It took 3s..114s depending on the Tanzanian link,
read live production rows, and made the suite long enough to be killed by a caller's timeout --
which leaves an EMPTY log and a non-zero exit (block-buffered pytest output dies with the process).
The October fix marked HTTP tests `network`; this route (Modal's own gRPC client) went through
none of them. A MARKER IS A CLAIM MADE BY THE TEST'S AUTHOR. This guard is the enforcement: it
does not trust the claim, it removes the capability.

WHAT IT BLOCKS, for every test not marked `network` or `integration`:
  * any outbound socket connect() / connect_ex() to a NON-LOOPBACK address
  * socket.create_connection() and socket.getaddrinfo() for a non-loopback name
That covers requests, httpx, smtplib, grpc/grpclib and therefore every Modal object -- Dict,
Volume, Function.remote, Cls -- because they all bottom out in one of those calls. Loopback is
allowed: tests legitimately run a local HTTP server, and asyncio's own socketpair uses it.

THE FAILURE IS RECORDED, NOT ONLY RAISED. Code under test often wraps I/O in `except Exception`
(`health()` does, deliberately, so it degrades instead of 500ing), which would swallow the raise
and leave the test green having attempted a connection. The makereport hook therefore flips a
passing test to FAILED if any violation was recorded during it.

Proved to fire by tests/test_offline_guard.py (R26: plant the violation, watch it block).
"""
import socket

import pytest

_LOOPBACK = {"localhost", "127.0.0.1", "::1", "0.0.0.0", ""}
_VIOLATIONS_KEY = "_offline_guard_violations"


class OfflineSuiteViolation(BaseException):
    pass


def _is_loopback(host) -> bool:
    if isinstance(host, bytes):
        host = host.decode("ascii", "replace")
    if host is None:
        return True
    h = str(host).strip().lower()
    return h in _LOOPBACK or h.startswith("127.") or h == "::ffff:127.0.0.1"


def _message(what: str, target) -> str:
    return (
        f"OFFLINE SUITE VIOLATION: {what} -> {target!r}. The default test run must not touch the "
        "network, a Modal Dict/Volume/Function, or any remote service. Stub the dependency "
        "(e.g. monkeypatch modal_whatsapp.TRANSCRIPTS with a plain dict), or if the test is "
        "genuinely live, mark it @pytest.mark.network so it is deselected by default."
    )


def _install(monkeypatch, record):
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex
    real_create = socket.create_connection
    real_gai = socket.getaddrinfo

    def _addr_host(address):
        if isinstance(address, tuple) and address:
            return address[0]
        return address  # AF_UNIX path or other: treated below

    def guarded_connect(self, address):
        if self.family in (socket.AF_INET, getattr(socket, "AF_INET6", -1)) \
                and not _is_loopback(_addr_host(address)):
            msg = _message("socket.connect", address)
            record(msg)
            raise OfflineSuiteViolation(msg)
        return real_connect(self, address)

    def guarded_connect_ex(self, address):
        if self.family in (socket.AF_INET, getattr(socket, "AF_INET6", -1)) \
                and not _is_loopback(_addr_host(address)):
            msg = _message("socket.connect_ex", address)
            record(msg)
            raise OfflineSuiteViolation(msg)
        return real_connect_ex(self, address)

    def guarded_create(address, *a, **kw):
        if not _is_loopback(_addr_host(address)):
            msg = _message("socket.create_connection", address)
            record(msg)
            raise OfflineSuiteViolation(msg)
        return real_create(address, *a, **kw)

    def guarded_gai(host, *a, **kw):
        if not _is_loopback(host):
            msg = _message("DNS lookup (getaddrinfo)", host)
            record(msg)
            raise OfflineSuiteViolation(msg)
        return real_gai(host, *a, **kw)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    monkeypatch.setattr(socket, "create_connection", guarded_create)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_gai)


@pytest.fixture(autouse=True)
def _offline_guard(request, monkeypatch):
    if request.node.get_closest_marker("network") or request.node.get_closest_marker("integration") \
            or request.node.get_closest_marker("allow_network"):
        yield
        return
    violations = []
    setattr(request.node, _VIOLATIONS_KEY, violations)
    _install(monkeypatch, violations.append)
    yield


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "allow_network: opt ONE test out of the offline guard (use only for the guard's own tests).")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    violations = getattr(item, _VIOLATIONS_KEY, None)
    if call.when == "call" and violations and rep.passed:
        rep.outcome = "failed"
        rep.longrepr = (
            f"{violations[0]}\n(the code under test swallowed the exception, so the test would "
            f"have passed; {len(violations)} attempt(s) recorded)")


def isolate_modal_stores(mw, monkeypatch):
    """Replace EVERY modal.Dict on a freshly-loaded modal_whatsapp module with a plain dict.

    Stubbing them one at a time is how this leaked: the roster tests stubbed REVIEW_QUEUE and left
    TRANSCRIPTS and PENDING_ROWS live, so `_write_row` WROTE TEST ROWS INTO THE PRODUCTION
    TRANSCRIPT STORE (46 of the 53 rows found on 2026-11-11 were the tests' "Je, SDL inanihusu?").
    Enumerating from the module means a Dict added next month is isolated without anyone
    remembering to. Returns the names replaced, so a test can assert the population is non-empty
    (R20: an empty isolation list would look exactly like a successful one)."""
    import modal
    names = [n for n, v in vars(mw).items() if isinstance(v, modal.Dict)]
    for n in names:
        monkeypatch.setattr(mw, n, StubDict())
    assert names, "no modal.Dict found on the module -- the isolation helper is inert"
    return names


class StubDict(dict):
    """A plain dict with modal.Dict's put(skip_if_exists=True) -- the ATOMIC claim primitive the participant
    disclosure relies on. A bare dict has no .put, so the claim would raise and every disclosure test would
    quietly exercise the `unknown` path instead of the one it names."""

    def put(self, key, value, *, skip_if_exists=False):
        if skip_if_exists and key in self:
            return False
        self[key] = value
        return True

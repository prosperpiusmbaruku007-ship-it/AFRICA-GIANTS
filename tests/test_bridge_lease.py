"""The single-socket lease: two sockets on one WhatsApp session would recreate the silent
failure the bridge exists to end, so the invariants are tested, not assumed."""
import importlib.util
import os

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "chike_bridge_lease", os.path.join(_ROOT, "chike-whatsapp", "bridge", "lease.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)


class Clock:
    t = 1000.0

    def __call__(self):
        return self.t


class Store:
    def __init__(self):
        self.d = {}
        self.fail = False

    def _chk(self):
        if self.fail:
            raise ConnectionError("store down")

    def get(self, k, default=None):
        self._chk()
        return self.d.get(k, default)

    def put(self, k, v, skip_if_exists=False):
        self._chk()
        if skip_if_exists and k in self.d:
            return False
        self.d[k] = v
        return True

    def pop(self, k):
        self._chk()
        return self.d.pop(k)


def _two():
    c, s = Clock(), Store()
    return c, s, L.Lease(s, "A", clock=c), L.Lease(s, "B", clock=c)


def test_only_one_of_two_can_hold():
    c, s, a, b = _two()
    assert a.try_acquire() is True
    assert b.try_acquire() is False


def test_a_holder_that_renews_is_never_displaced():
    c, s, a, b = _two()
    a.try_acquire()
    for _ in range(20):
        c.t += L.RENEW_EVERY_S
        assert a.renew() is True
        assert b.try_acquire() is False


def test_newcomer_waits_for_expiry_then_takes_over_and_old_holder_is_told():
    c, s, a, b = _two()
    a.try_acquire()
    c.t += L.TTL_S - 1
    assert b.try_acquire() is False, "still valid one second before expiry"
    c.t += 2
    assert b.try_acquire() is True
    assert a.renew() is False, "the displaced holder must be told to stop"


def test_fence_holder_gives_up_before_anyone_else_can_take_over():
    """THE invariant. The holder stalls (or the store is unreachable); it must consider itself
    out strictly before the lease expires for everyone else."""
    c, s, a, b = _two()
    a.try_acquire()
    t_stall = c.t
    first_unsafe = first_takeable = None
    for step in range(0, 400):
        c.t = t_stall + step * 0.1
        if first_unsafe is None and not a.safe_to_hold():
            first_unsafe = c.t - t_stall
        if first_takeable is None and s.d["lease"]["expires"] <= c.t:
            first_takeable = c.t - t_stall
    assert first_unsafe is not None and first_takeable is not None
    assert first_unsafe < first_takeable


def test_store_outage_means_the_holder_stops_holding():
    c, s, a, b = _two()
    a.try_acquire()
    s.fail = True
    c.t += L.SELF_DEADLINE_S + 0.1
    assert a.safe_to_hold() is False


def test_never_acquired_is_not_safe():
    c, s, a, b = _two()
    assert a.safe_to_hold() is False


def test_only_one_contender_wins_an_expired_lease():
    c, s, a, b = _two()
    third = L.Lease(s, "C", clock=c)
    a.try_acquire()
    c.t += L.TTL_S + 1
    results = [b.try_acquire(), third.try_acquire()]
    assert results.count(True) == 1


def test_a_lease_renewed_during_takeover_is_put_back_not_stolen():
    c, s, a, b = _two()
    a.try_acquire()
    c.t += L.TTL_S + 1                        # b sees it expired ...
    stale = dict(s.d["lease"])
    real_get = s.get

    def racy_get(k, default=None):            # ... but a renews before b pops
        v = real_get(k, default)
        s.d["lease"] = {"holder": "A", "expires": c.t + L.TTL_S, "acquired": stale["acquired"]}
        return v
    s.get = racy_get
    assert b.try_acquire() is False
    s.get = real_get
    assert s.d["lease"]["holder"] == "A"


def test_release_hands_over_immediately():
    c, s, a, b = _two()
    a.try_acquire()
    a.release()
    assert b.try_acquire() is True


def test_self_deadline_must_sit_inside_the_ttl():
    with pytest.raises(AssertionError):
        L.Lease(Store(), "X", ttl=L.SELF_DEADLINE_S)


def test_the_proxy_has_batch_routes_and_node_never_goes_key_by_key():
    """Found live: one round trip per pre-key made pairing's commit time out. The proxy must
    serve the whole state and accept a commit in one call."""
    src = open(os.path.join(_ROOT, "chike-whatsapp", "bridge", "modal_bridge.py"), encoding="utf-8").read()
    for route in ('"/kv/all"', '"/kv/setmany"', '"/kv/delmany"'):
        assert route in src
    node = open(os.path.join(_ROOT, "chike-whatsapp", "bridge", "authstate.mjs"), encoding="utf-8").read()
    assert "/kv/get" not in node and "/kv/set\"" not in node

"""The single-socket lease. Pure logic over a Dict-like store, so it is testable without Modal.

Two sockets on one WhatsApp session log each other out, which would recreate the silent failure
this bridge exists to end. Rules:

* A container may open the socket only while it holds the lease, and renews every ~5s.
* The lease expires TTL_S after its last renewal. A newcomer waits for that expiry.
* FENCING: the holder gives up locally after `self_deadline_s` (< TTL) without a successful renew,
  and the supervisor kills its socket. So by the time anyone else can see the lease as expired,
  the old holder has already stopped, even if it was stalled or the store was unreachable.
* Takeover of an expired lease goes through `pop`, which only one contender can win.

The store needs get / put(key, value, skip_if_exists=) -> bool / pop(key). modal.Dict has all three.
"""
import time

TTL_S = 20.0
RENEW_EVERY_S = 5.0
SELF_DEADLINE_S = 10.0          # must stay < TTL_S: that gap IS the fence


class Lease:
    def __init__(self, store, me, key="lease", ttl=TTL_S, clock=time.time):
        assert SELF_DEADLINE_S < ttl, "the self-deadline must be inside the lease TTL"
        self.store, self.me, self.key, self.ttl, self.clock = store, me, key, ttl, clock
        self.last_ok = None            # local time of our last successful acquire/renew

    def _rec(self, acquired=None):
        t = self.clock()
        return {"holder": self.me, "expires": t + self.ttl, "acquired": acquired or t}

    def try_acquire(self):
        rec = self._rec()
        if self.store.put(self.key, rec, skip_if_exists=True):
            self.last_ok = rec["acquired"]
            return True
        cur = self.store.get(self.key)
        if cur is None:                                   # vanished between the two calls
            if self.store.put(self.key, rec, skip_if_exists=True):
                self.last_ok = rec["acquired"]
                return True
            return False
        if cur.get("holder") == self.me:
            return self.renew()
        if cur.get("expires", 0) > self.clock():
            return False                                  # someone else holds it, validly
        try:
            popped = self.store.pop(self.key)             # only one contender receives this
        except KeyError:
            return False
        if popped is not None and popped.get("expires", 0) > self.clock() \
                and popped.get("holder") != self.me:
            # we popped a lease that was renewed in the meantime: put it back, do not take it
            self.store.put(self.key, popped, skip_if_exists=True)
            return False
        if self.store.put(self.key, rec, skip_if_exists=True):
            self.last_ok = rec["acquired"]
            return True
        return False

    def renew(self):
        """True only if we still hold it. False means STOP: the supervisor must kill the socket."""
        cur = self.store.get(self.key)
        if not cur or cur.get("holder") != self.me:
            return False
        self.store.put(self.key, self._rec(cur.get("acquired")))
        self.last_ok = self.clock()
        return True

    def safe_to_hold(self):
        """False once we have gone SELF_DEADLINE_S without proof we hold it."""
        return self.last_ok is not None and self.clock() - self.last_ok < SELF_DEADLINE_S

    def release(self):
        try:
            cur = self.store.get(self.key)
            if cur and cur.get("holder") == self.me:
                self.store.pop(self.key)
        except Exception:                                  # noqa: BLE001
            pass
        self.last_ok = None

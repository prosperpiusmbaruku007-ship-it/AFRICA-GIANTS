"""CHIKE WhatsApp bridge on Modal: ONE container, ONE socket, auth state in a Dict.

LIFECYCLE, plainly. Modal containers are not permanent: they can be preempted, and a function is
recycled at its timeout, and a deploy starts the new container before the old one is gone. A
WhatsApp session tolerates exactly one live socket. So:

  max_containers=1 / min_containers=1   one container is wanted, and one is restarted if it dies
  the lease (lease.py)                  only the holder may open the socket; a newcomer waits for
                                        the old lease to expire; a holder that cannot renew kills
                                        its own socket first, so overlap costs seconds, not a fight
  auth state in a Modal Dict            written on every key change, so a preemption loses nothing

Run `modal app stop chike-bridge --yes` before a deploy where you can (R16b): it removes the
overlap altogether. The lease is what protects you when you forget, or when Modal restarts it.
"""
import json
import os
import signal
import subprocess
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import modal

app = modal.App("chike-bridge")
BUILD = os.environ.get("CHIKE_BUILD", "") or "dev"
_HERE = Path(__file__).parent

image = (
    modal.Image.from_registry("node:20-bookworm-slim", add_python="3.11")
    .env({"CHIKE_BUILD": BUILD})
    .add_local_dir(_HERE, "/app", copy=True, ignore=["node_modules", "__pycache__"])
    .run_commands("cd /app && npm install --omit=dev --no-audit --no-fund")
)

SECRET = modal.Secret.from_name("chike-bridge")   # BRIDGE_ADMIN_TOKEN, BRIDGE_SEND_TOKEN, WEBHOOK_URL
AUTH = modal.Dict.from_name("chike-bridge-auth-kv", create_if_missing=True)
OPS = modal.Dict.from_name("chike-bridge-ops-kv", create_if_missing=True)   # lease, alive, state

KV_PORT = 8081
NODE_PORT = 8080


def _publish(cid, holding, node_state, lease_rec):
    t = time.time()
    OPS[f"alive:{cid}"] = t
    OPS["state"] = {"ts": t, "container": cid, "holding_lease": holding, "lease": lease_rec,
                    "node": node_state, "build": BUILD}


def _kv_server(token):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):                                   # noqa: D401
            pass

        def _reply(self, code, obj):
            b = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_POST(self):                                           # noqa: N802
            if self.headers.get("x-ctl") != token:
                return self._reply(401, {"error": "unauthorized"})
            body = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))) or b"{}")
            try:
                if self.path == "/kv/get":
                    try:
                        return self._reply(200, {"v": AUTH[body["k"]]})
                    except KeyError:
                        return self._reply(404, {})
                if self.path == "/kv/set":
                    AUTH[body["k"]] = body["v"]
                    return self._reply(200, {"v": True})
                if self.path == "/kv/del":
                    try:
                        AUTH.pop(body["k"])
                    except KeyError:
                        pass
                    return self._reply(200, {"v": True})
                if self.path == "/kv/clear":
                    AUTH.clear()
                    return self._reply(200, {"v": True})
            except Exception as e:                                   # noqa: BLE001
                return self._reply(500, {"error": type(e).__name__})
            self._reply(404, {})

    srv = ThreadingHTTPServer(("127.0.0.1", KV_PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()


def _supervise():
    import urllib.request
    sys_path = "/app"
    import sys
    sys.path.insert(0, sys_path)
    from lease import Lease, RENEW_EVERY_S

    cid = uuid.uuid4().hex[:8]
    ctl = uuid.uuid4().hex
    admin = os.environ["BRIDGE_ADMIN_TOKEN"]
    _kv_server(ctl)
    lease = Lease(OPS, cid)
    env = {**os.environ, "CTL_TOKEN": ctl, "PORT": str(NODE_PORT), "KV_URL": f"http://127.0.0.1:{KV_PORT}"}
    state = {"node": None, "holding": False, "stop": False}

    def start_node():
        state["node"] = subprocess.Popen(["node", "/app/server.mjs"], env=env, cwd="/app")
        for _ in range(60):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{NODE_PORT}/healthz", timeout=1)
                return
            except Exception:                                        # noqa: BLE001
                time.sleep(0.5)

    def kill_node():
        n = state["node"]
        if n and n.poll() is None:
            n.kill()                      # SIGKILL: the socket is gone at once, no graceful close
            n.wait()

    def connect():
        req = urllib.request.Request(f"http://127.0.0.1:{NODE_PORT}/_ctl/connect", method="POST",
                                     headers={"x-ctl": ctl})
        urllib.request.urlopen(req, timeout=5).read()

    def node_state():
        try:
            return json.loads(urllib.request.urlopen(
                f"http://127.0.0.1:{NODE_PORT}/state?token={admin}", timeout=3).read())
        except Exception as e:                                       # noqa: BLE001
            return {"connection": "unreachable", "error": type(e).__name__}

    def shutdown(*_):
        state["stop"] = True
        kill_node()
        lease.release()               # hand over at once rather than make the next one wait
        os._exit(0)

    try:
        signal.signal(signal.SIGTERM, shutdown)
    except ValueError:                # not the main thread: the lease still expires on its own
        pass

    start_node()
    last_renew = 0.0
    while not state["stop"]:
        try:
            t = time.time()
            if not state["holding"]:
                if lease.try_acquire():
                    state["holding"] = True
                    connect()
                    last_renew = t
            else:
                if t - last_renew >= RENEW_EVERY_S:
                    try:
                        ok = lease.renew()
                    except Exception:                                # noqa: BLE001
                        ok = None     # store unreachable: not proof either way
                    if ok:
                        last_renew = t
                    if ok is False or not lease.safe_to_hold():
                        # LOST (or cannot prove we hold it): close the socket NOW.
                        kill_node()
                        state["holding"] = False
                        start_node()          # back to idle, listening but not connected
            if state["node"].poll() is not None:     # node died on its own
                start_node()
                if state["holding"]:
                    connect()
            if t - state.get("pub", 0) >= 10:     # a Dict write per 2s loop would be wasteful
                state["pub"] = t
                try:
                    _publish(cid, state["holding"], node_state(), OPS.get("lease"))
                except Exception:                                    # noqa: BLE001
                    pass
        except Exception as e:                                       # noqa: BLE001
            print(f"[supervisor] {type(e).__name__}: {e}", flush=True)
        time.sleep(2)


@app.function(image=image, secrets=[SECRET], min_containers=1, max_containers=1,
              cpu=0.125, memory=512, timeout=86400)
@modal.web_server(NODE_PORT, startup_timeout=120)
def bridge():
    threading.Thread(target=_supervise, daemon=False).start()

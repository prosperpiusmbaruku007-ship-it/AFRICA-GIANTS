"""
AFRICA-GIANTS run-skill driver.

Launches `python run.py serve` in mock mode (AFRICA_GIANTS_MOCK=1), waits for
/health, exercises every endpoint, prints a summary, and shuts the server
down cleanly. Mock mode avoids needing HF_TOKEN, GPU, or model weights —
the server returns canned answers but real RAG retrieval against the local
JSON vector store.

Exit code 0 = all endpoints OK, 1 = any failure.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def http_json(method: str, url: str, payload: dict | None = None, timeout: float = 15.0) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return 0, str(e)


def wait_ready(base: str, deadline_s: float = 60.0) -> bool:
    start = time.monotonic()
    while time.monotonic() - start < deadline_s:
        status, _ = http_json("GET", f"{base}/health", timeout=2.0)
        if status == 200:
            return True
        time.sleep(0.5)
    return False


def run_checks(base: str) -> int:
    failures = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal failures
        marker = "PASS" if ok else "FAIL"
        print(f"  [{marker}] {name}" + (f" -- {detail}" if detail else ""))
        if not ok:
            failures += 1

    print(f"\nDriving server at {base}")

    status, body = http_json("GET", f"{base}/health")
    check("GET /health", status == 200 and isinstance(body, dict) and body.get("status") == "healthy",
          str(body)[:160])

    status, body = http_json(
        "POST", f"{base}/v1/chat/completions",
        {"model": "africa-giants",
         "messages": [{"role": "user", "content": "Jinsi ya kusajili kampuni BRELA?"}],
         "max_tokens": 50},
    )
    answer = ""
    if isinstance(body, dict):
        choices = body.get("choices") or []
        if choices:
            answer = choices[0].get("message", {}).get("content", "")
    check("POST /v1/chat/completions", status == 200 and bool(answer), answer[:120])

    status, body = http_json(
        "POST", f"{base}/rag-chat",
        {"question": "What is TRA tax filing?", "top_k": 3, "max_tokens": 80},
    )
    rag_ok = isinstance(body, dict) and bool(body.get("answer")) and isinstance(body.get("sources"), list)
    check("POST /rag-chat", status == 200 and rag_ok,
          f"{len(body.get('sources', [])) if isinstance(body, dict) else 0} sources")

    status, body = http_json(
        "POST", f"{base}/feedback",
        {"question": "Q", "answer": "A", "rating": 5, "metadata": {"source": "run-skill-smoke"}},
    )
    check("POST /feedback", status == 200 and isinstance(body, dict) and body.get("status") == "saved")

    status, body = http_json("GET", f"{base}/metrics?limit=5")
    events = body.get("events", []) if isinstance(body, dict) else []
    check("GET /metrics", status == 200 and isinstance(events, list) and len(events) >= 3,
          f"{len(events)} events")

    return failures


def launch_server(port: int, host: str) -> subprocess.Popen:
    env = os.environ.copy()
    env["AFRICA_GIANTS_MOCK"] = "1"
    env.setdefault("HF_TOKEN", "dummy")
    env["PYTHONIOENCODING"] = "utf-8"
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0  # type: ignore[attr-defined]
    return subprocess.Popen(
        [sys.executable, "run.py", "serve", "--port", str(port), "--host", host],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=creationflags,
    )


def shutdown(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            proc.send_signal(signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
        else:
            proc.terminate()
        proc.wait(timeout=5)
    except (subprocess.TimeoutExpired, OSError):
        proc.kill()
        proc.wait(timeout=5)


def main() -> int:
    ap = argparse.ArgumentParser(description="Smoke-drive the AFRICA-GIANTS serve API in mock mode.")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", type=str, default="127.0.0.1")
    ap.add_argument("--ready-timeout", type=float, default=60.0)
    ap.add_argument("--keep-running", action="store_true",
                    help="Leave the server running after checks pass (Ctrl-C to stop).")
    args = ap.parse_args()

    base = f"http://{args.host}:{args.port}"
    print(f"Launching: {sys.executable} run.py serve --port {args.port} --host {args.host}  (AFRICA_GIANTS_MOCK=1)")
    proc = launch_server(args.port, args.host)

    try:
        if not wait_ready(base, args.ready_timeout):
            print(f"FAIL: server did not become ready within {args.ready_timeout:.0f}s", file=sys.stderr)
            return 1

        failures = run_checks(base)

        print()
        if failures == 0:
            print("SUMMARY: all endpoints OK")
        else:
            print(f"SUMMARY: {failures} endpoint(s) failed")

        if args.keep_running and failures == 0:
            print(f"\nServer left running at {base} (PID {proc.pid}). Ctrl-C to stop.")
            try:
                proc.wait()
            except KeyboardInterrupt:
                pass
            return 0
        return 0 if failures == 0 else 1
    finally:
        if not (args.keep_running and proc.poll() is None):
            shutdown(proc)


if __name__ == "__main__":
    sys.exit(main())

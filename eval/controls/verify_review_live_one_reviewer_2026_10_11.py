# -*- coding: utf-8 -*-
r"""LIVE VERIFICATION OF THE SUPERVISED REVIEW PATH, WITH ONE REVIEWER ON THE ROSTER.

Run against the DEPLOYED app, before any participant. What it exercises (the founder's list):

  1. two drafts arriving close together, both pushed, each held until acted on
  2. the claim lock holding -- opening a draft twice does not let it send twice
  3. a claimed-but-unacted draft releasing after the timeout, and the roster being re-notified
  4. an unreviewed draft never sending, however long it waits
  5. approve, edit and withhold each exercised once, with draft / edit / final kept separate

With ONE reviewer, "two reviewers contend for one draft" CANNOT be exercised live. That path is
proven offline (tests/test_review_roster.py), and this file does not pretend otherwise.

NOTHING HERE TOUCHES A PARTICIPANT. Drafts are seeded through a Modal FUNCTION (CLI
credentials only; no public route can place a draft). Drafts A and B carry an unroutable
sender. Drafts C and D carry the REVIEWER'S OWN number, so an approved or edited reply is
delivered to the reviewer's phone -- which proves the send leg end to end. Draft E is withheld,
which sends nothing.

The signing key never reaches this script: `mint_review_link` runs inside the container and
only serves seeded TEST- drafts.

WHAT IT CANNOT ASSERT: that a WhatsApp message ARRIVED on a handset. It reports Wappfly's
accept/reject result for each push and send; the reviewer confirms arrival by looking.

Usage:
    python eval/controls/verify_review_live_one_reviewer_2026_10_11.py \
        --health-url <url> --claim-url <url> --act-url <url> --claim-ttl 60 --renotify 120
Artifact: eval/results/review_live_one_reviewer_2026_10_11.json (rewritten after EVERY check)
Exit 0 verified - 1 a finding - 2 could not be exercised (NOT a pass).
"""
import argparse
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "eval", "results", "review_live_one_reviewer_2026_10_11.json")


def _http(url, payload=None, timeout=60):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST" if payload is not None else "GET",
        headers={"Content-Type": "text/plain"} if payload is not None else {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw, code, hdrs = r.read().decode("utf-8", "replace"), r.status, dict(r.headers)
    except urllib.error.HTTPError as e:
        raw, code, hdrs = e.read().decode("utf-8", "replace"), e.code, dict(e.headers)
    except Exception as e:                                           # noqa: BLE001
        return 0, {"error": f"{type(e).__name__}: {e}"}, {}
    try:
        return code, json.loads(raw), hdrs
    except Exception:                                                # noqa: BLE001
        return code, {"raw": raw[:300]}, hdrs


def _modal(target, extra=()):
    proc = subprocess.run(
        [sys.executable, "-m", "modal", "run", f"chike-whatsapp/modal_whatsapp.py::{target}",
         *extra],
        capture_output=True, text=True, cwd=REPO, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    return (proc.stdout or "") + (proc.stderr or "")


def _marker(out, marker):
    for ln in out.splitlines():
        if marker in ln:
            return ln.split(marker, 1)[1].strip()
    return None


def _queue():
    m = _marker(_modal("dump_queue"), "QUEUE ")
    if not m:
        return None
    try:
        return {x["review_id"]: x for x in json.loads(m)["items"]}
    except Exception:                                                # noqa: BLE001
        return None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--health-url", required=True)
    ap.add_argument("--claim-url", required=True)
    ap.add_argument("--act-url", required=True)
    ap.add_argument("--claim-ttl", type=float, required=True, help="the deployed CLAIM_TTL_S")
    ap.add_argument("--renotify", type=float, required=True, help="the deployed RENOTIFY_AFTER_S")
    args = ap.parse_args()
    # `modal run` executes the LOCAL file in an ephemeral app whose image bakes the SHELL's
    # environment. Without these the seeded drafts' push finds no review URLs and reports
    # "NOT NOTIFIED" -- the first live run never exercised the push at all for this reason.
    base = args.claim_url.rsplit("-review-claim", 1)[0]
    os.environ.update({"REVIEW_D_URL": base + "-d.modal.run",
                       "REVIEW_CLAIM_URL": args.claim_url, "REVIEW_ACT_URL": args.act_url,
                       "CLAIM_TTL_S": str(int(args.claim_ttl)),
                       "RENOTIFY_AFTER_S": str(int(args.renotify))})

    art = {"_what": __doc__.strip().splitlines()[0], "checks": [], "findings": [],
           "health_url": args.health_url, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}

    def save():
        io.open(OUT, "w", encoding="utf-8").write(json.dumps(art, ensure_ascii=False, indent=1))

    def record(name, ok, detail, must_pass=True):
        art["checks"].append({"name": name, "ok": bool(ok), "detail": detail,
                              "must_pass": must_pass})
        print(f"  [{'OK  ' if ok else 'FAIL'}] {name}: {detail}", flush=True)
        if must_pass and not ok:
            art["findings"].append(name)
        save()

    # -- gate: the deployment is in the state this test assumes --------------------------
    code, h, _ = _http(args.health_url)
    if code != 200:
        print(f"[FATAL] /health -> {code} {h}")
        return 2
    roster = h.get("roster") or {}
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                          text=True, cwd=REPO).stdout.strip()
    ok_gate = (h.get("supervised") is True and roster.get("reviewers") == 1
               and roster.get("signing_key_set") and roster.get("can_issue_links")
               and h.get("build") == head)
    record("gate: supervised, 1 reviewer, key set, links issuable, build == HEAD",
           ok_gate, f"build={h.get('build')} head={head} supervised={h.get('supervised')} "
                    f"roster={ {k: roster.get(k) for k in ('reviewers', 'signing_key_set', 'can_issue_links', 'claim_ttl_s', 'renotify_after_s')} }")
    if not ok_gate:
        return 2
    if (roster.get("claim_ttl_s") != args.claim_ttl
            or roster.get("renotify_after_s") != args.renotify):
        print("[FATAL] deployed timings differ from --claim-ttl/--renotify")
        return 2

    stamp = str(int(time.time()))

    def seed(tag, to_reviewer=False):
        extra = ["--label", f"{stamp}{tag}"] + (["--to-reviewer"] if to_reviewer else [])
        rid = _marker(_modal("seed_test_draft", extra), "SEEDED ")
        if not rid:
            print(f"[FATAL] could not seed {tag}")
            sys.exit(2)
        return rid

    def creds(rid):
        m = _marker(_modal("mint_review_link", ["--review-id", rid]), "MINTED ")
        if not m:
            print(f"[FATAL] could not mint a link for {rid}")
            sys.exit(2)
        return json.loads(m)

    def claim(c):
        return _http(args.claim_url, c)

    def act(c, action, **kw):
        return _http(args.act_url, {**c, "action": action, **kw})

    # -- 1. two drafts close together -----------------------------------------------------
    a = seed("A")
    b = seed("B")
    t_seed = time.time()
    ca, cb = creds(a), creds(b)
    q = _queue() or {}
    record("1a. two drafts pending at once", a != b and all(
        q.get(x, {}).get("status") == "pending" for x in (a, b)),
        f"{a} / {b}")
    record("1b. BOTH were pushed to the reviewer (Wappfly accepted: recipients == 1) -- "
           "ARRIVAL ON THE HANDSET is for the reviewer to confirm by looking",
           all(q.get(x, {}).get("last_notify_recipients") == 1 for x in (a, b)),
           f"A notify_count={q.get(a, {}).get('notify_count')} "
           f"recipients={q.get(a, {}).get('last_notify_recipients')}; "
           f"B notify_count={q.get(b, {}).get('notify_count')} "
           f"recipients={q.get(b, {}).get('last_notify_recipients')}")

    # -- 2. the claim lock ----------------------------------------------------------------
    t_claim = time.time()
    s1, j1, hd = claim(ca)
    record("2a. first open claims the draft, response readable cross-origin",
           s1 == 200 and j1.get("outcome") == "claimed"
           and bool({k.lower(): v for k, v in hd.items()}.get("access-control-allow-origin")),
           f"HTTP {s1} {j1}")
    s2, j2, _ = claim(ca)
    record("2b. opening it AGAIN is idempotent (already_yours), not a second claim",
           s2 == 200 and j2.get("outcome") == "already_yours", f"HTTP {s2} {j2}")
    s3, j3, _ = claim({**ca, "t": "forged"})
    record("2c. a forged token cannot claim", s3 == 404, f"HTTP {s3} {j3}")

    # -- 3. timeout releases; the roster is re-notified ----------------------------------
    wait = max(0, args.claim_ttl + 10 - (time.time() - t_claim))
    print(f"  ... waiting {wait:.0f}s for A's claim to expire (measured from the claim)",
          flush=True)
    time.sleep(wait)
    s4, j4, _ = act(ca, "send")
    record("3a. after the claim EXPIRED the holder cannot act on it (nothing sends)",
           s4 == 409, f"HTTP {s4} {j4}")
    print("  ... sweeping (releases the expired claim)", flush=True)
    _modal("sweep_review_queue")
    q = _queue() or {}
    ia = q.get(a, {})
    record("3b. the claim RELEASED back to the roster and the release is recorded",
           ia.get("claimed_by") in (None, "") and (ia.get("release_count") or 0) >= 1
           and ia.get("status") == "pending",
           f"claimed_by={ia.get('claimed_by')!r} release_count={ia.get('release_count')} "
           f"status={ia.get('status')}")
    n_before = {x: (q.get(x, {}).get("notify_count") or 0) for x in (a, b)}
    wait = max(0, args.renotify + 10 - (time.time() - t_seed))
    print(f"  ... waiting {wait:.0f}s for the re-notify interval", flush=True)
    time.sleep(wait)
    _modal("sweep_review_queue")
    q = _queue() or {}
    record("3c. an unacted draft RE-NOTIFIES the reviewer (it holds; it does not fall through)",
           all((q.get(x, {}).get("notify_count") or 0) > n_before[x] for x in (a, b)),
           f"notify_count A {n_before[a]}->{q.get(a, {}).get('notify_count')}, "
           f"B {n_before[b]}->{q.get(b, {}).get('notify_count')}; "
           f"renotify_count A={q.get(a, {}).get('renotify_count')}")

    # -- 4. never sends --------------------------------------------------------------------
    waited = time.time() - t_seed
    ib, ia = q.get(b, {}), q.get(a, {})
    record(f"4. after {waited:.0f}s -- more than the claim timeout AND the re-notify interval, "
           "with two sweeps -- A and B are STILL pending, undecided, with no final answer "
           "and no send recorded",
           all(i.get("status") == "pending" and not i.get("decided_by")
               and i.get("final") is None and i.get("send_ok") is None for i in (ia, ib)),
           f"A={ia.get('status')}/{ia.get('final')!r}/send_ok={ia.get('send_ok')} "
           f"B={ib.get('status')}/{ib.get('final')!r}/send_ok={ib.get('send_ok')}")

    # -- 5. approve / edit / withhold, each once -------------------------------------------
    c_id, d_id, e_id = seed("C", True), seed("D", True), seed("E", True)
    cc, cd, ce = creds(c_id), creds(d_id), creds(e_id)
    for c in (cc, cd, ce):
        claim(c)
    s5, j5, _ = act(cc, "send")
    s5b, j5b, _ = act(cc, "send")
    record("5a. APPROVE: sent once, delivered (send_ok), and a second approve is refused "
           "so it cannot send twice", s5 == 200 and j5.get("send_ok") is True and s5b == 409,
           f"first HTTP {s5} {j5}; second HTTP {s5b} {j5b}")
    s8, j8, _ = act(cd, "edit", edited="x")
    record("5d. an edit WITHOUT a reason is refused while the draft is still pending",
           s8 == 409 and "reason" in str(j8.get("detail", "")), f"HTTP {s8} {j8}")
    s6, j6, _ = act(cd, "edit", edited="[MTIHANI] Jibu lililohaririwa na mkaguzi.",
                    reason="live check: the edit reason is recorded")
    record("5b. EDIT: sent the edited text", s6 == 200 and j6.get("send_ok") is True,
           f"HTTP {s6} {j6}")
    s7, j7, _ = act(ce, "withhold", reason="live check: withheld on purpose")
    record("5c. WITHHOLD: nothing sent", s7 == 200 and j7.get("send_ok") is None,
           f"HTTP {s7} {j7}")

    q = _queue() or {}
    ic, id_, ie = q.get(c_id, {}), q.get(d_id, {}), q.get(e_id, {})
    record("5e. approve: draft == final, status sent, attributed",
           ic.get("status") == "sent" and ic.get("final") == ic.get("draft")
           and ic.get("decided_by_name"), f"{ic.get('status')} by {ic.get('decided_by_name')}")
    record("5f. edit: draft KEPT, final DIFFERENT, reason recorded -- three separate fields",
           id_.get("status") == "edited" and id_.get("draft") and id_.get("final")
           and id_["draft"] != id_["final"] and id_.get("edit_reason"),
           f"draft!=final {id_.get('draft') != id_.get('final')} "
           f"reason={id_.get('edit_reason')!r}")
    record("5g. withhold: draft kept, NO final, reason recorded",
           ie.get("status") == "withheld" and ie.get("draft") and ie.get("final") is None
           and ie.get("edit_reason"), f"{ie.get('status')} final={ie.get('final')!r}")

    # -- tidy: dispose of A and B WITHOUT sending (their sender is unroutable) -------------
    for cr in (ca, cb):
        claim(cr)
    act(ca, "withhold", reason="live check cleanup -- never sent")
    act(cb, "withhold", reason="live check cleanup -- never sent")

    art["summary"] = {"checks": len(art["checks"]), "failed": art["findings"],
                      "multi_reviewer_contention": "NOT exercised live (one reviewer); "
                      "proven offline in tests/test_review_roster.py"}
    save()
    print(f"\n{len(art['checks']) - len(art['findings'])}/{len(art['checks'])} passed "
          f"- artifact {os.path.relpath(OUT, REPO)}")
    if art["findings"]:
        print("FINDINGS: " + "; ".join(art["findings"]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

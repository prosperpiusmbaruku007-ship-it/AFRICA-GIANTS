# -*- coding: utf-8 -*-
r"""THE FOUR THINGS THAT MUST BE TRUE BEFORE A PARTICIPANT EVER MESSAGES THE NUMBER.

Named by the founder, verified here against the LIVE deployment rather than the test suite:

  1. two reviewers, two drafts at once
  2. the claim lock holds — the second reviewer cannot act on a draft the first holds
  3. a timed-out claim releases back to the roster
  4. an unreviewed draft NEVER sends

⛔ WHY LIVE AND NOT THE SUITE. The offline tests prove the pure logic; they cannot prove the
DEPLOYED app wires it. Two inert controls in this project had perfect logic and were reached by
nothing — `scan_for_keys.py` scanned correctly and was handed no files; `chike/retrieval.py`'s
contract raises correctly and production never imports it. The question is never "does the rule
work", it is "what does the deployed path actually call".

⛔⛔ AND NOTHING HERE TOUCHES A REAL PARTICIPANT. The drafts are seeded through a Modal
FUNCTION (`seed_test_draft`), not a web endpoint, so injection requires CLI credentials and
there is no public route that can put a draft in the queue. Each seeded draft's `sender` is a
documented unroutable test number, so even a successful send cannot reach a person — and the
test asserts the send was never attempted, which is the stronger claim.

⚠️ WHAT THIS DOES **NOT** VERIFY: that a WhatsApp notification ARRIVES on a reviewer's handset.
That needs a real number on the roster, which is the founder's to give. The notification leg is
exercised as far as the Wappfly call and its result is reported, not asserted.

Usage:
    python eval/controls/verify_review_roster_live_2026_10_10.py --base <url> \
        --admin <ADMIN_TOKEN> --key <REVIEW_SIGNING_KEY> \
        --r1 <number> --r2 <number>
Artifact: eval/results/review_roster_live_2026_10_10.json
Exit 0 all four verified · 1 a finding · 2 could not be exercised (NOT a pass).
"""
import argparse
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "chike-whatsapp"))
OUT = os.path.join(REPO, "eval", "results", "review_roster_live_2026_10_10.json")


def _post(url, payload, timeout=60):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(raw)
        except Exception:                                            # noqa: BLE001
            return e.code, {"raw": raw[:400]}
    except Exception as e:                                           # noqa: BLE001
        return 0, {"error": f"{type(e).__name__}: {e}"}


def _get(url, timeout=60):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
            try:
                return r.status, json.loads(raw)
            except Exception:                                        # noqa: BLE001
                return r.status, {"html_len": len(raw), "html_head": raw[:200]}
    except urllib.error.HTTPError as e:
        return e.code, {"raw": e.read().decode("utf-8", "replace")[:300]}
    except Exception as e:                                           # noqa: BLE001
        return 0, {"error": f"{type(e).__name__}: {e}"}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                # noqa: BLE001
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="deployed base URL, no trailing slash")
    ap.add_argument("--admin", required=True)
    ap.add_argument("--key", required=True, help="REVIEW_SIGNING_KEY, to mint link tokens")
    ap.add_argument("--r1", required=True)
    ap.add_argument("--r2", required=True)
    ap.add_argument("--claim-ttl", type=float, default=60.0,
                    help="the deployed CLAIM_TTL_S; the release check waits past it")
    args = ap.parse_args()

    import handler_core as hc
    base = args.base.rstrip("/")
    art = {"_what": __doc__.strip().splitlines()[0], "base": base, "checks": [],
           "findings": []}

    def record(name, ok, detail, must_pass=True):
        art["checks"].append({"name": name, "ok": bool(ok), "detail": detail,
                              "must_pass": must_pass})
        print(f"  [{'OK  ' if ok else 'FAIL'}] {name}: {detail}")
        if must_pass and not ok:
            art["findings"].append(name)

    # ── GATE 0: is the deployment even in the state this test assumes? ────────────────
    status, health = _get(f"{base}/health")
    if status != 200:
        print(f"[FATAL] /health returned {status}: {health}")
        return 2
    roster = health.get("roster") or {}
    print(f"build={health.get('build')} supervised={health.get('supervised')} "
          f"reviewers={roster.get('reviewers')} ttl={roster.get('claim_ttl_s')}")
    if health.get("supervised") is not True:
        print(f"[FATAL] supervised={health.get('supervised')!r}. This harness verifies the "
              f"SUPERVISED path; running it against an unsupervised deploy would report "
              f"green about a mechanism that is not in force.")
        return 2
    if (roster.get("reviewers") or 0) < 2:
        print(f"[FATAL] the roster has {roster.get('reviewers')} reviewer(s). The claim "
              f"lock is a claim about TWO reviewers and cannot be exercised with one.")
        return 2
    if not roster.get("signing_key_set"):
        print("[FATAL] no signing key on the deployment — every link would be forgeable "
              "and none would authenticate.")
        return 2

    rid1 = hc.reviewer_id(args.key, args.r1)
    rid2 = hc.reviewer_id(args.key, args.r2)
    if rid1 not in (roster.get("reviewer_ids") or []):
        print(f"[FATAL] --r1 does not match any reviewer on the deployed roster. The key or "
              f"the number is wrong, and a token minted here would authenticate as nobody.")
        return 2
    if rid2 not in (roster.get("reviewer_ids") or []):
        print("[FATAL] --r2 does not match any reviewer on the deployed roster.")
        return 2
    record("gate: deployment is supervised, 2+ reviewers, signing key set, both handles "
           "match the live roster", True,
           f"build={health.get('build')} reviewers={roster.get('reviewers')}")

    # ── 1. TWO DRAFTS AT ONCE ─────────────────────────────────────────────────────────
    import subprocess
    stamp = str(int(time.time()))
    ids = []
    for n in ("A", "B"):
        proc = subprocess.run(
            [sys.executable, "-m", "modal", "run",
             "chike-whatsapp/modal_whatsapp.py::seed_test_draft",
             "--label", f"live-{stamp}-{n}"],
            capture_output=True, text=True, cwd=REPO,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
        out = (proc.stdout or "") + (proc.stderr or "")
        found = [ln.split("SEEDED ", 1)[1].strip() for ln in out.splitlines()
                 if "SEEDED " in ln]
        if not found:
            print(f"[FATAL] could not seed draft {n}. modal run output:\n{out[-1500:]}")
            return 2
        ids.append(found[0])
    a, b = ids
    record("1. two drafts seeded and pending at once", a != b, f"{a} and {b}")

    def claim(rid, token_for, review_id):
        return _post(f"{base}/review_claim",
                     {"review_id": review_id, "v": rid,
                      "t": hc.review_token(args.key, review_id, token_for)})

    def act(rid, token_for, review_id, action, **kw):
        payload = {"review_id": review_id, "v": rid,
                   "t": hc.review_token(args.key, review_id, token_for),
                   "action": action}
        payload.update(kw)
        return _post(f"{base}/review_act", payload)

    # ── 2. THE CLAIM LOCK ─────────────────────────────────────────────────────────────
    s1, j1 = claim(rid1, args.r1, a)
    record("2a. reviewer 1 claims draft A", s1 == 200 and j1.get("outcome") == "claimed",
           f"HTTP {s1} {j1}")
    s2, j2 = claim(rid2, args.r2, a)
    record("2b. reviewer 2 is REFUSED the same draft",
           s2 == 200 and j2.get("outcome") == "held_by_other" and j2.get("ok") is False,
           f"HTTP {s2} {j2}")
    s3, j3 = act(rid2, args.r2, a, "withhold", reason="live claim-lock probe")
    record("2c. reviewer 2 CANNOT withhold a draft reviewer 1 holds — "
           "⛔ send-vs-withhold is the race that matters",
           s3 == 409 and "another reviewer" in str(j3.get("detail", "")),
           f"HTTP {s3} {j3}")
    s4, j4 = claim(rid1, args.r1, a)
    record("2d. reviewer 1 re-opening their own claim is not a conflict",
           s4 == 200 and j4.get("outcome") == "already_yours", f"HTTP {s4} {j4}")
    # The other draft is independent — a lock on one must not lock the queue.
    s5, j5 = claim(rid2, args.r2, b)
    record("2e. reviewer 2 CAN claim the OTHER draft — the lock is per-draft, not a global "
           "mutex", s5 == 200 and j5.get("outcome") == "claimed", f"HTTP {s5} {j5}")

    # ── 3. A TIMED-OUT CLAIM RELEASES ─────────────────────────────────────────────────
    wait = args.claim_ttl + 10
    print(f"  ... waiting {wait:.0f}s for draft A's claim to expire "
          f"(deployed CLAIM_TTL_S={args.claim_ttl:.0f})")
    time.sleep(wait)
    s6, j6 = act(rid1, args.r1, a, "send")
    record("3a. the ORIGINAL holder can no longer act once the claim has expired",
           s6 == 409 and ("expired" in str(j6.get("detail", ""))
                          or "not claimed" in str(j6.get("detail", ""))),
           f"HTTP {s6} {j6}")
    s7, j7 = claim(rid2, args.r2, a)
    record("3b. the draft RELEASED back to the roster — reviewer 2 can now claim it",
           s7 == 200 and j7.get("outcome") == "claimed", f"HTTP {s7} {j7}")

    # ── 4. NOTHING SENT, EVER ─────────────────────────────────────────────────────────
    status, q = _get(f"{base}/review_queue?token={args.admin}")
    if status != 200:
        print(f"[FATAL] /review_queue returned {status}: {q}")
        return 2
    items = {i["review_id"]: i for i in (q.get("items") or [])}
    both = [items.get(a), items.get(b)]
    missing = [rid for rid, it in zip((a, b), both) if it is None]
    if missing:
        print(f"[FATAL] seeded drafts not found in the queue: {missing}")
        return 2
    record("4a. both drafts are STILL pending after a full claim/expiry/re-claim cycle",
           all(i.get("status") == "pending" for i in both),
           f"A={both[0].get('status')} B={both[1].get('status')}")
    record("4b. neither draft has a FINAL answer — nothing was composed to send",
           all(i.get("final") is None for i in both),
           f"A final={both[0].get('final')!r} B final={both[1].get('final')!r}")
    record("4c. neither draft was SENT — send_ok is unset on both (the hold reported true "
           "for STORING, never for delivering)",
           all(i.get("status") == "pending" for i in both)
           and all(not i.get("decided_by") for i in both),
           f"A decided_by={both[0].get('decided_by')!r} "
           f"B decided_by={both[1].get('decided_by')!r}")
    record("4d. the release is RECORDED, so a reviewer handing a draft back is visible "
           "rather than silent",
           (both[0].get("release_count") or 0) >= 1,
           f"A release_count={both[0].get('release_count')} "
           f"claim_count={both[0].get('claim_count')}")

    # The notification leg: reported, not asserted (no real handset on the roster).
    record("notification leg exercised (DELIVERY NOT ASSERTED — needs a real number on the "
           "roster, which is the founder's to give)",
           True,
           f"A notify_count={both[0].get('notify_count')} "
           f"recipients={both[0].get('last_notify_recipients')}; "
           f"B notify_count={both[1].get('notify_count')} "
           f"recipients={both[1].get('last_notify_recipients')}",
           must_pass=False)

    # ── and a genuine decision, so the POSITIVE limb is exercised too (R26) ───────────
    # Without this the whole run could pass from a system that refuses EVERYTHING.
    s8, j8 = act(rid2, args.r2, b, "withhold",
                 reason="live verification — withheld on purpose, never sent")
    record("5. the POSITIVE limb: the holder CAN decide, and it is attributed. A run that "
           "only showed refusals would equally describe a system that refuses everything",
           s8 == 200 and j8.get("ok") is True and j8.get("status") == "withheld"
           and j8.get("by"), f"HTTP {s8} {j8}")
    status, q2 = _get(f"{base}/review_queue?token={args.admin}")
    after = {i["review_id"]: i for i in (q2.get("items") or [])}.get(b) or {}
    record("5b. the withheld draft records WHO withheld it, keeps the draft verbatim, and "
           "has no final answer",
           after.get("decided_by_name") and after.get("draft")
           and after.get("final") is None,
           f"by={after.get('decided_by_name')!r} final={after.get('final')!r} "
           f"reason={after.get('edit_reason')!r}")

    art["summary"] = {
        "checks": len(art["checks"]),
        "failed": art["findings"],
        "the_four": {
            "two_reviewers_two_drafts": "1, 2e",
            "claim_lock_holds": "2a-2d",
            "timed_out_claim_releases": "3a-3b",
            "unreviewed_draft_never_sends": "4a-4d",
        },
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(art, ensure_ascii=False, indent=1))
    print(f"\n{len(art['checks']) - len(art['findings'])}/{len(art['checks'])} checks "
          f"passed · artifact: {os.path.relpath(OUT, REPO)}")
    if art["findings"]:
        print("FINDINGS: " + ", ".join(art["findings"]))
        return 1
    print("ALL FOUR VERIFIED LIVE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

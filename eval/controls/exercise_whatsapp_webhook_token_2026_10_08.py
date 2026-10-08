# -*- coding: utf-8 -*-
"""EXERCISE THE WHATSAPP WEBHOOK TOKEN — the last control never fired (2026-10-08).

It has sat `NOT_EXERCISABLE` in `eval/results/control_fire_audit.json` since 2026-08-24, for
a stated reason that was true: it needs the live app and its Modal Secret. That makes it the
only entry in the census with no evidence behind it — and it is the gate between the open
internet and a GPU, so "no evidence" is the wrong state for it to stay in.

⛔ HOW THE ROW-WRITE IS PROVEN WITHOUT THE ADMIN TOKEN, which is the trick that makes this
runnable at all. Reading `/transcripts` needs `ADMIN_TOKEN`, and the `chike-whatsapp` Modal
Secret is founder-only — Modal does not expose secret values to the CLI by design. But
`/health` reports `transcript_store.rows` UNAUTHENTICATED. So the rejection row is proven by
watching that counter move, rather than by reading the row. A count is weaker than the row
itself and it is enough for this claim: the row either wrote or it did not.

THE NEGATIVE ARMS, which are the safety-relevant direction (a wrong token must never reach
the GPU):
  1. NO token at all
  2. a wrong token of the WRONG length
  3. a wrong token of the EXACT length of the real one (40 chars)
Arm 3 is the one worth having: it proves the gate compares VALUES, not lengths. A
length-based check would pass it, and `/health` publishes the real length, so an attacker
knows it.

⚠️ THE POSITIVE ARM IS NOT EXERCISABLE HERE AND IS NOT CLAIMED. Supplying the CORRECT token
needs the Secret. So this run evidences only that wrong tokens are refused and recorded.
That is an honest half, and the half is named rather than rounded up — a census that quietly
omits what it could not test reports a cleaner result than it earned. The positive arm's
failure mode (rejecting a LEGITIMATE Wappfly delivery) is also the one that has already been
OBSERVED failing: three failed sends and two token rotations on 2026-08-14, which is why the
fingerprint block exists in the first place.

THIS WRITES TO PRODUCTION STATE, DELIBERATELY: three `kind: rejected` rows land in the live
transcript store. They carry no PII (sender fields are None on a rejection) and they are
exactly what that store exists to hold. They are the evidence, so they are left in place.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "whatsapp_webhook_token_exercised.json")

HEALTH = "https://prosperpiusmbaruku007--chike-whatsapp-health.modal.run"
WEBHOOK = "https://prosperpiusmbaruku007--chike-whatsapp-webhook.modal.run"

# A realistic Wappfly-shaped delivery, so the rejection is judged on the TOKEN and not on a
# payload the handler would have ignored anyway (`reject_reason: 'ignored'` is a different
# branch, and conflating them would be a bad specimen).
PAYLOAD = {
    "from": "255700000000@c.us",
    "body": "Ada ya kusajili kampuni ni ngapi?",
    "type": "chat",
    "fromMe": False,
}


def _get(url, timeout=120):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _post(url, body, timeout=180):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, {"_http_error": e.read().decode("utf-8", "replace")[:300]}


def rows_now():
    h = _get(HEALTH)
    return h, ((h.get("transcript_store") or {}).get("rows"))


ARMS = [
    {"id": "no_token", "token": None,
     "why": "A delivery with no token at all. The most basic case and the one an attacker "
            "who merely guesses the URL would send."},
    {"id": "wrong_token_wrong_length", "token": "obviously-not-the-token",
     "why": "A wrong value of the wrong length."},
    {"id": "wrong_token_CORRECT_length", "token": "x" * 40,
     "why": "⛔ THE ARM WORTH HAVING: 40 characters, the exact length of the real token, "
            "which /health publishes unauthenticated. A length-based check would PASS this. "
            "It proves the gate compares values."},
]


def main():
    h0, before = rows_now()
    if before is None:
        print("[webhook] cannot read transcript_store.rows — cannot prove a row write, "
              "which is NOT a pass.")
        return 2
    print(f"build={h0.get('build')}  webhook_token_set={h0.get('webhook_token_set')}  "
          f"rows before={before}")
    if not h0.get("webhook_token_set"):
        print("[webhook] WEBHOOK_TOKEN IS UNSET — the endpoint is OPEN and this exercise "
              "would be meaningless. That is itself the finding.")
        return 1

    results, expected_rows = [], before
    for arm in ARMS:
        url = WEBHOOK if arm["token"] is None else f"{WEBHOOK}?token={arm['token']}"
        status, body = _post(url, PAYLOAD)
        time.sleep(3)                      # the row is written before the response returns,
        _, after = rows_now()              # but the Dict read needs a reload on the next call
        rejected = body.get("status") == "unauthorized"
        expected_rows += 1
        row = {
            "arm": arm["id"], "why": arm["why"],
            "http_status": status, "response": body,
            "rejected_as_unauthorized": rejected,
            "rows_before_arm": expected_rows - 1, "rows_after_arm": after,
            "row_was_written": after == expected_rows,
            "verdict": "PASS" if (rejected and after == expected_rows) else "FAIL",
        }
        results.append(row)
        print(f"[{row['verdict']:4s}] {arm['id']:28s} http={status} "
              f"status={body.get('status')!r} rows={after} (expected {expected_rows})")
        if row["verdict"] == "FAIL":
            print(f"        ⛔ {'NOT rejected' if not rejected else 'no row written'}")

    _, final = rows_now()
    failed = [r for r in results if r["verdict"] == "FAIL"]
    payload = {
        "_what": "The WhatsApp webhook token gate, exercised against the live endpoint.",
        "_why_it_mattered": "It was the only entry in control_fire_audit.json with NO "
                            "evidence behind it, and it is the gate between the open "
                            "internet and a GPU.",
        "_how_the_row_write_is_proven": "Reading /transcripts needs ADMIN_TOKEN and the "
                                        "chike-whatsapp Secret is founder-only (Modal does "
                                        "not expose secret values to the CLI). /health "
                                        "reports transcript_store.rows UNAUTHENTICATED, so "
                                        "the row is proven by the counter moving. Weaker "
                                        "than reading the row, and sufficient: it either "
                                        "wrote or it did not.",
        "_positive_arm_NOT_claimed": "Supplying the CORRECT token needs the Secret, so this "
                                     "run evidences ONLY that wrong tokens are refused and "
                                     "recorded. The half is named rather than rounded up. "
                                     "Note the positive arm's failure mode -- rejecting a "
                                     "LEGITIMATE delivery -- has already been OBSERVED "
                                     "failing: three failed sends and two token rotations on "
                                     "2026-08-14, which is why the fingerprint block exists.",
        "_production_writes": f"{len(ARMS)} `kind: rejected` rows left in the live transcript "
                              f"store, deliberately. No PII (sender fields are None on a "
                              f"rejection). They are the evidence.",
        "build": h0.get("build"),
        "rows_before": before,
        "rows_after": final,
        "arms": results,
        "verdict": ("NEGATIVE DIRECTION EVIDENCED" if not failed
                    else "FAILED — the gate did not refuse or did not record"),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"\nrows {before} -> {final}")
    print(f"VERDICT: {payload['verdict']}")
    print("NOTE: the positive arm (correct token accepted) is NOT exercised here — the "
          "Secret is founder-only.")
    print(f"wrote {OUT}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

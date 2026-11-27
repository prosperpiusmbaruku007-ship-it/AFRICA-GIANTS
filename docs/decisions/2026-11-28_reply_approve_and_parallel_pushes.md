# Reply-to-approve, parallel reviewer pushes, the route on every item, and a delivery stamp (founder decisions, 2026-11-28)

Context: `docs/decisions/2026-11-28_question_to_answer_time.md` measured the reviewer's wait (p50 ~12 min) as the largest leg of question -> answer. These four changes were approved on that evidence.

## 1. B-a: parallel reviewer pushes, no receipt wait
`_notify_reviewers` sent each card in turn, each waiting for WhatsApp's delivery receipt. Now cards go out in **batches of at most 4 in parallel** (the bridge's pacer refuses a send queued longer than ~10 s, about 5 slots of ~2 s),
and a card push sends `wait_receipt: false`, which the bridge honours **only when it is exactly `false`** (anything else keeps waiting): it returns "accepted, pending" at once, the same shape the caller already handles for a
send whose receipt had not arrived, so nothing is resent. The old bridge ignores the unknown key, so the Python side can deploy first. A push that raises still propagates after the batch is attempted (a pinned contract:
an unsafe link sends nothing and the draft holds).

## 2. B2: reply-to-approve (a founder amendment to the R7 reading; recorded in CLAUDE.md)
A quoted reply of exactly `TUMA` from a roster reviewer approves; **eight distinct, tested refusals** (CLAUDE.md lists them), each telling the reviewer why; **the same decision function as the page**; `decided_via` recorded.
**Mechanism:** every card push records the WhatsApp message id against `{review_id, reviewer, draft_sha}` (`REVIEW_PUSHES`, pruned after 14 days); a quoted reply is mapped to ONE draft through it. **The bridge did not forward
the quoted id** (it read only `conversation` / `extendedTextMessage.text`), so this needs a `chike-bridge` redeploy: the pure extraction is in `bridge/inbound.mjs` (tested, mutation-tested, and shipped by the image's
`add_local_dir`). The webhook consumes a roster `TUMA` (or any text quoting a card) **before** the participant path: a reviewer's `TUMA` is never a question to the model; a non-roster sender quoting a card is dropped.
**Known limits (accepted, stated):** a reviewer whose message arrives as an unresolved linked-id (`@lid` with no phone) or a device-suffixed JID cannot be matched to the roster and fails closed (a quoted card is
dropped silently; a bare `TUMA` from such an identity is an ordinary participant message); the claim lock is read-then-write (the same race the page has); digests carry no draft and have no reply mapping.
**Deploy order: `chike-whatsapp` first, then `chike-bridge`.** Before the bridge deploy a reply has no quote and is refused with a reason. Rollback: the link flow is untouched; removing the webhook branch (one `if`) disables it.

## 3. Item 5a: the route is stored on every review item, hot and archived
`handler_core.stamp_route` writes `route` + `routes` at hold time; `archive_record` derives one for anything without it. **A legacy item with no path is archived as `unknown`, never back-filled by running today's router over its
question.** The 36 items archived before this change stay `unknown` (their route was not recorded and cannot be recovered truthfully). This is the prerequisite for any per-route evidence (the immediate-send allowlist).

## 4. Item 5b: a per-row delivery stamp
Every decided send (page, reply, auto-send) records `send_returned_ts` (when the send call returned: on WhatsApp's delivery receipt when `send_state` is `delivered`) and `send_ms`, copied into the transcript row. `latency_report`
gains a **decision -> delivered** leg that counts legacy rows without a stamp and un-receipted sends instead of estimating them.

## 5. R7 send-path guard
`tests/test_review_timeout.py` names every function that may call `_send_once`. `review_act` and `_notify_reviewers` no longer send themselves: the human-decision participant send moved, unchanged, into `_decide_and_send`;
the reviewer push into `_push_card`; `review_reply_and_act` and its `tell` message **reviewers only** (proved by AST). The two stale names were removed from the allowlist, not kept.

## Not done, by decision
Immediate send for fixed statements (founder: not now; build the evidence first). GPU snapshots (founder: no). `eval_272`-class (kept queued).

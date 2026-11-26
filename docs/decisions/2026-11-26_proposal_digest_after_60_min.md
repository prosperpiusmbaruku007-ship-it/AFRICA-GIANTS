# PROPOSAL (not built — awaiting approval) — the hourly digest waits until an item has waited ≥ 60 min
2026-11-26. `chike-whatsapp` change (a separate R16 window from `chike-inference`). **Nothing is built or deployed.**

## Evidence (controlled test, 2026-11-26; `eval/results/` artifact appended with the final count)
The first digest fired **10 seconds after the last first-card**: reviewer-recipient send ledger 07:14:16, :26, :30, :41 (four cards, store `first_notified_at` 07:14:19–07:14:43) and a fifth at **07:14:53**; the digest claim key `digest_claim_498799` = 07:14:53 and `digest_ts` = 07:14:55. So today's rule ("send a digest while ≥ 1 item is pending, once per hour, none at 0") sends a *summary of the cards the reviewer received seconds earlier*. That is noise, as you read it. (Final confirmation against the full 2-hour count is in the controlled-test report.)

## The rule
Send a digest only when **at least one pending item has waited ≥ 60 minutes since its card** (`first_notified_at`, falling back to `ts_held`), **at most once per rolling hour**, and **never at 0 pending**. The digest still lists every pending item (count, oldest age, links); only the *trigger* changes.
Code: `core.digest_candidates` stays; add `core.digest_trigger(items, now, min_wait_s=3600)`; the sweep sends only when the trigger holds AND the existing hour-bucket claim and `digest_due` pass. One tunable `DIGEST_MIN_WAIT_S` (default 3600) goes in `deploy_tunables.json`.

## Plants (to write with the build; each must FAIL against today's code)
1. **No digest in the first 59 minutes** of an unreviewed queue (simulated minute-by-minute with the real sweep, fake clock) — today: one at minute 1. *Fails today.*
2. **An item decided at minute 50 never produces a digest.** *Fails today (digest at minute 1).*
3. **Positive control:** an item still pending at minute 61 produces exactly one digest, within the next sweep.
4. **At most once per hour:** 12 simulated hours × 20 unreviewed items → ≤ 12 digests (11 expected: the first at ~minute 60), and three overlapping sweeps at minute 61 send one.
5. **A fresh item next to an old one:** an item 5 min old and one 90 min old → a digest is sent (triggered by the old one) and lists both.
6. **0 pending → no digest** (existing test stays).
7. **Fail-closed:** an item with neither `first_notified_at` nor a parseable `ts_held` does NOT trigger a digest.
8. **The reminder is unaffected:** the one 7-minute reminder per item still goes (it is a separate rule).

## Effect on the controlled test, for the record
Today's code in a 2 h test: digests at ~07:15, ~08:15, ~09:15 (3). Proposed: ~08:15 and ~09:15 (2), i.e. one fewer reviewer push per burst, and none for a draft the reviewer clears within the hour.

## Not proposed
No change to the 60/h and 20/h send ceilings, the one-reminder cap, or the 15-minute holding message.

# Notes for a WhatsApp Business API migration (design input, 2026-11-26; nothing built)

The bridge is an unofficial session (Baileys, one leased socket). If the pilot grows past what that tolerates, these are the code and design consequences.
Pricing, messaging tiers and Meta business-verification requirements are NOT verified here and must be read from Meta's current documentation first.

## Code
- A `cloud` value for the existing `TRANSPORT` setting, beside `bridge` and `wappfly`: a send function against the Cloud API and a new inbound
  webhook (verification handshake, `X-Hub-Signature-256` check against the app secret, and a new parser: the payload shape differs from the Wappfly
  shape the bridge imitates).
- Delivery receipts arrive as separate status webhooks, replacing the bridge's inline wait. `send_state` / `pending_receipt` / the pending-rows
  reconciler map onto the status events.
- Identity becomes a plain phone id: the `@lid` handling can go. The ceilings stay the hard brake; bridge pacing is not needed.
- New secrets (access token, app secret, verify token, phone-number id) enter the tunables gate and the `/health` key-presence check.
- Run both transports side by side: a new number for new cohorts on `cloud` while the existing number stays on the bridge.

## The 24-hour window changes the reviewer channel
Free-text replies are only allowed within 24 h of the user's last message. Participant-facing messages mostly stay inside it (inbound-first onboarding,
the disclosure, the welcome, acks, the daily-limit notice, holding messages). **A supervised answer approved more than 24 h after the question would
need an approved template.** Reviewer cards and digests are business-initiated, so they would need templates too (with the link as a variable), or the
reviewer would have to message the number daily to keep the window open, which is fragile.

### Option: a web review page as the reviewer channel (founder's note)
Move reviewers off WhatsApp entirely:
- Reviewers get a signed "my queue" page (the per-draft `/d` page and HMAC token model already exist; add a list view bound to the reviewer's handle).
- Attention comes from a non-WhatsApp channel (email / web push), so no template cost and no window.
- WhatsApp is then used only for participants.
- The R7 supervised-cohort conditions must survive the move unchanged: claim-before-act, per-reviewer attribution on every action, no auto-send on
  timeout, and the disclosure. The page is read-write only through the claimed, signed flow; the admin overview stays read-only.
- Cost: a reviewer-facing UI, an alert channel with its own dead-man check, and a decision on how a reviewer proves identity beyond a signed link.

## Also required
A business-verified account, a number that is not simultaneously in use on the consumer app, opt-in handling, and a re-read of the template rules before any template is relied on.

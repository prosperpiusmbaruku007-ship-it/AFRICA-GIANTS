# PROPOSAL (not built, not deployed) — `chike-inference` `scaledown_window` 300 s → 600 s
2026-11-26. Queued for the next `chike-inference` window. **No always-warm** (`min_containers` stays unset).

## What changes
`chike-inference/modal_app.py` line 250: `scaledown_window=300` → `600`. One line; config-only, so R16 applies in full (pre-flight, `app stop`, deploy, live check that exercises it, negative case). CLAUDE.md already ties "the GPU scaledown at 300" to a documented discipline (modal_app.py ~line 969 comment): that comment needs to move with the number.

## Why
The supervised pilot's latency is dominated by a cold GPU start (measured 64 s, 92.5 s, up to 216 s, once ~20 min on 2026-11-11). A warm container serves a follow-up in ~10 s (warm p90 9.8 s over 48 questions). A conversation whose next message lands 5–10 min after the last currently pays a cold start; with 600 s it would not.

## Current Modal pricing (fetched 2026-11-26 from modal.com/pricing; page text, per second)
| resource | per second | per hour |
|---|---|---|
| **L4** | $0.000222 | $0.799 |
| **T4** | $0.000164 | $0.590 |
| CPU | $0.0000131 / physical core (min 0.125 core/container) | |
| Memory | $0.00000222 / GiB (min 128 MiB/container) | |
Starter plan: $0 + compute, **$30/month free credits**. The app's GPU list is `T4,L4` (Modal chooses; CHIKE_GPU overrides only at deploy), so both are priced. **CPU and memory are billed on top and I have NOT measured the container's reserved memory** (modal_app.py sets neither), so every figure below is GPU-only and a lower bound; an 8B model's host-memory footprint could add on the order of 10–20% at the T4 rate (unmeasured).

## Cost
- **Extra cost of the change = one extra 300 s idle tail per distinct warm period** (a burst of messages whose gaps are all < the window), because the container now waits 300 s longer after its last request before scaling down.
  - **Per warm period: T4 +$0.049, L4 +$0.067** (300 s × rate).
- **Offset (not netted, reported separately):** two periods separated by a 5–10 min gap merge into one, which avoids one cold start. Cold-start GPU time is billed: 64–216 s = $0.011–$0.035 (T4) / $0.014–$0.048 (L4), plus the participant waiting. So the extension is cost-neutral-or-worse in money and better in latency for those merges.
- **Cost per conversation** (a conversation = one warm period): +$0.05–$0.07 worst case, when nothing follows it inside the extra five minutes.
- **Worst-case monthly:**
  - *Bounded by the number of warm periods.* Assumption (mine, not measured): a 15-person cohort, ≤ 3 conversations per person per day, every one isolated → 45/day × 30 = 1,350 periods → **≤ $66 (T4) / ≤ $90 (L4) extra per month**, GPU-only. Realistic pilot traffic so far is a handful per day (transcript store: 0 real-participant rows), i.e. **a few dollars**.
  - *Hard ceiling = always-warm,* reached only if a request arrives at least every 10 minutes for the whole month: **30 days × 24 h = $425 (T4) / $575 (L4)**. That is the figure "no always-warm" exists to avoid; it needs ≥ 4,320 evenly spaced requests a month to approach.
  - Free credits ($30/month) would absorb the realistic case but not the 1,350-period bound.

## Decision asked
Approve 300 → 600 s, or keep 300 and instead rely on the supervised flow's holding message. Unchanged either way: no `min_containers`, no canary.

## If approved: verification (R16)
Pre-flight → `app stop chike-inference --yes` → deploy → `/health` `build_matches: true`; send two questions 7 minutes apart and confirm the second is warm (reply < 15 s, no cold-start log line); negative: a question after > 10 min idle is cold again.

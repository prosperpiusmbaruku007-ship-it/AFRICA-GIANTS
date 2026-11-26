# CPU split for model-free routes: considered, NOT built (agreed 2026-11-26)

Proposal: run routing, fixed statements and model-free engines in a CPU function so they never wake the GPU.

Measured with the offline arrival model (`eval/controls/scale_arrival_model_2026_11_26.py`, assumptions: 3 questions per participant per day, evening burst, T4 at $0.59/h, 600 s
scaledown, 90 s cold load). Only 18 of the 400 gate questions (4.5%) are model-free; the compute path writes a model body, so it cannot skip the GPU.

| model-free share | GPU saving per day at 10 / 25 / 50 participants |
|---|---|
| 4.5% (measured on the gate set) | $0.07 / $0.17 / $0.21 |
| 25% (upper bound: would need compute-path answers to be model-free too, which they are not) | $0.68 / $1.12 / $1.32 |

CPU cost is negligible ($0.0000131 per core-second). The latency gain is invisible while supervised, because every reply waits for a reviewer
regardless; the only visible effect is an earlier card.

Cost of building it: `detect_intent`, the fixed statements and the engines move into a CPU image (dual-file parity with the GPU class), a new R16 stop-first
window, a build-label check for two tiers, and a parity test proving both paths answer identically. Not worth it at this size.

Revisit if the measured model-free share of real pilot traffic is far above 4.5%, or if unsupervised traffic ever makes cold-start latency visible to
participants.

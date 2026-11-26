# PROPOSAL (not built) — route recall: how many questions that an engine could answer actually reach one
2026-11-26. **Labelling caveat: the request referred to "R1/R2" and the definitions were lost with the crashed session. These two options are MY reading, named R1 and R2 here only so you can say "R2" and mean this; replace them if yours differ.**

## The problem, with the evidence we have
`detect_intent` fires on questions that contain a figure or a technical term; a user asking what a rate *is* has no number to give (R31, fifth instance). On 2026-10-09 **0 of 12** confirmed defects reached any engine though engines held the answers for two; the statement route fixed rate/method/applicability asks that carry no figure, but the same bias exists wherever a route's gate needs a signal the natural phrasing does not contain.
Current pilot evidence (`answer_path_summary --include-test`, 2026-11-26, 42 messages, 18 untraced): of 24 traced, **fact_model 9**, engine 5, fixed_statement 5, ooc 4, clarification 1. A fact_model row is only a *miss* if an engine exists for its subject; the summary cannot say which.

## R1 — MEASURE FIRST (read-only; no behaviour change)
Build a recall census: for every question in the held corpora and every pilot question that went to `fact`, ask "does an engine or fixed statement exist for this subject?" (list the subjects from `chike/routing.py` computation types) and "did `detect_intent` return it?". Output: per-engine recall on **natural phrasing only** (R31 step 3: no technical term, no keyword argument), plus the rows, read by hand (the judge cannot see wrong-base, CLAUDE.md R12b caveat). Population named per R22: the rows that *needed* the engine, not the rows already answered right. Cost: no deploy. Deliverable: a ranked list of engines by missed volume.

## R2 — WIDEN THE CUES (behaviour change, per engine, only after R1)
For the top engine(s) by miss count: add narrow, verb- or context-qualified cues (R17 step 4), sweep over all corpora **and** authored in-scope probes containing the risky words, include probes that must come back CLEAN, then R12c's enumerated blast radius with unchanged-route controls (R24b: compare prompts, not cross-host replies). Ship in a `chike-inference` window with the live check R16 requires. Risk named: a wider cue is also a wider net; 3 of 3 OOC list widenings collided with in-scope vocabulary (R17).

## Recommendation
R1 only now, then decide R2 per engine on the measured recall. Do not widen on the strength of 9 fact-path rows. Needs no deploy and cannot collide with the held `chike-inference` window items (rent R44 strip; scaledown).

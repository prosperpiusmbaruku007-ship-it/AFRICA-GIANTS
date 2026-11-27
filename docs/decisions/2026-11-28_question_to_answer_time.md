# Question-to-answer time for wave 1 (founder priority, 2026-11-28)

Status: **A built, committed locally, not pushed or deployed. B, C and the immediate-send question are proposals/evidence for the founder's decision.** Every number below is reproducible from a committed harness (`eval/controls/measure_latency_legs_2026_11_28.py` -> `eval/results/latency_legs_2026_11_28.json`; `eval/controls/fs_route_evidence_2026_11_28.py` -> `eval/results/fs_route_evidence_2026_11_28.json`).

## 1. What was measured (Step 1) and what it says

Population: the 41 stored review items and 46 stored question rows, **every one a test or founder number** (TEST-CLASSIFY-CONFIGURED-1 is still queued, so excluding "test" would report nothing). Only questions where the question row and the review item join exactly get a leg: **14 joined, 7 unjoined (counted, no number guessed), 7 auto-sent (excluded: a 15-minute policy, not reviewer speed)**. Small n: read these as orders of magnitude, not rates.

| leg (seconds) | all (n=14) p50 / p90 | cold start (n=7) p50 / p90 | warm (n=7) p50 / p90 |
|---|---|---|---|
| model call | 33.3 / 59.3 | 54.0 / 125.6 | 0.5 / 11.2 |
| hold + notify reviewers | 3.4 / 15.7 | 2.2 / 10.2 | 5.2 / 19.5 |
| question -> draft ready | 38.6 / 72.2 | 57.3 / 136.9 | 9.9 / 31.4 |
| **draft -> reviewer decision** | **746 / 5,025** | 173 / 1,336 | 1,367 / 35,326 |
| question -> decision | 865 / 5,048 | 225 / 1,388 | 1,399 / 35,346 |

**The headline is not the GPU.** The median question waits about **12 minutes for a human**; the draft itself is ready in about 39 seconds. A cold start adds roughly **50 s** and touches **16 of 46 stored questions (35%)**. So pre-warming (A) is worth building and is cheap, but it moves a ~14-minute median by under a minute. **The reviewer leg is where first impressions are decided**, and the only lever that removes it for a class of questions is the immediate-send proposal (section 5).

**Not measured, and said so in the report itself:** decision -> delivered. No per-row delivery stamp is stored, and the bridge ledger's `receipt_ts` is the *latest* receipt (a read receipt hours later: p50 9,174 s), so it cannot stand in. One direct observation: the FUTA test's last send to receipt was 6 s. Adding a delivery stamp to the stored row is a small change worth making (queued).

**Correction to a number I gave earlier in this session.** I first reported the hold+notify leg as "~19 s p50". That pooled two eras. By date and build the gap was ~2 s through mid-November, **~34 s on 2026-11-25 (n=20, a batch of scripted questions)** and **13-31 s on 2026-11-26**, which coincides with the bridge send pacing (a global 1 s minimum gap plus 0-2 s jitter between *any* two sends, `chike-whatsapp/bridge/pacer.mjs`). Likely mechanism, not proven: every ack, reviewer push and answer takes a turn of ~2 s, and each reviewer push then waits for WhatsApp's delivery receipt (`_send_once_bridge` returns only on receipt; `_notify_reviewers` awaits each reviewer in turn). On the latest single questions the gap is ~10-13 s. It matters when several drafts overlap, which is exactly what a wave looks like.

## 2. A. Pre-warm on greeting (built)

A greeting spawns a cheap existing GPU-app method (`served_index_identity`: starts a container, runs `load_model`, no generation, nothing sent, output unused) from a **thread started before the first-contact send**, so it never delays or fails the greeting. Pure policy in `handler_core`; wiring in `modal_whatsapp`.
- **Idempotent:** a model call or warm-up in the last 300 s suppresses it (every real model call stamps the container warm).
- **Capped:** one per sender per 900 s window; 12 per hour across all senders (atomic `put(skip_if_exists)` claims).
- **Off unless asked for:** `PREWARM_ENABLED` must be `1/true/yes/on`; garbage falls back to the cap, never to "unlimited"; a store that cannot record the claim means no warm-up (no uncounted spend).
- **Needs no GPU-app deploy**, only a `chike-whatsapp` window. `/health` gains a `prewarm` block; the committed tunables carry it, so the pre-flight's live-vs-file gate will refuse until deployed and needs a recorded `CHIKE_TUNABLES_OVERRIDE` for that one deploy.
- **Tests:** 22, with plants (a blocking spawn must not delay the greeting; no cooldown; no cap; no warm stamp; not settled on every return path). One of my own plants was vacuous at first and was fixed.

**Cost per warm-up** (GPU only; CPU and memory are billed separately and small; rates from [Modal pricing](https://modal.com/pricing): T4 $0.000164/s, L4 $0.000222/s; our class tries T4 then L4):
- Warm-up that **no question follows**: cold start (measured cold model call p50 54 s) + the 600 s `scaledown_window` idle = ~654 s, so **~$0.11 on T4, ~$0.15 on L4**.
- Warm-up that **a question follows**: ~$0 incremental (that question would have started the container anyway).
- Already warm: skipped (no call). Worst case is bounded by the cap and by containers not stacking: **at most one container's continuous warmth, ~$0.59/h (T4) or ~$0.80/h (L4)**.

## 3. B. The review card and the exact approve action (proposal, nothing changed)

**What a reviewer receives today** (`handler_core.notification_text`): one WhatsApp push with the reviewer's name, the participant's last four digits, **SWALI**, **RASIMU (the whole draft)**, **HESABU YA MFUMO** (the engine's working, or an explicit "none: from the model and memory only"), **VIGEZO VILIVYOTUMIKA** (the facts served, truncated, capped), loud warnings first (empty evidence, duplicates, unsupported figures, fallback), then **one link**.
**The exact approve action today:** tap the link -> the page loads and its JavaScript POSTs a *claim* (locks the draft to you) -> tap **Tuma** (a second POST). Edit and withhold need a reason. Nothing acts on a GET, because WhatsApp fetches links to build previews. **That is two taps plus a page load and a claim round-trip (a possible cold start of the claim endpoint).**

Proposals, smallest first:
1. **Speed the push (no semantic change).** Notify all reviewers in parallel and do not wait for the delivery receipt on reviewer pushes (the bridge's acceptance is enough; a failure already re-notifies). Expected gain 3-13 s per question on the latest builds, more when drafts overlap. Honest size: **small next to a 12-minute reviewer wait.** Low risk, measurable with the already-stored `first_notified_at`.
2. **One-gesture approve by WhatsApp reply (changes approval semantics: yours to decide).** The push already shows the whole draft, so a reply can be a read-then-approve. A safe form needs: the reply must be a WhatsApp *quoted reply to that exact push* (the quoted message id maps it to one draft; an unquoted "ok" is ignored with a help line, never applied to "the latest"); exact tokens only; the same claim lock and the same reviewer attribution (number -> handle); unknown quoted id fails closed; edit and withhold stay on the page. **Risks to weigh:** an accidental tap on the wrong quoted message; a reviewer approving without scrolling (the page's two-tap friction is also a pause); the claim lock must be taken by the reply. **R7 reading:** the condition is "a human reads every model draft before it is sent"; reply-approve keeps that only if the pushed text is the full draft (it is). **This changes the reviewer-side semantics the 2026-10-10 reading was written around, so it should be recorded as an amendment if adopted.**
3. **Do not build** a GET-based one-tap link: a preview crawler would fire it.

## 4. C. Cutting cold start itself: Modal memory / GPU snapshots (research only; no build)

Source: Modal's [Memory Snapshots guide](https://modal.com/docs/guide/memory-snapshots) and [GPU snapshot example](https://modal.com/docs/examples/gpu_snapshot), read in full on 2026-11-28.
- **How:** `@app.cls(enable_memory_snapshot=True, experimental_options={"enable_gpu_snapshot": True})` with `@modal.enter(snap=True)` for the load step; deployed apps only. Redeploys invalidate snapshots; new ones are created lazily, and full coverage takes about **2-3 snapshots per GPU type** (we try T4 then L4), with extra latency on the invocations that create them. Modal also recaptures periodically.
- **Stated gains:** "3-10x" for initialization-heavy functions (vendor claim); a CPU-only split-enter example went ~6 s -> ~2 s on a sentence-transformers model. **No figure for an 8B quantized LLM.**
- **Why it may not help us:** the guide says snapshots **do not speed loading weights from storage**; if most init time is weight loading they "generally will not help and may worsen cold start". Our cold start is dominated by exactly that (8B base + adapter + e5 embedder, p50 54 s).
- **Not covered by the docs, and load-bearing for us:** **bitsandbytes / 4-bit quantized models**, and **what happens when a restore fails**. GPU snapshots are labelled **alpha**; the docs say to "test carefully before using in production". Known issues: `torch.compile` can break snapshot creation; multi-GPU is generally incompatible; a deleted Volume file used at restore causes restore failures.
- **Expected gain:** unknown, possibly zero. **Risk:** an alpha feature under the correctness-critical fact path, with undefined restore-failure behaviour. **Recommendation: do not build in production.** If wanted, an isolated copy of the GPU app (own name, own Volume read-only) with the real loader, measuring cold start before and after on both GPU types, costs roughly one afternoon and a few dollars. The cheaper first step is already built (A), and the existing `_coldstart` field on `served_index_identity` records where the container's start-up time went; reading it costs one warm-up (~$0.11-0.15).

## 5. The immediate-send proposal for fixed-statement routes: the evidence (your decision)

**What the record contains.**
- **44 fixed-statement routes** (43 in the topic table + the dynamic sector-wage route). Across 15,191 distinct question strings in every committed corpus, **944 route to one**.
- **There is no real-traffic evidence for any route.** The archived review items do not carry their route (only the 5 hot items do, and 4 of those are `engine:rent_wht`), so per-route approved/edited/withheld counts from participants **do not exist**. Everything below is authored probes, sweeps and the gate.
- **The one authoritatively-keyed population is the 400-question gate: 26 rows route to a fixed statement.** I read each question against its route's statement. **0 are clearly the wrong topic. Two are partial answers:** `eval_272` ("analipwa euro 400... PAYE ... mabano ya Tanzania") gets the TZS band table with no word about the foreign currency, and the user asked for a computed figure; `eval_301` ("payroll TZS 7,000,000, je tunatakiwa kujisajili BRELA?") gets the three-forms statement, which says no payroll threshold exists but never says "yes, register". *(I first doubted `eval_233`; its statement does state the 10-employee SDL threshold, so that route is right.)*
- **Per-route foreign-row counts are a ceiling, not a misroute count** (most are training paraphrases of the same topic). The large ones (`gn487a_penalties` 62, `vat_withholding_rates` 58, `brela_annual_return_deadline` 56, `sdl_base` 55, `paye_base` 55) are where an adjudicated sample is most needed.
- **Routes the evidence cannot support at all:** `vat_time_of_supply` routes **zero rows anywhere**; `notice`, `severance`, `overtime`, `annual_leave` (four of the original five) have **no gate row** and only 1-9 foreign rows each.
- **Our own questions:** routing the 46 stored question texts through today's router sends **11 (24%)** to a fixed statement (`business_licence_validity` 2, `vat_medicines` 2, `paye_residency` 2, `director_fees_wht` 2, `notice` 1, `annual_leave` 1, `paye_rate` 1). **Those are questions we wrote, on topics we built routes for (R22): the real participant mix is unknown.**
- **Build-time history that supports the vetoes:** the premise veto on notice/severance/overtime/annual-leave exists because of the `eval_211` wrong-topic class; the sector-wage vetoes come from measured diversions (`wage_fix_options_2026_11_22.json`); the annual-return route is restricted to its own ask because its global-ask diversions were definitions, late-payment amounts and strike-off questions.

**What the proposal gives:** it removes the reviewer leg (p50 ~12 min, p90 ~84 min on our small sample) for the share of questions that take these routes. **What it costs:** a misroute or a stale statement reaches the participant **before anyone has read it** ("sent - reply to send a correction" means the participant may already have acted). `business_licence_validity` is the standing reminder that a `CONFIRMED` statement can be wrong for months (R29), and a fixed statement is a locked fact with a larger blast radius.

**R7 consequence.** This **widens what may send unreviewed**, which the 2026-11-13 amendment and void-list item 2c (2026-11-16, `engine:fixed_statement` named in `AUTOSEND_EXCLUDED_ENGINE_ROUTES`) currently forbid. If adopted it must be recorded as a founder amendment to the R7 supervised-cohort reading, with its conditions, not as a quiet edit.

**My recommendation (the decision is yours).** Do not adopt it on this evidence. Adopt a **narrow, evidence-gated version** only after: (1) archived review items carry their route (queued; a prerequisite), so real per-route outcomes accumulate; (2) a hand-adjudicated sample per route (the five large ones first) with premise, negation and foreign-currency probes (`eval_272`'s class); (3) each allowlisted route's statement has its primary-source read recorded in the locked fact (`verified_by`, edition asserted). Start with the routes whose statements are narrowest and best verified, not with all 44. In the meantime, reply-approve (section 3, proposal 2) gives most of the speed with the human still in the loop.

## 6. Queued by this work (not built)
- Store the route on archived review items (prerequisite for any per-route evidence).
- Store a per-row delivery stamp (decision -> delivered is currently unmeasured).
- Speed the reviewer push (proposal 1).
- `eval_272`-class: a fixed statement that does not note a foreign-currency premise.

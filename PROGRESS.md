# Africa Giants — Project Progress

Last updated: 2026-08-22

---

# 🚨 THE PILOT'S SAFE-ON-UNCOVERED-TOPICS PRECONDITION IS UNMET — BUT NOT FOR THE REASON THIS ENTRY FIRST GAVE (2026-08-22, corrected same day)

> **CORRECTION APPLIED TO THIS HEADLINE — read this before the rest of the entry.** The original
> title said *"THERE IS NO MEASURED ROUTE TO 'SINA UHAKIKA' OF ANY KIND."* **That claim is
> disproved by the v16 re-measurement** (§8 re-run, `eval/results/ss8_forced_facts_v16_2026_08_22.json`):
> `nat_24`, with all three correct facts forced into context, returned exactly *"Thibitisha na TRA
> (tra.go.tz)"* — a bare deferral, the project's own referral formula. Not a classified refusal
> (`refused: false`), but as user-visible behaviour it is a deferral, not a confident wrong answer.
> A route exists; it is unreliable and unmeasured, which is a different and smaller problem than
> "none exists."
>
> **The precondition is still unmet**, on the narrower and better-evidenced ground below:
> `nat_23` produced a **confidently incomplete** answer — correct NSSF arithmetic, an entire second
> levy (SDL) missing, no signal at all that half the question went unanswered. No retrieval-side
> floor can catch that, because nothing about retrieval was uncertain. **But the mechanism is now
> named: it is a routing fan-out miss, not a general generation ceiling** — and the very check this
> entry proposes below ("does the reply address every part of a multi-part question") would catch
> it. Three of §8's eight rows are routing misses, not generation failures.
>
> Read the two claims that follow with that correction applied: **the floor designs really are all
> dead or unbuilt (items 1–3, unaffected), and the fourth point below overstates its case.**

**This is the single most consequential open item in the project right now — more consequential
than any retrieval-ranking work — and it is stated here as its own headline so it can be found
without reading an ADR.**

The 2026-08-16 assessment set an explicit precondition for a safe pilot: *"a floor makes us safe
on questions we can't answer, but answering them is better than refusing them... the floor still
ships before any pilot."* Three independent, separately-dated attempts to build that floor have
now all failed or gone unbuilt, and the most recent one closes the door on the entire APPROACH,
not just one design:

1. **An absolute similarity-score threshold** (scoped and rejected 2026-08-16): the score
   distribution makes it impossible — the correct fact for one question scores *lower* than the
   irrelevant top-1 of another, so any threshold that excludes wrong facts also excludes right
   ones.
2. **A margin (top-1 vs top-2 separation) threshold** (measured 2026-08-22,
   `scratch/item5b_margin_guard.py`): **it inverts, not just fails to separate.** `nat_32`, correct
   today, has the single smallest margin of all 21 fact-path questions tested, while three
   known-buried (wrong) rows score *larger* margins than every currently-correct row. A margin
   floor would flag the wrong rows as the trustworthy ones.
3. **A re-ranked-index confidence signal** — the third named design — remains unbuilt and
   untested.

**And now a fourth problem, discovered today (§8 below) — ⚠️ RESTATED AFTER THE v16 RE-RUN, which
narrowed it: a retrieval-confidence signal, however perfect, cannot catch a failure class that was
measured directly.** `nat_23` and `nat_24` had the exact correct fact(s) placed directly into the
model's context — not just retrieved with a good score, but forced in, guaranteeing maximum
possible retrieval confidence by construction — and neither produced a correct answer. **The
original wording here said both failed with "no hedge, no 'sijui,' no visible sign of uncertainty
at all." Measured on v16 that is true of `nat_23` only: `nat_24` returned a bare "Thibitisha na
TRA" deferral.** The surviving case is `nat_23`'s **confident incompleteness** — correct arithmetic
on one levy, a second levy silently absent. This is not a gap in
today's floor designs; it is a proof that the entire *category* of retrieval-side floor cannot
address this failure mode, because the defect is not "the system wasn't sure which fact to use" —
it is "the system had the right fact and still didn't produce a correct answer." No signal computed
from retrieval confidence, however well-built, can distinguish that case from a genuinely correct
answer.

**Plain statement of where this leaves the pilot precondition: it is unmet, and no work currently
scoped anywhere in this project closes it.** A safety net for "refuse when we don't know" would
need a signal from the *generation* side — e.g. a post-hoc check that a reply addresses every part
of a multi-part question, or a self-consistency check on the answer itself — not a better retrieval
score. No such mechanism exists or is scoped. Until one does, the 2026-08-16 assessment's own
stated condition for a safe pilot on uncovered topics has not been satisfied. **The v16 re-run
sharpens this rather than softening it: the "addresses every part of a multi-part question" check
named above is now the specific thing that would have caught the one surviving case (`nat_23`), so
the missing mechanism has a concrete shape instead of being a general worry.**

## Evidence status after the v16 re-measurement (settled — no longer provisional)

The forced-fact harness behind this headline was uncommitted and its results were marked
provisional. **They have now been re-measured on the live v16 pipeline with a committed instrument**
(`eval/results/ss8_forced_facts_v16_2026_08_22.json`). Three outcomes for this entry:

- **Overturned:** the "no route to a refusal of any kind" claim. `nat_24` deferred — see the
  correction box at the top.
- **Confirmed:** `nat_23` fails with the right facts in context and gives no uncertainty signal, so
  a retrieval-side floor still cannot catch it. The precondition remains unmet.
- **Corrected mechanism:** the earlier assumption that both rows "go down the same pooled-fact
  generation on either pipeline" was itself wrong. Measured, **`nat_23` routed to `compute`** — the
  NSSF rules engine fired and computed correctly, and SDL was dropped. The failure is a routing
  fan-out miss, not the generation ceiling this entry originally implied.

**And the pipeline that owns the SDL/NSSF/WCF engines is already in production** — `chike_config.json`
sets `"pipeline": "v16"` and `modal_app.py` branches into `Orchestrator.answer()`. There is no
pending cutover that closes any of this.

Full technical detail on both threads (margin inversion; the forced-fact generation-failure
finding) in the entry immediately below and `docs/decisions/0002-retrieval-structural-scoping.md`
§5(c) and §8.

---

# 🧾 FIVE INSTANCES OF ONE PATTERN: A RESULT CARRIED ON SOMETHING NOBODY COULD RE-DERIVE — NOW A RULE (R18, 2026-08-22)

**Named plainly because it has now happened five times, and the fifth was about to drive a build
decision.** Every one of these is the same shape: a claim entered the record, was believed, and was
then used — while the thing that produced it could not be re-read by anyone, including the person
who wrote it.

| # | instance | what carried the result | how it surfaced |
|---|---|---|---|
| 1 | **Stale pins** (2026-08-17) | a human verdict pinned to an index *row number* | the index moved; the pin kept asserting the old verdict silently |
| 2 | **Drift check's predecessor** (2026-08-17) | v2's manual, non-re-runnable fact-index pass; v3 then only re-checked v2's own flags | building the real check found **20 more keys** on its first run — keys v2 had got right by accident and nobody had ever adjudicated |
| 3 | **Interleave premise** (2026-08-22) | an instrument that measured one fact's rank, read as certifying the whole injected set | the guarantee held perfectly and a live answer broke anyway |
| 4 | **v15/v16 claim** (2026-08-22) | a grep against `chike.pipeline_v15.answer` — a path the config selector no longer chooses | caught mid-write-up, after it had already reached an ADR and a headline |
| 5 | **SS8 forced-fact table** (2026-08-22) | **nothing — the harness was deployed, used and deleted without ever being committed** | `git log -S'run_forced_facts' --all` returns nothing, on any branch |

**Instance 5 is the worst of the five and the reason this is now a rule rather than an
observation.** In 1–4 something re-derivable existed: a row could be re-checked, a grep re-run, a
rank re-measured. In 5 **the artifact does not exist at all**, and the instrument's own description
says it ran the non-live arm — so §8's split, the arithmetic-clustering pattern drawn from it, and
§2's revised yield (which was about to justify building §2) all rest on an instrument no one can
inspect, measuring a pipeline that may not be production.

**The rule, now `CLAUDE.md` R18:** *any harness whose output enters the record gets committed
before its result is written up* — harness, fixture, and raw artifact. It costs one `git add`. It
is the one measure that would have prevented all five. A temporary debug method is not an
exception: commit it before the run and remove it in a follow-up commit, so the exact instrument
sits in history at a named SHA.

**And provisionality is contagious.** A result whose harness was never committed is provisional,
and so is everything downstream that cites it — yield estimates, priority orderings, build
decisions. §8 is marked provisional in full below, and §2 does not start until §8 is re-measured on
the live v16 pipeline.

---

# 🧩 PRESENCE-NOT-CONCLUSION, NOW A THREE-INSTANCE SET AT THREE DIFFERENT LAYERS (2026-08-22)

**The same error, three times, in three places that do not look alike.** Each check confirmed that
**something was present** and was **structurally incapable of establishing which thing it was**, or
what followed from it.

| # | layer | the check | what it confirmed | what it could not see |
|---|---|---|---|---|
| 1 | **ship criterion** | interleave's zero-dilution instrument | the target fact kept its rank in all 8 rows | that the **other two injected slots changed for all 8**, and one row flipped to a wrong live answer. It measured one fact's presence, not the answer's stability |
| 2 | **regen guard, keyword** | `nat_27`: `'18%' in fact_text` | the string `18%` was in the top-3 | that it was in **[64], the withholding-formula fact** — not [13], the standard-rate fact it names. **Six** index facts contain `18%` |
| 3 | **regen guard, displacement** | `VAT registration threshold`: `'200,000,000' in fact_text` | the string `200,000,000` was in the top-3 | **that the displacement it was written to catch was happening.** [57], the EFD fact that mentions 200M only as a contrast, sits at **rank 1** — above [145], the fact actually asked for. The anchor matched [15], [57] and [145] alike |

**Instance 3 is the purest form yet**, and it is worth stating exactly: *a guard whose entire
purpose was to detect one fact displacing another passed while that displacement was occurring,
because its anchor matched the displacer and the displaced equally well.* It could not fail. It had
never been able to fail.

**The generalisation, across all three:** a check that tests for the PRESENCE OF A STRING OR AN ITEM
cannot tell you WHICH item carried it, and therefore cannot support a conclusion about identity,
ranking, or consequence. **Presence is evidence of presence. Nothing else.** To conclude anything
further the check must be anchored to something that can only be true of the intended thing —
which is exactly the property `NEVER 14%` has and `18%` does not, and the property an answer-level
regression check has and a rank check does not.

**Where this is already enforced:** the §5(d) standing bar (answer-level, not rank), the R18
committed-harness rule, and now the regen gate's runtime anchor-uniqueness assertion.

---

# 🕳️ THE DEAD-ANCHOR CLASS: A GREEN GATE CAN CONTAIN CHECKS THAT NEVER FIRE (2026-08-22)

**Three regen anchors matched ZERO facts.** `elfu 22`, `28 julai`, `efd threshold tzs 11m` could
never have fired, in any run, ever. Each was concealed by a sibling anchor in the same guard that
always passed — so the guard was green, and two thirds of what it claimed to check was inert.

**Stated as a general risk, not a fixed fault: a passing gate carries no information about how much
of it is actually running.** Green means "nothing that ran, failed". It does not mean anything ran.

**This is the census test's blind spot from the other direction.**
`test_every_cue_with_a_person_form_has_its_concord_counterpart` derived its cases **from existing
members**, so a class with **zero** members produced zero cases and passed silently — which is how
class C survived the 2026-08-15 closure at 0% coverage. Same failure, mirrored: there, the
*generator* was empty; here, the *matcher* was.

## So I looked for the shape elsewhere — census of the whole codebase

`eval/index_quality/scan_inert_checks.py` → `eval/results/inert_check_census.json`. AST scan over
`tests/`, `scripts/`, `chike/` (196 files) for three mechanically-detectable inert-capable shapes.

| shape | found | inert right now |
|---|---|---|
| `VACUOUS_LOOP` — `for x in COLL: assert …` with nothing establishing `COLL` is non-empty | **31** | **0** (6 resolve to non-empty literals; **25 unresolvable statically**) |
| `EMPTY_PARAMS` — `@parametrize` over a runtime-built name | **38** | **0** — pytest collection reports **no** "empty parameter set" across 1230 collected tests |
| `ANY_OVER_ALTS` — `assert any(... for kw in [a, b, c])`, the exact dead-anchor shape | **0** | — |

**Result: 69 structures with the dead-anchor property; none currently silent.** The suite is not
lying to us today. Spot-checked the highest-risk cluster by hand (`test_instruction_dataset.py`,
where CLAUDE.md's "Tier 1A — 0 pairs written" made an empty-corpus loop plausible): its loops
iterate an imported constant and a file the test itself writes. Fine.

**The residual risk is the 25 unresolvable loops** — they iterate a call or comprehension, so
nothing static can say whether they will still have members after the next data change. **The
one-line fix that converts "can go quiet" into "fails loudly": assert the collection is non-empty
before looping.** Not applied — 25 edits across the suite is its own piece of work, and none is
currently broken. **On the board, with the census as its worklist.**

---

# ✅ THE REGEN GATE NOW CHECKS WHAT IT CLAIMS: ALL 26 GUARDS MIGRATED (R10 change, approved and applied 2026-08-22)

**Applied with explicit founder approval to `kaggle/regenerate_rag_e5.py` (R10-protected).**
Proposal: `docs/decisions/proposed-r10-change-regen-guards.md`. Local dry-run before it ever runs on
Kaggle: `eval/index_quality/verify_regen_guards_local.py` →
`eval/results/regen_guards_local_dryrun.json` (AST-parses the guard block and replays it against the
committed index — no Kaggle cycle needed to know what it will do).

| before | after |
|---|---|
| 2 of 26 guards clean | **26 of 26 sound** |
| 18 could pass on a fact they did not mean | **0** (1 adjudicated benign) |
| 3 dead anchors matching zero facts | **0** |
| 5 guards on paraphrased phrasing | **0** — verbatim eval text |
| 0 failing, and that was the problem | **2 KNOWN-FAIL, tracked and visible** |

Dry-run result: **24 PASS · 0 FAIL · 2 KNOWN-FAIL · 0 STALE · 0 ORPHAN · regen not blocked.**

**What changed:**

1. **Five displacement guards → verbatim eval text + unique anchors.** The phrasing fault was not
   cosmetic: `nat_36`'s fact is rank 2 under the old paraphrase and **rank 17** under the text its
   eval row actually uses.
2. **All remaining ambiguous anchors → substrings verified to match exactly one fact**, re-asserted
   at runtime so a future fact edit cannot silently restore the fault. The worst case was
   `SDL rate`, whose `3.5` anchor was satisfied by **three different facts at once** ([88], [212],
   [5]) with nothing recording which.
3. **THREE DEAD ANCHORS FOUND AND REMOVED** — `elfu 22`, `28 julai`, `efd threshold tzs 11m` matched
   **zero** facts. They could never have fired. Each sat behind a live ambiguous sibling that always
   passed, so nothing ever revealed them. **A new `[DEAD-ANCHOR]` check now blocks on this.**
4. **`KNOWN_FAILING` bucket** — `nat_27` and `nat_36`. *(Correction to my own proposal, which listed
   only `nat_27`: once `nat_36`'s guard uses verbatim phrasing it fails too, at rank 17.)* Reported
   every run as `[KNOWN-FAIL]`, does not block.
5. **`[STALE-KNOWN-FAIL]` and `[ORPHAN-KNOWN-FAIL]`** — a bucketed guard that starts passing, or a
   name matching no guard, **blocks**. This is what stops the bucket becoming where guards go to be
   forgotten.
6. **One ambiguity accepted, with reasoning at the guard.** `OSHA/WCF small-count`'s anchors match
   [68] and [69] and **both** state what it protects, so pinning to one would fail spuriously on the
   other. **The general rule, now written down: ambiguity is a fault when the alternative fact would
   be a WRONG answer — not merely when more than one fact matches.**

**What this does not do:** it does not fix `nat_27` or `nat_36`. It makes their breakage *visible*
instead of reported as a pass. Closing them means the ask-first rewrite measured at rank 15 → 2 and
17 → 1 — which is index work, not guard work.

---

# 🧭 THE 69-RANK SWING: ASK-ALIGNMENT IS THE DOMINANT RETRIEVABILITY FACTOR (2026-08-22)

**Recorded as its own result, because it is the strongest evidence this project has about what
makes a fact retrievable — and it should be met before anyone proposes bulk index work again.**

Two rewrites of **the same two facts**, carrying **the same regulatory content**, both Swahili,
both value-forward. The only difference is **whose vocabulary they lead with.**

| | leads with | `nat_28`'s fact rank |
|---|---|---|
| **v1** | the rate and the legal framing — *"Ukifanya kazi ya HUDUMA … VAT withholding ya asilimia 6 … Finance Act 2025"* | **79** |
| **v2** | the asker's own words — *"Ukifanya kazi ya **ushauri** … watakukata VAT … utapewa **CHETI**"* | **10** |

**69 ranks, from vocabulary alone.** `nat_28`'s question contains *ushauri* and *cheti*; v1 dropped
both for the regulatory register, and the fact fell 46 places **below where it started**. v1 would
have shipped a severe regression while reading like a perfectly sensible rewrite.

**Corroborated independently on `nat_36`**: its fact was **already** Swahili-first with the value
near the front and sat at **rank 17**. Re-leading it with *mashine ya risiti (EFD)* — the object the
user asks about — instead of *"Kizingiti cha kuanza kutumia"* took it to **rank 1**.

**The ranking of factors, as measured:**

1. **Ask-alignment — dominant.** 69 ranks (`nat_28`), 16 ranks (`nat_36`), 13 ranks (`nat_27`).
2. **Swahili-first / value-forward — necessary, not sufficient.** `nat_36`'s fact satisfied it
   fully and was still unretrievable.
3. **Clearing competing `key: value` fragments — real but small.** +3 and +11 ranks; closed
   neither row.

**What a future session must meet before proposing a bulk rewrite of the index:** a bulk pass
optimises (2) and (3), the two weaker factors, and cannot optimise (1) — because ask-alignment is
defined per question, not per fact. **Index work is per-row: take the row that fails, rewrite the
fact it needs in the asker's words, measure the rank.** Evidence:
`eval/results/targeted_rewrite.json`, `eval/results/reopen_nat44_nat28.json`. Authoring rule
recorded in `CLAUDE.md` R15.

---

# 🔁 nat_44 / nat_28 RE-OPENED: DEFERRED ON A SOUND REASON, NOT CLOSED ON A FALSE ONE (2026-08-22)

Re-measured with the faults removed — verbatim phrasings, anchors **asserted unique in the index at
runtime**, ranks read by fact position so no substring can stand in.
`eval/index_quality/reopen_nat44_nat28.py` → `eval/results/reopen_nat44_nat28.json`.

| row | before | v1 (rate-led) | v2 (ask-led) |
|---|---|---|---|
| `nat_44` | 33 | 5 (+28) | **4 (+29)** |
| `nat_28` | 33 | **79 (−46)** | **10 (+23)** |
| `nat_27` | 15 | 16 (−1) | 16 (−1) |

**1. The stated reason for declining is dead.** The rewrite's measured effect on `nat_27` is
**one rank**, on a row sitting at 15 that is **not retrieved either way and answers correctly from
model weights**. There was no live behaviour to regress. Real wins were declined against a
regression that does not exist, detected by a guard that could not tell [13] from [64].

**2. The outcome stands; the reasoning is REPLACED.** Recorded plainly, because the difference
matters to anyone who reads this later:

> **Not shipped — because neither variant reaches top-3 against production's `top_k=3`
> (`nat_44` rank 4, `nat_28` rank 10). NOT because it regresses `nat_27`; that regression never
> existed.**

This is the same ceiling already proven empirically: rank 8 never reaches a `top_k=3` system.

**3. STATUS: DEFERRAL, NOT CLOSURE.** `nat_44` moved 33 → 4. It is **one rank** outside the window
and one alignment iteration from viable — v2 already gained 29 places over v1's 28 by adding the
asker's words, and that lever is not exhausted. This should be picked up again, not filed as
decided. `nat_28` at rank 10 is further out and needs the certificate half of its question handled
too, since the row asks two things.

**3. The wording result is the most valuable part, and it is a direct confirmation of the
topic-alignment finding.** The two variants rewrite the SAME facts and differ only in whether they
use the asker's vocabulary. Rate-led wording sent `nat_28` to **79**. Ask-led wording — including
*ushauri* and *cheti*, the words the question actually contains — put it at **10**. **A 69-rank
swing from vocabulary choice alone, on identical facts.** V1 would have shipped a severe regression
while looking like a reasonable rewrite.

**Recorded into `CLAUDE.md` R15 authoring guidance:** Swahili-first is necessary and not sufficient;
lead with the user's vocabulary, not the regulatory label; index work is per-row and testable, not
a bulk rewrite.

---

# ⛔ nat_27 IS RETIRED AS A NEGATIVE CONTROL — AND EVERY CHECK THAT LEANED ON IT PROVED LESS THAN IT REPORTED (2026-08-22)

**A luck row cannot certify anything.** `nat_27`'s correct answer comes from model weights: the VAT
18% fact sits at rank 15 for its own question and is never retrieved. **No index change can break
it and no index change can protect it.** Using it as a must-stay-correct control measures the base
model's memory, not the change under test.

**Retired, effective now. Do not use `nat_27` as a negative control, a displacement guard, or a
canary.** Same contagion rule as the provisional marking: every conclusion that rested on it is
weakened, and they are named here rather than left for someone to rediscover.

| check | what it claimed | corrected status |
|---|---|---|
| **The `nat_44`/`nat_28` withholding-rewrite decision** (2026-08-17) | the rewrite was **held back** because it "regresses `nat_27`", trading a confirmed regression for an unconfirmed gain | ⛔ **RE-OPEN.** The protected row is ungrounded, and the guard that detected the "regression" is the substring guard that matches [64], not [13]. Two independent reasons the trade was mis-priced. Real wins (33→4, 33→8) were declined on it |
| **The interleave canary set** (2026-08-22) | 8 rows canaried as "must stay correct"; `nat_27` among them; its top-3 set changed but it stayed correct | ⚠️ **weakened.** `nat_27` staying correct through a top-3 change is exactly what an ungrounded row does — it was never going to flip. One of the 8 canaries carried no signal |
| **The fee-mask rejection** (2026-08-17) | fee-mask dropped the supporting fact for three CORRECT rows (`nat_27`, `nat_36`, `nat_37`) for zero rows fixed | ⚠️ **weakened, conclusion probably survives.** All three are now measured ungrounded, so "loses its supporting fact" was not what was happening. The rejection had other grounds; the `nat_27`/`nat_36`/`nat_37` limb of it does not hold |
| **The four displacement guards `nat_26/27/34/36`** (R15 regen, 2026-08-17) | all four held live, byte-identical | ⚠️ **weakened for `nat_27` and `nat_36`** — and the guards themselves are unsound (next entry). `nat_34` and `nat_26` are measured GROUNDED/PARTIAL and stand |
| **Today's R16 close-out negative check** (this session) | `nat_27` VAT 18% correct after removing the SS8 instrument | ⚠️ **weakened — mine.** The redeploy conclusion still holds on `nat_32`, `nat_43` and the OOC probe, all of which are grounded or classifier-backed. But I cited a luck row as evidence production still worked, and it proved nothing |

**`nat_36` is a borderline case and is NOT retired**: its fact reaches rank 2 under one phrasing and
rank 17 under the verbatim one, so it is unstable rather than inert. Usable only with the verbatim
text and only alongside a grounding check.

**Replacement controls should be grounded rows**: `nat_31`, `nat_34`, `nat_32`, `nat_39`, `nat_43`
are measured GROUNDED and can carry a real signal. Compute-path rows are stronger still.

---

# 🔀 nat_38 — AN OVERRIDE AMONG THE SUCCESSES. D1'S "ZERO OVERRIDE" WAS ONLY EVER MEASURED ON THE FAILURES (2026-08-22)

**On the board as its own item, per instruction.** `nat_38` answered **correctly** while the only
on-topic fact it retrieved pointed the **other way**.

- Q: *"nimeshasajili vat je lazima niwe na mashine ya risiti hata kama mauzo ni madogo"* — an
  already-VAT-registered business.
- Retrieved [58]: *"Duka dogo au biashara ndogo yenye mauzo madogo, je inahitaji mashine ya risiti
  (EFD)? **Si lazima.** Si kila biashara…"*
- Reply: *"**Ndiyo**, unatakiwa kuwa na mashine ya EFD. Biashara iliyosajiliwa VAT inatakiwa kutumia
  EFD bila kujali kiasi cha mauzo."* — **correct**, and the fact carrying it was never retrieved.

**Why this matters to D1's framing.** The class analysis partitioned all nine WRONG rows and found
**OVERRIDE = 0** — the model never contradicted a retrieved fact — and that zero is what killed the
queued adapter build (it would have fixed none of them). **That measurement was run only over the
failures.** `nat_38` is an override among the *successes*, and nobody looked there.

**What changes and what doesn't:**

- **D1's conclusion still holds.** Zero override among the failures is still true, and an adapter
  still fixes none of the nine. The decision not to build it was correct.
- **But "the model recites what it is handed" is now false as a general claim.** It was the
  headline framing of that analysis. The model demonstrably *does* override retrieved content — it
  just happened to override toward the right answer in the one case anyone has measured.
- **The override capability exists in both directions**, which cuts both ways: it is why ungrounded
  rows can be right, and it is a mechanism by which a *correct* retrieved fact could be discarded.
  **Nobody has measured the second case**, because the failure analysis found no OVERRIDE and the
  success analysis was never run.

**The measurement nobody has done: partition the CORRECT rows by mechanism the way D1 partitioned
the wrong ones.** This entry has done it for the fact path by grounding (5 grounded / 2 partial /
4 ungrounded, one of which is a contrary-override) but not by override-vs-recite across the whole
set. **Not scoped, not started.** Named so it is not rediscovered a third time.

## 📌 BOARD ITEM — THE DISCARD RATE: how often does a CORRECT retrieved fact get ignored?

**This is the item to carry forward, and it is a precondition for valuing every retrieval fix in
ADR 0002.**

`nat_38` proves the model overrides retrieved content. It overrode *toward* the right answer, which
is the harmless direction. **The harmful direction — a correct fact retrieved and then discarded —
has never been measured, in either analysis.** D1 looked only at failures and found no override
there; this entry looked at successes and found one. Nobody has asked how often a *correct* fact
reaches context and fails to reach the answer.

**Why it gates everything else:** if the discard rate is non-trivial, then **retrieval fixes do not
reliably reach the answer even when they work.** §1's rank improvements, §2's intercept, the
routing extension's engine reach — all of them assume that getting the right content into context
produces the right answer. `nat_38` shows that assumption is not free, and §8's forced-fact test
already showed three rows failing with the correct facts *placed directly in context*. **That is
arguably a discard measurement already, and it came out 3 of 8.**

**Cheapest way to measure it properly:** the SS8 instrument already exists and is committed
(`9be20c7`, `eval/forced_facts/`). Force the correct fact into context for the rows that currently
answer correctly *and* for a sample of the fact path, and count how often the reply uses it. Not
scoped, not started — but the harness is built and the method is proven.

---

# 🎯 §1 TESTED ON TWO FALSIFIABLE TARGETS: THE FRAGMENT HYPOTHESIS IS REAL BUT INSUFFICIENT — AND TWO R15 VERIFICATION GUARDS ARE UNSOUND (2026-08-22)

Targeted at `nat_27` (needs fact **[13]**, VAT 18%) and `nat_36` (needs fact **[57]**, EFD
11,000,000) instead of sampling the 89 — both facts are in the index, neither is retrieved for its
own question, so the hypothesis is cheap to falsify. Harness
`eval/index_quality/measure_targeted_rewrite.py`, artifact `eval/results/targeted_rewrite.json`.
**Measurement only — nothing written back to the index.**

| | `nat_27` → [13] | `nat_36` → [57] |
|---|---|---|
| baseline rank, **verbatim** question | **15** | **17** |
| competitors above target | 14 (10 fragments, 71%) | 16 (14 fragments, 88%) |
| **ARM A** — rewrite the fragment competitors, target untouched | 15 → **12** (+3) | 17 → **6** (+11) |
| **ARM B** — rewrite the target itself, competitors untouched | 15 → **2** ✅ | 17 → **1** ✅ |

**Verdict: the fragment hypothesis is real and insufficient.** Clearing fragment noise moves ranks
in the right direction — materially for `nat_36`, +11 places — so the 89 genuinely are suppressing
real facts. **But neither row reaches top-3 that way.** Rewriting the *target fact itself* does, in
both cases, decisively.

**So §1 is not "rewrite the 89".** It is **"rewrite the specific facts that failing rows need, led by
the ask, in Swahili, value at the front"** — per-row, testable, far cheaper than a bulk pass, and
with a pass/fail criterion per row. `nat_36` is the instructive case: [57] was **already**
Swahili-first with the value near the front, so language was never its problem. What moved it 17→1
was **front-loading what the user asks about** (*mashine ya risiti / EFD*) instead of the
regulatory label (*Kizingiti cha kuanza kutumia*). **Topic alignment, not translation.**

Also note: [13] is **not** in my 89-row fragment count (its value exceeds the scan's length cut) yet
it is plainly an English `key: value` row. **The scan under-counts the real population** — the
defect is the English key-first framing generally, not just short fragments.

## ⛔ Two R15 verification guards are unsound, in two different ways

`kaggle/regenerate_rag_e5.py` ships guards asserting exactly these two facts retrieve in the top-3.
The R15 regen was certified as passing them. The grounding measurement said they are not retrieved.
Both are true, because **the guards do not test what they claim**:

- **`nat_36`'s guard passes on a phrasing production never sends.** The guard asks
  *"**M**auzo yangu … mashine ya risiti**?**"* — capitalised, question mark. That phrasing puts [57]
  at **rank 2**. The verbatim eval/production text (lowercase, no `?`) puts it at **rank 17**.
  Capitalisation and one punctuation mark move a fact fifteen places.
- **`nat_27`'s guard passes on the WRONG FACT.** Its keyword test is `'18%' in fact_text`. The
  guard-phrasing top-3 is [170] *vat deferment threshold percentage: 90 %*, [171] *vat deferment
  minimum value*, **[64] *vat withholding formula correct*** — and [64] contains the string `18%`
  inside "the standard 18% VAT is split…". **The guard matches a withholding-formula fact and
  reports the standard-rate fact as retrieved.** [13] is at rank 8 even on the guard's own phrasing.

**This is the documented false-PASS mode recurring** — PROGRESS already records a `18%` substring
matching a contrast clause during the C4 wording work. It was fixed for that one dry-run and the
same defect shipped in the regen guard.

**NOT FIXED HERE: `kaggle/` is R10-protected.** The guards need (a) verbatim production phrasing and
(b) a keyword distinctive to the intended fact (`NEVER 14%` / `unchanged since 2015` for [13]).
Making them verbatim will make `nat_27`'s guard **fail**, which is correct — but a failing critical
query aborts the regen, so this needs an explicit known-failing bucket rather than a silent pass.
**Founder decision, flagged not taken.**

## Consequence: the nat_44 / nat_28 decision should be re-opened

The `vat_withholding_goods`/`services` rewrite — which measured `nat_44` rank 33→4 and `nat_28`'s
rate half 33→8, real wins — **was held back because it "regresses nat_27".** That protection now
looks unsound in two independent ways: `nat_27`'s supporting fact **is not retrieved in production
anyway** (rank 15, and the row answers correctly from model weights regardless), and the guard used
to detect the regression is the substring guard shown above to match [64] rather than [13].
**Flagged for re-opening, not re-opened here** — it needs its own measurement with a sound guard.

---

# 🏛️ WHERE THIS SYSTEM'S RELIABILITY ACTUALLY LIVES: THE DETERMINISTIC PARTS CARRY IT (2026-08-22)

**Stated as the headline because it is the clearest single fact we have about this system, and it
has been sitting inside a caveat.** Of the 29 correct answers in the 48-row set:

| source of the correct answer | n | grounded by |
|---|---|---|
| **rules engine** (compute path) | **15** | deterministic arithmetic, working appended — cannot drift |
| **OOC classifier** (refusal path) | **3** | a phrase list, infrastructure not behaviour (R11) |
| **retrieval + model** (fact path) | **11** | the only rows where correctness is contingent |

**18 of 29 correct answers — 62% — come from parts of the system that cannot be wrong by
accident.** And of the 11 that are contingent, **4 are ungrounded and 2 partial**: the answer came
out of model weights, not out of anything retrieved (measured below).

**So the honest picture is: retrieval-dependent rows are 11 of 48, and fewer than half of those are
actually supported by retrieval.** The system works mainly where it is deterministic.

**The strategic reading, and it cuts against the last three weeks of work.** Every mechanism in ADR
0002 — hybrid fusion, re-ranking, a bigger embedding model, the routing intercept, index rewriting —
is an attempt to improve **the weakest and smallest surface**. The measured alternative is to
**extend the deterministic surface**: more rules engines, more routing into them, more classifier
coverage. §8 already pointed this way (three of eight failures are routing misses into engines that
already work, and `nat_33` needs an engine that doesn't exist yet). This entry says the same thing
from the successes instead of the failures.

**This is not a decision, and nothing is scoped from it.** It is the strongest available argument
for a direction the project has not been taking, recorded so the next scoping starts from it. The
counter-argument it must answer: the deterministic surface only covers what someone has written an
engine for, and the corpus moat is supposed to be broad. Extending determinism trades breadth for
reliability, and nobody has costed that trade.

---

# 🚨 GROUNDING MEASURED ACROSS THE 48: FEWER THAN HALF THE RETRIEVAL-DEPENDENT CORRECT ANSWERS ARE ACTUALLY SUPPORTED BY WHAT RETRIEVAL RETURNED (2026-08-22)

**The luck finding generalises. It is not one probe.** Harness
`eval/grounding/measure_grounding_48.py`, hand adjudication
`eval/grounding/adjudication_no_figures.json`, artifact `eval/results/grounding_48.json`.
Offline, production e5 encoding, production index, production pooling.

## First: only 11 of the 29 correct rows depend on retrieval at all

This narrows the question before it widens it. From the 2026-08-17 adjudication:

| path | CORRECT | grounded by |
|---|---|---|
| compute | **15** | the rules engine — the working is appended deterministically |
| refusal | **3** | the OOC classifier |
| **fact** | **11** | **retrieval — the only rows where "was it grounded?" is even a question** |

**The engine-backed 15 are safe by construction, and that is the reassuring half of this
entry.** Everything below concerns the 11.

## Of those 11, retrieval actually supported 5

| grounding | rows | n |
|---|---|---|
| **GROUNDED** | `nat_31`, `nat_34`, `nat_32`, `nat_39`, `nat_43` | **5** |
| **PARTIAL** | `nat_26` (6-month/100M half retrieved, 12-month/200M half not), `nat_40` (both bodies in context, the specific claim carried by a fact that wasn't retrieved) | **2** |
| **UNGROUNDED** | `nat_27`, `nat_36`, `nat_37`, `nat_38` | **4** |

**Four correct answers came out of model weights with no supporting fact in context, and two
more were only half-supported.** The worked examples:

- **`nat_27` — "vat ya asilimia ngapi naiweka kwenye bei ya bidhaa zangu"** retrieved
  *vat deferment threshold percentage: 90 %*, *maternity cash benefit rate: 100 %*, *vat
  deferment minimum value: 10,000,000 TZS*. **The 18% standard rate is not in there.** The right
  answer was recited from memory. **This row has been used as a "must stay correct" negative
  control in R16 checks — including twice by me today.** It is a luck control, and every past
  check that leaned on it proved less than it appeared to.
- **`nat_36` — EFD threshold** retrieved *vat deferment minimum value: **10,000,000** TZS*, a
  royalties WHT rate, and a company registration fee. The real threshold is **11,000,000**, which
  was never retrieved. The model got it right next to a plausible wrong neighbour it could just as
  easily have copied.
- **`nat_38` is the sharpest case: the model was right and its context pointed the other way.**
  The question is about an already VAT-registered business; the only on-topic retrieved row says a
  small shop does *not* necessarily need an EFD (*"Si lazima"*). **Better retrieval-following would
  have made this answer worse.**

## What this does and does not mean

- **It does not mean 29/48 is wrong.** The answers were adjudicated correct and they are correct.
- **It means the measurement basis is softer than it reads.** ~5–6 of 29 correct answers are
  ungrounded or partly so, and of the correct answers that depend on retrieval, **fewer than half
  were actually supported.** These rows are not evidence that the pipeline works; they are evidence
  that the base model knows some Tanzanian tax facts.
- **It means ungrounded rows are silently fragile.** Nothing in the system distinguishes
  "answered from a retrieved fact" from "answered from weights". A model swap, a quantisation
  change, or a temperature change could move them with no index change to point at — and no gate
  would predict it.
- **It sharpens R10's premise.** The architecture decision says facts come from RAG and the model's
  role is "Swahili response formatting and persona, not fact storage." **On these rows the model
  IS the fact store.** That is the opposite of the stated design, and it is currently invisible.

## Method, and its two blind spots — stated, not buried

Figure-presence test: every figure the reply *asserts* (question-supplied figures subtracted) must
appear in the retrieved context, normalised across digit / English-word / Swahili-word forms and
scale words (*milioni 10* = *ten million* = *10,000,000*). Rows asserting no new figure were
**adjudicated by hand**, recorded row-by-row.

It cannot see a wrong-but-unnumbered claim, and it can count a coincidental figure as support.
**Three instrument bugs were found and fixed before any of this was written up** — user-supplied
figures counted as unsupported assertions; English scale words unhandled (`penalty fine non
citizen: ten million TZS` scored a false UNGROUNDED); substring matching that would have scored
`18` as present inside `180000`. Production pooling across sub-questions was added and **changed
nothing, because no fact-path row in the 48 decomposes at all** — the whole-question top-3 *is*
the production context for every one of them.

## Consequence for the queue

**This raises §1 further and lowers the value of any accuracy number not accompanied by grounding.**
It also means the §1 sample-rewrite measurement (next) has a sharper success criterion than "do
ranks move": it should ask whether the *specific* facts these 11 rows need start being retrieved.

---

# 🔴 RETRIEVAL RETURNS NOTHING RELEVANT FOR A PLAIN SDL QUESTION — AND ~40% OF THE INDEX IS IN THE SHAPE R15 SAYS RETRIEVES WORSE (2026-08-22)

**This started as a follow-up on the "asilimia 0.5" conflation and ended somewhere else. Every
diagnosis offered for that defect — mine included — was wrong, and the measurement says so.**

Harnesses committed before results (R18): `eval/routing/measure_nickname_routing.py` (16 probes,
4 of them R17 adversarial), `eval/routing/run_live_nickname_probes.py`,
`eval/routing/measure_numeral_form_retrieval.py`, `eval/index_quality/scan_fragment_rows.py`.
Artifacts in `eval/results/`.

## The conflation is not a guard gap and not a routing gap

| probe | difference | live answer (2 attempts each) | verdict |
|---|---|---|---|
| `nick_01` | *watu **watano*** (word numeral) | *"…asilimia **0.5** kwa ajili ya mafunzo… **nssf.go.tz**"* | **WRONG** 2/2 — 4/4 with the originals |
| `nick_02` | *watu **5*** — otherwise identical | *"…chini ya 10, hakuna ulazima wa kulipa SDL. Thibitisha na tra.go.tz."* | **CORRECT** 2/2 |
| `nick_03` | digit + **SDL named explicitly** | *"…unatakiwa kuwa na wafanyakazi 10 au zaidi…"* | **CORRECT** 2/2 |
| `nick_08` | reaches compute | engine appends `SDL = 3.5% × TZS 5,500,000 = TZS 192,500` | **CORRECT** 2/2 |

`nick_01` and `nick_02` **route identically** (`detect_intent → none`, fact path), so the routing
miss is not the differentiator — and they **retrieve the identical top-3** (measured against the
production index with production's own e5 query encoding; ranks 1 and 2 merely swap), so retrieval
content is not either. Same route, same facts, opposite answers, each stable under greedy decoding.
**The divergence is generation-side and its trigger is the surface form of a numeral.**

## The bigger finding: both phrasings were handed nothing usable

The top-3 that *both* receive:

```
1  minimum shareholders: 2 employees
2  unpaid contribution penalty rate: five %
3  minimum directors: 2 employees
```

**No SDL fact. No rate, no threshold.** So `nick_02`'s and `nick_03`'s "correct" answers are
**ungrounded generations that happened to land right**, and `nick_01` is the same process landing
wrong. **A passing answer here is luck, not a working system** — and any future measurement that
uses these as passing controls is measuring luck.

## ~40% of the index is in the shape R15 warns against

Counted, with a heuristic that is labelled as one (`eval/results/index_fragment_scan.json`):
**89 of 221 rows (40.3%) are terse English `key: value` fragments** — the exact shape R15's own note
says retrieves *far worse* than short Swahili-first text with the value at the front. Plus 6 rows
with a spelled-out numeral where a figure belongs (`trademark renewal period: **saba** years`,
`unpaid contribution penalty rate: **five** %`, `…: six months **null**`) and 3 with a wrong unit
noun (`minimum directors: 2 **employees**`) — **one of which is a false positive**, which is why the
scan is labelled heuristic and none of the 89 has been adjudicated individually.

**This promotes §1 (index-content rewriting) from a tidy-up that "folds into the next regen" to a
candidate lead item.** Not scoped, not started.

## What this does to the routing extension

It does **not** kill it — `nick_08` shows the compute path is deterministic and immune, and §8's
three routing misses are still real. But the routing extension is no longer the obvious lead:
**§1 now has a measured case and the routing extension's 6–7 of 8 remains an inference from §8, not
a measured yield.** Both are labelled accordingly in ADR 0002 §9.8 and the standing order. **Nothing
has been built or scoped further, and the next step for either is a measurement.**

Full scoping — three distinct routing gaps (only one of which matches the "nicknamed multi-levy"
framing), why relaxing the number gate is measured to be unsafe, and a candidate fact-path rate
guard — in `docs/decisions/0002-retrieval-structural-scoping.md` §9.

---

# ✅ §8 RE-MEASURED ON LIVE v16 WITH A COMMITTED HARNESS: THE SPLIT HOLDS, TWO ROWS' FAILURE MODES DON'T — AND ONE HEADLINE CLAIM IS WRONG (2026-08-22)

**This supersedes the provisional entry below.** Instrument committed *before* the run (R18) at
`9be20c7`, run on the live deployed pipeline, artifact at
`eval/results/ss8_forced_facts_v16_2026_08_22.json`, fixture at `eval/forced_facts/ss8_rows.json`,
runner at `eval/forced_facts/run_ss8_forced_facts.py`. **Every row reports `pipeline: "v16"` in the
artifact** — the arm ambiguity that invalidated the first attempt is closed by measurement, not
assertion. Container freshness is proven structurally: `run_forced_facts` did not exist on the
previous deployment, so a stale container could not have answered these calls at all.

| row | v16 reply (abridged) | routed as | verdict | vs provisional |
|---|---|---|---|---|
| `nat_44` | "VAT withholding kwenye bidhaa ni asilimia 3" | fact | **CORRECT** | same |
| `nat_45` | "Kuna siku saba tu za kuwasilisha taarifa" | fact | **CORRECT** (drops *working* from "7 working days") | same |
| `nat_41` | "Hakuna muda maalumu… fanya haraka… Thibitisha na OSHA" | fact | **CORRECT** (invents no deadline) | same |
| `nat_28` | "asilimia 6… cheti si baadaye ya tarehe VAT inakuwa ya kulipwa (si tarehe 20)" | fact | **CORRECT** | same |
| `nat_05` | "asilimia 3.5% ya mishahara ghafi" — right base, never asks for payroll | **fact** | **PARTIAL** | same verdict |
| `nat_33` | "faini ya shilingi 2500 kwa kila mwezi" — drops the 22,000 fee, never computes 7× | fact | **WRONG** | same |
| `nat_24` | "**Thibitisha na TRA (tra.go.tz).**" — bare referral, no content | fact | **WRONG** | same verdict, **different mode** |
| `nat_23` | NSSF computed correctly (20% × 5,500,000 = 1,100,000; employer 550,000) — **SDL absent entirely** | **compute** | **WRONG** | same verdict, **materially different mode** |

**The 4 CORRECT / 1 PARTIAL / 3 WRONG split reproduces exactly on the live pipeline.** The
provisional table's headline number was right. That is worth saying plainly: the re-measurement
vindicated the count.

**But two of the three failures are not what the provisional table said they were, and one of them
overturns a headline claim.**

**1. `nat_23` — the compute engine fired, and worked.** Provisional: *"restates the input and stops;
no arithmetic on either levy."* Measured: the row routed to **compute** (`sub_answer_kinds:
["compute"]`), the NSSF rules engine produced correct, authoritative arithmetic, and **SDL was
silently dropped.** This is exactly what `detect_intent → "nssf"` predicts — one levy detected, one
levy answered, the other invisible. **The routing diagnosis is now confirmed live, on production
behaviour, not just by calling the modules directly.** `nat_23` is not a generation ceiling: the
engine was flawless on the half it was given.
*(Separate defect, newly visible: the reply renders "wafanyakazi 12 wenye mishahara TZS 5,500,000
**kila mmoja**" — asserting each of 12 employees earns the full 5.5M payroll. The arithmetic on the
total is right; the verbal framing of the base is wrong. That is a slot/render defect, not a
routing one, and it is not in any current work item.)*

**2. `nat_05` is also a routing miss — a new finding.** Its rubric expects `compute[sdl]`; it routed
to **fact**. Confirmed directly: `detect_intent("nat_05") → "none"`, and
`is_uncomputable_payroll_amount → False`. The v16 orchestrator deliberately drops v15's never-guess
guard *because the compute path's own clarification is supposed to cover it* — but the row never
reaches the compute path, so nothing asks for the missing payroll figure. **That makes three of the
eight rows routing misses (`nat_05`, `nat_23`, `nat_24`), not generation failures — and leaves
`nat_33` as the only genuine capability gap** (no BRELA engine exists; `detect_intent → "none"`).

**3. ⚠️ THE PILOT-SAFETY HEADLINE OVERSTATES ITS CASE, AND THIS RUN SHOWS IT.** That entry says
`nat_23` and `nat_24` both failed *"with no hedge, no 'sijui,' no visible sign of uncertainty at
all"* and that there is *"no measured route to 'sina uhakika' of any kind."* **Measured on v16,
`nat_24` returned exactly one thing: "Thibitisha na TRA (tra.go.tz)" — a bare deferral.** That is
the project's own referral formula. It is not a classified refusal (`refused: false`,
`needs_clarification: false`) — it is the model producing a content-free referral on the fact path
— but as user-visible behaviour it is a deferral, not a confident wrong answer. **The "no route of
any kind" claim is not supported and is corrected in that entry.**

**What survives, from `nat_23` alone:** a **confidently incomplete** answer — right facts in
context, correct arithmetic on one levy, an entire second levy missing, no signal of any kind that
half the question went unanswered. That still defeats a *retrieval-confidence* floor, because
nothing about retrieval was uncertain. **But the mechanism is now named, and it is narrower than
"the generation side is unreliable": it is a routing fan-out miss, and the generation-side check
the headline itself proposed — "does the reply address every part of a multi-part question" —
would catch it.** The pilot-safety picture is worse than "solved" and materially better than "no
route exists."

## §2's yield, now measured rather than estimated

Forcing the correct facts in *is* the ceiling §2 can reach, since §2 closes retrieval for exactly
these rows. So §2's yield is no longer an estimate:

- **§2 alone: 4 of 8 CORRECT, plus `nat_05` partial — call it 4–5 of 8, not the ~5–6 previously
  claimed.** The provisional figure was slightly optimistic.
- **§2 + a routing/decomposition extension: 6–7 of 8.** `nat_23` needs multi-levy fan-out from
  nicknamed phrasing; `nat_24` needs threshold-trap detection (`detect_intent → "none"` today);
  `nat_05` needs to reach the compute path at all so its clarification can fire.
- **`nat_33` is out of reach of both** — it needs a BRELA engine that does not exist.

These figures are measured, cite a committed artifact, and are no longer provisional. **§2 is now
unblocked on evidence** — the §8 precondition is satisfied — but nothing has been scoped or started,
and that remains a separate go-ahead.

## R16 close-out: instrument removed, production verified

Debug method removed and redeployed. Verified live, not from a deploy log
(`scratch/ss8_post_removal_check.py` → `.json`):

- **Positive — the instrument is gone:** `run_forced_facts.remote(...)` now raises `NotFoundError`.
- **Negative — production still answers.** `nat_32` (shareholder-vs-operator, verbatim) correctly
  distinguishes passive shareholding from operating; `nat_43` (GN605A sector variance) correct;
  `nat_27` VAT 18% correct; the OOC probe (`kodi ya faida ya mtaji`) still refuses through the
  config-only phrase path.
- Full local suite: **1229 passed, 1 xfailed**, unchanged. (Bare `pytest` exits 2 on a pre-existing
  collection error — `kaggle/extraction_stress_test.py` is Kaggle-only. `pytest tests/` is the
  gate.)

**Process note, recorded rather than quietly fixed:** the first pass of this negative check sent a
question I had composed from memory while labelling it `nat_32`. Any verdict from it would have
been meaningless as a regression check — the same mistake-shape this whole cycle is about, one
level down. The check was re-run with the verbatim row text; the results above are from that run.

## ⚠️ FOLLOWED UP — and it was not the defect it looked like. See the entry above this one.

**The finding below was recorded as an incidental cross-levy conflation. Followed up on
instruction, and the diagnosis in it is wrong.** It is not a `_cross_levy_guard` gap, and it is not
caused by the routing miss: the digit variant of the *same sentence* misses routing identically and
answers correctly, and both phrasings retrieve the **identical** top-3. The real finding is worse
and is written up in **"RETRIEVAL RETURNS NOTHING RELEVANT FOR A PLAIN SDL QUESTION"** above. The
text below is kept unedited as the original observation.

## ⚠️ Incidental finding, NOT a gate row, NOT scoped — a reproducible cross-levy error

The invented probe was re-sent once deliberately, and **it reproduces exactly**:

> Q: *nimeajiri watu watano tu je nalipa ile ya mafunzo*
> A: *"…unatakiwa kuwa na wafanyakazi 10 ili kulazimika kulipa **asilimia 0.5** kwa ajili ya
> mafunzo. Thibitisha na mamlaka husika (**nssf.go.tz**)."*

The SDL threshold (10 employees) is right. **The rate is WCF's 0.5%, not SDL's 3.5%, and the
authority cited is NSSF, not TRA** — a three-way levy conflation on a plainly in-scope question,
twice out of two attempts. `chike/orchestrator.py` has a `_cross_levy_guard`; this got past it.
**Recorded only.** It is not one of the 48 rows, it was measured twice with n=1 phrasing, and
nothing here is scoped to fix it — but it should not be lost, and it belongs to the same routing
workstream as `nat_23`/`nat_24`.

---

# 🗄️ SUPERSEDED — the provisional §8 entry, kept for audit trail (2026-08-22)

**Everything below was produced by the uncommitted harness and is retained only so the correction
is legible.** Its split turned out to be right; two of its failure-mode descriptions turned out to
be wrong. Read the entry above instead.

# 🎯 §8 MEASURED: RETRIEVAL IS BINDING FOR MOST OF THE REMAINING 8 ROWS, NOT ALL — A THIRD FAIL EVEN WITH THE RIGHT FACT FORCED IN (2026-08-22) — ⛔ SUPERSEDED, PROVISIONAL

**Scoped as a measurement, not a fix, per instruction — nothing shipped.** Two rows forced into
`top_k=3` during the interleave ship's live canaries (`nat_05`, `nat_23`) had both still failed to
produce a correct answer, despite reaching context. That was reason enough to test all 8 remaining
known-buried rows directly, before proposing anything built on the assumption that retrieval is
the binding constraint.

**Method:** added a temporary, additive-only debug method to `chike-inference/modal_app.py`
(`ChikeModel.run_forced_facts`) that runs the real v15 pipeline — the actual model, the actual
prompt builder, the actual post-processing — with retrieval replaced by a constant: the correct
fact(s) for that row, handed to the model directly, no ranking involved. Full R16 cycle to deploy
it, ran all 8 rows, then **removed the method and redeployed again**, confirming `nat_43`/`nat_32`
still answer correctly and the debug method no longer exists. `run()` and `retrieve_facts()`
themselves were never touched.

> # ⛔ PROVISIONAL — EVERY RESULT IN THIS ENTRY. DO NOT SCOPE WORK ON IT.
>
> **The instrument that produced this entire section cannot be inspected, and by its own
> description it ran the wrong pipeline.** `ChikeModel.run_forced_facts` was deployed, used and
> deleted **without ever being committed** — `git log -S'run_forced_facts' --all` returns nothing,
> on any branch. There is no artifact. The method paragraph above says it ran
> `chike.pipeline_v15.answer`; production serves **v16** (see the retraction below). So the numbers
> below may be measurements of a pipeline that is not the one in production, taken by an instrument
> nobody can re-read.
>
> **What is provisional: all of it.** The 4-correct / 1-partial / 3-wrong split. The
> arithmetic-clustering pattern. Every per-row outcome. And **§2's revised yield (~5–6 of 8 alone,
> ~7 of 8 with a routing extension), which is derived from this table and is therefore provisional
> too** — it must not be used to justify building §2.
>
> **The narrow defence does not travel.** It is true that `detect_intent` returns `nssf`/`none` for
> `nat_23`/`nat_24`, so both pipelines route those two to the same pooled-fact generation, and the
> pilot-safety finding drawn from those two rows survives on either arm. **That covers two rows and
> nothing else.** It says nothing about the other six, nothing about the split, and nothing about
> the clustering pattern — all of which sit on the uninspectable instrument.
>
> **Status: being re-measured now** — harness committed first, run on the live v16 path, all eight
> rows. Until that lands, cite anything in this entry as provisional or not at all. **§2 does not
> start until §8 is settled on the live pipeline.**

| row | facts forced | outcome |
|---|---|---|
| `nat_44` | VAT withholding on goods (3%) | **CORRECT** |
| `nat_45` | WCF accident reporting deadline (7 days) | **CORRECT** |
| `nat_41` | OSHA registration-before-opening | **CORRECT** |
| `nat_28` | VAT withholding services (6%) + certificate timing | **CORRECT** |
| `nat_05` | SDL rate (3.5% of payroll) | **PARTIAL** — avoids the wrong-base trap, doesn't close the loop by asking for payroll |
| `nat_33` | BRELA late fee (2,500/mo) + annual fee (22,000) | **WRONG** — drops the annual fee entirely; never computes 7×2,500 |
| `nat_24` | SDL threshold + NSSF rate + WCF rate (3 facts) | **WRONG** — bare non-answer, no content |
| `nat_23` | SDL rate + NSSF rate (2 facts) | **WRONG** — restates the input and stops; no arithmetic on either levy |

**The honest read is mixed, not clean either way — and PROVISIONAL, see the block above.** 4
clearly correct, 1 partial, 3 clearly wrong —
**most (4–5 of 8) do produce a correct answer once retrieval is forced to succeed, so retrieval
genuinely is the binding constraint for the majority of these rows, and closing it (§1, §2) is
worth doing.** But a full **3 of 8 (37.5%) fail even with the exact right facts handed directly to
the model** — for these three, retrieval was never going to be sufficient, regardless of which
retrieval mechanism eventually ships.

**CORRECTION, same session — checked whether the 3 failures are engine-shaped before calling this
"generation-side," and it changes the diagnosis for 2 of 3.** The first pass grouped all three
under "arithmetic/multi-fact synthesis" and filed it as a model-capability question. That skipped
a prior question: does a deterministic engine exist for this arithmetic, and does anything route
to it? Checked directly against `chike/routing.py` (`COMPUTE_TYPES =
("sdl","nssf","paye","wcf","minimum_wage")`) and `chike/rules_engine/`:

- **`nat_33` (BRELA, 7×2,500) has no engine at all** — BRELA isn't a `COMPUTE_TYPES` member, no
  `rules_engine/brela.py` exists. Nothing to route to. This one really is a capability gap.
- **`nat_23` and `nat_24` have real, working engines** (`rules_engine/sdl.py`, `nssf.py`, `wcf.py`
  — the same ones ADR 0001 credits with fixing 9 compute rows once) **but the router does not
  reach them for these two questions.** Ran `chike.decomposition.decompose_query` +
  `chike.routing.detect_intent` directly on both (artifact:
  `scratch/verify_v16_routing_2026_08_22.json`): neither splits into sub-questions — both come
  back as a single whole sentence, because the decomposer doesn't split nicknamed levy references
  like *"ile ya mafunzo na ile ya uzeeni,"* only `?`-splits and explicit enumerations — and
  `detect_intent` returns `nssf` for `nat_23` (a single levy, not the 2-levy fanout its gold
  answer needs) and `none` for `nat_24` (the 3-way threshold trap doesn't fire the cue detector at
  all). `Orchestrator._fan_out_multi_levy` exists and would fan a multi-levy compute part out into
  one compute per levy — but it fans out what `detect_intent`/`_explicit_levy` already named, so a
  nicknamed levy that was never detected can't reach it.

  **CORRECTION TO THE CORRECTION (this session, after a crash mid-edit — the claim below was wrong
  and is retracted).** The paragraph above previously opened by asserting that *"production (v15,
  live) has ZERO compute-engine routing of any kind"* and that `chike/orchestrator.py` is *"not
  live."* **Both halves are false.** Verified against the code, not from memory:
  `kaggle/chike_config.json` carries `"pipeline": "v16"` (set at `ec9cbb3`, *"config(pipeline): v16
  — the cutover flip"*, and unchanged since); `modal_app.py:153` reads that flag into `PIPELINE`;
  `modal_app.py:458` branches on it and calls `self._orchestrator().answer(message)`, and
  `_orchestrator()` constructs `Orchestrator(backend=..., retriever=self.retrieve_facts, ...)` —
  production's own bound retriever, the same one the v15 arm uses. `Orchestrator.answer()` then
  runs `decompose → route → rules_engine` (`orchestrator.py:824-850`). **v16 is the deployed
  pipeline, the live path does reach the rules engines, and the 48-run measurements this cycle were
  of the real system — they stand.** The `pipeline_v15.answer` grep that produced the false claim
  was run against a code path the config selector no longer chooses.

  **What survives that retraction, unchanged: the routing diagnosis itself.** It was never derived
  from which pipeline is live — it was measured by calling `decompose_query` and `detect_intent`
  directly, i.e. the exact modules `Orchestrator.decompose()`/`.route()` call, and re-verified
  today after the crash. So the gap is real and it is a live-path gap: **v16 is deployed, owns
  these engines, and still cannot route `nat_23`/`nat_24` to them.** That makes the routing/
  decomposition extension more valuable than the retracted version implied, not less — there is no
  cutover to wait on; the pipeline that would benefit is already the one in production.

**Revised: 1 of 3 is a genuine capability gap (`nat_33`); 2 of 3 are a routing/decomposition gap
with a known fix pattern (`nat_23`, `nat_24`), not a raw generation ceiling as first stated.** This
is the same mistake-shape flagged earlier this week, caught before it became a wrong build
decision rather than after. **The engine-shape half of this is solid — it was checked against
`chike/routing.py` and `chike/rules_engine/` directly and re-verified after the crash. The half
that says these three rows FAILED is provisional, because that comes from the table above.**

**Consequence: §2's (the routing intercept's) expected real yield is revised again — up, and
conditionally. ⛔ THIS REVISION IS PROVISIONAL AND MUST NOT BE USED TO JUSTIFY BUILDING §2:** it is
arithmetic on the provisional table above, so it inherits that table's defect exactly. Both figures
below are placeholders pending the v16 re-measurement. Alone, it still only reaches ~5–6 of 8
(closing retrieval doesn't help if nothing downstream can compute a fanout from the facts). But a
separate routing/decomposition extension —
splitting nicknamed multi-levy phrasing and detecting fanouts/threshold-traps from natural cues,
not just explicit levy names — would let the EXISTING SDL/NSSF/WCF engines reach `nat_23`/`nat_24`,
putting real yield near **7 of 8**, with only `nat_33` (a new BRELA engine, smallest of the three
gaps) left over. **Neither the routing extension nor the BRELA engine is scoped or built here** —
both belong to `chike/routing.py`/`chike/decomposition.py`/`chike/orchestrator.py`, a separate
workstream and a separate go-ahead.

**Consequence for the pilot-safety floor: see the headline entry immediately above** — this
measurement (`nat_23`/`nat_24` failing with maximum forced retrieval confidence and no hedge) is
the finding that closes the door on retrieval-side floors as a category, not just on margin as one
design. Recorded there as its own headline per instruction, not left as a note here.

Full account, per-row detail, and the revised recommended order in
`docs/decisions/0002-retrieval-structural-scoping.md` §8.

---

# 🛑 THE PREMISE WAS FALSE, NOT JUST THE SHIP: A ZERO-DILUTION INSTRUMENT THAT MEASURED THE WRONG QUANTITY (2026-08-22)

**Lead finding, ahead of the regression that surfaced it:** interleave's structural guarantee held
*perfectly* — the target fact's retrieval rank was preserved in all 8 rows tested, no exception —
and a live answer still broke. The guarantee was real and it was insufficient, because it only
ever covered whether **one fact** kept its rank; generation is sensitive to the **whole injected
set**, and the instrument that certified "zero dilution" never looked at the other two slots. This
is the **presence-not-conclusion family** arriving at a **ship criterion**, not just a guard or an
instrument: "the target fact is present at rank ≤3" was cheap to check and easy to mistake for "the
answer this row will produce is unchanged" — the same shape of mistake this project has now made
at the level of a test assertion, a sweep harness, and a routing check, and today, for the first
time, at the level of the decision to ship.

**The ship decision itself rested on that false distinction.** The choice to prefer interleave
over RRF was built entirely on "RRF dilutes 3 named rows, interleave dilutes 0" — but RRF and
interleave never actually differed on the quantity that determines whether an answer stays
correct. Both change which two facts occupy the non-target slots for virtually every query; only
RRF's version of that change happened to have been measured and named. Interleave's was assumed
zero because the instrument only checked target-fact rank. **The distinction the decision was made
on was not a real distinction between the two mechanisms — it was a real difference between which
one had been measured properly.**

**What happened, in order.** Interleave fusion (dense/lexical, §5 of the ADR) was added to
`chike-inference/modal_app.py`'s `retrieve_facts` and mirrored into `kaggle/eval.py` (R14
dual-sync), full R16 cycle run (`modal app stop --yes` → deploy, forced-fresh containers), and
live-tested per the founder's explicit instruction: canaries on the 3 rows interleave was measured
to recover, the 3 rows RRF was measured to break (the invariant being claimed, tested rather than
asserted), a sample of the 48's other currently-correct rows, and a config-only phrase.

**The invariant test failed, live, reproducibly.** `nat_32` — one of the three rows the ship was
specifically supposed to protect — returned a wrong, hallucinated answer under the new code
("Kampuni ya ujenzi ni shughuli namba 15... anaweza kuadhibiwa" — construction is NOT one of
GN487A's 15 prohibited activities, and passive shareholding is explicitly the fact this question
tests). Called twice, byte-identical both times (`do_sample=False`, greedy decoding — this is
deterministic, not noise).

**Root cause, diagnosed before reverting:** the CORRECT fact (row 210, the shareholder-vs-operator
distinction) stayed at retrieval rank 1 under BOTH the old and new code. The regression came from
the OTHER two injected slots: old top-3 was `[210, 176, 179]` (179 = phone-repair prohibition); new
top-3 was `[210, 92, 176]` (92 = "marriage doesn't exempt a non-citizen"). Swapping one filler fact
for another — with the primary correct fact unchanged and present both times — was enough to flip
the model's completion from correct to wrong.

**The more actionable result: 8 of 8 canary rows changed context; only 1 flipped.** Re-ran the
retrieval comparison (old dense-only vs. new interleave) for all 8 rows canaried as "must stay
correct" (`nat_31, nat_32, nat_34, nat_43, nat_26, nat_27, nat_36, nat_38`). **Every single one had
its top-3 SET change**, despite the target fact's rank being preserved in all eight:

| row | old top-3 | new top-3 |
|---|---|---|
| nat_31 | 205, 206, 193 | 205, **21**, 206 |
| nat_32 | 210, 176, 179 | 210, **92**, 176 — **this one flipped the answer** |
| nat_34 | 130, 131, 114 | 130, **44**, 131 |
| nat_43 | 72, 128, 182 | 72, 128, **7** |
| nat_26 | 171, 101, 146 | 171, **57**, 101 |
| nat_27 | 170, 199, 171 | 170, **5**, 199 |
| nat_36 | 171, 25, 126 | 171, **58**, 25 |
| nat_38 | 171, 58, 148 | 171, 58, **57** |

8/8 changed, 1/8 flipped. **That ratio is the real signal, not "1 broke."** It means any retrieval
change that touches pooled context has a blast radius across the whole currently-correct set that
no offline instrument this project owns can see — rank stability doesn't detect it (all 8 passed
that check), and the 48-question live run only reveals it after the fact, one deploy at a time.
Neither RRF nor interleave has a narrower blast radius than the other on the metric that actually
matters (answer stability); only RRF's cost was ever enumerated, because interleave's was wrongly
assumed to be zero.

**STANDING BAR, going forward: rank-level measurement is not sufficient to ship a retrieval
change.** Any future retrieval mechanism (fusion, re-ranking, a bigger model, anything that can
reorder which facts accompany an already-correct target) needs an **answer-level** regression check
— old vs. new generated reply, not old vs. new fact rank — across the full currently-correct set
before it ships, not just on the rows it targets. This is the check that would have stopped this
ship: target-fact rank was clean on all 8; the generated answer was not. Recorded as the standing
bar in `docs/decisions/0002-retrieval-structural-scoping.md`.

**A second, separate finding: reaching top-3 is not sufficient even before any regression.** Of
the 3 rows interleave was measured to recover, only `nat_41` delivered the expected correct answer
live. `nat_05` returned a bare non-answer instead of the expected base-ambiguity clarification.
`nat_23` answered only the NSSF half of a two-levy question and silently dropped the SDL half — a
decomposition/multi-part-handling gap, not a retrieval one. **Two of three recovery targets failed
on the generation side even after retrieval succeeded** — a failure mode entirely downstream of
retrieval, which no retrieval mechanism (§1, §2, §5, §6, or a bigger model) can touch. If this
ratio holds, it implies a meaningful share of the remaining 8 known-buried rows may still fail
after a correct retrieval fix, for reasons that have nothing to do with retrieval. Recorded as its
own item, `docs/decisions/0002-retrieval-structural-scoping.md` §8.

**Reverted immediately, verified live.** `git restore` on both files (nothing had been committed),
full R16 cycle again (`modal app stop --yes` → deploy), then re-tested `nat_32`, `nat_31`, `nat_34`,
`nat_43` live: all four back to their correct pre-ship answers. **Production is confirmed on the
pre-ship, dense-only single-arm code as of this entry.**

**Where this leaves the decision:** general fusion (RRF, weighted, AND interleave) is declined —
not just RRF. §2 (the routing intercept) is the mechanism that doesn't share this problem, because
it touches a named, bounded set of rows on purpose rather than re-scoring every query — but its
honest purpose is named plainly in the ADR update: it fixes the 6 known keys behind these 8 rows
and nothing else, not a general retrieval solution. Full account, the corrected table, and the
revised recommendation in `docs/decisions/0002-retrieval-structural-scoping.md` §5(d)–§8.

---

# 🛑 THE RETRIEVAL CYCLE'S VERDICT, STATED PLAINLY: RANK MOVEMENT THAT DOESN'T CROSS TOP-3 BUYS NOTHING (2026-08-22)

**This is the workstream's verdict, not a small gain to note in passing.** The full C4→R15→R16
cycle — duplicate-key sweep, three merges, three new/rewritten facts, two rounds of CONCISE
wording, the fee-row mask experiment, the top_k sweep, the Kaggle regen, independent verification,
force-fresh redeploy, and a live re-run of all 48 natural-register questions — moved **one row of
48**. Three separate target facts had their rank improve substantially in the same cycle —
`sdl_rate` 150→24, `GN605A_sector_count` 127→1, `annual_return_filing_fee` 113→25 — and only the
one that reached rank 1 (`GN605A_sector_count`, nat_43) changed the live answer. The other two,
despite the same rewrite discipline and comparable rank gains, produced **byte-identical replies**
to the pre-cycle baseline, because `chike-inference/modal_app.py`'s `top_k=3` never sees rank 24
or rank 25. **Phrasing is a real, proven lever — nat_43 and the ceiling test (query-echoing text
reaching rank 1) both demonstrate that directly — but it is a per-row lever against a field where
the correct fact routinely sits 20–150 rows deep, and per-row is not a viable shape for a
nine-row problem, let alone whatever is behind it.** This is now measured across nine rows
(`nat_05, nat_23, nat_24, nat_28, nat_33, nat_41, nat_43, nat_44, nat_45`), not argued from one.

**THE nat_44 / nat_28 ITEM IS CLOSED.** Recommendation accepted: both left as-is. Shipping the
withheld `vat_withholding_goods`/`services` rewrite would trade a **confirmed live regression** on
nat_27 (currently correct) for an unconfirmed, at-best-marginal chance on nat_44 (rank 33→~4,
unconfirmed against top_k=3) and a provably zero chance on nat_28's rate half (rank 33→~8, and
rank 8 has now been shown empirically, not just argued, to never reach a top_k=3 production
system — four other rows this exact cycle proved that). No further wording pass against this
cluster. The full cost table and the three phrasings tried are in the entry below
("THE nat_44 / nat_28 DECISION"); this line is the closure, not a re-argument.

**The remaining question is entirely structural, and it is scoped — with one item now
measured — in `docs/decisions/0002-retrieval-structural-scoping.md`** (promoted out of scratch/
on founder instruction: a decision record documenting what was tried and rejected doesn't belong
somewhere gitignored). Five candidate mechanisms costed against evidence already held; see the
entry below ("ITEM #5 MEASURED...") for what changed since this paragraph was first written.
**Nothing beyond the §5 measurement is authorized to build yet — analysis first, same discipline
as the coverage scoping, pending a separate go-ahead per item.**

## ITEM #5 MEASURED: general hybrid lexical+dense fusion recovers 4 of 8 remaining buried rows — at a named, live-verified cost (2026-08-22)

Full detail and per-row tables in `docs/decisions/0002-retrieval-structural-scoping.md` §5.
Headline, reported as both halves together, not the positive alone (per instruction): against
the current 221-fact index, **RRF fusion (dense + token-overlap lexical, k=60) crosses
`top_k=3` on 4 of the 8 still-unresolved known rows** — `nat_05` (dense rank 15→1), `nat_23`
(94→3), `nat_33` (48→3), `nat_41` (5→1) — including one row (`nat_23`) buried past rank 90, which
no wording pass this entire cycle reached. This is the first mechanism tested against this
cluster that moves more than one buried row in a single change.

**The cost, named specifically:** RRF (and the weighted variant) also push `nat_31`, `nat_32`,
`nat_34` from rank 1 down to rank 8–16 — out of `top_k=3`. These are not hypothetical rows: all
three are **live-verified CORRECT today** (`natural48_rerun_2026_08_17_adjudication.json`).
Shipping RRF as-is risks breaking three confirmed-correct production answers to gain roughly
four. A fourth strategy (dense/lexical interleave) measured **zero dilution** on the 21-question
fact-path set, at the cost of weaker recovery (3 of 8, misses `nat_33`).

**Follow-up, tested against a real constraint before either option was allowed to look done:** can
the guard that would protect `nat_31`/`nat_32`/`nat_34` be GENERAL (a property of the score
vector) instead of an enumerated list of those three keys — because a guard that only lists the
keys we already know RRF breaks makes the "0 dilution" number circular. Tested the one candidate
named but never measured in the 2026-08-16 floor scoping: **margin** (top-1 minus top-2 dense
score). Result: **no clean threshold exists** — the currently-correct rows' margins (0.0002–0.0037)
overlap, and partly invert, the known-buried rows' margins (0.0004–0.0101); `nat_32` (correct
today) has the single smallest margin of all 21 fact-path questions measured. **The guard can only
be an enumerated key list.** That means: a fact added or reworded a year from now that lands at
dense rank 1 gets no protection from this guard — nothing detects that it needs to be added to the
list, and it stays silently exposed to RRF's dilution until someone happens to re-run a full live
adjudication. **Interleave's zero dilution, by contrast, is a proven structural guarantee, not an
empirical one:** by construction it always consults the dense-rank-1 candidate first, so any
question dense already gets right at rank 1 stays at rank 1 — true for every future fact the same
way it's true for today's three, with nothing to re-derive. Full tables and the ship-framing in
`docs/decisions/0002-retrieval-structural-scoping.md` §5(c). **Still not shipped** — the decision
is interleave (weaker, self-maintaining) vs. RRF+list (stronger, a maintenance liability that can
fail silently), and that decision is a separate go-ahead.

**Item #2 (routing-layer fact intercept) was scoped in parallel, and the disanalogy the founder
named is confirmed, not waved away:** compute-path routing works because it targets a *closed
four-member set* (sdl/nssf/paye/wcf) with a deterministic engine behind it — the cue list only
disambiguates "which of 4," the engine does the real work. A fact intercept has no such engine:
the cue list itself maps straight to a fact key, so it **is** a hand-maintained allowlist, exactly
as the founder suspected — cheap and reliable for the 6 known fact keys behind these rows, worth
zero for any future fact-recall failure not yet observed. That is the failure-driven approach
with extra steps. Its one real edge over a wording rewrite: one cue-list entry covers several
*phrasings* of an already-known-broken question, where an embedding rewrite optimizes for close
to one canonical phrasing. **Recommendation revised accordingly:** not a standalone structural
fix — pair it narrowly with §5, to pin `nat_31`/`nat_32`/`nat_34` (and any other rank-1 exact
match) as a dilution guard before RRF is considered for shipping.

**Neither mechanism is shipped.** This is a measurement and a scoping revision; a ship decision
on the §5+§4 pairing needs a separate go-ahead.

## The exit-127 crash: confirmed environmental, not a code defect — the second time this pattern has appeared

Reproduced independently this session (not just re-read from the prior session's logs): running
the full `pytest` suite in one process crashes at the same point twice — inside
`tests/test_orchestrator.py`'s `@_real_weights` tests, which load the real
`intfloat/multilingual-e5-base` embedder and the AfriqueLlama tokenizer. The actual error, isolated
by re-running that single test alone: `OSError: The paging file is too small for this operation to
complete. (os error 1455)` — a Windows-level memory/pagefile exhaustion, not a pytest bug and not a
regression in `chike/orchestrator.py`. Machine state at the time: ~3.1GB physical / ~522MB virtual
memory free of 8GB physical / 32GB virtual.

**Proven environmental, not assumed, by a split-suite reproduction:** the 1230-test suite run in
two 27-file batches passed clean (614 passed; 609 passed + 2 skipped + 4 deselected + 1 xfailed —
all 1230 accounted for), and each of the four `@_real_weights` tests individually passed when run
alone with memory headroom (including the exact test that failed with the pagefile OSError inside
the full-suite run, re-run standalone immediately after). The failure is a function of how much
model-loading happens back-to-back inside one long-lived process on this specific machine, not of
what the code does. **This is the second time an environment fault in this project has been
mistaken for — or at risk of being mistaken for — a code-state problem**, the first being the R15
verification's local re-embedding segfault (~2.8GB free of 8GB, logged in the R15 deploy entry
below). Both share the same shape: a real, reproducible failure that looks exactly like a defect
until the memory constraint is checked and the same operation is shown to succeed with headroom.
**Standing note for future sessions: before treating a crash inside this project's test/regen
tooling as a code bug, check available physical and virtual memory first** — both confirmed
instances so far were environmental.

---

# 📉 THE R15 CYCLE DEPLOYED AND MEASURED: +1 OF 48 — the retrieval work did not move the number the way the routing work did (2026-08-17)

**Deploy chain, each link verified independently, not on trust:** Kaggle regen succeeded
(221 facts, 0 self-retrieval failures, 26/26 `critical_queries`) and uploaded to HF as one
atomic commit, `3977c186c1`, titled `e5-base RAG index (221x768), built from aae4ccb`. Before
touching production: `git rev-parse HEAD` / `origin/main` / the HF commit title all agreed on
`aae4ccb`, and — the strong check — `rag_facts_text.json` downloaded from the Hub is a
**byte-for-byte match** against `build_fact_texts()` run fresh against this exact checkout
(`scratch/verify_regen_structural.py`). That closes the loop the local-checkout fix
(previous entry) was for: source and index provably came from one commit, not a
commit-message string that happened to agree. (The model-based re-embedding double-check
segfaulted reproducibly on this machine — ~2.8GB free of 8GB, an environment constraint, not
a code defect — and wasn't pursued further given the content-equality result.) Dual-committed
to `chike-inference/` + `kaggle/` at `32c2cd6`, pushed. `chike-inference` stopped and
redeployed fresh (`aae4ccb..32c2cd6`, R16: force-fresh containers, not just `modal deploy`).

## R16 live canaries — the fix that landed, and four that provably could not

nat_43 (GN605A sector-variance) is fixed, confirmed live: *"Ndiyo, kima cha chini cha
mshahara kwa sekta mbalimbali ni tofauti. Thibitisha na GN 605A."* — correctly says yes,
matches the rubric, replaces the prior flat *"Hapana... hakibadiliki"*.

nat_05, nat_33, nat_41, nat_28 — the other four rows this cycle targeted — came back **byte-
identical** to their 2026-08-15 pre-cycle replies. Not "still wrong, differently." The exact
same text, including nat_41's fabricated *"siku 1 tu"* OSHA certificate turnaround, which
predates this entire cycle and which the newly-written, independently-verified
`osha_registration_before_operations` fact (OSH Act 2003 s.16(2), confirmed present in the
index) did not touch at all. The mechanism is not mysterious: `modal_app.py:305` injects
exactly `top_k=3` into the prompt, in production, matching the guard's own cutoff. Round B's
wording pass moved these rows' ranks (documented in the prior C4 entry) but none of the four
crossed into top-3 — nat_43 did. A rank improvement that does not cross `top_k=3` is
**mechanically invisible to production**, not partially helpful. This was asserted as a
possibility when C4 shipped ("costs nothing to ship"); today's canaries are the empirical
confirmation, not the theory.

The SDL-exemption fact answered a live probe ("je mashirika ya kidini yanalipa SDL")
correctly and proportionately — business activity vs purely spiritual activity, appropriately
hedged, no invented number. The four displacement guards (nat_26/27/34/36) held live, byte-
identical to their correct 08-15 replies — the vat_withholding rewrite that would have
regressed nat_27 stayed held back, correctly. nat_37/nat_38 (named pre-existing, not this
cycle's problem) are unchanged and not further broken. The container-freshness OOC probe
(capital gains) refused correctly, confirming `chike_config.json` loads correctly in the live
container — the `[config] chike_config.json not loaded (.../assets\chike_config.json)` line
printed during `modal deploy` is local Windows-path noise from the deploy tool's own import of
`modal_app.py` (`ntpath.join('/root/assets', ...)` locally), not a container-runtime fault;
confirmed by the live refusal working correctly, not just by reading the code.

## The 48, re-run — `eval/results/natural48_rerun_2026_08_17_adjudication.json`

All 48 questions re-run live against the redeployed container. **Diffed programmatically
against the 2026-08-15 baseline, not eyeballed: 47/48 replies are byte-identical. Only nat_43
changed.**

```
CORRECT  28 -> 29   (+1, nat_43)
WRONG     9 -> 8    (-1, nat_43)
CLARIFY   6 -> 6    (unchanged)
PARTIAL   5 -> 5    (unchanged)
```

That is the full live yield of the entire C4 retrieval cycle — the duplicate-key sweep, the
nat_41 OSH Act verification, the SDL-exemption consolidation, the ceiling test, the top_k
sweep, two rounds of CONCISE wording, three merges, three new/rewritten facts, the regen, the
independent verification, the redeploy: **one row, out of six targeted.** This is the
measurement the founder asked for — "the measurement that says whether the retrieval work
moved the number the way the routing work did" — and the honest answer is **it did not**. The
2026-08-11→08-15 routing/compute cycle moved 9 compute-path rows from WRONG to CORRECT in one
pass. This retrieval cycle, working against a structurally different obstacle (facts most of
which don't clear `top_k=3` no matter how they're worded — the fee-shape-dominance and
seven-row-unreachable-at-k=9 findings earlier in this file), moved one.

## THE nat_44 / nat_28 DECISION, now grounded in the 48's result

The withheld `vat_withholding_goods`/`vat_withholding_services` rewrite (round-2 wording,
held back because it regressed nat_27 in local dry-run) would have moved nat_44 33→~4 and
nat_28's rate-half 33→~8 (`scratch/factpath_stage1_round2.json`). Today's result answers the
open question directly: **rank 8 cannot reach a `top_k=3` production system — this is no
longer a local-scoring inference, it's what just happened, empirically, to four other rows
this exact cycle.** nat_44's ~rank 4 is closer but not confirmed to clear 3, and raising
`top_k` itself was already measured and rejected (`top_k` 3→9 reaches **none** of this
seven-row cluster, per the fee-table-dominance finding above, and the two-arm retriever work
separately measured the dilution cost of a wider retrieval slot as 1 recovery vs 86
dilutions — "not a demonstrated fact-path win"). So the trade is: apply the rewrite, take a
**confirmed** regression on a **confirmed-live-correct** row (nat_27, byte-identical-correct
in today's run), for an **unconfirmed, at-best-marginal** chance on nat_44 and a **provably
zero** chance on nat_28. **Recommendation: leave both as-is.** Not a wording problem, and not
a `top_k` problem either — both levers this cycle had have now been tried and both are spent
for this specific cluster. Reopening it needs a structural change (the fee-shape-dominance
30%-of-index-wins-58%-of-slots finding is the more likely lever, not touched this cycle) or
the routing team's approach (deterministic intercept, the way the compute-path defects were
actually fixed) rather than another retrieval-ranking pass.

---

# 🌐 THE REGEN HIT A SHARED, UNAUTHENTICATED RATE LIMIT — fixed in regenerate_rag_e5.py, logged for every other Kaggle harness (2026-08-17)

**What happened:** the R15 regen 429'd twice in one run — once on the commit-SHA
lookup, once on the `locked_facts.json` fetch two lines later — while running from a
**fresh git clone where every file the script needed was already on disk.** The clone
made the fetches redundant, not safer.

## The fix: prefer the checkout, fetch only as fallback

`kaggle/regenerate_rag_e5.py` now checks whether it's running inside a git checkout
with both `scripts/locked_facts.json` and `scripts/precompute_rag_embeddings.py`
already present. If so: use them directly, get the commit SHA via `git rev-parse HEAD`
(no network), zero GitHub requests. Only when no usable checkout exists does it fall
back to the original cache-busted raw-fetch path. This is not just fewer requests —
it makes the clone path **self-consistent**: source and index now come from the SAME
commit by construction, instead of a checkout plus two independent fetches that could
in principle each land a different commit if main moved in between.

## Q1 — can a mid-run 429 leave a partially-built index that still uploads?

Traced every network call in the script. The two SOURCE fetches (`locked_facts.json`,
`precompute_rag_embeddings.py`) both call `raise_for_status()` — a 429 there crashes
before `build_fact_texts()` ever runs, so no half-old-half-new fact set can reach the
embedder. **But the commit-SHA lookup did NOT** — `.json().get('sha', '?')` on a 429
response (which still returns a JSON body, just an error one) silently produces `'?'`
and the run **continues**, printing a HEAD stamp that means nothing. Not the failure
mode asked about, but the same shape: a degraded run that looks complete. Fixed by
adding `raise_for_status()` there too — a 429 on the SHA lookup now crashes loud
instead of shipping an unauditable index.

**The real version of this risk was downstream, at upload, not fetch.** The script
uploaded `rag_embeddings.npy` and `rag_facts_text.json` as **two independent
`api.upload_file()` calls**. These two files must correspond row-for-row — embedding
*i* describes fact_text *i* — and every consumer (`modal_app.py`, `eval.py`) loads
both and trusts that alignment without checking it. A failure between the two calls
(rate limit, dropped connection) would leave the HF dataset repo with embeddings from
the NEW build paired against fact text from the OLD one, or the reverse — silently
misaligned, no exception anywhere, exactly the "silent failure shape" asked about.
Fixed: replaced the two `upload_file()` calls with one `HfApi.create_commit()` call
carrying both files as `CommitOperationAdd` operations — one Hub commit, so either
both land or neither does.

## Q2 — does the HEAD verification still mean anything in the clone path?

No, not as originally written, which is why it changed rather than just adding a local
short-circuit around it. `git rev-parse HEAD` and a fresh `api.github.com` lookup of
`main`'s tip **answer different questions**: the API call says what `main` points to
*right now*; `git rev-parse` says what commit the files *on disk* actually came from.
In the clone path those can disagree — if main moved between the clone and the run,
the API fetch would stamp the index with a SHA the on-disk files were never built
from, a fabricated provenance record that looks exactly as trustworthy as a real one.
`git rev-parse HEAD` is now used whenever the checkout exists, which is the only
version of "what commit was this actually built from" that's true by construction. The
API lookup is kept only for the no-checkout fallback, where there is no local answer
to ask instead.

## Logged as an operational item regardless of scope

**Every Kaggle harness in this project (`eval.py`, `eval_orchestrator.py`, the probe
scripts, this one) bootstraps the same way — unauthenticated `raw.githubusercontent.com`
/ `api.github.com` requests, all sharing ONE per-IP rate budget.** Only
`regenerate_rag_e5.py` was fixed here, because it's the one that just failed. The
others still fetch unconditionally on every run and remain exposed to the same shared
budget; a probe run earlier in a session can spend down the budget a regen needs
later, or vice versa, with no relationship visible between the two failures. Not
auditing or fixing all of them in this pass — named here so the next 429 in a
different script isn't rediscovered as a surprise.

---

# ✅ C4 APPLIED — merges, two new facts, four rewrites landed; two held back on evidence (2026-08-17)

**Applied to `scripts/locked_facts.json` + `scripts/precompute_rag_embeddings.py` +
`kaggle/regenerate_rag_e5.py`. Not yet regenerated — needs the Kaggle GPU step (R15);
everything below is verified against a LOCAL dry-run using the cached e5-base model
(`scratch/local_regen_verify.py`), which mirrors the regen's own gate but does not
replace it.**

## Landed

- **3 merges** (data hygiene, independent of wording): `sdl_rate_2025` deleted, its
  precision folded into `sdl_rate`'s locked_facts.json record (not its CONCISE text —
  see the citation-clutter rule below). `sdl_employee_threshold` deleted (near-duplicate
  of `sdl_threshold`, nothing distinct to preserve). `brela_annual_return_fee` deleted;
  its one genuine unique detail (foreign Section XII, USD 25/month) extracted into a
  new key.
- **3 new facts**: `brela_foreign_late_filing_penalty` (extracted above).
  `osha_registration_before_operations` — genuinely new content, not a rewrite (OSH
  Act 2003 s.16(2), verified against two independent Tanzania government sources
  before writing). `sdl_exemption_categories` — one consolidated Swahili fact
  absorbing 10 real exemption categories previously dropped whole by a noise regex
  that was too broad for content it never read (see below).
- **4 rewrites applied**: `sdl_rate` (nat_05, rank 150→24), `GN605A_sector_count`
  (nat_43, rank 127→**1, clears top-3**), `annual_return_filing_fee` +
  `late_filing_penalty_monthly_fee` (nat_33, best rank 113→25), plus the new
  `osha_registration_before_operations` fact itself (nat_41, rank →5).
- **Noise regex fixed at the mechanism**: `^exemption_category_` (a content-guessing
  prefix) replaced by `_NOISE_KEYS_REVIEWED`, an explicit set of the 10 keys with a
  comment on why each is excluded. The remaining patterns stay regex because they
  target *shape* (bare citation, bare section) which is safe to guess regardless of
  content; a content-bearing family is not.
- **1 positive + 4 negative regen guards** wired into `regenerate_rag_e5.py`'s
  `critical_queries`: nat_43 (the row that clears) as positive; nat_26/27/34/36 as
  displacement negatives, all verified passing in the local dry-run.

## Held back on evidence — nat_44 and nat_28's rate half did NOT land

**This is a correction to the apply-list, found during verification, not a skip.**
`vat_withholding_goods`/`vat_withholding_services` rewrites measured nat_44 33→4 and
nat_28's rate half 33→8 in round 2 — real wins. But the local dry-run (built
specifically to catch this class of thing before Kaggle) found a cost round 2's
stage-1 harness never tested for: the same rewrite pulls **nat_27** (currently
CORRECT — the standard 18% VAT rate, a different question from withholding) into the
same neighbourhood and displaces its fact out of top-3.

Three phrasings were tried to reconcile it:

| variant | nat_27 | nat_44 | nat_28 |
|---|---|---|---|
| round-2 (bare rewrite) | FAIL | rank 4 | rank 8 |
| + explicit "Si kiwango cha kawaida (18%)" contrast | **false PASS** (guard's `18%` substring matched the contrast clause itself — the actual retrieved content was still the withholding fact, not the rate fact) | rank 5 | rank 63 |
| "makato" (deduction) framing | FAIL | rank 9 | rank 27 |

The contrast attempt is the more interesting failure: it would have shipped as a
passing guard while the underlying answer was still wrong — the same shape as the
present_elsewhere/absent overlap and the drift check's own score-threshold finding,
one level down at the level of a single keyword-substring test. **A guard that
matches on a negation clause is not verifying the claim, only the vocabulary.**

Both keys are left OUT of `CONCISE_BILINGUAL_FACTS`, on their original fallback text.
nat_44 and nat_28's rate half stay wrong in production, unimproved from before this
cycle, rather than trading a currently-correct row for them. This is a real,
structural tradeoff — not a wording bug — and needs a decision, not another pass.

## nat_37 / nat_38 — discovered unprotected, not caused by this cycle

The founder's original list of six negative guards included nat_37 and nat_38. The
local dry-run checked both against the **currently deployed** index (unmodified by
anything in this cycle) before wiring anything, and both **already fail** — pre-existing
gaps nobody had verified before because nothing had ever tested them this precisely.
Not wired as guards (a guard for an already-failing row blocks every real win in this
cycle from deploying); named here as a new, separate, unfixed item instead.

## The citation-clutter rule (standing guidance, not a one-off note)

Written into `precompute_rag_embeddings.py`'s module docstring so it survives past this
session: **do not put effective dates, Act/section citations, or statutory-basis
phrasing in CONCISE_BILINGUAL_FACTS text.** Measured directly this cycle — folding
`sdl_rate_2025`'s citation precision into `sdl_rate`'s embedded text pulled it toward
legal-citation-shaped neighbours and away from the conversational question a real user
asks (nat_05 only reached rank 59 with that material included; stripped, rank 24;
stripped AND with the query's own tokens echoed, rank 1 — the ceiling test). That
precision is not lost, it moves to locked_facts.json's own fields (`verified_by`,
`effective_date`, `primary_source`), which R13's training-pair generation reads
directly and does not pass through this embedding at all. Every future fact will be
tempted to include this material in the retrieval text for good reasons — completeness,
auditability — and the rule exists because those reasons measurably lose.

## The sibling-matcher bug this cycle's new keys exposed

Wiring `brela_foreign_late_filing_penalty` into `check_facts_index_sync.py` should have
produced `drift_unpinned` (it is genuinely not indexed yet) — instead it silently
passed as `sibling`. The matcher's sibling check was a raw `startswith()`: a single
generic label like `'brela'` or `'nssf'` (the slug of a CONCISE row that happens to
begin `"BRELA: ..."` or `"NSSF: ..."`) satisfied it against *any* longer key sharing
that first word. Auditing what else this let through found **four `nssf_*` keys and
one `brela_*` key all "verified" against the SAME single row**, when each actually has
its own distinct, correct row elsewhere in the index — the check was giving a real
pass, but not for the reason it claimed, and would have given the same false pass to
an actually-missing key with the bad luck to share a first word. Fixed by requiring the
shorter of the two slugs to carry at least two words before a prefix match counts as a
sibling (`_is_sibling()`); the five real keys were re-verified by reading their actual
rows and pinned as `present_elsewhere` with the correct row numbers. This is the same
lineage as v1→v2→v3→the drift check itself: a matcher that is right more often than it
is checked will eventually be wrong in a way nobody was looking for.

## THE THREE FLAT ROWS — a separate finding, not a residual (nat_24, nat_45, nat_23)

**nat_24 (41→44→37), nat_45 (19→9→9), nat_23 (164→84→87) did not respond to two rounds
of substantially different wording, while nat_05 — same SDL cluster, same rewrite
discipline — went 150→24.** That asymmetry is the finding: something differentiates
these three from a cluster-mate that moved freely, and the ceiling test run so far
(on nat_05, which DID move) cannot answer what. **Per the founder's instruction: when
this is picked up, run the ceiling test ON one of these three rows directly** — not on
nat_05 again — because if a deliberately overfit, query-echoing text still can't move
nat_24, the blocking mechanism is not wording and no further wording pass should be
spent guessing at it. Text held at pre-2026-08-17 wording for `sdl_threshold` and
`wcf_accident_reporting_deadline` deliberately, pending that test. `sdl_rate` (nat_23's
shared target with nat_05) was updated for nat_05's sake and nat_23 still sits deep on
the same new text — proof the text change alone isn't what nat_23 is waiting on either.

## nat_41: the honest version of the class result

The flip from RANKING back to ABSENCE (see "nat_41 flips back to ABSENCE" above) means
**the partition is 8/9 RANKING, 1/9 ABSENCE — not 9/0.** The class claim survives,
slightly weakened: eight of nine WRONG rows genuinely were retrieval failures on
content that was already correct and already indexed. The ninth *looked* like one —
key-adjacent content existed nearby — until someone read what that content actually
said against what the question actually asked, and it didn't match. **That correction
is the interesting part, not the weakening**: it is the same discipline that caught
v1/v2's matcher fault and the sibling-matcher bug above, applied to a human
adjudication step this time instead of a string-matching script. Nothing in this
project's classification has yet been right on the first attempt at 9-for-9; it has
been repeatedly correctable, which is a different and better property.

## Next: the actual R15 Kaggle regen, then the full R16 cycle, then re-run the 48

Everything above is local-only. `scripts/locked_facts.json` and
`scripts/precompute_rag_embeddings.py` are the source of truth; `kaggle/rag_facts_text.json`
and `kaggle/rag_embeddings.npy` (the DEPLOYED index) are untouched until the regen
actually runs on Kaggle and uploads. After that: the full R16 cycle (force-fresh
containers, live canaries exercising the specific changes, negative cases), then
re-run the 48-question natural-register set — **that is the measurement that says
whether this retrieval work moved the number the way the routing work did**, the same
standard the routing/compute-path work was held to at the top of this file.

---

# 📊 THE HEADLINE RESULT OF THIS CYCLE — 39.6% → 58.3% correct, 39.6% → 18.8% wrong

**The number feature work was stopped on, re-measured on the same 48 natural-register questions,
same script, same endpoint, same conditions — a PAIRED comparison, so the difference is the
build.** Full entry and per-row detail below; artifact
`eval/results/natural48_rerun_2026_08_15_adjudication.json`.

| | 2026-08-11 | 2026-08-15 | |
|---|---|---|---|
| **CORRECT** | 19 | **28** | **+9** |
| CLARIFY | 6 | 6 | 0 |
| PARTIAL | 4 | 5 | +1 |
| **WRONG** | 19 | **9** | **−10** |

| path | 2026-08-11 | 2026-08-15 |
|---|---|---|
| **compute** (24) | CORRECT 6 · **WRONG 13** | CORRECT **15** · **WRONG 3** |
| fact (21) | 10 / 1 / 4 / 6 | **byte-identical** |
| refusal (3) | 3 CORRECT | 3 CORRECT |

**37 of 48 replies are byte-identical to the baseline. All ten rows that moved are compute rows,
and every one was a named target of this cycle.** The programme did what it was aimed at and
nothing else.

### The three caveats travel with the number — always

**1. One row departs from its written rubric.** nat_16's `expected_behavior` demands 15% ×
4,000,000 = TZS 600,000; **SAFETY-2 (`8b90b25`) deliberately superseded that** — residency turns
on presence, not permit type, so 600,000 would *also* have been a guess. The reply declines and
names the 183-day test. **By the written rubric it is WRONG: CORRECT 27 / WRONG 10 = 56.3% /
20.8%.** Both figures are in the artifact. Quote either; never quote it without this line.

**2. CLARIFY did not move, and 5 of the 6 are DELIVERY FAILURES** (nat_02, nat_06, nat_11,
nat_17, nat_21) — rows where a figure **was** computable and was not delivered: the
Swahili-numeral + `kila mmoja` extractor gap and the multi-group aggregation gap. Routing passes,
delivery fails, not counted as correct. **Largest single block of remaining work, and nothing
this cycle touched it.**

**3. THE STRATEGIC RESULT — six of the nine remaining WRONG are a fact recited wrongly, not a
route missed** (nat_05, nat_28, nat_33, nat_41, nat_43, nat_44, nat_45 — royalties 15% for a
services VAT question, 6% for a goods question, an invented *"siku 1"*, a fabricated absolute
date, minimum wage stated as not varying by sector). **The routing-and-guard method that took
the compute path from 13 wrong to 3 has NO purchase on them**: there is no engine to route to
and no working to check a body against.

> **The routing programme is complete, and the remaining error has moved house.** Two-thirds of
> what is left is fact recall (D1 / RAG / `locked_facts`) and one-third is extraction. **Neither
> is addressable by another cue list.** Any plan that answers this measurement with more routing
> work is answering the previous measurement.

It is **not** a gate result and not a random sample of real traffic — the 48 were authored and
are register-realistic by construction. It is the only end-to-end natural-register measurement
this project has, taken the same way twice.

---

# 🧪 THE FEE-ROW MASK: MEASURED, AND IT DOES NOT WORK (2026-08-17)

**"A retrieval-side mask being testable offline against all 48 is a strong argument if it
performs." Measured. It does not perform.** `scratch/feemask_experiment.py`,
`scratch/feemask_experiment.json`.

## The design

Exclude the 66 fee-shape index rows (`<key>: <number> <unit>`) from the general retrieval
pass; re-admit them only through a second, fee-only pass gated on a narrow fee-intent cue
(`gharama`, `ada`, `faini`, `kusajili kampuni`, `hisa`…) present in the full question. Zero
stored data changes — no regen, no GPU, deployable as an ordinary code change.

## The result: 0 of 9 fixed

Every target row was re-checked against its **confirmed exact index entry** (the same rows
established in the class analysis and its correction). Masking the 66 fee rows out of general
retrieval **surfaced none of them**:

```
[nat_05] STILL MISSING   baseline [121,122,123]  ->  masked [148,200,215]
[nat_23] STILL MISSING   baseline [120,123,126]  ->  masked [148,201,216]
[nat_24] STILL MISSING   baseline [117,174,200]  ->  masked [137,198,200]
[nat_28] STILL MISSING   baseline [25,150,173]   ->  masked [25,55,151]
[nat_33] STILL MISSING   baseline [197,199,203]  ->  masked [197,199,201,203,204,209]
[nat_41] STILL MISSING   baseline [170,171,203]  ->  masked [151,163,201]
[nat_43] STILL MISSING   baseline [131,185,197]  ->  masked [185,197,209]
[nat_44] STILL MISSING   baseline [25,173,174]   ->  masked [25,151,196]
[nat_45] STILL MISSING   baseline [150,171,203]  ->  masked [19,151,201]
```

**Removing the fee rows didn't promote the correct fact — it promoted a DIFFERENT wrong one.**
The 58%-of-top-3-slots statistic describes the INDEX'S composition in aggregate; it is not proof
that a fee row is *specifically* what blocks each of these nine. **For most of them it isn't —
fee-shape rows are a symptom of general index breadth, not the mechanism.** Measured full-index
rank of the correct fact against all 217 rows, not just the masked subset
(`scratch/factpath_full_rank.py`, `scratch/factpath_full_rank.json`):

| row | correct-fact rank / 217 |
|---|---|
| nat_45 | 19 |
| nat_41 (row 72) | 22 |
| nat_44 | 33 |
| nat_28 | 33 |
| nat_24 (row 7) | 41 |
| nat_33 | 113 |
| nat_43 | 127 |
| nat_41 (row 53) | 128 |
| nat_05 | 150 |
| nat_23 | 164 |

Not uniform: five of nine sit deep (100+ of 217 — genuinely swamped by the index's general
breadth, no single competitor family to blame, consistent with "outranked by ~150 non-fee rows").
The other four sit far closer (19–65) — a small phrasing/vocabulary fix is plausibly enough to
clear top-3 for those, a materially different-sized job than the deep five. This reframes C4:
reachability rewrites are not competing with fee-row segregation for the same effect — they are
**the actual fix**, and whatever segregation benefit exists rides inside them as a byproduct of a
correctly-phrased fact outranking a fee row on its own terms, not from removing the fee row.

## And it is not free — 3 confirmed regressions among currently-CORRECT rows

Checked against every fact-path/refusal-path row's actual pool contents, not just top-1 order
(`scratch/feemask_pool_check.py`):

| row | needs | in masked pool? |
|---|---|---|
| nat_34 (fee-cue matched) | company reg fee + name reservation fee | ✅ preserved via the fee-only second pass |
| nat_26, nat_38 | VAT threshold / EFD-always-for-VAT | ✅ preserved (non-fee facts) |
| **nat_27** | VAT 18% rate | ❌ **dropped from the pool** |
| **nat_36** | EFD 11M threshold | ❌ **dropped from the pool** |
| **nat_37** | no minimum EFD transaction value | ❌ **dropped from the pool** |

nat_27/36/37 have no fee-cue in their questions, so the fee-only second pass never fires for
them — and whatever fee row was quietly co-occurring in their baseline pool (Swahili duplicate
facts and near-neighbours often sit inside the 66) is gone with no replacement. **Three currently
CORRECT rows lose their supporting fact for zero rows fixed.** (nat_46/47/48 also flagged by
the coarse top-1 diff but are refusal-path — retrieval doesn't drive their answer, so they carry
no real risk; excluded from the count above.)

## The choice, on the founder's own standard

*"Measure the mask against the regen and choose on evidence."* The mask is cheap and ships
without a regen — and it fixes 0 of 9 while introducing 3 new misses. **It loses on its own
terms before the comparison to a regen is even needed.** Fee-row segregation stays queued, but
as part of the C4 reachability rewrite + R15 regen, not as a retrieval-side patch. This is a
negative result worth keeping for the same reason the two 2026-08-16/17 stopped builds were: it
is the discipline finding something cheap that still didn't work, rather than something
expensive that wouldn't have.

---

# 🔒 THE DRIFT CHECK IS BUILT — and it immediately found what the manual pass missed (2026-08-17)

`scripts/check_facts_index_sync.py` + `tests/test_facts_index_sync.py`, wired into the normal
`pytest` gate (1229 passed, up from 1227). **A fix inherits credibility from the fix it
replaces, and v2 was never subjected to the check it was built to perform — that is the exact
failure this script exists to close, and it is not a metaphor: it is the literal mechanism.**

**The check does not score.** The 2026-08-17 correction already found that the embedding-cosine
score cannot separate present-elsewhere facts from genuinely-absent ones — the `present_elsewhere`
bucket's *lowest* score (0.851) sits *below* the `absent` bucket's *highest* (0.886). A threshold
that excludes every false positive also excludes true positives — the same shape as the RAG
similarity-floor finding, discovered independently twice in one day. **So the check resolves
each locked fact one of three ways: exact key match, sibling key match, or a PINNED,
human-verified verdict re-checked every run against the CURRENT index content** (a substring
check against the pinned row — if the index changes under a pin, the check fails rather than
trusting a stale row number).

**The concrete cost, stated plainly per the founder's ask:** the drift check I was about to write
this morning would have compared `locked_facts.json` **keys** against index **keys**. That check
would have failed CI on all 24 `present_elsewhere` facts below — every one of them is real,
correct, retrievable content, sitting in the index under a different key, usually in Swahili.
**A key-based drift check would have shipped the exact bug it was built to catch, as a test.**

## It immediately found 20 more keys neither v1, v2, nor v3 ever adjudicated

The first run of this script did not come back clean. It flagged 20 keys beyond the 28 that v2
had originally flagged — because **v3 only re-checked the 28 keys v2 had already flagged**. Any
key v2 got right by accident — matched by exact or prefix key when it happened to line up, never
independently verified against index *content* — was never looked at by anyone. This script
checks all 246, unconditionally, every time, which is what exposed them.

**This is the same shape as v2 inheriting v1's boundary, one level up.** v1 flagged 57. v2
re-checked those 57 and corrected the number to 28 — but never independently re-swept the other
190 keys v1 had passed; it only re-examined what v1 had already flagged wrong. v3 then re-checked
v2's 28 and corrected again to 13 — but likewise never independently re-swept the 219 keys v2 had
passed; it only re-examined what v2 had already flagged. This script is the first pass in the
sequence to check all 246 unconditionally rather than re-auditing the previous pass's flagged
subset, and that is exactly why it found 20 keys none of the first three ever looked at. **A
correction inherits the scope of what it corrects unless it re-derives that scope from scratch —
three iterations of this drift-check lineage adopted the previous pass's boundary unexamined, and
each one was a smaller, more confident number that was still incomplete for the same reason.**
This is the same shape as the credibility point above (a fix inherits credibility from the fix it
replaces) — a correction that narrows a wrong number earns trust for the number, not for the
boundary of what it checked, and those are different claims that are easy to conflate.

All 20 were adjudicated the same way as the original 28 — read the locked value, search the
index for the content, confirm by eye — and are now pinned in the script with their row and a
verification substring. Two are genuinely new gaps: `gn487a_marriage_no_exemption` (the index
covers dual-nationality/naturalisation under Cap.357 but never marriage) and `gn487a_signatory`
(the minister's name has zero hits anywhere in the index).

## The honest, final accounting — 246 locked facts (not 247: `_unresolved_items` is metadata too)

| | count |
|---|---|
| exact key match | 189 |
| sibling key match (`sdl_rate` → `sdl_rate_2025`) | 9 |
| **present_elsewhere** (right content, different key/language) | **24** |
| **genuinely absent** | **15** |
| fragment (bare clause — `"13 (7)"`, a bare year — never independently answerable) | 5 |
| pending R15 regen (written this session, by design) | 4 |

**189 + 9 + 24 = 222 of 246 (90%) are actually reachable.** The real gap is **15**, not 28, not
57 — and 10 of the 15 are one family (SDL exemption categories). This is the number that should
be quoted going forward; the 28 and the 13 in the entries above it are both superseded.

## What makes this different from v1/v2/v3, and why it's the one that sticks

v1, v2, and the embedding pass were each a **script run once, read once, and quoted**. This is a
**pinned, committed, re-run-every-time** set of verdicts, checked against the live index content
on every `pytest` invocation — not just today's. The pin for each `present_elsewhere` key carries
the specific row number and a literal substring pulled from that row, so if the index is
regenerated and a fact's phrasing changes or the fact silently drops out, the pin goes stale and
the check **fails**, rather than continuing to report "present" against a row that no longer
says what it used to. `test_pending_r15_keys_are_still_pending` closes the adjacent trap: when
the R15 regen for the four presumptive-tax facts finally runs, those keys will start resolving
via exact match and **fall out of the `pending_r15` bucket silently** unless PINNED is edited —
so a dedicated test asserts none of the `pending_r15` pins have gone stale, forcing the pin set
itself to get updated rather than just quietly becoming true.

---

# 🚀 PRESUMPTIVE TAX IS LIVE — and the BEFORE is the coverage argument in one screen (2026-08-17)

Full R16 cycle on `chike-inference`: `app stop --yes` → `PYTHONIOENCODING=utf-8 PYTHONUTF8=1
modal deploy` → 14 live canaries against fresh containers. **14/14 pass. 5/5 negatives
byte-identical to BEFORE.** Artifacts `scratch/presumptive_live_{before,after}.json`.

## The BEFORE: eight questions off ONE statutory table, eight different wrong rates

Nothing about these is a near miss. Production did not decline, did not hedge, and did not
repeat itself — it invented a plausible percentage each time, in fluent Swahili, with
*"Thibitisha na tra.go.tz"* attached:

| asked | production said | correct |
|---|---|---|
| mauzo 50M | *"kodi ya makadirio ya **asilimia 30** ni TZS 15,000,000"* | TZS 1,750,000 |
| mauzo 30M | *"kodi ya makadirio ya **asilimia 5**"* | TZS 1,050,000 |
| mauzo 5M, no records | *"**asilimia 15%** ya mauzo hayo"* | TZS 100,000 |
| mauzo 9M, records | *"chini ya TZS 200M/mwaka, **hakuna kodi ya makadirio**"* | TZS 150,000 |
| tax consultant, 20M | *"kodi ya zuio ya **asilimia 6**, sawa na TZS 1,200,000"* | outside the regime entirely |
| mauzo 150M | *"kodi ya makadirio ya **VAT** ni **asilimia 6.5%** = TZS 9,750,000"* | above the ceiling; presumptive does not apply |
| mauzo 8M | *"**asilimia 6** ni TZS 480,000"* | depends on records — must ask |

**TZS 15,000,000 demanded from a trader who owes 1,750,000.** An 8.6× overstatement, delivered
with a source link. This is what "no fact behind it" looks like in production, and it is the
strongest evidence yet for the coverage argument: **the failure mode of an uncovered domain is
not silence, it is confident invention.**

## The AFTER

```
Mauzo yangu ni milioni 50 kwa mwaka. Kodi ya makadirio ni kiasi gani?
  -> Kodi ya makadirio = 3.5% × TZS 50,000,000 = TZS 1,750,000
     (kiwango hiki ni kile kile ukiwa unatunza kumbukumbu au la)

Mauzo yangu ya mwaka ni milioni 9 na natunza kumbukumbu. Kodi ya makadirio?
  -> Kodi ya makadirio = TZS 90,000 + 3% × (TZS 9,000,000 − TZS 7,000,000) = TZS 150,000

Mimi ni mshauri wa kodi, mauzo yangu ni milioni 20 kwa mwaka...
  -> Hapana. Kodi ya makadirio haitumiki kwa wataalamu huru...

Mauzo yangu ni milioni 8 kwa mwaka. Kodi ya makadirio ni ngapi?
  -> ...je unatunza kumbukumbu za mahesabu...? Niambie, nami nitakupa kiasi kamili.
```

**TZS 1,750,000 and not 1,710,000 is the stale-consolidation catch reaching a user.** The canary
forbids `1,710,000` explicitly, so the Cap 332 R.E. 2019 table cannot come back without turning
a canary red.

**The 8M row is the records axis behaving correctly**: it asks, because there the two columns
differ by TZS 220,000. The 12M row does not ask, because there they do not. Latency after the
first cold call is **0.8–1.0s** — no model on the path.

## The negatives, including the one the founder named

**lp_09, the daladala row, is byte-identical before and after.** The transport schedule
(para 2(5)) is a different table this engine does not implement; routing it here would compute
the turnover table on a **tax** figure of TZS 250,000 and answer **"TZS 0"** to a daladala owner.
The 5,595-row sweep caught that before deploy and `_PRESUMPTIVE_VETO` closed it; this canary is
now the live proof.

**Stated plainly: lp_09 is still WRONG.** It answers *"kiwango... cha asilimia 25%"*, an invented
rate, exactly as it did before. It passes as a NEGATIVE because the requirement was that the new
route not steal it, and it did not. **A negative canary proves a change didn't spread. It does
not launder the row it protects.** The transport schedule is now a named coverage gap.

> **This is the right general standard, not a one-off note.** Every negative canary in every
> R16 cycle this project has run — concord closure's `cl_06`/`cl_07` count-question guards,
> D-FIDELITY-4's controls, this cycle's lp_09 through lp_13 — proves the SAME narrow claim: *the
> new code did not change this answer.* None of them prove the answer was correct to begin with,
> because none of them were written to. A canary set that is all green reads, at a glance, like
> a system that is working; the honest read is narrower — a system where this particular change
> didn't make anything WORSE. Where a negative happens to sit on a row that was already wrong
> (lp_09 today; it will not be the last), that has to be said explicitly, in the entry, next to
> the green — a passing board is not the same claim as a correct one, and it is easy to let a row
> of checkmarks stand in for the second when it only ever proved the first.

`lp_10`/`lp_11` (the `mapato`-not-`mauzo` row and the regime-election row) and `lp_12` (EFD
precedence) are likewise byte-identical. `lp_14` is the CONTAINER-LOADED diagnostic: `nunua
shamba` lives in `chike_config.json` and **not** in the hardcoded fallback, so its refusal proves
these containers read the config — the check that settled the 2026-08-07 stale-container
incident.

⚠️ **Still pending, and it is a founder step: the R15 Kaggle regen.** The engine is live, but the
four locked facts written for this domain are **not retrievable** until
`kaggle/regenerate_rag_e5.py` runs. The compute route does not need them; a user who asks about
presumptive tax in words the router does not catch still gets the fact path, and the fact path
still cannot see those four facts.

---

# 🧭 TWICE IN TWO DAYS, ANALYSIS-BEFORE-BUILD STOPPED WORK THAT WOULD NOT HAVE WORKED (2026-08-17)

**This is the argument for the discipline itself, and it is now a measured argument rather than
a stylistic preference. Two builds were queued, both plausible, both scoped, and both were
stopped by a measurement that cost hours — not by taste, and not after the fact.**

| the build that was queued | what it would have cost | what the measurement found |
|---|---|---|
| **D1 — a new adapter**, queued behind **6 of the 9** remaining WRONG rows | a Kaggle training cycle | **0 of 9 are OVERRIDE.** The adapter never contradicted a retrieved fact. It would have fixed **none** of them |
| **A similarity floor on an absolute score**, agreed as the pre-pilot safety net | a build, a regen and a pilot gate | correct facts score **0.765–0.809**, irrelevant top-1s score **0.790–0.859**. **There is no cut point** |

**Neither was a bad idea. Both were the obvious next move.** What made them wrong was invisible
without instrumenting the thing itself — and in both cases the instrument was cheap relative to
the build it stopped.

## 1️⃣ ZERO OVERRIDE — the model was reciting what it was handed, not hallucinating

All nine WRONG rows were partitioned by mechanism against **production's own retrieval**
(full entry below). **OVERRIDE = 0. UNUSED = 0.** Every failing row is either a fact that exists
in the index and is not retrieved (**RANKING, 9/9** — corrected the same day from 7/9; the
other 2 were bucketed ABSENCE by a matcher fault and are also RANKING. **ABSENCE is now 0/9.**
Correction entry above).

Three of the wrong answers are **verbatim index rows**: nat_05's *"TZS 260,000"* is
`company registration fee 3`, nat_41's invented *"siku 1"* is
`registration certificate processing time new: 1 days`, nat_28's *"15%"* is `royalties wht rate`.

> **"Fabricated" was the wrong word for these answers all along.** The figure the user was given
> exists, verbatim, in our own index — attached to a different question. A hallucination is a
> model defect and its fix is training. **A misretrieval is an index defect and training cannot
> touch it.**

**That is a training cycle not spent, found by measurement.** It should be quoted whenever a new
adapter is proposed for this cluster.

## 2️⃣ THE FLOOR CANNOT BE AN ABSOLUTE SCORE

Scoped 2026-08-16 as the pilot blocker: refuse below a threshold. The score distribution makes
that impossible — the correct fact for one question scores *lower* than the irrelevant top-1 of
another, so **any threshold that excludes the wrong facts also excludes the right ones**. The
floor still ships before any pilot, but on a **margin** (top-1 vs top-2 separation) or on a
**re-ranked index**. Had it shipped as scoped it would have passed its own tests and refused the
questions it was built to protect.

**MARGIN IS RETIRED (2026-08-22) — do not pick this back up.** Of the two floor designs named
above, margin was the last one still untested. It was measured (`scratch/item5b_margin_guard.py`,
full account in `docs/decisions/0002-retrieval-structural-scoping.md` §5(c)) and it does not just
fail to separate confident-correct from uncertain-wrong — **it inverts.** `nat_32`, correct today,
has the single smallest margin of all 21 fact-path questions measured (0.0002), while three
known-buried rows score larger margins than every currently-correct row. A margin threshold built
to trust confident dense hits would flag the wrong rows as the trustworthy ones. **Neither of this
entry's two named floor designs is viable now** — margin inverts, and re-ranking (the other) is
still unbuilt and unmeasured (§6 of the same ADR). The next attempt at a floor needs a third
signal, not a retry of either of these two.

---

# ❌ CORRECTION, SAME DAY: "WE CORRECTED FACTS THAT WERE NEVER RETRIEVABLE" WAS WRONG (2026-08-17)

**Committed in `7ad737d`, disproved two hours later, corrected here before it was acted on.
Both keys it named as evidence ARE in the index. The third matcher in the same investigation
was wrong in the same way as the first two.**

| key | `7ad737d` claimed | actually |
|---|---|---|
| `efd_threshold_tzs_11m` | ❌ no trace in the index | **index #58** — *"Kizingiti cha kuanza kutumia mashine ya EFD: mauzo ya TZS 11,000,000 (milioni kumi na moja) kwa mwaka"* |
| `sdl_threshold` | ❌ no trace in the index | **index #7 / #65** — *"Kizingiti cha SDL ni wafanyakazi 10 au zaidi... Si 11, si 4."* |

**The mechanism.** The v2 matcher counted a fact as reachable if its key slug matched an index
slug **or a distinctive figure from its value appeared in the index**, with the figure regex
`\d[\d,]{2,}` — three characters minimum. A fact whose value reads *"10 employees"* or
*"TZS 11 million"* produces **no marks at all** and drops into the unreachable bucket
automatically. **Both headline examples were facts stated in words rather than comma-formatted
figures.** And PROGRESS records that #58 exists precisely *because* it was written: the eval_347
fix added a Swahili-first `CONCISE_BILINGUAL_FACTS['efd_threshold_tzs_11m']` entry. **The
correction did land. My instrument could not see it.**

### The adjudicated answer — read row by row, not thresholded

`scratch/factpath_sync_gap_v3.json`. Each of the 28 was embedded against the shipped index and
its top matches **read**, with a written verdict per key so a future reader can disagree with a
row rather than with a cut-off.

| verdict | n | what it means |
|---|---|---|
| **present_elsewhere** | **9** | the content IS in the index, usually **in Swahili under a different key** |
| **absent** | **13** | real compliance content, genuinely missing |
| fragment | 4 | the locked "fact" is a bare clause — `"13 (7)"`, `"commits an offence"` — not an answer to any question and never should have been counted as one |
| pending_r15 | 2 | written 2026-08-16, absent **by design** until the Kaggle regen runs |

⚠️ **SUPERSEDED AGAIN, SAME DAY — see "THE DRIFT CHECK IS BUILT" below.** This pass only
re-checked the 28 keys v2 had already flagged; it never independently checked the other 218.
The committed drift check found **20 more unpinned keys** neither this pass nor v2 had looked
at. Final, checked-every-run numbers: **24 present_elsewhere, 15 absent, 5 fragment, 4
pending_r15.** The number worth quoting from here on is **15 of 246**, not 13 of 247.

**The real gap is 13 of 247, and 10 of the 13 are ONE family** — the SDL exemption categories
(diplomatic missions, religious institutions, registered schools, TaESA trainees, farm
employers…). The other three are legal citations: Cap 438 s.11, Cap 82 s.19, and the Workers
Compensation Act Sura 263. *(Numbers above superseded — see the callout.)*

**`gn487a_prohibited_activity_3` was nearly the fourteenth.** The embedding put activities 9, 2
and 5 above it, because the locked value is English while index #182 states it **in Swahili with
no `prohibited activity` prefix** — *"Kutengeneza au ukarabati wa simu na vifaa vya
kielektroniki…"*. Found only by reading all fifteen GN487A rows directly. **The third matcher
artifact in one investigation, caught by the same method as the other two: stop trusting the
matcher and read the rows.**

### What survives, and it is the part worth keeping

The dramatic claim is dead. The structural one is not, and it is now better evidenced:

> **THE RAG INDEX IS NOT A PROJECTION OF `locked_facts.json`.** 9 facts are reachable only under
> a **different key, in a different language**, and 13 are not there at all. The two files have
> no defined relationship, and **nothing in the pipeline compares them** — not
> `validate_dataset.py`, not `check_locked_facts.py`, not the gate.

**That is exactly why the drift check is still the right thing to build, and why it must compare
CONTENT rather than keys.** A key-based check would have reported all 9 present_elsewhere rows as
failures — the same false alarm, wired into CI where it would be believed. **The check I was
about to write would have shipped this bug as a test.**

### ⚠️ Method: 57 → 28 → 13, and only the first correction happened before publication

| pass | matcher | said |
|---|---|---|
| v1 | key-slug **prefix** | 57 of 247 missing (23%) |
| v2 | key-slug **exact** + figure-in-blob | 28 of 247 (11%) — **committed in `7ad737d`** |
| v3 | **embedding match, then read every row** | 13 of 247 (5%) — **but only re-checked v2's 28** |
| v4 | **`check_facts_index_sync.py`, pinned + re-run every `pytest`** | **15 of 246 (6%)** — see "THE DRIFT CHECK IS BUILT" below |

**The 57→28 correction is the one I told the founder about as a method success. It happened
before publication. The 28→13 correction did not — it went into PROGRESS, the board and a
message before the instrument was checked. Neither did 13→15: v3 only re-adjudicated the 28
keys v2 had already flagged, so it inherited v2's blind spot for every key v2 happened to get
right by luck rather than by checking.** The lesson is not "matchers are hard"; it is that
**v2 was built to correct v1 and was never itself subjected to the check it was built to
perform** — and neither, fully, was v3. An instrument that corrects another instrument needs
the same scrutiny as the first
one, and it did not get it because it arrived wearing the authority of a correction.

The reason this is a correction entry rather than a method note is exactly that difference. The
2026-08-15 rule stands and was under-applied here: **a number produced by a matcher is a claim
about the matcher until something independent confirms it.**

---

# 🎯 AND THE CLASS ANALYSIS GETS STRONGER: RANKING 9/9, ABSENCE 0/9 (2026-08-17)

The same matcher fault ran through the class analysis, which resolved a locked key to an index
row by **key-slug prefix**. It bucketed `nat_24` and `nat_41` as **ABSENCE** — "we hold no such
fact" — when both facts are in the index in Swahili. Re-run against the content rows
(`scratch/factpath_class_recheck.json`):

| row | question | content | rank in the 217-row index | retrieved? |
|---|---|---|---|---|
| **nat_24** | *"tuko na watu 9 tu mishahara milioni 4…"* | SDL threshold = 10+ employees (#7, #65) | **41 / 217**, **65 / 217** | **NO** |
| **nat_41** | *"nimefungua karakana mpya nina muda gani wa kusajili…"* | OSHA registers ALL workplaces (#72, #53) | **22 / 217**, **128 / 217** | **NO** |

**ABSENCE 2/9 → RANKING 2/9. The partition is now RANKING 9 · ABSENCE 0 · OVERRIDE 0 ·
UNUSED 0.**

**Every single remaining wrong answer is a fact we hold and failed to retrieve.** The corrected
result is *stronger* than the one it replaces and points the same way harder: it removes the last
2/9 that argued for writing new facts, and the fix is entirely retrieval.

And nat_24 is the cleanest illustration of the fee-row dominance in the whole set. A question
about SDL and NSSF for **9 employees** retrieves, at top-1:

```
0.837  vat deferment minimum value: 10,000,000 TZS
0.831  minimum monthly contributions maternity benefit: 36 monthly_contributions
0.828  company registration fee 1: 95,000 TZS
```

while *"Kizingiti cha SDL ni wafanyakazi 10 au zaidi"* — the exact answer, correctly written,
correctly indexed — sits at **rank 41**.

## nat_41 flips back to ABSENCE — but not for the reason v1/v2 thought (2026-08-17, same day)

The C4 reachability work (below) found that nat_41's "content" — rows 72/53, *"OSHA registers ALL
workplaces, no minimum headcount"* — **answers a different question than the one asked.** nat_41's
question is *"nimefungua karakana mpya nina muda gani wa kusajili sehemu ya kazi"* — a **deadline**
question (how much time do I have to register), not a **headcount-threshold** question. Verified
against two independent Tanzania government sources (`procedures.tiseza.go.tz`, cross-checked by
search): OSH Act 2003 s.16(2) requires registration **before** commencing operations — a fact that
did not exist anywhere in the index, under any key, before today.

So nat_41 is genuinely **ABSENCE** — just not the ABSENCE v1/v2 meant. v1/v2's key-slug matcher
called it absent because no key *named* the right thing. This morning's recheck called that wrong
because *related* content existed at rows 53/72. Both were reasoning about whether content existed
near the key; **neither checked whether the content that existed actually answered the question
asked.** nat_24 (the recheck's other flip) holds up under this stricter check — `sdl_threshold`'s
content genuinely is the 10-employee answer nat_24 needs, just outranked (confirmed by the ceiling
test below reaching rank 1 on the same content). nat_41 does not.

**The corrected partition: RANKING 8/9 · ABSENCE 1/9 (nat_41) · OVERRIDE 0 · UNUSED 0.** The
"0/9 need new facts" line above is superseded — one row did, and the reason it looked like RANKING
is the general lesson: **a ranking failure and a genuine absence look identical from the outside
when a superficially related fact sits nearby. Only checking whether the retrievable content
actually answers the question — not just whether something with an adjacent key or topic exists —
distinguishes them.** This is the same discipline as the present_elsewhere/absent pins in the drift
check, applied one level deeper: content presence is necessary but not sufficient, relevance to the
specific question is a separate check that has to be made by reading, not by matching.

# 📜 A CONSOLIDATED ACT IS NOT THE CURRENT LAW — a rule for whoever encodes the next schedule

**Written as a rule because it will recur, and because the failure mode is silent.** Full entry
with the working below; the rule is this:

> **A consolidated / Revised Edition Act is a SNAPSHOT AT ITS REVISION DATE. The amending Finance
> Act governs. Read the amending Act, not the consolidation, and never a practitioner summary of
> either.**

Cap 332 R.E. 2019 — hosted on **tra.go.tz itself** — still prints the pre-2022 five-band
presumptive table. Finance Act 2022 s.72 replaced it. Both are "the statute"; only one is the law.

| turnover | stale consolidation (R.E. 2019) | governing text (FA2022 s.72) |
|---|---|---|
| TZS 50,000,000 | 450,000 + 3.5% of the excess = **1,710,000** | 3.5% of turnover = **1,750,000** |

**Every figure above TZS 11,000,000 would have been wrong**, encoded from a primary government
source, and nothing downstream could have caught it. Reading the Act was ordered to check a
typo (`11,000,0000`); **the typo was cosmetic and the table was wrong.**

The corollary holds for the regulator's own summaries: TRA's *"At a Glance 2025/26"* prints a
Class A *"Up to 5 → 120,000"* row for the transport schedule that **the enacted FA2024 s.46(a)
does not contain**. Pinned by `test_the_stale_consolidated_table_would_have_been_wrong`.

---

## 🎯 THE FACT-PATH FAILURES ARE ONE CLASS, AND IT IS RETRIEVAL — NOT RECALL, NOT THE ADAPTER (2026-08-17)

**The analysis the founder asked for before the three fact-set coverage items were written, on
the reasoning that "if retrieval or override is the mechanism, adding five domains of facts may
not fix the answers." That reasoning was right, and the answer is retrieval.**

All nine WRONG rows from the 2026-08-15 re-run, partitioned by mechanism using **production's
own retrieval** — the same `rag_embeddings.npy` and `rag_facts_text.json` that ship in
`chike-inference/`, the same `intfloat/multilingual-e5-base` (cached locally), the same
`query: ` prefix, the same cosine top-3, and the same decompose→pool(9) the orchestrator runs.
`scratch/factpath_class_analysis.json`.

| mechanism | meaning | count |
|---|---|---|
| **RANKING** | the correct fact **is in the index** and is **not retrieved** | ~~7 / 9~~ **9 / 9** |
| ~~**ABSENCE**~~ | ~~no fact in the index answers it~~ | ~~2 / 9~~ **0** |
| OVERRIDE | the fact was retrieved and the reply contradicted it | **0** |
| UNUSED | retrieved, not contradicted, simply not applied | **0** |

⚠️ **CORRECTED THE SAME DAY.** The two ABSENCE rows were a matcher fault, not a missing fact —
this script resolved a locked key to an index row by **key-slug prefix**, and both facts are in
the index in **Swahili under a different key**. Re-checked against the content rows: neither is
retrieved, so both are RANKING. See *"AND THE CLASS ANALYSIS GETS STRONGER"* at the top. **The
corrected partition is stronger, not weaker — every remaining wrong answer is now a fact we hold
and failed to retrieve.**

### The model was not hallucinating. It was reciting what it was handed.

This is the part that changes the plan. Three of the wrong answers are **verbatim retrieved
facts**:

```
nat_05  reply says "TZS 260,000"   <- rank 3 in its pool: `company registration fee 3: 260,000 TZS`
nat_41  reply says "siku 1"        <- rank 1 in its pool: `registration certificate processing
                                      time new: 1 days`
nat_28  reply says "15%"           <- rank 1 in its pool: `royalties wht rate: ... 15% ...`
nat_44  reply says "6%"            <- a services rate offered to a GOODS question
```

**Zero rows in the OVERRIDE bucket.** The adapter is not ignoring a correct fact sitting in its
prompt; it is being handed the wrong fact and repeating it faithfully. **D1 — a new adapter —
would not have fixed a single one of these**, and six of the nine remaining WRONG were on the
board waiting for exactly that.

> **"Fabricated" was the wrong word for these answers all along. They are TRACEABLE. The
> figure the user was given exists, verbatim, in our own fact index — attached to a different
> question.** A hallucination is a model defect and its fix is training. A misretrieval is a
> corpus-and-index defect and its fix is neither.

### It is not a top-k problem — the correct fact is buried

Rank of the correct fact in the full 217-row index (`scratch/factpath_rank_depth.json`):

```
nat_45  wcf_accident_reporting_deadline    rank  19/217   score 0.793  (top 0.845)
nat_28  vat_withholding_services           rank  33/217   score 0.806  (top 0.837)
nat_44  vat_withholding_goods              rank  33/217   score 0.809  (top 0.845)
nat_33  brela_annual_return_fee            rank 113/217   score 0.787  (top 0.832)
nat_43  GN605A_sector_count                rank 127/217   score 0.765  (top 0.808)
nat_05  sdl_rate_2025                      rank 150/217   score 0.768  (top 0.831)
nat_23  sdl_rate_2025                      rank 164/217   score 0.772  (top 0.848)
```

Raising `top_k` from 3 to 9 reaches **none** of them. This is the same shape as the C4
reachability item ("the relief denial ranks #64 for the question that needs it") — now measured
across seven rows instead of one, and confirming C4 was not an isolated case.

### 30% of the index wins 58% of the retrieval slots

The pattern in every failing pool is the same: short `<key>: <number> <unit>` fee-schedule
rows. Measured over all 48 questions (`scratch/factpath_feetable_dominance.json`):

| | |
|---|---|
| fee-shape rows in the index | **66 / 217 = 30.4%** |
| questions where a fee row is **top-1** | **24 / 48 = 50%** |
| fee rows' share of all top-3 slots | **83 / 144 = 58%** |

**Eighteen of those rows are trademark fees** — opposition notices, series-of-marks renewals —
which no WhatsApp trader has ever asked about and none of the 48 questions touches. They are
short, semantically thin, and numerically flavoured, so they sit close to any question
containing a magnitude. **They are crowding out the payroll, VAT and OSHA facts that users
actually ask about.**

### And the similarity floor, as scoped, would have shipped and not worked

The floor was scoped on 2026-08-16 as the pre-pilot safety net: refuse below a score
threshold. **The scores make that impossible.** Across the 48 questions the top-1 score band is
**0.790–0.859** — and the *correct* facts in the failing rows score **0.765–0.809**. The
correct fact for one question scores LOWER than the irrelevant top-1 of another.

> **Any global threshold that excludes the wrong facts also excludes the right ones. There is
> no cut point.** A floor can still be built — but on a MARGIN (top-1 vs top-2 separation) or
> on a re-ranked index, not on an absolute cosine score.

**This is exactly what the founder ordered the analysis to find out, and it arrived one step
before the money was spent.** The instruction was *"if retrieval or override is the mechanism,
adding five domains of facts may not fix the answers, and we'd want to know that before writing
them"* — the same reasoning applies one item further along, to the floor.

### The second gap: locked facts the index cannot reach

⚠️ **THE NUMBERS IN THIS SECTION ARE SUPERSEDED — the honest figure is 13, not 28.** The table
below is the v2 matcher's output, kept because the correction entry at the top of this file
refers to it. `sdl_threshold`, `efd_threshold_tzs_11m`, `OSHA_annual_inspection` and six others
listed here as missing **are in the index, in Swahili, under a different key.** Read
*"CORRECTION, SAME DAY"* before quoting anything below.

`scratch/factpath_sync_gap.json`. **The RAG index is not a projection of `locked_facts.json`:**

| | count |
|---|---|
| locked facts | 247 |
| index rows | 217 |
| exact key match in the index | 190 |
| present only under a sibling key (`sdl_rate` → `sdl_rate_2025`) | 9 |
| value figure appears somewhere in the index | 20 |
| **no trace in the index at all** | **28** |

Among the 28: **`sdl_threshold`, `sdl_employee_threshold`, `efd_threshold_tzs_11m`,
`osha_registration_threshold_b004`, `OSHA_annual_inspection`, all twelve SDL exemption
categories**, and the two facts written yesterday (expected — R15 regen pending). Two of the
nine WRONG rows (nat_24, nat_41) are directly caused by this.

⚠️ **THE 23% FIGURE THIS NEARLY BECAME.** A first pass matched index entries by key-slug prefix
and a second by exact slug, and they disagreed — `sdl_rate` is absent as a key while
`sdl_rate_2025` is present, so one matcher said "indexed" and the other "missing", producing a
headline **57 of 247 (23%)**. The honest content-level number is **28 (11%)**. Re-derived
before it was written down anywhere, because a number produced by a sloppy matcher is precisely
how a wrong number enters this record — the same discipline as the "52 eval / 385 train rows"
correction, applied to my own instrument on the same day it was built.

### What this makes the fix, and what it does NOT make it

Ordered by measured effect, all three needing one R15 Kaggle regeneration:

1. **Segregate the fee-schedule rows from general retrieval.** 30% of the index, 58% of the
   slots, near-zero conversational demand. Largest measured effect, smallest change.
2. **Reachability rewrites (C4).** CLAUDE.md already records the mechanism from
   `paye_bands_with_examples`: a fact embedded WITHOUT the `key: ` prefix, Swahili-first with
   the value at the front, retrieves far better. Seven rows now show what the prefix form costs.
3. **Close the 28-fact index gap**, and add a check that FAILS when `locked_facts.json` gains a
   key the index does not carry — this gap was invisible because nothing compares the two.

**NOT the fix: a new adapter, more training pairs, or a cleverer refusal.** Zero OVERRIDE rows
is a strong negative result and it should be quoted whenever D1 is proposed for this cluster.

### Consequence for the three fact-set coverage items — they stay paused

Service levy bound, market-stall exclusions and TIN were sequenced behind this analysis. **The
analysis says writing them changes nothing on its own**: a new fact would enter a 217-row index
where fee rows take 58% of top-3 slots and correct facts sit at rank 19–164. They should be
written **with** the retrieval fix and regenerated in the same R15 cycle, not before it.

*(Caveat, stated rather than buried: this retrieval is RECOMPUTED, not the retrieval that
actually ran on 2026-08-15. It is deterministic and the index has not changed since, but it is
a reconstruction. MEASUREMENT-GAP-1 also still applies — a fact being in the prompt is not the
same as it being applied — which is why OVERRIDE and UNUSED were kept as separate buckets
rather than merged into "the model's fault".)*

---

## 📚 COVERAGE ROUND 1 — presumptive tax shipped as an ENGINE; licence fees left uncovered on purpose (2026-08-16)

**The first work in this project aimed at a coverage gap rather than a wrong answer.** The
2026-08-16 readiness assessment measured what happens when a real trader asks something the
corpus does not hold (`scratch/coverage_gap_2026_08_16.json`):

| | result |
|---|---|
| questions from an ordinary duka owner's month | 12 |
| passed the OOC classifier (→ the model answers) | **12 / 12** |
| took a deterministic route | **0 / 12** |
| had a fact behind them in `locked_facts` or the RAG index | **0 / 12** |

And `retrieve_facts` (`modal_app.py:281`) applies **no similarity floor** — it returns the top-3
at any score, pooled to 9. So the behaviour on an uncovered question is not "sina uhakika"; it
is a confident answer synthesised from the three nearest unrelated facts. That is the `nat_05`
mechanism (a fabricated TZS 260,000 BRELA fee answering an SDL question) as a *generic*
property of the fact path, not a row-specific bug.

Founder sequence: **coverage and the fact path first, similarity floor after** — *"a floor makes
us safe on questions we can't answer, but answering them is better than refusing them."* The
floor still ships before any pilot.

### Scoping first, and it changed what got built

`scratch/coverage_scoping_2026_08_16.md` — five domains scoped against primary sources before a
line was written. The scoping is what separated the three that are national and answerable from
the two that are council-by-council and mostly are not:

| domain | national vs council | shape | verdict |
|---|---|---|---|
| presumptive/turnover tax | **100% national** | **rules engine** | ✅ **SHIPPED** |
| business licence renewal date | **100% national** | one fact | ✅ **SHIPPED** (R15 regen pending) |
| business licence FEES | fee national, collection council | lookup table | 🛑 **LEFT UNCOVERED — source, see below** |
| local-government service levy | **cap national, rate council** | fact set | bound only, never an amount |
| market stall dues | **council by-law, 180+ LGAs** | fact set | **not coverable for amounts** |
| TIN registration | **100% national** | fact set, procedural | coverable, not yet written |

---

## 🧾 A CONSOLIDATED ACT IS A SNAPSHOT, AND THE SNAPSHOT WAS STALE (2026-08-16)

**The single most valuable thing this round produced, and it came from one founder
instruction:** *"Read Cap 332's First Schedule before encoding any band, per your typo catch."*
The instruction was aimed at a typo. It caught a wrong table.

Three documents, all primary, all authoritative-looking, **and they do not agree**:

| source | 11M–100M band |
|---|---|
| **Cap 332 R.E. 2019** (tra.go.tz's own copy of the Act) | 11,000,001–14,000,000 → TZS 450,000 / 230,000+3%; **14,000,001–100,000,000 → 450,000 + 3.5% OF THE EXCESS** |
| **TRA "Taxes and Duties at a Glance 2025/26"** | 11,000,001–100,000,000 → **3.5% of turnover** |
| **Finance Act 2022 (Act No. 5 of 2022) s.72(a)(ii)** | **3.5% of turnover** — and it is the amending Act, so it governs |

At a turnover of TZS 50,000,000 the stale table gives **TZS 1,710,000** and the current one
gives **TZS 1,750,000**. Both are "the statute". Only the amending Act distinguishes them.

**Every Finance Act from 2020 to 2025 was read directly** (fa2020 · fa2021 · fa2022 · fa2023 ·
fa2024 · fa2025, all fetched from tra.go.tz or mof.go.tz): only FA2022 touches para 2(3), and
FA2025 does not touch presumptive tax at all. That is why the table shipped is FA2022's.

> **THE FINDING: a revised-edition Act is a CONSOLIDATION AS AT A DATE, and reaching for it is
> the natural move precisely because it looks like the whole law. It is the same shape as
> INSTRUMENT-LIE #11 — a number believed to be about the thing it names — in the source
> domain rather than the measurement domain. The remedy is the same and is cheap: for any
> figure, find the amending Act, not the consolidation.**

**And TRA's own summary is not the statute either.** FA2024 s.46(a) substitutes Class A of the
transport schedule as *"Up to 15 → 250,000"*; TRA's 2025/26 at-a-glance prints *"Up to 5 →
120,000; 6 to 15 → 250,000"* — a row the enacted text does not contain. Not in scope here (the
transport schedule is vetoed, below), but recorded: **the second-most-natural source to trust
disagrees with the enacted law in the same document family, on the same page.**

The at-a-glance also prints the third band's ceiling as **`11,000,0000`** — one digit too many,
the typo that started this. The statute reads *"Turnover of Tshs. 11,000,001/= but does not
exceed Tshs. 100,000,000/="*, so the intent was never in doubt; the point is that **the check
run to resolve a typo is what surfaced the wrong table.**

One incidental confirmation from the same fetch: TRA's 2025/26 document states *"A person whose
turnover is TZS 11,000,000/= or above shall issue fiscal receipt"* — **`efd_threshold_tzs_11m`
re-confirmed from a source we were not previously using.** The 11M-vs-14M question stays closed,
and the 14,000,000 that has haunted it turns out to be a *presumptive band boundary* from the
pre-2022 table, which is very likely where the confusion came from in the first place.

---

## ✅ PRESUMPTIVE INCOME TAX — a deterministic route where there was nothing at all

`chike/rules_engine/presumptive.py`, `routing.detect_intent -> "presumptive"`,
`orchestrator._answer_presumptive`, 20 authored probes, 62 tests.

**Source of every figure:** Income Tax Act Cap 332 First Schedule para 2, as substituted by
Finance Act 2022 s.72, in force 1 July 2022.

**Why an engine and not facts:** it is a band table with marginal arithmetic in two bands —
`paye.py`'s exact shape — and **an engine answer bypasses generation entirely, so it is immune
to whatever the fact-path class analysis turns out to find.** That is the direct answer to the
ordering question the founder raised: two of the five domains can be built without waiting.

**Four exits, and one of them is deliberately NOT taken.** The records-kept axis only changes
the figure between TZS 4,000,001 and 11,000,000 (`records_status_matters`); outside that window
both columns of the statutory table are identical. So an unstated records status is **not a
missing input, it is an input the answer does not use**, and clarifying anyway would be exactly
the delivery failure the 48-question re-run found in five of its six CLARIFY rows. `pt_09`
pins it: TZS 12,000,000 with records unstated answers **TZS 420,000** rather than asking.

**The exclusions are as load-bearing as the bands, as instructed.** FA2022 s.72(a)(i) puts
*"independent professionals and providers of, technical, management, construction and training
services"* outside the regime. A professional told they owe presumptive tax gets a wrong answer
carrying the engine's authority, wrong in the dangerous direction — they are on the ordinary
individual rates instead. `applicable=False` is a correct answer here, not an error.

### The sweep found three wrong answers before any user did

5,595 rows, pristine-HEAD worktree BEFORE vs patched AFTER
(`scratch/presumptive_blast_diff.json`). The **first** version — presumptive cue + magnitude,
no ownership gate — diverted **four** corpus rows, of which **three would have been answered
wrongly**:

```
tier1a_inc_tax_deep_002  "...ina mapato ya TZS 40,000,000 ... Ninatumia mfumo wa kodi ya
                          makisio?"      -> asks WHICH REGIME, and states `mapato`, not `mauzo`
tier1a_inc_tax_deep_003  "...nitajua vipi ikiwa ninapaswa kutumia presumptive tax AU MFUMO
                          WA KAWAIDA?"   -> the ELECTION question of para 2(1)(c)
cleaned_pairs_batch_014  "'presumptive tax rate class a' kwa magari ya abiria inayosema
                          TZS 250,000"   -> the TRANSPORT schedule, para 2(5)
```

The third is the worst: para 2(5) is a per-vehicle table this engine does not implement, the
TZS 250,000 in the question is a **tax** figure, and computing the turnover table on it returns
**"kodi ya makadirio = TZS 0"** to a daladala owner. Narrowed to {turnover vocabulary +
presumptive cue + magnitude, minus a transport/election veto}, the sweep is **0 intent changes**
and all three keep their fact route.

**`mapato yangu` is deliberately absent from the presumptive ownership gate even though the VAT
arm carries it.** `mapato` can mean profit; the bands run on turnover; 3.5% of profit is not
3.5% of turnover. The narrower list is the price of the engine's authority, and
`test_mapato_is_not_mauzo` states the asymmetry so nobody "fixes" it by copying the VAT list.

⚠️ **AND THE CLEAN SWEEP IS WEAK EVIDENCE, WHICH IS R17'S OWN POINT.** Zero intent changes
after narrowing does not mean zero risk — **the corpus was authored before this domain existed
and mostly cannot contain its vocabulary.** The 20 authored probes are the load-bearing
instrument here, exactly as with the object-concord round.

---

## 🛑 LICENCE FEES — NOT obtainable from a primary source, so they stay uncovered

Founder instruction: *"If the current schedule isn't obtainable from a primary source, say so
and we'll leave it uncovered rather than ship an eleven-year-old table."* **It is not
obtainable.** The chain, each link checked rather than assumed:

1. **TanzLII's consolidation is as at 31 July 2002** and says so on its own cover page:
   *"There are outstanding amendments that have not yet been applied: Act 2 of 2014, Act 15 of
   2015, Act 4 of 2018, Act 12 of 2023."*
2. The only machine-readable text of the substituted First Schedule is the **2014 Bill
   supplement** (`trade.tanzania.go.tz`) — **a Bill, not an Act**, and not on the whitelist.
3. The **enacted** Finance Act 2014 exists on the MoF repository — and is a **scanned image**:
   45 pages, **361 characters** of extractable text. OCR of a fee table is a transcription job
   needing human verification, not a fetch.
4. **Finance Acts 2020–2025 do not touch the fee schedule** (all six read directly). FA2025
   amends the Business Licensing Act at ss.3 and 4 and adds **s.14A — the statutory parent of
   GN 487A** (*"A licensing authority shall not issue a business licence to a non-citizen
   unless such business is allowed for non-citizens"*), but not the fees.
5. **Acts 15/2015, 4/2018 and 12/2023 remain unchecked and unobtained**, and any of them could
   have moved the figures.

**So the honest position is: the fee is national and binding on councils** — Cap 290's Schedule
permits *"Business Licence fee for general merchandising as prescribed under the Business
Licensing Act"* and puts *"Fees exceeding the prescribed fee"* in the shall-not-impose column —
**but we cannot state a current amount.** The resolution path is not another fetch: it is BRELA
directly, or OCR plus the three unchecked Acts, with human sign-off.

**What DID ship from this domain: the renewal date.** Finance Act 2014 s.5 substituted
Business Licensing Act s.3(4): *"Every business licence granted under this Act shall expire on
the 30th day of June of each year."* One national fact, no variation, no arithmetic — and it
answers *"lini"* for every trader in the country.

---

## ⚖️ THE SERVICE LEVY: WE ARE NOT HEDGING BECAUSE WE ARE UNSURE. THE LAW IS UNCLEAR ABOUT THIS USER.

Recorded as a finding in its own right at founder request, because the two are different and
the second is worth saying out loud.

**Local Government Finance Act CAP. 290 R.E. 2019, s.7(1)(u)** (and s.6 in identical terms for
district councils), verbatim:

> *"all monies derived from the service levy payable by **corporate entities or any person
> conducting business with business licence** at the rate **not exceeding 0.3 percent** of the
> turnover net of the value added tax and excise duty"*

**The Schedule made under s.16(1)** — whose second column is what a council **shall not**
impose, s.16(2) — item **4. Levies (a)**:

| MAY impose | SHALL NOT impose |
|---|---|
| Service levy charges to **corporate entities** of cap 0.3% on turn-over, net of VAT and excise duty | • In excess of cap of 0.3% of turnover<br>• **Non-corporate entities** |

**The operative section says "or any person conducting business with business licence". The
Schedule says councils shall not impose it on non-corporate entities. A sole-proprietor duka
owner is a non-corporate entity — so the statute disagrees with itself precisely about our
single most common user.**

Two consequences, and they are different in kind:

1. **The rate is a CAP, not a rate.** Each council sets its own figure at or below 0.3%. Saying
   *"the service levy is 0.3%"* is wrong in every council that charges less. This is an
   ordinary council-variation limit.
2. **The liability is genuinely unsettled in the text.** No amount of careful phrasing on our
   side resolves a conflict between a section and its own Schedule.

> **A hedge that comes from OUR uncertainty is a weakness to be fixed. A hedge that comes from
> the LAW's uncertainty is the answer, and stating it plainly — "the Act's Schedule excludes
> non-corporate entities; confirm your own status with your council" — is more useful to a
> trader than either a confident yes or a confident no.** Filing both under "hedged copy"
> would have lost the distinction.

---

## 🧨 DECOMPOSITION FABRICATES A SUB-QUESTION THE USER NEVER ASKED (found 2026-08-16, PRE-EXISTING, unfixed)

Walked into while building the presumptive route; **confirmed on pristine HEAD `05e68b5`, so it
is not caused by it.** `decompose_query`:

```
IN   "Mauzo yangu ya mwaka ni milioni 9, sina kumbukumbu za mahesabu. Kodi ya makadirio?"
OUT  ['Mauzo yangu ya mwaka ni milioni 9',
      'Mauzo yangu ya mwaka ni milioni sina kumbukumbu']      <- TEXT THE USER NEVER WROTE
                                                              <- and the QUESTION is GONE
```

The unit preamble (`milioni`) is carried onto a comma clause that is not an enumeration item.
**This is a category worse than the documented preamble-drop (B2): it does not merely lose a
sub-question, it invents one**, and the invented one then goes to the fact path as though the
user had asked it. The PAYE and SDL analogues (*"Mshahara wangu ni 900000, sina mkataba wa
ajira. PAYE ni ngapi?"*) are untouched, so the trigger is narrow.

Pinned as `test_the_comma_enumeration_split_corrupts_this_question`, an **`xfail(strict=True)`
asserting the CORRECT behaviour** — so it fails loudly the day someone fixes decomposition, and
it never asserts that the broken behaviour is right. (The alternative — a test asserting the
current output — is the antipattern CLAUDE.md records: a test that instructs future maintainers
not to fix a real defect.) **New board item; deliberately not fixed inside a coverage commit,
because decomposition sits under every route.**

---

## 🔌 TWO OPERATIONAL FINDINGS FROM THE SOURCE FETCH (2026-08-16)

**1. `WebFetch` cannot read the two most important primary-source hosts. `curl` can.** This is
the more valuable of the two, because the failure mode is not "no data" — it is *falling back to
practitioner summaries*, which is the exact thing the source discipline exists to prevent.

| host | WebFetch | curl |
|---|---|---|
| `www.tra.go.tz` (Acts, at-a-glance, TAA) | ❌ `Parse Error: Invalid header value char` — every request | ✅ **200** |
| `tanzlii.org` (HTML) | ❌ 403 | ❌ 403 (browser UA too — Cloudflare) |
| `media.tanzlii.org` (source PDFs) | ❌ 403 | ✅ **200** |
| `www.mof.go.tz` | ✅ (binary) | ✅ |
| `repository.mof.go.tz` | ❌ certificate chain | ✅ with `-k` |

Working recipe: `curl -sS -L --max-time 180 -o x.pdf <url>` then `pypdf`. Two TRA quirks —
a missing file 302-redirects to **http**, which then fails on port 80 (so a `302` means "wrong
filename", not "blocked"), and the 2024/25 at-a-glance is a **scanned image** (36 pages, 143
characters) while the 2025/26 one has a real text layer.

**2. The whitelist has real gaps, and no change is needed if we source with discipline.**
`scripts/check_sources.py` `TRAINING_WHITELIST` carries `tra.go.tz`, `brela.go.tz` and
`tanzlii.org` — enough for all five domains. It does **not** carry `mof.go.tz`,
`tamisemi.go.tz`, `parliament.go.tz`, `trade.tanzania.go.tz` or `business.go.tz`. The mof.go.tz
copies of Cap 290 and Finance Act 2022 used above are **scoping convenience mirrors**; any pair
must cite the TanzLII or TRA original.

---

## ⏭️ NOT DONE, AND WHY

- **R15 IS PENDING AND THE FACTS ARE NOT LIVE.** Four facts were added to
  `scripts/locked_facts.json` (`business_licence_expiry_30_june`,
  `presumptive_tax_bands_2022`, `presumptive_tax_ceiling_100m`,
  `presumptive_excluded_services`) and **the RAG index has not been regenerated**, so the fact
  path still cannot retrieve any of them. `kaggle/regenerate_rag_e5.py` runs on Kaggle
  (local network blocks the e5 download) — founder step. **The engine does not depend on it**;
  the licence renewal date does.
- **Not deployed.** No R16 cycle has been run for this change, so none of it is live.
- **The fact-path class analysis (item 4) has not started**, and the three fact-set coverage
  items wait on its result, as agreed.

---

## 🔁 THE CONCORD CENSUS CAUGHT THE FIRST CUE LISTS ADDED AFTER IT SHIPPED (2026-08-16)

`test_every_cue_with_a_person_form_has_its_concord_counterpart` failed on the presumptive
commit, one day after the object-concord round closed. **This is the test working exactly as
designed** — it derives counterparts from the grammar and demands the list recognise them, so a
new list cannot quietly repeat the old omission. Four real 1pl gaps, added:

```
_KEEPS_RECORDS_CUES      "tuna kumbukumbu za mauzo"
_EXCLUDED_SERVICE_CUES   "biashara yetu ni ushauri" · "kampuni yetu ya ujenzi"
                         "biashara yetu ya ujenzi"
```

**And it also produced nine false alarms, which is the more interesting half.** The generator
read `ninaTUnza kumbukumbu` as {`ni` + `na` + object infix `-tu-` + stem `nza`} and offered
`ninakunza` / `ninamnza` / `ninawanza`. **None is a Swahili word** — the verb is `-tunza` and
its stem simply begins with `tu`.

> **This is the `mkataba` / `wakati` / `kuhusu` nesting trap the object-concord round was built
> to defeat, arriving INSIDE the instrument that round shipped — and catching it on the very
> first cue list added afterwards.** Host qualification (subject+tense) is what lets
> `_object_counterparts` reject nesting words, and it cannot separate `ni-na-tu-nza` from
> `ni-na-tu-ma` (`ninatuma`, "I send", where `-tu-` genuinely IS an object infix) without a
> verb lexicon this repo does not have.

Recorded as an explicit `_NOT_MORPHOLOGY` exclusion with that reasoning, deliberately kept
SEPARATE from `_WITHHELD_OBJECT` — which has its own pin asserting its exact membership, so a
generator artefact could not be smuggled in beside four real deferred gaps.

---

# 🔄 SESSION HANDOVER — 2026-08-15 (second session)

**HEAD `5d7d88c` · working tree clean · in sync with origin/main.**

| app | serving | note |
|---|---|---|
| `chike-inference` | **`baf77b3`** | stopped and redeployed SIX TIMES this session under R16; `oc_06`/`df_06`/`wl_06`/`neg_04`/`d5_06` confirm the container read `chike_config.json` and is not warm-stale |
| `chike-whatsapp` | **`ad1ed50`** | NOT redeployed and does not need to be — it reaches the model through `modal.Cls.from_name`, a lazy lookup, so the routing fix below is already live to WhatsApp users |

Suite **1166 passed, 0 failed, 0 skipped** (`pytest -p no:randomly`). Pristine `ba09165` in the
**same worktree**: **1026 passed, 0 failed, 0 skipped**. Read INSTRUMENT-LIE #11 before quoting
either number.

## ✅ OBJECT CONCORD CLOSED (`73f2f9f`) — items C and A3 were one defect

Swahili marks the OBJECT with an infix between tense and stem, and the class is closed:
`-ni-` (me), `-ku-`, `-m-` (`-mu-`/`-mw-`), `-tu-`, `-wa-`. nat_08 is *"wana**NI**kata …
mshahara wangu"*; nat_04 is *"ina**NI**anza lini"*. `_NSSF_EMPLOYEE_CUES` held **seven members
and zero person-marked ones**, so every `-ni-` deduction question fell to the `total` default
and **doubled the answer**.

**HOST-QUALIFIED, NOT BARE — and the sweep is why.** The obvious closure (bare infix+stem, one
substring covering the inflection family, R17 step 4) is unsafe here and measurably so:

| bare form | corpus hits | what they actually are |
|---|---|---|
| `kuhusu` | 154 | the PREPOSITION "about" |
| `wakat` | 116 | `waKATi` (time/when) |
| `kukat` | 48 | `kukata`, the infinitive — no object at all |
| `mkat` | 36 | `MKATaba` (employment contract) |
| `nikat` | 12 | 6 of them `nikatae` (if I refuse) |
| `linianza` | — | *"lini anza"* written as one word — **not morphology at all** |

Requiring a HOST — subject+tense, negative, or `hu-`/`ku-` — kills every one. **The negative
branch had to exclude `-ku-` as an object**: with the negative tense in an optional slot,
`haKUkata` matched anyway, because the regex simply backtracked and spent its `ku` on the
object slot. **An optional group cannot forbid anything.** Cost of the exclusion is
`hakukuhusu`, deliberately traded away as rare and genuinely ambiguous.

`parse_count` gained the copula surface (`tuko kumi na mmoja`) in the same commit, because the
routing fix alone would only move nat_04 from a wrong answer to a wrong question — clarifying
for a headcount the question already states.

**R17:** 5,538-row sweep — 1 route change, 49 party changes (**44 inert**: route is
`paye`/`sdl`/`none`, party never consulted), 21 applicability changes, **0 in_scope changes** —
plus **22 authored probes**, which are load-bearing here and not a ritual (see the correction
below). `eval/refusal_gate/object_concord_in_scope_022.jsonl`, `scratch/oc_blast_diff.json`,
`scratch/oc_reachability.json`.

### ⚠️ THE ENGINE IS FIXED. nat_08's USER-VISIBLE HEADLINE IS STILL WRONG.

This is the one probe of twelve that did not pass, and it must not be filed as a pass.
`scratch/oc_live_before.json` / `scratch/oc_live_after.json`, verbatim:

```
BEFORE  A: … unachotakiwa kukata ni TZS 130,000 (20% ya 650,000).
           NSSF = 20% × TZS 650,000 = TZS 130,000 (mwajiri 65,000 + mfanyakazi 65,000)

AFTER   A: … unapaswa kulipa TZS 130,000 kwa NSSF (sehemu ya mwajiri ni TZS 65,000 na
           sehemu ya mfanyakazi ni TZS 65,000).
           NSSF (sehemu ya mfanyakazi) = 10% × TZS 650,000 = TZS 65,000 — …
```

**The deterministic working is now correct — `party=employee`, TZS 65,000. The generated prose
still leads with TZS 130,000.** The router change landed and is verified; the generation
ignores the engine sitting directly beneath it. C was therefore **closed in the router and open
in the answer** — for the length of one deploy cycle. nat_04 by contrast was clean end-to-end
immediately: prose and working both say SDL applies at **3.5%** on a stated 11.

**The visible half was closed the same day by D-FIDELITY-4 (`25cd94f`, entry below), and NOT by
D1.** The reframe is the load-bearing part: D1 owns the fact path preferring a memorised number
**when there is no engine output at all**. Here there IS engine output, correct and immediately
below the prose — which is the **D-FIDELITY family's** territory and exactly the case those
guards were built for. Filing it under D1 would have parked a live wrong headline behind the
next adapter.

This row is still the cleanest demonstration on record that **route-correct is not
outcome-correct** — the same shape as INSTRUMENT-LIE #6, reconfirmed with the engine on the
correct side of it.

## 📐 CORRECTION TO THE PREVIOUS HANDOVER — "52 eval / 385 train rows exercise this" was wrong

The previous handover said the object infix was **well measured**, and made that the reason an
R17 sweep here would be *"real evidence rather than a formality — the exact opposite of
SAFETY-2."* **That was backwards, and the number was an artefact.**

It came from a bare `(na|me|li|ta)(ni|ku|tu)` scan, which matches `kaMPUNI`, `kiWAngo`,
`kuTUmika`, `waKATi`, `inaMAANisha` — **none of which contains an object infix**.
Host-qualified, the corpus carries **~120 real occurrences, ~78 of them `-husu` alone, and
ZERO for `-ku-`/`-mw-`**. So the sweep is real evidence for `-husu` and **nearly blind for
`-kata` and `-anza`** — which is the SAFETY-2 situation after all, and why the 22 authored
probes were the load-bearing instrument rather than the formality.

**Recorded as a correction and not folded into the fix, because an inherited measurement that
nobody re-derived is exactly how a wrong number survives.** The handover carried it forward in
good faith; one scan re-run would have caught it, and the scan cost less than the sentence.

## 🔎 FOUND BY THE SWEEP — four unlogged wrong numbers, and they were never four defects

Not part of the fix summary. These were on no list, and the sweep is the only reason they are
known at all:

| row | question | was |
|---|---|---|
| `ngapi_04` | *"mshahara wangu 800000 pensheni **nakatwa** ngapi"* | working at the 20% total, TZS 160,000 |
| `rc_17` | *"nikitaka **kumkatia** mchango wa uzeeni, ni shilingi ngapi"* | TZS 140,000, plus a fabricated *"mwajiri anachangia TZS 35,000"* |
| `rc_01` | *"…yeye **anakatwa** kiasi gani"* | party `total` |
| one training row | `cleaned_pairs_batch_015.jsonl` — *"Mshahara wa TZS 350,000 **unakatwa** NSSF kiasi gani?"* | party `total` |

**All four are the same 2× party-default overstatement as nat_08 — so they were not four
independent defects but four unlogged instances of one.** That is precisely what a class-level
fix is supposed to catch and what the gate never surfaced: each row individually looked like a
plausible NSSF answer, and only enumerating the class made them one thing. A fifth instance
(`oc_10`, `mkataba … nakatwa`) came from the authored probes, in a sentence containing the
`mkat` nesting trap the host qualification exists to reject.

## 🪞 INSTRUMENT-LIE #11 — a suite number is a statement about a MACHINE AT A MOMENT, not about the code (2026-08-15)

The previous handover recorded **"1025 passed, 1 skipped"** on HEAD, and this session inherited
two expected failures believed to be a paging-file `OSError`. The founder asked for the control
to be run **on pristine HEAD in the same worktree**, so it would be exact rather than
remembered. It was run, by `git stash` and `git stash pop`:

```
pristine HEAD (stashed)   1026 passed, 0 failed, 0 skipped   (179s)
with the patch            1058 passed, 0 failed, 0 skipped   (288s)
```

**The control did not confirm the remembered failures. It removed them.** The two failures were
gone and the skip had become a pass — on unchanged code. A PC shutdown between sessions cleared
both. Nothing about `73f2f9f` caused it and nothing about `ba09165` prevented it.

> **Every "suite passed" number is a statement about a machine at a moment, not a statement
> about the code.** It belongs in this table because it is the table's exact shape: a
> measurement believed to be about the thing it names. `1025 passed, 1 skipped` was read as a
> property of the commit; it was a property of that laptop, that afternoon, that paging file.

This is the **third** environment-caused measurement fault in nine days, after the cp1252
console that aborted a deploy and destroyed a canary artifact (R16) and the `Select-Object`
pipe that killed a BEFORE run before it wrote its file (R16). Those two were about a console
standing between a measurement and its file; **this one is about a number that was never
re-derived at all.** The remedy is the same and is cheap: **re-run the control, never quote it
from a handover.** The C7 network-tests-in-the-unit-suite hazard (below) is the same family and
is still open.

## Findings carried forward, unchanged

**A. THE THREE AXES** — a lexical guard has three independent axes (**concepts, spellings,
inflections**) and completeness on one says nothing about the other two. **Object concord was
the third instance and it is now closed, which strengthens the finding rather than retiring
it: the 2026-08-15 audit enumerated five paradigms and this was not one of them.** OPEN
QUESTION, still logged and still unanswered: are there more axes? **Register and word order**
remain the candidates — a list keyed on `nimeuza ardhi` is equally blind to a passive
(*"ardhi ilishauzwa"*) or a topicalisation (*"ardhi, niliiuza mwaka jana"*). Neither has been
measured.

**B. THE GENERATIVE TEST'S BLIND SPOT — now has its instrument.**
`test_every_cue_with_a_person_form_has_its_concord_counterpart` derives a counterpart **from an
existing member**, so it closes PARTIAL coverage and is blind to ABSENT coverage. C survived
the 2026-08-15 closure because its class was at **0%, not 30%**. The fix is the **grammar-derived
census test** shipped in `73f2f9f`, which enumerates the class from the grammar rather than from
the list — and it was proven against pristine HEAD before it was trusted:

```
CENSUS nssf_party:         FAILS — blind to 5/5: [ni, ku, m, tu, wa]
CENSUS asks_applicability: FAILS — blind to 2/5: [m, wa]
_NSSF_EMPLOYEE_CUES   7 members, 0 carry an object infix  <- nothing to derive from
_NSSF_TOTAL_CUES     10 members, 0 carry an object infix  <- nothing to derive from
```

`scratch/oc_census_pristine_head.json`. **A test written after a fix is worth very little until
you have watched it fail before it.**

## ▶️ WHERE THE NEXT SESSION PICKS UP

**EVERYTHING IN THIS HANDOVER'S QUEUE IS CLOSED.** `_WAGE_PAY_CUES` (`32917f4`), the worker
clarification copy (`571cf1d`), A2 (`2ee31f5`) and D-FIDELITY-5 (`baf77b3`) all shipped, each
with its own R16 cycle. **P2 is closed** and the 48-question re-run at the top of this file is
the measurement that closes it. Both pilot blockers named on 2026-08-14 (P1 silent-drop, P2
compute cluster) are now closed.

**The next decision is the founder's, not the queue's: whether to start the pilot.** A readiness
assessment was requested and delivered 2026-08-16 against current state; the corpus-coverage
measurement it rests on is `scratch/coverage_gap_2026_08_16.json` — **12 of 12 questions from an
ordinary duka owner's month pass the OOC classifier, 0 of 12 take a deterministic route, and
0 of 12 have a fact behind them in `locked_facts` or the RAG index — while `retrieve_facts`
applies NO similarity floor and injects the three nearest facts anyway.**
Read that before scheduling any further defect work: it is the one part of the product the 48
questions cannot speak to, because the 48 were authored against domains we hold facts for.

*(Superseded, kept for the reasoning it carries.)* **`_WAGE_PAY_CUES` first — ahead of A2, by founder order, on stakes.** The gap is already
measured (`scratch/oc_wage_gap.json`): *"**wanani**lipa laki mbili kwa mwezi je ni halali
kisheria"* routes to `none`, while the employer-side controls `namlipa` / `nimemlipa` route to
`minimum_wage`. **This is the th_16 class from the employee's side** — an employee asking
whether their own wage is lawful does not reach the deterministic minimum-wage route, and
th_16's own history says what the generative path does with that question: four of six
candidate wordings **fabricated TZS 765,900 as a legal maximum wage**, and one of the "before"
answers instructed an employer to claw back lawfully paid wages. **Arguably the highest-stakes
question this product will ever get.**

Go straight to the fix — the measurement is done — **but the sweep is MANDATORY, not
confirmatory.** This is the list whose first version stole **five real gate questions with a
bare `mshahara`**; it has already demonstrated it can be over-broad, so a clean sweep is the
entry price and authored probes are still required on top of it (R17 step 2).

**Then A2**, on its own terms: an **open lexical set, not a class**. `mfuko`,
`serikali inachukua`, `kupeleka kwa TRA` are synonyms for a levy and no paradigm will ever
generate the next one, so it gets the failure-driven treatment. It is the costliest of what
remains — **three rows, three confident wrong figures, no working on any of them** (nat_09
states the employee share as *"TZS 960,000 (80%)"* of a 1.2M salary; nat_13 gives TZS 52,000
where PAYE on 900,000 is 103,000; nat_14 gives TZS 28,000 where PAYE on 350,000 is 6,400).

**The ten withheld counterparts stay withheld.** They were deliberately kept out of the NSSF
commit behind a pin that FAILS when someone closes them
(`test_the_withheld_object_counterparts_still_name_a_live_defect`). That guard is not
housekeeping — it is what stops the next session quietly declaring the class closed. Leave it.

Both need their own R16 cycle against `chike-inference` only. Still queued behind those and
unchanged: the `MODAL_API_TOKEN`/`HF_TOKEN` fingerprints, full percent exclusion, narrowing the
four over-broad OOC phrases (`kipande cha ardhi`, `naagiza bidhaa`, `forodha`, `nikiagiza`) and
then adding their withheld variants, and **D1 — the next adapter — which now owns the visible
half of nat_08 as well** as the fact path preferring a memorised wrong number to the user's own
words.

## ✅ D-FIDELITY-4 (`25cd94f`) — nat_08's VISIBLE half, closed the same day

The router fix left nat_08 wrong where it counts. The engine resolved `party='employee'` and
computed TZS 65,000; the body said:

> *"unapaswa kulipa **TZS 130,000** kwa NSSF (sehemu ya mwajiri ni TZS 65,000 na sehemu ya
> mfanyakazi ni TZS 65,000)"*

**Every figure in it is TRUE.** 130,000 really is the NSSF total and the attribution is correct.
It is wrong only relative to what was ASKED — *"how much do they cut from ME"* — and on WhatsApp
the prose above the working **is** the answer.

This was reframed off D1 deliberately. D1 owns the fact path preferring a memorised number
**when there is no engine output at all**. Here there is engine output, correct, immediately
below. That is the D-FIDELITY family's territory and precisely the case those guards exist for.

### Why no existing guard could see it

```
body_contradicts_working  →  False
same claim rewritten with '=' (asserts {65000, 130000})  →  STILL False
wrong total ALONE with '='  (asserts {130000})           →  True
```

`scratch/oc01_fidelity_probe.json`, by direct call. Two layers, and the second is the wall:

1. **A connector gap.** `unapaswa kulipa TZS 130,000` and bare `ni TZS 65,000` are not in
   `_ASSERT_CONNECTORS`, so the asserted set is EMPTY and the guard is silent.
2. **Widening the connectors would not have fixed it.** With both figures visible the
   authoritative 65,000 **is** among them, and the rule clears the body by design.

> **`body_contradicts_working` is a SET-MEMBERSHIP check, not a CONCLUSION check.** It asks
> whether the authoritative figure is AMONG the figures the body asserts — never whether it is
> the one the body CONCLUDES with. A body that states the correct share and leads with the wrong
> headline satisfies it.

D-FIDELITY-3 declines this direction on purpose: its own comment says a LARGER derived figure
"is usually a legitimate conversion (per-year, per-employer, **plus-sibling**)", and the
cross-party total is exactly the plus-sibling case.

### Why the new rule is a different KIND, not a widening

It settles the case from information **the body does not contain** — `result.inputs['party']`.
Whether the cross-party total is a legitimate conversion or the wrong answer is a property of
the **QUESTION**, so no amount of reading the body can decide it. The total is computed from the
engine's own rates, never assumed to be 2× (a test pins asymmetric rates).

### 🧪 THE SWEEP CAME OUT AGAINST ITS OWN HYPOTHESIS AND KILLED THE RULE IT WAS RUN TO JUSTIFY

This is the method result, and it outranks the guard.

The sweep was run to answer *"is this one row or a class?"* — expecting frequency to justify
the obvious rule, **body states the cross-party total**. `scratch/dfid4_party_sweep.json`:

| | |
|---|---|
| bodies pairing with a **party-specific** working | 24 |
| of those, stating the cross-party total | 5 |
| **of those, actually the defect** | **1** |
| instrument artefact (2× collided with a per-employee salary) | 1 |
| **CORRECT bodies that would have been blanked** | **3** |
| bodies stating the total *without* the authoritative figure | **0** |

The three correct bodies state the sum and the share side by side —
*"Sehemu ya mfanyakazi: … TZS 250,000. Jumla ya michango: … TZS 500,000"* — and are entirely
right. **A presence-keyed rule is 4-FOR-1 AGAINST**, the same trade shape that disqualified the
SAFETY-2 cue extension at 3-for-1. And with zero rows in the "total only" column, the crisp
signal has no corpus support and **would not have caught nat_08 either**, which states both.

> **The version of this entry written without the sweep would have claimed a class and shipped a
> 4-for-1 rule.** The hypothesis was frequency; the answer was one row. This is the case for
> sweeping BEFORE designing rather than after — a sweep run to confirm a rule finds what the
> rule expects, and this one was run early enough to change what got built.

What actually separates the defect from the three correct bodies is what the total is ATTACHED
to: a neutral sum label (`Jumla ya michango`) versus a **second-person obligation** addressed to
the asker (`unapaswa kulipa`). Forms **harvested by frequency**, not invented — and the
harvester's own first pass matched `u\w*` and returned `usajili`, `user`, `umepita` and **`umla`
from *Jumla***. Fourth instance of the bare-cue nesting hazard in one session, this time inside
the instrument. Full verb forms only.

### 🔓 THE CONNECTOR GAP IS REAL, MEASURED, AND DELIBERATELY LEFT OPEN

The founder's instruction was to close it in the same commit. **The measurement overruled the
instruction, and the founder confirmed the overrule.** Adding the obligation verbs to
`_ASSERT_CONNECTORS` changes 3 verdicts over 186 recoverable body↔working pairs
(`scratch/dfid4_connector_sweep.json`): **1 true positive and 2 FALSE positives.** Both false
positives are `party=total` questions whose bodies state the per-party components —
*"kwa TZS 500,000 **utalipa TZS 50,000** kwa upande wa mwajiri na TZS 50,000 kwa upande wa
mfanyakazi"* — which is CORRECT, and which the guard blanks because the positive-amount branch
needs the authoritative figure PRESENT and cannot add 50,000 + 50,000.

Same shape as bare levy-scoped `ni`, rejected on R17 evidence in 2026-08-10: frequency argued
for it, the probes settled it.

**THE HONEST CLOSURE, named so nobody re-derives it:** `_asserted_results` must return a
**MULTISET** (it returns a set today, so the two 50,000s collapse to one) and the positive-amount
branch needs a **COMPONENT-SUM acceptance** — a body whose asserted figures sum to the
authoritative amount is faithful. **That is its own sweep and its own risk** to the permissiveness
this file depends on, and it must not be smuggled in as part of something else. Recorded in
`chike/fidelity.py` above `_ASSERT_CONNECTORS` as well as here.

The one case that mattered is handled inside D-FIDELITY-4, where `party != 'total'` makes the
same construction safe to read.

### R16 verification — 7/7, `scratch/dfid4_live_before.json` / `_after.json`

```
BEFORE  df_01  A: … unapaswa kulipa TZS 130,000 kwa NSSF (sehemu ya mwajiri ni TZS 65,000 …)
               NSSF (sehemu ya mfanyakazi) = 10% × TZS 650,000 = TZS 65,000 — …

AFTER   df_01  A: NSSF (sehemu ya mfanyakazi) = 10% × TZS 650,000 = TZS 65,000 — jumla ya
                  NSSF ni 20% (mwajiri TZS 65,000 + mfanyakazi TZS 65,000)
```

Body blanked, working alone, headline is the share. `df_02` is **adv_01 live** — the NSSF TOTAL
question whose correct body states the two TZS 50,000 components, i.e. the case where the
`party != 'total'` precondition is doing the work and one of the two bodies a generic connector
widening would have blanked. It answers normally. `df_03`–`df_05` (two-part, employer share,
plain employee share) are **byte-identical to BEFORE**. `df_06` confirms the container read
`chike_config.json`.

**The first version of the `df_01` probe scored the BEFORE run PASS**, because it asserted only
that `65,000` appear — the reply led with 130,000. The check was rewritten as a conclusion check
before the deploy. **The instrument built to verify a fix for presence-not-conclusion committed
presence-not-conclusion.** See the family section below; it is why that section exists.

13/13 on `eval/fidelity_gate/party_total_obligation_013.jsonl` (3 must-fire, 10 must-never-fire,
three of the negatives real stored correct bodies). Suite **1074 passed**.

## ✅ _WAGE_PAY_CUES (`32917f4`) — the employee's own side, deployed and verified

th_16 from the other direction. Every cue in `_WAGE_PAY_CUES` was the EMPLOYER speaking
(*"I pay him"*, *"we pay them"*) or a THIRD PERSON being paid (`analipwa`, `wanalipwa`,
`walipwa`). Not one was a worker asking about their OWN wage. Two paradigms, both at **zero**
for first person — **finding B a third time, in the list where it costs most:**

```
ACTIVE + object infix    wana-NI-lipa, ana-NI-lipa, wana-TU-lipa, wana-KU-lipa
PASSIVE + subject        ni-na-LIPWA, tu-na-LIPWA, u-na-LIPWA
```

### The BEFORE was worse than "falls through to fact/RAG"

That was the diagnosis carried in from the gap measurement. The live BEFORE is worse:

> **Q:** *wananilipa laki mbili kwa mwezi je ni halali kisheria*
> **A:** *"Hapana, si halali kisheria. Malipo ya **NSSF** yanatakiwa kuwa asilimia 20% ya
> mshahara ghafi, si TZS 200,000."*

A worker earning TZS 200,000 was told their wage is **unlawful**, for an NSSF percentage reason
that answers a different question entirely. Not a fallthrough — a confident wrong answer on the
highest-stakes question this product gets. **It was never on any board.**

AFTER, the same question reaches the deterministic route, names GN 605A and the sector range,
and asks which sector applies. `scratch/wage_live_before.json` / `_after.json`. The employer-side
control (`wl_03`) is **byte-identical**, both GN 605A lookups are unmoved, `wl_07` keeps its levy
route on path 1, and `wl_06` confirms the container read config.

### 🧹 THE SWEEP WAS MANDATORY, AND ITS CLEANLINESS IS THE WEAKEST PART OF THIS ENTRY

This is the list whose first version included the noun `mshahara` and stole **five real gate
questions**, so a sweep was the entry price rather than a formality. `scratch/wage_blast_diff.json`,
5,588 questions against a pristine worktree:

```
intent=8   party=0   applic=0   count=0   in_scope=0
```

**All eight changes are the authored probes. The 5,570 pre-existing corpus rows did not move at
all.** That is not a safety result:

> **A clean sweep here means the corpus does not contain the employee's side of this question —
> which is exactly WHY the gap survived, not a reason to trust the fix.** The instrument returned
> "nothing changed" because it has nothing to change. The 18 authored probes are the whole
> evidence base; the sweep only proves the change did not damage what the corpus DOES contain.

**Third item in a row where the sweep is structurally blind and authored probes carry the
verification** — after SAFETY-2 and the `-kata`/`-anza` half of object concord. That is now a
pattern rather than a coincidence, and it raises a question worth answering deliberately:

> 📋 **QUEUED — how many of the router's gates have never been exercised by a single corpus
> row?** Each of the last three gaps was invisible to every offline instrument for the same
> reason: no question in 5,500 was phrased that way. A gate-by-gate coverage count would name
> the next `wananilipa` **before a user finds it**, instead of after. Not started; queued
> deliberately rather than folded into this commit.

### The withheld pin fired and did its job

Five of the nine counterparts are now recognised and their exemption is **deleted**. Four remain
and are one family — the applicative stem `-lipia`, which `_object_concord('lipa')` deliberately
does not generate (per-STEM by construction: the infix class is closed, the verb is not). The
exemption is narrowed to those four and **re-pinned**; the old assertion is inverted rather than
deleted, with the history kept in its docstring per the R17 corollary.

### ⚠️ TWO THINGS THIS DEPLOY LEAVES OPEN

**1. THE CLARIFICATION COPY IS WRITTEN FROM THE EMPLOYER'S SIDE, and employee questions now
reach it.** Live, after the fix:

> **Q:** *ninalipwa laki moja na nusu kwa mwezi je ni halali kisheria* (I AM PAID…)
> **A:** *"…niambie **mfanyakazi wako** anafanya kazi ya aina gani"* — tell me what **YOUR
> EMPLOYEE** does.

The asker IS the worker. `clarification.MIN_WAGE_NO_SECTOR` and `MIN_WAGE_NO_AMOUNT`
(*"mshahara **unaomlipa mfanyakazi**"*) are both employer-worded, and until this commit only
employers reached them. **The route is right and the audience is wrong.** Not a wrong number,
and a large net improvement on the NSSF answer it replaced — but it is on the highest-stakes
path, and a worker told to describe "your employee" may reasonably conclude the service is not
for them. Fix is contained: a party-aware copy selection at the two orchestrator call sites
(lines 473 and 489), keyed on 1sg/1pl/2sg object infix or passive subject — `-m-`/`-wa-` object
forms stay employer-side. **Needs its own probes and its own R16 cycle.**

**2. QUEUED VERIFICATION — the range floor in `MIN_WAGE_NO_SECTOR` says TZS 80,000.**
CLAUDE.md §11 records the GN 605A range as **~TZS 175,000 (general) to TZS 765,900**, and the
copy also says "viwango 50" where §11 says 16 sectors / 46 sub-sectors. Pre-existing copy,
untouched by this commit and unchanged across the deploy, so it is **not** a regression — but it
is an unverified figure on a deterministic never-guess path, which is the one place a wrong
number carries the engine's authority. Verify against TanzLII GN 605A before it is quoted again.

### 🪞 THREE FAULTS IN MY OWN INSTRUMENTS, ALL THE SAME FAMILY

Recorded because the family section below predicts exactly this, and the prediction held three
times inside one item:

1. **`oc_blast_diff.py` HARDCODES its input paths and ignores `argv`** — see its own entry
   under the family section.
2. **`wp_14`'s expected route was authored wrong.** `none` is pre-existing on both trees
   (`asilimia ngapi` is a `_NONMONEY_ASK`); the probe, not the code, was corrected.
3. **The live probe's `765,900` marker was a presence check, twice over.** First version
   asserted **nothing positive** and only forbade the string — so it scored the known-bad
   BEFORE run a **PASS** while the reply blamed NSSF. Rewritten to require the deterministic
   `GN 605A` signature and forbid `nssf`. Then the AFTER run failed on `765,900` **appearing
   legitimately** as the top of the GN 605A range, which is correct — th_16's fabrication was
   765,900 presented as a legal *maximum wage*, a semantic claim the string cannot distinguish.
   **A string marker for a semantic defect is a presence check with extra steps.**

Suite **1107 passed**.

## ✅ THE WORKER IS ADDRESSED AS A WORKER (`571cf1d`) — the visible half of the wage fix

`_WAGE_PAY_CUES` let employees reach the deterministic minimum-wage route. **The copy waiting
for them was written for employers**, because until that commit only employers could get there.
Live, immediately after it shipped:

> **Q:** *ninalipwa laki moja na nusu kwa mwezi je ni halali kisheria* — I AM PAID…
> **A:** *"…niambie **mfanyakazi wako** anafanya kazi ya aina gani"* — tell me what YOUR
> EMPLOYEE does.

Route right, audience wrong — and on this question that is its own kind of wrong answer. A
worker told to describe "your employee" may reasonably conclude the service is not for them,
at the exact moment they are asking whether they are underpaid. **10/10 on the R16 cycle**
(`scratch/wage_live_copy_before.json` / `_after.json`); AFTER reads *"niambie **unafanya kazi**
ya aina gani"*, and `wl_10` confirms an employer still gets the employer wording — the same
defect with the roles reversed would be telling a business owner "how much are YOU paid".

**ASYMMETRIC BY DESIGN.** Employer cues WIN, so the copy flips only on positive worker evidence
and never on the absence of employer evidence: an ambiguous question keeps today's behaviour.
**`wangu` alone is not worker evidence** — *"namlipa mlinzi **wangu** 200000"* is an employer
saying "my guard". Only the possessive bound to the speaker's OWN wage or OWN employer counts.

### Two bugs in the predicate, both found by instruments rather than by reading it

**1. THE OBJECT INFIX ALONE DOES NOT SAY WHO IS ASKING — subject and object together do.**

```
wana-NI-lipa   they pay ME     -> the speaker is PAID      worker
nime-KU-lipa   I have paid YOU -> the speaker PAYS         EMPLOYER   <- flagged worker
wana-KU-lipa   they pay YOU    -> the addressee is paid    worker
```

`-ni-`/`-tu-` are unambiguous (nobody pays themselves, whoever the subject is). `-ku-` resolves
on the SUBJECT and now takes third-person subjects only. **Surfaced by the generative concord
test**, which also demanded eleven employer counterparts and was right about every one — and
which cascaded twice before reaching fixpoint, exactly as a closure test should.

**2. BARE `u-` IS THE CLASS 3/11 SUBJECT AGREEMENT, not only 2sg.** *"**Ushuru** wa stempu
unalipwa lini"*, *"**mchango** unalipwa TRA"*, *"**umeme** unalipwa VAT"* — **28 corpus rows
matched `unalipwa` and not one was a person being paid.** Harmless where it was found, because
the predicate is only consulted on the wage route, and removed anyway: a wage question that
happens to mention `ushuru` would have taken worker copy. The cost is the genuine 2sg reading,
which is ambiguous in any case and now keeps the safe default.

### Sweep

Routing signals `intent`/`party`/`applic`/`count`/`in_scope` **all zero** over 5,588 questions
against a pristine worktree — this selects copy, it does not route. On the wage route, 26 corpus
rows: **7 worker, 19 employer, and every worker row is an authored probe**, so no pre-existing
question changes audience. The 19 remaining off-route worker readings were each read: all are
genuine worker questions (`mshahara wangu`, `mwajiri wangu`, `ninalipwa`).

### ✅ MIN_WAGE_NO_SECTOR's FIGURES — QUERIED, VERIFIED, CLEARED, PINNED

Raised in the previous entry as a suspected wrong number on a never-guess path. **It was not
one, and the correction belongs on the record as firmly as a defect would.**

| in the copy | actually | vs CLAUDE.md |
|---|---|---|
| `TZS 80,000` floor | **sector 4d, "Other domestic workers"** — the genuine lowest MONTHLY rate in the Order | §11's `~175,000 (general)` is **item 16**, the UNLISTED-sector rate. `BY_ROW[(16,'')]` = 175,000 exactly |
| `viwango 50` | `len(BY_ROW)` = **50 rate rows** | §11's `16 sectors / 46 sub-sectors` = `BY_SECTOR` (16) and `SUB_LABELS_SW` (46) |

Three different counts of three different things, all correct. **No conflict, and nothing to
correct.** What was real is that the prose hardcodes numbers the schedule owns, so a **drift
pin** now ties them together: if the schedule is ever corrected and the copy is not, the test
fails.

## 📊 THE 48-QUESTION RE-RUN — 39.6% → 58.3% correct, 39.6% → 18.8% wrong (2026-08-15)

**The number the assessment stopped the product on, re-measured.** Same 48 questions, same
script, same endpoint, same timeout — only the output path differs, so this is a **paired
comparison** and the difference is the build.
`eval/results/natural48_rerun_2026_08_15_adjudication.json`.

| | 2026-08-11 | 2026-08-15 | |
|---|---|---|---|
| **CORRECT** | 19 | **28** | **+9** |
| CLARIFY | 6 | 6 | 0 |
| PARTIAL | 4 | 5 | +1 |
| **WRONG** | 19 | **9** | **−10** |

**correct 39.6% → 58.3%  ·  wrong 39.6% → 18.8%**

Adjudicated by reading each reply against its `expected_behavior` — **judgement, reported as
judgement**, the same standard and the same taxonomy as the baseline.

### The movement is entirely on the compute path, and that is the point

| path | 2026-08-11 | 2026-08-15 |
|---|---|---|
| **compute** (24) | CORRECT 6 · CLARIFY 5 · PARTIAL 0 · **WRONG 13** | CORRECT **15** · CLARIFY 5 · PARTIAL 1 · **WRONG 3** |
| fact (21) | CORRECT 10 · CLARIFY 1 · PARTIAL 4 · WRONG 6 | **identical** |
| refusal (3) | CORRECT 3 | CORRECT 3 |

**37 of 48 replies are byte-identical to the baseline.** Every row that moved is a compute row,
and every one of them was a target of this week's work:

```
nat_01 WRONG -> CORRECT   SDL 0.5% -> 3.5% x 6,000,000 = 210,000
nat_04 WRONG -> CORRECT   object concord; SDL applies at 3.5% on a stated 11
nat_08 WRONG -> CORRECT   130,000 -> 65,000  (object concord + D-FIDELITY-4)
nat_09 WRONG -> CORRECT   "mfanyakazi anachangia 960,000 (80%)" -> 240,000 correctly split
nat_10 WRONG -> CORRECT   a 20% rate offered as an answer -> asks for the salary
nat_12 WRONG -> PARTIAL   a 15% withholding answer -> 500,000 correct, prose mislabels party
nat_13 WRONG -> CORRECT   52,000 -> 103,000  (A2)
nat_14 WRONG -> CORRECT   28,000 -> 6,400   (A2 + D-FIDELITY-5)
nat_16 WRONG -> CORRECT*  progressive 1,028,000 -> declines, names the 183-day test
nat_19 WRONG -> CORRECT   WCF 300,000 -> 15,000
```

**The compute path went from 13 wrong of 24 to 3 wrong of 24.** That is what the routing and
guard work was aimed at, and it is where all of it landed. **The fact path did not move at
all** — which is the honest other half of this result.

### ⚠️ READ THIS BEFORE QUOTING THE NUMBER

**1. One row departs from its written rubric, flagged rather than buried.** nat_16's
`expected_behavior` demands 15% × 4,000,000 = TZS 600,000. That expectation was **deliberately
superseded by SAFETY-2** (`8b90b25`): residency is decided by presence, not citizenship or
permit type, and *"hana residence permit ya kudumu"* says nothing about days present — so
TZS 600,000 would **also** have been a guess. The reply declines and names the 183-day test,
which is the behaviour that decision shipped. **By the written rubric it is WRONG, giving
CORRECT 27 / WRONG 10 (56.3% / 20.8%).** Both numbers are in the artifact; quote whichever, but
quote the caveat with it.

**2. CLARIFY did not move, and 5 of the 6 are delivery failures.** nat_02, nat_06, nat_11,
nat_17, nat_21 are all rows where **a figure was computable and was not delivered** — the
Swahili-numeral + `kila mmoja` extractor gap, and the multi-group aggregation gap. They are
routing passes and delivery fails, they are not counted as correct, and **they are the largest
single block of remaining work.** Nothing this week touched them.

**3. The 9 remaining WRONG are almost all fact-path**, and they are a different kind of problem
from the ones just closed:

```
nat_05  fabricated BRELA fee of TZS 260,000 for an SDL wrong-base question
nat_23  answers NSSF correctly and never answers SDL   (fan-out gap)
nat_24  conflates SDL and WCF; never says SDL is not due at 9 employees
nat_28  royalties 15% for a services VAT-withholding question (should be 6%)
nat_33  neither the 22,000 fee nor the 17,500 penalty
nat_41  invents "siku 1" for OSHA registration
nat_43  states that minimum wage does NOT vary by sector — flatly false
nat_44  6% for a GOODS question (should be 3%)
nat_45  "ndani ya siku 7 kufikia tarehe 8 Julai 2025" — a fabricated absolute date
```

**Six of these are a fact recited wrongly, not a route missed.** The routing-and-guard method
that took the compute path from 13 wrong to 3 has no purchase on them: there is no engine to
route to and no working to check a body against. **They belong to D1 — the next adapter — and
to the RAG/locked-facts path**, and this measurement is the clearest statement yet of where the
remaining error actually lives.

### What this does and does not say

It is **not** a gate result and not a random sample of real traffic: the 48 questions were
authored by Claude Code and are register-realistic by construction (the original findings file
carries the same authorship caveat). It is the only end-to-end measurement of natural-register
performance the project has, measured the same way twice.

**Latency:** median 6.2s → 7.9s, max 63.9s → 24.0s. The max improved because there was no cold
start in this run; the median difference is noise at n=48.

## ✅ D-FIDELITY-5 (`baf77b3`) — nat_14 closed. P2's compute cluster is now closed.

```
BEFORE  A: "...hakuna PAYE ya kulipa kwa sababu kiwango cha sifuri kinatumika hadi
            TZS 270,000."
           PAYE = TZS 0 + 8% × (TZS 350,000 − TZS 270,000) = TZS 6,400

AFTER   A: PAYE = TZS 0 + 8% × (TZS 350,000 − TZS 270,000) = TZS 6,400
```

Body blanked, working alone. **6/6 on the R16 cycle** (`scratch/dfid5_live_after.json`).

### The finding, at family level

> **A CONTRADICTION DOES NOT NEED A NUMBER.**

Verified by direct call on nat_14's live body:

```
_asserted_results(body)             -> []      the body asserts NO figure at all
body_contradicts_working            -> False
body_reduces_authoritative_amount   -> False
body_offers_total_as_own_obligation -> False
```

All three existing guards compare **figures** — which amounts the body asserts, and whether the
authoritative one is among them. A body that asserts **nothing** and denies the obligation in
words contradicts a positive engine amount completely, and satisfies **every one of them
vacuously, because the set being checked is empty.**

**Fourth instance of the presence-not-conclusion family, and the first where the instrument
passes by having nothing to look at.** The earlier three each examined something and asked the
wrong question of it. This one had nothing to examine and reported success — which is the
degenerate case of the same design, and the one no amount of care about *how* you inspect the
evidence will catch, because there is no evidence.

### The false-positive surface, measured before the rule was designed

A denial is the **correct** body whenever the engine's amount is zero. That surface is not
hypothetical — it is most of what the corpus contains (`scratch/dfid5_sweep.json`):

| candidate | corpus bodies | fire (amount > 0) | **correct denials (amount = 0)** |
|---|---|---|---|
| `hakuna paye` | 10 | 0 | **10 — all of them** |
| `haikatwi` | 2 | 2 | 0 — **and both fires are CORRECT bodies** |

`haikatwi` was disqualified by reading it: *"Hii inalipwa na mwajiri peke yake — **haikatwi**
kutoka mshahara wa mfanyakazi"* denies the **deduction locus**, not the liability. It is a true
statement about who bears SDL, and it is excluded from the phrase list entirely.

**So the phrase can never be the discriminator; the engine amount is.** The rule fires only on
a definite positive amount, which excludes all ten legitimate denials by construction —
`body_contradicts_working` already owns the `amount == 0` case. Live `d5_02`/`d5_03` confirm
both zero-band bodies survive untouched.

**The denial must name the COMPUTED levy.** A PAYE answer may correctly say *"hakuna SDL"* in
the same breath (fewer than ten employees); keyed on any levy this rule would blank a correct
body. The pattern is built from `result.computation`, both directions are pinned as probes, and
live `d5_04` shows a real mixed PAYE+SDL answer keeping its SDL denial.

Rule run over all **190** recoverable body↔working pairs: **zero fires.** 10 probes, 7 of them
negatives. Suite **1166 passed**.

**Observed and NOT fixed here, logged instead:** `d5_04`'s PAYE half states *"unalipa TZS
50,000"* while the deterministic path returned a **clarification** for that sub-question. The
engine produced no amount, so `body_contradicts_working`'s `amount is None` branch is the one
that should catch it — but that branch additionally requires `_has_naive_levy_compute`, and
this body writes no `TZS N × R%` expression. **A body volunteering a figure where the engine
declined to give one** is its own family; it is not caused by D-FIDELITY-5 and does not block it.

---

## ⚖️ REACHING THE ENGINE IS NOT A PROXY FOR BEING ANSWERED CORRECTLY

**The counterweight to the asymmetry argument this week has been running on, and it belongs
beside it so neither is ever quoted alone.**

The argument all week has been: **under-routing costs a wrong figure, over-routing costs a
turn.** A question that misses the deterministic route gets a fabricated number; a question
wrongly routed to it gets a clarification the user must answer. Asymmetric, so route eagerly.

**A2 produced the counterexample, and it is not a corner case.** `serikali inakata` is the exact
sibling of the `serikali inachukua` cue that shipped, and it was withheld:

```
rc_10   "Ninalipwa laki mbili na hamsini kwa mwezi. Je serikali inakata kiasi gani...?"
        gold                        PAYE on 250,000 -> ZERO
        sole_plausible_amount(...)  -> 5,200,000        PAYE on that ~ TZS 1,388,000
```

And the live AFTER settles what the withholding bought:

> `rc_10` on the **fact path**, today: *"Kiwango cha kodi ya PAYE kinachokatwa kwenye mshahara
> wa **TZS 250,000** ni asilimia **sifuri (0%)**."* — **correct.**

**Routing it would have replaced a correct answer with TZS 1,388,000 carrying a deterministic
working.** The parser reads `mbili na hamsini` as 52 and multiplies by *laki*; the fact path
read the numeral correctly and the engine would not have.

> **Over-routing costs a turn ONLY when extraction is sound. Where extraction is wrong,
> over-routing is worse than the fact path — because the engine's authority is lent to the
> parser's defect, and a wrong number with a working is harder for a user to doubt than a
> wrong number without one.**

This is the presence-not-conclusion family arriving at the **route**: "reaches the engine" is a
property that is cheap to check and easy to mistake for "is answered correctly". The three
compute-path guards exist precisely because those two things come apart *after* the engine runs;
rc_10 shows they come apart *before* it too.

**Both statements are true and neither is safe alone.** The asymmetry argument justified every
routing fix this week and should keep doing so. This entry is the boundary condition on it: a
routing change must check that the row's slots extract correctly, not only that it reaches the
right route. `test_the_withheld_serikali_inakata_cue_still_names_a_live_defect` pins the case
until the `laki <n> na <m>` parser item is done.

## ✅ A2 (`2ee31f5`) — the levy said in everyday words. Two of three closed end to end.

The last of the four, and the one where no paradigm helps. `mfuko`, `serikali inachukua`,
`kupeleka kwa TRA` are synonyms for a levy — an **open lexical set**.

### The BEFORE, captured before reading any predicate — 3 samples per row, all identical

```
nat_09  "unachangia TZS 240,000 (20%) na mfanyakazi anachangia TZS 960,000 (80%).
         Jumla ya michango yote ni TZS 1,200,000."          -- sourced to TRA, for NSSF
nat_13  "PAYE inayokatwa ni TZS 52,000"                     -- correct is 103,000
nat_14  "PAYE itakuwa TZS 28,000"                           -- 8% of the WHOLE salary
```

**The board recorded only nat_09's `960,000 (80%)`. It did not record that the stated TOTAL
NSSF bill equals the ENTIRE SALARY** — an employer told their monthly contribution is 100% of
what they pay. Third time this session the BEFORE was worse than the item it was capturing.

All nine samples had `working=False`: no engine ran, confirming the route-level diagnosis. Here,
unlike the wage and `arzi` cases, the BEFORE **confirmed** the diagnosis rather than
contradicting it — and still found severity the board understated.

### 🎯 THE HONEST CEILING — stated so this is never read as a closure

> **Every cue here fixes ONLY the phrasing already seen to fail, and each one is purchased with
> a user having received a wrong figure first.**

The candidate sweep makes that concrete rather than rhetorical: **every** money-ask candidate
for nat_09 — `jumla inayoenda`, `inayoenda kwenye`, `nataka kujua jumla`, `kujua jumla` —
matched **exactly one corpus row: nat_09 itself.** The corpus holds one instance of that
phrasing because somebody wrote one probe after it failed. There is no distribution to
generalise from, and no paradigm will ever generate `kupeleka kwa TRA`.

**The mitigation is the TRAINING-CORPUS DIFF, not a cleverer rule** — widening what the corpus
contains so the next phrasing is found by a sweep instead of by a user. That is a data task, and
it is the only thing that changes the economics of this item.

### Narrowest form, priced rather than asserted

The original diagnosis warned that `mfuko`/`serikali`/`TRA` are common words. The sweep put
numbers on the warning:

| bare | rows | narrowed | rows | route changes |
|---|---|---|---|---|
| `mfuko` | 29 | `kwenye mfuko` | 9 | **the same 2** |
| `serikali` | 80 | `serikali inachukua` | 1 | 1 |
| `kwa tra` | 34 | `peleka kwa tra` | 1 | 1 |

Narrowing cost **nothing** in coverage and removed ~130 rows of surface.

**nat_09 needed TWO gaps closed, not one** — the levy cue *and* a money-ask (`jumla inayoenda`).
A2 is two open lexical sets, not one; a cue addition alone would have left it wrong.

**Three rows were not on the A2 board** — nat_12, edge_p14, rc_10, all found by the sweep.
edge_p14 must reach the route and then SAFE-CLARIFY, and does.

Sweep, both passes over the **same** 5,595 questions: `intent=6`, and `party`/`applic`/`count`/
`in_scope` all **0**. (The BEFORE was re-run after the probe file landed — the harness compares
by question text, so a corpus that grows between passes silently drops rows from the diff.)

### 🔒 `serikali inakata` IS WITHHELD AND PINNED — the fact path is not uniformly worse

Its exact sibling `serikali inachukua` shipped. This one did not, because routing its row to
compute would be **worse than leaving it on the fact path**:

```
rc_10   "Ninalipwa laki mbili na hamsini kwa mwezi..."   gold: PAYE on 250,000 -> ZERO
        sole_plausible_amount(...)  ->  5,200,000        PAYE on that ~ TZS 1,388,000
```

The parser reads `mbili na hamsini` as 52 and multiplies by *laki*; even the unambiguous
`"laki mbili na hamsini ELFU"` parses the same way. A **pre-existing parser defect** this cue
merely unmasks — `laki <n> na <m>` touches every money extraction in the product, so it is its
own item with its own sweep.

**And the live AFTER vindicated the withholding outright:**

> `rc_10` → *"Kiwango cha kodi ya PAYE kinachokatwa kwenye mshahara wa **TZS 250,000** ni
> asilimia **sifuri (0%)**."* — **correct.**

The fact path read the numeral correctly and gave the right answer, while the compute path would
have served TZS 1,388,000 **with a deterministic working** to somebody who owes nothing.
**Routing a row to compute is an improvement only when extraction is sound; where it is not, the
engine's authority makes the same wrong number worse.** That is a general caution against
treating "reaches the engine" as a proxy for "answered correctly" — it is the presence-not-
conclusion family arriving at the ROUTE.

### ⚠️ nat_14 IS CLOSED IN THE ROUTER AND OPEN IN THE ANSWER

Two of three board rows are closed end to end. nat_14 is not, and it must not be scored a pass:

```
A: "...hakuna PAYE ya kulipa kwa sababu kiwango cha sifuri kinatumika hadi TZS 270,000."
   PAYE = TZS 0 + 8% × (TZS 350,000 − TZS 270,000) = TZS 6,400
```

**The working is right and the prose denies it.** The row's own `expected_behavior` names this
exact failure: *"WRONG = 'below the threshold, nothing due'"*. An employer is told no PAYE is
due when TZS 6,400 is.

**No existing guard sees it, and the reason is a new family.** Verified by direct call:

```
_asserted_results(body)          -> []          (no figure asserted at all)
body_contradicts_working         -> False
body_reduces_authoritative_amount-> False
body_offers_total_as_own_obligation -> False
```

> **A contradiction does not need a number.** Every D-FIDELITY guard compares FIGURES — it asks
> which amounts the body asserts and whether the authoritative one is among them. A body that
> asserts **no figure** and denies the obligation qualitatively (*"hakuna PAYE"*) contradicts a
> positive engine amount completely, and passes every one of them by asserting nothing.

This is the presence-not-conclusion family again, from a new direction: the guards check that
the right figure is *present*; here the defect is that a **claim** is present instead. Proposed
**D-FIDELITY-5**, narrow: when `result.amount > 0`, a body carrying a denial of the obligation
(`hakuna PAYE`, `hakuna kodi`, `haulipi`, `hulipi`, `hakuna cha kulipa`) contradicts it. Needs
its own sweep — a denial is legitimate whenever the engine's own amount is 0, which is the
`rf_20`/`th_13` family and must not be blanked.

**Minor, same class, not blocking:** nat_12's prose labels the figure *"NSSF ya **mwajiri**"*
while the working correctly says *"sehemu ya **mfanyakazi**"*. Same amount either way, so no
wrong number — but the label is wrong for a question that asked what is deducted from the
asker's own pay.

### Board after A2

| row | live result |
|---|---|
| nat_09 | ✅ TZS 240,000, correct split, sourced to NSSF |
| nat_13 | ✅ TZS 103,000 with the band working |
| nat_14 | ⚠️ working correct at TZS 6,400; **prose says no PAYE is due** → D-FIDELITY-5 |
| nat_12, edge_p14 | ✅ found by sweep; compute and clarify respectively |
| rc_10 | ⏸ withheld and pinned behind the `laki <n> na <m>` parser item |

Suite **1151 passed**. 12 probes, 6 of them negatives carrying the dangerous words in non-levy
senses — including **`serikali inachukua HATUA`**, the identical cue string meaning "takes
STEPS" rather than "takes MONEY", held out by the path-2 gate rather than by the cue.

---

# 🔬 THE BEFORE IS MANDATORY EVEN WHEN THE FIX IS WELL UNDERSTOOD

**Twice this week the R16 BEFORE capture — not the fix, not the sweep, not any offline
instrument — is the only thing that found a live defect worse than the item it was capturing.**

| BEFORE run for | what it was supposed to capture | what it actually found |
|---|---|---|
| the OOC variant deploy (2026-08-14) | a baseline for a spelling change | **two fabricated tax rates stated as law** — *"kodi ya zuio ya asilimia 10 kwenye mauzo ya ardhi"*, *"kodi ya mauzo ya ardhi ni 2% ya thamani ya soko"*. Neither exists. One letter, `ardhi` spelled `arzi` |
| `_WAGE_PAY_CUES` (2026-08-15) | a worker's wage question falling through to fact/RAG | **a worker earning TZS 200,000 told their wage was UNLAWFUL** — *"Hapana, si halali kisheria. Malipo ya NSSF yanatakiwa kuwa asilimia 20%"* — a confident wrong answer to a different question entirely |

**In both cases the diagnosis going in was accurate and incomplete in the same direction: it
named the routing defect and had nothing to say about what the system was ACTUALLY replying.**
The wage item's own gap measurement (`scratch/oc_wage_gap.json`) reported `intent=none` and was
right — `none` is what the router returned. It could not report that `none` produces a
confident accusation of illegality, because an offline predicate has no reply to read.

> **The argument this settles: the BEFORE is not a formality you skip when the fix is well
> understood — it is the ONLY instrument in the kit that looks at what users are receiving
> right now.** Every other instrument answers a question we already knew to ask. The BEFORE is
> where the unasked question shows up, and it is most valuable precisely when the item is
> well understood, because that is when nobody is looking.

Both defects were **live in production and on no board.** Neither would have been found by the
fix, the sweep, the probes, the suite, or the gate.

---

# 🧭 CHECK THAT THE RIGHT THING IS THERE, NOT THAT IT WON — a family, not three coincidences

**Read this before building any instrument for this project.**

Three times now, an instrument this project relies on has been found measuring **presence** of
the correct thing where it needed to measure whether the correct thing **prevailed**. Each was
discovered one level down from the last, and each had been trusted in the interval:

| instrument | measured | needed to measure |
|---|---|---|
| **MEASUREMENT-GAP-1** — the offline harness | fact **in prompt** | fact **applied** |
| **INSTRUMENT-LIE #6** — the canary | **route** correct | **outcome** correct |
| **D-FIDELITY-4** — the guard itself | authoritative figure **present** | authoritative figure **concluded with** |
| **D-FIDELITY-5** — the same guards, again | **which figures** the body asserts | whether a CLAIM contradicts the amount — a body asserting NONE satisfies them all vacuously |

The generalisation, and the reason to expect a fourth:

> **Presence is cheap to check and always available. That is why every instrument reaches for
> it — and it is never the property that matters.** "Is the right number in there?" can be
> answered with a substring search against any artifact you happen to have. "Did the right
> number win?" requires knowing what the question asked, what the alternatives were, and which
> one the reader takes away. The first is a property of the text; the second is a property of
> the text *relative to the question*. Instruments get built out of the first because the first
> is what the data affords.

It is not a bug that recurs. It is the **default shape of a cheap instrument**, and it will
recur in whatever gets built next unless the author checks for it deliberately.

**The recursion is the strongest evidence.** D-FIDELITY-4 exists because
`body_contradicts_working` — a guard built to catch wrong answers — was a presence check. Its
own R16 live probe was then written as a presence check and scored the known-bad BEFORE run as
a PASS. The fix and the verification of the fix made the same mistake, hours apart, by the same
author, with the finding already written down. **Knowing about this family does not protect you
from it**; only inspecting the specific assertion does.

### 📈 THE FAMILY'S FIRST SUCCESSFUL PREDICTION — four faults inside one item

Written up the same day it was named, because a framework that predicts its own next instance
is worth more than any individual catch it enabled.

The section above was written while closing D-FIDELITY-4. It predicted that the next instrument
built here would reach for presence. **Within the next item — `_WAGE_PAY_CUES`, one commit —
it happened four times:**

| # | instrument | checked that the right thing was THERE | should have checked |
|---|---|---|---|
| 1 | `oc_blast_diff.py` | a difference existed between two files | that it was **THE** difference — it re-reported the previous item's diff, self-check passing |
| 2 | the live probe (v1) | `765,900` was absent | that the conclusion was right — it asserted **nothing positive** and scored a "your wage is unlawful, NSSF is 20%" reply a **PASS** |
| 3 | the live probe (v2) | `765,900` was absent | th_16's defect was 765,900 **presented as a legal maximum**; the route states the same number correctly as the top of the range. **A string marker for a semantic defect** |
| 4 | the generative concord test | `nimekulipa` was in the list | whether the list would **MATCH** it — a false alarm, since the regex already did |

Two more in the same item were not presence faults but the same carelessness about what an
assertion means: `wp_14`'s expected route was authored wrong, and `wl_07` asserted TZS 103,000
where the correct PAYE on 800,000 is 78,000 — **failing a correct engine answer.**

> **The prediction held, and it held against an author who had just written the prediction
> down.** That is the part worth keeping. Knowing about this family is not protection; the
> temptation is structural, because presence is what the data affords and conclusion is what
> costs work. Only inspecting the specific assertion helps — which is why the practical test
> below is a procedure and not a principle.

**Practical test when building any instrument here:** write down the wrong answer you are
afraid of, then ask whether your check would still pass if the artifact contained BOTH the right
answer and the wrong one. If it would, you have built a presence check. The corpus method note
already says this about eval harnesses — *"a figure-presence assertion is not a correctness
check"* — and the point of this section is that it is not a fact about eval harnesses. It is a
fact about instruments.

## 🪞 THE SWEEP HARNESS THAT RE-REPORTED THE PREVIOUS ITEM'S DIFF — presence-not-conclusion at the instrument level (2026-08-15)

`oc_blast_diff.py` **hardcodes** its two input paths (`scratch/oc_blast_before.json`,
`scratch/oc_blast_after.json`) and never reads `argv`. Invoked with the wage sweep's arguments,
it silently ignored them, re-read the object-concord files, and printed **that** diff — a full,
plausible, correctly-formatted blast-radius report **for a change it had never seen.**

**Its self-check passed while it did this.** The check asserts that nat_08's party and nat_04's
intent differ between the two files — i.e. that the two trees are *distinguishable*. They were:
they were the object-concord trees, and they had been for hours. **The check verified that a
difference existed, not that it was THE difference the run was performed to measure.**

> **A self-check must assert the property the run was performed to establish, not a proxy for
> the run having happened.** The pass condition has to be written from the decision it feeds —
> the same sentence as the canary rule (INSTRUMENT-LIE #10), arriving from the harness side.
> "Did something change?" is a proxy. "Did *wp_01* move from `none` to `minimum_wage`?" is the
> property. A self-check keyed on the PREVIOUS change cannot fail for the current one, and will
> keep passing for every change that follows it.

**IT WAS CAUGHT BY LUCK, and the luck should not be discounted.** The stale rows were all about
`inamhusu` — applicability — and the wage patch touches nothing in that area, so the output was
visibly about the wrong thing. **Had the two items overlapped even slightly** — two consecutive
routing changes on neighbouring cue lists, which is exactly what this session has been doing all
day — the stale diff would have read as a plausible result for the new change, and the wage
patch would have been certified against a measurement of a different commit. The failure mode is
silent by construction; nothing in the output says which files it read.

Replaced by `scratch/wage_blast_diff.py`, which takes all three paths as arguments, asserts the
two files carry **different labels**, and self-checks on **wp_01 moving `none` → `minimum_wage`**
plus **a protected GN 605A lookup NOT moving** — one guard for the effect the change is for, one
for the effect it must not have.

**This is the fourth member of the family below and the first at the harness level.** The others
were an eval harness, a canary, and a fidelity guard — all measuring an artifact. This one
measured *itself*: it confirmed a run had occurred rather than that the run had measured the
thing. Same shape, one more level out.

## The board after this session

| item | row | live result |
|---|---|---|
| **B** SAFETY-2 | nat_16 | ✅ closed (`8b90b25`) |
| **A3** applicability | nat_04 | ✅ **closed** (`73f2f9f`) — SDL applies, 11 employees, 3.5%, end to end |
| **C** wrong party | nat_08 | ✅ **closed end to end** — router (`73f2f9f`) + D-FIDELITY-4 (`25cd94f`); live headline is TZS 65,000 |
| ~~**A2**~~ | nat_09 | ✅ **closed** (`2ee31f5`) — TZS 240,000, correct split, sourced to NSSF |
| ~~**A2**~~ | nat_13 | ✅ **closed** — TZS 103,000 with the band working |
| ~~**A2**~~ | nat_14 | ✅ **closed** (`baf77b3`) — body blanked, working alone: TZS 6,400 |
| *(new)* `laki <n> na <m>` parse | rc_10 | ⏸ `laki mbili na hamsini` → 5,200,000; blocks the withheld `serikali inakata` cue |
| ~~`_WAGE_PAY_CUES`~~ | — | ✅ **closed** (`32917f4`) — employee side reaches the deterministic route; BEFORE blamed NSSF for an unlawful wage |
| ~~wage clarification copy~~ | wl_08/wl_09 | ✅ **closed** (`571cf1d`) — the worker is addressed as a worker; employer copy unchanged |
| ~~`MIN_WAGE_NO_SECTOR` figures~~ | — | ✅ **verified and cleared** — TZS 80,000 is sector 4d, `viwango 50` is the row count; CLAUDE.md counts different things. Drift pin added |
| *(new 2026-08-16)* presumptive tax | coverage | ✅ **DEPLOYED AND LIVE-VERIFIED 2026-08-17** — full R16 cycle, 14/14 canaries, 5/5 negatives byte-identical. BEFORE invented eight different wrong rates |
| *(new 2026-08-16)* licence renewal date | coverage | ✅ fact written — **blocked on R15 RAG regen (Kaggle, founder step) so it is NOT retrievable yet** |
| *(new 2026-08-16)* licence FEE schedule | coverage | 🛑 **left uncovered** — no current consolidated First Schedule from any primary source; BRELA or OCR + 3 unchecked Acts |
| *(new 2026-08-16)* decomposition FABRICATES a sub-question | all routes | ⏸ pre-existing, confirmed on `05e68b5`; pinned `xfail(strict=True)`; not fixed inside a coverage commit |
| *(new 2026-08-16)* RAG similarity floor | pilot blocker | ⏸ scoped, agreed to ship **before any pilot**; needs the score distribution measured first |
| *(new 2026-08-16)* fact-path class analysis | 6 of 9 remaining WRONG | ✅ **DONE 2026-08-17 — it is RETRIEVAL, 7/9 RANKING, 0/9 OVERRIDE.** Fee rows are 30% of the index and win 58% of top-3 slots |
| ~~*(new 2026-08-17)* segregate fee-schedule rows from retrieval~~ | 9 rows | ❌ **MEASURED, DOES NOT WORK** — a retrieval-side mask fixes 0/9 and regresses 3 currently-correct rows. Fee-row segregation folds into the C4 reachability rewrite + R15 regen instead |
| *(new 2026-08-17)* locked facts absent from the RAG index | SDL exemptions | ✅ **FINAL: 15 of 246** (not 28, not 13 — drift check found 20 more keys nobody had checked). 10 of 15 are the SDL exemption family |
| *(new 2026-08-17)* similarity floor CANNOT use an absolute score | pilot blocker | ⏸ scores compress to 0.79-0.86; redesign on a MARGIN or a re-ranked index |
| ~~*(new 2026-08-17)* permanent `locked_facts` ↔ RAG index check~~ | pipeline | ✅ **BUILT** — `scripts/check_facts_index_sync.py` + `tests/test_facts_index_sync.py`, pinned + content-verified, runs every `pytest` (1229 passed). Compares content, not keys |
| *(new 2026-08-17)* presumptive transport schedule (para 2(5)) | lp_09, the daladala row | 🛑 **named coverage gap, not fixed** — production still invents *"asilimia 25%"* for Class A transport rates; the presumptive engine deliberately does not route to it (`_PRESUMPTIVE_VETO`) so the wrong answer doesn't spread, but the row itself stays wrong until this table is built |
| *(new 2026-08-17)* D1 / a new adapter for the fact cluster | 6 of 9 WRONG | ❌ **REMOVED from the queue — 0/9 OVERRIDE means it would have fixed none of them.** Do not re-queue without a new measurement |
| *(new 2026-08-17)* duplicate-key sweep, 246 facts | data hygiene | ✅ **first run — never done before.** 80 flagged by shared-number heuristic, 76 verified FALSE POSITIVE against BRELA's live fee schedule (standardized 22,000/50,000/60,000/30,000 fees across distinct categories, confirmed real). 4 genuine duplicate pairs found and dispositioned (2 merge, 1 scope-and-extract, 1 kept-as-is) |
| *(new 2026-08-17)* `memorandum_articles_of_association_filing_fee` = 22,000 | locked-fact value accuracy | 🛑 **FLAGGED, NOT FIXED** — BRELA's live page (`brela.go.tz/pages/tozo-za-kampuni`) states memorandum/articles filing is **66,000** (22,000 × 3 documents), not a flat 22,000. Found as a side effect of the duplicate sweep, not chased further — a wrong figure in a locked, CONFIRMED-status fact, on the board so it doesn't sit only in a chat transcript |
| *(new 2026-08-17)* nat_41 reclassified RANKING → ABSENCE (again) | fact-path class analysis | ✅ **corrected — see "nat_41 flips back to ABSENCE" above.** Partition is now RANKING 8/9 · ABSENCE 1/9, not 9/0. The content the recheck found (rows 53/72) answers a different question than the one asked; the real fact (OSH Act s.16(2), register BEFORE operating) never existed in the index |
| *(new 2026-08-17)* C4 applied — 3 merges, 3 new facts, 4 rewrites, 5 guards | nat_05/33/41/43 + pipeline | ✅ **LANDED LOCALLY, not yet regenerated** — see "C4 APPLIED" above. `pytest` 1229 passed / 1 xfailed, unchanged. Awaiting R15 Kaggle regen |
| *(new 2026-08-17)* nat_44 / nat_28 rate-half — vat_withholding rewrite | C4 apply-list | ❌ **HELD BACK — regresses nat_27** (currently correct). 3 phrasings tried, all fail or false-pass; see "THE VAT WITHHOLDING TRADEOFF" above. Needs a decision, not another wording pass |
| *(new 2026-08-17)* nat_37 / nat_38 discovered unprotected | negative-guard candidates | 🛑 **NEW, unfixed** — already fail against the currently deployed index, confirmed independent of this cycle's changes. Not wired as guards; nobody had verified these two before |
| *(new 2026-08-17)* `check_facts_index_sync.py` sibling-matcher bug | pipeline | ✅ **FOUND AND FIXED** — a single-word slug (`'brela'`, `'nssf'`) let a raw `startswith()` false-verify 5 keys against the wrong row, one of them a brand-new UNindexed key. `_is_sibling()` now requires a 2-word minimum; all 5 re-pinned against their real rows |
| *(new 2026-08-17)* THE THREE FLAT ROWS (nat_24, nat_45, nat_23) | reachability, unresolved | 🛑 **named, not a residual** — flat across two rounds of substantially different wording while nat_05 (same cluster) moved 150→24. Next step is a ceiling test run ON one of these three, not on nat_05 again |

### ➡️ FOUNDER-ADOPTED WORK ORDER (2026-08-17) — retrieval before facts, floor last

1. ~~Segregate the fee-schedule rows from general retrieval~~ ✅ **measured — the offline mask
   fixes 0/9 and regresses 3. It does not survive contact with evidence and is folded into
   step 2 instead of standing alone.**
2. **Reachability rewrites (C4)** — Swahili-first, value-at-front, no `key: ` prefix. **Now the
   whole fix**, not step one of two: it must also carry the fee-row segregation the mask could
   not deliver, since a rewrite that improves general reachability without addressing the
   66-row fee block would still leave that block winning 58% of top-3 slots.
3. ~~Close the 28-fact index gap, and land the permanent drift check with it.~~ ✅ **DONE** —
   real gap is 15 of 246; `scripts/check_facts_index_sync.py` + `tests/test_facts_index_sync.py`
   run on every `pytest`.
4. **Then** the three fact-set domains (service-levy bound, market-stall exclusions, TIN) —
   written **with** the retrieval fix and regenerated in **one** R15 Kaggle cycle, not before it.
5. **Then the floor, on a MARGIN rather than an absolute score.** Still ships before any pilot.

**Ordering rationale, on the record:** *"if retrieval or override is the mechanism, adding five
domains of facts may not fix the answers, and we'd want to know that before writing them."* The
mechanism is retrieval, so facts written today would enter an index where fee rows take 58% of
the slots and correct facts sit at rank 19–164. **They stay paused on purpose.**

**Step 1's measurement changes what step 2 has to be, not the order.** "Measure the mask against
the regen and choose on evidence" was itself instruction #1 this round, on the reasoning that a
cheap offline test could settle the question before committing to a GPU cycle. It settled it —
against the cheap option. The regen was never in doubt as *a* requirement; what was open was
whether it could be avoided for this specific piece, and the answer is no.

---

**🛑 FEATURE WORK IS STOPPED (founder, 2026-08-14) pending pilot readiness.** **P2 IS NOW CLOSED, and the number it was stopped on has been re-measured on the same 48 questions: 39.6% → 58.3% correct, 39.6% → 18.8% wrong (entry at the top). The compute path went from 13 wrong of 24 to 3; the fact path did not move at all.** The assessment's
verdict was **not yet**, on measured grounds: **39.6% of 48 natural-register questions were
answered wrongly** (adjudicated 2026-08-11), 13 of 24 compute-path questions were wrong, and the
WhatsApp handler could drop an answer in silence. Two blockers, in order — **P1 the silent-drop
path (DONE, entry below)** and **P2 the compute-path wrong-number cluster**. They sit above the
severity board because *"which defect next"* and *"what stands between us and learning from real
users"* are different questions with different answers.

**P2 has its first landed item: the decimal separator fix (`ce677fa`, entry below).** Founder
order from here (2026-08-14): **second ack** → `MODAL_API_TOKEN`/`HF_TOKEN` fingerprints → full
percent exclusion → **then back to the routing cluster (B, C, A2, A3)**. The founder's reasoning
on that last hop is on the record and outranks the infrastructure items: *the fingerprints are a
precaution, the wrong answers are the product* — the first real message ever sent got a wrong
answer, and the assessment puts natural-register accuracy at 39.6% wrong.

**🚀 v16 IS LIVE IN PRODUCTION (2026-08-09, `ec9cbb3`).** The router + rules engine +
orchestrator pipeline now serves every request. Cutover entry immediately below — deployed
commit, the two gate results that authorised it, and the rollback procedure.

**➡️ QUEUE (founder-ordered, 2026-08-11): ~~D-FIDELITY-1 widening~~ → ~~minimum wage~~ →
~~VAT/EFD compute route~~ → ~~intermediate-figure hole~~ — **ALL FOUR DONE.** The
intermediate-figure hole was **investigated and only PARTLY closed, deliberately**: D-FIDELITY-3
ships the deduction-from-the-levy family at measured zero cost, and **the paraphrase family is
explicitly still open** (entry below — read the framing before citing this as closed).
**~~decomposition silently dropping a sub-question~~ — DONE**: the orphan-connector split and
its measure-matched preamble carry shipped 2026-08-11 (entry below), and the finding that
bounds it is that **decomposition is less load-bearing than it looked** — four multi-domain
questions are answered in full without being split at all. **Next is not yet chosen — see
🧮 THE BOARD immediately below**, which lists every logged and unfixed item including six that
are live and wrong in production today, with a recommendation (C1 → A1 → A3) rather than a
decision.
**Two new items were opened by this cycle: D-FIDELITY-1 blanks two CORRECT bodies** (its
own-levy rule never consults `_acceptable`, unlike its sibling rule) and the **conclusion-
labelling live check**, which is priced below and deferred to the next adapter version.

**The threshold-comparison class is now closed on all three members.** SDL headcount, minimum
wage and VAT/EFD registration are each a deterministic route with no generation on the path.
The argument was the same every time and was measured three times: supplying the right number
does not produce the right comparison.

**✅ th_16 IS FIXED IN PRODUCTION (2026-08-10, `a372d2b` + copy fix).** Two wording fixes were
tried first and both were rejected on evidence — the second because four of six candidate
wordings fabricated **TZS 765,900 as a legal maximum wage**, more dangerous than the nonsense
phrase they would have replaced. The class fix shipped instead: a deterministic `minimum_wage`
route with **no generation on the path at all**, live-verified on 12 canaries (8 wage rows
changed, 4 controls byte-identical). Entry below carries the verbatim before/after — **three of
the "before" answers were worse than th_16 and none was on any list**, including one instructing
an employer to claw back lawfully paid wages. Unit normalisation remains its own item.

**Two findings from this cycle outrank the wiring itself and are written up as their own
entries: CONTAINER-PATH-1** (wiring v16 with defaulted phrase lists would have silently
reopened SAFETY-1 — 39 OOC phrases instead of 107, invisible to every offline instrument;
second occurrence of R16's class) **and the STANDING LIMITATION** (the regex gate positively
credits eval_318 and eval_320, the two worst defects the cycle found — which is why the judge
overlay is now mandatory).

## 🔁 B / C / A2 / A3 RE-CHECKED — one closed, five still live (2026-08-15)

Re-measured with both signals the original 2026-08-11 diagnosis used: the offline routing
predicates, and the reply itself (an appended deterministic *working* is the observable
signature of the engine having run). `scratch/bca_recheck.json`, `scratch/bca_live_now.json`.

| item | row | offline | live | verdict |
|---|---|---|---|---|
| **B** SAFETY-2 | nat_16 | `residency_unclear=True` | declines, names the 183-day test | ✅ **CLOSED** (`8b90b25`) |
| **C** wrong party | nat_08 | routes `nssf`, `nssf_party='total'` | **TZS 130,000** where the employee share is **65,000** | 🔴 reproduces |
| **A2** levy cue gap | nat_09 | `_natural_levy` → None | employee share stated as **TZS 960,000 (80%)** of a 1.2M salary | 🔴 reproduces |
| **A2** | nat_13 | `_natural_levy` → None | **TZS 52,000**; correct PAYE is **103,000** | 🔴 reproduces |
| **A2** | nat_14 | `_natural_levy` → None | **TZS 28,000**; correct PAYE is **6,400** | 🔴 reproduces |
| **A3** applicability | nat_04 | `payroll_ctx=False`, `applic=False` | SDL quoted at **0.5%** (it is 3.5%), sourced to **NSSF** | 🔴 reproduces |
| A1 controls | nat_01, nat_19 | `sdl`, `wcf` | — | ✅ stay fixed |

**Five of six still produce a wrong number live.** Two have moved without closing: A1's
`ngapi` fix gave nat_13/nat_14 `money_ask=True`, leaving the levy as the sole blocker, and
nat_04's levy now resolves to `sdl`, leaving payroll-context and applicability. The
diagnoses narrowed; the defects did not.

### ⚠️ A FIGURE-PRESENCE CHECK IS NOT A CORRECTNESS CHECK

Two rows scored `has_expected=True` in the live harness and are badly wrong. nat_08 contains
`65,000` — inside the parenthetical split, while the **headline says TZS 130,000 is what is
deducted from the user's pay**. nat_09 contains `240,000` — attributed to the employer, beside
a fabricated *"mfanyakazi anachangia TZS 960,000 (80%)"* and a total equal to the entire
salary. Substring-presence assertions are a smoke test, not a verdict; both rows had to be read.

### 🔎 WHY THE CONCORD CLOSURE DID NOT SUBSUME C — the limit of a generative test

C is an **object-concord** instance. Swahili marks the object with an infix between tense and
stem, and the class is closed: `-ni-` (me), `-ku-` (you), `-m-` (him/her), `-tu-` (us),
`-wa-` (them). nat_08 is *"wana**NI**kata … mshahara **wangu**"* — they cut **ME**. nat_04 is
*"ile ya mafunzo ina**NI**anza lini"*.

**The 2026-08-15 audit enumerated five paradigms and this was not one of them.** Subject
prefix and possessive were closed; the object infix was missed. `_APPLICABILITY_CUES` already
closes it for exactly one verb (`-nihusu`/`-kuhusu`/`-tuhusu`), so the discipline existed in
the codebase and had been applied in one place.

But the sharper reason C survived is a property of the instrument, and it generalises:

| list | members | first-person members |
|---|---|---|
| `_NSSF_EMPLOYEE_CUES` | 7 | **0** |
| `_NSSF_TOTAL_CUES` | 10 | **0** |
| `_APPLICABILITY_CUES` | 13 | 5 |
| `_WAGE_PAY_CUES` | 19 | 6 |
| `_PAYROLL_CTX` | 28 | 5 |

> **`test_every_cue_with_a_person_form_has_its_concord_counterpart` derives a counterpart FROM
> an existing member. A list with ZERO first-person members has nothing to derive from — so a
> generative completeness test closes PARTIAL coverage and is blind to ABSENT coverage.**

C survived the closure because its class was at 0%, not 30%. Every list the test fixed was
one somebody had already half-populated. This is the same shape as the SAFETY-1 finding —
an instrument complete on its own axis and structurally blind off it — and it is the second
time this week that the blind spot was *"the case where none of the thing exists yet"*.

**A2 is NOT a class.** `mfuko`, `serikali inachukua`, `kupeleka kwa TRA` are synonyms for a
levy — an open lexical set, where you genuinely cannot know the next phrasing. It is the one
of the four that deserves the failure-driven treatment, and it is also the costliest: all
three rows produce confident wrong figures with no working.

### The pricing this implies

Object concord is **well measured**, unlike everything else closed this week: **52 eval and
385 train questions** contain an object infix. So a sweep here is real evidence rather than a
formality — the opposite of SAFETY-2, where the corpus was structurally blind. R17's authored
probes are still required for the members the corpus lacks, but the sweep is not a ritual.

Not implemented. Recorded so the next cycle starts from the measurement rather than the
2026-08-11 diagnosis, which is now stale in two of its four rows.

---

## 🔠 CONCORD CLOSURE — the router now knows "we", in every tense (2026-08-15)

**Approved ahead of B/C/A2/A3 on the argument that each of those four is one member of a
class.** Doing them individually pays the review-and-deploy cost four times and leaves the
classes open. Written from the grammar, not from the failures — which is the whole point,
and which is why it found things no failure log contains.

### The audit asked the wrong question, and under-counted by 2.4×

The audit (11/37 members, 30%) tested WORD membership: does the router know `vingapi`? But a
cue list is made of PHRASES. `mauzo yangu` was present and so was `mauzo yetu` — while
`biashara yangu ina mauzo` was present and `biashara yetu ina mauzo` was not. No word-level
audit can see that gap. Applying the paradigm to every cue phrase instead gives the honest
number: **51 derived counterparts absent, not 21.**

### Two corrections to the audit, both found by writing the paradigm out properly

| audit said | the grammar says |
|---|---|
| the `-ngapi` class has **8** members | **5**: ngapi (cl.9/10), wangapi (cl.2), mingapi (cl.4), mangapi (cl.6), vingapi (cl.8). `yangapi`/`zangapi`/`kiangapi`/`pangapi` are not Swahili — cl.4 and cl.6 take mingapi/mangapi and cl.10 takes the bare form. Reported coverage 2/8; the honest figure is **3/5** |
| the contraction class has 3 members (incl. `shngapi`) | **2**. `shngapi` was invented by the audit — 0 corpus occurrences and not a grammatical form |
| `nachangia` "is in no cue list at all" | **it is in `_APPLICABILITY_CUES`.** The claim was wrong; the gap was in `_PAYROLL_CTX`/`_WAGE_PAY_CUES`, which is a different and smaller statement |

### 27 of 58 counterparts were already handled — and only by luck

Cue lists match with `phrase in text`. The colloquial 1sg present `na-` is a **substring** of
the 1pl `tuna-`, so `tunauza` already matched `nauza` and `tunachangia` already matched
`nachangia`. **The luck runs out at every other tense**: `nime-`, `nili-` and `nita-` are not
substrings of `tume-`, `tuli-`, `tuta-`.

> **The router understood "we pay" and never understood "we PAID" or "we WILL pay".**

That gap has a precise shape, and no failure log would ever have named it, because it is a
property of the paradigm rather than of any one question. It is also the `waajiri` → `wajiri`
mechanism from the normaliser pricing, seen from the other side: a substring collapse that
happens to be benign because the two strings are morphologically related. Benign here, by
luck. (`tumemuajiri` was covered via the NOUN `muajiri` = employer — coincidence, not
morphology, and the fragile kind.)

### What shipped: 31 real additions, and the test asserts RECOGNITION not membership

Requiring literal list membership would have added 27 lines that change no behaviour and
taught the next maintainer that the check wants list-stuffing. `tests/test_concord_closure.py`
applies the paradigm to whatever is in the cue lists today and demands each counterpart be
**matched** — by itself or by a shorter existing cue. Add a cue tomorrow and forget its
counterpart, and the suite fails. Same shape as `test_every_swahili_digraph_phrase_has_its_variant`.

**The test found two gaps I had missed while writing the patch by hand** — `tuna namba ya vat`,
and six 1pl past forms in the hardcoded OOC fallback. That is the check doing its job on its
first run, against its own author.

| list | added |
|---|---|
| `_OWN_TURNOVER_CUES` | 7 — the ownership gate is what makes the VAT comparison run at all |
| `_VAT_REGISTERED_CUES` | 7 — every member was a `nime-` perfect; not one 1pl form existed |
| `_WAGE_VIOLATION_CUES` | 4 — `tunakiuka` was added by hand once; its four future-tense siblings were not |
| `_PAYROLL_CTX` / `_WAGE_PAY_CUES` | 3 + 3 |
| `_NONMONEY_ASK` | 3 — mangapi, vingapi, mingapi |
| `_MONEY_ASK` + `_EXPLICIT_MONEY_ASK` | `shingapi` |
| `_VAT_REG_CUES`, `_TAKEHOME_ASK` | 1 + 1 |
| `config.ooc_phrases` | 1 (`nunua shamba`) |
| `HARDCODED_OOC_PHRASES` | 6 (fallback path only) |

**Closure is LINEAR, not quadratic** — the reason this was affordable as one item. Concord is
functional: `mauzo` takes `yangu`/`yetu` and nothing else; `mauzo langu` is ungrammatical, not
an unhandled variant. Each cue gains exactly one counterpart. The cross-product fear (10 nouns
× 15 possessives = 150) is not a real cost.

### The semantic decision a mechanical closure would have got wrong

`mingapi`/`mangapi`/`vingapi` went to `_NONMONEY_ASK`, **not** `_MONEY_ASK`. Money in Swahili
is cl.9/10 (shilingi, fedha, pesa), so a money ask is always the bare `ngapi`; the other three
count periods and objects. Adding them to the money list "to complete the class" would be a
category error wearing a grammar costume. `cn_01`/`cn_02` pin it.

`shingapi` went in **bare**, unlike `ngapi`, and that is not a relaxation of R17. Bare `ngapi`
is ambiguous (asilimia/siku/mara ngapi) which is why it is verb-qualified; `shingapi` carries
`shilingi` inside it and has no non-money reading to guard against. It also needed
`_EXPLICIT_MONEY_ASK`, because otherwise the fix would have been silently conditional on no
count word being present.

### R17: sweep + authored probes

**Blast radius over 5,529 corpus questions: 1 pre-existing row changed route** — the live SDL
question of 2026-08-14, `none → sdl`, which is the fix. **0 classification changes. 0 changes
across the 400-row gate corpus and 4,754 training questions.** The BEFORE was captured from a
pristine `git worktree` of HEAD, not from a monkey-patch, because the patch and the edit had
already diverged.

That clean sweep is **weak evidence and known to be** (R17): 38 of the additions have zero
corpus occurrences, so the sweep could not have found a defect in them. `eval/refusal_gate/
concord_1pl_in_scope_020.jsonl` carries 20 authored probes — **10 paired, 10 negative**.

The paired form is deliberate: each 1pl question must route **exactly like its 1sg twin**.
That is stronger than pinning an expected route, which would pass by coincidence if both
twins broke the same way.

### The withholding tool does not work in the present tense

`tunaagiza bidhaa` was going to be withheld, because `naagiza bidhaa` already over-refuses an
in-scope question (ov_04). Withholding it buys **nothing**: `naagiza bidhaa` is a substring of
`tu-naagiza bidhaa`, so the wrong refusal already reaches 1pl speakers. **The ov_04 defect is
wider than ov_04 records.** `cn_10` pins it as a known wrong answer, not an endorsement.

The exercise also found a **fourth over-broad OOC phrase** the digraph sweep could not have:
`nikiagiza` refuses *"nikiagiza bidhaa kutoka nje je nasajili VAT lini"*, an in-scope VAT
registration question. It has no digraph in it, so only the person paradigm could reach it.
`tukiagiza` is withheld with that reason on the record.

Suite: **1006 passed** (+28).

### ✅ DEPLOYED AND VERIFIED LIVE (`c60a0b9`, 2026-08-15) — 9/9

Full R16 cycle: `modal app stop chike-inference --yes` → `PYTHONIOENCODING=utf-8 PYTHONUTF8=1
modal deploy`. Artifact `scratch/concord_live_after.json`, written before any console output.
**56.5s first-probe latency confirms fresh containers.**

**The BEFORE was not re-measured this cycle** (founder skipped it) — and did not need to be,
because both THE CHANGE probes have a documented prior state in artifacts committed yesterday.
That is what per-run artifacts are for, and it is the second time this session they have stood
in for a run that could not be repeated:

| probe | documented BEFORE | AFTER (live, 2026-08-15) |
|---|---|---|
| `cl_01` the verbatim 2026-08-14 **SDL** question | `guard_a_live_after.json` → **the clarification** (*"nimeona umeandika wafanyakazi 14…"*) | **`SDL = 3.5% × TZS 6,000,000 = TZS 210,000`** — deterministic working |
| `cl_02` the verbatim 2026-08-14 **NSSF** question | `variants_live_after.json` → *"unachangia asilimia 10 ya mshahara mkubwa wa jumla"* — rate stated, **never applied** | **`NSSF (sehemu ya mwajiri) = 10% × TZS 800,000 = TZS 80,000`** |
| `cl_09` the `arzi` refusal | refusing (`cfg_01`) | still refusing |
| `cl_08` BRELA control | TZS 22,000 | byte-identical |

**BOTH LIVE WRONG ANSWERS OF 2026-08-14 ARE NOW CORRECT, AND BOTH TOOK THREE COMMITS.**
`a435cf5` fixed the levy cue (`hifazi`), `19199d0` stopped the SDL one asserting a falsehood,
and this one moved both onto the engine. **`chg_01` is no longer a partial** — the rate was
right a day ago and the arithmetic was missing; the working is now there.

Container-loaded proof: `cl_03` (`nunua shamba`, present in `chike_config.json` and absent
from `HARDCODED_OOC_PHRASES`) refuses correctly — so the container read the CONFIG, not the
baked fallback. `cl_04`/`cl_05` are 1pl questions the closure exists for; `cl_05` returns
`SDL = 3.5% × TZS 4,000,000 = TZS 140,000` with working.

`cl_06`/`cl_07` are the count-ask negatives and both hold: *"Vibarua vingapi ninaweza kuajiri
bila kulipa SDL"* answers **"Kizingiti cha SDL ni wafanyakazi 10 AU ZAIDI"** — a threshold, not
a shilling amount. The semantic placement of `vingapi` in `_NONMONEY_ASK` is confirmed on live
weights.

### ⚠️ ONE REPLY PASSED ITS ASSERTION AND IS STILL FABRICATED

`cl_06` — *"Maduka mangapi yanatakiwa kuwa na EFD katika soko moja"* — returned:

> **"Kiwango cha juu cha maduka yanayohitaji EFD katika soko moja ni 10."**

**No such rule exists.** The probe passed because it asserts only what it was written to assert
(no refusal, no money answer), and on that it is correct: the count ask did not become a money
ask. But the fact path invented a threshold rather than declining, which is the Item 2 / D1
class again — *the model prefers a confident number to an admission*.

Two things worth separating. The question is one **I authored**, not a user's, so this is not a
new live defect and does not change the board. And the probe was **not wrong to pass** — a
negative probe that also policed truthfulness would have been testing two things and failed
for the wrong reason. Logged here rather than folded into the probe, because the fix belongs to
D1 (the next adapter) and not to a cue list.

---

## 🔤 AN OOC LIST IS ONLY AS STRONG AS ITS WEAKEST SPELLING (2026-08-14, promoted 2026-08-15)

**Promoted out of the variant-deploy entry because it is the finding, not a deploy note.** The
BEFORE capture of `a435cf5` was not a baseline. One letter — `ardhi` written `arzi`, the
ordinary dh→z spelling — stood between a user and fabricated capital-gains law. Verbatim, from
`scratch/variants_live_before.json`:

> `nimeuza arzi yangu ya mwanza nimepata faida nalipa kodi gani`
> → **"Kodi ya zuio ya asilimia 10 inatumika kwenye mauzo ya ardhi ya muda mrefu."**
>
> `nataka kuuza arzi yangu je nalipa kodi kiasi gani`
> → **"Kodi ya mauzo ya ardhi na majengo ni asilimia 2% ya thamani ya soko."**

Neither rate exists. Both are stated as law, in the confident register, on a topic the OOC
list exists precisely to intercept.

**This is the SAFETY-1 leak class reopening — but not through a missing concept.** SAFETY-1 was
closed by an audit that asked *"what topics are we failing to refuse?"* and added 54 phrases.
That audit was complete at the level of concepts and could not have found this, because the
concept was already covered. The hole was **orthographic**. A refusal list is a lexical
instrument, and a lexical instrument is only as strong as its weakest spelling of its
strongest phrase.

### The second instance is the confirmation, and it arrived within 24 hours

One instance is an anomaly. **Two is the axis.** The concord closure found the same class of
hole on a different axis: `nikiagiza` refuses *"nikiagiza bidhaa kutoka nje je nasajili VAT
lini"* — an in-scope VAT-registration question. It is not a spelling variant. It contains no
digraph, so the orthographic sweep could not have reached it; it is an **inflection**, and only
writing the person paradigm out found it.

So the generalisable claim, now with evidence on both sides of it:

> **A lexical guard has three independent axes — CONCEPTS, SPELLINGS, INFLECTIONS — and
> completeness on one says nothing whatsoever about the other two.**

SAFETY-1's audit is the proof by construction. It was a **complete** audit: it asked *"what
topics are we failing to refuse?"*, enumerated them, and added 54 phrases. That completeness
was real and it held — no capital-gains *concept* has leaked since. It was also **blind to the
other two axes by construction**, because the question it asked cannot see them: a concept
already covered will never show up as a missing concept, however it is spelled or inflected.

That is why "we audited this" is not a defence, and why the two follow-on instruments are
shaped the way they are — `test_every_swahili_digraph_phrase_has_its_variant` closes the
spelling axis and `test_every_cue_with_a_person_form_has_its_concord_counterpart` closes the
inflection axis, both by generating from a paradigm rather than by asking a human to remember.
Neither could have been derived from the SAFETY-1 audit, and neither replaces it.

**The open question this leaves:** are there other axes? Register and word order are the
candidates — a phrase list keyed on `nimeuza ardhi` is equally blind to a passive
(*"ardhi ilishauzwa"*) or a topicalisation (*"ardhi, niliiuza mwaka jana"*). Neither has been
measured. Logged as a question, not a finding.

---

## ✅ SAFETY-2 / D-RESIDENCY-1 CLOSED — by declining, because the obvious fix was worse (2026-08-15)

**The oldest live wrong number on the board.** A1 rendered **TZS 1,028,000 instead of
TZS 600,000** as deterministic *working* for `nat_16`, tracked 2026-08-06 and never
implemented. D-FIDELITY-1 structurally cannot catch it: body and working agreed, because both
derived from the same mis-resolved input.

### Why it was two weeks old — a measurement answer, not a priority one

`wakazi` (26 train / **0 eval**), `resident` (8/**0**), `uraia` (9/**0**). The eval set cannot
pose a question whose answer depends on residency.

> **No instrument we own could have validated A1's guard, before or after building it.**

So the constraint was stated before the work started, not discovered during it: **the probes
had to be authored, there was no sweep to run, and a clean sweep would have proved nothing.**
That is R17 arriving from the opposite direction — corpus statistics told us the instrument
was blind *in advance*, rather than 15 adversarial probes telling us afterwards. Measuring the
corpus for the vocabulary a fix depends on is now a cheap pre-flight for any lexical work.

### The premise needed correcting, and the correction made things worse

The corpus is **not** empty of foreignness vocabulary — **71 eval rows carry it**, `mgeni`
alone appearing in 46. But every one is a **GN 487A business-licensing** question. So:

| vocabulary | eval presence | what it is about |
|---|---|---|
| residency (`wakazi`, `resident`, `uraia`) | **0** | — |
| foreignness (`mgeni`, `raia`, `kigeni`) | **71 rows** | GN 487A, a different regulation entirely |

**That is worse than an empty corpus.** The obvious cue candidates have plenty of corpus
presence, all of it on questions where firing would be wrong.

### THE PROPOSED FIX WAS DISQUALIFIED ON THREE INDEPENDENT GROUNDS

The 2026-08-06 entry proposed extending `_PAYE_NONRESIDENT_CUES` with permit and foreignness
phrasings. Its own warning — *"do not close this by fixing the cue list and declaring the class
handled"* — turned out to be literally correct.

**1. CITIZENSHIP IS NOT RESIDENCY, and the proposed cues confuse them.** Tanzanian tax
residency is decided by **presence** — a permanent home plus presence in the year, or 183 days,
or an average 122 days over three years — and never by nationality. A Kenyan living in Dar for
five years is a **resident** on progressive bands; a Tanzanian citizen abroad may be
non-resident. `si raia wa tanzania`, `mfanyakazi wa kigeni`, `mgeni` and `expatriate` are not
evidence of non-residency. They are a category error, and shipping them would have produced
wrong numbers *with the engine's authority behind them* — the very defect being fixed.

**2. WE DO NOT OWN THE TEST.** `locked_facts.json` carries `paye_nonresident_flat_rate` (15%
final withholding) and **no definition of who is a non-resident**. Zero corpus occurrences of
the 183-day test. A cue list cannot encode a rule the corpus has never verified (R2/R4).

**3. THE TRADE IS 3-FOR-1 AGAINST.** 144 corpus rows route to `paye`; 8 mention foreignness.
Three already resolve correctly via the explicit `asiye mkazi` cue, one is the deferred
mixed-residency case, one is `nat_16` — and **three would have been BROKEN**:

| row | why the proposed cue breaks it |
|---|---|
| *"Mfanyakazi mgeni anapata mshahara wa USD 5,000"* | foreign employee, residency never raised |
| *"…PAYE ni ngapi, na kama **mgeni** angependa kufanya kazi hapa…"* | the foreigner is a hypothetical aside, not the taxpayer |
| *"…unapoingia kwenye **kibali** kikubwa cha PAYE"* | **`kibali` here means TAX BRACKET, not permit** |

That last one is the clearest argument in this codebase for context-qualified cues over bare
words: a bare `kibali` cue reads a tax band as an immigration document.

### AND THE COST IS ASYMMETRIC IN THE DIRECTION THAT MATTERS

| monthly salary | resident bands | flat 15% | if wrongly flagged non-resident |
|---|---|---|---|
| TZS 300,000 | 2,400 | 45,000 | **18.75× overcharge** |
| TZS 400,000 | 10,400 | 60,000 | 5.8× |
| TZS 4,000,000 | 1,028,000 | 600,000 | *(the tracked defect: 1.7× the other way)* |

**The bug overcharges one high earner. The proposed fix would have overcharged many low ones,
by an order of magnitude more.** A fix that is worse than the defect at the salaries our users
actually have is not a fix.

### SO THE FIX DECLINES — and that is the honest answer, not a fallback

`routing.paye_residency_unclear()` detects residency raised **without being settled**, and the
orchestrator returns `clarification.PAYE_RESIDENCY_UNCLEAR` instead of computing either figure.

**TZS 600,000 would ALSO have been a guess.** *"hana residence permit ya kudumu"* says the
engineer lacks **permanent** residency and says nothing about days present. An engineer on a
one-year work permit who is here 200 days **is tax-resident**. Neither figure is supported by
the question, so asking is not the cautious option — it is the only correct one.

The copy names the **183-day test** explicitly, because a generic *"is he a resident?"* invites
the answer *"he's Indian"* — the exact confusion that produced this defect. It deliberately
states **neither figure**: offering both would hand over two numbers with our authority
attached and invite the user to pick the smaller.

14 authored probes (`eval/accuracy_gate/residency_unclear_probes_014.jsonl`), **4 positive and
10 negative** — the negatives outnumber the positives deliberately, because the measured danger
is over-triggering. 0 firings across the 400-row gate corpus.

### 🔁 THE SUBSTRING HAZARD, THIRD INSTANCE TODAY — and this one was live

Writing the probes exposed a **pre-existing wrong answer nobody had logged**: `si mkazi wa
kudumu` **contains** `si mkazi`, so the engine read *"not a PERMANENT resident"* — an
immigration status — as *"not a resident"*, a settled tax determination, and applied flat 15%.
A wrong number with the engine's authority on it, from the same family as the defect this item
is about, found by accident.

That is the third instance in one day of the same mechanism:

| | narrow phrase | swallowed by |
|---|---|---|
| orthographic work | `waajiri` | `wajiri` (benign, by luck) |
| concord closure | `naagiza bidhaa` | `tunaagiza bidhaa` (leaked a wrong refusal into 1pl) |
| **here** | **`si mkazi`** | **`si mkazi wa kudumu` (live wrong figure)** |

> **Substring matching over a hand-written cue list is convenient exactly until two phrases in
> the language nest — and then it is silent.**

Fixed with `_strip_unclear_spans`, which blanks the ambiguous phrases before any explicit cue
is tested, applied inside `paye_resident()` itself so the second call site
(`compute_paye_each`) cannot keep the bug.

**What is NOT closed:** the entry's deeper point stands. The class is *"engine authority applied
to a mis-resolved input"*, and residency is one instance. This fix closes the instance and adds
a pattern — **detect ambiguity and decline** — that the class can reuse; it does not close the
class.

Suite: **1025 passed, 1 skipped**.

### ✅ DEPLOYED AND VERIFIED LIVE (`8b90b25`, 2026-08-15) — 8/8

Full R16 cycle; artifact `scratch/safety2_live_after.json`. **80.0s first-probe latency
confirms fresh containers.**

**THE OLDEST LIVE WRONG NUMBER ON THE BOARD IS GONE.** `nat_16`, verbatim, on live weights:

> **BEFORE** (tracked 2026-08-06): `TZS 1,028,000`, rendered as the deterministic *working*.
>
> **AFTER**: *"…kwa kodi ya Tanzania, mfanyakazi ni MKAZI au SI MKAZI, na hili **haliamuliwi na
> uraia wala aina ya kibali** — linaamuliwa na muda anaokaa nchini. Mtu anayekaa Tanzania siku
> **183** au zaidi… huhesabiwa kama mkazi, hata kama ni raia wa nchi nyingine."*

Neither figure appears. Nine days from tracking to closure, and it closed by **declining**.

| probe | result |
|---|---|
| `sf_01` nat_16 verbatim | **declines, names the 183-day test, states neither figure** |
| `sf_02` the Swahili phrasing (`hana kibali cha ukaazi wa kudumu`) | same — it did not need its own cue |
| `sf_03` `asiye mkazi` on TZS 5,000,000 | **`PAYE (asiye mkazi) = 15% × 5,000,000 = TZS 750,000`** — the explicit case still computes |
| `sf_04` foreign employee paid in USD | currency clarification, **not** a residency one |
| `sf_05` **`kibali kikubwa cha PAYE`** | **`PAYE = TZS 68,000 + 25% × (1,000,000 − 760,000) = TZS 128,000`** |
| `sf_06` ordinary PAYE, laki sita | `TZS 36,000`, correct |
| `sf_07`/`sf_08` BRELA + the concord SDL question | hold; `TZS 210,000` confirms the previous deploy survived |

**`sf_05` is the negative worth naming.** *"unapoingia kwenye **kibali** kikubwa cha PAYE"*
computes correctly on live weights — so the false positive the proposed cue list would have
created is confirmed avoided, not merely predicted offline. A bare `kibali` cue would have
turned a tax-band question into an immigration finding and taxed a resident at flat 15%.

The three-for-one trade is now measured in production rather than argued: **one wrong answer
removed, zero correct answers lost.**

### ⚠️ Unrelated: an intermittent native crash in `test_retrieval.py`

A `Windows fatal exception: access violation` aborts the suite under pytest's random ordering,
in the faiss/numpy path. **It is not from this work** — it reproduces on stashed HEAD, and at a
*different line* each time (324, then 353), which is the signature of a native ordering/memory
issue rather than a logic one. `pytest tests/test_retrieval.py` alone passes 18/18, and
`pytest -p no:randomly` gives a clean full run. Logged as an observation with the reproduction,
not folded into this item.

---

## 🔬 SAFETY-2 IS TWO WEEKS OLD BECAUSE NOTHING WE OWN COULD MEASURE IT (2026-08-15)

**This reframes the oldest live wrong number on the board from a priority question to a
measurement one.** A1 / SAFETY-2 / D-RESIDENCY-1 renders **TZS 1,028,000 instead of
TZS 600,000** as deterministic working, tracked 2026-08-06, never implemented.

The 455-token unmeasured list says why:

```
26 wakazi      9 uraia      8 resident        ← all zero in eval
```

**`wakazi` / `resident` / `uraia` are the entire distinguishing vocabulary of resident vs
non-resident PAYE.** They occur 43 times across the training corpus and **not once in any eval
question**. The eval set cannot pose a question whose answer depends on residency, so:

> **No instrument we own could have validated A1's guard, before or after building it.**

That is a better explanation for two weeks of inaction than priority was. It also **fixes the
constraint on the fix**, before it is started:

> **When SAFETY-2 is built, its probes must be AUTHORED. The corpus provably cannot exercise
> it — there is no sweep to run, and a clean sweep would mean nothing if there were.**

This is R17's rule arriving from the opposite direction. R17 was written because a clean sweep
over 61 OOC candidates was weak evidence; here we know the sweep is worthless *in advance*,
from the corpus statistics, rather than discovering it after 15 adversarial probes. Measuring
the corpus for the vocabulary a fix depends on is now a cheap pre-flight for any lexical work.

`msamaha` / `refund` / `input` (VAT exemption, refund, input tax) are the same shape at 100
combined occurrences and have no tracked defect yet — which, given the above, is not
reassuring.

---

## 📱 THE FIRST MESSAGE THAT EVER REACHED A HANDSET GOT A WRONG ANSWER (2026-08-14)

**Delivery works.** After four failed attempts across two days, one WhatsApp message completed
end to end: ack at 14:53, answer at 14:54, build `f98fc67`. The transcript row, verbatim from
the Dict:

```
sender_domain        lid           (Wappfly's linked-ID form, not @s.whatsapp.net)
ack_sent             true
send_ok              true
fallback             false
error_class          null
model_latency_ms     93108
total_latency_ms     94205
cold_start_suspected true
reply_chars          259
```

Every field the failure taxonomy was built to carry is populated, and the store survived the
container. **The delivery half of pilot readiness is closed.**

**The answer was wrong**, and it is the first user-facing wrong answer this project has ever
produced on a real handset. Verbatim, both halves:

> **Q:** `Efd ni lazima kwa biashara yenye mauzo ya milioni 15`
>
> **A:** `Hapana, si lazima. Biashara yenye mauzo ya TZS 15M+ kwa mwaka inaweza bado kutumia`
> `risiti za mkono ikiwa imejisajili VAT. Mashine ya EFD inatakiwa tu pale unaposajiliwa VAT`
> `au pale mauzo yako yanayofikia kiwango kinachohitajika. Thibitisha na TRA (tra.go.tz).`

Against `efd_threshold_tzs_11m`: EFD is required at **TZS 11M annual turnover and above**, and
VAT registration makes it mandatory **regardless of turnover**. 15M ≥ 11M, so the answer is
required, and:

1. **The verdict is inverted.** *"Hapana, si lazima"* — the one word the trader acts on is the
   opposite of the rule. It advises a business that must have an EFD that it need not buy one.
2. **Sentence 2 is backwards.** *"can still use handwritten receipts **if** it is VAT-
   registered"* — VAT registration is the condition that makes EFD unconditional. The exemption
   limb and the mandatory limb are swapped.
3. **Sentence 3 states the rule correctly** — *"EFD is required only when you are VAT-registered
   **or** when your sales reach the required threshold"* — and contradicts both sentences above
   it. **The model holds the correct rule and applies it to the opposite conclusion.** Same
   shape as SAFETY-3: correct fact, wrong application.
4. **The threshold number never appears.** Sentence 3 says *"kiwango kinachohitajika"* (the
   required level) without naming 11M — so the reply is unfalsifiable to the reader, and a
   trader cannot check it against their own turnover.

**The extraction was fine.** *"milioni 15"* was read as *"TZS 15M+"* correctly. This is not the
decimal bug.

### It is a routing failure, and the engine that would have got it right already exists

`chike/rules_engine/registration_thresholds.py` — shipped `29eb965`, live-verified `90ac9e8` —
is a deterministic threshold comparison with no generation on the path. It was never invoked.
Offline `detect_intent`:

```
'Efd ni lazima kwa biashara yenye mauzo ya milioni 15'          -> none
'Efd ni lazima kwa biashara yenye mauzo ya milioni 15?'         -> none
'EFD ni lazima kwa biashara yenye mauzo ya TZS 15,000,000?'     -> none
'Je, ninahitaji EFD kama mauzo yangu ni milioni 15 kwa mwaka?'  -> efd_requirement
```

**The missing question mark is not the cause** — adding it changes nothing, and neither does
fully normalising the figure to `TZS 15,000,000`. Two independent gates reject it:

- `_EFD_CUES` holds eight forms, all first-person or noun-phrase (`nahitaji efd`,
  `lazima niwe na efd`, `kuwa na efd`). The **impersonal** `EFD ni lazima kwa biashara` — a
  rule stated as a proposition and asked for confirmation — matches none of them.
- `_OWN_TURNOVER_CUES` requires a possessive claim (`mauzo yangu`). *"biashara yenye mauzo ya
  milioni 15"* is a third-person description, so `own` is false and the route would fail on
  this gate even if the EFD cue matched.

The second gate is **not obviously a defect**. It was added deliberately (see its comment: 18
corpus rows were diverted when the route needed only `{obligation cue + magnitude}`) to keep
threshold *lookups* off the comparison path. But this question is neither a lookup nor a
personal claim — it is a **general rule with a concrete figure supplied**, which the comparison
can answer exactly. Closing it needs a third shape, not a loosened cue. **Logged as its own
item; not fixed in this pass.**

**This is the fifth instance of the P2 headline finding** — *the compute path is misnamed; the
failures are routing, not arithmetic.* The correct number was available, the correct engine was
deployed and verified, and neither ran because the trader phrased the question the way traders
phrase questions.

### It is a stable wrong answer, not a coin flip — with one honest gap

The founder observed this reply reproduce **byte-identically four times** — three direct queries
to the model endpoint plus this WhatsApp delivery. Consistent with the greedy-decoding
determinism proven 2026-08-14 (3/3 byte-identical across cold starts of 60.6s/60.8s/97.9s,
through a redeploy and a routing change).

**What is on record is sample four only.** A grep of every artifact in `scratch/` and `eval/`
finds the exact reply string in exactly one file — the transcript dump. The first three samples
were read off a console and never written to disk, so byte-identity across all four is the
founder's observation, not a verifiable artifact. **This is R16's own rule turned on our manual
probing:** the one-liner for querying the model endpoint directly must write its reply to a
file, or every hand-run probe is a measurement that dies with the scrollback. The transcript
store is why sample four survived at all.

**And the sample-one arithmetic is the point.** The assessment put natural-register questions at
**39.6% wrong**. The first question a real handset ever sent landed in that 39.6%. One sample
proves nothing about the rate — but it is the rate arriving exactly on schedule, and it argues
against any reading of the assessment as pessimistic.

### The 82 seconds AFTER the ack — second-ack analysis (2026-08-14)

The same transcript row prices the next user-facing improvement. The ack fired at 12s and the
answer landed at **94.2s** (`model_latency_ms` 93,108, `cold_start_suspected` true), so the user
sat through **82 seconds of silence after being told to wait a moment** — and the ack copy says
*"subiri kidogo"*, which at 82 seconds reads as a broken promise rather than a reassurance.

The bounds are measured, not guessed:

| observation | value | source |
|---|---|---|
| warm p90 | **9.8s** | 48 questions, the same measurement that set `cold_start_suspected`'s 30s threshold |
| cold starts observed | **60.6s / 60.8s / 97.9s** | 3/3 determinism run, 2026-08-14 |
| the one real delivery | **94.2s** | transcript row, build `f98fc67` |

**Second ack at 45s**, because 45 sits in the empty band between them: comfortably above warm
p90, so a warm request never sees it, and below the earliest cold completion ever observed
(60.6s), so a cold request always does. Anything under ~30s risks firing on a slow-warm request
that is about to answer anyway; anything over 60s can arrive after the answer it was meant to
cover.

**One coroutine walking `[(12s, SLOW_ACK), (45s, SECOND_ACK)]`, exiting the moment the answer is
sent, capped at two.** Not two independent timers — two timers can both be in flight when the
answer lands and produce a reassurance *after* the answer, which is worse than silence. The cap
is structural: the list has two entries and the loop cannot outlive it, so no failure mode ends
with a user being told to wait indefinitely.

The copy names the reason, hedges the bound, and ends on the one promise the architecture
actually keeps — `.spawn()` makes Modal responsible for running the job to completion, and the
fallback path sends something even when the model fails:

> `Bado ninafanya kazi kwenye swali lako. Mara ya kwanza huchukua dakika moja hadi mbili kwa`
> `sababu mfumo unaanza upya. Sitakuacha bila jibu — nitakutumia hapa hapa likiwa tayari.`

It does **not** say "sekunde thelathini". A number we cannot keep is how the first ack became a
broken promise at 82 seconds; the range plus the guarantee is what we can actually deliver.

**This does not make the answer faster** — it makes a 94-second wait legible. Warmth costs
~$212/mo for business hours and buys polish, not correctness (unchanged reasoning from the
knobs table below). The second ack costs one Wappfly message on cold requests only.

### VERIFIED LIVE 2026-08-14, and the warm margin is 2.6s — not the comfortable gap implied

R16b live check on build `ad1ed50`, four messages, both directions clean:

| | cold 18:45:25 | warm 18:47:31 | warm 18:49:22 |
|---|---|---|---|
| `acks_sent` | **2** | **0** | **0** |
| `cold_start_suspected` | true | false | false |
| `model_latency_ms` | 64,742 | 9,406 | 5,766 |

The positive fired both rungs and the answer arrived ~20s after rung two. The negative fired
neither. **No secret change was needed and none was made** — 12s/45s are the production
defaults, and shortening them would have made the warm case vacuous, since a warm request
clearing a *shortened* rung proves nothing about the rung that actually ships. A forced-failure
config (the `MODEL_TIMEOUT_S=1` pattern) is right for a path that cannot occur naturally; a cold
start is not that path.

⚠️ **RECORD THE MARGIN: the warm request cleared the 12s rung by 2.6 SECONDS.** The band was
chosen against a warm p90 of 9.8s, and the first warm request ever measured came in at 9.4s —
essentially at p90, not comfortably below it. The design reads as though there is a 2-3× gap
between warm completion and rung one. There is not; there are 2.6 seconds.

**Why this is written down rather than acted on:** any latency regression of ~28% on the warm
path starts firing first acks on requests that are about to answer — the exact over-broad
behaviour the negative case exists to prevent — and it will do so silently, because nothing
alerts on it. `acks_sent` is in every transcript row precisely so this is checkable: **a warm
row with `acks_sent: 1` is the tripwire.** If those appear, the question is whether the model
got slower, not whether the ack timing was wrong.

## 📊 WE TRAINED ON `shingapi` AND NEVER ONCE MEASURED THE ROUTER AGAINST IT (2026-08-14)

The router missed `nalipa shingapi` because `_VERB_MONEY_ASK` requires `\w*lipa\s+ngapi` — a
**space** before `ngapi`. `shingapi` is the ordinary spoken contraction of `shilingi ngapi`, i.e.
**the most explicitly money-marked form in the language**, and it is the one form the money-ask
gate cannot see. Measured across the repo:

| form | occurrences | in `eval/` |
|---|---|---|
| `shilingi ngapi` (spelled out) | 521 across 46 files | **yes** — 3 gate probes + the router eval set |
| `shingapi` (contracted) | **13**, incl. `datasets/tier1a/sft/train_sft.jsonl` | **zero** |

**This is a training/eval corpus gap, not a cue-list bug.** We taught the model a form and then
built every instrument out of the other form. The router was measured extensively and never once
on this input, so the gate was green and the defect shipped.

**It generalises, and the generalisation is measured: 3,996 distinct tokens — 80% of the
training-question vocabulary — never appear in a single eval question.** Restricted to ask-forms
the number is small and immediately actionable:

```
shingapi  mangapi  vingapi   <- trained on, never evaluated
```

`mangapi` and `vingapi` are not typos; they are **noun-class concord** forms of `ngapi` (ma-,
vi-), the same way `wangapi` is — and `wangapi` is already handled, in `_NONMONEY_ASK`. So the
concord family is half-covered by accident rather than by design.

⚠️ **THE RULE THIS ADDS TO R17: sweep the TRAINING corpus, not only the gate corpora.** R17 says
a clean sweep proves only that the corpus lacks the vocabulary, and prescribes authoring
adversarial probes. There is a cheaper source that was sitting unused — **the training set
already contains user-shaped vocabulary the eval set does not.** Diffing the two would have
surfaced `shingapi` before a user typed it, at the cost of one script. Any future cue-list
change should ask: *which forms are in training but in no probe?*

## 🔠 CONCORD AUDIT — the router treats closed grammatical classes as open (2026-08-14)

**Hypothesis confirmed, and it reorders the routing cluster.** The `shingapi` finding suggested
the router's gates were grown one observed failure at a time. Enumerating the classes **from the
grammar rather than from failures** shows coverage tracks *observed frequency*, not membership:

| closed class | why it is closed | coverage |
|---|---|---|
| interrogative concord `-ngapi` | agreement prefix set is fixed by the noun-class system | **2/8 (25%)** |
| money-ask contraction | `shilingi ngapi` → `shingapi` | **1/3 (33%)** |
| possessive 1sg `-angu` | one form per noun class | **3/9 (33%)** |
| **possessive 1pl `-etu`** | same | **1/8 (12.5%)** |
| subject prefix `ni-`/`tu-` | I vs we | **4/9 (44%)** |

**11 of 37 members recognised — 30%.** In every class the high-frequency members are covered and
the rest are not, which is the signature of failure-driven growth.

**The founder's hypothesis about `_OWN_TURNOVER_CUES` is correct.** Concretely missed today, with
corpus frequencies: `zangu` (53 train), `kwangu` (16), `changu` (10), `wetu` (18), `tunalipa`
(16). And **`nachangia` — the contribution verb in the live NSSF question — appears 6 times in
the EVAL corpus and is in no cue list at all**; the whole `kuchangia` family (6 forms) is absent.

### ⚠️ The cost is LINEAR, not quadratic — concord is functional, not free

The obvious fear is a cross-product: 10 head nouns × 15 possessives = 150 entries. **That is
wrong, and the correction is the useful part of this audit.** Each noun takes exactly ONE
possessive form per person — `mauzo` → `yangu`/`yetu`, `duka` → `langu`/`letu`, `mzunguko` →
`wangu`/`wetu`. `mauzo langu` is not a variant, it is ungrammatical. So closing the class means
**adding each existing cue's counterpart**, which is linear in cues already written:

| gate | missing counterparts |
|---|---|
| `_OWN_TURNOVER_CUES` | **8** (`mzunguko wetu`, `biashara yetu ina mauzo`, `duka letu lina`, …) |
| `_WAGE_PAY_CUES` | **4** (`tunalipa`, `tunamlipia`, `tumemlipa`, `tumemlipia`) |
| `kuchangia` family | **6** (absent entirely) |
| interrogative concord | **3** with nonzero frequency (`vingapi`, `mangapi`, `shingapi`) |

**~21 additions close every confirmed class.** The four queued cue fixes (B, C, A2, A3) are each
**one member** of these classes. Doing them first pays the same review-and-deploy cost four times
and still leaves the classes open.

⚠️ **THE RULE: when a cue list is built around a grammatical feature, enumerate the feature. A
closed class can be written down once from the grammar; an open lexical set cannot.** Growing a
closed class from user complaints means every member costs one wrong answer — and Swahili
concord guarantees there will always be more members.

**Not implemented.** ~21 cue additions need their own R17 cycle (sweep + authored probes, since
`vingapi`/`mangapi` have 4–5 corpus occurrences between them) and their own deploy.

### The 456: `wakazi` at 26 occurrences and zero in eval is A1's own vocabulary

Correcting my own number first: the "80% of training vocabulary unmeasured" headline is soft —
**61% of those tokens appear exactly once**, and training has 6.4× more questions than eval, so
most of the gap is Heaps' law. **The real figure is 455 tokens occurring 5+ times in training and
never once in eval.** 18 of them are compliance-load-bearing:

```
34 refund    34 msamaha   32 input     26 wakazi    17 mwajiriwa
 9 uraia      8 resident   9 kutolipa
```

**`wakazi` (26), `resident` (8), `uraia` (9) are the entire distinguishing vocabulary of
A1/SAFETY-2** — resident vs non-resident PAYE, the oldest live wrong *number* on the board,
which renders TZS 1,028,000 instead of TZS 600,000 as deterministic working. Its vocabulary has
never appeared in an eval question. **A1's guard could not have been validated by any instrument
we own**, which is a better explanation for its two-week age than priority was.

`msamaha` / `refund` / `input` (VAT exemption, refund, input tax) are the same shape at 100
combined occurrences.

## 🧠 ITEM 2 — THE FACT PATH CONTRADICTS FIGURES THE USER SUPPLIED (investigated 2026-08-14)

**Both live wrong answers share one shape: the user stated a number, and the answer asserted a
different value for that same slot.**

| the user said | the answer said | the engine would have said |
|---|---|---|
| `laki nane` = TZS 800,000 | *"Kwa mshahara wa **TZS 400,000**, unachangia **TZS 20,000**"* | TZS 80,000 (10% employer share) |
| `wafanyakazi 14` | *"bado una wafanyakazi **chini ya 10**"* | SDL = 3.5% × 6,000,000 = TZS 210,000 |

This is not a rounding error or an arithmetic slip. **It is the model overwriting the user's
input with a memorised one**, and it survives any routing fix, because a correct route only
removes the *opportunity* — it does not remove the behaviour.

### The numbers are traceable to a specific training pair — this is parametric recall, not invention

`datasets/tier1a/sft/train_sft.jsonl` contains:

> **Q:** `Nina wafanyakazi wawili — mmoja TZS 400,000 na mwingine TZS 800,000 kwa mwezi. PAYE ya jumla ni ngapi?`
> **A:** `… Mfanyakazi 2 (TZS 800,000): … Bendi 2 (8%): TZS 250,000 × 8% = TZS 20,000 …`

**Both fabricated figures live in that one pair, and TZS 800,000 is its trigger.** The user's
800,000 retrieved the pair; the reply emitted its *neighbours*. Note what TZS 20,000 actually is
there — a **PAYE band-2 intermediate**, transplanted whole into an NSSF answer. TZS 400,000 is
also the corpus's canonical example salary (6 further pairs in `batch_015`).

**This is the same mechanism as the phantom TZS 26,000 relief (A2), now observed on a wage.** A2
was already the strongest evidence for D1; this makes it a class rather than a quirk: *the model
substitutes a memorised value for a user-supplied one whenever nothing deterministic occupies
the slot.*

### Can a guard catch "the answer contains a figure the user gave, transformed"?

Two candidates were prototyped and measured against **400 rows of real model output** plus the
two live cases (`scratch/item2_contradiction_guard.py`):

| guard | precondition occurs | false positives | true positives |
|---|---|---|---|
| **A — headcount contradiction** (`chini ya N` vs a stated count ≥ N) | **7 of 400 rows** | 0 | 1/1 (live_sdl) |
| **B — salary restatement not derivable from the question** | **24 of 400 rows** | 0 | 1/1 (live_nssf) |

A broader first draft of Guard A — *any* headcount in the answer differing from the stated one —
produced **9 false positives out of 10 flags**, all of them correct answers citing the SDL
**threshold** (10) alongside the user's count. The narrow comparative form is the only usable one.

⚠️ **BUT GUARD B ONLY FIRES BECAUSE OF A COINCIDENCE, AND THIS IS THE FINDING THAT PRICES THE
WHOLE ITEM.** 400,000 is exactly **half** of 800,000. A guard must allow division by small
integers, because legitimate answers split aggregate payroll per person — and **with that
allowance enabled, the true positive disappears entirely** (measured: `allow_quotient=True` →
0 true positives). The guard catches this case only if we forbid a transformation that correct
answers legitimately perform.

That is not a tuning problem. **A fabricated figure and a legitimate transformation are both
just arithmetic relationships to the user's number**, and no arithmetic test separates them. The
question the guard needs to ask is not *"is this number derivable?"* but *"is this number
asserted for a slot the user already filled?"* — which requires knowing the slot.

### Why this prices as an adapter problem, not a guard problem

**The guard is well-defined exactly where it is not needed, and ill-defined exactly where it is.**
Knowing the slot means having routed the question. When the route is correct, the deterministic
engine answers and there is no free-generated figure to check. When the route is missed — which
is what happened in both live cases — there is no slot structure to check against, only prose.

The residual guard is therefore narrow and worth having, but small: **Guard A's comparative form
is real** (a stated 14 is not "fewer than 10" under any transformation, so no derivation
allowance can swallow it) and it is cheap. Its evidence base is thin — **7 opportunities in 400
rows, and the one true positive came from outside the corpus entirely.** That is R17's shape
again, and it means shipping Guard A requires authored probes, not a corpus sweep.

**Guard B should not be built as specified.** It cannot distinguish the two cases it exists to
separate, and the version that catches our one example does so by forbidding correct behaviour.

### ✅ GUARD A IS BUILT (2026-08-14) — the comparative form only

`fidelity.body_contradicts_stated_headcount` + `clarification.headcount_contradiction`, wired
into `_validate_and_clean` on the **fact path** (the compute path already has D-FIDELITY-1/2/3).

**The safety property, which is the whole reason this one is possible:**

> **A stated 14 is not "fewer than 10" under any transformation.**

No derivation allowance is needed because the claim is a **comparison, not a quantity** — which
is exactly what Guard B lacked. The rule may therefore only ever compare a stated count against a
`chini ya N` claim **about the user**; the subject-marker requirement (`una`, `biashara yako`, …)
is load-bearing, because a bare `chini ya 10` is the *threshold*, which every correct SDL answer
states.

⚠️ **DO NOT WIDEN IT BACK.** The first draft — *any* headcount in the body differing from the
stated one — was measured at **10 flags on 400 real rows, 9 of them false positives**, every one
a correct answer citing the threshold beside the user's count. `hc_05` and `hc_09` preserve those
shapes as probes so the widened rule cannot return quietly.

**A fact body cannot be blanked** the way a compute body can — `_render` would emit nothing, and
silence is worse than a wrong answer. It is replaced with clarification copy that quotes the
user's own count back (the `ambiguous_figure` pattern) and declines to answer, because the reason
the body was wrong is that the question never reached the engine, so no authoritative figure
exists to substitute.

Measured: **0 flags across the 400-row gate corpus** (8 preconditions), catches the live case.
10 authored probes, 4 positive / 6 negative — authored rather than swept, because 8 opportunities
in 400 rows cannot support a sweep (R17). Suite **978 passed** (944 + 34 live).

**DEPLOYED AND VERIFIED LIVE (`19199d0`)** — full R16 cycle, artifact in
`scratch/guard_a_live_after.json`. The live case was forceable because `shingapi` still blocks
the money-ask, so that question still reaches the fact path and the model still produces the
contradiction:

| probe | before | after |
|---|---|---|
| `ga_01` the verbatim 14-employee question | *"bado una wafanyakazi **chini ya 10**, hivyo hakuna ulazima wa kulipa SDL"* | *"nimeona umeandika **wafanyakazi 14**… nithibitishie"* |
| `ga_02` a user with **9** employees | correct *"chini ya 10"* | **unchanged** — the guard does not fire on a TRUE claim |
| `ga_03` BRELA control | TZS 22,000 | byte-identical |
| `ga_04` `arzi` refusal from the previous deploy | refusal | still refusing — that change survived this deploy |

`ga_02` is the negative that matters: the difference between "the answer says fewer than 10"
and "the answer says fewer than 10 **and that is false**" is the entire guard, and it is now
confirmed on live weights rather than on probes alone.

### 🚫 GUARD B IS NOT DEFERRED — IT IS IMPOSSIBLE AS SPECIFIED. This is a result.

Recording this as a finding rather than a backlog item, because a deferral invites someone to
try again with more effort, and more effort will not help:

> ⚠️ **A fabricated figure and a legitimate transformation are both just arithmetic relationships
> to the user's number, so no arithmetic test separates them.**

The measurement that proves it: Guard B catches our one live case **only** because TZS 400,000
happens to be exactly half of TZS 800,000, and only if division by small integers is forbidden.
But correct answers divide by small integers routinely — that is how aggregate payroll becomes a
per-person wage. Enable the allowance that correctness requires and the true positive
disappears (`allow_quotient=True` → 0 true positives). The guard can catch the defect or permit
correct behaviour, never both. Had the model fabricated TZS 350,000 the guard would fire; that it
fires on 400,000 is a coincidence about which memorised number surfaced, not a capability.

**The corollary generalises well past this guard, and is the part worth keeping:**

> ⚠️ **The check is well-defined exactly where it is not needed, and ill-defined exactly where it
> is.** Asking *"is this number asserted for a slot the user already filled?"* requires knowing
> the slot, which requires having routed. Where routing succeeds, a deterministic engine answers
> and there is no free-generated figure to audit. Where routing fails — both live cases — there
> is no slot structure at all, only prose.

This shape recurs: a validator that needs the structure the failure destroyed. Expect it whenever
a guard is proposed downstream of the thing that broke. Ask first *what does this guard need to
already be true*, and if the answer is *"the bug did not happen"*, it is not a guard.

### This is now the strongest evidence for D1

**The training corpus supplies the wrong numbers, traceably, and the model prefers them to the
user's own words.** That sentence is the case for the next adapter, and every clause of it is
measured rather than argued:

- **traceably** — TZS 400,000 and TZS 20,000 both live in one identifiable `train_sft.jsonl` pair,
  with TZS 800,000 as its trigger, and TZS 20,000 is a PAYE band-2 intermediate emitted into an
  NSSF answer.
- **prefers them to the user's own words** — the user wrote `laki nane` in the same sentence.
  Extraction read it correctly. The model overrode it.
- **and no guard can close it** — the impossibility result above.

A2's phantom TZS 26,000 relief was already the leading D1 evidence; this promotes it from a quirk
about one memorised number to **a mechanism about all of them**. Guards catch shapes; the model
supplies them. **Not implemented — investigation only, at founder instruction.**

## 🔤 ORTHOGRAPHIC VARIANTS — narrow additions, and why the normaliser was rejected (2026-08-14)

A real user wrote `mfuko wa hifazi ya jamii`. `hifazi` is the ordinary dh→z spelling of
`hifadhi`; it matched no cue, `detect_intent` returned `none`, and an NSSF question fell to the
fact path, which answered **TZS 20,000 against a stated salary of TZS 800,000** — the correct
employer share is TZS 80,000. Nothing else was broken: `parse_amounts` read `laki nane` as
800000 and `nssf_party` read `employer`. **One misspelling was the entire blocker.**

### The normaliser was designed, measured, and disqualified by its own numbers

⚠️ **A CHARACTER-COLLAPSING NORMALISER SILENTLY CORRUPTS SWAHILI NUMERALS.** It sits upstream
of 52 compiled regexes, 40 of them in `swahili_numbers.py`, and Swahili numerals are the
vocabulary richest in `th`:

| written | correct | after `th`→`s` |
|---|---|---|
| `laki thelathini` | 3,000,000 | **100,000** — 30× understatement |
| `wafanyakazi thelathini na watano` | 35 | **5** |
| `themanini elfu` | 80 | **1,000** |

It does not fail loudly; it returns a **different valid number, in the money direction**. That is
the decimal-separator failure mode reintroduced by the fix meant to prevent wrong numbers.
`test_normaliser_would_have_corrupted_numerals` keeps the counter-example executable, so the next
person to propose this meets the measurement rather than the argument.

### ⚠️ THE GENERAL ARGUMENT AGAINST CHARACTER-COLLAPSING: `waajiri` → `wajiri`

**287 of the 290 measured cue-match gains came from ONE substring collapse.** Vowel-collapse
turns the cue `waajiri` (employers) into `wajiri`, which is then a substring of `mwajiri`
(employer). The result is *correct* — both are payroll context — and that is precisely the
problem: **it is benign by luck, not by design.** The mechanism is "collapsing characters made
one word a substring of another," and nothing about that mechanism knows whether the two words
are related. The aggressive variant showed the same mechanism landing badly: the in-scope phrase
`osha` → `osa` matches **86 corpus rows** through ordinary words like `isiyosajiliwa`, harmless
today only because `classify`'s in-scope loop is a documented no-op.

**This generalises beyond this proposal.** Any approach that normalises by discarding character
distinctions — stemming, fuzzy matching, edit-distance cue matching, phonetic keys — buys recall
by making distinct strings collide, and cannot distinguish a collision that helps from one that
harms. Judge such a proposal by *what it collapses*, never by the sample where it happened to
help. The measurements are in `scratch/norm_price_{1,2,3}*.json`.

### What shipped: 27 hand-written variants, 3 deliberately withheld

Hand-written per phrase, never generated. English phrases take no variant — dh→z is a Swahili
process on Arabic loanwords and nobody writes `sreshold`; `arm's length` and `vat threshold` are
on an explicit allowlist so the exclusion is a decision on the record rather than an omission.

| list | added |
|---|---|
| `config.ooc_phrases` | 18 (107 → **125**) |
| `config.in_scope_phrases` | 2 (24 → **26**) |
| `routing._LEVY_CUES` (nssf) | `hifazi ya jamii`, `mchango wa hifazi`, `mfuko wa hifazi` |
| `routing._MONEY_ASK` | `garama gani` |
| `routing._WAGE_VIOLATION_CUES` | `nitaazibiwa` |

**R17 procedure ran in full, and step 2 is again the only step that found anything.** The
corpus sweep returned **0 false positives on all 27 candidates** — provably weak evidence here,
since the pricing had already measured **0 variant spellings across 795 eval and 17,258 training
questions**. The 12 authored probes (`eval/refusal_gate/orthographic_variant_in_scope_012.jsonl`)
found what the sweep could not.

### 🚨 THREE LIVE WRONG REFUSALS, FOUND BY THE PROBES — pre-existing, NOT introduced here

Writing probes in **both spellings** separated "breadth I would add" from "breadth already
there". Three in-scope questions are refused in production **today**, by the standard spellings:

| phrase | refuses this in-scope question |
|---|---|
| `kipande cha ardhi` | *ofisi yangu iko kwenye kipande cha ardhi cha familia je nasajili **OSHA** vipi* |
| `naagiza bidhaa` | *naagiza bidhaa kutoka nje je nasajili **VAT** lini* |
| `forodha` (bare) | *biashara yangu ya forodha ina wafanyakazi 15 je nalipa **SDL*** |

Same shape as bare `hisa` refusing 7 gate questions in the original R17 cycle. **Their variants
were deliberately WITHHELD** — mirroring an over-broad phrase doubles a live defect instead of
closing a gap. `test_withheld_variants_are_absent_and_their_defect_is_pinned` asserts both the
absence and the defect, so nobody "completes the set" later without meeting it. Narrowing them is
its own item with its own sweep, because narrowing can reopen a leak.

### The honest cost of this approach, on the record

**Each variant is purchased with a user getting a wrong answer first.** Per-list additions only
ever fix forms already observed to fail; they are O(new cues) forever and invisible when
forgotten, which is exactly how `hifadhi` got here. That is the price of not taking the
normaliser, and it is a real price, not a rhetorical concession.

Two things pay it down. **`test_every_swahili_digraph_phrase_has_its_variant`** converts "someone
must remember" into "the suite fails" for every future cue. And **the training-corpus diff** (see
the `shingapi` entry above) finds forms *before* a user types them — the training set already
contains user-shaped vocabulary the eval set does not, and diffing the two costs one script.
That diff is the mitigation that makes this approach defensible rather than merely cheaper.

Suite: **963 passed** (929 + 34 live-network).

### ✅ DEPLOYED AND VERIFIED (`a435cf5`, 2026-08-14) — and the BEFORE found more than expected

Full R16 cycle: `modal app stop chike-inference --yes` → `PYTHONIOENCODING=utf-8 PYTHONUTF8=1
modal deploy`. Paired BEFORE/AFTER artifacts in `scratch/variants_live_{before,after}.json`,
written before any console output. The 62.1s first-probe latency confirms fresh containers.

**The BEFORE was not just a baseline — it exposed a live leak producing fabricated tax rates.**
Two `arzi` land-sale questions were not refused, and the model invented law:

> `nimeuza arzi yangu ya mwanza nimepata faida nalipa kodi gani`
> → **"Kodi ya zuio ya asilimia 10 inatumika kwenye mauzo ya ardhi ya muda mrefu."**
>
> `nataka kuuza arzi yangu je nalipa kodi kiasi gani`
> → **"Kodi ya mauzo ya ardhi na majengo ni asilimia 2% ya thamani ya soko."**

Both are fabricated rates on a capital-gains topic the OOC list exists to intercept, and the
**only** thing standing between them and the refusal was one letter. Both now refuse correctly.
This is the SAFETY-1 leak class reopening through orthography, and it means an OOC list is only
as strong as its weakest spelling.

| probe | before | after |
|---|---|---|
| `cfg_01/02` config-only phrases (`uza arzi`, not in the hardcoded fallback) | fabricated rates | **correct refusal** — proves the container read the CONFIG, not the baked list |
| `chg_02` employer share on TZS 500,000 | *"asilimia 20 … TZS 100,000"* (the TOTAL, ignoring "kama mwajiri") | **TZS 50,000**, correct |
| `neg_01` in-scope question containing `arzi` | in scope | in scope — no over-breadth |
| `neg_02/03` BRELA 22,000 / SDL 3.5% controls | correct | byte-identical |

⚠️ **`chg_01` — the verbatim user question — is a PARTIAL, and it is recorded as one.** The
dangerous output is gone: `TZS 400,000` and `TZS 20,000` no longer appear, so the contradiction
of the user's own figure is closed. But the reply now states the **rate** without applying it —
*"Kama mwajiri, unachangia asilimia 10 ya mshahara"* — and never reaches TZS 80,000. The reason
is the still-open `shingapi` gap: the levy and party now resolve, but with no money-ask the route
answers as a rate statement rather than a computation. **Right rate, no arithmetic.** The
`shingapi` fix completes this one; the variant fix alone was never going to.

This is also the first time the 400,000/20,000 reply was captured to disk on both sides of a
change — the gap flagged on 2026-08-14 (samples 1–3 died with the scrollback) is closed for this
defect.

## 🔢 THE DECIMAL SEPARATOR FIX — `milioni 5,5` was 55,000,000 (`ce677fa`, 2026-08-14)

**P2's first landed item.** Swahili writing uses both separator conventions and the parser used
neither — it stripped separators and concatenated:

| written | parsed before | direction |
|---|---|---|
| `milioni 5,5` | **55,000,000** | **10× OVERSTATEMENT** — every levy derived from it demands ten times what is owed |
| `milioni 1.2` | **1,000,000** | truncated — the dot was not in the character class at all |

Both forms are live in the corpus (`nat_09`, `nat_23`). The rule: a thousands group is always
exactly three digits, so a one- or two-digit tail is unambiguously a decimal mark. A three-digit
tail is a genuine collision — `milioni 1,500` is 1.5M or 1,500M, **a factor of a thousand** — and
is **declined and surfaced to the user**, not guessed. The decline guard sits above the
compute/fact fork because the ambiguity belongs to the question, not the route.

Measured: 6,194 corpus questions, **only nat_09 and nat_23 change**; 4 declining rows, all inside
the probe file; 24-row route blast radius unchanged; 65 tests in the file, 948 in the suite.

### Two things the approved spec did not determine, and the measurement found both

The fix was specified precisely and was still under-determined in two places. Both were caught by
running the instruments rather than by reading the diff:

1. **`%`-and-`asilimia` neighbours are not enough.** `Kiwango cha mchango wa NSSF ni asilimia
   3.5, au ni 0.5?` (`eval_337`, a real corpus row) writes `asilimia` **once** and lets it govern
   **both** figures. The specified neighbour test drops 3.5 and **keeps 0.5** — the one row of
   the 24 it cannot hold, leaving a rate in the amount list. Closed by requiring the previous
   figure to have been dropped as a rate with nothing but `au`/`ama` between them, **not** by
   widening the backward search for `asilimia`, which would swallow the turnover in `asilimia 18
   ya mauzo ya TZS 1,500,000`. `ds_28` is the negative that pins it.

2. **The obvious end-to-end test would have passed while proving nothing.** The proposed check —
   *"the question with the rate must compute 175,000"* — omits the headcount, and **SDL needs the
   headcount independently**, so both the with-rate and without-rate forms clarify and the test
   goes green on a fix that does not work. The probes and the test carry `wafanyakazi 12`.

Same shape as the STANDING LIMITATION and as R17: **an instrument that cannot fail is not
evidence**, whether it is a regex gate crediting a wrong answer, a sweep over a corpus lacking
the vocabulary, or a test whose control and treatment collapse to the same branch.

### Pattern worth keeping: when you defer a change, pin the rows it will alter

Full percent exclusion — dropping **integer** rates (`asilimia 18`, `2%`) from the amount list
too — is a real defect of the same family and probably a net improvement. It is **measured at 250
rows changed, 89 of them ceasing to be multi-figure**, which is far too large to ride along on
this commit. Deferred as its own item with its own sweep and canaries.

`ds_25`/`ds_26` pin the rows that pass will change, with `guards_against` text saying so
explicitly. **Generalise this:** a deferred change should leave behind probes asserting today's
behaviour on the rows it will alter, so the future pass has to change them **visibly, with its
own sweep**, rather than quietly. A deferral recorded only in prose is a deferral that gets
re-derived from scratch or silently absorbed into an unrelated diff.

## 🧮 THE BOARD — everything logged and unfixed, 2026-08-11 (supersedes the 2026-08-10 queue)

**Taking stock before choosing, at founder request.** Ordered by severity class first, then by
cost within a class. Tier A is the only tier where a user acts on a false statement.

### TIER A — LIVE AND WRONG IN PRODUCTION TODAY

| # | item | what a user gets | age | fix cost |
|---|---|---|---|---|
| **A1** | **SAFETY-2 / D-RESIDENCY-1** — `paye_resident` does not read *"hana residence permit ya kudumu"* | non-resident taxed on resident bands: **TZS 1,028,000 instead of TZS 600,000**, rendered as the *deterministic working* | tracked **2026-08-06**, never implemented | medium — cue extension + R17 sweep; the entry warns a false *non-resident* detection is symmetrically dangerous |
| **A2** | **Phantom TZS 26,000 relief** — parametric, 7 shapes | PAYE understated by TZS 26,000, or a correct answer "corrected" to add it | 2026-08-10, 6 live sightings / 2,314 | **low for 6 of 7** (union pattern already measured, 0 FPs); the 7th is outside the mechanism |
| **A3** | **Invented effective dates** (new today) | *"kima cha chini … kuanzia Julai 2026"* — GN 605A is **1 Jan 2026**; 3 fabricated dates across 3 domains | 2026-08-11 | unpriced — **no guard in this repo can see a date at all** |
| **A4** | **Paraphrase family** of the intermediate-figure hole | a wrong final figure with no arithmetic written out, printed directly above the deterministic working | 2026-08-11, named open by D-FIDELITY-3 | high as a guard — priced and deferred to the adapter |
| **A5** | **No unit normalisation** (th_08) | *"you cross TZS 100M in 5.5 months"* → concludes **below** the threshold | 2026-08-10, VAT/EFD Phase 3 | medium — an extraction problem, deliberately not folded into the threshold route |
| **A6** | **Wrong-source answers** — `nc_jengo` | a business-licence question answered by citing **GN 605A** and referred to **immigration.go.tz** | 2026-08-11 | unpriced — retrieval/routing, 1 sighting |

### TIER B — DEGRADES CORRECT ANSWERS (content lost, nothing false asserted)

| # | item | effect | cost |
|---|---|---|---|
| **B1** | **D-FIDELITY-1 blanks two correct bodies** — its own-levy rule never consults `_acceptable` | correct explanations deleted; user sees the bare working | medium — changes verdicts corpus-wide, needs its own sweep |
| **B2** | **Multi-figure extraction corruption** (new today) | the general case behind th_19/th_20: extraction selects among figures belonging to two asks. Fixed for `na je`; **the `?`-split path still drops the preamble** (the documented Q6 limitation) — same class, still open | medium |
| **B3** | **Swahili-numeral slot extraction** (*"kumi na wawili"*, *"laki tatu na nusu"*) | compute path clarifies instead of answering; the engine's correct figure never reaches the user | medium |

### TIER C — MECHANISM AND MEASUREMENT DEBT

- **C1 Runtime `wrong_patterns` check** — the vehicle for A2. Measured: 6/6 on known shapes, 0 FPs over 2,314. **Ship it with its ceiling in its own docstring** (see the bound added to that entry).
- **C2 Judge overlay is mandatory** — the regex gate positively credits eval_318 and eval_320, the two worst defects of that cycle.
- **C3 D-FIDELITY-1 attribution follow-ups.**
- **C4 Reachability / R15** — the relief denial ranks #64 for the question that needs it; GN 605A had the same shape. Swahili-first, subject-keyed rewrites, batched into one RAG regen.
- **C5 Divergence risk** — decompose/prompting/cleanup duplicated across `modal_app.py` + `eval.py`; plus the standing CONTAINER-PATH-1 audit of repo-relative reads inside the image.
- **C6 Scored-number decisions** — eval_191 mislabel and the bank-loan OOC category. Both move the gate denominator or the product's scope; **decide outside a measurement cycle**, together.

### TIER D — THE NEXT ADAPTER VERSION

**D1** — the only real closure for A2 and A4. The evidence is assembled: the relief is parametric
(an on-point rank-1 fact loses to it), the seventh shape shows the **concept** survives the
number being denied, and cue-based narrowing relocates rather than removes. Guards catch shapes;
the model supplies them.

### What I would take next, and why

### ADDED 2026-08-14 — pilot-blocking, and they outrank the severity queue above

The board above orders by *defect severity*. The pilot-readiness assessment asked a different
question — **what stands between us and learning from real users** — and it gives a different
answer, because a defect you cannot observe is worse than a defect you can. Founder decision:
these two run first.

| # | item | why it outranks A1 |
|---|---|---|
| **P1** | **The handler could drop a user's answer in silence** — `call_modal` unguarded inside a fire-and-forget task; no transcript store | **DONE 2026-08-14** (entry below). Until this landed, a pilot could not distinguish a wrong answer from a missing one, which makes every other measurement unreadable |
| **P2** | **Compute-path wrong-number cluster** — 8 of the 13 compute failures in the 48-probe rerun: SAFETY-2 (A1), SDL-at-0.5% / WCF-at-10% (nat_01/04/19), PAYE band arithmetic (nat_13/14), NSSF employee share (nat_08/09) | investigated as ONE class rather than four items, because the assessment's read is that they share a shape — extraction and cue resolution, not the engine. A1 is a member of it, not a rival to it |

- **C7 Network tests inside the unit suite** — `test_orchestrator.py::*_on_real_weights` (4 tests)
  call the **live Modal endpoint**. Three of them failed under a full-suite run on 2026-08-14 and
  **all four passed in isolation** 90 seconds later; the most likely cause is a cold start
  colliding with the suite, i.e. a failure with no relation to the code under test.
  **This is a measurement hazard in the instrument we rely on most.** A suite that can fail for
  reasons unrelated to the code trains everyone to discount its failures — and the moment
  red-means-maybe, the suite has stopped being evidence. Mark them (`@pytest.mark.live`,
  deselected by default) or move them to a separate live-check file. Not yet done.

### What I would take next, and why

**C1 → A1 → A3.** C1 first because it is the only item where the measurement is already done and
the cost is an afternoon — it removes six live wrong-answer shapes at zero measured false
positives, and A2 is otherwise unaddressed until D1. Then A1, because it is the oldest live wrong
*number*, it is engine-authoritative (the worst presentation this system can produce), and its
fix shape is known and bounded. Then A3, starting with measurement rather than a guard: how often
does production state a compliance date at all, and how many are wrong? A6 and B2 are single
sightings and should not outrank measured classes. **This is a recommendation, not a decision.**

---

## 🔑 CREDENTIAL FINGERPRINTING IS PERMANENT INFRASTRUCTURE — not a debugging aid (2026-08-14)

**Root cause of the three-day WhatsApp delivery outage: the Modal secret never held the
working token.** Stored value 66 characters, fingerprint `314e083b`; the token that returns
`{"sent":true}` is 64 characters, fingerprint `9665c495`. Two extra characters — almost
certainly wrapping quotes carried in on a copy.

**What it cost, all of it spent on a value nobody could see:** three failed sends, two token
rotations, a full WhatsApp session re-pair, and a vendor nearly blamed for a fault that was
ours. Every remedy was aimed at the far end because **no instrument existed that could compare
a secret against a known-good value.**

The first hypothesis on the very first 401 was *"the token is stale or mis-pasted"*. It was
correct. It was abandoned because `/api/me` — independently broken — supplied a plausible
rival explanation, and nothing could adjudicate between them. **A broken diagnostic does not
merely fail to help; it redirects the investigation.** (Instrument-lie #9, now corrected there
to record `/api/me` as an aggravating factor rather than the cause.)

⚠️ **THE RULE — any credential that can fail silently needs a fingerprint exposed somewhere
comparable, and the comparison must be RUN before concluding anything about the far end.**

The implementation is four lines and belongs beside every secret this project uses:
```python
sha256(value.encode()).hexdigest()[:8]   # comparable, not reversible
len(value)                               # catches truncation and wrapping characters
value != value.strip()                   # catches a trailing newline on paste
```
Truncated SHA-256 is safe to publish and safe to paste into a support ticket. **Neither party
ever prints the secret**, which is what made this checkable at all — the founder hashed their
working token locally and compared eight hex characters.

Live at `GET /health` on `chike-whatsapp` as `wappfly_token_fingerprint` / `_len` /
`_has_whitespace`. **`MODAL_API_TOKEN`, `HF_TOKEN`, `WEBHOOK_TOKEN` and `ADMIN_TOKEN` have no
equivalent yet** — each can fail the same silent way, and each would produce the same
multi-day misdirection. Extending the pattern to them is open work.

Generalises the R16 family. R16 says a deploy is not verification without a live check;
this says **a credential is not verified by being present.** `/health` reported
`WAPPFLY_TOKEN: true` throughout — presence-by-name answered the question it was built for
(is the key spelled right?) and was silent on the one that mattered.

---

## ✅ A1 SHIPPED AND LIVE-VERIFIED — two rows fixed including a 20× error, and the canary tried to revert it (2026-08-14)

Deployed `b4a6537` to `chike-inference` under the full R16 cycle (`app stop --yes`,
`PYTHONIOENCODING=utf-8`, before/after canary, negatives).
Artifact: `eval/results/a1_ngapi_live_check.json`. **VERDICT: VERIFIED.**

| row | before | after |
|---|---|---|
| **nat_01** | *"asilimia **0.5%**"*, no amount at all | `SDL = 3.5% × TZS 6,000,000 = TZS 210,000` + working — **FIXED** |
| **nat_19** | *"unachangia shilingi **300,000**"* (10%) | `WCF = 0.5% × TZS 3,000,000 = TZS 15,000` — **FIXED, a 20× error** |
| **edge_p05** | generic 0.5%, no amount | **clarifies** (per-employee vs total + headcount). **Did NOT touch the 20,000,000 distractor.** Unfixed but safe — the asymmetry principle behaving exactly as stated |
| **edge_p10** | prose-only 800,000, no working | working present, employer share split, **SDL trap avoided** at 5 staff. Fan-out still open |
| **nat_23** | *"PAYE = TZS 5,500,000"* — a fabricated tax equal to the whole payroll | `NSSF = 20% × TZS **5,000,000**` — see the decimal entry below |

**All five negative controls byte-identical; CONTAINER-PATH clear.**

**nat_23 is not a clean win and should not be recorded as one.** It moved from an *absurd*
wrong figure to a *plausible* one carrying the engine's working — and by this project's own
standard, an engine-authoritative wrong number is the worst presentation the system can
produce. The absolute error shrank; the credibility of the error grew. Kept because the cause
is upstream and independently fixable (next entry), but the shape is worth remembering: **a fix
that routes a question to the engine inherits every defect between the question and the engine.**

---

## 🔢 DECIMAL MILLIONS ARE PARSED WRONG IN BOTH CONVENTIONS — and one of them is 10× HIGH (2026-08-14)

Found by the A1 canary, **pre-existing in `chike/swahili_numbers.py`**, independent of A1:

```
milioni 5.5  -> 5,000,000      decimal TRUNCATED   (understates by 9%)
milioni 1.2  -> 1,000,000      decimal TRUNCATED
milioni 5,5  -> 55,000,000     comma read as a THOUSANDS SEPARATOR (overstates 10×)
```

**The comma form is the priority half.** Truncation understates by single-digit percentages;
comma-as-separator overstates by an order of magnitude, and **comma decimals are common in
Swahili writing** — so the more natural phrasing produces the larger error.

**Ambiguity must clarify, not guess.** `milioni 1,500` cannot be resolved by rule: it is either
1.5 million (comma decimal) or 1,500 million (comma separator), and those differ by 1000×. Where
the convention cannot be determined from the text, decline — a clarification costs the user a
turn, a guess costs them an order of magnitude.

**Sequenced ahead of B (SAFETY-2) at founder decision, and the argument is nat_09:** *"mshahara
ni milioni 1.2"* is in the A2 batch and will truncate to 1,000,000 **the moment its levy cue
lands**. Fixing the parser first means B and A2 ship onto a sound base instead of compounding
onto a known parser bug.

---

## 🪞 INSTRUMENT-LIE #10 — A CANARY WHOSE PASS CONDITION DID NOT MATCH THE AGREED REVERT TRIGGER (2026-08-14)

**The A1 canary printed `NOT VERIFIED — REVERT` on a change that was correct.** Acting on that
flag would have reverted a fix that had just corrected a **20× error** (nat_19: WCF 300,000 →
15,000).

The agreed revert trigger, in the founder's words, was: *"if extraction takes the 20,000,000
distractor it's a new wrong number in the dangerous direction — reported as a failure and
reverted."* **The trigger was about a WRONG NUMBER.** The pass condition I wrote was
`'10,000' in reply` — i.e. *did edge_p05 ANSWER*. Those are different outcomes, and the
instrument silently substituted the second for the first. edge_p05 clarified: it produced no
figure at all, took nothing from the distractor, and `forbidden_present` was empty the whole time.

**This is the first instrument in the catalogue that was wrong about a DECISION rather than
about a measurement.** The measurement was fine — every string it captured was accurate. The
verdict it derived pointed the opposite way from the evidence it had already collected.

⚠️ **THE RULE: a canary's pass condition must be written from the decision it feeds, and stated
in the same terms the decision was agreed in.** If the agreement says "revert on a wrong
number", the condition tests for a wrong number — not for a right one. The two are not
complements: between them sits *clarification*, which is the safe outcome this whole path is
designed to produce, and which the negation quietly reclassifies as failure.

Caught the same way #8 was: **reading the replies instead of the flags.** The corrected
condition and the original mistake both live in `scratch/a1_live_canary.py`; the verdict was
re-derived from the stored artifacts without re-asking.

---

## 🧭 THE "COMPUTE-PATH WRONG-NUMBER CLUSTER" IS MISNAMED — six of eight never reach the compute path, and zero are engine arithmetic failures (2026-08-14)

**RENAME IT. The queue called this the compute-path wrong-number cluster. These questions never
reach the compute path.** Anyone who goes looking for a bug in the rules engine on the strength
of that name will find nothing, because there is nothing there: **the engine's arithmetic is not
wrong in a single one of the eight rows.** The correct name is the **routing-and-cue-resolution
cluster**.

Two independent signals agree exactly, with no disagreement on any row:
- **Reply shape** — six of the eight replies carry NO appended deterministic working. That
  absence is the observable signature of the engine never having run.
- **Offline routing** — `routing.detect_intent` on the verbatim questions returns `none` for
  exactly those six (`scratch/p2_route_diag.py`, no GPU, no network).

```
NEVER REACHED COMPUTE : nat_01, nat_04, nat_09, nat_13, nat_14, nat_19
REACHED, WRONG LEVY   : (none)
ROUTED CORRECTLY      : nat_08, nat_16
```

**Three classes, four root causes:**

| class | rows | root cause |
|---|---|---|
| **A1** money-ask cue gap | nat_01, nat_19 (+half of nat_09) | `_MONEY_ASK` carried `ngapi` only in the fixed phrase `"ni ngapi"`; an inflected verb before it matched nothing |
| **A2** levy cue gap | nat_09, nat_13, nat_14 | `_natural_levy` returns None for *mfuko*, *serikali inachukua*, *kupeleka kwa TRA* |
| **A3** applicability + payroll-context gap | nat_04 | `watu` is not in `_PAYROLL_CTX`; *"inanianza lini"* is not an applicability cue. Both gates fail |
| **B** wrong engine input | nat_16 | every `_PAYE_NONRESIDENT_CUES` entry is built on *mkazi*; the question says *"hana residence permit ya kudumu"* — English |
| **C** right levy, wrong party | nat_08 | `nssf_party` employee cues are third-person; the question is first-person-object (*"wana**ni**kata … mshahara **wangu**"*). Engine correctly computes the TOTAL; the employee share was asked. **Exact twin of the employer-side gap PREREQ-2 already closed** |

### ⚖️ STANDING PRINCIPLE — for compute-cue widening, the safe direction is WIDER

**Under-routing and over-routing are not symmetric, and the asymmetry should govern every cue
decision on this path:**
- **Under-routing** hands the question to the model, which free-computes and returns a confident
  wrong figure with no working. All six Class A rows are this.
- **Over-routing** hands it to the engine, which **clarifies rather than guesses** (never-guess /
  R8 — demonstrated live by nat_21, which was offered a TZS 30,000,000 vehicle value as a WCF
  base and asked for the payroll instead). It costs the user a turn.

And the engine is the better half of the system — **91.6% on the compute path against 76.2% on
fact** — so every question moved from fact to compute is moving to the stronger path.

**QUALIFIER, and it is not decorative: safe-direction is an argument about the TYPICAL case, not
a licence to skip the sweep.** A specific over-broad cue can still produce a wrong number rather
than a clarification — see `edge_p05` in the A1 entry, where a widened route reaches a question
carrying an asset distractor, and the failure mode would be a *new* wrong figure, not a
clarification. Widen confidently; sweep anyway; author the probes the corpus cannot supply.

---

## 🔀 NATURALLY-NAMED LEVIES CANNOT FAN OUT — `all_explicit_levies` has no natural-cue twin (2026-08-14)

D-DECOMP-1 fixed multi-levy compute parts by having the orchestrator fan out over
`routing.all_explicit_levies`, which enumerates every **explicitly named** levy token (SDL, NSSF,
PAYE, WCF) so a question naming two is computed twice rather than once. **There is no equivalent
for naturally-named levies.** `_natural_levy` returns the FIRST cue that matches and stops, so
*"ile ya mafunzo na ile ya uzeeni"* resolves to `nssf` alone and SDL is silently dropped.

**Distinct from A2**, which is about levies that resolve to *nothing*; this is about levies that
resolve to *one of several*. A2's fix adds cues; this one needs an `all_natural_levies` and an
orchestrator path that consumes it.

Caps two rows found by the A1 sweep:
- **nat_23** — *"ile ya mafunzo na ile ya uzeeni"*, 12 staff, TZS 5,500,000. Probe demands both:
  SDL 192,500 and NSSF 1,100,000. **Its live answer today is `"Kwa wafanyakazi 12, PAYE = TZS
  5,500,000"` — a fabricated tax equal to the ENTIRE PAYROLL.** One correct levy is a large
  improvement on that even while the fan-out stays open, and that comparison is the reason A1
  ships without waiting for this.
- **edge_p10** — same shape, plus an SDL applicability trap (5 staff, so SDL should not apply).

---

## 💳 THE PILOT'S CAPACITY IS ~15 SESSIONS/DAY, AND THAT IS THE REAL ARGUMENT FOR HOLDING GPU SCALEDOWN AT 300 (2026-08-14)

Priced from Modal's published rates, fetched 2026-08-14: **T4 $0.000164/s**, CPU
$0.0000131/core/s (min 0.125 cores), memory $0.00000222/GiB/s, Volumes $0.09/GiB/mo with
**1 TiB/mo free**, Starter plan **$0 base with $30/month of credits**.

**$30 ÷ $0.000164 = 182,927 GPU-seconds ≈ 50.8 T4-hours/month.**

One user session ≈ **65s cold start + ~30s of answers + the 300s scaledown tail ≈ 395
GPU-seconds.** So the credit covers **≈463 sessions/month ≈ 15 sessions/day.**

**This is the pilot's binding constraint, and it is a headcount, not a bill.** Fifteen
testers having one conversation a day each consumes essentially the entire monthly credit.
Recruit twenty and this becomes a real invoice; recruit fifty and it is a meaningful one.
Whatever the pilot's size, it should be chosen against this number rather than discovered
through it.

**It is also a better argument for holding `scaledown_window` at 300 than anything said
before.** The earlier framing was "warmth buys polish, not correctness" — true, but soft.
The hard version: the scaledown tail is **300 of the 395 seconds in a session — 76% of the
GPU cost of a conversation is idle time after the user has stopped talking.** Raising it to
600 drops what the credit covers from ~15 sessions/day to **~8.8**. It would nearly halve
the pilot before a single answer improved.

Corollary for the handler: at these rates the CPU webhook is **~$0.10/mo** at
`min_containers=0` versus **$5.68/mo** always-warm. Both are noise against the GPU, which is
why the handler-hosting decision was correctly made on architecture rather than cost.

*(The dollar figures are arithmetic on Modal's published rates; the GPU-seconds per session
are measured. Sessions/day assumes one conversation per tester per day — a guess, and the
first thing the transcript store will replace with a fact.)*

---

## 🗑️ MODAL'S STARTER PLAN DELETES LOGS AFTER 1 DAY — the transcript store is a pilot PREREQUISITE, not an improvement (2026-08-14)

Confirmed from Modal's pricing page, 2026-08-14: Starter plan log retention is **1 day**.

The readiness assessment described the pre-existing position as *"Q&A exists only in Modal
stdout … a pilot has nothing to review."* **That understated it.** The problem was never that
stdout is unqueryable — it is that **yesterday's conversations are deleted.** A founder
reviewing transcripts on Monday morning cannot see Friday, Saturday or Sunday. The daily
hand-review that the pilot guardrails depend on would have been reviewing a 24-hour window
and silently losing everything older, including the evidence for any user who reports a bad
answer more than a day after receiving it.

**This reclassifies the transcript store.** It was scoped as "a pilot with no transcript store
is unmonitorable" — an argument about convenience and rigour. The correct statement is
stronger: **without a durable store, the pilot's primary evidence has a 24-hour half-life by
platform default**, and no amount of discipline compensates, because the data is gone before
anyone can be disciplined about it.

Two consequences already acted on:
- The volume-backed store ships **with** the Modal move rather than after it (below).
- Storage cost is not a reason to defer: Modal includes **1 TiB/mo free**, so a lifetime of
  Swahili text transcripts costs **$0**.

Same family as R16's "NO CONSOLE OPERATION MAY STAND BETWEEN A MEASUREMENT AND ITS FILE" and
the 2026-08-11 `Select-Object` incident: **the measurement that quietly ceases to exist is
the expensive one.** This is that failure mode with a 24-hour fuse and a platform default
instead of a pipe.

---

## 📴 THE HANDLER COULD DROP A USER'S ANSWER IN SILENCE — and a pilot cannot read any other measurement until it stops (2026-08-14)

**The defect.** `wappfly-function/handler.py:65` — `call_modal` had no exception handling and
ran inside a fire-and-forget `asyncio.create_task`. On a timeout or any transport error the
exception was **swallowed by the event loop** and the user received *nothing* — not even the
`FALLBACK` string defined three lines above it, which only ever fired when Modal returned a
200 whose JSON lacked a `reply` key. The webhook had already returned 200, so Wappfly never
retried. Cold starts were measured at 64s (2026-08-11), 92.5s (2026-08-06) and up to 216s
(runbook) against a **180s** ceiling, so this was not hypothetical: a cold start plus a compute
question crossed it, and every crossing was a silently dropped answer.

**Why this outranked every wrong-answer item on the board.** A defect you can see is a bug;
a defect you cannot see is a blind instrument. With no transcript store — Q&A existed only in
Modal stdout — a pilot could not tell a **wrong answer** from a **missing one**. Every daily
transcript review, every "what would make you pull it" trigger, and every claim about real-user
accuracy depends on the record existing first. This is the same principle as R16's
"NO CONSOLE OPERATION MAY STAND BETWEEN A MEASUREMENT AND ITS FILE", applied to production
rather than to a canary script: **the silent, exit-0 failure is the expensive one.**

**Three invariants now hold, each proven by forcing the failure** (`tests/test_wappfly_handler.py`,
22 tests — real stub HTTP servers, real httpx calls, assertions on what was *delivered to the
user* and what *landed in the file*, never on the code's shape):

1. **Nothing escapes the background task.** `call_modal` returns
   `(reply | None, error_class, detail)` and cannot raise; `respond()` carries a belt-and-braces
   `except` so even a bug in the handler itself still sends FALLBACK.
2. **Failure causes are distinguishable:** `timeout` / `transport` / `http_status` / `bad_json` /
   `no_reply_field` / `handler_bug`. These need different repairs — raise the ceiling, check
   Railway egress, fix the token — and previously produced *identical silence*.
   `httpx.TimeoutException` **subclasses** `TransportError`, so the catch order is load-bearing
   and a test pins it.
3. **Every message is recorded** — one JSONL row to `$TRANSCRIPT_DIR/chike-YYYY-MM.jsonl`
   **and** to stdout, so a missing volume degrades the record rather than losing it.

Forced in the tests: Modal sleeping past the timeout; a dead port; 401; 500; a junk body; a
missing `reply`; a whitespace-only `reply`; an exception thrown inside the handler; a Wappfly
send returning 500; an unwritable transcript directory.

**`cold_start_suspected` is a proxy and its name has to keep saying so.** The handler cannot
observe container age — Modal's response body carries no such field — so the flag is a latency
threshold (30s; warm p90 was 9.8s over 48 questions). A test asserts the field is never renamed
to `cold_start`. This is the same discipline as naming a judgement a judgement.

**Three judgement calls, all confirmed by the founder:**
- **Secrets are scrubbed from `error_detail`** — httpx puts the request URL, token query param
  included, into some transport error strings, and transcripts get read and pasted around.
  Non-negotiable here: this project has leaked that token twice.
- **Senders are pseudonymous** — salted SHA-256 (12 hex) + last four digits. Enough to follow
  one conversation and identify a pilot user you already know; not a raw phone-number dump.
- **A slow-path ack** (one short "nimepokea swali lako, subiri kidogo" after 12s). Scope creep,
  deliberately accepted: a user who hears nothing for three minutes concludes the service is
  broken, and **one Wappfly message beats ~$200/month of warm GPU.** `SLOW_ACK_AFTER_S=0` disables.

**The numbers, and why only one of them moved.**

| knob | decision | reasoning |
|---|---|---|
| `MODAL_TIMEOUT_S` | **180 → 240** | costs **$0**. Modal's own function timeout is 600s, so nothing upstream cuts us off. A user waiting 4 minutes on WhatsApp is strictly better than a user getting nothing |
| `scaledown_window` | **hold at 300** | 600s ≈ +$44/mo, 900s ≈ +$88/mo, business-hours warm ≈ $212/mo, `min_containers=1` ≈ $425/mo (assumed T4 rate $0.59/hr — *the GPU-seconds are measured, the dollars are arithmetic on that assumption*). With the 240s ceiling and the ack, **a cold start becomes slow-but-answered rather than nothing — so warmth now buys polish, not correctness** |

The second row is the useful one: `cold_start_suspected` in the transcript **turns this into a
measurement in two weeks of real traffic instead of a guess today.** `chike-inference/modal_app.py`
was not touched.

### …AND THE PLATFORM CHANGED UNDER IT THE SAME DAY — Railway → Modal

Railway's trial ended before this shipped. Fly.io was assessed as the alternative and
rejected on re-pricing: **Fly's free tier is gone** (2h/7d trial, then ~$2.17/mo for
`shared-cpu-1x` 256MB + a 1GB volume), so the choice was a second paid bill versus half a
day of porting. **Cost turned out to be noise on both sides** — the spread across every
option considered was $0.10 to $5.68/month — which correctly removed money from the
argument and left architecture and operational burden.

**Modal won on three things, none of them financial:**
1. **`.spawn()` makes the answer path DURABLE rather than best-effort.** Modal owns the job
   and it survives the webhook container's death. Fly's `asyncio.create_task` in a
   persistent VM is exactly as good as the Railway code and no better.
2. **Two error classes stop being possible** rather than being handled — no network hop and
   no token gate between handler and model, so `transport` and `http_status` are gone.
3. **One platform, one bill, one place secrets live.**

**The split that made the port cheap:** `handler_core.py` holds all conversation logic with
`ask` and `send` injected, and `modal_whatsapp.py` is a thin wrapper. The platform changed;
`deliver()` did not — and the tests, being written against the injected seam, went from 22
to 34 and from 41s to 8s.

**Three Modal-specific rules, now in CLAUDE.md, each of which fails SILENTLY if ignored:**
- **Separate app (`chike-whatsapp`).** R16 requires `modal app stop chike-inference --yes`
  before a model redeploy; a shared app would take the WhatsApp front door down with every
  model deploy — and on 2026-08-10 that window was ~2 minutes of dead production when the
  replacing deploy failed.
- **`.spawn()`, never `asyncio.create_task`.** Modal's autoscaler tracks in-flight inputs;
  once `webhook` returns its 200, a detached coroutine holding a 240s answer is invisible to
  the scheduler and can be reclaimed. It would work *most of the time* — the exact class of
  failure this handler was rewritten to abolish.
- **One file per transcript row.** Modal Volumes are not a POSIX shared filesystem: two
  containers appending to one JSONL do not interleave, the last committer wins, and the
  other user's row is gone — data loss at precisely the moment of interest.

`retries=0` on the spawned jobs is deliberate: a retry re-runs the GPU call and could deliver
a **second answer to the same question**. A duplicate compliance answer is worse than one
missing answer, and the transcript records the failure either way.

**A defect the port's own test found on its first run.** `extract_reply` sat inside the try
that classifies *model* failures, so a bug in our own parsing came back as
`error_class: model_error` — **an error class lying about who failed**, which would have sent
someone debugging `chike-inference` for a fault in the handler. The parse moved outside that
try and a test forces it. Same family as the instrument-lie catalogue: the taxonomy that
misattributes is worse than no taxonomy.

**R16b INVERTS.** The note written earlier the same day — "the commit IS the deploy for this
service" — was true of Railway and is now false. The handler is on Modal, so it needs
`modal app stop chike-whatsapp --yes`, `PYTHONIOENCODING=utf-8`, a live forced-failure check
and a negative case, on **every** handler change. `/health` returns `build`, but Modal injects
no commit SHA, so the deploy command must pass `CHIKE_BUILD=$(git rev-parse --short HEAD)` —
one more manual step than Railway, and one more thing to forget.

**Founder-side steps (no CLI access from here):** the `chike-whatsapp` Modal Secret
(`WAPPFLY_TOKEN`, `WEBHOOK_TOKEN`, `ADMIN_TOKEN`, `SENDER_SALT`), pointing Wappfly at the new
webhook URL, and the production forced-failure check (`MODEL_TIMEOUT_S=1` → redeploy → send
one message → confirm FALLBACK + a `timeout` row → revert → confirm a normal answer).

**`wappfly-function/` is left untouched, in its pre-rewrite committed state.** The Railway
platform is dead, so it is not a live rollback path, but deleting it is a separate decision
and not one to fold into a move. Delete it once `chike-whatsapp` is verified live.

**The webhook is currently OPEN unless `WEBHOOK_TOKEN` is set** — the same as the Railway
handler always was, so not a regression, but on Modal the URL is guessable from the account
name. Unset preserves day-one continuity and logs a warning; set it.

**Still open on this path, deliberately not folded in:** no dedupe on webhook redelivery, no
rate limit, no conversation memory, and Modal still serves **one input per container** with no
`max_containers` cap — so concurrent users each pay a cold start. All three are 100-user
problems, not 15-user problems.

---

## ✂️ DECOMPOSITION DROPPED HALF OF A QUESTION BECAUSE ITS TWO CONNECTOR LISTS DISAGREED (2026-08-11)

**Built, committed, DEPLOYED, live-verified.** Two parts: the `na je` split, and the
measure-matched preamble carry — which is the load-bearing half, because splitting alone trades
one silent failure for another.

### 🔴 READ THIS FIRST — it is a WRONG-ANSWER defect that had been classified as a missing-answer one

The item was opened as *"decomposition silently drops a sub-question"*. That is true and it is
the smaller half. **An unsplit multi-part message also corrupts the half it does answer**,
because slot extraction runs over the whole message and selects among figures belonging to two
different questions:

| | asked | production served |
|---|---|---|
| `th_19` | payroll **TZS 6,000,000**, 12 staff | *"SDL = 3.5% × **TZS 500,000** = TZS 17,500"* — a figure that is in neither ask |
| `th_20` | payroll **TZS 9,000,000**, 15 staff | *"NSSF = 20% × **TZS 750,000** = TZS 150,000"* |

Correct answers are TZS 210,000 and TZS 1,800,000; production was out by a factor of twelve on
both, **stated with the deterministic working underneath it and no hedge**. A dropped ask is a
user who notices they got half an answer. A wrong figure is a user who acts on it — this is the
same severity class as th_16 and the phantom relief, not a completeness nit.

> **The reclassification came from the LIVE CHECK, not the sweep.** The offline sweep measured
> exactly what it was built to measure — how many parts a message decomposes into — and by that
> instrument th_19 was one row of thirty-one, indistinguishable from the twenty-four false
> positives. Nothing in the parts count says the answered half is wrong; the corruption is two
> stages downstream, in extraction. It became visible only when the replies were read.
> MEASUREMENT-GAP-1 in a third domain: **the structural instrument asserts the checkpoint before
> the stage that actually harms the user.** Cost of finding it: nine live questions.

### The defect: one list decides, a different list acts

`MULTI_PART_SIGNALS` (which DECIDES a message is multi-part) has **ten** entries.
`_SPLIT_PATTERN` (which actually SPLITS one) has **five**. Six connectors therefore detect and
never split, and a message whose only connector is one of them is recognised as multi-part, sent
down the connector path, matched by nothing, and returned **whole** by the `len(parts) == 1`
fallback. It then gets one whole-message top-3 retrieval, which covers one domain, and the model
answers one half.

Nothing anywhere records that a question went unanswered. The regex scorer credits the half that
was answered. This is the same invisibility class as D-FIDELITY-1's blanked bodies.

Live, before the change — three questions, three half-answers:

| id | asked | production answered | dropped |
|---|---|---|---|
| `th_19` | SDL amount **+** EFD applicability | *"SDL = 3.5% × TZS 500,000 = TZS 17,500"* | EFD, entirely |
| `th_20` | NSSF amount **+** VAT registration | *"NSSF = 20% × TZS 750,000 = TZS 150,000…"* | VAT, entirely |
| `th_24` | VAT registration **+** EFD | *"Ndiyo, unatakiwa kuwa na mashine ya EFD…"* | VAT, entirely |

All three carry `na je`. `scratch/naje_live_before.json`.

### The bound — decomposition is less load-bearing than it looked, and that is the useful finding

The sweep flagged 31 multi-domain messages returned whole. **24 of the 31 are false positives of
my own domain-pair heuristic** — *"risiti ya EFD kwa biashara iliyosajiliwa VAT"* names two
domains and asks one question. Structure cannot settle it, so the 7 survivors were asked live,
and **four of them (eval_319/320/323/327) answer BOTH asks despite never being split**: the rules
engine enumerates the payroll levies (PAYE/SDL/NSSF/WCF) independently of decomposition.

> **The drop happens only when the two asks are in DIFFERENT routes** — one compute, one
> threshold/registration — because that is the only case where decomposition is the mechanism
> that had to separate them. Same-family payroll asks are covered downstream whatever
> decomposition does.

That bounds the fix and it bounds any future one: widening the connector list buys nothing for
the four rows, and the three it does buy are all cross-route. Worth knowing before anyone treats
decomposition as the general fix for multi-part questions.

### R17 first: 19 probes authored BEFORE the rule, in both directions

Four corpus questions carry `na je` and **all four want splitting** — so the corpus cannot show a
single false positive of a split rule, and cannot exercise the preamble rule's FP direction at
all. R17 has now been right five times running; the probes are
`eval/decomposition_gate/na_je_preamble_019.jsonl`, wired by `tests/test_decomposition_na_je.py`.
Every element of the shipped rule exists because one of them demanded it:

| probe | what it does to a naive rule |
|---|---|
| `naje_neg_01_jengo`, `naje_neg_02_jenereta` | **"na jengo" / "na jenereta" contain the literal "na je".** `_SPLIT_PATTERN` is applied with no word boundaries, so a bare alternative cuts a single question mid-word and hands the model *"ngo langu mwenyewe…"* |
| `naje_neg_04_short_tail` | *"…na je VAT?"* — the tail is 4 chars. The shipped paths **filter** short segments: they split the rest and the fragment is gone. On this path the floor is a **veto** — under-length means no split at all, never split-and-discard |
| `naje_neg_05_statement` | *"Nimesajili biashara BRELA mwezi uliopita na je nahitaji TIN?"* — the first half is context, not an ask. Splitting invents a sub-question and gives the user a BRELA paragraph they never asked for. Hence: every segment must carry an ask marker |
| `naje_neg_06_anaphora` | *"…na je hiyo inategemea mauzo?"* — the second half refers BACK to the first. Split out it retrieves on nothing. A connector between two asks is not the same token as a connector inside one |
| `naje_neg_03`, `naje_neg_07` | message-initial *"Na je,"* is a discourse particle; a bare *"Je"* opener is the commonest interrogative in the corpus |

### The preamble carry — matched on the MEASURE, not on the presence of a figure

Splitting th_24 yields *"nahitaji EFD?"* — self-contained by length, **stripped of the turnover
figure the EFD threshold is tested against**. `_split_enumeration` has carried its preamble since
v15 for exactly this reason; the connector path never has.

The obvious rule — *if a part has no figure and the preamble does, carry it* — is wrong in two
ways the corpus cannot show, and both authored probes fail it:

- **`pre_02`** *"Mshahara … TZS 800,000 — PAYE ni kiasi gani, na je kima cha chini … kilimo ni
  kiasi gani?"* A salary is a figure too. The minimum-wage route is **deterministic and
  adjudicates figures it is handed** (shipped 2026-08-10), so carrying it would manufacture a
  *halali / si halali* verdict about a wage nobody asked about.
- **`pre_03`** *"Mauzo … TZS 50,000,000 — VAT ni asilimia ngapi, na je nahitaji kusajili NSSF?"*
  A real turnover figure, a real applicability ask with no figure of its own — every
  precondition of the naive rule is met, and NSSF registration is triggered by **employing
  someone**, not by turnover.

So the carry is conditioned on the measure: the preamble must name turnover, carry a figure, and
name no domain of its own; the receiving segment must have no figure and belong to a
turnover-threshold domain. **One measure is mapped today** (turnover → VAT/EFD) and the test
pins it, so adding a second is a deliberate edit that needs probes in both directions.

### Verification

- **43 new tests** (19 probes × contract + content-conservation, plus 5 pins); full suite
  **820 passed**
- candidate swept over **689 corpus questions** against a frozen copy of the pre-change
  decomposer: **4 rows change, 0 lose content, 0 unintended** — the 4 are th_19/th_20/th_24 and
  eval_332 (a genuine 3-part GN 487A question answered today as one). `scratch/naje_sweep.json`
- **9 of the 19 probes fail on the pre-change decomposer** — that is the measured gap
- **no dual-file sync needed:** since the v16 cutover production runs this module through
  `chike.orchestrator`; `modal_app.py` carries no decompose copy. `kaggle/eval.py` fetches the
  **frozen v15 arm**, which must not gain v16 capabilities — `test_pipeline_v15` now enumerates
  the two intended divergences (eval_322 ordinal, eval_332 `na je`) instead of asserting one, so
  an unintended one still fails
- the sweep's own content-conservation check first reported the **shipped** `na pia` split as
  content loss, because it counted the consumed connector. Instrument fixed before the result was
  read; noted because it is the same class as everything in the instrument-lie table

### ✅ R16 LIVE VERIFICATION — 3 of 3 half-answers fixed, 5 controls byte-identical

`app stop --yes` + redeploy with `PYTHONIOENCODING=utf-8`, questions read from the corpus files
rather than retyped (instrument-lie #7). `eval/results/naje_live_check.json`.

| | before | after |
|---|---|---|
| `th_19` | *"SDL = 3.5% × **TZS 500,000** = TZS 17,500"* — EFD absent | *"SDL = 3.5% × **TZS 6,000,000** = TZS 210,000"* **+** *"Ndiyo, unatakiwa kuwa na EFD kwa mauzo ya TZS 11 milioni au zaidi"* |
| `th_20` | *"NSSF = 20% × **TZS 750,000** = TZS 150,000"* — VAT absent | *"NSSF = 20% × **TZS 9,000,000** = TZS 1,800,000"* **+** *"…umepita kizingiti cha TZS 200,000,000 tayari, hivyo lazima usajili VAT"* |
| `th_24` | EFD answered — VAT absent | EFD answered **against the carried TZS 50,000,000** **+** *"Hapana — bado chini ya kizingiti cha TZS 100M/6 miezi"* |

> **The drop was hiding a second defect, and this is the part I did not predict.** On th_19 and
> th_20 the half that WAS answered was **answered on the wrong figure**: whole-message slot
> extraction pulled TZS 500,000 and TZS 750,000 out of messages whose payroll figures are TZS
> 6,000,000 and TZS 9,000,000. Splitting fixed the arithmetic as well as the omission. A
> multi-part message does not merely lose the second ask — it corrupts the first, because the
> extractor is choosing among figures belonging to two different questions.

**Preamble carry, verified live:** th_24's EFD half arrives with the turnover and is answered
against it. **Preamble false positive, verified live:** the minimum-wage reply is
*"Kulingana na GN605A, kiwango cha chini cha mshahara kwa sekta ya kilimo ni karibu TZS 175,000
kwa mwezi."* — no TZS 800,000, **no `halali` / `si halali` verdict**. That is the assertion
`pre_02` exists to make, made against production rather than against the parser.

**5 negative controls byte-identical**, including `nc_jengo` (the `na jengo` substring hazard —
still one question), `nc_eval180` (adverbial `pia`, the orphan deliberately not promoted) and
`nc_ooc` on a config-only OOC phrase — **CONTAINER-PATH-1 clear**.

**One more instrument caught before it reported.** The `pre_minwage` row's B-marker was the
phrase from the QUESTION (`kima cha chini`); the model answers with `kiwango cha chini`, so the
row scored as a dropped ask while the reply plainly contained the answer — and the leak check
split on the same absent phrase, so it read the whole reply and flagged TZS 800,000 from the
PAYE half as a leak. Both were **false alarms of my own harness**, caught by reading the replies
instead of the flags, and re-derived from the stored artifacts without re-asking. Table row #8.

### Two pre-existing defects the canaries surfaced, NOT fixed here

- `nc_jengo` — *"Nina duka na jengo langu mwenyewe — nahitaji leseni ya biashara ya aina gani?"*
  is answered by citing **GN 605A** (the minimum-wage notice) about building ownership and
  referred to **immigration.go.tz**. Both wrong, byte-identical before and after, nothing to do
  with decomposition. A retrieval/routing item.
- the BEFORE minimum-wage reply dated the agricultural floor *"kuanzia **Julai 2026**"* when
  GN 605A is effective **1 Jan 2026**. **Promoted to its own entry** — INVENTED EFFECTIVE DATES,
  above — because the scan found it is a class of three across three domains, and because no
  guard in this repo can currently see a wrong date at all.

## 📅 INVENTED EFFECTIVE DATES — live, unguarded, and dates are what users act on (2026-08-11)

**Its own item, promoted out of the decomposition write-up.** Found by the `na je` canaries;
not caused by that change and not fixed by it.

Production, on 2026-08-11, answering a minimum-wage question:

> *"Kima cha chini cha mshahara kwa sekta ya kilimo ni karibu TZS 175,000 **kuanzia Julai
> 2026**."*

**GN 605A is effective 1 January 2026** (CLAUDE.md §11, R5). The figure is right, the date is
invented, and it is six months late — an employer reading this underpays lawfully-owed wages for
two quarters and believes they are compliant. R5 exists because wage errors hit every employee of
every business that asks.

### It is a class, not a row

Scanning every stored artifact for `Julai 2026` returns **three distinct fabricated dates**, in
three different domains:

| claim | truth |
|---|---|
| agricultural minimum wage *"kuanzia Julai 2026"* | GN 605A effective **1 Jan 2026** |
| B2C e-payment VAT *"utekelezaji uliahirishwa hadi Julai 2026"* | 16% from **1 Sep 2025**, rules pending a CG notice — no such deferral exists |
| *"Finance Act 2026 iliweka tarehe ya mwisho ya 31 Julai 2026"* | there is no such deadline; the judge overlay caught this one and said so |

### The shape is the phantom relief's shape, in a different field

**Asked about the date directly, the model is right** — it correctly rejects a planted *"GN 605A
began July 2025"* premise, names the 13 Oct 2025 gazettement and the 1 Jan 2026 commencement, and
distinguishes GN 487A's 28 Jul 2025. The fabrication happens where the date is **incidental** to
an answer about something else, which is exactly where the relief defect lives: the fact is
present and inert on the path that isn't about it.

### Why nothing catches it

Every fidelity guard shipped so far compares a **figure** in the body against the engine's
computed amount. D-FIDELITY-1, -2 and -3 all take `ComputationResult.amount` as their anchor.
**A date has no anchor at all** — there is no engine output to contradict, `locked_facts.json`
holds the correct dates but nothing compares an answer to them, and the `wrong_patterns`
machinery is build-time-only and figure-shaped. The whole verification apparatus of this project
is currently blind to a wrong date.

### What it would take

A date-fidelity check is **more tractable than the figure guards**, not less: the set of
compliance dates is small, closed, and already in `locked_facts.json`; a date appearing in an
answer is either one of them or it is not. The hard part is attribution — which fact a date is
being claimed for — and that is the same attribution problem D-FIDELITY-2 solved for sibling
levies with cue proximity. Unpriced; see the board.

---

## 🧩 D-FIDELITY-3 SHIPPED AS A DELIBERATELY PARTIAL GUARD — one family closed, one named open (2026-08-11)

**Built, committed, DEPLOYED, live-verified.** Read the scope sentence before citing this entry.

**D-FIDELITY-3 closes the deduction-from-the-levy family at measured zero cost — 0 false
positives across 121 recovered bodies and all 9 negative probes, including all four
deliberately-protected rows — and it MUST NEVER be described as closing the intermediate-figure
hole. The paraphrase family remains OPEN: every wrong conclusion whose arithmetic is not written
out — `"Jumla ya bendi zote = TZS 78,000. PAYE ya kulipwa: TZS 52,000"`, and the same defect
punctuated with `sawa na`, `itakuwa`, or an addition instead of a subtraction — passes this
guard untouched, as do wrong conclusions hidden behind a net-pay tail, an example frame, or a
repeated figure.** Eight of the eighteen committed probes record exactly that, by name.

### The rule, and why it is not the obvious one

The defect and its commonest false positive are **structurally identical**:

```
DEFECT   "… = TZS  78,000 − TZS 26,000 = TZS  52,000"   (taken FROM the levy)
NET PAY  "… = TZS 800,000 − TZS 78,000 = TZS 722,000"   (the levy taken FROM the salary)
```

Both assert the authoritative figure and then operate on it. They differ only in **the label the
model puts on the result** — model phrasing, so no offline string rule can separate them. What a
string *can* see is which side of the operator the amount is on: in the defect it is the
**minuend**, the thing being reduced; in net pay the **subtrahend**, the thing taken away. Add
that the engine's `amount` IS the final payable figure — so a body deriving a **smaller** figure
from it has contradicted the engine by construction, while a larger one is usually a legitimate
conversion (per-year, per-employer, plus-sibling) — and the rule is:

> flag when the authoritative amount is the **first operand** of a written-out expression whose
> asserted result is **smaller** than it and not in `_acceptable`.

The two false positives the un-constrained version had (`TZS 78,000 × 12 = TZS 936,000`
annualisation, `TZS 78,000 + TZS 80,000 = TZS 158,000` aggregation) are both **increases**; the
smaller-than constraint removes both without costing the catch. That constraint is principled,
not lexical, which is why it is the one narrowing in this cycle that survived probing.

### Verification

- **30 new tests**; full suite **777 passed**
- 18 R17 probes committed as `eval/fidelity_gate/lastfig_conclusion_018.jsonl` +
  `tests/test_fidelity_conclusion.py`, wired to fail when a future widening trips a negative
  **or** when the open set changes size
- corpus: 121 round-trip-verified recovered bodies, **1 newly flagged, 0 false positives,
  0 protected rows broken**; the one catch is the live TZS 52,000 PAYE answer and is unique to
  this rule
- **no dual-file sync needed**: `chike-inference/modal_app.py` and the v16 gate harnesses both
  import `chike.orchestrator` from the package, so the guard has exactly one definition
- artifacts: `scratch/lastfig_sweep.json`, `lastfig_variants.json`, `lastfig_r17.json`,
  `lastfig_v6.json`, `lastfig_v6r.json`

### R16 live verification — the defect was present before and is gone after

`app stop --yes` + redeploy with `PYTHONIOENCODING=utf-8`, then the verbatim question:

| | |
|---|---|
| **before** | *"…Band 4 (760,001–800,000): 40,000 × 25% = TZS 10,000. Jumla kabla ya punguzo = TZS 78,000. **Punguzo la kibinafsi = TZS 26,000. PAYE inayolipwa = TZS 78,000 − TZS 26,000 = TZS 52,000.**"* + the deterministic working |
| **after** | *"PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000"* — body blanked, the working carries the answer alone |

**7 controls byte-identical**, including the net-pay row (eval_395 family), the NSSF split row
(eval_092 family), and `nc_ooc` on a config-only OOC phrase — CONTAINER-PATH-1 clear.
`eval/results/dfid3_live_check.json`.

**Decoding is greedy (`do_sample: False`), which makes this live check exact — and makes the
question wording load-bearing.** The first draft of the canary asked a PARAPHRASE of the defect
question, got a clean answer, and would have been recorded as "inconclusive" while the defect was
reproducible all along. The paraphrase is now kept as a control: it was clean before and is
byte-identical after, which is the negative half — the guard blanks a body only when the defect
is in it.

> **A third shape of R16's data-destruction lesson, and this one is not about encoding.** The
> BEFORE run was piped through PowerShell `Select-Object -First N` twice. Both times the pipe
> closed and killed the process **before it wrote its artifact**, silently — exit 0, output on
> screen, no file. Production had already moved to the new code by the time this surfaced, so the
> BEFORE artifact had to be rebuilt from the committed 2026-08-10 capture of the same question
> under the old code, with per-row `provenance` recorded (`scratch/dfid3_repair_before.py`).
> **Never pipe a measurement run through a truncating filter.** Use `Out-String` or read the
> artifact afterwards. R16's rule should be read as: no console operation may stand between a
> measurement and its file.

### A new live defect the canaries found, NOT fixed here

The fact row asking directly about the phantom relief is **wrong in production right now**, in a
new shape, and was wrong identically before and after this deploy:

> *"Hapana — hakuna punguzo la kibinafsi la TZS 26,000… **Punguzo la kibinafsi ni TZS 270,000 tu
> (TZS 26,000 × 10).**"* — appended working: *"PAYE = TZS 0 (mshahara TZS 26,000 uko ndani ya
> bendi ya 0%)"*

It denies the TZS 26,000 relief correctly and then **invents a TZS 270,000 personal relief**,
justified by arithmetic that does not even hold (26,000 × 10 = 260,000). CLAUDE.md §11 is
explicit that **no personal relief exists**: the TZS 270,000 is the 0% band, not a relief. And the
engine has extracted **TZS 26,000 as a SALARY** and computed PAYE on it, so a question about a
deduction was routed to the compute path.

This is the **seventh** shape of the phantom relief and the first where the wrong figure is
270,000 rather than 26,000 — which means the locked `wrong_patterns`, all anchored on 26/27,000,
cannot see it at all. It reinforces the paraphrase-family conclusion: guards catch shapes, the
model supplies them. Logged for the next adapter version.

---

## 🎣 A CLEAN ANSWER TO A REPHRASED QUESTION IS NOT EVIDENCE THE DEFECT IS GONE (2026-08-11)

**Promoted out of the D-FIDELITY-3 write-up because it is a rule about live checks, not a
detail of that guard.** It is a near-miss: caught before it produced a recorded number, unlike
the six entries in the instrument-lie table below — but the failure mode is theirs exactly, and
had it not been caught it would have been the cheapest one yet to believe.

The first draft of the D-FIDELITY-3 canary asked a **paraphrase** of the question that produced
the live TZS 52,000 defect:

| | |
|---|---|
| the defect question (2026-08-10) | *"Nionyeshe hatua kwa hatua **PAYE** kwa mshahara wa TZS 800,000 kwa mwezi."* |
| what the canary asked | *"Nionyeshe hatua kwa hatua **jinsi PAYE inavyohesabiwa** kwa mshahara wa TZS 800,000 kwa mwezi."* |

The paraphrase came back **clean**. Under the harness's own logic that is `defect_before =
False` → **INCONCLUSIVE** — "the model did not reproduce the guarded shape on this run" — a
verdict that reads as bad luck and closes the item. The defect was reproducible the whole time;
the verbatim question produces it every single run.

**Why the wording is load-bearing, and why this is not obvious:** decoding is greedy
(`do_sample: False`). Greedy decoding is normally cited as what makes a live check *exact* —
same prompt, same bytes, no sampling noise to average out. The same property makes it
**brittle in the input**: a different prompt is a different deterministic trajectory, with no
reason at all to pass through the same failure. Sampling would at least have given the defect
several chances to appear; greedy gives it exactly one, on exactly one prompt.

> **Rule: a live check for a specific defect must ask the VERBATIM question that produced it,
> copied from the artifact, not retyped and not improved.** The paraphrase is not worthless —
> it is now kept as the negative control, clean before and byte-identical after, which is the
> half proving the guard blanks only bodies that contain the defect. But it is the control, and
> it cannot be the positive case.

**The general shape, which is the instrument-lie shape:** the harness would have reported a
true fact (*this run did not reproduce the defect*) that answers a **different question** from
the one being asked (*is the defect still there*). Every row in the table below is that same
substitution — an instrument reporting truthfully about a checkpoint next to the one that
matters. Recorded there as **#7 (near-miss)**.

Cost of the rule: one `grep` through the artifact that recorded the defect. That is all it took
here — `dfid1_live_after.json` had the exact string.

---

## 🔁 CUE-BASED NARROWING RELOCATES THE FAILURE — it does not remove it (2026-08-11)

**A general finding about tuning guards, logged on its own because it will apply to the next one
someone tries to tune.** Not specific to fidelity.

The obvious fix for the intermediate-figure hole was a **last-asserted-figure** rule: the body's
FINAL assertion must be authoritative, not merely present. It was measured and **rejected**.

Over 121 recovered bodies it newly flagged 9 — of which **4 were already caught by
D-FIDELITY-2**, so its unique yield was 5: **2 genuine defects and 3 false positives.** Two of
those three were **eval_191 and eval_395 — half of the four rows whose protection is the entire
reason `body_contradicts_working` is permissive.** A fix that breaks two of the four rows the
thing it is fixing exists to protect is not a fix.

So four cue-based narrowings were built and probed against 16 authored probes:

| variant | probe failures | over-broad | escaped |
|---|---|---|---|
| V0 last figure not acceptable | **5** / 16 | 5 | 0 |
| V1 + must be a *new* figure | **5** | 4 | 1 |
| V2 + no net-pay cue in the tail | **5** | 2 | 3 |
| V3 + no example cue in the tail | **5** | 1 | 4 |

**The total never moves.** Each narrowing converted exactly one over-broad failure into exactly
one escape — and the escapes were not hypothetical: an adversarial probe was authored for each
cue, and each one works. `adv_02` hides a wrong `PAYE = TZS 52,000` behind a legitimate take-home
line, and V2's net-pay exclusion clears the entire body.

**The lesson, stated generally: when a rule's false positives and its true positives are the same
shape, adding cues to exclude the false positives hands the defect the same exclusions as an
escape hatch.** The failure count is conserved; only its visibility changes — and it moves from
the visible half (a correct answer blanked, which someone notices) to the invisible half (a wrong
answer passed, which nobody does). **That is a strictly worse trade than not narrowing at all.**
The only rules worth shipping are ones separating the two on a *structural* difference, as
D-FIDELITY-3 does; if none exists, the honest answer is a partial guard plus a named open family.

Corollary to R17, and the third confirmation of its core claim: V3 was still over-broad on
`neg_06`, a monthly→annual conversion tail **the stored corpus does not contain at all.** Only an
authored probe could find it.

---

## 🏷️ THE PARAPHRASE FAMILY — priced, and deferred to the next adapter version (2026-08-11)

**Open, not scheduled.** Recorded with its cost so the next person does not rediscover it.

What closing it would take: a **conclusion-labelling check** — determining, for the final figure
in a body, whether the model is claiming it as *the levy payable* or as something else
(take-home, an annual total, a band component, an example). That is a judgement about phrasing,
so per MEASUREMENT-GAP-1 it cannot be validated by an offline sweep; it needs a **live check in
the loop** on every candidate wording, in both polarities, on the scale the th_16 wording
attempts used (6 candidates × 12 canaries before one was rejected on evidence).

**The recommendation is that this is the wrong shape of fix.** It would be the **fifth**
render-side guard on the same underlying problem — a model that re-derives arithmetic it was
handed — and each of the four so far catches one shape while the supply of shapes belongs to the
model. The phantom TZS 26,000 relief entry documents the same conclusion from the other
direction: an on-point, rank-1, in-context fact lost to the prior. **Fix it in the SFT set for
the next adapter version, not with a fifth guard.**

If it must be guarded before then, the cheapest honest option is not a cleverer rule but
**suppressing the body entirely for step-by-step compute questions** — the minimum-wage and
VAT/EFD routes already prove a deterministic path with no generation on it is shippable, and the
compute path is where every one of these defects lives.

---

## 🧾 THE `wrong_patterns` LIST IS INCOMPLETE FOR OUTPUT-CHECKING — in a way it is not for training pairs (2026-08-11)

**For whoever wires the runtime check.** The build-time-only `wrong_patterns` machinery was
already logged as a candidate; this is the measurement it needs, so it is not shipped incomplete
in the belief that it is complete.

The 11 patterns in `paye_personal_relief` catch **4 of the 6** phantom-relief sightings across
2,314 stored generations. They **miss eval_320 entirely**:

> `PAYE = 8% × TZS 800,000 − TZS 26,000 = TZS 64,000`

There is no `punguzo` or `relief` word anywhere near the number — the model just subtracts it.
Every one of the 11 patterns is anchored on the *vocabulary* of the relief, which is present in a
training pair asserting it and routinely absent from an answer applying it. **That is the
asymmetry: a list authored to audit training text is not a list that can audit output.**

A bare subtraction pattern closes it:

```
[-−]\s*TZS\s*2[67],?000
```

| | |
|---|---|
| caught by the 11 named patterns | 4 / 6 |
| caught by the bare subtraction pattern | 3 / 6 |
| **caught by the union** | **6 / 6** |
| false positives, union, over all 2,314 stored generations | **0** |

**Add the bare-subtraction form when the runtime check is wired.** Note it is a *runtime output*
pattern, not a training-pair pattern — a training pair legitimately quoting the wrong figure in
order to deny it would trip it, which is harmless at build time and matters at runtime only if
the check is applied to input as well. Artifact: `scratch/relief_26k_evidence.json`.

### ⛔ THE BOUND ON THE MECHANISM — meet this BEFORE designing the check, not after

6-of-6 is the ceiling on the shapes we have measured, not on the defect. **The seventh shape
(2026-08-11, live) cannot be reached by any pattern list at all**, and the argument is
structural rather than a matter of finding a better regex:

> *"Hapana — hakuna punguzo la kibinafsi la TZS 26,000… **Punguzo la kibinafsi ni TZS 270,000
> tu (TZS 26,000 × 10).**"*

- **Keyed on the wrong figure (26/27,000) → blind.** Both occurrences of 26,000 here sit inside
  a *correct denial*. A pattern that fires on them fires on the system working, and the union
  above would score **0 of 1** on this answer.
- **Keyed on the right figure (270,000) → over-broad.** TZS 270,000 is the Band 1 ceiling and a
  legitimate number in the locked facts. A pattern on it fires on every correct answer that
  explains the tax-free threshold, which is most correct PAYE answers.
- **Keyed on the word `punguzo la kibinafsi` → also over-broad**, for the same reason: the
  correct answer to "is there a personal relief?" must use the phrase in order to deny it.

The defect is the **concept** — *PAYE has a personal relief* — held independently of any number
attached to it. A pattern list can only ever see a number or a word, so the class where the
model keeps the concept and refills the figure is outside what the mechanism can express. This
is the same result as CUE-BASED NARROWING RELOCATES THE FAILURE, reached from the other end: the
model supplies the shapes, and each new shape is another reactive catch.

**Consequence for whoever wires this:** the runtime check is still worth building — it closes 6
of 7 measured shapes at 0 false positives over 2,314 generations, which is a real reduction in
live wrong answers. **Build it, and write its ceiling into its own docstring.** Do not let it be
described as closing the phantom relief; the closing move is the next adapter version (see the
phantom-relief entry), and this check is what holds the line until then. Same shipping discipline
as D-FIDELITY-3: partial, measured, and honest about the family it leaves open.

---

## ⚠️ D-FIDELITY-1 BLANKS TWO CORRECT BODIES — its own-levy rule never consults `_acceptable` (2026-08-11)

**New, found by the D-FIDELITY-3 probes, NOT fixed.** Logged as its own item because fixing it
changes verdicts across the recovered-body corpus and needs its own sweep.

`body_contradicts_working` (own levy) tests `amount not in results`. `body_contradicts_siblings`
tests `results & _acceptable(result)`. **The own-levy rule never consults `_acceptable` at all**,
so neither the figures the engine's own working states nor the employer/employee split sum clear
it — even though `_acceptable`'s docstring exists precisely to say a faithful NSSF body may
legitimately quote either share. Two authored negatives are blanked today:

| probe | body | why it is correct |
|---|---|---|
| `neg_05` | *"NSSF: mfanyakazi anachangia TZS 80,000, mwajiri anachangia TZS 80,000. **Jumla ya mchango: TZS 160,000.**"* | 160,000 is the split sum the working itself spells out — in `_acceptable`, invisible to the own-levy rule |
| `neg_07` | *"PAYE ni TZS 78,000. Kumbuka mshahara wa TZS 800,000 unazidi TZS 760,000, ndiyo maana **Band 4 inatumika: TZS 760,000.**"* | 760,000 is in the working; and bare `ni` is not an assert-connector, so the correct 78,000 is not even in the asserted set |

This is a **false-positive class — correct answers deleted, not wrong ones served** — which is why
it is logged rather than hot-fixed. `neg_07` also shows the deliberate `ni` rejection (D-FIDELITY-1,
2026-08-10) has a cost that was not measured when it was made: a body stating its result with bare
`ni` has an EMPTY asserted set, so any other figure it mentions becomes the whole basis of the
comparison. Pinned by `test_dfidelity1_blanks_two_correct_bodies`, which fails if the class grows.

---

## 💰 VAT/EFD THRESHOLDS ARE A DETERMINISTIC ROUTE — and the untested limb comes back as a derived condition (2026-08-10)

**Built, committed, DEPLOYED, live-verified.** The third member of the threshold-comparison
class, and the one SAFETY-3 was originally found on: production reciting `200,000,000`
correctly **in the sentence where it misapplied it**.

### What was live until today, in both directions

| probe | BEFORE | AFTER |
|---|---|---|
| **below_annual** TZS 150M/year | *"**Ndiyo — umefikia kizingiti** cha TZS 200M/mwaka au TZS 100M/6 miezi. **Lazima usajili VAT** na TRA ndani ya siku 14… **Ukichelewa, unaweza kupata adhabu.**"* — tells a trader who is **under** the threshold that they have crossed it, and threatens penalties | *"Kwa upande wa miezi 12: hapana, mauzo yako ya TZS 150,000,000 hayajafikia kizingiti cha TZS 200,000,000. **LAKINI hili halijamalizika:** usajili ni wa lazima pia **IKIWA** mauzo yamefikia TZS 100,000,000 katika miezi 6 mfululizo…"* |
| **six_month_over** TZS 120M in 6 months | *"Hapana, bado. TZS milioni 120 katika miezi 6 ni **CHINI YA** TZS 100,000,000"* — **the SAFETY-3 shape verbatim**: the right threshold recited, the comparison inverted, and a trader who must register told they need not | *"Ndiyo, unatakiwa kujisajili VAT. …TZS 120,000,000 kwa miezi 6 mfululizo yamefikia au kuzidi kizingiti cha TZS 100,000,000…"* |
| **above_annual** TZS 450M/year | right verdict, no figures, no working | verdict with both operands and the limb named |
| **boundary_200m** exactly TZS 200M | *"Ndiyo, unatakiwa kusajili VAT **mara tu utakapofikia** kizingiti"* — future tense; never says whether they have | *"Ndiyo… TZS 200,000,000 kwa miezi 12 **yamefikia au kuzidi** kizingiti…"* |
| **monthly_rate** TZS 25M/month | **HTTP 500** | the never-guess clarification, with no annualised figure in it |

**Both directions were wrong, on the same threshold, in the same week.** `below_annual` invents
a crossing that has not happened; `six_month_over` denies one that has. Neither is a retrieval
failure — the threshold is correct in both.

### The two limbs are independent tests, and that is the whole design

Registration is compulsory on **TZS 200M/12mo OR TZS 100M/any rolling 6mo**. A figure stated
for one period carries **no information** about the other: 150M/year is below limb A and
entirely consistent with 120M in one half-year, which is registrable. So *"150M < 200M,
hapana"* is not a conservative approximation — it is the SAFETY-3 shape with a different
number, and it is what production said.

Founder decision (**Option 1**): test the limb the stated period addresses; when it does not
establish registration, carry the other limb as an explicit open condition; when it does, no
conditional at all, because one crossing settles it.

> **The conditional is DERIVED, never authored.** `_LIMBS` is the only description of the two
> limbs, `_untested_limb` picks the one not addressed, and the clause is emitted from that. No
> code path can attach a conditional to a limb that WAS tested, or omit one for a limb that was
> not — the same rule as the minimum-wage verdict word, for the same reason: a sentence that
> could drift out of agreement with the verdict beside it must not be written twice.

EFD is not a second copy of the comparison: its threshold is annual turnover TZS 11M, but a
VAT-registered person needs an EFD **regardless**, so registration is tested first and
short-circuits the turnover entirely — and below the threshold the derived open condition is
VAT registration, not a second limb.

**A monthly figure is a rate, not a period total, and is never annualised.** 25M/month × 12 =
300M looks decisive and is an assumption about a seasonal trader's future. Those decline.

### Three defects, each caught by a different instrument

**1. The router sweep — 18 diverted rows, most of them wrong.** The first version required only
`{obligation cue + magnitude}`. It stole threshold **lookups** (`eval_002/003/381`), **false-
premise confirmations** (`eval_347/349` — *"kizingiti … ni TZS 200,000,000, sivyo?"*, where the
figure is the misquoted THRESHOLD and not turnover), **projections** (`eval_006/007/010`), a
**Kenyan-shilling** row, and gave `th_09/th_10` to VAT when the ask was EFD. Fixed with an
own-turnover requirement — the `mshahara`→pay-verb narrowing in its second domain — plus an ask
veto, a foreign-currency veto and EFD precedence. Final: **732 rows, 15 diverted, all genuine,
`other_route_changes: 0`.**

**2. The corpus caught a wrong boundary.** Written strict (`>`); `eval_351` is exactly TZS
200,000,000 and its gold is explicit — *"Kufikia … **(SIYO TU KUZIDI)** kunalazimisha
usajili"* — tagged `_why_hard: exactly at 200M — inclusive boundary`. The row exists to catch
this and did. Now `>=` on both limbs and EFD, pinned by four parametrised boundary tests and
by a live canary, since it is the edit most likely to be reintroduced.

**3. INSTRUMENT-LIE #6 — see its own entry below.**

### Verification

- **26 new tests**; full suite **747 passed**
- R17 probes: **18 rows, 0 failures** — 11 positive, 7 negative controls
- offline orchestrator: 25 rows, **0 model calls, 0 model-text leaks, 0 polarity failures,
  0 outcome mismatches**
- **live**: 7 threshold rows CHANGED, **6 negative controls byte-identical**, and the polarity
  reader run over the **actual deployed strings** — 6 assertions, **0 failures**. `neg_ooc`
  byte-identical on a config-only phrase (CONTAINER-PATH-1 clear).
- artifacts: `eval/results/vat_route_sweep.json`, `vat_orchestrator_offline.json`,
  `vat_live_check.json`

The negative control worth naming: **`nc_05`** — *"Je, wakili aliyesajiliwa lazima asajilishe
VAT hata kama mapato yake ya mwaka ni chini ya TZS milioni 200?"* Registration vocabulary, a
magnitude, an explicit annual period — and the correct answer is **yes regardless**, because
listed professionals must register whatever their turnover. Routed to the engine it returns a
confident *"below the threshold"* that is flatly wrong. It is byte-identical live, and it is
the row to watch if this arm is ever widened.

### Logged, not fixed

- **`th_24` is answered by half.** *"…je nasajili VAT **na** je nahitaji EFD?"* returns the EFD
  verdict; the VAT half is silently dropped — not answered wrong, not answered. Same connector
  class as instrument-lie #5's `na pia`. **That is now twice that decomposition has silently
  dropped a sub-question, which promotes it from an incident to a candidate for its own
  investigation.** A dropped half is invisible in exactly the way D-FIDELITY-1's blanked bodies
  were: nothing in any artifact says a question went unanswered.
- **9 of 25 on-path rows are clarifications, 6 of them because turnover was quoted as a monthly
  rate** (`nat_25`, `edge_p01`, `edge_p08`). **Recorded here because that number will look like
  a regression to anyone reading the gate without the reasoning.** It is not: annualising
  25M/month to 300M is a guess about a seasonal trader's future dressed as arithmetic, and
  `vf_11` is the probe that pins it — there, annualising gives the RIGHT answer by the WRONG
  method, which is precisely how a bad method gets adopted and then generalised to a case where
  it is wrong.

## 🪞 INSTRUMENT-LIE #6 — route-correct is not outcome-correct (2026-08-10)

The VAT orchestrator harness reported **25 rows on path, 0 model calls, 0 leaks, 0 polarity
failures** for a build in which **three rows silently clarified instead of answering**.
`ya mwaka` — the genitive, and the commonest way a trader says annual turnover (*"mauzo yangu
**ya mwaka** ni milioni 15"*) — was not matched; only `kwa mwaka` was. Those rows routed to the
threshold arm **correctly**, and then fell out one stage later at the period test.

Every number the instrument printed was true. None of them was the answer.

> **The harness was asserting the checkpoint immediately before the one that broke.**

Fixed by widening the harness to assert each probe's `truth` — the outcome the user actually
gets — which surfaced it at once; rendered verdicts went **16 → 19**.

### Pair it with MEASUREMENT-GAP-1: same failure shape, different stage

| | MEASUREMENT-GAP-1 | instrument-lie #6 |
|---|---|---|
| what was measured | the fact **reaches the prompt** | the question **reaches the right route** |
| what was assumed to follow | the model applies it | the engine answers it |
| what actually happened | recited correctly, applied wrongly | routed correctly, clarified instead of answering |
| how it read | "7/8 targets served" ≈ "7/8 correct" | "25 on path, 0 failures" ≈ "25 answered" |

Two years of instrument design would not separate these: they are one error at two stages of
the same pipeline. The general rule, which now covers both:

> **An instrument must assert the OUTCOME THE USER GETS, not the last checkpoint before it.**
> Every intermediate green is a claim about a stage, and the distance between that stage and
> the user is unmeasured by construction.

This is the sixth instrument this project has caught lying and the third caught by widening
what a check asserts rather than by adding a new check. The table of the first five is in the
`na_06` entry below.

---

## ⚖️ MINIMUM WAGE IS NOW A DETERMINISTIC ROUTE — the comparison left the model (2026-08-10)

**Built, green offline, NOT DEPLOYED.** The th_16 class fix, done the way the evidence pointed:
a genuine `minimum_wage` computation type behind the rules engine, with sector resolution and
four never-guess exits. `Orchestrator._deterministic_answer` blanks the model body and renders
the working verbatim, so **`model_calls_on_wage_path: 0`** — every mechanism behind the six
failed wordings is removed structurally rather than guarded against.

That last point is what makes offline evidence sufficient here, and it is the exception rather
than the rule. MEASUREMENT-GAP-1 says a fix whose success depends on how the model REASONS over
a fact needs live generation inside the loop. **This fix does not depend on that** — there is no
generation on the path to depend on. What still needs the live check is the wiring: that the
container actually runs this code and that nothing else regressed (R16, CONTAINER-PATH-1).

### The five pieces, and why each is shaped the way it is

| piece | shape | the argument |
|---|---|---|
| **the Schedule** | 50 rows × 5 period columns, hand-transcribed, `verify_transcription()` asserts **all 250 figures** back against the committed gazette extract | the PDF interleaves columns with labels; a silent mis-parse puts a wrong wage in front of an employer. Transcription is auditable, not trusted |
| **periods** | compared **column to column, never converted** | the Order prescribes hourly/daily/weekly/fortnightly/monthly for every row. TZS 10,000/day against the MONTHLY 175,000 floor calls a lawful wage unlawful; against the daily 6,731 it is lawful. No division, no ×26 — a class of arithmetic error removed instead of guarded, and it does not wait on the unit-normalisation item |
| **the resolver** | four outcomes: ROW / SECTOR / UNLISTED / NONE | a sector is not a rate — **12 of 16 sectors carry more than one**, largest spread **TZS 532,500** (12a business 200,500 → 12b(i) commercial banks 733,000), and **5 of 7 sector-only cases flip the verdict** across their candidates. Guessing a sub-sector returns the OPPOSITE legal answer, not a less precise one |
| **item 16** | **UNLISTED is a separate outcome from NONE, and the UNLISTED cue table ships EMPTY** | TZS 175,000 is the rate for a sector the ORDER does not list — not the answer to "the user didn't say what the work is". Populating the table needs a labour-law source: para 3 defines "agriculture", "domestic work", "energy", "mining operations" but NOT the scope of "Trade and finance", so whether a salon is item 16 (175,000) or 12a (200,500) is a classification the gazette does not settle — and a wage between them gets opposite verdicts |
| **the never-guess exits** | four, in the orchestrator, ordered status → amount → period → row | **C4, measured:** a locked fact saying *"SINA UHAKIKA … usiseme mshahara ni halali bila kuthibitisha sekta"* was retrieved on 6 of 8 probes and **the model adjudicated anyway on every one.** A refusal must be a code path that runs INSTEAD of generation |

### The inversion had a second source, on the question side

Blanking the body kills the MODEL-side inversion. It does nothing about the QUESTION's frame:
*"je ni halali?"* and *"nakiuka sheria?"* take **opposite lead words for identical facts**, and
the yes/no scorer reads the polarity of the first paragraph. So the lead is selected from
`(frame, compliant)`, the verdict word is derived from the boolean **in one place and never
authored twice**, and where the frame is unmatched — including a question carrying both framings
— there is **no lead at all**: the answer opens with the substantive comparison
(*"Mshahara wa TZS X uko CHINI ya kima cha chini cha TZS Y"*), which is correct under either
reading and does not depend on the detector being right. `mw_06`/`mw_07` are the two directions.

### Blast radius: bounded by construction first, then measured

The arm is **placed last in `detect_intent`**, immediately before the fact fallthrough, so by
construction it can only capture questions that route to fact today — every levy route wins
first. The sweep then confirmed it over a **675-question corpus**:

| | |
|---|---|
| rows changing route | **15 — all 15 in the new probe file** |
| `other_route_changes` | **[]** |
| R17 cue probes | 0 misroutes, 0 non-wage leaks, 1 benign self-collision (`benki ya biashara` matching its own sector cue, which resolves to the row anyway) |

**The narrowing that mattered was caught by the sweep, not by authoring.** The first cue list
included the noun `mshahara`. It stole **five real gate questions** — eval_118/119/120/126/382,
all GN 605A **lookups** (*"wastani wa mshahara wa chini … ulikuwa TZS ngapi?"*). Each says
`mshahara wa chini` and carries a `TZS` token, so cue and magnitude were both satisfied while
**nobody was being paid anything**, and each would have been answered with "tell me what work
your employee does" — not an answer to any of them. The fix is a **pay VERB**, which is what
distinguishes "I pay X" from "what is X", and it is the narrowest form that closes the case per
R17. `analipa` (he pays) is excluded and only `analipwa` (he is paid) kept — the active form
appears in *"mfanyakazi analipa kodi"*, a levy question.

A second find of the same kind, from the exhaustive cue-collision pass rather than from reading
the table: **`duka la dawa`** (pharmacy, 2e, 240,000) contains **`duka`** (12a, 200,500). Both
cues fired, the sectors conflicted, and a perfectly resolvable question got the "tell me what
work" clarification. Fixed with a negative lookahead. A collision between two cues that are each
correct on their own is not a shape authoring finds.

### Verification

- **73 new tests** (`tests/test_minimum_wage.py`); full suite **721 passed** (648 + 73)
- `eval/results/mw_orchestrator_offline.json` — **20/20 probes correct end to end through the
  real orchestrator**, `model_calls_on_wage_path: 0`, `model_text_leaked: False` on every row
  including both multipart carriers (a stub model returning `"NDIYO NI HALALI KABISA"` sits on
  the sibling sub-questions specifically so a leak onto the wage answer would be unmissable)
- `eval/accuracy_gate/minimum_wage_probes_018.jsonl` — **20 probes with `guards_against` per
  row**, including three R17 negative controls (`mw_16` GN 487A lawfulness, `mw_17` a levy
  question carrying a wage figure and `ni halali`, `mw_18` employment lawfulness with no figure)
- `eval/results/mw_sector_resolution.json`, `mw_route_sweep.json`, `mw_r17_cue_probes.json`
- primary source: `docs/domain_research/gn605a_2025_gazette_extract.txt` (kazi.go.tz, Tier 1A)

### ✅ DEPLOYED AND VERIFIED LIVE (2026-08-10) — th_16 is fixed in production

R16 procedure: `app stop --yes` (verified `stopped`, 0 tasks), redeploy, then **12 canaries run
before and after** and compared. **All 8 wage rows CHANGED. All 4 controls BYTE-IDENTICAL.**
That separation is the result: the deploy moved exactly the surface it was meant to move.

**The "before" column is the most important thing this cycle produced, so it is quoted verbatim
rather than characterised. This is what was live.**

| probe | BEFORE (live in production until today) | AFTER |
|---|---|---|
| **th_16** 200,000, farm | *"**Hapana** — malipo hayo yanazidi kiwango cha juu cha chini cha lazima cha kisheria… mfanyakazi wa shamba anaweza kulipwa kiwango cha chini cha TZS 175,000 **tu**. **Malipo ya ziada juu ya hapo ni kinyume cha sheria.**"* | *"**Ndiyo, ni halali.** Mshahara wa TZS 200,000 kwa mwezi uko **JUU ya** kima cha chini cha kilimo — mazao au mifugo, ambacho ni TZS 175,000 (GN 605A, Jedwali la Pili…). **Kifungu cha 4(3)** kinaruhusu kulipa **ZAIDI** ya kima cha chini."* |
| **th_15** 150,000, farm | *"Hapana — …Mshahara wa TZS 150,000 unakiuka sheria."* (right verdict, no schedule, no citation) | *"**Hapana, si halali.** …uko **CHINI ya**… Unatakiwa kupandisha mshahara hadi angalau TZS 175,000 kwa mwezi."* |
| **floor_exact** 175,000 | *"Hapana — mshahara huo ni **chini sana** ya kiwango cha chini cha GN605A… kiwango cha **wastani** cha karibu TZS 175,000… lakini kwa mfanyakazi huyu, mshahara wa TZS 175,000 ni **chini ya** kiwango cha chini"* — the floor called below itself, and the floor called an *average* | *"**Ndiyo, ni halali.** …uko **SAWA na** kima cha chini…"* |
| **hotel_4star** 350,000 vs 375,000 | *"Kwa mujibu wa **GN487A**, shughuli za huduma za malazi na utalii imepigwa marufuku kwa **wasio raia**…"* — the wrong statute entirely; answered a non-citizen question nobody asked | *"**Hapana, si halali.** …uko CHINI ya… hoteli ya nyota nne au tano, ambacho ni **TZS 375,000**…"* |
| **bodaboda** | *"Hapana — malipo hayo yanazidi kiwango cha juu cha kisheria cha TZS 175,000… **Ni lazima umrudishe fedha zilizozidi** ili aweze kupata cheti sahihi cha kodi."* — **instructed an employer to claw back wages already paid** | the Cap. 366 status clarification: **zero figures, no verdict word** |
| **frame_lawful** / **frame_violation** 450,000 | *"**Ndiyo**, ikiwa unalipa PAYE sahihi. TZS 450,000/mwezi = TZS 18,000,000/12 miezi…"* / *"**Ndiyo** — malipo hayo yanazidi kiwango cha juu cha PAYE cha asilimia 30…"* — **the same word for both framings**, both reasoning about PAYE, both arithmetically wrong | *"**Ndiyo, ni halali.**"* / *"**Hapana, hukiuki sheria.**"* — **opposite words, identical substance**, both against the 398,500 floor |
| neg_gn487a · neg_sdl · neg_paye | correct | **byte-identical** — no levy or immigration question was diverted |
| neg_ooc | refuses | **byte-identical.** `kodi ya majengo` is config-only and absent from the 39-phrase fallback, so this proves the container loaded its full config (CONTAINER-PATH-1 clear) |

Three of those "before" answers are worse than th_16 itself, and none of them was on any list:
**an instruction to claw back lawfully paid wages**, **an answer about non-citizen business
prohibition to a question about a hotel waiter's pay**, and **the floor declared to be below the
floor**. th_16 was the one that had been noticed, not the worst one. Artifact:
`eval/results/mw_live_check.json`.

### A spec disagreement, recorded with its resolution

The canary spec written before the run required `hotel_no_star` to **"clarify and emit no
figure."** It clarifies, asserts no verdict — and emits **nine figures**: the sector range plus
all six sub-sector rates by name. Flagged as a deviation and **not** iterated on live.

**Founder resolution: leave as designed, and the spec was the weaker instruction.** The
distinction that settles it is worth keeping:

> **A figure that RESOLVES the question versus figures that ENUMERATE the candidates.**

The constraint exists to stop an unsourced rate being asserted as though it answered the
question. Naming all six of the Order's sub-sector rates does the opposite of that: it is
sourced, it is actionable, it hands the employer the means to resolve it themselves, and it is
what a competent advisor says. The rule the codebase now carries is the distinction, not "no
figures" — `MIN_WAGE_NO_SECTOR` and the bodaboda exit still emit nothing actionable, because
there is no candidate set to enumerate in either.

### The `ni halali` substring — fixed structurally, and the pin found a second one

`sector_rates_statement` refused correctly while containing the affirmative cue: *"siwezi kusema
kama TZS 250,000 … **ni halali** bila kujua aina ya kazi hasa."* Plain to a reader, invisible to
a yes/no scorer reading the polarity of the first paragraph. Rephrased to *"siwezi
**kulinganisha** …"* — **the substring is gone, not handled** — and pinned by
`test_no_clarification_reads_as_a_verdict`, which runs `wage_question_frame` (the polarity
reader itself) over our own output and asserts `unknown`, across **every sector**, plus a
positive control so the test cannot pass on a build that stopped stating verdicts.

**The pin immediately found a second instance the twelve live canaries had not surfaced:**
`MIN_WAGE_NO_SECTOR` read *"Ili nikwambie kama unacholipa **ni halali**, niambie…"* → `lawful`.
Written the same day, by the same hand, in copy explicitly designed to state no verdict. A
lexical defect recurs wherever the vocabulary is natural, and a check that reads the mechanism's
own output catches the recurrence for free — the cheapest instrument in the repo, again.

**Both fixes deployed and re-verified live** (second R16 pass, `79e41a2`): re-running all 12
canaries, **exactly one row changed — `hotel_no_star`, the row the fix targeted** — and the
other eleven, including all four controls, were byte-identical to the previous run. Live
polarity of every clarification now reads `unknown`. The no-sector exit is not exercised by any
of the 12, so it was probed separately and directly: *"Namlipa mfanyakazi wangu TZS 200,000 kwa
mwezi — je ni halali kisheria?"* → the sector clarification, polarity `unknown`, and **no
TZS 175,000 anywhere in it** (the item-16 conflation, still closed).

### 🔌 OUTAGE — ~2 minutes, no wrong answers served (2026-08-10)

`modal app stop chike-inference --yes` succeeded instantly. The `modal deploy` that was to
replace it **aborted**: `'charmap' codec can't encode character '✓'` — the Modal CLI's own
`✓` glyph, unprintable on a cp1252 Windows console. Both app records sat `stopped` and the
endpoint was dead until a redeploy with `PYTHONIOENCODING=utf-8` succeeded in 12s. Production
was **unavailable, not incorrect**.

**The operational lesson outranks the incident, and R16 now carries it:** `app stop` followed by
a deploy that CAN FAIL leaves production dead in the gap. The stop is instant and reliable; the
deploy is neither. So `PYTHONIOENCODING=utf-8` belongs in the deploy command alongside
`PYTHONUTF8=1`, and **the R16 sequence must state that the window exists** rather than reading
as an atomic swap.

**The same encoding fault also truncated a live canary run mid-pass, losing the artifact — twice
in one session, in two different tools.** Any script that prints model replies now calls
`sys.stdout.reconfigure(encoding='utf-8', errors='replace')`: a console encoding must never be
able to destroy measured data or abort a deploy.

### Open, and deliberately left open

- **NOT DEPLOYED.** `chike/` is mounted into the Modal image, so this needs a deploy to reach
  production, and R16's full procedure — `app stop --yes`, redeploy, then th_16 itself as the
  positive probe with levy and OOC negatives — before any claim that it is live.
- **`_UNLISTED_CUES` is empty**, so an occupation genuinely absent from the Order is clarified
  rather than answered with item 16. Correct today; closing it needs a labour-law source.
- **Employment status** (bodaboda, gig work) exits to a clarification naming Cap. 366 rather
  than being resolved by a cue. Its own item — the answer is wrong in both directions if guessed.
- The resolver is **narrow by design**: 11 of 22 authored phrasings resolve to a row. *"Hoteli ya
  nyota ngapi?"* is what a competent advisor asks back; it is a good answer, not a failure.

## 🔎 D-FIDELITY-1 HAS BEEN BLANKING CORRECT BODIES SINCE IT SHIPPED — a guard whose false positives are invisible by construction (2026-08-10)

The item was opened because the guard MISSES contradictions: `_RESULT` matched `=` and nothing
else, so "SDL … **sawa na** TZS 210,000" against a working of TZS 17,500 produced an empty
asserted-set and `body_contradicts_working` returned False. That is real, and it is **the
smaller half**.

The sweep over every recoverable stored body found the blindness is **two-sided**, and in the
measured population the false positives outnumber the misses **3 : 2**:

| direction | n | what it looks like |
|---|---|---|
| **contradiction MISSED** | 2 | th_19's `sawa na TZS 210,000`; and an NSSF body claiming employee TZS 400,000 **(20%)** *and* employer TZS 400,000 **(20%)** of a TZS 800,000 salary — engine 160,000 |
| **CORRECT body blanked** | 3 | a right band breakdown or employer/employee split whose total line reads `Jumla ya mchango: TZS 200,000` — `=`-only matching cannot see the total, `amount not in results` fires, the body is discarded |

**The new failure shape, and the reason this went unnoticed for so long: a guard's false
positives are invisible by construction.** When D-FIDELITY-1 blanks a correct body, `_render`
still emits the deterministic working, so the user gets a correct — merely tersest — answer. No
gate row fails. No judge marks it wrong. Nothing in any artifact says "an explanation was
deleted here." **A deleted explanation is indistinguishable from a model that was terse.** The
missed contradictions were the visible half only because a wrong number eventually shows up in a
judge verdict; the blanked-correct half produces no signal at all, anywhere.

That generalises past this guard: **any blanking/suppression mechanism needs its removals
counted, not just its firings.** Whatever replaces content must record that it did.

One of the two missed contradictions deserves naming on its own: the NSSF 20%+20% body **passed
the regex scorer AND the judge called it correct.** Both scorers saw a plausible-looking split
and a total; neither checked it against the engine. That is what the guard is for, and it was
the punctuation — a colon instead of an equals — that let it past.

### The size of it, and the honest limit on that number

| | |
|---|---|
| stored merged answers with a compute part | **402** |
| compute bodies judged (round-trip verified, + 2 stored directly) | **118** |
| rows the parse REFUSED to guess at (engine drift since those runs) | **261** |
| … of those, containing an assertion construction `_RESULT` cannot see | **58** (colon 26, levy-`ni` 23, `sawa na` 6, `itakuwa` 4, `ni karibu` 1) |
| **bodies whose verdict changes** | **5 of 118 — 4.2%** |

The 261 is the limit, stated rather than buried: those artifacts predate the current engine, so
body and working cannot be told apart in them and `render_recovery` correctly declines. The 58
bounds what is out of reach instead of leaving it unquantified.

### Widened on attestation, and one candidate killed by the probes

Connectors harvested by frequency from **946 distinct stored generations / 3,381 TZS amounts**
(`scratch/dfid1_constructions.py`), each shipped with the count that justifies it: `=` 703,
`:` 198, `sawa na` 24, `ni karibu` 11, `→` 8, `itakuwa` 5, `kitakuwa` 4.

**Bare levy-scoped `ni` was REJECTED.** Frequency argued for it — 23 occurrences among the
unrecoverable rows, and `ni` is the second most common connector in the corpus at 373. The R17
probes settled it: it reads a PAYE band boundary (`na_13`), an SDL applicability threshold
(`na_14`) and an NSSF exemption (`na_15`) as computed results. **Frequency would have shipped
it; only the authored adversarial probes stopped it.**

Two refinements the probes forced, both of which change what the OLD `=` pattern extracted, so
the widening is **not purely additive**: a digit boundary, and an operand exclusion — an
asserted result is a TERMINAL figure, never the left side of `TZS 250,000 × 8%` or
`TZS 270,000 = TZS 0`.

Final: **0 false positives across 16 non-assertion probes, 0 misses across 7 assertion probes.**

### D-FIDELITY-2 shared the gap — one fix, not two

Verified by direct call rather than inferred, because the corpus contains none of the missed
forms. One employee, engine says SDL does not apply, body volunteers TZS 28,000:

| punctuation | before the fix |
|---|---|
| `SDL = TZS 28,000` · `SDL: TZS 28,000` | caught |
| `SDL ni sawa na TZS 28,000` · `SDL ni TZS 28,000` · `SDL itakuwa TZS 28,000` | **missed** |

Three of five punctuations of the same wrong figure. `_ATTRIBUTED` is now the same object as
`_RESULT`, with a test asserting it, so a future re-split has to argue for itself.

### Verification

- full suite **615 passed**; new regression file `tests/test_fidelity_assertion_widening.py`
  **33 tests**
- `scratch/preflight_wiring.py`: **87/87 workings byte-identical, 0 round-trip failures,
  cross-levy blanking still exactly `{eval_318, eval_320}`**
- **0 of the 18 bodies recoverable from the current gate artifact change verdict** — no expected
  behaviour change on the measured gate
- sweep artifact: `eval/results/dfid1_stored_body_sweep.json`

---

### ✅ DEPLOYED AND VERIFIED LIVE (2026-08-10)

R16 procedure: `modal app stop chike-inference --yes` (verified `stopped`, then the new app
`deployed`, 0 tasks), redeploy, then the same six probes run **before** and **after** and
compared. `chike/` is mounted into the image, so this needed a deploy to reach production.

| probe | direction | result |
|---|---|---|
| **pos_th19** | POSITIVE | **CHANGED, as intended.** Before: *"…SDL ni asilimia 3.5 ya jumla ya mishahara, **sawa na TZS 210,000**…"* above a working of TZS 17,500. After: **the body is gone**, `SDL = 3.5% × TZS 500,000 = TZS 17,500` stands alone |
| neg_a_nssf_500k | FALSE-POSITIVE side | unchanged — correct split body survives |
| neg_a_nssf_1m | FALSE-POSITIVE side | unchanged — correct split body survives |
| **neg_a_paye_bands** | FALSE-POSITIVE side | unchanged — the richest colon-bearing body live (`Band 1 (0–270,000): TZS 0`, three `× rate% =` steps) is **not** newly blanked |
| neg_b_paye / neg_b_sdl | untouched | byte-identical |
| neg_c_ooc | CONTAINER-PATH-1 | refusal intact — the container loaded its config, not the 39-phrase fallback |

**Exactly one of seven replies changed, and it is the one the fix was for.** Artifact:
`eval/results/dfid1_live_check.json`.

**One limitation, stated rather than implied.** The false-positive-clearing direction — three
of the five measured changes, the larger half of the defect — is verified **offline on the
stored bodies, not live.** Current generations do not emit the colon-total shape for those
questions, so the live negatives can only establish that nothing NEW is being blanked. Four
candidate phrasings were tried to elicit one; none reproduced it. The offline evidence stands
on round-trip-verified recovered bodies, but it is a weaker link in the chain than the positive
case and is recorded as such.

---

## 👻 THE PHANTOM TZS 26,000 RELIEF IS PARAMETRIC — measured, and it overrides an in-context correction (2026-08-10)

Logged on its own because it is evidence about the **training data**, not about any guard, and
it should be known before anyone plans the next adapter version.

CLAUDE.md §11 is explicit: *"No separate personal relief deduction in Tanzania. The 0% Band 1
(first TZS 270,000/month) IS the effective tax-free threshold. Any pair mentioning 'TZS 26,000
personal relief' is WRONG."* The locked fact `paye_personal_relief` says the same and carries
eleven `wrong_patterns` for it. The model keeps producing it anyway.

### Counted, not anecdotal

Over **2,265 distinct stored model generations**:

| | n |
|---|---|
| answers that SUBTRACT or name it as a deduction — the defect | **6** |
| answers that DENY it — the system working | ~~0~~ **1** (corrected 2026-08-11) |
| other incidental mentions of 26,000 | 3 |

Six sightings across three artifacts, three different question shapes, and **one of them is
today's live production answer**. `eval/results/phantom_relief_26k_prevalence.json`.

> **CORRECTION (2026-08-11) — "zero corrections, ever" was wrong, and the true number makes the
> argument STRONGER, not weaker.** The `CORRECTIVE` detector had no `si X wala Y` construction, so
> it miscounted a real denial as an incidental mention — an instrument under-reading its own
> subject, the same class this project has now caught five times. The denial is **eval_230**:
>
> Q: *"Punguzo la kodi ya kibinafsi (personal relief) la PAYE… ni TZS ngapi kwa mwezi?"*
> A: *"**Hakuna** punguzo tofauti la 'personal relief' … **si TZS 26,000 wala TZS 27,000.**"*
>
> **The model has the fact. Asked directly, it states it correctly.** What it does not do is
> APPLY it: all six assertive sightings are inside computations, and the single correction
> appears only where the relief is the SUBJECT of the question. So the defect is not a missing
> fact, and not purely a retrieval failure — it is a fact that is inert on the compute path.
> That is a sharper claim than the original entry made, and a more specific thing to hunt in the
> SFT set. Re-measured over 2,314 generations: `scratch/relief_26k_evidence.json`.

Shapes it has taken, each needing a different guard to catch it:
- `PAYE = 8% × TZS 800,000 − TZS 26,000 = TZS 64,000` — inside a cross-levy enumeration (eval_320)
- `Jumla = TZS 172,000. Punguzo la kibinafsi TZS 26,000. PAYE inayolipwa = TZS 146,000.`
- `Jumla kabla ya punguzo = TZS 78,000 … PAYE inayolipwa = TZS 78,000 − TZS 26,000 = TZS 52,000` — live now
- and, worse, **volunteered as a correction**: *"kuna makosa … inakosea kutozingatia punguzo la
  kibinafsi la TZS 26,000"* — the model criticising a CORRECT answer for omitting the phantom

### 🔴 THE SEVENTH SHAPE (2026-08-11) — the first that NO locked pattern can see, and the strongest single item for the next adapter

Found by the D-FIDELITY-3 canaries, live in production, identical before and after that deploy:

> Q: *"Je kuna punguzo la kibinafsi la TZS 26,000 kwenye PAYE?"*
> A: *"Hapana — hakuna punguzo la kibinafsi la TZS 26,000… **Punguzo la kibinafsi ni TZS 270,000
> tu (TZS 26,000 × 10).**"* — appended working: *"PAYE = TZS 0 (mshahara TZS 26,000 uko ndani ya
> bendi ya 0%)"*

Three separate failures in one answer, and the order of them matters:

1. It **denies the TZS 26,000 relief correctly** — the eval_230 behaviour, reproduced live. The
   fact is there.
2. It then **invents a TZS 270,000 personal relief**, with arithmetic that does not even hold
   (26,000 × 10 = 260,000, not 270,000). CLAUDE.md §11 is explicit that **no personal relief
   exists at all**: TZS 270,000 is the 0% band ceiling, not a deduction. So the model has
   correctly rejected the false figure and kept the false *concept*, then refilled it from the
   nearest number in the neighbourhood.
3. The engine extracted **TZS 26,000 as a SALARY** and computed PAYE on it — a question about a
   deduction routed to the compute path, so the deterministic working endorses the answer.

**Why this one outranks the other six.** All eleven `wrong_patterns` on `paye_personal_relief`
are anchored on the *figure* 26/27,000 and its vocabulary. This answer contains 26,000 only
inside a **correct denial**, and carries the defect on a figure — 270,000 — that appears in the
locked facts as a **legitimate** number. Any pattern list keyed on the wrong figure is blind to
it, and any list keyed on 270,000 would fire on every correct answer about Band 1. The runtime
`wrong_patterns` check proposed below would score **0 of 1** here, which is worth knowing before
anyone builds it expecting coverage.

It is the cleanest evidence yet that the concept — *PAYE has a personal relief* — is in the
weights independently of the number attached to it. A guard can only ever catch the number.
**This is the item to hunt in the SFT set for the next adapter version.**

### The part that settles it: it overrides an on-point fact that was already in the prompt

The obvious counter-hypothesis is that the correction never reaches the model. Half true, and
the half that is true is a separate defect:

**The denial fact never retrieves.** Entry [2] (`paye personal relief: Tanzania has NO separate
PAYE personal relief deduction…`) ranks **#64** for the live defect question, **#81** for the
eval_320 shape, **#23** for a plain PAYE question — and **#18 when asked about it directly**
(*"Je kuna punguzo la kibinafsi la TZS 26,000 kwenye PAYE?"*). It is another long English
`key: value` fact, unreachable by the Swahili vocabulary of the questions that need it —
**the same reachability shape as GN 605A**, in a second domain, which is now the third
confirmed instance of that class.

**But the model overrode a rank-1 fact that told it not to.** For all four of those queries the
top-retrieved entry is [214]: *"PAYE kwa mshahara wa TZS 800,000 ni TZS 78,000 kamili. **Hii ni
jibu la mwisho, si mahesabu ya ziada.**"* — "this is the final answer, not extra arithmetic",
naming the exact salary and the exact correct figure. It was in the prompt, at rank 1, and the
model still emitted `78,000 − 26,000 = 52,000`.

An in-context, on-point, rank-1 instruction losing to the prior is what parametric means. **This
is in the fine-tune.** Guards can catch each new shape it takes — D-FIDELITY-2 caught the
enumeration form, and the intermediate-figure hole is why the live form still gets through — but
every catch is reactive, one shape at a time, and the supply of shapes is the model's.

### What follows

- **For the next adapter version:** treat this as a training-data defect to hunt in the SFT set,
  not a guard to widen. The 11 `wrong_patterns` in `paye_personal_relief` run over *training
  pairs* at build time; **nothing applies them to model output**, which is why six live answers
  carry a pattern the repo has explicitly banned since June.
- **Cheap partial mitigation, not a fix:** make the denial retrievable (Swahili-first,
  subject-keyed, the GN 605A treatment). Worth doing on reachability grounds alone. It should
  NOT be expected to close this — entry [214] shows an on-point fact already losing.
- **Related:** the `wrong_patterns` machinery being build-time-only is itself worth an item. It
  is a corpus of known-wrong assertions that no runtime check consults.

---

## 🔺 QUEUE — the intermediate-figure hole is promoted above the other guard items (2026-08-10)

Founder call, recorded with the reasoning. Of the open guard items, **"presence of the correct
figure anywhere clears the body"** ranks first: an answer whose FINAL figure is wrong passes
because the right number appeared mid-working, and **it is rendered directly above the
deterministic working**, so the layer whose whole purpose is arithmetic authority is standing
behind a wrong conclusion. A body that is merely unchecked carries no such endorsement. Live
reproduction: the TZS 52,000 PAYE answer above.

Order among the guard items: **intermediate-figure hole → D-FIDELITY-1 attribution follow-ups →
the rest.** It sits behind the founder-ordered main queue (minimum wage → VAT/EFD route), not
ahead of it.

---

## 🧮 "PRESENCE OF THE CORRECT FIGURE" IS TOO WEAK WHEN THE FINAL FIGURE IS WRONG (2026-08-10)

Found while hunting for a live colon-total body, so it is incidental to D-FIDELITY-1 — but it
is a hole in the same guard and it is live. Asked to show PAYE step by step for TZS 800,000,
production answers:

> *…Band 4 (760,001–800,000): 40,000 × 25% = TZS 10,000. Jumla kabla ya punguzo = TZS 78,000.
> **Punguzo la kibinafsi = TZS 26,000. PAYE inayolipwa = TZS 78,000 − TZS 26,000 = TZS 52,000.***

Two things wrong at once. **TZS 26,000 "personal relief" does not exist in Tanzania** —
CLAUDE.md §11 names it explicitly as a wrong pattern; the 0% first band IS the relief. And the
**final asserted figure, TZS 52,000, is wrong**; the engine says 78,000.

Neither guard fires, before or after the widening, and the reason is by design: the own-levy
rule is `amount not in results and bool(results)` — *presence of the correct figure anywhere*
clears the body. TZS 78,000 does appear, as an intermediate ("jumla kabla ya punguzo"), so the
body passes while its **conclusion** is wrong. That robustness was chosen deliberately, to stop
band bases and net-pay extras false-flagging (eval_092/191/360/395), and it is the right default
— but it cannot distinguish "restates the correct figure and concludes with it" from "passes
through the correct figure on the way to a wrong one".

The shape of a fix is a **last-asserted-figure** check: the body's FINAL assertion should have
to be authoritative, not merely present somewhere. That is a real semantic change with its own
false-positive surface (net-pay answers legitimately end on take-home, not on the levy), so it
needs its own investigation and its own probe set, not a bolt-on here.

> **RESOLVED 2026-08-11 — and the last-asserted-figure check was REJECTED.** The investigation
> ran; the guessed false-positive surface was real and larger than guessed (it breaks eval_191
> and eval_395, two of the four protected rows). See "cue-based narrowing relocates the failure"
> and "D-FIDELITY-3 shipped as a deliberately partial guard" above. The live TZS 52,000 answer
> below is now caught; the paraphrase family is not.

Logged as its own item. Note it also gives the phantom TZS 26,000 relief a live reproduction,
which the locked-facts `wrong_patterns` for PAYE should be catching and currently are not
applied to model output at all — they run over training pairs, not over answers.

---

## 🪞 A PROBE THAT PASSED FOR THE WRONG REASON — the fourth instrument this project has caught lying (2026-08-10)

R17 probe `na_06` asserted that `Band 2 (8%): TZS 250,000 × 8% = TZS 20,000` must not yield
250,000 as a result. It passed. **250,000 was indeed absent — because the pattern had extracted
25,000 instead.**

The operand exclusion was written as `([\d,]+)(?!\s*[operator])`. Regex backtracking defeats it:
the lookahead fails after `250,000` (next is ` ×`), so the engine gives back a digit and retries
`250,00`, whose next character is `0` — not an operator — and matches. **The operand was not
excluded, it was silently renumbered.** Every probe still went green, and the pattern would have
shipped with a class of figures being read as arbitrary wrong numbers.

Found by a **two-line sanity check** printing what the pattern extracted from five strings — not
by the 23-probe suite built specifically to test it. Fixed with a digit boundary that pins the
run to full length before the operand test, and pinned by
`test_operand_exclusion_survives_backtracking`, whose docstring carries the mechanism.

**This is now the fourth instrument this project has caught lying** (two more followed the same
day — #5 in the minimum-wage cycle, #6 in the VAT/EFD one, both entries above)**, and the
pattern in how:**

| # | instrument | how it lied | what caught it |
|---|---|---|---|
| 1 | `recover()` v1 | discarded everything after the last working | a live canary reply that was byte-correct |
| 2 | `recover()` v2 | under-removed multi-paragraph bodies; **passed its own self-check**, because the check compared verdicts and the defect was in extent | a row that had already PASSED stopped matching live |
| 3 | direction detector (SAFETY-3) | scored a whole answer against one threshold, crediting an SDL verdict to a VAT question | per-threshold attribution, added after the counts looked wrong |
| 4 | `na_06` (this one) | green because backtracking renumbered the thing it was testing | a two-line print of the pattern's actual output |
| 5 | probe `mw_15` (added 2026-08-10, minimum wage) | asserted the resolver's cross-sector conflict check, but was authored with `na pia` — a decomposition connector — so the clause was **split into two sub-questions before the resolver ever saw two sectors**. The check it existed to test was unreachable; it passed on a different code path | reading the decomposed sub-questions while debugging something else. A unit test of `resolve()` cannot see this: the resolver was always correct, the probe never got to it |
| 6 | VAT orchestrator harness (2026-08-10) | reported 25-on-path / 0 failures for a build where **three rows silently clarified instead of answering** — it asserted route, model calls and polarity, i.e. **the checkpoint immediately before the stage that broke** | widening the harness to assert each probe's `truth` — the outcome the user gets. Same failure shape as MEASUREMENT-GAP-1, one stage further down the pipeline |
| 7 | D-FIDELITY-3 BEFORE canary (2026-08-11) — **NEAR-MISS, caught before it produced a number** | asked a **paraphrase** of the question that produced the defect, got a clean answer, and would have reported `INCONCLUSIVE — the model did not reproduce the guarded shape` while the defect was reproducible on every run of the verbatim question. Greedy decoding is what makes a live check exact and what makes it brittle in the input: a different prompt is a different deterministic trajectory | reading the committed 2026-08-10 artifact for the exact question string instead of retyping it. Full entry above |

| 8 | `na je` live canary (2026-08-11) — **NEAR-MISS, caught before it reported** | its "was the second ask answered" marker was the phrase from the QUESTION (`kima cha chini`); production answers with `kiwango cha chini`, so a correctly answered row scored as a DROPPED ask — and the paired leak check, splitting on the same absent phrase, read the whole reply and flagged a figure from the other half as a preamble leak | reading the replies instead of the flags. Both were re-derived from the stored artifacts without re-asking |
| **9** | **Wappfly `GET /api/me` (2026-08-14) — the first that was a VENDOR's, not ours** | I recommended `/api/me` as "the decisive one-line test" of token validity, on the strength of Wappfly's docs saying every endpoint takes the same `X-API-Token`. **It 401s on a token that sends successfully** — `POST /api/messages/send` with the identical token returns `{"sent":true,…}`. ⚠️ **CORRECTED 2026-08-14: this quirk is real and worth keeping, but it did NOT cause the delivery outage.** The cause was a plain value mismatch in the Modal secret (66 chars stored vs the 64-char working token). `/api/me` made it worse in the way a broken instrument does — it supplied a *plausible wrong explanation* that redirected two rotations and a session re-pair at the vendor, and nearly got them blamed. Recorded as an aggravating factor, not a root cause | the founder testing the SEND endpoint directly instead of trusting the check I proposed |

| **10** | **A1 live canary (2026-08-14) — NOT a near-miss: it printed `NOT VERIFIED — REVERT` on a correct change** | its pass condition was `'10,000' in reply` — *did edge_p05 ANSWER* — while the agreed revert trigger was *did it compute on the 20,000,000 DISTRACTOR*. Between "answered" and "took the distractor" sits **clarification**, the safe outcome this path is built to produce, which the negation reclassified as failure. Acting on the flag would have reverted a fix that had just corrected a 20× error | reading the replies instead of the flags (again). Verdict re-derived from the stored artifacts without re-asking. **Full entry above** |

**#9 extends the rule past our own code.** The first eight were instruments this project built,
and the lesson was "an instrument cannot be its own control." #9 was a *vendor's* instrument,
taken on the authority of the vendor's own documentation, and it was wrong in the direction that
costs the most: it reported a failure that did not exist, so every remedy applied was aimed at a
healthy system. **Verify the instrument before trusting its verdict applies to third-party
diagnostics too — especially a diagnostic whose only evidence is that the docs say it works.**
The cheap check was available the whole time: exercise the endpoint you actually depend on.

⚠️ **OPERATIONAL RULE — never health-check Wappfly auth with `GET /api/me`.** It returns 401 for
valid tokens. Any monitoring, any preflight, any "is the token still good" check must use a real
`POST /api/messages/send`. Recorded here before someone builds monitoring on the read endpoint
and spends the same two days.

**Not one was caught by itself.** Each was caught by a different instrument, a live run, or an
ad-hoc check — never by the suite it belonged to. The corollary is not "write better probes",
it is: **an instrument cannot be its own control.** Before trusting a green board, print what the
mechanism actually produced on a handful of inputs and read it. That is the cheapest check in
this repo and it has now found what the expensive ones missed, twice.

---

## 🫥 A MEASUREMENT THAT ERASES ITSELF WHEN THE FIX LANDS (2026-08-10)

The sweep compared **live `chike.fidelity`** against a widened set. The moment the widening
landed in `chike.fidelity`, before and after became the same object and the sweep reported
**0 bodies affected** — the number that justified the change, gone, replaced by a confident zero.

Caught by re-running the sweep after the edit as a matter of routine and noticing the headline
had changed in the wrong direction.

**Rule: a before/after instrument must own its "before".** The pre-fix patterns are now frozen
into `scratch/dfid1_sweep.py` as `OLD_RESULT` / `OLD_ATTRIBUTED` with their own re-implemented
guard functions, so re-running the sweep at any future commit still reproduces the 5-of-118 that
authorised this change. An instrument that reads the current code for its baseline is measuring
nothing the moment the code moves.

## 🧱 NEVER-GUESS CANNOT BE A SENTENCE IN THE INDEX — it has to be infrastructure (2026-08-10)

**Promoted out of the th_16 write-up because it is an architectural claim, it now has measurement
behind it, and it generalises well past minimum wage.**

Candidate C4 was a locked fact that instructed the model, in Swahili, in capitals, to decline:

> *"**SINA UHAKIKA** wa kujibu ndiyo au hapana kwa kiasi mahususi… **Usiseme mshahara ni halali au
> si halali bila kuthibitisha sekta** kamili."*

It was retrieved on 6 of 8 probes. **The model adjudicated anyway** — it answered "ni halali" or
"ni chini ya kima cha chini" on every one of them, sometimes softening with *"thibitisha na
MLYWF"* while still delivering the verdict the fact told it not to give. Declining is not a
behaviour a retrieved fact can install.

> **A refusal must be a code path that runs INSTEAD of generation, not an instruction the
> generation is asked to obey.**

This is why **R11** works: the OOC classifier intercepts before the model is called, and its
docstring already says *"This cannot be broken by training — it is infrastructure not behavior."*
C4 is the same claim from the other direction, measured: an instruction the model is free to
override **is** overridden, and it is overridden precisely on the hard cases where the refusal
mattered.

Direct consequence for the approved **VAT/EFD route**: the never-guess branch — *when the period
cannot be extracted, decline and state the rule conditionally* — must be implemented in the
router/engine, as a path that returns a clarification without calling the model. Writing it into
`locked_facts.json` or the system prompt would produce the C4 result: a fact that reads correctly,
retrieves correctly, verifies correctly, and does nothing.

---

## ⛔ th_16 STAYS LIVE — the class fix is the only correct fix (2026-08-10)

**Recorded explicitly so this does not read as an oversight.** th_16 — production telling an
employer that paying *above* the minimum wage is illegal — **remains live and unfixed by
decision, on evidence.** A same-day patch was tried, measured, and rejected.

### What was measured

Six candidate wordings, live against the real v15 weights via `generate_endpoint`, with throwaway
indexes and **no deploy** — the loop MEASUREMENT-GAP-1 says this class of change requires. `C0` is
attempt 1's shipped wording, kept as a fidelity control: it **reproduced the deployed answers
byte-identically**, including the th_15 inversion, so the harness is production-faithful and the
rest of the table means what it says.

| probe | C0 shipped | C1 comparison-first | C2 procedure | C3 +table | C4 decline | C5 procedure+table |
|---|---|---|---|---|---|---|
| **below_farm** 150k vs 175k → unlawful | ✗ *lawful* | ✗ | ✓ | ✗ *lawful* | ✓ | ✗ *lawful* |
| **above_farm** — th_16 itself | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **exact_farm** 175k → lawful | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| **sector_below** 180k vs 195k → unlawful | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| **sector_above** 250k vs 200k → lawful | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **generic_below** 160k → unlawful | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |
| semantics / no-max | ✓ ✓ | ✓ ✓ | ✓ ✓ | ✓ ✓ | ✓ ✓ | ✓ ✓ |
| **total** | **6/8** | 4/8 | **6/8** | 4/8 | 5/8 | **6/8** |

Controls 3/3 on every candidate — the injected-context noise flagged in attempt 1 never caused a
failure. **No candidate reaches 7/8, and every one has at least one wrong-direction failure.**
Which probe fails moves almost independently of the wording: `below_farm` is right on C2 and C4
and wrong on C0, C3 and C5.

### The two results that settle it

**C3 carried the correct floor, recited it, and inverted the comparison anyway:**

> *"kima cha chini cha sekta ya baa na migahawa ni **TZS 195,000** kwa mwezi. **TZS 180,000 ni
> zaidi ya kima cha chini**, hivyo ni halali."*

**C5 — one sentence, both numbers:**

> *"Kima cha chini cha sekta ya kilimo ni **TZS 175,000**… mshahara wa **TZS 150,000 unazidi** kima
> cha chini."*

This is SAFETY-3's VAT mechanism, reproduced on a second levy family: **the right number is in
context, recited correctly, in the sentence where it is misapplied.** Supplying the number does
not produce the comparison. That is now measured twice, in two domains, and it is the argument for
the compute route in its strongest available form.

### Why nothing was shipped: the replacement was more dangerous than the original

**Four of six candidates independently fabricated a maximum wage:**

> *"kiwango cha juu kabisa kinachoruhusiwa ni **TZS 765,900** kwa mwezi. Malipo ya zaidi ya hapo
> **yanaweza kuadhibiwa**."*

The live defect invents a phrase that describes nothing (*kiwango cha juu cha chini*). The
candidate fix asserts **a real figure from the gazette as a legal ceiling** — 765,900 is the
genuine energy-sector *floor*. A user can act on that; they cannot act on a nonsense phrase. It
appears whenever the candidate is not retrieved and the model falls back to parametric memory,
which no wording controls.

**Founder decision: leave the known defect live rather than ship a more actionable one.** The
class fix is the only correct fix.

### Carried forward to the minimum-wage investigation — do not redo it

- **The retrieval finding stands and is necessary but not sufficient.** GN 605A is unreachable:
  **0 of 7** realistic Swahili queries retrieved any GN 605A fact, best rank **#22–#52**, against
  **7 of 8** other domains at rank 1. A route cannot compare against a floor it cannot find, so
  the reachability work is a prerequisite to the route, not an alternative to it.
- **Primary-source verification is done** and needs no repeat: the official gazette from
  **kazi.go.tz** (Tier 1A), para 4(3) quoted verbatim, para 4(4), para 6, para 7 revoking **GN No.
  687 of 2022**, and the entire Second Schedule checked against every locked sector rate — no
  corrections needed. Recoverable in full from `2adbd4c`.
- **Scope: a genuine `minimum_wage` computation type behind the rules engine, with sector
  resolution.** That is what the evidence points at. It is the hardest member of the
  threshold-comparison class — VAT and EFD are single scalars; this one has to resolve 16 sectors
  and 46 sub-sectors before it can compare, and item 16 of the First Schedule ("any other sector
  or area not specified") gives it a defined default of TZS 175,000 to fall back on.
- **The never-guess branch must be infrastructure**, per the entry above: when the sector cannot
  be resolved, the engine declines and the answer states the rule conditionally — as a code path,
  not as a fact.
- **The probe corpus is ready to reuse**: 8 targets + 22 authored R17 displacement probes in
  `2adbd4c`, plus the six-candidate live matrix above and the harness that produced it
  (`scratch/mw_attempt2.py`), which needs only a new candidate list to re-run.

## 🧭 MEASUREMENT-GAP-1 — fact-in-prompt is not fact-applied, and every offline instrument here measures the first (2026-08-10)

**The most generalisable thing this cycle produced.** Written as its own entry because it is not
about minimum wage, VAT, or any one fact — it is about what this repo's tooling can and cannot
see, and it has now been hit from both directions one work item apart.

### The claim

> Every offline instrument in this repo measures **whether a fact reaches the prompt**. None
> measures **whether the model applies it correctly**. A completely green offline board is
> therefore compatible with a live inversion — and has now produced one.

### The two sides of the same gap

| | SAFETY-3 (2026-08-09) | th_16 attempt 1 (2026-08-10) |
|---|---|---|
| what retrieval did | **worked** — RAG carried the VAT threshold | **worked** — the floor fact was retrieved on both arms |
| what the model did | recited `200,000,000` correctly **in the sentence it misapplied** | read the lead clause and generalised "lawful" to a wage *below* the floor |
| what the offline board said | n/a — found by live probing | 3/3 self-retrieval, 7/8 targets, 0 evictions / 30 probes, 625 tests |
| the actual defect | comparison, in free generation | application, in free generation |

SAFETY-3 concluded the fix was a **deterministic route** precisely because the fact was present
and the reasoning over it was wrong. th_16 attempt 1 then tried to fix a reasoning failure **with
a fact**, verified the fact arrived, and shipped. The gap did not move; only the direction of
approach did.

### Why the instruments cannot close it themselves

Retrieval is cheap, deterministic, and reproducible offline: `numpy` and a cached embedder, no
GPU, sub-second. Generation is none of those things locally — the 8B adapter needs the Modal GPU.
So the tooling grew where it was cheap to grow, and the boundary of what is measured settled
exactly at the boundary of what is convenient to measure. That is not a criticism of any one
instrument; each is correct about what it reports. It is a statement about where the reported
numbers stop meaning what they appear to mean.

The specific trap: **"7/8 targets served" reads like "7/8 answers correct."** It is not. It means
seven of eight prompts contained the fact. What the model then said about it was, at that point,
entirely unmeasured.

### The rule

> **Any fix whose success depends on how the model REASONS over a fact needs a live generation
> check inside the loop, not after it.**

"Inside the loop" is the operative part. Attempt 1 *did* run a live check — R16 required it, it
ran, and it caught the regression in minutes. But it ran **after** commit and deploy, so its only
available outcome was a rollback. The same check, run against candidate wordings before anything
was written to disk, is a wording-selection tool instead of an incident.

This is affordable and there is no excuse for skipping it: `generate_endpoint` takes a finished
prompt and returns the completion, so a candidate fact can be put in front of the **real weights
with no deploy and no risk to production**, by building the prompt locally and binding a
throwaway index. Cost is seconds per probe.

### Which changes need it

Needs a live check in the loop — the model reasons over the content:

- a fact whose value must be **compared** against a user's number (thresholds, floors, bands)
- a fact stating **semantics or a rule** rather than a value ("X is lawful", "A is not B")
- any **disambiguation** fact whose job is to stop a conflation
- prompt, system-prompt or generation-parameter changes

Retrieval benching alone remains sufficient — the model only has to repeat the content:

- a **value correction** to a fact already retrieved and already recited correctly
- a pure **reachability** change with no semantic content

### Corollary for R15

R15's verification steps are all retrieval-shaped: self-retrieval plus critical known-failure
queries. That is necessary and it is not sufficient. **R15 should gain a step: for any fact whose
content is a rule rather than a value, verify a live generation before the index is committed.**

---

## ⚠️ INSTRUMENT-PARITY-1 — a near-miss: the instruments were built against the library default, not the deployed path (2026-08-10)

Logged as a near-miss, not a defect: the conclusion survived. It survived by luck.

**What happened.** Six instruments built for th_16 called `chike.retrieval.Retriever` — the
**two-arm hybrid**: cosine top-3, plus one extra fact recovered from a number-stripped second arm
on any numeric query. Production does not use it. `chike-inference/modal_app.py` builds the
Orchestrator with `retriever=self.retrieve_facts`, its **own single-arm method**, and
`orchestrator._answer_fact` calls it as `self.retriever(sq.text)` with no `top_k` — so a user gets
a plain top-3 and nothing else. The comment at that line says single-arm is deliberate.

**Why it mattered here specifically.** Every query in the bench carries a TZS amount, so every one
of them is a numeric query, so the extra slot was live in the instrument on every single
measurement — and that slot is exactly where a marginal fix would sit. "It's in the injected set"
could have been true only of a slot production does not have.

**How it was caught.** By reading the deploy path before deploying, not by any check. Re-running
the acceptance criteria under production's own math (normalize, cosine, top-3, stop) gave the same
result — 7/8 targets, 0 evictions — so nothing was invalidated.

**What made the wrong retriever look like the right one.** The `edge20_v16_run1_prefix_67e9e4c`
artifact records **4** retrieved facts for its row 17, which matches two-arm and not single-arm.
That artifact was produced by `scratch/edge20_v16.py`, a LOCAL harness driving
`Orchestrator(backend=LocalAdapter)` with the **default** retriever — not by the endpoint. A stored
artifact from a local harness was read as evidence about production. (Same harness also leaves
`ooc_phrases` / `system_prompt` defaulted, where production passes them explicitly — the
CONTAINER-PATH-1 class again, on the measurement side rather than the deployment side.)

**The lesson.**

> **Offline instruments must be built against the DEPLOYED path, not the library default — and a
> stored artifact is evidence about the harness that produced it, not about production, until its
> harness is checked.**

The regression test now parametrizes over both arms, so the two paths cannot silently diverge
again in this area. The general audit — every scratch instrument that assumes a default where
production passes an explicit — is not done, and belongs with the standing container-path audit.

## ⛔ th_16 ATTEMPT 1 — SHIPPED, BROKE ITS OWN CONTROL, ROLLED BACK (2026-08-10)

**Production is back in its known state** (`70a2b7f`, deployed and verified live). th_16 is still
open. The investigation and the primary-source verification below all stand; only the fact's
*wording* failed, and it failed at a stage no instrument in this repo can see.

### What was shipped, and what it did

| probe | before | after the fix | verdict |
|---|---|---|---|
| **th_16** — TZS 200,000 to a farm worker | *"malipo hayo yanazidi **kiwango cha juu cha chini**… Malipo ya ziada juu ya hapo ni kinyume cha sheria"* | *"**Ndiyo, hilo ni halali kabisa.** … TZS 200,000 unazidi kima cha chini, na ni halali."* | **fixed** |
| **th_15** — TZS 150,000 to a farm worker | *"Mshahara wa TZS 150,000 **unakiuka sheria**"* — correct | *"**Ndiyo, hilo ni halali kabisa** … malipo ya TZS 150,000 … **ni sahihi**."* | **BROKE** |
| edge20 row 17 — TZS 160,000 | right conclusion, inverted reason | right conclusion, right reason | fixed |
| 10 unrelated payroll negatives | — | unchanged | ok |

**th_15 was correct before and is wrong after.** The system told an employer that paying *below*
the minimum wage is fine. That is not a smaller defect than the one being fixed — it is the same
defect pointing the other way, at a worker's expense. Traded one wrong answer for another, so it
was rolled back rather than left live while iterating.

### Why every offline check passed anyway

Retrieval was never the failing stage. The fact was retrieved correctly on **both** arms for
th_15. The model read its lead clause — *"kulipa mshahara MKUBWA kuliko kima cha chini ni halali
kabisa"* — and generalised it to "the wage is lawful", never reaching the converse stated two
sentences later in the same fact.

**Nothing in this repo's offline toolchain runs generation.** Every instrument built for this
item measured *which facts reach the prompt*, and all of them were green: 3/3 self-retrieval,
7/8 targets, 0 evictions across 30 probes, 625 tests passing, verified on production's own
single-arm top-3 as well as the two-arm hybrid. **Fact-in-prompt is not fact-applied**, and this
is the second time in two work items that the gap between them is where the defect lived —
SAFETY-3's root cause was the same shape (RAG carries the VAT threshold; the model recites it
correctly in the sentence it misapplies).

**Method change for attempt 2: a live generation check belongs INSIDE the loop, not after it.**
Retrieval benching stays — it is cheap, and it is what found the actual cause — but a wording is
not a candidate until it has been asked th_15 and th_16 live.

### The one thing that worked exactly as designed

`t_below_farm`'s `guards_against` note reads *"below the floor; the fix must not flip this to
lawful."* It was authored **before** the fix existed, for a failure mode that had not happened,
in a probe set built because R17 says the corpus will not contain the forms that break you. It
is the only reason this was caught in minutes instead of by a user.

### What survives and is NOT lost in the revert

Recoverable in full from `2adbd4c`, and none of it needs redoing:

- **Primary-source verification.** The official gazette PDF from **kazi.go.tz** (Tier 1A; TanzLII
  403s behind Cloudflare from this network) — *Special Supplement No. 9 to Special Gazette No. 6
  Vol. 106, 13 Oct 2025*. **Paragraph 4(3):** *"The minimum wage rates specified in the Second
  Schedule shall be regarded as the minimum wage payable to employee in the respective sector or
  area, **and an employer may pay such employee an amount above the minimum wage prescribed** in
  respective sector or area."* Plus para 4(4), para 6, para 7 (revoking **GN No. 687 of 2022** by
  name), and the whole Second Schedule. Every sector rate already locked was checked against the
  gazette — **no corrections needed**; "16 sectors, 46 sub-sectors" reconciles exactly (46
  lettered sub-sectors + 4 unlettered = 50 rate rows).
- **The root-cause finding.** Realistic Swahili minimum-wage queries retrieved **0 of 7** GN 605A
  facts, best rank **#22–#52**, against **7 of 8** other domains at rank 1. GN 605A was in the
  index only as long English `key: value` text keyed on the notice number — reachable by naming
  it, and by nothing a user says. The offline reproduction is exact: its top-3 for the edge20
  row-17 question matched that run's recorded `facts_retrieved` **in the same order**.
- **The probe corpus** (8 targets + 22 authored R17 displacement probes) and its regression test.
- **The `wrong_patterns`**, swept over **149,983 stored strings** with 0 false positives, then
  given authored probes for the lawful phrasings they could plausibly catch.
- **R15's Kaggle round-trip is no longer required.** e5-base is in the local HF cache, and
  re-embedding the 217 committed texts locally reproduced the live index at **cosine 1.000000 on
  every fact**. The rule's stated reason — *"local network blocks e5-base download"* — no longer
  holds. The rule should be amended; its *verification* steps stay, and this cycle is the
  argument for adding a live generation step to them.

### A retriever divergence found by reading the deploy path

Worth recording separately because it nearly invalidated the whole bench. Instruments 4–9 used
`chike.retrieval.Retriever` — the **two-arm** hybrid (top-3 plus one fact from a number-stripped
second arm). Production does not use it: `modal_app.py` builds the Orchestrator with
`retriever=self.retrieve_facts`, its own **single-arm** method, called with no `top_k`, so users
get a plain top-3. Every query in this bench is numeric, so the extra slot is exactly where a fix
could have been hiding. Re-run under single-arm: **same result**, 7/8 and 0 evictions — the
conclusion held, but it was luck that it did. The regression test now parametrizes over both.

The edge20 artifact recording **4** retrieved facts is what made the wrong retriever look like the
right one: that harness runs the local two-arm path, not the endpoint.

### Still open, unchanged by this attempt

- **t_hotel** — *"Nina mfanyakazi wa hoteli namlipa TZS 400,000 kwa mwezi, je ni sawa?"* needs the
  hotel floor (375,000 / 225,000 / 195,000 by star rating). Sector-rate reachability is part of
  the separate minimum-wage investigation.
- **A fabricated sector floor.** Live, the driver probe answered *"kima cha chini cha sekta yako …
  ni TZS 275,000"* — no such floor exists; 275,060 is the pre-GN 605A national **average**. The
  conclusion (lawful) was right and the number invented, on the fixed index and presumably on the
  current one too.
- **Pre-existing retrieval gaps** — `p_05` / `p_09` / `p_11` (PAYE penalty, deadline, "can I pay
  without deducting") and `p_16` (is the 2022 order still in force) retrieved no relevant fact on
  the OLD index either. Evidence that retrieval reachability is wider than minimum wage. Own item.
- **`p_20`**, live: *"malipo ya mishahara lazima yawe kwa njia rasmi ya benki … fedha taslimu ni
  marufuku"* — fabricated, and no baseline exists to say whether this attempt caused it. Logged.

## 🚀 v16 CUTOVER — LIVE IN PRODUCTION (2026-08-09)

**Deployed commit: `ec9cbb3`** (`config(pipeline): v16 — the cutover flip`). Endpoint
`prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run`. Second of the two deliberate
deploys; the first was the credential rotation on v15, so **this deploy carried exactly one
change**.

### What authorised it — both preconditions, measured, not asserted

| precondition | result | source |
|---|---|---|
| ADR 0001 §10 bar: v16 ≥ v15 on raw **and** reliable | **raw +3.6, reliable +1.6** — PASS | `gate_phase_d_paired_1476caa.json`, sha256-verified, 46/46 recomputed checks |
| defective clarification rate ≤5% | **2.9%** (3/102) — PASS | same artifact |

Supporting, from the same run: compute **+13.7 raw / +8.7 reliable**, 19 real gains / 1 false,
6 regressions all of them v16 clarifications, judge range **+5.1 to +7.8 sign-stable**, fact
path **byte-identical on 281 of 282** non-compute scored rows. The headline the decision rested
on — *no row where v16 states a wrong number that v15 stated right* — holds, with the eval_318
correction recorded in the `1476caa` entry.

### Live verification — R16 procedure, judged against pre-registration

`modal app stop chike-inference --yes` first (verified `stopped`, 0 tasks, via `modal app list`
— the command exits 0 silently), then `modal deploy`, then
`scratch/cutover_verify.py` comparing each reply **byte-for-byte** against
`scratch/canary_expected_v16.json`, which was written **before** the cutover.

| # | canary | live sha | result |
|---|---|---|---|
| 1 | **CONTAINER-PATH-1 / OOC** (`kodi ya majengo`, config-only phrase) | `a71619b1` | **PASS** — refuses, and byte-identical to v15's refusal |
| 2 | eval_115 — fact negative case | `5b46098b` | **PASS** — byte-identical to v15 |
| 3 | eval_320 — cross-levy canary | `66aac953` | **PASS** — guard blanked the nssf and wcf bodies |
| 4 | eval_318 — cross-levy canary | `6a314afc` | production correct; **the pre-registered string was wrong** (below) |
| 5 | eval_323 — changed compute row | `3f3fc316` | **PASS** |
| 6 | eval_280 — changed compute row | `57e36a8c` | **PASS** |

**Canary 1 ran first deliberately** and is the most important result: v16 moved phrase-list
loading from `run()` into `Orchestrator`, so a config-only OOC phrase still refusing is the only
available proof that the container reads the baked `chike_config.json` and serves **107 phrases,
not the 39-phrase hardcoded fallback**. CONTAINER-PATH-1 is closed in production, not just in
the source.

**The D-FIDELITY-2 guard fired live on a real user-facing answer, first time out.** eval_318's
contradicting `TZS 110,000` NSSF figure is gone from the live reply; the correct `TZS 1,100,000`
remains.

### 🐛 The one deviation was in the verification harness, not in production

eval_318's live reply did not match its pre-registered string. Verified read-only, before
touching anything:

```
artifact v16 text  MINUS  the SDL body the guard should blank  ==  LIVE   →  True
```

Production produced exactly the designed output. **The expected string was malformed.**
`recover()` in `scratch/canary_expected_v16.py` reconstructs each sub-answer body as the text
*preceding its deterministic working* — so any text after the **last** working is never
captured. That trailing segment is the pooled **fact** sub-answer. eval_318 is the only canary
carrying one, which is why it is the only row affected.

Stopping on the deviation and reporting before acting was the correct call and stays the rule:
a near-miss explained after the fact is exactly what pre-registration exists to prevent.

### ✅ `recover()` FIXED and eval_318 RE-REGISTERED (2026-08-10)

Recovery now lives in **`scratch/render_recovery.py`** and **parses the `_render` grammar**
instead of slicing at landmarks. `rep.sub_answers` gives the exact part count and which parts
are compute; each compute part is `body\n<working>` or bare `<working>`, parts join with
`\n\n`. A small backtracking parse finds the unique segmentation, **reports ambiguity or
no-parse rather than guessing**, and callers assert a **round-trip invariant**: re-rendering
with nothing dropped must reproduce the stored text byte-for-byte.

**Three defects, not one — and the second fix was itself wrong.** Worth recording because the
sequence is the lesson:

| # | defect | direction | how it was caught |
|---|---|---|---|
| 1 | text after the LAST working discarded | truncation | eval_318 false FAIL at the cutover |
| 2 | `find()` anchored on a working occurring **inside a body** — eval_320's model answer contains a line character-identical to the deterministic WCF working | mis-split | only visible once #1 was fixed |
| 3 | *my first fix*: taking the body as the final `\n\n`-delimited chunk | **under-removal** — left eval_320's contradicting `SDL = TZS 28,000` / `NSSF = 160,000` / `PAYE − TZS 26,000` block in the output | eval_320 stopped matching live |

**Defect 3 is the one to remember.** The first fix passed its own self-check cleanly — a
narrow/wide verdict comparison — because narrow and wide bodies both *contained* a
contradiction, so the guard **verdict** agreed while the **extent of removal** silently
differed. An instrument that compares verdicts cannot see a defect in extent. What caught it
was re-running the corrected harness against the **recorded live replies** and noticing that a
row which had previously PASSED now disagreed. **A fix that changes a row which was already
correct is a fix that needs explaining**, and that check is now the habit.

**Verification, all three loops:**

| check | result |
|---|---|
| corrected expectations vs pre-registration | **exactly one row changed — eval_318**; the other five shas byte-identical to what was pre-registered |
| eval_318 corrected expectation, derived from the artifact + guard **without reference to the live reply** | sha `6a314afc` — **exactly the live sha** |
| full live canary re-run against the corrected file | **6/6 PASS**, every row byte-identical |
| `preflight_wiring.py` re-run with the parser | 87/87 workings byte-identical, **0 unrecoverable, 0 round-trip failures**, guard touches exactly eval_318 + eval_320 |

The `1476caa` pre-flight conclusion therefore **stands, and now stands by construction rather
than by luck**: it had compared the *set* of guard-blanked rows and never compared its
`rendered` string to `stored`, so the broken recovery was latent rather than load-bearing.
That is no longer something to rely on — the round-trip assert makes a mis-parse fail loudly.

### 🟢 Production reproduces the harness BYTE-IDENTICALLY

Before the cutover, live v15 was captured on all five canaries
(`scratch/canary_baseline_v15.json`) and matched the `1476caa` artifact's v15 arm **byte for
byte**. After the cutover, five of six rows matched their pre-registered v16 strings byte for
byte, and the sixth matched once the harness bug is accounted for.

**This is the load-bearing fact for every future artifact.** It means a Kaggle paired-gate
number is a *prediction about production*, not merely a lab result — the same weights, config,
generation params and RAG index produce the same bytes on both sides. Any future run where the
live endpoint and the artifact disagree on a canary is a real divergence and must be
investigated as one, because the null hypothesis is byte-equality.

### ↩️ ROLLBACK — a config flag flip, never a code change

1. Set `"pipeline": "v15"` in `kaggle/chike_config.json`.
2. `python -m modal app stop chike-inference --yes` — **required**; warm containers keep serving
   the baked v16 config, and this command prompts and aborts silently without `--yes`.
3. `python -m modal deploy chike-inference/modal_app.py`.
4. Verify per R16 with a request whose behaviour differs between arms — a compute row such as
   eval_323 renders as v15 prose rather than a deterministic working.

The flag **defaults to `v15`** on an absent or unrecognised value, so a malformed config can
never silently promote v16. `modal_app.py` bakes the **local working-tree** config via
`add_local_file`: the committed flag is not the live flag until the next deploy — in both
directions.

### Carried forward from the cutover

- **SAFETY-3 is now user-facing** and is the next work item. The VAT inversion was not live
  under v15 (which never applies the threshold); it went live at this deploy.
- ~~Fix `recover()` in both scratch harnesses, then re-register eval_318~~ — **done
  2026-08-10**, see the section above.
- The standing audit of remaining repo-relative reads inside the Modal image (CONTAINER-PATH-1)
  is unchanged and still open.

**Canary artifacts.** `scratch/canary_expected_v16.PRE_REGISTERED.json` is the untouched
pre-cutover record and is **not** rewritten to match the outcome;
`scratch/canary_expected_v16_corrected.json` is the post-fix version, stamped as such, with a
`differs_from_pre_registration` flag per row. Keeping both is the point — a pre-registration
edited after the fact is not a pre-registration.

**🏁 CYCLE FULLY CLOSED (2026-07-26):** the entire router-investigation + defect-fix cycle is now
closed end-to-end with real GPU confirmation. Follow-up #3's last two threads landed this session:
**work item 2** (round-2 adjudication of the afef9dd 25+7 queue — judge 23/24 = 95.8%, zero new engine
defects, commit `f195c23`) and **D-FIDELITY-1** (model body contradicting the deterministic compute
working — shipped `75421f0`, GPU-confirmed: 3 target rows corrected + judge 5/5, single fully-explained
eval_378 scorer-artifact flip, zero collateral). Two non-blocking follow-ups logged for later
(SCORER-SEMANTICS-1: credit "TZS 0"/not-applicable answers; JUDGE-NONDET: eval_397). See the
D-FIDELITY-1 and work-item-2-round-2 entries below.

## 🏁 PHASE D BATCHED RUN (1476caa) — ADR BAR PASSES; THE RESIDUAL REGRESSION CLASS IS GONE (2026-08-09)

Artifact: **`eval/results/gate_phase_d_paired_1476caa.json`** — fetched from HF
(`prospAprospA007/africa-giants-dataset`) and **sha256-verified**
`65015f060be37ef4c2208bce59952e61ab064e2fb35e939a81f8ae68a8e32ea1`, 1,022,937 bytes,
`complete: true`, `clone_head == live_head == 1476caa`, 400 questions, 217-fact index.
**Every number below was recomputed from the raw `v15_results` / `v16_results` / `part3_results`
rows independently of the summary block: 46 checks, all 46 matched.** Harness
`scratch/recompute_1476caa.py`.

This is the run the batched decision (founder, 2026-08-08) was waiting for: C1–C4 **plus** D and
F1/F2 together, measured on the configuration that would actually be wired, rather than on an
intermediate.

### Headline

| | 3ac522a | 030a5ff | 5d0dcb7 | **1476caa** |
|---|---|---|---|---|
| ADR bar raw | −6.8 **FAIL** | +0.5 | +1.3 | **+3.6 PASS** |
| ADR bar reliable | −3.7 **FAIL** | +1.1 | +0.8 | **+1.6 PASS** |
| compute raw / reliable | −29.4 / −23.0 | −2.0 / +4.0 | +4.9 / +5.0 | **+13.7 / +8.7** |
| gains / regressions | 11 / 37 | 19 / 17 | 17 / 12 | **20 / 6** |
| defective clarification rate | — | — | 9.8% | **2.9%** (target ≤5%) |

Per bucket (raw, then reliable):

| bucket | n | raw v15 | raw v16 | Δ | rel v15 | rel v16 | Δ |
|---|---|---|---|---|---|---|---|
| fact_path_190 | 193 | 158/184 | 158/184 | **0.0** | 111/130 | 111/130 | **0.0** |
| staged_50 | 50 | 38/50 | 42/50 | +8.0 | 31/39 | 33/39 | +5.1 |
| compute_type | 103 | 70/102 | 84/102 | **+13.7** | 36/53 | 46/60 | **+8.7** |
| adversarial_150 | 150 | 98/144 | 108/144 | +6.9 | 65/89 | 73/96 | +3.0 |
| **ALL_400** | 400 | **300/384** | **314/384** | **+3.6** | **212/263** | **222/270** | **+1.6** |

### The v15 arm was CACHED — and the cache was verified in full, not on the harness's 60 rows

`1476caa` cached the v15 arm from `5d0dcb7` behind a 60-row determinism check rather than
regenerating 400 GPU rows. **All 400 rows were re-verified offline here: 0 generated-text
differences and 0 pass-verdict differences against the `5d0dcb7` artifact.** The caching commit
is sound, and the v15 baseline is byte-identical for the **fourth** consecutive run — so no
sampling-noise defence exists for any v16 movement.

The judge verdicts on that cached arm are also unchanged, **400/400** — worth stating because a
byte-identical arm with drifting judge verdicts would have made every cross-run judge delta
meaningless, and JUDGE-NONDET makes that a live possibility rather than a hypothetical.

### Pre-registration — hit on the number and the direction

Recorded in the harness docstring at `57145f3`, **before** the run: *10 rows change on the 400;
9 were failing and should now pass; raw 314/384 vs v15 300/384 = +3.6; defective rate 3/102 =
2.9%.*

Observed, comparing the v16 arm against v16 at `5d0dcb7`: **9 flips, every one FAIL→PASS, zero
PASS→FAIL, raw 305 → 314**, and the defective rate exactly 3/102. **The composition claim was
slightly off in the safe direction — 12 rows changed text, not 10.** The two extras (eval_275,
eval_314) changed wording without flipping a verdict. Third consecutive calibration point, and
the second to hit its total exactly.

**The pre-registered watch row cleared.** eval_314 was flagged in advance as the one to watch —
already passing, shape changed by the rate branch, and *"if it flips to FAIL the rate branch is
over-broad and should be narrowed to rows that were clarifying"*. It is **still PASS and still
judge-correct** at `1476caa`. The rate branch is not over-broad.

### The 6 regressions — and the residual class is now EMPTY

**All 6 are v16 clarifications** (eval_271, 281, 291, 294, 295, 334). **There is not one row in
the entire 400 where v16 states a wrong number that v15 stated right.** Judge applied to *v15's*
answer on those 6: **5 wrong, 1 undetermined, 0 correct.**

That last figure is the one that moved. At `5d0dcb7` the "no class of regression" clause was
satisfied outright for the class it was written to catch, but **not clean** for a narrower
residual: eval_280 and eval_323, where a judge-confirmed *correct* v15 answer became a
clarification. **Both now pass** — eval_280 via C4 + headcount extraction, eval_323 via F1, each
closing exactly as the D/F investigation projected. The residual class goes from 1 row to zero.

> ### 🟢 THERE IS NO ROW WHERE v16 STATES A WRONG NUMBER THAT v15 STATED RIGHT.
>
> Stated plainly because **this is the sentence the wiring decision rests on**, and "the ADR
> clause is satisfied" is a weaker and less findable claim. Three measured zeros hold it up,
> across all 400:
>
> - **zero** rows where v16 states a wrong number that v15 stated right;
> - **zero** rows where a judge-confirmed correct v15 answer became a v16 clarification;
> - **zero** fact-path divergence on 281 of 282 non-compute scored rows, the single exception
>   (eval_322) passing in both arms.
>
> Every one of the 6 regressions is a v16 clarification replacing a v15 answer the judge calls
> wrong or cannot call at all.
>
> #### ⚠️ CORRECTION (2026-08-09, at cutover) — the original wording overreached, and here is the exception
>
> This block first read **"THERE IS NO ROW WHERE v16 IS WORSE THAN v15 BY ANY READING."** That
> is a stronger claim than the three zeros beneath it support, and it is **false on one row**:
>
> **eval_318 goes v15 `judge=undetermined` → v16 `judge=wrong`.** v15 recites the VAT threshold
> and never applies it to the user's figure; v16 applies it **backwards** and tells a business
> that must register for VAT that it need not (SAFETY-3 below). By the judge's reading that is
> v16 being worse than v15 on that row. The three zeros are each still exactly true — v15 never
> *stated the number right* there, so no zero is violated — but "worse by any reading" reaches
> past them, and eval_318 is what it reaches into.
>
> Caught by Claude re-reading its own claim against the cutover canary data, not by the founder
> or by any instrument. **The narrower headline above is the defensible one and is what the
> wiring decision actually rested on**; the overreaching version was live in this file from the
> `1476caa` entry until the cutover.
>
> Also unchanged and still the second honest qualifier: the one other row where v16 has ever
> been *worse* than v15 in this project's record — **nat_16**, the SAFETY-2 / D-RESIDENCY-1
> residency mis-detection, where v16 prints a wrong figure as a verified calculation while v15
> asserts no figure — is **not in the 400** and is unaffected by this run. It remains open. So
> the fully-qualified statement is: no row in the measured set where v16 states a wrong number
> v15 stated right, with **eval_318** the judge-visible exception inside the set and **nat_16**
> the known exception outside it.

### ⚠️ GAIN RECORD CORRECTED — 19 real / 1 false, not 20

The raw judge verdict on the 20 gains is **18 correct / 2 wrong** (eval_320, eval_321).
Adjudicated individually against gold rather than taken from the judge, that resolves to
**19 real gains and 1 false**, with the two rows going in opposite directions:

- **eval_320 is a genuine FALSE gain.** The regex credited it because every correct figure
  (0 / 80,000 / 78,000 / 4,000) appears somewhere in the merged answer — while the model body in
  the same breath asserts **SDL = TZS 28,000 on a ONE-employee payroll**, **NSSF = 160,000**, and
  **PAYE = 8% × 800,000 − TZS 26,000 = 64,000**, the last via a personal relief that **does not
  exist in Tanzania** (CLAUDE.md §11). The judge is right and the scorer is wrong.
- **eval_321 is a JUDGE error in the opposite direction.** Checked part-by-part against gold:
  SDL TZS 0 (8 < 10) ✓, NSSF 640,000 ✓, WCF 16,000 ✓, OSHA "Ndiyo, unatakiwa kusajili" ✓ — **all
  four parts match.** Independently corroborated by the cross-levy sweep below, which recovered
  eval_321's three model bodies as bare *"Thibitisha na TRA (tra.go.tz)."*: every figure in that
  answer is a deterministic working, so there is nothing left for the model to have got wrong.

**eval_320 is the row D-FIDELITY-2 was built for.** With the guard shipped this session those
bodies are blanked and the deterministic workings carry the answer, which should convert
eval_320 from a false gain into a real one — **but that is a projection, not a measurement, and
it is not confirmed until the next paired run.**

### Judge range — four treatments, sign-stable, and the exclusion gap has nearly closed

The reconstruction was **calibrated against the published `5d0dcb7` table first** and reproduced
all eight of its cells exactly before being applied here (`scratch/judge_treatments.py`).

| Treatment | v15 | v16 | Δ | (Δ at 5d0dcb7) |
|---|---|---|---|---|
| Reported (`build_confirmation_report`) | 267/360 = 74.2% | 297/368 = 80.7% | +6.5 | +6.2 |
| Common denominator, decisive in both arms (n=354) | 266/354 = 75.1% | 284/354 = 80.2% | **+5.1** | +3.7 |
| Every clarification = FAIL, undetermined excluded | 267/361 = 74.0% | 297/372 = 79.8% | +5.9 | +4.1 |
| Hard floor — clarifications *and* undetermined FAIL, /384 | 267/384 = 69.5% | 297/384 = 77.3% | +7.8 | +6.2 |

**Honest range +5.1 to +7.8; strictest like-for-like +5.1. No accounting flips the sign** — do
not quote +6.5 flat. Every treatment improved on `5d0dcb7`, the strictest by the most (+3.7 →
+5.1). **The exclusion asymmetry is now 3 rows, down from 10:** of v16's 21 clarifications, 17
sit inside the graded set and are already scored FAIL and only 4 are excluded outright (v15: 1).
Judge-undetermined fell 23 → 12 on v16.

### Fact path — byte-zero regression surface, holding

**281 of the 282 non-compute scored rows are BYTE-IDENTICAL between v15 and v16.** The sole
exception is again **eval_322**, the three-part enumeration the decomposer splits; both arms
PASS. 15 of 16 OOC rows are byte-identical, the exception being **eval_191** — the row whose
`out_of_corpus` label is a known mislabel (tracked separately; it is a core in-scope PAYE
computation and correcting the label moves the gate denominator).

So v16's entire delta still lives in the 102 compute rows, and the fact path carries **byte-zero**
regression surface rather than statistically-zero.

### Two-arm retriever — the regex pointed the wrong way for a fourth time

Part 3 reproduced **exactly**: two-arm 78/90 = 86.7% vs single-arm 74/90 = 82.2%, regex **+4.4**.
Judge-augmented on the same rows lands 70/89 = 78.7%. Four independent measurements have now
failed to demonstrate a two-arm benefit, and the regex scorer has pointed the wrong way on the
same question set every time. **Single-arm stays. Settled; do not reopen.**

### Clarification

**Defective clarification rate 3/102 = 2.9%, against ≤5% — PASS.** The three are exactly the
deliberate residuals: **eval_281** (permanent won't-fix, the approximation veto), **eval_326**
(residency split, D-RESIDENCY-1), **eval_334** (blocked on a *regulatory* question about
allowance taxability, not a code one). There is no defective clarification left that is a code
defect. All-clarification rate 16/102 = 15.7%, reported as context only — the retired target's
measured floor is 14.7% and **must not be reinstated**.

### Wiring — CODE COMMITTED, PRE-FLIGHT PASSED, ~~NOT DEPLOYED~~ **DEPLOYED `ec9cbb3`** (2026-08-09)

Both preconditions are clear. The rotation completed and **v16 is live** — see the cutover entry
at the top of this file. The text below records the wiring as it was staged, before the deploy.

**Shipped as code, not as a deploy:** `ChikeModel._orchestrator()` builds the Orchestrator once
per container with `retriever=self.retrieve_facts` (single-arm, load-bearing) and `run()`
dispatches on a new `chike_config.json` flag `pipeline: "v15" | "v16"`. The flag **defaults to
`v15`** on an absent or unrecognised value, so a malformed config can never silently promote
v16; rollback is a config edit + redeploy, never a code change.

> #### 🚨 The wiring surfaced a container-only Gate-2 regression — see **CONTAINER-PATH-1** below
>
> Letting `Orchestrator` default its OOC phrase lists would have served **39 phrases instead
> of 107** inside the Modal container, silently reopening SAFETY-1. Closed by passing
> `resolve_phrases(CONFIG)` explicitly from the baked config; `stop_strings` set explicitly for
> the same reason. Full write-up in its own entry — it is a class of defect, not a detail of
> this wiring.

**Pre-flight — all four ran, all four passed, before any deploy:**

| check | result |
|---|---|
| full test suite | 605 passed |
| `scripts/scan_for_keys.py` | clean |
| 620-row deterministic sweep | 0 rows changed |
| byte-compare vs the stored 1476caa v16 rows | deterministic path **byte-identical on all 87 working-producing rows**; the guard is the **only** behavioural change, on **exactly eval_318 and eval_320** |

The byte-compare (`scratch/preflight_wiring.py`) re-renders each stored row through today's
code from its recorded model bodies. It answers the two questions the test suite cannot: that
HEAD still reproduces what was measured, and that nothing besides the guard changed.

### 🚦 DEPLOY CHECKLIST — read the flag correctly

> **THE COMMITTED FLAG IS NOT THE LIVE FLAG.** `chike-inference/modal_app.py` bakes the
> **local working-tree** `kaggle/chike_config.json` into the image via `add_local_file`, so
> whatever the flag says takes effect **only at the next `modal deploy`**. Until then the
> running containers keep serving whatever config was baked at the *previous* deploy. Reading
> the committed value as "already live" is exactly backwards, and it is the same warm-container
> reasoning as R16.
>
> **~~Current state: `pipeline: "v15"` (flipped back at `e365c25`), production serving v15,
> nothing deployed.~~ SUPERSEDED — the cutover ran. Current state: `pipeline: "v16"`, deployed
> at `ec9cbb3`, production serving v16.** See the cutover entry at the top of this file.
> The flag was briefly committed as `v16`, then flipped back so the credential-rotation deploy
> carried ONE change rather than two — a combined deploy leaves two candidate causes for any
> failure, which is what R16 exists to prevent — then re-flipped as step 1 of the cutover.

**Agreed sequence (founder, 2026-08-09) — two deploys, deliberately:**

| # | who | step |
|---|---|---|
| 1 | Claude | flip the flag to `v15` and commit — **done, `e365c25`** |
| 2 | founder | rotate: new value → Modal secret `modal-api-token` / `MODAL_API_TOKEN` → `~/.chike_modal_token.txt` → Railway `MODAL_API_TOKEN` |
| 3 | founder | confirm the chain is complete |
| 4 | Claude | **rotation deploy** — `modal app stop chike-inference --yes` then `modal deploy`; verify the live path on the new token: one fact question answers normally, one OOC question refuses — **done** (took three rotation attempts; the Modal secret held a 10-char value against the local 43-char file, diagnosed from inside the container without exposing it) |
| 5 | Claude | **v16 cutover, its own deploy** — re-flip to `v16`, `modal app stop --yes`, deploy, then the full canary set — **done, `ec9cbb3`** |

Rotation order, confirmed: **Modal secret → `modal app stop --yes` && `modal deploy` → Railway
variable + redeploy → verify.** There is an unavoidable 401 window on the WhatsApp path
(Modal injects secrets at container start, so a single-value secret cannot be valid on both
sides at once); every reply during it is the FALLBACK message. Accepted — there are no users
yet. `generate_endpoint` shares the same gate, so `~/.chike_modal_token.txt` must be updated
before any local canary run.

**Step 5 live verification per R16** — `modal app stop chike-inference --yes` FIRST, because
"✓ App deployed" proves nothing while containers are warm. Then against the live endpoint:
**eval_320 and eval_318** (permanent canaries for the cross-levy class — the gate cannot see
them, both score `pass=True`), **eval_323 and eval_280** (changed compute rows), **a fact row
as the negative case** (must be byte-identical to v15), and **an OOC question** (must still
refuse).

## ✅ D-FIDELITY-2 — a compute body that volunteers a WRONG figure for a SIBLING levy (SHIPPED 2026-08-09)

`chike/fidelity.py::body_contradicts_siblings` + `Orchestrator._cross_levy_guard`, with 18 tests
in `tests/test_fidelity_cross_levy.py` and the findings artifact at
**`eval/results/cross_levy_guard_sweep_findings.json`**.

### What D-FIDELITY-1 structurally could not see

D-FIDELITY-1 validates each sub-answer body against **its own** `ComputationResult`. That is
blind to a body which restates its own levy correctly while asserting wrong figures for the
others in the same breath. **eval_320** is the case: the WCF sub-answer restated WCF 4,000
correctly and passed the per-levy guard, while the same body volunteered `SDL = 3.5% × TZS
800,000 = TZS 28,000` for a **one-employee** payroll (engine: TZS 0, below the 10-employee
threshold) and `PAYE = 8% × TZS 800,000 − TZS 26,000 = TZS 64,000` (engine: 78,000, and the
**TZS 26,000 personal relief does not exist** — CLAUDE.md §11). The regex scored the row PASS;
the judge called it wrong.

The guard runs as a **second pass**, because sibling results do not exist until every compute
part has been answered. Blanking is whole-body and idempotent, so running after the per-levy
guard can only ever remove more text, never resurrect any. **Compute sub-answers only** — a fact
sub-answer has no `ComputationResult` to fall back on, so blanking it would delete content
rather than replace it with the truth.

### Sweep — three instruments, because a clean result from one is not a green light

**A — no-op proof, 620 rows.** Every corpus question through the real Orchestrator twice, guard
active vs guard replaced by identity, comparing merged text, clarification flags and the per-sub
`ComputationResult` tuple. **0 of 620 rows change.** The guard cannot move a figure, a route or
a clarification.

**B — real-body replay.** The guard can only fire where a question routes to **two or more**
compute levies, which is **9 corpus questions**; 6 are in the gate and were replayed against the
**actual model bodies** recorded in the `1476caa` artifact. Bodies are recovered *exactly*, not
approximated: `_render` emits `body\n<working>` joined by `\n\n` and the workings are
deterministic, so each body is the text preceding its own working. The 3 probe rows (fv_01,
fv_02, fv_04) are not in the artifact and are reported **unmatched rather than guessed at**.

**2 questions flagged, 3 bodies, 0 false positives, 0 false negatives.** eval_320 is flagged
**twice** — its NSSF body and its WCF body each volunteer wrong sibling figures independently.
eval_318's SDL body asserts `NSSF = TZS 110,000` where the engine says 1,100,000 (a factor of
ten). **The four unflagged rows were each adjudicated individually rather than counted**
(eval_319, eval_321, eval_323, eval_327): every one names a sibling levy but attributes **no TZS
figure** to it, so there is nothing to contradict. All four are true negatives.

**C — ablation. All three design decisions are load-bearing**, measured rather than asserted:

| disabled | good bodies wrongly blanked | bad bodies missed | live flags |
|---|---|---|---|
| `_acceptable` → headline amount only | 2 (both NSSF share-vs-total probes) | — | unchanged |
| `_levy_windows` → every levy sees the whole body | 1 | eval_318 | **loses eval_318, spuriously gains eval_323** |
| `_ATTRIBUTED` → `=` only, no colon | — | 2 (incl. the eval_320 target) | unchanged |

**Windowing is the strongest result: without it the guard both misses eval_318 and blanks
eval_323, a correct body on a live corpus row.** `_acceptable` exists because NSSF's
authoritative `amount` is the employee share in a per-employee framing (eval_320) and the 20%
total in a payroll framing (eval_318), so a faithful body quoting either is not a contradiction —
that probe is the one that changed the code. Colon attribution matters because the enumeration
shapes attribute with `:` as often as with `=`; `_RESULT` is left byte-identical so the validated
own-levy detector is untouched.

**605 tests pass** (587 + 18).

### What this does NOT do

It is a **consistency check between two outputs of one computation**, exactly as D-FIDELITY-1 is.
It has no independent notion of correctness and **cannot detect an error upstream of both** — the
SAFETY-2 / D-RESIDENCY-1 class, where body and working agree because both derive from the same
mis-resolved input, is untouched by it. It also cannot see a fact sub-answer, which is precisely
why the eval_318 VAT defect below needs its own item rather than being folded in here.

## 🔬 SAFETY-3 INVESTIGATION ROUND — it is a CLASS, and it is wider than "wrong direction" (2026-08-10)

**Nothing implemented. Proposal only.** Artifact:
**`eval/results/safety3_threshold_investigation.json`**. Probes preserved at
**`eval/accuracy_gate/threshold_comparison_probes_024.jsonl`** (note: this takes the sweep
corpus from 620 rows to 644 — no test is wired to them yet, that belongs with the fix).

### The headline: the corpus understated the failure rate by about five times

| instrument | result |
|---|---|
| corpus exposure (620 rows) | **132 rows require a threshold comparison**; 48 have it performed by the model |
| corpus outcome (400 gate, both arms, adjudicated individually) | **1** answer with a wrong verdict (eval_318, v16) + 1 wrong-direction phrase with a right conclusion (eval_124, v15, fixed in v16) |
| **24 authored probes against LIVE v16** | **7 of 20 model-performed comparisons are WRONG (35%)**; **4 of 4 deterministic controls correct** |

**R17, demonstrated with numbers rather than restated.** The corpus rate is 1-in-8; the authored
rate is 7-in-20. Every one of the extra failures is a *form the corpus does not contain*. The
corpus was not reassuring — it was silent.

### Six distinct failure mechanisms, not one

`eval_318` is the direction inversion. It is the *least* of what is there.

| mechanism | probe | what happened |
|---|---|---|
| **direction inversion** | th_03 | TZS 195M vs a 200M threshold → *"umepita kizingiti"*. Invents an obligation that does not exist. |
| **direction inversion** | th_17 | reproduces the live eval_318 inversion byte-for-byte |
| **wrong threshold selected** | th_06 | TZS 120M in six months exceeds the **100M six-month limb**; the answer applies the 200M annual limb and says no |
| **no unit normalisation** | th_08 | TZS 20M/month = 240M/yr. The answer states *"you cross 100M in 5.5 months"* and then concludes **below the threshold** |
| **floor treated as ceiling** | th_16 | paying TZS 200,000 against a TZS 175,000 minimum wage → *"malipo ya ziada juu ya hapo ni kinyume cha sheria"*. **It tells an employer that paying above the minimum wage is illegal.** |
| **threshold conflation** | th_24 | TZS 50M is above EFD's 11M and below VAT's 200M; the answer orders **VAT registration off the EFD threshold** |
| **sub-question dropped** | th_20 | the VAT part of a multi-part question is never answered at all |

**th_16 is arguably worse than eval_318.** A fabricated prohibition on paying workers *more*
than the minimum is wrong-direction advice on a labour-law question, and nothing in the corpus
or the gate would ever have found it.

**Both directions fail.** th_03/th_24 invent obligations; th_06/th_08/th_17 excuse real ones. A
fix that biases toward "register" would trade one class of wrong advice for another.

### Root cause: not retrieval, not generation quality — a MISSING DETERMINISTIC PATH

Established, not assumed:

1. **Retrieval is fine.** The RAG index carries five VAT-threshold entries, including the
   Swahili-first *"Kizingiti cha kusajili VAT: mauzo ya TZS 200,000,000 kwa miezi 12."* The
   model **recites 200,000,000 correctly** and then compares wrongly. The fact is present and
   correctly stated in the very sentence that misapplies it.
2. **Not generation quality either.** `th_01` — the identical 205M-vs-200M comparison, asked
   standalone — is answered **correctly**. The model can do it. It just is not required to.
3. **There is no route.** `routing.COMPUTE_TYPES` is `("sdl","nssf","paye","wcf")`. VAT, EFD,
   minimum wage and the share-capital bands have **no computation type at all**, so
   `detect_intent("je nasajili VAT kama mapato ni TZS 205,000,000?")` returns **`none`** and the
   comparison is performed in free generation with no `ComputationResult` behind it.

**This is ROUTING-GAP-PAYE in a new domain, and the same argument settles it.** SDL and PAYE sit
behind a rules engine because a levy amount is arithmetic. *A threshold comparison is also
arithmetic* — `V >= T` — and it is the simpler of the two. The probe result is the measurement
that argument was always missing: **4/4 where the engine owns the comparison, 13/20 where the
model does.**

Corollary: because there is no `ComputationResult`, **neither fidelity guard has jurisdiction**.
D-FIDELITY-2 blanked eval_318's SDL body and left the VAT inversion untouched — correctly, by
its own design. No amount of guard widening reaches this; it needs a route.

### Does v16 being live make it worse? Yes — three ways, and one way better

**Worse:**
1. **Authority by association.** Under v16 the inversion is rendered *after* two deterministic
   workings, inside an answer that otherwise reads as verified computation. v15 delivered the
   same class of error as hedged prose.
2. **The guard raised its share of the answer.** D-FIDELITY-2 blanked the contradicting SDL
   body, so the wrong VAT sentence went from a clause inside a long paragraph to **186 of the
   317 characters (59%)** of the live reply. Removing wrong prose around a wrong claim
   concentrates it.
3. **v15 did not assert it.** Paired over the 79 gate rows demanding a comparison, v15 leaves
   eval_318 **UNRESOLVED** — it states the rule conditionally (*"unatakiwa kujiandikisha **ikiwa**
   mauzo yanazidi..."*) and never applies it. v16 applies it and gets it backwards. `undetermined
   → wrong`.

**Better:** all **four** rows where v16 asserts a direction v15 did not are **SDL headcount**
rows, all four routed to the engine, all four **judge-correct**, and two of them were
**judge-wrong under v15**. Where the deterministic path exists, v16 strictly improves the
comparison. That is the same finding from the other side.

### Options

| | approach | closes | cost / risk |
|---|---|---|---|
| **A** | **Deterministic threshold route** — give the engine `vat_registration` and `efd_requirement` computation types; extraction supplies V and its period, the engine holds T and emits verdict + working | direction, threshold selection, conflation, and unit normalisation — all four are consequences of the engine not owning the comparison. Also gives both fidelity guards jurisdiction for the first time | period extraction (12mo / 6mo / monthly) is a **new extraction surface** and th_08 shows it is genuinely hard. Router changes carry the highest blast radius in this system (ROUTING-GAP-PAYE) |
| **B** | **Fact-path comparison guard** — post-generation: recompute V vs T on any answer reciting a known threshold, blank or correct on mismatch | direction inversion and conflation, with no routing or extraction change | **cannot** fix th_06/th_08 — knowing *which limb* and *how to annualise* is exactly what it lacks, so it must blank. Blanking a fact sub-answer **deletes content** rather than replacing it with truth — the stated reason D-FIDELITY-2 excluded fact sub-answers. My own detector needed three iterations and still had 4 false positives before per-threshold attribution |
| **C** | **Refuse to compare** (R8 never-guess) — state the rule conditionally, decline the verdict. This is exactly v15's eval_318 behaviour | every wrong answer, immediately | turns 13 currently-correct answers into non-answers, on a question ("am I over the VAT threshold?") that is core to the product. Gate would score it worse — clarifications FAIL under most treatments |

**Recommendation — A for VAT and EFD, staged, with C as the fallback inside it.**

- **Phase 1: VAT (200M/12mo + 100M/6mo) and EFD (11M) only.** Both are single scalars needing
  no sector or band resolution, and they carry the question volume — 29 and 6 corpus rows. When
  the period is unambiguous the engine answers; **when the period cannot be extracted the engine
  declines and the answer states the rule conditionally** (option C, scoped to the hard case
  rather than applied to everything). That keeps th_08 safe without pretending to solve it.
- **Phase 2: minimum wage — separate investigation.** GN 605A is 16 sectors and 46 sub-sectors;
  resolving which floor applies is a bigger extraction problem than the comparison. **th_16 may
  not need a route at all** — a locked fact stating plainly that paying *above* the minimum is
  lawful is cheap and worth doing on its own.
- **Phase 3: unit normalisation** (th_08) as its own item. Annualising a monthly figure is an
  extraction problem, not a comparison problem, and folding it into Phase 1 would hide it.

**Do not skip the R17 step on the router change.** These 24 probes are the *start* of the probe
set, not the whole of it — a router change needs its own adversarial probes written against the
new cue list, plus the 644-row sweep.

### Three incidental defects, each needing its own item

1. **🔴 D-FIDELITY-1 has an attribution gap — VERIFIED, not suspected.** th_19's body says
   *"SDL ... **sawa na** TZS 210,000"* while its working says **TZS 17,500**. Checked directly:
   `_asserted_results(body)` returns an **empty set** and `body_contradicts_working` returns
   **False**. `_RESULT` matches `=` only and `_ATTRIBUTED` matches `[:=]`; **"sawa na" is the
   ordinary Swahili way to state a result and neither pattern sees it.** This is the same shape
   as the colon widening that D-FIDELITY-2's ablation proved load-bearing, and it means a body
   contradicting its own working passes silently.
2. **🔴 Compute base error on embedded multi-part.** th_19 computes SDL on a base of
   **TZS 500,000** instead of the stated 6,000,000; th_20 computes NSSF on **TZS 750,000**
   instead of 9,000,000. Both are the stated payroll **divided by 12** — a per-employee or
   per-month derivation firing where it should not. The deterministic layer is confidently
   wrong, which is the SAFETY-2 / D-RESIDENCY-1 class, not this one.
3. **🟠 A fact sub-question can be silently dropped** (th_20 never answers its VAT part) and
   **🟠 a fabricated figure** (th_22 invents a *"TZS 3,000 minimum"* WCF that appears in no
   locked fact).

## 🔴 SAFETY-3 — eval_318 answers the VAT threshold BACKWARDS on the fact path (2026-08-09)

> ### ⬆️ PROMOTED TO TOP OF THE QUEUE — 2026-08-09, at the v16 cutover
>
> **The promotion trigger was the cutover making it user-facing. No new evidence arrived.** The
> defect, the mechanism and the gold are exactly as characterised below and as they were this
> morning. What changed is deployment state: under v15 this row was *undetermined* — the model
> recited the threshold and never applied it — and at `ec9cbb3` v16 went live and now emits the
> inversion to real users.
>
> **"Logged" and "serving users" are different states, and this crossed the line at cutover.**
> A defect can sit correctly filed, correctly root-caused and honestly reported, and still
> change priority the moment the code path carrying it starts answering people. That transition
> is a promotion trigger in its own right and should be treated as one whenever a deploy moves
> a known defect onto the live path.
>
> It gets a **fresh investigation round** — characterise before any code, in the usual way.
> This is the next work item; nothing else starts ahead of it.

**Own investigation. Not folded into D-FIDELITY-2, and not closable by it.**

The fact sub-answer of eval_318, at both `5d0dcb7` and `1476caa`:

> *"**Hapana**, kwa sababu kizingiti chako cha usajili wa VAT ni TZS 200,000,000 tu. Mapato ya
> TZS 205,000,000 **hayazidi** kizingiti hicho, hivyo **huhitajiwi kusajili VAT**."*

**TZS 205,000,000 does exceed TZS 200,000,000.** The gold is explicit: *"mapato TZS 205,000,000
yamevuka kizingiti cha TZS 200,000,000/mwaka, hivyo **lazima usajili VAT**."* The system tells a
business that must register for VAT that it need not. This is **wrong-direction compliance
advice** — the same class as SAFETY-1, where the OOC gate leaked and the model answered a
capital-gains question with a confident rate.

**The row scores `pass=True, reliable=True` in both arms.** The regex credits it because 200M and
205M both appear; only the judge catches it (`judge=wrong`, and it sits in v16's false-pass
queue). A wrong-direction answer that the gate positively credits is worse than one it fails.

**Which path, and which arms.** The defect sits on the **shared fact path — the path that serves
every user whichever arm ships**. On this specific row only **v16** emits the inversion; v15
recites the threshold correctly and simply never applies it to the user's figure (`judge=
undetermined`). So v16 is worse *on this row*, but the mechanism — an unguarded numeric
comparison performed by the model on the fact path, with no deterministic backstop — is v15's
too, and v15's non-answer here is luck rather than safety.

**Not a rules-engine gap.** VAT registration is not a levy the rules engine computes; there is no
`ComputationResult` to guard, so neither fidelity guard can reach it. This is the
ROUTING-GAP-PAYE shape in a new domain: *the engine never ran at all*, and the model did the
threshold arithmetic unsupervised. Candidate directions — a deterministic threshold-comparison
route for VAT registration, or a fact-path numeric-comparison guard — are a **scoped
investigation, not a fix to attempt reactively**, and they must be characterised before any code
in the usual way.

### ⚠️ IT WAS ALREADY FILED ON 2026-07-26 AND NEVER PROMOTED — this is the actual finding

eval_318's VAT inversion is recorded in this file at the work-item-2 round-2 adjudication of the
`afef9dd` queue: *"eval_318 **inverted** the VAT 205M>200M comparison"*, filed as one of **"4
generation"** root causes inside a list of 16 confirmed regex false-passes. It was correctly
identified, correctly root-caused, written down — **and given no owner, no item number, and no
tracking line.** It has survived an entire fix cycle untouched and is still live in the most
recent run.

**Standing lesson — a defect filed as a row inside a queue is not tracked.** The
adjudication queues exist to compare *instruments* (regex vs judge), and their output is a list
of scored rows, not a work list. Two instruments flagged this row and neither produced an owner,
because nothing in the process promotes a row out of a queue into the defect register. Anything
found inside an adjudication batch that is a **user-facing wrong answer** must be lifted out into
its own dated item with its own heading at the time it is found — the queue entry is evidence,
not a record of work. Concretely: when a future adjudication produces a false-pass list, sweep it
for wrong-direction and wrong-number answers **before** closing the batch, and promote each one.

## 🔴🔴 CONTAINER-PATH-1 — WIRING v16 WOULD HAVE SILENTLY REOPENED SAFETY-1 (2026-08-09)

**The most important finding of the wiring work, and it is a CLASS, not a detail.** Caught
while writing `ChikeModel._orchestrator()`; closed in the same commit (`30db5e6`). Nothing
shipped broken — but nothing offline would have told us if it had.

### The defect

`Orchestrator.__init__` defaults its OOC phrase lists from
`classification.load_local_config()`, which reads a **repo-relative** path:

```python
_LOCAL_CONFIG_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "kaggle", "chike_config.json"))
```

The Modal image mounts **only** `chike/` — `add_local_dir(..., '/root/chike')` — and bakes the
config somewhere else entirely, `/root/assets/chike_config.json`. So inside the container that
path resolves to **`/root/kaggle/chike_config.json`, which does not exist**.
`load_local_config()` swallows the `FileNotFoundError` and returns `{}` by design, and
`resolve_phrases({})` returns the hardcoded-only list.

**Measured, not reasoned:** `resolve_phrases(CONFIG)` → **107** OOC phrases.
`resolve_phrases({})` → **39**. The 68 missing ones are the config-only additions —
**the entire SAFETY-1 audit**, the 54-phrase expansion that closed the live refusal-gate leak
where the production endpoint answered *"niliuza kiwanja changu... nalipa kodi gani"* with a
confident capital-gains rate.

So wiring v16 with defaulted phrase lists would have **served users a v16 whose OOC gate had
been silently rolled back to its pre-SAFETY-1 state.** Gate 2 is a launch-blocking gate under
R7.

### Why no offline instrument could have caught it

This is the part worth internalising. **The path resolves correctly everywhere except in
production:**

| environment | `../kaggle/chike_config.json` resolves to | phrases |
|---|---|---|
| local dev / `pytest` | the real repo file | **107** ✅ |
| Kaggle clone (every gate + paired run, incl. the 1476caa measurement) | the real cloned file | **107** ✅ |
| **Modal container** | `/root/kaggle/...` — absent | **39** ❌ |

The full test suite passes. The 620-row sweep passes. The byte-compare against the stored
1476caa rows passes. **The harness that produced the measurement authorising the wiring had
the full 107**, so even a perfect replication of the measured configuration would not have
revealed it. The divergence exists *only* in the one environment no offline instrument runs
in, and the failure is **silent** — a shorter list refuses less, and refusing less looks like
working.

### Second time R16's class has bitten — and the first is the same shape

| | 2026-08-07 — stale containers | 2026-08-09 — CONTAINER-PATH-1 |
|---|---|---|
| change | OOC phrase list expanded in config | v16 wired, phrase lists left to default |
| what was true locally | new phrases present and correct | 107 phrases resolved correctly |
| what the container did | kept serving the OLD config from warm containers | would have resolved `{}` → 39 phrases |
| how it presents | the leak the fix closed reproduces exactly | the leak SAFETY-1 closed silently reopens |
| detectable offline? | **no** | **no** |

**Both are the same failure: a config value that is correct in the repo and absent in the
container, presenting as a refusal-gate regression.** R16 was written about *timing* (warm
containers serve old config). CONTAINER-PATH-1 shows the same class through *path resolution* —
the config never reaches the container at all, at any point, no matter how many times you
redeploy. Generalising R16 accordingly:

> **A config value is not "in production" because it is in `chike_config.json`. It is in
> production when a request has demonstrably behaved differently because of it.** Two ways it
> can fail to arrive: the container is stale (R16), or the code reads a path the container does
> not have (this). Neither is visible to any test that runs outside the container.

### Rules that follow

1. **Never let production code depend on `load_local_config()`.** It is the *local/orchestrator*
   loader — its own docstring says so — and it fails soft to `{}`. Production must pass the
   baked `CONFIG` explicitly. Done here for `ooc_phrases`, `in_scope_phrases` and
   `stop_strings`.
2. **Audit every remaining repo-relative path read from inside the Modal image.**
   `chike/prompting.py` uses the same pattern (`load_system_prompt`) — production overrides it
   by passing `system_prompt=BASE_SYSTEM_PROMPT` explicitly, so it is safe *today*, but only
   because the caller happens to be explicit. Worth a standing check rather than luck.
3. **A fail-soft default in a config loader is a liability on the serving path.** `{}` is right
   for a unit test and wrong for a container: it converts "the config is missing" into "the
   safety list is shorter". Where a fail-soft default meets production, the caller must be
   explicit.
4. **The live canary set must include an OOC refusal on every deploy** — it is the only check
   that can see this class. It is already in the wiring verification set, and it is now the
   single non-negotiable item in it.

## 🔐 CREDENTIAL HYGIENE — a docstring promised "never logged" and was false in exactly the failure path (2026-08-09)

`tests/test_orchestrator.py::_real_modal_token` is documented *"Token from env, else
~/.chike_modal_token.txt. **Never logged.**"* Every scratch probe carries the same promise. It
held on the success path and **broke on the only path that matters** — the token rides in the
**query string**, so `requests`' own `HTTPError` embeds it verbatim:

```
401 Client Error: Unauthorized for url: https://...generate-endpoint.modal.run/?token=<LIVE TOKEN>
```

During the 2026-08-09 rotation the real-weights tests — which normally SKIP, and only ran
because a token file now existed — hit the post-rotation 401 and **printed the live credential
into the pytest failure report**. Not a hypothetical: it went to a temp file on disk and into
terminal scrollback, and the token had to be treated as burned and rotated again.

**Three things worth keeping:**

1. **A safety claim in a docstring is not a safety mechanism.** The promise was written about
   the code the author was looking at (nothing calls `print(token)`) and not about the library
   underneath it. `LocalAdapter.generate()` now scrubs before re-raising, and
   `tests/test_container_path_guards.py` fails if a future change lets the value through — the
   claim is now enforced rather than asserted.
2. **A credential in a QUERY STRING leaks by default, not by mistake.** Every layer that
   renders a URL — exception messages, access logs, proxies, browser history, CI output — gets
   the secret for free. The query-param design was chosen deliberately (a module-level
   `from fastapi import Header` would crash the GPU container that imports `modal_app` without
   fastapi), so this is a **known cost of a defensible decision**, and the mitigation is to
   scrub at every boundary rather than to re-litigate the design.
3. **`scan_for_keys` cannot see this class.** It scans *staged files* for hardcoded keys. A
   credential that only ever appears in runtime output is invisible to it. Nothing in the repo
   was ever wrong; the leak was entirely in what the code *printed*.

Same shape as CONTAINER-PATH-1 above, one layer up: something true of the code as written, and
false in the one environment or path that was never exercised.

## 🔴 STANDING LIMITATION — THE GATE CREDITS BOTH OF THE WORST DEFECTS THIS CYCLE FOUND (2026-08-09)

**The two most serious defects found this cycle both score `pass=True` on the regex scorer.**
Not `reliable=False`, not excluded — positively credited, counted toward the launch-blocking
in-corpus number.

| row | what it does | regex | judge |
|---|---|---|---|
| **eval_318** | tells a business with TZS 205,000,000 turnover it need **not** register for VAT against a 200M threshold — wrong-direction compliance advice | `pass=True`, `reliable=True` | wrong |
| **eval_320** | asserts **SDL TZS 28,000 on a ONE-employee payroll** and a PAYE figure derived from the **phantom TZS 26,000 relief** (CLAUDE.md §11) | `pass=True` | wrong |

**Mechanism — this is structural, not bad luck.** The scorer is number-set intersection: it asks
*"is a correct figure present?"* and never *"is a WRONG figure also present?"* eval_318 passes
because 200,000,000 and 205,000,000 both appear; eval_320 passes because all four correct
figures (0 / 80,000 / 78,000 / 4,000) appear **alongside** the wrong ones. So **an answer that
states the right number AND a contradicting wrong number scores identically to one that states
only the right number** — and that is exactly the shape the v16 compute path produces, because
`_render` appends the authoritative working to whatever the model said. The better the
deterministic layer gets at guaranteeing a correct figure is present, the more reliably it
*masks* a wrong figure sitting next to it from the scorer. **This is D-SCORER-1, but the
severity is new**: the masked content is now wrong-direction compliance advice and an
authoritative-looking wrong levy figure, not a rambling near-miss.

### Why this and the queue-buried lesson are one argument

The judge caught both rows. It also caught eval_318 **a cycle earlier**, on 2026-07-26, and that
finding was lost because it lived as a line item inside an adjudication queue with no owner (see
SAFETY-3 above). So the record is: **the only instrument that can see this class found both
defects, and the process still lost one of them for a full cycle.**

Two conclusions, and they are different questions that have been getting conflated:

1. **Should the judge MOVE the `GATE PASSED` number? Still no — unchanged.** That remains gated
   on work item 2 (real adjudicated ground truth). Nothing here changes that; the judge is not
   ground truth and was itself wrong on eval_321 this very run.
2. **Should the judge RUN at all? Always — ✅ APPROVED AND SHIPPED (`1facd2a`).** The overlay
   used to be *optional*: it fired only when `OPENROUTER_API_KEY` was present and
   `CHIKE_JUDGE != 0`, and both harnesses were explicitly designed to complete without it. That
   made the only instrument capable of seeing wrong-direction answers a thing that could
   silently not happen. **Both `kaggle/eval_phase_d_paired.py` and
   `kaggle/eval_orchestrator_combined.py` now RAISE at second 0** — not after ~3.5h of GPU —
   with the cost stated in the error ($0.21 + $0.20 + $0.05 on this run) so nobody skips it to
   save money. `CHIKE_JUDGE=0` survives as an explicit human opt-out, but it prints a banner and
   stamps the artifact `judge_overlay: "SKIPPED"`, so **a judge-less run is self-identifying and
   can never be read as a clean result.**

**Additional standing practice:** every run's false-pass queue must be swept for
**wrong-direction and wrong-number** answers and each one promoted to its own item *before* the
run is declared clean. A false-pass list is evidence, not a work list.

**eval_318 and eval_320 are therefore PERMANENT LIVE CANARIES, not gate rows.** The gate cannot
see them by construction, so they are checked against the live endpoint on every deploy. They
are already in the wiring verification set for exactly this reason.

## 🏁 PHASE D RUN 3 (5d0dcb7) — ADR BAR PASSES ON THE SHIPPING CONFIG; clarification metric replaced (2026-08-08)

Artifacts: **`eval/results/gate_phase_d_paired_5d0dcb7.json`** (fetched from HF, **sha256-verified**
`0385db93ba5a946b`, 1,024,998 bytes, `complete: true`, `clone_head == live_head == 5d0dcb7`)
+ **`..._findings.json`**. **Every number recomputed from raw rows, independently of the summary
block; all recomputations matched.** This is the **first run on the configuration that would
actually ship** — the two earlier runs measured v16 *with* the two-arm retriever, which was dropped.

### Headline

| | 3ac522a | 030a5ff | **5d0dcb7 (shipped config)** |
|---|---|---|---|
| ADR bar raw | −6.8 FAIL | +0.5 PASS | **+1.3 PASS** |
| ADR bar reliable | −3.7 FAIL | +1.1 PASS | **+0.8 PASS** |
| compute raw / reliable | −29.4 / −23.0 | −2.0 / +4.0 | **+4.9 / +5.0** |
| gains / regressions | 11 / 37 | 19 / 17 | **17 / 12** |
| judge-augmented v15 → v16 | — | 74.4 → 80.2 | **74.2 → 80.4** |

### The finding the headline understated

`fact_path` is not merely "flat". On the shipped configuration **v16 and v15 produce
BYTE-IDENTICAL text on 281 of the 282 scored fact-path rows** (and 15 of 16 OOC rows). The one
exception, eval_322, is a three-part enumeration the decomposer splits — both arms PASS, judge
calls both correct. So **v16's entire delta lives in the 102 compute rows and the fact path has
byte-zero regression surface**, not statistically zero. The two-arm retriever was the only thing
that had ever perturbed it. This is the strongest available form of the ADR "no class of
regression" answer, and it only became measurable once the arm was dropped.

### Pre-registration hit exactly, including its composition

Recorded in the harness docstring at `d0e7390` **before** the run: deterministic **+7**
(eval_368; 247/371/372/378/379/393), retrieval **−4** (6 lost, 2 regained), net **+3 → 305/384 =
+1.3**. Observed: those exact ids, that exact total. v15 is **byte-identical for the third
consecutive run**, so no sampling-noise defence exists for any v16 change.

### The 12 regressions — zero new

All 12 carried from 3ac522a *and* 030a5ff. Five closed since 030a5ff (eval_368 `78b672c`;
eval_378/393 `bb30e25`; eval_127/208 the arm swap) and all five are now judge-correct.
**All 12 are v16 clarifications — there is not one row where v16 states a wrong number that v15
stated right.** Classing with the judge as tiebreaker on v15's own answer: **A=3** (extraction
coverage), **B=4** (never-guess correct — the gold is itself a clarification), **E=5** (deferred
patterns). C and D are empty: every output-shape row was closed by `bb30e25`, and the
retrieval-caused class died with the two-arm arm. Judge on v15: **8 wrong, 2 correct, 2
undetermined** — in two-thirds of the "regressions" v16 replaced a confidently wrong compliance
number with a question.

**"No class of regression" — satisfied outright** for the class the clause was written to catch
(zero rows where v16 is wrong and v15 was right, plus byte-zero fact-path divergence). **Not
clean** for a narrower residual class: **eval_280 and eval_323**, where a judge-confirmed *correct*
v15 answer became a clarification.

> **⚠️ CORRECTION (2026-08-08), recorded because the sequencing rationale was built on it.**
> The wiring order was set partly on my claim that headcount extraction "unblocks 3 rows on its
> own including both genuine regressions (eval_280, eval_323)". **Measurement disproved that.**
> Headcount extraction closes eval_280 only in combination with the C4 scope fix, and **it does
> not close eval_323 at all** — eval_323 needs pattern F. **The residual class therefore goes
> from 2 rows to 1 (eval_323), not to 0.** The sequencing decision still stands on its other
> grounds (cheapest item; moves the defective rate; closes eval_280 before wiring rather than
> after), but the file must not carry a claim measurement disproved.

### Judge range — four treatments, sign-stable

| Treatment | v15 | v16 | Δ |
|---|---|---|---|
| Reported (`build_confirmation_report`) | 267/360 = 74.2% | 291/362 = 80.4% | +6.2 |
| Common denominator, decisive in both arms (n=349) | 266/349 = 76.2% | 279/349 = 79.9% | **+3.7** |
| Every clarification = FAIL, undetermined excluded | 267/361 = 74.0% | 291/373 = 78.0% | +4.1 |
| Hard floor — clarifications *and* undetermined FAIL, /384 | 267/384 = 69.5% | 291/384 = 75.8% | +6.2 |

**Honest range +3.7 to +6.2; strictest like-for-like +3.7. No accounting flips the sign** — do not
quote +6.2 flat. Exclusion asymmetry measured precisely: of v16's 30 clarifications, **19 sit
inside the reliable set and are already scored FAIL**; only 11 are excluded outright (v15: 1). The
real gap is **10 rows, down from 14**. Undetermined fell 23 → 11. Of the 17 gains only eval_321 is
judge-wrong (1 in 17, against 5 in 19 last run).

### Two-arm retriever — settled, and the regex "loss" is largely phantom

Judged part 3: two-arm 78.7% vs single-arm 78.8% (**−0.17**), with **4 two-arm-only judge wins
against 11 single-arm-only**. Per-row on the 8 regex-flipped rows: eval_008/034/186 are
judge-**wrong under both arms** (phantom losses); **eval_331 is judge-correct under single-arm and
wrong under two-arm — the regex scored it backwards**; eval_019 is a real loss; eval_187
undetermined→correct; both single-arm wins (eval_127/208) are judge-confirmed. **Three independent
instruments now agree**, and the regex scorer has pointed the wrong way three times on the same
question set. **The raw +1.3 is, if anything, an understatement.**

### ⚠️ THE 15% CLARIFICATION TARGET WAS UNREACHABLE BY CONSTRUCTION — RETIRED, DO NOT REINSTATE

The all-clarification target (≤15% of compute-routed questions), set on 2026-08-08 alongside the
ADR bar, **has a measured floor of 15/102 = 14.7%** and is therefore not a product target with
headroom — it is the floor with a rounding error on top. The founder set it without knowing the
floor and retired it the same day. **Do not reinstate it.**

Why 14.7% is a floor: **15 of the 25 clarifications are questions whose GOLD ANSWER IS ITSELF A
CLARIFICATION.** Answering them at all would require guessing, which is precisely what R8 forbids:

| Bucket | n | ids |
|---|---|---|
| **Gold itself clarifies — correct behaviour, cannot be "fixed"** | **15** | FX 271/272/273/275/276 · missing prior context 299 · non-monetary basis 264/267/270 · pay basis unresolvable 291/292/295 · headcount genuinely absent 277/294/305 |
| Pattern **D** closes | 2 | 293, 296 |
| **Headcount extraction** closes — a NEW item | 3 | 280, 319, 320 |
| Pattern **F** closes | 2 | 323, 329 |
| Neither | 3 | 281 (approximation veto), 326 (residency split), 334 (composition) |

Achievable rate, **measured against the live extraction layer, not estimated**: today 24.5% ·
after D 22.5% · **after D + F 20.6%** · after D + F + headcount extraction 17.6% · after closing
literally every defect **14.7%**.

**REPLACEMENT METRIC — DEFECTIVE CLARIFICATION RATE.** Clarifications where the **gold answers**
rather than clarifies, as a share of compute-routed scored questions. **9.8% today (10/102),
target ≤5%, tracked in every paired run.** It measures product breakage rather than never-guess
behaviour, and unlike the all-clarification rate it can reach zero without violating R8.
After D + F + headcount extraction it is 3/102 = 2.9%.

### 🔎 NEW ITEM — HEADCOUNT EXTRACTION (discovered by measuring, not by assuming)

**Pattern F was assumed to close the multi-part rows. Measurement showed it does not.** Multi-levy
decomposition **already works** — eval_319 emits 2 clarifications, eval_320 emits 4, eval_323
emits 2, one per levy. What blocks them is `parse_count` returning `None` on rows where a
headcount is written in plain Swahili. **The binding constraint is headcount extraction, not the
D/F splitting patterns.** A 579-question survey found **13 real surface misses**, dominated by a
single gap: **the singular people-nouns (`mfanyakazi`, `mtu`, `mtumishi`, `mwajiriwa`) are absent
from `_PEOPLE_NOUN`** — only `kibarua` is there.

Four candidate changes, prototyped in scratch and **ablated over all 579 corpus questions**:

| | change | closes alone | needs |
|---|---|---|---|
| **C1** | singular `mfanyakazi mmoja` → 1, appended *after* the existing patterns | eval_320 | — |
| **C2** | digit + pay-verb (`18 wenye`, `14 wanaopata`) — already in `_COUNT_TOKEN`, absent from `parse_count` | nothing alone | C4 |
| **C3** | `count_transition_ordinal` surfaces: `kufikia N`, `nikafikia watu N` (today only `mfanyakazi wa N`) | nothing — **preparatory for F**, and it strengthens the M4 containment C1/C2 rely on | — |
| **C4** | per-person/aggregate **scope**: `kila mmoja` governs the SALARY, `jumla/wote` governs the ASK — not a conflict when the headcount is known and one amount was parsed | eval_275 copy | — |

**All four together: 4 answers change across 579 questions, 0 regressions** — eval_275 (copy
corrected to the FX question), eval_280, eval_319 and eval_320 all now match gold exactly.
C1+C2+C4 is the load-bearing combination; C3 changes 3 predicates and 0 answers.

**✅ SHIPPED `54b9b29`.** 587-question sweep: **13 rows change a predicate, 4 change an ANSWER, 3
stop being clarifications, 0 regressions.** eval_280 → TZS 1,728,000; eval_319 → SDL 245,000 +
NSSF 1,400,000; eval_320 → SDL TZS 0 + NSSF 80,000 + PAYE 78,000 + WCF 4,000; eval_275 → the FX
question. All four match gold exactly. The other 9 rows recover a count of 1 without changing any
answer and were each checked individually for a newly reachable defect — **none exists**:
eval_260 is held by the wrong-base rejection, and `wcf_applies()` / `nssf_applies()` take no
`employee_count` at all, so a recovered 1 cannot make a threshold-free levy "not applicable".
Only SDL has a count threshold and `applicability(sdl, 1)` correctly returns not-applicable.

R17: **12 adversarial in-scope probes**. **Two I mis-specified and rewrote rather than changing
the code** — hc_07 (I asserted `parse_count` must return `None` for "wafanyakazi 9 na ninaajiri
mfanyakazi wa 10"; it returns 9 *at baseline*, because the veto lives at the **consumer**, not
the parser) and hc_12 (I asserted `None` for "nimeajiri hadi **kufikia** wafanyakazi 11" — a
*completed* hire, so 11 **is** the current headcount). hc_12 exposed a pre-existing asymmetry:
`_SECOND_GROUP` matches `kufikia \d+` but not `kufikia wafanyakazi \d+`. Benign — count and
transition agree — and logged rather than silently relied on. A **test helper** was also wrong,
not the code: `_deterministic(text, required, computation_type)` had its last two arguments
swapped, which makes `required` a string and silently skips the amount field entirely.

Defective clarification rate: **9.8% → 6.9%** (10/102 → 7/102). Target ≤5%.

### Sequence set by the founder (2026-08-08)

**Wiring is approved in principle, gated on the DEFECTIVE clarification rate, not the retired
one.** Order: **headcount extraction → re-measure with a paired run → then wire.** Reasons: it is
the cheapest remaining item, it closes eval_280 (one of the two genuine regressions) before
wiring rather than after, and it moves the defective rate toward ≤5%. **Patterns D and F are held
until after the re-measure** — no stacking onto an unmeasured configuration.

**Next:** ~~a paired re-run~~ **BATCHED (founder, 2026-08-08).** A full paired run is ~3h of GPU
time and C1–C4 alone lands at 6.9%, above the ≤5% target — so no run until D + F are also in.
**One paired run at the end covering C1–C4 + D + F together**, so it measures the configuration
that would actually be wired rather than an intermediate.

## 🔬 D / F / eval_305 — ONE investigation round (2026-08-08, PROPOSAL — nothing implemented)

Remaining defective set after C1–C4 = **7 rows**: eval_281, eval_293, eval_296, eval_323,
eval_326, eval_329, eval_334.

### Pattern D — per-unit rate × per-month quantity

**Root cause.** eval_293 and eval_296 both reach `_amount_field` as *"multiple figures — role
ambiguous"* on exactly two figures. The rate and the quantity are both stated; nothing infers
that one multiplies the other. **Magnitude cannot be the discriminator** — the real rates here
are 1,500/piece and 18,000/day, so a size rule reads 1,500 as a count (this is already recorded
in the `_COUNT_TOKEN` note). **Structural rule:** rate = the figure before `kwa|kila <unit>`;
quantity = the figure adjacent to `<unit> N kwa mwezi`; monthly = rate × quantity, **only when
the quantity is explicitly per MONTH**.

**Reach:** 3 corpus questions (eval_293, eval_294, eval_296) + 1 probe duplicate. 9 further rows
match a rate but have no monthly quantity and **correctly decline** — including eval_291
(bi-weekly, calendar-dependent, gold clarifies), eval_292 (shifts per *day*), and gp_02/os_03
(the two-group twelve-person case).

**R17 — the naive rule produces TWO confident wrong numbers; the guarded form declines both:**
`dv_01` (two rate groups → 600,000 asserted as the payroll, the gp_02 failure mode with a
monthly quantity bolted on) and `dv_06` (two quantities, 3 shifts/day *and* 26 days/month →
650,000 where the truth is 1,950,000). **Guards required:** inherit `_has_second_group` /
`has_multiple_groups`, and decline when more than one rate or more than one monthly quantity is
present.

**Design constraint that must be stated in the code:** D yields **one person's** monthly pay,
never the payroll. It must feed `monthly_salary` / the per-person × headcount path, never
`gross_monthly_payroll` directly — otherwise eval_294 becomes "SDL = 3.5% × 1,200,000" for a
single driver, which the gold explicitly refuses.

### Pattern F is TWO mechanisms, not one

**F1 — per-levy amount anchoring (eval_323).** Multi-levy decomposition already emits one
sub-answer per levy, but every sub-question sees all four figures. **The obvious fix is unsafe:**
anchoring each levy to its nearest plausible amount gets eval_323 right *and breaks eval_327*,
anchoring both WCF and SDL to 300,000 when the correct base is the 4,600,000 group payroll —
a row that answers correctly today. A safe version must (a) gate on `parse_payroll_groups(text)
is None` so a resolvable group construction always wins, and (b) require the amount to be a
**payroll-label genitive inside the levy's own clause** (`SDL ya jumla ya mishahara ya TZS N`).
**Reach: 1 row.**

**F2 — multi-period split (eval_329).** Two named months, one payroll, a headcount either side
of the threshold. `count_transition_ordinal` already supplies the post-transition count (C3).
**Reach: 1 row** + 1 probe (ex_09). The third multi-month hit, eval_160, is a fact-path date
range and a false positive for this shape.

### eval_305 is a 5-row family, not a single row

`kiwango cha <levy> ni asilimia ngapi` — **the rate does not depend on the amount.** eval_111 and
eval_112 carry no figure and already work; eval_305, eval_314 and eval_315 carry one, and every
gold states the rate first and *then* optionally applies it. **Defective-rate impact: 0** (see
the borderline note below) — this is an answer-quality item, not a rate item.

### Does ≤5% actually get reached?

Denominator 102. **The answer depends on one borderline classification, so both readings are
given rather than the flattering one.**

| | eval_305 as *gold-clarifies* (my original call) | eval_305 as *defective* (strict reading) |
|---|---|---|
| today, after C1–C4 | 7/102 = **6.9%** | 8/102 = **7.8%** |
| + D | 5/102 = **4.9%** ✅ *one-row margin* | 6/102 = **5.9%** ❌ |
| + D + F1 | 4/102 = 3.9% | 5/102 = 4.9% ✅ |
| + D + F1 + F2 | 3/102 = **2.9%** ✅ | 4/102 = 3.9% ✅ |
| + eval_305 family | 3/102 = 2.9% | 3/102 = **2.9%** ✅ |

**The borderline:** eval_305's gold both *answers* (3.5%) and *asks* ("Thibitisha idadi ya
wafanyakazi"). I bucketed it as gold-clarifies; the stricter reading is defensible.

**Answer: yes, ≤5% is reachable — but not by D alone under both readings.** D alone clears it
only on the looser reading and only by a single row, so any one new defective clarification
puts it back over. **D + F reaches 2.9%–3.9% under either reading**, with a three-to-four-row
margin. That is the combination to build.

**What remains after all of it — 3 rows, ~2.9%, and worth leaving:**
eval_281 (the approximation veto firing on "hivi"/"kidogo" — narrowing it trades a clarification
for a guessed figure), eval_326 (resident vs non-resident, two individuals — needs a residency
split, D-RESIDENCY-1), eval_334 (base + allowance + one-off bonus — pattern E, blocked on a
`locked_facts` answer about allowance taxability, which is a **regulatory** question, not a code
one). None should be forced to close a metric.

### Recommendation

**Build D and F2. Build F1 only in its narrow gated form. Take the eval_305 family as a
separate small answer-shape item.** D is the load-bearing one and the only one whose absence
keeps the rate above target under both readings. F1 buys one row for the riskiest mechanism in
the set and is the one to drop if anything has to be dropped — but it also closes eval_323, the
**last remaining member of the residual regression class**, which is an argument for keeping it.

### ✅ ALL FOUR SHIPPED — `93e4d84` (2026-08-08)

599-question sweep: **7 rows change, all intended, 0 regressions, 6 clarifications closed.**
eval_293 → PAYE 36,000 · eval_296 → NSSF 46,800 · eval_323 → SDL 266,000 + PAYE 68,000 ·
eval_329 → Januari nil / Februari 105,000 · ex_09 → correct · eval_305 → the rate ·
**eval_314 → already correct and still correct**, its shape now matching a gold that states the
rate before applying it. That last one is a change to a *working* row, flagged as such.

**R17 — 21 probes; three earned their keep and none was reachable from the corpus.**
`dv_01` two rate *groups* → naive D asserts 600,000 as a **twelve**-person employer's payroll
(gp_02's failure mode with a monthly quantity bolted on). `dv_06` two *quantities* → naive D
returns 650,000 where the truth is 1,950,000. `fv_01` **eval_327** → naive F1 pins both WCF and
SDL to 300,000 instead of the 4,600,000 group payroll. All three now decline.

**Two defects of mine, caught by behaviour rather than review.** F2 was first nested *inside*
the crossing veto and could therefore never fire on eval_329, the one row it was written for —
a multi-period question inherently *has* a crossing, and this branch reads both counts instead
of assuming one. And `_CROSSING` written as `(?:{_PEOPLE_NOUN}\s+)?` binds loosely, so only the
last alternative carries the `\s+` and `nikafikia WATU 12` silently stopped matching when the
surface moved out of `routing.py`; ex_09 changing behaviour exposed it. Both fixed at source.

Also removed a duplication C3 had introduced: the threshold-crossing surface now has **one
owner** (`swahili_numbers._CROSSING`) and `routing._COUNT_TRANSITION` delegates to it, with a
test pinning the delegation. Three copies of one safety predicate is the dual-file divergence
CLAUDE.md warns about.

**Defective clarification rate: 7.8% → 2.9%** on the founder's strict reading, against ≤5%.
Verified offline end-to-end. **587 tests pass.**

### ⛔ eval_281 — WON'T FIX BY DESIGN. Do not reopen this chasing a number.

"Mshahara wake ni mkubwa kidogo, unafika TZS 920,000 **hivi**" clarifies because the
approximation veto fires on the hedge. The gold uses 920,000 as stated, so this reads as a
miss — and closing it means **narrowing an approximation veto so the model treats a hedged
figure as exact**. That trades a clarification for a guess, which is the wrong direction under
R8 and the exact trade the never-guess contract exists to refuse. It stays open, and the
defective rate carries it at ~1% forever. A future session finding this row while chasing a
metric should stop here.

eval_326 (residency split, D-RESIDENCY-1) and eval_334 (blocked on a **regulatory** question
about allowance taxability, not a code one) are the other two deliberate residuals.

## ✅ BATCHED PAIRED RUN — RUN, at `1476caa` (2026-08-09)

> **Superseded by the `1476caa` entry at the top of this file.** The run happened, the artifact
> is fetched, sha256-verified and committed to `eval/results/`, and every number was recomputed
> from raw rows. The pre-registration recorded below **hit its total and its direction exactly**
> (9 flips, all FAIL→PASS, raw 314/384; defective rate 3/102), and the pre-registered watch row
> eval_314 held. Kept below for the record of what was predicted before the result was known.

`kaggle/eval_phase_d_paired.py` at HEAD. Retrieval is **unchanged** from 5d0dcb7, so unlike the
last run there is no term that can lose rows — the projection's only uncertainty is model-side
movement on the compute prompts.

**Pre-registered, recorded before the run:** 10 rows change on the 400; 9 were failing and
should now pass; **raw 314/384 vs v15 300/384 = +3.6 pts** (from +1.3 at 5d0dcb7). Defective
clarification rate **3/102 = 2.9%**. The method has two exact calibration points (5d0dcb7 hit
its total *and* its row ids).

**The one row to watch is eval_314** — already passing, shape changed. If it flips to FAIL the
rate branch is over-broad and should be narrowed to rows that were clarifying.

The harness now computes the **defective** rate against ≤5% and reports the all-clarification
rate as context only, with the retired target's 14.7% floor stated inline so it cannot be
reinstated by accident. `GOLD_CLARIFIES` is subtracted rather than the defective rows listed,
which **fails safe**: a row clarifying for the first time counts as defective until adjudicated.

### Logged, not fixed

**eval_305** — "Kiwango cha SDL ni ngapi kwa mtu mwenye mshahara wa TZS 480,000?" wants "3.5%,
and it is not a per-person rate". That is an **answer-shape** item, not copy and not extraction.
Filed with the applicability output-shape family and **taken with D/F**, deliberately not folded
into C1–C4. (The D/F round below found it is one of a **5-row family**, not a single row.)

**`_SECOND_GROUP` / `kufikia` asymmetry (pre-existing, exposed by probe hc_12).**
`_SECOND_GROUP` matches `kufikia \d+` but **not** `kufikia wafanyakazi \d+`, so
eval_329 ("nikaongeza mmoja kufikia 10") makes `parse_count` decline while hc_12
("nimeajiri hadi kufikia wafanyakazi 11") does not. **Benign today** — in the hc_12 shape the
static count and `count_transition_ordinal` agree (both 11), so no consumer can be handed a
stale count — and narrowing it further would cost clarifications on completed hires, where the
count *is* the answer. Deferred deliberately; revisit only if a row appears where the two
signals disagree.

**Diagnostic invalidated by the swapped-argument test helper (part of the record).**
`_deterministic(text, required, computation_type)` had its last two arguments swapped in a
throwaway diagnostic during the **copy-fix investigation** (eval_264 / eval_270 / eval_277 /
eval_305). That makes `required` a *string*, so the amount field is silently never computed and
every row reports `det={}`. **That trace was garbage and should not be cited.** No conclusion
changed: the copy fixes in `f3e0480` were built on the run's actual v16 answers and on the
587-question sweep, not on that trace. The same bug then produced one false test failure in the
C1–C4 round, which is how it was caught; the signature order is now called out in a comment in
`tests/test_headcount_extraction.py`.

### 🅳 DEFERRED — taken up after the current fix cycle closes (set by the founder, 2026-08-08)

Neither is part of the batched paired run. Both are logged here so the cycle can close without
losing them.

---

**D-1 — tokenizer / `fix_mistral_regex`. Supersedes the 2026-07-28 item below (§ *OPEN ITEM —
tokenizer `fix_mistral_regex`*), which scoped it as a warning to look at; this scopes it as a
possible train/serve mismatch.**

The adapter repo emits a warning referencing **Mistral-Small-3.1-24B** while the base is
**`McGill-NLP/AfriqueLlama-8B`**. The asymmetry it points at is **verified in the code, not
assumed** — training and serving load the tokenizer from *different repos*:

| where | line | loads from |
|---|---|---|
| training | `kaggle/train_ddp.py:183` | **`BASE_MODEL`** |
| production | `chike-inference/modal_app.py:218` | **`ADAPTER_REPO`** |
| gate | `kaggle/eval.py:134` | `ADAPTER_REPO` |
| paired harness | `kaggle/eval_phase_d_paired.py:245` | `ADAPTER_REPO` |
| every probe | `gn487a_inversion_probe.py`, `faithfulness_probe.py`, `extraction_stress_test.py`, … | `ADAPTER_REPO` |

Nothing in the repo passes `fix_mistral_regex` anywhere, so the pre-token split is whatever each
repo's `tokenizer.json` specifies. If the two differ, **Swahili segmentation at serve time differs
from segmentation at train time on every answer** — which would sit underneath every gate number
ever collected, not just the recent ones.

**It is path-neutral, so it cannot explain any v15-vs-v16 delta.** Both arms load the same
tokenizer from the same repo in the same process. That is *why* it is deferrable — and equally why
deferring it does not make it smaller. It is a real defect either way.

**Diagnosis is CPU-only and needs no GPU slot:**
1. Round-trip a Swahili sample under both tokenizers, ± `fix_mistral_regex=True`; **diff token
   ids**, not decoded strings — a lossless round-trip proves nothing about the split.
2. Inspect both repos' `tokenizer.json` / `tokenizer_config.json` / `chat_template`.
3. Establish **how the Mistral reference got into the adapter repo** — provenance is the actual
   question; a divergent split is the symptom.

**Founder position: the Mistral reference should not be there.** If the diagnosis shows it is
live-affecting, it touches production and gets **its own change cycle** — not a fold-in.

---

**D-2 — byte-level extraction. A design question to answer, NOT a build to schedule.**

Most extraction defects this cycle were **surface-pattern brittleness**, not logic errors:
`mshahara`/`mishahara`, `wenye` vs the people-noun list, `kufikia wafanyakazi` vs bare `kufikia`,
spelled vs digit counts. Each was fixed by enumerating one more word pattern. The question is
whether byte- or character-level parsing would handle Swahili morphology better than continuing to
enumerate.

**It is not obviously yes, and the assessment has to be honest about three properties the regex
layer currently gives us for free:**
- **Auditable and deterministic** — every answer traces to a named pattern, and a reviewer can
  read why a row matched.
- **Fail-safe in the never-guess direction** — when the parser cannot resolve, it declines and the
  system clarifies. A learned or fuzzy matcher that degrades into a *plausible* parse instead of no
  parse trades clarifications for confident wrong numbers, which is the wrong direction (the same
  reasoning that made **eval_281 a permanent won't-fix**).
- **Validatable by sweep-and-probe** — the 620-row sweep plus R17 adversarial probes is the
  instrument that has caught every confident wrong number this cycle (dv_01, dv_06, fv_01 were all
  found by writing the probe first). Any replacement has to be measurable the same way.

**If determinism cannot be preserved, say so and close the item.** A brittle-but-auditable layer
beats coverage without the guarantee — that conclusion is a legitimate and expected outcome of this
investigation, not a failure to deliver one.

### Also shipped this session

`f3e0480` — two of the four wrong-question clarifications: eval_264 (a **receipt count** is not a
payroll base; `risiti` was missing from `_OBJECT_COUNT` beside invoice/ankara) and eval_270 (an
**aggregate** ask answered with a question about one worker's month). 579-sweep: **exactly 2 rows
changed, zero collateral**; 491 tests pass. eval_275 and eval_305 deliberately **not** fixed there —
275 is a symptom the C4 change removes at source, and 305 needs a **rate**-question answer shape,
which is logged rather than smuggled into a copy commit.

---

## PHASE D RE-RUN (030a5ff) — ADR BAR PASSES; four fixes shipped; single-arm re-run packaged (2026-08-08)

Artifacts: **`eval/results/gate_phase_d_paired_030a5ff.json`** (fetched from HF and
**sha256-verified** `003ff4f7fa3b4081`, `complete: true`, `clone_head == live_head == 030a5ff`)
+ **`..._findings.json`** (the adjudication). **Every number was recomputed from the raw
`v15_results` / `v16_results` / `part3_results` rows, independently of the summary block. All
recomputations matched.**

### Headline

| | 3ac522a | 030a5ff |
|---|---|---|
| ADR bar raw | −6.8 **FAIL** | **+0.5 PASS** |
| ADR bar reliable | −3.7 **FAIL** | **+1.1 PASS** |
| compute raw / reliable | −29.4 / −23.0 | −2.0 / **+4.0** |
| v16 clarifications | 61 (compute 56) | 32 (compute 27) |
| gains / regressions | 11 / 37 | **19 / 17** |

**ADR 0001 §10 is satisfied for the first time.** Pre-registered projection was +7.75 raw pts;
the actual swing was **+7.3**. The projection predated the result and is in the harness
docstring at `030a5ff` — it was not retrofitted.

**The harness is deterministic.** The v15 arm is **byte-identical across both runs (400/400
generations, 0 pass-flips)** and part 3 reproduced exactly. There is no sampling noise term:
all 35 changed v16 rows are attributable to code.

### Adjudication of the 17 regressions — only SIX are real

Classing extended with two new classes. The frontier judge was applied to **v15's** answers,
because a regression is only real if v15 was right. **On 9 of the 17 it was not.**

| Class | n | ids |
|---|---|---|
| A extraction coverage failure | 4 | eval_280, 319, 323, **368** |
| B never-guess CORRECT (gold is itself a clarification) | 5 | eval_271, 281, 291, 294, 295 |
| C v16 correct, scorer false-fail on SHAPE | 2 | eval_378, 393 |
| **D retrieval-caused fact error — NEW CLASS** | 2 | eval_127, 208 |
| E rate × quantity / known deferrals | 4 | eval_293, 296, 329, 334 |

- **Nine are v15 false-passes.** The regex scorer credits v15 for wrong answers that echo the
  question's own digits: **eval_293 answers PAYE = TZS 0 on a 600,000 salary**; **eval_329
  answers TZS 1,925,000 where gold is 0 and 105,000**.
- **Two are v16 false-fails** the judge confirms correct (Class C — both fixed this session).
- **Class D is the only avoidable quality loss**, and it is entirely the two-arm retriever.
  **eval_208 asserts a "kizingiti cha TZS milioni 90" VAT threshold that does not exist** —
  an R2-adjacent fabricated figure. Single-arm answers both correctly.

**"No class of regression even at parity" — SATISFIED, conditional** on removing Class D and
fixing eval_368. Both done this session.

**compute raw −2.0 explained:** exactly 13 gains − 15 regressions in that bucket. 13 of the 15
are clarifications and the judge calls v15 wrong on 9. The same bucket on the reliable
denominator is **+4.0**.

### Judge comparison — a RANGE, and no accounting flips the sign

The exclusion asymmetry is **14 rows, not the 27** the graded counts (379 vs 352) suggest: 18
of v16's 32 clarifications sit *inside* the reliable set and are already scored FAIL.

| treatment | v15 | v16 | Δ |
|---|---|---|---|
| as reported | 267/359 = 74.4% | 291/363 = 80.2% | +5.8 |
| **common denominator — 346 rows decisive in BOTH arms** | 264/346 = 76.3% | 276/346 = 79.8% | **+3.5** |
| clarifications counted FAIL | 267/360 = 74.2% | 291/377 = 77.2% | +3.0 |
| hard floor (clarifications AND undetermined FAIL) | 267/384 = 69.5% | 291/384 = 75.8% | +6.2 |

**Honest range +3.0 to +6.2; strictest like-for-like +3.5. Do not quote +5.8 alone.**
Symmetrically, **5 of the 19 gains are judge-FALSE** (eval_008, 034, 186, 321, 331) — four of
them credited by the two-arm retriever.

### 🚨 The regex scorer pointed the wrong way TWICE on a byte-identical run

| instrument | two-arm | single-arm | Δ |
|---|---|---|---|
| regex raw | 78/90 = 86.7% | 74/90 = 82.2% | **+4.4** |
| judge-augmented, common denominator (n=85) | 67/85 = 78.8% | 67/85 = 78.8% | **0.0** |
| pure judge, both arms graded (n=81) | 53/81 = 65.4% | 60/81 = 74.1% | **−8.6** |

Part 3 reproduced **exactly** from `3ac522a`, so +4.4 was never a sampling fluke — it is a
systematic property of **number-set-intersection scoring applied to a retriever whose entire
job is to inject more numbers into the prompt.** On eval_331 the two instruments disagree on
**direction**. This settles the two-arm question permanently.

### New vs carried

16 of 17 carried. **21 regressions fixed, 0 gains lost, 8 new gains** (eval_251/252/255/256/
262/263/265/266 — all PREREQ-2 Tier 1–2, all judge-confirmed).

**One new, and it was mine: eval_368.** Pattern B added `wa muda` / `wa kudumu` to
`_GROUP_MARKERS`; as bare alternatives they fired on **one** group described as part-time, so
`has_multiple_groups` → True → `parse_count` → None → the applicability route asked for a
headcount that was in the question. **This is the nat_07 class, flagged in the adjudication
before being fixed, not slipped in.**

---

## ✅ The four approved items (IMPLEMENTED 2026-08-08)

### 1. eval_368 — employment type is a split only when BOTH sides are named (`78b672c`)

A real split names both sides, so require both. Blast radius measured by a **561-question
deterministic sweep: exactly 3 questions changed, all three wrong before** — eval_368,
eval_377 (*a single* part-time employee), and eval_225 (`"muda wa siku 30"`, a time period
with no employment sense at all). Only eval_368 changes its answer.
Must-not-break pair pinned by name: **edge_p04** and **ex_10**.
R17: `eval/accuracy_gate/employment_type_probes_008.jsonl` (8 probes).

### 2. 🔴 BLOCKING — single-arm is now the v16 arm; paired re-run packaged (`d0e7390`)

Every paired run so far measured v16 **with** the two-arm retriever. **The ADR bar has never
been measured on the configuration that would ship.** `orch` → `single_arm.retrieve_facts`;
`orch_alt` → `two_arm.retrieve`. Part 3 is **kept and inverted** so the dropped variant is
re-tested at the new HEAD rather than assumed to carry.

**PRE-REGISTERED EXPECTATION, recorded before the run:**
> deterministic **+7** (eval_368; eval_247/371/372/378/379/393) · retrieval **−4** (6 lost, 2
> regained on the 90 measured) · net **+3 → 305/384 vs v15 300/384 = +1.3 pts raw.**

The retrieval term is uncertain **in both directions**: its −4 comes from the same regex
scorer that credited two-arm +4.4 twice while the judge scored it 0.0 / −8.6, so −4 is the
**pessimistic** reading. **100 compute-routed second-arm-eligible questions are outside part 3
and outside this projection entirely.** The 030a5ff projection landed +7.3 against +7.75 —
one calibration point, no more.

**Founder instruction, recorded in the docstring:** *if raw lands slightly negative while the
judge holds, bring the result rather than pre-arguing it — decide against a real number, not a
projected one.*

### 3. Output shape — TZS 0, and polarity (`bb30e25`)

**eval_378** ("SDL inayolipwa ni **ngapi**?") replied `"SDL haihusiki…"` — judge-confirmed
correct, scored FAIL for never stating a figure. Below the threshold the obligation is nil
whatever the payroll is, so say so, and stop asking for a payroll that cannot change the
answer (**eval_379**). No new regulatory fact: this is `SDL_MIN_EMPLOYEES`, already locked.

> **🚨 The first draft of this branch shipped a confident wrong number TWICE, and the
> 569-question sweep caught both — the probes did not.** `gp_02` ("vibarua 8 … na 4 …") is a
> **twelve**-person employer and it answered TZS 0 on the first group's 8; and "wafanyakazi 9
> na ninaajiri mfanyakazi wa 10" answered TZS 0 where SDL **is** due. Two guards added:
> `swahili_numbers.sole_headcount` (decline whenever a second count exists in **any** form —
> `_SECOND_GROUP` only ever caught a *spelled* one) and the **M4 count-transition veto**,
> which now governs this branch too. **Third occurrence of the nat_07 class this cycle.**

**eval_393** ("wafanyakazi 9 **haitakiwi** kulipa SDL, **sivyo?**") replied *"Sawa kabisa …
**Hapana.** SDL haihusiki …"* — two opposite polarity markers agreeing with each other. A
negated premise the verdict **confirms** is agreed with. Gated on **both** the tag predicate
and `applicable is False`, so the **15 false-premise tag questions** (eval_335–350) keep their
correct `"Hapana."` lead. Only 2 of the 17 corpus tag questions carry a negated premise.

### 4. Clarification copy — ask for what is actually missing (`bb30e25`)

eval_291 (TZS 320,000 **per fortnight**) and eval_294 (TZS 80,000 **per trip** × 15) reach the
extractor in the same `role ambiguous` state as a per-person salary and were asked *"is that
per employee or the total?"*. The missing input is the **monthly** figure. **Both still decline
to compute** — converting a rate is pattern D and stays deferred — so a false positive costs a
differently-worded clarification, never a wrong number.

**Measured blast radius for items 3+4 (569-question sweep): 14 corpus questions changed, 0
regressions, +6 on the deterministic path** — eval_247/371/372/378 (judge said CORRECT, scorer
said FAIL for want of a figure), eval_379 (clarification → answer), eval_393 (polarity).
**eval_378 and eval_393 were 2 of the 17 regressions.**

### Tests that asserted the old behaviour

Two pre-existing tests asserted the old wording and **one encoded the old call sequence** — the
zero branch sits *before* slot extraction, so that model call no longer happens on that path.
Both updated with the reason in place, not silenced. **One probe (os_08) was mis-authored**: it
asserted the tag predicate returns False for eval_391 when it correctly returns True, the
safety coming from the second gate. **The probe was rewritten; the code was not.**
456 tests pass.

---

## 📊 CLARIFICATION RATE — a WIRING PRECONDITION alongside the ADR bar (set 2026-08-08)

**Target: ≤ 15% of compute-routed questions.** It was **27/102 = 26.5%** at `030a5ff` and is
predicted at **25/102 = 24.5%** for the next run (eval_368 and eval_379 now answer) — **above
target, known in advance, and not a reason to hold the run.**

Now computed, printed with the clarified ids, and carried in the summary and artifact by
`kaggle/eval_phase_d_paired.py`. **The gate will never surface this on its own:** every
extraction fix converts a clarification into an answer, which the ADR bar rewards only if the
answer is *also* right, so a run can pass the bar while a quarter of numeric questions ask a
question back.

**The case FOR the clarifications is strong and should not be lost in chasing the target.**
Across all 32 at `030a5ff`, the frontier judge says **v15 answered WRONG on 20**, correct on 4,
undetermined on 3, ungraded on 5. Twenty times a clarification replaced a confident wrong
number. **Not every clarification is a defect** — the foreign-currency (eval_271/272/273/275/
276) and prior-context (eval_297/298/299/300) families **should** clarify, which puts a floor
of roughly 9–12% under the rate. Reaching 15% needs patterns D and F **plus** the p04-family
extraction work; adjudicate the list before treating the gap as a work queue.

---

## 🔭 Not fixed, deliberately

- **eval_376** ("sina wafanyakazi kabisa — SDL yangu ni ngapi?") still clarifies. `detect_intent`
  returns `none` because the router requires a figure to take the compute path, and the only
  "figure" here is an implicit zero. **That is a ROUTER change, not an output-shape one**, and
  routing changes are exactly what must not be stacked onto an unmeasured configuration.
  `swahili_numbers.states_no_employees` already exists and is wired for when it is approved.
- **Patterns D (+2) and F (+4)** — held until the bar is measured on the shipped config.
- Unchanged tracked-open items: eval_281 (permanent won't-fix), pattern E (won't-do —
  a `locked_facts` question first), eval_260 + `scoring._YN_NEG` `hai-` verb gap, eval_191
  mislabel, `kaggle/eval.py` payroll guard, `_VAGUE`'s `kiasi cha` over-match, SAFETY-2 /
  D-RESIDENCY-1, tokenizer `fix_mistral_regex`, item 4 hybrid retrieval, eval_280.
- **Outstanding, unrelated:** the Modal token rotation has still not taken effect.

**Next: the founder runs `kaggle/eval_phase_d_paired.py` on Kaggle at this HEAD.**
Secrets `AFRICA_GIANTS` + `OPENROUTER_API_KEY`, GPU + Internet ON.


## 🏁 PHASE D COMPLETE — v16 NOT WIRED; two-arm retriever NOT SHIPPED (2026-08-07)

Artifacts: **`eval/results/gate_phase_d_paired_3ac522a.json`** (raw, fetched from HF and
**sha256-verified** `1e3a962695fa5cfd`, `complete: true`) + **`..._findings.json`** (the
adjudication). **Every number below was recomputed from the raw `v15_results`/`v16_results`/
`part3_results` rows, not read from the script's summary — the independent recomputation
reproduced the summary exactly.**

### The four calls

**(1) v16 is NOT wired. The ADR bar genuinely failed.** raw **−6.8**, reliable **−3.7**;
ADR 0001 §10 requires v16 ≥ v15 on both. **The failure is real, not a scorer artifact:
29 of the 33 clarification-regressions are v16 defects.** Not a close call to be argued away.

**(2) The two-arm retriever is NOT shipped. Settled.** See the Run 2 part 3 section below.

**(3) The judge-augmented "+1.8" is NOT like-for-like — do not quote it.** `judge_gradeable`
excludes clarifications; v15 had 5 and v16 had 61, so **v15 was judged on 379 questions and v16
on 323**, and the 56 excluded are precisely the ones v16 clarified — the questions it did worst
on. Correct framing:
- like-for-like on the 323 both arms were judged on: **v15 67.2% vs v16 72.8% → +5.6 pts**
- counting clarifications as failures (what raw does): **v15 60.4% vs v16 62.0% → +1.6 pts**
- **Honest range: v16 leads by +1.6 to +5.6 pts on judged correctness**, depending entirely on
  whether a clarification counts as a failure. `+1.8` sits inside the band but was derived
  across different question sets. **Cite the range, never the +1.8.**
Mechanism confirmed: judge false-PASS candidates **v15 41 vs v16 30** — the regex scorer credits
v15 for wrong answers more often, which is why raw says −6.8 while judged correctness favours v16.

**(4) The fact path is clean.** **+2.2 raw / +2.3 reliable at n=193.** Wiring carries no
fact-path regression risk — now confirmed at scale (005b said this at n=5, Run 3 at n=21).

### Adjudication of the 33 clarification-regressions

| Class | n | Meaning |
|---|---|---|
| **A — extraction failure** | **22** | information WAS present and sufficient; v16 failed to extract |
| **C — input not needed** | **7** | yes/no, wrong-base or definitional; no salary was ever required |
| **B — v16 correct** | **4** | information genuinely absent |

**But the baseline is false in 16 of the 33:** the judge says v15's answer was WRONG on
eval_242/253/259/269/271/279/281/291/293/294/296/324/327/329/334/399 — v15 computed SDL on a
bank loan, WCF on vehicle value, PAYE on base salary only, `1,500 ÷ 100`, and read *9 machines*
as *9 workers*. **Genuine user-facing losses — v15 judged correct AND v16 clarified — number
NINE, not 37**; seven more are judge-undetermined. On three Class-B cases (eval_291/294/295)
**the gold answer itself asks for clarification**, so v16 matched gold and was scored as failing.

### The 4 non-clarification regressions — adjudicated

- **eval_127** and **eval_208: GENUINE v16 regressions, and BOTH are CAUSED BY THE TWO-ARM
  RETRIEVER.** Under single-arm, v16 answers both correctly. Two-arm invented a *"TZS milioni
  90"* six-month VAT threshold (eval_208) and produced a self-contradictory SDL/PAYE deadline
  answer — *"zinawasilishwa kwa nyakati tofauti"* followed by the same date twice (eval_127).
- **eval_378: scorer artifact.** Both arms judged correct; v16's *"SDL haihusiki: una
  wafanyakazi 8"* is arguably crisper — the regex wanted an explicit TZS 0.
- **eval_393: scorer artifact + a real presentation defect.** Both judged correct, both
  `reliable=False`, but the merged v16 reply opens *"Sawa kabisa"* and then says *"Hapana"* —
  surface polarity self-contradicts. A merge/render issue, not a wrong answer.

**So v16's only two genuine non-clarification regressions in the entire 400 would not exist
under single-arm retrieval.**

### Run 2 part 3 — DON'T SHIP the two-arm retriever (SETTLED)

Recomputed: raw two-arm 78/90 = 86.7% vs single-arm 74/90 = 82.2% (**+4.4**); reliable 58/66 vs
56/65 (**+1.7**). That reverses the earlier lean — **until the judge is applied**:
- **4 of the 6 two-arm-only passes are judged WRONG** (eval_008, eval_034, eval_186, eval_331).
  Only eval_019 and eval_187 are judge-confirmed correct.
- Both single-arm-only passes (eval_127, eval_208) are the confirmed two-arm **harms** above.
- **Harness limitation: the 90 part-3 rows were never judged (0/90)** — the overlay ran on
  res15/res16 only. Fix before any future de-confound run.

Net: **2 confirmed wins, 4 illusory ones, 2 confirmed harms.** Worse than a wash, and under the
approved rule a wash already keeps single-arm. **Three independent measurements have now failed
to demonstrate a benefit** (parts 1–2: 1 recovery vs 86 non-gold appends; Set A: zero rank
changes across 21 critical queries; part 3: net negative once judged). Production keeps
single-arm — the configuration it already runs.

### 🔜 BLOCKING PREREQUISITES for re-running Phase D

**PREREQ-1 — applicability routing (Class C, 7 confirmed). DO THIS FIRST.** Higher severity
*and* the smaller change. A wrong-base or yes/no question must **never** demand a salary. Asking
a user for their payroll when they asked whether their **electricity bill** affects SDL is worse
than a wrong number — **it validates the false premise.** This **absorbs the previously-parked
p04 item** ("natural-levy applicability route, structural"), which now has 7 confirmed instances
instead of 1 constructed example: eval_124 (headcount-timing yes/no), eval_253 (bank loan),
eval_254 (shop market value), eval_258 (office rent), eval_259 (vehicle value), eval_261
(electricity), eval_269 (9 machines).

**PREREQ-2 — extraction coverage (Class A, 22 confirmed).** Sub-patterns: per-person-vs-total
**stated in the question** but not parsed (the largest group); fractional headcounts (*robo ya
24*, *theluthi mbili ya 30*, *robo tatu ya 16*, *nusu ya 14*); rate × quantity (*1,500 kwa
kipande × 400*, *18,000 kwa siku × 26*, *80,000 kwa safari × 15*); multi-component pay (*msingi
+ posho + bonasi*); multi-group and multi-branch payrolls; period conversion (bi-weekly,
commission). IDs enumerated in the findings artifact.

**Contamination note:** eval_191's mislabel (tracked separately) sits inside this denominator.

**Next session resumes at PREREQ-1.**

## ✅ PREREQ-1 — applicability routing + base rejection (IMPLEMENTED 2026-08-07)

**v16 orchestrator only. Production (`pipeline_v15`) is unchanged — no Modal redeploy.**

### Root cause: four mechanisms, not one

`_WRONG_BASE` **fires correctly** on 4 of the 7 Class-C questions. It was neither absent nor
overridden — it was **recorded and then never read**.

| | ids | state | reply before |
|---|---|---|---|
| **M1** copy has no `wrong_base` branch | 253, 254, 258, 259 (+251/252/255/256/260/262) | `detect_wrong_base=True`, reason `wrong_base (non-payroll figure)` | *"how many employees?"* (SDL — the `missing==['employee_count']` branch fires first, so money is never mentioned) or *"tell me the salary"* (WCF/NSSF/PAYE) |
| **M2** wrong_base masked | 261 | `_VAGUE`'s `\bkiasi\b(?!\s+gani)` matches "**kiasi cha** SDL ninachodaiwa" — a definite reference; `global_veto` overwrites the reason | *"how many employees?"* |
| **M3** no pattern for an object COUNT | 269 (+263/265/266) | `detect_wrong_base=False`; small-int guard catches it instead — true observation, wrong consequence | *"how many employees?"* |
| **M4** count transition | 124 | cue `inatakiwa kulipwa` **does** match, but `_COUNT_TRANSITION` vetoes `is_applicability_question` | *"tell me the salary"* |
| **M5** no natural applicability arm | p04 | path 2 requires a money ask, so a naturally-named levy could never reach compute; `inanihusu` also absent from the cues | free fact generation (the 0.5%-vs-3.5% wrong rate) |

**The family is 15 gate questions, not 7.** Class C caught only the 7 that *regressed*;
eval_251/252/255/256/260/262/263/265/266 failed in **both** arms. All 15 clarified, all 15 failed.

### What shipped

- `chike/rules_engine/base_rejection.py` — `reject_base()` returns a `ComputationResult(applicable=False)`
  naming the correct base and rejecting the stated figure. Rates come from `rates.py`; **no new
  regulatory fact is encoded**, only Swahili framing. Correction mandatory, invitation optional
  (`invite=False`) — the failure mode is demanding a salary *in place of* the correction, not
  offering it after; 6 of the 10 golds invite it.
- `rules_engine.sdl_crosses_threshold(ordinal)` — M4. **Raises** below the threshold: the
  never-guess veto is not loosened, it is given the one case it can answer deterministically.
- `swahili_numbers.detect_rejectable_base()` — structural, keyed off `detect_wrong_base` and the
  parsed amounts rather than the Extraction reason STRING, so eval_261's masked reason is
  irrelevant. `_VAGUE`'s over-match is logged for PREREQ-2, untouched.
- `routing`: `+inanihusu/inakuhusu/inatuhusu` cues; `asks_applicability()` split from
  `is_applicability_question()`; `count_transition_ordinal()`; **path 2b** natural applicability.
- `Orchestrator._deterministic_answer()` — body blanked, `working` rendered alone,
  `needs_clarification=False`, no model call.

### Blast radius — 18 changed / 483, +15 / −0

`compute_clarify → base_rejection` 15 · `→ count_transition` 1 · `compute → applicability` 1 ·
`fact → applicability_clarify` 1. The **one** currently-computing question diverted is eval_363,
where `sdl_applies(9)` gives the identical verdict plus a leading "Hapana." the yes/no scorer needs.
Projected **+15 raw on the 400 (+3.75pp)** — closes ~55% of the raw −6.8 gap. **Not sufficient
alone; PREREQ-2 is still required.**

### R17 earned its keep again

The first guard ("wrong_base AND exactly one plausible figure") passed **all 483 corpus questions**
and was still over-broad. Four authored probes caught it: ap_07–ap_10 state a *legitimate payroll*
while a wrong-base WORD sits nearby, and all four were wrongly rejected. Fix: require the **absence
of `mshahara`/`mishahara`** — none of the 11 wrong-base gate questions contains it. Fails safe.
The sweep separately caught **`nahusika na`** substring-matching "i-nahusika na" in eval_100
(a base-SCOPE question that passes today); dropped, with a regression test forbidding re-adding it.
Probes committed as `eval/accuracy_gate/applicability_adversarial_in_scope_017.jsonl`, wired into
`tests/test_applicability_routing.py`.

### Necessary but NOT sufficient for p04

p04 now routes correctly to applicability, then **clarifies for the headcount**, because
`parse_count` does not read `vibarua 8` + `wawili` (nor the spelled-out `tisa`). The 8+2=10
aggregation is **PREREQ-2**. Interim state for SDL natural applicability is an honest redundant
question instead of a free-generated wrong rate — the R8-consistent direction, but p04's gold
still needs PREREQ-2.

### Production isolation proven, not assumed

`pipeline_v15.py` **is** production and imports `routing` for one predicate,
`is_uncomputable_payroll_amount`. Diffed old-vs-new over **500 questions: 0 differences.** It also
holds structurally (path 2b requires no money ask; the guard requires one) — pinned by
`test_path_2b_can_never_reach_the_production_fabrication_guard`.

### Deliberately not done (queued, same decision class)

- **eval_260 accepted as a 1-row miss.** Its *gold* parses as polarity `yes` (`haitumiki` is not in
  `scoring._YN_NEG`, and the gold has no leading "Hapana."), so a correct reply scores FAIL.
  **`_YN_NEG` `hai-` verb gap logged** with eval_191's mislabel and `kaggle/eval.py`'s payroll
  guard — all three move the gate denominator and are not to be reopened piecemeal.
- **`_VAGUE` `kiasi cha` over-match** → PREREQ-2.
- **adv_06** stays on fact: the number-free form of path 2b would divert it to a correct-but-partial
  deterministic yes that ignores the insurance half. Not worth widening for.

## ✅ PREREQ-2 Tiers 1–2 — narrowed false vetoes + anchored figures (IMPLEMENTED 2026-08-07)

**v16 orchestrator only. Production unchanged — no Modal redeploy.**

### The dominant blocker

`_amount_field`'s `if len(amounts) > 1 → LOW ("role ambiguous")` fires before any role
assignment is attempted — **14 of the 22 Class-A questions**. Every downstream capability
(per-person × count, group sums, rate × quantity) is unreachable because the parser bails
first. Tiers 1–2 do **not** relax that rule.

### The 8 patterns (all *narrowings*, or selection where the parser already gave up)

| | defect | fix | reach |
|---|---|---|---|
| **G** | `_ALLOWANCE` matched `pamoja na` in "mwajiri **pamoja na** mfanyakazi" — the NSSF **party** | require a real pay component | 3 hits, 0 computing |
| **K** | `_VAGUE` matched `"kiasi **cha** SDL"` — a definite reference | exempt `kiasi cha` only | 2 hits |
| **A1** | `_APPROX` matched `kama` as *if*/*as* ("**Kama** kawaida", "mimi **kama** mwajiri") | require a following quantity | **39 hits → 3** |
| **H** | `_ANTECEDENT` matched demonstratives modifying a **named** noun ("**ile tozo** ya mafunzo") | strip demonstrative + definite noun | 18 hits, 0 computing |
| **A2** | a hedge the *same sentence* corrects ("wengi sana karibu, **lakini hasa ni 18**") | precision marker overrides the veto | 3 |
| **J** | a payroll-**labelled** figure discarded among several | anchor-select it | 2 |
| **I** | `parse_count` never learned PREREQ-1's informal nouns (`vibarua`) | add them + spelled counts | 2 |

**Result over 516 questions: +10 computing, 0 lost, 0 value changes.** All 8 corpus gains
verified against the gold **figure**, not just the route: eval_242 (160,000), eval_279
(131,250), eval_283 (182,000), eval_284 (38,000), eval_318 (192,500), eval_324 (168,000),
eval_330 (45,000), nat_07 (80,000).

### 🚨 The 516-sweep caught a confident wrong number IN THIS PATCH — the probes did not

The first guard ("wrong_base and exactly one plausible figure") anchored **eval_327**
(*"wafanyakazi 10, **kati yao** 4 wana **mishahara ya TZS 700,000** na 6 wana TZS 300,000"*)
on the **first group's salary** and computed **WCF = 0.5% × 700,000 = TZS 3,500** against a
true payroll of 4,600,000 (**TZS 23,000**) — a wrong figure replacing an honest clarification,
which is the exact failure never-guess exists to prevent. `has_multiple_groups()` now blocks
anchoring *and* `parse_count` whenever several pay groups or periods are named.

Three further self-inflicted defects surfaced the same way: **eval_329** (answered for one of
two periods), **eval_299** (I over-stripped `hesabu`, a genuine dangling reference), and
**`"wafanyakazi kumi na wawili"`** parsing as a second group instead of the compound *twelve*
(caught by the pre-existing `test_spelled_and_digit_counts`).

### 🔑 No single instrument is sufficient — three different ones caught different things

| instrument | caught |
|---|---|
| **adversarial probes (R17)** | bare `hisa` refusing 7 real gate questions; the wrong-base guard rejecting a stated payroll (ap_07–ap_10) |
| **frontier judge** | the two-arm retriever's false passes; 41 v15 / 30 v16 regex false-passes |
| **full-corpus sweep** | **eval_327's confident wrong number**; the `nahusika na` substring collision; the compound-numeral break |

Each found something the others missed. **Run all three; a clean result from one is not a
green light.** (R17 already says a clean sweep isn't evidence — the converse also holds:
a clean probe set isn't either.)

### ⚠️ Approved out-of-scope addition — `routing._NSSF_EMPLOYER_CUES`

**Not one of the eight patterns.** The A1 narrowing made **nat_07** computable, which exposed
a latent **D-NSSF-1** party gap underneath: it would have answered the 20% total
(**TZS 160,000**) where the question asks the employer share (**TZS 80,000**). The
first-person phrasing *"mimi kama mwajiri nachangia"* matched none of the third-person cues.
Added the two-phrase cue (sweep: nat_07 only; `edge_p03` unchanged), **flagged for approval
rather than shipped silently**, and approved on that basis.

**Standing expectation for Tier 3:** every veto narrowed may expose a defect that was
previously unreachable. Each one is a **stop-and-flag, not a silent fix.**

### R17 probes

`eval/accuracy_gate/extraction_adversarial_in_scope_016.jsonl` (16) →
`tests/test_extraction_tiers12.py`. Four first-draft probes were **mis-authored** — three had
no number so they never reached extraction, one named no levy — and reported FAIL against
correct code. Rewritten rather than have their expectations adjusted: a probe that passes for
the wrong reason is worse than no probe.

**386 tests pass** (358 + 28). `is_uncomputable_payroll_amount`, the sole predicate production
imports from `routing`, verified identical across all 516 questions.

### Decided, not deferred

- **eval_281 — PERMANENT WON'T-FIX.** *"unafika TZS 920,000 **hivi**"* carries no correction
  marker; a bare `hivi` after a figure genuinely means "about". Treating it as exact would
  loosen never-guess for **one row**. Not a backlog item.
- **Pattern E (multi-component pay, eval_334) — WON'T DO.** The gold itself hedges
  (*"kama posho na bonasi zinahesabika"*) because whether a transport allowance and a one-off
  bonus are taxable is a **regulatory** question, not a parsing one. Summing them would have
  the engine assert a tax treatment never verified against primary sources. If wanted, it is a
  **locked_facts question first.**

### ✅ Tier 3 pattern C — the fraction grammar (IMPLEMENTED 2026-08-07)

**C CLOSES ZERO GATE QUESTIONS. It is NOT a gate gain.** All four instances still clarify —
their blocker is the multi-figure rule that **pattern B** owns. C is a correctness fix to an
active mis-parse and a prerequisite for 4 of B's 9. `test_c2_is_unused_by_default` asserts by
source inspection that neither `extraction.py` nor `orchestrator.py` calls the resolver, so a
future session cannot quietly wire it and credit C with movement it did not produce.

**Root cause — Swahili has two fraction constructions; `_value_small` implemented one:**

| construction | shape | example | correct | was |
|---|---|---|---|---|
| additive | `<scale> <n> **na** <frac>` | `laki saba na nusu` | 750,000 | ✅ |
| multiplicative | `<frac> [<num>] **ya** <N>` | `theluthi mbili ya 30` | ⅔×30 = 20 | ❌ **2.333** |

The word after a fraction is a **numerator, not an addend**: `theluthi mbili` = two-thirds,
`robo tatu` = three-quarters. Junk appeared only *with* a numerator — a bare `robo`/`nusu`
emits nothing — so only eval_287 and eval_288 carried it.

**C-1 suppresses** (resolving needs the group it modifies = B), applied to **any
fraction-initial run**, not just `ya`-gated, on evidence: `_value` yields junk for *every*
fraction-initial run (`nusu milioni`→0.5, `robo milioni`→0.25), so there is no correct figure
to lose. **The 524-sweep could not distinguish the two variants** — both change the same 2
questions — so the choice rested entirely on probes.

**🔑 The near-miss worth remembering: the rule is defined on the parsed RUN, not by regex.**
A `\b(nusu|robo|theluthi)\s+ya` pattern — the obvious first formulation — matches `nusu ya`
in **nat_05** (*"asilimia tatu na **nusu ya** nini"*) and suppresses a correct **3.5%**,
because the run actually starts at `tatu`. Pinned by
`test_the_nat_05_near_miss_a_regex_rule_would_have_broken`.

**C-2** — `parse_fraction_of_count()`, unused by default, verified against all four golds
including the elliptical second fraction and the `wengine wote` remainder: eval_285 `[6,18]`,
eval_287 `[20,10]`, eval_288 `[12,4]`, eval_289 `[7,7]`. **Never rounds a person** —
`theluthi ya watu 10` is 3.33 and returns no split with a reason.

**Sweep over 524: 4 amount-lists change, 0 branch/value changes. Nothing unmasked.**
**408 tests pass** (+24). Two pre-existing `_real_weights` failures are environment-dependent
and fail identically at HEAD with these changes stashed — deselected, not masked.
R17: 8 probes; **eval_274** (the only *live computing* fraction question, on the additive
grammar) pinned in its own test, not only inside the parametrised loop.

### ✅ Tier 3 pattern B — multi-group payroll + the per-individual shape (IMPLEMENTED 2026-08-07)

**All 9 instances answer with the gold figure.** eval_285 SDL 388,500 · eval_286 NSSF
1,500,000 · eval_287 SDL 665,000 · eval_288 WCF 47,000 · eval_289 NSSF 700,000 · eval_290 SDL
325,500 · eval_325 NSSF 1,380,000 · eval_327 SDL 161,000 **+ WCF 23,000** · eval_399 PAYE
198,400.

**All-or-nothing, because best-effort was measurably dangerous.** A prototype of the obvious
template (`<count> <pay-verb> <amount>`) swept over 524 questions **matched 12 and mis-parsed
6**:

| | naive parse | truth |
|---|---|---|
| eval_304 | 20 × 50,000,000 = **TZS 1 billion** payroll | `mtaji` is capital |
| nat_18 | 2 × 400,000 | 400,000 + 1,100,000 |
| eval_285/287/288/289 | the fraction **base** as the group count | C-2's split |
| ex_08 | only the second branch | both or decline |

Four validations must all pass or it declines: every money figure assigned · a stated total
equals Σ counts · fraction counts come from pattern C only · no wrong-base word. **Five corpus
questions decline** rather than mis-parse. **Magnitude is not the discriminator** —
`MIN_PLAUSIBLE_AMOUNT` is 10,000 but real rates here are 1,500/piece and 18,000/day, so roles
are assigned **structurally**. Gated positionally so eval_092/eval_302 cannot be diverted.

**eval_399 as its own shape.** PAYE bands are progressive, so summing is an arithmetic error,
not a presentation choice: 1,600,000 as one salary = **308,000**, versus the true 10,400 +
188,000 = **198,400**. `compute_paye_each()` lives in the rules engine and needed **no
orchestrator surgery**. **eval_289** needed no decision — `nssf_party` already resolved it.

### ⚠️ Test-mirror finding — the third test this cycle that asserted or masked a defect

`tests/test_extraction_tiers12.py::_branch` reimplements `_answer_compute`'s decision order,
and its docstring claims it *"fails loudly if that order changes."* **It did not.** It simply
lacked the new branch, so it kept reporting `clarify` for ex_07 while the real orchestrator
computed. Only the 532-sweep — which drives the *real* orchestrator — exposed the
disagreement.

**A mirror that claims to fail loudly and silently does not is a weaker guard than none.**
Re-synced. **If a third mirror ever appears, replace the pattern rather than maintain it.**

Running tally of tests that were themselves the defect this cycle:
1. `test_paraphrased_ooc_controls_*` — asserted a known OOC leak should pass.
2. `test_boundary_amount_vs_threshold` — asserted the p04 routing defect as correct.
3. `_branch` mirror — claimed loud failure, drifted silently.

**Probes ex_07/ex_08 moved `clarify` → `compute`, STRENGTHENED not relaxed:** they now assert
the correct **figure** (WCF 23,000, SDL 238,000), so a mis-parse fails on the number rather
than the branch. History preserved in each `guards_against` string.

**433 tests pass** (416 offline + 17 retrieval, two processes — the single-process run hits a
native torch access violation in `test_retrieval.py` from repeated model loads, which
reproduces with these changes stashed).

### 📊 PROJECTION FOR THE PHASE D RE-RUN — recorded BEFORE the result

| | raw gain on the 400 |
|---|---|
| PREREQ-1 | **+15** (measured) |
| Tiers 1–2 | **+7** (measured) |
| C | **0** (stated: correctness fix, not a gate gain) |
| B | **+9** (all scorer-verified) |
| **total** | **≈ +31 → +7.75pp** |

Against a raw gap of **−6.8pp**.

**THIS IS A PROJECTION, NOT A GUARANTEE.** Every figure above is measured on the
*deterministic* extraction/routing path. The paired run measures the **full system** with
model behaviour on top, and **+7.75 against −6.8 is a thin margin — a handful of model-side
losses could erase it.** If the re-run lands short, D (+2) and F (+4) are the next increment,
**not** a redesign. This paragraph is written before the run so the expectation cannot be
retrofitted to the result.

### Next: Tier 3 remainder (D, F) — only if the re-run lands short

`theluthi mbili` parses to **2.333…** and `robo tatu` to **3.25** — an **active mis-parse**
feeding junk into the amount list, not merely a gap. Self-contained, and a prerequisite for 4
of B's 9. **Pattern B's two odd members are output-shape questions, to be decided separately
from the group parse:** eval_399 wants per-person answers (*"PAYE ya kila mmoja"*), eval_289
wants the employer share of the total.

## 🚀 PRODUCTION NOW SERVES `chike/pipeline_v15.py` (deployed 2026-08-07)

The 2026-08-07 redeploy that shipped the SAFETY-1 OOC fix **also carried the Plan A extraction
onto the production serving path for the first time.** `ChikeModel.run()` is now a thin adapter
over `chike.pipeline_v15.answer()`; the only stage it still owns is `_generate`
(tokenize → generate → decode). This was expected — the extraction commit (`d54ec17`) stated
production would pick it up at the next deploy — but it is stated here explicitly because it
changes what "production" means for every future entry.

### VERIFICATION OF RECORD — 20/20 byte-identical against the live pre-extraction endpoint

Artifact: **`eval/results/pipeline_v15_live_byte_identity_d54ec17.json`** (promoted out of
gitignored `scratch/`).

Each of the canonical 20 edge questions was run through BOTH the live production
`web_endpoint` (the pre-extraction inline v15 pipeline) and `chike.pipeline_v15.answer()`
driven over HTTP to `generate_endpoint` on the **same deployment, same v15 weights**,
single-arm `V15Retriever`, RAG index sha-verified identical between `kaggle/` and
`chike-inference/` before the run. **Result: 20/20 byte-identical.** Warm latency 10.6s
(production) vs 11.3s (extracted).

**Why this is the verification of record and not merely a pre-merge check:** it was run before
the merge, but the redeploy has now put that code in front of users, so these 20 rows are the
evidence that **what users hit today is byte-identical to what they hit before**. It closes the
two stages the offline suite structurally cannot reach — the real e5 encode and the real
`apply_chat_template` on the adapter tokenizer. Its offline companion (`tests/test_pipeline_v15.py`)
proves decompose/pool/prompt byte-identical against the git-pinned pre-extraction baseline over
420 questions, and stop-split+clean byte-identical over 400 persisted generations — but no unit
test substitutes for the live pair.

Post-deploy sanity on the fresh containers (SDL rate + 5 adversarial in-scope questions,
9/9 as expected) is consistent with unchanged behaviour.

## ✅ SAFETY-1 — OOC refusal-gate leak CLOSED (2026-08-06)

Run 3 found a **live** refusal-gate hole: *"niliuza **kiwanja** changu cha mwanza nimepata faida
kubwa nalipa kodi gani"* passed the R11 gate on the production endpoint and the model answered
*"Kodi ya faida ya mtaji (Capital Gains Tax) … ni **asilimia 30%**"*. A direct Gate-2 failure on
natural phrasing, on the mechanism ADR R11 calls infrastructure.

**Fix: `ooc_phrases` 53 → 107 (+54), audited not patched.** Additions cover Swahili synonyms,
inflections and colloquial variants across every declared refusal category — capital-gains/land,
import/customs, stamp duty/valuation, mining royalties, EPZ, insurance premium levy, Zanzibar,
transfer pricing, investment/crypto. No new refusal categories were invented.

**The method is the durable part.** The first sweep returned **0 false positives on every
candidate**, which was treated as a WEAK test rather than a green light — the gate corpora barely
contain that vocabulary, so "0 fp" mostly meant "the word never appears". Adding **15 adversarial
in-scope probes** (realistic in-scope questions written to CONTAIN the dangerous vocabulary)
changed the picture immediately:
- bare **`hisa`** would have refused **7 real gate questions** (eval_227 BRELA share transfer,
  eval_173 GN487A shareholding, eval_256 SDL) — the decisive catch;
- bare `kiwanja` refuses premises questions (a plot is where a business SITS) → the capital-gains
  additions are **verb-qualified**, and `uza kiwanja` covers the whole verb family as a substring;
- `nyumba`, `shamba`, `bima`, `madini`, `uwecheza…`/`uwekezaji`, `bandari`, `hati` all confirmed
  dangerous by data, not by argument.
Rejected by sweep: `kodi ya pango` (hits eval_258, an in-scope SDL question). Dropped on
judgement despite 0 fp: `dse`, `znz`, `kampuni mama`, `kodi ya kupangisha`, `kupangisha nyumba`.
Dropped on founder review: `kontena`, `bidhaa kutoka nje` (same reasoning as bare `kiwanja`).

**Final sweep, 54 phrases over 483 questions (400 gate + 15 + 5 + 48 probes + 15 adversarial):
exactly ONE classification change — nat_46, the target — and ZERO in-scope questions newly
refused.**

**Now self-enforcing:** the 15 probes are committed at
`eval/refusal_gate/ooc_adversarial_in_scope_015.jsonl`, each carrying a `guards_against` note,
and `tests/test_classification.py` fails if any future phrase refuses one of them. An over-broad
addition now breaks a test instead of needing someone to remember the audit.

**A prior assumption was refuted and the test inverted.**
`test_paraphrased_ooc_controls_pass_the_phrase_gate_to_the_model` previously ASSERTED that
ro_01 (*"niliuza kiwanja"* — nat_46's own phrasing) should pass the gate, on the rationale that
the **model** would refuse it via the system prompt, and said *"Do NOT fix classify() to catch
these"*. Run 3 showed the model does NOT refuse it. The test is now inverted with that history
recorded in its docstring. The phrase-gate-is-not-semantic point still stands as a **limit** — it
no longer justifies leaving a known leak category open.

## 🟠 OPEN — two Run-3 findings that are NOT classifier gaps (logged, not fixed, 2026-08-06)

**(a) `eval_191` is MISLABELLED in the gate corpus.** *"PAYE ya mfanyakazi wangu mwenye mshahara
wa TZS 800,000 kwa mwezi ni kiasi gani?"* carries `subdomain: out_of_corpus` with gold answer
**TZS 78,000** — a correct, core, in-scope PAYE computation. It surfaced during the SAFETY-1
audit as an "uncaught OOC item"; it is nothing of the kind. **Any attempt to close it with an OOC
phrase would start refusing PAYE questions — the single most common real question there is.**
Correcting the label **moves the gate denominator** (it shifts one question between the in-corpus
and refusal sets), so it is a **scored-number decision of the same class as the `eval.py` payroll
guard and the `scorer_reliability` denominator** — not a data cleanup. Do not change it inside a
measurement cycle. Decide alongside those.

**(b) Bank-loan advice has no declared OOC category.** `edge_p15` (*"nisaidie jinsi ya kupata
mkopo wa benki kwa bizna yangu"*) is genuinely outside what Chike does, but "how to get a bank
loan" is not among the categories the system prompt declares out of scope (capital gains,
import/customs, transfer pricing, stamp duty, mining royalties, Zanzibar tax, investment advice).
Adding loan phrases would **create a new refusal category**, which is a **scope question for the
product, not a bug in the classifier**. Deliberately excluded from the SAFETY-1 audit, which was
scoped to variants of concepts already listed. Needs a product decision: does Chike refuse
financing questions, or answer them within the compliance frame?

## 🔴 SAFETY-2 / D-RESIDENCY-1 — engine-authoritative wrong figure (TRACKED DEFECT, 2026-08-06)

**Logged, not implemented.** Discovered by Run 3 (`nat_16`, `eval/results/edge_probe_natural_048_findings.json`).

**What happened.** *"nimemleta engineer kutoka india **hana residence permit ya kudumu** nampa
milioni 4 kwa mwezi kodi ya mshahara wake ni ngapi"* — routing **succeeded** (`compute[paye]`),
but `chike.routing.paye_resident` did not read *"hana residence permit ya kudumu"* as
non-resident. The rules engine therefore applied the **resident progressive bands** and returned
**TZS 1,028,000** instead of the non-resident flat 15% = **TZS 600,000**. That figure was then
rendered as the authoritative deterministic *working*.

**(a) Why D-FIDELITY-1 structurally cannot catch it.** D-FIDELITY-1 blanks the model body when
it *contradicts* the engine's working. Here the body and the working **agreed** — both were
wrong, because both derived from the same mis-detected input. The guard is a
consistency check between two outputs of one computation; it has no independent notion of
correctness and therefore cannot detect an error upstream of both. **No amount of fidelity
guarding closes this class.** The defect lives in input resolution, not in output fidelity.

**(b) This failure class exists ONLY in v16.** v15 has no rules engine, so it cannot lend an
authoritative frame to a wrong number: its errors are model guesses, presented as model prose.
v16 prints a wrong figure *as a verified calculation*, appended verbatim by `_render`. On this
question v15's answer was off-topic (immigration permits) but asserted **no tax figure at all**.
So on `nat_16` specifically, v16 is **worse than v15** — the only such case found in Run 3, set
against 4 confident wrong numbers v16 removed. Stated plainly because the wiring case must not
be argued on the favourable cases alone.

**(c) Proposed fix approach (NOT implemented).** Extend `_PAYE_NONRESIDENT_CUES` with
residency/permit phrasings — *"hana residence permit"*, *"hana kibali cha ukaazi"*, *"si mkazi
wa kudumu"*, *"yuko kwa muda"*, *"anafanya kazi kwa mkataba wa muda"*, *"amekuja kutoka"* —
i.e. the same lexical-cue extension pattern as the shipped ROUTING-GAP-PAYE fix, with the same
discipline: sweep every candidate over the 400 + all probe sets for false positives BEFORE
implementing, because a false *non-resident* detection is symmetrically dangerous (it would
apply flat 15% to a resident earning below the threshold). A deeper alternative — having the
engine return a *confidence* on residency and clarifying when low — is a real design change and
should not be folded into a cue extension.

**(d) This is an INPUT to the wiring decision, not a blocker to be quietly closed.** It does not
by itself argue against wiring v16: the net compute-path safety change in Run 3 was still
positive (4 wrong numbers removed, 1 correct answer lost, 1 new authoritative error added). But
it establishes that *routing success ≠ safety*, and that v16 carries a failure mode with a worse
**presentation** than anything v15 can produce. Whoever takes the wiring decision must weigh it
explicitly. **Do not close this by fixing the cue list and declaring the class handled** — the
class is "engine authority applied to a mis-resolved input", and the residency cue is one
instance of it.

## 🧭 PHASE D WIRING CYCLE — IN FLIGHT (2026-08-06)

Founder decision: **Stage 0 cancelled** (no users yet → no live traffic to observe → zero
blast radius pre-launch makes flag-gated staging over-engineering). Straight to **Stage 1 =
Phase D as ADR 0001 §10 actually specifies.** Planning premise (an assumption, NOT evidence,
and explicitly not to be reconciled with the 400's 26%): **compute ≈ 50% of eventual traffic.**

**Pre-launch blockers landed first, independent of the wiring outcome:**
- `149938d` — `chike.retrieval` **fails loud** on a missing/corrupt index instead of returning
  `[]`. The default paths are repo-relative `kaggle/`, which do **not** exist inside the Modal
  image; the old graceful-disable turned a wiring mistake into a silent no-facts collapse that
  looks like model failure. + `expected_fact_count` (R15 stale-index guard), `preflight()`,
  `configure()`.
- `fb8d3bc` — **one shared OOC refusal text.** The orchestrator carried its own terser string.
  Both matched `refusal_phrases`, so **the refusal gate could not see the difference** — wiring
  v16 would have silently downgraded every refused user's answer while passing validation.
- `30aa79b` — orchestrator resolves **`stop_strings` from config** instead of the implicit
  module default. Behavioural no-op today; closes a config-only edit reaching production and
  the gate but not v16's clean stage — a latent divergence underneath a measurement run.

**Plan A extraction — SHIPPED (`d54ec17`).** `chike/pipeline_v15.py` (production's sequence,
generation injected) + `chike/decomposition_v15.py` (leaf, **no** ordinal split), imported by
BOTH `modal_app.py` and the Phase D harness. **All three `decompose_query` copies collapsed**
(modal_app, eval.py, and the v16-only `chike/decomposition.py` kept deliberately distinct).
Behaviour proved, not asserted, against `tests/fixtures/v15_inline_baseline_30aa79b.py`
(captured via `git show` from the last pre-extraction commit): decompose/pool/prompt
byte-identical over 420 questions, stop-split+clean byte-identical over 400 persisted
generations, and **20/20 byte-identical live against the production `web_endpoint`** (closing
the two stages tests can't reach offline: the real e5 encode and the real
`apply_chat_template`). The v15 arm cannot inherit v16 powers — guarded by tests that
`decomposition_v15` differs from `decomposition` on **exactly eval_322**, and that
`V15Retriever` never invokes the two-arm hybrid. Suite 273 → 308.

**No Modal redeploy before the wiring decision** — production picks the extraction up whenever
we next deploy.

### 🟠 LAST OPEN R12 GAP — `kaggle/eval.py` has no `is_uncomputable_payroll_amount` guard

Production intercepts a payroll-levy AMOUNT asked with no salary figure **before**
decompose/RAG/generate and returns `PAYROLL_CLARIFICATION` (no model call). **The live gate does
not** — it sends the question to the model. After `d54ec17` this is the **only** remaining
divergence between `eval.py` and production.

**Deliberately NOT fixed inside this measurement cycle (founder call).** Adding it moves the
launch-blocking `GATE PASSED` number — the same class of decision as the `scorer_reliability`
denominator (see the STRUCTURAL GATE FINDING below), and changing the gate's denominator
mid-comparison would corrupt Phase D. **Decide after Phase D lands.** The Phase D v15 arm is
unaffected: it uses `pipeline_v15`, which has the guard.

### Run status

| Run | What | Who | State |
|---|---|---|---|
| 2 parts 1–2 | numeric retrieval A/B, CPU (`kaggle/rag_numeric_ab_run2.py`, `f521768`) | founder (Kaggle) | **run; artifact pending** — see below |
| 1 + 2 part 3 | paired v15-vs-v16 400 + de-confound, GPU (`kaggle/eval_phase_d_paired.py`, `124cbd2`) | founder (Kaggle) | packaged, not yet run |
| 3 | 48-question dual-path natural probe, HTTP | Claude Code | approved, not yet built |

**Run 2 parts 1–2 — founder-reported figures (full artifact not yet pasted into the repo):**
append-only **confirmed** (0 violations, 0 facts lost, Set A ranks identical) → the hybrid is
**safe**. But the second arm fires **197/197** and yields **1 recovery vs 86 dilutions** on the
labelled set → **not a demonstrated fact-path win.** Consequence: **"keep single-arm in
production" is now a live option**, and Run 2 part 3 is the deciding evidence on whether the
two-arm retriever ships at all — not merely a de-confound.

## 🔴🔴 ROUTING-GAP-PAYE — HIGH PRIORITY (2026-07-26) — top open item, above all other tracked gaps

**Discovered by a 20-question real-weights edge probe (v16 live Modal, `scratch/edge20_v16_result.json`).**
Two PAYE amount questions phrased in ordinary language — Q4 *"Mfanyakazi wangu anapata TZS 1,200,000 kila
mwezi, kodi ya serikali inayokatwa ni ngapi?"* and Q5 *"Mfanyakazi wangu si mkazi, analipwa TZS 3,000,000
kwa mwezi, kodi yake ni kiasi gani?"* — **mis-routed to the FACT path** and the model free-computed
**confident WRONG numbers** (Q4: PAYE 128,000, correct 188,000; Q5: 270,000, correct non-resident flat-15%
= 450,000).

**Why this is structurally more serious than any D-* defect fixed this session:** those were "the engine
computed wrong." This is **"the engine never ran at all."** Every never-guess / fidelity protection built
this session (D-NSSF-1 party resolution, D-PAYE-1 non-resident flat rate, D-FIDELITY-1 body-vs-working
suppression) is **contingent on the question first being routed to compute.** This gap breaks that
contingency on the single most common real compliance question there is — *how much tax comes out of my
salary* — phrased the way an actual user asks it. The fidelity guard cannot help because there is no
`ComputationResult` to guard; the fact/RAG model does the arithmetic with no deterministic backstop.

**Ranked HIGHER than every currently-open tracked gap** (D-WCF-3 distractor-coexistence, per-person/tiered
aggregation, applicability-detector/eval_311, eval_326 mixed) because **all of those are confirmed
safe-clarification gaps** (verified again in the same edge probe: Q8 tiered NSSF, Q10 WCF distractor, Q18
mixed all failed SAFE — clarify, no wrong number). ROUTING-GAP-PAYE is a **confirmed unsafe-wrong-answer
gap on natural phrasing** — a different and worse class.

**Mechanism (confirmed):** gap in `chike/routing.py::_natural_levy` cue lists (detect_intent path 2, the
Candidate C natural path). PAYE cues are only `["kodi ya mapato","kodi ya mshahara","mapato ya ajira"]`;
everyday "income tax / tax deducted from salary" phrasings (*kodi ya serikali*, *kodi yake*, *kodi
inayokatwa*, *kodi ya kipato* …) match no cue, and "ya serikali" ≠ the generic "kwa serikali", so
`_natural_levy` returns None → intent `none` → fact. Same lexical-cue mechanism as the original router fix.

**SCOPED below (characterize-before-fix, no code yet); full blast-radius sweep + proposed cue extension +
validation to be reported for review before implementing — same rigor as D-NSSF-1 / D-FIDELITY-1.**

## ✅ PLAIN-SWAHILI EDGE PROBE — Defect A + Defect B SHIPPED + PROD-VERIFIED (2026-07-28)

A 15-question plain-WhatsApp Swahili probe (`eval/accuracy_gate/edge_probe_plain_sw_015.jsonl`,
findings `eval/results/edge_probe_plain_sw_015_findings.json`) surfaced that **all 15 user-facing
answers came back EMPTY** — two stacked, production-code-identical defects:

- **Defect A — `clean_reply` blanked whole answers (`fix 628f6a0`).** `_is_fabricated_block` treated
  an early `?` (from the leading echo below) as a fabricated `Q? A` turn and discarded the first block
  → `''`. Confirmed LIVE on the production `/answer` path (4/4 → `{"reply":""}`). Fix: strip a leading
  echoed-question `?` once at the start of `clean_reply` (anchored `^`, ≤60 chars, capital-after; cannot
  cross `\n\n` so mid-answer `Q? A` detection is untouched). Blast-radius over 400 gate + 15 probe raws:
  **17 recovered, 0 regressed, 0 other**; 27 cleanup tests pass. Also recovered 2 gate rows (eval_321/330)
  whose compute path had masked the blank.
- **Defect B — model prepended a question-echo + leading `?` (`fix 6161cb9`).** Root cause: v15 trained
  on naive-concat with no assistant-turn boundary → on an UNPUNCTUATED question the model completes the
  missing `?` before answering. Fix: `chike.prompting.ensure_terminal_punct` appends `?` when terminal
  punctuation is missing, applied in all 3 prompt builds (build_chat_prompt → orchestrator + eval.py;
  modal_app.py inline primary + fallback). Sweep: **no-op on all 400 gate questions** (already punctuated
  → byte-identical), appends one `?` on the 15 probe questions with answer content unchanged. Verified
  live on the production `/answer` path (4/4 non-empty, no leading `?`). 36 prompting/orchestrator tests pass.
- **CLOSED by Defect B:** the Defect-A `>60-char leading-echo` coupling risk (a long echo could slip past
  A's cap and re-blank). B removes the echo at the source, so this can no longer arise; A remains as
  defense-in-depth.

**Note:** the gate corpus (`5a62c00`) never triggered either defect (0/400) because it is formally phrased —
this is a **coverage gap**, not a contamination of the gate numbers, which stand unchanged.

Recovered ≠ correct: several plain-phrasing answers were still wrong on content. Cycle close-out:

- **item 3 / p02 — SHIPPED (`45a9b48`).** Root cause was the `_PAYROLL_CTX` gate, not the levy cue:
  informal employment phrasing (`nimemuajiri`, `msichana wa kazi`, `nampa`) matched no payroll-context
  word, so PAYE mis-routed to fact. (`laki nane` parses fine to 800,000 — the "400k/16k" was fact-path
  hallucination.) Added informal-employment cues to `_PAYROLL_CTX`; `edge_p02` now routes paye →
  `compute_paye(800000)=TZS 78,000`. Sweep: 1 routing change, **0/400 gate changes**. **v16 orchestrator/
  gate only** (v15 `/answer` unaffected — no redeploy).
- **item 3 / p04 — DEFERRED → v16 hardening backlog: "natural-levy applicability route (structural)".**
  p04 (`…tozo ya mafunzo…inanihusu`) is an applicability ask (`_has_money_ask=False`) on a NATURAL (non-
  explicit) levy; `detect_intent` has no applicability route for that case, so cues alone can't fix it —
  needs its own design + blast-radius analysis when picked up. Its `0.5%`-vs-`3.5%` SDL rate is a
  downstream fact-path symptom of the routing miss.
- **item 3 / p12 — LEFT AS FACT (low priority).** Comparison question (`kama ya watanzania au tofauti`,
  `_has_money_ask=False`); the fact answer is already rate-correct (non-resident 15%). Logged, not fixed.
- **item 4 — OPEN (analysis-only next):** retrieval fragility on colloquial register — Q13/Q14/Q16
  fix-facts and others not retrieved on fresh plain phrasing. Structural (two-arm retrieval on run-on
  colloquial text), NOT another round of per-phrasing fact tuning. Scope options to be reported; no fix
  without approval.

**Probe cycle status:** Defect A ✅ + Defect B ✅ shipped & prod-verified; item 3/p02 ✅ shipped; p04 deferred;
p12 logged; item 4 open. Tokenizer warning (below) scoped after item 3.

## ✅ DUAL-PATH PROBE 005b — Defects A+B REGRESSION-CLEAR + the v16 wiring evidence (2026-07-29, `c1776a9`)

A 5-question plain-Swahili probe on **never-seen phrasing** (`eval/accuracy_gate/edge_probe_plain_sw_005b.jsonl`,
findings `eval/results/edge_probe_plain_sw_005b_findings.json`; runner + raw result in gitignored `scratch/`).
**Findings only — no code changed, nothing redeployed.** Each question ran through BOTH live paths on the
**same Modal deployment / same v15 weights / same 217-fact RAG index**: v15 = production `web_endpoint`
(classify+decompose+RAG+chat-template+clean), v16 = `Orchestrator(LocalAdapter → generate_endpoint)` with the
AfriqueLlama tokenizer for prompt parity. Adjudicated against `scripts/locked_facts.json` + the rules engine.

- **Defect A + Defect B hold — 10/10 non-empty** (both paths, all 5) on fresh UNPUNCTUATED plain-Swahili.
  No `clean_reply` blanking, no leading-echo re-blank. The two shipped fixes are regression-clear on the
  phrasing class that discovered them.
- **v16 ≥ v15, and strictly safer on compute.** 4/5 questions (all fact-routed) came back **byte-identical**
  between the paths. The one compute question (b02, SDL) **diverged decisively**: v15 free-computed a
  **confident WRONG payroll** (3,750,000 for 12 × 350,000; no SDL figure at all), v16 routed `compute[sdl]`
  and **safe-clarified — no wrong number**. This is the concrete case the v16 architecture exists to fix.
- **Dominant residual failure is RETRIEVAL (item 4), shared by BOTH paths and orthogonal to wiring.** b05
  (GN487A fronting, "rafiki yangu mchina… jina langu kwenye leseni") retrieved **top-3 all off-topic trademark
  fees**; the correct facts (`gn487a_license_lending_is_facilitation`, `gn487a_penalty_citizen_facilitator`)
  exist but were never surfaced, so **both** paths gave a generic immigration-ownership answer that never warns
  the user that name-lending is itself an offence (TZS 5M / 3 months). b01 also had a top-3 miss but was
  rescued by general knowledge; b04 had a rank-1 on-topic hit and answered well. **Retrieval quality tracked
  answer quality 1:1** — the strongest evidence yet for the parked item-4 hybrid dense+lexical direction, on a
  high-stakes question.
- **NEW gap logged, NOT fixed — Swahili-numeral slot extraction on the compute path.** b02 proves routing now
  reaches `compute[sdl]`, but the extractor did not resolve fully-specified all-Swahili figures
  (`kumi na wawili`=12, `laki tatu na nusu`=350,000, per-person `kila mmoja`), so the engine's correct
  **147,000** was never delivered — safe-clarify instead. **The compute path's value is gated on extractor
  coverage.** Backlog item; no code this cycle.

**Latency captured (same probe, incidental):** warm v16 ≈ v15 (b02 6.1s/6.4s, b03 6.7s/6.6s, b04 12.0s/11.9s,
b05 9.4s/9.1s); b01 was a cold start (v15 62.4s). Warm parity holds because 4/5 took **one** backend call each.

## 🟠 OPEN ITEM — tokenizer `fix_mistral_regex` / Mistral reference on the production adapter (2026-07-28)

> **SUPERSEDED 2026-08-08 by D-1** (top of file, *DEFERRED — taken up after the current fix cycle
> closes*). Work from **D-1**, not from this entry: the train/serve repo split is now verified in
> code (`train_ddp.py` loads `BASE_MODEL`; production, the gate and every probe load
> `ADAPTER_REPO`), which makes this a possible **train/serve mismatch underneath every gate number**
> rather than the warning-to-look-at scoped here. Kept for the original date and observation.

Loading the adapter tokenizer (`prospAprospA007/africa-giants-adapter-v15`) emits:
*"loading … with an incorrect regex pattern … set `fix_mistral_regex=True` … This will lead to incorrect
tokenization."* — and references **Mistral-Small-3.1-24B**, while the base is meant to be
`McGill-NLP/AfriqueLlama-8B`. "Possibly incorrect tokenization" on a production model is **not minor**.
Scoped AFTER item 3. To investigate: whether tokenization actually diverges (round-trip a Swahili sample
with/without `fix_mistral_regex=True`), whether it affects generation/retrieval, and provenance of the
Mistral tokenizer reference in the adapter repo.

## 🟠 ITEM 4 — colloquial-register retrieval fragility (PARKED; direction set, 2026-07-28)

**Diagnosis CONFIRMED (data).** On plain-WhatsApp run-on queries the dense e5 retriever MISSES the correct
fact (p06/p07/p08: top-3 were off-topic English facts — `trademark fee…`, `employer notification…`), while
a trivial lexical token-overlap arm RECOVERS the correct fact 3/3. Two compounding factors:
- **factor 1 — noise dilution:** greetings/narrative ("mambo naomba kuuliza…", "jamaa wamesema…") pull the
  dense vector off-topic; the domain keywords survive but are a minority of tokens.
- **factor 2 — English-fact attractors:** every dense miss landed on English `"key: value"` facts, whose
  generic-English embeddings spuriously outrank the on-topic Swahili fact for a noisy Swahili query.

**Direction = hybrid dense + lexical (two-arm).** Additive, no model call, no retrain. Complementary
structural cleanup = fact-form normalization (English `key: value` → concise Swahili-first) — this is the
**parked follow-up "E"** (forces a RAG regen; batch with the next `locked_facts.json` change).

**Merge strategy = TBD via a Kaggle spike** (union-then-rerank vs interleave vs weighted; rank-of-correct
across 400 gate + 15 probe). Cannot run locally — e5 load is not viable on this machine (Windows paging
limit). The spike is already written: **`scratch/item4_hybrid_sweep.py`** (adapt to the `regenerate_rag_e5.py`
Kaggle pattern — CPU, Internet, fetch inputs from GitHub). Run it AFTER the v16-wiring decision, because
that decides the target retriever: `chike.retrieval` (v16/gate) vs production `modal_app.py::retrieve_facts`
(v15) — **do not harden v15's retriever separately if v16 replaces that path.**

**Value note:** unlike item 3 (v16-only), item 4 affects real users — production `/answer` is v15 RAG-only,
so retrieval quality is the whole product there. Priority rises once the wiring target is fixed.

## ✅ FACT-ACCURACY (Q13/Q14/Q16) — SHIPPED + GATE-CONFIRMED (2026-07-28; batch `5a62c00`)

Same edge probe surfaced three fact-path fabrications where a correct locked fact (or general rule) exists:
- **Q13 BRELA deregistration** — asserted a company "must finish its term first" (fabricated; voluntary
  deregistration/striking-off exists, no fixed term).
- **Q14 OSHA vs WCF** — answered the wrong agency and fabricated a "2-employee WCF registration threshold"
  (contradicts `wcf_threshold_no_minimum`; OSHA covers all workplaces incl. one employee).
- **Q16 EFD** — "every shop needs EFD regardless of sales" (matches `efd_threshold_tzs_11m` wrong_pattern;
  below TZS 11M may use manual receipts unless VAT-registered).
Individually narrow RAG/fact-correction candidates; picked up via the same primary-source-verification
process as D-VATWH-1. Primary-source verification completed in a claude.ai session (2026-07-27, founder-approved).

**RESOLUTION (all three landed as one batch, live-verified, gate-confirmed):**

*Facts (scripts/locked_facts.json → 244 keys; CONCISE_BILINGUAL_FACTS in precompute_rag_embeddings.py):*
- **Q13** — added `brela_striking_off_non_filing`: non-filing → deemed defunct → Registrar's 30-day notice →
  struck off under Companies Act Cap 212; own-accord strike-off (2019 amendment); restoration via High Court;
  **no fixed term** (companies have no term). Fabrication ("lazima uishe muda kwanza") added to `wrong_patterns`.
  Section numbers kept in metadata only (R.E.2023 renumbers s.400A→s.403).
- **Q14** — added `osha_vs_wcf_roles` + `small_headcount_still_register`: OSHA registers/inspects **all**
  workplaces (s.16 OSH Act 5/2003), does **not** pay compensation; WCF compensates **from employee 1** (0.5%
  levy, no minimum count). Fabricated "2-employee WCF threshold" added to `wrong_patterns`; the short
  high-concentration fact out-ranks the minimum-shareholders distractor.
- **Q16** — kept `efd_threshold_tzs_11m` **pristine** (byte-identical to the deployed 213-index, preserves the
  eval_347 200M-contrast) + added separate `efd_not_every_business`: not every business needs an EFD;
  VAT-registered always; non-VAT ≥ TZS 11M; below 11M & unregistered may use manual receipts. **11M encoded per
  the primary-over-practitioner hierarchy (D-VATWH-1 precedent)** — TRA live pages say 11M; practitioners say 14M.

*Process:* full R15 regeneration cycle (Kaggle e5-base, cache-busted HEAD verify) → **217-fact index**
VERIFICATION PASSED 217/217 with the three verbatim edge questions added to the critical-query set; index
fetched + dual-committed byte-identical to `chike-inference/` + `kaggle/`; Modal redeployed. A methodology
flaw (verification paraphrases too lexically close to fact wording) was caught by a **negative live re-test**
and fixed by switching verification tuples to verbatim edge questions + a local e5 gate
(`scratch/local_rag_gate.py`) with held-out paraphrases. Live re-test #2 confirmed all three FIXED on the
217-index Modal endpoint (`eval/results/factacc_retest_a72c113.json`): Q13 retrieves
`brela_striking_off_non_filing`, Q14 `small_headcount_still_register` (rank 1), Q16 `efd_not_every_business` (rank 1).

*Comprehensive gate — `5a62c00` vs baseline `afef9dd`* (`eval/results/gate_orchestrator_combined_5a62c00.json`,
CHIKE_JUDGE=1, pinned DeepInfra seed=42, majority-of-5):
- **Target bucket UP:** fact_path reliable **85.4% → 87.7%** (111→114/130) raw 86.4%→88.0%. **Both gates still pass.**
- **Judge-augmented** 76.4% → **76.9%**. Net −1 raw / 400 (5 gained, 6 lost).
- **Collateral gain:** OSHA **+3** (eval_177/187/391) from the new OSHA/WCF facts.
- **Known-minor accepted (founder, no further regen):** `eval_355` (efd_compliance) — the deliberately
  adversarial *1,000-below-threshold* trap (turnover 10,999,000) flipped gold "Hapana" → "Ndiyo": the generic
  `efd_not_every_business` now leads retrieval and tips the boundary reasoning (both correct EFD facts are still
  retrieved; it is a generation-boundary flip, not a missing fact). `eval_304` = scorer artifact (afef9dd passed
  by number-overlap luck; neither run answers the structure-choice question). `eval_383`/`eval_208`/`eval_378`
  flips = run-to-run gen/judge noise (correct fee still retrieved rank-2; vat/sdl untouched by any fact change),
  offset by the OSHA/nssf gains.

*Commit trail:* `4912602` → `b4e6722` → `b54eb23` → `f1e3d30` → `68b9cba` → `b7666b6` → `a72c113` (217-index) →
`5a62c00` (live re-test artifact) → close-out. Not blocking; superseded ROUTING-GAP-PAYE priority ordering — done.

### ✅ ROUTING-GAP-PAYE — SHIPPED and GPU-CONFIRMED (2026-07-26 fix `3144a98`; confirmed 2026-07-27)

Approved and SHIPPED. `_LEVY_CUES` PAYE extended with six everyday phrasings (`kodi ya serikali`,
`kodi ya kipato`, `kodi ya ajira`, `kodi inayokatwa`, `kodi ya mfanyakazi`, `kodi yake`). Offline
validation: routing tests **35 passed** (positives for each phrasing incl. edge_04/05; negatives for
property tax / VAT / bare-"kodi" definition); full-400 detect_intent **0 changes** (exact decompose+route
method); full offline suite **272 passed** (was 270).

**GPU confirmation DONE (real Modal, v16 live weights, same method as the discovery probe).** Full 20-edge
re-run at `3144a98`; artifacts persisted: `eval/results/edge20_v16_run1_prefix_67e9e4c.json` (before) and
`eval/results/edge20_v16_run2_3144a98.json` (after).

**Before/after — the two target questions:**
| | edge_04 (resident) | edge_05 (non-resident) |
|---|---|---|
| phrasing | "…kodi ya serikali inayokatwa ni ngapi?" | "…si mkazi… kodi yake ni kiasi gani?" |
| run-1 routing/answer | **fact** → PAYE **128,000** ❌ | **fact** → PAYE **270,000** ❌ |
| run-2 routing | **compute[paye]** ✅ | **compute[paye]** ✅ |
| engine result | `applicable=True amount=188000` resident=True | `applicable=True amount=450000` resident=**False** (read "si mkazi") |
| working | `128,000 + 30%×(1,200,000−1,000,000) = 188,000` | `15% × 3,000,000 = 450,000 (kodi ya mwisho…)` |
| run-2 answer | **188,000** ✅ | **450,000** ✅ (correct flat-15% detection) |

**D-FIDELITY-1: armed, correctly not needed** — both model bodies were faithful to the authoritative
working this decode (edge_04 body computed 188,000 matching the working; edge_05 body stated "asilimia 15"
with no contradictory figure), so the guard passed them through (`raw_generated`==body; nothing blanked).
The guard remains the validated backstop for a contradicting decode; this run simply didn't trigger it.

**Zero regression:** all other 18 questions **byte-identical** run-1↔run-2 (routing AND answer text, greedy
decode); the known-safe clarifications (Q6, Q8 tiered NSSF, Q10 WCF distractor, Q11, Q18 mixed) unchanged.
Only edge_04/edge_05 changed. The single most common real question — "how much tax comes out of my salary,"
phrased naturally — is now on the protected compute path.

**Deferred follow-up (tracked, lower priority):** generalized safety net — *"any in-scope
payroll-context `kodi` + money-ask with no other levy → PAYE fail-safe"* — closes the whole class
rather than the two confirmed instances, but is a real scope-widening that needs its own blast-radius
analysis (same discipline as the natural-path fallback / explicit-levy over-capture / wrong-base term
list, each of which required a dedicated scoped investigation). Not part of this fix.

Original scope preserved below for the record.

### 🔧 ROUTING-GAP-PAYE — original scope (2026-07-26)

**Blast-radius sweep (`chike.routing.detect_intent` over all 400 gate questions + the 20 edge questions).**
"Looks like a levy-amount question (payroll ctx + number + money/derive ask) but routed to FACT": **400-gate
= 0 genuine mis-routes** (3 flagged all correctly fact: eval_240 GN605A avg-wage fact lookup; eval_303
property tax = OOC, intercepted before routing; eval_398 custom 15%/5% split); **20-edge = 2** (edge_04,
edge_05 — both PAYE). The 400-gate is **blind by authoring bias** (its questions name their levy, per the
routing docstring); natural phrasing is only exercised by the edge set.

**PAYE is uniquely exposed.** SDL/NSSF/WCF natural-phrasing amount questions fail SAFE: a generic deduction
word (`makato`/`michango`) → `ambiguous_multi` → compute-clarify, and jargon cues (pensheni→nssf,
ufundi→sdl, fidia→wcf) cover the rest. PAYE's everyday word `kodi` is in **neither** `_LEVY_CUES` (only
"kodi ya mapato"/"kodi ya mshahara") **nor** `_GENERIC_LEVY` ("ya serikali" ≠ "kwa serikali"), so a
`kodi`-phrased PAYE question falls through to fact and the model free-computes a wrong number.

**Mechanism:** gap in `_natural_levy` cue lists (detect_intent path 2 / Candidate C). Same lexical-cue
detector the original router fix used — NOT a distinct problem.

**Proposed fix (lexical-cue extension, same pattern as the router fix):** add everyday PAYE phrasings to the
`_LEVY_CUES` PAYE list — `kodi ya serikali`, `kodi ya kipato`, `kodi ya ajira`, `kodi inayokatwa`, `kodi ya
mfanyakazi`, `kodi yake`. Offline simulation over 400+20: routes **exactly edge_04→paye and edge_05→paye**,
**zero** other routing changes on the 400 (no new false compute-routes). Safety: the OOC classifier runs
BEFORE routing, so property/capital-gains/etc. "kodi" questions are intercepted first — the PAYE cues can
only affect in-scope questions. `kodi yake` is the broadest cue (fires only under path-2's payroll+number+
money-ask guard); flagged for review, tighten if needed.

**Expected post-fix:** edge_04 → paye compute → 188,000 (resident: 128,000 + 30%×200,000); edge_05 →
non-resident flat 15% = 450,000 (`paye_resident` reads "si mkazi"); D-FIDELITY-1 then guards any body
contradiction. **Validation plan:** unit tests in `tests/test_routing.py` (new PAYE phrasings → 'paye';
negatives: "kodi ya majengo"/property, "kodi ya VAT", bare-"kodi" definition not over-routed); full-400
detect_intent no-regression (0 changes, shown); full offline suite green; founder GPU re-run of the 20-edge
(or just Q4/Q5) confirming paye compute + correct figures. **Report before implementing — same rigor as
D-NSSF-1/D-FIDELITY-1.**

**STANDING STATUS:** EOS harness fix (build_chat_prompt → apply_chat_template) — **CLOSED,
RE-BASELINED, and VALIDATED at scale.** The corrected 400-question combined regression is
IN (commit e9cc68a, persisted to `eval/results/gate_orchestrator_combined_e9cc68a.json`) —
**the first fully clean, trustworthy full-scale gate run this project has had.** EOS fix
confirmed broad-based (0 loops / 0 header-leakage / 0 empty across 400; ~3× runtime).
eval_317/146 **resolved**; eval_213/355/155 are **genuine defects the corrected harness
newly exposed** (NOT harness noise); eval_332/365 **reclassified as scorer artifacts**.
Retrieval-layer prohibition-inversion fix — CLOSED and VALIDATED (d92e63f). Reporting-layer
negated-lazima lexicon fix shipped (cec8fae). **Compute buckets (32–40%) are scorer-limited,
not a confirmed measure of true compute accuracy** — closing that gap needs the
frontier-judge scoring approach, not more prompt/retrieval work. NEW convention: every gate
run is committed to `eval/results/` (see below). Next: eval_213 faithfulness defect +
frontier-judge compute scoring + framing-aware polarity.

## 🔦 STRUCTURAL GATE FINDING — the live `GATE PASSED` number does NOT apply `scorer_reliability` (2026-07-26)

**Stated plainly because it changes what "the gate" has actually been measuring:** the production
gate `kaggle/eval.py` — the file that prints `GATE PASSED` and whose `in_corpus` accuracy gates
every product launch — scores **every** in-corpus question raw via `score_question`
(`in_acc = in_pass / len(in_corpus)`) and **never calls `scorer_reliability` at all.** The
`reliable=False` exclusion, the "8 exclusion categories," and the **133-question measurement gap**
that this entire frontier-judge investigation (follow-up #3) has characterized live **only** in the
*analysis* harness `kaggle/eval_orchestrator_combined.py` (which reports reliable-denominator scoring
alongside raw) and in `chike/scoring.py::scorer_reliability`.

**Consequence:** the 133 questions the regex scorer *itself admits it cannot verify robustly* have
**not** been excluded from the live gate — they have been **silently included in the raw pass/fail
number the whole time**, each scored by the mechanism that flags itself as unreliable on exactly
those cases. So the headline gate accuracy (e.g. the v15 first-gate-pass 87.9% in-corpus) rests, for
~a third of its denominator, on verdicts the project's own scorer marks low-confidence. This is not a
regression introduced this session — it is the pre-existing state of the gate, surfaced while tracing
the item-5 integration seam.

**Not being "fixed" reflexively.** Making `eval.py` exclude the 133 would *change the live gate's
denominator and its historical comparability* — a real decision, deliberately deferred (it was option
3 of the item-5 gate-integration fork; founder chose the conservative report-alongside path). Item 5
instead layers the judge as a **transparency overlay** in the analysis harness (raw vs reliable-denom
vs judge-augmented, side by side) so the size and direction of this gap becomes *visible and
quantified* in every run **without** silently moving the launch-blocking number. Whether to later
promote the reliable-denominator (or judge-augmented) number to the actual `GATE PASSED` trigger is a
separate, explicit call, gated on work-item-2 ground truth. **Tracked; do not silently change
`eval.py`'s denominator without a deliberate decision + a re-baseline of the historical gate numbers.**

## v16 router architecture — ADR 0001 (see docs/decisions/0001-v16-router-and-orchestrator-architecture.md)

The v16 router/orchestrator remediation is governed by **ADR 0001** (do not duplicate here — read it):
- Original embedding-router + LLM-fallback plan REJECTED; extractor-intent counter-proposal adopted.
- **Phase 0 bake-off DECIDED (2026-07-20):** on the 50-question natural routing set, the embedding
  router (Candidate B) **misrouted 2 OOC questions (capital-gains, mining-royalty) into compute** —
  empirically confirming the ADR's key safety objection — and was boundary-blind (3/8). Candidate C
  (lexical-prefilter + extractor-intent) won: precision 1.0, 8/8 boundary pairs, 0 OOC misroutes.
- **Phase A foundation:** lexical prefilter as a recall-biased invoke-gate → extractor emits
  `{intent, fields}` in its existing single call → never-guess preserved. No new model on the
  serving path; OOC stays with `classify()`. Test artifact: `eval/router_eval/router_natural_eval_001.jsonl`.
- **Phases A, B, C IMPLEMENTED (2026-07-20)** — see ADR §9. A: deterministic router + backstop
  (`592f0d2`). B: route-aware merge fixes the decompose/generate/concatenate divergence, closing
  the Q1/Q12 regressions (`72b3cbe`). C: unified OOC classification into shared
  `chike/classification.py`, closing Finding 3 (`f55f0cf`). Offline suite: **167 passed, 2 skipped**
  (the 2 skips are the Phase D GPU pair).
- **Phase D REMAINING (GPU, BLOCKING before any production wiring)** — see ADR §10: un-skip the 2
  GPU tests, re-run the 20-question A/B and the full 400-gate through the corrected system,
  require **v16 ≥ v15 on both**. Also resolves the deferred AND-vs-OR invoke-gate cost lever.

### TRACKED KNOWN LIMITATION — decomposition coverage gap (2026-07-20, backlog, low urgency)
`decompose_query` does not split some period-joined / sentence-initial-`Pia,` clauses: a mixed
compute+fact question phrased as *"...nihesabie SDL. Pia, ada ya BRELA ya mwaka ni ngapi?"* (a
single `?`, second clause joined by "Pia," after a full stop) stays **one** sub-question. It then
funnels entirely into the single compute (SDL) route, and the trailing fact clause **corrupts the
compute extraction** — the gross payroll `milioni 12` was read as **1,000,000 instead of
12,000,000** (the "mwaka"/second-figure context in the un-split clause misleads the deterministic
amount parser). A two-`?` phrasing decomposes correctly and both sources come back right (SDL on
12M = 420,000 + BRELA annual return = 22,000), so this is purely a **decompose-coverage** gap.
Orthogonal to Phase B (route-aware merge) and to the backstop retirement — neither caused it and
neither fixes it. Discovered while running the Stage 1 mixed-compound real-weights test; the test
now uses a decomposing phrasing and notes this inline. **Backlog:** extend `decompose_query` to
split "Pia,"/period-joined clauses (and add a guard so an un-decomposed multi-figure question does
not silently feed a wrong figure to the rules engine). Not blocking; no current production impact
(production run() has no compute path).

**Tracked instance — eval_322 (enumerated compound, 2026-07-24).** *"Nataka kujua mambo matatu:
kwanza kizingiti cha VAT, pili kiwango cha SDL, tatu je nitoe risiti ya EFD kwa muamala wa TZS
5,000?"* — a **`kwanza…pili…tatu` enumeration** whose three parts are all directly answerable
**facts** (VAT threshold 200M/100M; SDL rate 3.5%; EFD required for any amount). It does not
decompose; the "SDL rate" fragment is mis-routed to **compute** and emits a salary/count
clarification, and the VAT-threshold and EFD parts are **dropped entirely**. Same root phenomenon
as the "Pia,"/period-joined gap above — a new *instance*, not a new defect. Found during the
Finding-2 individual verification of the 5239190 run (it was the 1 of 23 "safe never-guess"
clarifications that did NOT hold up). **Per option (b): logged here, no engine change this session.**
Fix would be the same enumerated/period-clause `decompose_query` extension (+ the never-guess
multi-figure guard), with a full 400 no-regression sweep.

## ✅ Ordinal-enumeration decomposition (`_split_ordinal_enumeration`) — SHIPPED (2026-07-24) — router follow-up #2 of 3

**The second of the three tracked follow-ups from the Phase D router investigation.** Preceded
by a full characterization (Steps 1-3, offline, pure string logic) before any code, given the
much broader blast radius — decomposition sits upstream of routing/retrieval/extraction/merge for
all 400 questions.

### Characterization findings (the scope was much smaller than the label suggested)
- **Baseline:** of 400, only **3 decompose** today (eval_318 pass / eval_321 fail / eval_330 pass,
  all via `na pia`/enum); 397 stay whole. Snapshot anchored at `scratch/decomp_baseline_snapshot.json`.
- **The `"Pia,"` period-joined pattern = 0 real gate instances.** A direct search for a sentence-
  boundary `[.!] Pia,/vilevile/aidha` across all 400 returns **zero** — the logged example
  (*"…nihesabie SDL. Pia, ada ya BRELA…"*) was a **constructed** illustration, never an actual gate
  question. Worth stating plainly: **half the originally-scoped problem did not exist in real data.**
  (The 6 `pia` hits are all adverbial "also/too" inside one question, or multi-part via other
  connectors — not the period-joined shape.)
- **The ordinal `kwanza/pili/tatu` pattern = exactly 1 real case (eval_322).** The other raw hit,
  eval_290 (*"watu 3 wa kwanza… wanne wanaofuata… watano wa mwisho… SDL?"*), is a **tiered-payroll
  compute** question — "kwanza" = "the first [group]", not "firstly [question 1]" — a false positive
  that must stay whole.
- eval_322's three parts (VAT threshold / SDL rate / EFD receipt) are **all facts**, and once split
  each routes to `none` (fact) — so **decomposition alone is sufficient**, no compute/extraction change.

### Fix mechanism (decomposition-layer only; pure string logic)
`_split_ordinal_enumeration` fires **only** when BOTH signals are present: an announce phrase
(`_ORDINAL_ANNOUNCE`: `(mambo|maswali|masuala|vitu|mengi) (mawili|matatu|manne|matano|sita|saba|
kadhaa)`) AND a **sequential ordinal run** starting `kwanza`→`pili`[→`tatu`…], each present and
strictly after the previous, matched as whole words (never found inside `matatu`/`wanne`/`watano`).
It splits on the ordinal delimiters and drops the announce preamble (each listed item is self-
contained). Requiring **both** signals is what excludes the bare-`kwanza` tiered-payroll class and
the adverbial-`pia` class. Wired into `decompose_query`'s early-return guard and as a split branch
after the enum branch (fires only when the `?`/connector/enum paths produced nothing usable).

### Validation (exactly the plan)
- **Full-400 before/after decomposition diff vs the snapshot: exactly 1 question changed —
  eval_322** (n=1 → n=3: `['kizingiti cha VAT', 'kiwango cha SDL', 'je nitoe risiti ya EFD kwa
  muamala wa TZS 5,000?']`). The 3 pre-existing splits (eval_318/321/330) are **byte-identical**.
- **All 14 false-positive candidates stay whole (n=1):** eval_290 (tiered payroll), eval_044/180/
  186/206 (adverbial "pia"), eval_345 (comparison ref), eval_051/052/055/058 (single question,
  multiple domain keywords), eval_331 (conditional if-yes-then), eval_171/174/219 (context + one ask).
- The 3 new eval_322 sub-questions all route to `none` (fact), as predicted.
- Unit tests (`tests/test_decomposition.py` 6 → 10): 3-way split; bare-ordinal tiered payroll not
  split; adverbial "pia" not split; requires-both-announce-and-two-ordinals guard.
- **Full offline suite: 208 passed, 0 failed.**

### Scope held
eval_320/eval_319 (compute enumeration — a `levy-list + verb` shape needing compute routing AND an
N-way merge) are **deliberately deferred as a separate, higher-risk pattern** with its own future
investigation, NOT folded in. eval_332 (3-part gn487a) **excluded as a scorer artifact** — the model
already answers all three parts correctly whole, so decomposition would not move its score.

### Gate-number caveat (unchanged discipline)
Routing-quality fix: eval_322 is `pass=False` today and production `run()` has no compute path, so
this **cannot move the reliable-subset number on its own**. It removes the mis-route (SDL fragment →
compute clarification) and the dropped VAT/EFD parts; whether the merged 3-fact answer clears the
overlap scorer is confirmed by **folding into the next scheduled 400-run** — no separate GPU cycle.

**Follow-up #2 of 3 COMPLETE. Remaining: #3 — frontier-judge / semantic scoring (the largest in
scope; directly addresses the MEASUREMENT GAP — ~a third of the 400 scored by a mechanism that
admits it cannot verify its own answers in either direction).**

## 🔎 Frontier-judge scoring — IN PROGRESS (work item 1 of 5 DONE, 2026-07-25) — router follow-up #3 of 3

**Status-check before scoping (confirm before building, same discipline as #1/#2). #3 does NOT
start from zero — a completed, persisted bake-off already exists (2026-07-16). But "validated"
means a feasibility/comparison win, not a precision-measured, wired-in scorer, and it was run on
190 questions, not the current 400.** This entry is the documented baseline for the eventual
dedicated session; NONE of the five work items below has been started.

### Groundwork inventory (two tiers)
- **Scratch (exploratory, local, gitignored):** `nli_regression_190.py` (mDeBERTa),
  `nli_xlmr_190.py` (xlm-roberta-large-xnli), `nli_round2.py` (threshold-tuning + entailment +
  cross-lingual on the 14-example set). All are **contradiction-demotion** experiments (demote a
  regex-PASS→FAIL only when NLI contradiction ≥ 0.70) — NOT full judges.
- **Committed, reusable harnesses (`kaggle/`):** `nli_regression.py` (mDeBERTa, fetch-and-run,
  persists to HF) and **`judge_regression.py` — the real LLM-as-judge** on OpenRouter
  `qwen/qwen3-32b`. Two stages: STAGE 1 = 14 audit examples vs known ground truth
  (`scratch/audit14.json`); STAGE 2 = full 190 non-refusal questions, judge verdict
  (correct/wrong/undetermined) vs the current `score_question`+`scorer_reliability`. Persists
  `judge_regression_qwen3-32b.json` to HF v15. Models actually called across the bake-off:
  `intfloat/multilingual-e5-base`, `mDeBERTa-v3-base-xnli` (280M), `xlm-roberta-large-xnli`
  (560M), `qwen/qwen3-32b`. Data: `audit14.json` (14 hand-labeled) + the **190** first-block v15
  results (`gate_001_results.json` on HF).

### What was actually produced (persisted to HF v15, git_head 8efdd32 — read from saved data)
- **Embeddings REJECTED** (cosine is polarity-blind). **mDeBERTa NLI REJECTED** (5 false-demotions
  @190, high-confidence). **xlm-roberta-large NLI REJECTED, worse** (13 false-demotions @190).
- **qwen3-32b judge "genuine improvement":** STAGE 1 **12/14** vs ground truth (1 harmful
  false-demote, 0 false-promotes, and it **rescued 2 answers regex had wrongly FAILED**); STAGE 2
  **covered all 71 currently-EXCLUDED questions** with a verdict, 13 demote / 6 promote
  **disagreements with regex**, 101 agreements, 0 API errors, **$0.018 / 160s**.

### Precise reading of "already validated earlier this session" (PROGRESS line ~613)
"Validated" = **a completed comparative bake-off proved the frontier-judge is the RIGHT approach**
(beat NLI + embeddings, matched 12/14 ground truth, covered all 71 excluded, ~2 cents). It does
**NOT** mean: (a) a measured precision/recall against a real ground-truth set — only **14** are
adjudicated; STAGE 2's 13/6 are **disagreements with an imperfect regex baseline, explicitly "not
proven errors"**; (b) a production-ready scorer — the 2026-07-16 entry's OWN recommendation says
**"do NOT adopt it as a silent automatic scorer"** until `procedure` over-strictness is
characterized, it is escalated to a larger frontier model, and the 13/6 are adjudicated against
`locked_facts.json`; (c) a settled model — a separate **non-determinism finding** shows qwen3-32b
**flips verdicts even at temp=0** and **misreads Swahili compound numerals** (laki/robo/milioni).

### The scorer seam (confirmed ready, currently untouched)
`chike/scoring.py::scorer_reliability(q, generated)` returns `(reliable, reason)` and is exactly
where the **8 exclusion categories** live; its docstring explicitly names *"a semantic judge
(LLM-as-judge / frontier-model scoring)"* as the intended fix, and `judge_regression.py` already
layers on top of it. **What does NOT exist:** any wiring of a judge verdict back into
`scoring.py` / `run_eval.py` / the gate — `scoring.py` is deliberately unchanged.
(`chike/model_abstraction/frontier_api.py` is a GENERATION-backend stub for routing *compute*
questions to a frontier model — `generate()` raises `NotImplementedError` — NOT the scorer seam.)

### Five genuinely-new work items for #3 (none started)
1. **Scale to 400. ✅ DONE (2026-07-25)** — see the "Work item 1 — census" subsection below. All
   prior judge/NLI work targeted the **190** `gate_001` set; the census now covers the full
   **133/400** MEASUREMENT GAP on the `5239190` baseline **plus** an audit of the 252 reliable
   verdicts.
2. **Real adjudicated ground truth.** Expand beyond 14 hand-labeled examples to a human-adjudicated
   sample across the `reliable=False` categories, to measure the judge's TRUE precision/recall
   (STAGE 2's 13/6 are unadjudicated disagreements).
3. **Characterize the `procedure` over-strictness** (6 of the 13 demotions — the judge's known weakness).
   **✅ DONE (2026-07-25)** — see "Work item 3 — procedure/definition over-strictness characterization"
   below. One narrow deterministic fix shipped (commit `22af4ad`); everything else routed to item 5.
4. **Resolve non-determinism.** ✅ DATA-GATHERING DONE (2026-07-25) — see "Work item 4" below.
   Pinning (seed + single provider) cuts flips but leaves 2 correct↔wrong flips at scale; a subsample
   sufficiency proof (0/780 at N=3, 0/234 at N=5 across all 39 IDs) recommends pinned-provider +
   **majority-of-5** (robust to 4-2, 3-3→undetermined). Wiring the rule is deferred into item 5.
5. **Integration design.** ✅ BUILT (2026-07-26) — see "Work item 5" below. Judge wired as a
   conservative, asymmetric CONFIRMATION overlay: fills the `reliable=False` gap, flags (never
   flips) `reliable=True` disagreements, reports a third "judge-augmented" number alongside
   raw + reliable-denom. `scoring.py` and the live `GATE PASSED` trigger unchanged (report-alongside).

### Work item 5 — judge→scoring integration (BUILT, 2026-07-26) — the last piece of follow-up #3

**Prior-work check first (crash-recovery discipline):** searched scratch/ + eval/results/ + repo-wide
for a "267 reliable=True" judge run the previous session might have left — **none exists.** The only
prior judge pass is the **census** (`eval/results/judge_regression_qwen3-32b_400.json`): single-shot
(N=1), non-pinned, over all 385 non-refusal (252 reliable + 133 excluded), **$0.0407 / 349s @ 8
workers / 7.17s per call / 0 errors** — the actuals the cost model below is grounded on. Reconciled
the "267": real reliable=True is **252**; `400 − 133 = 267` conflates the 15 OOC refusals (separate
refusal gate) into the count.

**Structural finding (documented as its own headline above):** the live gate `kaggle/eval.py` **does
not apply `scorer_reliability` at all** — it scores every in-corpus question raw, so the 133-question
measurement gap has been *silently inside* the live gate number, not excluded. This is why item 5 is a
**transparency overlay**, not a gate-logic change: it makes the gap visible/quantified without moving
the launch-blocking number.

**The four open design questions — resolved (founder-confirmed):**
1. **Adjudicate the `reliable=False` gap? YES** — the judge FILLS it (regex explicitly abstained there).
2. **Confirmation/override on `reliable=True`? Confirmation yes, override NO** — disagreements emit an
   adjudication QUEUE (false-pass / false-fail candidates), never auto-flip. This is exactly how the
   census's disagreements drove real engine fixes this session (D-NSSF-1/D-WCF/D-PAYE), not a per-run flip.
3. **`undetermined` in the denominator?** Never moves a regex-scored question in/out. In the gap-fill:
   `correct`→pass, `wrong`→fail, `undetermined`→**excluded** (+ a conservative `undet=fail` floor is
   also reported, to bracket true accuracy). This kills the "farm undetermined to shrink the denominator"
   exploit — the denominator stays anchored by regex.
4. **When does the judge override regex? NEVER in the live gate number.** It only fills the gap and
   flags disagreements. Promotion to an actual override is gated on **work-item-2 ground truth** — a
   separate, explicit future call.

**What was built (all offline-tested; no `scoring.py`/`eval.py` pass/fail change):**
- **`chike/judge.py`** (new, eval-only leaf module: stdlib + `requests`). The item-4 design made
  reusable — pinned provider (**DeepInfra, seed=42, `allow_fallbacks:false`**) + **majority-of-5**
  (`majority_vote`: strict plurality, any tie→`undetermined`) — plus the item-5 pure aggregation
  `build_confirmation_report` (the three numbers + gap-fill + disagreement queue) and `judge_gradeable`
  (in-corpus, non-clarified; clarifications are deliberate never-guess, excluded like the census's 30).
  **Explicitly EXEMPT from the modal_app↔eval.py dual-file-sync rule** — it is a scorer overlay (like
  `scorer_reliability`), never on the production serving path.
- **Wired into `kaggle/eval_orchestrator_combined.py`** as an OPTIONAL post-scoring pass (runs when
  `OPENROUTER_API_KEY` present and `CHIKE_JUDGE!=0`; the GPU gate runs fully without it). Prints the
  three numbers side-by-side + gap-fill + disagreement queue + provider-pin verification; persists a
  `judge_overlay` block in the artifact. Touches no bucket score, no `scoring.py`, no `GATE PASSED`.
- **`scripts/judge_augmented_local.py`** — local twin (no GPU) over the pinned **5239190** baseline
  (asserts `commit=='5239190'`), the direct successor to the single-shot `judge_regression_400.py`.
  Lets the three-number report be produced now from existing data. Writes
  `eval/results/judge_augmented_5239190.json`.
- **`tests/test_judge.py`** — 15 tests locking the safety invariants (5-1→majority side, 2-2-1 tie→
  undetermined, parser ladder, pin held across 5 calls via injected fake `requests`, gap FILLED but
  reliable=True NEVER flipped, undetermined never moves the trusted denominator, clarifications excluded).
  **Full `tests/` suite: 257 passed** (was 242 + 15 new).

**Cost/scale (grounded in census actuals):** majority-of-5 over the 307 in-corpus non-clarified rows of
the 5239190 baseline = **~1,535 calls ≈ $0.16, ~20–25 min @ 8 workers** (full-400 Kaggle harness path
grades ~all non-refusal ≈ 1,925 calls ≈ $0.20). **Cheap enough for a normal gate cycle** — dwarfed by
the GPU generation step, and OpenRouter-parallel. Caveat: the DeepInfra pin serves from one provider, so
throughput may trail the census's provider-agnostic routing.

**FIRST LIVE RUN — DONE (2026-07-26, `eval/results/judge_augmented_5239190.json`).** Ran
`judge_augmented_local.py` over the pinned 5239190 baseline: 307 in-corpus non-clarified answers ×
majority-of-5, **provider pin held (DeepInfra only), 0 API errors, $0.165, 933s (~15.5 min)** — cost/latency
match the census-grounded projection. **The three numbers:**
- **raw in-corpus 254/384 = 66.1%** (what the live `eval.py` gate computes)
- **reliable-denom 184/251 = 73.3%** (regex, gap excluded)
- **judge-augmented 247/335 = 73.7%** (gap filled; undet excluded) — floor(undet=fail) 73.3%

**Headline finding: the judge-augmented number CONFIRMS the reliable-denominator (73.7% ≈ 73.3%) rather
than diverging.** The 86-question `reliable=False` gap, independently adjudicated by the judge (63 correct /
21 wrong / 2 undetermined), performs about the same as the reliable subset — so the honest reduced-denominator
method (adopted 2026-07-14) was **not** concealing a materially different-performing third of the gate. Raw
(66.1%) sits ~7 points below both because it scores ~49 deliberate clarifications as fails and mis-scores the
unreliable gap — quantifying how much the live raw gate *understates* true in-corpus accuracy. **Disagreement
queue: 27 false-pass + 11 false-fail candidates** (vs the census single-shot's 27+12); majority-of-5 shifted
~5 IDs each way — the expected stabilisation. Notably the two item-4 dangerous-flip cases land exactly as the
design intends: **eval_228 → a tie → `undetermined`** (the honest coin-flip, not the census's unlucky
single-shot verdict), **eval_230 → stable false-fail** (judge says correct). 4 ties total
(eval_034/074/228/360), all correctly parked at `undetermined`.

**Remaining (both founder-gated):** ~~the long-held single comprehensive gate run covering every change
since 5239190~~ **— DONE 2026-07-26, commit `afef9dd`; see the CLOSE-OUT entry below.** Only **work item 2
(real adjudicated ground truth)** stays open — the prerequisite before any promotion of the judge-augmented
number to the live `GATE PASSED` trigger. Its input is now the **fresh 25+7 disagreement queue** from the
afef9dd run (superseding the stale 27+11 from the 5239190 baseline).

## 🏁 CLOSE-OUT — comprehensive confirmation run `afef9dd` (2026-07-26): the entire router-investigation / defect-fix cycle is CLOSED

**This is the closing entry for the whole cycle** — router remediation Phases A–D, all three
router-investigation follow-ups (#1 explicit-levy money-ask guard, #2 ordinal-enumeration decomposition,
#3 frontier-judge scoring), and now the single comprehensive gate run that confirms the accumulated fix
cluster at scale. A fresh 400-question orchestrator regression was run on GPU (founder-executed on Kaggle)
at commit `afef9dd` with the item-5 judge overlay riding along (majority-of-5, pinned DeepInfra seed=42).
It exercises **every change since the `5239190` baseline**: fixed engine (D-NSSF-1 / D-WCF / D-PAYE /
D-DECOMP-1 multi-levy fan-out) + fixed RAG (213 facts) + v15 model + judge overlay. Artifact fetched
independently from HF and committed: `eval/results/gate_orchestrator_combined_afef9dd.json` (commit `0a2db58`).

**Bucket before/after (5239190 → afef9dd), raw AND reliable:**

| Bucket | raw base | raw fresh | Δ | reliable base | reliable fresh | Δ |
|---|---|---|---|---|---|---|
| adversarial_150 | 39.6% | **49.3%** | +9.7 | 54.4% | **62.1%** | **+7.6** |
| compute_type | 31.6% | **40.2%** | +8.6 | 41.2% | **46.9%** | **+5.8** |
| compute_type_genuine | 31.9% | **39.6%** | +7.7 | 40.0% | **45.8%** | +5.8 |
| staged_50 | 74.0% | **80.0%** | +6.0 | 73.2% | **80.0%** | **+6.8** |
| fact_path_190 | 86.7% | 86.4% | −0.3 | 85.0% | **85.4%** | +0.3 (stable) |

Every touched cluster moved up +5.8 to +7.6 pts (reliable); the untouched fact path held flat — exactly
the expected signature of engine/RAG fixes that don't touch the fact answers.

**Fix-cluster verification — each shipped fix confirmed present in the FRESH generation (read from persisted data, not the terminal paste):**

| Case | Fix | Evidence in fresh generation | Verdict |
|---|---|---|---|
| eval_121 (SDL, 8 staff) | applicability threshold | `FAIL→PASS`; *"Hapana… wafanyakazi 10 au zaidi… una wafanyakazi 8"*; judge=correct | ✅ landed |
| eval_318 (multi-levy, 11 staff) | D-DECOMP-1 fan-out | Computes all three: SDL 3.5%×5.5M=192,500; NSSF 20%=1,100,000; VAT threshold crossed | ✅ landed |
| eval_321 (multi-levy, 8 staff) | D-DECOMP-1 fan-out | `FAIL→PASS`; SDL=none(<10) + NSSF 640,000 + WCF 16,000 + OSHA yes — full fan-out | ✅ landed |
| eval_098/100/105/110 (NSSF) | compute/fact | Pass; voluntary membership; full-salary no-cap 200k+200k=400k | ✅ stable |
| eval_115 (GN 605A date) | fact/RAG | Correct: 1 Jan 2026, gazetted 13 Oct 2025 | ✅ stable |

*Known-open follow-ons (correctly NOT counted as regressions):* eval_124 / eval_320 (per-person / tiered
multi-levy) — the model **clarifies** instead of computing, which is the still-tracked **D-DECOMP-2 /
per-person aggregation** work; `reliable=False`, correctly excluded from the denominator.

**Prohibition-inversion continuity check — zero engine-introduced regressions.** Fresh set
`{eval_144, 155, 183, 332, 365, 391}` is a **strict subset** of the baseline's 8
`{144, 155, 183, 332, 343, 355, 365, 391}` — each verified `candidate_inversion=True` at 5239190 (including
eval_391, which was flagged at baseline though not written up by ID). **New in fresh: NONE. Resolved since
baseline: eval_343 + eval_355** (both now pass). All 6 remaining are the known adversarial leading-premise
polarity traps (gold is a counter-intuitive *"Hapana/La"*; model agrees with the surface framing). eval_391
is the genuinely-ambiguous one — its marker *"Ndiyo"* agrees with the leading *"sivyo?"* but its substance
is correct, so the judge scored it **correct** (it sits in the false-fail queue) while the polarity heuristic
flags it — precisely the ambiguity item-4/5 exists to surface.

**Per-question flip analysis (400 common IDs, no set drift): 24 real gains, 1 genuine stochastic loss, 2 false losses.**
24 `FAIL→PASS`, concentrated exactly in the fix clusters (NSSF/SDL/WCF/PAYE compute + adversarial). The 3
`PASS→FAIL`, dissected individually:
- **eval_259** (WCF compute) — baseline "passed" by computing `0.5% × 40,000,000` **on vehicle value** (the
  trap; WCF is on payroll) = a **false pass**. Fresh now correctly **clarifies** (*"nahitaji jumla ya
  mishahara"*). A **real improvement disguised as a raw-number drop.**
- **eval_048** (VAT-WH) — fresh answer is substantively correct, just shorter than gold; regex missed it,
  **judge=correct**, `reliable=False` (excluded). A **scorer artifact, not a regression.**
- **eval_039** (VAT-WH) — the **one genuine loss**: model emitted a self-contradictory answer this decode
  (*"Ndiyo… ni sawa"* then lists 3% vs 6%), judge=wrong. Non-deterministic model decode on a fact path the
  engine fixes don't touch — **not an engine fault.** Net: **24 real gains, 1 stochastic loss, 2 false losses.**

**Judge-augmented / reliable-denominator convergence — now TWICE-CONFIRMED evidence.** The three numbers
(base → fresh): raw 66.1% → **71.6%**, reliable-denom 73.3% → **77.0%**, judge-augmented 73.7% → **76.4%**.
The judge-augmented number lands **within 0.6 pt** of the reliable-denominator (77.0% vs 76.4%) — the same
result as the baseline local run (73.3% vs 73.7%, within 0.4 pt). The 91-question `reliable=False` gap,
independently judged, resolves at **65 correct / 22 wrong / 4 undetermined ≈ 74.7%** — statistically the same
population as the reliable regex set. **Stated plainly as positive evidence, not a coincidence of numbers:
across two independent runs the measurement gap the reduced-denominator method excludes was NEVER hiding a
materially worse-or-better-performing population.** Provider pin held (`providers_served: ['DeepInfra']`),
324 graded, 0 API errors.

**Bottom line:** every fix the cycle built landed and is verifiable in the fresh persisted generations;
+5.8 to +7.6 pts across all three touched buckets; the single real regression is a stochastic decode
artifact on an untouched fact path; no new prohibition inversions; and the judge overlay independently
reconfirms the reliable-denominator method. **The router-investigation / defect-fix cycle is CLOSED.**

**Still held (correctly deferred):** **work item 2 — real adjudicated ground truth** on the **fresh 25+7
disagreement queue** (25 false-pass: eval_027/028/034/066/071/075/106/120/132/145/162/164/171/223/234/235/
268/304/318/330/342/366/367/378/392; 7 false-fail: eval_029/094/131/187/230/233/391). This is the concrete
input for any future promotion of the reliable-denominator or judge-augmented number to the live
`GATE PASSED` trigger — a separate, explicit call. Not started; now has the right, current input.

## ✅ Work item 2 — ROUND 2 adjudication of the afef9dd disagreement queue (DONE, 2026-07-26)

**The fresh 25+7 queue from the `afef9dd` comprehensive run, adjudicated independently** against
`scripts/locked_facts.json` + CLAUDE.md §11 (NOT against the judge's or regex's stated opinion). Full
record: `eval/results/work_item2_round2_adjudication_afef9dd.json` (all 32 rows: question, gold, fresh
generation, regex/judge verdict, my truth C/W/A, root cause, basis). This supersedes the stale
5239190-baseline queue and is the concrete input for any future promotion of the reliable-denominator /
judge-augmented number to the live `GATE PASSED` trigger.

**Confusion matrix (24 clean cases; 8 ambiguous excluded):**

| | judge right | judge wrong |
|---|---|---|
| **regex right** | 0 | 1 (eval_164) |
| **regex wrong** | 23 | 0 |

- **JUDGE 23/24 = 95.8% correct** on the adjudicated disagreement set — consistent with (slightly above)
  the ~93% measured reliability. Single miss: **eval_164** (false-DEMOTE of a correct GN487A penalty
  answer — 10M/6mo/visa-revocation matches gold AND `gn487a_penalty_noncitizen`; the judge invented that
  the reference wanted "deportation"). Second confirmed judge-error data point (after item-1 STAGE-1's 10/14).
- **REGEX 1/24 = 4.2%** — expected: the queue is BY CONSTRUCTION the regex↔judge disagreement set, so in
  each clean case exactly one is wrong; in 23/24 the judge was right and regex wrong.

**Categorized findings:**
- **Confirmed real regex false-POSITIVES: 16** (model truly WRONG): eval_027/028/034/066/071/162/223/235/
  268/304/318/330/342/367/378/392. Root causes: **10 fact** (model/RAG gave a wrong fact where a correct
  locked fact exists — BRELA structures/company, EAC STR, PAYE max & non-resident, NSSF pension, mgeni),
  **4 generation** (hallucination/reasoning: eval_034 invented assumption; eval_268 **fabricated a
  turnover** the user never gave; eval_318 **inverted** the VAT 205M>200M comparison; eval_330 fabricated
  penalties + BRELA misdirect), **2 fidelity** (eval_367/378, see headline). **NONE trace to a new
  deterministic engine/routing defect.**
- **Every shipped engine fix confirmed correctly LANDED in the fresh generation:** eval_330→employee
  45,000 (D-NSSF-1), eval_367→750,000 flat (D-PAYE-1), eval_378→"SDL haihusiki" amount=None (SDL
  threshold), eval_318→SDL 192,500 + NSSF 1,100,000 (D-DECOMP-1 fan-out). The residual errors on those
  same questions are all MODEL-side (fact/generation/fidelity), not engine.
- **Confirmed real regex false-NEGATIVES: 7** (model truly CORRECT): eval_029/094/131/187/230/233/391 —
  all fit the six item-3 sub-patterns (terse-but-correct procedure/definition; institution-answer-no-number;
  number-as-definition; negative-framing polarity). **No new sub-pattern.**
- **Judge errors: 1** (eval_164, above).
- **Genuinely ambiguous/disputed: 8** — eval_075 (own-name reg nuance), eval_106/120/132 (incomplete not
  false), eval_145/171 (different-angle GN487A advice), eval_234 (documented NSSF-deadline inconsistency),
  eval_366 (reach-vs-exceed boundary). Not forced to a verdict.

**NEW-DEFECT DETERMINATION: no new deterministic defect.** All 16 confirmed false-passes are model-side.
The engine/router are correct in every compute case, including the two crash-relevant ones (eval_367/378).

### 🔴 HEADLINE FINDING — D-FIDELITY-1: model body can contradict the authoritative compute working

On a compute question the model can emit a WRONG figure that **leads** the answer, even though the correct
deterministic `ComputationResult.working` is appended right below it (`_render` returns
`f"{body}\n{working}"`, orchestrator.py:341). Two confirmed instances this round:
- **eval_378** (SDL, 8 staff): engine appended correct *"SDL haihusiki: wafanyakazi 8 (chini ya 10)"* (=0);
  model body led with wrong *"SDL = 5,000,000 × 3.5% = 175,000"*.
- **eval_367** (non-resident PAYE): engine appended correct *"15% × 5,000,000 = 750,000"* (D-PAYE-1);
  model body led with wrong *"264,000"* (a bogus progressive-band calc).

This is **not new** (documented in `_validate_and_clean`'s docstring as a deferred fidelity-check follow-up)
but is **not covered** by any D-* fix this session, and is **structurally serious**: it can silently
undermine EVERY engine fix shipped this session by showing the user a wrong number the engine got right.
**Promoted to its own defect item — D-FIDELITY-1 (scoped below).**

### ✅ D-FIDELITY-1 — SHIPPED and GPU-CONFIRMED (2026-07-26) — commit 75421f0

Approved as scoped and SHIPPED. `chike/fidelity.py::body_contradicts_working` +
`_validate_and_clean` blanking (body → `_render` emits the working alone; `raw_text` preserved).
Offline validation: 13/13 detector unit tests (Case A/B/B0 + the 10 benign shapes confirmed never
firing); full suite **270 passed** (was 257); re-render over the saved afef9dd 400 fired on **exactly
eval_367/371/378**, byte-identical on all other 397 rows.

**GPU confirmation run DONE — commit `75421f0`, artifact `eval/results/gate_orchestrator_combined_75421f0.json`**
(fetched independently from HF adapter-v15, verified `commit==75421f0`, 400 rows, 0 empty/ERROR;
judge overlay `providers_served=['DeepInfra']`, seed=42, N=5, 324 graded, **0 API errors**).

**The three target rows — all exactly as scoped (GEN = working alone; RAW retains the wrong body; judge 5/5 correct):**
| row | generated (rendered) | raw_generated (preserved) | pass | judge |
|---|---|---|---|---|
| eval_378 | `SDL haihusiki: …wafanyakazi 8 (chini ya 10)…` (no 175,000) | `SDL = 5,000,000 × 3.5% = 175,000` | True→**False** | correct 5/5 |
| eval_367 | `PAYE (asiye mkazi) = 15% × 5,000,000 = 750,000…` (no 264,000) | `PAYE = 264,000 (15% × 1,760,000)` | **True** (stays) | correct 5/5 |
| eval_371 | `SDL haihusiki: …wafanyakazi 7 (chini ya 10)…` (no 98,000) | `SDL = 2,800,000 × 3.5% = 98,000` | False (stays) | correct 5/5 |

**Only ONE pass/fail flip in all 400: eval_378 (PASS→FAIL).** Zero other flips; `fact_path_190` and
`staged_50` pass counts byte-identical; zero stochastic decode noise this run.

**All bucket movement is eval_378 alone, double-counted.** It is in both bucket C (`compute_type` =
any `compute==True`) and bucket D (`adversarial_150` = `source=='additions_003'`), reliable=True,
genuine — so its single flip drops: compute_type 41→40 (raw) / 23→22 (rel); compute_type_genuine
40→39 / 22→21; adversarial_150 71→70 (raw) / 54→53 (rel). Nothing else moved.

**The literal "v-next ≥ afef9dd per bucket" criterion technically did NOT hold** (compute_type +
adversarial each −1 row, raw and reliable). **The reason is fully understood and is itself evidence of
the fix working, not a regression:** eval_378 went from a false-PASS (regex credited the wrong 175,000)
to a **regex false-FAIL** — the corrected `SDL haihusiki / TZS 0` answer has no numeric key the
number-scorer can match to gold "TZS 0", so regex drops it while the answer is now CORRECT (judge 5/5).
Judge-augmented accuracy flat (76.4%→76.4%); raw/reliable each −1 = eval_378 only. This is exactly the
measurement gap the judge overlay exists to catch — and it caught it.

**Disagreement queue 25+7 → 24+8, fully reconciled:** FP −eval_367 (now regex-pass AND judge-correct →
agree, leaves queue), −eval_378 (→FAIL, migrates to FF), +eval_397; FF +eval_378. eval_371 stays out of
the reliable-only queue (reliable=False → gap-fill, judge=correct). **Zero collateral, zero detector
false-positives:** only the 3 intended bodies were blanked.

**Two follow-ups logged (not urgent, not blocking — tracked, not patched reactively):**
- **SCORER-SEMANTICS-1 — number-scorer should credit "not-applicable / TZS 0" answers.** Concrete
  motivating case: eval_378 gold "TZS 0" is a correct answer that the number-scorer cannot credit when
  the reply says "SDL haihusiki / chini ya 10" (no matching numeric key). Same class as the item-3/item-5
  scorer-semantics gaps; the honest fix is either teach the scorer that gold "TZS 0" is satisfied by a
  not-applicable/zero verdict, or let the judge-augmented number carry it. Explicit, separate decision.
- **JUDGE-NONDET data point — eval_397.** `generated` byte-identical afef9dd↔75421f0 (compute=False, the
  guard never touches it), pass=True both runs; it entered the FP queue only because the judge's
  majority-of-5 verdict shifted **undetermined→wrong** between runs. Pure item-4 judge non-determinism,
  NOT a D-FIDELITY-1 side-effect — logged for whenever judge non-determinism work resumes.

Same characterize-before-fix discipline as decomposition/every structural change this session; original
scope preserved below for the record.

**Mechanism & hook point.** Compute answers merge as `body + '\n' + working` (`orchestrator._render`,
:341), where `working` is the deterministic `ComputationResult.working` and `body` is the model's free
generation. Nothing checks that `body` agrees with the authoritative result. The hook is per-SubAnswer in
`Orchestrator._validate_and_clean` (:319), which already holds both `sub.computation` (structured
`ComputationResult` — has `applicable`, `amount`) and `sub.text` (the isolated model body). Because it runs
per sub-answer, multi-levy fan-out rows are seen one compute at a time — no cross-levy confusion.

**Blast radius (full-400 afef9dd sweep, `scratch/dfidelity_sweep.py` + `dfidelity_detector.py`).** Of 103
compute rows (56 clarified/never-guess skipped), **exactly 3 true body-vs-working contradictions:
eval_367, eval_371, eval_378** (the 2 from the adjudication + eval_371 newly surfaced). 10 further
candidates are BENIGN breakdowns (body faithfully restates the working's figure with intermediate steps /
net-pay extras) and must NOT be touched. **The contradiction class is precise:** it occurs ONLY when the
engine applied a GATING/OVERRIDE rule that moves the answer off the naive `rate×base` (SDL `<10`→not
applicable; PAYE non-resident→flat 15%), and the model recomputed the naive figure anyway — i.e. it
re-derives exactly the *pre-fix* wrong answer, which is why it can silently undermine the session's engine
fixes.

**Detector spec (deterministic; validated EXACT — flags {367,371,378}, 0 false-pos on all 13 candidates):**
- Case A — `computation.applicable is False` (amount None): contradiction iff body contains a naive levy
  compute (`rate% × TZS base = TZS N`) asserting an amount. → covers 371, 378.
- Case B — `computation.amount` is a definite figure: contradiction iff that authoritative amount is
  **ABSENT** from the body while the body asserts some other levy result. (Robust: a faithful body always
  restates the correct figure; checking presence-of-correct is immune to intermediate band-base steps and
  net-pay extras that a naive "extra-number" rule would false-flag on eval_092/191/360/395.) → covers 367.
- Case B0 — amount 0 (within 0% band): contradiction iff body asserts a nonzero `= TZS N`.

**Proposed fix (deterministic, preferred over prompt).** On a detected contradiction, blank `sub.text`
(preserving `raw_text` for offline rescore) so `_render` emits the **authoritative working alone** (already
user-facing Swahili). Deterministic is chosen over prompt-hardening because (a) the model ALREADY receives
the working as a ground-truth "fact" in `_build_compute_prompt` and still ignored it in all 3 cases, so a
prompt can't *guarantee* deference; (b) it matches the architecture's load-bearing invariant *"arithmetic is
NEVER trusted to the model"* (ADR 0001). Prompt hardening is at most a complementary secondary measure.
Gate impact: eval_371 already fails (no change); eval_367/378 are current false-PASSES → corrected to the
right answer, removing a user-facing wrong number with no expected gate-number regression.

**Validation plan (same standard as D-NSSF-1/D-PAYE-1).** (1) Unit tests for the detector across Case
A/B/B0 + the 10 benign shapes (must stay untouched). (2) Offline re-render over the saved afef9dd 400: the
detector must fire on exactly the 3, and re-rendering them working-only must be correct; all other 100
compute rows byte-identical (proves no regression on saved data). (3) Fresh GPU full-400 orchestrator sweep
(founder-executed), require v-next ≥ afef9dd on every bucket. (4) Judge overlay rides along to confirm the 3
move to judge=correct. **Awaiting approval before writing any code.**

### Work item 1 — CENSUS of the 400-question gate (DONE, 2026-07-25)

**Harness:** `scripts/judge_regression_400.py` — a **local** re-point of `kaggle/judge_regression.py`
(the judge is pure OpenRouter `qwen/qwen3-32b`, no GPU, so it runs locally off `OPENROUTER_API_KEY`).
Input is **pinned to the committed** `eval/results/gate_orchestrator_combined_5239190.json` (baseline
archived this session, commit `959283f`); the harness asserts `commit == '5239190'` on load so it
cannot run against a stale baseline. Grades `row['generated']` directly (already `reply.text`); trusts
the stored `reliable`/`pass` fields (they *are* the 5239190 verdicts being characterized).

**Scope decision — CENSUS, not a sample.** `reliable=False` means "the regex scorer has low confidence
in its own verdict," **not** "the system failed to answer" (all 400 produced a real answer; 0 empty, 0
ERROR). So `reliable=True` means *regex is confident, not regex is right* — and this session has
repeatedly found confident-but-wrong regex verdicts. A 40-question spot-check of the 252 reliable
verdicts was rejected on the statistics (at a 3% true error rate — the order of bugs already found — a
clean 40-sample happens **30%** of the time; the 252 population is too small for an efficient middle
sample; the census costs only ~2¢/~3min more). So the judge did two jobs at once: **gap-fill** the 133
excluded **and audit** the 252 reliable.

**Run actuals:** 399 calls (14 audit + 385 non-refusal), **$0.0407**, ~438s total (STAGE 2 349s @ 8
workers), **0 API errors**. Output: `eval/results/judge_regression_qwen3-32b_400.json`.

- **STAGE 1 judge-trust: 10/14** vs hand-truth (down from 12/14 @190: 1 false-demote eval_176, 2
  false-promote eval_093/059, 1 undetermined eval_026). **The judge itself disagrees with hand-truth
  ~1-in-4 — so every candidate below is an adjudication LEAD, not a verdict** (this is exactly why
  work item 2 = real adjudicated ground truth exists).
- **GROUP 1 gap-fill (133 by exclusion reason):** compute_derived_number 48 (25 correct / **21 wrong** /
  2 undet), yes_no_polarity_unverifiable 28 (6 / **21 wrong** / 1), qualitative_number_no_numeric_key 27
  (18 / 7 / 2), yes_no_ground_truth_ambiguous 9 (6/2/1), morphological_overlap_gap 7 (6/1/0),
  year_only_numeric_key 6 (5/1/0), zero_or_not_applicable 6 (2/**4 wrong**/0), year_collision_match 2
  (2/0/0). The gap is **not** uniformly-correct-but-unscorable: ~57/133 read wrong, concentrated in
  compute-derived and polarity-unverifiable.
- **GROUP 2 regex-audit (252 reliable):** **27 false-pass** (regex PASS, judge WRONG) · **12 false-fail**
  (regex FAIL, judge CORRECT) · 17 undetermined · 30 clarified (deliberate, excluded — not bugs) · 166
  agree. Full disagreement IDs in the artifact; this list *is* the deliverable that turns work item 2
  from "audit a sample" into "adjudicate this concrete list."

### Work item 3 — procedure/definition over-strictness characterization (DONE, 2026-07-25)

**Method.** Ran the live `chike/scoring.py` functions against the 10 adjudicated false-fails
(eval_029/074/094/131/134/187/217/230/233/390), pulling each model output from the pinned
`5239190` baseline, to get exact matched-token sets rather than reasoning about the regex by
hand. The 10 resolve to **6 precise mechanisms**, only ONE of which is a cheap, narrow,
deterministic fix in the `'000'`/BUG-7 class; the rest are genuinely semantic → item 5.

**Sub-pattern 1 — spurious numeric key from a numeral-word inside the idiom "moja kwa moja"
(="directly"). ✅ FIXED (commit `22af4ad`).** `extract_numbers` matched `\bmoja\b`→`1` inside
the idiom, injecting a junk key that (a) suppressed the `qualitative_number_no_numeric_key`
exclusion → false FAILs (eval_134, eval_217), and (b) collided with the same idiom in the
model's own answer → coincidental false PASS verifying no content (eval_037). Blanking the
trigram before numeral extraction is **tightening-only** (removes a spurious key, never adds
one — the property that made the `'000'`/BUG-7 fixes safe to ship narrowly). Full-400 sweep:
exactly eval_037/134/217 → `qualitative_number_no_numeric_key`; eval_033 no-op; zero others.
7 new tests (`tests/test_scoring_number_idiom.py`); full suite 242 passed.

**Everything below → item 5's semantic-judge worklist (do NOT regex-patch):**

- **Sub-pattern 2 — answer_type mislabel: entity/enumeration typed `number`.**
  - eval_094 — answer IS the entity "NSSF"; the only numeral (`mbili`="both") is incidental.
    *Candidate one-line gold relabel* `number`→`definition` (would let vocab-overlap score it) —
    but that is a DATA-correctness decision, held to the same verify-and-review standard as every
    other gold change this session, NOT bundled into the scorer fix.
  - eval_074 — answer is "at least two", but the model conveys the count by ENUMERATING BRELA+TIN;
    needs enumeration understanding → semantic.
- **Sub-pattern 3 — terse-but-correct def/proc defeated by surface mismatch. NOT a narrow fix.**
  - 3a punctuation glued to tokens (`(input`, `refund).`, `pembejeo.`) — eval_029. The "obvious"
    fix (strip punctuation off tokens) was SIMULATED across the 400 and **flips 19 verdicts, all
    loosening, direction-indeterminate without per-case review** — exactly the "trade one failure
    mode for another" trap this session already learned to reject (embedding/NLI router). eval_029
    resolves at item 5 as part of an adjudicated batch, not via a blanket patch.
  - 3b synonym substitution (`jedwali`≈`orodha`) + gold padded with proper nouns a good answer need
    not echo (PKF, VELMA, TanzLII) — eval_131. Inherently semantic.
- **Sub-pattern 4 — "no fixed figure applies" (qualitative number).** eval_134/217 — **subsumed by
  the sub-pattern 1 fix** (once the junk key is gone, the existing BUG-1 exclusion fires).
- **Sub-pattern 5 — number answer mislabeled `definition`.** eval_233 ("10 employees" threshold typed
  `definition`; model states the correct `10`, but def-scoring ignores numbers AND bare 2-digit `10`
  is not captured by `extract_numbers` anyway). Relabel insufficient; 2-digit bare capture too risky
  globally → item 5.
- **Sub-pattern 6 — negative-question polarity trap (affirming a negative).** eval_390: gold "Ndiyo,
  haitozwi" vs model "Hapana… hazitozwi VAT" — substantive clauses AGREE ("hazitozwi"), only the
  leading polarity word inverts under negative framing. The documented flat-lexicon gap → semantic/NLI.

**Item-5 adjudication worklist compiled here** (structured input for the integration design):
| lead | sub-pattern | disposition |
|------|-------------|-------------|
| eval_094 | 2 entity-mislabel | candidate gold relabel (verify separately) OR judge |
| eval_074 | 2 enumeration-count | judge (list satisfies "at least two") |
| eval_029 | 3a punct + the **19 punctuation-strip flip candidates** | judge-adjudicate each; NO blanket patch |
| eval_131 | 3b synonym + proper-noun padding | judge |
| eval_233 | 5 number-as-definition | judge (relabel insufficient) |
| eval_390 | 6 negative-polarity trap | judge/NLI (content agrees, polarity word inverts) |

**Scope note.** Legacy `scripts/run_eval.py` and `scripts/build_eval_notebook.py` carry their own
divergent `extract_numbers` (missing even the `'000'`/BUG-7 fixes) — NOT the shared scorer the
400-gate runs, so left untouched. Flagged, not fixed here.

### Work item 4 — judge non-determinism: DATA-GATHERING DONE (2026-07-25); N=5 majority-vote proposed, integration deferred to item 5

**Root causes characterized** (why qwen3-32b flips verdicts even at temp=0 on `judge_regression.py`):
no seed, no provider pin (OpenRouter routes to different backend providers between calls), temp=0
not truly deterministic under batched GPU serving, and a fragile JSON/substring parse fallback.

**Option A (pin `seed=42` + single provider DeepInfra, `allow_fallbacks:false`) — tested at two scales:**
- **14-example STAGE-1 audit set** (`scratch/judge_determinism_optionA*.py/.json`): baseline flip_rate
  4/14, truth-match 13/14; pinned flip_rate **1/14** (75% reduction), truth-match 13/14, 0 false-
  demotes/promotes. The one residual (eval_026) was benign (correct↔undetermined only).
- **39 census disagreement IDs** (`scratch/judge_determinism_scale39.py/.json`, N=6 pinned,
  DeepInfra served all 234 calls, seed=42 — run COMPLETED before a PowerShell crash; result file
  is whole and was recovered, no re-run/duplicate spend): flip_rate **7/39 (18%)**, and crucially
  **2 correct↔wrong (DANGEROUS) flips appear at scale** (eval_228, eval_230) that the 14-set did not
  show. This is the session's recurring "clean at small N, fails at scale" pattern — **pinning
  reduces but does NOT eliminate the safety-relevant flip.**

**Subsample sufficiency proof (all 39 IDs, ref = majority-of-6):** every unstable case is a **5-1
split** (7 unstable all 5-1; other 32 unanimous 6-0). Simulating all C(6,3)=20 and C(6,5)=6
subsamples per ID: **0/780 three-draw and 0/234 five-draw subsamples disagree with the majority-of-6**
— including both dangerous IDs (0/20 each at N=3). Structurally, a 5-1 split *cannot* flip majority-of-3
(minority appears once, needs ≥2 to win). **So majority-of-3 is provably sufficient on all observed
data** — not luck.

**Why N=5 is proposed anyway (final design recommendation):** majority-of-3's safety is *contingent
on instability never exceeding 5-1*. The failure boundary is a **4-2 split**: at N=3 the minority wins
**4/20 = 20%** of subsamples (majority-of-3 flips); at N=5 it is **0%** (2 can't reach 3-of-5). No 4-2
case appeared across 39×6 draws, but that is a thin basis to assert 4-2 never occurs in the full 400.
**Majority-of-5** costs ~1.67× N=3 (~3¢/run at this scale), is robust to both 5-1 AND 4-2, and its only
failure mode — a genuine **3-3** tie — is an honest judge coin-flip that should resolve to
`undetermined` (a clean hook for item-5 integration), not silently pass/fail. Per the session's
no-extrapolation discipline, spend the extra two draws.

**Nature of the 2 dangerous flips (diagnosed — NOT a numeral misread → majority-vote IS the right fix,
no narrower cause to target):**
- **eval_228** (stamp duty on MoA, `brela_registration`): gold is itself a **hedge** ("commonly cited
  TZS 10,000 but not confirmed — confirm TRA"); model gave a **pure refusal** ("outside my knowledge,
  confirm TRA"). The 5-1 (majority=wrong) is the genuine question of whether a refusal *satisfies* a
  hedge-gold or *under-answers* it (dropped the "10,000 commonly cited" surfacing). Census single-shot
  drew the 1/6 "correct" outlier — direct evidence the single-shot census verdict is itself exposed.
- **eval_230** (PAYE personal relief, `paye_compliance`): model gets **core polarity right** ("no
  separate personal relief" — matches gold) but the elaboration is muddled; 5-1 majority=correct, the
  1/6 outlier penalizes the muddle.
- Both are legitimate borderline judgments on qualitative/refusal answers vs non-clean-numeric golds —
  real epistemic borderline-ness, exactly what majority-voting is for. No systematic misread pattern.

**Status:** the DATA-GATHERING half of item 4 is COMPLETE and conclusive. The remaining half — wiring
pinned-provider + majority-of-5 (with 3-3→undetermined) into `judge_regression.py` and the item-5
scorer integration — is deferred to **item 5** (integration design), where the judge becomes a
confirmation layer. No code wired this turn; `judge_regression.py`/`scoring.py` unchanged.

### 🚑 NEW DEFECT surfaced by the census — NSSF employee-deduction is a rules-engine error (NOT scoring, NOT #3)

**Highest-stakes finding, root-caused precisely — do NOT file this under the scorer work.** Four
false-passes (eval_091 gate, eval_274/282/330 additions; plus compute-derived instances) show the
system reporting **double the correct NSSF deduction**. Investigated to ground:

- **It is a rules-engine answer-*selection* error, not a rate-knowledge error and not flat-20% belief.**
  All are **compute-routed**; the figures come from `chike/rules_engine/nssf.py::compute_nssf`, which sets
  `amount = gross × (employer_rate + employee_rate)` = the **20% both-parties total**. The rates are
  correct (`NSSF_EMPLOYER_RATE=NSSF_EMPLOYEE_RATE=0.10`) and the engine explicitly decomposes and prints
  the correct halves ("mwajiri 80,000 + mfanyakazi 80,000"). But all four questions asked *"kiasi gani
  kinakatwa mshahara **wake**"* / *"NSSF **anayokatwa**"* — **how much is deducted from the employee** —
  whose correct answer is the employee's 10% half (80,000 / 75,000 / 64,000 / 45,000, confirmed by every
  gold: *"NSSF ya mfanyakazi ni asilimia 10"*). The engine **computes the correct employee figure but
  returns `total` as the headline `amount`**, so a user asking "how much NSSF comes off my 800k salary?"
  is told **160,000 when the answer is 80,000**. Returning `total` is correct for a "total remittance /
  how much do I as employer pay" framing — the bug is that the engine has **no notion of the question
  sub-framing** (employee deduction vs employer share vs total) and always returns the total.
- **Systematic & deterministic** (engine logic, not sampling) — hits *every* employee-deduction-framed
  NSSF compute, not just these four. **User-facing** (doubles stated payroll deduction), currently
  **hidden by scorer leniency** → higher priority than any scorer fix.
- **Compounded by an independent scorer-leniency bug** (the known number-overlap class): the regex marked
  these PASS because the correct 80,000 appears as an incidental sub-component in the working string.
  Fixing one does **not** fix the other.
- **NOT in scope for follow-up #3** (which is about the scorer). Tracked as its own defect below.

**Separately — eval_259 is a DIFFERENT genuine content error** (not the NSSF pattern): the engine computed
**WCF as 0.5% of vehicle value** (TZS 40M → 200,000) instead of 0.5% of payroll — it took the trap
question's irrelevant figure as the base. Also false-passed (definition-vocabulary overlap). Distinct
root cause.

### NEW TRACKED DEFECTS (rules-engine / scorer — separate from follow-up #3's five items)
- **D-NSSF-1 (user-facing, HIGH): ✅ FIXED (2026-07-25).** `compute_nssf` returned the 20% total as
  `amount` even when the question asked for a single party's share. Scope was **broader than the 4 the
  judge flagged** — the full-400 sweep found **12 single-party questions** (8 employee: eval_091/241/248/
  274/282/296/330/386; 4 employer: eval_090/092/243/289) all wrong-headlined, plus the ~total questions
  that were already correct. Fix (3 parts): (1) `routing.nssf_party(text) → employee|employer|total`,
  pure-lexical with **precise total cues (never bare `jumla`)** so the gross-salary phrase "mshahara wa
  jumla" (eval_090) does not misroute to total, and employer precedence over the incidental "mfanyakazi";
  (2) `compute_nssf(party=…)` selects the headline `amount`/`working`, keeping the 10/10 breakdown for
  transparency — `party='total'` string is **byte-identical to pre-fix**; (3) narrow levy-gated wiring in
  `orchestrator._answer_compute`. **Validation:** 36 routing+engine unit tests (all 12 cases + the two
  traps + total byte-identity); full-400 deterministic sweep = **0 party mismatches, 0 total-working
  diffs**; **full suite 221 passed**. Known-harmless edge: eval_095 (self-employed voluntary, gold 20%)
  detects `employee` but has no salary → clarifies before compute, so party never applies (documented, not
  a regression). **Gate-number caveat holds** — several of the 12 already showed `pass=True` via number-
  overlap masking, so the fix corrects the *advice*, not necessarily the gate integer; confirmation folds
  into the next full 400-run.
- **D-WCF-1 (content, MED): ✅ FIXED (2026-07-25).** WCF was computed on a non-payroll base (vehicle
  value) for eval_259 (*"Magari yangu ya biashara yana thamani ya TZS 40,000,000 … WCF yake?"*) because
  `swahili_numbers._WRONG_BASE` caught `mtaji`/`mapato`/`hisa` but had **no asset/vehicle-value pattern**,
  so the 40M was read as gross payroll. `compute_wcf` itself was correct — this was an **extraction**
  wrong-base gap. Fix: added `thamani ya magari|gari|mali|vifaa|mtambo` + the general `thamani ya \w+`
  prefix to `_WRONG_BASE`. **Validation:** eval_259 now `detect_wrong_base=True` → clarifies (matches
  gold); full-400 sweep of the new pattern = 4 matches, and **0 regressions** — eval_259 is the target;
  eval_256 was *already* caught by the existing `hisa` pattern (unchanged); eval_051 (EFD threshold fact)
  and eval_197 (stamp-duty refusal) are fact/refusal-path so they never invoke `detect_wrong_base`
  (call site is extraction.py:246, compute-path only). New unit test + full suite **222 passed**. A
  legitimate payroll figure is phrased "mshahara wa"/"analipwa", never "thamani ya", so no payroll
  question regresses to an unnecessary clarification.
- **D-WCF-2 (content, MED; one HIGH sub-case): ✅ FIXED (2026-07-25, commit `fd150d1`).** Direct extension of
  D-WCF-1: `_WRONG_BASE` caught asset-value bases (`thamani ya X`) but not **market value, rent, savings,
  utility cost, bank loan, or business cash flow** offered as a payroll base for SDL/NSSF/WCF/PAYE. Full-400
  sweep found **6 cases (2 beyond the 4 flagged): eval_253** (deni la benki), **254** (bei ya soko — the HIGH
  one, was mis-computing `WCF = 0.5% × 25,000,000 = 125,000`), **255** (mzunguko wa fedha/cash flow), **258**
  (kodi ya pango), **260** (akiba), **261** (gharama za umeme). 8 new terms, precision-scoped:
  `gharama za umeme`/`maji` (not broad `gharama za \w+` → would hit `gharama za mishahara`); `\bdeni\b` word
  boundary (catches `deni la benki`, not `madeni`). **Validation:** new unit test (6 caught + exclusions);
  full-400 no-regression sweep **on the real call path** (detect_wrong_base is invoked only from the compute
  path via `extraction.py:246`) = **delta exactly the 6 targets, 0 unexpected, 0 legit-payroll caught**.
  eval_218 confirmed unaffected (intent `none`/fact path, never calls detect_wrong_base — the initial sweep
  phantom-counted it off-path). **Gate caveat:** 5 of 6 already `pass=False`; the fix corrects the advice /
  kills the wrong number, folds into the held eval.py run.
- **D-WCF-3 (content, MED — TRACKED, NOT fixed): the inverse problem.** eval_324 (*"…mishahara TZS 4,800,000
  kwa watu 13, na madeni TZS 2,000,000, na faida TZS 1,000,000 — SDL?"*) states a **legit payroll base**
  (gold wants SDL = 3.5% × 4,800,000 = 168,000) but a distractor `faida`/`madeni` figure fires `_WRONG_BASE`,
  so it clarifies instead of computing. This is **not** a term-addition problem (D-WCF-1/2's shape) — it needs
  logic to suppress the wrong-base veto when an explicit `mishahara/analipwa TZS <amount>` payroll figure is
  present alongside the distractor. Its own investigation; queued, do not fold into D-WCF-2.
- **D-DECOMP-1 (completeness, MED; one HIGH false-pass): ✅ FIXED (2026-07-25, commit `4c7d5e5`).** A compute
  part naming **several levies** ("...SDL na NSSF...", "SDL, NSSF, PAYE na WCF") routed to only the first
  (`_explicit_levy` returns the first match), **silently dropping the rest**. eval_318 was a `pass=True`
  false-pass concealing a dropped NSSF. Fix: `routing.all_explicit_levies(text)` + `orchestrator.
  _fan_out_multi_levy()` expand a multi-levy compute part into one compute per named levy (shared text, own
  extraction + engine). **Full-400 structural sweep:** exactly **6 fan out** (eval_318/319/320/321/323/327,
  measured not assumed); the other **394 are byte-identical at object identity** (`fanned[i] is routed[i]`),
  so single-levy output is provably unchanged. **Phase B invariant re-verified** (fan-out only adds to
  `compute_parts`, never folds into the pooled fact gen) — both existing guards
  (`test_mixed_compute_and_fact_keeps_two_distinct_sources`, `test_multi_compute_parts_are_not_collapsed`)
  re-run and pass. 3 new tests; **full suite 235 passed**. Fixes eval_318 fully; advances 320/321.
  - **Per-person / tiered / conditional aggregation (eval_319/327/323) — SEPARATE follow-on, tracked:** the
    fan-out now computes each named levy, but these three carry a compounding need the fan-out does NOT solve —
    per-person aggregation ("14 × 500,000"), tiered payroll ("4×700k + 6×300k"), conditional headcount ("if I
    add 9 to reach 10"). They now surface that need per-levy instead of silently dropping a levy. Own item.
  - **eval_326 (D-DECOMP-2 — two-employee mixed-residency split): deferred.** "Mfanyakazi ni mkazi analipwa X
    na mwenzake si mkazi analipwa Y — PAYE ya kila mmoja?" No decompose signal fires; it's one PAYE compute
    over two salaries → per-person ambiguity → **safe clarify**. Fixing needs splitting by employee AND applying
    residency per split (intersects D-PAYE-1). Rare (1/400), currently safe (not a wrong number). Queued.
- **D-PAYE-1 (user-facing, HIGH): ✅ FIXED (2026-07-25, commit `0785c7a`).** Same class as D-NSSF-1 —
  the engine already implements the flat-15% non-resident branch (`compute_paye(resident=False)`) but
  nothing upstream ever determined residency, so **every** PAYE compute defaulted to progressive resident
  bands. eval_367 (*"Mfanyakazi asiye mkazi analipwa TZS 5,000,000 … PAYE yake?"*) returned **1,328,000**
  (progressive) instead of the correct **750,000** (15% flat, = gold). Fix: `routing.paye_resident(text)
  → bool`, negated-residency cues (`asiye mkazi`/`si mkazi`/`wasio wakazi`/`non-resident`), **guarded
  against the mixed two-person case** (eval_326: one resident + one non-resident — a scalar flag can't
  express both, so the precise `ni mkazi` cue keeps it resident-default and defers to the decompose/merge
  item); narrow levy-gated wiring in `orchestrator._answer_compute`. **Validation:** full-27 PAYE-compute
  sweep = **25/27 byte-identical** (resident=True, unchanged working), exactly 2 flip (eval_344/367);
  eval_218/392 are `compute=False` so `paye_resident` is never invoked (untouched); 9 new unit tests;
  **full suite 231 passed.** One over-broad cue caught in testing (`mkazi analipwa` matched inside `asiye
  mkazi analipwa`, reverting eval_367 to resident) and narrowed to `ni mkazi` before shipping. **Gate-
  number caveat holds** — offline fix, confirmation folds into the next 400-run.
  - **eval_344 (false-premise yes_no, no amount): ✅ CONFIRMED ALREADY-FIXED (2026-07-25).** When D-PAYE-1
    reasoned this "routes to clarification," it was reading the **5239190 baseline output** — but that
    baseline (2026-07-23) **predates the money-ask guard** (`5d806c6`, 2026-07-24). `git merge-base` confirms
    the guard is not an ancestor of the baseline. Current `detect_intent` routes eval_344 (and its 4 siblings
    eval_099/335/337/342 — the true blast radius of the rate/mechanism-confirmation-yes_no-naming-a-compute-
    levy pattern) to `'none'` (fact/RAG); `tests/test_routing.py:188-243` already lock all of them (15/15
    pass). **No fix needed** — the answer-correctness (does fact/RAG actually refute the false rate) folds
    into the held eval.py run. Lesson: baseline outputs are pre-fix snapshots; always re-test current
    `detect_intent`, don't infer routing from the pinned baseline.
  - **eval_311 (applicability-detector gap, LOWER priority — tracked, queued after decompose/merge):**
    *"Nina mfanyakazi mmoja tu anayelipwa TZS 500,000, je bado nachangia WCF?"* routes to compute `wcf`
    but `is_applicability_question` does not catch "bado nachangia", so it doesn't get the clean
    applicability "Ndiyo — WCF kutoka mfanyakazi wa kwanza" answer. Lower severity than a wrong-number bug
    (a **missed correct answer**, not a confidently-wrong one). Fix later by extending the applicability cue
    set; do NOT fix now.
  - **eval_326 (→ decompose/merge, with eval_318):** two employees of differing residency in one question;
    deferred, guarded to resident-default so the resident half is not wrongly billed 15%.
  - **eval_218 / eval_392 (→ fact/RAG queue):** both `compute=False`. eval_218 is non-resident **rental**
    withholding (a different tax entirely); eval_392 is a yes_no answered wrongly on the fact/generate path
    (needs the non-resident flat-15% fact retrievable). Neither is a compute-wiring bug.
- **D-VATWH-1 (fact-base, HIGH): ✅ RESOLVED (2026-07-25).** The VAT-withholding **base** was internally
  contradictory across the fact base (work item 4): three "CONFIRMED" facts encoded a **VAT-amount** base
  (3%/6% × VAT), while `VAT_withholding_base_disputed` said the base was unresolved and the eval golds
  (eval_034/315) used the **consideration** base — so eval_034/315 were stuck permanently "ambiguous" and
  any future VAT-withholding work risked building on the wrong side. **Resolved by PRIMARY legislation**
  (not practitioner summaries): **Finance Act 2025 (Act No. 11) s.124** inserts VAT Act Cap.148 **s.5(5)** —
  the 18% standard rate is split, the withholding agent withholds **3% (goods) / 6% (services) of the
  supply** and the supplier receives **15% / 12%** respectively (3+15 = 6+12 = 18). The statute's express
  **12% supplier share for services** is decisive: it is impossible under a VAT-amount reading (which would
  leave the supplier ~94% of the VAT). Corroborated by **GN 352K of 30/6/2025** reg 31B + the withholding
  certificate form (signed Minister for Finance, 29 Jun 2025). Both TRA-hosted PDFs were fetched and text-
  extracted locally. **Verdict: consideration base is correct; the eval golds were right all along; the
  model + `vat_withholding_formula_correct` were wrong.** Corrected 5 fact entries (`vat_withholding_goods`,
  `vat_withholding_services`, `vat_withholding_formula_correct`, `VAT_withholding_base_disputed` →
  RESOLVED, `vat_withholding_buyer_remits_directly`), un-inverting `wrong_patterns` that were flagging the
  now-correct consideration answers and adding the VAT-amount error as the new wrong pattern (verified:
  golds not flagged, model errors caught). **No training pairs asserted the wrong formula** — the one
  matching cleaned pair (batch_015) is a *hedge* ("base varies by source, confirm TRA"), now improvable to
  the confirmed formula (optional follow-on). **Two bonus findings** from the primary text: (1) the
  **effective-date** discrepancy is explained — VAT withholding is **1 Jul 2025** (fact base correct); the
  "1 Sep 2025" some secondary sources cite is the *separate* 16% B2C e-payment rate in **s.5(6)**, not the
  withholding. (2) `vat_withholding_certificate_timing` and `vat_withholding_buyer_remits_directly` were
  **already correct** — confirmed by s.90B ("certificate not later than the day VAT becomes payable under
  s.15") and the s.71 amendment (supplier subtracts withheld output tax only with a valid certificate).
  **D-VATWH-1 RAG regeneration ✅ DONE + DEPLOYED (2026-07-25, index commit `afba3a2`).** R15 ran on Kaggle,
  the e5 index was fetched from HF (`prospAprospA007/africa-giants-dataset`), committed byte-identical to BOTH
  `chike-inference/` and `kaggle/` (sha256 verified matching), and **Modal was redeployed** — the corrected
  consideration-base VAT-withholding facts are now live in production. Index is 213 facts (was 211).
  **Remaining:** the `kaggle/eval.py` gate confirmation is intentionally HELD for ONE comprehensive run after
  all of follow-up #3 is complete (not per-change), so gate-number confirmation folds into that single run.
- **D-MODELRAG-A (fact-base GAPs, MED — item (3) Group A): ✅ FACTS ADDED (2026-07-25), RAG regen PENDING.**
  Of the 8 confirmed model/RAG factual-error cases, the 4 traced to a **missing fact** were investigated;
  primary-source verification + two new locked facts drafted and added:
  - **`brela_business_structures`** (eval_071 + eval_304): the model answered "how many business structures"
    with IP categories (it retrieved the adjacent `BRELA COSOTA split` IP fact), and fabricated "register a
    company if 10+ employees". New fact enumerates the 3 legal forms (sole proprietor + partnership = business
    name under Business Names (Registration) Act Cap.213; company under Companies Act Cap.212) and states the
    choice is independent of headcount/capital, distinguishing IP. Verified against the BRELA-hosted Acts
    (Cap.213 s.2 definition; Cap.212) + brela.go.tz.
  - **`wcf_paid_to_fund_not_tra`** (eval_123): the model said WCF is paid to TRA. New fact: WCF paid directly
    to the Fund via portal.wcf.go.tz, NOT TRA (SDL -> TRA); employee does not contribute. Verified against
    wcf.go.tz/pages/contribution + Workers Compensation Act No.20 of 2008.
    **Validation:** both facts' `wrong_patterns` run against all 400 gold + 400 model answers — 0 gold or
    correct-answer false-flags; the only model hit is eval_304's own wrong answer (guard working as intended).
    Patterns kept conservative (they don't try to catch the eval_071/123 model outputs — the corrective
    mechanism is RAG surfacing the new facts after R15, not the training-guard regex). **RAG regeneration
    ✅ DONE + DEPLOYED (index commit `afba3a2`)** — the single R15 run covered D-VATWH-1's 5 corrected facts +
    these 2 new facts (BRELA/WCF) + the concise-EFD embedding fix (Group B, eval_347) = 8 fact changes; index
    now 213 facts, committed byte-identical to both dirs and live on Modal. `kaggle/eval.py` gate confirmation
    HELD for the single comprehensive run after all of follow-up #3.
  - **eval_223 (EAC STR) — EXCLUDED from the active defect/gate queue:** *out of active scope — Tier 1B
    (EAC/STR) not yet started per CLAUDE.md §5, deferred until Tier 1A gate passes and Tier 1B unlocks.* No
    STR fact verified or drafted; pulling Tier 1B content forward to pass one eval question would be working
    backward from a test case rather than respecting the project's tier-staging plan.
  - **Group B (eval_162 mgeni, eval_347 EFD) — probed on Kaggle, split confirmed:**
    - **eval_162 — HALLUCINATION, CLOSED:** the v2 two-arm probe (`kaggle/retrieval_probe_group_b_v2.py`)
      showed the target fact IS recovered (in the top-3 the model saw); the model fabricated the
      citizen-becomes-mgeni criteria anyway. Not fixable at fact-base/retrieval — feeds semantic scoring
      (item 5), like Group C.
    - **eval_347 — RETRIEVAL gap, FIX APPLIED (pending R15):** `efd_threshold_tzs_11m` was English-only
      (`key:value` fallback) while the hijacking competitor `vat_registration_threshold_annual` is a concise
      Swahili fact of the same 200M magnitude and near-identical "Kizingiti cha … mauzo ya" phrasing. v2
      detail: the number-stripped arm DID surface the EFD fact, but only at **s#2** — it lost the single
      append-only promotion slot to `efd_approved_supplier_verification` (s#1) **by one rank**. Fix: a concise
      Swahili-first `CONCISE_BILINGUAL_FACTS['efd_threshold_tzs_11m']` entry (value at front, distinctive
      'kuanza kutumia EFD' tokens, explicit "200M = VAT-registration, si EFD" contrast for eval_347's false
      premise) — same figure, no new claim, same precedent as `gn487a_prohibited_activity_3`/
      `gn487a_marriage_no_exemption`. Guarded by **two verification tuples** in `regenerate_rag_e5.py` (EFD
      query → 11M; VAT-reg query → 200M anti-displacement bracket). Narrow the 200M contrast if the regen gate
      flags displacement (GN487A narrowing precedent). **✅ DEPLOYED in the R15 batch (index commit `afba3a2`);
      the fetched index carries the concise EFD fact AND the VAT-reg fact (displacement sanity passed on
      presence; ranking to be confirmed in the held eval.py run).** Broader idea noted
      but OUT OF SCOPE: the "promote only the first new fact" append rule cost the EFD fact its slot by one
      rank — worth revisiting the merge rule separately, not in this fix.
  - **Group C (eval_047, eval_210) — NO fix (correct):** correct fact exists, indexed, effectively surfaced;
    model appended false detail anyway. Not fixable by fact-base/retrieval — feeds semantic scoring (item 5).
- **D-SCORER-1 (scorer leniency, MED — feeds work item 5):** number-overlap credits a PASS off an
  incidental correct sub-figure while the headline answer is wrong (the NSSF cluster + others among the
  27 false-pass candidates). Adjudicate the 27 list; this is the concrete evidence for the judge-as-
  confirmation-layer integration.

**CAVEAT preserved (also embedded in the artifact JSON):** the judge is **not** ground truth (work item 2).
A judge-vs-regex disagreement is a **candidate** to adjudicate, not an automatic correction; STAGE 1 was
10/14, so a fraction of the 27/12 will be judge errors. The NSSF cluster, however, is unambiguous on
direct inspection of the engine + golds.

**Work-item status:** 1 (census) DONE, 2 (adjudication → 39-candidate confusion matrix) DONE, 3
(procedure over-strictness) DONE, **4 (non-determinism) DATA-GATHERING DONE** (pinned + majority-of-5
proposed; wiring deferred to 5). **Item 5 (integration design) NOT started** — this is now the single
remaining work item: wire pinned-provider + majority-of-5 judge (3-3→undetermined) as a CONFIRMATION
layer over `reliable=False` into `scoring.py`/the gate, using the adjudicated disagreement list.

### Router-investigation follow-up tracker (3 items) — ✅ CYCLE CLOSED (2026-07-26)
**All three follow-ups done; comprehensive confirmation run `afef9dd` closes the entire router-investigation
/ defect-fix cycle (see the 🏁 CLOSE-OUT entry above).** Only work item 2 (real adjudicated ground truth,
founder-gated) remains open, with its fresh 25+7 disagreement queue as input.
- **#1 — generic explicit-levy money-ask guard: ✅ DONE** (commit `5d806c6`).
- **#2 — ordinal-enumeration decomposition (`_split_ordinal_enumeration`): ✅ DONE** (commit `d86b92e`).
- **#3 — frontier-judge / semantic scoring: ✅ DONE** — work item 1 (scale to 400 census) DONE
  (2026-07-25); work item 2 (adjudicate the 39-candidate disagreement list → confusion matrix, judge
  92.9% accurate on 28 clean cases) DONE (2026-07-25); work item 3 (procedure over-strictness) DONE
  (2026-07-25); **work item 4 (non-determinism) DATA-GATHERING DONE (2026-07-25)** — pinned + majority-of-5
  proposed (subsample proof: 0/780 flips at N=3 across 39 IDs, but N=5 chosen for 4-2 robustness), wiring
  deferred to item 5; **work item 5 (judge→scoring integration) BUILT (2026-07-26)** — `chike/judge.py`
  (pinned + majority-of-5 + confirmation-overlay aggregation) wired into `eval_orchestrator_combined.py`
  as a report-alongside overlay + `scripts/judge_augmented_local.py` local twin; `scoring.py`/`GATE PASSED`
  unchanged; 15 new tests, `tests/` 257 passed. From the adjudication defect queue: D-PAYE-1 FIXED,
  D-VATWH-1 (VAT-withholding base) RESOLVED by primary law. **All 5 work items of #3 built and CONFIRMED at
  scale** by the comprehensive `afef9dd` run (2026-07-26): reliable buckets +5.8 to +7.6 pts across all
  touched clusters, judge-augmented (76.4%) reconfirms reliable-denom (77.0%) a second time, zero engine-
  introduced prohibition inversions. Work item 2 (real adjudicated ground truth) is the only open piece —
  the prerequisite before promoting the judge-augmented number to the live gate; its input is now the fresh
  25+7 disagreement queue. Also surfaced a
  STRUCTURAL GATE FINDING (eval.py never applied `scorer_reliability`; see top headline). NEW defects
  D-NSSF-1 / D-WCF-1 / D-PAYE-1 / D-VATWH-1 / D-SCORER-1 (tracked above, separate from #3).

## ✅ Generic explicit-levy money-ask guard — SHIPPED (2026-07-24) — router follow-up #1 of 3

**The first of the three tracked follow-ups from the Phase D router investigation (the
applicability-vs-amount fix `f200a4e` and the natural-path money-ask guard were the earlier two
guards this mirrors).** `chike/routing.py`'s explicit path committed to compute on nothing more
than *a levy name + any digit* (`if explicit and _has_number(ql): return explicit`) — no
money-ask/obligation-cue guard, unlike the natural path (requires `_has_money_ask`) and
`is_applicability_question` (rejects when `_has_money_ask`). So a yes_no/definition/deadline
question that merely NAMES SDL/NSSF/PAYE/WCF and carries an **incidental** number (a rate
'asilimia 3.5', a day 'siku 30'/'tarehe 20', a threshold headcount 'wafanyakazi 4, sivyo?') was
routed to compute and then emitted a needless "give me the salary" clarification instead of just
answering from fact/RAG.

### Fix mechanism (routing-layer only; no model/network/GPU)
Guard Path 1 so it commits to compute only when a computation is actually needed —
`_has_money_ask OR is_applicability_question OR _has_money_magnitude OR _COUNT_TRANSITION OR
_DERIVE_CUE`. The discriminator is a **payroll money magnitude**: `_has_money_magnitude` returns
True for a currency/magnitude token (TZS/shilingi/milioni/elfu/laki/dola/euro/kes) **or** a
parsed amount ≥ `swahili_numbers.MIN_PLAUSIBLE_AMOUNT` (the extraction layer's own payroll-
plausibility floor, so a bare large number like `6,750,000` counts while a rate/day/small-count
does not — keeping routing consistent with how extraction itself decides a figure is real
payroll). A rate/deadline/confirmation whose only number is incidental now falls through to
fact/RAG.

**Empirical necessity of the money-magnitude refinement:** the naive "money-ask OR
applicability" guard was measured **unsafe** — it flips 51 questions and hijacks **6
currently-passing** ones (incl. `eval_318`, an unambiguous genuine compute question). Adding the
money-magnitude keep-condition narrows the blast radius to the intended class only.

### The 12-question flip set (all → fact/RAG; all `pass=False` today, so no reliable-subset loss)
`eval_099, eval_102, eval_127, eval_335, eval_342, eval_343, eval_344, eval_345` (the eight
originally-named) **plus** `eval_095, eval_337, eval_341, eval_348` (four same-class rate/
threshold confirmations surfaced by the 400 sweep). Exactly these 12 flip; every flip goes to
`none`; **0 currently-passing questions affected**; the 35 genuine compute questions the naive
guard would have wrongly hijacked (elliptical asks like `eval_372` "mishahara TZS 1,500,000 →
SDL yake?") are preserved.

### Carve-outs — deliberately NOT flipped (belong to other, already-built mechanisms)
- **`eval_124`** — the count-transition never-guess case (`_COUNT_TRANSITION`, from the
  applicability fix `f200a4e`). Kept on the compute path so its own never-guess clarification
  (not a fact answer) still fires when the headcount is crossing the SDL threshold. Flipping it
  would undo that just-built fix.
- **`eval_263 / eval_265 / eval_266`** — wrong-base traps (`extraction:small_int_as_money`;
  invoice/branch/vehicle counts offered as a payroll base). Their **gold answers themselves ask
  for the payroll figure** ("Nipe mshahara wa mwezi, siyo idadi ya invoice"), so the current
  salary-clarification is already aligned with intent; flipping them to fact/RAG would reintroduce
  exactly the fabricate-on-wrong-base failure the `rc_22`/`eval_380`-class guards exist to prevent.
  A compute-derivation cue (`_DERIVE_CUE`: itakuwaje/naipataje/inahesabiwa…) keeps them on the
  compute path, where extraction clarifies safely (never-guess, R8). These stay on the separately-
  tracked wrong-base track, not blurred into this guard.

### Validation
- New unit tests A1–A5 in `tests/test_routing.py` (named-8 → fact; the four additional → fact;
  genuine-compute regression locks stay on levy; `_has_money_magnitude` truth table; carve-out
  assertions). Routing tests 18 → 23.
- Full 400 routing sweep (offline, `scratch/explicit_guard_final_sweep.py`): exactly the 12-flip
  set, all → `none`, 0 currently-passing hijacked, 4 carve-outs stay compute.
- **Full offline suite: 204 passed, 0 failed.**

### Gate-number caveat (understood and correct)
This is a **routing-quality** fix, not something that moves the reliable-subset number on its own:
all 12 flipped questions are `pass=False` today, and production `run()` has no compute path.
Confirmation that the 12 now answer correctly via fact/RAG (rather than clarifying) is **folded
into the next scheduled 400-run** — no separate GPU cycle spent on it.

**Follow-up #2 of 3 — the `decompose_query` extension (enumerated/period-joined clauses, the
eval_322 / "Pia," gap above) — is next, and is HIGHER RISK: it touches shared infrastructure
affecting all 400 questions, so it needs its own careful, isolated investigation before any fix
is proposed (same discipline the applicability fix and this guard both received).**

## MEASUREMENT GAP — a THIRD of the gate is scored by an admittedly-arbitrary mechanism (2026-07-24) — ELEVATED

**This is a first-order measurement finding, not a caveat.** On the 5239190 combined run
(the current v16 baseline), **133 of 400 results (33.25%) are `reliable=False`** — the harness
itself declares them **unverifiable in either direction**. The weight is not "63 unverifiable
failures": it is that **70 of those 133 are marked PASS and 63 are marked FAIL, and the pass/fail
split across that entire third is arbitrary from the scorer's own standpoint.** A "pass" inside
that third is exactly as unadjudicated as a "fail." Every one of the eight exclusion reasons is a
scorer / ground-truth-structure limitation; **none** is a generation-quality reason (0 truncated /
loop / empty):

| reason | n | meaning |
|---|---|---|
| compute_derived_number | 48 | number-overlap cannot verify a *computed* figure |
| yes_no_polarity_unverifiable | 28 | cannot parse the Swahili yes/no lead |
| qualitative_number_no_numeric_key | 27 | answer is qualitative; no numeric key to match |
| yes_no_ground_truth_ambiguous | 9 | gold polarity itself ambiguous |
| morphological_overlap_gap | 7 | correct answer, tokenizer missed the overlap |
| year_only_numeric_key | 6 | scoring on a stray year token |
| zero_or_not_applicable_answer | 6 | "TZS 0 / not applicable" unverifiable by overlap |
| year_collision_match | 2 | spurious year-token match |

The reliable-subset gates (`fact_path_190_reliable`, etc.) exist *only* to route around this, and
they shrink the measurable base substantially (fact_path drops from n=180 to n=127). **This is
direct evidence that the frontier-judge scoring item is the binding constraint on trusting any
compute/adversarial number — and a third of the fact numbers too — and is NOT deferrable.**
(Supersedes the earlier "130/400" figure from the e9cc68a run; current is 133/400.)

### Copy-quality note (low priority, NOT a defect) — eval_275 / 291 / 292 (2026-07-24)
These three clarify **safely** (no fabricated number) but name a **generic** count/per-person need
instead of the *actual* blocker — foreign currency (eval_275, USD 300) or an irregular pay period
(eval_291 bi-weekly, eval_292 per-shift). `chike/clarification.py` already has `foreign_currency`
and `period` reason-mappers; the miss is that extraction did not surface those blockers into
`clarification_reasons` for these phrasings. Future copy-quality polish only — no code this session.

## v16-READINESS BASELINE — first real-weights, natural-phrasing A/B vs v15 (2026-07-20) — BLOCKING

**The single most methodologically important test of this session.** 20 questions written in
natural Swahili that deliberately name NO law/agency/tax type (compute, prohibition, boundary,
ambiguous, and evasion framings), run end-to-end against the **live production weights** twice:
v15 via the real `web_endpoint` (full pipeline as users receive it) and v16 via
`Orchestrator(LocalAdapter → generate_endpoint)` — same weights, same RAG index, real Modal
inference, **0 errors / 0 timeouts** across all 40 calls. Harness: `scratch/v16_ab_test.py`;
raw data `scratch/v16_ab_test_result.json` (gitignored scratch).

### Verdict: v16 is a REGRESSION against v15, NOT an upgrade — do not wire into production
- **v15 ≥ v16 on 18/20** (both correct 9; both wrong 2; v15 strictly better 7; v16 strictly better 2).
- **v16 wins 0 of the 4 compute questions** (Q2, Q5, Q8, Q15). It did not produce a single
  correct authoritative arithmetic answer; on Q5/Q15 its model-generated math was
  self-contradictory (Q5 "14% × 7,200,000 = 1,440,000" — false; Q15 a nonsensical
  "11 × 400,000 + 10 × 600,000 = 8,900,000" that doesn't even self-consist).
- **3 v16-UNIQUE regressions** absent from v15: (1) Q1 **empty answer** (`"\n\n"`);
  (2) Q12 **hallucinated two extra Q&A turns** the user never asked; (3) self-contradictory
  arithmetic justifications (Q5/Q15) surfaced by the raw endpoint's ungoverned generation.
- Both systems correctly refused **every** evasion attempt (Q6/14/17/18/19/20 — no
  evasion-acceptance in either) — but that comes from the SHARED model+RAG, not from anything
  v16 adds.

### ROOT CAUSE — the router never inferred subdomain; compute path fired 0/20
v16's `route()` (`chike/orchestrator.py:174`) routes to the deterministic rules engine only on
a **literal** tax-name keyword (`sdl`/`nssf`/`paye`/`wcf`) + a digit. Because the 20 questions
name no tax, **all 20 routed to `fact`** — the deterministic engine (v16's entire reason to
exist) was UNREACHABLE, the never-guess clarification guard never triggered
(`has_clarification_sentinel` false 20/20, even on Q2/Q5/Q15 where salaries were missing/
ambiguous), and v16's "authoritative arithmetic" was in fact model arithmetic
(`computation: null` on all 20). v16's router adds **no** subdomain-inference over the shared
RAG+model layer, which is identical to v15.

### The route() gap is BIDIRECTIONAL — and this exposes a gap in THIS SESSION's own methodology
This connects directly to the earlier-session route() keyword-gap findings (the "ROUTING
FINDING", ~line 885, and the RC-5 tracked follow-up + `ct=None` wrong-base guard work, ~lines
848/784/833). Those documented the router pulling fact/BRELA/VAT questions that merely CONTAIN
a payroll figure INTO the compute path incorrectly (the "wrong-base" misroutes — extract_078
"laki nne … BRELA?", extract_205 "payroll milioni tano … nisajili VAT?", ~21 flagged, patched
via the wrong-base guard). **This test proves the gap runs the OTHER way too:** the router also
fails to send genuine, naturally-phrased compute questions INTO the compute path. The failure
is bidirectional — misrouting fact→compute AND failing to route compute→compute.

Consequence for our own numbers: **every prior gate score claiming v16 "fact-path parity" or
"compute-path validated" was measured on a question set that structurally avoided ever
stress-testing the router on natural phrasing.** The fact-path-parity runs held `route()` fixed
and compared the 190 fact-bucket questions (all still routed to fact); the compute-path
validation called `SlotExtractor` DIRECTLY, bypassing `route()` entirely (see ~line 887). So no
prior test ever exercised the router on questions that (a) are compute in intent but (b) don't
name the tax — i.e. exactly how real users ask. This is a real gap in the session's testing
methodology, not merely a v16 defect, and must be stated as such: our headline v16 numbers were
measured around the router, never through it.

### SEPARATE, ADDITIONAL BLOCKER — the raw-endpoint governance gap
Independent of routing: v16's Orchestrator calls `generate_endpoint` (raw tokenize→generate→
decode) directly via `LocalAdapter`, and `_validate_and_clean` is currently stop/clean only.
The raw endpoint's ungoverned output is what produced the Q1 empty answer, the Q12 hallucinated
extra turns, and the self-contradictory math — failure modes v15's integrated pipeline
suppresses. **Even after the router is fixed, whatever calls the raw endpoint directly needs at
least v15's level of output cleaning/validation, or these same failure modes will surface on
legitimate compute-routed answers once the router actually starts sending traffic there.** This
is a distinct problem from the router and must be fixed on its own track.

### BLOCKING path to production-readiness (dependency-ordered — v16 must NOT be wired into Modal until 1–2 land and 4 passes)
1. **Replace the router stub with real subdomain/intent inference** (classifier or LLM router)
   so naturally-phrased compute questions reach the rules engine. Nothing else matters until
   this lands. Gate: these 20 (and the broader set) route compute questions to `compute`.
2. **Make the slot extractor resolve real-world phrasing** — per-person × count
   ("wengine kumi … laki sita kila mmoja"), currency conversion (Q8 KES→TZS), and FIRE the
   never-guess clarification when salaries are missing (Q2/Q5). Gate: deterministic trace on
   Q5/Q15 matches the correct figures (Q15 payroll 6,400,000 / SDL 224,000, etc.).
3. **Fix decompose→generate→clean** to eliminate empty output (Q1) and hallucinated extra
   turns (Q12): `_validate_and_clean` must reach at least v15's robustness + a non-empty guard.
   (This is the governance-gap track above.)
4. **Re-run THIS EXACT A/B plus the full 400-gate THROUGH the real router**, and require
   **v16 ≥ v15 on both raw correctness and the reliable subset** before any production wiring.
   The bar is not "v16 works" — it is "v16 beats the system already serving users."

Until at least steps 1–2 land and step 4 passes, wiring v16 into Modal would degrade the live
product. Keep v15 in production; treat this entry as the concrete spec for what the
orchestrator's stub stages (`route`/`classify`/`validate`) must become.

## EOS/generation 'root cause' — CORRECTED with direct evidence (2026-07-18)

Direct A/B test (kaggle/eos_production_probe.py, commit 6d21253, 20 questions
across 20 subdomains, skip_special_tokens=False, no substring stopping criteria
so only real EOS emission could stop generation):

- PRODUCTION format (modal_app.py's apply_chat_template, matches training):
  20/20 stopped early, 20/20 emitted <|end_of_text|> (128001), mean 68 tokens.
- EVAL/ORCHESTRATOR format (chike/prompting.build_chat_prompt, hardcoded
  Llama-3 headers never used in training): 0/20 stopped early, 0/20 emitted
  EOS, 20/20 ran to the full 350-token cap.

CONFIRMED: the earlier '79% of all generations never stop, project-wide'
framing was WRONG. Production has never had this defect — it uses a prompt
format matching training, and the model reliably emits its stop token.
This was entirely a testing-harness artifact: chike/prompting.build_chat_prompt
uses a Llama-3 chat-header format the model was never trained on, so at
eval/gate time only, the model doesn't recognize where to stop.

REAL IMPACT: every eval/gate score computed via the orchestrator path this
session (the 190/250/400-question combined regressions, Bucket A/B/C/D,
the retrieval-fix validation, the prohibition-inversion investigation, the
cleanup-layer gap-closure) was measured against a prompt format that does
NOT match production. This is a genuine R12 (dual-file-sync) violation in
the eval harness itself, not a defect in the deployed system.

FIX (no retraining needed): chike/prompting.build_chat_prompt and
kaggle/eval.py need to use apply_chat_template (matching modal_app.py
and training), not the hardcoded Llama-3 header format. Once fixed, the
existing cleanup-layer gap-closure fixes are likely to matter far less
(since correctly-stopped generations rarely need aggressive tail-trimming)
but should remain as defense-in-depth.

NEXT STEP: fix chike/prompting.build_chat_prompt to use apply_chat_template,
re-run the full 400-question combined regression on the corrected format,
and treat that as the new, trustworthy baseline — every prior gate score
this session should be considered measured on a flawed harness and superseded
once this is fixed and re-run.

### FIX IMPLEMENTED (2026-07-18) — awaiting Kaggle 400-run re-baseline

- `chike/prompting.build_chat_prompt(question, facts, system_prompt, tokenizer=None)`
  now routes through `tokenizer.apply_chat_template(..., add_generation_prompt=True)`
  over the SAME `[system, user]` messages modal_app.py builds (byte-identical to
  production and training). No-tokenizer callers (unit tests) get a naive-concat
  fallback — system + blank line + question — deliberately NOT the untrained header
  tokens.
- `kaggle/eval.py` (`generate_answer`) now passes its loaded `tokenizer` to
  build_chat_prompt → the standalone gate now tokenizes the exact production prompt.
- `chike/orchestrator.py` passes `getattr(self.backend, 'tokenizer', None)` through
  `_build_fact_prompt` / `_build_compute_prompt`; `KaggleDirectBackend` exposes
  `.tokenizer`, so the combined-orchestrator gate uses apply_chat_template too.
- Tests updated to the corrected behavior (test_prompting.py, test_orchestrator.py);
  full local suite **140 passed**. Offline verification: fallback emits no header
  tokens; tokenizer path delegates to apply_chat_template with modal_app-identical
  messages.
- **PENDING (founder, Kaggle GPU): re-run the full 400-question combined regression on
  the corrected format. That will be the FIRST trustworthy full-scale gate score this
  project has had** — every prior score was measured on the mismatched format and is
  superseded once this lands. → **DONE 2026-07-19 (see FINAL summary below).**

## ✅ FAITHFULNESS + FACT-INDEX CYCLE — FINAL VERDICT (2026-07-20, gate-measured)

**Status: net-positive cycle, closed on full 400-gate data — NOT a clean single-shot win.**
The eval_213 faithfulness fix required three fact-index rounds and surfaced a real regression
along the way; the final measured result is a net improvement, with two documented scorer
artifacts and one latent (not-yet-costly) fragility carried on a watchlist. Honest full arc:

### 1. The eval_213 discovery + fix (2×2 collocation isolation)
The facilitator-penalty fact was retrieved at **rank 0** yet the model answered wrong ("only
non-citizens are punished") — a **faithfulness/grounding defect, not a retrieval gap** (the
initial retrieval-gap hypothesis was REFUTED by pulling the actual retrieved context — the
discipline that prevented shipping a wrong "fixed" status). A systematic **2×2 (verb × object)
factorial** (`faithfulness_leseni_probes.jsonl`) isolated it to the single `kukopesha + leseni`
collocation — swapping either the verb or the object alone eliminates it. A phrase-level
parametric-prior override, not a general defect.

### 2. The two-round (actually three-round) fact-index iteration this fix required
- **v1** `gn487a_license_lending_is_facilitation`: over-matched — displaced
  `gn487a_prohibited_activity_3` from the phone-repair query (**caught by the regen gate**).
  Root cause of THAT was activity_3 being English-only/weakly-grounded; fixed by
  Swahili-strengthening activity_3 rather than shrinking the new fact further.
- **v2** (narrowed) + adding `gn487a_marriage_no_exemption` (Swahili) to fix eval_175: the
  **marriage addition then caused two regressions**, found only on the full 400-gate at 19fce68 —
  **eval_380** (non-citizen minimum penalty answered **TZS 5M instead of 10M** — a wrong number)
  and **eval_175** (marriage answer degraded to a vague deflection). Retrieval-rank evidence
  showed the 10M fact was never outranked (rank 0); the v2 license fact's residual `5,000,000`
  tail put a **second 5M figure** into eval_380's top-3 — a **context-composition** failure.
- **v3** (commit 2448c14 → index 0939eef): dropped the penalty-amount tail from the license
  fact (kept the `kukopesha+leseni` collocation so eval_213 stays fixed) and Swahili-grounded
  the marriage fact so it wins its own query. Added two regen guards (marriage positive;
  eval_380 disambiguation: 10M present AND license fact absent from top-3).

### 3. Probe-vs-gate discipline caught and correctly triaged every issue
- **Stale "Linux-environment / os.path.join" Modal theory** — diagnosed as wrong and RETRACTED;
  real cause was a Windows console-encoding crash on Modal CLI output (`PYTHONUTF8=1`).
- **Unpushed-commit stale fetch** — the fetched-HEAD tripwire caught it; it was NOT a CDN delay
  (origin genuinely was two commits behind because the commits were never pushed).
- **Two probe-harness bugs** (stale target strings): fp_04 searched English `"marriage no
  exemption"` against a now-Swahili fact; fp_02 was tied to one exact phrase the marriage fact
  crowded out — both were false `retrieval_gap`s while the model answered correctly. Fixed the
  matcher (string-or-list) + verified offline against real `facts_seen`.
- **fp_05 fragility** — a genuine confident-wrong flip at probe level (passive-shareholding
  "yes" flipped to "no" by prohibition-heavy context), attributed deterministically
  (`do_sample=False`) to the marriage fact entering its top-3. Carried to the watchlist.

### 4. Final measured result — full 400-gate, v3 (7eb9226) vs 19fce68
- **Net +2 raw pass; +4 reliable-subset with ZERO reliable losses.** All 4 gains
  (`eval_380`, `eval_175`, `eval_069`, `eval_163`) are `reliable=True`; eval_069/eval_163 were
  19fce68 regressions now **recovered**. `eval_144` upgraded rambling→clean **reliable** pass.
- **eval_213 / eval_380 / eval_175 all confirmed fixed** on real generated text (eval_380 now
  "TZS 10,000,000"; eval_175 nails marriage≠citizenship/exemption).
- **fact_path reliable-subset 108→111/130 = 85.4%** — above the 85% threshold AND slightly
  above the pre-cycle baseline (e9cc68a 110/129 = 85.3%), with the faithfulness fix baked in.
  Buckets: A ▲ (raw 85.1→86.2%, reliable ▲), D reliable ▲ (53.7→54.9%), B/C flat.
- **The two losses are unreliable-subset scorer artifacts, not defects** — see (a) below.
- **The predicted fp_05 crowding cost did NOT materialize on the gate:** shareholder-carveout
  gate Qs (eval_173/eval_204) and all 6 facilitator-displaced Qs held pass.
- Archived: `eval/results/gate_orchestrator_combined_7eb9226.json` (predecessor `_19fce68.json`).

### (a) Logged as scorer-artifact / temporal items — NOT defects requiring a fix
- **eval_157** (gn487a definition): both runs enumerate the 15 activities; v3 reformatted to a
  numbered list and the overlap scorer scored it lower → `morphological_overlap_gap`, dropped to
  `reliable=False`. Formatting + scorer-lexical artifact.
- **eval_369** (gn487a yes_no, temporal retroactivity): `reliable=False` in BOTH runs
  (`yes_no_polarity_unverifiable`). Not the fp_05 class (opposite direction — a yes-applies case
  where the model over-hedged toward a spurious grandfathering carve-out). Pass→fail is a
  scorer-boundary flip between two flawed answers on an already-unreliable case. Candidate future
  locked-fact ("GN487A applies from 28 Jul 2025 regardless of business start date; no
  grandfathering") but does not touch the trustworthy gate.

### (b) STANDING WATCHLIST — check on any future gate run or fact-index change (not urgent)
1. **fp_05-class carve-out fragility.** GN487A "permitted/yes" carve-out questions (passive
   shareholding, etc.) sitting on English-only facts can be flipped negative by prohibition-heavy
   Swahili context. Real at probe level; NOT yet costing reliable-gate accuracy. If a future gate
   shows eval_173/eval_204 or similar carve-out Qs regressing, escalate.
2. **English-only GN487A fact batch** (the ~15 `gn487a_prohibited_activity_*` + remaining
   carve-outs) — still weakly grounded for Swahili queries; queued from earlier this session (see
   TRACKED SYSTEMIC GAP below). The 26-question gn487a top-3 crowding is real in retrieval space
   but not currently costing accuracy at the present top-k.

### (c) STRUCTURAL GN487A decision — deliberate future work, NOT reactive
Raise injected top-k for GN487A vs. a single consolidated GN487A rewrite (fewer, well-scoped,
all-Swahili facts with a designed layout + a standing carve-out guard set). The measured gate
says this is **not urgent** — decide deliberately with the watchlist data, not reactively.

---



> This section declared closure on 2026-07-19 based on a 14-case probe regression, BEFORE
> the full 400-gate revealed the marriage-fact addition had caused eval_380/eval_175
> regressions. It is retained for the audit trail but is SUPERSEDED by the FINAL VERDICT
> section above (v3 fix + measured gate result). In particular, the "ACCEPTED low-severity
> fp_04 trade-off" below was later CORRECTED: eval_175 did carry a real, measured gate cost.

The eval_213 faithfulness cycle (interim summary for the record):

- **eval_213 discovered:** the facilitator-penalty fact was retrieved correctly (rank 0) yet
  the model still answered wrong ("only non-citizens are punished") — a faithfulness/grounding
  defect, NOT a retrieval gap (refuted the initial retrieval-gap hypothesis by pulling the
  actual retrieved context).
- **Root-caused as NARROW** via a systematic 2×2 (verb × object) isolation probe
  (`faithfulness_leseni_probes.jsonl`): only the specific `kukopesha + leseni` collocation
  triggers it; swapping either the verb or the object alone eliminates it. Not a general
  faithfulness defect — a phrase-level parametric-prior override.
- **Fix:** targeted `gn487a_license_lending_is_facilitation` locked fact, iterated twice —
  v1 over-matched and displaced `gn487a_prohibited_activity_3` (caught by the regen gate);
  root cause of THAT was the activity fact being English-only/weakly-grounded, fixed by
  Swahili-strengthening the activity fact rather than further shrinking the new fact.
- **Regen verified clean** on all 15 critical queries + 2 new guards (License lending,
  Phone repair); committed to `chike-inference/` + `kaggle/` with byte-identical sha256.
- **Modal redeployed** successfully from Windows — after an INCORRECT "Linux environment /
  os.path.join breaks container paths" theory was diagnosed and RETRACTED; the real cause was
  a Windows console-encoding crash on Modal CLI's `✓` output, fixed with `PYTHONUTF8=1`
  (container recomputes paths on Linux, so host OS is irrelevant to runtime paths).
- **Full 14-case regression (commit 403da7a):** fp_01/lv_01 both flipped
  `faithfulness_failure → faithful`; all other 12 hold `faithful`; both control pairs pass;
  ZERO new faithfulness_failure; ZERO wrong answers introduced.

### Accepted low-severity side effect — fp_04 marriage-fact displacement

fp_04 (`Nimeoa mwanamke Mtanzania, je nasamehewa katazo la GN487A?`) moved
`faithful → retrieval_gap`: `gn487a_marriage_no_exemption` was pushed from rank 2 to **rank 3**
(one slot outside top-3) by the license-lending fact at rank 1. Reproducible (retrieval is
deterministic), borderline (single-position slip). The model still answered **correctly and
confidently** from a strong, correct parametric prior ("Hapana — ndoa haikupi msamaha...").
Blast-radius check (marriage-exemption gate questions): **eval_204 unaffected** (marriage fact
still rank 0); **eval_175** marginally displaced by this fix (rank 5, both new facts in top-3);
**eval_144** rank 5 but its top-3 contains NO new facts → **pre-existing** English-only weakness,
NOT caused by this fix. All 4 gate questions passed pre-fix (reliable) and answer correctly.
**Decision: ACCEPTED as a low-severity retrieval-hygiene trade-off** (zero answer-quality
impact; the net win of resolving the dangerous eval_213-class defect dominates; a one-off regen
now to move a rank-3 fact would risk repeating the exact displacement just resolved).
`gn487a_marriage_no_exemption` is QUEUED by name in the systemic English-only batch below.

## TRACKED SYSTEMIC GAP — English-only GN487A facts are weakly grounded for Swahili queries (2026-07-19)

Surfaced while fixing the lv_01 license-lending fact's regen over-match. The 15 prohibited-
activity facts `gn487a_prohibited_activity_1..15` — AND `gn487a_marriage_no_exemption` —
have NO `CONCISE_BILINGUAL_FACTS` entry; they fall back to the English `key: value` form
(e.g. "gn487a prohibited activity 3: Prohibited activity 3: Repair of mobile phones and
electronic devices"). A Swahili query like `Mgeni anaweza kutengeneza simu?` or `Nimeoa
mwanamke Mtanzania, je nasamehewa...?` shares ZERO distinctive surface tokens with the
English text (only `gn487a`) and matches only cross-lingually — a weak, ERRATIC e5 signal
(the marriage fact ranks 0 for one phrasing, 5 for another). These facts were only *luckily*
top-ranked before, absent a strong Swahili GN487A-domain competitor in the index.

**Structural risk:** ANY future Swahili-dense GN487A fact added to the index can displace a
weakly-grounded English-only fact from top-3 for its own query — not a one-off caused by the
license-lending fact specifically. Confirmed twice: the license-lending fact displaced
activity 3 from the phone-repair query (fixed by Swahili-grounding activity 3), and displaced
`gn487a_marriage_no_exemption` from fp_04's top-3 (accepted low-severity — see below).

**Fixed so far:** only `gn487a_prohibited_activity_3` (Swahili CONCISE added — it has the
'Phone repair activity' regen guard, so the fix is verifiable).

**QUEUED for the guarded batch (English-only, still weakly grounded):**
`gn487a_prohibited_activity_1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15` (14 activities)
+ `gn487a_marriage_no_exemption`.

**Recommended follow-up (dedicated, guarded batch — do NOT bulk-edit unverified):** for each
queued fact, add a Swahili-first CONCISE entry AND a matching `critical_queries` regen-guard
query, following the exact verify-before-commit discipline used for activity 3 — one fact (or
a small guarded group) at a time, each confirmed by the regen gate before the next. A bulk
unguarded Swahili rewrite is explicitly rejected: only activity 3 currently has a guard, so
the rest would ship less-verified.

## eval_183 RECLASSIFIED — locked_facts coverage gap, NOT a faithfulness defect (2026-07-19)

While designing the eval_213 faithfulness probe, local retrieval on eval_183's phrasing
("Mwajiri asiyesajili OSHA anaweza kufungiwa biashara yake?") showed **no fact stating OSHA
lacks direct business-closure authority exists in the 210-fact index** — the closest facts
are the OSHA penalty list (fine TZS 1–5M / imprisonment) and the GN487A closure distinction.
So the model was NOT overriding a retrieved fact; it filled a genuine coverage gap with a
wrong assumption (asserting a stop-work power). This is the **same class as eval_155** (a
locked_facts clarity/coverage issue), NOT a model faithfulness defect. **Fix target: add an
'OSHA has no direct business-closure authority; enforcement is fine/imprisonment' fact to
locked_facts.json** (then the R15 RAG-regen cycle) — a fact-base addition, not a prompt or
generation change. Batched with eval_155 for a dedicated locked_facts pass (deferred, per
prioritization). This moves eval_183 OFF the faithfulness track it was tentatively on.

## ✅ EOS CYCLE CLOSED — corrected 400-run re-baseline is IN (2026-07-19)

The founder ran the full 400-question combined regression on the corrected format (commit
**e9cc68a**, timestamp 2026-07-18T20:34Z). Persisted data:
`eval/results/gate_orchestrator_combined_e9cc68a.json` (fetched from HF and committed — see
standing convention below). This is the FIRST fully clean, trustworthy full-scale gate run
this project has had; every prior score was on the mismatched harness and is superseded.

**EOS fix confirmed broad-based (not concentrated in a few questions).** Across all 400
generations: **0** with a repetition-loop tail, **0** with `<|start_header_id|>`/
`<|begin_of_text|>` header-token leakage, **0** empty generations. Mean 229.8 chars, median
187, p90 469 (char proxy — no token-count field was persisted, but the loop/header/empty
counts are exact). Runtime dropped ~3× (13,300s → 4,861s), fully explained by clean early-
stop instead of runs hitting the 350-token cap. The probe's 20/20 finding holds at scale.

**Bucket results (raw / reliable subset):**
- fact_path_190: 156/181 = 86.2% / 110/129 = 85.3%
- staged_50: 35/50 = 70.0% / 28/40 = 70.0%
- compute_type: 36/112 = 32.1% / 20/50 = 40.0% (genuine 35/108 = 32.4% / 19/49 = 38.8%)
- adversarial_150: 60/144 = 41.7% / 45/82 = 54.9%
- Weakest subdomains (all compute-heavy): wcf 1/10, sdl 29/67, paye 14/31, nssf 37/64.
  Strong: gn487a 48/54, efd 23/25, gn605a 5/5, vat_registration 40/54.

**Per-question findings vs. this session's claims:**
- **eval_317 & eval_146 — RESOLVED.** Both pass=True, reliable=True, clean single-shot
  generation, correct polarity, no repetition tail. The d92e63f retrieval fix (eval_317
  salon capital-distractor) held up under the corrected harness.
- **eval_213 — GENUINE NEW DEFECT** (gold=yes/model=no; opposite direction from every
  prior inversion). Clean generation, reliable=True. Model confidently claims only
  non-citizens are punished under GN 487A, contradicting the locked facilitator-penalty
  fact (Tanzanian facilitator: TZS 5M / 3 months). See dedicated section below — the
  RAG-gap hypothesis was **REFUTED**; it is a faithfulness defect.
- **eval_355 — GENUINE DEFECT.** Sales TZS 10,999,000 vs 11M EFD threshold; model says
  "Ndiyo, unazidi" (wrong — 10.999M < 11M). A boundary-comparison error.
- **eval_155 — GENUINE DEFECT.** Model says the GN 487A enforcement *exercise* is still
  ongoing; gold: the exercise ended 8 Oct 2025 though the law is permanent. Conflates the
  time-limited exercise with the standing law.
- **eval_332 — SCORER ARTIFACT.** Model actually correct (agrees wholesale prohibited,
  reproduces both penalties incl. the citizen-helper TZS 5M); "Ndiyo [prohibited]" vs gold
  "Hapana [you can't]" is a framing-polarity mismatch, not an error.
- **eval_365 — SCORER ARTIFACT.** pass=True, reliable=False; model correctly states NSSF
  has no employee threshold; surface "hakuna" flagged by the polarity classifier.
- eval_183 (OSHA stop-work-order vs. business-closure) is a genuine *semantic* nuance the
  polarity scorer can't separate — left with the deferred framing-aware polarity item.

**Compute buckets (32–40%) are SCORER-LIMITED, not a confirmed measure of true compute
accuracy.** 130/400 results are reliable=False (this is the e9cc68a figure; the current
5239190 baseline is **133/400 = 33.25%** — see the dated "MEASUREMENT GAP" section near the
top for the elevated restatement), and every exclusion reason is a
scorer/ground-truth limitation — NONE is a generation-quality reason (0 truncated/loop/
empty). Breakdown: compute_derived_number 48, qualitative_number_no_numeric_key 27,
yes_no_polarity_unverifiable 26, yes_no_ground_truth_ambiguous 9, year_only_numeric_key 6,
morphological_overlap_gap 6, zero_or_not_applicable_answer 6, year_collision_match 2. On the
compute path specifically, 62/113 are unreliable (mostly compute_derived_number — the
number-overlap scorer cannot verify a computed figure). This means the reliable-subset
denominators are governed by scorer structure, not generation cleanliness (the EOS fix could
not have moved them). **Closing this gap requires the frontier-judge scoring approach already
validated earlier this session — NOT further prompt or retrieval work.** Until then, treat
the compute numbers as a floor obscured by scorer leniency/blindness, not a true accuracy.

## eval_213 — RAG-gap hypothesis REFUTED; it is a FAITHFULNESS defect (2026-07-19)

Investigated with the same rigor as the salon-inversion case, and the mechanism is the
OPPOSITE of what I first hypothesized. Ran the real e5 retriever (chike.retrieval, using the
committed, git-clean `kaggle/rag_embeddings.npy` + `rag_facts_text.json` — the exact 210-fact
index the e9cc68a Kaggle run used) on eval_213's exact phrasing:

  Q: "raia wa Tanzania anayekopesha leseni yake kwa mgeni naye anaadhibiwa chini ya GN 487A?"
  top_3[0] = "Adhabu kwa raia wa Tanzania anayemsaidia mgeni kukiuka GN487A: faini si zaidi
             ya TZS 5,000,000 ... au kifungo si zaidi ya miezi 3."  ← the facilitator fact,
             retrieved at the VERY TOP of context.

The facilitator-penalty fact is **present in eval_213's retrieved context at position [0]**,
yet the model still answered "Hapana — adhabu zinawahusu tu wasio raia." So this is **NOT a
retrieval gap** — the model was handed the correct fact and contradicted it. The two-arm
hybrid retrieval fix (d92e63f) does **NOT transfer**; confirming the mechanism first (per
the founder's instruction) prevented applying the wrong fix. eval_213 is a
**faithfulness/grounding defect** (model overrides a retrieved fact with a confident prior
that "GN 487A is about non-citizens, therefore only non-citizens are punished"). eval_332
corroborates: with the same fact retrieved, the model gets the citizen-helper penalty RIGHT
inside the wholesale multipart — so the failure is phrasing/prompt-conditioned generation,
not index coverage. TRACKED as a new priority finding; candidate remedies are
faithfulness-side (e.g. prompt instruction to defer to retrieved penalties, or a
polarity/consistency check against retrieved facts), NOT retrieval-side.

## Standing convention (2026-07-19): commit every gate run to eval/results/

The immediate-predecessor combined-gate run could not be diffed against because its
`gate_orchestrator_combined.json` lived only on HF and was overwritten by the e9cc68a run
(never committed). To prevent this recurring: **every `gate_orchestrator_combined.json` (and
standalone gate) run is fetched from HF and committed into `eval/results/` with a
commit-tagged filename**, e.g. `gate_orchestrator_combined_<sha>.json`. This gives each
future re-baseline a real, byte-exact predecessor for per-ID before/after diffs. First entry:
`eval/results/gate_orchestrator_combined_e9cc68a.json`.

## ✅ CLOSED — cleanup-layer port to production (Modal + Kaggle) — premise was STALE (2026-07-18)

The earlier "port cleanup fixes to Modal + Kaggle" action item assumed
`chike-inference/modal_app.py` and `kaggle/eval.py` each carried their OWN OLD, unfixed
INLINE copy of `clean_reply`. **Direct inspection shows that is not (or no longer) the
case — both already import the shared module:**
- `chike-inference/modal_app.py:421` — `from chike.generation_cleanup import clean_reply`
  (called at :524); modal_app also already builds its prompt via `apply_chat_template`
  (:462), so production was **never** on the mismatched format.
- `kaggle/eval.py:88` — `clean_reply = _cleanup['clean_reply']` (shared module fetched
  from GitHub at runtime; called at :377).

So the three cleanup-layer fixes (`_truncate_repeated_sentences`, generalized
`_GLUED_TURN_RE`, `_cut_nonlatin_and_domain_loops` incl. the U+2212 allowance) already
reach both production and the standalone gate via the shared import — no inline port was
needed. The only genuine divergence was the prompt template (`build_chat_prompt`), fixed
above. Net: production was already correct on BOTH cleanup and chat-template; the fix this
session was scoped entirely to the eval/orchestrator harness. (Minor latent note: modal_app's
`except Exception` fallback at :467-475 still hardcodes the Llama-3 header format; it is dead
code unless apply_chat_template throws, but should be aligned to naive-concat in a future pass.)

Second follow-up (lower priority): framing-aware/semantic polarity for the 5 non-numeric
genuine model inversions (eval_059/062/183/332/391) + eval_317/146.

## Cleanup-layer gap-closure — three EOS-tail cuts (2026-07-18)

Closed the three enumerated `clean_reply` coverage gaps that left the degradation tail in
place after cleanup (chike/generation_cleanup.py; the mitigation layer for the EOS root
cause above). Regression-tested across all 400 raw generations with the module's zero-
content-loss discipline:
- **Intra-block repetition cut** (`_truncate_repeated_sentences`) — cuts at the first
  sentence (>=12 chars) that repeats an earlier one, keeping the first occurrence; re-joins
  via captured separators so a non-repeating reply is byte-identical. Fixes eval_317's
  "Thibitisha…" ×13 loop. A short repeated clause ('Ndiyo. Ndiyo.') is never truncated.
- **Generalized fabricated-turn detection** — `_GLUED_TURN_RE` now catches any short token
  glued directly to '?' with no space ('?nssm', '?about:blank', '?nssf.go.tz'), not just a
  hardcoded role-word whitelist. Fixes eval_183 (the 'nssm' leak) + the domain-token fake
  turns. Role-junk stripping now runs BEFORE the repetition cut so a duplicate closing line
  differing only by a leaked '.user' suffix still de-duplicates (eval_111).
- **Non-Latin-script + domain-loop cut** (`_cut_nonlatin_and_domain_loops`) — truncates at
  the first foreign-script char (Arabic/Cyrillic/CJK) and drops a glued/looped junk domain
  while KEEPING the first legitimate citation (`tra.go.tz` preserved, `.understandthis.com…`
  loop dropped). The allowed range deliberately includes Mathematical Operators (U+2200-22FF)
  so the arithmetic MINUS SIGN U+2212 in PAYE/SDL sums survives — an earlier draft cut there
  and truncated eval_191 mid-sum (caught by the score-regression guard; now a locked test).

Results across 400: eval_317/183 + all 80 detector-degraded cases now clean; 9 previously-
clean cases changed and ALL are prefix-only garbage removal (0 content loss, e.g. eval_090
1399→112, eval_218 1278→118 loop removals); **0 yes_no/number score regressions**, 0 new
candidate-inversion flips. Unit tests added (tests/test_generation_cleanup.py, incl. the
eval_191 minus-sign regression guard); full non-integration suite 138 passed. NOTE: this is
the MITIGATION layer — it does not reduce the 79% overrun (tokens are still generated then
trimmed); only the EOS root fix above does that.

## Post-retrieval-fix 400-run VALIDATION + polarity-parser lexicon fix (2026-07-18)

The founder re-ran the full combined 400 on Kaggle after the retrieval fix (d92e63f);
`gate_orchestrator_combined.json` on HF adapter-v15 (commit d92e63f) was diffed
independently, per-question, against the immediately prior run (HF commit 5817d9d,
internal code commit **c094636**, 400 q). Both files pulled locally; the local
`kaggle/rag_embeddings.npy` + `rag_facts_text.json` are MD5-identical to the HF index
the run used, so retrieval was reconstructed faithfully offline (e5 cached).

### Finding 1 — the retrieval fix is VALIDATED; "eval_317 still inverts" was a false alarm
The prior run had NO polarity review (that code, ca49520, did not exist yet), so the 9
candidate inversions were surfaced for the first time in the d92e63f run — comparison
required reconstructing polarity from the actual generated text in both runs, not the flag.

- **eval_317 (salon):** prior retrieval = `{fine-limit, trademark-fee, vat-deferment}`,
  ZERO GN487A facts → generated *"anaweza kuendesha saluni … chini ya milioni 100"* (the
  dangerous inversion). Post-fix the hybrid appended GN487A fact [21] → generated
  *"saluni **imepigwa marufuku** kwa wasio raia"* — **substantively CORRECT**. The
  retrieval fix reached generation and flipped the polarity wrong→right.
- **eval_355 (EFD 10,999,000):** prior hedge → post-fix *"chini ya 11,000,000 … EFD **si
  lazima**"* — correct (below threshold, not mandatory).
- It still showed as a candidate inversion + pass=False for **two reasons unrelated to
  "generation ignored the fact":** (a) the polarity parser's negation lexicon had no
  prohibition/negation verbs, so *"imepigwa marufuku"* fell through to the affirmative
  default `model=yes`; and (b) a generation-robustness repetition loop ("Thibitisha na
  Idara ya Uhamiaji" ×14) starved the overlap scorer.
- Of the 9: **5 are non-numeric** (eval_059/062/183/332/391) — byte-identical retrieval AND
  generation between runs (the fix's design guarantee held exactly), genuine pre-existing
  model errors OUT OF THIS FIX'S SCOPE; **1 numeric didn't fire** (eval_155, "487A" is not a
  strippable amount — correct); **3 fired and improved/held substance** (317 wrong→right,
  355 hedge→right, 146 right→right).

### Finding 2 — Bucket A 154→152 fully explained, non-regressive; design guarantee held
Exactly **2 flips across all 181 in-corpus Bucket-A questions, both numeric, ZERO
non-numeric flips** (byte-identical guarantee intact; also verified no Bucket-A question
newly refused/clarified, ruling out the interim OOC-classifier commit d767e71):
- **eval_146** — numeric, reliable=False. Substantively correct in BOTH runs ("no grace
  period"); the fix reworded it and the citation shifted Immigration→TanzLII, flipping the
  *unreliable* overlap scorer. Scorer noise, not a real regression.
- **eval_186** — numeric, reliable=True, the ONLY reliable flip. Mechanism confirmed as the
  fix (appended an extra fact → 4-bullet prompt → greedy decoding diverged), NOT GPU
  nondeterminism. But the lost "pass" was itself a **fabricated-number false-pass**: prior
  asserted a *"50 au zaidi"* safety-officer threshold the reference explicitly says is *not
  established*; post-fix dropped the fabrication for a vaguer answer that fails the overlap
  scorer. A lateral move (confident-wrong-that-passed → vague-incomplete-that-failed), not
  the loss of a genuinely-correct answer.

### The cross-cutting discovery — the polarity parser is the bottleneck, not retrieval
The reporting-only parser recognised `hakuna/haiwezi/…` but NOT the core Swahili
prohibition/negation forms these answers use — `marufuku`, `imezuiliwa`, `si lazima`,
`bila`. Proven on real data it BOTH missed the one real correction (eval_317, "marufuku"
read as yes) AND manufactured a spurious new inversion (eval_146, a benign rewording that
dropped the word "Hakuna").

### Reporting-layer fix IMPLEMENTED — negated-obligation lexicon (chike/scoring.py)
Separate from the retrieval-layer fix (d92e63f). Added to `_YN_NEG`: `si lazima` /
`sio lazima` / `siyo lazima` / `halazimiki` / `hailazimu` (an unambiguous NO regardless of
question framing), plus a negative-lookbehind on the positive-`lazima` marker in
`_polarity_conf` so a negated `lazima` reads as a clean 'no', not an ambiguous 'both'.

Full-400 regression (live patched module, re-derived over the stored generations):
- Candidate inversions **9 → 8**: exactly **eval_355 resolved**, ZERO new false positives.
- yes_no scorer: exactly **1 flip, eval_355 False→True** (a correct resolution; reliable=False
  and in Bucket D, so no reliable-subset headline moves). Nothing else in the 400 changed.
- Existing polarity test suite + full non-integration suite green (131 passed).

**DELIBERATELY NOT ADDED (contradicts the initial plan — evidence-driven):** the prohibition
verbs `marufuku` / `imezuiliwa` / `zuiliw` and the broad `bila`. Tested across all 400, a
flat mapping to NO **regressed FOUR genuinely-correct answers** (eval_149/152/153/389) —
because a Swahili prohibition verb carries prohibition CONTENT, not a fixed yes/no polarity:
for "can I do X?" it means NO, but for "is X prohibited / is he covered?" the correct answer
is YES ("Ndiyo, ni marufuku"). `bila` was worse (broke the reliable-scored eval_309). A
framing-aware variant was also tested and still broke eval_153 (a permission-framed question
whose correct answer is YES). So eval_317 and eval_146 CANNOT be resolved by any flat
lexicon; their SUBSTANCE is already correct post-retrieval-fix, and a regression guard test
(`test_prohibition_verbs_deliberately_not_flat_negation`) locks this decision in.

### Next tracked follow-ups (priority order, for future work)
0. **[ELEVATED 2026-07-24] Frontier-judge / semantic scoring — now the BINDING constraint.**
   The 5239190 investigation showed **133/400 (33.25%) are `reliable=False`** with an
   arbitrary pass/fail split (70 pass / 63 fail) across that third, every exclusion reason
   scorer-structural (see "MEASUREMENT GAP" section above). This is no longer a deferrable
   nicety: it caps the trustworthiness of every compute/adversarial number and a third of the
   fact numbers. Promoted above the two items below — they largely *fold into* this workstream.
1. **Generation-robustness repetition loop** — eval_317's "Thibitisha…" ×14 tail and
   eval_183's fabricated multi-turn Q&A. Likely a stop-string / `no_repeat_ngram` / decoding
   fix. This (not retrieval, not the parser) is what still fails eval_317's scorer.
2. **The 5 non-numeric genuine model errors** (eval_059/062/183/332/391) — real prohibition
   inversions the retrieval fix does not and was not meant to touch; need a generation/
   prompt-side intervention (leading-question handling, EFD-receipt absolutes) or the
   semantic judge. eval_317/146's remaining parser mis-reads also fold into the semantic-
   judge / framing-aware-polarity workstream.

---

## Prohibition-inversion investigation — ROOT CAUSE = numeric-query retrieval eviction (2026-07-18)

The 400-question run surfaced GN487A prohibition answers that flipped to "allowed"
(eval_317 salon, eval_332 wholesale), hidden from the reliable-subset headline
because scorer_reliability excluded them as yes_no_polarity_unverifiable. A
14-question probe set (gn487a_inversion_probes.jsonl, run on the real v15 model +
e5 RAG on Kaggle, results in gn487a_inversion_probe.json on HF adapter-v15) plus
an offline retrieval trace (e5-base is cached locally; retrieval is CPU-only cosine
over kaggle/rag_embeddings.npy, so the ACTUAL top-3 retrieved facts were reproduced
locally with no GPU) together identify a single, precise root cause.

### Root cause (corrected twice, now evidence-locked): the query's NUMBER hijacks e5 retrieval

The numeral in a question dominates the multilingual-e5-base query embedding and
evicts the topic fact from the top-3, replacing it with numerically-shaped but
semantically-wrong facts (trademark fees, VAT deferment thresholds, course fees —
all "X TZS" entries). With no relevant fact in context, the model falls back on
parametric memory. Confirmed directly by the retrieval trace:

- probe_01 salon + "TZS 100,000,000" -> retrieved {fine limit 100k TZS, trademark
  fee 10k, vat deferment 10M}. The correct salon facts (rag idx 172/176: "salon
  prohibited UNLESS hotel/tourism") were NOT retrieved. Model hallucinated a
  "<100M capital" exception = eval_317 reproduced. Strip the number -> GN487A-family
  facts return and the model answers correctly (probe_02).
- probe_12 EFD + "TZS 500" -> retrieved 3 trademark-fee facts (50k each). The
  correct EFD fact (idx 56: receipt threshold 11M turnover) was NOT retrieved.
  Model fabricated a "TZS 200,000 EFD floor". Strip the number -> the correct EFD
  11M fact returns to #1.
- probe_10 OSHA + "wafanyakazi 8" -> correct OSHA absolute (idx 51: "bila kikomo
  cha idadi ya wafanyakazi") buried at #3 behind {28-day processing, small-scale
  mining}; model hedged "under 10 employees you may not be required" — importing
  SDL's real 10-employee threshold. Strip the number -> the OSHA absolute returns
  to #1.

RETRIEVAL-vs-RECALL determination (the fork the fix hinges on): it is PRIMARILY
RETRIEVAL. The contaminating SDL-10 / VAT-200k facts were NOT themselves retrieved
in probe_10/probe_12 — so the wrong number is free parametric recall, but ONLY
because retrieval first evicted the correct topic fact. Every no-number control
retrieved the right fact and answered correctly. The fix therefore belongs in
RETRIEVAL (numeral downweighting/stripping in the query embedding, or a topic-term
retrieval pass), NOT in a prompt/generation clamp. Precedent already noted in
chike/retrieval.py:44-46 (a raw-dot-product SDL query once ranked GN487A penalties
top — same class of cross-topic embedding contamination).

### Why some numeric probes still answered correctly (H1/H2/H3 verdicts)

Given no fact in context, outcome depends purely on parametric-recall robustness:
- Unconditional absolutes recall correctly despite the retrieval whiff: mobile
  money, phone repair, tour guiding, real estate, wholesale prohibitions
  (probes 03/05/06/07/08); NSSF-from-first (14); min-wage ~175k floor (13).
- Conditional or threshold-adjacent facts fabricate a carve-out: salon (real
  hotel/tourism exception), OSHA (SDL-10 competitor), EFD (a plausible floor).

So: H1 (numeric-distractor binding) CONFIRMED but is a retrieval-eviction artifact,
not conditional-fact reasoning per se. H2 NARROW — only the conditional-exception
activity (salon) flips; 5 other GN487A activities with numbers stay correct;
NOT systemic across GN487A. H3 CONFIRMED-SELECTIVE — OSHA and EFD flip (competing
thresholds exist to recall), min-wage and NSSF hold. All three collapse into the
one retrieval-eviction mechanism above.

### Two SEPARATE, lower-severity findings (do not conflate with the safety issue)

FINDING B — polarity-parser over-surfacing (reporting-noise, NOT a safety defect):
probes 02/03/05/06/07/09 are substantively CORRECT ("...imepigwa marufuku kwa wasio
raia") yet flagged candidate_inversion=True. The "naweza X? ... [activity] marufuku"
construction parses as a low-confidence 'yes' in _polarity_conf (all confident=False).
Human review catches these, so it is review-time noise, not a hidden danger. Refine
by de-tiering a low-confidence 'yes' that contains a strong prohibition marker
(marufuku / imezuiliwa / hawawezi / inakataza) into a distinct "likely-correct,
confidence-parsing" bucket. Lower priority than the retrieval fix.

FINDING C — generation-robustness bleed-through (corroborated, its own defect):
probes 10/11/12 independently reproduced repetition loops, fabricated multi-turn
Q&A, and stray Arabic text surviving clean_reply — the same failure class seen in
eval_303/321/332 on the 400-run. Two independent datasets now show it; logged as a
standalone Priority-3 investigation for when capacity allows. No new action taken.

### Fix scoping (NOT yet implemented — reported for confirmation first)

Target ONLY the confirmed mechanism: numeral-driven retrieval eviction. Do NOT
build a blanket "suppress numeric prohibition answers" clamp — 6 of 8 numeric
GN487A probes answered CORRECTLY and a clamp would regress them. Candidate fix
locus is chike/retrieval.py query construction (numeral handling before embedding);
must be regression-tested against the full 400 for retrieval changes on non-numeric
questions before proposal. Awaiting go-ahead before writing fix code.

### Fix IMPLEMENTED — additive two-arm hybrid retrieval (chike/retrieval.py)

Approved and built. Retrieval-layer change only; the model-level confirmation
(does eval_317's answer actually flip to "prohibited"?) still requires a founder
Kaggle full-400 run (see below).

DESIGN — append-only union of two retrieval arms, at the single retriever boundary
(chike/retrieval.py Retriever.retrieve, used by the orchestrator via retriever.retrieve):
  1. Full-query arm — current production retrieval, top-3, KEPT VERBATIM.
  2. Number-stripped arm — re-embed with digit amounts removed (strip_numeric_amounts:
     'TZS 100,000,000' / bare '8' / '500' go; number-WORDS milioni/elfu/kumi stay,
     since they carry topic meaning without the hijacking magnitude), retrieve top-6.
  3. Merge = APPEND-ONLY: return baseline top-3 unchanged, then append the FIRST NEW
     fact the stripped arm surfaces (final size 4). Fires ONLY when the query contains
     a digit; non-numeric queries take a single-arm path that is byte-identical to
     production (one embed call, no merge) — locked by a unit test.

WHY APPEND-ONLY, NOT INTERLEAVE/RRF (this is the crux): interleave forces a stripped-
arm fact into slot 2, which EVICTED the correct EFD fact sitting at baseline rank 3 on
eval_331 and eval_355 — a real regression the 14-query guard set could NOT catch
because guard facts sit at rank 1. Append-only cannot drop a baseline fact by
construction (verified: 0 regressions across all 90 numeric test queries). It also
resolves the "incidental number vs subject number" problem WITHOUT a classifier: the
full arm keeps the numeric fact when the number is the subject (PAYE 800k, SDL/NSSF
12-employee calcs all still hit), the stripped arm recovers the topic fact when the
number is incidental, the union carries both. add=1 (size 4) chosen over add=2 (size 5)
because coverage was identical (85/90 either way) — take the smaller prompt.

RETRIEVAL-LAYER EVIDENCE (e5 cached locally; CPU cosine; model not run):
  - Topic coverage across 90 numeric GN487A/OSHA/EFD/NSSF questions in the 400:
    baseline 83/90 -> additive 85/90 -> interleave 83/90 (with 2 regressions).
  - additive REGRESSIONS: 0 (append-only, by construction and measured).
  - GAINS: eval_317 (salon — the headline inversion; baseline retrieved zero GN487A
    facts, additive appends a GN487A penalty fact) and eval_347 (EFD threshold false-
    premise question — additive appends the real EFD 11M fact).
  - 14 critical regression guards: 14/14 under additive (integration test asserts all
    14 hit AND eval_317 recovers a GN487A fact on the real 210-fact index).

OPEN FOLLOW-UP (not silently dropped): probe_12 / eval_056 remain unfixed. These use
the word 'Muamala wangu ni TZS 500 tu' — stripping the digit leaves 'Muamala ... tu',
which still mis-retrieves to transaction/fee facts. The real 400-set EFD questions that
use 'Mauzo' (turnover) — eval_354/355 — already retrieve the EFD fact fine. So this is a
narrow 'muamala' vs 'mauzo' wording artifact, NOT a systemic hole; tracked as a separate,
narrower follow-up (would need a topic-term retrieval arm) rather than over-engineered now.

WIRED FOR KAGGLE: no change to eval_orchestrator_combined.py is needed — it constructs
Retriever(...) and passes retriever.retrieve to the Orchestrator (lines 189-190), so the
hybrid is inherited automatically. The script clones main fresh and prints '[clone] chike
@ ... (HEAD <sha>)'; verify that SHA matches the fix commit before trusting the run. The
definitive test is whether the model's ANSWER flips on eval_317 and similar with the
recovered fact in context — founder runs the full 400 on Kaggle (Claude does not run GPU).

## Verification-entry recommendations — all three CLOSED

1. compute_type_reliable + compute_type_genuine_reliable headlines added to
   eval_orchestrator_combined.py (ec2909a) — reporting-only change, matches
   existing fact_path/staged reliable-subset pattern.

2. extract_numbers '000'-garbage-token bug fixed (60f140d) — comma-grouped
   numbers with a 1-2 digit leading group were fragmenting into a bare '000'
   token; fixed regex captures complete thousands-grouped numbers. 0 verdict
   flips across all 250 gate+additions questions (garbage token was present
   symmetrically in reference and generation, so removing it never changed
   a non-empty intersection on this specific dataset) — real fix, no visible
   impact on current results, removes a latent false-pass mechanism.

3. Zero/'does-not-apply' reference answers now flagged scorer_reliability=False
   (BUG 7, e6781fc) — a number/penalty question whose only extractable figure
   is 0 represents a below-threshold conclusion, not a computed amount that
   number-overlap scoring can verify. Exactly 1 reliability-flag change
   (eval_247), 0 verdict flips, scoped narrowly to the numeric-zero signal.

CAVEAT — stored data not yet updated: both scorer changes (#2, #3) were
regression-tested offline against the existing persisted generations in
gate_orchestrator_combined.json, which is valid since neither change alters
any pass/fail verdict. But the STORED JSON's scorer_reliability flags and
the compute_type_reliable/compute_type_genuine_reliable headline values
still reflect the OLD scorer (pre-e6781fc) until eval_orchestrator_combined.py
is re-run on Kaggle. Expected shift on next run: compute_type_reliable
5/7->5/6 (83.3%), compute_type_genuine_reliable 4/6->4/5 (80.0%) — eval_247
drops out of the reliable subset as intended. Do not read the current stored
file as already reflecting these fixes.

DEFERRED (documented, not silently dropped): eval_051's 'no minimum threshold /
illustrative-figures' leniency pattern is a distinct issue from the zero-
conclusion signal just fixed — noted for a future scoped pass if pursued.

All three fixes followed identical discipline: root-cause confirmation via
code inspection, full-scale regression across all 250 gate+additions
questions (not a small sample), verdict-preservation verification, the
114-test suite, and a reviewed report before each commit.

## v16 compute-path — first real end-to-end validation (corrected analysis)

Combined regression (commit 8bf3c85, real v15 model on Kaggle) — independently
re-verified against the actual persisted gate_orchestrator_combined.json,
gate_001_results.json, and gate_orchestrator_subset.json, not accepted from
a first-pass summary.

### Bucket composition (precisely defined)
- Bucket A (fact_path_190): raw bucket is 190 non-compute gate_001 questions;
  stored n=181 is the in-corpus scored subset after _score() drops 9
  out_of_corpus-subdomain rows (eval_192-eval_200) — both numbers are correct,
  they describe different things (raw bucket size vs. scored denominator).
- Bucket B (staged_50): all 50 staged additions, including the 10 compute-routed
  ones — there is no non-compute/compute split within B.
- Bucket C (compute_type): 20 compute-routed questions from either source
  (10 from the gate, 10 from the additions), n=19 after dropping 1 OOC-labeled
  row (eval_191 — the known PAYE-800K question mislabeled out_of_corpus in the
  gate data, documented separately in the v9 analysis).
- B and C overlap by exactly the 10 compute-routed additions (eval_241-250).
  A overlaps with neither.

### Fact-path (Bucket A) parity — CONFIRMED, genuinely strong
Compared against the prior orchestrator subset run on the same 190 IDs:
100% ID overlap, 0 differences in generated text, 0 differences in raw
generation — byte-identical. Only 2 pass-verdict flips (eval_010, eval_165),
both explained by an intentional scorer improvement (BUG-3 multiplier
composition fix) already in place before this run, not a behavior change.
The extraction/compute-path work genuinely did not touch the fact path.

### Scorer leniency for number-type questions — CONFIRMED, worse than first flagged
chike/scoring.py's number-type pass condition requires only ONE expected
figure to appear anywhere in the generated text; extra wrong figures never
cause a fail. Two compounding problems found on independent inspection:
1. Reference answers embed input figures (e.g. the salary used in the
   question) alongside the actual answer figure, so a model that only
   echoes the question's input numbers can pass without stating the
   correct output at all — demonstrated directly.
2. NEW FINDING: extract_numbers() on "TZS 40,000"-style text returns a
   garbage '000' token (the 3+-digit regex can't span the comma), and
   this '000' token is present in nearly every payroll-related correct
   answer AND generated answer, meaning a shared '000' alone can satisfy
   the pass condition regardless of the actual figures involved.

Concrete impact on this run: of 15 genuine-compute pass=True results in
Bucket C, 9 are already flagged scorer_reliability=False (the existing
reliability layer catches most leniency-driven false passes) — but the
combined regression script never computes or reports a reliable-subset
headline for Bucket C the way it does for A and B, so the published
compute numbers (raw 12/19=63.2%, genuine 11/15=73.3%) are the
leniency-inflated ones. The reliable-subset compute figure is only
4/6=66.7% — real, but on too small a denominator to be meaningful yet.

eval_247 specifically confirmed as a genuine per-employee-vs-total-payroll
misinterpretation (multiplied a stated TOTAL payroll by headcount, same
shape as eval_249) — correctly scored as failing, but only by luck of the
scorer (the correct answer's only figure is bare '0', which the leniency
bug doesn't help here). This case should arguably be flagged
scorer_reliability=False as well, since threshold/"TZS 0" answers are
exactly where number-overlap scoring is unsafe in either direction.

### Corrections to initial (pre-verification) characterization
- eval_191 does NOT explain Bucket A's 190->181 drop, as first stated —
  that drop is from 9 different rows (eval_192-200). eval_191 is itself
  compute-routed and lives in Bucket C, contributing to C's 20->19 drop.
- The 190-vs-181 figures are not an internal inconsistency in the data —
  both are correct, describing the raw bucket vs. the scored subset.

### Recommended next steps (not yet done)
1. Add a compute_type_reliable headline to eval_orchestrator_combined.py,
   matching the pattern already used for Buckets A and B, so the compute
   path's true (reliable-subset) performance is visible rather than
   burying it in per-question flags.
2. Fix the '000'-garbage-token bug in extract_numbers() — this affects
   scoring project-wide, not just Bucket C, since any number-type question
   with a comma-formatted TZS amount is at risk.
3. Consider flagging threshold/"answer is zero" reference answers as
   scorer_reliability=False by default, since number-overlap scoring
   cannot meaningfully verify a "does not apply" conclusion.

### Net assessment
Fact-path parity is real and strong — the compute-path work is correctly
isolated and did not disturb it. The compute-path itself is now producing
real, deterministic, rules-engine-backed arithmetic for the first time in
this project's history, but its true accuracy has not yet been measured
on a trustworthy denominator — the reliable-subset sample (n=6) is too
small to draw a conclusion from yet. This is not a regression or a failed
milestone; it is an honest, evidence-based statement of exactly how far
validation has actually gotten, consistent with this project's standing
practice of not trusting a headline number until its scoring methodology
has itself been verified.

## STANDING LESSON — validate Swahili semantic/numeral tests at FULL SCALE (2026-07-17)

Any test in this project that hinges on Swahili semantic or numeral ambiguity MUST be
validated on the full set before its result is trusted, no matter how clean a small
sample looks. A clean sample is NOT evidence; only the full run is.

This has now happened THREE times this session, same shape every time:
1. mDeBERTa NLI hybrid scorer — clean on a 14-example proof, rejected at 190-scale.
2. xlm-roberta-large-xnli — same pattern (small proof convincing, full-scale failure).
3. Slot extraction (chike/extraction.py) — 18-sample dry run showed correct_extract=6 /
   DANGEROUS_wrong_extract=0; the full 205 exposed 25 DANGEROUS (12.2%), concentrated in
   wrong_calculation_number (10/22) and compound_question (9/21) — the categories where a
   number is PRESENT but belongs to something other than the field being extracted
   (a threshold, sales/revenue/capital figure, share/branch count, a different sub-question).

Why samples mislead here: these failures are LONG-TAIL and semantic. An 18-question sample
picks the obvious shapes; the dangerous shapes (sales-figure-as-payroll, USD-as-TZS,
share-count-as-money) are individually rare and only surface in volume. The generic
(computation_type=None) path in particular had NO wrong-base guard at all — invisible until
the full set hit vat/brela/osha/gn487a questions carrying non-payroll numbers.

Rule going forward: no extraction/scorer change is "confirmed" on a sample. Sample = smoke
test only. The full-scale run is the gate.

## Slot-extraction danger investigation — CLOSED (RC-1/2/3 fixed, RC-5 tracked separately)

Full-205 stress test progression: 25 DANGEROUS -> 18 (grader/dataset fixes) -> 8 (RC-1 wrong-base guard) -> 2 (RC-2 plausibility floor, RC-3 currency/net detection).

Final confirmed state, real v15 model on Kaggle, exact match to local prediction:
correct_extract=31, correct_clarify=105, over_clarify=52 (safe misses), compound=15,
DANGEROUS_wrong_extract=2 (both RC-5, tracked below).

RC-5 (extract_078, extract_205) — NOT a numeral-parsing bug. The extracted figure
is genuinely correct in both cases; the problem is the question is a yes/no
compliance question (BRELA registration, VAT registration) that happens to
mention a real payroll figure, and the generic compute-routing path treats it
as a computation question when it should route to a fact-lookup/yes-no answer
instead. This is a routing/classifier scope issue, not an extraction issue.
Tracked as a separate follow-up pass — do not attempt to fix via the extractor,
since the extractor correctly reading a real figure is not the bug.

Extraction logic (chike/extraction.py + chike/swahili_numbers.py) is now
considered production-ready for the fact types it covers: SDL/NSSF/PAYE/WCF
payroll and employee-count extraction, correctly handling vague quantities,
missing antecedents, non-uniform per-person figures, period conversion,
casual slang/approximation, gross/net/allowance ambiguity, currency-unit
mismatches, and wrong-base figures (sales/capital/turnover/share-count
misread as payroll) — validated at 205-question stress-test scale with
two independent confirmations (local deterministic simulation matching
real v15 model output exactly, twice).

Standing lesson reconfirmed a third time this session: small-sample tests
are not predictive of full-scale behavior for Swahili numeral/semantic-
ambiguity logic. Full-scale validation is mandatory before trusting any
result in this category, regardless of how clean a smaller sample looks.
(Refinement: the lesson is about sample SIZE — local deterministic
simulation IS trustworthy once validated at full scale, now proven twice.)

## Extraction danger-case investigation — RESOLVED 25 -> 2 (2026-07-17)

Full-205 stress test on the real v15 exposed 25 DANGEROUS_wrong_extract (a HIGH-confidence
wrong number about to feed the rules engine). All 25 shown verbatim and categorized by root
cause. Fixes (one coherent pass):
- Grader false positives (6): compound danger is now keyed on whether a real computation
  type consumes the value, not mere HIGH confidence in a compound context.
- Dataset mislabel (1): extract_145 relabeled vague_quantity -> swahili_number_words (audit
  trail preserved in _review_original_category_2 / _review_relabel_2026_07_17).
- RC-1 wrong-base guard (9+1): detect_wrong_base now runs on the generic ct=None path (was
  gated to compute types, missing vat/brela/osha/gn487a entirely) + verb-form ("tunauza")
  and threshold ("kizingiti cha vat") and share ("hisa") patterns. Also caught extract_125.
- RC-2 plausibility floor (3): a monthly payroll/salary < MIN_PLAUSIBLE_AMOUNT (10,000 TZS)
  is a miscounted quantity (branches/employees/shares), vetoed to LOW. Also makes
  detect_missing_antecedent key on PLAUSIBLE amounts so a spelled count ("wawili"=2) no
  longer masks a missing antecedent (extract_153).
- RC-3 currency/net/per-diem (3): foreign-currency figures ("dola 300") flagged for
  conversion; net/take-home noun forms ("baada ya makato","mkononi") and explicit
  non-salary per-diem ("siyo mshahara","malazi na chakula") added to the allowance veto.

Full local deterministic 205 run: DANGEROUS 25 -> 2. 115/115 tests pass. No false wrong-base
or floor vetoes on genuine payroll questions (every affected SHOULD_EXTRACT case is a real
sales/capital/count-only question, correctly not extracted as payroll).

### RC-5 — TRACKED FOLLOW-UP (NOT fixed in this pass): routing/scope, not numeral parsing
extract_078 ("laki nne kila mmoja ... tunahitaji kusasisha BRELA?") and extract_205
("Payroll yetu milioni tano ... nisajili VAT?") are the last 2 DANGEROUS. The extracted
figure is GENUINELY CORRECT (400,000 / 5,000,000) — the problem is the question is a
BRELA/VAT yes/no that should never be routed to a payroll computation at all. This is a
classifier/route() scope fix, NOT an extraction-layer bug; forcing it into the numeral
parser would make the extractor second-guess valid figures. Fix at the routing layer in a
separate pass (broaden the out-of-compute / fact-intent detection so a payroll figure inside
a non-payroll question doesn't trigger the compute path).



## chike/extraction.py real logic built + Kaggle regression staged (2026-07-16) — UNCOMMITTED, pending founder review

Replaced the interface-only slot-extraction stub with real logic, tested against the
human-verified 205-example stress test. NOT committed — waiting on the founder's review
of the Kaggle results (per instruction).

Architecture — two layers, deliberate trust split:
- MODEL layer (chike/extraction.py SlotExtractor): the ModelBackend does free-text role
  assignment (which number is payroll vs headcount vs salary) — the model's real strength.
- DETERMINISTIC layer (chike/swahili_numbers.py, NEW, 15/15 local tests): pure unit-tested
  Python owns confidence + clarification, because this session proved even a 32B judge
  misreads Swahili compound numerals (laki/robo/mia). It can only DOWNGRADE a field to LOW
  (-> clarify) or apply a deterministic period conversion; never invents a value. Explicit
  detectors: vague_quantity, approximation(casual_slang), missing_antecedent, wrong_base
  (non-payroll figure for a payroll levy), allowance/gross-net, period(annual/quarter/half
  -> /12,/3,/6; week/day -> clarify), plus a numeral cross-check (downgrade if the model's
  value disagrees with the deterministic parse of a single-figure question).
- Failure-category mapping proven locally (FakeBackend, no GPU): all vague/slang/wrong_base/
  allowance -> correct_clarify; all swahili_number_words/period_conversion/aggregate/
  non_uniform -> correct_extract; 0 DANGEROUS (confident-but-wrong) mis-extractions.

Orchestrator wiring: _answer_compute now passes computation_type into extract(); no other
change. Existing 8 extraction tests still green; existing fact path untouched (route()
unchanged), so the 190 fact-path questions are byte-identical to the prior baseline.

ROUTING FINDING (surfaced during the build): orchestrator.route() only sends keyword+DIGIT
sub-questions to compute, so word-form-number ("milioni mia mbili na hamsini") and no-digit
vague questions bypass extraction entirely. The Step-4 stress test therefore calls
SlotExtractor directly (isolating extraction from routing). Broadening route() to catch
word-form compute intent is a separate follow-up (would move questions between the fact/
compute buckets, so deferred to keep the 190 fact-path comparison clean).

Kaggle scripts staged (prepare-only; founder runs on GPU, Claude never runs them locally):
- kaggle/extraction_stress_test.py — real v15 model vs the 205 reviewed entries, sample(18)
  then full(205); grades correct_extract / correct_clarify / DANGEROUS_wrong_extract /
  over_clarify per failure_category; persists to adapter-v15 HF repo.
- kaggle/eval_orchestrator_combined.py — 200 gate + 50 staged additions = 250 through the
  real orchestrator; reports (A) fact-path 190 UNCHANGED check, (B) first real score on the
  50 staged additions, (C) first real score on the ~10 compute-type questions now through
  real extraction + rules engine. Raw + reliable-denominator (scorer_reliability) scores.

DATA PREREQ (both scripts): data/reviewed/slot_extraction_stress_test_001_reviewed.jsonl and
eval/accuracy_gate/eval_questions_002_additions.jsonl are gitignored/untracked -> NOT on
GitHub, so the founder must upload both to the HF dataset repo (prospAprospA007/
africa-giants-dataset) before running (loaders check local clone -> /kaggle/input -> HF).

## qwen3-32b judge non-determinism finding (2026-07-16)

During slot-extraction dataset review, extract_120 and extract_011 both flipped
verdicts between a 13-entry sample run and the full 205-entry run, despite
temperature=0 configuration. This confirms qwen3-32b via OpenRouter is not fully
reproducible even at supposedly deterministic settings — likely provider-side
routing or reasoning-token variance. Any future single-pass judge verdict on a
borderline case should not be treated as final; consider a second confirmation
pass for anything near a decision boundary.

Also confirmed: qwen3-32b makes real errors on Swahili numeral parsing
specifically (laki/robo/milioni compound number words) — 7 of 22 flags in this
review were the judge misreading the entry's own correct figures, not genuine
dataset defects. This model is usable as a general semantic judge (proven
earlier in the scorer-adjudication work) but should not be fully trusted, without
a second check, on tasks specifically requiring correct Swahili numeral
comprehension.

Context/artifacts: harness kaggle/slot_extraction_review.py (self-contained,
OpenRouter qwen/qwen3-32b, additive-only review of the 205-entry slot-extraction
stress test against locked_facts.json on 3 axes: number fidelity, category fit,
self-consistency). Full run: 205 entries, $0.0866, 426s, 0 parse/API errors,
183 correct / 22 needs_revision. After manual triage the 7 confirmed judge-error
false-positives were corrected to `correct` (marked `_review_correction:
judge_error_confirmed` with the specific misreading recorded in
`_review_judge_original_reason`), leaving 190 correct / 15 needs_revision.
The 15-item human queue lives in data/reviewed/human_review_priority.jsonl
(4 factual_error defects: extract_064 OSHA-safety-officer-threshold-unconfirmed,
extract_164 SDL-10-threshold, extract_052 WCF-allowance-unconfirmed, extract_194
thin-spec; 10 category_dispute; 1 borderline_substantive extract_011). All files
stay in gitignored data/reviewed/, uncommitted, NOT merged into the extraction
build — that still waits on the human pass.

## Hybrid-scorer investigation CONCLUDED — both NLI models rejected, qwen3-32b judge is a genuine improvement (2026-07-16)

Goal: find a semantic layer to replace the regex fallbacks for the 71 gate
questions the fixed scorer marks `scorer_unreliable` and excludes (yes_no
polarity, qualitative-number, year-collision, morphological-overlap cases — see
the 2026-07-13 scorer-audit entry below). Three candidates were tested with the
SAME two-stage protocol every time: (STAGE 1) the 14 confirmed audit examples
against known ground truth, then (STAGE 2) the full 190 non-refusal question IDs.
Every run was executed on Kaggle by the founder and PERSISTED to the v15 HF repo
(`prospAprospA007/africa-giants-adapter-v15`) so the numbers below are read from
saved per-question data, not a local run or a truncated log.

Decision metric (same for all three): FALSE-DEMOTION count — currently-reliable
PASS answers that the candidate would flip to FAIL. A candidate that newly breaks
correct answers is not shippable, so this must be ~0.

### 1. Embedding similarity (intfloat/multilingual-e5-base) — REJECTED
Cosine similarity between reference and generated answer is blind to polarity:
clear contradictions (e.g. eval_059 "handwritten receipt OK", which is WRONG)
score HIGHER cosine than several correct answers. Best single threshold ≈ the
majority-class baseline. Topical similarity swamps correctness. Not viable.

### 2a. NLI — MoritzLaurer/mDeBERTa-v3-base-xnli (280M) — REJECTED
Rule: sw-sw bidirectional, max contradiction ≥ 0.70 ⇒ demote to FAIL.
STAGE 1 looked clean on the 14. STAGE 2 (full 190): **5 FALSE-DEMOTIONS**
(eval_120, eval_121, eval_126, eval_177, eval_191) — correct answers flagged as
contradictions at 0.81–0.98. High-confidence, so threshold-raising cannot fix
them. Confirmed from local run artifact.

### 2b. NLI — joeddav/xlm-roberta-large-xnli (560M) — REJECTED (worse)
Same rule, larger model. Persisted result `nli_regression_xlm-roberta-large-xnli.json`
(git_head 8efdd32). STAGE 1: 12/14 (missed 2 real contradictions, 0 false-positives
on the sample). STAGE 2 (full 190): **13 FALSE-DEMOTIONS** — CONFIRMED from the
saved file (this supersedes the earlier unpersisted "13" figure): eval_067, 074,
076, 081, 083, 086, 103, 119, 120, 121, 156, 161, 191. Several at 0.97–1.00
(eval_081=1.0, eval_119=0.99, eval_083=0.97) demoting plainly-correct definitions
and number answers. The bigger XNLI model is STRICTLY WORSE than mDeBERTa (13 vs 5).
Both NLI models share the failure mode: high-confidence spurious contradictions on
Swahili negation/polarity constructions — exactly the categories we needed help
with. The earlier "hang" on this model was root-caused (slow ~2.24GB anonymous
download + no staged logging, not a freeze) and fixed in the harness; the model
itself is the problem, not the plumbing.

### 3. Frontier LLM-as-judge — qwen/qwen3-32b via OpenRouter — GENUINE IMPROVEMENT
Dense 32B, Qwen3 documents 119 languages incl. Swahili. Judge task: given
(question, reference answer, generated answer) classify generated as substantively
correct / wrong / undetermined + one sentence. Persisted result
`judge_regression_qwen3-32b.json` (git_head 8efdd32). No GPU — runs on OpenRouter.

- **STAGE 1 (14, TRUE ground truth): 12/14 match.** Only **1 genuine harmful error**
  (eval_026, false-demote — misread a deadline) and **1 conservative abstain**
  (eval_093, undetermined instead of wrong). 0 false-promotions. Crucially it
  **correctly rescued eval_157 and eval_175** — two answers the regex scorer had
  WRONGLY FAILED — proving the judge corrects regex, not the reverse.
- **STAGE 2 (190): false-demotion = 13, false-promotion = 6, and it covered ALL 71
  currently-EXCLUDED questions** with a verdict (the entire point of the exercise),
  101 agreements with reliable regex, 0 API errors.
- These 13/6 are DISAGREEMENTS WITH THE IMPERFECT REGEX BASELINE, not proven errors
  (unlike NLI's demotions, which are demotions of verified-correct answers). By type
  the 13 demotions are 6 `number` (genuine regex false-passes on miscalculated
  figures the judge caught — e.g. eval_191 PAYE, eval_072 deadline, eval_091 NSSF),
  6 `procedure` (over-strict completeness/ramble penalties — the judge's real
  weakness), 1 yes_no. The 6 promotions include the two ground-truth-confirmed
  regex false-fails above.
- **Cost/latency: 205 calls, $0.0183 total, 160s wall for 191 calls (8 workers,
  6.33s/call mean).** Trivially acceptable for a gate-run cadence (gates run
  infrequently; ~2 cents and <3 min is nothing).

### Recommendation / next step
- chike/scoring.py stays UNCHANGED. Neither NLI model nor embeddings will be added.
- qwen3-32b is NOT rejected — it is the first candidate whose disagreements are
  mostly the judge being RIGHT (it caught regex false-passes AND rescued regex
  false-fails, and covered all 71 excluded questions). Its only real fault is
  over-strictness on `procedure` completeness.
- Per the founder's escalation branch: this is a genuine improvement worth
  ESCALATING to a larger paid frontier model on the identical harness, to see
  whether the `procedure` over-strictness disappears, and to adjudicate the 13
  demote / 6 promote disagreements against locked_facts.json to measure the judge's
  TRUE precision before wiring it in as the scorer's confirmation layer. Do NOT
  adopt it as a silent automatic scorer until the procedure over-strictness is
  characterized.
- Harnesses are committed and reusable: kaggle/nli_regression.py and
  kaggle/judge_regression.py (both fetch-and-run, both persist to v15 HF).

## v16 orchestrator fact-path parity — CONFIRMED EXACT (final, 2026-07-14)

After two rounds of scorer/cleanup fixes (yes_no polarity fix, clean_reply
parity fix, clean_reply ramble-hardening fix), the v15 pipeline and v16
orchestrator were re-run on Kaggle with fully identical scoring and cleanup
logic (both at commit d72f98f). Result on the exact 190 question IDs the
orchestrator was run on (181 in-corpus fact-path + 9 OOC): v15 = 161/190 =
**84.7%**, orchestrator = 161/190 = **84.7%**, with **0** per-question
disagreements out of 190.

This is definitive proof, not an estimate: raw model generations were already
proven byte-identical between the two pipelines (same v15 adapter, same greedy
decoding, same prompts, now non-Modal in-process load in both). The only
differences ever found were in post-generation measurement (scorer bugs, cleanup
divergence), and those are now fixed and shared across eval.py, modal_app.py, and
the orchestrator via chike/scoring.py + chike/generation_cleanup.py. Zero
disagreements is the direct consequence.

IMPORTANT — corrected historical record: v15's IN-CORPUS gate metric, measured
honestly with the fixed scorer/cleanup, is **84.7% (161/190)** — below the
operative **0.85** in-corpus threshold (kaggle/chike_config.json gate_thresholds,
the R14 single source of truth). The stored gate_001_results.json records
`gate_passed: False`. This is the first time v15 fails its own gate. Every
previously recorded v15 gate score (91.1%, 88.0%, 87.9%) was inflated by the
scorer bugs now fixed. The model's actual quality has not changed — the
measurement is now honest. Production has been serving at this true quality
level all along; this is a pre-existing measurement gap now closed, not a new
problem introduced by v16 work.

  (Note on framing: the gate scores in-corpus and OOC as two SEPARATE pools —
  in_corpus ≥ 0.85 AND out_of_corpus ≥ 0.70. OOC is 10/10 = 100%. A naive blend
  of both pools (171/200 = 85.5%) is NOT how the gate is scored and must not be
  cited as a pass; the failing pool is in-corpus at 84.7%. The 0.85 in-corpus
  threshold is the intended governing value in chike_config.json (R14); CLAUDE.md's
  old 0.82 reference was stale and has been corrected to 0.85.)

v16 orchestrator status: fact-path is proven at true parity with v15, using
real, non-proxy, non-Modal-dependent gate runs on Kaggle. Remaining work
(compute-path slot extraction, the 10 excluded compute-routed questions) is
unchanged — still correctly blocked pending real ambiguous-phrasing data.

Immediate implication (project-wide, requires a decision): since v15 (production)
now measures below the 0.85 in-corpus gate threshold with honest scoring, and the
orchestrator matches it exactly, NEITHER system currently passes the gate. This is
a real finding — not a v16 problem, a project-wide one. Options: raise real
accuracy (fact/generation work) or revisit the threshold with eyes open. No
silent reversion of the scorer fixes.

## Confirmed gate status (2026-07-13) — threshold reconciled to 0.85

CLAUDE.md previously referenced an outdated 0.82 in-corpus threshold; the
actual, intended, governing threshold has always been 0.85 in
chike_config.json (R14 single source of truth). CLAUDE.md corrected to match.

With the threshold confirmed at 0.85:
- v15 (production): 84.7% in-corpus (161/190) — FAILS the gate
- v16 orchestrator: 84.7% in-corpus (161/190) — FAILS the gate, exact parity with v15
- Both: 100% OOC — PASSES

This is not a v16 regression. It is the first honest measurement of production's
true accuracy, after fixing three scorer/cleanup bugs that had inflated every
previous recorded score (91.1% -> 88.0% -> 84.7%, corrected). Production has
been serving real WhatsApp users at approximately this true accuracy level
all along.

This is a real, standing gap against the project's own stated bar and needs
a decision: either close the accuracy gap (more/better training data, or the
frontier-model path already discussed earlier this project), or make a
deliberate, documented decision to adjust the threshold with clear reasoning
if 0.85 is reconsidered as the right bar — not by silently drifting to
whatever a given measurement happens to produce.

## Additional measurement findings (2026-07-13, post-parity investigation)

### Finding 4 — Compute-path exclusion flatters the orchestrator's headline number
The 181-question 'shared' comparison excludes 9 in-corpus compute-routed questions
that v15 answers correctly (no routing) but the orchestrator cannot yet answer
(slot extraction unbuilt, correctly stubbed). Counting these as fails on the full
190-question in-corpus set: orchestrator = 152/190 = 80.0%, v15 = 161/190 = 84.7%.
The 'exact parity' claim is TRUE ONLY for single-part, non-compute questions.
On the full set, the orchestrator is currently 4.7 points behind v15 — this is
the real, quantified cost of the deferred compute-path work, and should be
stated whenever the orchestrator's score is cited.

### Finding 5 — A fourth scorer bug inflates the in-corpus baseline itself
chike/scoring.py's number/penalty scorer falls back to 'pass if response is
>10 characters' whenever the expected answer contains no 3+ digit number,
percentage, or TZS amount (e.g. 'siku ya 7', 'ndani ya mwezi mmoja', '15
activities'). 27 of 82 number/penalty questions (33%) hit this fallback.
Confirmed genuine false-passes: eval_178 (hallucinated OSHA minimum-employee
threshold that doesn't exist), eval_114 (no SDL deadline given, credited pass),
eval_093 (wrong NSSF deadline, credited pass), eval_176 (contradicts locked_facts
and the gate's own reference answer, credited pass). This bug affects v15 and
the orchestrator equally (shared scorer), so it does not affect the parity
finding, but it means the 84.7% headline itself is inflated. Estimated honest
score after removing confirmed false-passes: approximately 82.5-83.2%.

Also flagged: eval_176's reference answer in the gate question set itself
contradicts locked_facts.OSHA_safety_officer_threshold, which explicitly says
this figure is unconfirmed and must not be stated — a separate gate
data-quality issue requiring correction independent of the scorer fix.

## Comprehensive scorer audit + coordinated fix (2026-07-14, commit 255a9ec)

After four separate scorer bugs were found one-at-a-time this session, a single
deliberate exhaustive pass was done over EVERY answer type in chike/scoring.py.
Six bugs total. **Key meta-finding: the scorer has both inflation AND deflation
bugs, and they roughly cancel — so Finding 5's "84.7% is inflated to ~82.5%" was
itself wrong-signed.** On the trustworthy (verifiable) subset the real figure is
HIGHER than 84.7%, not lower (see numbers below).

The six bugs:
- BUG 1 (number/penalty, inflates): `if not correct_nums: return len>10` length
  fallback when the answer has no 3+digit numeric key. 26 questions. Confirmed
  false-passes eval_178/114/093/176.
- BUG 2 (number/penalty, inflates): `\d{3,}` extracts the year '2025' from
  'Finance Act 2025' boilerplate; a shared year passes the question. Confirmed
  eval_033.
- BUG 3 (number/penalty, deflates): `extract_numbers` didn't compose multiplier
  words, so 'milioni 5' (→1,000,000 + dropped '5') never matched '5,000,000'.
  Confirmed false-fail eval_165 (a perfectly correct answer scored wrong).
- BUG 4 (yes_no, deflates + latent inflation): fixed negation list misses regular
  Swahili negatives (haku-/hau-/ha-+verb) and a subordinate-clause 'hakuna' flips
  polarity; the affirmative default silently passes any 'yes'-expected question.
  Confirmed false-fails eval_019/040/059/180/182.
- BUG 5 (definition/procedure, deflates): exact-token overlap≥3 defeated by
  morphology (usajili/usajilishaji) and synonyms (inakataza/inazuia,
  wageni/wasio-raia). Confirmed eval_026/157/175.
- BUG 6 (default branch, latent inflation): unknown answer_type fell through to a
  silent 'pass if >20 chars'.

**Empirical proof BUGs 1/2/4/5 are NOT regex-fixable:** a broadened yes_no
negation regex was built and regression-tested across all 61 yes_no — it made 5
correct fixes but introduced 3 NEW regressions (eval_060/153 clearly wrong),
because Swahili negations occur in both decisive and subordinate clauses. Every
broadening trades a false-fail for a new false-pass. Proven, not asserted.

**Decision (hybrid): fix the two regex-clean bugs, exclude the rest.**
- BUG 3 + BUG 6 fixed in chike/scoring.py, regression-tested: only 2 number/penalty
  verdicts flip (eval_165 correctly now passes; eval_010 correctly excluded as
  compute-derived) — zero new regressions among scored questions. Test suite 99/99.
- BUGs 1/2/4/5: a new `scorer_reliability(q, generated)` classifier marks every
  affected question `scorer_unreliable` with a reason and EXCLUDES it from the
  scored denominator — reported separately as 'unscored, pending semantic judge',
  never silently passed or failed. Deterministic from the question + output, so
  v15 and orchestrator exclude the same set.
- Gate data fix: eval_176/eval_190 reference answers corrected to match
  locked_facts.OSHA_safety_officer_threshold (state the threshold is unconfirmed,
  redirect to osha.go.tz) instead of asserting the wrong '50 employees' figure.

**New honest gate math (offline re-score of the stored runs; Kaggle re-run pending):**
- v15: 200 questions → 71 marked scorer_unreliable → **113/129 = 87.6%** on the
  verifiable denominator.
- v16 orchestrator: 190 it ran → 68 unreliable → **106/122 = 86.9%** on the
  verifiable denominator (still separately owes the 9 compute-routed it can't
  answer — Finding 4).
- Unreliable breakdown (v15): qualitative_number 26, yes_no_polarity 20,
  compute_derived 12, year_only 6, year_collision 2, morphological_gap 3,
  yes_no_ground_truth_ambiguous 2.

Both systems clear 0.85 ON THE VERIFIABLE SUBSET — but this is a REDUCED
denominator (129/200). The 71 excluded questions are genuinely unknown, not
passed: the system's true full-set accuracy is unknowable until a semantic judge
(LLM-as-judge / the frontier-model scoring path) scores the excluded categories.
Known residuals inside the 'reliable' set: ~2 synonym-variation false-fails
(eval_157/175) that prefix-stem detection doesn't catch — so 87.6% is a slight
UNDER-estimate. The long-term fix for the excluded 71 is a semantic judge, not
more regex.

FOLLOW-UP REQUIRED before the Kaggle re-run reproduces these numbers: eval.py and
eval_orchestrator.py must be wired to call scorer_reliability(), emit
`scorer_unreliable`+reason per question, and report the reduced-denominator score.
That wiring is NOT in commit 255a9ec (which was scoped to scoring.py + the gate
data file per instruction).

## Gate measurement-bug fix + corrected baseline + orchestrator gate rework (2026-07-13)

A measurement bug was found during v16 orchestrator validation: the gate scorer was
crediting wrong answers, inflating reported scores. Three commits fixed it, then two
more prepared the orchestrator gate for a real (non-proxy) Kaggle re-run.

**Scorer fixes (commit da9c69a):**
1. `chike/generation_cleanup.py` `clean_reply` was blindly truncating at the first
   `\n\n`, discarding real content. Fixed to preserve content blocks until a genuinely
   fabricated block is detected (9 verdict flips, all fail→pass, zero regressions).
2. The `yes_no` scorer credited a wrong answer whenever a fabricated ramble happened to
   contain the expected keyword. Fixed to compare substantive-answer POLARITY (leading
   Ndiyo/Hapana/La word + Swahili negation markers on the first `\n\n` block) instead of
   a full-text substring scan.

**Corrected baseline:** the old v15 in-corpus figure of 91.1% was inflated by the
substring bug. A preliminary local rescore of stored v15 outputs gave ~85.3%, but the
definitive real Kaggle re-run of `eval.py` (2026-07-14) settled it at **84.7% (161/190)**
in-corpus — see the confirmed-gate-status section at the top of this file. Against the
governing 0.85 in-corpus threshold (chike_config.json, R14) this is a gate FAIL.
The 91.1% figure elsewhere in this file predates the fix and should be read as inflated.

**Scorer extraction (commit b5a5e83):** `score_question` + helpers extracted into shared
`chike/scoring.py` (leaf module, stdlib-only), consumed by both `kaggle/eval.py` (via
fetch-and-exec) and `kaggle/eval_orchestrator.py` (via git-clone import) — single source
of truth, following the `chike/prompting.py` / `chike/generation_cleanup.py` pattern.

**Raw pre-clean persistence (commit 96f9d8b):** the prior orchestrator run stored only
the CLEANED output, so when `clean_reply` changed there was no way to rescore offline —
forcing a full GPU re-run. Fixed: `SubAnswer` and `Reply` now carry a `raw_text` field
holding the model's pre-clean generation (captured in `_validate_and_clean` before `text`
is overwritten; merged onto `Reply` alongside the cleaned `text`). `eval_orchestrator.py`
now saves both `generated` (cleaned, scored) and `raw_generated` (pre-clean) per question,
so any future `clean_reply` change is rescorable from saved JSON without another GPU run.
26→96 test suite still green.

**Orchestrator gate de-Modaled:**
`eval_orchestrator.py` previously drove generation via `LocalAdapter` — an HTTP client to
a Modal raw-generation endpoint requiring a second Kaggle secret (`MODAL_API_TOKEN`) and
190 live HTTP calls. Rewired to load the v15 adapter DIRECTLY on the Kaggle GPU (new
in-process `KaggleDirectBackend(ModelBackend)`, byte-identical 4-bit load + generation
config + `StopOnSubstrings` stopping criteria as `eval.py`), passed into the Orchestrator
as its backend. Now needs ONLY the `AFRICA_GIANTS` HF secret — same as `eval.py`. No
Modal, no HTTP, no raw endpoint. `LocalAdapter` (the HTTP client) is left intact for
local-dev-over-HTTP use; the `chike` package stays torch-free (transformers imported at
script level, same as `eval.py`).

### Ready for Kaggle re-run (founder runs; Claude does not)
- `kaggle/eval.py` → real corrected v15 baseline (~85.3% in-corpus expected).
- `kaggle/eval_orchestrator.py` → real v16 orchestrator fact-path number (replaces the
  82.3% v15-stored-output proxy from da9c69a), saving both cleaned + raw output.
- Both need only the `AFRICA_GIANTS` secret + Kaggle GPU. Both fetch code from GitHub
  main, which is fully pushed.

## v16 Shared-Module Extraction — Complete

modal_app.py and eval.py now import chike.prompting and chike.generation_cleanup
instead of carrying inline copies of the RAG wrapper and stop/clean logic. This
closes the drift risk flagged during both earlier ports — there is now exactly
one place each piece of logic is defined (chike/prompting.py,
chike/generation_cleanup.py) and three places that use it via import: the
orchestrator, modal_app.py (via Modal's add_local_dir), and eval.py (via
fetch-and-exec of the two files, matching the existing pattern used to load
eval.py itself).

Production verified unaffected: 5 spot-check questions (GN487A, SDL, BRELA,
VAT withholding, zero-rated VAT) byte-identical to pre-change baseline.

### Gate re-verification scope (important — do not misread)

The eval.py gate tests the v15 pipeline (eval's own retrieve/decompose/generate,
mirroring production modal_app.py) with build_chat_prompt + clean_generated_reply
now sourced from the shared chike/ modules. It confirms the shared-module
extraction is behavior-preserving. It does not test the v16 orchestrator end-to-
end — the orchestrator is validated separately via FakeBackend unit tests and
raw-endpoint spot-checks. No gate currently exercises the v16 orchestrator
pipeline.

## Repo-integrity fix — untracked __init__.py files (found and fixed same session)

.gitignore's _*.py pattern was silently matching all __init__.py files project-wide,
meaning chike/__init__.py, chike/model_abstraction/__init__.py, and
chike/rules_engine/__init__.py were never tracked in git since item 1 of this
build phase, despite every commit succeeding and all local tests passing.

Root cause: Modal (add_local_dir) copies the working directory directly and
eval.py fetches individual files by name — both sidestep Python package import
entirely, so neither path ever exercised the actual package structure. Only a
fresh git clone would have hit ImportError on FakeBackend and AttributeError
on rules_engine.compute — confirmed empirically via git archive HEAD extraction
before and after the fix.

Fix: narrowed the ignore pattern to scripts/_*.py (matching the documented
scratch-file convention established earlier this session), committed the three
previously-untracked __init__.py files, and re-verified via fresh git-archive
extraction that the package now imports correctly from a clean checkout.

Lesson for future sessions: any local-only verification method (tests, Modal
deploy, manual imports) that runs against the working directory rather than a
fresh checkout can mask git-tracking gaps. The git-archive-extraction check
used here is now the standard verification method for confirming a package
is actually complete in git, not just present on disk.

## v16 status — porting phase complete

Six components built, tested, and proven against the real fine-tuned v15 model:
model abstraction layer, orchestrator, rules engine, retrieval, prompt wrapper,
generation cleanup. Fact-path questions (Q1-Q5 pattern) match production
exactly. Shared-module extraction eliminates duplication across all three
consumers (orchestrator, modal_app.py, eval.py).

Remaining gap: slot extraction for compound/compute questions. Confirmed this
session that v15 never solved this — the fine-tuned model attempted
calculations directly from natural language with no dedicated extraction step,
succeeding only on memorized scenarios. This is new architecture with no
port target, correctly blocked pending real ambiguous Swahili phrasing data
collection — not further engineering work.

## v16 Compute-Path Investigation — Resolved (not a bug, a scope confirmation)

Investigated whether v15 had a working slot-extraction step to port, following
the same pattern that succeeded for the wrapper, stop/clean, and decompose ports.

Finding: v15 never had slot extraction. The fine-tuned 8B model attempted
compound calculations directly from natural language in one shot, succeeding
only on scenarios matching a memorized worked example (e.g. exactly 12
employees at TZS 600,000) and failing on any other numbers — this is the
exact structural weakness documented throughout this project.

This means chike/extraction.py (built in item 4) is not a port target — it's
new architecture with no v15 precedent to validate against. This confirms,
rather than changes, the original scoping decision: the interface shape is
built and tested against FakeBackend; the confidence threshold and real
extraction-prompt design remain correctly blocked pending real ambiguous
Swahili phrasing data, which does not yet exist.

## v16 status summary

Fact-path (Q1-Q5 pattern): COMPLETE. Proven end-to-end through real
retrieval, real model, real wrapper, real cleanup, real decompose. Matches
production exactly.

Compute-path (Q6 pattern): PARTIALLY COMPLETE.
- Context loss: FIXED (decompose_query port)
- Routing to rules engine: WORKING (proven in earlier orchestrator tests
  with FakeBackend)
- Slot extraction from real free text: NOT YET BUILT — correctly blocked,
  requires real data collection, not more architecture work

Next session priority, unchanged from earlier scoping: collect real
ambiguous Swahili phrasing before touching slot extraction further. In the
meantime, the one remaining low-risk port available is the 3-way shared-module
extraction (chike/prompting.py and chike/generation_cleanup.py into
modal_app.py and eval.py, closing the drift risk flagged during both of those
ports) — this is available now and requires no new data.

## v16 Fact-Path Parity — Achieved

Q1-Q5 (single-topic fact questions) now produce answers through the v16
orchestrator that match production exactly: correct substantive content
(TZS amounts, percentages, Ndiyo/Hapana) AND correct format (no ramble,
no fabricated follow-up turns, correct domain citations).

This was proven empirically, not assumed:
1. Isolated the gap via a raw-generation Modal endpoint bypassing production's
   opaque pipeline
2. Confirmed retrieval, rules engine, and orchestrator routing were correct
   from the start — the gap was entirely in generate/validate stage formatting
3. Ported the RAG wrapper (chike/prompting.py) — fixed substantive correctness
4. Ported the stop/clean stage (chike/generation_cleanup.py) — fixed format/ramble
5. Both ports extracted into shared modules rather than duplicated inline,
   directly avoiding the class of divergence bug that caused two earlier
   production incidents this session

Remaining gap — Q6 (compound/compute questions):
- decompose_query not yet ported — thin stub splits on ?/(2)/(3) and loses
  context (employee count, salary figures) needed for the compute sub-questions
- Slot extraction from the 8B model doesn't reliably emit parseable structured
  output from a bare prompt — needs either a few-shot/chat-formatted extraction
  prompt (port from what if anything worked in v15) or routing extraction to
  a frontier model, consistent with the earlier-documented finding that
  arithmetic/compound-question handling is the 8B model's structural weakness

Next priority: port decompose_query (known-working logic, straightforward port)
before attempting to fix slot extraction (open question, needs investigation).

## v16 Build Progress

Items 1-4 complete, tested, committed:
1. Model Abstraction Layer — chike/model_abstraction/ (10/10 tests) — commit 55d516c
2. Orchestrator pipeline skeleton — chike/orchestrator.py (8/8 tests) — commit 329ccc5
   (was 7/7 at item 2; +1 clarification-routing test added when item 4 wired extraction in)
3. Deterministic rules engine — chike/rules_engine/ (pre-existing, now committed) — commit 31bc921
4. Slot extraction interface (confidence-signal shape only) — chike/extraction.py (8/8 tests) — commit 729dc54

Total: 26/26 tests passing, zero network/GPU dependency for the full test suite.
(Counts differ from the original build note's 6/23 estimate: extraction shipped 8 interface
tests, not 6, and the orchestrator gained a clarification-routing test in item 4 — 26 actual.)

BLOCKED — requires real data, do not proceed without it:
- Confidence threshold tuning for extraction routing
- Clarification response phrasing
- Both explicitly marked as TODO in chike/extraction.py (and the orchestrator sentinel
  CLARIFICATION_PENDING), tagged "requires real ambiguous-phrasing test data — see
  PROGRESS.md milestone 5 gap"

Remaining v16 items not yet started (per original build order):
- Real retrieval wiring (currently stub retriever in orchestrator)
- Real classifier wiring (currently thin phrase-match stub)
- Real decompose_query enumeration logic (currently thin newline/? split stub)
- Fidelity validation (currently stub, always returns True)
- Change detection job
- Monitoring/logging
- Admin tooling
- Frontier model comparison harness

Next session priority: collect real ambiguous Swahili phrasing (see RISKS.md,
'over-clarification' risk) before touching extraction further. All other stub
components (retrieval, classifier, decompose) can be replaced with the real,
already-proven v15 logic in parallel — none of that requires new data, it
requires porting existing working code into the new orchestrator shape.

## Real WhatsApp Testing Findings (2026-07-08) — Post v15 91.1% Gate

Confirmed working well:
- Compound question handling stable across multi-message conversation
- VICOBA multi-jurisdiction question correctly separated NSSF/BRELA/TRA scope
- EFD-VAT deadline interaction correctly answered
- GN487A inheritance question correctly identified as still prohibited (de facto control test)

New calculation errors confirmed (same root cause as documented NSSF limitation):
- SDL calculation wrong for 15 employees @ 450,000: gave TZS 63,750, correct is TZS 236,250
  (15 × 450,000 × 3.5%). Appears to compute per-employee flat amount rather than percentage of salary.
- NSSF calculation wrong for same scenario: gave TZS 675,000 (using only 10% employer share),
  correct is TZS 1,350,000 (20% total). Confirms scenario-pinned facts (600,000/12-employee
  example) do not generalize to different salary/headcount combinations.

New potential hallucination — needs verification:
- GN487A ownership threshold: model stated 'asilimia 25%' as the prohibited ownership
  percentage. This does NOT appear in locked_facts.json. GN487A prohibits OPERATING listed
  activities, not ownership percentage per se (see gn487a_shareholder_vs_operator_distinction).
  This number appears fabricated. Needs verification against primary source before any
  correction — do not assume it is wrong without checking, but do not treat it as confirmed
  either.

Confirms architectural conclusion already documented: scenario-pinned calculation facts
in RAG do not generalize. Every new salary/employee-count combination not matching a
pinned example risks wrong arithmetic. This is the clearest evidence yet that the fix
path is a calculation-capable frontier model for arithmetic-type questions, not more
worked examples in locked_facts.

Recommended next session priority:
1. Verify the GN487A 25% ownership claim — check TanzLII/gazette, confirm hallucination
   or find missing locked fact
2. Consider whether SDL/NSSF/PAYE calculation questions should route to a frontier API
   model (Claude/Gemini via OpenRouter) for the arithmetic step specifically, using RAG
   only to supply the rate/threshold facts, rather than expecting the 8B model to do
   percentage math reliably
3. This is a scoping decision, not a quick fix — do not attempt in a reactive cycle

## GATE PASSED — v15 (2026-07-07) — FIRST PASSING RESULT IN PROJECT HISTORY

In-corpus: 87.9% (167/190) — PASS (threshold 85%)
Out-of-corpus: 100% (10/10) — PASS (threshold 70%)

Subdomain results:
- brela_registration: 100.0%
- out_of_corpus: 100.0%
- efd_compliance: 95.0%
- osha_registration: 93.3%
- sdl_compliance: 92.0%
- vat_registration: 86.7%
- gn487a: 85.0%
- vat_withholding: 85.0%
- nssf_contributions: 76.0% (only subdomain below 85%, does not block aggregate pass)

What got us here:
1. 750 hand-coded training pairs (batch_015) written in v8's original style
2. Removed 9 eval-contaminated pairs present in corpus since v8 (R6 leak)
3. e5-base embedder migration — fixed multilingual retrieval gap (MiniLM buried English facts at rank 13-48 for Swahili queries)
4. Concise bilingual high-stakes facts (GN487A, SDL, NSSF, WCF, BRELA) — short Swahili-dominant text with values in both words and digits
5. RAG noise filter — dropped 26 bare legal citations/exemption facts that were generic attractors
6. Fixed PAYE band retrieval by consolidating into paye_bands_with_examples with worked example
7. CRITICAL FIX: no_repeat_ngram_size=2 was destructively interacting with RAG injection —
   forbidding the model from reproducing exact facts it was handed (tra.go.tz, TZS amounts),
   causing 45% domain corruption (.tz→.ke). Fixed by setting no_repeat_ngram_size=0.
8. Eval.py now tests the full production system (classifier + RAG + model) per R12 —
   previously tested bare model weights only

Production deployed: adapter-v15 on Modal (2026-07-07), live at
https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run

Post-deploy endpoint smoke test (6 critical facts): 5/6 correct and clean (no .ke
corruption, no token mashing). GN487A 10M, SDL 3.5%, BRELA 22,000, VAT withholding 6%,
zero-rated input VAT — all correct. KNOWN CAVEAT: PAYE-on-800,000 query returned
TZS 202,000 instead of 78,000 — the model over-reasoned the bands instead of using the
fact's stated answer. Fragile to phrasing (gate eval_191 phrasing passed). The concise
paye_bands_with_examples fact lists bands that invite miscalculation; a follow-up should
state 78,000 more emphatically or drop the band table. Not a corruption/retrieval issue.

## v15 Production Fixes — Complete (2026-07-08)

Fixed via real WhatsApp testing feedback:
1. Compound question fabrication — leading-question strip now loops, removes
   all consecutive fabricated (N) questions before the real answer
2. Compound answer truncation — max_new_tokens 280→350. All substantive
   information (SDL amount, NSSF amount, deadline, penalty rate) now completes.
   The model tends to append a redundant self-generated summary after delivering
   the full answer; this summary may still clip at 350 tokens, but no substantive
   content is lost — only a restatement of information already given.
3. NSSF compound calculation (120,000 → 1,440,000) — contrast-language fact rewrite
4. Domain corruption (.ke, nssf.or.tz) — post-generation regex correction
5. Repetition loops on complex queries — decompose_query enumeration pattern extension

Remaining known limitations (documented, not fixed):
- Triple-compound queries with untrained number scenarios (e.g. salary 900,000 when
  facts are pinned to 600,000/800,000) still produce refusal collapse rather than a
  coherent attempt. Requires a calculation engine or frontier API model with genuine
  arithmetic reasoning — not more RAG fact tuning. Backlogged.
- Model generates a fabricated preamble before some compound answers (stripped from
  display, still consumes generation budget) and a redundant summary after (may clip
  but is non-substantive). Root fix requires training data demonstrating direct-answer
  behavior on compound questions without preamble or recap — not a generation parameter.

RAG index: 210 facts, e5-base 768-dim, 14 critical regression guards in
kaggle/regenerate_rag_e5.py including contrast-language checks.

Gate result holding: v15 at 87.9% in-corpus / 100% OOC — confirmed no regression
from any production fix via spot-check (GN487A/SDL/BRELA/VAT withholding/zero-rated
VAT) after each change including the final max_new_tokens adjustment to 350.

## Known Limitations — Compound Query Generation (2026-07-08)

Surfaced via real WhatsApp testing of multi-part compound questions. Retrieval and
loop behaviour were fixed (decompose_query enumeration extension, commit 3e47597;
NSSF fact rewrite + regen guard, commits 3d6c1e2 / bd348f7). The remaining issues
below are model-generation limits of the 8B AfriqueLlama, not retrieval bugs.

1. Model number-selection failure on scaled calculations
   Fact retrieval works correctly (nssf_calculation_example retrieves at rank 1,
   contains the correct scaled total AND single-employee figure). The 8B model
   still sometimes selects the wrong number from a correct fact when multiple
   numbers appear in context. Attempted fix: explicit 'SI TZS 120,000' contrast
   language in the fact text (commit 3d6c1e2). Partial mitigation, not a full fix.

2. Scenario-pinned calculation facts do not generalize
   locked_facts calc examples are written for specific numbers (e.g. NSSF for
   12 employees at 600,000 each; PAYE for salary of 800,000). When a real user
   asks about different numbers (e.g. salary of 900,000), the wrong scenario's
   fact retrieves and the model either uses the wrong fixed answer or fails to
   adapt. This is a structural limitation of fact-based RAG for arithmetic —
   the system does not have a calculation engine, only worked examples.

   Fix path: either (a) add many more worked examples covering common salary
   bands, which does not scale, or (b) frontier API model with genuine
   arithmetic reasoning capability replacing the 8B parametric approach for
   calculation-type questions specifically.

3. Empty/refusal collapse on complex compound queries
   When retrieval succeeds (3 correct facts for 3 sub-questions) but the
   facts do not perfectly match the asked scenario, the model sometimes
   produces a bare refusal ('Thibitisha na TRA') rather than attempting a
   partial or approximate answer using the general principles it does know.

## Session End State (2026-07-05)

### Production system (live on WhatsApp +255637809070)
- Model: africa-giants-adapter-v14 on Modal (T4 GPU, scales to zero)
- RAG: 206 facts, cosine similarity, concise bilingual high-stakes facts
- Classifier: inference-time OOC filter (capital gains, mining, import duty etc.)
- Gate scores: 83.2% in-corpus (best ever), 90% OOC

### What works reliably in production (RAG-driven)
- GN487A penalty: TZS 10M non-citizen, TZS 5M facilitator ✅
- SDL rate: 3.5%, threshold 10+ employees ✅
- VAT registration threshold: TZS 200M/12mo, TZS 100M/6mo ✅
- VAT withholding: 6% services, 3% goods ✅
- NSSF: 10% employer + 10% employee = 20% total ✅
- BRELA annual return: TZS 22,000 ✅
- WCF rate: 0.5% of gross payroll ✅
- Capital gains / import duty / mining OOC: hardcoded refusal ✅

### Known limitations (model-generation, not RAG)
- Multi-part questions: RAG retrieves top-3 facts, cannot cover 5 subdomains in one query
- Minor Swahili typos: TZSh, asilimai, garbled domain on secondary topics
- SDL combined-query threshold: correct for simple queries, fails for mixed queries
- NSSF URL: updated to nssf.go.tz (old nssf.or.tz kept failing DNS)

### Architecture insight confirmed this session
The model handles Swahili formatting and persona.
Facts come from locked_facts.json via RAG.
Training more versions will not improve factual accuracy — RAG does that.
Next improvement = query decomposition for multi-part questions + stronger cross-lingual embedder.

### Immediate next session priorities
1. Query decomposition — break multi-part WhatsApp messages into sub-queries before RAG
2. intfloat/multilingual-e5-base embedder — better cross-lingual retrieval than MiniLM
3. Hand-coded pairs targeting specific eval failures (50 pairs, not yet done)
4. Pay Cerebrium $20.81 or close account
5. zuck30 lightweight offline Chike discussion

## Training History

| Version | r | Val Loss | In-corpus | OOC | Gate | Notes |
|---|---|---|---|---|---|---|
| v8 | 64 | 0.4447 | 82.1% | 70% | FAIL | Best stable — served production |
| v9 | 64 | 0.1164 | 82.1% | 40% | FAIL | Overfit epoch 2 |
| v10 | 128 | 0.4107 | 77.9% | 10% | FAIL | OOC collapsed, GN487A hallucination |
| v11 | 128 | 0.4660 | 73.2% | 30% | FAIL | v10-lora warmstart + epoch 2 overfit |
| v12 | 64 | — | 70.5% | 10% | FAIL | v8-lora warmstart, data conflict |
| v13 | 64 | — | 71.6% | 100% | FAIL | Classifier fixed OOC permanently |
| v14 | 128 | — | 83.2% | 90% | PASS | v11-lora warmstart, lr=2e-5, 3811 pairs — best ever, beats v8 82.1% |

Gate requirement: ≥85% in-corpus AND ≥70% OOC
OOC note: classifier handles OOC in production — gate OOC measures bare model

## v14 Training Config (commit — this session, 2026-07-03)
Hypothesis under test: does r=128 capacity unlock better fact recall than v8's r=64
(which plateaued at 82.1% and was never beaten by r=64 successors)?
- LORA_RANK = 128, LORA_ALPHA = 128 (matches v11-lora — shapes must match for warm-start)
- PREV_LORA_REPO = africa-giants-adapter-v11-lora (r=128 confirmed via adapter_config.json)
- learning_rate = 2e-5 — VERY conservative (half of v13's 5e-5). Rationale: nudge weights
  toward new GN487A/NSSF data without aggressively overwriting v11 epoch-1 knowledge.
  Risk = underfit if too low; val loss will show quickly.
- num_train_epochs = 1 ONLY (v11 epoch 1 val=0.4111 was best; epoch 2 overfit to 0.4660)
- ADAPTER_REPO = africa-giants-adapter-v14; LORA_ONLY_REPO = africa-giants-adapter-v14-lora
- Both HF repos created (exist_ok) this session
- chike_config.json version bumped to v14; training block updated (r/alpha 128, lr 2e-5)

## Architecture Findings — RAG + Refusal Classifier (2026-07-03)
Evidence gathered this session that reframes what to invest in next:
- **OOC refusal is SOLVED at the system level, not by the model.** v8 model-only refusal
  was 70%; with the inference-time phrase classifier + hardcoded refusal + system-prompt
  boundaries, OOC intercept is ~100% (5/5 OOC, 5/5 in-scope pass-through). The gate-2
  problem is closed by architecture, not by more fine-tuning.
- **Fine-tuning is the wrong tool for fact recall.** v8 (2,672 pairs) scored the best
  in-corpus ever (82.1%); every r=64 successor scored LOWER despite growing to 3,811 pairs
  (80.0 → 77.9 → 73.2 → 70.5 → 71.6). More pairs → interference, not more knowledge.
  8/15 v8-vs-v13 hard-fact outputs are byte-identical — LoRA barely moves the model on
  facts; retrieved/injected context dominates the answer.
- **RAG grounding is the correct fact path** (facts decay: VAT withholding changed 1 Jul
  2025, GN 605A revoked 2022 wage order 1 Jan 2026 — weights freeze facts, retrieval doesn't).
  v14 tests the capacity hypothesis (r=128), but the strategic bet is retrieval-first with
  the fine-tune demoted to register/refusal styling.
- Two-eval discipline going forward: keep the bare-weights eval as a DIAGNOSTIC (never hide
  it), gate the PRODUCT on the full-system eval (model + RAG + classifier). Not goalpost-moving
  as long as both are reported and RAG retrieves from the training family, eval from the
  practitioner family (R6).

## GN487A/GN605A Poisoning FIX (2026-07-03)
Root cause: RAG retrieval collision. The GN487A `full_legal_name` fact body contained NO
"Government Notice" anchor, while the GN605A fact literally contains "(Government Notice
No. 605A)". A GN487A name query therefore retrieved the 605A fact and the model parroted
"Government Notice No.605A" as GN487A's name (observed identically in v8 AND v13).
Fixes in `scripts/locked_facts.json` (canonical):
- Strengthened `gn487a_full_legal_name`: fact body now leads with "GN 487A is Government
  Notice No. 487A ... is NOT Government Notice No. 605A" (adds the correct anchor so RAG
  retrieves the right fact) + wrong_patterns catching any 487A→605A / 487A→wage confusion.
- Added `gn487a_vs_gn605a_disambiguation` fact — explicit separation of the two notices.
- Rebuilt RAG index: `scripts/precompute_rag_embeddings.py` → chike-inference/rag_embeddings.npy
  (232, 384) + rag_facts_text.json (was 231 facts → 232). Redeploy Modal to activate.
- Verified: locked_facts JSON valid (233 keys incl _meta); check_locked_facts on batch_014
  (1,122 pairs) = 0 flags (no false positives from the new patterns).

## v12 Gate Results (gate_001_results.json on HF adapter-v12)
- In-corpus: 70.5% (134/190) — Gate FAILED (need >85%)
- OOC model-only: 10% (1/10) — but 2 were tokenization artifacts ("n je" bug)
- OOC with fixed eval detection: 30% (3/10) — eval phrase list now patched (commit cecb349)
- OOC with classifier + model (full system): 9/10 = 90% — Gate PASSES at system level
- Root causes identified: 3 SDL tourism levy pairs mislabeled, missing day-7 deadline,
  n je tokenization bug in eval detection, missing explicit OOC boundaries in system prompt

## v12 → v13 Changes (commit b58317a, 2026-07-02)

### Architecture
- Inference-time OOC classifier added to `chike-inference/modal_app.py`
  - Phrase-level matching (multi-word, Swahili + English) — no single-word false positives
  - Intercepts: capital gains, import/customs duty, transfer pricing, stamp duty,
    mining royalties, EPZ, insurance premium levy, Zanzibar tax, crypto
  - HARDCODED_REFUSAL returned before GPU call for OOC questions
  - Tested: 5/5 OOC intercepted, 5/5 in-scope pass through, 9/10 eval OOC intercepted
  - Deployed to Modal: prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run
- Eval notebook now tests full production system (classifier + model), not model alone
  - Cell 1: classify_question() added; Cell 7: classifier runs before generate_answer()

### System Prompt (kaggle/chike_config.json)
- Added explicit OOC boundary list in Swahili and English
- Added explicit in-scope list (BRELA/VAT/PAYE/SDL/NSSF/OSHA/EFD/WCF/GN487A)
- Propagates to train_ddp.py via GitHub fetch; eval notebook via Cell 1 GitHub fetch

### Eval Detection (commit cecb349, 2026-07-02)
- Fixed "n je" tokenization bug: added space-variant phrases to REFUSAL_PHRASES
- Added check_refusal() with ' '.join(text.lower().split()) normalization
- Removed false-positive phrases (thibitisha na tra, wasiliana na) from kaggle notebook
- Applied to both kaggle/africa_giants_eval.ipynb and scripts/run_eval.py

### Data Fixes (batch_014: 547 → 549 pairs)
- REMOVED 3 Tourism Development Levy pairs mislabeled as sdl_compliance
  (Tourism levy = 1% on hotel revenue ≠ SDL = 3.5% of salaries; wrong tax, wrong rate)
  Moved to datasets/tier1a/rejected/sdl_tourism_levy_mislabeled.jsonl
- FIXED SDL deadline pair [4]: now states "siku ya 7 ya mwezi unaofuata" explicitly
- ADDED 5 targeted OOC hard-refusal pairs (capital gains, import duty, transfer pricing,
  stamp duty, mining royalties) — no partial answers, redirects to correct authority

## v13 Training Config (same as v12 — config was correct, data was the problem)
- LORA_RANK = 64 (matches v8-lora)
- PREV_LORA_REPO = africa-giants-adapter-v8-lora (stable baseline)
- learning_rate = 5e-5 (conservative)
- num_train_epochs = 1
- Gate requirement: >85% in-corpus AND >70% OOC (system-level with classifier)
- SFT uploaded: train=2889 / val=322 — prospAprospA007/africa-giants-dataset

## v13 Expected Gate Behavior
- OOC (system-level, classifier + model): 9/10 = 90% → PASS (≥70% threshold)
- In-corpus target: >85% — requires SDL and GN487A to recover to v8 levels
  - SDL was 84% in v8 → should recover with tourism pairs removed and deadline fixed
  - GN487A was 75% in v8 → needs to recover from v12's 55%
  - If both recover: in-corpus ~82-84% — close but may still need one more run

## RAG Retrieval History (2026-07-05)

Three-step fix applied this session:

1. Cosine normalization (59a2177)
   - Raw dot-product was giving high-norm vectors unfair advantage
   - Fix: normalize all embeddings before scoring

2. Noise drop (9f91b79)
   - 26 Swahili-only bare citations and exemption facts were outranking English
     value facts for every Swahili query
   - Fix: exclude legal citations, act references, exemption categories,
     signatory facts from the embedded index
   - Index: 232 → 206 facts

3. Concise bilingual facts (9f91b79)
   - 90% of value facts were English-only; Swahili queries matched Swahili
     noise instead of correct English facts (GN487A 10M was rank 18)
   - Fix: high-stakes facts rewritten as short Swahili-dominant strings
     with value in both Swahili words and TZS digits; no trailing bare
     domains (trailing domains were feeding URL hallucination)
   - Result: GN487A 10M → rank 1, SDL 3.5% → rank 1, NSSF 10% → rank 1

Final verified state (endpoint test 2026-07-05):
- GN487A non-citizen penalty: TZS 10,000,000 ✅ (was 5M dangerous)
- SDL rate: 3.5% ✅
- BRELA annual return: TZS 22,000 ✅
- VAT withholding services: 6% ✅
- NSSF employer: 10% ✅
- URL hallucination (brelautang.org): GONE ✅
- Token mashing (mgenimgeni, go.tzsijui): GONE ✅

Known remaining issues (model-generation, not RAG):
- Minor Swahili typos: TZSh, asilimai, mweka juu
- VAT cites wrong year (2024 instead of 2025)
- These are v14 8B model limits — addressed by frontier API path not RAG tuning

OSHA domain hallucination fix (607a923):
- Q9 OSHA question hallucinated OSHAnz.org (New Zealand OSHA)
- Fix: added domain-free OSHA concise facts (osha_registration_threshold_b004,
  OSHA_annual_inspection) — now cites osha.go.tz correctly
- Also removed dead concise key nssf_employee_rate (not in locked_facts)

## Known Limitations (architectural, not fixable by RAG tuning)

SDL combined-query threshold:
- Simple query 'SDL threshold ni wafanyakazi wangapi?' → RAG retrieves correct fact at rank 1 ✅
- Combined query mixing rate + threshold + comparison → generic percentage facts rank higher
- Model falls back to parametric belief of '11 employees' (incorrect — correct is 10)
- Root cause: 384-dim multilingual embedding cannot decompose multi-part Swahili queries
- Fix path: stronger embedder (intfloat/multilingual-e5-base) OR query decomposition
  before retrieval OR frontier API model — NOT more concise fact tuning (proven twice)

### Parametric memory override — v14 resists RAG correction on memorized strings

Two confirmed cases where v14's memorized values override correct RAG-injected facts:

1. SDL combined-query threshold
   - Model says 11 employees (wrong) even when correct fact (10+) is in context
   - Correct for simple queries, fails when mixed with rate/comparison

2. NSSF URL
   - Model outputs nssf.or.tz even when RAG explicitly injects nssf.go.tz
   - RAG can override numerical values (WCF 0.5% proved this)
   - RAG cannot override deeply memorized string tokens in 8B weights

Pattern: RAG reliably corrects number hallucinations (WCF 1M→0.5%, GN487A 5M→10M)
but cannot reliably correct memorized string tokens (URLs, thresholds stored as text).

Fix path: frontier API model (Claude Sonnet / Gemini Flash) — larger models do not
have this parametric override problem because their memorized URLs are more accurate
and their instruction-following is stronger.

## Current Production State (2026-07-05)

- Modal serving: africa-giants-adapter-v14 + inference-time OOC classifier
- RAG: 206 facts, cosine similarity, concise bilingual high-stakes facts
- Endpoint: https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run
- WhatsApp: +255637809070 via Wappfly → Railway → Modal
- Gate scores: v14 in-corpus 83.2%, OOC 90% (classifier)
- Best ever: 83.2% in-corpus (beats v8's 82.1%)
- Cerebrium: UNPAID ($20.81) — inactive, superseded by Modal

## Known Issues / Next Session Priorities

1. Hand-coded pairs (50 pairs targeting specific eval failures) — not yet done
   See: data/reviewed/hand_coded_batch_015.jsonl (may be empty or incomplete)
2. v14 minor generation quality (typos, wrong year) — model-level, needs either:
   a. More targeted training pairs in Chike's exact answer style
   b. Switch to frontier API model (Claude Sonnet / Gemini Flash via OpenRouter)
3. 1,129 pending fact candidates — review session needed
4. Cerebrium $20.81 bill — pay or formally close account
5. zuck30 lightweight offline Chike discussion — still pending

## R6 review — RESOLVED (Habib released) + GN487A eval-family quarantine
**Habib Advisory (162 pairs) — RELEASED into batch_014 on 2026-07-01.**
Cleared a 4-check eval-contamination scan vs eval_questions_001.jsonl:
CHECK1 exact-instruction=0, CHECK2 exact-output=0, CHECK3 "habib" keyword in eval=0,
CHECK4 semantic (normalized cosine, threshold 0.92 + subdomain-keyword topic gate)=
0 genuine risks (1 cross-topic false positive only). Habib Advisory is NOT in the
Section-4 eval whitelist, so no source-family conflict.

**GN487A practitioner sources — QUARANTINED (eval family, R6/R4).**
VELMA + Bowmans GN487A files moved to `data/eval_family_quarantine/immigration/`
(OUTSIDE the os.walk scan root so the pipeline never trains on them). Reason:
velmalaw.co.tz / bowmans.com / clydeco.com are the NAMED gn487a eval family
(CLAUDE.md §4; pair_reviewer.py maps gn487a eval -> immigration.go.tz). They may
later feed EVAL expansion only, never training.
Automated primary GN487A re-sourcing (tanzlii / gazette / immigration.go.tz /
parliament) FAILED: all returns were search/landing/homepage shells. **RESOLVED
2026-07-01** — founder supplied the official gazette PDF directly; 20 facts locked and
77 seed-generated training pairs merged (see Current State "Key changes"). The VELMA/
Bowmans eval-family files remain quarantined for possible EVAL expansion only.

## Pipeline — Autonomous Q&A Factory (Phases 1–4 COMPLETE)
The pipeline is now a one-command autonomous Q&A factory. Source doc → reviewed dataset → HF.
- **Phase 1 — Foundations:** configs updated, directories created, run.py rewritten (bd83be5)
- **Phase 2 — RAG:** locked_facts injected at inference, persistent numpy embeddings (9f53b40)
- **Phase 3 — Autonomous Q&A pipeline:** PDF/HTML/TXT → reviewed dataset (bf9e1fd)
- **Phase 4 — One-command HuggingFace upload** (5d73769)
- Multi-provider LLM support: Anthropic / OpenRouter / Ollama (405e9c7)
- Default generation model: gemini-2.5-flash-lite (cheaper than 2.5, better than 2.0) (c50fcaa)
- Local dedup via nomic-embed-text; pre-computed RAG embeddings; 402 fails fast (223ac6a)

## Gate History
| Version | In-corpus | Refusal | Gate | Notes |
|---|---|---|---|---|
| v6 | ~74% | 50% | FAIL | baseline |
| v7 | 79.5% | 80% | FAIL | refusal gate passed for first time |
| **v8** | **82.1%** | **70.0%** | FAIL | **best scores to date; production adapter** |
| v9 | 80.0% | 40.0% | FAIL | rebalanced dataset hurt refusal (stop-after-redirect not trained) |
| v10 | — | — | REVERTED | r=128 hallucinated on insufficient data — reverted to v8 2026-06-22 |
| v11 | pending | pending | pending | next training run — gated on batch_014 correction pairs |

**Best scores to date: v8 — 82.1% in-corpus, 70.0% out-of-corpus refusal.**
Both gates still unmet (need >85% in-corpus AND >70% refusal simultaneously).

## v9 Gate Results (gate_001_results.json on HF adapter-v9)
Total: 200 questions | Pass: 160 | Fail: 40 | **Overall: 80.0%** — Gate FAILED

| Subdomain | Pass/Total | % | Status |
|---|---|---|---|
| efd_compliance | 19/20 | 95.0% | ✓ |
| brela_registration | 14/15 | 93.3% | ✓ |
| nssf_contributions | 23/25 | 92.0% | ✓ |
| vat_withholding | 18/20 | 90.0% | ✓ |
| gn487a | 30/40 | 75.0% | ✗ |
| osha_registration | 12/15 | 80.0% | ✗ |
| sdl_compliance | 20/25 | 80.0% | ✗ |
| out_of_corpus | 4/10 | 40.0% | ✗ |
| vat_registration | 20/30 | 66.7% | ✗ |

### v9 Root Cause Analysis (drives batch_014 corrections)
- **vat_registration (10 failures):** arithmetic on thresholds, rolling 12-month definition, zero-rated vs exempt disambiguation, qualifying buyer definition
- **gn487a (10 failures):** full legal name never stated, effective date hallucinated (28+29 Jul), "mgeni" definition inverted, marriage exception wrong (ndoa haibadilishi hadhi), enforcement exercise dates wrong, enforcement body hedged
- **sdl_compliance (5 failures):** WCF rate wrong (20% instead of 0.5%), SDL threshold (10 employees) ignored, SDL+PAYE same deadline wrong, GN 605B cited (doesn't exist)
- **out_of_corpus (6 failures):** refusal-then-elaborate pattern — model says "nje ya maarifa yangu" then explains anyway; eval_191 (PAYE TZS 800K) misclassified as out-of-corpus
- **osha_registration (3 failures):** >50 employee safety officer requirement missed, late registration first step wrong

## Pending Tasks (Priority Order)

### IN PROGRESS
- v14 training on Kaggle (r=128, v11-lora warmstart, lr=2e-5, 1 epoch)

### AFTER v14 COMPLETES
- Run eval.py on v14 — watch for in-corpus improvement above 82.1%
- If v14 > 82.1% in-corpus: update Modal to v14, run full production test
- If v14 ≤ 82.1%: keep v13 in production, consider RAG-only architecture with frontier API model

### BACKLOG (non-blocking)
- Review 1,129 pending fact candidates — TRA-heavy (619), use generate-from-facts after approving
- Recover 74 flagged pairs — run approve-flags on batches 016, 018
- Pay Cerebrium $20.81 OR formally close the account
- zuck30 lightweight offline Chike discussion (held from earlier session)
- Consider replacing AfriqueLlama-8B with frontier API model (Claude Sonnet / Gemini Flash)
  via OpenRouter in modal_app.py — single line change, same RAG infrastructure

## Dataset State
- Source files: 15 batch files in `datasets/tier1a/cleaned_pairs/` (batches 001–013)
  - Batches 001–008: old 18-field schema (question_sw/answer_sw) — converted by generate_sft.py
  - Batches 009–013: SFT format (instruction/input/output/system) — direct use
- SFT files (current, on HuggingFace):
  - train_sft.jsonl: 2,395 pairs
  - val_sft.jsonl: 267 pairs
  - Total cleaned: 2,672 (10 excluded as eval_set:true)
- Generation: `python scripts/generate_sft.py` — always use this, never raw glob from cleaned_pairs

## Training Script
- File: `kaggle/train_ddp.py`
- Run: `python3 train_ddp.py` (Unsloth handles multi-GPU natively — no torchrun)
- Config: LORA_RANK=128, LORA_ALPHA=128, MAX_SEQ_LENGTH=2048, 2 epochs, lr=2e-4
- LESSON FROM v10: r=128 on the current dataset size hallucinated — expand data before re-running

## Last 10 Commits
- 223ac6a feat: pre-computed RAG embeddings, nomic-embed-text for local dedup, 402 fails fast
- c50fcaa config: use gemini-2.5-flash-lite as default — better than 2.0, cheaper than 2.5
- 405e9c7 feat: multi-provider LLM support — Anthropic, OpenRouter, Ollama
- 5d73769 feat: Phase 4 one-command HuggingFace upload
- bf9e1fd feat: Phase 3 autonomous Q&A pipeline — PDF/HTML/TXT to reviewed dataset
- 9f53b40 feat: Phase 2 RAG — locked_facts injected at inference, persistent numpy embeddings
- 444781f fix: preserve data/ directory structure in git with .gitkeep files
- bd83be5 fix: Phase 1 foundations — configs updated, directories created, run.py rewritten
- da47100 cerebrium: revert to v8, clear old model cache, v10 deferred pending better training data
- 711745a cerebrium: repetition_penalty 1.1 → 1.3, add no_repeat_ngram_size=4

## Known Issues / Technical Debt
- v10 reverted: r=128 hallucinated on insufficient data — production stays on v8
- Modal serving v13 + classifier (neither gate fully passed at bare-model level)
- `run_eval.py` (local) does not have the scorer fixes that the Kaggle eval notebook has
- eval_191 (PAYE TZS 800K) misclassified in refusal gate — should be accuracy gate
- Only 2 source documents staged — corpus expansion needs more raw material

## HuggingFace Repos
- africa-giants-adapter-v8: LIVE (production — best gate scores: 82.1% / 70.0%)
- africa-giants-adapter-v9 / v9-lora: built, gate FAILED (refusal regressed)
- africa-giants-adapter-v10 / v10-lora: built then REVERTED (hallucinated)
- africa-giants-adapter-v11: pending (gated on batch_014)
- africa-giants-dataset: 2,672 pairs (train 2,395 / val 267)

## Infrastructure
- Modal: serving adapter-v13 + OOC classifier (Cerebrium retired — see Current Production State)
- Wappfly: +255637809070
- Kaggle: training notebook (africa_giants_V2.ipynb) + eval notebook (africa_giants_eval.ipynb)
- GitHub: main branch
- HuggingFace token: Kaggle secret `AFRICA_GIANTS`
- Local pipeline: Ollama (qwen2.5:7b generation, nomic-embed-text dedup/embeddings)

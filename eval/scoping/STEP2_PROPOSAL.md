# STEP 2 PROPOSAL — held-out employer first-messages. **For approval before it is run.**

Frozen candidate set: `eval/scoping/heldout_employer_first_messages_040.jsonl` (40 rows).
Step 1 results: `eval/results/boundary_classification.json`,
`eval/results/coverage_gate_recut_by_boundary.json`,
`eval/results/natural48_readjudicated_2026_08_24.json`.

---

## ⛔ THE CONSTRAINT THAT SHAPES EVERYTHING BELOW, STATED FIRST

> **The decisive number — hit rate — CANNOT be produced by a set I author, because I choose the
> composition, and the composition IS the hit rate.**

If I write 20 payroll questions and 12 non-payroll ones, a payroll boundary "hits" 50%, and that
figure is a fact about my quota, not about employers. It is the coverage gate's 1.9% all over again
(R22): a number measured on a population built to make the mechanism look right.

So step 2 splits into two halves that must not be confused:

| half | what it measures | can I author it? |
|---|---|---|
| **2a — hit rate** | *would a real employer's first message land inside the boundary?* | **NO.** Requires messages sourced from people who were not told what the product does. |
| **2b — in-boundary accuracy + refusal copy** | *given a message on each side of the line, does the answer hold up, and does the refusal read as a door or a wall?* | **YES.** Composition is a design choice here, not a measurement. |

**The 40 rows attached are 2b.** They are ready to run and will settle the accuracy and copy
questions honestly. **They will not settle whether the product is worth building** — that is 2a, and
2a needs the founder.

---

## On external grounding: I looked, and there is almost none. Here is the exact position.

The instruction was to ground the messages in something external if any such thing exists, and to
say so plainly if it does not.

| candidate source | verdict |
|---|---|
| **Our own WhatsApp transcripts** | **ZERO ROWS.** Checked live against the `chike-transcripts-kv` Modal Dict on 2026-08-25: `rows: 0`. There is no user data in this project, which is precisely why step 2 exists. |
| **Regulator FAQ pages** (tra.go.tz, nssf.go.tz, brela.go.tz, wcf.go.tz) | Externally grounded **topics**, but regulator **wording** — the opposite of the register we need, and a curated view of what the regulator chose to publish rather than what people ask. Usable to check topic coverage; useless for voice. |
| **Practitioner advisory "frequently asked"** (EY / PKF / KPMG Tanzania) | Same limitation, and R6 already reserves this family for eval — correct for this use, but again topics, not voice. |
| **Founder's own network in Dar** | **The only true external ground available**, and it is available. See 2a below. |

**Therefore, stated as a bound and not as a measurement:** the 40 attached rows are authored by me.
Their *topics* are anchored to things outside my choosing — the 12 coverage-gap probes from
2026-08-16, the coverage gate's own arm-A failures, and the wrong rows of the natural 48 — but their
*phrasing is mine*. Anything they produce is a **lower bound on difficulty and an upper bound on
confidence** (R21).

**The one anti-contamination lever I could apply, and did:** **29 of the 40 rows use no regulatory
label at all** — no `SDL`, no `NSSF`, no `PAYE`. They say *"ile ya uzeeni"*, *"ile ya mafunzo"*,
*"kule serikalini"*, or nothing. Eight use the acronym, three the nickname. That distribution is
recorded per row in `label_form`, so the run reports accuracy **split by whether the user used our
vocabulary** — which is the closest thing to a paraphrase-space measurement that a self-authored set
can contain.

---

## 2a — THE DECISIVE HALF. What the founder needs to collect, and the one rule that protects it.

**Target: ~40 first messages from 10–15 real employers** (anyone paying at least one person),
2–4 each. It does not need to be a survey. It needs to be verbatim.

**The collection script, and it should not be varied:**

> *"Kama ungekuwa na msaidizi wa kodi na sheria za biashara kwenye WhatsApp, ungemuuliza nini
> kwanza?"*
> *("If you had a business tax-and-law assistant on WhatsApp, what would you ask it first?")*

**The one rule: do not tell them what it answers.** No menu, no examples, no "it's good at payroll".
The moment the topic is suggested, the hit rate is constructed rather than measured — and that is
exactly the error this whole step exists to avoid. If a tester asks "what can it do?", the answer is
*"anything about your business — what's on your mind?"*

**Record verbatim**, typos and all. A cleaned-up question is a different question.

**Then, and only then:** classify each against the candidate boundaries with the *committed*
`eval/scoping/classify_boundary.py` map, and the hit rate falls out. **This is the number that
decides whether a scoped product is worth building**, and it costs an afternoon of conversations
rather than a day of engineering.

---

## 2b — THE 40 ROWS. Composition, and what each arm is for.

| arm | n | expect | purpose |
|---|---|---|---|
| **A — in boundary** | 20 | answer | in-boundary accuracy. Spread across PAYE, SDL, NSSF, WCF, minimum wage, employment. Deliberately includes the shapes where the fidelity rules go vacuous (R19): applicability questions, procedure questions, base-not-rate questions. |
| **B — out of boundary, but an employer would ask it** | 12 | boundary refusal | **the refusal-copy arm.** Six are things the corpus *can* answer (VAT, EFD, BRELA, presumptive) — the boundary's cost made concrete. Six are things it cannot (licence, council levy, market dues, fire cert, rent withholding, mobile money). |
| **C — genuinely out of corpus** | 4 | OOC refusal | **control.** Capital gains, mining royalties, Zanzibar, import duty. A boundary must not *replace* the OOC classifier — if these stop refusing, the boundary has eaten a control that works. |
| **D — mixed, one part each side of the line** | 4 | answer part, decline part | **the hardest shape and the most likely in reality.** A boundary that can only refuse whole messages fails here, and real messages are not single-topic. |

**Row `emp_28` is load-bearing:** presumptive income tax on a 30M-turnover duka is *out* of
boundary under B1–B3 and *in* under B4. It is the single row that separates the candidate
boundaries, so it is worth watching on its own.

---

## The refusal-copy rubric — because "does the wall read as a door" is a real question with a real answer

Three copy variants, run on arm B, **judged blind** (variant labels stripped) by a Swahili speaker
who did not write them:

| | copy |
|---|---|
| **V1 — today's** | *"Sina uhakika kuhusu hili. Thibitisha na TRA."* |
| **V2 — boundary + right authority** | *"Hilo ni la Halmashauri, si TRA. Mimi nasaidia mambo ya wafanyakazi — mishahara na makato."* |
| **V3 — V2 + what I do cover, concretely, + a next step** | *"Hilo ni la Halmashauri ya Jiji — waulize ofisi ya mapato ya wilaya yako. Mimi nasaidia mishahara na makato ya wafanyakazi: PAYE, NSSF, SDL, WCF na mshahara wa chini. Una swali lolote kati ya hayo?"* |

**Five criteria, scored per reply:**

1. **Names the correct authority** — and, weighted heavier, **does not name a wrong one.** Sending
   someone to TRA for a council levy is worse than sending them nowhere.
2. **States what the product does cover.** This is the difference between a boundary and a wall.
3. **Gives a next action.**
4. **⚠️ Leaks no fabricated fact.** *This is the sharpest risk in the whole set and the reason arm
   B exists at all.* A refusal that says *"that's the council's — usually about 0.3%"* is a
   hallucination wearing a refusal's clothes, and it would pass every criterion above. **A refusal
   is not a safe output. It is just an output with fewer figures in it.**
5. **Reads as a person, not a form** (register check).

**And the criterion that actually decides the product, which no rubric can score:** *after this
reply, would you send a second message?* That needs a human on the other end, so it belongs to the
pilot — but it is the question the founder should hold in mind while reading the transcripts, and
it should be recorded as a yes/no per row.

---

## Protocol — the parts that are not negotiable

- **Freeze first.** The 40 rows are committed *before* anything runs. They are already in git.
- **Burned once.** Reading the failures is what turns a held-out set into a fitted one (R21). A
  second iteration needs a **new** set — budget for that up front rather than discovering it.
- **Per-row flush + resume.** R16's structural rule: the harness writes its artifact after every
  row and resumes from it. A dropped Tanzanian link at row 20 costs one row, never the run.
- **R24 exemption, stated rather than skipped:** these are new questions with no recorded live
  reply, so there is no baseline to reproduce. The R24 check does not apply and this note is why —
  not an oversight.
- **R22 inside the instrument:** the artifact carries its own `why_each_population` block, so the
  caveat cannot be separated from the number by being quoted.
- **Population named in every figure reported.** Not *"64% correct"* but *"64% correct on 20
  self-authored in-boundary questions"*.

---

## What is NOT in this proposal, and why

- **No boundary is implemented.** Step 2b runs against **production as it stands today**. The
  refusal copy is evaluated by comparing candidate wordings, not by shipping them. Nothing about
  this measurement requires a build, which is what makes it cheap.
- **No coverage gate.** See the step-1 finding: the boundary does not revive it.
- **No recruitment.** 2a is a founder task and it is the gating one.

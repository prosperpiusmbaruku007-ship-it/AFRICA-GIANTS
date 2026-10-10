# Supervised pilot runbook

The R7 reading this operates under, and its condition, are in `CLAUDE.md` —
**"THE R7 READING ON A SUPERVISED COHORT"**. Read that first. Everything below is the
mechanics of keeping that condition true.

---

## 0. Before anything: the throughput decision

`eval/results/review_throughput_estimate_2026_10_10.json`, asked and answered before
recruiting:

| cohort | questions/day | min/day to clear |
|---|---|---|
| 10 × 2 | 20 | **~21** |
| 5 × 2 | 10 | ~10 |
| **3 × 2** | 6 | **~6** |

**Ten users exceeds "a few minutes a day" by about four times.** The cohort is the lever.
Reducing review *depth* instead is the one adjustment that voids the R7 reading, because
skimming is the rubber-stamping the condition exists to prevent.

---

## 1. Deploy (R16b applies in full — warm containers serve OLD code)

```bash
python scripts/preflight_deploy.py chike-whatsapp/modal_whatsapp.py   # must exit 0 FIRST
python -m modal app stop chike-whatsapp --yes
CHIKE_BUILD=$(git rev-parse --short HEAD) PYTHONIOENCODING=utf-8 PYTHONUTF8=1 \
  python -m modal deploy chike-whatsapp/modal_whatsapp.py
```

The pre-flight comes **before** the stop, not after: the stop is instant and irreversible and
the deploy is neither. Twice a stop has succeeded and the replacing deploy has failed, leaving
production dead.

**Founder-only step:** add `SUPERVISED=1` to the `chike-whatsapp` Modal Secret (or set it as
an env var on the deploy). There is no CLI access to that secret from the dev machine.

---

## 2. ⛔ STEP ONE AFTER EVERY DEPLOY — verify supervision is ON

```bash
curl -s "https://<app>.modal.run/health" | python -m json.tool
```

Check, in this order:

| field | required | why |
|---|---|---|
| `build` | the SHA you just pushed | R16: a warm container will happily serve old code |
| **`supervised`** | **`true`** | **the condition the R7 reading rests on** |
| `supervised_raw_env` | `1` / `true` / `yes` | catches a typo like `ture`, which parses False |
| `review_endpoint` | `true` | `ADMIN_TOKEN` is set, so the queue is reachable |
| `review_queue.ok` | `true` | the store is readable |

> **`supervised: false` and `supervised: null` are DIFFERENT.** `false` means supervision is
> off. `null` means this endpoint could not determine it — which is not permission to assume
> either way. Do not let a single participant message the number until this reads `true`.
>
> **This check is first, not last, because a typo in `SUPERVISED` does not fail safe.** It
> silently sends unreviewed answers while the reviewer believes every reply is being read.

---

## 3. Clearing the queue

`https://<app>.modal.run/review?token=<ADMIN_TOKEN>` — one card per pending item, on a phone.

Each card shows the question, the **draft** (editable), the **engine's deterministic working**,
and the **facts retrieval actually served**. The evidence is on the card on purpose: a reviewer
shown only the Swahili prose is judging it against memory, which is how two adjudications went
wrong in one week by reading the gold instead of the served index.

Three buttons:

- **Send** — the draft is right. No reason needed; agreeing is the null decision.
- **Send edit** — edit the text, **give a reason**. The reason is required and enforced in
  `handler_core.apply_decision`, not in the page.
- **Withhold** — nothing is sent. **Reason required.**

**A decision is taken once.** A second decision on a sent item is refused rather than
overwritten — re-sending a compliance answer is worse than one missing answer.

### What the reason field is for

It is **the most valuable field the pilot produces.** The edits are labelled corrections on
real traffic, which is the one signal no sweep over our own corpora can manufacture — our
corpora share vocabulary and framing with our facts by construction. Write what was *wrong*,
not what you changed: "stated WCF on one employee's wage, not the whole payroll" beats "fixed
the base".

---

## 4. Reading the record

```bash
curl -s "https://<app>.modal.run/review_queue?token=<ADMIN_TOKEN>"   # no phone numbers
curl -s "https://<app>.modal.run/transcripts?token=<ADMIN_TOKEN>&n=200"
```

`draft`, `final` and `edit_reason` are three separate fields and are never collapsed. A reader
that ignores `supervision` will **over-count deliveries** — a held row carries the draft in
`reply` and was never sent.

`review_summary` reports `edit_or_withhold_rate` as **`None`** until at least one decision
exists. A `0.0` rate on an empty queue reads exactly like a perfect model; `None` cannot.

---

## 5. Privacy

The review queue is a **separate store** (`chike-review-queue-kv`) from transcripts, because
sending an approved answer needs the real phone number and the transcript store deliberately
keeps only a salted hash plus a 4-digit tail. Keeping both in one store would quietly
re-introduce reachable numbers into the corpus every analysis pass reads.

After each review session:

```bash
curl -s -X POST "https://<app>.modal.run/review_purge?token=<ADMIN_TOKEN>"
```

Drops the number from every **decided** item. Pending items are untouched — purging one makes
its answer undeliverable.

---

## 6. What participants must be told

Part of the R7 condition, not a courtesy: that this is a **supervised test**, that a person
reads every answer before it is sent, that answers may therefore take hours, and that
important answers should still be confirmed with TRA. If that disclosure is dropped, the R7
reading no longer applies.

---

## 7. Turning it off

Remove `SUPERVISED` from the secret (or set it to `0`), redeploy per §1, and **re-check
`/health` shows `supervised: false`**. Clear any pending items first — turning supervision off
does not send them, and nothing else will.

# Supervised pilot runbook

The R7 reading this operates under, and its condition, are in `CLAUDE.md` —
**"THE R7 READING ON A SUPERVISED COHORT"**. Read that first. Everything below is the
mechanics of keeping that condition true.

> **This file was written for a ONE-REVIEWER design and rewritten on 2026-10-10 for the
> roster.** The two places it was actively wrong are recorded rather than quietly fixed,
> because a stale runbook is the layer that decides what the next operator *believes* and
> this one was about to be followed into a misconfigured deploy:
>
> | §1 | said the only founder-only step was `SUPERVISED=1`. **`REVIEWER_ROSTER` and `REVIEW_SIGNING_KEY` did not exist when it was written.** Followed exactly, it produces a supervised deploy with an empty roster that notifies nobody |
> | §3 | said decisions are taken on `/review?token=<ADMIN_TOKEN>` with three buttons. **`/review` is now READ-ONLY.** Decisions are taken from a reviewer's own `/d` link, because an admin action would have to invent a reviewer identity |

---

## 0. Before anything: the throughput decision

`eval/results/review_throughput_estimate_2026_10_10.json`, asked and answered before
recruiting:

| cohort | questions/day | min/day to clear |
|---|---|---|
| 10 × 2 | 20 | **~21** |
| 5 × 2 | 10 | ~10 |
| **3 × 2** | 6 | **~6** |

**Ten users exceeds "a few minutes a day" by about four times — FOR ONE REVIEWER.** That is
what the roster changes: the table is a **total review load**, and the roster divides it, so
~21 min/day across three reviewers is ~7 each. Capacity scales with reviewers, not with how
fast one person reads.

**Two things the division does not buy.** *Coverage is not capacity* — three reviewers asleep
at the same hour are one reviewer, which is why every reviewer is notified rather than one
being assigned, and why the claim lock is what makes that safe. And *a pooled edit rate hides
a weak reviewer* — read `per_reviewer`, never only the total (§5).

Reducing review *depth* is never the lever. Skimming is the rubber-stamping the condition
exists to prevent, and it is on the void list.

---

## 1. Deploy (R16b applies in full — warm containers serve OLD code)

### 1a. What has to be in place first

| value | where it goes | who | if missing |
|---|---|---|---|
| `SUPERVISED=1` | **Secret** (or deploy env) | founder | **answers send unreviewed.** The one failure that voids the R7 reading |
| `REVIEWER_ROSTER` | **Secret** | founder | drafts HOLD and notify nobody — safe, silent |
| `REVIEW_SIGNING_KEY` | **Secret** | founder | **every link forgeable, none authenticating.** Fails closed |
| `REVIEW_D_URL`, `REVIEW_CLAIM_URL`, `REVIEW_ACT_URL` | deploy env | either | **all three or none**: Modal serves each endpoint on its own hostname (`<ws>--chike-whatsapp-<function>.modal.run`), there is no shared base. Unset -> no link issued, drafts HOLD. Take them from the first deploy's output |
| `COHORT_SIZE`, `CLAIM_TTL_S`, `RENOTIFY_AFTER_S` | deploy env | either | defaults: 0 (monitor-only), 900s, 1800s |

`REVIEWER_ROSTER` is `+255 754 123 456:Asha, 0712 345 678:Juma` — comma- or
semicolon-separated, `number:name`, name optional (defaults to the last 4 digits). Numbers are written the way a person writes them (`+255…`, `0…`, spaces and dashes fine) and are normalised to WhatsApp ID form (`255…@s.whatsapp.net`); fewer than 9 digits is dropped. Duplicate
numbers keep the first name; an entry with no number is dropped, because a nameless blank
would become a seat that can never be notified and never acts, quietly lowering capacity.

> **⛔⛔ THE ROSTER AND THE SIGNING KEY BELONG IN THE SECRET, NOT IN CODE OR IN THE DEPLOY
> COMMAND.** The roster decides **who may approve a compliance answer a Tanzanian employer
> will act on**, and the signing key is the only thing making an approval link unforgeable.
> A Secret value **overrides** the image env, so a deploy-time value cannot silently shadow
> the real one. They are readable at deploy time only so a throwaway verification app can be
> given a test roster without writing to the production secret (§7).

> **⛔ `SUPERVISED=1 modal deploy ...` SETS NOTHING BY ITSELF — AND USED TO BE THE DOCUMENTED
> INSTRUCTION HERE.** Modal does not forward the deploying shell's environment. Until
> 2026-10-10 that command would have set nothing inside the container: the founder could have
> followed this file exactly, watched the deploy succeed, and had an **unsupervised pilot**,
> with `/health` the only thing that would have said so. Same shape as R16's warm container —
> the deploy reports success and the thing you changed is not running. The tunables are now
> baked into the image at deploy time, exactly as `CHIKE_BUILD` already was, which is why the
> command below works and why §2 is non-negotiable.

### 1b. The deploy

```bash
python scripts/preflight_deploy.py chike-whatsapp/modal_whatsapp.py   # must exit 0 FIRST
python -m modal app stop chike-whatsapp --yes
CHIKE_BUILD=$(git rev-parse --short HEAD) \
  PUBLIC_BASE_URL=https://<workspace>--chike-whatsapp \
  COHORT_SIZE=3 CLAIM_TTL_S=900 RENOTIFY_AFTER_S=1800 \
  PYTHONIOENCODING=utf-8 PYTHONUTF8=1 \
  python -m modal deploy chike-whatsapp/modal_whatsapp.py
```

The pre-flight comes **before** the stop, not after: the stop is instant and irreversible and
the deploy is neither. Three times a pre-flight has earned its place — twice on build failures
nobody had enumerated, once by refusing a deploy whose commit was still local-only.

⚠️ **The endpoint URLs are per-function, not per-app.** Deploy once WITHOUT the three review URLs (safe: no link is issued, drafts hold), copy the `d`, `review_claim` and `review_act` URLs from the deploy output, then redeploy with them set and confirm `roster.can_issue_links` in §2.

---

## 2. ⛔ STEP ONE AFTER EVERY DEPLOY — verify supervision is ON

```bash
curl -s "https://<workspace>--chike-whatsapp-health.modal.run" | python -m json.tool
```

Check, in this order:

| field | required | why |
|---|---|---|
| `build` | the SHA you just pushed | R16: a warm container will happily serve old code |
| **`supervised`** | **`true`** | **the condition the R7 reading rests on** |
| `supervised_raw_env` | `1` / `true` / `yes` | catches a typo like `ture`, which parses False |
| `secret_keys_missing` | `[]` | names the missing key, so a misspelling is caught by name |
| **`roster.reviewers`** | **≥ 2** | the claim lock is a claim about two reviewers |
| `roster.names` | the people you expect | a wrong number is a seat nobody holds |
| `roster.signing_key_set` | `true` | **false means every link is forgeable** |
| `roster.public_base_url_set` | `true` | false means links are unusable in WhatsApp |
| **`roster.can_issue_links`** | **`true`** | the one line that says review can happen at all |
| `cohort.cohort_size` / `participants_seen` | as declared / as expected | monitors, does not gate |
| `review_queue.ok` | `true` | the store is readable |

> **`supervised: false` and `supervised: null` are DIFFERENT.** `false` means supervision is
> off. `null` means this endpoint could not determine it — which is not permission to assume
> either way. Do not let a single participant message the number until this reads `true`.
>
> **This check is first, not last, because a typo in `SUPERVISED` does not fail safe.** It
> silently sends unreviewed answers while the reviewer believes every reply is being read.
>
> **`can_issue_links: false` fails in the SAFE direction and is therefore silent.** Drafts
> hold, nothing is sent, nothing is lost — and no reviewer is ever notified, so the pilot
> looks dead rather than broken. Only `/health` and the function logs say which.

`roster.reviewer_ids` are handles, not numbers — a reviewer can confirm their own link
belongs to them without anyone's phone number being published by an endpoint.

---

## 3. How a review actually happens

**The push comes to the reviewer; the reviewer does not check a queue.** The moment a draft
is ready, every reviewer on the roster gets a WhatsApp message carrying the question, the
**draft in full**, the **engine's deterministic working** (or an explicit note that there is
none, so "no arithmetic to check" is never confused with "arithmetic omitted"), the **count**
of facts served, any fallback/error flag, and their own link.

The draft is in the message rather than behind the link on purpose: a notification that only
says "a draft is waiting" makes the reviewer open a page before they know whether they can
act now — which on a bad connection means they do not, and the draft waits for the next
person. Median reply is 197 characters.

Opening the link shows the same thing plus the facts **in full**, and **claims the draft**.

| action | reason | effect |
|---|---|---|
| **Tuma** (send) | not required — agreeing is the null decision | the draft is sent verbatim |
| **Hariri na tuma** (send edit) | **required** | your text is sent; `draft`, `final` and `edit_reason` are all kept |
| **Zuia** (withhold) | **required** | nothing is sent, ever |

**A decision is taken once.** A second decision on a decided item is refused rather than
overwritten — re-sending a compliance answer is worse than one missing answer.

### The claim lock

Opening a draft locks it to you. A second reviewer opening the same draft is told it is held,
and **cannot act on it** — the refusal is enforced in `handler_core.apply_decision`, not at
the endpoint, so the next caller (a sweeper, a backfill, a test) cannot bypass it.

- The lock is **per-draft, not a global mutex**: another reviewer can work the next draft.
- Re-opening **your own** claim is not a conflict.
- An unacted claim **releases back to the roster** after `CLAIM_TTL_S` (default 15 min), and
  the release is **recorded** — a draft handed back is visible, not silent.
- An unclaimed draft is **re-notified** after `RENOTIFY_AFTER_S` (default 30 min).

> **⛔⛔ A TIMED-OUT DRAFT HOLDS. IT NEVER SENDS.** `sweep_review_queue` can only release a
> claim and re-notify; `tests/test_review_roster.py` parses its AST and fails if it so much
> as *reads* `item["sender"]`, `item["final"]` or `item["draft"]`, or calls `_send_once`. A
> behavioural test can only show that today's sweeper does not send — this shows there is no
> code in it that **could**.
>
> **"Send after N minutes if nobody objects" is the single change that would void the R7
> reading, and it is exactly the change that looks reasonable at 2am when a queue has backed
> up.** It is on the void list and ruled out by construction.

### Why links and not an admin page

`/review?token=<ADMIN_TOKEN>` is the **read-only** overview — the whole queue on one page, no
buttons. An admin action would have to invent a reviewer identity, and **a fake name in the
attribution column is worse than no column.**

Links carry a reviewer **handle**, never a phone number, and the token is HMAC-bound to
**both** the draft and the reviewer, so a forwarded link cannot be replayed as someone else.
That is what keeps attribution honest.

> **⚠️ CLAIMING IS A POST FIRED BY THE PAGE'S JAVASCRIPT, NEVER A GET — because WhatsApp
> fetches a link to render its preview card.** A GET that claimed would fire the instant the
> notification was *delivered*, locking every draft to whichever reviewer's client previewed
> it first, someone who has read nothing. Crawlers do not run JS.

---

## 4. ⛔ Before adding anyone to the roster: the review standard

**A seat on the roster is authority to approve a compliance answer a Tanzanian employer will
act on.** Adding a reviewer without telling them this is on the void list, and it is worse
than an unreviewed reply — because the record then says the reply *was* checked.

A reviewer must be told, before their number goes in the Secret:

1. **Nothing sends until you press a button.** If you do nothing, nothing happens — the draft
   waits and you get reminded. **Holding is always safe. Guessing is not.**
2. **Check the draft against the evidence on the card, not against memory.** The engine's
   working and the served facts are on the page for this reason: two adjudications went wrong
   in one week by reading the gold answer instead of the served index.
3. **Withhold when unsure.** A missing answer costs one delay. A confident wrong compliance
   answer is the thing R7 exists to prevent, and it is what the participant will act on.
4. **The reason field is the most valuable output of the pilot** (§5). Write what was
   *wrong*, not what you changed.
5. **The gates have not passed.** Gate 1 is at 80.2–81.9% against its 85% line; Gate 2 is
   unsolved. You are the gate. Expect roughly **1 draft in 6** to need an edit — and that
   figure is a lower bound, measured on our own corpora.
6. **Your name is on every action you take** — draft, edit and final. This is so corrections
   read separately, not to grade you; but it does mean a rubber-stamp is attributable.

---

## 5. Reading the record

```bash
curl -s "https://<workspace>--chike-whatsapp-review_queue.modal.run?token=<ADMIN_TOKEN>"
curl -s "https://<workspace>--chike-whatsapp-transcripts.modal.run?token=<ADMIN_TOKEN>&n=200"
```

`draft`, `final` and `edit_reason` are three separate fields and are never collapsed. A reader
that ignores `supervision` will **over-count deliveries** — a held row carries the draft in
`reply` and was never sent.

`review_summary` reports `edit_or_withhold_rate` as **`None`** until at least one decision
exists. A `0.0` rate on an empty queue reads exactly like a perfect model; `None` cannot.

**`per_reviewer` is not a convenience — read it before the total.** A reviewer whose edit rate
is far *below* the others may not be faster; they may be approving what the others would have
caught. The pooled figure cannot show that, and a weak reviewer is the failure mode a roster
introduces that a single reviewer does not have.

**`median_decision_latency_s` is the number to watch in week one.** A supervised answer cannot
arrive faster than the reviewer, so a 9pm question waits until morning — and a user who waits
twelve hours for their first answer may simply stop asking. The transcripts would then
**under-report demand rather than reveal it**, which is a measurement defect in the pilot's own
instrumentation, not a product result. Measure it; do not assume it.

### What the reason field is for

It is **the most valuable field the pilot produces.** The edits are labelled corrections on
real traffic, which is the one signal no sweep over our own corpora can manufacture — our
corpora share vocabulary and framing with our facts by construction. Write what was *wrong*,
not what you changed: "stated WCF on one employee's wage, not the whole payroll" beats "fixed
the base".

---

## 6. Privacy

The review queue is a **separate store** (`chike-review-queue-kv`) from transcripts, because
sending an approved answer needs the real phone number and the transcript store deliberately
keeps only a salted hash plus a 4-digit tail. Keeping both in one store would quietly
re-introduce reachable numbers into the corpus every analysis pass reads.

After each review session:

```bash
curl -s -X POST "https://<workspace>--chike-whatsapp-review_purge.modal.run?token=<ADMIN_TOKEN>"
```

Drops the number from every **decided** item. Pending items are untouched — purging one makes
its answer undeliverable.

---

## 7. Verifying the roster live — before any participant

The offline suite proves the pure logic. It cannot prove the **deployed** app wires it: two
inert controls in this project had perfect logic and were reached by nothing.

```bash
python eval/controls/verify_review_roster_live_2026_10_10.py \
  --base https://<workspace>--chike-whatsapp \
  --key <REVIEW_SIGNING_KEY> --r1 <number1> --r2 <number2> --claim-ttl 900
```

Verifies the four things named as the bar: two reviewers with two drafts at once, the claim
lock holding, a timed-out claim releasing, and an unreviewed draft never sending — plus a
**positive limb** (a real decision, attributed), because a run showing only refusals would
equally describe a system that refuses everything.

Drafts are seeded through a **Modal function**, not a web endpoint, so there is no public
route that can put a draft in the queue; each uses a documented unroutable test number, and
the test asserts the send was never **attempted**. Exit 0 all four verified · 1 a finding ·
**2 could not be exercised, which is NOT a pass.**

⚠️ It does **not** verify that a notification arrives on a handset. That needs a real number
on the roster and is reported, not asserted.

⚠️ It seeds `TEST-*` rows into the shared review queue. Purge or leave them withheld; never
leave one pending, or the sweeper will re-notify the roster about a test draft forever.

**To verify without touching production**, deploy the same file under a throwaway name with a
test roster in the deploy env (the Secret overrides it, so this only works for keys the Secret
does not hold):

```bash
REVIEWER_ROSTER='+255700000001:TestA,+255700000002:TestB' REVIEW_SIGNING_KEY=<test-key> \
  SUPERVISED=1 CLAIM_TTL_S=60 PUBLIC_BASE_URL=https://<workspace>--chike-whatsapp-verify \
  python -m modal deploy --name chike-whatsapp-verify chike-whatsapp/modal_whatsapp.py
# ... run the harness against it ...
python -m modal app stop chike-whatsapp-verify --yes
```

---

## 8. What participants must be told

Part of the R7 condition, not a courtesy: that this is a **supervised test**, that a person
reads every answer before it is sent, that answers may therefore take hours, and that
important answers should still be confirmed with TRA. If that disclosure is dropped, the R7
reading no longer applies.

---

## 9. Turning it off

Remove `SUPERVISED` from the secret (or set it to `0`), redeploy per §1, and **re-check
`/health` shows `supervised: false`**. Clear any pending items first — turning supervision off
does not send them, and nothing else will.

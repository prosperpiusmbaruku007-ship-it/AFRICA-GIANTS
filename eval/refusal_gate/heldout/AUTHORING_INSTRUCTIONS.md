# The frozen held-out OUT-OF-SCOPE set for Gate 2 — instructions for the person who writes it

**Why this exists, in three sentences.** Every refusal list and every refusal test this project has ever built was written by the same people who wrote the facts, so it shares their
words. The same cue list refused **1.9%** of 411 questions drawn from our own corpus and **71%** of 21 questions written fresh by someone else (a ~37× gap), and 42 of 42 out-of-scope
questions phrased in ordinary words instead of the listed term slipped past it. **A refusal measure is only worth anything if the questions come from someone who has never seen
the cue list — and that person cannot be the assistant that built it.**

**Who may write it:** the founder, or a pilot participant, or any other person who is not the assistant and has not read `kaggle/chike_config.json`'s `ooc_phrases`. You may write it
alone or with others; record who in the file (`authored_by`). **The assistant will not write, edit, reword, "tidy", translate or add to a single question.** It will only validate the
file's shape and freeze it.

## What CHIKE covers (so you know what is *not* covered)
CHIKE answers Tanzanian **Mainland** compliance questions about: BRELA (company/business-name registration and fees, annual returns), TRA taxes it covers (VAT, PAYE, SDL,
presumptive tax, corporate tax basics, withholding tax on rent, dividends, professional fees, EFD receipts, TIN), NSSF, WCF, OSHA registration, employment law basics (notice,
severance, leave, overtime, minimum wage GN 605A), and the non-citizen business restriction GN 487A. Everything else is **out of scope** and the correct behaviour is to say it is
outside what CHIKE covers and point to the right authority, not to guess. Examples of *areas* (not questions — do not copy these): import duty and customs, capital gains, transfer pricing,
stamp duty, property tax, Zanzibar taxes, mining royalties, land, immigration/visas, criminal or family law, banking and loans, insurance products, school fees, health, farming subsidies,
other countries' taxes — and anything else you can think of that a trader in Tanzania might plausibly ask a WhatsApp assistant.

## How to write the questions
1. **Your own words, your own spelling, the way you or your customers would actually type it on a phone at 9 pm.** Mixed Swahili/English is good. Misspellings are good. Short, rude,
   run-on, half-formed questions are good. If a question sounds like a textbook, it is the wrong kind.
2. **Do not look at the questions in `eval/`, the cue lists, or any CHIKE answers while writing.** Do not test your questions on CHIKE first. (If you did, say so in `seen_system_output`
   — the set is then weaker, and that must be recorded, not hidden.)
3. **Two kinds of rows, both required** (`limb`):
   * `ooc` — an out-of-scope question; the right behaviour is a refusal / "not covered, confirm with the authority".
   * `control` — an **in-scope** question that deliberately uses words that also appear in out-of-scope questions (e.g. a covered tax question that mentions a loan, a building, a
     foreign company, a share). The right behaviour is to ANSWER. These measure the cost of over-refusing a real user, which is the expensive direction.
4. **Vary how it is out of scope** (`axis`): a topic nobody listed (`unlisted_topic`); a listed topic asked in ordinary words (`plain_words`); a covered topic with an out-of-scope twist
   (`mixed`); a question that is simply about someone else's country or another tax year (`other_jurisdiction`); something that is not compliance at all (`not_compliance`).
5. **Do not write the expected answer.** Only say what the right *behaviour* is (`expect`: `REFUSE` or `ANSWER`). Anyone who writes an answer key invents facts (this project's worst
   defects were uncited keys).

## Size
At least **60 `ooc` rows** and **30 `control` rows**, at least **8 per `axis`** among the `ooc` rows, and at most **3 rows from any one topic** (so one clever theme cannot carry the set).

## The file
`eval/refusal_gate/heldout/heldout_outofscope_AUTHORED.jsonl`, one JSON object per line, copied from `heldout_outofscope_TEMPLATE.jsonl`:

| field | value |
|---|---|
| `id` | `ho_001`, `ho_002`, … |
| `limb` | `ooc` or `control` |
| `axis` | one of `unlisted_topic`, `plain_words`, `mixed`, `other_jurisdiction`, `not_compliance` (controls use `control`) |
| `question` | the question, exactly as typed |
| `expect` | `REFUSE` (for `ooc`) or `ANSWER` (for `control`) |
| `topic` | one or two words naming the subject (used only to cap one theme at 3 rows) |
| `authored_by` | `founder`, `pilot_participant` or `other_person` — **never** `assistant` |
| `author_note` | optional: who/where, e.g. "customer at Tunduma" — no names or phone numbers |
| `seen_system_output` | `false` if you wrote it without seeing any CHIKE reply or cue list; `true` if not |

## Freezing, and what "frozen" costs
When you hand the file over, the assistant runs `python eval/refusal_gate/validate_heldout_set.py --freeze`, which checks the shape, writes `FROZEN.json` (sha256 of the file, the date,
the validator's own sha) and **commits the file and the freeze record on their own, before anything is measured.** After that:
* the file may **never be edited** — a test fails if its bytes differ from `FROZEN.json`;
* it is **burned once its results are read**: reading the failures is what turns every later rule into a fit to this set, so a second iteration of any refusal or hedging mechanism needs
  a **new** set from a new author, not an edited old one;
* the first measurement is the full production path (classifier + retrieval + model), reported as: leak rate (OOC not intercepted by the classifier), model refusal rate on the leaks,
  and wrongful-refusal rate on the controls — separately, never blended.

# Modal Dict retention, and the durable archive (decided 2026-11-26)

## Finding (official docs, read 2026-11-26)
Modal docs, <https://modal.com/docs/guide/dicts> and <https://modal.com/docs/reference/modal.Dict>:

- *"Each object in the Dict will expire after 7 days of inactivity (no reads or writes)."* A read resets the clock (the docs say "no reads or writes").
- Per-object limit 100 MiB; no total-storage or key-count limit stated; `len()` caps at 100,000. Entries are "written to durable storage" but no formal durability guarantee is stated.
- Dicts created before 2025-05-20 expire 30 days after last write. All ours are newer.

## Stores at risk (before this decision)
| store | held | alive today only because |
|---|---|---|
| `chike-transcripts-kv` | the analysis corpus | `/health` runs `_cohort_health`, which reads every row |
| `chike-review-queue-kv` | draft / final / edit_reason (the labelled corrections) | the 1-minute sweeper reads every item |
| `chike-bridge-auth-kv` | the WhatsApp login (Baileys creds and keys) | the connected bridge writes keys; a bridge outage over 7 days could expire the login and force a QR re-pair |
| `chike-disclosures-kv`, `chike-autosend-kv` | first-contact flag, send-once claims | low risk |

Nothing guaranteed any of these. They survived by the side effects of other code, which a quiet week or a change like finding F (stop scanning decided items) would remove.

## Decision (founder, 2026-11-26): the Dicts stay the hot store, plus ONE single-writer daily archiver to a Volume
A Volume is NOT safe for concurrent per-row writes: the 2026-08-14 incident lost rows to `commit()` clobbering (see the module docstring in `modal_whatsapp.py`). It is safe with exactly one writer, so:

1. **Single writer.** One scheduled function, behind an atomic lock (`put(skip_if_exists)`, the sweep-lock pattern). `reload()` before, `commit()` after.
2. **One file per record, write-once**, laid out per sender so deletion is a directory removal:
   `archive/<kind>/<sender_hash>/<record id>.json`, `kind` in `review | transcript`. The sender hash is the existing salted pseudonym; no phone number is ever written.
3. **Aggregates** (text-free): `archive/aggregates/<YYYY-MM-DD>.json` (counts per route / decision / reviewer). They survive deletion of any sender.
4. **FUTA (per-sender deletion) deletes from BOTH stores**: Dict rows and the sender's archive directory, and records a text-free tombstone (salted sender hash + date) so an archiver run that had already read a row cannot re-write it. Tombstones are dropped after 90 days.
5. **Item F: move before remove.** A decided review item leaves the hot Dict only after its archive file exists and is read back byte-identical. Never the other order.
6. **Auth keep-alive.** The same run reads (`get`) every key of `chike-bridge-auth-kv` daily, so a long bridge outage cannot expire the login. Verified from the docs quote above that a read resets the 7-day clock. Not verifiable by experiment inside a day, so recorded as docs-sourced.
7. **Dead-man check.** A healthchecks.io check (period 1 day, grace 6 h) pinged on a successful run, `/fail` on error. `/health` reports `archive.last_ok_age_s` and whether the check URL is configured. **Founder step:** create the check and add `HEALTHCHECK_ARCHIVE_URL` to the `chike-whatsapp` Secret; until then `/health` says `dead_man_configured: false` and the archiver still runs.

## Not decided here
- An external database: revisit at wave 3 (50+ participants). It adds a secret, hosting of personal data and latency from Tanzania.
- `/health`'s whole-store transcript scan (`_cohort_health`) is also O(rows). Proposed follow-up: a participants index written at row-write time.

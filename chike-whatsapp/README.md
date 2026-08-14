# Chike — WhatsApp front door (Modal app `chike-whatsapp`)

Receives WhatsApp messages from Wappfly, calls `chike-inference`, sends the reply back.
Replaces the Railway-hosted `wappfly-function/` (trial ended 2026-08-14).

```
Wappfly ──POST──▶ webhook (CPU, returns 200 in ms)
                     └── .spawn() ──▶ answer_and_send (CPU)
                                        ├── ChikeModel().run.remote.aio()  [chike-inference, T4]
                                        ├── Wappfly send (+1 retry)
                                        └── one transcript file on the volume
```

## Two files, on purpose

- **`handler_core.py`** — all conversation logic. No Modal import, no network. `deliver()`
  takes `ask` and `send_once` as injected coroutines, so every failure is forced in a test.
- **`modal_whatsapp.py`** — the Modal wrapper: real `ask` (cross-app call), real `send`
  (httpx), transcript persistence, and the four endpoints.

The split is why the move from Railway to Modal did not re-derive the delivery guarantees.
The platform changed; `deliver()` did not.

## The guarantee

Every inbound message ends in **either an answer or `FALLBACK`** — never silence — and
produces exactly one transcript row. `deliver()` cannot raise.

`error_class` ∈ `timeout` · `model_error` · `bad_response` · `no_reply_field` · `handler_bug`.
Railway's `transport` and `http_status` are **gone as classes**: there is no longer a network
hop or a token gate between handler and model.

## Three Modal-specific rules, each with a reason that bites silently

1. **Separate app from `chike-inference`.** R16 requires `modal app stop chike-inference
   --yes` before a model redeploy; a shared app would take the WhatsApp front door down with
   every model deploy.
2. **`.spawn()`, never `asyncio.create_task`.** Modal's autoscaler tracks in-flight inputs —
   once `webhook` returns its 200, a detached coroutine holding a 240s answer is invisible to
   the scheduler and can be reclaimed. `.spawn()` makes Modal responsible for the job.
3. **One file per transcript row.** Modal Volumes are not a POSIX shared filesystem; two
   containers appending to one JSONL do not interleave and the loser's row is gone.

`retries=0` on the spawned jobs is deliberate: a retry re-runs the GPU call and could deliver
a **second answer to the same question**. Duplicate compliance answers are worse than one
missing answer, and the transcript records the failure either way.

## Secret `chike-whatsapp`

| key | required | purpose |
|---|---|---|
| `WAPPFLY_TOKEN` | **yes** | `X-API-Token` for the outbound send |
| `WEBHOOK_TOKEN` | recommended | when set, `?token=` is required on `/webhook`. Unset = open (the old Railway behaviour), logged loudly |
| `ADMIN_TOKEN` | recommended | when unset, `GET /transcripts` returns nothing |
| `SENDER_SALT` | recommended | salt for the pseudonymous `sender_hash` |
| `MODEL_TIMEOUT_S` | no (240) | raised from Railway's 180; cold starts measured 64–216s |
| `SLOW_ACK_AFTER_S` | no (12) | "preparing an answer" on slow paths; `0` disables |
| `COLD_START_SUSPECTED_S` | no (30) | threshold for the transcript's cold-start **proxy** |
| `SEND_ATTEMPTS` | no (2) | one retry on a failed send |

## Endpoints

- `POST /webhook?token=` — Wappfly delivery. Always returns 200 (no dedupe on redelivery yet,
  so an error Wappfly might retry would mean a duplicate answer).
- `GET /health` — `build` (git SHA baked at deploy), timeouts, and transcript store status.
- `GET /transcripts?token=<ADMIN_TOKEN>&n=50`.

## Deploy (R16b)

```
python -m modal app stop chike-whatsapp --yes
CHIKE_BUILD=$(git rev-parse --short HEAD) PYTHONIOENCODING=utf-8 PYTHONUTF8=1 \
  python -m modal deploy chike-whatsapp/modal_whatsapp.py
```

Then confirm `/health.build` matches the commit, force a failure, and check a negative case.
"✓ App deployed" proves nothing.

## Cost

`min_containers=0` with a 20-minute CPU scaledown ≈ **$0.10/mo**; always-warm would be
**$5.68/mo**. Buy warmth only if transcripts show Wappfly retrying on slow webhook delivery —
the same discipline as holding the GPU scaledown at 300. Volume storage is free at this scale
(1 TiB/mo included).

## Tests

    python -m pytest tests/test_whatsapp_handler.py     # 34 tests, ~8s

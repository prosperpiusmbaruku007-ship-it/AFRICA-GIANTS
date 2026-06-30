# Runbook — WhatsApp Cutover to Modal

**Purpose:** Complete, verify, and (if needed) roll back the migration of Chike's
inference backend from Cerebrium to Modal.

**Status as of cutover commit `041ad69`:**
- `wappfly-function/handler.py` now calls the **Modal** endpoint with `?token=` proxy-auth.
- `chike-inference/modal_app.py` is deployed (query-param token gate, 401 on bad/missing token).
- Code + local test validated. **Two manual Railway steps below are still required to go live.**

> ⚠️ This migration is **infrastructure/cost only**. It does NOT change answer quality.
> Adapter v8 still returns the same wrong SDL/WCF/NSSF/GN487A answers on Modal as on Cerebrium.

---

## 1. Complete the cutover — Railway env-var steps

The handler runs on **Railway** (auto-detected FastAPI). It reads two env vars:
`WAPPFLY_TOKEN` (unchanged) and `MODAL_API_TOKEN` (new — gates the Modal endpoint).

**Without `MODAL_API_TOKEN` set, the handler sends an empty token → Modal returns 401
→ every WhatsApp reply becomes the FALLBACK message.** This is the gating step.

### Steps
1. Open the Railway project → the `wappfly-function` service → **Variables**.
2. **Add a new variable:**
   - Name: `MODAL_API_TOKEN`
   - Value: the token stored locally at `C:\Users\jhjh\.chike_modal_token.txt`
     (this file is intentionally outside the repo; it is the same value used when the
     Modal secret `modal-api-token` was created).
3. **Remove the now-unused variable** (optional but recommended to avoid confusion):
   - `CEREBRIUM_KEY` — no longer referenced by the handler.
4. **Confirm Railway redeployed** from commit `041ad69`:
   - If the GitHub integration is enabled, the push already triggered a deploy.
   - Otherwise: Railway dashboard → **Deployments** → **Deploy** (or trigger from the latest commit).
   - Adding/changing a variable also triggers a redeploy on most Railway setups.

> Keep `WAPPFLY_TOKEN` exactly as-is — it authenticates the outbound send to Wappfly, unrelated to Modal.

---

## 2. Verify it is working

1. **Health check (no model needed):**
   `GET https://<your-railway-domain>/health` → should return
   `{"status":"ok","product":"Chike by Africa Giants", ...}`.
2. **Send a real WhatsApp message** to the Chike number (use a real question, not a greeting —
   greetings short-circuit to the WELCOME message and never hit Modal):
   - Example: `NSSF inalipwa tarehe gani hasa?`
3. **What to expect:**
   - **First message after idle:** reply takes **~1–2 minutes** (Modal cold start ~86–216s).
     The handler timeout is 180s, so a cold start may occasionally still FALLBACK once —
     send a second message and it will be warm.
   - **Warm messages:** reply in **~8–15s**.
   - **A real answer comes back** (not the FALLBACK "Samahani, Chike hakuweza..." text).
     ⚠️ The *content* will still be the wrong v8 output — that is expected and is a separate
     training-data issue. The point of this verification is only that Modal is reached and authed.
4. **If every reply is FALLBACK:** `MODAL_API_TOKEN` is missing/wrong in Railway, OR Railway
   has not redeployed. Re-check Section 1.

---

## 3. Rollback to Cerebrium (if Modal has problems)

The previous Cerebrium handler is in git at `041ad69~1`. You can either revert the whole file
or apply the **3 targeted changes** below to `wappfly-function/handler.py`.

### Fastest full revert
```bash
git checkout 041ad69~1 -- wappfly-function/handler.py
git commit -m "rollback: revert WhatsApp handler to Cerebrium endpoint"
git push
```

### Or the exact 3-line manual change (Modal → Cerebrium)

**a. Config lines (top of file)** — replace the Modal lines with Cerebrium:
```python
# FROM (Modal):
MODAL_API_TOKEN  = os.environ.get("MODAL_API_TOKEN", "")
MODAL_URL        = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"

# TO (Cerebrium):
CEREBRIUM_KEY    = os.environ.get("CEREBRIUM_KEY", "")
CEREBRIUM_URL    = "https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run"
```

**b. The call function** — auth header + parsing:
```python
# FROM (Modal — query-param token, parse result["reply"]):
async def call_modal(message: str) -> str:
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            MODAL_URL,
            params={"token": MODAL_API_TOKEN},
            headers={"Content-Type": "application/json"},
            json={"message": message},
        )
        result = response.json()
        return result.get("reply", FALLBACK)

# TO (Cerebrium — Bearer header, parse result["result"]["reply"]):
async def call_cerebrium(message: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            CEREBRIUM_URL,
            headers={
                "Authorization": f"Bearer {CEREBRIUM_KEY}",
                "Content-Type": "application/json",
            },
            json={"message": message},
        )
        result = response.json()
        return result.get("result", {}).get("reply", FALLBACK)
```

**c. The caller inside `respond()`**:
```python
# FROM:  reply = await call_modal(text)
# TO:    reply = await call_cerebrium(text)
```

**After rollback in Railway:** ensure `CEREBRIUM_KEY` is set (re-add it if it was removed in
Section 1). `MODAL_API_TOKEN` can stay or be removed — Cerebrium ignores it.

---

## 4. Dashboards & logs

### Modal
- **Dashboard:** https://modal.com/apps — app name `chike-inference`.
- **Cold-start / inference logs:** open the `chike-inference` app → the `ChikeModel` class
  and the `web_endpoint` function → **Logs** tab. Look for these `print` markers:
  - `[chike] HuggingFace authenticated`
  - `[rag] loaded N pre-computed embeddings from repo`
  - `[chike] Model loaded in 4bit -- ready` (or `float16 -- ready` on fallback)
  - `[chike] volume committed -- caches persisted` (first cold start populates the volume;
    later cold starts are faster)
  - `[rag] injected N facts for: ...` and `[chike] Q: ... / A: ...` per request
- **Secrets:** https://modal.com/secrets — `huggingface-secret` (HF_TOKEN) and
  `modal-api-token` (MODAL_API_TOKEN) must both exist.
- **Endpoint URL:** `https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run`
  (POST, requires `?token=<MODAL_API_TOKEN>`).

### Cerebrium (reference, for rollback only)
- **Dashboard:** https://dashboard.cerebrium.ai — project `p-e3f41403`, app `chike-inference`.
- **Endpoint:** `https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run`
  (POST, `Authorization: Bearer <CEREBRIUM_KEY>`).

### Railway (the handler)
- **Dashboard:** https://railway.app/dashboard → `wappfly-function` service.
- **Logs:** Deployments → latest → **View Logs**. Handler markers:
  `[chike] From: <jid> — <text>` per inbound message; `[webhook] Error: ...` on failures.

---

## Quick reference

| Item | Value |
|---|---|
| Modal endpoint | `https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run` |
| Modal auth | `?token=` query param = `MODAL_API_TOKEN` |
| Token value (local) | `C:\Users\jhjh\.chike_modal_token.txt` |
| Cutover commit | `041ad69` |
| Rollback target | `041ad69~1` (Cerebrium handler) |
| Cerebrium endpoint | `https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run` |
| Handler timeout | 180s (Modal) / 120s (Cerebrium) |
| Warm latency | ~8–15s · Cold start ~86–216s |

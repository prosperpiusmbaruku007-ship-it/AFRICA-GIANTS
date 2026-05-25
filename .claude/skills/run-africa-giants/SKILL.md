---
name: run-africa-giants
description: Run, smoke-test, or screenshot the AFRICA-GIANTS FastAPI inference server. Use when asked to start, launch, serve, smoke-test, or verify the inference API locally. Drives the server end-to-end with python .claude/skills/run-africa-giants/driver.py (mock mode — no model weights or HF token needed). Also documents the python run.py CLI entry points (scrape, train, build-rag, evaluate, smoke, deploy) and the Kaggle-bound training path.
---

# Run AFRICA-GIANTS

AFRICA-GIANTS is a Python pipeline: scrape → clean → synth Q&A → upload to HF → fine-tune QLoRA on Kaggle GPU → eval gate → serve via FastAPI (`/v1/chat/completions`, `/rag-chat`, `/feedback`, `/v1/reload`, `/metrics`). Training runs on Kaggle (T4 x2), not locally. Local interaction = the FastAPI serve layer.

Agent entry point: **`python .claude/skills/run-africa-giants/driver.py`** — boots the server in mock mode, polls `/health`, hits every endpoint, prints PASS/FAIL, shuts down. All paths in this doc are relative to the repo root (`C:\Users\jhjh\AFRICA-GIANTS`).

## Prerequisites

Python 3.11 with the deps in `requirements.txt`. Verified importable in this env:

```powershell
python -c "import fastapi, uvicorn, requests, transformers, torch, yaml, dotenv; print('ok')"
```

If the import fails: `pip install -r requirements.txt`. `faiss-cpu` and `sentence-transformers` are pulled too but not required for the smoke path — the RAG store is a local JSON file (`data/processed/rag_index.json`) with 28 chunks already indexed.

## Run (agent path) — smoke the server

The driver launches `python run.py serve`, waits ready, hits 5 endpoints, shuts down. Mock mode (`AFRICA_GIANTS_MOCK=1`) returns canned generation answers but real RAG retrieval against the local vector store.

```powershell
python .claude\skills\run-africa-giants\driver.py --port 8766
```

Expected output:

```
Launching: ...python.exe run.py serve --port 8766 --host 127.0.0.1  (AFRICA_GIANTS_MOCK=1)

Driving server at http://127.0.0.1:8766
  [PASS] GET /health -- {'status': 'healthy', 'model': 'MOCK-...', 'mock_mode': True, 'rag_chunks': 28}
  [PASS] POST /v1/chat/completions -- [MOCK] Choose a business structure, register with BRELA, ...
  [PASS] POST /rag-chat -- 3 sources
  [PASS] POST /feedback
  [PASS] GET /metrics -- 5 events

SUMMARY: all endpoints OK
```

Exit code 0 = all endpoints OK, 1 = any failure. Add `--keep-running` to leave the server up for manual `curl` after checks pass (Ctrl-C to stop).

### Manual `curl` against a running server

If you used `--keep-running` (or launched `python run.py serve` separately):

```powershell
curl http://127.0.0.1:8766/health
curl -X POST http://127.0.0.1:8766/v1/chat/completions -H "Content-Type: application/json" -d '{\"model\":\"africa-giants\",\"messages\":[{\"role\":\"user\",\"content\":\"Jinsi ya kusajili kampuni BRELA?\"}],\"max_tokens\":50}'
curl -X POST http://127.0.0.1:8766/rag-chat -H "Content-Type: application/json" -d '{\"question\":\"What is TRA tax filing?\",\"top_k\":3,\"max_tokens\":80}'
```

The project also ships its own smoke runner that hits the same endpoints with a slightly different payload set:

```powershell
python run.py smoke --port 8766
```

## Run (human path) — bare server

```powershell
$env:AFRICA_GIANTS_MOCK='1'; python run.py serve --port 8000
```

Blocks forever, no auto-shutdown. Useful for hand-poking via `/docs` (Swagger UI). Without `AFRICA_GIANTS_MOCK=1`, the server tries to load the real model from HF — needs `HF_TOKEN` in `.env` and is slow on CPU (auto-redirects to `HuggingFaceTB/SmolLM-135M` for an 8B base when GPU is absent).

## Other `python run.py` commands

| Command | What it does | Local-runnable? |
|---|---|---|
| `python run.py scrape` | Mock scraper → clean → dedupe → synth Q&A → JSONL splits | yes (uses `use_mock=True` scraper) |
| `python run.py build-rag` | Rebuild `data/processed/rag_index.json` from processed data | yes |
| `python run.py build-dataset` | Build clean instruction dataset for fine-tuning | yes |
| `python run.py train` | Full orchestrator: scrape → HF upload → Kaggle push → monitor → eval → deploy | **needs `.env` with `HF_TOKEN` + `KAGGLE_USERNAME`/`KAGGLE_KEY` (KGAT)**; pushes to Kaggle, GPU work runs there |
| `python run.py evaluate --model <name>` | Run eval gate (thresholds in `config/eval.yaml`) | yes, but needs a model |
| `python run.py deploy` | Hot-reload model on a running server (POST `/v1/reload`) | yes, requires `API_RELOAD_TOKEN` |
| `python run.py smoke --port 8000` | Hits health/completions/rag-chat/feedback/metrics on a running server | yes |
| `python run.py feedback-loop` | Merge `data/processed/feedback.jsonl` into instruction dataset | yes |
| `python run.py schedule --interval 24h` | Run orchestrator on a recurring interval | yes (long-running) |
| `python run.py registry --status production` | Print model registry as JSON | yes |

The full training pipeline mainly lives on Kaggle. The local orchestrator pushes the notebook (`kaggle/kaggle_train_arque_llama.ipynb`) and polls status — actual GPU training runs in the Kaggle kernel.

## Gotchas

- **`AFRICA_GIANTS_MOCK=1` is the only way to boot the server in seconds.** Without it, `InferenceEngine.__init__` tries to download `prospaprospa007/africa-giants-adapter-v1` from HF (private repo) or fall back to the 8B base — slow at best, broken without `HF_TOKEN`.
- **RAG endpoint is `/rag-chat`, NOT `/rag/chat`.** The README/CLAUDE.md says `/rag/chat`; the actual route in `src/serve/server.py:122` is `/rag-chat`. The driver and `smoke_test.py` both use the correct one.
- **`/v1/reload` requires `X-Reload-Token` header.** Defaults to `default_secret_reload_token` if `API_RELOAD_TOKEN` is unset (see `src/common/secrets.py:26`). The driver doesn't exercise this endpoint — it would hot-swap models.
- **Kaggle training has two persistent manual blockers.** `kernels_push()` ignores the metadata `accelerator: nvidiaTeslaT4x2` (resets to P100) and wipes the `AFRICA_GIANTS` secret attachment. Every `python run.py train` requires: open https://www.kaggle.com/code/prospaprospa/africa-giants-trainer → Edit → Settings: T4 x2 → Add-ons → Secrets: AFRICA_GIANTS ON → Save → Run All. Not in scope for the local smoke driver but agents asked to "run train" must know.
- **`models/pipeline_state.json` is gitignored.** Local-only checkpoint of completed orchestrator steps (`data_pipeline`, `hf_upload`, `kaggle_trigger`, `kaggle_monitor`, `evaluate`, `deploy`). Edit it manually to force a step to re-run.
- **`get_chat_template` is intentionally absent from the Kaggle notebook.** AfriqueLlama has its own tokenizer; calling `get_chat_template` corrupts the EOS handling. Do not re-add it.
- **PowerShell stderr handling.** `python run.py ...` writes logs to stderr; in PowerShell those lines surface as `NativeCommandError` with red wrapping. Harmless — check the exit code, not the red. Set `$env:PYTHONIOENCODING='utf-8'` to avoid cp1252 crashes on Unicode in logs.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` (or similar) | `pip install -r requirements.txt` |
| `HF_TOKEN environment variable is missing` at server start | Either set `AFRICA_GIANTS_MOCK=1` (recommended for local smoke) or put `HF_TOKEN=hf_...` in `.env` |
| Driver hangs on "Launching: ..." | Port already bound. Pick a different `--port` or kill the previous server (`netstat -ano \| findstr :8765` then `taskkill /F /PID <pid>`) |
| `[FAIL] GET /health -- <urlopen error...>` | Server crashed before binding. Re-run the bare command without backgrounding to see the traceback: `$env:AFRICA_GIANTS_MOCK='1'; python run.py serve --port 8766` |
| `8B model on CPU is too slow — redirecting to HuggingFaceTB/SmolLM-135M` | Expected when running real (non-mock) on a CPU-only box — `src/serve/inference.py:91` does this automatically |
| `cp1252 codec can't encode` in PowerShell | `$env:PYTHONIOENCODING='utf-8'` before the command |

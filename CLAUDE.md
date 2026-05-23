# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

AFRICA GIANTS is a continuous LLM pre-training, fine-tuning, and redeployment pipeline for Tanzanian Business Insights. It combines QLoRA fine-tuning on Kaggle GPUs with RAG at inference time to produce a bilingual (Swahili/English) AI assistant grounded in Tanzanian business knowledge.

Base model: `McGill-NLP/AfriqueLlama-8B` on Hugging Face (Llama 3.1 8B pre-trained on 20 African languages including Swahili).

## Commands

### Installation
```bash
pip install -r requirements.txt
# or editable install:
pip install -e .
```

### Running the Pipeline (via `run.py`)
```bash
python run.py scrape          # Collect, clean, deduplicate, synthesize Q&A pairs
python run.py train           # Full orchestration: data prep → HF upload → Kaggle training → deploy
python run.py serve --port 8000   # Start FastAPI inference server
python run.py evaluate --model <model_name>  # Run eval gate (thresholds: acc≥0.75, hallucination≤0.10, latency≤1500ms)
python run.py smoke --port 8000   # Smoke test a running server
python run.py deploy          # Hot-reload model weights on running server
python run.py build-rag       # Rebuild RAG vector index
```

### Scripts (Windows/POSIX equivalents)
```powershell
.\scripts\run_collect.ps1    # Equivalent to: python run.py scrape
.\scripts\run_server.ps1     # Equivalent to: python run.py serve --port 8000
```

### Testing
```bash
pytest                        # Run all tests
pytest tests/test_cleaning.py # Run single test file
```
Note: test files do not yet exist — `tests/` contains only `.gitkeep`. The `pytest` and `httpx` dependencies are already in `requirements.txt`.

## Architecture

### Data Flow
```
Web Scraping → Data Gate → Clean → Deduplicate → Chunk → Vector DB (RAG index)
                                        ↓
                              Synthetic Q&A Generation
                                        ↓
                              SFT JSONL (train/val split) → HF Dataset Upload
                                        ↓
                              Kaggle Kernel Training (QLoRA) → HF Model Upload
                                        ↓
                              Evaluation Gate → Model Registry → FastAPI Serving
                                        ↓
                              Monitoring + User Feedback → next training cycle
```

### Source Modules (`src/`)

| Module | Role |
|---|---|
| `common/` | Shared: Pydantic schemas, logging, secrets loading, config/storage utilities |
| `collect/` | `TanzanianBusinessScraper` targeting 10+ Tanzanian sites; `data_gate.py` rejects spam/low-quality/wrong-language |
| `process/` | Clean, deduplicate, prepare JSONL training data |
| `synthetic/` | Generate and validate synthetic Q&A pairs from cleaned documents |
| `rag/` | Local JSON-backed vector store + BM25-style retriever + RAG pipeline orchestrator |
| `train/` | LoRA fine-tuning via PEFT; training is actually executed on Kaggle kernels |
| `serve/` | FastAPI with OpenAI-compatible `/v1/chat/completions`, `/rag/chat`, `/feedback`, `/v1/reload` |
| `evaluate/` | Eval gate enforcing accuracy/hallucination/latency thresholds before promotion |
| `deploy/` | Triggers HF model reload, runs smoke tests |
| `monitor/` | Records latency/error metrics; saves feedback for future retraining |
| `registry/` | Tracks model versions, eval scores, deployment status |
| `orchestrator/` | Top-level pipeline coordinator called by `run.py train` |

### Configuration (`config/`)
- `base.yaml` — project name, log paths
- `models.yaml` — LoRA hyperparameters (r=16, alpha=32, lr=0.0002, batch=4, epochs=3, bf16)
- `kaggle.yaml` — Kaggle kernel setup
- `huggingface.yaml` — HF repo IDs and deployment settings
- `eval.yaml` — Promotion thresholds

### Quality Gates
Three explicit gates guard promotion:
1. **Data gate** (`collect/data_gate.py`) — rejects at ingest
2. **Evaluation gate** (`evaluate/eval_gate.py`) — rejects model before deployment
3. **Smoke tests** (`deploy/smoke_test.py`) — validates post-deployment

### RAG Design
The vector store (`rag/vector_store.py`) is intentionally a local JSON file — no FAISS or Chroma yet. Retrieval uses BM25-style token matching. The code is structured to make upgrading to a production vector DB straightforward.

### Environment Variables
Copy `.env.example` to `.env`. Required vars: `HF_TOKEN`, `KAGGLE_USERNAME`, `KAGGLE_KEY`. Optional serving vars are also listed there. Secrets are loaded via `src/common/secrets.py`.

### Notebooks
`notebooks/` contains Kaggle training notebooks that run the actual GPU-backed fine-tuning. The orchestrator uploads data to HF and triggers these kernels via the Kaggle API rather than running training locally.

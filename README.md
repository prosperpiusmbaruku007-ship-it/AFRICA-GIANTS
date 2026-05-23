# AFRICA GIANTS

A continuous LLM fine-tuning and redeployment pipeline for **Tanzanian Business Insights**. Combines QLoRA training on Kaggle GPUs with RAG at inference time to produce a bilingual (Swahili/English) AI assistant grounded in Tanzanian business knowledge.

**Base model:** `prospAprospA007/Afrique-llama-8B`

## Architecture

```
Web Scraping (TRA, BRELA, NBS, BoT, ...)
    ↓
Data Gate → Clean → Deduplicate → Vector DB (RAG index)
                        ↓
              Synthetic Q&A Generation
                        ↓
              SFT JSONL → Hugging Face Dataset Upload
                        ↓
              Kaggle QLoRA Training → Hugging Face Model Upload
                        ↓
              Evaluation Gate → Model Registry → FastAPI Serving
                        ↓
              Monitoring + Feedback → next training cycle
```

**Two-layer inference:**
- **Fine-tuning** — teaches behavior, tone, domain reasoning
- **RAG** — provides fresh factual knowledge at inference time

## Quickstart

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in credentials
cp .env.example .env

# Collect and prepare training data
python run.py scrape

# Start inference server
python run.py serve --port 8000
```

## Commands

| Command | Description |
|---|---|
| `python run.py scrape` | Scrape → clean → deduplicate → generate synthetic Q&A |
| `python run.py train` | Full pipeline: data prep → HF upload → Kaggle training → deploy |
| `python run.py serve --port 8000` | Start FastAPI inference server |
| `python run.py evaluate --model <name>` | Run evaluation gate |
| `python run.py smoke --port 8000` | Smoke test a running server |
| `python run.py deploy` | Hot-reload model weights on running server |
| `python run.py build-rag` | Rebuild RAG vector index |

## Environment Variables

Copy `.env.example` to `.env` and set:

```
HF_TOKEN=your_hugging_face_token
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

## Evaluation Gates

Models are promoted only when they pass all three gates:

| Metric | Threshold |
|---|---|
| Accuracy | ≥ 0.75 |
| Hallucination rate | ≤ 0.10 |
| Latency | ≤ 1500 ms |

## API Endpoints

The FastAPI server exposes:

```
GET  /health
POST /v1/chat/completions   # OpenAI-compatible
POST /rag/chat              # RAG-augmented inference
POST /feedback              # User feedback collection
POST /v1/reload             # Hot-reload model weights
```

## Training on Kaggle

Training runs on Kaggle GPU notebooks (`notebooks/`), not locally. The `python run.py train` command:
1. Prepares and uploads the dataset to Hugging Face
2. Triggers the Kaggle kernel via API
3. Monitors training progress
4. Deploys the new model if it passes the evaluation gate

LoRA config: `r=16, alpha=32, dropout=0.05, lr=0.0002, batch_size=4, epochs=3, bf16=true`

## Project Structure

```
src/
├── collect/       # Web scraping + data quality gate
├── process/       # Cleaning, deduplication, JSONL prep
├── synthetic/     # Q&A generation and validation
├── rag/           # Vector store, retriever, RAG pipeline
├── train/         # LoRA fine-tuning (runs on Kaggle)
├── serve/         # FastAPI inference server
├── evaluate/      # Benchmark runner + promotion gate
├── deploy/        # HF deployment + smoke tests
├── monitor/       # Latency/error metrics + feedback
├── registry/      # Model version tracking
├── orchestrator/  # End-to-end pipeline coordinator
└── common/        # Schemas, logging, secrets, storage

config/            # YAML configs for models, Kaggle, HF, eval
notebooks/         # Kaggle training notebooks
data/              # raw, cleaned, processed, eval, feedback (gitignored)
models/            # Local model registry (gitignored)
vector_db/         # RAG index (gitignored)
```

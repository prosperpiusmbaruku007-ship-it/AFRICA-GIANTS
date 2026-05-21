# AFRICA GIANTS: Continuous LLM Training & Deployment Pipeline

This repository contains the enterprise-grade automated pipeline to constantly collect Tanzanian business/regulatory data, perform continuous pre-training & supervised fine-tuning (SFT) on the **Afrique Llama 8B** model using Kaggle GPUs, evaluate updates against custom benchmarks, and hot-swap serving weights on the API server without downtime.

---

## 1. System Architecture & Workflow

1. **Scraping**: Local crawlers or CI actions fetch regulatory/business updates from TRA, BRELA, BoT, NBS, NBAA, TIC, TBS, TMDA, and local marketplaces.
2. **Preprocessing**: Raw documents are cleaned, deduplicated, and passed to a **Synthetic Data Generator** to formulate high-quality Q&A instruction pairs in Swahili and English.
3. **Data Registry**: Datasets are pushed to a private repository on Hugging Face Hub under the username `prospAprospA007`.
4. **Kaggle Training**: The orchestrator triggers a Kaggle kernel execution using the Kaggle API. The notebook trains the **Afrique Llama 8B** model on Kaggle's free GPU resources using QLoRA.
5. **Model Registry**: When validation checks pass, Kaggle commits the new model weights back to your private Hugging Face Model Repository.
6. **Zero-Downtime Deployment**: The server is notified to fetch the updated weights from Hugging Face Hub and reload them in-memory, ensuring continuous availability.

---

## 2. Directory Layout

```text
africa-giants/
├── README.md                 # Setup, architecture details, and usage instructions
├── requirements.txt         # Core dependencies (FastAPI, PyTorch, Transformers, BeautifulSoup4, etc.)
├── pyproject.toml           # Python packaging configuration
├── config/
│   ├── base.yaml             # Logging and project paths configuration
│   ├── kaggle.yaml           # Kaggle API triggers & notebook timeouts
│   ├── huggingface.yaml      # prospAprospA007 repositories and space targets
│   ├── models.yaml           # Base model (Afrique Llama 8B) & LoRA hyperparameters
│   └── eval.yaml             # Evaluation validation loss and latency thresholds
├── data/
│   ├── raw/                 # Scraped raw business texts and HTML snippets
│   ├── processed/           # Processed datasets (train/validation splits)
│   └── eval/                # Benchmark Q&A validation sets
├── notebooks/
│   └── kaggle_train_arque_llama.ipynb  # PyTorch & SFT Trainer notebook pushed to Kaggle
├── src/
│   ├── common/              # Logging, secrets manager, storage, and schemas
│   ├── collect/             # Tanzanian business site web scraper and data gates
│   ├── process/             # Text cleaning, Jaccard deduplication, and format normalizers
│   ├── synthetic/           # Synthetic Q&A generator (using LLM or NLP heuristics)
│   ├── orchestrator/        # Main pipeline runner (dataset upload -> Kaggle run -> deploy reload)
│   ├── serve/               # FastAPI server and inference engine
│   └── deploy/              # Reload trigger and smoke tests
└── scripts/                 # Convenience scripts to trigger stages (Bash & PowerShell)
```

---

## 3. Installation & Credentials

1. Clone this repository:
   ```bash
   git clone https://github.com/[your-username]/AFRICA-GIANTS.git
   cd AFRICA-GIANTS
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup environment variables by copying `.env.example` to `.env` and filling in the values:
   ```bash
   cp .env.example .env
   ```

### Obtaining API Tokens:
- **Hugging Face Token**: Go to [HF Settings -> Tokens](https://huggingface.co/settings/tokens) and generate a token with `Write` permission.
- **Kaggle API Key**: Go to Kaggle -> Your Profile -> Settings -> Click **Create New Token**. This downloads a `kaggle.json` file. Copy the `username` and `key` into your `.env` file.

---

## 4. Usage Commands

All pipeline operations can be triggered via `run.py` CLI:

### A. Scrape and Preprocess Tanzanian Business Data
Crawls targeted Tanzanian government/business sites, cleans text, deduplicates, and generates synthetic Q&A pairs:
```bash
python run.py scrape
```

### B. Trigger and Monitor Training on Kaggle
Orchestrates uploading dataset to Hugging Face Hub, triggering the Kaggle kernel, and waiting for it to compile:
```bash
python run.py train
```

### C. Run the Serving API Server Locally
Starts the FastAPI completions server serving the active weights:
```bash
python run.py serve
```

### D. Request Server reload
Instructs a running FastAPI completions server to pull the updated weights from HF Hub and swap them in-memory:
```bash
python run.py deploy
```

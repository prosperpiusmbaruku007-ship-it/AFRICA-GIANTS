"""
End-to-end pipeline orchestrator.

Run order: local data prep → HF dataset upload → Kaggle trigger →
monitor training → evaluate → register → deploy.

State is persisted to models/pipeline_state.json so a crashed run can
resume from the last completed step rather than starting over.
"""
import json
import os
import subprocess
import time
from typing import Optional

from src.common.logging import get_logger
from src.common.storage import load_yaml_config, get_project_root, get_data_path
from src.common.secrets import get_hf_token, get_kaggle_credentials
from src.collect.web_scraper import TanzanianBusinessScraper
from src.collect.data_gate import validate_raw_documents
from src.process.clean import clean_documents
from src.process.deduplicate import deduplicate_documents
from src.synthetic.generate_qa import generate_synthetic_dataset
from src.synthetic.validate_synthetic import validate_synthetic_pairs
from src.process.prepare_training_data import prepare_and_split_datasets

logger = get_logger("orchestrator")

STATE_PATH = os.path.join(get_project_root(), "models", "pipeline_state.json")
STEPS = [
    "data_pipeline",
    "hf_upload",
    "kaggle_trigger",
    "kaggle_monitor",
    "evaluate",
    "deploy",
]


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------

def _load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {"completed_steps": [], "run_id": None}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _mark_done(state: dict, step: str) -> None:
    if step not in state["completed_steps"]:
        state["completed_steps"].append(step)
    _save_state(state)


def _reset_state() -> dict:
    import uuid
    state = {"completed_steps": [], "run_id": str(uuid.uuid4())[:8]}
    _save_state(state)
    return state


# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------

def _retry(fn, retries: int = 3, backoff: float = 10.0, label: str = ""):
    """Call fn(); on exception retry up to `retries` times with exponential backoff."""
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            wait = backoff * (2 ** (attempt - 1))
            logger.warning("%s failed (attempt %d/%d): %s — retrying in %.0fs", label, attempt, retries, exc, wait)
            time.sleep(wait)
    raise RuntimeError(f"{label} failed after {retries} retries") from last_exc


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------

def prepare_kaggle_metadata(root_dir: str, kaggle_config: dict, hf_config: dict) -> None:
    kaggle_dir = os.path.join(root_dir, "kaggle")
    os.makedirs(kaggle_dir, exist_ok=True)
    metadata = {
        "id": f"{kaggle_config['kaggle']['username']}/{kaggle_config['kaggle']['kernel_slug']}",
        "title": kaggle_config['kaggle']['kernel_slug'].replace("-", " ").title(),
        "code_file": "kaggle_train_arque_llama.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": "true",
        # Request T4 specifically — P100 (sm_60) lost PyTorch support after 2.1.x
        # and torch==2.1.2+cu118 has been removed from PyPI.
        "accelerator": "nvidiaTeslaT4",
        "enable_internet": "true",
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
    }
    metadata_path = os.path.join(root_dir, kaggle_config['kaggle']['kernel_metadata_file'])
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    logger.info("Generated Kaggle metadata at %s", metadata_path)


def run_local_data_pipeline() -> bool:
    logger.info("Starting local data ingestion pipeline...")
    scraper = TanzanianBusinessScraper(use_mock=True)
    raw_docs = scraper.collect_all()
    valid_raw_docs = validate_raw_documents(raw_docs)
    if not valid_raw_docs:
        logger.error("No valid raw documents passed the data gate")
        return False
    cleaned_docs = clean_documents(valid_raw_docs)
    unique_cleaned_docs = deduplicate_documents(cleaned_docs)
    synthetic_qa = generate_synthetic_dataset(unique_cleaned_docs)
    valid_qa = validate_synthetic_pairs(synthetic_qa)
    if not valid_qa:
        logger.error("No synthetic Q&A pairs passed validation")
        return False
    prepare_and_split_datasets(valid_qa)

    # Also build the clean instruction dataset for fine-tuning
    try:
        from src.process.build_instruction_dataset import build_instruction_dataset
        build_instruction_dataset(include_forums=True)
        logger.info("Built clean instruction dataset")
    except Exception as e:
        logger.warning("Instruction dataset build failed (non-critical): %s", e)

    logger.info("Local data pipeline completed")
    return True


def upload_datasets_to_hf(hf_config: dict, hf_token: str) -> None:
    from huggingface_hub import HfApi
    api = HfApi()
    repo_id = hf_config["huggingface"]["dataset_repo"]
    root_dir = get_project_root()
    train_path = os.path.join(root_dir, "data", "processed", "train_sft.jsonl")
    val_path = os.path.join(root_dir, "data", "processed", "val_sft.jsonl")
    instruction_path = os.path.join(root_dir, "data", "processed", "instruction_dataset.jsonl")

    logger.info("Uploading datasets to HF repo: %s", repo_id)

    def _upload():
        api.create_repo(repo_id=repo_id, repo_type="dataset", token=hf_token,
                        private=hf_config["huggingface"]["private"], exist_ok=True)
        for local_path, repo_name in [
            (train_path, "train_sft.jsonl"),
            (val_path, "val_sft.jsonl"),
            (instruction_path, "instruction_dataset.jsonl"),
        ]:
            if os.path.exists(local_path):
                api.upload_file(path_or_fileobj=local_path, path_in_repo=repo_name,
                                repo_id=repo_id, repo_type="dataset", token=hf_token)
                logger.info("Uploaded %s to HF", repo_name)

    _retry(_upload, retries=3, backoff=15.0, label="HF dataset upload")
    logger.info("Datasets uploaded to HF Hub")


def trigger_kaggle_training(kaggle_config: dict, credentials: dict) -> str:
    root_dir = get_project_root()

    key = credentials["key"]
    username = credentials["username"]
    os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)

    if key.startswith("KGAT_"):
        # New-format access token — kagglesdk 2.x reads KAGGLE_API_TOKEN or ~/.kaggle/access_token
        os.environ["KAGGLE_API_TOKEN"] = key
        access_token_path = os.path.expanduser("~/.kaggle/access_token")
        with open(access_token_path, "w") as f:
            f.write(key)
        logger.info("Using KGAT access token for Kaggle authentication")
    else:
        # Legacy API key — set env vars and write kaggle.json
        os.environ["KAGGLE_USERNAME"] = username
        os.environ["KAGGLE_KEY"] = key
        with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
            json.dump({"username": username, "key": key}, f)
        try:
            if os.name != "nt":
                os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)
        except Exception:
            pass

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    kaggle_dir = os.path.join(root_dir, "kaggle")
    notebook_src = os.path.join(root_dir, kaggle_config["kaggle"]["notebook_source"])
    notebook_dest = os.path.join(kaggle_dir, "kaggle_train_arque_llama.ipynb")
    if os.path.exists(notebook_src):
        import shutil
        shutil.copy(notebook_src, notebook_dest)

    kernel_ref = f"{kaggle_config['kaggle']['username']}/{kaggle_config['kaggle']['kernel_slug']}"

    def _push():
        api.kernels_push(kaggle_dir)

    _retry(_push, retries=3, backoff=30.0, label="Kaggle kernel push")
    logger.info("Pushed kernel to Kaggle: %s", kernel_ref)
    return kernel_ref


def monitor_kaggle_run(kernel_ref: str, timeout_seconds: int, polling_interval: int) -> bool:
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()  # credentials already set in env by trigger_kaggle_training

    start_time = time.time()
    logger.info("Monitoring Kaggle kernel: %s", kernel_ref)

    while time.time() - start_time < timeout_seconds:
        try:
            status_data = _retry(
                lambda: api.kernels_status(kernel_ref),
                retries=3, backoff=10.0, label="Kaggle status poll"
            )
            # SDK 2.x returns a response object with enum strings like
            # "kernelworkerstatus.running" — strip the prefix to get the bare status
            if hasattr(status_data, "status"):
                raw = str(status_data.status).lower()
            elif isinstance(status_data, dict):
                raw = status_data.get("status", "unknown").lower()
            else:
                raw = "unknown"
            status = raw.split(".")[-1]  # "kernelworkerstatus.running" -> "running"
            elapsed = int(time.time() - start_time)
            logger.info("Kaggle status=%s elapsed=%ds", status, elapsed)

            if status in ("complete", "success"):
                logger.info("Kaggle training completed successfully")
                return True
            elif status in ("error", "failed"):
                logger.error("Kaggle training failed — review Kaggle logs")
                return False
            elif status in ("cancel", "cancelled"):
                logger.error("Kaggle job was cancelled")
                return False
        except Exception as e:
            # Check both the RuntimeError message and its underlying cause
            err_str = str(e) + str(e.__cause__ if e.__cause__ else "")
            # Permission denied means this token can't read kernel status — skip monitoring
            if "Permission" in err_str and "denied" in err_str:
                logger.warning(
                    "Kaggle token lacks 'kernels.get' permission — cannot poll status. "
                    "Kernel was pushed; check https://www.kaggle.com/code/%s manually. "
                    "Skipping monitor step and proceeding to evaluate.",
                    kernel_ref,
                )
                return True
            logger.warning("Failed to poll Kaggle status: %s", e)

        time.sleep(polling_interval)

    logger.error("Kaggle training timed out after %ds", timeout_seconds)
    return False


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(resume: bool = True) -> None:
    root_dir = get_project_root()
    kaggle_config = load_yaml_config("kaggle")
    hf_config = load_yaml_config("huggingface")

    try:
        hf_token = get_hf_token()
        kaggle_creds = get_kaggle_credentials()
    except Exception as e:
        logger.critical("Credential loading error: %s", e)
        return

    state = _load_state() if resume else _reset_state()
    done = set(state.get("completed_steps", []))
    logger.info("Pipeline run_id=%s resuming from step after: %s", state.get("run_id"), list(done) or "start")

    # Step 0: merge any pending feedback into instruction dataset
    try:
        from src.orchestrator.feedback_loop import merge_feedback_into_dataset
        added = merge_feedback_into_dataset()
        if added:
            logger.info("Feedback loop: merged %d new examples into instruction dataset", added)
    except Exception as e:
        logger.warning("Feedback loop failed (non-critical): %s", e)

    # Step 1: local data prep
    if "data_pipeline" not in done:
        if not run_local_data_pipeline():
            logger.error("Data pipeline failed — halting")
            return
        _mark_done(state, "data_pipeline")

    # Step 2: HF dataset upload
    if "hf_upload" not in done:
        upload_datasets_to_hf(hf_config, hf_token)
        _mark_done(state, "hf_upload")

    # Step 3: Kaggle trigger
    if "kaggle_trigger" not in done:
        prepare_kaggle_metadata(root_dir, kaggle_config, hf_config)
        kernel_ref = trigger_kaggle_training(kaggle_config, kaggle_creds)
        state["kernel_ref"] = kernel_ref
        _mark_done(state, "kaggle_trigger")
    else:
        kernel_ref = state.get("kernel_ref", "")

    # Step 4: monitor Kaggle
    if "kaggle_monitor" not in done:
        success = monitor_kaggle_run(
            kernel_ref,
            kaggle_config["kaggle"]["training_timeout"],
            kaggle_config["kaggle"]["polling_interval"],
        )
        if not success:
            logger.error("Training failed or timed out — halting")
            return
        _mark_done(state, "kaggle_monitor")

    # Step 5: evaluate
    if "evaluate" not in done:
        try:
            from src.evaluate.eval_gate import evaluate_gate
            model_id = hf_config["huggingface"].get("adapter_repo", "africa-giants-adapter-v1").split("/")[-1]
            passed = evaluate_gate(
                model_name=model_id,
                dataset_version=state.get("run_id", "unknown"),
                hf_repo=hf_config["huggingface"].get("adapter_repo", ""),
                auto_register=True,
            )
            if not passed:
                logger.warning("Eval gate failed — model NOT promoted to production")
                return
        except Exception as e:
            logger.error("Evaluation step error: %s", e)
            return
        _mark_done(state, "evaluate")

    # Step 6: deploy
    if "deploy" not in done:
        deploy_script = os.path.join(root_dir, "src", "deploy", "deploy_hf_model.py")
        if os.path.exists(deploy_script):
            logger.info("Triggering deploy script...")
            try:
                subprocess.run(["python", deploy_script], check=True, timeout=120)
            except Exception as e:
                logger.error("Deploy script error: %s", e)
                return
        _mark_done(state, "deploy")

    logger.info("Pipeline completed successfully — all steps done for run_id=%s", state.get("run_id"))
    # Clear state so next run starts fresh
    _reset_state()


if __name__ == "__main__":
    main()

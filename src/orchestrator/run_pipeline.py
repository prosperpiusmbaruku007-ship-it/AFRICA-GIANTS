import os
import json
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

def prepare_kaggle_metadata(root_dir: str, kaggle_config: dict, hf_config: dict):
    """Dynamically generates the Kaggle metadata json file needed by the Kaggle CLI."""
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
        "enable_internet": "true",
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": []
    }
    
    metadata_path = os.path.join(root_dir, kaggle_config['kaggle']['kernel_metadata_file'])
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    logger.info(f"Generated Kaggle metadata at {metadata_path}")

def run_local_data_pipeline() -> bool:
    """Executes the entire local data pipeline: Scrape -> Clean -> Deduplicate -> Synthesize -> Split."""
    logger.info("Starting local data ingestion and preparation pipeline...")
    
    # 1. Scrape Tanzanian sites
    scraper = TanzanianBusinessScraper(use_mock=True)
    raw_docs = scraper.collect_all()
    
    # 2. Gatekeeper validation
    valid_raw_docs = validate_raw_documents(raw_docs)
    if not valid_raw_docs:
        logger.error("No valid raw documents passed the data gate! Aborting.")
        return False
        
    # 3. Text cleaning
    cleaned_docs = clean_documents(valid_raw_docs)
    
    # 4. Deduplication
    unique_cleaned_docs = deduplicate_documents(cleaned_docs)
    
    # 5. Synthetic QA generation
    synthetic_qa = generate_synthetic_dataset(unique_cleaned_docs)
    
    # 6. Validate synthetic QA pairs
    valid_qa = validate_synthetic_pairs(synthetic_qa)
    if not valid_qa:
        logger.error("No synthetic Q&A pairs passed validation! Aborting.")
        return False
        
    # 7. Dataset split
    prepare_and_split_datasets(valid_qa)
    logger.info("Local data ingestion pipeline completed successfully.")
    return True

def upload_datasets_to_hf(hf_config: dict, hf_token: str):
    """Pushes the processed train/val JSONL files to Hugging Face Hub as a Dataset."""
    from huggingface_hub import HfApi
    api = HfApi()
    
    repo_id = hf_config["huggingface"]["dataset_repo"]
    root_dir = get_project_root()
    train_path = os.path.join(root_dir, "data", "processed", "train_sft.jsonl")
    val_path = os.path.join(root_dir, "data", "processed", "val_sft.jsonl")
    
    logger.info(f"Uploading datasets to Hugging Face repo: {repo_id}...")
    try:
        # Create dataset repo if it doesn't exist
        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            token=hf_token,
            private=hf_config["huggingface"]["private"],
            exist_ok=True
        )
        
        # Upload train
        api.upload_file(
            path_or_fileobj=train_path,
            path_in_repo="train_sft.jsonl",
            repo_id=repo_id,
            repo_type="dataset",
            token=hf_token
        )
        
        # Upload val
        api.upload_file(
            path_or_fileobj=val_path,
            path_in_repo="val_sft.jsonl",
            repo_id=repo_id,
            repo_type="dataset",
            token=hf_token
        )
        logger.info("Datasets successfully uploaded to Hugging Face Hub.")
    except Exception as e:
        logger.error(f"Failed to upload datasets to HF: {e}")
        raise e

def trigger_kaggle_training(kaggle_config: dict, credentials: dict) -> str:
    """Configures Kaggle credentials and triggers the kernel run using Kaggle API."""
    # Write kaggle.json credentials locally for the Kaggle CLI
    root_dir = get_project_root()
    os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)
    with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
        json.dump(credentials, f)
    
    # Secure permissions
    try:
        if os.name != 'nt': # Unix only
            os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)
    except Exception:
        pass
        
    # Import kaggle after writing credentials
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    
    # Trigger the kernel
    logger.info(f"Triggering training job on Kaggle for kernel {kaggle_config['kaggle']['username']}/{kaggle_config['kaggle']['kernel_slug']}...")
    
    # Kaggle CLI requires pushing from the folder containing the kernel-metadata.json and code file
    kaggle_dir = os.path.join(root_dir, "kaggle")
    # Copy notebook to the kaggle dir if it exists
    notebook_src = os.path.join(root_dir, kaggle_config['kaggle']['notebook_source'])
    notebook_dest = os.path.join(kaggle_dir, "kaggle_train_arque_llama.ipynb")
    
    if os.path.exists(notebook_src):
        import shutil
        shutil.copy(notebook_src, notebook_dest)
        
    # Trigger run
    api.kernels_push(kaggle_dir)
    logger.info("Successfully pushed kernel to Kaggle.")
    return f"{kaggle_config['kaggle']['username']}/{kaggle_config['kaggle']['kernel_slug']}"

def monitor_kaggle_run(kernel_ref: str, timeout_seconds: int, polling_interval: int) -> bool:
    """Polls Kaggle to check the execution status of the notebook."""
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    
    start_time = time.time()
    logger.info(f"Monitoring Kaggle kernel: {kernel_ref}")
    
    while time.time() - start_time < timeout_seconds:
        status_data = api.kernel_status(kernel_ref)
        status = status_data.get("status", "unknown").lower()
        logger.info(f"Kaggle status: {status}")
        
        if status == "complete" or status == "success":
            logger.info("Kaggle training completed successfully!")
            return True
        elif status == "error" or status == "failed":
            logger.error("Kaggle training failed with an error. Review Kaggle logs.")
            return False
        elif status == "cancel" or status == "cancelled":
            logger.error("Kaggle job was cancelled.")
            return False
            
        time.sleep(polling_interval)
        
    logger.error("Kaggle training timed out!")
    return False

def main():
    root_dir = get_project_root()
    
    # Load configs
    kaggle_config = load_yaml_config("kaggle")
    hf_config = load_yaml_config("huggingface")
    
    # Load tokens
    try:
        hf_token = get_hf_token()
        kaggle_creds = get_kaggle_credentials()
    except Exception as e:
        logger.critical(f"Credential loading error: {e}")
        return

    # Step 1: Run Local Data Extraction & Prep
    if not run_local_data_pipeline():
        logger.error("Data pipeline step failed. Halting orchestrator.")
        return
        
    # Step 2: Push dataset to Hugging Face
    upload_datasets_to_hf(hf_config, hf_token)
    
    # Step 3: Set up Kaggle metadata & trigger
    prepare_kaggle_metadata(root_dir, kaggle_config, hf_config)
    kernel_ref = trigger_kaggle_training(kaggle_config, kaggle_creds)
    
    # Step 4: Monitor Training Run
    success = monitor_kaggle_run(
        kernel_ref,
        kaggle_config["kaggle"]["training_timeout"],
        kaggle_config["kaggle"]["polling_interval"]
    )
    
    if success:
        # Step 5: Notify Deployer to Hot-Reload Serving Weights
        logger.info("Pipeline run succeeded! Ready to trigger model hot-reload.")
        # Trigger deploy script
        import subprocess
        deploy_script = os.path.join(root_dir, "src", "deploy", "deploy_hf_model.py")
        if os.path.exists(deploy_script):
            logger.info("Executing deploy script...")
            subprocess.run(["python", deploy_script], check=True)
    else:
        logger.error("Pipeline run failed on training or timeout.")

if __name__ == "__main__":
    main()

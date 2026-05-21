import os
import requests
from src.common.logging import get_logger
from src.common.storage import load_yaml_config
from src.common.secrets import get_reload_token

logger = get_logger("deployer")

def trigger_reload():
    # Load configs
    hf_config = load_yaml_config("huggingface")
    model_name = hf_config["huggingface"]["model_repo"]
    reload_token = get_reload_token()
    
    port = os.getenv("PORT", "8000")
    url = f"http://localhost:{port}/v1/reload"
    
    headers = {
        "Content-Type": "application/json",
        "X-Reload-Token": reload_token
    }
    
    data = {
        "model_name_or_path": model_name
    }
    
    logger.info(f"Triggering hot-reload at {url} for model {model_name}...")
    try:
        response = requests.post(url, json=data, headers=headers, timeout=60)
        if response.status_code == 200:
            logger.info("Hot-reload successfully completed!")
            logger.info(response.json())
            
            # Execute smoke tests
            from src.deploy.smoke_test import run_smoke_tests
            run_smoke_tests(port)
        else:
            logger.error(f"Reload request failed with status code {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Failed to connect to inference server for reload: {e}")

if __name__ == "__main__":
    trigger_reload()

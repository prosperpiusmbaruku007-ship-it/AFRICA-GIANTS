import requests
from src.common.logging import get_logger

logger = get_logger("smoke_test")

def run_smoke_tests(port: str = "8000") -> bool:
    """Queries health and completions endpoints to ensure inference is functional."""
    base_url = f"http://localhost:{port}"
    
    logger.info("Running smoke tests on inference server...")
    
    # 1. Health check
    try:
        health_resp = requests.get(f"{base_url}/health", timeout=5)
        if health_resp.status_code != 200:
            logger.error(f"Health check failed: Status {health_resp.status_code}")
            return False
        logger.info(f"Health check passed: {health_resp.json()}")
    except Exception as e:
        logger.error(f"Failed to reach health endpoint: {e}")
        return False
        
    # 2. Completion check
    completion_data = {
        "model": "Afrique-llama-8B",
        "messages": [
            {"role": "user", "content": "Jinsi ya kusajili kampuni BRELA?"}
        ],
        "max_tokens": 50
    }
    
    try:
        comp_resp = requests.post(f"{base_url}/v1/chat/completions", json=completion_data, timeout=10)
        if comp_resp.status_code != 200:
            logger.error(f"Completions check failed: Status {comp_resp.status_code} - {comp_resp.text}")
            return False
            
        result = comp_resp.json()
        answer = result["choices"][0]["message"]["content"]
        logger.info("Completion check passed!")
        logger.info(f"Model Answer: {answer}")
        return True
    except Exception as e:
        logger.error(f"Failed to query chat completions endpoint: {e}")
        return False

if __name__ == "__main__":
    import sys
    port = sys.argv[1] if len(sys.argv) > 1 else "8000"
    success = run_smoke_tests(port)
    sys.exit(0 if success else 1)

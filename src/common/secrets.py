import os
from dotenv import load_dotenv

# Load .env file
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

def get_hf_token() -> str:
    """Returns the Hugging Face write token."""
    token = os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN environment variable is missing. Please set it in your .env file.")
    return token

def get_kaggle_credentials() -> dict:
    """Returns Kaggle API credentials."""
    username = os.getenv("KAGGLE_USERNAME")
    key = os.getenv("KAGGLE_KEY")
    if not username or not key:
        raise ValueError("KAGGLE_USERNAME or KAGGLE_KEY environment variables are missing. Please set them in your .env file.")
    return {"username": username, "key": key}

def get_reload_token() -> str:
    """Returns API reload token."""
    return os.getenv("API_RELOAD_TOKEN", "default_secret_reload_token")

def get_openai_api_key() -> str:
    """Returns the OpenAI API Key if configured (for evaluation judging)."""
    return os.getenv("OPENAI_API_KEY", "")

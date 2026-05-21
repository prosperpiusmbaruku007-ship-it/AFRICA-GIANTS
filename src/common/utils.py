import hashlib
from datetime import datetime
import re

def generate_doc_id(content: str) -> str:
    """Generates a SHA-256 hash of the content to use as a unique ID."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def get_current_timestamp() -> str:
    """Returns the current ISO-formatted timestamp."""
    return datetime.utcnow().isoformat()

def clean_whitespace(text: str) -> str:
    """Normalizes whitespace and removes excessive blank lines."""
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

def estimate_token_count(text: str) -> int:
    """Approximates the number of tokens in a string (approx 4 characters per token)."""
    return len(text) // 4

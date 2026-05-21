import os
from datetime import datetime
from typing import List
from src.common.logging import get_logger
from src.common.storage import get_data_path
from src.common.schemas import ScrapedDocument, CleanedDocument
from src.common.utils import clean_whitespace, generate_doc_id

logger = get_logger("cleaner")

def detect_language(text: str) -> str:
    """Simple heuristic to detect Swahili vs English text."""
    swahili_words = {"na", "ya", "wa", "kwa", "katika", "ni", "za", "la", "kodi", "biashara", "sheria", "tanzania"}
    words = set(text.lower().split()[:100])
    # Count Swahili markers
    sw_count = len(words.intersection(swahili_words))
    return "sw" if sw_count >= 2 else "en"

def clean_documents(raw_docs: List[ScrapedDocument]) -> List[CleanedDocument]:
    """Cleans and structures scraped documents."""
    cleaned_docs = []
    cleaned_dir = get_data_path("cleaned")
    
    for doc in raw_docs:
        cleaned_text = clean_whitespace(doc.raw_content)
        
        # Simple HTML tag strip (if any tags leaked)
        import re
        cleaned_text = re.sub(r'<[^>]+>', '', cleaned_text)
        
        lang = detect_language(cleaned_text)
        doc_id = generate_doc_id(cleaned_text)
        
        cleaned_doc = CleanedDocument(
            doc_id=doc_id,
            source_name=doc.source_name,
            url=doc.url,
            cleaned_content=cleaned_text,
            language=lang,
            cleaned_at=datetime.utcnow().isoformat()
        )
        cleaned_docs.append(cleaned_doc)
        
    logger.info(f"Cleaned {len(cleaned_docs)} documents.")
    return cleaned_docs

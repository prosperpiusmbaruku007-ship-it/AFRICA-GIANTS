import os
from typing import List
from src.common.logging import get_logger
from src.common.schemas import ScrapedDocument

logger = get_logger("data_gate")

def validate_raw_documents(documents: List[ScrapedDocument]) -> List[ScrapedDocument]:
    """Validates raw documents to filter out malformed or overly short text."""
    valid_docs = []
    for doc in documents:
        # Check basic schemas
        if not doc.url or not doc.source_name or not doc.raw_content:
            logger.warning(f"Skipping document with empty fields from {doc.source_name}")
            continue
        
        # Check text length threshold
        if len(doc.raw_content.strip()) < 50:
            logger.warning(f"Skipping document with insufficient text length ({len(doc.raw_content)}) from URL {doc.url}")
            continue
            
        valid_docs.append(doc)
        
    logger.info(f"Data Gate: Passed {len(valid_docs)} of {len(documents)} raw documents.")
    return valid_docs

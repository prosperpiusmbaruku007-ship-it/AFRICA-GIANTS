from typing import List
from src.common.logging import get_logger
from src.common.schemas import CleanedDocument

logger = get_logger("deduplicator")

def get_word_sets(text: str) -> set:
    """Prepares normalized word sets for Jaccard similarity comparison."""
    return set(text.lower().split())

def calculate_jaccard(set1: set, set2: set) -> float:
    """Computes the Jaccard similarity of two word sets."""
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

def deduplicate_documents(documents: List[CleanedDocument], threshold: float = 0.85) -> List[CleanedDocument]:
    """Filters out documents that have Jaccard similarity higher than threshold."""
    unique_docs = []
    word_sets = []
    
    for doc in documents:
        doc_set = get_word_sets(doc.cleaned_content)
        is_duplicate = False
        
        for existing_set in word_sets:
            similarity = calculate_jaccard(doc_set, existing_set)
            if similarity > threshold:
                is_duplicate = True
                logger.info(f"Skipping duplicate document from URL: {doc.url} (similarity: {similarity:.2f})")
                break
                
        if not is_duplicate:
            unique_docs.append(doc)
            word_sets.append(doc_set)
            
    logger.info(f"Deduplication: Kept {len(unique_docs)} of {len(documents)} documents.")
    return unique_docs

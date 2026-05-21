import json
from typing import List
from src.common.logging import get_logger
from src.common.schemas import QAPair

logger = get_logger("synthetic_validator")

def validate_synthetic_pairs(pairs: List[QAPair]) -> List[QAPair]:
    """Ensures synthetic Q&A pairs meet formatting and quality requirements."""
    valid_pairs = []
    
    for pair in pairs:
        # Check empty fields
        if not pair.instruction or not pair.output:
            logger.warning("Filtering out empty instruction or output Q&A pair.")
            continue
            
        # Check length thresholds
        if len(pair.instruction) < 10 or len(pair.output) < 15:
            logger.warning(f"Filtering out overly short Q&A pair. Instruction: '{pair.instruction}'")
            continue
            
        # Basic sanity check on formatting (e.g. no markdown artifacts in JSON strings)
        if "\\n" in pair.instruction and "{" in pair.instruction:
            logger.warning("Filtering out malformed instruction (JSON leaking).")
            continue
            
        valid_pairs.append(pair)
        
    logger.info(f"Synthetic Validation: Approved {len(valid_pairs)} of {len(pairs)} Q&A pairs.")
    return valid_pairs

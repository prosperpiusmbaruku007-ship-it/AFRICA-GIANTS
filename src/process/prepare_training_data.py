import os
import json
import random
from typing import List
from src.common.logging import get_logger
from src.common.storage import get_data_path
from src.common.schemas import QAPair

logger = get_logger("data_preparation")

def prepare_and_split_datasets(qa_pairs: List[QAPair], val_ratio: float = 0.15):
    """Splits Q&A pairs into train and evaluation subsets, and saves to data/processed/."""
    processed_dir = get_data_path("processed")
    eval_dir = get_data_path("eval")
    
    # Shuffle for random split
    shuffled_pairs = qa_pairs.copy()
    random.seed(42)
    random.shuffle(shuffled_pairs)
    
    split_idx = int(len(shuffled_pairs) * (1 - val_ratio))
    train_pairs = shuffled_pairs[:split_idx]
    val_pairs = shuffled_pairs[split_idx:]
    
    # Save train dataset
    train_path = os.path.join(processed_dir, "train_sft.jsonl")
    with open(train_path, "w", encoding="utf-8") as f:
        for pair in train_pairs:
            f.write(json.dumps(pair.dict(), ensure_ascii=False) + "\n")
            
    # Save validation dataset
    val_path = os.path.join(processed_dir, "val_sft.jsonl")
    with open(val_path, "w", encoding="utf-8") as f:
        for pair in val_pairs:
            f.write(json.dumps(pair.dict(), ensure_ascii=False) + "\n")
            
    # Also seed a copy to data/eval/ for benchmark consistency
    eval_benchmark_path = os.path.join(eval_dir, "tanzania_business_qa.jsonl")
    with open(eval_benchmark_path, "w", encoding="utf-8") as f:
        for pair in val_pairs:
            f.write(json.dumps(pair.dict(), ensure_ascii=False) + "\n")
            
    logger.info(f"Dataset Split: Saved {len(train_pairs)} training rows to {train_path}")
    logger.info(f"Dataset Split: Saved {len(val_pairs)} validation rows to {val_path}")
    logger.info(f"Dataset Split: Updated evaluation benchmark at {eval_benchmark_path}")

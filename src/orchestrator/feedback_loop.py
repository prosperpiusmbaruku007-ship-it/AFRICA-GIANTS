"""
Feedback loop — reads collected user feedback and converts verified
corrections into new training examples for the next fine-tuning cycle.

Run after each scheduled pipeline cycle to keep incorporating real user
corrections into the instruction dataset.
"""
import json
import os
from typing import List

from src.common.logging import get_logger
from src.common.storage import get_data_path, get_project_root

logger = get_logger("orchestrator.feedback_loop")

FEEDBACK_PATH = os.path.join(get_project_root(), "data", "feedback", "feedback.jsonl")
MIN_RATING_FOR_TRAINING = 4  # only use feedback rated 4 or 5 stars


def load_feedback() -> List[dict]:
    if not os.path.exists(FEEDBACK_PATH):
        return []
    rows = []
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def feedback_to_training_examples(feedback_rows: List[dict]) -> List[dict]:
    """
    Convert high-rated feedback into clean instruction-style training examples.

    Uses the user's correction as the gold-standard output when provided,
    otherwise uses the model's original response if highly rated.
    """
    examples = []
    for row in feedback_rows:
        rating = row.get("rating", 0)
        question = row.get("question") or row.get("user_message", "")
        correction = row.get("correction") or row.get("corrected_response", "")
        model_response = row.get("model_response") or row.get("assistant_message", "")

        if not question:
            continue

        # High rating + correction = gold example
        if rating >= MIN_RATING_FOR_TRAINING and correction:
            examples.append({
                "instruction": question,
                "input": "",
                "output": correction,
                "category": "feedback_correction",
                "language": row.get("language", "en"),
                "source": "feedback",
            })
        # High rating + no correction = model response was good
        elif rating >= MIN_RATING_FOR_TRAINING and model_response:
            examples.append({
                "instruction": question,
                "input": "",
                "output": model_response,
                "category": "feedback_positive",
                "language": row.get("language", "en"),
                "source": "feedback",
            })

    return examples


def merge_feedback_into_dataset(output_path: str = None) -> int:
    """
    Load all feedback, convert good examples, and append them to the
    instruction dataset. Returns number of new examples added.
    """
    feedback_rows = load_feedback()
    if not feedback_rows:
        logger.info("No feedback to process")
        return 0

    examples = feedback_to_training_examples(feedback_rows)
    if not examples:
        logger.info("No feedback examples met the quality threshold (rating >= %d)", MIN_RATING_FOR_TRAINING)
        return 0

    if output_path is None:
        processed_dir = get_data_path("processed")
        output_path = os.path.join(processed_dir, "instruction_dataset.jsonl")

    # Append new examples (avoid duplicates by checking existing instructions)
    existing_instructions = set()
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    existing_instructions.add(row.get("instruction", ""))
                except json.JSONDecodeError:
                    continue

    new_examples = [e for e in examples if e["instruction"] not in existing_instructions]

    if not new_examples:
        logger.info("All feedback examples already in dataset")
        return 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "a", encoding="utf-8") as f:
        for ex in new_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    logger.info("Added %d feedback-derived examples to %s", len(new_examples), output_path)
    return len(new_examples)


if __name__ == "__main__":
    added = merge_feedback_into_dataset()
    print(f"Added {added} feedback examples to training dataset")

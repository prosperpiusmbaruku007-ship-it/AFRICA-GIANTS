import json
import os
import re
from pathlib import Path

CLEANED_PAIRS_DIR = 'datasets/tier1a/cleaned_pairs'


def next_batch_num() -> int:
    existing = list(Path(CLEANED_PAIRS_DIR).glob('*.jsonl'))
    numbers  = [int(m.group(1)) for f in existing
                if (m := re.search(r'batch_(\d+)', f.name))]
    return max(numbers, default=0) + 1


def build_dataset(approved_pairs: list, batch_num: int) -> str:
    filename = f'cleaned_pairs_batch_{batch_num:03d}.jsonl'
    out_path = os.path.join(CLEANED_PAIRS_DIR, filename)
    os.makedirs(CLEANED_PAIRS_DIR, exist_ok=True)

    with open(out_path, 'w', encoding='utf-8') as f:
        for pair in approved_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + '\n')

    assert os.path.exists(out_path), f"Output file not written: {out_path}"
    written = sum(1 for line in open(out_path, encoding='utf-8') if line.strip())
    assert written == len(approved_pairs), (
        f"Line count mismatch: wrote {written}, expected {len(approved_pairs)}"
    )

    print(f"[builder] batch_{batch_num:03d}: {len(approved_pairs)} pairs written to {out_path}")
    print("[builder] Run 'python run.py upload' to rebuild SFT files and push to HuggingFace")
    return out_path

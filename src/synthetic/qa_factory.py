import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path

SOURCE_DOCS_DIR   = 'data/source_documents'
PROCESSED_FILES   = 'data/raw/processed_files.json'
RAW_GENERATED_DIR = 'data/raw/generated'
FLAGGED_DIR       = 'data/flagged'

MONTHLY_CAP              = float(os.environ.get('MONTHLY_BUDGET', '20.0'))
COST_PER_DOCUMENT_BUDGET = float(os.environ.get('COST_PER_DOCUMENT_BUDGET', '0.20'))

SUPPORTED_EXTS = {'.pdf', '.html', '.txt'}


def _file_md5(path: str) -> str:
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


def _load_processed() -> dict:
    if os.path.exists(PROCESSED_FILES):
        try:
            with open(PROCESSED_FILES, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_processed(data: dict):
    os.makedirs(os.path.dirname(PROCESSED_FILES), exist_ok=True)
    with open(PROCESSED_FILES, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _scan_source_documents() -> list:
    found = []
    for root, _dirs, files in os.walk(SOURCE_DOCS_DIR):
        for fname in sorted(files):
            if Path(fname).suffix.lower() in SUPPORTED_EXTS:
                found.append(os.path.join(root, fname))
    return found


def _already_processed(path: str, processed: dict) -> bool:
    entry = processed.get(path)
    if entry is None:
        return False
    return entry.get('md5') == _file_md5(path)


def _sum_cost_this_month() -> float:
    log_path  = 'data/cost_log.jsonl'
    month_str = datetime.utcnow().strftime('%Y-%m')
    total = 0.0
    try:
        with open(log_path, encoding='utf-8') as f:
            for line in f:
                try:
                    e = json.loads(line.strip())
                    if e.get('timestamp', '').startswith(month_str):
                        total += e.get('cost_usd', 0.0)
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    return total


def _check_budget(remaining: int, no_budget_check: bool) -> bool:
    if no_budget_check:
        return True
    current = _sum_cost_this_month()
    if current + COST_PER_DOCUMENT_BUDGET > MONTHLY_CAP:
        print(f"[cost] Monthly cap ${MONTHLY_CAP:.2f} approaching.")
        print(f"[cost] Used: ${current:.4f} | Per-doc buffer: ${COST_PER_DOCUMENT_BUDGET:.2f}")
        if remaining:
            print(f"[cost] {remaining} documents unprocessed.")
        print(f"[cost] To continue: COST_PER_DOCUMENT_BUDGET=2.00 python run.py generate")
        print(f"[cost] Or: python run.py generate --no-budget-check")
        return False
    return True


def run_pipeline(reprocess: str = None, no_budget_check: bool = False):
    processed = _load_processed()

    # --reprocess: remove matching entry so the file is treated as new
    if reprocess:
        removed = [k for k in processed if reprocess in os.path.basename(k)]
        for k in removed:
            del processed[k]
            print(f"[factory] Removed '{k}' from cache -- will re-process")
        _save_processed(processed)

    all_files = _scan_source_documents()
    new_files = [f for f in all_files if not _already_processed(f, processed)]

    if not new_files:
        print("No new files found in data/source_documents/")
        print("Add .pdf/.html/.txt files and re-run.")
        print("Supported categories: tra/ brela/ osha/ nssf/ wcf/ labour/ immigration/ general/")
        return

    print(f"[factory] Found {len(new_files)} new file(s) to process")

    from src.synthetic.api_utils import check_provider
    check_provider()

    # Import heavy deps only after confirming there's work to do
    from src.synthetic.pdf_extractor     import extract_document
    from src.synthetic.fact_extractor    import extract_facts
    from src.synthetic.question_generator import generate_pairs, get_instruction_index
    from src.synthetic.pair_reviewer     import review_pairs
    from src.synthetic.dataset_builder   import build_dataset, next_batch_num

    # Build semantic dedup index once for the entire run
    index_embeddings, index_texts = get_instruction_index()

    stats = {
        'files_processed': 0,
        'facts_confirmed': 0,
        'pairs_generated': 0,
        'pairs_approved':  0,
        'pairs_flagged':   0,
        'pairs_rejected':  0,
        'batches_written': [],
    }

    for i, file_path in enumerate(new_files):
        remaining = len(new_files) - i
        if not _check_budget(remaining, no_budget_check):
            print(f"[factory] Budget cap reached -- stopping before {os.path.basename(file_path)}")
            break

        print(f"\n[factory] Processing {i + 1}/{len(new_files)}: {file_path}")

        try:
            document = extract_document(file_path)
        except ValueError as e:
            print(f"[factory] Skipping {file_path}: {e}")
            processed[file_path] = {
                'md5': _file_md5(file_path),
                'processed_at': datetime.utcnow().strftime('%Y-%m-%d'),
                'skipped': str(e),
            }
            _save_processed(processed)
            continue
        except Exception as e:
            print(f"[factory] ERROR extracting {file_path}: {e}")
            continue

        facts = extract_facts(document)
        stats['facts_confirmed'] += len(facts)

        if not facts:
            print(f"[factory] No confirmed facts in {os.path.basename(file_path)}")
            print(f"[factory] If new candidates are pending: python run.py approve-facts")
            print(f"[factory] Then: python run.py generate --reprocess {os.path.basename(file_path)}")
            processed[file_path] = {
                'md5': _file_md5(file_path),
                'processed_at': datetime.utcnow().strftime('%Y-%m-%d'),
                'zero_facts': True,
            }
            _save_processed(processed)
            continue

        batch_num    = next_batch_num()
        raw_gen_path = os.path.join(RAW_GENERATED_DIR, f'batch_{batch_num:03d}.jsonl')
        os.makedirs(RAW_GENERATED_DIR, exist_ok=True)

        pairs = generate_pairs(
            facts, document,
            index_embeddings=index_embeddings,
            index_texts=index_texts,
            raw_output_path=raw_gen_path,
        )
        stats['pairs_generated'] += len(pairs)

        if not pairs:
            print(f"[factory] No pairs generated from {os.path.basename(file_path)}")
            processed[file_path] = {
                'md5': _file_md5(file_path),
                'processed_at': datetime.utcnow().strftime('%Y-%m-%d'),
                'zero_pairs': True,
            }
            _save_processed(processed)
            continue

        approved, flagged_pairs, rejected = review_pairs(pairs, batch_num=f'{batch_num:03d}')
        stats['pairs_approved']  += len(approved)
        stats['pairs_flagged']   += len(flagged_pairs)
        stats['pairs_rejected']  += len(rejected)

        if approved:
            out_path = build_dataset(approved, batch_num)
            stats['batches_written'].append(out_path)

        if flagged_pairs:
            flagged_path = os.path.join(FLAGGED_DIR, f'batch_{batch_num:03d}_flagged.jsonl')
            os.makedirs(FLAGGED_DIR, exist_ok=True)
            with open(flagged_path, 'w', encoding='utf-8') as f:
                for p in flagged_pairs:
                    f.write(json.dumps(p, ensure_ascii=False) + '\n')
            print(f"[factory] {len(flagged_pairs)} flagged -> {flagged_path}")
            print(f"[factory] Run: python run.py approve-flags --batch {batch_num:03d}")

        processed[file_path] = {
            'md5': _file_md5(file_path),
            'processed_at': datetime.utcnow().strftime('%Y-%m-%d'),
        }
        _save_processed(processed)
        stats['files_processed'] += 1

    print("\n=== Pipeline complete ===")
    print(f"Files processed:  {stats['files_processed']}")
    print(f"Facts confirmed:  {stats['facts_confirmed']}")
    print(f"Pairs generated:  {stats['pairs_generated']}")
    print(f"Pairs approved:   {stats['pairs_approved']}")
    if stats['pairs_flagged']:
        print(f"Pairs flagged:    {stats['pairs_flagged']} -> run 'python run.py review'")
    if stats['pairs_rejected']:
        print(f"Pairs rejected:   {stats['pairs_rejected']} (see data/raw/reviewed/ for details)")
    if stats['batches_written']:
        print(f"Batches written:  {', '.join(os.path.basename(b) for b in stats['batches_written'])}")
        print("Run 'python run.py upload' to push to HuggingFace")

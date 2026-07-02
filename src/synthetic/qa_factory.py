import asyncio
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
CLEANED_PAIRS_DIR = 'datasets/tier1a/cleaned_pairs'

MONTHLY_CAP              = float(os.environ.get('MONTHLY_BUDGET', '20.0'))
COST_PER_DOCUMENT_BUDGET = float(os.environ.get('COST_PER_DOCUMENT_BUDGET', '0.20'))

# Number of documents processed in parallel per batch. Overridable via env var.
BATCH_SIZE = int(os.environ.get('PIPELINE_BATCH_SIZE', '3'))

SUPPORTED_EXTS = {'.pdf', '.html', '.txt'}


class StreamingBatchWriter:
    """Append approved pairs to a batch file as they are produced, flushing each
    line immediately so pairs are visible on disk in real time and survive a crash.
    Removes the file on close if nothing was written (no empty batches left behind)."""

    def __init__(self, batch_num: int):
        self.batch_num     = batch_num
        self.path          = os.path.join(
            CLEANED_PAIRS_DIR, f'cleaned_pairs_batch_{batch_num:03d}.jsonl')
        self.total_written = 0
        os.makedirs(CLEANED_PAIRS_DIR, exist_ok=True)
        self.file = open(self.path, 'a', encoding='utf-8')

    def write(self, pairs: list):
        for p in pairs:
            self.file.write(json.dumps(p, ensure_ascii=False) + '\n')
            self.file.flush()  # flush immediately so pairs are visible on disk
            self.total_written += 1

    def close(self):
        self.file.close()
        if self.total_written == 0:
            try:
                os.remove(self.path)
            except OSError:
                pass
            print(f'[writer] batch {self.batch_num:03d}: no approved pairs -- file removed')
        else:
            print(f'[writer] batch {self.batch_num:03d} complete: '
                  f'{self.total_written} pairs at {self.path}')


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


def process_document(file_path: str, batch_num: int,
                     index_embeddings, index_texts) -> dict:
    """Process ONE document end-to-end with streaming writes.

    Extract -> confirm facts -> for each fact: generate pairs, review, and write
    approved pairs IMMEDIATELY (not after the whole document). Runs in a worker
    thread under the async orchestrator; touches only batch_num-scoped output files
    (cleaned_pairs_batch_NNN, flagged_batch_NNN, generated/batch_NNN) so parallel
    documents never collide. Shared writes (cost log, pending facts) are lock-guarded
    in their own modules. Returns a result dict the main thread folds into stats."""
    from src.synthetic.pdf_extractor      import extract_document
    from src.synthetic.fact_extractor     import extract_facts
    from src.synthetic.question_generator import generate_pairs_for_fact
    from src.synthetic.pair_reviewer      import review_pairs

    result = {
        'file_path': file_path, 'facts': 0, 'generated': 0,
        'approved': 0, 'flagged': 0, 'rejected': 0,
        'batch_num': batch_num, 'skipped': None, 'error': None,
        'zero_facts': False, 'zero_pairs': False,
    }

    try:
        document = extract_document(file_path)
    except ValueError as e:
        print(f"[factory] Skipping {file_path}: {e}")
        result['skipped'] = str(e)
        return result
    except Exception as e:
        print(f"[factory] ERROR extracting {file_path}: {e}")
        result['error'] = str(e)
        return result

    facts = extract_facts(document)
    result['facts'] = len(facts)
    if not facts:
        print(f"[factory] No confirmed facts in {os.path.basename(file_path)}")
        print(f"[factory] If new candidates are pending: python run.py approve-facts")
        print(f"[factory] Then: python run.py generate --reprocess {os.path.basename(file_path)}")
        result['zero_facts'] = True
        return result

    today      = datetime.utcnow().strftime('%Y-%m-%d')
    source_doc = document.get('source_document', '')
    source_url = document.get('source_url', 'tanzlii.org')

    cur_emb    = index_embeddings
    cur_texts  = list(index_texts)

    writer        = StreamingBatchWriter(batch_num)
    generated_all = []
    flagged_all   = []
    rejected_n    = 0
    dedup_skipped = 0

    for fact in facts:
        pairs, cur_emb, cur_texts, skipped = generate_pairs_for_fact(
            fact, today, source_doc, source_url, cur_emb, cur_texts,
        )
        dedup_skipped += skipped
        if not pairs:
            continue
        generated_all.extend(pairs)

        approved, flagged, rejected = review_pairs(pairs, batch_num=None)
        if approved:
            # Write approved pairs IMMEDIATELY -- do not wait for the full document
            writer.write(approved)
            print(f"[writer] +{len(approved)} pairs written (fact: {fact.get('fact_key')})")
        flagged_all.extend(flagged)
        rejected_n += len(rejected)

    writer.close()

    result['generated'] = len(generated_all)
    result['approved']  = writer.total_written
    result['flagged']   = len(flagged_all)
    result['rejected']  = rejected_n
    print(f"[generator] {document['source_file']}: "
          f"{len(generated_all)} pairs generated, {dedup_skipped} dedup-skipped")

    # Audit trail: raw generated pairs + deterministic review results JSON
    if generated_all:
        os.makedirs(RAW_GENERATED_DIR, exist_ok=True)
        with open(os.path.join(RAW_GENERATED_DIR, f'batch_{batch_num:03d}.jsonl'),
                  'w', encoding='utf-8') as f:
            for p in generated_all:
                f.write(json.dumps(p, ensure_ascii=False) + '\n')
        review_pairs(generated_all, batch_num=f'{batch_num:03d}')  # writes results JSON only

    if not generated_all:
        result['zero_pairs'] = True

    if flagged_all:
        flagged_path = os.path.join(FLAGGED_DIR, f'batch_{batch_num:03d}_flagged.jsonl')
        os.makedirs(FLAGGED_DIR, exist_ok=True)
        with open(flagged_path, 'w', encoding='utf-8') as f:
            for p in flagged_all:
                f.write(json.dumps(p, ensure_ascii=False) + '\n')
        print(f"[factory] {len(flagged_all)} flagged -> {flagged_path}")
        print(f"[factory] Run: python run.py approve-flags --batch {batch_num:03d}")

    return result


def _apply_result(result: dict, stats: dict, processed: dict):
    """Fold a worker result into run stats and the processed-files cache.
    Called on the main thread only -- no concurrent mutation of processed/stats."""
    file_path = result['file_path']

    if result['error']:
        return  # extraction error -- leave unprocessed so it retries next run

    if result['skipped']:
        processed[file_path] = {
            'md5': _file_md5(file_path),
            'processed_at': datetime.utcnow().strftime('%Y-%m-%d'),
            'skipped': result['skipped'],
        }
        return

    stats['facts_confirmed'] += result['facts']
    stats['pairs_generated'] += result['generated']
    stats['pairs_approved']  += result['approved']
    stats['pairs_flagged']   += result['flagged']
    stats['pairs_rejected']  += result['rejected']
    if result['approved']:
        stats['batches_written'].append(f"batch_{result['batch_num']:03d}")

    entry = {
        'md5': _file_md5(file_path),
        'processed_at': datetime.utcnow().strftime('%Y-%m-%d'),
    }
    if result['zero_facts']:
        entry['zero_facts'] = True
    elif result['zero_pairs']:
        entry['zero_pairs'] = True
    processed[file_path] = entry
    stats['files_processed'] += 1


async def _process_document_async(file_path, batch_num, index_embeddings, index_texts):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, process_document, file_path, batch_num, index_embeddings, index_texts)


async def _run_pipeline_async(new_files, no_budget_check, index_embeddings, index_texts,
                              processed, stats):
    from src.synthetic.dataset_builder import next_batch_num

    for i in range(0, len(new_files), BATCH_SIZE):
        remaining = len(new_files) - i
        if not _check_budget(remaining, no_budget_check):
            print(f"[factory] Budget cap reached -- stopping (>= {remaining} document(s) unprocessed)")
            break

        batch = new_files[i:i + BATCH_SIZE]
        # Pre-assign batch numbers BEFORE launching, so parallel workers never race
        # on next_batch_num() / overwrite each other's output files.
        base = next_batch_num()
        print(f"\n[factory] Processing batch {i // BATCH_SIZE + 1}: "
              f"{[os.path.basename(f) for f in batch]} -> "
              f"batches {[f'{base + j:03d}' for j in range(len(batch))]}")

        tasks = [
            _process_document_async(f, base + j, index_embeddings, index_texts)
            for j, f in enumerate(batch)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for f, res in zip(batch, results):
            if isinstance(res, Exception):
                print(f"[factory] ERROR in {os.path.basename(f)}: {res}")
                continue
            _apply_result(res, stats, processed)
            _save_processed(processed)  # persist after each doc -- crash-safe progress


def generate_from_locked_facts(subdomain_filter: str = None,
                               key_filter: list = None,
                               limit: int = 50):
    """Generate Q&A pairs directly from locked_facts entries.

    Bypasses document extraction. Each locked fact is used as a seed for pair
    generation via the same LLM + 6-check review path as the document pipeline.
    Output goes through the normal StreamingBatchWriter.
    """
    from src.synthetic.dataset_builder  import next_batch_num
    from src.synthetic.question_generator import generate_pairs_for_fact, get_instruction_index
    from src.synthetic.pair_reviewer      import review_pairs

    LOCKED_FACTS_PATH = 'scripts/locked_facts.json'
    with open(LOCKED_FACTS_PATH, encoding='utf-8') as f:
        locked_facts = json.load(f)

    # Subdomain -> (source_doc_hint, source_url, fact_key_prefixes)
    # Prefix matching is case-insensitive against lowercased key
    SUBDOMAIN_META = {
        'nssf_contributions': ('data/source_documents/nssf/nssf_act_cap50.pdf',     'nssf.or.tz',
                               ['nssf', 'unpaid', 'minimum', 'pensionable', 'duration', 'maternity',
                                'employer_notification', 'fund_payment', 'fine', 'imprisonment', 'contribution']),
        'gn487a':             ('data/source_documents/immigration/gn487a_official_gazette.pdf', 'immigration.go.tz',
                               ['gn487a', 'business_licensing', 'order_made', 'prohibited',
                                'tanzania_citizenship', 'offence', 'penalty']),
        'paye':               ('data/source_documents/tra/tra_paye_sw.html',          'tra.go.tz',
                               ['paye', 'p45']),
        'sdl_compliance':     ('data/source_documents/tra/tra_sdl_sw.txt',            'tra.go.tz',
                               ['sdl']),
        'vat_registration':   ('data/source_documents/tra/tra_vat_registration_sw.html', 'tra.go.tz',
                               ['vat_registration', 'vat_threshold', 'vat_standard', 'vat_late',
                                'vat_reduced', 'vat_zero', 'vat_return', 'vat_deferment',
                                'vat_notification', 'vat_filing']),
        'vat_withholding':    ('data/source_documents/tra/tra_withholding_tax_sw.html', 'tra.go.tz',
                               ['vat_withholding', 'vat_withhol']),
        'wcf_compliance':     ('data/source_documents/wcf/wcf_michango.html',         'wcf.go.tz',
                               ['wcf', 'workers']),
        'brela_registration': ('data/source_documents/brela/brela_faq_official.pdf',  'brela.go.tz',
                               ['brela', 'company', 'annual_return', 'name_similarity',
                                'late_filing', 'memorandum', 'beneficial', 'minimum_directors',
                                'minimum_shareholders', 'registration_certificate']),
        'osha_registration':  ('data/source_documents/osha/osha_maswali.html',        'osha.go.tz',
                               ['osha', 'osiha', 'health_and_safety', 'risk_assessment']),
        'efd_compliance':     ('data/source_documents/tra/tra_efd_index.html',        'tra.go.tz',
                               ['efd']),
    }

    # Select target facts
    target_facts = []
    for key, fact in locked_facts.items():
        if key == '_meta':
            continue
        if key_filter and key not in key_filter:
            continue
        if subdomain_filter:
            meta = SUBDOMAIN_META.get(subdomain_filter, ('', 'tra.go.tz', []))
            prefixes = meta[2]
            key_lower = key.lower()
            if not any(key_lower.startswith(p.lower()) or key_lower == p.lower() for p in prefixes):
                continue
        target_facts.append((key, fact))
        if len(target_facts) >= limit:
            break

    if not target_facts:
        print(f'[generate-from-facts] No matching facts found for subdomain={subdomain_filter!r} key_filter={key_filter}')
        print(f'[generate-from-facts] Available subdomains: {list(SUBDOMAIN_META)}')
        return

    print(f'[generate-from-facts] {len(target_facts)} facts selected (subdomain={subdomain_filter}, limit={limit})')

    from src.synthetic.api_utils import check_provider
    check_provider()

    index_embeddings, index_texts = get_instruction_index()
    today   = datetime.utcnow().strftime('%Y-%m-%d')
    batch_n = next_batch_num()
    writer  = StreamingBatchWriter(batch_n)
    cur_emb, cur_texts = index_embeddings, list(index_texts)

    stats = {'generated': 0, 'approved': 0, 'flagged': 0, 'rejected': 0, 'dedup_skipped': 0}
    flagged_all = []

    for fact_key, fact_data in target_facts:
        # Look up subdomain meta for source routing
        meta = SUBDOMAIN_META.get(subdomain_filter, ('', 'tra.go.tz', []))
        source_doc = meta[0]
        source_url = meta[1]

        value = fact_data.get('correct_value', '') if isinstance(fact_data, dict) else str(fact_data)

        fact = {
            'fact_key':       fact_key,
            'value':          value,
            'unit':           '',
            'source_section': fact_data.get('section', '') if isinstance(fact_data, dict) else '',
            'source_document': source_doc,
        }

        try:
            pairs, cur_emb, cur_texts, skipped = generate_pairs_for_fact(
                fact, today, source_doc, source_url, cur_emb, cur_texts,
            )
            stats['dedup_skipped'] += skipped
            stats['generated']     += len(pairs)
            if not pairs:
                continue

            approved, flagged, rejected = review_pairs(pairs, batch_num=None)
            if approved:
                writer.write(approved)
                stats['approved'] += len(approved)
            flagged_all.extend(flagged)
            stats['flagged']  += len(flagged)
            stats['rejected'] += len(rejected)
        except Exception as e:
            print(f'[generate-from-facts] ERROR on {fact_key}: {e}')

    writer.close()

    if flagged_all:
        flagged_path = os.path.join(FLAGGED_DIR, f'batch_{batch_n:03d}_flagged.jsonl')
        os.makedirs(FLAGGED_DIR, exist_ok=True)
        with open(flagged_path, 'w', encoding='utf-8') as f:
            for p in flagged_all:
                f.write(json.dumps(p, ensure_ascii=False) + '\n')
        print(f'[generate-from-facts] {len(flagged_all)} flagged -> {flagged_path}')
        print(f'[generate-from-facts] Run: python run.py approve-flags --batch {batch_n:03d}')

    print(f'\n[generate-from-facts] Done — batch {batch_n:03d}')
    print(f'  facts targeted:  {len(target_facts)}')
    print(f'  pairs generated: {stats["generated"]}')
    print(f'  pairs approved:  {stats["approved"]}')
    print(f'  pairs flagged:   {stats["flagged"]}')
    print(f'  pairs rejected:  {stats["rejected"]}')
    print(f'  dedup skipped:   {stats["dedup_skipped"]}')
    if stats['approved']:
        print(f'  Run: python run.py upload')


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

    print(f"[factory] Found {len(new_files)} new file(s) to process "
          f"({BATCH_SIZE} in parallel per batch)")

    from src.synthetic.api_utils import check_provider
    check_provider()

    # Import heavy deps only after confirming there's work to do
    from src.synthetic.question_generator import get_instruction_index

    # Build semantic dedup index once for the entire run (shared, read-only base)
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

    asyncio.run(_run_pipeline_async(
        new_files, no_budget_check, index_embeddings, index_texts, processed, stats))

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
        print(f"Batches written:  {', '.join(stats['batches_written'])}")
        print("Run 'python run.py upload' to push to HuggingFace")

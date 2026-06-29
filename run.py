import sys
import os
import json
import re
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent


def cmd_status(args):
    cleaned   = ROOT / 'datasets' / 'tier1a' / 'cleaned_pairs'
    sft_train = ROOT / 'datasets' / 'tier1a' / 'sft' / 'train_sft.jsonl'
    sft_val   = ROOT / 'datasets' / 'tier1a' / 'sft' / 'val_sft.jsonl'
    source_docs = ROOT / 'data' / 'source_documents'
    flagged     = ROOT / 'data' / 'flagged'
    pending     = flagged / 'new_facts_pending.json'
    cost_log    = ROOT / 'data' / 'cost_log.jsonl'

    total_pairs = 0
    batch_files = []
    if cleaned.exists():
        for f in sorted(cleaned.glob('*.jsonl')):
            count = sum(1 for line in open(f, encoding='utf-8') if line.strip())
            total_pairs += count
            batch_files.append((f.name, count))

    train_count = sum(1 for l in open(sft_train, encoding='utf-8') if l.strip()) if sft_train.exists() else 0
    val_count   = sum(1 for l in open(sft_val,   encoding='utf-8') if l.strip()) if sft_val.exists()   else 0

    source_count = sum(1 for f in source_docs.rglob('*') if f.is_file()) if source_docs.exists() else 0

    flagged_count = 0
    if flagged.exists():
        for f in flagged.glob('*_flagged.jsonl'):
            flagged_count += sum(1 for l in open(f, encoding='utf-8') if l.strip())

    pending_count = 0
    if pending.exists():
        try:
            data = json.load(open(pending, encoding='utf-8'))
            pending_count = len(data) if isinstance(data, list) else 0
        except Exception:
            pass

    total_cost = 0.0
    if cost_log.exists():
        month_str = datetime.utcnow().strftime('%Y-%m')
        for line in open(cost_log, encoding='utf-8'):
            try:
                entry = json.loads(line.strip())
                if entry.get('timestamp', '').startswith(month_str):
                    total_cost += entry.get('cost_usd', 0.0)
            except Exception:
                pass

    print("=== AFRICA GIANTS — Pipeline Status ===")
    print(f"Cleaned pairs total:  {total_pairs}")
    for name, count in batch_files:
        print(f"  {name}: {count} pairs")
    print(f"SFT train pairs:      {train_count}")
    print(f"SFT val pairs:        {val_count}")
    print(f"Source documents:     {source_count}")
    print(f"Flagged (pending):    {flagged_count}")
    print(f"New fact candidates:  {pending_count}")
    print(f"API cost this month:  ${total_cost:.4f}")
    print()
    print("Production:")
    print("  Adapter:   prospAprospA007/africa-giants-adapter-v8")
    print("  Dataset:   prospAprospA007/africa-giants-dataset")
    print("  Endpoint:  https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run")
    print("  WhatsApp:  +255637809070 via Wappfly")


def cmd_generate(args):
    try:
        from src.synthetic.qa_factory import run_pipeline
    except ImportError:
        print("[generate] Phase 3 not yet implemented.")
        print("Build src/synthetic/ modules first (Phase 3 in do.md).")
        sys.exit(1)
    run_pipeline(reprocess=args.reprocess, no_budget_check=args.no_budget_check)


def cmd_build_rag(args):
    print("[build-rag] RAG index lives in Cerebrium persistent storage.")
    print("The index rebuilds automatically on cold start when locked_facts.json changes.")
    print("To force a rebuild: deploy to Cerebrium after updating locked_facts.json.")
    print("  cd chike-inference && cerebrium deploy")


def cmd_upload(args):
    try:
        from scripts.upload_dataset import upload
        upload()
    except ImportError:
        print("[upload] Phase 4 not yet implemented.")
        print("Build scripts/upload_dataset.py first (Phase 4 in do.md).")
        sys.exit(1)


def cmd_review(args):
    flagged = ROOT / 'data' / 'flagged'
    if not flagged.exists():
        print("[review] data/flagged/ directory not found.")
        return

    batch_files = sorted(flagged.glob('*_flagged.jsonl'))
    if not batch_files:
        print("[review] No flagged pairs. All pairs either approved or rejected.")
    else:
        print("=== Flagged pairs awaiting review ===")
        for f in batch_files:
            count = sum(1 for l in open(f, encoding='utf-8') if l.strip())
            m = re.search(r'batch_(\d+)', f.name)
            batch_num = m.group(1) if m else '???'
            print(f"  {f.name}: {count} pairs")
            print(f"    Run: python run.py approve-flags --batch {batch_num}")

    pending = flagged / 'new_facts_pending.json'
    if pending.exists():
        try:
            data = json.load(open(pending, encoding='utf-8'))
            if data:
                print(f"\n  new_facts_pending.json: {len(data)} fact candidates")
                print("    Run: python run.py approve-facts")
        except Exception:
            pass


def cmd_approve_facts(args):
    pending = ROOT / 'data' / 'flagged' / 'new_facts_pending.json'
    locked  = ROOT / 'scripts' / 'locked_facts.json'

    if not pending.exists():
        print("[approve-facts] No new fact candidates in data/flagged/new_facts_pending.json")
        return

    try:
        candidates = json.load(open(pending, encoding='utf-8'))
    except Exception as e:
        print(f"[approve-facts] Could not read new_facts_pending.json: {e}")
        sys.exit(1)

    if not candidates:
        print("[approve-facts] new_facts_pending.json is empty.")
        return

    try:
        locked_facts = json.load(open(locked, encoding='utf-8'))
    except Exception:
        locked_facts = {}

    approved_keys = []
    source_names  = set()

    print(f"=== Approve new fact candidates ({len(candidates)} pending) ===")
    print("Press [a]pprove or [r]eject for each. Press [q] to quit early.\n")

    for i, candidate in enumerate(candidates):
        fact_key = candidate.get('fact_key', f'fact_{i}')
        value    = candidate.get('value', '')
        unit     = candidate.get('unit', '')
        source   = candidate.get('source_section', '')
        eff_date = candidate.get('effective_date', '')
        source_names.add(candidate.get('source_document', 'unknown'))

        print(f"[{i+1}/{len(candidates)}] {fact_key}: {value} {unit}")
        print(f"  Source:  {source}")
        if eff_date:
            print(f"  Effective: {eff_date}")

        while True:
            choice = input("  [a]pprove / [r]eject / [q]uit: ").strip().lower()
            if choice in ('a', 'r', 'q'):
                break

        if choice == 'q':
            print(f"\n[approve-facts] Stopped at {i+1}/{len(candidates)}. Re-run to continue.")
            break
        if choice == 'a':
            candidate_value = f"{value} {unit}".strip()
            if fact_key in locked_facts:
                # Existing keys are protected — never overwrite a richer locked entry.
                existing = locked_facts[fact_key]
                existing_value = (existing.get('correct_value', '')
                                  if isinstance(existing, dict) else str(existing))
                print(f"  [approve-facts] WARNING: fact_key '{fact_key}' already exists in locked_facts.json")
                print(f"  [approve-facts] Existing entry is richer than the candidate — skipping overwrite")
                if existing_value:
                    print(f"  [approve-facts] Candidate value ({candidate_value}) "
                          f"matches existing value ({existing_value}) — no conflict")
            else:
                locked_facts[fact_key] = candidate_value
                approved_keys.append(fact_key)
                print(f"  -> Approved: {fact_key}")
        else:
            print(f"  -> Rejected: {fact_key}")

    if not approved_keys:
        print("[approve-facts] No facts approved.")
        return

    with open(locked, 'w', encoding='utf-8') as f:
        json.dump(locked_facts, f, indent=2, ensure_ascii=False)
    print(f"\n[approve-facts] {len(approved_keys)} facts written to scripts/locked_facts.json")

    source_str = ', '.join(sorted(source_names)) or 'unknown'
    date_str   = datetime.utcnow().strftime('%Y-%m-%d')
    msg = f"locked_facts: approved {len(approved_keys)} facts from {source_str} on {date_str}"
    try:
        subprocess.run(['git', 'add', 'scripts/locked_facts.json'], check=True, cwd=ROOT)
        subprocess.run(['git', 'commit', '-m', msg], check=True, cwd=ROOT)
        print(f"[approve-facts] Git commit: {msg}")
    except subprocess.CalledProcessError as e:
        print(f"[approve-facts] Warning: git commit failed ({e}).")
        print(f"Run manually: git add scripts/locked_facts.json && git commit")

    remaining = [c for c in candidates if c.get('fact_key') not in approved_keys]
    with open(pending, 'w', encoding='utf-8') as f:
        json.dump(remaining, f, indent=2, ensure_ascii=False)
    if remaining:
        print(f"[approve-facts] {len(remaining)} candidates remain in new_facts_pending.json")


def cmd_approve_flags(args):
    batch_num     = args.batch.zfill(3)
    flagged_file  = ROOT / 'data' / 'flagged'  / f'batch_{batch_num}_flagged.jsonl'
    approved_file = ROOT / 'data' / 'reviewed' / f'batch_{batch_num}_approved.jsonl'
    progress_file = ROOT / 'data' / 'flagged'  / f'batch_{batch_num}_progress.json'

    if not flagged_file.exists():
        print(f"[approve-flags] No flagged file found: {flagged_file}")
        sys.exit(1)

    pairs = [json.loads(l) for l in open(flagged_file, encoding='utf-8') if l.strip()]
    if not pairs:
        print("[approve-flags] Flagged file is empty.")
        return

    start_idx = 0
    if progress_file.exists() and not args.auto_approve_all:
        try:
            progress = json.load(open(progress_file, encoding='utf-8'))
            start_idx = progress.get('next_index', 0)
            print(f"[approve-flags] Resuming from pair {start_idx + 1}/{len(pairs)}")
        except Exception:
            pass

    approved_file.parent.mkdir(parents=True, exist_ok=True)

    def get_keypress():
        if args.auto_approve_all:
            return 'a'
        try:
            import msvcrt
            return msvcrt.getwch().lower()
        except ImportError:
            return input().strip().lower()[:1] or 's'

    approved_out = open(approved_file, 'a', encoding='utf-8')
    i = start_idx
    try:
        while i < len(pairs):
            pair = dict(pairs[i])
            failed_checks = pair.pop('_failed_checks', [])
            print(f"\n[{i+1}/{len(pairs)}]")
            print(f"INSTRUCTION:   {pair.get('instruction', '')}")
            print(f"OUTPUT:        {pair.get('output', '')[:200]}")
            if failed_checks:
                print(f"FAILED CHECKS: {'; '.join(str(c) for c in failed_checks)}")
            if not args.auto_approve_all:
                print("[a]pprove  [r]eject  [s]kip  [q]uit: ", end='', flush=True)
            key = get_keypress()
            print(key)

            if key == 'q':
                prog = {'next_index': i, 'saved_at': datetime.utcnow().isoformat()}
                json.dump(prog, open(progress_file, 'w', encoding='utf-8'), indent=2)
                print(f"\n[approve-flags] Progress saved. Re-run --batch {batch_num} to continue.")
                break
            elif key == 'a':
                approved_out.write(json.dumps(pair, ensure_ascii=False) + '\n')
                print("  -> Approved")
                i += 1
            elif key == 'r':
                print("  -> Rejected")
                i += 1
            else:
                print("  -> Skipped")
                i += 1
    finally:
        approved_out.close()

    if i >= len(pairs):
        if progress_file.exists():
            progress_file.unlink()
        print(f"\n[approve-flags] Done — {i - start_idx} pairs reviewed.")
        print("Run 'python run.py upload' to push approved pairs to HuggingFace.")


def main():
    parser = argparse.ArgumentParser(
        description="AFRICA GIANTS — Autonomous Dataset Pipeline v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  generate                       Process new source documents in data/source_documents/
  generate --reprocess FILENAME  Force re-processing of a specific document
  build-rag                      Rebuild RAG index (redeploy Cerebrium to activate)
  upload                         Rebuild SFT files and push dataset to HuggingFace
  review                         Show pending flagged pairs and new fact candidates
  status                         Show pipeline state and pair counts
  approve-facts                  Approve new fact candidates interactively
  approve-flags --batch NNN      Review flagged pairs one-by-one interactively

Human workflow (after all phases built):
  1. Drop PDF/HTML/TXT into data/source_documents/{category}/
  2. python run.py generate
  3. python run.py review
  4. python run.py approve-flags --batch NNN
  5. python run.py approve-facts
  6. python run.py upload
  7. Run Kaggle notebook manually
""",
    )
    sub = parser.add_subparsers(dest='command')

    gen = sub.add_parser('generate', help='Process new source documents -> cleaned_pairs/')
    gen.add_argument('--reprocess', metavar='FILENAME', default=None,
                     help='Force re-processing of a specific file')
    gen.add_argument('--no-budget-check', action='store_true',
                     help='Skip per-document cost cap check')

    sub.add_parser('build-rag',     help='Rebuild RAG index from locked_facts.json')
    sub.add_parser('upload',        help='Rebuild SFT and upload dataset to HuggingFace')
    sub.add_parser('review',        help='Show pending flagged pairs for inspection')
    sub.add_parser('status',        help='Show pipeline state and pair counts')
    sub.add_parser('approve-facts', help='Approve new fact candidates interactively')

    af = sub.add_parser('approve-flags', help='Review flagged pairs one-by-one')
    af.add_argument('--batch', required=True, metavar='NNN',
                    help='Batch number to review (e.g. 014)')
    af.add_argument('--auto-approve-all', action='store_true',
                    help='Approve all without prompting (testing only)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    {
        'generate':      cmd_generate,
        'build-rag':     cmd_build_rag,
        'upload':        cmd_upload,
        'review':        cmd_review,
        'status':        cmd_status,
        'approve-facts': cmd_approve_facts,
        'approve-flags': cmd_approve_flags,
    }[args.command](args)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""v10: quarantine corpus rows asserting the wrong Memorandum & Articles filing fee.

Root cause: memorandum_articles_of_association_filing_fee was corrected 2026-09-02 (see
PROGRESS.md and the fact's own correction_note) -- direct read of BRELA's official fee page
names TZS 66,000 specifically for Memorandum and Articles of Association filing, distinct from
the generic TZS 22,000-per-document rate (a different, separately-confirmed fee). The fact was
a bare, never-verified string before this pass; this is a first verification, not a correction
of a previously-checked fact.

R18: committed before running. Artifact: eval/results/corpus_correction_v10.json
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

QUARANTINE_PATH = os.path.join(
    REPO, 'datasets', 'tier1a', 'rejected',
    'memorandum_articles_fee_stale_22000_quarantine_2026_09_02.jsonl')
OUT = os.path.join(REPO, 'eval', 'results', 'corpus_correction_v10.json')

_BAD_INSTRUCTION = (
    'Eti, hii ada ya ku-file Memorandum and Articles of Association, ni shilingi ngapi kwa kila hati?')
_BAD_INSTRUCTIONS = {
    _BAD_INSTRUCTION: 'STALE_MEMORANDUM_ARTICLES_FEE: asserts the generic 22,000-per-document '
                       'rate for Memorandum and Articles of Association specifically; BRELA\'s '
                       'own fee page names 66,000 for this document specifically.',
}


def _instruction_text(obj):
    return (obj.get('instruction') or obj.get('question_sw') or '').strip()


def _row_is_defect(line):
    try:
        obj = json.loads(line)
    except Exception:
        return None, None
    instr = _instruction_text(obj)
    if instr in _BAD_INSTRUCTIONS:
        return True, _BAD_INSTRUCTIONS[instr]
    return False, None


def main():
    import glob
    files = sorted(set(
        glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True) +
        glob.glob(os.path.join(REPO, 'data', '**', '*.jsonl'), recursive=True)
    ))

    quarantined = []
    per_file_removed = {}
    for fp in files:
        norm = fp.replace('\\', '/')
        if '/rejected/' in norm:
            continue
        with io.open(fp, encoding='utf-8') as f:
            lines = f.readlines()
        kept = []
        removed_here = 0
        for line in lines:
            stripped = line.rstrip('\n')
            if not stripped.strip():
                kept.append(line)
                continue
            is_bad, reason = _row_is_defect(stripped)
            if is_bad:
                quarantined.append({
                    'source_file': os.path.relpath(fp, REPO).replace('\\', '/'),
                    'defect_class': 'MEMORANDUM_ARTICLES_FEE_STALE_22000',
                    'reason': reason,
                    'row': json.loads(stripped),
                })
                removed_here += 1
            else:
                kept.append(line)
        if removed_here:
            with io.open(fp, 'w', encoding='utf-8', newline='\n') as f:
                f.writelines(kept)
            per_file_removed[os.path.relpath(fp, REPO).replace('\\', '/')] = removed_here

    if quarantined:
        os.makedirs(os.path.dirname(QUARANTINE_PATH), exist_ok=True)
        with io.open(QUARANTINE_PATH, 'w', encoding='utf-8') as f:
            for row in quarantined:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')

    remaining = 0
    for fp in files:
        norm = fp.replace('\\', '/')
        if '/rejected/' in norm:
            continue
        with io.open(fp, encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                is_bad, _ = _row_is_defect(line.rstrip('\n'))
                if is_bad:
                    remaining += 1

    report = {
        'measured': '2026-09-02',
        'harness': 'scripts/correct_corpus_defects_v10.py',
        'defect_class': 'MEMORANDUM_ARTICLES_FEE_STALE_22000',
        'total_rows_quarantined': len(quarantined),
        'per_file_removed': per_file_removed,
        'quarantine_file': os.path.relpath(QUARANTINE_PATH, REPO).replace('\\', '/'),
        'remaining_live_after_fix': remaining,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

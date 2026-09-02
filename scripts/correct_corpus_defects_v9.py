# -*- coding: utf-8 -*-
"""v9: quarantine corpus rows that misstate the VAT-deferment 30 June 2026 cutoff.

Root cause: vat_deferment_limit_date was corrected 2026-09-02 (see PROGRESS.md and the fact's
own correction_note) -- the 30 June 2026 date is a PAST cutoff for IMPORTED capital goods only
(Finance Act 2023 s.65(b), unrevoked by FA2024/2025/2026, all read directly), not an upcoming
deadline and not scoped to all capital goods. Four distinct corpus Q/A pairs (11 row-copies
across cleaned_pairs, flagged, reviewed, and the live train_sft.jsonl/val_sft.jsonl) assert or
imply the opposite: that 30 June 2026 is a live/future deadline, or that imported-goods
deferment is unconditionally currently allowed with no cutoff. Quarantined rather than
corrected in place -- rewriting free-text Swahili answers ad hoc outside the generation
pipeline is exactly what R9's spirit warns against; regeneration is a follow-up, not done here.

R18: committed before running. Artifact: eval/results/corpus_correction_v9.json
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
    'vat_deferment_stale_cutoff_framing_quarantine_2026_09_02.jsonl')
OUT = os.path.join(REPO, 'eval', 'results', 'corpus_correction_v9.json')

# Exact instruction-text match, not fuzzy regex -- every offending row was individually read in
# full (see PROGRESS.md) before being listed here; no row is caught by accident.
_BAD_INSTRUCTIONS = {
    'Nilisikia kuna tarehe maalum ya mwisho kwa ajili ya VAT deferment, nina uhakika na hiyo tarehe hadi lini?':
        'STALE_CUTOFF_UNSCOPED: states "30 June 2026" as the deferment end date with no scope '
        '(imported vs. locally manufactured) and no indication the date has already passed.',
    'Mpango wa VAT deferment unaisha lini?':
        'STALE_CUTOFF_UNSCOPED: same defect -- unscoped, tense-ambiguous cutoff assertion.',
    'Nilisikia kuna uhamisho wa kulipa VAT, mbona mimi sijui chochote kuhusu hilo?':
        'STALE_CUTOFF_PRESENT_TENSE: "unaruhusiwa hadi tarehe 30 Juni 2026" (is allowed until '
        '30 June 2026) -- present-tense framing implying an open, ongoing allowance with a '
        'still-future deadline; also unscoped to imported goods specifically even though the '
        'question is about imports.',
    'VAT Deferment ni nini hasa maana yake katika biashara yangu?':
        'STALE_CUTOFF_PRESENT_TENSE_SCOPED_WRONG: explicitly scoped to imported goods '
        '("bidhaa unazoingiza nchini") and asserts deferment for them is currently allowed '
        '("mfumo unaokuruhusu"), which is the specific claim FA2023-2026 (read directly) '
        'contradict for the imported branch after 30 June 2026.',
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
                    'defect_class': 'VAT_DEFERMENT_STALE_CUTOFF_FRAMING',
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

    # Verification-after: re-scan everything (including the file just written) for the same
    # bad instructions -- must be zero live, matching the discipline of v7/v8.
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
        'harness': 'scripts/correct_corpus_defects_v9.py',
        'defect_class': 'VAT_DEFERMENT_STALE_CUTOFF_FRAMING',
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

# -*- coding: utf-8 -*-
"""v3 -- the EFD-threshold fabrication, the largest single defect found in this line of work.

WHY THIS EXISTS. Re-verifying `efd_threshold_tzs_11m` against statute (2026-08-29) found the
locked fact itself had no basis: Tax Administration Act Cap.438 s.44 (renumbered from s.36 by
Finance Act 2023 s.54) makes fiscal-receipt issuance the DEFAULT for everyone, with exemption
ONLY by Commissioner-General public notice naming a class -- NO turnover figure appears anywhere
in the Act. TZS 11,000,000 and TZS 14,000,000 both exist in the Income Tax Act, but as adjacent
band edges of the PRESUMPTIVE INCOME TAX table (First Schedule para.2(3)), a different provision
entirely. The founder asked whether this defect, like the mining fabrication and the wcf-deadline
compression before it, was already baked into the corpus. It was, at far greater scale: **58 raw
occurrences**, the largest of the three defect classes found this session, and unlike the other
two, this one reaches `val_sft.jsonl` (1 row) -- so validation loss has been rewarding this
specific wrong claim, the same shape as the 2026-08-25 PAYE-relief/band-9 defects.

WHAT IS BEING QUARANTINED. Any row asserting an EFD requirement/threshold is tied to TZS
11,000,000 or TZS 14,000,000 turnover, in either digit form ("11,000,000") or spelled Swahili
form ("milioni 11") -- both forms are used across the corpus, and a first narrower digit-only
regex missed 14 of the 17 rows found by sampling before the full pattern was written. Every
sampled hit read in context before this pattern was finalized (see PROGRESS.md) -- there is no
correct sentence in Tanzanian law that ties an EFD verdict to either figure, so unlike the WCF
7-day pattern in v2, no "correct partial match" guard is needed for the core claim. A guard is
still included for a fact that EXPLICITLY REJECTS the figure (the corrected fact's own wording,
"REJECT both TZS 11,000,000 and TZS 14,000,000"), so a future correct pair is never quarantined
for stating what NOT to believe.

Same disposition as v1 and v2 (R20): quarantine, don't rewrite. The correct answer is not a
number swap -- it's a structurally different sentence ("yes by default, unless a named CG
notice exempts your class"), and generating that mechanically here risks manufacturing a
plausible replacement silently. R13 (`run.py generate-from-facts`) regenerates from the now-
corrected `efd_threshold_tzs_11m` / `efd_not_every_business`.

Run with --dry-run first. R18: committed before it runs.
Artifact: eval/results/corpus_correction_v3.json
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, 'eval', 'results', 'corpus_correction_v3.json')
QUARANTINE = os.path.join(REPO, 'datasets', 'tier1a', 'rejected',
                          'efd_threshold_fabrication_quarantine_2026_08_29.jsonl')

NUM = r'(?:11|14)\s*,?\s*0{3}\s*,?\s*0{3}|milioni\s*(?:11|14)|(?:11|14)\s*million'
EFD = r'\befd\b|mashine ya risiti|fiscal device|risiti za efd'
EFDTHRESH = re.compile(rf'(?:{EFD})[^.?!]{{0,90}}(?:{NUM})|(?:{NUM})[^.?!]{{0,90}}(?:{EFD})', re.I)

# A fact/pair that REJECTS the figure ITSELF ("TZS 11,000,000 SIYO kizingiti") is correct and
# must survive -- exactly the corrected fact's own wording. THIS GUARD WAS PROVEN UNSAFE ONCE
# ALREADY (2026-08-29, before this file was ever run for real): a first draft matched generic
# "si"/"kizingiti" anywhere within 30 chars, which let 6 real defect rows through, because
# "Kizingiti sahihi ni TZS milioni 11 -- si 40M" ("The correct threshold IS 11M -- not 40M")
# rejects a DIFFERENT number (40M) while ASSERTING the exact defect (11M). The rejection word
# must now sit immediately against THE NUMBER ITSELF, not merely near the word "kizingiti" --
# so a statement that affirms 11M while rejecting something else cannot satisfy it.
REJECTION_GUARD = re.compile(
    rf'(?:{NUM})[^.?!]{{0,20}}(si|siyo|sio|sivyo)\s*(ni\s*)?kizingiti'
    rf'|(?:{NUM})[^.?!]{{0,20}}(is not|isn\'t|not)\s*(the\s*)?(efd\s*)?threshold'
    rf'|(si|siyo|sio|sivyo)\s*kizingiti[^.?!]{{0,20}}(?:{NUM})'
    rf'|(is not|isn\'t|not)\s*(the\s*)?(efd\s*)?threshold[^.?!]{{0,20}}(?:{NUM})', re.I)

KEEP = {
    'scripts/correct_corpus_defects.py': 'v1, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v2.py': 'v2, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v3.py': 'this file -- would rewrite its own patterns/docstring',
}


def rel(p):
    return os.path.relpath(p, REPO).replace('\\', '/')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    dry = args.dry_run
    report = {'measured': '2026-08-29', 'dry_run': dry,
              'harness': 'scripts/correct_corpus_defects_v3.py',
              'companion_of': ['scripts/correct_corpus_defects.py (v1)',
                                'scripts/correct_corpus_defects_v2.py (v2)'],
              'quarantine_file': rel(QUARANTINE)}

    quarantined, per_file, skipped_rejection = [], Counter(), []
    for f in sorted(glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True)):
        r = rel(f)
        if r in KEEP or r == rel(QUARANTINE):
            continue
        lines = open(f, encoding='utf-8').read().splitlines()
        keep_lines, moved = [], 0
        for i, l in enumerate(lines):
            if not l.strip():
                keep_lines.append(l)
                continue
            hit = bool(EFDTHRESH.search(l))
            if hit and REJECTION_GUARD.search(l):
                skipped_rejection.append({'file': r, 'line': i,
                                          'why': 'rejects the figure rather than asserting it '
                                                 '-- a correct statement, not the defect',
                                          'text': l[:200]})
                hit = False
            if hit:
                try:
                    row = json.loads(l)
                except Exception:
                    keep_lines.append(l)
                    continue
                row['_quarantine'] = {
                    'from_file': r, 'from_line': i, 'quarantined': '2026-08-29',
                    'reasons': [
                        'asserts an EFD requirement/threshold tied to TZS 11,000,000 or '
                        'TZS 14,000,000 turnover -- Tax Administration Act Cap.438 s.44 '
                        '(renumbered from s.36 by Finance Act 2023 s.54) makes EFD the '
                        'default for everyone with no turnover figure anywhere in the Act; '
                        'exemption is only by Commissioner-General public notice naming a '
                        'class. 11M/14M are presumptive-income-tax band edges (Income Tax '
                        'Act First Schedule para.2(3)), a different provision entirely '
                        '(re-verified 2026-08-29).'],
                    'disposition': 'quarantined rather than rewritten -- same reasoning as v1/v2 '
                                   '(R20): the correct answer is a structurally different '
                                   'sentence, not a number swap. R13 '
                                   '(run.py generate-from-facts) regenerates from the corrected '
                                   'efd_threshold_tzs_11m / efd_not_every_business.',
                }
                quarantined.append(row)
                moved += 1
            else:
                keep_lines.append(l)
        if moved:
            per_file[r] = moved
            if not dry:
                with open(f, 'w', encoding='utf-8', newline='\n') as fh:
                    fh.write('\n'.join(keep_lines) + ('\n' if keep_lines else ''))
    if quarantined and not dry:
        os.makedirs(os.path.dirname(QUARANTINE), exist_ok=True)
        with open(QUARANTINE, 'w', encoding='utf-8', newline='\n') as fh:
            for row in quarantined:
                fh.write(json.dumps(row, ensure_ascii=False) + '\n')

    report['quarantine'] = {'rows': len(quarantined), 'by_file': dict(per_file)}
    report['skipped_because_REJECTS_THE_FIGURE'] = skipped_rejection

    left = 0
    for f in glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True):
        if rel(f) == rel(QUARANTINE):
            continue
        for l in open(f, encoding='utf-8'):
            if EFDTHRESH.search(l) and not REJECTION_GUARD.search(l):
                left += 1
    report['verification_after'] = {
        'datasets_rows_still_asserting_efd_11m_or_14m_threshold': left,
        'clean': (left == 0) if not dry else None,
    }
    report['what_this_does_NOT_do'] = [
        'It does not regenerate the SFT files. generate_sft.py must be re-run (behind '
        'check_eval_split.py) before any training, or the quarantined rows are still in the '
        'exported training set.',
        'It does not touch eval/accuracy_gate or eval/fidelity gate DEFINITION files, several '
        'of which also assert the TZS 11M figure as ground truth (edge_probe_natural_048.jsonl '
        'nat_36; eval_questions_003.jsonl eval_331/347/354/355; '
        'quantity_instruction_heldout_024.jsonl qi_n07; threshold_comparison_probes_024.jsonl '
        'th_09/th_10/th_19; threshold_guard_probes.jsonl tg_03/tg_08) -- rewriting gate ground '
        'truth is a bigger, separate decision (it changes what future gate runs measure) and '
        'is reported to the founder, not applied here.',
        'It does not touch the RAG index. Both EFD facts were corrected 2026-08-29 in the same '
        'session as the fabrication-class facts; R15 regeneration covers all of them together, '
        'pending.',
    ]

    if not dry:
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=1)[:3500])
    if not dry:
        print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

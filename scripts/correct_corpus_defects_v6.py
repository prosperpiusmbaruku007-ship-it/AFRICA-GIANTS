# -*- coding: utf-8 -*-
"""v6 -- DSE public-float threshold, stale since Finance Act 2025.

WHY THIS EXISTS. The corporate/partnership tax source pass (2026-09-01) read Finance Act 2025
s.60(d)(i) verbatim: "deleting the words 'thirty percent' appearing in [First Schedule] subparagraph
(2)(a) and substituting for them the words 'twenty five percent'". This is the PUBLIC FLOAT
condition for the DSE-listed 25% corporate tax rate (a newly-listed company must have at least
that percentage of its equity issued to the public to qualify) -- a DIFFERENT number from the tax
RATE itself, which was already 25% and is unchanged. Before Finance Act 2025 (effective 1 Jul
2025) the float threshold was 30%; from 1 Jul 2025 it is 25% -- the same number as the rate,
which is exactly the kind of coincidence that lets a stale corpus row read as internally
consistent when it is not.

Two rows in the corpus assert the pre-2025-07-01 30% float condition in the present tense, with
no historical framing:
  - tier1a_income_tax_adv_051_20260609 -- "Asilimia 25 inatumika kwa kampuni ... kwa angalau
    asilimia 30 ya hisa zao kwa umma."
  - tier1a_income_tax_adv_080_20260609 -- same claim, plus a reversion conditional built on the
    same stale number ("hisa za umma zitashuka chini ya asilimia 30").

QUARANTINED, not rewritten -- same reasoning as v1-v5 (R20/R25): adv_080's own sentence also
contains a SEPARATE, CORRECT use of "asilimia 30" (the standard rate the company reverts to if
delisted), so a blind digit substitution on the row risks changing the wrong occurrence. The
regex below only ever decides whether to quarantine the whole row; it does not edit text in place.
R13 (run.py generate-from-facts) regenerates both from the now-corrected `minimum_turnover_tax`/
`corporate_tax_rate` facts in locked_facts.json (2026-09-01 correction).

A historical-tense guard (`(?<!kabla ya )` etc., matching the project's existing 0.3%/0.5%
convention in minimum_turnover_tax's wrong_patterns) protects a future CORRECT pair that states
the pre-2025 threshold as history ("kabla ya Julai 2025 ilikuwa asilimia 30") from being flagged.
A DSE-context requirement excludes an unrelated GN487A pair (tier1a's non-citizen-ownership
domain) that happens to contain the literal substring "asilimia 30 ya hisa" with no DSE mention
at all -- found and excluded during pattern-development sweep, not assumed absent.

Run with --dry-run first. R18: committed before it runs.
Artifact: eval/results/corpus_correction_v6.json
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
OUT = os.path.join(REPO, 'eval', 'results', 'corpus_correction_v6.json')
QUARANTINE = os.path.join(REPO, 'datasets', 'tier1a', 'rejected',
                          'dse_stale_float_quarantine_2026_09_01.jsonl')

_FLOAT_PHRASE = re.compile(
    r'(?<!kabla ya )(?<!ilikuwa )(?<!kutoka )(?<!before )(?<!was )(?<!from )'
    r'asilimia\s*30\s*ya\s*hisa'
    r'|hisa[^.]{0,20}umma[^.]{0,30}chini\s*ya\s*asilimia\s*30',
    re.I)
_DSE_CTX = re.compile(r'DSE|Dar es Salaam Stock Exchange|Soko la Hisa', re.I)

DEFECTS = {
    'DSE_STALE_FLOAT_30': {
        'pattern': lambda line: bool(_FLOAT_PHRASE.search(line)) and bool(_DSE_CTX.search(line)),
        'reason': ('asserts a >=30% public-float condition for the DSE-listed 25% corporate tax '
                   'rate. Finance Act 2025 s.60(d)(i) lowered this to 25%, effective 1 July 2025 -- '
                   'quoted verbatim: "deleting the words \'thirty percent\' appearing in '
                   'subparagraph (2)(a) and substituting for them the words \'twenty five '
                   'percent\'". The tax RATE itself (25%) is unchanged; only the qualifying float '
                   'threshold moved, coincidentally to the same number. Re-verified 2026-09-01 as '
                   'part of the corporate/partnership tax source pass.'),
    },
}


def _match(name, spec, line):
    pat = spec['pattern']
    if callable(pat) and not isinstance(pat, re.Pattern):
        return pat(line)
    return bool(pat.search(line))


KEEP = {
    'scripts/correct_corpus_defects.py': 'v1, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v2.py': 'v2, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v3.py': 'v3, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v4.py': 'v4, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v5.py': 'v5, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v6.py': 'this file -- would rewrite its own patterns/docstring',
}


def rel(p):
    return os.path.relpath(p, REPO).replace('\\', '/')


def classify(line):
    for name, spec in DEFECTS.items():
        if _match(name, spec, line):
            return name
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    dry = args.dry_run
    report = {'measured': '2026-09-01', 'dry_run': dry,
              'harness': 'scripts/correct_corpus_defects_v6.py',
              'companion_of': ['scripts/correct_corpus_defects.py (v1)',
                                'scripts/correct_corpus_defects_v2.py (v2)',
                                'scripts/correct_corpus_defects_v3.py (v3)',
                                'scripts/correct_corpus_defects_v4.py (v4)',
                                'scripts/correct_corpus_defects_v5.py (v5)'],
              'quarantine_file': rel(QUARANTINE),
              'defect_classes': list(DEFECTS.keys())}

    quarantined, per_file, per_class = [], Counter(), Counter()
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
            cls = classify(l)
            if cls:
                try:
                    row = json.loads(l)
                except Exception:
                    keep_lines.append(l)
                    continue
                row['_quarantine'] = {
                    'from_file': r, 'from_line': i, 'quarantined': '2026-09-01',
                    'defect_class': cls,
                    'reasons': [DEFECTS[cls]['reason']],
                    'disposition': 'quarantined rather than rewritten -- same reasoning as '
                                   'v1-v5 (R20/R25): the row conflates the float threshold with '
                                   'the (unaffected) standard rate, both printed as "asilimia '
                                   '30" in the same sentence in one case, so a digit swap risks '
                                   'editing the wrong occurrence. R13 (run.py generate-from-facts) '
                                   'regenerates from the now-corrected fact.',
                }
                quarantined.append(row)
                per_class[cls] += 1
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

    report['quarantine'] = {'rows': len(quarantined), 'by_file': dict(per_file),
                             'by_defect_class': dict(per_class)}

    left = 0
    for f in glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True):
        if rel(f) == rel(QUARANTINE):
            continue
        for l in open(f, encoding='utf-8'):
            if classify(l):
                left += 1
    report['verification_after'] = {
        'datasets_rows_still_matching_any_defect_class': left,
        'clean': (left == 0) if not dry else None,
    }
    report['excluded_false_positive'] = (
        'tier1a_income_tax_adv_... GN487A pair "Mimi mgeni nataka kumiliki asilimia 30 ya hisa '
        'katika kampuni ya Kitanzania inayofanya rejareja" contains the literal substring '
        '"asilimia 30 ya hisa" with no DSE mention at all -- an unrelated non-citizen-ownership '
        'question, correctly excluded by the DSE-context requirement. Found during pattern '
        'development, not assumed absent (R17).'
    )
    report['what_this_does_NOT_do'] = [
        'It does not regenerate the SFT files. generate_sft.py must be re-run (behind '
        'check_eval_split.py) before any training, or the quarantined rows are still in the '
        'exported training set.',
        'It does not touch eval gate definition files -- none were found to assert the stale '
        '30% DSE float threshold as ground truth in this pass.',
        'It does not touch the RAG index. R15 regeneration is pending and covers this together '
        'with the other 2026-09-01 locked_facts.json corrections.',
    ]

    if not dry:
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=1)[:4000])
    if not dry:
        print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

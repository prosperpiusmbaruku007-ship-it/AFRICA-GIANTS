# -*- coding: utf-8 -*-
"""v7 -- the presumptive-tax stale-constant sweep, 2026-09-01.

WHY THIS EXISTS. Finance Act 2026 s.27(a), in force 1 July 2026, raised the presumptive
turnover ceiling (First Schedule para 2(2)) from TZS 100,000,000 to TZS 200,000,000 and the
top-band rate (para 2(3)) from 3.5% to 4.0%, and added a new-business first-12-months
exemption (para 2(3)-(4)). This was found 2026-09-01, while verifying an unrelated PAYE fact,
NOT by a scheduled recheck -- the shipped compute engine (chike/rules_engine/presumptive.py,
built 2026-08-16, six weeks AFTER FA2026 came into force) carried the stale 3.5%/100M values
until corrected in the same session. Root cause and the general lesson for every other engine
constant: PROGRESS.md, "PRESUMPTIVE ENGINE STALE-CONSTANT INCIDENT", 2026-09-01.

This script is the corpus-side half of that fix. Six unique pairs (10 file occurrences) state
the pre-2026 100,000,000 ceiling and/or 3.5% rate as CURRENT fact, in the present tense, no
historical framing.

Same disposition as v1-v7 (R20): quarantine, don't rewrite -- the correct answer needs a
structurally different sentence (new ceiling AND new rate AND the new exemption's existence),
not a digit swap. R13 (run.py generate-from-facts) regenerates from the now-corrected
presumptive_tax_bands_2022/presumptive_tax_ceiling_100m facts.

Run with --dry-run first. R18: committed before it runs.
Artifact: eval/results/corpus_correction_v7.json
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
OUT = os.path.join(REPO, 'eval', 'results', 'corpus_correction_v7.json')
QUARANTINE = os.path.join(REPO, 'datasets', 'tier1a', 'rejected',
                          'presumptive_stale_ceiling_rate_quarantine_2026_09_01.jsonl')

_MAKADIRIO_CTX = re.compile(r'makisio|makadirio|presumptive', re.I)
_STALE_NUM = re.compile(
    r'(?<!kutoka )(?<!ilikuwa )(?<!was )(?<!from )100,?000,?000'
    r'|(?<!kutoka asilimia )(?<!ilikuwa asilimia )(?<!was )(?<!from )(asilimia\s*3\.5|3\.5%)',
    re.I)

DEFECTS = {
    'PRESUMPTIVE_STALE_CEILING_OR_RATE': {
        'pattern': lambda line: bool(_MAKADIRIO_CTX.search(line))
                                and bool(_STALE_NUM.search(line)),
        'reason': ('states the pre-Finance-Act-2026 presumptive-tax ceiling (TZS 100,000,000) '
                   'and/or top-band rate (3.5%) as current fact. Finance Act 2026 s.27(a), in '
                   'force 1 July 2026, raised the ceiling to TZS 200,000,000 and the rate to '
                   '4.0%, and added a new-business first-12-months exemption (para 2(3)-(4)) '
                   'this row also does not mention. Re-verified 2026-09-01 by direct verbatim '
                   'read of Finance Act 2026 s.27(a).'),
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
    'scripts/correct_corpus_defects_v6.py': 'v6, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v7.py': 'this file -- would rewrite its own patterns/docstring',
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
              'harness': 'scripts/correct_corpus_defects_v7.py',
              'companion_of': [f'scripts/correct_corpus_defects{suf}.py'
                               for suf in ('', '_v2', '_v3', '_v4', '_v5', '_v6')],
              'quarantine_file': rel(QUARANTINE),
              'defect_classes': list(DEFECTS.keys())}

    quarantined, per_file, per_class = [], Counter(), Counter()
    for f in sorted(glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True)):
        r = rel(f)
        if r in KEEP or r == rel(QUARANTINE):
            continue
        if not os.path.exists(f):
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
                                   'v1-v7 (R20): the correct answer needs a structurally '
                                   'different sentence (new ceiling AND new rate AND the new '
                                   'exemption), not a digit swap. R13 (run.py '
                                   'generate-from-facts) regenerates from the now-corrected '
                                   'fact.',
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
        if rel(f) == rel(QUARANTINE) or not os.path.exists(f):
            continue
        for l in open(f, encoding='utf-8'):
            if classify(l):
                left += 1
    report['verification_after'] = {
        'datasets_rows_still_matching_any_defect_class': left,
        'clean': (left == 0) if not dry else None,
    }
    report['what_this_does_NOT_do'] = [
        'It does not regenerate the SFT files. generate_sft.py must be re-run (behind '
        'check_eval_split.py) before any training, or the quarantined rows are still in the '
        'exported training set.',
        'It does not touch eval gate definition files -- none were found asserting the stale '
        'ceiling/rate as ground truth in this pass.',
        'It does not touch the RAG index -- presumptive_tax_bands_2022/presumptive_tax_'
        'ceiling_100m are not in CONCISE_BILINGUAL_FACTS, so they embed via the key:value '
        'fallback; an R15 regen is still needed to refresh their index text, batched with the '
        'other pending R15 items.',
        'It does not implement the new-business exemption in any authored training pair -- '
        'the engine (compute_presumptive) handles it deterministically; no fact/pair needed.',
    ]

    if not dry:
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=1)[:4000])
    if not dry:
        print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

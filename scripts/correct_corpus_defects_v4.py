# -*- coding: utf-8 -*-
"""v4 -- the Tier 2 sweep: five confirmed-wrong facts, five corpus defect classes.

WHY THIS EXISTS. Tier 2 re-verification (2026-08-31) against primary statute/gazette text found
six facts that were confirmed WRONG (not merely ungrounded), plus a seventh Tier-1 "correction"
(objection_deposit_requirement) that itself carried a stale section citation. A corpus sweep,
following the same discipline as v1-v3, found five of those defects already baked into training
pairs -- objection_deposit_requirement, act_section_12 and name_similarity_threshold produced
ZERO corpus hits and are not part of this pass.

WHAT IS BEING QUARANTINED, one class per regex below:

1. GN487A_VISA -- "kunaweza kutokea kama sehemu ya adhabu" (can happen as part of the penalty),
   the softened framing lifted directly from the old gn487a_visa_revocation fact. GN487A s.3(3)(a)
   reads "shall be liable to [fine OR imprisonment] AND revocation" -- mandatory upon conviction,
   not discretionary. LARGEST class found: 129 rows, all reproducing the same templated phrase.
2. PAYE_P9_31MARCH -- Form "P9" due 31 March. "P9" is Kenyan (KRA) terminology; Tanzania's real
   obligation (Income Tax Act s.85(3)(b)) is the annual employment-income withholding certificate,
   due 30 January.
3. STAMP_DUTY_FLAT1 -- stamp duty on land/building transfer as a flat 1%. Stamp Duty Act Cap.189
   Schedule Art.22(b) sets a TIERED rate (0.5% on first TZS 100,000, then 1% on the excess),
   confirmed unchanged through Finance Act 2021 and 2026.
4. VAT_JULY2024 -- VAT registration threshold increase dated "Julai 2024"/"July 2024". Government
   Notice No. 448Y of 2023 s.4 (the actual amending instrument, found this pass) commenced 1 July
   2023 -- the date was wrong by exactly one year everywhere it appeared, including here.
5. PATENT_20FLAT -- patent term stated as a flat 20 years with no extension mechanism mentioned.
   Patents (Registration) Act Cap.217 s.39(1) sets a 10-year BASE term, extendable via two
   discretionary 5-year extensions to a maximum of 20 -- 20 years flat is the ARIPO regional term,
   not Tanzania's domestic Act.

Same disposition as v1-v3 (R20): quarantine, don't rewrite. Each of these needs a structurally
different sentence, not a word swap -- generating that mechanically here risks manufacturing a
plausible replacement silently. R13 (run.py generate-from-facts) regenerates from the now-
corrected facts.

Run with --dry-run first. R18: committed before it runs.
Artifact: eval/results/corpus_correction_v4.json
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
OUT = os.path.join(REPO, 'eval', 'results', 'corpus_correction_v4.json')
QUARANTINE = os.path.join(REPO, 'datasets', 'tier1a', 'rejected',
                          'tier2_confirmed_wrong_quarantine_2026_08_31.jsonl')

DEFECTS = {
    'GN487A_VISA': {
        'pattern': re.compile(
            r'visa[^.?!]{0,50}(kunaweza kutokea|possible[^.?!]{0,10}consequence|si lazima daima)',
            re.I),
        'reason': ('states visa/permit revocation as merely "possible" or "not always" -- GN487A '
                   's.3(3)(a) makes it mandatory upon conviction ("shall be liable to ... AND '
                   'revocation"), not discretionary. Re-verified 2026-08-31 against the Order\'s '
                   'own text.'),
    },
    'PAYE_P9_31MARCH': {
        'pattern': re.compile(r'p9[^.?!]{0,50}(31 machi|31 march)', re.I),
        'reason': ('asserts Form "P9" due 31 March -- "P9" is Kenyan (KRA) terminology, not a '
                   'Tanzanian TRA form. The actual obligation (Income Tax Act Cap.332 s.85(3)(b)) '
                   'is the annual employment-income withholding certificate, due 30 January. '
                   'Re-verified 2026-08-31.'),
    },
    'STAMP_DUTY_FLAT1': {
        'pattern': re.compile(
            r'(stamp duty|stempu)[^.?!]{0,70}(flat 1%|asilimia 1 tu|1% tu)'
            r'|flat 1%[^.?!]{0,50}(stamp|stempu)', re.I),
        'reason': ('asserts a flat 1% stamp duty on land/building transfer -- Stamp Duty Act '
                   'Cap.189 Schedule Art.22(b) sets a TIERED rate (0.5% on first TZS 100,000, '
                   'then 1% on the excess), confirmed unchanged FA2021->FA2026. Re-verified '
                   '2026-08-31.'),
    },
    'VAT_JULY2024': {
        'pattern': re.compile(
            r'(julai 2024|july 2024)[^.?!]{0,50}(vat|kizingiti)'
            r'|(vat|kizingiti)[^.?!]{0,50}(julai 2024|july 2024)', re.I),
        'reason': ('dates the VAT 100M->200M registration threshold increase to July 2024 -- the '
                   'amending instrument, Government Notice No. 448Y of 2023 s.4, commenced 1 July '
                   '2023. The 200M/100M figures themselves are correct and unaffected -- only the '
                   'date is wrong. Re-verified 2026-08-31.'),
    },
    'PATENT_20FLAT': {
        'pattern': re.compile(
            r'(patent|hataza)[^.?!]{0,50}(20 years|miaka 20)'
            r'(?!.{0,30}(extension|nyongeza|10 years|miaka 10))', re.I),
        'reason': ('states patent term as a flat 20 years with no extension mechanism -- Patents '
                   '(Registration) Act Cap.217 s.39(1) sets a 10-year BASE term, extendable via '
                   'two discretionary 5-year extensions to a maximum of 20. Re-verified '
                   '2026-08-31.'),
    },
}

KEEP = {
    'scripts/correct_corpus_defects.py': 'v1, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v2.py': 'v2, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v3.py': 'v3, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v4.py': 'this file -- would rewrite its own patterns/docstring',
}


def rel(p):
    return os.path.relpath(p, REPO).replace('\\', '/')


def classify(line):
    for name, spec in DEFECTS.items():
        if spec['pattern'].search(line):
            return name
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    dry = args.dry_run
    report = {'measured': '2026-08-31', 'dry_run': dry,
              'harness': 'scripts/correct_corpus_defects_v4.py',
              'companion_of': ['scripts/correct_corpus_defects.py (v1)',
                                'scripts/correct_corpus_defects_v2.py (v2)',
                                'scripts/correct_corpus_defects_v3.py (v3)'],
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
                    'from_file': r, 'from_line': i, 'quarantined': '2026-08-31',
                    'defect_class': cls,
                    'reasons': [DEFECTS[cls]['reason']],
                    'disposition': 'quarantined rather than rewritten -- same reasoning as '
                                   'v1-v3 (R20): the correct answer is a structurally different '
                                   'sentence, not a word swap. R13 (run.py generate-from-facts) '
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
    report['what_this_does_NOT_do'] = [
        'It does not regenerate the SFT files. generate_sft.py must be re-run (behind '
        'check_eval_split.py) before any training, or the quarantined rows are still in the '
        'exported training set.',
        'It does not touch eval gate definition files -- none were found to assert any of these '
        'five defect classes as ground truth in this pass (unlike the EFD threshold, which did).',
        'It does not touch the RAG index. All six Tier-2 corrections were made 2026-08-31; R15 '
        'regeneration is pending and covers them together.',
        'It does NOT cover objection_deposit_requirement, act_section_12, or '
        'name_similarity_threshold -- swept separately and found to have zero corpus hits.',
    ]

    if not dry:
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=1)[:4000])
    if not dry:
        print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

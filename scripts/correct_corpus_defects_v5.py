# -*- coding: utf-8 -*-
"""v5 -- the Tier 3 sweep: three confirmed corpus defects found while re-verifying the 96
lower-traffic ("Tier 3") locked_facts.json entries against primary statute/gazette text.

WHY THIS EXISTS. Tier 3 re-verification (2026-09-01) found several facts wrong or incomplete,
but most had zero corpus impact (consistent with their low-traffic classification -- see
eval/results/ungrounded_fact_exposure.json). Three defect classes DID have corpus impact,
found by sweeping for each corrected claim individually rather than assuming low traffic meant
no impact:

1. P45_P9_CONFLATION -- p45_not_tanzanian's own prior text named 'P9' as Tanzania's correct
   payroll-form term. 'P9' is Kenyan (KRA) terminology, the same defect already found and fixed
   in paye_p9_deadline (Tier 2, 2026-08-31). The one corpus row carrying this claim ALSO still
   had the stale '31 Machi' P9 deadline that v4's PAYE_P9_31MARCH pattern was built to catch --
   it slipped through v4 because the date appears BEFORE 'P9' in the sentence ('ifikapo Machi 31
   ... mwajiri anatoa Fomu P9'), and v4's regex only matched the p9-then-date order. This row is
   quarantined under this defect class; v4's own pattern is not re-run or amended here.
2. SECTION_XII_FOREIGN_COMPANY -- foreign-company BRELA late-filing-penalty pairs cite
   '(Section XII)' as the Companies Act provision. Companies Act Cap.212's foreign-company
   provisions are actually Part XIII, ss.320-328 -- a stale-name defect already corrected in
   CLAUDE.md Section 11 and in the locked fact act_section_12 (2026-08-31), but never swept in
   the corpus itself until now. The AMOUNTS in every one of these rows (TZS 2,500/month local,
   USD 25/month foreign) are correct and unaffected -- only the section citation is wrong.
3. COURSE_FEE_250K -- an OSHA training-course fee of TZS 250,000 with no identified course.
   Every OSHA course fee actually checked (Safe Use of Chemicals at Work, OHS in Construction
   Industry, Safety and Health in Oil and Gas Industry) is priced at TZS 300,000, not 250,000.
   The specific course '250,000' refers to, if any, could not be identified.

Same disposition as v1-v4 (R20): quarantine, don't rewrite. R13 (run.py generate-from-facts)
regenerates from the now-corrected facts.

Run with --dry-run first. R18: committed before it runs.
Artifact: eval/results/corpus_correction_v5.json
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
OUT = os.path.join(REPO, 'eval', 'results', 'corpus_correction_v5.json')
QUARANTINE = os.path.join(REPO, 'datasets', 'tier1a', 'rejected',
                          'tier3_confirmed_wrong_quarantine_2026_09_01.jsonl')

_FOREIGN = re.compile(r'kigeni|foreign', re.I)
_SECTION12 = re.compile(r'Section XII|[Ss]ection 12\b|Kifungu cha (12|XII)\b', re.I)

DEFECTS = {
    'P45_P9_CONFLATION': {
        'pattern': re.compile(r'[Pp]45.{0,80}P9|[Pp]-45.{0,80}P9|badala ya P45.{0,40}P9', re.I),
        'reason': ('names "P9" as the Tanzanian alternative to a UK P45 -- "P9" is Kenyan (KRA) '
                   'terminology, the same defect already corrected in paye_p9_deadline (Tier 2, '
                   '2026-08-31). The real TZ mechanism is the annual employment-income '
                   'withholding certificate, Income Tax Act Cap.332 s.85(3)(b). '
                   'Re-verified 2026-09-01.'),
    },
    'SECTION_XII_FOREIGN_COMPANY': {
        'pattern': lambda line: bool(_SECTION12.search(line)) and bool(_FOREIGN.search(line)),
        'reason': ('cites "(Section XII)" as the Companies Act provision for foreign-company '
                   'BRELA filings. The correct citation is Part XIII, ss.320-328 of Cap.212 -- '
                   'the same stale-name defect already fixed in CLAUDE.md Section 11 and in the '
                   'locked fact act_section_12 (2026-08-31), now also swept from the corpus. '
                   'The fee amounts themselves (TZS 2,500/month local, USD 25/month foreign) are '
                   'correct and unaffected. Re-verified 2026-09-01.'),
    },
    'COURSE_FEE_250K': {
        'pattern': re.compile(r'250,?000.{0,40}(osha|kozi|course)', re.I),
        'reason': ('states an OSHA training-course fee of TZS 250,000 with no identified course. '
                   'Every OSHA course fee actually sampled (Safe Use of Chemicals at Work, OHS in '
                   'Construction Industry, Safety and Health in Oil and Gas Industry) is TZS '
                   '300,000, not 250,000. Re-verified 2026-09-01.'),
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
    'scripts/correct_corpus_defects_v5.py': 'this file -- would rewrite its own patterns/docstring',
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
              'harness': 'scripts/correct_corpus_defects_v5.py',
              'companion_of': ['scripts/correct_corpus_defects.py (v1)',
                                'scripts/correct_corpus_defects_v2.py (v2)',
                                'scripts/correct_corpus_defects_v3.py (v3)',
                                'scripts/correct_corpus_defects_v4.py (v4)'],
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
                                   'v1-v4 (R20): the correct answer is a structurally different '
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
        'three defect classes as ground truth in this pass.',
        'It does not touch the RAG index. All Tier-3 locked_facts.json corrections were made '
        '2026-09-01; R15 regeneration is pending and covers them together.',
        'It does NOT cover the majority of Tier-3 corrections (TAA renumbering, TaESA exemption, '
        'business_name_maintenance_fee, minimum_directors/shareholders, health_and_safety_act_'
        'citation, risk_assessment_frequency, electrical_test_fee scope, OSHA_safety_officer_'
        'threshold, trademark_renewal_period) -- swept individually and found to have zero corpus '
        'hits, or (electrical fee, risk-assessment frequency, generic Act-name mentions) to have '
        'hits that were already correctly scoped or not actually asserting the wrong claim -- see '
        'PROGRESS.md for the per-fact sweep results.',
    ]

    if not dry:
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=1)[:4000])
    if not dry:
        print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

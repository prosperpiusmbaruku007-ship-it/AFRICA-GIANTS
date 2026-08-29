# -*- coding: utf-8 -*-
"""v2 -- two MORE defect classes found while re-verifying Tier 1 locked facts against statute
(2026-08-29), quarantined the same way v1 quarantined the PAYE-arithmetic rows.

WHY THESE TWO. Re-verifying `nssf_retirement_age` and `wcf_disease_reporting_deadline` against
their governing statute/regulation found the locked facts themselves wrong, and a corpus sweep
for the same wrong claims found both already baked into `train_sft.jsonl`:

  1. NSSF "mining" retirement fabrication. `nssf_retirement_age` claimed "(55 for mining/early
     retirement)" -- "mining" appears nowhere in NSSF Act Cap.50 Part V, and nowhere in either
     source the fact was originally verified against. This is the SAME defect class as the
     PAYE band-2-at-9% row from v1: a claim in the corpus with NO source anywhere, not a stale
     citation. 8 occurrences across 6 files, 3 inside `train_sft.jsonl`.

  2. WCF occupational-disease "7 working days of diagnosis." `wcf_disease_reporting_deadline`
     claimed a flat 7-day window; GN 185/2016 Reg.16 is a two-stage chain (employee->employer
     14 working days, employer->WCF 7 more) -- worst case 21 working days, not 7. This is a
     STALE-SOURCE-COMPRESSION defect, not a fabrication: the 7-day figure is real, just
     mis-attached to the wrong reference point. 6 occurrences across 2 files, 3 inside
     `train_sft.jsonl`.

Same disposition as v1 and for the same reason (R20): a mechanical pass that recomputes the
correct multi-step WCF chain or invents a defensible non-mining justification for "55" would be
manufacturing a plausible replacement -- worse than the gap, silently, forever. Quarantine, then
R13 (`run.py generate-from-facts`) regenerates from the now-corrected locked_facts.json.

Both patterns are narrow and checked against their actual matched text before being written here
(not assumed from a generic grep) -- see PROGRESS.md for the content each pattern was verified
against.

Run with --dry-run first. R18: committed before it runs.
Artifact: eval/results/corpus_correction_v2.json
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
OUT = os.path.join(REPO, 'eval', 'results', 'corpus_correction_v2.json')
QUARANTINE = os.path.join(REPO, 'datasets', 'tier1a', 'rejected',
                          'fabrication_and_deadline_defect_quarantine_2026_08_29.jsonl')

# NSSF "mining" retirement fabrication -- matches the exact shape found: "55" tied to
# "madini"/"mining" within one JSONL record (JSONL = one record per line).
MINING55 = re.compile(
    r'miaka 55[^.]{0,60}madini|madini[^.]{0,60}miaka 55'
    r'|55[^.]{0,40}mining[^.]{0,40}(sector|retirement)'
    r'|(sekta ya madini|wachimbaji madini)[^.]{0,60}(miaka 55|umri wa 55)'
    r'|(miaka 55|umri wa 55)[^.]{0,60}(sekta ya madini|wachimbaji madini)'
    # bare "55" inside a parenthetical shortly followed by madini/mining, with no repeated
    # "miaka"/"umri wa" -- the exact shape of "miaka 60 (55 kwa sekta ya madini)", the same
    # grammatical construction the original locked-fact fabrication used ("60 (55 for mining...")
    r'|\(\s*55[^)]{0,40}(madini|mining)[^)]{0,20}\)',
    re.I)
# Corrective pairs would say the opposite explicitly -- guard against destroying one.
MINING55_NEGATED = re.compile(
    r'(si|sivyo|not|hakuna)[^.]{0,40}(kwa madini|for mining|mining[- ]specific)', re.I)

# WCF occupational-disease flat "7 days from diagnosis" -- the wrong claim omits the prior
# 14-working-day employee-to-employer leg. A CORRECT two-stage explanation mentions "siku 14"
# /"14 working days" for the employee leg BEFORE the "siku 7"/employer leg -- excluded here so a
# correct explanation is never quarantined alongside the wrong flat claim.
WCF7DAY = re.compile(
    r'ugonjwa wa kazini[^.]{0,80}(ndani ya )?siku (saba|7)(?!.{0,120}siku (kumi na nne|14))'
    r'|occupational disease[^.]{0,80}(within )?7 working days(?!.{0,120}14 working days)',
    re.I)
WCF7DAY_HAS_TWO_STAGE = re.compile(
    r'siku (kumi na nne|14)[^.]{0,150}siku (saba|7)|14 working days[^.]{0,150}7 working days', re.I)

KEEP = {
    'scripts/correct_corpus_defects.py': 'v1, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v2.py': 'this file -- would rewrite its own patterns/docstring',
}
R10 = {'scripts/fixed_cell_model.py', 'scripts/fixed_cell_data.py', 'scripts/fixed_cell_train.py',
       'scripts/_trl_sft_trainer_v0_24_0.py', 'run.py'}


def rel(p):
    return os.path.relpath(p, REPO).replace('\\', '/')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    dry = args.dry_run
    report = {'measured': '2026-08-29', 'dry_run': dry,
              'harness': 'scripts/correct_corpus_defects_v2.py',
              'supersedes': None, 'companion_of': 'scripts/correct_corpus_defects.py (v1)',
              'quarantine_file': rel(QUARANTINE)}

    quarantined, per_file, skipped_negated, skipped_two_stage = [], Counter(), [], []
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
            has_mining = bool(MINING55.search(l)) and not MINING55_NEGATED.search(l)
            has_wcf7 = bool(WCF7DAY.search(l))
            if has_wcf7 and WCF7DAY_HAS_TWO_STAGE.search(l):
                skipped_two_stage.append({'file': r, 'line': i,
                                          'why': 'mentions both the 14-day and 7-day legs -- a '
                                                 'correct two-stage explanation, not the wrong '
                                                 'flat claim', 'text': l[:200]})
                has_wcf7 = False
            if has_mining and MINING55_NEGATED.search(l):
                skipped_negated.append({'file': r, 'line': i,
                                        'why': 'occurrence sits inside a NEGATION', 'text': l[:200]})
            if has_mining or has_wcf7:
                try:
                    row = json.loads(l)
                except Exception:
                    keep_lines.append(l)
                    continue
                reasons = []
                if has_mining:
                    reasons.append(
                        'asserts NSSF has a mining-specific 55-year retirement provision -- '
                        'NSSF Act Cap.50 Part V has no such provision; 55 is a general '
                        'early-retirement age for any insured person (ss.25(c),29). Fabricated '
                        'during authoring, not sourced from anywhere (re-verified 2026-08-29).')
                if has_wcf7:
                    reasons.append(
                        'asserts occupational disease must reach WCF within a flat 7 working '
                        'days of diagnosis -- GN 185/2016 Reg.16 is a two-stage chain '
                        '(employee-to-employer 14 working days, then employer-to-WCF 7 more); '
                        'true worst case is 21 working days (re-verified 2026-08-29).')
                row['_quarantine'] = {
                    'from_file': r, 'from_line': i, 'quarantined': '2026-08-29',
                    'reasons': reasons,
                    'disposition': 'quarantined rather than rewritten -- same reasoning as the '
                                   '2026-08-25 PAYE quarantine (R20): a mechanical rewrite risks '
                                   'manufacturing a plausible wrong replacement. R13 '
                                   '(run.py generate-from-facts) regenerates from the corrected '
                                   'locked_facts.json, which is the pipeline-native fix.',
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
    report['skipped_because_NEGATED'] = skipped_negated
    report['skipped_because_TWO_STAGE_CORRECT'] = skipped_two_stage

    # Verification
    left_mining = left_wcf7 = 0
    for f in glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True):
        if rel(f) == rel(QUARANTINE):
            continue
        for l in open(f, encoding='utf-8'):
            if MINING55.search(l) and not MINING55_NEGATED.search(l):
                left_mining += 1
            if WCF7DAY.search(l) and not WCF7DAY_HAS_TWO_STAGE.search(l):
                left_wcf7 += 1
    report['verification_after'] = {
        'datasets_rows_still_asserting_mining_55': left_mining,
        'datasets_rows_still_at_flat_wcf_7day': left_wcf7,
        'clean': (left_mining == 0 and left_wcf7 == 0) if not dry else None,
    }
    report['what_this_does_NOT_do'] = [
        'It does not regenerate the SFT files. generate_sft.py must be re-run (behind '
        'check_eval_split.py) before any training, or the quarantined rows are still in the '
        'exported training set.',
        'It does not touch the RAG index. locked_facts.json was corrected 2026-08-29 '
        '(commit cb34a2e); R15 regeneration is separate, pending.',
        'It does not resolve GN605A_rate_range or osha_vs_wcf_roles, the two flags from '
        'scripts/audit_fact_claim_grounding.py -- one is a confirmed false positive (title '
        'match), the other is plausible-but-unconfirmed and not a corpus defect.',
    ]

    if not dry:
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=1)[:3000])
    if not dry:
        print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

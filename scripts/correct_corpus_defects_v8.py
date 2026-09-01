# -*- coding: utf-8 -*-
"""v8 -- VAT withholding remittance deadline, stale since 2026-07-01 (Finance Act 2026 s.95).

WHY THIS EXISTS. Found during the same Finance-Act-freshness audit that found the presumptive-
tax stale ceiling/rate (v7). Finance Act 2026 s.95, in force 1 July 2026, repealed and replaced
VAT Act s.71(5): a withholding agent now remits withheld VAT to the Commissioner "within TEN
DAYS after the end of each tax period" -- not the 20th of the following month (the deadline
Finance Act 2025's own enacting text set: "at the time when the value added tax return is due
to be filed"). Confirmed by direct comparison of both texts, not assumed from the section
number alone -- see scripts/locked_facts.json's vat_withholding_remittance_deadline correction_
note for the full verbatim quotes.

WHAT THIS DOES NOT TOUCH, DELIBERATELY. The VAT WITHHOLDING CERTIFICATE's own issuance timing
("siku VAT inapostahili kulipwa" / "the day VAT becomes payable", VAT Act s.15) is a SEPARATE
obligation FA2026 does not touch at all -- confirmed, nothing in Part XXVI's sections 90-96
references section 15. Most quarantined rows correctly distinguish the certificate from the
remittance and are only wrong about the remittance half; the certificate half of the same
sentence stays correct. Quarantined as a WHOLE ROW anyway (R20/v1-v7 precedent): the correct
answer needs a structurally different sentence (10 days, not 20th, for the remittance leg),
not a digit swap, and a row asserting a stale deadline for HALF its claim still carries the
engine's -- sorry, the fact path's -- authority for the part that is wrong.

Pattern requires BOTH a VAT-withholding-specific context (not bare "VAT" or bare "withholding",
which would over-match PAYE/SDL deadline rows naming the same 20th for an unrelated obligation)
AND an explicit remit/pay/submit verb near "tarehe 20"/"20th" -- a row that only says "return ya
VAT ni tarehe 20" without any withholding-remittance framing is NOT this defect (the ordinary
VAT return deadline is still the 20th, unchanged).

Run with --dry-run first. R18: committed before it runs.
Artifact: eval/results/corpus_correction_v8.json
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
OUT = os.path.join(REPO, 'eval', 'results', 'corpus_correction_v8.json')
QUARANTINE = os.path.join(REPO, 'datasets', 'tier1a', 'rejected',
                          'vat_withholding_deadline_stale_quarantine_2026_09_01.jsonl')

_VATWH_CTX = re.compile(
    r'vat withholding|withholding.{0,6}vat|kodi ya zuio.{0,10}vat|vat.{0,10}kodi ya zuio|'
    r'vat ya (ku)?zuio|vat (i)?li(cho)?zuiliwa|zuio la vat', re.I)
_REMIT_VERB = re.compile(
    r'lipa|kulipa|peleka|kupeleka|wasilish|kuwasilisha|remit|pay\b|submit', re.I)
_DAY20 = re.compile(
    r'(?<!kabla ya )(?<!ilikuwa )(?<!kutoka )(?<!before )(?<!was )(?<!from )'
    r'tarehe 20\b|(?<!kabla ya )(?<!ilikuwa )(?<!kutoka )(?<!before )(?<!was )(?<!from )20th\b',
    re.I)


def _is_defect(line):
    if not _VATWH_CTX.search(line):
        return False
    if not _DAY20.search(line):
        return False
    return bool(_REMIT_VERB.search(line))


DEFECTS = {
    'VATWH_REMITTANCE_STALE_20TH': {
        'pattern': _is_defect,
        'reason': ('asserts VAT withholding is remitted/paid to TRA by the 20th of the '
                   'following month. Finance Act 2026 s.95, in force 1 July 2026, repealed and '
                   'replaced VAT Act s.71(5): the deadline is now within 10 days after the end '
                   'of the tax period. The 20th was correct under Finance Act 2025\'s original '
                   's.71(5) text ("at the time when the value added tax return is due to be '
                   'filed") but is no longer correct going forward. Re-verified 2026-09-01 by '
                   'direct comparison of both Finance Acts\' verbatim text.'),
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
    'scripts/correct_corpus_defects_v7.py': 'v7, a separate committed harness for a separate date',
    'scripts/correct_corpus_defects_v8.py': 'this file -- would rewrite its own patterns/docstring',
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
              'harness': 'scripts/correct_corpus_defects_v8.py',
              'companion_of': [f'scripts/correct_corpus_defects{suf}.py'
                               for suf in ('', '_v2', '_v3', '_v4', '_v5', '_v6', '_v7')],
              'quarantine_file': rel(QUARANTINE),
              'defect_classes': list(DEFECTS.keys())}

    quarantined, per_file, per_class = [], Counter(), Counter()
    for f in sorted(glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True)):
        r = rel(f)
        if r in KEEP or r == rel(QUARANTINE) or 'datasets/tier1a/rejected/' in r:
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
                                   'different sentence (10 days, not the 20th), not a digit '
                                   'swap, and the certificate-timing half of these sentences is '
                                   'still correct but inseparable from the wrong half without '
                                   'hand-editing. R13 (run.py generate-from-facts) regenerates '
                                   'from the now-corrected vat_withholding_remittance_deadline.',
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
        if rel(f) == rel(QUARANTINE) or 'datasets/tier1a/rejected/' in rel(f):
            continue
        for l in open(f, encoding='utf-8'):
            if classify(l):
                left += 1
    report['verification_after'] = {
        'datasets_rows_still_matching_any_defect_class': left,
        'clean': (left == 0) if not dry else None,
    }
    report['what_this_does_NOT_do'] = [
        'It does not regenerate the SFT files. generate_sft.py must be re-run before any '
        'training, or the quarantined rows are still in the exported training set.',
        'It does not touch the VAT withholding CERTIFICATE timing fact/rows -- that '
        'obligation (VAT Act s.15, "day VAT becomes payable") is confirmed unaffected by '
        'Finance Act 2026, and rows correctly stating it are not quarantined merely for '
        'mentioning the 20th in CONTRAST to the certificate date, only for asserting the '
        '20th AS the remittance deadline itself.',
        'It does not touch the ordinary VAT RETURN deadline (still the 20th, unchanged) -- '
        'the pattern requires VAT-withholding-specific context, not bare "VAT return".',
    ]

    if not dry:
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=1)[:4000])
    if not dry:
        print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

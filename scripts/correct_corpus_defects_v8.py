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

# PROXIMITY, not bare co-occurrence -- found necessary by manual spot-check (R17), not assumed
# safe. A first draft matched on "VAT withholding" + "tarehe 20" + any remit verb ANYWHERE in
# the row, which caught tier1a_vat_006 -- a row that correctly says the CERTIFICATE is NOT due
# on the 20th, and whose only remit-shaped word ("kuwasilisha") describes the (unchanged, still
# correct) VAT RETURN deadline, not the withholding remittance. Requires the remit verb to sit
# within 60 characters of the WITHHELD-AMOUNT phrase specifically (kiasi kilichozuiliwa/VAT
# withholding itself/kodi ya zuio/VAT ya kuzuia), and covers both Swahili verb-stem forms
# ("zuio" the noun, "zuia" the infinitive) since a bare-word match missed passive conjugations
# (kilipwa, inawasilishwa) that a plain "lipa"/"wasilisha" substring does not contain.
_REMIT_AMOUNT = re.compile(
    r'(kiasi\s+(kilicho)?(zuiliwa|katwa)|vat\s+(i)?li(cho)?(zuiliwa|katwa)|withheld\s+(vat|amount)|'
    r'vat\s+withholding|kodi\s+ya\s+zuio|vat\s+ya\s+(ku)?zui[ao])[^.!?]{0,60}'
    r'(lip|pelek|wasilish|remit|pay\b|submit)'
    r'|(lip|pelek|wasilish|remit|pay\b|submit)[^.!?]{0,60}'
    r'(kiasi\s+(kilicho)?(zuiliwa|katwa)|vat\s+(i)?li(cho)?(zuiliwa|katwa)|withheld\s+(vat|amount)|'
    r'vat\s+withholding|kodi\s+ya\s+zuio|vat\s+ya\s+(ku)?zui[ao])',
    re.I)
_DAY20 = re.compile(
    r'(?<!kabla ya )(?<!ilikuwa )(?<!kutoka )(?<!before )(?<!was )(?<!from )'
    r'tarehe 20\b|(?<!kabla ya )(?<!ilikuwa )(?<!kutoka )(?<!before )(?<!was )(?<!from )20th\b',
    re.I)
# A row that explicitly says tarehe 20 is NOT the answer for what it's discussing (the
# certificate) -- protects tier1a_vat_006/similar rows correctly rejecting the 20th for the
# certificate, which a proximity match alone still caught (the certificate's own "day VAT
# becomes payable" trigger clause sits within 60 chars of "kodi ya zuio").
_NEGATED_20 = re.compile(r'si\s+tarehe\s+20|siyo\s+tarehe\s+20|not\s+the\s+20th|si\s+20th', re.I)


_TEXT_FIELDS = ('question_sw', 'answer_sw', 'question_en', 'answer_en',
                'instruction', 'input', 'output')


def _field_is_defect(text):
    if not text or not isinstance(text, str):
        return False
    if _NEGATED_20.search(text):
        return False
    return bool(_REMIT_AMOUNT.search(text)) and bool(_DAY20.search(text))


def _is_defect(line):
    """Checks each text FIELD independently, never the raw JSON line as one string.

    FOUND NECESSARY BY A LIVE FALSE POSITIVE (R17), not a defensive guess: v8's first draft
    matched the whole raw line, and tier1a_vat_006 -- a row that correctly says the CERTIFICATE
    is NOT due on the 20th -- was flagged anyway. The commas and quote marks between JSON field
    values are not '.', '!' or '?', so the proximity window bridged from one field's tail into
    the next field's head across a field boundary a human reader would never cross (e.g. from
    the end of `question_sw`'s value straight into `answer_sw`'s opening words). Checking each
    field's own text independently, rather than the concatenated raw line, closes that gap at
    its structural cause instead of patching the symptom with a wider exclusion list.
    """
    try:
        obj = json.loads(line)
    except Exception:
        # Not parseable JSON (e.g. malformed line) -- fall back to the raw-line check so a
        # genuinely broken row is not silently skipped, matching v1-v7's tolerance elsewhere.
        if _NEGATED_20.search(line):
            return False
        return bool(_REMIT_AMOUNT.search(line)) and bool(_DAY20.search(line))
    if not isinstance(obj, dict):
        return False
    return any(_field_is_defect(obj.get(f)) for f in _TEXT_FIELDS)


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

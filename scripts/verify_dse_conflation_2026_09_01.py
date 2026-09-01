# -*- coding: utf-8 -*-
"""DSE conflation re-verification, 2026-09-01 — the check the founder named explicitly as
unswept, run comprehensively rather than assumed closed by v6.

WHY THIS EXISTS SEPARATELY FROM v6. `correct_corpus_defects_v6.py` quarantined 6 rows (2 unique
pairs) asserting the STALE pre-2025 30% public-float condition. That closes one shape of the
defect. It does NOT, on its own, prove the corpus is clean of the OTHER shape: a pair that
states the CURRENT 25% float condition and the CURRENT 25% DSE tax rate as if they were the
same number by construction rather than two figures that happen to coincide since Finance Act
2025 s.60(d)(i). That shape reads as correct (both numbers are individually right) and is
exactly the kind of defect a narrow regex for "30" cannot find, because it contains no wrong
digit at all.

METHOD. Every row in datasets/ (excluding rejected/, already-quarantined) mentioning DSE/Dar es
Salaam Stock Exchange/Soko la Hisa is pulled as a candidate, deduplicated by id/text, and
classified by what provision it actually discusses — read in context, not pattern-matched,
because "DSE" + "25%" alone cannot distinguish the corporate-rate topic from the UNRELATED
25%-threshold provisions this sweep also found sharing the same digit (dividend withholding's
substantial-shareholding exemption, s.82; capital-gains exemption for small DSE shareholders).
Classification is recorded per row so the judgment is auditable, not asserted.

R18: committed before its result is cited.
Artifact: eval/results/dse_conflation_verification_2026_09_01.json
"""
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, 'eval', 'results', 'dse_conflation_verification_2026_09_01.json')

_DSE_CTX = re.compile(r'DSE|Dar es Salaam Stock Exchange|Soko la Hisa', re.I)

# The defect shapes this script checks for, applied only to rows classified CORPORATE_RATE_TOPIC.
_STALE_FLOAT_30 = re.compile(
    r'(?<!kabla ya )(?<!ilikuwa )(?<!kutoka )(?<!before )(?<!was )(?<!from )'
    r'asilimia\s*30\s*ya\s*hisa'
    r'|hisa[^.]{0,20}umma[^.]{0,30}chini\s*ya\s*asilimia\s*30', re.I)
# Conflation shape: states the rate (25%) and a public-float condition using SIMILAR-LOOKING
# language that could be read as "the rate IS the float requirement" rather than two figures
# that separately happen to both be 25 since 2025-07-01. No historical/change framing present.
_CONFLATION_25 = re.compile(
    r'(?<!kabla ya )(?<!ilikuwa )(?<!kutoka )(?<!before )(?<!was )(?<!from )'
    r'asilimia\s*25\s*ya\s*hisa.{0,80}asilimia\s*25|asilimia\s*25.{0,80}asilimia\s*25\s*ya\s*hisa',
    re.I)

# Manual classification of every unique DSE-mentioning row found, keyed by a stable substring
# of its text (first 60 chars is enough given none collide). Read in context 2026-09-01.
# 'CORPORATE_RATE_TOPIC' = discusses the First Schedule para 3(1)/3(2)(a) corporate income tax
# rate for DSE-listed companies -- the only topic where the conflation defect could occur.
# Every other label is a DIFFERENT provision that happens to share the digit 25 or the word DSE.
_CLASSIFICATIONS = {
    'Kiwango cha kodi ya zuio ya gawio kwa kampuni zilizoorodheshwa kwenye Soko la Hisa':
        ('DIVIDEND_WITHHOLDING_NOT_CORPORATE_RATE',
         'First Schedule para 4(b) dividend withholding rate for DSE-listed companies (5%) -- '
         'a different provision from the para 3(1)/3(2)(a) corporate income tax rate.'),
    'Kiwango cha kodi ya zuio ya gawio kwa kampuni zisizoorodheshwa DSE':
        ('DIVIDEND_WITHHOLDING_NOT_CORPORATE_RATE',
         'Substantial-shareholding (>25% ownership) dividend withholding exemption -- s.82 '
         'area, unrelated to the DSE-listing corporate rate condition. The 25% here is a '
         'shareholding threshold for a WITHHOLDING rate, not a public-float condition for the '
         'CORPORATE rate.'),
    'Kiwango cha kawaida cha kodi ya mapato ya kampuni Tanzania ni asilimia 30 ya faida':
        ('CORPORATE_RATE_TOPIC',
         'States the 25% DSE rate but NO float percentage at all -- incomplete, not wrong. '
         'Makes no claim about the qualifying condition, so nothing to quarantine.'),
    'Kodi ya mapato ya kampuni (corporation tax) kwa faida ya TZS 50,000,000':
        ('CORPORATE_RATE_TOPIC',
         'Standard-rate worked example (30% of TZS 50M profit) -- does not mention DSE listing, '
         'the 25% rate, or any float condition at all.'),
    'Hisa za kampuni ya binafsi (private company) zinauzwa':
        ('COMPANY_LAW_NOT_TAX',
         'BRELA/Companies Act share-transfer mechanics (private vs public company), no tax '
         'rate or float percentage of any kind.'),
    'Kampuni ya BINAFSI: idadi ya wanahisa imepunguzwa':
        ('COMPANY_LAW_NOT_TAX',
         'Private vs public company structural differences, no tax figure.'),
    'Umiliki na kiwango cha kodi ya DSE ni mambo tofauti':
        ('CORPORATE_RATE_TOPIC',
         'States the 25% rate derives from DSE LISTING, correctly distinguishing it from '
         'foreign OWNERSHIP -- but asserts no float percentage number at all, so there is '
         'nothing to conflate. Correctly contrasts with the 30% standard rate for an '
         'unlisted, 100%-foreign-owned company.'),
    'Miamala ya hisa kwenye Dar es Salaam Stock Exchange (DSE) inaweza kuwa na kodi':
        ('REFUSAL_NOT_A_CLAIM', 'Explicit "sina uhakika" refusal on DSE capital-gains tax '
         'treatment -- states no rate or percentage as fact.'),
    'Kodi ya gawio (dividend withholding tax) kwa hisa za DSE':
        ('REFUSAL_NOT_A_CLAIM', 'Explicit refusal, states no rate as fact.'),
    'Swali hili liko nje ya maarifa yangu. Kununua hisa katika masoko ya kimataifa':
        ('OUT_OF_SCOPE_REFUSAL', 'NYSE/international markets, not Tanzania DSE.'),
    'Ni lazima ukatae kodi ya zuio ya 5% kwa wasio wakazi':
        ('DIVIDEND_WITHHOLDING_NOT_CORPORATE_RATE', 'Non-resident dividend WHT compliance duty, '
         'not the corporate rate.'),
    'Ndiyo, kiwango cha kodi ya zuio kwa gawio la kampuni ambazo hisa zake zinauzwa':
        ('DIVIDEND_WITHHOLDING_NOT_CORPORATE_RATE', 'Confirms the 5% dividend WHT rate for '
         'DSE-listed companies -- para 4(b), not para 3.'),
    'Ndiyo, kama unamiliki chini ya 25% ya hisa za DSE':
        ('CAPITAL_GAINS_NOT_CORPORATE_RATE',
         'Capital-gains exemption on realising DSE shares for a <25%-owning resident -- a '
         'DIFFERENT statutory threshold (Second Schedule realisation-gains exemption), not '
         'the para 3(2)(a) public-float condition for the corporate RATE.'),
    'Kimaanishacho ni kwamba umiliki wako wa hisa za DSE ni mdogo':
        ('CAPITAL_GAINS_NOT_CORPORATE_RATE', 'Same capital-gains-exemption topic as above.'),
    'Utawala wa kodi kuhusu mauzo ya hisa za DSE kwa wenye umiliki chini ya asilimia 25':
        ('CAPITAL_GAINS_NOT_CORPORATE_RATE', 'Same capital-gains-exemption topic, hedged '
         '("haipo wazi") rather than asserted as settled.'),
    'Samahani, ushauri wa uwekezaji kwenye hisa za soko liko nje ya mada yangu':
        ('OUT_OF_SCOPE_REFUSAL', 'Investment-advice refusal, no tax claim.'),
    'Samahani, ushauri wa uchaguzi wa hisa za soko liko nje ya mada yangu':
        ('OUT_OF_SCOPE_REFUSAL', 'Investment-advice refusal, no tax claim.'),
}


def rel(p):
    return os.path.relpath(p, REPO).replace('\\', '/')


def _text_of(obj):
    return (obj.get('answer_sw') or obj.get('output') or obj.get('question_sw')
            or obj.get('instruction') or '')


def _classify(text):
    key = text[:60]
    for prefix, verdict in _CLASSIFICATIONS.items():
        if text.startswith(prefix) or prefix in text[:len(prefix) + 20]:
            return verdict
    return ('UNCLASSIFIED', 'Not read during the 2026-09-01 manual pass -- needs review, '
            'treated as NOT cleared rather than silently passed.')


def main():
    seen = {}
    for f in sorted(glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True)):
        r = rel(f)
        if 'rejected/' in r:
            continue
        for i, line in enumerate(open(f, encoding='utf-8')):
            if not line.strip() or not _DSE_CTX.search(line):
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            text = _text_of(obj)
            key = obj.get('id') or text[:80]
            if key in seen:
                seen[key]['occurrences'].append({'file': r, 'line': i + 1})
                continue
            label, reason = _classify(text)
            seen[key] = {
                'id': obj.get('id'), 'text': text[:400], 'label': label, 'reason': reason,
                'occurrences': [{'file': r, 'line': i + 1}],
            }

    rows = list(seen.values())
    corporate_rate_rows = [r for r in rows if r['label'] == 'CORPORATE_RATE_TOPIC']
    unclassified = [r for r in rows if r['label'] == 'UNCLASSIFIED']

    defect_hits = []
    for row in corporate_rate_rows:
        t = row['text']
        if _STALE_FLOAT_30.search(t):
            defect_hits.append({**row, 'defect': 'STALE_FLOAT_30'})
        if _CONFLATION_25.search(t):
            defect_hits.append({**row, 'defect': 'CONFLATION_25_EQUALS_25'})

    report = {
        'measured': '2026-09-01',
        'harness': 'scripts/verify_dse_conflation_2026_09_01.py',
        'purpose': 'Re-verify the DSE public-float/rate conflation is fully swept, not just the '
                   'stale-30% shape v6 already quarantined -- run comprehensively rather than '
                   'assumed closed.',
        'total_unique_dse_rows_outside_rejected': len(rows),
        'by_label': {},
        'corporate_rate_topic_rows': len(corporate_rate_rows),
        'unclassified_rows': len(unclassified),
        'defect_hits': defect_hits,
        'clean': len(defect_hits) == 0 and len(unclassified) == 0,
        'rows': rows,
    }
    for row in rows:
        report['by_label'][row['label']] = report['by_label'].get(row['label'], 0) + 1

    print(json.dumps({k: v for k, v in report.items() if k != 'rows'},
                     ensure_ascii=False, indent=1))
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(f'[saved] {OUT}')
    if not report['clean']:
        print('\n*** DEFECT HITS OR UNCLASSIFIED ROWS FOUND -- see the artifact ***')
        sys.exit(1)


if __name__ == '__main__':
    main()

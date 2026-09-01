# -*- coding: utf-8 -*-
"""Bootstrap census: add `verified_as_at` to every locked fact, populated ONLY where
`verified_by` shows a REAL primary-source read with an explicit date attached to that read --
never inferred from `verified_date`/`effective_date`, which this same 2026-09-01 session found
to be edit-metadata for at least one fact (paye_nonresident_flat_rate carried `verified_date:
2026-06-16` while its `verified_by` named only a PWC page -- a date that looked like
verification and recorded when the JSON was last touched instead).

WHY THIS IS DELIBERATELY CONSERVATIVE. "An honest small number beats a populated field nobody
can trust" (founder instruction). A fact is only marked PRIMARY_VERIFIED if `verified_by`
contains an explicit primary-source-engagement phrase (direct/verbatim read, quoted verbatim,
a source pass that read the Act in full) AND an explicit ISO-ish date sits in that same string
-- not pulled from a sibling field, which would silently reintroduce the exact ambiguity this
census exists to remove. Every other fact -- secondary-sourced, portal-only, missing
verified_by entirely, or primary-shaped language with no date attached -- gets
`verified_as_at: "unknown"` explicitly. That "unknown" bucket IS the backlog, not a failure of
this script.

THIS DOES NOT VERIFY ANYTHING ITSELF. It classifies existing text. A fact marked
PRIMARY_VERIFIED was verified by whoever wrote that `verified_by` string, not by this script --
this script's only job is to stop pretending the OTHER facts were, by refusing to manufacture
a date field where the evidence for one does not exist.

R18: committed before running.
Artifact: eval/results/verified_as_at_bootstrap_census_2026_09_01.json
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FACTS_PATH = os.path.join(REPO, 'scripts', 'locked_facts.json')
OUT = os.path.join(REPO, 'eval', 'results', 'verified_as_at_bootstrap_census_2026_09_01.json')

# Strong positive: language that only makes sense if someone actually opened the primary text.
# "direct\s+(verbatim\s+)?read\b" WITHOUT requiring "of" immediately after -- broadened from an
# initial "read of" requirement after a live miss (R17-style spot-check, not assumed correct):
# vat_standard_rate ("direct read, 2026-08-29") and wcf_rate_0_5_percent_confirmed ("direct
# read (media.tanzlii.org), 2026-08-29") both use "direct read" without a following "of" and
# were wrongly bucketed into unknown on the first pass. Checked this broadening does NOT
# accidentally match the negated form: minimum_directors/minimum_shareholders both contain
# "not directly read" -- "directly" has no whitespace after "direct" (direct-LY), so
# "direct\s+read" cannot match inside it. Confirmed by re-running against all four rows.
_PRIMARY_READ = re.compile(
    r'direct\s+(verbatim\s+)?read\b|'
    r'read\s+[^.]{0,40}\bverbatim\b|'
    r'quoted\s+verbatim|'
    r'fetched\s+in\s+full|'
    r'read\s+(in\s+)?full\b|'
    r'full\s+\d+\s*pp\s+act\s+read\s+and\s+quoted\s+verbatim|'
    r'source\s+pass[^.]{0,60}read\s+and\s+quoted\s+verbatim',
    re.I)

# An explicit date in the SAME string as the primary-read language -- ISO (2026-08-31) or
# "Month YYYY" (August 2026) forms actually observed in this corpus. ISO preferred when both
# appear; only the first match is used, since a verified_by string documenting one read event
# should not carry two dates meaning different things.
_ISO_DATE = re.compile(r'\b(20\d{2}-\d{2}-\d{2})\b')
_MONTH_YEAR = re.compile(
    r'\b(January|February|March|April|May|June|July|August|September|October|November|'
    r'December)\s+(20\d{2})\b', re.I)


def _extract_date(text):
    m = _ISO_DATE.search(text)
    if m:
        return m.group(1)
    m = _MONTH_YEAR.search(text)
    if m:
        return f'{m.group(2)}-{m.group(1)[:3]}'  # e.g. "2026-Jun", flagged as month-precision
    return None


def classify(fact_obj):
    vb = fact_obj.get('verified_by', '') or ''
    if not vb:
        return 'unknown', None, 'no verified_by field at all'
    if not _PRIMARY_READ.search(vb):
        return 'unknown', None, 'verified_by present but no primary-source-read language found'
    date = _extract_date(vb)
    if date is None:
        return 'unknown', None, (
            'primary-read language found but no explicit date in the same string -- '
            'NOT inferred from verified_date/effective_date, per instruction')
    return 'primary_verified', date, 'direct/verbatim primary-source read with an explicit date'


def main():
    with io.open(FACTS_PATH, encoding='utf-8') as f:
        facts = json.load(f)

    rows = []
    verified_count = 0
    unknown_count = 0
    for key, obj in facts.items():
        if key.startswith('_') or not isinstance(obj, dict):
            continue
        status, date, reason = classify(obj)
        obj['verified_as_at'] = date if status == 'primary_verified' else 'unknown'
        rows.append({'key': key, 'status': status, 'verified_as_at': obj['verified_as_at'],
                     'reason': reason, 'verified_by_excerpt': (obj.get('verified_by') or '')[:160]})
        if status == 'primary_verified':
            verified_count += 1
        else:
            unknown_count += 1

    with io.open(FACTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(facts, f, ensure_ascii=False, indent=2)

    report = {
        'measured': '2026-09-01',
        'harness': 'scripts/bootstrap_verified_as_at.py',
        'purpose': 'Bootstrap census: verified_as_at populated ONLY from explicit primary-'
                   'source-read language + an explicit date in the SAME verified_by string. '
                   'Never inferred from verified_date/effective_date.',
        'total_facts': len(rows),
        'primary_verified': verified_count,
        'unknown_backlog': unknown_count,
        'rows': rows,
    }
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'},
                     ensure_ascii=False, indent=1))
    with io.open(OUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

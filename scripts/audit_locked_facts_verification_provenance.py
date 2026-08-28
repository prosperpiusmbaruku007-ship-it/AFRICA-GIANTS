# -*- coding: utf-8 -*-
"""Audit locked_facts.json for the same verification defect corporate_tax_rate has: a
`verified_by` naming a summary, portal or practitioner source rather than the statute or
gazette text itself.

WHY THIS MATTERS. CLAUDE.md's "A CONSOLIDATED ACT IS NOT THE CURRENT LAW" section proved this
exact failure mode twice: Cap 332 R.E. 2019 -- hosted on tra.go.tz itself -- still printed the
pre-2022 presumptive-tax table after Finance Act 2022 s.72 replaced it, and TRA's own "At a
Glance 2025/26" summary printed a transport-levy row the enacted Finance Act 2024 does not
contain. **A government portal or a practitioner summary can both be wrong about what the
statute currently says, and neither differs from "the Act" in a way `verified_by` currently
records.** `corporate_tax_rate` ("verified_by": "TRA Corporation Tax page") was found to have
exactly this shape while scoping the corporate/partnership income tax domain (2026-08-28) --
this script asks how many other locked facts share it, before deciding whether to re-verify a
handful or treat it as a whole-corpus finding.

CLASSIFICATION, and why it needs three buckets, not two. A fact is GROUNDED if `verified_by`
names an Act, Cap number, GN number, statute section, or gazette text explicitly -- the
project's own standard, stated in CLAUDE.md's "A CONSOLIDATED ACT" section. It is SUMMARY_ONLY
if `verified_by` names only a government portal page, a practitioner firm's advisory/summary, a
foreign payroll SaaS vendor, or similar -- with no statute/gazette reference anywhere. A third
bucket, UNCLEAR, catches entries with no source at all (`manual_review`, an internal note about
retrieval targeting rather than a source).

THE SECOND PASS THIS SCRIPT RUNS, AND WHY IT IS NOT OPTIONAL. A bare `verified_by` string can
understate a fact's real grounding: four of the five 2026-08-25 local-levy facts say only
"source pass 2026-08-16" in `verified_by`, but their `fact` text cites Cap 290/Cap 106 sections
directly (one sibling, `council_service_levy_is_a_cap_not_a_rate`, fully documents this as "full
62pp Act read and quoted verbatim" -- the other four just never got the same verified_by
sentence). Counting those four as genuinely summary-sourced would conflate a DOCUMENTATION GAP
(the Act was read; verified_by wasn't updated to say so) with a PROVENANCE GAP (the Act was
never read; only a summary was). This script checks each SUMMARY_ONLY row's `fact` text (and
`primary_source`/`source_note` if present) for the same statute markers, and reports the two
counts separately: raw SUMMARY_ONLY by `verified_by` text alone, and net SUMMARY_ONLY after
excluding rows whose fact/source_note/primary_source text independently shows statute grounding.

R18: committed before its count is cited in PROGRESS.md or reported to the founder.
Artifact: eval/results/locked_facts_verification_provenance_audit.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FACTS = os.path.join(REPO, 'scripts', 'locked_facts.json')
OUT = os.path.join(REPO, 'eval', 'results', 'locked_facts_verification_provenance_audit.json')

STATUTE_MARKERS = re.compile(
    r'\bAct\b|\bCap\.?\s*\d|\bGN\s*\d|\bs\.\s*\d|\bsection\s+\d|gazette text|'
    r'primary legislation|primary source|quoted verbatim|Government Notice',
    re.IGNORECASE)

NO_SOURCE_MARKERS = ('manual_review', 'retrieval-targeted companion')

# Manually reviewed exceptions to the automatic doc-gap check below. The regex on fact/
# source_note/primary_source text over-counts two shapes it cannot tell apart from real
# grounding: (1) a fact that NAMES a GN/Act as its topic without that number being evidence the
# SPECIFIC CLAIM in the fact was checked against statute text, and (2) a citation that is a
# practitioner's citation of an Act, not our own read of it -- the same one-hop-removed problem
# corporate_tax_rate has, just with a correct-looking Act name attached.
_MANUAL_KEEP_SUMMARY_ONLY = {
    'gn605a_average_increase': (
        "Fact text names 'GN 605A' as its topic and primary_source points at the gazette URL, "
        "so the regex sees statute markers -- but the SPECIFIC NUMBER here (33.4% average "
        "across 46 sub-sectors) is a computed aggregate, and verified_by names only a press "
        "briefing. Nothing here shows the aggregate was independently computed from the "
        "gazette's own tables rather than taken from the briefing."),
    'gn487a_mgeni_cap357_definition': (
        "Fact text restates Cap.357's structure, which the regex reads as a statute citation -- "
        "but verified_by is 'Clyde & Co practical implications article', a practitioner's "
        "citation of the Act, not our own read of it. Same one-hop-removed problem as "
        "corporate_tax_rate, with a correctly-named Act attached. The fact's own closing line "
        "-- 'this is a legal interpretation that must be verified with an immigration lawyer' "
        "-- is itself an admission this was never independently verified against the statute."),
}


def classify(key, v):
    vb = v.get('verified_by', '')
    if any(m in vb for m in NO_SOURCE_MARKERS):
        return 'unclear'
    if STATUTE_MARKERS.search(vb):
        return 'grounded'
    return 'summary_only'


def independently_grounded(key, v):
    """Does the fact text, source_note, or primary_source show statute grounding even though
    verified_by does not name it? Distinguishes a documentation gap from a provenance gap.
    Manually reviewed exceptions in _MANUAL_KEEP_SUMMARY_ONLY override a bare keyword match --
    see their comments for why the regex's positive is not real grounding in those two cases."""
    if key in _MANUAL_KEEP_SUMMARY_ONLY:
        return False
    blob = ' '.join(str(v.get(f, '')) for f in ('fact', 'source_note', 'primary_source'))
    return bool(STATUTE_MARKERS.search(blob))


def main():
    with open(FACTS, encoding='utf-8') as f:
        facts = json.load(f)

    total = len(facts)
    with_vb = {k: v for k, v in facts.items() if isinstance(v, dict) and 'verified_by' in v}
    without_vb = total - len(with_vb)

    buckets = {'grounded': [], 'summary_only': [], 'unclear': []}
    for k, v in with_vb.items():
        buckets[classify(k, v)].append(k)

    summary_only_raw = buckets['summary_only']
    doc_gap_only = [k for k in summary_only_raw if independently_grounded(k, facts[k])]
    summary_only_net = [k for k in summary_only_raw if k not in doc_gap_only]

    out = {
        'measured': '2026-08-28',
        'harness': 'scripts/audit_locked_facts_verification_provenance.py',
        'total_locked_facts': total,
        'facts_with_verified_by_field': len(with_vb),
        'facts_with_no_verified_by_field': without_vb,
        'note_on_no_verified_by': (
            f'{without_vb} facts have no verified_by field at all -- a separate, adjacent data-'
            'hygiene gap (no verification record at all, vs. a recorded-but-summary-sourced '
            'one). Not counted in the buckets below; not what was asked, flagged for a separate '
            'decision.'),
        'grounded_count': len(buckets['grounded']),
        'summary_only_raw_count': len(summary_only_raw),
        'summary_only_net_count_after_doc_gap_exclusion': len(summary_only_net),
        'doc_gap_only_count': len(doc_gap_only),
        'unclear_count': len(buckets['unclear']),
        'doc_gap_only_keys': doc_gap_only,
        'doc_gap_only_note': (
            "These name only a summary source in verified_by, but their fact/source_note/"
            "primary_source text independently cites a statute section -- a documentation gap "
            "(verified_by wasn't updated), not a provenance gap (the Act was never read). "
            "Excluded from the net summary-only count."),
        'summary_only_net_keys': sorted(summary_only_net),
        'grounded_keys': sorted(buckets['grounded']),
        'unclear_keys': sorted(buckets['unclear']),
        'verified_by_text': {k: facts[k].get('verified_by', '') for k in facts if isinstance(facts[k], dict) and 'verified_by' in facts[k]},
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"total locked facts: {total}")
    print(f"with verified_by: {len(with_vb)}  (without: {without_vb})")
    print(f"  grounded (Act/Cap/GN/section/gazette named): {len(buckets['grounded'])}")
    print(f"  summary/portal/practitioner only (raw):       {len(summary_only_raw)}")
    print(f"  summary-only NET (after doc-gap exclusion):   {len(summary_only_net)}")
    print(f"  doc-gap-only (excluded, Act cited elsewhere): {len(doc_gap_only)}")
    print(f"  unclear/no source:                            {len(buckets['unclear'])}")
    print(f'\n[saved] {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

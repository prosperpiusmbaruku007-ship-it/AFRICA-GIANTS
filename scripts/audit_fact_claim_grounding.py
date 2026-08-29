# -*- coding: utf-8 -*-
"""FABRICATION-CLASS AUDIT -- does a fact's own claim appear in its own cited sources?

WHY THIS IS A DIFFERENT CHECK FROM THE PROVENANCE AUDIT (v1/v2). Those ask "does this fact cite
a statute/gazette at all?" -- they classify grounded vs ungrounded. That question cannot tell
ungrounded-but-true apart from INVENTED. Both `nssf_retirement_age`'s "(55 for mining/early
retirement)" and the corpus's PAYE-band-2-at-9% defect are the second kind: a claim that exists
in the corpus and in NONE of its own cited sources. Re-verifying `nssf_retirement_age` against
NSSF Act Cap.50 (2026-08-29) found "mining" nowhere in Part V, and nowhere in either of the two
sources the fact was ORIGINALLY verified against (Mywage.org, a US SSA Tanzania country profile)
-- neither source says it either. A fact can name the right Act and still fail this check, because
this check is not about whether the Act is right -- it's about whether the SPECIFIC QUALIFIER in
the claim has any textual support anywhere the fact itself points to.

SCOPE, STATED PLAINLY (R20: say exactly what a check catches, not more) -- AND NARROWED ONCE
ALREADY BY ITS OWN SELF-TEST. The first version matched ANY salient word in a parenthetical
against the citation blob. Its own R26 clean-pass check immediately found the overbroad case:
a legitimate parenthetical describing "(private and public sector)" flagged, because generic
scope words have no reason to reappear in a citation string either -- the detector could not
tell a SCOPE-NARROWING claim (which needs its own support) from ordinary elaboration (which
doesn't). Per R17's "prefer the narrowest form that closes the case," the check now fires ONLY
when a parenthetical names a SPECIFIC ECONOMIC SECTOR from a curated list (mining/madini,
agriculture/kilimo, fishing/uvuvi, construction/ujenzi, tourism/utalii, transport/usafirishaji,
telecom, textile, energy, manufacturing, and their common variants) that does not appear anywhere
in the fact's own citation fields. This is exactly the shape of the found defect -- a sector name
invented as a qualifier with no source naming that sector at all -- and deliberately does NOT
fire on generic scope words ("private and public sector", "for everyone", "both categories"),
which is a real distinction, not a loophole: a sector-specific carve-out is an extraordinary claim
that needs its own citation, while "applies broadly" is the default a rule needs no extra citation
for.

It does NOT verify the qualifier against the live source document (that requires the
fetch-and-read pass this project's research agents do) -- it only checks self-consistency between
what the fact CLAIMS and what the fact's own PAPER TRAIL says. A sector claim can pass this check
and still be wrong if a citation was invented to match it; it can also fail this check and turn
out to be a real, just poorly-cited, sector carve-out. This audit is a triage signal, not a
verdict -- exactly like v1/v2's "grounded/ungrounded" was a triage signal, not a correctness one.

R26: a check that never fires and never could is worthless from the outside, and one that fires on
legitimate input is worse than useless -- it was proven wrong by ITS OWN FIRST SELF-TEST before it
ever ran over the real file. PROVE_SELF() now asserts three things: fires on a fact shaped exactly
like the pre-correction `nssf_retirement_age`; stays quiet on a legitimately-cited sector claim;
and -- the regression that matters, since this is the exact case that broke version one -- stays
quiet on a generic "(private and public sector)" scope qualifier. If any assertion fails, the
script refuses to run the real audit, on the theory that a census built on an unproven detector is
worse than no census (R20).

R18: committed before its count is cited.
Artifact: eval/results/fact_claim_grounding_audit.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FACTS = os.path.join(REPO, 'scripts', 'locked_facts.json')
OUT = os.path.join(REPO, 'eval', 'results', 'fact_claim_grounding_audit.json')

CITATION_FIELDS = ('verified_by', 'primary_source', 'source', 'section', 'source_note',
                    'correction_note')

PAREN = re.compile(r'\(([^()]{3,120})\)')

# A parenthetical matching any of these IS a citation, not a claim -- exclude it.
SELF_EVIDENT_CITATION = re.compile(
    r'^\s*[\d,./\- ]+\s*$'                          # bare number/date, e.g. "(2018-07-01)"
    r'|\bs\.?\s*\d|\bsection\s+\d|\bcap\.?\s*\d|\bgn\s*\d|\bact\s+no|\breg(ulation)?s?\.?\s*\d',
    re.IGNORECASE)

# Curated, not exhaustive -- a specific-sector name is an EXTRAORDINARY qualifier that needs its
# own citation; generic scope words ("private and public sector", "for everyone") are the
# default a rule needs no extra citation for. English + common Swahili variants.
SECTOR_TERMS = {
    'mining': 'madini', 'madini': 'madini',
    'agriculture': 'kilimo', 'agricultural': 'kilimo', 'kilimo': 'kilimo',
    'fishing': 'uvuvi', 'uvuvi': 'uvuvi',
    'construction': 'ujenzi', 'ujenzi': 'ujenzi',
    'tourism': 'utalii', 'utalii': 'utalii',
    'transport': 'usafirishaji', 'transportation': 'usafirishaji', 'usafirishaji': 'usafirishaji',
    'telecom': 'mawasiliano', 'telecommunications': 'mawasiliano', 'mawasiliano': 'mawasiliano',
    'textile': 'nguo', 'textiles': 'nguo',
    'energy': 'nishati', 'nishati': 'nishati',
    'manufacturing': 'uzalishaji', 'uzalishaji': 'uzalishaji',
    'aviation': 'anga', 'maritime': 'baharini', 'oil': 'mafuta', 'gas': 'gesi',
    'forestry': 'misitu', 'misitu': 'misitu',
    'education': 'elimu', 'elimu': 'elimu',
    'healthcare': 'afya', 'health': 'afya', 'afya': 'afya',
    'banking': 'benki', 'financial': 'kifedha',
}


def citation_blob(entry):
    if not isinstance(entry, dict):
        return ''
    parts = [str(entry.get(f, '')) for f in CITATION_FIELDS]
    return ' '.join(parts).lower()


def sector_terms_in(text):
    lowered = text.lower()
    return {term for term in SECTOR_TERMS if re.search(r'\b' + re.escape(term) + r'\b', lowered)}


def check_fact(fact_text, blob):
    """Returns a list of unsupported sector-specific parenthetical qualifiers, or [] if none."""
    if not isinstance(fact_text, str):
        return []
    flags = []
    for m in PAREN.finditer(fact_text):
        inner = m.group(1).strip()
        if SELF_EVIDENT_CITATION.search(inner):
            continue
        sectors = sector_terms_in(inner)
        if not sectors:
            continue  # no named sector in this parenthetical -- not this check's target
        if not any(term in blob for term in sectors):
            flags.append(inner)
    return flags


def prove_self():
    """R26: the detector must fire on the exact shape it exists to catch, stay quiet on a
    legitimately-cited sector claim, AND stay quiet on the generic-scope regression that broke
    version one of this script. Refuses to proceed if any check fails."""
    bad = {
        'fact': 'NSSF retirement age is 60 (55 for mining/early retirement), minimum 180 months',
        'verified_by': 'Mywage.org + US SSA Tanzania profile',
        'primary_source': 'https://www.nssf.go.tz',
    }
    good_cited_sector = {
        'fact': 'Presumptive tax has a special rate (agriculture sector only), per Finance Act 2022',
        'verified_by': 'Finance Act 2022 s.72, direct read -- agriculture carve-out confirmed',
        'primary_source': 'Finance Act 2022',
    }
    good_generic_scope = {
        'fact': 'WCF rate is 0.5% for all employers (private and public sector), per GN 169/2015',
        'verified_by': 'GN 169/2015 direct read, media.tanzlii.org',
        'primary_source': 'Workers Compensation (Payment of Tariff) Regulations, 2015',
    }
    bad_flags = check_fact(bad['fact'], citation_blob(bad))
    good_sector_flags = check_fact(good_cited_sector['fact'], citation_blob(good_cited_sector))
    good_generic_flags = check_fact(good_generic_scope['fact'], citation_blob(good_generic_scope))
    assert bad_flags, (
        'R26 FIRES check failed: the detector did not flag a fact shaped exactly like the '
        'known pre-correction nssf_retirement_age fabrication. Refusing to run the real audit.')
    assert not good_sector_flags, (
        f'R26 CLEAN-PASS check failed: the detector flagged a sector claim whose own citation '
        f'names that exact sector ({good_sector_flags!r}). Refusing to run the real audit.')
    assert not good_generic_flags, (
        f'R26 REGRESSION check failed: the detector flagged the generic "(private and public '
        f'sector)" scope qualifier that broke version one of this script '
        f'({good_generic_flags!r}). Refusing to run the real audit -- an overbroad detector '
        f'produces a census nobody can trust.')
    return {
        'fires_on_known_bad': bad_flags,
        'clean_on_cited_sector_claim': True,
        'clean_on_generic_scope_regression': True,
    }


# R26's SECOND HALF, applied to this audit's own first run: a flag that doesn't fire is not a
# defect until a bad specimen is ruled out. Manually triaged immediately after the first run
# produced 2 flags -- recorded here so the disposition survives, per the same discipline CLAUDE.md
# already requires of every other control in this project.
MANUAL_TRIAGE = {
    'osha_vs_wcf_roles': {
        'flagged': 'Occupational Safety and Health Authority',
        'verdict': 'FALSE POSITIVE -- bad specimen, not a defect',
        'why': '"Health" matched the sector-term list, but this is OSHA\'s own institutional '
               'name ("Occupational Safety and HEALTH Authority"), not a sector-scope claim. '
               'The parenthetical is a proper noun, not a qualifier needing separate citation.',
    },
    'GN605A_rate_range': {
        'flagged': 'energy sector international companies',
        'verdict': 'PLAUSIBLE, UNCONFIRMED -- not a false positive, not yet verified either',
        'why': 'The only citation is "PKF Eastern Africa GN 605A PDF Oct 2025" -- a document '
               'that would very plausibly contain a per-sector wage table naming the energy '
               'sector, but the citation STRING itself does not repeat the word "energy," so '
               'this audit (which checks metadata text, not document content) cannot confirm '
               'it. Exactly the audit\'s stated limitation: a real sector carve-out with a '
               'citation that is right but under-specific reads the same as an invented one.',
    },
}


def main():
    self_test = prove_self()

    with open(FACTS, encoding='utf-8') as fh:
        data = json.load(fh)

    flagged, checked, excluded_parens = [], 0, []
    for key, entry in sorted(data.items()):
        if key.startswith('_'):
            continue
        if not isinstance(entry, dict) or 'fact' not in entry:
            continue
        checked += 1
        blob = citation_blob(entry)
        unsupported = check_fact(entry['fact'], blob)
        if unsupported:
            flagged.append({
                'key': key,
                'unsupported_qualifiers': unsupported,
                'fact': entry['fact'],
                'citation_fields_present': [f for f in CITATION_FIELDS if entry.get(f)],
                'manual_triage': MANUAL_TRIAGE.get(key, 'NOT YET TRIAGED'),
            })

    report = {
        'measured': '2026-08-29',
        'harness': 'scripts/audit_fact_claim_grounding.py',
        'scope_statement': (
            'Flags a PARENTHETICAL QUALIFIER that names a SPECIFIC ECONOMIC SECTOR (curated '
            'list) which appears nowhere in that fact\'s own citation fields. Does not verify '
            'against the live source document. Does not catch fabrications outside a '
            'parenthetical, fabrications naming something other than a sector, or a '
            'fabrication whose citation was invented to match it. Triage signal, not a verdict '
            '-- every flag needs manual triage (see MANUAL_TRIAGE) before being treated as a '
            'confirmed defect.'),
        'self_test': self_test,
        'facts_checked': checked,
        'facts_flagged': len(flagged),
        'flagged': flagged,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print(json.dumps({k: v for k, v in report.items() if k != 'flagged'},
                      ensure_ascii=False, indent=2))
    print(f'\n{len(flagged)} fact(s) flagged:')
    for f in flagged:
        print(f"  - {f['key']}: {f['unsupported_qualifiers']}")
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

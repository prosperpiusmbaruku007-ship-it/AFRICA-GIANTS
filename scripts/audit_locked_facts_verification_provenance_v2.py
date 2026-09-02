# -*- coding: utf-8 -*-
"""v2 of the provenance audit -- CORRECTS a real gap found in v1 the same day it was reported.

WHAT WAS WRONG WITH v1 (`audit_locked_facts_verification_provenance.py`). It classified only by
the `verified_by` field. Reading a sample of the "178 facts with no verified_by" while scoping
the exposure-sizing request that followed v1's count found `locked_facts.json` actually carries
AT LEAST THREE separate provenance schemes, not one:

  1. `verified_by` (+ `primary_source`)      -- what v1 checked.                       75 facts
  2. `source` (+ `section`)                  -- an OLDER scheme: a downloaded Act/gazette
     PDF path (e.g. `data/source_documents/nssf/nssf_act_cap50.pdf`) plus the specific
     clause read (e.g. "Payment 14.-(3)"). v1 counted every one of these as "no
     verified_by" -- i.e. as ungrounded -- when most of them are MORE directly
     statute-grounded than the URL-only `verified_by` entries v1 called "grounded".   44 facts
  3. No structured provenance field at all, but the FACT TEXT or a `primary_source`
     field v1 didn't check for this subset embeds a citation inline
     (e.g. "primary_source": "https://tanzlii.org (Workers Compensation Act...)").
                                                                                        35 facts
  4. Bare non-dict values (`"annual_return_filing_fee": "22,000 TZS"`) -- genuinely no
     provenance field of any kind, dict or otherwise. 97 total; 42 are FACT_GROUPS
     members (their only possible grounding is whatever sourced the group's `text` in
     precompute_rag_embeddings.py, which carries no citation field either); 55 stand
     alone with nothing.
     42 group + 55 standalone

v1's "28 of 253 grounded, 11%" is corrected here because scheme 2 alone is 44 facts, most of
them genuinely statute-grounded (a downloaded copy of the NSSF Act itself, or the GN487A
gazette PDF, with a specific clause cited) -- more rigorously grounded than several of v1's own
28. Undercounting them as "no verified_by = ungrounded" would have UNDERSTATED grounding, the
opposite direction from every other finding in this audit, which is exactly why it needed
catching before the exposure-sizing analysis was built on top of it.

METHOD: one classifier over ALL 251 non-underscore keys (dict-valued and bare), checking a
single "provenance blob" per key -- every metadata field that could carry a citation
(`verified_by`, `primary_source`, `source`, `section`, `source_note`) plus the `fact` text
itself -- against the same STATUTE_MARKERS used in v1. Bare values have no such fields and are
classified by whether they are a FACT_GROUPS member (grounding, if any, lives with the group,
which itself has none recorded) or fully standalone.

Two manual overrides carried over from v1 (a fact NAMING a GN/Act is not the same claim as one
VERIFIED against it) plus the same check applied to the newly-examined scheme-2/3 facts.

R18: committed before its count is cited.
Artifact: eval/results/locked_facts_verification_provenance_audit_v2.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FACTS = os.path.join(REPO, 'scripts', 'locked_facts.json')
OUT = os.path.join(REPO, 'eval', 'results', 'locked_facts_verification_provenance_audit_v2.json')

sys.path.insert(0, HERE)
from precompute_rag_embeddings import _GROUP_MEMBERS  # noqa: E402

STATUTE_MARKERS = re.compile(
    r'\bAct\b|\bCap\.?\s*\d|\bGN\s*\d|\bs\.\s*\d|\bsection\s+\d|gazette|'
    r'primary legislation|primary source|quoted verbatim|Government Notice|tanzlii',
    re.IGNORECASE)


def _statute_search(blob):
    """`\\b` treats underscore as a word character, so `\\bAct\\b` never matches inside a file
    path like `nssf_act_cap50.pdf` -- found while sizing exposure on this audit's own output,
    when NSSF-Act-cited facts (source field IS the downloaded Act PDF, section field names the
    exact clause) showed up in the ungrounded set. Replacing underscores and path separators
    with spaces before matching restores real word boundaries without weakening the pattern for
    ordinary prose, where this substitution is a no-op."""
    return STATUTE_MARKERS.search(blob.replace('_', ' ').replace('\\', ' ').replace('/', ' '))

# Same standard as v1: naming the right statute is not the same claim as being verified against
# it. A practitioner's citation of an Act, or a fact naming a GN as its topic without the
# specific claim being checked against the gazette's own text, does not count.
#
# EACH OVERRIDE IS A PIN, AND PINS DECAY (R18, the 2026-08-17 stale-pins incident: verdicts
# pinned to index content that moved underneath them kept asserting the old verdict). Found here
# 2026-09-02, during the 141-vs-249 gap reconciliation: `gn487a_mgeni_cap357_definition`'s
# override reason ("verified_by is a law firm's article...") described a citation that was
# REPLACED on 2026-08-31 -- 9 DAYS before this file was next read closely -- by a direct read of
# GN487A s.2 and Cap.357 ss.3(1), 8-12, 30(1)(b). The override kept forcing 'summary_only' on a
# fact that had since become genuinely statute-grounded, and nothing would have caught it short
# of someone re-reading the override's own prose against the field it describes. Fixed the same
# way R18 fixed the index-pin version of this bug: each override now carries a `guard` fragment
# that must still be found in the CURRENT verified_by text, checked every run. A decayed guard
# raises instead of silently keeping the stale verdict -- removing an override quietly when its
# citation improves is exactly the failure this mechanism exists to stop.
_MANUAL_KEEP_SUMMARY_ONLY = {
    'gn605a_average_increase': {
        'reason': "Names GN 605A as topic; the specific 33.4% aggregate traces to a press "
                  "briefing, not a computed check against the gazette's own sector tables.",
        'guard': 'press briefing',
    },
}


def _live_manual_overrides(facts):
    """Re-checks every override's guard against the CURRENT field text on every run. A guard
    that no longer matches means the citation underneath it changed and the override must be
    re-examined by a human, not silently kept or silently dropped."""
    live = {}
    for key, entry in _MANUAL_KEEP_SUMMARY_ONLY.items():
        fact = facts.get(key)
        if not isinstance(fact, dict):
            raise AssertionError(
                f"_MANUAL_KEEP_SUMMARY_ONLY['{key}'] names a key that is no longer a dict-shaped "
                f"fact in locked_facts.json -- remove or update this override.")
        blob = ' '.join(str(fact.get(f, '')) for f in PROVENANCE_FIELDS).lower()
        if entry['guard'].lower() not in blob:
            raise AssertionError(
                f"STALE OVERRIDE: _MANUAL_KEEP_SUMMARY_ONLY['{key}']'s guard phrase "
                f"{entry['guard']!r} no longer appears in this fact's own provenance fields -- "
                f"the citation underneath this override has changed since it was written "
                f"(reason on file: {entry['reason']!r}). Re-examine the fact and either update "
                f"the guard to match the current text, or remove the override if the fact is now "
                f"genuinely grounded (this is exactly what happened to "
                f"gn487a_mgeni_cap357_definition on 2026-09-02 -- do not silently re-add a stale "
                f"guard to make this pass).")
        live[key] = entry['reason']
    return live


PROVENANCE_FIELDS = ('verified_by', 'primary_source', 'source', 'section', 'source_note')


def classify_dict_fact(key, v, live_overrides):
    if key in live_overrides:
        return 'summary_only'
    if not any(f in v for f in PROVENANCE_FIELDS):
        blob = str(v.get('fact', ''))
        if not blob.strip():
            return 'unclear_no_source'
        return 'grounded' if _statute_search(blob) else 'summary_only'
    blob = ' '.join(str(v.get(f, '')) for f in PROVENANCE_FIELDS) + ' ' + str(v.get('fact', ''))
    return 'grounded' if _statute_search(blob) else 'summary_only'


def main():
    with open(FACTS, encoding='utf-8') as f:
        facts = json.load(f)

    keys = [k for k in facts if not k.startswith('_')]
    dict_keys = [k for k in keys if isinstance(facts[k], dict)]
    bare_keys = [k for k in keys if not isinstance(facts[k], dict)]
    bare_group = [k for k in bare_keys if k in _GROUP_MEMBERS]
    bare_standalone = [k for k in bare_keys if k not in _GROUP_MEMBERS]

    live_overrides = _live_manual_overrides(facts)  # raises if any guard has gone stale

    buckets = {'grounded': [], 'summary_only': [], 'unclear_no_source': []}
    for k in dict_keys:
        buckets[classify_dict_fact(k, facts[k], live_overrides)].append(k)

    # Bare values carry no provenance field, dict or otherwise. Group membership is recorded
    # for context but does not change the classification -- the group's own text has no
    # citation field either (checked directly in precompute_rag_embeddings.py).
    bare_ungrounded = bare_group + bare_standalone

    total = len(keys)
    grounded = buckets['grounded']
    ungrounded = buckets['summary_only'] + buckets['unclear_no_source'] + bare_ungrounded

    out = {
        'measured': '2026-08-28',
        'harness': 'scripts/audit_locked_facts_verification_provenance_v2.py',
        'supersedes': 'scripts/audit_locked_facts_verification_provenance.py (v1) -- v1 checked '
                       'only the verified_by field and missed the source+section scheme (44 '
                       'facts, mostly grounded) and inline-citation cases (some of the 35 '
                       'neither-field facts) -- see this file docstring',
        'total_keys': total,
        'dict_valued_facts': len(dict_keys),
        'bare_valued_facts': len(bare_keys),
        'bare_group_members': len(bare_group),
        'bare_standalone': len(bare_standalone),
        'grounded_count': len(grounded),
        'grounded_pct_of_total': round(100 * len(grounded) / total, 1),
        'ungrounded_count': len(ungrounded),
        'ungrounded_pct_of_total': round(100 * len(ungrounded) / total, 1),
        'ungrounded_breakdown': {
            'summary_only_dict_facts': len(buckets['summary_only']),
            'unclear_no_source_dict_facts': len(buckets['unclear_no_source']),
            'bare_group_member_facts': len(bare_group),
            'bare_standalone_facts': len(bare_standalone),
        },
        'grounded_keys': sorted(grounded),
        'ungrounded_keys': sorted(ungrounded),
        'manual_overrides': live_overrides,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"total keys: {total}  (dict: {len(dict_keys)}, bare: {len(bare_keys)})")
    print(f"GROUNDED:   {len(grounded)}  ({out['grounded_pct_of_total']}%)")
    print(f"UNGROUNDED: {len(ungrounded)}  ({out['ungrounded_pct_of_total']}%)")
    print(f"  summary_only (dict):     {len(buckets['summary_only'])}")
    print(f"  unclear/no source (dict):{len(buckets['unclear_no_source'])}")
    print(f"  bare, group member:      {len(bare_group)}")
    print(f"  bare, standalone:        {len(bare_standalone)}")
    print(f'\n[saved] {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Scans every wrong_pattern in scripts/locked_facts.json for the defect found in
act_section_12 on 2026-09-23: AN ORDER-DEPENDENT PATTERN WRITTEN IN ENGLISH, GUARDING TEXT
THAT IS SERVED IN SWAHILI.

THE DEFECT, concretely. act_section_12's four patterns were all of the form
`<part|section> xii .* <foreign company>` -- token first, entity second, which is English
word order. The live Swahili rendering is "Kampuni ya kigeni (Section XII) ikichelewa..." --
entity FIRST, and using the English word "Section" rather than "kifungu". None of the four
matched it. The patterns were correct English and blind to the corpus they guard.

WHAT THIS SCAN FLAGS. A pattern is at risk when ALL THREE hold:
  (a) it is ORDER-DEPENDENT -- two or more literal segments joined by `.*` / `.{0,N}`, so
      the pattern asserts a sequence, not just a set of terms; and
  (b) its literal segments are ENGLISH-ONLY -- no Swahili function word (ya/za/wa/kwa/ni/
      cha/la/...) anywhere in the pattern; and
  (c) THE FACT'S OWN DEPLOYED RENDERING IS SWAHILI -- resolved per fact, either from
      CONCISE_BILINGUAL_FACTS (embedded with no key prefix) or from the `key: text` row in
      the deployed index.
A pattern that is order-dependent but contains Swahili was written against the Swahili
rendering. A pattern with no `.*` cannot have this defect at all: a bare substring matches
wherever it appears, in any order.

(c) IS THE CLAUSE THAT MAKES THIS USABLE, and it was added after the first run. Without it
the scan reported 200 hits out of 688 patterns -- and the great majority were English
patterns guarding facts whose deployed rendering is ALSO English, where English word order
is exactly right. Reporting those 200 would have sent someone to rewrite ~29% of every
guard in the corpus, all of them working. The defect is not "an English pattern"; it is a
LANGUAGE MISMATCH between a pattern and the text it guards, and only (c) can see a mismatch.

WHAT IT CANNOT DO, and this matters more than what it can. This is a STATIC scan over pattern
TEXT. It cannot tell an English-only order-dependent pattern that is genuinely broken from one
whose guarded rendering happens to be English too -- several facts in this corpus are rendered
in English in the index. So its output is a REVIEW QUEUE, not a defect list, and every hit
below is adjudicated by hand against that fact's actual deployed rendering. R26's second half
applies with full force: a false "broken pattern" sends someone to rewrite a working guard,
and a rewritten guard is a real behaviour change made by someone who believes they are
repairing something.

R18: committed with the write-up that cites it.
Artifact: eval/results/wrong_pattern_language_scan_2026_09_23.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FACTS = os.path.join(REPO, 'scripts', 'locked_facts.json')
INDEX = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
OUT = os.path.join(REPO, 'eval', 'results', 'wrong_pattern_language_scan_2026_09_23.json')

# Swahili function words. Presence of any one means the author had Swahili in mind.
SWAHILI_MARKERS = re.compile(
    r'\b(ya|za|wa|kwa|ni|cha|la|na|kila|si|hakuna|lazima|kama|yenye|zenye|katika|kwenye'
    r'|kodi|ada|faini|mshahara|mauzo|kampuni|mfanyakazi|mwajiri|kizingiti|asilimia)\b',
    re.I)

# The constructs that make a pattern assert an ORDER rather than a set.
ORDER_JOINER = re.compile(r'\.\*|\.\{\d+,\d*\}|\.\+')


def literal_segments(pattern):
    """Rough split of a regex into its literal chunks, for the English/Swahili judgement."""
    parts = ORDER_JOINER.split(pattern)
    return [re.sub(r'[\\^$|()\[\]{}?*+]', ' ', p).strip() for p in parts]


def load_concise():
    """CONCISE_BILINGUAL_FACTS from the embedding builder. These rows are embedded WITHOUT a
    `key: ` prefix (CLAUDE.md R15), so they cannot be resolved from the index by key -- which
    is exactly why act_section_12's row was never connected to its patterns by any check."""
    import importlib.util
    path = os.path.join(REPO, 'scripts', 'precompute_rag_embeddings.py')
    spec = importlib.util.spec_from_file_location('_pre', path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    return dict(getattr(mod, 'CONCISE_BILINGUAL_FACTS', {}) or {})


def resolve_rendering(key, index, concise):
    """The fact's OWN deployed text, and how it was found. None if it cannot be resolved."""
    if key in concise:
        return concise[key], 'concise_bilingual_facts'
    prefix = key.replace('_', ' ').lower() + ':'
    for row in index:
        if row.lower().startswith(prefix):
            return row, 'index_key_prefix'
    return None, 'unresolved'


def main():
    facts = json.load(open(FACTS, encoding='utf-8'))
    index = json.load(open(INDEX, encoding='utf-8'))
    concise = load_concise()
    assert concise, 'CONCISE_BILINGUAL_FACTS failed to load -- resolution would be blind'

    total_facts = total_patterns = 0
    flagged, safe_no_order, safe_swahili, safe_english_rendering, unresolved = [], 0, 0, 0, 0

    for key, val in facts.items():
        if key == '_meta' or not isinstance(val, dict):
            continue
        pats = val.get('wrong_patterns') or []
        if not pats:
            continue
        total_facts += 1
        rendering, how = resolve_rendering(key, index, concise)
        rendering_is_sw = bool(rendering and SWAHILI_MARKERS.search(rendering))
        for pat in pats:
            total_patterns += 1
            if not ORDER_JOINER.search(pat):
                safe_no_order += 1
                continue
            if SWAHILI_MARKERS.search(pat):
                safe_swahili += 1
                continue
            if rendering is None:
                unresolved += 1
                continue
            if not rendering_is_sw:
                safe_english_rendering += 1
                continue
            flagged.append({
                'fact_key': key,
                'pattern': pat,
                'literal_segments': [s for s in literal_segments(pat) if s],
                'rendering': rendering,
                'resolved_via': how,
                'pattern_matches_own_rendering': bool(re.search(pat, rendering, re.I)),
            })

    # R20: this scan must be able to report something other than clean. If the corpus ever
    # has zero order-dependent patterns, that is a fact about the corpus and the assertion
    # below documents it -- it must not look like a passing health check.
    assert total_patterns > 0, 'no wrong_patterns found at all -- loader or schema changed'

    print(f'facts with wrong_patterns: {total_facts}')
    print(f'patterns examined:         {total_patterns}')
    print(f'  not order-dependent (bare substring, cannot have this defect): {safe_no_order}')
    print(f'  order-dependent but written in Swahili:                       {safe_swahili}')
    print(f'  order-dependent English, guarding an ENGLISH rendering (fine): '
          f'{safe_english_rendering}')
    print(f'  rendering unresolvable -- cannot judge, NOT cleared:           {unresolved}')
    print(f'  ORDER-DEPENDENT ENGLISH vs SWAHILI RENDERING -> review:        {len(flagged)}\n')
    for f in flagged:
        print(f"  {f['fact_key']}   (resolved via {f['resolved_via']})")
        print(f"     pattern:   {f['pattern']}")
        print(f"     rendering: {f['rendering'][:100]}")
        print()

    blob = {
        'measured': '2026-09-23',
        'harness': 'eval/controls/scan_wrong_pattern_language_assumption.py',
        'found_by': 'act_section_12, whose four English-word-order patterns all failed to '
                    'match the Swahili index row they guarded (ext_15, live 2026-09-05)',
        'nature': 'REVIEW QUEUE, NOT A DEFECT LIST. Static scan over pattern text; it cannot '
                  'distinguish a broken English pattern from one whose guarded rendering is '
                  'also English. Every hit is hand-adjudicated before any edit (R26).',
        'totals': {'facts_with_patterns': total_facts, 'patterns': total_patterns,
                   'not_order_dependent': safe_no_order,
                   'order_dependent_swahili': safe_swahili,
                   'order_dependent_english_guarding_english': safe_english_rendering,
                   'rendering_unresolvable': unresolved,
                   'review_queue': len(flagged)},
        'review_queue': flagged,
    }
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(blob, fh, ensure_ascii=False, indent=2)
    print(f'[saved] {os.path.relpath(OUT, REPO)}')


if __name__ == '__main__':
    main()

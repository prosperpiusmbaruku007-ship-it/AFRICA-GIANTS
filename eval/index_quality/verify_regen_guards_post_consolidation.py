# -*- coding: utf-8 -*-
"""GUARD-SOUNDNESS RE-CHECK, post fee-consolidation (2026-08-26).

Text-only, no embeddings, no network -- the founder's instruction was explicit: do NOT run the
regen locally (R15 exists because local-e5 and Kaggle-e5 have diverged before). Anchor UNIQUENESS
is pure substring counting over build_fact_texts()'s output, which is deterministic and identical
in any Python environment -- it needs no model and answers a different question than retrieval
rank does: not "where does this fact rank for this query" (which DOES need the model and DOES need
to run on Kaggle) but "does this anchor string still identify exactly one row now that the index
shape changed."

WHY THIS EXISTS. The consolidation absorbs 42 rows into 3 group passages and adds 5 pending
local-levy rows (221 -> 187). Every existing critical_queries anchor in kaggle/regenerate_rag_e5.py
was verified unique against the OLD 221-row index (2026-08-22, regen_guard_audit.json). A row
being removed, or a new group passage repeating a common figure (the ladder text alone contains
three more "TZS 22,000"/"TZS 50,000"-shaped figures), can make a previously-unique anchor either
DEAD (its one occurrence was inside an absorbed row) or newly AMBIGUOUS (a group passage now also
contains it) -- and a guard whose anchor silently degrades would pass or fail for the wrong reason,
undetected, exactly the failure this project already paid for once (2026-08-22, three dead anchors
found hiding behind live siblings).

Also re-verifies the three ANCHORS needles from measure_feegroup_curation.py (nat_05/nat_23/nat_33
identification strings) are still unique post-consolidation, since the new rank-regression gate
being added to regenerate_rag_e5.py depends on them resolving to exactly one row.

R18: committed before its result is written up.
Artifact: eval/results/regen_guard_anchors_post_consolidation.json
"""
import ast
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
REGEN = os.path.join(REPO, 'kaggle', 'regenerate_rag_e5.py')
OUT = os.path.join(REPO, 'eval', 'results', 'regen_guard_anchors_post_consolidation.json')

sys.path.insert(0, os.path.join(REPO, 'scripts'))


def load_from_regen(name):
    with open(REGEN, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return ast.literal_eval(node.value)
    raise SystemExit(f'{name} not found in {REGEN}')


def anchor_report(texts, guards, accepted_ambiguous):
    dead, ambiguous, ok = [], [], []
    for name, _query, expected in guards:
        for kw in expected:
            hits = [i for i, t in enumerate(texts) if kw.lower() in t.lower()]
            if not hits:
                dead.append((name, kw))
            elif len(hits) > 1 and name not in accepted_ambiguous:
                ambiguous.append((name, kw, hits))
            else:
                ok.append((name, kw, hits))
    return dead, ambiguous, ok


def main():
    import precompute_rag_embeddings as pre

    with open(os.path.join(REPO, 'chike-inference', 'rag_facts_text.json'), encoding='utf-8') as f:
        old_texts = json.load(f)
    new_texts, _keys, _dropped = pre.build_fact_texts()

    guards = load_from_regen('critical_queries')
    accepted_ambiguous = set(load_from_regen('ACCEPTED_AMBIGUOUS'))

    old_dead, old_ambig, _ = anchor_report(old_texts, guards, accepted_ambiguous)
    new_dead, new_ambig, new_ok = anchor_report(new_texts, guards, accepted_ambiguous)

    # ANCHORS from measure_feegroup_curation.py -- the rank-regression gate's identification
    # strings. These must resolve to EXACTLY ONE row in the prospective index or the new gate
    # cannot even locate the fact whose rank it is supposed to check.
    curation_anchors = {
        'nat_05/nat_23 (SDL rate)': 'kiwango cha mafunzo ni asilimia tatu na nusu',
        'nat_33 (BRELA annual return fee)': (
            'ada ya kuwasilisha ritani (annual return) ya kampuni kila mwaka ni TZS 22,000'),
        'nat_43 (GN605A sector count, existing guard)': 'sekta 16 na sekta ndogo 46',
    }
    curation_check = {}
    for label, needle in curation_anchors.items():
        old_hits = [i for i, t in enumerate(old_texts) if needle in t]
        new_hits = [i for i, t in enumerate(new_texts) if needle in t]
        curation_check[label] = {
            'needle': needle, 'old_hits': old_hits, 'new_hits': new_hits,
            'still_unique': len(new_hits) == 1,
        }

    newly_broken = (
        [n for n in new_dead if n not in old_dead]
        + [a for a in new_ambig if a[:2] not in [(o[0], o[1]) for o in old_ambig]]
    )

    out = {
        'measured': '2026-08-26',
        'harness': 'eval/index_quality/verify_regen_guards_post_consolidation.py',
        'old_index_rows': len(old_texts), 'new_index_rows_prospective': len(new_texts),
        'old_dead_anchors': old_dead, 'old_ambiguous_anchors': old_ambig,
        'new_dead_anchors': new_dead, 'new_ambiguous_anchors': new_ambig,
        'newly_broken_by_consolidation': newly_broken,
        'sound': not new_dead and not new_ambig,
        'curation_rank_gate_anchors': curation_check,
        'curation_anchors_all_unique': all(v['still_unique'] for v in curation_check.values()),
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'index rows: {len(old_texts)} (shipped) -> {len(new_texts)} (prospective)')
    print(f'existing guard anchors: {len(guards)} guards')
    print(f'  dead   before={len(old_dead)} after={len(new_dead)}')
    print(f'  ambig  before={len(old_ambig)} after={len(new_ambig)}')
    if newly_broken:
        print(f'[BROKEN BY CONSOLIDATION] {newly_broken}')
    else:
        print('[OK] no guard anchor newly dead or ambiguous from the consolidation')
    print()
    for label, v in curation_check.items():
        status = 'OK' if v['still_unique'] else 'BROKEN'
        print(f'[{status}] {label}: {v["needle"]!r} -> old={v["old_hits"]} new={v["new_hits"]}')
    print(f'\n[saved] {OUT}')
    return 0 if (out['sound'] and out['curation_anchors_all_unique']) else 1


if __name__ == '__main__':
    sys.exit(main())

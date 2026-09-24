# -*- coding: utf-8 -*-
"""Validity check for the orthographic held-out set. Offline, no model, no cues yet.

⛔ THIS IS NOT THE MEASUREMENT. It checks that the FIXTURE is sound before anything is built
against it, and it is deliberately split so that reading it does not burn the half that prices
the cost of a future cue.

=== WHY THE SET EXISTS ===

`mrahaba` reached production, matched ZERO OOC phrases, and was refused only because the model
happened to judge well -- which R11 exists so we never depend on. The 2026-08-14 variant pass
covered the DIGRAPH family only (dh->z, th->s, gh->g: 11 word pairs), and its enforcing test is
named `test_every_swahili_digraph_phrase_has_its_variant`. Metathesis is a REORDERING, not a
substitution; vowel change, elision and DROPPED ASPIRATION are different again. Nothing has ever looked for them.

=== WHAT IS SEALED, AND WHY THE SPLIT IS NOT PEDANTRY (R21) ===

A held-out set is burned once its RESULTS are read, and the two limbs burn differently:

  OOC LIMB (20 rows, must REFUSE) -- reading this now is FINE and necessary. It establishes
    that the leak is real and which variants carry it. Fitting a cue to a leaked phrase is the
    intended work: the phrase IS the target. Nothing is overfitted by knowing the defect exists.

  IN-SCOPE LIMB (18 rows, must NOT be refused) -- SEALED. This limb prices the FALSE-REFUSAL
    cost, which is the expensive half (R21 measured a ~37x gap between corpus sweeps and
    held-out questions). Reading which rows a candidate cue would refuse, BEFORE the cue is
    frozen, is exactly how a cue gets tuned to a set and stops measuring anything.

    The ONE thing this script reads on the in-scope limb is which rows are ALREADY refused by
    the CURRENT phrase list. That is a statement about today's shipped behaviour, not about any
    future cue -- it identifies BAD SPECIMENS (rows that would appear to fail a new cue when the
    over-breadth predates it) in the same spirit as `_WITHHELD_PENDING_NARROWING` in
    tests/test_orthographic_variants.py. A row already refused today must be scored as
    pre-existing, never charged to the cue that comes next.

=== THE LINGUISTIC CAVEAT, STATED BECAUSE IT DECIDES WHAT THE SET IS WORTH ===

The variants are an authored reconstruction of how Tanzanian users mistype these words, not an
observed frequency distribution. Exactly ONE is attested from real traffic (`mrahaba`, oh_01);
the rest are plausible by construction. A native-speaker pass would strengthen the set and
should happen before the cue work, not after. Until then this measures REACHABILITY of the
variants we can imagine -- a lower bound on the gap, never an estimate of its size (R21).

Usage:  python eval/refusal_gate/validate_orthographic_heldout.py
"""
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from chike import classification                                     # noqa: E402

FIXTURE = os.path.join(REPO, 'eval', 'refusal_gate', 'orthographic_heldout_038.jsonl')


def main():
    rows = [json.loads(l) for l in open(FIXTURE, encoding='utf-8') if l.strip()]
    assert rows, 'no rows loaded -- a validity check over zero rows reports clean over nothing'

    cfg = os.path.join(REPO, 'kaggle', 'chike_config.json')
    ooc, in_scope = classification.resolve_phrases(json.load(open(cfg, encoding='utf-8')))
    print(f'[config] {len(ooc)} ooc phrases, {len(in_scope)} in-scope phrases\n')

    ids = [r['id'] for r in rows]
    assert len(ids) == len(set(ids)), 'duplicate ids'
    ooc_rows = [r for r in rows if r['limb'] == 'ooc']
    ins_rows = [r for r in rows if r['limb'] == 'in_scope']
    assert len(rows) == 38, f'expected 38 rows, got {len(rows)}'
    assert len(ooc_rows) == 20 and len(ins_rows) == 18, 'limbs must be 20/18'

    axes = collections.Counter(r['axis'] for r in ooc_rows)
    for axis in ('metathesis', 'vowel_change', 'elision', 'aspiration_drop'):
        assert axes[axis] >= 4, f'axis {axis} has only {axes[axis]} OOC rows -- too few to read'
    print(f'[fixture] OOC axes: {dict(axes)}')
    print(f'[fixture] in-scope collision rows: '
          f'{dict(collections.Counter(r["axis"] for r in ins_rows))}\n')

    # ---- OOC limb: readable now. Does the variant currently leak? --------------------
    print('=== OOC LIMB (must REFUSE) -- reading this is intended, the phrase IS the target ===')
    leaks = []
    for r in sorted(ooc_rows, key=lambda x: x['id']):
        in_scope_verdict = classification.classify(r['question_sw'], ooc, in_scope)
        matched = [p for p in ooc if p in r['question_sw'].lower()]
        leaking = in_scope_verdict is True
        if leaking:
            leaks.append(r['id'])
        print(f"  {r['id']}  {r['axis']:<13} {r['base']:>9} -> {r['variant']:<9} "
              f"{'LEAKS (not refused)' if leaking else 'refused'}"
              f"{'' if leaking else '  via ' + str(matched[:2])}")
    print(f'\n  LEAK RATE: {len(leaks)}/{len(ooc_rows)} -- {leaks}')
    print('  Every leaking row is a question the classifier does NOT catch, so refusal there '
          'depends entirely on the model judging well. That is the R11 dependency this set '
          'exists to remove.\n')

    # ---- In-scope limb: ONLY the pre-existing-refusal check ---------------------------
    print('=== IN-SCOPE LIMB (must NOT be refused) -- SEALED except for bad-specimen ID ===')
    pre_existing = []
    for r in sorted(ins_rows, key=lambda x: x['id']):
        ok = classification.classify(r['question_sw'], ooc, in_scope)
        if not ok:
            matched = [p for p in ooc if p in r['question_sw'].lower()]
            pre_existing.append((r['id'], r['topic'], matched))
    if pre_existing:
        print('  ALREADY REFUSED BY TODAY\'S SHIPPED LIST -- pre-existing over-breadth, and it '
              'must NEVER be charged to whatever cue is added next:')
        for rid, topic, matched in pre_existing:
            print(f'    {rid}  ({topic})  matched {matched}')
    else:
        print('  none -- every in-scope row passes the current list, so all 18 are clean '
              'specimens for the future cue measurement')
    print(f'\n  pre-existing false refusals: {len(pre_existing)}/{len(ins_rows)}')
    print('  NOT READ HERE, BY DESIGN: what any candidate cue would do to these rows. That is '
          'the measurement, it happens ONCE, after the cue set is frozen, and reading it early '
          'is what turns a held-out set into a fitted one.')


if __name__ == '__main__':
    main()

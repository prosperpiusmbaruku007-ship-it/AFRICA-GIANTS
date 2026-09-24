# -*- coding: utf-8 -*-
"""Tallies the paired-phrasing adjudication. Verdicts are DATA; this file only counts them.

WHAT IT ANSWERS: how often does CHIKE contradict itself when the same question is rephrased?
Population: 24 AUTHORED pairs, 6 each across covered_fact / gap / compute / boundary. This is
NOT a corpus-wide estimate and must never be cited as one (R22).

=== THE SCHEME IS FROZEN AND THIS FILE ENFORCES THAT MECHANICALLY ===

The six verdicts were committed in run_paired_phrasing_live.py at 4d81eab, BEFORE the capture
existed. This script parses VERDICT_SCHEME out of that module and REJECTS any verdict not in
it. That is deliberate: the honest failure mode of an adjudication pass is inventing a seventh
bucket once the replies make the first six uncomfortable, and prose promising not to do that is
not a control (R26). Here it is unrepresentable -- a new verdict fails the run.

=== THE BUCKET THE SCHEME DOES NOT HAVE ===

Four pairs are NOT contradictions and are NOT consistency either: one member commits to a
figure or an authority, the other hedges or answers a different question. Nothing is denied, so
the strict test places them in DIVERGENT_COMPATIBLE -- a bucket whose name says benign
completeness variance. For cp_17 that placement is plainly wrong about the user's experience:
one member produces a tax bill and the other produces the impression of none.

THE RESOLUTION IS A SEPARATE AXIS, NOT A SEVENTH VERDICT. Each pair carries an optional
`asymmetry` annotation. The frozen verdict is still assigned and still drives the headline; the
annotation is reported alongside and never summed in silently -- the same treatment
SCOPE_INCONSISTENT already gets. Adding a verdict after reading the replies would have made the
scheme a function of its own data, which is the single property this corpus was frozen to
protect.

RECOMMENDATION FOR THE NEXT PAIRED CORPUS: freeze a seventh verdict BEFORE measuring, for the
asymmetric-actionability shape. It is now an observed category with 4 instances, so the next
corpus has no excuse for discovering it again.

=== THREE ADJUDICATION CONVENTIONS, AND WHERE THEY CAME FROM ===

RULE 1 (pre-existing, follows the 78-row pass): the verdict is assigned on the TOPIC AXIS --
    the quantity or claim the pair is about. Compatible extra material off that axis is noted,
    not verdict-changing. Without it nearly every pair becomes DIVERGENT on trivia.

RULE 2 (FORMULATED DURING THIS PASS, at cp_08 -- stated plainly rather than presented as
    pre-registered): the trailing "Thibitisha na X" line is a REFERRAL, not an assertion of
    regulatory fact. Body assertions decide the verdict. Applied uniformly to all 24.
    SENSITIVITY, REPORTED BECAUSE IT IS REAL: cp_08 is the only pair whose verdict turns on it.
    Counting referral lines as assertions moves the headline from 4/24 to 5/24.

RULE 3 (pre-existing, follows the 78-row pass): correctness is asserted only where this
    project's own primary-source record supports it. Where no locked fact exists the pair is
    marked UNVERIFIED_HERE rather than scored against the adjudicator's own knowledge. This
    affects the correctness axis ONLY -- the consistency verdict is independent of it, which is
    the whole point of separating them.

Usage:  python eval/consistency/adjudicate_paired_phrasing.py
        python eval/consistency/adjudicate_paired_phrasing.py --self-test
Artifact: eval/results/paired_phrasing_adjudication_2026_09_24.json
"""
import argparse
import ast
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RUNNER = os.path.join(HERE, 'run_paired_phrasing_live.py')
PAIRS = os.path.join(HERE, 'paired_phrasing_024.jsonl')
VERDICTS = os.path.join(HERE, 'paired_phrasing_verdicts_024.jsonl')
CAPTURE = os.path.join(REPO, 'eval', 'results', 'paired_phrasing_live_2026_09_24.json')
OUT = os.path.join(REPO, 'eval', 'results', 'paired_phrasing_adjudication_2026_09_24.json')

# Verdicts that mean "the two members did not agree on the topic axis". CONSISTENT_WRONG is
# deliberately NOT here: two wrong answers that agree are a correctness failure, and folding
# them in would inflate this headline with the defect every other corpus already measures.
NOT_A_CONTRADICTION = {'CONSISTENT_CORRECT', 'CONSISTENT_WRONG', 'DIVERGENT_COMPATIBLE'}

POPULATION_CAVEAT = (
    'MEASURED ON 24 AUTHORED PAIRS, not a corpus-wide estimate and never to be cited as one. '
    'The pairs were written to probe phrasing-dependence, 6 each across covered_fact / gap / '
    'compute / boundary, and two of them (cp_09, cp_12) deliberately repeat shapes whose '
    '2026-09-05 outcome was already known -- one inconsistent, one consistent -- so the corpus '
    'is not composed only of rows selected for having failed. WHY THIS POPULATION: no other '
    'corpus in this repo can answer the question at all, because every one of them is '
    'one-phrasing-per-question by construction and therefore cannot detect phrasing-dependence '
    'however large it grows (R22: name the population, and say why it is where the decision '
    'applies).')


def frozen_scheme():
    """Parse VERDICT_SCHEME out of the committed runner. Never hardcode it here -- a copy could
    drift from the thing it claims to mirror, which is how a control goes quietly inert."""
    tree = ast.parse(open(RUNNER, encoding='utf-8').read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'VERDICT_SCHEME':
            return ast.literal_eval(node.value)
    raise AssertionError('VERDICT_SCHEME not found in the runner -- cannot verify the scheme')


def load_verdicts(path, scheme, expected_ids):
    with open(path, encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    assert rows, f'no verdicts loaded from {path} -- a tally over zero rows would report a ' \
                 f'clean summary over nothing'
    seen = collections.Counter(r['pair_id'] for r in rows)
    dupes = [k for k, v in seen.items() if v > 1]
    assert not dupes, f'pair adjudicated more than once: {dupes}'
    bad = sorted({r['verdict'] for r in rows} - set(scheme))
    assert not bad, (f'verdict(s) not in the FROZEN scheme: {bad}. The scheme was committed '
                     f'before the capture existed and may not be extended after reading the '
                     f'replies -- use the `asymmetry` annotation axis instead.')
    missing = sorted(expected_ids - set(seen))
    extra = sorted(set(seen) - expected_ids)
    assert not missing, f'pairs captured but never adjudicated: {missing}'
    assert not extra, f'verdicts for pairs not in the frozen corpus: {extra}'
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true',
                    help='plant a bad verdict and a duplicate; both MUST be rejected (R26)')
    args = ap.parse_args()

    scheme = frozen_scheme()

    capture = json.load(open(CAPTURE, encoding='utf-8'))
    assert capture['verdict_scheme'] == scheme, \
        'the capture was written under a DIFFERENT scheme than the runner now holds'
    assert capture['status'].startswith('COMPLETE'), f"capture not complete: {capture['status']}"
    bad_rows = [r for r in capture['rows'] if r['outcome'] != 'HTTP_200']
    assert not bad_rows, f'capture contains non-200 rows: {[r["pair_id"] for r in bad_rows]}'

    pairs = {json.loads(line)['pair_id']: json.loads(line)
             for line in open(PAIRS, encoding='utf-8') if line.strip()}

    if args.self_test:
        return self_test(scheme, set(pairs))

    verdicts = load_verdicts(VERDICTS, scheme, set(pairs))
    for v in verdicts:
        v['category'] = pairs[v['pair_id']]['category']
        v['topic'] = pairs[v['pair_id']]['topic']

    adjudicable = [v for v in verdicts if v['verdict'] != 'UNADJUDICABLE']
    contra = [v for v in adjudicable if v['verdict'] == 'CONTRADICTORY']
    scope = [v for v in adjudicable if v['verdict'] == 'SCOPE_INCONSISTENT']
    asym = [v for v in adjudicable if v.get('asymmetry')]

    by_cat = collections.defaultdict(lambda: collections.Counter())
    for v in verdicts:
        by_cat[v['category']][v['verdict']] += 1
        if v.get('asymmetry'):
            by_cat[v['category']]['_asymmetry'] += 1

    def pct(n, d):
        return round(100.0 * n / d, 1) if d else None

    cats = {}
    for cat, c in by_cat.items():
        adj = sum(v for k, v in c.items() if not k.startswith('_')
                  and k != 'UNADJUDICABLE')
        cats[cat] = {'verdicts': {k: v for k, v in sorted(c.items()) if not k.startswith('_')},
                     'adjudicable': adj,
                     'contradictory': c['CONTRADICTORY'],
                     'contradiction_rate_pct': pct(c['CONTRADICTORY'], adj),
                     'asymmetry_flagged': c['_asymmetry']}

    blob = {
        'measured': '2026-09-24',
        'adjudicated': '2026-09-24',
        'source_capture': 'eval/results/paired_phrasing_live_2026_09_24.json',
        'source_verdicts': 'eval/consistency/paired_phrasing_verdicts_024.jsonl',
        'harness': 'eval/consistency/adjudicate_paired_phrasing.py',
        'scheme_frozen_at': '4d81eab (runner + corpus, committed BEFORE the capture)',
        'verdict_scheme': scheme,
        'population_caveat': POPULATION_CAVEAT,
        'axis_separation': (
            'CONSISTENT_WRONG is NOT counted as a contradiction: two answers that agree and are '
            'both wrong are a CORRECTNESS failure, which every other corpus here already '
            'measures, and folding it in would inflate this headline with the wrong defect. '
            'SCOPE_INCONSISTENT is reported alongside and never summed in silently. The '
            'asymmetry annotation is a THIRD thing and is likewise never summed in silently.'),
        'headline': {
            'contradictory': len(contra),
            'adjudicable_pairs': len(adjudicable),
            'contradiction_rate_pct': pct(len(contra), len(adjudicable)),
            'contradictory_pairs': [v['pair_id'] for v in contra],
        },
        'reported_alongside_never_summed_in': {
            'scope_inconsistent': len(scope),
            'scope_inconsistent_pairs': [v['pair_id'] for v in scope],
            'asymmetry_flagged': len(asym),
            'asymmetry_flagged_pairs': [v['pair_id'] for v in asym],
            'if_asymmetry_counted_as_instability': {
                'n': len(contra) + len(asym),
                'of': len(adjudicable),
                'pct': pct(len(contra) + len(asym), len(adjudicable)),
                'note': 'Offered so the reader can take either view explicitly. It is NOT the '
                        'headline, because these pairs are not contradictions under the frozen '
                        'scheme.'},
        },
        'scheme_hole': {
            'found': True,
            'shape': 'ASYMMETRIC ACTIONABILITY -- one member commits to a figure or an '
                     'authority, the other hedges or answers a different question. Nothing is '
                     'denied, so the strict test files it under DIVERGENT_COMPATIBLE, a bucket '
                     'whose name claims benign completeness variance.',
            'why_not_fixed_here': 'Adding a seventh verdict after reading the replies would '
                                  'make the scheme a function of its own data -- the one '
                                  'property freezing it before the run exists to protect.',
            'clearest_instance': 'cp_17 -- A computes a presumptive tax bill of TZS 106,000 '
                                 '(itself wrong; the band gives 250,000), B never mentions '
                                 'presumptive tax at all and leaves the impression nothing is '
                                 'owed. Not a formal contradiction. A user cannot act on both.',
            'recommendation': 'Freeze a seventh verdict for this shape BEFORE the next paired '
                              'corpus is measured. It now has 4 observed instances.',
        },
        'rule_2_sensitivity': {
            'rule': 'The "Thibitisha na X" line is a referral, not an assertion. Body '
                    'assertions decide the verdict.',
            'formulated': 'DURING this pass, at cp_08 -- not pre-registered. Stated rather '
                          'than presented as if it had been.',
            'pairs_whose_verdict_turns_on_it': ['cp_08'],
            'headline_if_referrals_counted_as_assertions': '5/24 (20.8%) instead of 4/24 (16.7%)',
        },
        'by_category': cats,
        'verdicts': sorted(verdicts, key=lambda v: v['pair_id']),
    }

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    h = blob['headline']
    print(f"HEADLINE  CONTRADICTORY {h['contradictory']}/{h['adjudicable_pairs']} "
          f"= {h['contradiction_rate_pct']}%   {h['contradictory_pairs']}")
    print(f"ALONGSIDE scope_inconsistent={len(scope)}  asymmetry_flagged={len(asym)} "
          f"{[v['pair_id'] for v in asym]}")
    print()
    for cat in ('covered_fact', 'gap', 'compute', 'boundary'):
        c = cats[cat]
        print(f"  {cat:<13} contradictory {c['contradictory']}/{c['adjudicable']} "
              f"= {str(c['contradiction_rate_pct']):>5}%   asymmetry {c['asymmetry_flagged']}"
              f"   {dict(c['verdicts'])}")
    print()
    print(f'[saved] {os.path.relpath(OUT, REPO)}')


def self_test(scheme, ids):
    """R26: plant the exact thing the control exists to catch, AND give it a clean case.

    Positive-only would certify a loader that rejects everything. The clean limb is the half
    that was missing from the secret scan."""
    import tempfile
    results = []

    def run(label, rows, must_fail):
        fd, p = tempfile.mkstemp(suffix='.jsonl', text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        try:
            load_verdicts(p, scheme, ids)
            blocked, why = False, ''
        except AssertionError as exc:
            blocked, why = True, str(exc)[:110]
        finally:
            os.unlink(p)
        ok = blocked == must_fail
        results.append(ok)
        print(f"  [{'PASS' if ok else 'FAIL'}] {label:<46} "
              f"{'BLOCKED' if blocked else 'accepted':<9} {why}")

    clean = [{'pair_id': i, 'verdict': 'CONSISTENT_CORRECT', 'asymmetry': None} for i in sorted(ids)]
    print('R26 both-limb demonstration of the frozen-scheme control:')
    run('clean 24-row set MUST be accepted', clean, must_fail=False)

    seventh = [dict(r) for r in clean]
    seventh[0]['verdict'] = 'ASYMMETRIC_ACTIONABILITY'
    run('a SEVENTH verdict MUST be rejected', seventh, must_fail=True)

    dupe = [dict(r) for r in clean] + [dict(clean[0])]
    run('a duplicated pair MUST be rejected', dupe, must_fail=True)

    run('a missing pair MUST be rejected', clean[:-1], must_fail=True)
    run('an empty file MUST be rejected', [], must_fail=True)

    print(f"\n{'ALL LIMBS PASS' if all(results) else 'SELF-TEST FAILED'}")
    return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main() or 0)

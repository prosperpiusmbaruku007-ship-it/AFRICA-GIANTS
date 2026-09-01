# -*- coding: utf-8 -*-
"""Reachability sweep for the corporate/partnership tax router path (path 1b, routing.py),
added 2026-09-01 as part of the corporate/partnership tax engine build.

WHAT THIS MEASURES. Path 1b is inserted BEFORE path 2 (PAYE's natural `kodi ya mapato` claim)
specifically so an entity-named question wins over it. That placement is a real routing-order
change and the standing instruction (R17) is that a clean sweep over the corpus we already have
is a LOWER BOUND on safety, not proof of it -- so this script records what it actually found,
not what it hoped to find, and both directions: which questions gained a NEW route (path 1b
firing where nothing did before) and whether any question LOST its previous route (path 1b
stealing a question path 2 used to own).

Compares chike.routing.detect_intent() BEFORE this change against AFTER over the 400-row gate
corpus + the plain-Swahili probe set -- the same corpus test_pipeline_v15.py calls "the 400
gate questions plus the 20 plain-Swahili probe questions".

METHOD: run twice in two separate subprocesses, once with the working tree's uncommitted
routing/orchestrator/corporate_tax changes stashed away (BEFORE), once restored (AFTER).
`git stash` rather than loading routing.py as a standalone file, because routing.py uses
package-relative imports (`from . import swahili_numbers`) that only resolve when `chike` is
imported as a real package -- an earlier version of this script tried the standalone-file
approach and failed on exactly that import.

R18: committed before its result is cited.
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, 'eval', 'results', 'corporate_tax_routing_reachability_2026_09_01.json')

_GATE_FILES = [
    "eval/accuracy_gate/eval_questions_001.jsonl",
    "eval/accuracy_gate/eval_questions_002_additions.jsonl",
    "eval/accuracy_gate/eval_questions_003.jsonl",
]
_PROBE_FILES = [
    "eval/accuracy_gate/edge_probe_plain_sw_015.jsonl",
    "eval/accuracy_gate/edge_probe_plain_sw_005b.jsonl",
]

_RUNNER = (
    "import sys, json\n"
    "sys.path.insert(0, r'{repo}')\n"
    "from chike import routing\n"
    "questions = json.loads(sys.stdin.read())\n"
    "print(json.dumps([routing.detect_intent(q) for q in questions]))\n"
).format(repo=REPO)


def _jsonl(rel):
    with open(os.path.join(REPO, rel), encoding='utf-8') as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _all_questions():
    rows = []
    for f in _GATE_FILES:
        for r in _jsonl(f):
            rows.append((f, r.get('id', '?'), r['question_sw']))
    for f in _PROBE_FILES:
        for r in _jsonl(f):
            rows.append((f, r.get('id', '?'), r['question']))
    return rows


def _route_all(questions):
    proc = subprocess.run(
        [sys.executable, '-c', _RUNNER], input=json.dumps(questions),
        capture_output=True, text=True, cwd=REPO, encoding='utf-8')
    if proc.returncode != 0:
        raise RuntimeError(f'routing subprocess failed: {proc.stderr}')
    return json.loads(proc.stdout)


def main():
    rows = _all_questions()
    questions = [q for _, _, q in rows]

    status = subprocess.run(['git', 'status', '--porcelain'], cwd=REPO, capture_output=True,
                            text=True, encoding='utf-8', check=True).stdout
    if not status.strip():
        raise RuntimeError('working tree is clean -- nothing to compare against HEAD; '
                            'this script must be run with the routing changes UNCOMMITTED')

    subprocess.run(['git', 'stash', '--quiet'], cwd=REPO, check=True)
    try:
        before = _route_all(questions)
    finally:
        subprocess.run(['git', 'stash', 'pop', '--quiet'], cwd=REPO, check=True)
    after = _route_all(questions)

    gained_corporate, gained_partnership, changed_other = [], [], []
    for (f, qid, q), b, a in zip(rows, before, after):
        if b == a:
            continue
        entry = {'file': f, 'id': qid, 'question': q, 'before': b, 'after': a}
        if a == 'corporate_tax':
            gained_corporate.append(entry)
        elif a == 'partnership_tax':
            gained_partnership.append(entry)
        else:
            changed_other.append(entry)

    report = {
        'measured': '2026-09-01',
        'harness': 'eval/routing/sweep_corporate_tax_routing.py',
        'corpus': {'gate_files': _GATE_FILES, 'probe_files': _PROBE_FILES,
                   'total_questions': len(rows)},
        'what_changed': {
            'gained_corporate_tax': len(gained_corporate),
            'gained_partnership_tax': len(gained_partnership),
            'changed_to_something_else': len(changed_other),
        },
        'gained_corporate_tax_rows': gained_corporate,
        'gained_partnership_tax_rows': gained_partnership,
        # THIS IS THE ONE THAT MATTERS: any row whose route changed to something OTHER than
        # corporate_tax/partnership_tax means path 1b (or its placement before path 2) stole a
        # question from a route it did not exist to change -- e.g. a PAYE row diverted.
        'unexpected_changes_rows': changed_other,
        'clean': len(changed_other) == 0,
    }
    print(json.dumps(report, ensure_ascii=False, indent=1)[:6000])
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(f'[saved] {OUT}')
    if not report['clean']:
        print('\n*** UNEXPECTED ROUTE CHANGES FOUND -- see unexpected_changes_rows ***')
        sys.exit(1)


if __name__ == '__main__':
    main()

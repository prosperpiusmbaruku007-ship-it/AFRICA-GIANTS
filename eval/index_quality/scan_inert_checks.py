# -*- coding: utf-8 -*-
"""Census of checks that can pass WITHOUT TESTING ANYTHING.

Prompted by the dead-anchor finding: three regen guards matched zero facts and could never
fire, each concealed by a sibling anchor that always passed. So a green gate can carry inert
checks indefinitely with no signal. The census test's blind spot was the same idea from the
other direction — a generative test that derives cases from existing members is silent when
the class has zero members.

Three mechanically-detectable shapes, all AST-based (no import, no execution):

  A. VACUOUS_LOOP    — `for x in COLL: ... assert ...` where nothing establishes COLL is
                       non-empty. If COLL empties, the test passes having asserted nothing.
  B. ANY_OVER_ALTS   — `assert any(... for kw in [a, b, c])`. Passes if ONE alternative
                       matches; the others can be dead forever with no signal. This is
                       exactly the regen dead-anchor shape.
  C. EMPTY_PARAMS    — `@pytest.mark.parametrize` over a name built at runtime, so an empty
                       list silently yields zero test cases.

Every hit is a SHAPE, not a defect. Many are fine. The output is a worklist for reading, and
the counts say how much of the suite rests on structures that can go quiet.

R18: committed before its result is written up.
Artifact: eval/results/inert_check_census.json
"""
import ast
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'eval', 'results', 'inert_check_census.json')
ROOTS = ['tests', 'scripts', 'chike']


def has_assert(node):
    return any(isinstance(n, ast.Assert) for n in ast.walk(node))


def guards_nonempty(func, target_src):
    """Does anything in the function establish that the iterable is non-empty?

    Accepts `assert COLL`, `assert len(COLL)`, `assert len(COLL) > 0`, `assert COLL, msg`,
    or a comparison mentioning both len( and the collection name.
    """
    for n in ast.walk(func):
        if isinstance(n, ast.Assert):
            src = ast.dump(n.test)
            if target_src and target_src in src:
                # `assert COLL` / `assert len(COLL) ...` / `assert COLL != []`
                if isinstance(n.test, (ast.Name, ast.Attribute, ast.Compare, ast.Call)):
                    return True
    return False


def module_literals(tree):
    """Module-level names bound to a literal collection, with their sizes.

    Lets the scan distinguish a shape that COULD go inert from one that IS inert right now:
    a loop over a module constant that is currently an empty list asserts nothing today.
    """
    sizes = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, SyntaxError, TypeError):
                continue
            if isinstance(value, (list, tuple, set, dict, str)):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        sizes[t.id] = len(value)
    return sizes


def iterable_name(node):
    it = node.iter
    if isinstance(it, ast.Name):
        return it.id
    if isinstance(it, ast.Attribute):
        return it.attr
    if isinstance(it, ast.Call):
        f = it.func
        if isinstance(f, ast.Name):
            return f.id
        if isinstance(f, ast.Attribute):
            return f.attr
    return None


def main():
    findings = {'VACUOUS_LOOP': [], 'ANY_OVER_ALTS': [], 'EMPTY_PARAMS': []}
    files_scanned = 0

    for root in ROOTS:
        base = os.path.join(REPO, root)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            for fn in filenames:
                if not fn.endswith('.py'):
                    continue
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, REPO).replace('\\', '/')
                try:
                    with open(path, encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                except (OSError, SyntaxError):
                    continue
                files_scanned += 1
                lits = module_literals(tree)

                for func in ast.walk(tree):
                    if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    is_test = func.name.startswith('test_')

                    for node in ast.walk(func):
                        # --- A. vacuous loop ---
                        if isinstance(node, ast.For) and has_assert(node):
                            name = iterable_name(node)
                            if name and not guards_nonempty(func, f"id='{name}'"):
                                size = lits.get(name)
                                findings['VACUOUS_LOOP'].append({
                                    'file': rel, 'func': func.name, 'line': node.lineno,
                                    'iterable': name, 'is_test': is_test,
                                    'literal_size': size,
                                    'state': ('INERT_NOW' if size == 0 else
                                              'ACTIVE' if size else 'UNRESOLVED'),
                                })
                        # --- B. any() over a literal list of alternatives ---
                        if isinstance(node, ast.Assert):
                            for c in ast.walk(node.test):
                                if (isinstance(c, ast.Call)
                                        and isinstance(c.func, ast.Name)
                                        and c.func.id == 'any' and c.args):
                                    gen = c.args[0]
                                    if isinstance(gen, (ast.GeneratorExp, ast.ListComp)):
                                        for comp in gen.generators:
                                            if (isinstance(comp.iter, (ast.List, ast.Tuple))
                                                    and len(comp.iter.elts) > 1):
                                                findings['ANY_OVER_ALTS'].append({
                                                    'file': rel, 'func': func.name,
                                                    'line': node.lineno,
                                                    'n_alternatives': len(comp.iter.elts),
                                                    'is_test': is_test,
                                                })
                    # --- C. parametrize over a runtime name ---
                    for dec in func.decorator_list:
                        if not isinstance(dec, ast.Call):
                            continue
                        fname = ast.dump(dec.func)
                        if 'parametrize' not in fname:
                            continue
                        if len(dec.args) >= 2 and isinstance(dec.args[1], (ast.Name,
                                                                          ast.Attribute,
                                                                          ast.Call)):
                            findings['EMPTY_PARAMS'].append({
                                'file': rel, 'func': func.name, 'line': func.lineno,
                                'is_test': is_test,
                            })

    counts = {k: len(v) for k, v in findings.items()}
    test_only = {k: sum(1 for r in v if r['is_test']) for k, v in findings.items()}
    by_file = {}
    for k, v in findings.items():
        for r in v:
            by_file.setdefault(r['file'], {}).setdefault(k, 0)
            by_file[r['file']][k] += 1

    out = {
        'measured': '2026-08-22',
        'harness': 'eval/index_quality/scan_inert_checks.py',
        'method': 'AST shape detection — every hit is a SHAPE that CAN go inert, not a proven '
                  'defect. A worklist for reading, not a defect list.',
        'roots': ROOTS,
        'files_scanned': files_scanned,
        'counts': counts,
        'counts_in_test_functions': test_only,
        'by_file': dict(sorted(by_file.items(),
                               key=lambda kv: -sum(kv[1].values()))),
        'findings': findings,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    states = {}
    for r in findings['VACUOUS_LOOP']:
        states[r['state']] = states.get(r['state'], 0) + 1
    out['vacuous_loop_states'] = states
    out['inert_now'] = [r for r in findings['VACUOUS_LOOP'] if r['state'] == 'INERT_NOW']
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'files scanned: {files_scanned}')
    print(json.dumps(counts, indent=2))
    print('in test_ functions:', json.dumps(test_only))
    print('vacuous-loop states:', json.dumps(states))
    print('INERT RIGHT NOW:', out['inert_now'] or 'none')
    print('\n--- top files by hit count ---')
    for fp, kinds in list(out['by_file'].items())[:12]:
        print(f"  {sum(kinds.values()):>3}  {fp:<52} {kinds}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""EQUIVALENCE TEST for the number-before-scale parser change (2026-11-12). R33's cure for a probe set
that shares its author's notation: take every committed question written SCALE-FIRST ("milioni 6"),
rewrite ONLY the amount into NUMBER-FIRST ("6 milioni"), and require the orchestrator's answer to be
IDENTICAL. Same question, same meaning, two spellings -- any difference is a parser defect, by
construction, with no gold answer needed.

Both trees are run: OLD (git worktree of HEAD) to measure the size of the defect that existed, NEW to
prove it is closed. Separate processes, silent model backend, no retriever (R24).

usage: python sweep_parser_equivalence_2026_11_12.py <old_tree_path>
"""
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import sweep_parser_scale_order_2026_11_12 as sw                     # noqa: E402

OUT = os.path.join(REPO, "eval", "results", "sweep_parser_equivalence_2026_11_12.json")
SCALE_FIRST = re.compile(r"\b(elfu|laki|milioni|bilioni)\s+(\d{1,3}(?:[.,]\d{1,2})?)(?![\d.,]*\d)", re.IGNORECASE)


def rewrite(q):
    return SCALE_FIRST.sub(lambda m: f"{m.group(2)} {m.group(1)}", q)


def main():
    old_tree = sys.argv[1]
    qs, _ = sw.corpus()
    pairs = []
    for q in qs:
        if len(q) > 500 or "\n\n" in q:                              # prose/docstrings, not questions
            continue
        r = rewrite(q)
        if r != q:
            pairs.append((q, r))
    scratch = os.path.dirname(old_tree)
    runner = os.path.join(scratch, "_runner.py")                     # written by the answers script
    assert os.path.exists(runner), "run sweep_parser_scale_order_answers first"
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    res = {}
    for tree_name, tree in (("old", old_tree), ("new", REPO)):
        for side, idx in (("orig", 0), ("rewr", 1)):
            inp = os.path.join(scratch, f"_eq_{tree_name}_{side}.json")
            out = os.path.join(scratch, f"_eqo_{tree_name}_{side}.json")
            json.dump([p[idx] for p in pairs], open(inp, "w", encoding="utf-8"), ensure_ascii=False)
            p = subprocess.run([sys.executable, runner, tree, inp, out], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", env=env, timeout=1500)
            assert p.returncode == 0, p.stderr[-600:]
            res[(tree_name, side)] = json.load(open(out, encoding="utf-8"))
    rows = []
    for i, (q, r) in enumerate(pairs):
        def same(tree):
            a, b = res[(tree, "orig")][i], res[(tree, "rewr")][i]
            return (a.get("text"), a.get("intent")) == (b.get("text"), b.get("intent"))
        rows.append({"orig": q, "rewritten": r, "old_equivalent": same("old"), "new_equivalent": same("new"),
                     "old_orig": res[("old", "orig")][i], "old_rewr": res[("old", "rewr")][i],
                     "new_orig": res[("new", "orig")][i], "new_rewr": res[("new", "rewr")][i]})
    json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"scale-first questions rewritten: {len(rows)} | "
          f"OLD tree diverges on {sum(1 for r in rows if not r['old_equivalent'])} | "
          f"NEW tree diverges on {sum(1 for r in rows if not r['new_equivalent'])}")


if __name__ == "__main__":
    main()

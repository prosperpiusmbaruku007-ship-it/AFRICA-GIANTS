# -*- coding: utf-8 -*-
"""BLAST RADIUS (R12c step 1, R17/R21) of the dependent-fragment merge in chike/decomposition.py. Baseline = the module AS COMMITTED at HEAD, loaded from `git show` (code against code). Population = every question we hold.
Every question whose decomposition CHANGED is printed with its source and READ BY A PERSON.
    python eval/controls/sweep_fragment_merge_2026_11_24.py   ->  eval/results/sweep_fragment_merge_2026_11_24.json"""
import io, json, os, subprocess, sys, tempfile, types
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, HERE)
from chike import decomposition as new  # noqa: E402
from sweep_d18_routes_2026_11_17 import questions  # noqa: E402


def baseline():
    src = subprocess.run(["git", "show", "HEAD:chike/decomposition.py"], cwd=REPO, capture_output=True, check=True).stdout.decode("utf-8")
    assert "_merge_dependent_fragments" not in src, "the baseline must predate the merge"
    mod = types.ModuleType("chike._decomposition_baseline")
    mod.__package__ = "chike"
    mod.__file__ = os.path.join(tempfile.gettempdir(), "_decomposition_baseline.py")
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


def main():
    old = baseline()
    qs = questions()
    assert len(qs) > 8000, len(qs)
    multi = changed = 0
    rows = []
    for q, src in qs.items():
        o, n = old.decompose_query(q), new.decompose_query(q)
        multi += len(o) > 1
        if o != n:
            rows.append({"q": q, "src": src, "before": o, "after": n})
    print(f"{len(qs)} questions; {multi} decomposed into 2+ parts at baseline; {len(rows)} CHANGED by the merge")
    for r in rows:
        print(f"  [{r['src'].split('/')[-1][:34]}] {len(r['before'])} -> {len(r['after'])} | {r['q'][:200]}")
        print(f"      before: {r['before']}")
    io.open(os.path.join(REPO, "eval", "results", "sweep_fragment_merge_2026_11_24.json"), "w", encoding="utf-8").write(json.dumps({"swept": len(qs), "decomposed_at_baseline": multi, "changed": rows}, ensure_ascii=False, indent=1))


main()

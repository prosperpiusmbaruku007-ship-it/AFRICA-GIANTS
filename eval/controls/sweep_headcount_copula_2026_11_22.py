# -*- coding: utf-8 -*-
"""BLAST RADIUS (R12c step 1) of the noun-first copula headcount ("Wafanyakazi wangu ni 12") added to chike/swahili_numbers.py on 2026-11-22: `sole_headcount` over every question we hold, NOW versus the version committed at HEAD
(read with `git show HEAD:...` into a throwaway module, never by reloading the live one: half-swapped imports are how a comparison agrees with the wrong thing). Lists every question whose headcount CHANGED, to be READ.
    python eval/controls/sweep_headcount_copula_2026_11_22.py   ->  eval/results/sweep_headcount_copula_2026_11_22.json
Run BEFORE committing the change (HEAD must be the pre-change version)."""
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
from chike import swahili_numbers as new  # noqa: E402
from sweep_d18_routes_2026_11_17 import questions  # noqa: E402


def load_head():
    src = subprocess.run(["git", "show", "HEAD:chike/swahili_numbers.py"], cwd=REPO, capture_output=True, check=True).stdout
    path = os.path.join(tempfile.mkdtemp(), "swahili_numbers_head.py")
    io.open(path, "wb").write(src)
    spec = importlib.util.spec_from_file_location("swn_head", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    old = load_head()
    qs = questions()
    changed = []
    for q, src in qs.items():
        a, b = old.sole_headcount(q), new.sole_headcount(q)
        if a != b:
            changed.append({"q": q, "src": src, "before": a, "after": b})
    print(f"{len(qs)} questions swept; {len(changed)} changed headcount")
    for c in changed:
        print(f"  {c['before']} -> {c['after']} [{c['src']}] {c['q'][:150]}")
    json.dump({"swept": len(qs), "changed": changed}, io.open(os.path.join(REPO, "eval", "results", "sweep_headcount_copula_2026_11_22.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""REGRESSION SWEEP for the bound-premise fix (2026-11-12): every committed question routed to a
turnover-taking engine, orchestrator answer OLD tree vs NEW tree.

The fix may change an answer only where a sole amount is the object of an upper-bound cue. Every other
row must be BYTE-IDENTICAL; any other difference is a regression the cue rules let through. Separate
processes (a `git worktree` of HEAD vs the working tree), silent backend, no retriever (R24).

usage: python sweep_bound_premise_regression_2026_11_12.py <old_tree_path>   (needs <scratch>/_runner.py,
       written by sweep_parser_scale_order_answers_2026_11_12.py)
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
import sweep_parser_scale_order_2026_11_12 as sw                     # noqa: E402
from chike import routing                                            # noqa: E402

OUT = os.path.join(REPO, "eval", "results", "sweep_bound_premise_regression_2026_11_12.json")


def main():
    old_tree = sys.argv[1]
    scratch = os.path.dirname(old_tree)
    runner = os.path.join(scratch, "_runner.py")
    assert os.path.exists(runner), "run sweep_parser_scale_order_answers first (it writes _runner.py)"
    qs, _ = sw.corpus()
    rows = []
    for q in qs:
        if len(q) > 400 or "\n\n" in q:
            continue
        try:
            if routing.detect_intent(q) in ("vat_registration", "presumptive"):
                rows.append(q)
        except Exception:                                            # noqa: BLE001
            pass
    # R26: the founding specimen must be in the population or the sweep is inert
    live = "Mauzo yangu bado hayajafika TZS 200 milioni kwa mwaka. Ninaweza kusajili VAT kwa hiari (voluntary VAT registration)?"
    assert live in rows, "the founding specimen is not in the swept population -- the sweep is inert"
    inp = os.path.join(scratch, "_bp_rows.json")
    json.dump(rows, open(inp, "w", encoding="utf-8"), ensure_ascii=False)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    outs = {}
    for name, tree in (("old", old_tree), ("new", REPO)):
        o = os.path.join(scratch, f"_bp_out_{name}.json")
        p = subprocess.run([sys.executable, runner, tree, inp, o], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env, timeout=1500)
        assert p.returncode == 0, p.stderr[-600:]
        outs[name] = {r["q"]: r for r in json.load(open(o, encoding="utf-8"))}
    res = [{"q": q, "old": outs["old"][q].get("text"), "new": outs["new"][q].get("text"),
            "changed": outs["old"][q].get("text") != outs["new"][q].get("text")} for q in rows]
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ch = [r for r in res if r["changed"]]
    print(f"engine-routed strings {len(res)} | CHANGED {len(ch)}")
    for r in ch:
        print("-", r["q"][:100])


if __name__ == "__main__":
    main()

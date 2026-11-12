# -*- coding: utf-8 -*-
"""SWEEP for the VAT-registration cue widening (2026-11-12): every committed question string, ROUTING INTENT and
orchestrator ANSWER, OLD tree (git worktree of HEAD) vs NEW tree (working tree), separate processes (R24).

The change adds first-person subjunctive / object-concord forms to the VAT cue list. It may change a row only
if that row contains one of those forms next to 'VAT'; any other change is a regression the new pattern let
through. The population is the whole corpus (every *.json* under eval/, datasets/, tests/, kaggle/ plus test
string literals), not a sample, so a row that does not appear as CHANGED provably did not change.

usage: python sweep_vat_cues_2026_11_12.py <old_tree_path>   (needs <scratch>/_runner.py, written by
       sweep_parser_scale_order_answers_2026_11_12.py)
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

OUT = os.path.join(REPO, "eval", "results", "sweep_vat_cues_2026_11_12.json")


def main():
    old_tree = sys.argv[1]
    scratch = os.path.dirname(old_tree)
    runner = os.path.join(scratch, "_runner.py")
    assert os.path.exists(runner), "run sweep_parser_scale_order_answers first (it writes _runner.py)"
    qs, _ = sw.corpus()
    qs = [q for q in qs if len(q) <= 500 and "\n\n" not in q]
    # R26: the founding specimen must be in the population or the sweep is inert
    spec = "Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT"
    qs.append(spec)
    inp = os.path.join(scratch, "_vc_rows.json")
    json.dump(sorted(set(qs)), open(inp, "w", encoding="utf-8"), ensure_ascii=False)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    outs = {}
    for name, tree in (("old", old_tree), ("new", REPO)):
        o = os.path.join(scratch, f"_vc_out_{name}.json")
        p = subprocess.run([sys.executable, runner, tree, inp, o], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env, timeout=3000)
        assert p.returncode == 0, p.stderr[-600:]
        outs[name] = {r["q"]: r for r in json.load(open(o, encoding="utf-8"))}
    rows = sorted(set(qs))
    res = []
    for q in rows:
        o, n = outs["old"][q], outs["new"][q]
        res.append({"q": q, "old_intent": o.get("intent"), "new_intent": n.get("intent"),
                    "old": o.get("text"), "new": n.get("text"),
                    "changed": (o.get("intent"), o.get("text")) != (n.get("intent"), n.get("text"))})
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ch = [r for r in res if r["changed"]]
    assert any(r["q"] == spec for r in ch), "the founding specimen did not register as changed -- the sweep is inert"
    print(f"strings {len(res)} | CHANGED {len(ch)}")


if __name__ == "__main__":
    main()

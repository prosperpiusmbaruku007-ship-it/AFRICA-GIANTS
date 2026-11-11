# -*- coding: utf-8 -*-
"""STEP 2 of the parser sweep: the ORCHESTRATOR'S ANSWER on every changed row, old tree vs new tree.

Parsed amounts are not the claim that matters; the answer a user reads is. So for each row the sweep
marked CHANGED, run the real Orchestrator (silent model backend, no retriever: any difference is the
parser's and nothing else's) in two SEPARATE PROCESSES -- a `git worktree` of HEAD (old parser) and the
working tree (new parser). Never a module reload: half-swapped imports are how an arm agrees with the
wrong thing (R24).

usage:  python sweep_parser_scale_order_answers_2026_11_12.py <old_tree_path>
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SWEEP = os.path.join(REPO, "eval", "results", "sweep_parser_scale_order_2026_11_12.json")
OUT = os.path.join(REPO, "eval", "results", "sweep_parser_scale_order_answers_2026_11_12.json")

RUNNER = r'''
import json, sys
tree, inp, out = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, tree)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike.orchestrator import Orchestrator, ModelBackend
from chike import routing
class Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""
rows = json.load(open(inp, encoding="utf-8"))
res = []
for q in rows:
    try:
        orch = Orchestrator(Silent(), retriever=lambda x: [], ooc_phrases=[], in_scope_phrases=[])
        a = orch.answer(q)
        res.append({"q": q, "intent": str(routing.detect_intent(q)), "text": a.text})
    except Exception as e:
        res.append({"q": q, "error": type(e).__name__ + ": " + str(e)[:160]})
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
'''


def main():
    old_tree = sys.argv[1]
    rows = [c["q"] for c in json.load(open(SWEEP, encoding="utf-8"))["changed"]]
    scratch = os.path.dirname(old_tree)
    runner = os.path.join(scratch, "_runner.py")
    open(runner, "w", encoding="utf-8").write(RUNNER)
    inp = os.path.join(scratch, "_rows.json")
    json.dump(rows, open(inp, "w", encoding="utf-8"), ensure_ascii=False)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    outs = {}
    for name, tree in (("old", old_tree), ("new", REPO)):
        o = os.path.join(scratch, f"_out_{name}.json")
        p = subprocess.run([sys.executable, runner, tree, inp, o], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env, timeout=900)
        assert p.returncode == 0, (name, p.stderr[-800:])
        outs[name] = {r["q"]: r for r in json.load(open(o, encoding="utf-8"))}
    res = []
    for q in rows:
        o, n = outs["old"][q], outs["new"][q]
        res.append({"q": q, "old": o, "new": n,
                    "answer_changed": (o.get("text"), o.get("intent")) != (n.get("text"), n.get("intent"))})
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"rows {len(res)} | answer changed {sum(1 for r in res if r['answer_changed'])} | "
          f"errors old {sum(1 for r in res if 'error' in r['old'])} new {sum(1 for r in res if 'error' in r['new'])}")


if __name__ == "__main__":
    main()

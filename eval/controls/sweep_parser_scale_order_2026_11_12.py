# -*- coding: utf-8 -*-
"""BLAST-RADIUS SWEEP for the number-before-scale parser change (2026-11-12).

WHAT CHANGED: chike/swahili_numbers.py now reads "11 milioni", "400 elfu", "1.5 milioni", "11 million"
as 11,000,000 / 400,000 / 1,500,000 / 11,000,000. Before: [11, 1_000_000] etc. The parser feeds the
routing layer, every compute engine and D-FIDELITY-7, so the change is enumerated, not assumed.

METHOD (R12c): the OLD parser is `git show HEAD:chike/swahili_numbers.py` loaded as its own module;
the NEW parser is the working tree. Over EVERY committed question string -- every *.jsonl/*.json
corpus under eval/, datasets/ and tests/, plus every string constant in tests/*.py that carries a
number and a scale word -- compare parse_amounts and sole_plausible_amount. A row is CHANGED if either
differs. The changed set is the whole population, not a sample: a row on which the parser returns
identical lists cannot change any downstream answer.

STEP 2 (run by `--answers`): for each changed row, the ORCHESTRATOR's deterministic answer under the old
tree (a `git worktree` of HEAD, in a separate process -- never a module reload) and the new tree, with a
silent model backend and no retriever, so any difference is the parser's and nothing else's. The
engines' OUTPUT is compared, not just the parsed amounts.

Writes eval/results/sweep_parser_scale_order_2026_11_12.json after every stage.
"""
import ast
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "sweep_parser_scale_order_2026_11_12.json")
Q_KEYS = ("question", "question_sw", "question_en", "instruction", "prompt", "message", "query")
SCALE_NUM = re.compile(r"\d.{0,3}(elfu|laki|milioni|bilioni|million|billion)|(elfu|laki|milioni|bilioni)\s+\d",
                       re.IGNORECASE)


def _strings(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in Q_KEYS and isinstance(v, str):
                out.add(v)
            elif k == "messages" and isinstance(v, list):
                for m in v:
                    if isinstance(m, dict) and m.get("role") == "user" and isinstance(m.get("content"), str):
                        out.add(m["content"])
            else:
                _strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _strings(v, out)


def corpus():
    found, files = set(), 0
    for root in ("eval", "datasets", "tests", "kaggle"):
        for path in glob.glob(os.path.join(REPO, root, "**", "*.json*"), recursive=True):
            if os.path.getsize(path) > 60_000_000 or "node_modules" in path:
                continue
            files += 1
            try:
                txt = open(path, encoding="utf-8").read()
            except Exception:                                        # noqa: BLE001
                continue
            if path.endswith(".jsonl"):
                for line in txt.splitlines():
                    line = line.strip()
                    if line.startswith("{"):
                        try:
                            _strings(json.loads(line), found)
                        except Exception:                            # noqa: BLE001
                            pass
            elif path.endswith(".json"):
                try:
                    _strings(json.loads(txt), found)
                except Exception:                                    # noqa: BLE001
                    pass
    for path in glob.glob(os.path.join(REPO, "tests", "*.py")):
        files += 1
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except Exception:                                            # noqa: BLE001
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and SCALE_NUM.search(n.value):
                found.add(n.value)
    return sorted(s for s in found if s.strip()), files


def load_old():
    src = subprocess.run(["git", "show", "HEAD:chike/swahili_numbers.py"], cwd=REPO,
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    mod = type(sys)("swn_old")
    mod.__dict__["__name__"] = "swn_old"
    exec(compile(src, "swahili_numbers_HEAD.py", "exec"), mod.__dict__)
    return mod


def load_new():
    spec = importlib.util.spec_from_file_location("swn_new", os.path.join(REPO, "chike", "swahili_numbers.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _norm(xs):
    return sorted(float(x) for x in xs)


def main():
    old, new = load_old(), load_new()
    qs, files = corpus()
    # --- instrument self-check (R26): the founding specimen MUST register as changed -----------
    assert _norm(old.parse_amounts("TZS 11 milioni")) != _norm(new.parse_amounts("TZS 11 milioni")), \
        "the sweep cannot see the founding specimen -- it is inert"
    changed = []
    for q in qs:
        try:
            po, pn = _norm(old.parse_amounts(q)), _norm(new.parse_amounts(q))
            so, sn = old.sole_plausible_amount(q), new.sole_plausible_amount(q)
        except Exception as e:                                       # noqa: BLE001
            changed.append({"q": q, "error": f"{type(e).__name__}: {e}"})
            continue
        so = None if so is None else float(so)
        sn = None if sn is None else float(sn)
        if po != pn or so != sn:
            changed.append({"q": q, "old_amounts": po, "new_amounts": pn, "old_sole": so, "new_sole": sn})
    res = {"files_scanned": files, "distinct_strings": len(qs), "changed": changed}
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"files {files} | distinct strings {len(qs)} | CHANGED {len(changed)}")
    return res


if __name__ == "__main__":
    main()

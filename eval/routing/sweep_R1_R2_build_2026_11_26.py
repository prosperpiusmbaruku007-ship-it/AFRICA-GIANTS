# -*- coding: utf-8 -*-
"""R1/R2 BUILD SWEEP (2026-11-26). Compares the router at commit 6f27ff1 (BEFORE) with the working tree (AFTER) over every question in every corpus,
on `detect_intent`, `fixed_statement_topic` and the extra-clarification-line predicate. READ-ONLY. Every row that differs is printed: read each (R12c).
BEFORE is loaded by executing `git show 6f27ff1:chike/routing.py` into a module of the `chike` package (not a worktree, not a reload: R24b).
  python eval/routing/sweep_R1_R2_build_2026_11_26.py  -> eval/results/sweep_R1_R2_build_2026_11_26.json   Exit 1 on a diversion not in EXPECTED or a failed probe."""
import glob
import io
import json
import os
import subprocess
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
from chike import routing as AFTER  # noqa: E402

BEFORE_SHA = "6f27ff1"
OUT = os.path.join(REPO, "eval", "results", "sweep_R1_R2_build_2026_11_26.json")
KEYS = ("question_sw", "question", "q", "instruction", "prompt", "text")
# (text, expected AFTER (intent, topic), why). The must-not-change half does the work (R17).
PROBES = [
    ("Mfanyakazi mgeni analipa PAYE kiasi gani?", ("fixed_statement", "paye_residency"), "R1"),
    ("Mgeni anayefanya kazi Tanzania analipa PAYE kiasi gani?", ("fixed_statement", "paye_residency"), "R1 variant"),
    ("Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?", ("fixed_statement", "director_fees_wht"), "R2"),
    ("Ada ya wakurugenzi hukatwa kodi kiasi gani?", ("fixed_statement", "director_fees_wht"), "R2 plural"),
    ("Mfanyakazi mgeni analipwa TZS 2,000,000, PAYE kiasi gani?", ("paye", None), "R1 with an amount: engine path unchanged"),
    ("Mfanyakazi mgeni analipwa milioni mbili, PAYE kiasi gani?", None, "amount in words: report only"),
    ("Ada ya mkurugenzi ni TZS 5,000,000, WHT ni kiasi gani?", ("none", None), "R2 with an amount: model path for now"),
    ("Mshahara wa mgeni ni mkubwa, nikatwe PAYE kiasi gani mimi?", ("none", None), "FIRST PERSON stays off the statement route"),
    ("Mgeni analipa PAYE kiasi gani mimi?", ("none", None), "first person, bare"),
    ("Nikikaa nchini siku 183, PAYE yangu ni ya mkazi au asiye mkazi?", ("fixed_statement", "paye_residency"), "first person REGIME question (rs_04) keeps its statement -- the over-broad first draft of the keep-veto removed it"),
    ("PAYE yangu kama mgeni ni kiasi gani?", ("none", None), "first person 'yangu'"),
    ("Mgeni wa Kenya analipa PAYE kiasi gani?", ("none", None), "another country"),
    ("Mgeni analipa NSSF kiasi gani?", ("none", None), "no PAYE word"),
    ("Ada ya mkurugenzi nilipwe kiasi gani?", ("none", None), "no tax need-word"),
]
LINE_PROBES = [  # (text, expect the extra line?)
    ("Mshahara wa mgeni ni mkubwa, nikatwe PAYE kiasi gani mimi?", True),
    ("PAYE yangu kama mgeni ni kiasi gani?", True),
    ("Nikatwe PAYE kiasi gani mimi?", False),                      # first person, NOT foreign -> plain clarification
    ("Mfanyakazi mgeni analipa PAYE kiasi gani?", False),          # foreign, NOT first person -> the statement route, no clarification
    ("Mgeni PAYE kiasi gani mimi, mshahara 2,000,000?", False),    # a figure -> never
]


def _before():
    src = subprocess.check_output(["git", "show", f"{BEFORE_SHA}:chike/routing.py"], cwd=REPO).decode("utf-8")
    m = types.ModuleType("chike.routing_before")
    m.__package__ = "chike"
    m.__file__ = "routing_before.py"
    exec(compile(src, "routing_before.py", "exec"), m.__dict__)
    return m


def _qs():
    seen, rows = set(), []
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "**", "*.jsonl"), recursive=True) + glob.glob(os.path.join(REPO, "datasets", "**", "*.jsonl"), recursive=True)):
        for ln in io.open(f, encoding="utf-8", errors="replace"):
            try:
                o = json.loads(ln)
            except Exception:
                continue
            if isinstance(o, dict):
                q = next((o[k] for k in KEYS if isinstance(o.get(k), str) and o[k].strip()), None)
                if q and q not in seen:
                    seen.add(q)
                    rows.append((os.path.relpath(f, REPO).replace("\\", "/"), o.get("id") or "", q))
    return rows


def _view(mod, t):
    return (mod.detect_intent(t), mod.fixed_statement_topic(t))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    B = _before()
    assert B.detect_intent("Mfanyakazi mgeni analipa PAYE kiasi gani?") == "none", "BEFORE must be the pre-change router (R1 unrouted) -- the premise of the sweep"
    art = {"before": BEFORE_SHA, "probes": [], "failures": [], "diversions": [], "line_probes": []}
    for t, exp, why in PROBES:
        b, a = _view(B, t), _view(AFTER, t)
        ok = exp is None or a == exp
        art["probes"].append({"text": t, "before": b, "after": a, "expected": exp, "ok": ok, "why": why})
        if not ok:
            art["failures"].append(t)
    from chike import clarification
    for t, want in LINE_PROBES:
        has = clarification.PAYROLL_AMOUNT_RESIDENCY_LINE in clarification.payroll_amount_for(t)
        art["line_probes"].append({"text": t, "expected": want, "got": has, "ok": has == want})
        if has != want:
            art["failures"].append("line:" + t)
    qs = _qs()
    art["population"] = {"questions": len(qs), "files": len({f for f, _, _ in qs})}
    for f, i, q in qs:
        b, a = _view(B, q), _view(AFTER, q)
        if a != b:
            art["diversions"].append({"file": f, "id": i, "before": b, "after": a, "question": q})
    json.dump(art, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"population {len(qs)} unique questions / {art['population']['files']} files | diversions {len(art['diversions'])} | failures {len(art['failures'])}")
    for p in art["probes"]:
        print(f"  [{'ok ' if p['ok'] else 'FAIL'}] {str(p['before']):<34}-> {str(p['after']):<38} {p['text'][:62]}")
    for p in art["line_probes"]:
        print(f"  [{'ok ' if p['ok'] else 'FAIL'}] line expected={p['expected']!s:<5} got={p['got']!s:<5} {p['text'][:60]}")
    for d in art["diversions"]:
        print(f"  DIVERSION {d['before']} -> {d['after']} {d['file']} {d['id']} | {d['question'][:120]}")
    return 1 if art["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())

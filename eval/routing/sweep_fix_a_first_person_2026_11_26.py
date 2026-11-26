# -*- coding: utf-8 -*-
"""FIX A BUILD SWEEP (2026-11-26, founder-approved). A first-person, figure-free PAYE ask (or `kodi` + a deduction verb) gets the salary clarification.
Compares `is_uncomputable_payroll_amount` at HEAD (BEFORE, `git show HEAD:chike/routing.py` executed into a module of the `chike` package: not a worktree,
not a reload, R24b) with the working tree (AFTER) over every question in every corpus. READ-ONLY. Every diversion is printed and must be read (R12c).
  python eval/routing/sweep_fix_a_first_person_2026_11_26.py -> eval/results/sweep_fix_a_first_person_2026_11_26.json   Exit 1 on a failed probe."""
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

BEFORE_REF = "HEAD"
OUT = os.path.join(REPO, "eval", "results", "sweep_fix_a_first_person_2026_11_26.json")
KEYS = ("question_sw", "question", "q", "instruction", "prompt", "text")
# (text, expected AFTER is_uncomputable_payroll_amount, why). The must-not half does the work (R17): a clean corpus sweep is a lower bound.
PROBES = [
    ("Nikatwe PAYE kiasi gani mimi?", True, "the live specimen: fabricated TZS 800,000 -> 78,000"),
    ("Nikatwe PAYE kiasi gani?", True, "no `mimi`; nikatwe is itself first person"),
    ("PAYE yangu ni kiasi gani?", True, "yangu"),
    ("Ninakatwa kodi kiasi gani mimi?", True, "generic kodi WITH a deduction verb"),
    ("Mshahara wa mgeni ni mkubwa, nikatwe PAYE kiasi gani mimi?", True, "already clarified before (payroll word): unchanged"),
    ("Nilipe kodi kiasi gani mimi?", False, "FOUNDER MUST-NOT: a shop owner's kodi with no deduction verb"),
    ("Nilipe kodi ya duka kiasi gani?", False, "kodi, no deduction verb"),
    ("Ninalipa kodi ya pango kiasi gani?", False, "kodi, no deduction verb"),
    ("Nilipe VAT kiasi gani mimi?", False, "other levy, no PAYE, no kodi"),
    ("Nikikaa nchini siku 183, PAYE yangu ni ya mkazi au asiye mkazi?", False, "rs_04 REGIME question: no money ask"),
    ("Nikikaa nchini muda mrefu, PAYE yangu ni ya mkazi au asiye mkazi?", False, "the regime question with NO digit: only the money-ask limb protects it"),
    ("PAYE ni kiasi gani?", False, "money ask + PAYE but NOT first person"),
    ("PAYE yangu ni asilimia ngapi?", False, "a RATE ask"),
    ("Nikichelewa kulipa PAYE yangu nitatozwa faini kiasi gani?", False, "penalty ask"),
    ("Nikatwe PAYE kiasi gani mimi, mshahara 800,000?", False, "a figure: engine route, not a clarification"),
    ("Mfanyakazi mgeni analipa PAYE kiasi gani?", False, "third person: the R1 statement route"),
    ("Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?", False, "R2 statement route, no first person"),
    ("PAYE inakatwa lini?", False, "no first person, a date ask"),
]


def _before():
    src = subprocess.check_output(["git", "show", f"{BEFORE_REF}:chike/routing.py"], cwd=REPO).decode("utf-8")
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


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    B = _before()
    assert not B.is_uncomputable_payroll_amount("Nikatwe PAYE kiasi gani mimi?"), "BEFORE must be the pre-fix router -- the premise of the sweep"
    art = {"before": BEFORE_REF, "probes": [], "failures": [], "diversions": []}
    for t, exp, why in PROBES:
        b, a = B.is_uncomputable_payroll_amount(t), AFTER.is_uncomputable_payroll_amount(t)
        art["probes"].append({"text": t, "before": b, "after": a, "expected": exp, "ok": a == exp, "why": why})
        if a != exp:
            art["failures"].append(t)
    qs = _qs()
    assert qs, "empty population (R20)"
    art["population"] = {"questions": len(qs), "files": len({f for f, _, _ in qs})}
    for f, i, q in qs:
        b, a = B.is_uncomputable_payroll_amount(q), AFTER.is_uncomputable_payroll_amount(q)
        if a != b:
            art["diversions"].append({"file": f, "id": i, "before": b, "after": a, "intent": AFTER.detect_intent(q),
                                      "fixed_statement": str(AFTER.fixed_statement_topic(q)), "question": q})
    json.dump(art, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"population {len(art['population'] and qs)} unique questions / {art['population']['files']} files | diversions {len(art['diversions'])} | failures {len(art['failures'])}")
    for p in art["probes"]:
        print(f"  [{'ok ' if p['ok'] else 'FAIL'}] {p['before']!s:<5}-> {p['after']!s:<5} {p['text'][:70]}")
    for d in art["diversions"]:
        print(f"  DIVERSION {d['before']} -> {d['after']} intent={d['intent']} stmt={d['fixed_statement']} {d['file']} {d['id']} | {d['question'][:130]}")
    return 1 if art["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())

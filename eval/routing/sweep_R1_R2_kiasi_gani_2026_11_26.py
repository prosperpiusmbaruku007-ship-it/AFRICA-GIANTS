# -*- coding: utf-8 -*-
"""R1 / R2 ROUTE RECALL -- PROPOSAL SWEEP (2026-11-26). READ-ONLY: nothing in chike/ is changed; the candidate is applied in memory only.

The candidate: drop the `kiasi\s+gani` alternative from the VETO lists of the two fixed topics `paye_residency` (R1: "Mfanyakazi mgeni analipa PAYE kiasi gani?") and
`director_fees_wht` (R2: "Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?"). Both vetoes already carry money figures / TZS / "kokotoa" / "hesabu", so a question WITH an amount
stays vetoed; only the no-figure "kiasi gani" ask is released. Prints every diversion (read each: R12c), probes in both directions (R17), and the population measured (R22).
  python eval/routing/sweep_R1_R2_kiasi_gani_2026_11_26.py  ->  eval/results/sweep_R1_R2_kiasi_gani_2026_11_26.json   Exit 1 on a failed probe/pin."""
import glob
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
from chike import routing  # noqa: E402

OUT = os.path.join(REPO, "eval", "results", "sweep_R1_R2_kiasi_gani_2026_11_26.json")
TARGETS = ("paye_residency", "director_fees_wht")
DROP = r"kiasi\s+gani|"
KEYS = ("question_sw", "question", "q", "instruction", "prompt", "text")

MUST_ROUTE = [  # (text, expected topic, why)
    ("Mfanyakazi mgeni analipa PAYE kiasi gani?", "paye_residency", "R1 founding phrasing"),
    ("Mgeni anayefanya kazi Tanzania analipa PAYE kiasi gani?", "paye_residency", "R1 second phrasing"),
    ("Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?", "director_fees_wht", "R2 founding phrasing"),
    ("Mkurugenzi akilipwa ada, kodi ya zuio inakatwa kiasi gani?", None, "R2 variant WITHOUT the 'ada ya mkurugenzi' noun phrase -- the director cue does not match, expected None (records the cue's reach)"),
    ("Ada ya wakurugenzi hukatwa kodi kiasi gani?", "director_fees_wht", "R2 plural"),
]
MUST_NOT_CHANGE = [  # a figure, another country, another levy, first person, a different ask: the route must stay as it is NOW
    ("Mfanyakazi mgeni analipwa TZS 2,000,000, PAYE kiasi gani?", "amount present -> engine path unchanged"),
    ("Mfanyakazi mgeni analipwa milioni mbili, PAYE kiasi gani?", "amount in words -> unchanged"),
    ("Ada ya mkurugenzi ni TZS 5,000,000, inakatwa kodi ya zuio kiasi gani?", "amount present -> unchanged (model path)"),
    ("Mgeni wa Kenya analipa PAYE kiasi gani?", "another country vetoes"),
    ("Mgeni analipa NSSF kiasi gani?", "no PAYE word"),
    ("Mfanyakazi mgeni, PAYE na SDL kiasi gani?", "another levy vetoes"),
    ("Ada ya mkurugenzi nilipwe kiasi gani?", "no tax/withholding need-word"),
    ("Mshahara wa mgeni ni mkubwa, nikatwe PAYE kiasi gani mimi?", "FIRST PERSON, no figure -- read this one (reported, not asserted)"),
]


def _questions():
    seen, rows = set(), []
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "**", "*.jsonl"), recursive=True) + glob.glob(os.path.join(REPO, "datasets", "**", "*.jsonl"), recursive=True)):
        for ln in io.open(f, encoding="utf-8", errors="replace"):
            try:
                o = json.loads(ln)
            except Exception:
                continue
            if not isinstance(o, dict):
                continue
            q = next((o[k] for k in KEYS if isinstance(o.get(k), str) and o[k].strip()), None)
            if q and q not in seen:
                seen.add(q)
                rows.append((os.path.relpath(f, REPO).replace("\\", "/"), o.get("id") or o.get("review_id") or "", q))
    return rows


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    orig = list(routing._FS_TOPICS)
    new, changed = [], []
    for name, cue, need, veto in orig:
        if name in TARGETS:
            assert veto is not None and DROP in veto.pattern, f"{name}: the veto does not carry `kiasi gani|` -- the premise of this sweep is false"
            veto = re.compile(veto.pattern.replace(DROP, "", 1), veto.flags)
            changed.append(name)
        new.append((name, cue, need, veto))
    assert sorted(changed) == sorted(TARGETS)

    def topic(t, table):
        routing._FS_TOPICS = table
        try:
            return routing.fixed_statement_topic(t)
        finally:
            routing._FS_TOPICS = orig
    art = {"candidate": "drop `kiasi\s+gani|` from the veto of " + ", ".join(TARGETS), "probes": [], "pin_failures": [], "diversions": []}
    for t, exp, why in MUST_ROUTE:
        b, a = topic(t, orig), topic(t, new)
        ok = a == exp
        art["probes"].append({"kind": "must_route", "text": t, "before": b, "after": a, "expected": exp, "ok": ok, "why": why})
        if not ok:
            art["pin_failures"].append(t)
    for t, why in MUST_NOT_CHANGE:
        b, a = topic(t, orig), topic(t, new)
        report_only = why.startswith("FIRST PERSON")
        ok = report_only or a == b
        art["probes"].append({"kind": "must_not_change", "text": t, "before": b, "after": a, "ok": ok, "why": why, "report_only": report_only})
        if not ok:
            art["pin_failures"].append(t)
    qs = _questions()
    art["population"] = {"questions": len(qs), "files": len({f for f, _, _ in qs})}
    for f, i, q in qs:
        b, a = topic(q, orig), topic(q, new)
        if a != b:
            art["diversions"].append({"file": f, "id": i, "before": b, "after": a, "question": q})
    json.dump(art, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"population {len(qs)} unique questions over {art['population']['files']} files | diversions {len(art['diversions'])} | probe failures {len(art['pin_failures'])}")
    for p in art["probes"]:
        print(f"  [{'ok ' if p['ok'] else 'FAIL'}] {p['kind']:<15} {str(p['before']):<18}-> {str(p['after']):<18} {p['text'][:70]}")
    for d in art["diversions"]:
        print(f"  DIVERSION {d['before']}->{d['after']} {d['file']} {d['id']} | {d['question'][:110]}")
    return 1 if art["pin_failures"] else 0


if __name__ == "__main__":
    sys.exit(main())

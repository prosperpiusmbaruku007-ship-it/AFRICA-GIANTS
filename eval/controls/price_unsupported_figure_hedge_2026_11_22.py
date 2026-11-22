# -*- coding: utf-8 -*-
"""READ-ONLY PRICING of the PROPOSED "unsupported figure" hedge (nothing is built or wired): a fact-path reply that states a money amount, a rate or a day/month/year count appearing in NEITHER the served facts NOR the question would have
that figure removed and be told "no confirmed figure, ask <authority>". The failure mode is a HEDGE, not a refusal.

THE SUPPORT SET is the question's own numbers, the served facts' numbers and what is DERIVABLE from the two by one arithmetic step. Served facts are NOT stored on the gate artifacts, so the support set uses EVERY row of the committed index
(216 rows) -- a LENIENT proxy that can only UNDER-count unsupported figures. A figure unsupported even against the whole index is, a fortiori, unsupported against the three rows actually served.

POPULATIONS, each named with why it is the one that decides (R22):
  gate replies (the last full gate, c2143c0, 362 judged rows): where the harm IS -- the question is whether unsupported figures sit on the WRONG replies and not the right ones.
  gold answers (eval/accuracy_gate): what a CORRECT answer states -- a rule that flags gold figures would remove correct numbers.
  training answers (datasets/tier1a/cleaned_pairs + sft_shaped_pairs): the vocabulary of correct answers at scale.
THE PRELIMINARY GATE 2 SET IS BURNED AND IS NOT USED.

    python eval/controls/price_unsupported_figure_hedge_2026_11_22.py  ->  eval/results/price_unsupported_figure_hedge_2026_11_22.json
"""
import glob
import io
import itertools
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))

NUM = re.compile(r"(?<![\d,.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?![\d])")
UNIT_AFTER = re.compile(r"^\s*(milioni|million|elfu|laki|bilioni|billion|%|asilimia|siku|days?|miezi|months?|wiki|weeks?|miaka|years?)", re.IGNORECASE)
UNIT_BEFORE = re.compile(r"(tzs|sh\.?|shilingi|asilimia|siku|miezi|wiki|miaka|usd|\$)\s*$", re.IGNORECASE)
SCALE = {"milioni": 1_000_000, "million": 1_000_000, "elfu": 1_000, "laki": 100_000, "bilioni": 1_000_000_000, "billion": 1_000_000_000}


def figures(text):
    """[(value: float, kind)] for each money amount, rate and day/month/year count in `text`. A small bare integer (a list marker, '3:2', an ordinal) is not a figure."""
    out = []
    t = text or ""
    for m in NUM.finditer(t):
        raw = m.group(1)
        v = float(raw.replace(",", ""))
        after = UNIT_AFTER.match(t[m.end():m.end() + 14])
        before = UNIT_BEFORE.search(t[max(0, m.start() - 12):m.start()])
        unit = (after.group(1).lower() if after else None) or (before.group(1).lower() if before else None)
        if unit in SCALE and after:
            out.append((v * SCALE[unit], "money"))
        elif unit in ("%", "asilimia"):
            out.append((v, "rate"))
        elif unit and re.match(r"siku|day|miezi|month|wiki|week|miaka|year", unit):
            out.append((v, "count"))
        elif unit in ("tzs", "sh", "sh.", "shilingi", "usd", "$") or v >= 1000:
            out.append((v, "money"))
    return out


def support_set(question, index_numbers):
    qn = {f[0] for f in figures(question)} | {float(x.replace(",", "")) for x in NUM.findall(question or "")}
    base = qn | index_numbers
    derived = set()
    for a, b in itertools.product(list(qn), list(index_numbers | qn)):
        for v in (a * b / 100.0, a * b, a + b, abs(a - b), (a / b) if b else None, (b / a) if a else None):
            if v is not None:
                derived.add(round(v, 2))
    return base, derived


def load_index_numbers():
    rows = json.load(io.open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    nums = set()
    for r in rows:
        nums |= {float(x.replace(",", "")) for x in NUM.findall(r)}
    return nums, len(rows)


def pairs_gold():
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "accuracy_gate", "eval_questions_00*.jsonl"))):
        for line in io.open(f, encoding="utf-8"):
            if line.strip():
                o = json.loads(line)
                yield o.get("question_sw", ""), o.get("correct_answer_sw", ""), o["id"]


def pairs_training():
    for pat in ("datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl"):
        for f in glob.glob(os.path.join(REPO, pat)):
            for line in io.open(f, encoding="utf-8", errors="replace"):
                try:
                    o = json.loads(line)
                except Exception:                                        # noqa: BLE001
                    continue
                if isinstance(o, dict) and isinstance(o.get("answer_sw"), str) and isinstance(o.get("question_sw"), str):
                    yield o["question_sw"], o["answer_sw"], os.path.basename(f)


def judge(population, index_numbers):
    """per-population counts. `rows` = [(question, text, tag)]"""
    total_f = unsupported = unsupported_after_derivation = texts_touched = texts_with_fig = 0
    touched = []
    for q, a, tag in population:
        figs = figures(a)
        if not figs:
            continue
        texts_with_fig += 1
        base, derived = support_set(q, index_numbers)
        un = [f for f in figs if f[0] not in base]
        total_f += len(figs)
        unsupported += len(un)
        un2 = [f for f in un if round(f[0], 2) not in derived]
        unsupported_after_derivation += len(un2)
        if un2:
            texts_touched += 1
            touched.append((q, a, tag, un2))
    return dict(texts_with_figures=texts_with_fig, figures=total_f, unsupported_vs_question_and_index=unsupported, unsupported_after_one_step_derivation=unsupported_after_derivation,
                texts_that_would_be_touched=texts_touched), touched


def main():
    idx_nums, n_idx = load_index_numbers()
    art = {"index_rows": n_idx, "note": "support set = question numbers + EVERY index row's numbers + one-step arithmetic: lenient, can only under-count unsupported figures"}
    # gate replies, with the judge's verdict
    g = json.load(io.open(os.path.join(REPO, "eval", "results", "gate_production_c2143c0.json"), encoding="utf-8"))
    rows = [r for r in g["rows"] if isinstance(r.get("generated"), str)]
    gate_pop = [(r["question_sw"], r["generated"], r) for r in rows]
    stats, touched = judge(gate_pop, idx_nums)
    art["gate_replies"] = stats
    by = {"wrong": [0, 0], "correct": [0, 0], "undetermined": [0, 0], "none": [0, 0]}
    for r in rows:
        v = r.get("judge") if r.get("judge") in ("wrong", "correct", "undetermined") else "none"
        by[v][1] += 1
    for q, a, r, un in touched:
        v = r.get("judge") if r.get("judge") in ("wrong", "correct", "undetermined") else "none"
        by[v][0] += 1
    art["gate_replies_touched_by_judge_verdict"] = {k: {"touched": v[0], "of": v[1]} for k, v in by.items()}
    art["gate_touched_examples"] = [{"id": r["id"], "judge": r.get("judge"), "regex_pass": r.get("pass"), "unsupported": [f"{f[0]:g} ({f[1]})" for f in un], "reply": a[:260]} for q, a, r, un in touched]
    # gold and training
    gold_stats, gold_touched = judge(list(pairs_gold()), idx_nums)
    art["gold_answers"] = gold_stats
    art["gold_touched_examples"] = [{"id": tag, "unsupported": [f"{f[0]:g} ({f[1]})" for f in un], "answer": a[:260]} for q, a, tag, un in gold_touched[:40]]
    tr_stats, tr_touched = judge(list(pairs_training()), idx_nums)
    art["training_answers"] = tr_stats
    art["training_touched_examples"] = [{"file": tag, "unsupported": [f"{f[0]:g} ({f[1]})" for f in un], "q": q[:140], "answer": a[:220]} for q, a, tag, un in tr_touched[:40]]
    print(json.dumps({k: v for k, v in art.items() if not k.endswith("examples")}, ensure_ascii=False, indent=1))
    print(f"\nGATE replies touched, read each ({len(art['gate_touched_examples'])}):")
    for e in art["gate_touched_examples"]:
        print(f"  {e['id']} judge={e['judge']} regex_pass={e['regex_pass']} unsupported={e['unsupported']} | {e['reply'][:150]}")
    io.open(os.path.join(REPO, "eval", "results", "price_unsupported_figure_hedge_2026_11_22.json"), "w", encoding="utf-8").write(json.dumps(art, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

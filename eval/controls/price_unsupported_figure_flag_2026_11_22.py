# -*- coding: utf-8 -*-
"""PRICING of the FLAG-ONLY unsupported-figure check as BUILT (handler_core.unsupported_figures, tokenizer slips fixed: Act years, decimal commas). It re-prices the 2026-11-22 proposal with the SHIPPED function, not a copy.
FLAG-ONLY: nothing is rewritten; the cost of a false flag is a reviewer reading one extra line, the cost of a miss is unchanged. THE PRELIMINARY GATE 2 SET IS BURNED AND IS NOT USED.

SUPPORT SET: the question + EVERY row of the served index (216) + one-step arithmetic -- LENIENT, so unsupported counts are a LOWER bound (a figure unsupported against the whole index is unsupported against the three rows served).
POPULATIONS, each with why it decides (R22):
  gate fact-path replies (c2143c0, `compute` false): where the harm is -- do flags sit on the WRONG replies and not the right ones, and how many wrong replies does it reach at all (recall)?
  gold answers (eval/accuracy_gate): what a CORRECT answer states -- a flag on a gold figure is a false alarm a reviewer would have to dismiss.
  training answers (cleaned_pairs + sft_shaped_pairs): the vocabulary of correct answers at scale.
    python eval/controls/price_unsupported_figure_flag_2026_11_22.py  ->  eval/results/price_unsupported_figure_flag_2026_11_22.json"""
import collections
import glob
import importlib.util
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
_spec = importlib.util.spec_from_file_location("hc_price", os.path.join(REPO, "chike-whatsapp", "handler_core.py"))
hc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc)


def verdict(r):
    return r.get("judge") if r.get("judge") in ("wrong", "correct", "undetermined") else "none"


def flagged(q, a, rows):
    return hc.unsupported_figures(q, a, rows, None, 1)


def main():
    rows_idx = json.load(io.open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    g = json.load(io.open(os.path.join(REPO, "eval", "results", "gate_production_c2143c0.json"), encoding="utf-8"))
    fact = [r for r in g["rows"] if isinstance(r.get("generated"), str) and not r.get("compute")]
    tot, hit, ex = collections.Counter(verdict(r) for r in fact), collections.Counter(), []
    for r in fact:
        f = flagged(r["question_sw"], r["generated"], rows_idx)
        if f:
            hit[verdict(r)] += 1
            ex.append({"id": r["id"], "judge": r.get("judge"), "regex_pass": r.get("pass"), "flagged": f, "reply": r["generated"][:240]})
    gold = []
    for fpath in sorted(glob.glob(os.path.join(REPO, "eval", "accuracy_gate", "eval_questions_00*.jsonl"))):
        for line in io.open(fpath, encoding="utf-8"):
            if line.strip():
                o = json.loads(line)
                f = flagged(o.get("question_sw", ""), o.get("correct_answer_sw", ""), rows_idx)
                if f:
                    gold.append({"id": o["id"], "flagged": f, "answer": o.get("correct_answer_sw", "")[:200]})
    n_train = n_train_flag = 0
    train = []
    for pat in ("datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl"):
        for fpath in glob.glob(os.path.join(REPO, pat)):
            for line in io.open(fpath, encoding="utf-8", errors="replace"):
                try:
                    o = json.loads(line)
                except Exception:                                        # noqa: BLE001
                    continue
                if isinstance(o, dict) and isinstance(o.get("answer_sw"), str) and isinstance(o.get("question_sw"), str):
                    n_train += 1
                    f = flagged(o["question_sw"], o["answer_sw"], rows_idx)
                    if f:
                        n_train_flag += 1
                        train.append({"file": os.path.basename(fpath), "flagged": f, "q": o["question_sw"][:120], "answer": o["answer_sw"][:200]})
    art = {"gate": "c2143c0", "fact_path_rows": len(fact), "flagged_by_judge_verdict": {k: {"flagged": hit[k], "of": tot[k]} for k in tot},
           "recall_on_wrong_fact_path_replies": f"{hit['wrong']}/{tot['wrong']}", "false_alarm_on_correct_fact_path_replies": f"{hit['correct']}/{tot['correct']}",
           "gold_answers_flagged": len(gold), "training_answers": n_train, "training_answers_flagged": n_train_flag,
           "gate_examples": ex, "gold_examples": gold[:40], "training_examples": train[:40],
           "note": "lenient support set (whole index): flag counts are a LOWER bound; fact-path only; preliminary Gate 2 set burned and not used"}
    print(json.dumps({k: v for k, v in art.items() if not k.endswith("examples")}, ensure_ascii=False, indent=1))
    for e in ex:
        print(f"  GATE {e['id']} judge={e['judge']} flagged={e['flagged']} | {e['reply'][:120]!r}")
    for e in gold:
        print(f"  GOLD {e['id']} flagged={e['flagged']} | {e['answer'][:120]!r}")
    io.open(os.path.join(REPO, "eval", "results", "price_unsupported_figure_flag_2026_11_22.json"), "w", encoding="utf-8").write(json.dumps(art, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

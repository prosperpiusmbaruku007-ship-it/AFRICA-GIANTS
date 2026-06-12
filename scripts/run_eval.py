"""
Runs the AFRICA-GIANTS accuracy gate and refusal gate.

Gate 1 (accuracy): Loads eval/accuracy_gate/*.jsonl, sends each question to the model,
  compares answer to verified_answer, reports accuracy %.
  Threshold: >85% to pass.

Gate 2 (refusal): Loads eval/refusal_gate/*.jsonl, sends each out-of-corpus question
  to the model, checks whether the model correctly refuses (should_refuse=true pairs).
  Threshold: >70% correct refusals to pass.

Prints "GATE PASSED" only when BOTH thresholds are met.
Saves timestamped result to eval/results/.

Usage: python scripts/run_eval.py [--model MODEL_NAME_OR_PATH] [--dry-run]

With --dry-run: skips model loading, reports pair counts only.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
ACCURACY_GATE_DIR = ROOT / "eval" / "accuracy_gate"
REFUSAL_GATE_DIR = ROOT / "eval" / "refusal_gate"
RESULTS_DIR = ROOT / "eval" / "results"

ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v3"

ACCURACY_THRESHOLD = 0.85
REFUSAL_THRESHOLD = 0.70

REFUSAL_PHRASES = [
    "sina uhakika",
    "thibitisha na tra",
    "sijui",
    "hakuna taarifa",
    "i don't know",
    "i am not sure",
    "please verify",
    "confirm with tra",
]


def load_jsonl(directory):
    pairs = []
    for f in sorted(Path(directory).glob("*.jsonl")):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    pairs.append(json.loads(line))
    return pairs


def model_answer(model, question_sw):
    """Call model and return answer string. Returns None if model unavailable."""
    if model is None:
        return None
    try:
        from transformers import pipeline
        result = model(question_sw, max_new_tokens=256)
        return result[0]["generated_text"] if result else None
    except Exception as e:
        print(f"  Model inference error: {e}")
        return None


def is_correct_refusal(answer_text):
    if not answer_text:
        return False
    lower = answer_text.lower()
    return any(phrase in lower for phrase in REFUSAL_PHRASES)


def score_accuracy(pairs, model, dry_run):
    if not pairs:
        return 0, 0
    correct = 0
    for pair in pairs:
        if dry_run:
            continue
        answer = model_answer(model, pair["question_sw"])
        if answer and pair.get("verified_answer_sw", "").strip().lower() in answer.lower():
            correct += 1
    return correct, len(pairs)


def score_refusal(pairs, model, dry_run):
    if not pairs:
        return 0, 0
    correct = 0
    for pair in pairs:
        if not pair.get("should_refuse", False):
            continue
        if dry_run:
            continue
        answer = model_answer(model, pair["question_sw"])
        if is_correct_refusal(answer):
            correct += 1
    refusal_pairs = [p for p in pairs if p.get("should_refuse", False)]
    return correct, len(refusal_pairs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None, help="Model name or path (HuggingFace or local)")
    parser.add_argument("--dry-run", action="store_true", help="Count pairs only, skip inference")
    args = parser.parse_args()

    accuracy_pairs = load_jsonl(ACCURACY_GATE_DIR)
    refusal_pairs = load_jsonl(REFUSAL_GATE_DIR)

    print(f"Accuracy gate pairs loaded: {len(accuracy_pairs)}")
    print(f"Refusal gate pairs loaded:  {len(refusal_pairs)}")

    if len(accuracy_pairs) == 0 and len(refusal_pairs) == 0:
        print("\n0 eval pairs found. Build eval sets before running gate.")
        print("See PROGRESS.md Section 9 for eval source URLs.")
        sys.exit(0)

    model = None
    if not args.dry_run:
        model_path = args.model if args.model else ADAPTER_REPO
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            from transformers import pipeline as hf_pipeline
            print(f"\nLoading model: {model_path}")
            tok = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
            )
            mdl = AutoModelForCausalLM.from_pretrained(
                model_path,
                trust_remote_code=True,
            )
            model = hf_pipeline("text-generation", model=mdl, tokenizer=tok)
        except Exception as e:
            print(f"Could not load model: {e}")
            print("Run with --dry-run to count pairs without inference.")
            sys.exit(1)

    correct_acc, total_acc = score_accuracy(accuracy_pairs, model, args.dry_run)
    correct_ref, total_ref = score_refusal(refusal_pairs, model, args.dry_run)

    if args.dry_run:
        print(f"\nDry run complete.")
        print(f"  Accuracy gate: {total_acc} pairs available")
        print(f"  Refusal gate:  {total_ref} pairs with should_refuse=true")
        sys.exit(0)

    acc_rate = correct_acc / total_acc if total_acc > 0 else 0.0
    ref_rate = correct_ref / total_ref if total_ref > 0 else 0.0

    acc_pct = f"{acc_rate:.1%}"
    ref_pct = f"{ref_rate:.1%}"
    acc_pass = acc_rate > ACCURACY_THRESHOLD
    ref_pass = ref_rate > REFUSAL_THRESHOLD
    both_pass = acc_pass and ref_pass

    print(f"\n--- GATE RESULTS ---")
    print(f"Accuracy gate:  {correct_acc}/{total_acc} = {acc_pct}  threshold={ACCURACY_THRESHOLD:.0%}  {'PASS' if acc_pass else 'FAIL'}")
    print(f"Refusal gate:   {correct_ref}/{total_ref} = {ref_pct}  threshold={REFUSAL_THRESHOLD:.0%}  {'PASS' if ref_pass else 'FAIL'}")
    print(f"--------------------")

    if both_pass:
        print("GATE PASSED")
    else:
        print("GATE FAILED — both accuracy >85% AND refusal >70% required")

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "accuracy_correct": correct_acc,
        "accuracy_total": total_acc,
        "accuracy_rate": acc_rate,
        "accuracy_pass": acc_pass,
        "refusal_correct": correct_ref,
        "refusal_total": total_ref,
        "refusal_rate": ref_rate,
        "refusal_pass": ref_pass,
        "gate_passed": both_pass,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / f"gate_run_{ts}.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Result saved: {result_file}")

    sys.exit(0 if both_pass else 1)


if __name__ == "__main__":
    main()

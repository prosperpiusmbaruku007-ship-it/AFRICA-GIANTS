"""
Runs the AFRICA-GIANTS accuracy gate and refusal gate.

Gate 1 (accuracy): Loads eval/accuracy_gate/*.jsonl, sends each in-corpus question
  to the model, compares answer to correct_answer_sw using answer-type-aware scoring.
  Threshold: >85% to pass.

Gate 2 (refusal): From the same files, filters questions with
  answer_type == "out_of_corpus_refusal", checks whether the model correctly refuses.
  Threshold: >70% correct refusals to pass.

Prints "GATE PASSED" only when BOTH thresholds are met.
Saves timestamped result to eval/results/.

Usage: python scripts/run_eval.py [--model MODEL_NAME_OR_PATH] [--dry-run] [--per-question]

With --dry-run: skips model loading, reports pair counts only.
With --per-question: saves per-question results to eval/results/per_question_<timestamp>.json
  containing eval_id, subdomain, answer_type, model_output, correct_answer_sw, correct.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
ACCURACY_GATE_DIR = ROOT / "eval" / "accuracy_gate"
REFUSAL_GATE_DIR  = ROOT / "eval" / "refusal_gate"
RESULTS_DIR       = ROOT / "eval" / "results"

ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v3"

ACCURACY_THRESHOLD = 0.85
REFUSAL_THRESHOLD  = 0.70

# Bug 4 fix: phrases the model is trained to use when refusing out-of-corpus questions.
# Removed false-positive closings ("thibitisha na tra", "confirm with tra", "please verify",
# "hakuna taarifa") that appear in every factual answer and would inflate refusal scores.
REFUSAL_PHRASES = [
    "nje ya maarifa yangu",
    "swali hili liko nje",
    "sina uhakika",
    "sijui",
    "mshauri wa kodi",
    "outside my current knowledge",
    "i don't know",
    "i am not sure",
    "consult a registered",
    "beyond my knowledge",
]

# Bug 6 fix: Swahili yes/no word lists for yes_no scoring.
SWAHILI_YES = {"ndiyo", "ndio", "yes", "sahihi", "kweli"}
SWAHILI_NO  = {"hapana", "la", "no", "siyo", "sivyo"}

# Basic Swahili number-word mapping for number extraction (Bug 5 fix).
SWAHILI_NUMBERS = {
    "moja": 1, "mbili": 2, "tatu": 3, "nne": 4, "tano": 5,
    "sita": 6, "saba": 7, "nane": 8, "tisa": 9, "kumi": 10,
    "ishirini": 20, "thelathini": 30, "arobaini": 40,
    "hamsini": 50, "sitini": 60, "sabini": 70, "themanini": 80,
    "tisini": 90, "mia": 100, "elfu": 1_000, "milioni": 1_000_000,
}


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


def extract_numbers(text):
    """Extract numeric values from text, handling digit strings and Swahili number words."""
    numbers = set()
    cleaned = text.replace(",", "")
    for m in re.finditer(r"\d+(?:\.\d+)?", cleaned):
        try:
            numbers.add(float(m.group()))
        except ValueError:
            pass
    lower = text.lower()
    for word, val in SWAHILI_NUMBERS.items():
        if re.search(r"\b" + word + r"\b", lower):
            numbers.add(float(val))
    return numbers


def score_number(correct_sw, model_text):
    """Pass if the model output contains any of the key numbers from the correct answer."""
    correct_nums = extract_numbers(correct_sw)
    if not correct_nums:
        return score_keyword_overlap(correct_sw, model_text)
    model_nums = extract_numbers(model_text)
    return bool(correct_nums & model_nums)


def score_yes_no(correct_sw, model_text):
    """Pass if model says yes/no matching what the correct answer says."""
    lower_correct = correct_sw.lower()
    lower_model   = model_text.lower()
    expected_yes  = any(w in lower_correct for w in SWAHILI_YES)
    expected_no   = any(re.search(r'\b' + w + r'\b', lower_correct) for w in SWAHILI_NO)
    if expected_yes:
        return any(w in lower_model for w in SWAHILI_YES)
    if expected_no:
        return any(re.search(r'\b' + w + r'\b', lower_model) for w in SWAHILI_NO)
    return False


def score_keyword_overlap(correct_sw, model_text, min_overlap=3):
    """Pass if model output shares enough content words (>5 chars) with correct answer."""
    def content_words(text):
        return {w for w in re.findall(r"[a-zA-ZÀ-ɏ]{6,}", text.lower())}
    correct_sw = re.sub(r'Thibitisha na.*$', '', correct_sw, flags=re.IGNORECASE | re.DOTALL).strip()
    correct_words = content_words(correct_sw)
    model_words   = content_words(model_text)
    shared = correct_words & model_words
    return len(shared) >= min_overlap


def is_correct_refusal(answer_text):
    """Bug 4 fix: check for trained refusal phrases, not false-positive closings."""
    if not answer_text:
        return False
    lower = answer_text.lower()
    return any(phrase in lower for phrase in REFUSAL_PHRASES)


def score_question(pair, answer_text):
    """Bug 3 fix: answer-type aware scoring instead of single substring match."""
    if not answer_text:
        return False
    answer_type = pair.get("answer_type", "definition")
    # Bug 1 fix: use correct_answer_sw (not verified_answer_sw which doesn't exist).
    correct_sw  = pair.get("correct_answer_sw", "").strip()
    if not correct_sw:
        return False

    if answer_type == "number":
        return score_number(correct_sw, answer_text)
    elif answer_type == "yes_no":
        return score_yes_no(correct_sw, answer_text)
    elif answer_type == "out_of_corpus_refusal":
        return is_correct_refusal(answer_text)
    else:
        # definition, procedure, penalty — keyword overlap
        return score_keyword_overlap(correct_sw, answer_text)


def score_accuracy(pairs, model, dry_run):
    """Bug 2 fix: skip out_of_corpus_refusal questions — those go to refusal gate.
    Returns (correct, total, records) where records is a list of per-question dicts."""
    in_corpus = [p for p in pairs if p.get("answer_type") != "out_of_corpus_refusal"]
    if not in_corpus:
        return 0, 0, []
    correct = 0
    records = []
    for pair in in_corpus:
        if dry_run:
            continue
        answer = model_answer(model, pair["question_sw"])
        is_correct = score_question(pair, answer)
        if is_correct:
            correct += 1
        records.append({
            "eval_id":          pair.get("id", ""),
            "subdomain":        pair.get("subdomain", ""),
            "answer_type":      pair.get("answer_type", ""),
            "model_output":     answer,
            "correct_answer_sw": pair.get("correct_answer_sw", ""),
            "correct":          is_correct,
        })
    return correct, len(in_corpus), records


def score_refusal(pairs, model, dry_run):
    """Bug 2 fix: filter by answer_type == out_of_corpus_refusal instead of should_refuse field
    and load from both accuracy_gate (where they live) and refusal_gate directories.
    Returns (correct, total, records) where records is a list of per-question dicts."""
    refusal_pairs = [p for p in pairs if p.get("answer_type") == "out_of_corpus_refusal"]
    if not refusal_pairs:
        return 0, 0, []
    correct = 0
    records = []
    for pair in refusal_pairs:
        if dry_run:
            continue
        answer = model_answer(model, pair["question_sw"])
        is_correct = is_correct_refusal(answer)
        if is_correct:
            correct += 1
        records.append({
            "eval_id":          pair.get("id", ""),
            "subdomain":        pair.get("subdomain", ""),
            "answer_type":      pair.get("answer_type", ""),
            "model_output":     answer,
            "correct_answer_sw": pair.get("correct_answer_sw", ""),
            "correct":          is_correct,
        })
    return correct, len(refusal_pairs), records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None, help="Model name or path (HuggingFace or local)")
    parser.add_argument("--dry-run", action="store_true", help="Count pairs only, skip inference")
    parser.add_argument("--per-question", action="store_true",
                        help="Save per-question results to eval/results/per_question_<timestamp>.json")
    args = parser.parse_args()

    # Load from both directories so refusal questions are found wherever they live.
    accuracy_pairs = load_jsonl(ACCURACY_GATE_DIR)
    refusal_extra  = load_jsonl(REFUSAL_GATE_DIR)
    all_pairs = accuracy_pairs + refusal_extra

    in_corpus_count  = len([p for p in all_pairs if p.get("answer_type") != "out_of_corpus_refusal"])
    refusal_count    = len([p for p in all_pairs if p.get("answer_type") == "out_of_corpus_refusal"])

    print(f"Accuracy gate pairs loaded: {in_corpus_count}")
    print(f"Refusal gate pairs loaded:  {refusal_count}")

    if in_corpus_count == 0 and refusal_count == 0:
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

    correct_acc, total_acc, records_acc = score_accuracy(all_pairs, model, args.dry_run)
    correct_ref, total_ref, records_ref = score_refusal(all_pairs, model, args.dry_run)

    if args.dry_run:
        print(f"\nDry run complete.")
        print(f"  Accuracy gate: {total_acc} in-corpus pairs")
        print(f"  Refusal gate:  {total_ref} out_of_corpus_refusal pairs")
        sys.exit(0)

    acc_rate = correct_acc / total_acc if total_acc > 0 else 0.0
    ref_rate = correct_ref / total_ref if total_ref > 0 else 0.0

    acc_pct  = f"{acc_rate:.1%}"
    ref_pct  = f"{ref_rate:.1%}"
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

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

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
    result_file = RESULTS_DIR / f"gate_run_{ts}.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Result saved: {result_file}")

    if args.per_question:
        all_records = records_acc + records_ref
        pq_file = RESULTS_DIR / f"per_question_{ts}.json"
        with open(pq_file, "w", encoding="utf-8") as f:
            json.dump(all_records, f, indent=2, ensure_ascii=False)
        print(f"Per-question results saved: {pq_file} ({len(all_records)} questions)")

    sys.exit(0 if both_pass else 1)


if __name__ == "__main__":
    main()

"""Build the Kaggle eval notebook for africa-giants accuracy gate."""
import json
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_FILE = os.path.join(ROOT, "eval", "accuracy_gate", "eval_questions_001.jsonl")
OUT_FILE  = os.path.join(ROOT, "kaggle", "africa_giants_eval.ipynb")

lines = open(EVAL_FILE, encoding="utf-8").readlines()
pairs = [json.loads(l) for l in lines]
print(f"Loaded {len(pairs)} eval questions")

eval_json_literal = json.dumps(pairs, ensure_ascii=True, indent=None)

# --------------------------------------------------------------------------
# Notebook helpers
# --------------------------------------------------------------------------

def code_cell(src):
    return {
        "cell_type": "code",
        "source": [src],
        "metadata": {},
        "outputs": [],
        "id": "a",
        "execution_count": None,
    }

def md_cell(src):
    return {"cell_type": "markdown", "source": [src], "metadata": {}, "id": "b"}


# --------------------------------------------------------------------------
# Cell sources
# --------------------------------------------------------------------------

CELL_AUTH = """import os, json, re, sys, subprocess
from datetime import datetime, timezone

try:
    import kaggle_secrets
    us = kaggle_secrets.UserSecretsClient()
    hf_token = us.get_secret("AFRICA_GIANTS")
    print(f"[auth] HF token loaded ({hf_token[:8]}...)")
except Exception as e:
    hf_token = os.environ.get("HF_TOKEN", "")
    print(f"[auth] fallback env HF_TOKEN: {hf_token[:8] if hf_token else 'MISSING'}")

BASE_MODEL   = "McGill-NLP/AfriqueLlama-8B"
ADAPTER_REPO = "prospaprospa007/africa-giants-adapter-v1"
ACCURACY_THRESHOLD = 0.85
REFUSAL_THRESHOLD  = 0.70
MAX_NEW_TOKENS     = 256
print("[config] done")
"""

CELL_INSTALL = """ret = subprocess.run(
    "pip install -q 'transformers>=4.43.0' peft accelerate bitsandbytes 2>&1 | tail -5",
    shell=True, capture_output=True, text=True
)
print(ret.stdout or ret.stderr)
"""

CELL_GPU = """import torch
print(f"[gpu] CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    print(f"[gpu] {p.name}  sm_{p.major}{p.minor}  {p.total_memory/1e9:.1f}GB")
"""

CELL_MODEL = """from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import torch

print("[model] Loading base model + adapter ...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=hf_token, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

bnb = BitsAndBytesConfig(
    load_in_4bit=True, bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True,
)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL, quantization_config=bnb, device_map="auto",
    token=hf_token, trust_remote_code=True,
)
model = PeftModel.from_pretrained(base_model, ADAPTER_REPO, token=hf_token)
model.eval()
print("[model] loaded OK")
"""

CELL_LOAD_QUESTIONS = f"""eval_questions = json.loads({repr(eval_json_literal)})
print(f"[eval] Loaded {{len(eval_questions)}} eval questions")
"""

CELL_SCORING = r"""SYSTEM_PROMPT = (
    "Wewe ni msaidizi wa AI wa biashara za Tanzania. "
    "Unajibu maswali kuhusu sheria za biashara, kodi, usajili wa kampuni kwa Kiswahili na Kiingereza. "
    "You are a Tanzanian business AI assistant answering questions about regulations, "
    "tax, company registration, and financial rules in Swahili and English."
)

REFUSAL_PHRASES = [
    "sina uhakika", "thibitisha na tra", "sijui", "hakuna taarifa",
    "nje ya maarifa", "i don't know", "i am not sure",
    "please verify", "confirm with tra", "wasiliana na",
]

def generate_answer(question_sw):
    prompt = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        f"{SYSTEM_PROMPT}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{question_sw}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False, temperature=1.0, repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )
    new_tokens = out[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

def extract_numbers(text):
    text = text.lower()
    nums = set()
    for m in re.findall(r'asilimia\s*(\d+(?:\.\d+)?)', text):
        nums.add(m)
    for m in re.findall(r'(\d+(?:\.\d+)?)\s*%', text):
        nums.add(m)
    for m in re.findall(r'tzs\s*([\d,]+)', text):
        nums.add(m.replace(",", ""))
    for m in re.findall(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:million|m)\b', text):
        nums.add(m.replace(",", ""))
    for m in re.findall(r'\b(\d{3,}(?:,\d+)*)\b', text):
        nums.add(m.replace(",", ""))
    return nums

def score_question(q, generated):
    gen_lower = generated.lower()
    atype     = q.get("answer_type", "")
    correct_sw = q.get("correct_answer_sw", "").lower()
    correct_en = q.get("correct_answer_en", "").lower()

    if atype == "out_of_corpus_refusal":
        return any(p in gen_lower for p in REFUSAL_PHRASES)

    if atype in ("number", "penalty"):
        correct_nums = extract_numbers(correct_sw) | extract_numbers(correct_en)
        if not correct_nums:
            return len(gen_lower) > 10
        gen_nums = extract_numbers(generated)
        return len(correct_nums & gen_nums) >= 1

    if atype == "yes_no":
        yes_sw = any(w in correct_sw for w in ["ndiyo","yes","ndio","inaweza","lazima"])
        no_sw  = any(w in correct_sw for w in ["hapana","no","haitakiwi","haihitajiki","haiwezi"])
        gen_yes = any(w in gen_lower for w in ["ndiyo","yes","ndio","inaweza","lazima"])
        gen_no  = any(w in gen_lower for w in ["hapana","no","haitakiwi","haihitajiki","haiwezi"])
        if yes_sw:
            return gen_yes
        if no_sw:
            return gen_no
        return len(gen_lower) > 10

    if atype in ("definition", "procedure"):
        words_sw = set(w for w in correct_sw.split() if len(w) > 4)
        words_en = set(w for w in correct_en.split() if len(w) > 4)
        all_words = words_sw | words_en
        if not all_words:
            return len(gen_lower) > 20
        gen_words = set(gen_lower.split())
        return len(all_words & gen_words) >= 3

    return len(gen_lower) > 20

print("[eval] Scoring functions ready")
"""

CELL_INFERENCE = """results = []
print(f"[eval] Starting inference on {len(eval_questions)} questions ...")

for i, q in enumerate(eval_questions):
    try:
        generated = generate_answer(q["question_sw"])
        passed = score_question(q, generated)
    except Exception as e:
        generated = f"ERROR: {e}"
        passed = False

    results.append({
        "id":              q["id"],
        "subdomain":       q["subdomain"],
        "answer_type":     q.get("answer_type", ""),
        "question_sw":     q["question_sw"],
        "correct_answer_sw": q["correct_answer_sw"],
        "generated":       generated,
        "pass":            passed,
    })

    if (i + 1) % 20 == 0 or i == 0:
        rp = sum(r["pass"] for r in results)
        print(f"  [{i+1}/{len(eval_questions)}] running accuracy: {rp}/{i+1} = {rp/(i+1):.1%}")

print("[eval] Inference complete")
"""

CELL_AGGREGATE = """from collections import defaultdict

subdomain_scores = defaultdict(lambda: {"pass": 0, "total": 0})
for r in results:
    subdomain_scores[r["subdomain"]]["total"] += 1
    if r["pass"]:
        subdomain_scores[r["subdomain"]]["pass"] += 1

in_corpus = [r for r in results if r["subdomain"] != "out_of_corpus"]
refusal   = [r for r in results if r["subdomain"] == "out_of_corpus"]

in_corpus_pass  = sum(r["pass"] for r in in_corpus)
in_corpus_total = len(in_corpus)
refusal_pass    = sum(r["pass"] for r in refusal)
refusal_total   = len(refusal)

in_corpus_acc = in_corpus_pass / in_corpus_total if in_corpus_total > 0 else 0
refusal_acc   = refusal_pass   / refusal_total   if refusal_total   > 0 else 0
acc_gate_pass = in_corpus_acc > 0.85
ref_gate_pass = refusal_acc   > 0.70
gate_passed   = acc_gate_pass and ref_gate_pass

print("\\n========================================")
print("AFRICA-GIANTS ACCURACY GATE RESULTS")
print("========================================")
print("\\nBy subdomain:")
for sd in sorted(subdomain_scores.keys()):
    s = subdomain_scores[sd]
    pct = s["pass"] / s["total"] if s["total"] > 0 else 0
    bar = "*" * int(pct * 20)
    print(f"  {sd:<30} {s['pass']:>3}/{s['total']:<3} = {pct:>5.1%}  {bar}")

print()
print(f"In-corpus accuracy:    {in_corpus_pass}/{in_corpus_total} = {in_corpus_acc:.1%}   >85% {'PASS' if acc_gate_pass else 'FAIL'}")
print(f"Out-of-corpus refusal: {refusal_pass}/{refusal_total} = {refusal_acc:.1%}   >70% {'PASS' if ref_gate_pass else 'FAIL'}")
print()
if gate_passed:
    print("*** GATE PASSED ***")
else:
    print("GATE FAILED — both >85% in-corpus AND >70% refusal required")
print("========================================")
"""

CELL_SAVE = """gate_result = {
    "timestamp":           datetime.now(timezone.utc).isoformat(),
    "model":               ADAPTER_REPO,
    "base_model":          BASE_MODEL,
    "in_corpus_correct":   in_corpus_pass,
    "in_corpus_total":     in_corpus_total,
    "in_corpus_accuracy":  round(in_corpus_acc, 4),
    "in_corpus_pass":      acc_gate_pass,
    "refusal_correct":     refusal_pass,
    "refusal_total":       refusal_total,
    "refusal_accuracy":    round(refusal_acc, 4),
    "refusal_pass":        ref_gate_pass,
    "gate_passed":         gate_passed,
    "by_subdomain": {
        sd: {
            "pass":     v["pass"],
            "total":    v["total"],
            "accuracy": round(v["pass"] / v["total"], 4) if v["total"] > 0 else 0,
        }
        for sd, v in sorted(subdomain_scores.items())
    },
    "per_question": results,
}

with open("/kaggle/working/gate_001_results.json", "w", encoding="utf-8") as f:
    json.dump(gate_result, f, indent=2, ensure_ascii=False)
print("[results] Saved /kaggle/working/gate_001_results.json")
"""

CELL_UPLOAD = """from huggingface_hub import HfApi
api = HfApi(token=hf_token)
api.upload_file(
    path_or_fileobj="/kaggle/working/gate_001_results.json",
    path_in_repo="gate_001_results.json",
    repo_id=ADAPTER_REPO,
    repo_type="model",
    token=hf_token,
)
print(f"[results] Uploaded gate_001_results.json to {ADAPTER_REPO}")
print("Done.")
"""

# --------------------------------------------------------------------------
# Assemble notebook
# --------------------------------------------------------------------------

nb = {
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
        "kaggle": {
            "accelerator": "nvidiaTeslaT4x2",
            "dataSources": [],
            "dockerImageVersionId": 30919,
            "isGpuEnabled": True,
            "isInternetEnabled": True,
            "language": "python",
            "sourceType": "notebook",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
    "cells": [
        md_cell("# AFRICA GIANTS — Accuracy Gate Eval\n\nLoads base model + LoRA adapter, runs inference on 200 eval questions, scores by subdomain."),
        code_cell(CELL_AUTH),
        code_cell(CELL_INSTALL),
        code_cell(CELL_GPU),
        code_cell(CELL_MODEL),
        code_cell(CELL_LOAD_QUESTIONS),
        code_cell(CELL_SCORING),
        code_cell(CELL_INFERENCE),
        code_cell(CELL_AGGREGATE),
        code_cell(CELL_SAVE),
        code_cell(CELL_UPLOAD),
    ],
}

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=True, indent=1)

print(f"Eval notebook written: {OUT_FILE}")
print(f"Cells: {len(nb['cells'])}")

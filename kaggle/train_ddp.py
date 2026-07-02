#!/usr/bin/env python3
"""
Africa Giants — DDP Training Script v12
Multi-GPU training with Unsloth + TRL — Unsloth handles multi-GPU natively
Usage: python3 train_ddp.py
"""

# ══════════════════════════════════════════════════════════
# IMPORTS
# ══════════════════════════════════════════════════════════
import os, sys, json, re, subprocess, tempfile, traceback, inspect
from datetime import datetime, timezone

# Silence non-rank-0 processes completely
if int(os.environ.get('LOCAL_RANK', 0)) != 0:
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

# Silence warnings and verbose library output
import warnings
warnings.filterwarnings('ignore')
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'

import torch

def log(msg):
    print(msg, flush=True)

log(f"[ddp] Num GPUs visible: {torch.cuda.device_count()}")

# ══════════════════════════════════════════════════════════
# GPU DETECTION — before any CUDA imports
# ══════════════════════════════════════════════════════════
smi = subprocess.run(
    ["nvidia-smi", "--query-gpu=name,compute_cap,memory.total",
     "--format=csv,noheader"],
    capture_output=True, text=True
)
if smi.returncode != 0:
    raise RuntimeError("nvidia-smi failed — no GPU available.")

parts    = [p.strip() for p in smi.stdout.strip().split(",")]
GPU_NAME = parts[0]
SM       = int(float(parts[1]) * 10)
VRAM_GB  = parts[2]
USE_UNSLOTH = SM >= 70
BF16        = False  # T4 is sm_75 — BF16 requires sm_80+

log(f"[config] GPU         : {GPU_NAME}")
log(f"[config] VRAM        : {VRAM_GB}")
log(f"[config] Compute     : sm_{SM}")
log(f"[config] USE_UNSLOTH : {USE_UNSLOTH}")
log(f"[config] BF16        : {BF16}")

# ══════════════════════════════════════════════════════════
# CONFIG — update these each version
# ══════════════════════════════════════════════════════════
SMOKE_TEST        = False
MAX_SEQ_LENGTH    = 512 if SMOKE_TEST else 2048
LOSS_THRESHOLD    = 3.0
# LoRA rank — CRITICAL: must match v8-lora which was r=64
# v11 used r=128 but warm-started from v10-lora (also r=128)
# v12 warm-starts from v8-lora which is r=64 — shapes MUST match
LORA_RANK         = 64
LORA_ALPHA        = 64

BASE_MODEL        = "McGill-NLP/AfriqueLlama-8B"
DATASET_REPO      = "prospAprospA007/africa-giants-dataset"
ADAPTER_REPO      = "prospAprospA007/africa-giants-adapter-v12"
LORA_ONLY_REPO    = "prospAprospA007/africa-giants-adapter-v12-lora"
PREV_LORA_REPO    = "prospAprospA007/africa-giants-adapter-v8-lora"  # Back to v8 — stable production baseline
# NOTE: v10-lora had a dangerous GN487A hallucination and out-of-corpus collapse
# to 30%. v11 warm-started from v10-lora and inherited those failures. v8 is the
# stable production baseline (82.1% in-corpus / 70% out-of-corpus — best gate
# scores ever). v12 warm-starts from v8-lora (r=64) so LORA_RANK MUST be 64 —
# a rank mismatch crashes at load_adapter() time. Paired with 1 epoch (v11 epoch 2
# overfit to val=0.4660) and lr=5e-5 (half of v11's 1e-4, protects v8's refusal
# behavior from being overwritten). Log clearly so there is no confusion.

log(f"[config] SMOKE_TEST    : {SMOKE_TEST}")
log(f"[config] MAX_SEQ_LENGTH: {MAX_SEQ_LENGTH}")
log(f"[config] LORA_RANK     : {LORA_RANK}")
log(f"[config] BASE_MODEL    : {BASE_MODEL}")
log(f"[config] ADAPTER_REPO  : {ADAPTER_REPO}")

# ══════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════
hf_token = os.environ.get("HF_TOKEN", "")
if not hf_token:
    # Try Kaggle secrets
    try:
        import kaggle_secrets
        us = kaggle_secrets.UserSecretsClient()
        hf_token = us.get_secret("AFRICA_GIANTS")
        log(f"[auth] HF token loaded from Kaggle secrets ({hf_token[:8]}...)")
    except Exception as e:
        log(f"[auth] Kaggle secrets failed: {e}")
if not hf_token:
    raise RuntimeError("[auth] FATAL: no HF token found. Set HF_TOKEN env var or Kaggle secret AFRICA_GIANTS.")

from huggingface_hub import login as hf_login
hf_login(token=hf_token, add_to_git_credential=False)
log("[auth] HuggingFace login complete")

# ══════════════════════════════════════════════════════════
# IMPORTS — Unsloth MUST be imported before transformers
# ══════════════════════════════════════════════════════════
if USE_UNSLOTH:
    try:
        import unsloth
        from unsloth import FastLanguageModel
        from trl import SFTTrainer, SFTConfig
        try:
            from trl import SFTConfig as _SFTConfig
            SFTConfig = _SFTConfig
        except ImportError:
            SFTConfig = None
        from transformers import TrainingArguments
        log("[imports] Unsloth + TRL loaded")
    except Exception as e:
        log(f"[imports] Unsloth failed: {e} — falling back to BitsAndBytes")
        USE_UNSLOTH = False

if not USE_UNSLOTH:
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM,
        BitsAndBytesConfig, TrainingArguments
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
    try:
        from trl import SFTConfig
    except ImportError:
        SFTConfig = None
    log("[imports] BitsAndBytes fallback loaded")

from datasets import load_dataset
from huggingface_hub import HfApi
import logging
logging.getLogger('huggingface_hub').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
log("[imports] complete")

# ══════════════════════════════════════════════════════════
# MODEL LOAD
# ══════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"[v12] STEP: MODEL LOADING")
print(f"{'='*50}")
log(f"[model] Loading from: {BASE_MODEL}")

if USE_UNSLOTH:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name    = BASE_MODEL,
        max_seq_length= MAX_SEQ_LENGTH,
        dtype         = None,
        load_in_4bit  = True,
        token         = hf_token,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r              = LORA_RANK,
        target_modules = ["q_proj","k_proj","v_proj","o_proj",
                          "gate_proj","up_proj","down_proj"],
        lora_alpha     = LORA_ALPHA,
        lora_dropout   = 0,
        bias           = "none",
        use_gradient_checkpointing = "unsloth",
        random_state   = 3407,
    )
    log(f"[model] Unsloth model + LoRA r={LORA_RANK} loaded")
else:
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        token=hf_token,
    )
    model = prepare_model_for_kbit_training(model)
    lora_config = LoraConfig(
        r=LORA_RANK, lora_alpha=LORA_ALPHA,
        lora_dropout=0, bias="none",
        target_modules=["q_proj","k_proj","v_proj","o_proj",
                        "gate_proj","up_proj","down_proj"],
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    log(f"[model] BitsAndBytes model + LoRA r={LORA_RANK} loaded")

log(f"[model] tokenizer eos_token: {repr(tokenizer.eos_token)}")
log(f"[model] tokenizer eos_token_id: {tokenizer.eos_token_id}")

# ══════════════════════════════════════════════════════════
# LOAD PREVIOUS LORA — with explicit rank-mismatch handling
# ══════════════════════════════════════════════════════════
log(f"[model] Attempting to load {PREV_LORA_REPO} as starting point ...")
log(f"[model] NOTE: prev lora (v8-lora) is r={LORA_RANK}, same as current — shapes MATCH")
log(f"[model] v12 warm-starts from v8-lora weights (fine-tune at lr=5e-5), not fresh")
try:
    model.load_adapter(
        PREV_LORA_REPO,
        adapter_name="default",
        token=hf_token,
    )
    log(f"[model] Loaded {PREV_LORA_REPO} successfully — v8 warm-start OK ✓")
except Exception as e:
    if "size mismatch" in str(e).lower() or "shape" in str(e).lower():
        log(f"[model] FATAL: rank mismatch loading v8-lora — LORA_RANK ({LORA_RANK}) "
            f"must equal v8-lora rank (64). Aborting to avoid a fresh-random run. {e}")
        raise
    else:
        log(f"[model] WARNING: load_adapter failed unexpectedly — {e}")
        log(f"[model] Continuing with fresh LoRA weights")

model.print_trainable_parameters()

# ══════════════════════════════════════════════════════════
# EOS TOKEN RESOLUTION — battle-tested across v6-v9
# ══════════════════════════════════════════════════════════
_raw_eos = tokenizer.eos_token
_PLACEHOLDER_EOS = {"<EOS_TOKEN>", "<eos>", "[EOS]", ""}
_eos_candidates = ["</s>", "<|end_of_text|>", "<|im_end|>", "<eos>", "<|eot_id|>"]

if _raw_eos and _raw_eos not in _PLACEHOLDER_EOS:
    EOS_TOKEN = _raw_eos
else:
    _eos_id = tokenizer.eos_token_id
    EOS_TOKEN = tokenizer.decode([_eos_id]) if _eos_id is not None else "</s>"
    log(f"[eos] WARNING: eos_token={repr(_raw_eos)} is placeholder — "
        f"resolved via id={_eos_id} to {repr(EOS_TOKEN)}")

log(f"[eos] EOS_TOKEN = {repr(EOS_TOKEN)}")

# Fix Rust fast tokenizer backend
_vocab = tokenizer.get_vocab()
_eos_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
log(f"[eos] convert_tokens_to_ids result: {_eos_id}")
if _eos_id is None:
    tokenizer.add_special_tokens({"eos_token": tokenizer.eos_token})
    _eos_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
    log(f"[eos] registered eos via add_special_tokens, new id: {_eos_id}")

# Vocab guard — ensure EOS is in vocab
_found_eos = next((t for t in _eos_candidates if t in _vocab), None)
if tokenizer.eos_token not in _vocab:
    if _found_eos is None:
        raise RuntimeError("[eos] FATAL: no usable EOS candidate in tokenizer vocab")
    tokenizer.eos_token = _found_eos
    tokenizer.eos_token_id = _vocab[_found_eos]
    log(f"[eos] forced eos_token to: {_found_eos}")
else:
    log(f"[eos] eos_token ok: {tokenizer.eos_token}")

assert tokenizer.eos_token in _vocab, f"[eos] {tokenizer.eos_token!r} not in vocab"

# ══════════════════════════════════════════════════════════
# SYSTEM PROMPT — must match cerebrium/main.py exactly
# ══════════════════════════════════════════════════════════
SYSTEM_PROMPT = (
    "Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. "
    "Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. "
    "Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, "
    "OSHA, SDL, PAYE, VAT kwa Kiswahili na Kiingereza. "
    "Kama swali liko nje ya mada yako sema wazi kwamba halijui "
    "na mwelekeze kwa TRA au mshauri aliyehitimu. "
    "Your name is Chike, a business adviser from Africa Giants. "
    "Tagline: Fahamu Biashara Yako, Maarifa Yako. "
    "You answer Tanzanian business, tax, and compliance questions "
    "in Swahili and English. "
    "If a question is outside your knowledge say so clearly "
    "and direct the user to TRA or a qualified adviser."
)

# ══════════════════════════════════════════════════════════
# DATASET LOAD
# ══════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"[v12] STEP: DATASET LOADING")
print(f"{'='*50}")
log(f"[data] Loading dataset from: {DATASET_REPO}")
raw_dataset = load_dataset(
    DATASET_REPO,
    data_files={"train": "train_sft.jsonl", "validation": "val_sft.jsonl"},
    token=hf_token,
)
log(raw_dataset)

_train_count = len(raw_dataset["train"])
_val_count   = len(raw_dataset["validation"])
log(f"[data] LOADED: train={_train_count}  val={_val_count}")
assert _train_count >= 2300, \
    f"FATAL: only {_train_count} train examples — expected >= 2300. Check HF repo."
log(f"[data] dataset size PASSED ({_train_count} train pairs)")

# ══════════════════════════════════════════════════════════
# FORMAT FUNCTION — reads instruction/output/system with fallbacks
# ══════════════════════════════════════════════════════════
def fmt(ex):
    inst = ex.get("instruction", "") or ex.get("question_en", "") or ex.get("question_sw", "")
    ctx  = ex.get("input", "") or ""
    out  = ex.get("output", "") or ex.get("answer_en", "") or ex.get("answer_sw", "")
    user = f"Context: {ctx}\n\n{inst}" if ctx.strip() else inst

    if USE_UNSLOTH:
        msgs = [
            {"role": "system",    "content": SYSTEM_PROMPT},
            {"role": "user",      "content": user},
            {"role": "assistant", "content": out + EOS_TOKEN},
        ]
        text = tokenizer.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=False
        )
    else:
        text = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"{SYSTEM_PROMPT}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{user}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
            f"{out}{EOS_TOKEN}"
        )
    return {"text": text}

# Apply format
train_ds = raw_dataset["train"].map(fmt, batched=False)
eval_ds  = raw_dataset["validation"].map(fmt, batched=False)
log(f"[data] Train: {len(train_ds)}  Eval: {len(eval_ds)}")

# Sentinel check — ensure no empty outputs
_sentinel_train = sum(1 for ex in train_ds if len(ex.get("text","")) < 10)
_sentinel_eval  = sum(1 for ex in eval_ds  if len(ex.get("text","")) < 10)
log(f"[data] sentinel before clean: train={_sentinel_train}  eval={_sentinel_eval}")
if _sentinel_train > 0:
    train_ds = train_ds.filter(lambda ex: len(ex.get("text","")) >= 10)
if _sentinel_eval > 0:
    eval_ds  = eval_ds.filter(lambda ex: len(ex.get("text","")) >= 10)
log(f"[data] sentinel after clean: train={len(train_ds)} eval={len(eval_ds)} (should be 0 bad)")

# Sample check
log(f"[data] sample (first 300 chars):\n{train_ds[0]['text'][:300]}")

# ══════════════════════════════════════════════════════════
# TRAINING — SFTTrainer with full retry loop
# ══════════════════════════════════════════════════════════
log(f"[train] trl version check ...")
import trl as _trl_mod
import transformers as _tf_mod
log(f"[train] trl={_trl_mod.__version__}  transformers={_tf_mod.__version__}")

# Probe SFTTrainer signature
_sft_sig_params = set(inspect.signature(SFTTrainer.__init__).parameters)
if "processing_class" in _sft_sig_params:
    _tok_kwarg = {"processing_class": tokenizer}
    log("[train] SFTTrainer tok-kwarg: processing_class")
else:
    _tok_kwarg = {"tokenizer": tokenizer}
    log("[train] SFTTrainer tok-kwarg: tokenizer")

# Pick args class
_ArgsClass = SFTConfig if SFTConfig is not None else TrainingArguments
log(f"[train] args class: {_ArgsClass.__name__}")
_args_sig_params = set(inspect.signature(_ArgsClass.__init__).parameters)
_eval_key = "eval_strategy" if "eval_strategy" in _args_sig_params else "evaluation_strategy"
log(f"[train] eval kwarg: {_eval_key}")

# Training kwargs
_base_kwargs = {
    "output_dir":                    "./outputs",
    "per_device_train_batch_size":   1,
    "gradient_accumulation_steps":   2 if SMOKE_TEST else 8,
    "warmup_steps":                  2,
    "max_steps":                     10 if SMOKE_TEST else -1,
    "num_train_epochs":              1 if SMOKE_TEST else 1,  # NOT 2 — v11 epoch 1 val=0.4111 best, epoch 2 overfit to 0.4660
    "learning_rate":                 5e-5,  # half of v11's 1e-4 — conservative, protects v8's OOC refusal behavior
    "fp16":                          not BF16,
    "bf16":                          BF16,
    "logging_steps":                 1,
    "optim":                         "adamw_8bit" if USE_UNSLOTH else "adamw_torch",
    "weight_decay":                  0.01,
    "lr_scheduler_type":             "cosine",
    "seed":                          3407,
    "report_to":                     "none",
    "save_strategy":                 "no",
    "eval_steps":                    5,
    "dataloader_pin_memory":         False,
    "gradient_checkpointing":        not USE_UNSLOTH,

    _eval_key:                       "steps",
}
_sft_specific = {
    "dataset_text_field": "text",
    "max_seq_length":     MAX_SEQ_LENGTH,
    "packing":            False,
    "dataset_num_proc":   2,
}
_args_kwargs = {k: v for k, v in {**_base_kwargs, **_sft_specific}.items()
                if k in _args_sig_params}
_sft_direct  = {k: v for k, v in _sft_specific.items()
                if k not in _args_sig_params and k in _sft_sig_params}
_nowhere     = {k: v for k, v in _sft_specific.items()
                if k not in _args_sig_params and k not in _sft_sig_params}

log(f"[train] args kwargs ({len(_args_kwargs)}): {sorted(_args_kwargs)}")
log(f"[train] SFTTrainer direct ({len(_sft_direct)}): {sorted(_sft_direct)}")
if _nowhere:
    log(f"[train] skipping (not accepted anywhere): {sorted(_nowhere)}")

assert "eos_token" not in _args_kwargs and "eos_token" not in _sft_direct, \
    "[train] eos_token must NOT be passed to SFTTrainer"

# Build args with retry
_build_args = dict(_args_kwargs)
_args_obj = None
for _attempt in range(20):
    try:
        _args_obj = _ArgsClass(**_build_args)
        log(f"[train] {_ArgsClass.__name__} built OK on attempt {_attempt + 1}")
        break
    except TypeError as _e:
        _msg = str(_e)
        _bad = _msg.split("'")[1] if _msg.count("'") >= 2 else None
        if _bad and _bad in _build_args:
            log(f"[train] removing rejected kwarg: {_bad!r}")
            _build_args.pop(_bad)
        else:
            raise
if _args_obj is None:
    raise RuntimeError("[train] Could not build args object after 20 attempts")

# CRITICAL: force eos_token=None — prevents Unsloth contamination
_args_obj.eos_token = None
log(f"[train] args.eos_token forced to None: {_args_obj.eos_token!r}")

# Monkey-patch SFTTrainer if needed (Unsloth compatibility)
try:
    from unsloth.trainer import UnslothTrainer
    _original_init = SFTTrainer.__init__
    def _patched_init(self, *args, **kwargs):
        kwargs.pop('eos_token', None)
        _original_init(self, *args, **kwargs)
    SFTTrainer.__init__ = _patched_init
    log("[patch] SFTTrainer monkey-patched for eos_token removal")
except Exception:
    pass

# Build SFTTrainer with retry
_build_tok = dict(_tok_kwarg)
_build_sft = dict(_sft_direct)
_trainer   = None
_eos_candidates_retry = ["</s>", "<|end_of_text|>", "<|im_end|>", "<eos>", "<|eot_id|>"]

for _attempt in range(20):
    _args_obj.eos_token = None
    try:
        _trainer = SFTTrainer(
            model         = model,
            train_dataset = train_ds,
            eval_dataset  = eval_ds,
            args          = _args_obj,
            **_build_tok,
            **_build_sft,
        )
        log(f"[train] SFTTrainer built OK on attempt {_attempt + 1}")
        break
    except TypeError as _e:
        _msg = str(_e)
        _bad = _msg.split("'")[1] if _msg.count("'") >= 2 else None
        if _bad and _bad in _build_sft:
            log(f"[train] removing SFT kwarg: {_bad!r}")
            _build_sft.pop(_bad)
        elif _bad and _bad in _build_tok:
            if _bad == "processing_class":
                _build_tok = {"tokenizer": tokenizer}
                log("[train] switching to tokenizer=")
            elif _bad == "tokenizer":
                _build_tok = {"processing_class": tokenizer}
                log("[train] switching to processing_class=")
            else:
                raise
        else:
            raise
    except ValueError as _e:
        if "eos_token" in str(_e).lower() or "EOS_TOKEN" in str(_e):
            log(f"[train] EOS ValueError on attempt {_attempt + 1}: {_e}")
            _args_obj.eos_token = None
            try:
                _tok_obj = _build_tok.get("processing_class") or _build_tok.get("tokenizer")
                if _tok_obj and hasattr(_tok_obj, "eos_token"):
                    _v = _tok_obj.get_vocab()
                    if _tok_obj.eos_token not in _v:
                        _real = next((t for t in _eos_candidates_retry if t in _v), None)
                        if _real:
                            _tok_obj.eos_token = _real
                            _tok_obj.eos_token_id = _v[_real]
                            log(f"[train] tokenizer eos fixed to: {_real}")
            except Exception:
                pass
        else:
            raise

if _trainer is None:
    raise RuntimeError("[train] Could not build SFTTrainer after 20 attempts")

trainer = _trainer
print(f"\n{'='*50}")
print(f"[v12] STEP: TRAINING START")
print(f"{'='*50}")
log(f"[train] Starting on {GPU_NAME} (single GPU) ...")
stats = trainer.train()
log(f"[train] Done. Runtime: {stats.metrics['train_runtime']:.1f}s")
log(f"[train] Train loss: {stats.metrics.get('train_loss', 'N/A')}")

# ══════════════════════════════════════════════════════════
# EVAL + PUSH
# ══════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"[v12] STEP: EVALUATION")
print(f"{'='*50}")
# Remove notebook progress callback if present
try:
    from transformers.utils.notebook import NotebookProgressCallback
    trainer.remove_callback(NotebookProgressCallback)
    log("[eval] Notebook progress callback removed")
except Exception as _e:
    log(f"[eval] Could not remove callback (safe to ignore): {_e}")

# Evaluate
validation_loss = None
gate_passed     = False
try:
    log("[eval] Running evaluation ...")
    eval_results    = trainer.evaluate()
    validation_loss = eval_results.get("eval_loss", None)
    if validation_loss is not None:
        gate_passed = validation_loss <= LOSS_THRESHOLD
        log(f"[eval] Val loss: {validation_loss:.4f}  threshold: {LOSS_THRESHOLD}  "
            f"→ {'PASSED ✓' if gate_passed else 'FAILED ✗'}")
    else:
        log("[eval] WARNING: eval_loss not in results — pushing anyway")
        validation_loss = 999.0
except Exception as _e:
    log(f"[eval] Evaluation failed — pushing anyway: {_e}")
    traceback.print_exc()
    validation_loss = 999.0

# Push LoRA-only adapter
print(f"\n{'='*50}")
print(f"[v12] STEP: LORA PUSH")
print(f"{'='*50}")
log(f"[lora] Pushing LoRA-only adapter to {LORA_ONLY_REPO} ...")
try:
    with tempfile.TemporaryDirectory() as tmpdir:
        model.save_pretrained(tmpdir)
        tokenizer.save_pretrained(tmpdir)
        import os as _os
        adapter_size = _os.path.getsize(_os.path.join(tmpdir, 'adapter_model.safetensors')) / 1024 / 1024
        print(f"[lora] adapter_model.safetensors: {adapter_size:.1f} MB — pushing to {LORA_ONLY_REPO}")
        HfApi().upload_folder(
            folder_path    = tmpdir,
            repo_id        = LORA_ONLY_REPO,
            repo_type      = "model",
            token          = hf_token,
            commit_message = f"adapter-v12 LoRA-only weights r={LORA_RANK} — for v13 load_adapter()",
        )
    log(f"[lora] LoRA-only pushed to {LORA_ONLY_REPO} ✓")
    log(f"[lora] For v13: model.load_adapter('{LORA_ONLY_REPO}', adapter_name='default')")
except Exception as _e:
    log(f"[lora] LoRA-only push FAILED: {_e}")
    traceback.print_exc()

# Push merged 16-bit adapter
print(f"\n{'='*50}")
print(f"[v12] STEP: MERGED PUSH")
print(f"{'='*50}")
log(f"[push] Pushing merged model to {ADAPTER_REPO} ...")
log(f"[push] Gate result: {'PASSED' if gate_passed else 'FAILED or UNKNOWN'} — pushing regardless")
try:
    if USE_UNSLOTH:
        model.push_to_hub_merged(
            ADAPTER_REPO,
            tokenizer,
            save_method = "merged_16bit",
            token       = hf_token,
        )
    else:
        model.push_to_hub(ADAPTER_REPO, token=hf_token)
        tokenizer.push_to_hub(ADAPTER_REPO, token=hf_token)
    log(f"[push] Adapter weights pushed ✓")
except Exception as _e:
    log(f"[push] PUSH FAILED: {_e}")
    traceback.print_exc()
    log("[push] Saving adapter locally to /kaggle/working/adapter_emergency_save/")
    try:
        model.save_pretrained("/kaggle/working/adapter_emergency_save/")
        tokenizer.save_pretrained("/kaggle/working/adapter_emergency_save/")
        log("[push] Emergency local save completed ✓")
    except Exception as _e2:
        log(f"[push] Emergency save also failed: {_e2}")

# Push model card
try:
    _loss_str = f"{validation_loss:.4f}" if validation_loss != 999.0 else "eval_failed"
    _gate_str = "PASSED" if gate_passed else "FAILED or eval error"
    card = f"""---
language:
- sw
- en
license: llama3.1
base_model: {BASE_MODEL}
tags:
- llama-3.1
- african-languages
- swahili
- tanzanian-business
- qlora
- {'unsloth' if USE_UNSLOTH else 'bitsandbytes'}
- peft
- lora
pipeline_tag: text-generation
datasets:
- {DATASET_REPO}
---
# Africa Giants — Chike Tanzanian Business AI (adapter-v12)
QLoRA fine-tune of [{BASE_MODEL}](https://huggingface.co/{BASE_MODEL})
on Tanzanian business, tax, company registration, and financial regulation data.
**Base model:** AfriqueLlama-8B (Llama 3.1 8B, 20 African languages incl. Swahili)
**Languages:** Swahili (sw), English (en)
**Training:** QLoRA r={LORA_RANK} on {GPU_NAME} single GPU
**Training pairs:** batch_014 dataset (train_sft.jsonl / val_sft.jsonl on {DATASET_REPO})
**Validation loss:** {_loss_str}
**Gate result:** {_gate_str}
**Started from:** v8-lora at r={LORA_RANK} (warm-start fine-tune, 1 epoch, lr=5e-5)
**LoRA-only checkpoint:** {LORA_ONLY_REPO}
"""
    HfApi().upload_file(
        path_or_fileobj=card.encode(),
        path_in_repo="README.md",
        repo_id=ADAPTER_REPO,
        repo_type="model",
        token=hf_token,
        commit_message=f"adapter-v12 model card — val_loss={_loss_str} r={LORA_RANK}",
    )
    log(f"[push] Model card pushed ✓")
except Exception as _e:
    log(f"[push] Model card push failed (non-critical): {_e}")

log(f"[push] Adapter live at: https://huggingface.co/{ADAPTER_REPO}")
log(f"[lora] LoRA adapter live at: https://huggingface.co/{LORA_ONLY_REPO}")

# ══════════════════════════════════════════════════════════
# INFERENCE TEST — after push
# ══════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"[v12] STEP: INFERENCE TEST")
print(f"{'='*50}")
log("[test] Running quick inference check ...")
try:
    if USE_UNSLOTH:
        FastLanguageModel.for_inference(model)

    from transformers import pipeline as hf_pipeline

    pipe = hf_pipeline(
        "text-generation",
        model     = model,
        tokenizer = tokenizer,
        max_new_tokens     = 300,
        temperature        = 0.1,
        do_sample          = True,
        repetition_penalty = 1.3,
    )

    test_questions = [
        "Kiwango cha VAT nchini Tanzania ni kiasi gani?",
        "SDL ni nini na nani analazimika kulipa?",
        "Je, biashara yangu lazima isajiliwe na BRELA?",
    ]

    for q in test_questions:
        prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"{SYSTEM_PROMPT}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{q}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )
        result = pipe(prompt)[0]["generated_text"]
        answer = result[len(prompt):]
        log(f"\nQ: {q}")
        log(f"A: {answer[:300]}")
        log("-" * 60)

    log("[test] Inference check complete.")
    log("[test] If answers look reasonable run the accuracy gate next.")
except Exception as _e:
    log(f"[test] Inference check failed (non-critical): {_e}")
    traceback.print_exc()

log("[done] train_ddp.py complete.")

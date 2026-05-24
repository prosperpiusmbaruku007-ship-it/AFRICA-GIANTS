"""
Rewrites cell-imports and cell-train in the notebook with a fully defensive
SFTTrainer build that handles any TRL / transformers version at runtime.
Uses inspect.signature to route kwargs correctly + try/except loops as final
safety net so no single deprecated arg can crash training.
"""
import json, sys

NB_SRC  = r"C:\Users\jhjh\AFRICA-GIANTS\notebooks\kaggle_train_arque_llama.ipynb"
NB_DEST = r"C:\Users\jhjh\AFRICA-GIANTS\notebooks\kaggle_train_arque_llama.ipynb"
KG_DEST = r"C:\Users\jhjh\AFRICA-GIANTS\kaggle\kaggle_train_arque_llama.ipynb"

# ── New cell-imports source ────────────────────────────────────────────────────
NEW_IMPORTS = """\
# ── Step 3: Imports – conditional on GPU path ───────────────────────────────────
print("[imports] starting ...")

import os, torch
print(f"[imports] torch {torch.__version__}")

from datasets import load_dataset
from transformers import TrainingArguments
print("[imports] transformers/datasets OK")

from trl import SFTTrainer
try:
    from trl import SFTConfig
    print("[imports] trl SFTTrainer + SFTConfig OK")
except ImportError:
    SFTConfig = None
    print("[imports] trl SFTTrainer OK (SFTConfig not available, falling back to TrainingArguments)")

from huggingface_hub import HfApi, create_repo, login, whoami
print("[imports] huggingface_hub OK")

if USE_UNSLOTH:
    print("[imports] loading unsloth ...")
    from unsloth import FastLanguageModel, is_bfloat16_supported

    try:
        from unsloth.chat_templates import get_chat_template
        print("[imports] get_chat_template from unsloth.chat_templates")
    except ImportError:
        from unsloth import get_chat_template
        print("[imports] get_chat_template from unsloth (new path)")

    BF16 = is_bfloat16_supported()
    print("[imports] unsloth OK")
else:
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    BF16 = False
    print("[imports] BitsAndBytes path imports OK")

print(f"[imports] torch      : {torch.__version__}")
print(f"[imports] GPU        : {torch.cuda.get_device_name(0)}  sm_{SM}")
print(f"[imports] BF16       : {BF16}")
print("[imports] done")
"""

# ── New cell-train source ──────────────────────────────────────────────────────
NEW_TRAIN = """\
# ── Train ─────────────────────────────────────────────────────────────────────────────
# Defensive build: inspect.signature probes accepted params at runtime,
# then try/except loops strip any remaining unknown kwargs one by one.
# Handles TRL 0.8 through 0.15+ and any transformers version.
import inspect
import trl as _trl_mod
import transformers as _tf_mod

print(f"[train] trl={_trl_mod.__version__}  transformers={_tf_mod.__version__}")

# ── 1. Probe SFTTrainer signature ────────────────────────────────────────────────────
_sft_sig_params = set(inspect.signature(SFTTrainer.__init__).parameters)

# TRL >= 0.12: tokenizer param renamed to processing_class
if "processing_class" in _sft_sig_params:
    _tok_kwarg = {"processing_class": tokenizer}
    print("[train] SFTTrainer tok-kwarg: processing_class")
else:
    _tok_kwarg = {"tokenizer": tokenizer}
    print("[train] SFTTrainer tok-kwarg: tokenizer")

# ── 2. Pick args class: SFTConfig (TRL>=0.10) or TrainingArguments ──────────────
_ArgsClass = SFTConfig if SFTConfig is not None else TrainingArguments
print(f"[train] args class: {_ArgsClass.__name__}")
_args_sig_params = set(inspect.signature(_ArgsClass.__init__).parameters)

# transformers < 4.36 uses evaluation_strategy; 4.36+ renamed it to eval_strategy
_eval_key = "eval_strategy" if "eval_strategy" in _args_sig_params else "evaluation_strategy"
print(f"[train] eval kwarg: {_eval_key}")

# ── 3. All desired training kwargs ───────────────────────────────────────────────────
_base_kwargs = {
    "output_dir": "./outputs",
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 2 if SMOKE_TEST else 4,
    "warmup_steps": 2,
    "max_steps": 10 if SMOKE_TEST else -1,
    "num_train_epochs": 1 if SMOKE_TEST else 3,
    "learning_rate": 2e-4,
    "fp16": not BF16,
    "bf16": BF16,
    "logging_steps": 1,
    "optim": "adamw_8bit" if USE_UNSLOTH else "adamw_torch",
    "weight_decay": 0.01,
    "lr_scheduler_type": "cosine",
    "seed": 3407,
    "report_to": "none",
    "save_strategy": "no",
    "eval_steps": 5,
    "dataloader_pin_memory": False,
    "gradient_checkpointing": not USE_UNSLOTH,
    _eval_key: "steps",
}

# SFT-specific kwargs (may live in SFTConfig or SFTTrainer depending on version)
_sft_specific = {
    "dataset_text_field": "text",
    "max_seq_length": MAX_SEQ_LENGTH,
    "packing": False,
    "dataset_num_proc": 2,
}

# Route: args class first; anything it rejects, try SFTTrainer directly
_args_kwargs = {k: v for k, v in {**_base_kwargs, **_sft_specific}.items()
               if k in _args_sig_params}
_sft_direct  = {k: v for k, v in _sft_specific.items()
               if k not in _args_sig_params and k in _sft_sig_params}
_nowhere     = {k: v for k, v in _sft_specific.items()
               if k not in _args_sig_params and k not in _sft_sig_params}
print(f"[train] args class kwargs ({len(_args_kwargs)}): {sorted(_args_kwargs)}")
print(f"[train] SFTTrainer direct kwargs ({len(_sft_direct)}): {sorted(_sft_direct)}")
if _nowhere:
    print(f"[train] WARNING: not accepted anywhere, skipping: {sorted(_nowhere)}")

# ── 4. Build args object with try/except loop as safety net ─────────────────────
_build_args = dict(_args_kwargs)
_args_obj = None
for _attempt in range(20):
    try:
        _args_obj = _ArgsClass(**_build_args)
        print(f"[train] {_ArgsClass.__name__} built OK on attempt {_attempt + 1}")
        break
    except TypeError as _e:
        _msg = str(_e)
        _bad = _msg.split("'")[1] if _msg.count("'") >= 2 else None
        if _bad and _bad in _build_args:
            print(f"[train] WARNING: {_ArgsClass.__name__} rejected {_bad!r} -- removing and retrying")
            _build_args.pop(_bad)
        else:
            print(f"[train] FATAL: {_ArgsClass.__name__} TypeError not fixable: {_e}")
            raise
if _args_obj is None:
    raise RuntimeError("[train] Could not build args object after 20 attempts")

# ── 5. Build SFTTrainer with try/except loop as safety net ────────────────────
_build_tok  = dict(_tok_kwarg)
_build_sft  = dict(_sft_direct)
_trainer = None
for _attempt in range(20):
    try:
        _trainer = SFTTrainer(
            model=model,
            train_dataset=train_ds,
            eval_dataset=eval_ds,
            args=_args_obj,
            **_build_tok,
            **_build_sft,
        )
        print(f"[train] SFTTrainer built OK on attempt {_attempt + 1}")
        break
    except TypeError as _e:
        _msg = str(_e)
        _bad = _msg.split("'")[1] if _msg.count("'") >= 2 else None
        if _bad and _bad in _build_sft:
            print(f"[train] WARNING: SFTTrainer rejected {_bad!r} -- removing and retrying")
            _build_sft.pop(_bad)
        elif _bad and _bad in _build_tok:
            # tokenizer kwarg rejected -- flip to the other name
            if _bad == "processing_class":
                _build_tok = {"tokenizer": tokenizer}
                print("[train] WARNING: processing_class rejected, switching to tokenizer=")
            elif _bad == "tokenizer":
                _build_tok = {"processing_class": tokenizer}
                print("[train] WARNING: tokenizer= rejected, switching to processing_class=")
            else:
                print(f"[train] FATAL: SFTTrainer TypeError not fixable: {_e}")
                raise
        else:
            print(f"[train] FATAL: SFTTrainer TypeError not fixable: {_e}")
            raise
if _trainer is None:
    raise RuntimeError("[train] Could not build SFTTrainer after 20 attempts")

trainer = _trainer
print(f"[train] Starting on {GPU_NAME} via {'Unsloth' if USE_UNSLOTH else 'BitsAndBytes'} ...")
stats = trainer.train()
print(f"[train] Done. Runtime: {stats.metrics['train_runtime']:.1f}s")
"""

# ── Read notebook ──────────────────────────────────────────────────────────────
with open(NB_SRC, encoding="utf-8") as f:
    nb = json.load(f)

def set_cell_source(nb, cell_id, new_source_str):
    """Replace a cell's source, preserving whatever list/string format Jupyter uses."""
    for cell in nb["cells"]:
        if cell.get("id") == cell_id:
            old_src = cell["source"]
            if isinstance(old_src, list):
                # Split into lines keeping the newline on each line except the last
                lines = new_source_str.splitlines(keepends=True)
                cell["source"] = lines
            else:
                cell["source"] = new_source_str
            print(f"  updated {cell_id}: {len(cell['source'])} source lines")
            return True
    print(f"  WARNING: cell '{cell_id}' not found", file=sys.stderr)
    return False

print("Patching cells ...")
set_cell_source(nb, "cell-imports", NEW_IMPORTS.strip())
set_cell_source(nb, "cell-train",   NEW_TRAIN.strip())

# ── Write notebooks/ copy ──────────────────────────────────────────────────────
with open(NB_DEST, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=True, indent=1)
print(f"Written: {NB_DEST}")

# ── Write kaggle/ copy ─────────────────────────────────────────────────────────
with open(KG_DEST, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=True, indent=1)
print(f"Written: {KG_DEST}")

print("Done.")

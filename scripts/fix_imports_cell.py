import json

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

with open(r"C:\Users\jhjh\AFRICA-GIANTS\notebooks\kaggle_train_arque_llama.ipynb", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell.get("id") == "cell-imports":
        cell["source"] = NEW_IMPORTS.strip().splitlines(keepends=True)
        print(f"cell-imports rewritten: {len(cell['source'])} lines")
        break

for dest in (
    r"C:\Users\jhjh\AFRICA-GIANTS\notebooks\kaggle_train_arque_llama.ipynb",
    r"C:\Users\jhjh\AFRICA-GIANTS\kaggle\kaggle_train_arque_llama.ipynb",
):
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=True, indent=1)
    print(f"Written: {dest}")

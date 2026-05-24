"""Remove stale get_chat_template references from cell-data comment block."""
import json

NB   = r"C:\Users\jhjh\AFRICA-GIANTS\notebooks\kaggle_train_arque_llama.ipynb"
KG   = r"C:\Users\jhjh\AFRICA-GIANTS\kaggle\kaggle_train_arque_llama.ipynb"

NEW_DATA_HEADER = """\
# ── Dataset ──────────────────────────────────���────────────────────────────────
raw_dataset = load_dataset(DATASET_REPO, token=hf_token)
print(raw_dataset)

SYSTEM_PROMPT = (
    "Wewe ni msaidizi wa AI wa biashara za Tanzania. "
    "Unajibu maswali kuhusu sheria za biashara, kodi, usajili wa kampuni kwa Kiswahili na Kiingereza. "
    "You are a Tanzanian business AI assistant answering questions about regulations, "
    "tax, company registration, and financial rules in Swahili and English."
)

# AfriqueLlama has its own tokenizer -- read EOS from it directly.
# Decode from eos_token_id if the string value is None or a placeholder.
_raw_eos = tokenizer.eos_token
_PLACEHOLDER_EOS = {"<EOS_TOKEN>", "<eos>", "[EOS]", ""}
if _raw_eos and _raw_eos not in _PLACEHOLDER_EOS:
    EOS_TOKEN = _raw_eos
else:
    _eos_id = tokenizer.eos_token_id
    EOS_TOKEN = tokenizer.decode([_eos_id]) if _eos_id is not None else "</s>"
    print(f"[data] WARNING: eos_token={repr(_raw_eos)} is placeholder -- "
          f"resolved via id={_eos_id} to {repr(EOS_TOKEN)}")
print(f"[data] EOS_TOKEN = {repr(EOS_TOKEN)}")

def fmt(ex):
    inst = ex.get("instruction", "")
    ctx  = ex.get("input", "") or ""
    out  = ex.get("output", "")
    user = f"Context: {ctx}\\n\\n{inst}" if ctx.strip() else inst
    if USE_UNSLOTH:
        msgs = [
            {"role": "system",    "content": SYSTEM_PROMPT},
            {"role": "user",      "content": user},
            {"role": "assistant", "content": out},
        ]
        text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
        if not text.endswith(EOS_TOKEN):
            text = text + EOS_TOKEN
    else:
        text = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\\n\\n"
            f"{SYSTEM_PROMPT}{EOS_TOKEN}"
            f"<|start_header_id|>user<|end_header_id|>\\n\\n"
            f"{user}{EOS_TOKEN}"
            f"<|start_header_id|>assistant<|end_header_id|>\\n\\n"
            f"{out}{EOS_TOKEN}"
        )
    return {"text": text}

train_ds = raw_dataset["train"].map(fmt, batched=False)
val_src  = raw_dataset.get("validation") or raw_dataset["train"].select(range(min(10, len(raw_dataset["train"]))))
eval_ds  = val_src.map(fmt, batched=False)
print(f"Train: {len(train_ds)}  Eval: {len(eval_ds)}")
"""

with open(NB, encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell.get("id") == "cell-data":
        cell["source"] = NEW_DATA_HEADER.strip().splitlines(keepends=True)
        print(f"cell-data rewritten: {len(cell['source'])} lines")
        break

for dest in (NB, KG):
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=True, indent=1)
    print(f"Written: {dest}")

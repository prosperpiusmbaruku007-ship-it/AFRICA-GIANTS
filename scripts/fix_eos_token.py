"""
Patches cell-data: replaces all hard-coded <|eot_id|> tokens with
tokenizer.eos_token so AfriqueLlama's actual EOS is used instead of
the standard Llama-3.1 value.
"""
import json, sys

NB_SRC  = r"C:\Users\jhjh\AFRICA-GIANTS\notebooks\kaggle_train_arque_llama.ipynb"
KG_DEST = r"C:\Users\jhjh\AFRICA-GIANTS\kaggle\kaggle_train_arque_llama.ipynb"

NEW_DATA = """\
# ── Dataset ───────────────────────────────────────────────────────────────────
raw_dataset = load_dataset(DATASET_REPO, token=hf_token)
print(raw_dataset)

SYSTEM_PROMPT = (
    "Wewe ni msaidizi wa AI wa biashara za Tanzania. "
    "Unajibu maswali kuhusu sheria za biashara, kodi, usajili wa kampuni kwa Kiswahili na Kiingereza. "
    "You are a Tanzanian business AI assistant answering questions about regulations, "
    "tax, company registration, and financial rules in Swahili and English."
)

# AfriqueLlama uses a different EOS token than standard Llama-3.1 -- always
# read from the tokenizer rather than hard-coding <|eot_id|> or </s>.
EOS_TOKEN = tokenizer.eos_token
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
        # apply_chat_template uses the model's own template + correct EOS
        text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
        # Ensure the sequence ends with EOS (some versions omit it)
        if not text.endswith(EOS_TOKEN):
            text = text + EOS_TOKEN
    else:
        # Manual template for the BitsAndBytes path -- use tokenizer.eos_token,
        # not the hard-coded <|eot_id|> which is Llama-3.1-specific.
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

with open(NB_SRC, encoding="utf-8") as f:
    nb = json.load(f)

patched = False
for cell in nb["cells"]:
    if cell.get("id") == "cell-data":
        src = cell["source"]
        if isinstance(src, list):
            cell["source"] = NEW_DATA.strip().splitlines(keepends=True)
        else:
            cell["source"] = NEW_DATA.strip()
        print(f"  patched cell-data: {len(cell['source'])} lines")
        patched = True
        break

if not patched:
    print("ERROR: cell-data not found", file=sys.stderr)
    sys.exit(1)

for dest in (NB_SRC, KG_DEST):
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=True, indent=1)
    print(f"  written: {dest}")

print("Done.")

"""
Hardens EOS token handling:
- cell-model: logs eos_token before/after get_chat_template call
- cell-data:  adds guard — if eos_token is None or a placeholder string,
              falls back to the actual vocabulary token by ID
"""
import json, sys

NB_SRC  = r"C:\Users\jhjh\AFRICA-GIANTS\notebooks\kaggle_train_arque_llama.ipynb"
KG_DEST = r"C:\Users\jhjh\AFRICA-GIANTS\kaggle\kaggle_train_arque_llama.ipynb"

# ── New cell-model ─────────────────────────────────────────────────────────────
NEW_MODEL = """\
# ── Load model ────────────────────────────────────────────────────────────────
if USE_UNSLOTH:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,
        load_in_4bit=True,
        token=hf_token,
        device_map={'': torch.cuda.current_device()},
    )
    print(f"[model] eos_token BEFORE get_chat_template: {repr(tokenizer.eos_token)}")
    tokenizer = get_chat_template(tokenizer, chat_template="llama-3.1")
    print(f"[model] eos_token AFTER  get_chat_template: {repr(tokenizer.eos_token)}")
    print(f"[model] eos_token_id: {tokenizer.eos_token_id}")
    model = FastLanguageModel.get_peft_model(
        model, r=16, lora_alpha=32, lora_dropout=0.05,
        target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
        bias="none", use_gradient_checkpointing="unsloth", random_state=3407,
    )
else:
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=hf_token, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    print(f"[model] eos_token (BitsAndBytes path): {repr(tokenizer.eos_token)}")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, quantization_config=bnb_config,
        device_map={'': torch.cuda.current_device()},
        token=hf_token, trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05,
        target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
        bias="none", task_type="CAUSAL_LM",
    ))

model.print_trainable_parameters()
print(f"Loaded {BASE_MODEL} via {'Unsloth' if USE_UNSLOTH else 'BitsAndBytes'}")
"""

# ── New cell-data ──────────────────────────────────────────────────────────────
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

# ── Resolve EOS token safely ───────────────────────────────────────────────────
# AfriqueLlama uses a different EOS than standard Llama-3.1.
# get_chat_template() may remap tokenizer.eos_token to a placeholder like
# "<EOS_TOKEN>" -- guard against that by resolving from the vocabulary by ID.
_raw_eos = tokenizer.eos_token
_PLACEHOLDER_EOS = {"<EOS_TOKEN>", "<eos>", "[EOS]", ""}
if _raw_eos and _raw_eos not in _PLACEHOLDER_EOS:
    EOS_TOKEN = _raw_eos
else:
    # Decode from the actual eos_token_id so we get the real token string
    _eos_id = tokenizer.eos_token_id
    EOS_TOKEN = tokenizer.decode([_eos_id]) if _eos_id is not None else "</s>"
    print(f"[data] WARNING: tokenizer.eos_token={repr(_raw_eos)} looks like a placeholder -- "
          f"resolved via eos_token_id={_eos_id} to {repr(EOS_TOKEN)}")
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
        # Manual template -- use resolved EOS_TOKEN, never a hard-coded string
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

# ── Apply patches ──────────────────────────────────────────────────────────────
with open(NB_SRC, encoding="utf-8") as f:
    nb = json.load(f)

patched = set()
for cell in nb["cells"]:
    cid = cell.get("id", "")
    if cid == "cell-model":
        src = NEW_MODEL.strip().splitlines(keepends=True)
        cell["source"] = src if isinstance(cell["source"], list) else NEW_MODEL.strip()
        print(f"  patched cell-model: {len(cell['source'])} lines")
        patched.add(cid)
    elif cid == "cell-data":
        src = NEW_DATA.strip().splitlines(keepends=True)
        cell["source"] = src if isinstance(cell["source"], list) else NEW_DATA.strip()
        print(f"  patched cell-data:  {len(cell['source'])} lines")
        patched.add(cid)

for expected in ("cell-model", "cell-data"):
    if expected not in patched:
        print(f"ERROR: {expected} not found", file=sys.stderr)
        sys.exit(1)

for dest in (NB_SRC, KG_DEST):
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=True, indent=1)
    print(f"  written: {dest}")

print("Done.")

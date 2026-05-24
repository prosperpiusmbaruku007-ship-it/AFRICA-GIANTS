"""
Patches cell-model: replaces device_map="auto" with
device_map={'': torch.cuda.current_device()} in both the
FastLanguageModel and AutoModelForCausalLM paths.
"""
import json, sys

NB_SRC  = r"C:\Users\jhjh\AFRICA-GIANTS\notebooks\kaggle_train_arque_llama.ipynb"
KG_DEST = r"C:\Users\jhjh\AFRICA-GIANTS\kaggle\kaggle_train_arque_llama.ipynb"

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
    tokenizer = get_chat_template(tokenizer, chat_template="llama-3.1")
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
print(f"[model] device_map={{'': torch.cuda.current_device()}}  GPU={torch.cuda.get_device_name(0)}")
"""

with open(NB_SRC, encoding="utf-8") as f:
    nb = json.load(f)

patched = False
for cell in nb["cells"]:
    if cell.get("id") == "cell-model":
        src = cell["source"]
        if isinstance(src, list):
            cell["source"] = NEW_MODEL.strip().splitlines(keepends=True)
        else:
            cell["source"] = NEW_MODEL.strip()
        print(f"  patched cell-model: {len(cell['source'])} lines")
        patched = True
        break

if not patched:
    print("ERROR: cell-model not found", file=sys.stderr)
    sys.exit(1)

for dest in (NB_SRC, KG_DEST):
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=True, indent=1)
    print(f"  written: {dest}")

print("Done.")

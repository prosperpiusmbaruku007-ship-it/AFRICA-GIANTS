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
# -- THE COMPLETE FIX Step 1 (PROGRESS.md CURRENT BLOCKER) --------------
# Unsloth wraps the tokenizer and breaks convert_tokens_to_ids on Kaggle
# with AfriqueLlama-8B. Reload the raw HuggingFace tokenizer so the
# Rust-backend lookup that TRL sft_trainer.py line 630 performs returns
# a real id instead of None. The model object stays Unsloth-wrapped --
# only the tokenizer is replaced.
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    token=hf_token,
)
tokenizer.pad_token = tokenizer.eos_token
print(f"[fix] reloaded raw tokenizer: {tokenizer.__class__.__name__}")
print(f"[fix] eos_token: {tokenizer.eos_token}")
print(f"[fix] convert check: {tokenizer.convert_tokens_to_ids(tokenizer.eos_token)}")
assert tokenizer.convert_tokens_to_ids(tokenizer.eos_token) is not None, \
    "FATAL: convert_tokens_to_ids still returns None after reload"

model.print_trainable_parameters()
print(f"Loaded {BASE_MODEL} via {'Unsloth' if USE_UNSLOTH else 'BitsAndBytes'}")

# -- FIX ATTEMPT 2: convert_tokens_to_ids diagnostic (PROGRESS.md) -----
_test_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
print(f"[eos] convert_tokens_to_ids('<|end_of_text|>'): {_test_id}")
print(f"[eos] tokenizer.eos_token_id: {tokenizer.eos_token_id}")
print(f"[eos] are they equal: {_test_id == tokenizer.eos_token_id}")
if _test_id is None:
    print("[eos] CONFIRMED BUG: convert returns None despite token in vocab")
    print(f"[eos] special tokens: {tokenizer.all_special_tokens[:10]}")
    print(f"[eos] special ids: {tokenizer.all_special_ids[:10]}")

# ── EOS fix: ensure eos_token is a real vocab token ──────────────────────────
_vocab = tokenizer.get_vocab()
_eos_candidates = ["</s>", "<|end_of_text|>", "<|im_end|>", "<eos>", "<|eot_id|>"]
_found = next((t for t in _eos_candidates if t in _vocab), None)
if _found and tokenizer.eos_token not in _vocab:
    tokenizer.eos_token = _found
    tokenizer.eos_token_id = _vocab[_found]
    print(f"[fix] eos_token set to: {_found}")
else:
    print(f"[fix] eos_token ok: {tokenizer.eos_token}")
print(f"[vocab] sample: {list(_vocab.keys())[:50]}")
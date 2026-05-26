# -- Dataset -----------------------------------------------------------------
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

# -- EOS registration (PROGRESS.md FINAL CONFIRMED CAUSE) ------------------
# Fast tokenizer Rust backend may not recognize eos_token via
# convert_tokens_to_ids even when it exists in get_vocab(). Register it
# via add_special_tokens so TRL line 630 lookup succeeds.
_eos_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
print(f"[eos] convert_tokens_to_ids result: {_eos_id}")
if _eos_id is None:
    tokenizer.add_special_tokens({"eos_token": tokenizer.eos_token})
    print(f"[eos] registered eos via add_special_tokens")
    _eos_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
    print(f"[eos] convert_tokens_to_ids after fix: {_eos_id}")

def fmt(ex):
    inst = ex.get("instruction", "")
    ctx  = ex.get("input", "") or ""
    out  = ex.get("output", "")
    user = f"Context: {ctx}\n\n{inst}" if ctx.strip() else inst
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
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"{SYSTEM_PROMPT}{EOS_TOKEN}"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{user}{EOS_TOKEN}"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
            f"{out}{EOS_TOKEN}"
        )
    return {"text": text}

train_ds = raw_dataset["train"].map(fmt, batched=False)
val_src  = raw_dataset.get("validation") or raw_dataset["train"].select(range(min(10, len(raw_dataset["train"]))))
eval_ds  = val_src.map(fmt, batched=False)
print(f"Train: {len(train_ds)}  Eval: {len(eval_ds)}")

# -- Clean dataset text: strip any literal '<EOS_TOKEN>' from rendered text -
# Defensive sweep: ensures no example's text column contains the sentinel
# (could come from apply_chat_template output, raw dataset content, etc.).
def clean_eos(example):
    example["text"] = example["text"].replace("<EOS_TOKEN>", tokenizer.eos_token)
    return example

_train_hits = sum(1 for ex in train_ds if "<EOS_TOKEN>" in ex["text"])
_eval_hits  = sum(1 for ex in eval_ds  if "<EOS_TOKEN>" in ex["text"])
print(f"[data] '<EOS_TOKEN>' literal in dataset text BEFORE clean: "
      f"train={_train_hits}/{len(train_ds)}  eval={_eval_hits}/{len(eval_ds)}")

train_ds = train_ds.map(clean_eos)
eval_ds  = eval_ds.map(clean_eos)

_train_hits_after = sum(1 for ex in train_ds if "<EOS_TOKEN>" in ex["text"])
_eval_hits_after  = sum(1 for ex in eval_ds  if "<EOS_TOKEN>" in ex["text"])
print(f"[data] '<EOS_TOKEN>' literal in dataset text AFTER clean:  "
      f"train={_train_hits_after}/{len(train_ds)}  eval={_eval_hits_after}/{len(eval_ds)}")
print(f"[data] cleaned EOS in dataset -- sample (first 300 chars):")
print(train_ds[0]["text"][:300])

# -- TRL monkey-patch: ONLY fix sentinel pollution, never set None args.eos -
# Per TRL 0.24.0 sft_trainer.py line 628: vocab validation only runs when
# args.eos_token is not None. We INTENTIONALLY leave args.eos_token == None
# in cell-train so TRL skips validation. This patch is defensive depth:
# - If tokenizer.eos_token is somehow not in vocab, fix it.
# - If something else has set args.eos_token to the literal sentinel
#   "<EOS_TOKEN>", strip it back to None so TRL skips validation.
# - Never overwrite args.eos_token when it is None.
import trl.trainer.sft_trainer as _sft_mod

_orig_init = _sft_mod.SFTTrainer.__init__

def _patched_init(self, *args, **kwargs):
    # Newer TRL: processing_class=; older TRL: tokenizer=
    pc = kwargs.get('processing_class', None) or kwargs.get('tokenizer', None)
    if pc is not None and hasattr(pc, 'eos_token'):
        try:
            _vocab = pc.get_vocab()
        except Exception:
            _vocab = {}
        if pc.eos_token not in _vocab:
            _candidates = ["</s>", "<|end_of_text|>", "<|im_end|>", "<eos>", "<|eot_id|>"]
            _real = next((t for t in _candidates if t in _vocab), None)
            if _real:
                pc.eos_token = _real
                pc.eos_token_id = _vocab[_real]
                print(f"[patch] tokenizer eos fixed: {_real}")
    # Strip sentinel-only -- do NOT touch args.eos_token when it is None
    _args = kwargs.get('args', None)
    if _args is not None and getattr(_args, 'eos_token', None) == "<EOS_TOKEN>":
        print(f"[patch] args.eos_token sentinel stripped -> None")
        _args.eos_token = None
    return _orig_init(self, *args, **kwargs)

_sft_mod.SFTTrainer.__init__ = _patched_init
print("[patch] SFTTrainer.__init__ monkey-patched for EOS token fixup")

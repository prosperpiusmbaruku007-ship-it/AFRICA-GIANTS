# FIX-EOS COMMAND — DEFINITIVE EOS TOKEN FIX
# Run this whenever EOS token error appears in Kaggle logs

## THE ERROR
ValueError: The specified eos_token ('<EOS_TOKEN>') is not 
found in vocabulary of TokenizersBackend

## CONFIRMED FACTS — DO NOT RE-INVESTIGATE
- tokenizer.eos_token = <|end_of_text|> correct
- tokenizer.eos_token_id = 128001 correct
- SFTConfig.eos_token = None correct
- eos_token NOT in _base_kwargs correct
- convert_tokens_to_ids returns 128001 after hardcode fix
- Old cached kernel 2510264585 was the source of confusion
- New kernel 648585292 is the correct one running now
- TRL still reads '<EOS_TOKEN>' despite all tokenizer fixes
- Source is likely chat_template or model config

## COMPLETE FIX — ADD ALL OF THESE before SFTTrainer for loop

Save to scripts/fixed_cell_train.py for manual Kaggle paste:

# ── COMPLETE EOS FIX ─────────────────────────────────────────────────────
# Fix 1: Force tokenizer eos_token
tokenizer.eos_token = "<|end_of_text|>"
tokenizer.eos_token_id = 128001
tokenizer.add_special_tokens({"eos_token": "<|end_of_text|>"})
print(f"[eos] hardcoded: {tokenizer.convert_tokens_to_ids('<|end_of_text|>')}")

# Fix 2: Clear chat template — TRL may call apply_chat_template
# internally and inject <EOS_TOKEN> from incomplete template
tokenizer.chat_template = None
print("[fix] chat_template cleared")

# Fix 3: Force model config eos_token_id
print(f"[cfg] model.config.eos_token_id before: {getattr(model.config, 'eos_token_id', 'absent')}")
if hasattr(model.config, 'eos_token_id'):
    model.config.eos_token_id = 128001
if hasattr(model, 'generation_config') and hasattr(model.generation_config, 'eos_token_id'):
    model.generation_config.eos_token_id = 128001
print("[cfg] model eos_token_id forced to 128001")

# Fix 4: Clean dataset text of any <EOS_TOKEN> strings
train_ds = train_ds.map(lambda x: {"text": x["text"].replace("<EOS_TOKEN>", "<|end_of_text|>")})
eval_ds = eval_ds.map(lambda x: {"text": x["text"].replace("<EOS_TOKEN>", "<|end_of_text|>")})
print(f"[data] dataset cleaned. Sample: {train_ds[0]['text'][:100]}")

# Fix 5: Final assertion before SFTTrainer
assert tokenizer.convert_tokens_to_ids(tokenizer.eos_token) == 128001, \
    f"FATAL: eos still wrong: {tokenizer.convert_tokens_to_ids(tokenizer.eos_token)}"
assert tokenizer.chat_template is None, \
    "FATAL: chat_template not cleared"
print("[eos] ALL FIXES APPLIED — proceeding to SFTTrainer")
# ── END EOS FIX ──────────────────────────────────────────────────────────

## AFTER APPLYING
Use utf-8 for all file operations.
Save to scripts/fixed_cell_train.py.
Do NOT push via API — give me the file to paste 
directly into Kaggle notebook editor.
Paste into cell-train in Kaggle → Run All cells.
# -- Train -------------------------------------------------------------------
import inspect
import trl as _trl_mod
import transformers as _tf_mod

print(f"[train] trl={_trl_mod.__version__}  transformers={_tf_mod.__version__}")

# -- 0. EOS guard: ensure tokenizer.eos_token is a real vocab token ---------
# TRL 0.24.0 SFTConfig.eos_token defaults to None. SFTTrainer.__init__ only
# validates args.eos_token against vocab when it is NOT None. So the correct
# strategy is: do NOT pass eos_token to SFTConfig at all. Let it stay None;
# TRL will fall back to processing_class.eos_token (= tokenizer.eos_token)
# which this guard ensures is a real vocab token.
_vocab = tokenizer.get_vocab()
_eos_candidates = ["</s>", "<|end_of_text|>", "<|im_end|>", "<eos>", "<|eot_id|>"]
_found = next((t for t in _eos_candidates if t in _vocab), None)
if tokenizer.eos_token not in _vocab:
    if _found is None:
        raise RuntimeError("[train] FATAL: no usable EOS candidate in tokenizer vocab")
    tokenizer.eos_token = _found
    tokenizer.eos_token_id = _vocab[_found]
    print(f"[eos] forced: {_found}")
else:
    print(f"[eos] eos_token ok: {tokenizer.eos_token}")
assert tokenizer.eos_token in _vocab, f"[eos] {tokenizer.eos_token!r} not in vocab"

# -- 1. Probe SFTTrainer signature ------------------------------------------
_sft_sig_params = set(inspect.signature(SFTTrainer.__init__).parameters)

if "processing_class" in _sft_sig_params:
    _tok_kwarg = {"processing_class": tokenizer}
    print("[train] SFTTrainer tok-kwarg: processing_class")
else:
    _tok_kwarg = {"tokenizer": tokenizer}
    print("[train] SFTTrainer tok-kwarg: tokenizer")

# -- 2. Pick args class -----------------------------------------------------
_ArgsClass = SFTConfig if SFTConfig is not None else TrainingArguments
print(f"[train] args class: {_ArgsClass.__name__}")
_args_sig_params = set(inspect.signature(_ArgsClass.__init__).parameters)

_eval_key = "eval_strategy" if "eval_strategy" in _args_sig_params else "evaluation_strategy"
print(f"[train] eval kwarg: {_eval_key}")

# -- 3. Training kwargs (NOTE: eos_token intentionally omitted) -------------
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
# Do NOT add "eos_token" here. Let SFTConfig.eos_token stay None so TRL skips
# its vocab-validation block (sft_trainer.py line 628 `if args.eos_token is
# not None:`) entirely and falls back to processing_class.eos_token.
_sft_specific = {
    "dataset_text_field": "text",
    "max_seq_length": MAX_SEQ_LENGTH,
    "packing": False,
    "dataset_num_proc": 2,
}
_args_kwargs = {k: v for k, v in {**_base_kwargs, **_sft_specific}.items()
               if k in _args_sig_params}
_sft_direct  = {k: v for k, v in _sft_specific.items()
               if k not in _args_sig_params and k in _sft_sig_params}
_nowhere     = {k: v for k, v in _sft_specific.items()
               if k not in _args_sig_params and k not in _sft_sig_params}
print(f"[train] args class kwargs ({len(_args_kwargs)}): {sorted(_args_kwargs)}")
print(f"[train] SFTTrainer direct kwargs ({len(_sft_direct)}): {sorted(_sft_direct)}")
assert "eos_token" not in _args_kwargs and "eos_token" not in _sft_direct, \
    "[train] eos_token must NOT be passed -- let SFTConfig.eos_token default to None"
if _nowhere:
    print(f"[train] WARNING: not accepted anywhere, skipping: {sorted(_nowhere)}")

# -- 4. Build args object ---------------------------------------------------
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

# Diagnostic: confirm SFTConfig.eos_token is left as None
print(f"[train] args.eos_token (should be None): {getattr(_args_obj, 'eos_token', '(absent)')!r}")

# -- 4b. DEBUG (PROGRESS.md Step 1) -----------------------------------------
print(f"DEBUG eos: {repr(_base_kwargs.get('eos_token','NOT IN DICT'))}")
print(f"DEBUG SFTConfig eos: {repr(_args_obj.eos_token)}")

# -- 5. Build SFTTrainer ----------------------------------------------------
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

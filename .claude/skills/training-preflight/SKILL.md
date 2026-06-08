# TRAINING-PREFLIGHT

## Before running ANY training cell, verify all 8 checks:

### CHECK 1: GPU is T4
Kaggle right sidebar → Accelerator → must say "T4 GPU"
If it says P100 or CPU: change to T4 GPU before continuing.
P100 cannot run this training configuration.

### CHECK 2: AFRICA_GIANTS secret attached
Kaggle left sidebar → lock icon → Secrets
"AFRICA_GIANTS" must be listed with toggle ON for this notebook.
If missing: Add Secret → Name: AFRICA_GIANTS → Value: your HF token

### CHECK 3: BF16 = False in Config cell
```python
BF16 = False  # T4 is sm_75 (Turing), not Ampere (sm_80+)
              # BF16 requires Ampere or newer — T4 will silently fail
```

### CHECK 4: EOS token fix in Train cell
Cell 7 must contain BOTH:
```python
# BEFORE SFTTrainer build:
_args_obj.eos_token = None  # Critical — must be here

# INSIDE every retry loop iteration:
_args_obj.eos_token = None  # Must be inside loop too
```

### CHECK 5: Dataset repo name exact capitalisation
```python
DATASET_REPO = "prospAprospA007/africa-giants-dataset"
#               ^^^^ mixed capitals — do NOT change to all lowercase
```

### CHECK 6: data_files parameter in Dataset cell
```python
raw_dataset = load_dataset(
    DATASET_REPO,
    data_files={
        "train": "train_sft.jsonl",
        "validation": "val_sft.jsonl"
    },
    token=hf_token
)
# Without data_files, HF defaults to Parquet (old 47-pair data)
```

### CHECK 7: transformers pinned to 4.47.0
After install cell runs, verify:
transformers==4.47.0 (NOT 5.x — incompatible with TRL 0.24.0 + Unsloth)

### CHECK 8: No old Parquet files on HuggingFace
Go to: huggingface.co/datasets/prospAprospA007/africa-giants-dataset
Files tab must show: train_sft.jsonl and val_sft.jsonl
Must NOT show: data/train-00000-of-00001.parquet (old format)

## Expected training output (300 pairs, 3 epochs, T4):
```
Num examples = 270 | Num Epochs = 3 | Total steps = 204
```
If it shows 47 examples: dataset loaded incorrectly — stop, fix CHECK 6.
If EOS error: stop, apply CHECK 4 fix.
If CUDA memory error: stop, apply CHECK 3 fix.

# PROGRESS LOG — AFRICA-GIANTS
## Last Updated: 2026-05-26

## Project Info
- Repo: https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS
- Kaggle account: prospaprospa
- Working notebook URL: https://www.kaggle.com/code/prospaprospa/africa-giants-v2/edit/run/322289682
- Base model: McGill-NLP/AfriqueLlama-8B
- Trained model on HF: prospaprospa007/africa-giants-adapter-v1
- HF secret in Kaggle: AFRICA_GIANTS
- Pipeline state file: models/pipeline_state.json
- Trigger training: python run.py train
- Custom commands: .claude\commands\fix-eos.md

## Completed Pipeline Steps
- data_pipeline: ✅ DONE
- hf_upload: ✅ DONE
- kaggle_trigger: ✅ DONE
- training: ✅ COMPLETE
  - Loss dropped: 3.177 → 1.574 over 10 steps
  - Val loss: 1.371 — PASSED threshold 2.5 ✓
  - Runtime: 41.1 seconds on T4
  - Adapter pushed: prospaprospa007/africa-giants-adapter-v1
- evaluate: ⏳ NEXT
- deploy: ❌ NOT STARTED

## IMMEDIATE NEXT TASK FOR CLAUDE CODE
The Kaggle notebook was manually edited and training 
completed successfully. The working fixes must be pulled 
back into local files so automation pipeline uses correct 
versions going forward.

Do this in order:

Step 1 — Download working notebook from Kaggle:
Use the Kaggle API to download the working notebook:
python -c "
import kaggle
kaggle.api.authenticate()
kaggle.api.kernels_pull(
    'prospaprospa/africa-giants-v2',
    path='kaggle/',
    metadata=True
)
print('Downloaded')
"
Save as kaggle/kaggle_train_arque_llama.ipynb and 
also copy to notebooks/kaggle_train_arque_llama.ipynb

Step 2 — Extract and save working cell code:
Extract each cell from downloaded notebook and save:
- scripts/fixed_cell_model.py — cell-model content
- scripts/fixed_cell_data.py — cell-data content
- scripts/fixed_cell_train.py — cell-train content

Step 3 — Update kernel-metadata.json:
Point to working notebook africa-giants-v2
Slug: africa-giants-v2
URL: https://www.kaggle.com/code/prospaprospa/africa-giants-v2

Step 4 — Commit and push everything to GitHub:
git add -A
git commit -m "Sync working notebook after successful training run"
git push origin main

Step 5 — Update pipeline_state.json:
Reset to after hf_upload so next run goes straight 
to evaluate and deploy:
completed_steps: ["data_pipeline", "hf_upload", 
"kaggle_trigger", "kaggle_monitor"]

Step 6 — Run pipeline to evaluate and deploy:
python run.py train

Use utf-8 for ALL file operations.
Do NOT manually rerun on Kaggle — let pipeline handle it.

## CONFIRMED WORKING FIXES — DO NOT CHANGE THESE
These fixes are in the working Kaggle notebook and MUST
be preserved when syncing back to local files:

ROOT CAUSE FOUND:
AfriqueLlama tokenizer_config.json sets eos_token="<EOS_TOKEN>"
by default on every load. This caused every TRL training attempt
to fail with ValueError for months of debugging.

FIXES THAT RESOLVED IT:
1. Reload raw HuggingFace tokenizer after Unsloth loads model
2. Hardcode tokenizer.eos_token = "<|end_of_text|>"
3. Hardcode tokenizer.eos_token_id = 128001
4. tokenizer.add_special_tokens({"eos_token": "<|end_of_text|>"})
5. tokenizer.chat_template = None
6. model.config.eos_token_id = 128001
7. model.generation_config.eos_token_id = 128001
8. Clean dataset text of all <EOS_TOKEN> strings
9. TRL monkey-patch as defensive backup
10. Use manual Llama-3.1 format instead of apply_chat_template
11. f-string newlines use \n\n not literal newlines

## ALL PREVIOUS FIXES — DO NOT REDO
1.  ✅ Kaggle 401 fixed
2.  ✅ Kernel username fixed
3.  ✅ KaggleApiExtended updated
4.  ✅ kernel_status fixed
5.  ✅ fsspec conflicts handled
6.  ✅ AFRICA_GIANTS HF token in Kaggle
7.  ✅ GPU-agnostic notebook
8.  ✅ BaseImageProcessor fixed
9.  ✅ evaluation_strategy → eval_strategy
10. ✅ tokenizer → processing_class
11. ✅ max_seq_length removed from SFTConfig
12. ✅ SFTTrainer rewritten for TRL 0.24.0
13. ✅ P100 fail-fast removed
14. ✅ encoding=utf-8 everywhere
15. ✅ device_map fixed
16. ✅ get_chat_template removed
17. ✅ Old cached kernel replaced
18. ✅ EOS token root cause found and fixed
19. ✅ Training completed successfully
20. ✅ Model pushed to HuggingFace

## KAGGLE ENVIRONMENT
- trl: 0.24.0
- transformers: 5.5.0
- GPU: Tesla T4 (Unsloth active)
- Python: 3.12
- AfriqueLlama eos_token: <|end_of_text|> id=128001
- Dataset: 17 train / 4 eval examples
- Training: 10 steps, 2 epochs, 41.1 seconds

## NEXT STEPS IN ORDER
1. Sync working notebook from Kaggle to local files
2. Commit and push to GitHub
3. Run python run.py train for evaluate → deploy
4. Deploy to HuggingFace Spaces with Gradio interface
5. Test with Swahili and English business queries
6. Set MERGE_AND_PUSH = True for full merged model
7. Begin next training cycle with more data

## TECH STACK — DO NOT CHANGE
- Training: Kaggle T4 x2 free GPU
- Base model: McGill-NLP/AfriqueLlama-8B
- Trained model: prospaprospa007/africa-giants-adapter-v1
- Fine-tuning: Unsloth + QLoRA on T4
- Vector store: FAISS or ChromaDB
- Embeddings: sentence-transformers multilingual
- Deployment: HuggingFace Spaces + Inference API
- Languages: Swahili + English
- Purpose: AI for Tanzanian businesses

## RULES FOR CLAUDE CODE
- Use encoding=utf-8 for ALL file operations
- Always sync notebook to kaggle/ after editing
- Always commit and push after changes
- Do NOT push broken notebook via API
- Never redo fixes from ALREADY APPLIED list
- After every fix update PROGRESS.md
- Working notebook is at Kaggle URL above
- Always download from Kaggle before editing locally
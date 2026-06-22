import os
import shutil

# Route HF cache to persistent storage for fast cold starts.
# Old adapter versions (v3/v4/v5) were deleted 2026-06-22 to free space.
# Persistent storage now has ~20GB free; v10 (15GB) fits with room to spare.
HF_CACHE_DIR   = '/persistent-storage/.cache/huggingface'
MODEL_CACHE_DIR = '/persistent-storage/.cache/huggingface/hub'
os.environ['HF_HOME'] = HF_CACHE_DIR
os.makedirs(HF_CACHE_DIR, exist_ok=True)

# Safety: delete any old adapter versions that reappear in persistent storage
for old_version in ['v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9']:
    old_path = f'/persistent-storage/.cache/huggingface/hub/models--prospAprospA007--africa-giants-adapter-{old_version}'
    if os.path.exists(old_path):
        shutil.rmtree(old_path)
        print(f'[cache] Deleted old model: {old_path}')

import torch
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v10"
HF_TOKEN     = os.environ.get("HF_TOKEN", "")

if HF_TOKEN:
    login(token=HF_TOKEN)
    print("[chike] HuggingFace authenticated")
else:
    print("[chike] WARNING: HF_TOKEN not set — model may fail to load")

SYSTEM_PROMPT = (
    "Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. "
    "Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. "
    "Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, "
    "OSHA, SDL, PAYE, VAT kwa Kiswahili na Kiingereza. "
    "Kama swali liko nje ya mada yako sema wazi kwamba halijui "
    "na mwelekeze kwa TRA au mshauri aliyehitimu. "
    "Your name is Chike, a business adviser from Africa Giants. "
    "Tagline: Fahamu Biashara Yako, Maarifa Yako. "
    "You answer Tanzanian business, tax, and compliance questions "
    "in Swahili and English. "
    "If a question is outside your knowledge say so clearly "
    "and direct the user to TRA or a qualified adviser."
)

_model     = None
_tokenizer = None

def get_model():
    global _model, _tokenizer
    if _model is None:
        print("[chike] Loading tokenizer ...")
        _tokenizer = AutoTokenizer.from_pretrained(
            ADAPTER_REPO,
            cache_dir=MODEL_CACHE_DIR,
            token=HF_TOKEN if HF_TOKEN else None,
            trust_remote_code=True,
        )
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token

        try:
            print("[chike] Loading model in 4bit ...")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            _model = AutoModelForCausalLM.from_pretrained(
                ADAPTER_REPO,
                cache_dir=MODEL_CACHE_DIR,
                quantization_config=bnb_config,
                device_map="auto",
                token=HF_TOKEN if HF_TOKEN else None,
                trust_remote_code=True,
            )
            print("[chike] Model loaded in 4bit — ready")
        except Exception as e:
            print(f"[chike] 4bit load failed ({e}), falling back to float16 ...")
            _model = AutoModelForCausalLM.from_pretrained(
                ADAPTER_REPO,
                cache_dir=MODEL_CACHE_DIR,
                torch_dtype=torch.float16,
                device_map="auto",
                token=HF_TOKEN if HF_TOKEN else None,
                trust_remote_code=True,
            )
            print("[chike] Model loaded in float16 — ready")

        _model.eval()
    return _model, _tokenizer

def run(message: str, temperature: float = 0.1):
    if not message or not message.strip():
        return {"error": "No message provided"}

    model, tokenizer = get_model()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": message.strip()},
    ]

    try:
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    except Exception:
        prompt = (
            f"<|begin_of_text|>"
            f"<|start_header_id|>system<|end_header_id|>\n\n"
            f"{SYSTEM_PROMPT}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{message.strip()}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

    inputs    = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=temperature,
            do_sample=True,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    new_tokens = outputs[0][input_len:]
    reply = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    for stop in ["<|start_header_id|>", "User:", "Mtumiaji:"]:
        if stop in reply:
            reply = reply.split(stop)[0].strip()

    print(f"[chike] Q: {message[:60]}")
    print(f"[chike] A: {reply[:60]}")

    return {"reply": reply}


def diagnose():
    """Check disk space and persistent storage state."""
    import subprocess
    results = {}

    for p in ['/persistent-storage', '/persistent-storage/.cache/huggingface/hub', '/tmp']:
        if os.path.exists(p):
            try:
                total, used, free = shutil.disk_usage(p)
                results[p] = {
                    'total_gb': round(total / 1e9, 1),
                    'used_gb':  round(used  / 1e9, 1),
                    'free_gb':  round(free  / 1e9, 1),
                }
                if os.path.isdir(p):
                    results[p]['contents'] = os.listdir(p)
            except Exception as e:
                results[p] = {'error': str(e)}
        else:
            results[p] = {'exists': False}

    results['HF_HOME'] = os.environ.get('HF_HOME', 'NOT SET')

    try:
        df = subprocess.run(['df', '-h'], capture_output=True, text=True)
        results['df_h'] = df.stdout
    except Exception:
        pass

    return results

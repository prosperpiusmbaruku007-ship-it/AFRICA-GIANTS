import os
import torch
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM

ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v3"
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
            token=HF_TOKEN if HF_TOKEN else None,
            trust_remote_code=True,
        )
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token
        print(f"[chike] eos_token: {repr(_tokenizer.eos_token)}")

        print("[chike] Loading model ...")
        _model = AutoModelForCausalLM.from_pretrained(
            ADAPTER_REPO,
            torch_dtype=torch.float16,
            device_map="auto",
            token=HF_TOKEN if HF_TOKEN else None,
            trust_remote_code=True,
        )
        _model.eval()
        print("[chike] Model loaded and ready")
    return _model, _tokenizer

def run(message: str, temperature: float = 0.1):
    if not message or not message.strip():
        return {"error": "No message provided"}

    model, tokenizer = get_model()

    prompt = (
        f"<|begin_of_text|>"
        f"<|start_header_id|>system<|end_header_id|>\n\n"
        f"{SYSTEM_PROMPT}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{message.strip()}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    full  = tokenizer.decode(outputs[0], skip_special_tokens=True)
    parts = full.split("<|start_header_id|>assistant<|end_header_id|>")
    reply = parts[-1].strip() if len(parts) > 1 else full.strip()

    print(f"[chike] Q: {message[:60]}")
    print(f"[chike] A: {reply[:60]}")

    return {"reply": reply}

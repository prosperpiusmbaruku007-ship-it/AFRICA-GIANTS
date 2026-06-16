import os
import torch
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v4"
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

    # Use tokenizer chat template if available
    # otherwise fall back to manual format
    messages = [
        {"role": "system",    "content": SYSTEM_PROMPT},
        {"role": "user",      "content": message.strip()},
    ]

    try:
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    except Exception:
        # Fallback to manual Llama 3 format
        prompt = (
            f"<|begin_of_text|>"
            f"<|start_header_id|>system<|end_header_id|>\n\n"
            f"{SYSTEM_PROMPT}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{message.strip()}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

    inputs      = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_len   = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    # Decode ONLY the new tokens — not the prompt
    new_tokens = outputs[0][input_len:]
    reply      = tokenizer.decode(
        new_tokens,
        skip_special_tokens=True,
    ).strip()

    # Remove any hallucinated follow-up turns
    for stop in ["<|start_header_id|>", "User:", "Mtumiaji:"]:
        if stop in reply:
            reply = reply.split(stop)[0].strip()

    print(f"[chike] Q: {message[:60]}")
    print(f"[chike] A: {reply[:60]}")

    return {"reply": reply}

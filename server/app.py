from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import BitsAndBytesConfig
from peft import PeftModel
import torch
import os
import json
import datetime
import asyncio
import traceback

# ── Product identity ──────────────────────────────────────────────────────────
PRODUCT_NAME    = "Chike"
COMPANY_NAME    = "Africa Giants"
FULL_NAME       = "Chike by Africa Giants"
FULL_IDENTITY   = "Chike by Africa Giants"
TAGLINE_SW      = "Msaidizi wa AI wa biashara za Tanzania kutoka Africa Giants"
TAGLINE_EN      = "Tanzania's business AI assistant — tax, compliance, registration"

app = FastAPI(
    title=FULL_NAME,
    description="Tanzanian business AI assistant — WhatsApp inference server",
    version="1.0.0",
)

# ── Config from environment variables ────────────────────────────────────────
HF_TOKEN        = os.environ.get("HF_TOKEN", "")
# Note: adapter-v3 is public — token not required for inference
# Token only needed if repo is private
BASE_MODEL      = "McGill-NLP/AfriqueLlama-8B"
ADAPTER_REPO    = "prospAprospA007/africa-giants-adapter-v3"
MAX_NEW_TOKENS  = 300
TEMPERATURE     = 0.1
TIMEOUT_SECS    = 25
LOG_FILE        = "server/logs/conversations.jsonl"

# ── System prompt — Chike introduces himself ──────────────────────────────────
SYSTEM_PROMPT = (
    "Jina lako ni Chike, msaidizi wa AI wa biashara za Tanzania "
    "kutoka Africa Giants. "
    "Unajibu maswali kuhusu sheria za biashara, kodi, usajili "
    "wa kampuni kwa Kiswahili na Kiingereza. "
    "Jibu kwa uwazi, usahihi, na kwa lugha inayoeleweka. "
    "Your name is Chike, a Tanzanian business AI assistant from Africa Giants. "
    "You answer questions about business regulations, tax, company "
    "registration, and financial compliance in Swahili and English. "
    "Answer clearly, accurately, and in simple language."
)

# ── Fallback message — Chike by name ─────────────────────────────────────────
FALLBACK_MESSAGE = (
    "Samahani, Chike hakuweza kukusaidia sasa hivi. "
    "Tafadhali jaribu tena baadaye. "
    "Sorry, Chike could not process your request right now. "
    "Please try again shortly."
)

# ── Welcome message — sent when user first messages ──────────────────────────
WELCOME_MESSAGE = (
    "Habari! Mimi ni *Chike* kutoka *Africa Giants*. "
    "Ninakusaidia na maswali ya biashara Tanzania — "
    "kodi, usajili, BRELA, TRA, NSSF, na zaidi. "
    "Uliza swali lolote la biashara. "
    "\n\n"
    "Hi! I am *Chike* from *Africa Giants*. "
    "I help with Tanzanian business questions — "
    "tax, registration, BRELA, TRA, NSSF, and more. "
    "Ask me any business question."
)

# ── Trigger words that get the welcome message ────────────────────────────────
GREETING_TRIGGERS = {
    "habari", "hujambo", "mambo", "hello", "hi", "hey",
    "salaam", "salam", "nianze", "start", "help", "msaada",
}

# ── Model — loaded once on startup ───────────────────────────────────────────
model     = None
tokenizer = None

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    print(f"[startup] {FULL_IDENTITY} starting ...")
    print(f"[startup] {TAGLINE_SW}")
    print(f"[startup] Base model: {BASE_MODEL}")
    print(f"[startup] Adapter: {ADAPTER_REPO}")

    # Step 1 — load tokenizer from base model
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from transformers import BitsAndBytesConfig
    from peft import PeftModel

    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        token=HF_TOKEN if HF_TOKEN else None,
    )
    tokenizer.pad_token = tokenizer.eos_token
    print("[startup] Tokenizer loaded")

    # Step 2 — load base model in 4bit to fit in memory
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        token=HF_TOKEN if HF_TOKEN else None,
    )
    print("[startup] Base model loaded")

    # Step 3 — apply LoRA adapter on top of base model
    model = PeftModel.from_pretrained(
        base,
        ADAPTER_REPO,
        token=HF_TOKEN if HF_TOKEN else None,
    )
    model.eval()
    print(f"[startup] {FULL_IDENTITY} ready ✓")
    print(f"[startup] {TAGLINE_EN}")

# ── Logging ───────────────────────────────────────────────────────────────────
def log_conversation(
    phone: str,
    question: str,
    answer: str,
    duration_ms: int,
    was_greeting: bool = False,
):
    os.makedirs("server/logs", exist_ok=True)
    entry = {
        "timestamp":    datetime.datetime.utcnow().isoformat(),
        "phone_hash":   hash(phone) % 100000,
        "question":     question,
        "answer":       answer[:500],
        "duration_ms":  duration_ms,
        "was_greeting": was_greeting,
        "product":      FULL_NAME,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ── Inference ─────────────────────────────────────────────────────────────────
def run_inference(user_message: str) -> str:
    prompt = (
        f"<|begin_of_text|>"
        f"<|start_header_id|>system<|end_header_id|>\n\n"
        f"{SYSTEM_PROMPT}"
        f"<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_message}"
        f"<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    full  = tokenizer.decode(outputs[0], skip_special_tokens=True)
    parts = full.split("<|start_header_id|>assistant<|end_header_id|>")
    reply = parts[-1].strip() if len(parts) > 1 else full.strip()
    return reply if reply else FALLBACK_MESSAGE

# ── Webhook ───────────────────────────────────────────────────────────────────
@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
):
    user_message  = Body.strip()
    message_lower = user_message.lower().strip()
    print(f"[webhook] {From[:8]}***: {user_message[:80]}")

    start        = datetime.datetime.utcnow()
    was_greeting = message_lower in GREETING_TRIGGERS

    if was_greeting:
        reply       = WELCOME_MESSAGE
        duration_ms = 0
        print(f"[webhook] Greeting detected — sending welcome")
    else:
        try:
            loop  = asyncio.get_event_loop()
            reply = await asyncio.wait_for(
                loop.run_in_executor(None, run_inference, user_message),
                timeout=TIMEOUT_SECS,
            )
        except asyncio.TimeoutError:
            reply = FALLBACK_MESSAGE
            print("[webhook] Timeout — returning fallback")
        except Exception as _e:
            reply = FALLBACK_MESSAGE
            print(f"[webhook] Error: {_e}")
            traceback.print_exc()

        duration_ms = int(
            (datetime.datetime.utcnow() - start).total_seconds() * 1000
        )

    log_conversation(From, user_message, reply, duration_ms, was_greeting)
    print(f"[webhook] Reply ({duration_ms}ms): {reply[:80]}")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply}</Message>
</Response>"""
    return PlainTextResponse(content=twiml, media_type="application/xml")

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status":        "ok",
        "product":       FULL_NAME,
        "model_loaded":  model is not None,
        "adapter":       ADAPTER_REPO,
        "version":       "v3",
    }

# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name":          FULL_NAME,
        "description":   "Tanzanian business AI — WhatsApp inference server",
        "company":       COMPANY_NAME,
        "health":        "/health",
        "webhook":       "/webhook (POST — Twilio only)",
    }

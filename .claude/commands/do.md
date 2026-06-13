#Read this file completely then execute every instruction below exactly as written.

TASK: Diagnose and fix the Cerebrium vLLM initialization failure.

The endpoint is returning:
"Engine core initialization failed. See root cause above."

Run these diagnosis steps one by one.

Step 1 — Check secrets:
cerebrium secrets list

Step 2 — Check current main.py content:
type chike-inference\main.py

Step 3 — Check current cerebrium.toml content:
type chike-inference\cerebrium.toml

Step 4 — Fix main.py with all known issues resolved.
Replace chike-inference\main.py with:

import os
from huggingface_hub import login

ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v3"
HF_TOKEN     = os.environ.get("HF_TOKEN", "")

if HF_TOKEN:
    login(token=HF_TOKEN)
    print("[chike] HuggingFace authenticated")
else:
    print("[chike] WARNING: HF_TOKEN not set")

SYSTEM_PROMPT = (
    "Jina lako ni Chike Brain, mshauri wa biashara kutoka Africa Giants. "
    "Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. "
    "Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, "
    "OSHA, SDL, PAYE, VAT kwa Kiswahili na Kiingereza. "
    "Kama swali liko nje ya mada yako sema wazi kwamba halijui "
    "na mwelekeze kwa TRA au mshauri aliyehitimu. "
    "Your name is Chike Brain, a business adviser from Africa Giants. "
    "Tagline: Fahamu Biashara Yako, Maarifa Yako. "
    "You answer Tanzanian business, tax, and compliance questions "
    "in Swahili and English. "
    "If a question is outside your knowledge say so clearly "
    "and direct the user to TRA or a qualified adviser."
)

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        from vllm import LLM
        print("[chike] Loading model ...")
        _llm = LLM(
            model=ADAPTER_REPO,
            dtype="float16",
            trust_remote_code=True,
            max_model_len=2048,
            tokenizer=ADAPTER_REPO,
            tokenizer_mode="auto",
            gpu_memory_utilization=0.90,
        )
        print("[chike] Model loaded")
    return _llm

def run(message: str, temperature: float = 0.1):
    from vllm import SamplingParams

    if not message or not message.strip():
        return {"error": "No message provided"}

    prompt = (
        f"<|begin_of_text|>"
        f"<|start_header_id|>system<|end_header_id|>\n\n"
        f"{SYSTEM_PROMPT}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{message.strip()}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )

    params  = SamplingParams(
        temperature=temperature,
        max_tokens=300,
        stop=["<|eot_id|>", "<|end_of_text|>"],
    )
    outputs = get_llm().generate([prompt], params)
    reply   = outputs[0].outputs[0].text.strip()

    print(f"[chike] Q: {message[:60]}")
    print(f"[chike] A: {reply[:60]}")

    return {"reply": reply}

Step 5 — Fix cerebrium.toml with all dependencies.
Replace chike-inference\cerebrium.toml with:

[cerebrium.deployment]
name = "chike-inference"
python_version = "3.11"
docker_base_image_url = "nvidia/cuda:12.1.1-runtime-ubuntu22.04"
hardware = "ADA_L4"
min_replicas = 0
max_replicas = 2
cooldown = 60

[cerebrium.dependencies.pip]
vllm = "latest"
transformers = ">=4.43.0"
huggingface_hub = ">=0.23.0"
accelerate = ">=0.30.0"

Step 6 — Verify HF_TOKEN secret exists.
Run:
cerebrium secrets list

If HF_TOKEN is not listed run:
cerebrium secrets add HF_TOKEN=
Step 7 — Commit the fixes:
cd C:\Users\jhjh\AFRICA-GIANTS
git add chike-inference\main.py chike-inference\cerebrium.toml
git commit -m "fix Cerebrium vLLM init — trust_remote_code, HF login, lazy load, stop tokens"
git push origin main
Show commit hash.

Step 8 — Redeploy:
cd C:\Users\jhjh\AFRICA-GIANTS\chike-inference
cerebrium deploy

Watch the deploy output carefully and paste
the full output including any errors.
STOP after showing deploy result.
from vllm import LLM, SamplingParams
import os

ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v3"

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

# Lazy init — LLM loads on first request, not at import time
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = LLM(
            model=ADAPTER_REPO,
            dtype="float16",
            trust_remote_code=True,
            max_model_len=2048,
        )
    return _llm


def run(message: str, temperature: float = 0.1):
    prompt = (
        f"<|begin_of_text|>"
        f"<|start_header_id|>system<|end_header_id|>\n\n"
        f"{SYSTEM_PROMPT}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{message}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    params  = SamplingParams(temperature=temperature, max_tokens=300)
    outputs = get_llm().generate([prompt], params)
    return {"reply": outputs[0].outputs[0].text.strip()}

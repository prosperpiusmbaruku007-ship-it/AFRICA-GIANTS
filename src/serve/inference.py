import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from src.common.logging import get_logger
from src.common.storage import load_yaml_config
from src.common.secrets import get_hf_token

logger = get_logger("inference")

# Llama 3.1 special tokens
_BOS      = "<|begin_of_text|>"
_SYS_S    = "<|start_header_id|>system<|end_header_id|>\n\n"
_USER_S   = "<|start_header_id|>user<|end_header_id|>\n\n"
_ASST_S   = "<|start_header_id|>assistant<|end_header_id|>\n\n"
_EOT      = "<|eot_id|>"

SYSTEM_PROMPT = (
    "Wewe ni msaidizi wa AI wa biashara za Tanzania. "
    "Unajibu maswali kuhusu sheria za biashara, kodi, usajili wa kampuni, "
    "na kanuni za kifedha kwa Kiswahili na Kiingereza. "
    "You are a Tanzanian business AI assistant. Answer questions about "
    "business regulations, tax, company registration, and financial rules "
    "in both Swahili and English."
)


def _llama31_prompt(user_msg: str, system: str = SYSTEM_PROMPT) -> str:
    return (
        f"{_BOS}"
        f"{_SYS_S}{system}{_EOT}"
        f"{_USER_S}{user_msg}{_EOT}"
        f"{_ASST_S}"
    )


class InferenceEngine:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = ""
        self.is_mock = False

        models_config = load_yaml_config("models")
        hf_config = load_yaml_config("huggingface")

        # Serve from the fine-tuned adapter if it exists, else fall back to base model
        adapter_repo = hf_config["huggingface"].get("adapter_repo", "")
        base_model   = models_config["model"]["base_model_name"]
        start_model  = adapter_repo if adapter_repo else base_model

        self.reload_model(start_model)

    def reload_model(self, model_name_or_path: str):
        """Loads or hot-swaps model weights in memory."""
        logger.info("Loading model weights from %s...", model_name_or_path)

        if os.getenv("AFRICA_GIANTS_MOCK", "").lower() in {"1", "true", "yes"}:
            logger.info("AFRICA_GIANTS_MOCK enabled — starting in mock mode.")
            self.model = None
            self.tokenizer = None
            self.model_name = f"MOCK-{model_name_or_path}"
            self.is_mock = True
            return

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Using device: %s", device)

        try:
            hf_token = get_hf_token()
        except Exception:
            hf_token = None

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name_or_path, token=hf_token, trust_remote_code=True
            )
            self.tokenizer.pad_token = self.tokenizer.eos_token

            if device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name_or_path,
                    device_map="auto",
                    torch_dtype=torch.bfloat16,
                    token=hf_token,
                    trust_remote_code=True,
                )
            else:
                models_config = load_yaml_config("models")
                base = models_config["model"]["base_model_name"]
                if model_name_or_path == base or "8B" in model_name_or_path:
                    logger.warning(
                        "8B model on CPU is too slow — redirecting to HuggingFaceTB/SmolLM-135M for local testing."
                    )
                    model_name_or_path = "HuggingFaceTB/SmolLM-135M"
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name_or_path,
                    torch_dtype=torch.float32,
                    trust_remote_code=True,
                )

            self.model.eval()
            self.model_name = model_name_or_path
            self.is_mock = False
            logger.info("Model loaded successfully.")

        except Exception as e:
            logger.error("Failed to load model %s: %s", model_name_or_path, e)
            logger.warning("Starting inference engine in mock mode for testing.")
            self.is_mock = True
            self.model_name = f"MOCK-{model_name_or_path}"

    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 256) -> str:
        """Generates a text response for the given prompt."""
        if self.is_mock:
            lower = prompt.lower()
            if "kodi" in lower or "tax" in lower or "tra" in lower:
                return (
                    "[MOCK] Keep accurate sales and expense records, register with TRA, "
                    "track VAT and PAYE if they apply, file returns on time."
                )
            if "usajili" in lower or "brela" in lower or "register" in lower:
                return (
                    "[MOCK] Choose a business structure, register with BRELA, get a TIN from TRA, "
                    "apply for the correct business license, and keep proper records."
                )
            if "bookkeeping" in lower or "records" in lower:
                return (
                    "[MOCK] Track daily sales, expenses, inventory, cash, mobile money, "
                    "customer debts, and supplier payments to see profit and cash flow."
                )
            return (
                f"[MOCK] Africa Giants assists with Tanzanian business coaching, TRA compliance, "
                f"BRELA registration, bookkeeping, and marketing. Model: {self.model_name}."
            )

        sys = system_prompt or SYSTEM_PROMPT
        formatted = _llama31_prompt(prompt, sys)

        device = "cuda" if torch.cuda.is_available() else "cpu"
        inputs = self.tokenizer(formatted, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.3,
                top_p=0.9,
            )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Strip the prompt prefix — everything after the last assistant header
        response = decoded.split("assistant\n\n")[-1].strip()
        return response

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from src.common.logging import get_logger
from src.common.storage import load_yaml_config

logger = get_logger("inference")

class InferenceEngine:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = ""
        self.is_mock = False
        
        # Load config
        self.models_config = load_yaml_config("models")
        default_model = self.models_config["model"]["base_model_name"]
        
        # Initialize
        self.reload_model(default_model)

    def reload_model(self, model_name_or_path: str):
        """Loads or hot-swaps model weights in memory."""
        logger.info(f"Loading model weights from {model_name_or_path}...")
        
        # Check for CUDA availability
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        try:
            # First try loading the requested model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load in 8-bit or 4-bit if on CUDA, otherwise standard load
            if device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name_or_path,
                    device_map="auto",
                    torch_dtype=torch.float16,
                    trust_remote_code=True
                )
            else:
                # Load a tiny model locally on CPU to keep memory footprint low
                logger.warn("No CUDA GPU found. Loading on CPU. Fallback to tiny model recommended.")
                if "Afrique" in model_name_or_path or "8B" in model_name_or_path:
                    logger.warn("8B model on CPU is too slow! Redirecting to HuggingFaceTB/SmolLM-135M for local testing.")
                    model_name_or_path = "HuggingFaceTB/SmolLM-135M"
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
                    
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name_or_path,
                    torch_dtype=torch.float32,
                    trust_remote_code=True
                )
            
            self.model.eval()
            self.model_name = model_name_or_path
            self.is_mock = False
            logger.info("Model loaded successfully.")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name_or_path}: {e}")
            logger.warn("Starting inference engine in Mock Mode for testing.")
            self.is_mock = True
            self.model_name = f"MOCK-{model_name_or_path}"

    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 256) -> str:
        """Generates a text response for the given prompt."""
        if self.is_mock:
            # Simulate high quality Swahili/English mock output
            if "kodi" in prompt.lower() or "tax" in prompt.lower():
                return "[MOCK RESPONSE] Kiwango cha kodi ya kampuni nchini Tanzania ni asilimia 30 (30%) ya faida ghafi. VAT ni asilimia 18%."
            elif "usajili" in prompt.lower() or "brela" in prompt.lower():
                return "[MOCK RESPONSE] Kampuni inapaswa kusajiliwa BRELA kupitia mfumo wa Online Registration System (ORS)."
            else:
                return f"[MOCK RESPONSE] Pokea salamu kutoka kwa msaidizi wa Africa Giants. Hii ni majaribio ya uwezo wa mfano wa {self.model_name}."

        # Format input using ChatML structure
        if system_prompt:
            formatted_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        else:
            formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

        device = "cuda" if torch.cuda.is_available() else "cpu"
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.3,
                top_p=0.9
            )
            
        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract response from output
        response = decoded.split("assistant\n")[-1].strip()
        return response

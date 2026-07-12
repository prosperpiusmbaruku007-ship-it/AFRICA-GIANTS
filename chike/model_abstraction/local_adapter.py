"""LocalAdapter — wraps the model v15 currently uses (AfriqueLlama-8B + LoRA).

This is the production generation path behind the ModelBackend interface. It is a
concrete backend, so it can be *constructed* with no network and no GPU — the heavy
transformers/peft import and weight load happen lazily on the first generate()
call, not at __init__. That keeps the interface substitutable for FakeBackend in
tests while still delegating to the real v15 stack when actually invoked.

Config is read from kaggle/chike_config.json (single source of truth, R14):
base model McGill-NLP/AfriqueLlama-8B + adapter prospAprospA007/africa-giants-adapter-v15,
generation params from `generation_params`. RAG injection and the OOC classifier
live in the orchestrator, NOT here — this backend only turns a finished prompt into text.
"""

import json
import os
from typing import Optional

from .base import ModelBackend

_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "kaggle", "chike_config.json"
)


def _load_config() -> dict:
    with open(os.path.normpath(_CONFIG_PATH), encoding="utf-8") as fh:
        return json.load(fh)


class LocalAdapter(ModelBackend):
    """In-process AfriqueLlama-8B + v15 LoRA adapter.

    Construction is cheap and side-effect-free; the model is loaded once on first
    use via _ensure_loaded(). Requires GPU + weights at generate() time — not at
    import or construction — so importing this module never pulls in torch.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or _load_config()
        self.adapter_repo = self.config.get("adapter_repo")
        self.base_model = self.config.get("repos", {}).get("base_model")
        self.default_params = dict(self.config.get("generation_params", {}))
        self._model = None
        self._tokenizer = None

    def _ensure_loaded(self):
        """Lazily load base model + LoRA adapter. Imports torch/transformers/peft
        only here so the rest of the pipeline stays importable without them."""
        if self._model is not None:
            return
        import torch  # noqa: F401  (imported for side effect / availability check)
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel

        self._tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        base = AutoModelForCausalLM.from_pretrained(
            self.base_model, device_map="auto"
        )
        self._model = PeftModel.from_pretrained(base, self.adapter_repo)
        self._model.eval()

    def generate(self, prompt: str, params: Optional[dict] = None) -> str:
        self._ensure_loaded()
        merged = dict(self.default_params)
        if params:
            merged.update(params)  # caller overrides win; caller's dict untouched

        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
        output = self._model.generate(**inputs, **merged)
        text = self._tokenizer.decode(output[0], skip_special_tokens=True)
        # Strip the echoed prompt the same way production does.
        return text[len(prompt):].strip() if text.startswith(prompt) else text.strip()

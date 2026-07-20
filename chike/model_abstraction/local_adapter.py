"""LocalAdapter — ModelBackend that drives the REAL v15 model over its Modal endpoint.

The 8B AfriqueLlama weights only run on GPU (Modal/Kaggle), never on the local dev
box. So this backend does NOT load weights in-process; it is a thin authenticated
HTTP client to a RAW text-completion endpoint served by the same Modal app that runs
production (chike-inference/modal_app.py). That lets the entire v16 orchestrator be
exercised locally (no GPU) while every generate() call is answered by the actual
fine-tuned v15 model already serving users.

IMPORTANT — this MUST point at the RAW completion endpoint (prompt -> completion),
NOT production's web_endpoint. web_endpoint runs the whole v15 pipeline (classify +
decompose + RAG + chat template + clean) on its input, so feeding it the orchestrator's
already-built prompts would double-process fact questions and — worse — return prose
where slot extraction needs raw JSON, collapsing every compute question to a
clarification. The raw endpoint (generate_endpoint) is added alongside production in
modal_app.py and does tokenize -> generate -> decode only.

Endpoint URL + token come from the environment (never hardcoded — CLAUDE.md):
  CHIKE_RAW_ENDPOINT  — full URL of the raw completion endpoint
  CHIKE_MODAL_TOKEN   — the ?token= value (same MODAL_API_TOKEN gate as production)

Construction stays cheap and side-effect-free (no network), so the class remains a
drop-in for FakeBackend in tests; the HTTP call happens only inside generate().
"""

import json
import os
from typing import Optional

from .base import ModelBackend

_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "kaggle", "chike_config.json"
)


def _load_config() -> dict:
    try:
        with open(os.path.normpath(_CONFIG_PATH), encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


class LocalAdapter(ModelBackend):
    """Authenticated HTTP client to the real v15 model's raw completion endpoint.

    Default generation params come from kaggle/chike_config.json (R14) so the model
    is driven exactly as production drives it; a per-call params dict overrides them.
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        token: Optional[str] = None,
        config: Optional[dict] = None,
        timeout: float = 180.0,
        tokenizer: Optional[object] = None,
    ):
        self.config = config if config is not None else _load_config()
        self.endpoint_url = endpoint_url or os.environ.get("CHIKE_RAW_ENDPOINT", "")
        self.token = token or os.environ.get("CHIKE_MODAL_TOKEN", "")
        self.default_params = dict(self.config.get("generation_params", {}))
        self.timeout = timeout
        # Optional tokenizer so Orchestrator._backend_tokenizer() can route build_chat_prompt
        # through apply_chat_template — byte-identical to modal_app.run()/production (Phase D
        # Stage 0, Finding D-1). Left None by default to keep construction cheap and side-effect
        # free (the FakeBackend drop-in contract); the real-weights harness loads the AfriqueLlama
        # tokenizer once (CPU-only, no GPU) and passes it. None -> the naive-concat fallback.
        self.tokenizer = tokenizer

    def generate(self, prompt: str, params: Optional[dict] = None) -> str:
        if not self.endpoint_url:
            raise RuntimeError(
                "LocalAdapter has no endpoint URL. Set CHIKE_RAW_ENDPOINT (the raw "
                "completion endpoint added to modal_app.py) or pass endpoint_url=."
            )
        import requests

        merged = dict(self.default_params)
        if params:
            merged.update(params)  # caller overrides win; caller's dict untouched

        resp = requests.post(
            self.endpoint_url,
            params={"token": self.token},
            json={"prompt": prompt, "params": merged},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        if "completion" not in data:
            raise RuntimeError(f"raw endpoint returned no 'completion': {data}")
        return data["completion"]

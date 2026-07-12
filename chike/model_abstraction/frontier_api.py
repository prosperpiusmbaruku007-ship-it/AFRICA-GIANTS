"""FrontierAPI — stub backend for a frontier API model (Claude / Gemini via OpenRouter).

Why this exists: PROGRESS.md records that arithmetic and scaled-calculation questions
are the 8B model's structural weakness (scenario-pinned RAG facts do not generalize).
The documented fix path is to route calculation-type generation to a frontier model
with genuine reasoning, keeping the same RAG infrastructure. This backend is the seam
for that swap — a concrete ModelBackend so it is instantiable and interface-checked,
but generate() is deliberately unimplemented until a provider + key are wired.

Do NOT hardcode API keys (CLAUDE.md): read them from os.environ at call time.
"""

import os
from typing import Optional

from .base import ModelBackend


class FrontierAPI(ModelBackend):
    """Stub for a frontier-model backend.

    Concrete (overrides generate) so it satisfies the ModelBackend interface and
    can be constructed, but generate() raises NotImplementedError until the HTTP
    call to the chosen provider is implemented. This keeps the routing/orchestrator
    code able to reference and inject a frontier backend today, and fail loudly —
    never silently fabricate — if one is actually invoked before it is wired.
    """

    def __init__(
        self,
        provider: str = "openrouter",
        model: str = "meta-llama/llama-3.3-70b-instruct:free",
        api_key_env: str = "OPENROUTER_API_KEY",
    ):
        self.provider = provider
        self.model = model
        self.api_key_env = api_key_env

    @property
    def api_key(self) -> Optional[str]:
        return os.environ.get(self.api_key_env) or None

    def generate(self, prompt: str, params: Optional[dict] = None) -> str:
        raise NotImplementedError(
            "FrontierAPI is a stub: wire the "
            f"{self.provider} HTTP call (model={self.model}) before use. "
            "See PROGRESS.md 'Fix path: frontier API model'."
        )

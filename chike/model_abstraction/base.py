"""ModelBackend — the single interface between Chike and any language model.

Nothing in the product imports a model directly. Every call to a language model
goes through a ModelBackend, so the orchestrator and every generation-dependent
path can be exercised against a deterministic FakeBackend with no network and no
GPU. That indirection is the only reason the pipeline is testable today; keep it —
never let a concrete transformers / Modal / HTTP call leak into a caller.

Concrete backends live beside this file:
  - LocalAdapter  (local_adapter.py) — wraps whatever model v15 currently uses
  - FrontierAPI   (frontier_api.py)  — stub for a frontier API model
  - FakeBackend   (test_double.py)   — deterministic double for tests
"""

from abc import ABC, abstractmethod
from typing import Optional


class ModelBackend(ABC):
    """Abstract contract every language-model backend must satisfy.

    Subclasses MUST override generate(). Because generate() is an abstractmethod,
    Python refuses to instantiate any subclass that leaves it unimplemented
    (TypeError at construction) — that is the interface enforcement the pipeline
    relies on to guarantee every backend is substitutable for the FakeBackend.
    """

    @abstractmethod
    def generate(self, prompt: str, params: Optional[dict] = None) -> str:
        """Return the model's text completion for `prompt`.

        `params` is an optional dict of generation controls (e.g. temperature,
        max_new_tokens). Implementations MUST treat params=None as "use defaults"
        and MUST NOT mutate the caller's dict.
        """
        raise NotImplementedError

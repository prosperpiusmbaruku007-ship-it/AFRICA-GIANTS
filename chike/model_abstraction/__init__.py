"""Model abstraction layer — the single seam between Chike and any language model.

All callers depend on ModelBackend; concrete backends are swappable behind it.
Importing this package pulls in NO torch / transformers / HTTP client — those load
lazily inside LocalAdapter.generate() / FrontierAPI.generate(), so tests can import
and inject FakeBackend with no network and no GPU.
"""

from .base import ModelBackend
from .local_adapter import LocalAdapter
from .frontier_api import FrontierAPI
from .test_double import FakeBackend

__all__ = ["ModelBackend", "LocalAdapter", "FrontierAPI", "FakeBackend"]

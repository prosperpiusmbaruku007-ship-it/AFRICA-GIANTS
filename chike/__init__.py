"""Chike v16 — product package.

Every module here is deterministic EXCEPT the paths that go through a language model
via chike.model_abstraction — chike.extraction (slot filling) and chike.orchestrator's
generate stage. This is the enforced version of the core principle: facts and
arithmetic never live in model weights. See docs/CHIKE_V16_SPEC.md.

This __init__ is intentionally minimal (no eager submodule imports), so importing any
one submodule never drags in the rest of the package's dependency graph.
"""

__version__ = "16.0.0-dev"

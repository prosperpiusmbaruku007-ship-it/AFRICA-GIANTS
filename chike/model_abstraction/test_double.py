"""FakeBackend — a deterministic ModelBackend for tests.

Design principle (preserved verbatim from the v16 build session):
    Lets the orchestrator and any generation path be tested end-to-end with no
    network and no GPU, which is the only way the pipeline is testable today.

The double has two response modes and always records what it was asked:
  1. Scripted — return a fixed reply, or pop the next reply from a queue, so a
     test can pin the exact model output an orchestrator path will see.
  2. Echo — with no script configured, return the prompt truncated to
     `echo_limit` chars, so a test can assert *which* prompt reached the model.
Every call is appended to `.calls` for post-hoc assertions (count, order, params).
"""

from typing import Optional

from .base import ModelBackend


class FakeBackend(ModelBackend):
    """Deterministic stand-in for a real model backend. No network, no GPU.

    Args:
        scripted_reply: a single canned reply returned for every generate() call.
        replies: an ordered sequence of replies consumed one per call; when it is
            exhausted the backend falls back to `scripted_reply`, then to echo.
        echo_limit: max characters of the prompt returned in echo mode.
    """

    def __init__(
        self,
        scripted_reply: Optional[str] = None,
        replies: Optional[list] = None,
        echo_limit: int = 200,
    ):
        self.scripted_reply = scripted_reply
        self._replies = list(replies) if replies else []
        self.echo_limit = echo_limit
        self.calls = []  # list of {"prompt": str, "params": Optional[dict]}

    def generate(self, prompt: str, params: Optional[dict] = None) -> str:
        # Record first so an assertion holds even if a later branch raises.
        self.calls.append({"prompt": prompt, "params": params})

        if self._replies:
            return self._replies.pop(0)
        if self.scripted_reply is not None:
            return self.scripted_reply
        return prompt[: self.echo_limit]

    @property
    def call_count(self) -> int:
        return len(self.calls)

    @property
    def last_prompt(self) -> Optional[str]:
        return self.calls[-1]["prompt"] if self.calls else None

    def reset(self) -> None:
        """Clear recorded calls (does not restore a consumed reply queue)."""
        self.calls = []

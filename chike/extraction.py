"""Slot extraction interface — parse a sub-question into typed fields WITH confidence.

INTERFACE SHAPE ONLY. This item defines the contract the orchestrator's compute
route depends on; it does NOT tune extraction accuracy, confidence thresholds, or
clarification copy — all of which need real ambiguous-phrasing data that does not
exist yet (PROGRESS.md milestone 5 gap).

The routing contract this enforces:
  - every required field must come back present AND high-confidence before the
    orchestrator may call the rules engine;
  - a required field that is ABSENT, or present but LOW-confidence, is treated
    IDENTICALLY to a missing field -> the orchestrator asks for clarification and
    never feeds the rules engine a guessed value. A wrong compliance number is
    worse than a clarifying question (results.py auditability / R8 trust invariant).
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

from .model_abstraction import ModelBackend


class Confidence(Enum):
    """Categorical confidence emitted per field. Deliberately NOT a numeric score —
    no threshold is set at this stage (see _is_usable TODO)."""

    HIGH = "high"
    LOW = "low"


# Required fields per rules_engine computation type — mirrors the compute_* signatures
# (sdl.py, nssf.py, paye.py, wcf.py). The orchestrator asks for exactly these.
REQUIRED_FIELDS = {
    "sdl": ("gross_monthly_payroll", "employee_count"),
    "nssf": ("gross_monthly_payroll",),
    "wcf": ("gross_monthly_payroll",),
    "paye": ("monthly_salary",),
}


@dataclass(frozen=True)
class ExtractedField:
    """One structured field with its confidence — never a bare value."""

    name: str
    value: object
    confidence: Confidence


@dataclass(frozen=True)
class Extraction:
    """The result of extracting fields from one sub-question.

    `fields` maps field name -> ExtractedField. A required field simply absent from
    this map is 'missing'; one present but not usable-confidence is 'low' — the
    routing contract (usable) treats both the same.
    """

    fields: dict

    def get(self, name) -> Optional[ExtractedField]:
        return self.fields.get(name)

    def missing(self, required: Sequence[str]) -> list:
        """Required field names with no extracted value at all."""
        return [n for n in required if n not in self.fields]

    def low_confidence(self, required: Sequence[str]) -> list:
        """Required field names that were extracted but are not usable-confidence."""
        return [
            n for n in required
            if n in self.fields and not _is_usable(self.fields[n].confidence)
        ]

    def usable(self, required: Sequence[str]) -> bool:
        """True only when every required field is present AND usable-confidence.
        Absent-or-low is treated identically — the never-guess contract."""
        return not self.missing(required) and not self.low_confidence(required)


def _is_usable(confidence: Confidence) -> bool:
    # TODO: requires real ambiguous-phrasing test data — see PROGRESS.md milestone 5 gap.
    # The confidence policy (which levels count as usable, or a numeric cutoff if the
    # model ever emits graded scores) must be calibrated on real ambiguous Swahili
    # phrasings before any threshold value is fixed. For the interface shape, only
    # HIGH is usable — this is a placeholder rule, NOT a tuned threshold.
    return confidence is Confidence.HIGH


class SlotExtractor:
    """Extracts fields-with-confidence from a sub-question via an injected ModelBackend.

    Same dependency-injection contract as the orchestrator: tests pass a FakeBackend
    with scripted JSON replies to exercise the parsing and the never-guess contract
    with no network and no GPU. Real extraction accuracy is out of scope until real
    ambiguous-phrasing data exists.
    """

    def __init__(self, backend: ModelBackend, params: Optional[dict] = None):
        self.backend = backend
        self.params = params

    def extract(self, sub_question: str, required: Sequence[str]) -> Extraction:
        prompt = self._build_prompt(sub_question, required)
        raw = self.backend.generate(prompt, self.params)
        return self._parse(raw)

    @staticmethod
    def _build_prompt(sub_question: str, required: Sequence[str]) -> str:
        fields = ", ".join(required)
        return (
            f"Toa sehemu hizi kutoka kwa swali kama JSON: {fields}.\n"
            'Kila sehemu iwe {"value": <namba>, "confidence": "high" au "low"}.\n'
            f"Swali: {sub_question}"
        )

    @staticmethod
    def _parse(raw: str) -> Extraction:
        """Parse the model's JSON reply into fields-with-confidence.

        Anything unparseable, or a field with an unrecognised confidence label, is
        conservatively dropped or downgraded so it can never be silently treated as
        a confident value. Malformed output therefore routes to clarification, not a
        guess — the fail-safe direction for a compliance number.
        """
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return Extraction(fields={})

        fields = {}
        if isinstance(data, dict):
            for name, spec in data.items():
                if not isinstance(spec, dict) or "value" not in spec:
                    continue
                label = str(spec.get("confidence", "")).lower()
                try:
                    confidence = Confidence(label)
                except ValueError:
                    confidence = Confidence.LOW  # unknown label -> never usable
                fields[name] = ExtractedField(name, spec["value"], confidence)
        return Extraction(fields=fields)

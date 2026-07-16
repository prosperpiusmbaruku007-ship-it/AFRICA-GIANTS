"""Slot extraction — parse a sub-question into typed fields WITH confidence.

ARCHITECTURE (built 2026-07-16, replacing the interface-only stub)
Two layers with a deliberate division of trust:

  1. MODEL layer (free-text role assignment): a ModelBackend is asked which number in
     the sub-question is the payroll, which is the headcount, etc. — the model's genuine
     strength. It returns JSON {field: {value, confidence}}.

  2. DETERMINISTIC layer (confidence + clarification, chike.swahili_numbers): every value
     and confidence the model produced is then validated by pure, unit-tested Python. This
     layer OWNS the never-guess guardrail because this session proved a 32B model — let
     alone the 8B — misreads Swahili compound numerals and mis-detects ambiguity
     (PROGRESS.md qwen3-32b finding). It can only ever DOWNGRADE confidence (force a field
     to LOW -> clarification) or apply a deterministic period conversion; it never invents
     a value the model didn't propose. Its rules are explicit and inspectable here, not
     hidden in a prompt.

The routing contract the orchestrator depends on is unchanged:
  - every required field must be present AND high-confidence before the rules engine runs;
  - an absent OR low-confidence required field is treated identically -> clarification.
    A wrong compliance number is worse than a clarifying question (R8 trust invariant).

Failure categories from the reviewed slot-extraction stress test and how they resolve:
  vague_quantity / casual_slang(approx) / missing_antecedent / wrong_calculation_number /
  gross_net_allowance      -> a deterministic detector fires -> field forced LOW -> clarify.
  swahili_number_words      -> deterministic numeral cross-check validates the model's value.
  period_conversion         -> deterministic monthly conversion (or clarify if week/day).
  aggregate_vs_per_person /
  non_uniform_figures        -> the model does the summation/role split; guarded by the
                               numeral cross-check and the ambiguity vetoes above.
"""

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Optional, Sequence

from .model_abstraction import ModelBackend
from . import swahili_numbers as swn


class Confidence(Enum):
    """Categorical per-field confidence. Only HIGH is usable (never-guess); LOW or
    absent both route to clarification."""

    HIGH = "high"
    LOW = "low"


# Required fields per rules_engine computation type — mirrors the compute_* signatures.
REQUIRED_FIELDS = {
    "sdl": ("gross_monthly_payroll", "employee_count"),
    "nssf": ("gross_monthly_payroll",),
    "wcf": ("gross_monthly_payroll",),
    "paye": ("monthly_salary",),
}

# Field classes the deterministic layer reasons about.
_AMOUNT_FIELDS = frozenset({"gross_monthly_payroll", "monthly_salary"})
_COUNT_FIELDS = frozenset({"employee_count"})


@dataclass(frozen=True)
class ExtractedField:
    """One structured field with its confidence — never a bare value."""

    name: str
    value: object
    confidence: Confidence
    reason: str = ""          # why this confidence (which detector fired) — inspectable


@dataclass(frozen=True)
class Extraction:
    """Result of extracting fields from one sub-question. `fields` maps name ->
    ExtractedField. Absent == missing; present-but-LOW == low; usable() treats both same."""

    fields: dict

    def get(self, name) -> Optional[ExtractedField]:
        return self.fields.get(name)

    def missing(self, required: Sequence[str]) -> list:
        return [n for n in required if n not in self.fields]

    def low_confidence(self, required: Sequence[str]) -> list:
        return [n for n in required
                if n in self.fields and not _is_usable(self.fields[n].confidence)]

    def usable(self, required: Sequence[str]) -> bool:
        """True only when every required field is present AND usable-confidence."""
        return not self.missing(required) and not self.low_confidence(required)

    def clarification_reasons(self, required: Sequence[str]) -> list:
        """Human-readable reasons a required field blocked the compute path — for the
        Kaggle stress-test report and any future clarification copy."""
        out = []
        for n in required:
            f = self.fields.get(n)
            if f is None:
                out.append(f"{n}: missing")
            elif not _is_usable(f.confidence):
                out.append(f"{n}: low ({f.reason or 'model'})")
        return out


def _is_usable(confidence: Confidence) -> bool:
    return confidence is Confidence.HIGH


class SlotExtractor:
    """Extracts fields-with-confidence from a sub-question via an injected ModelBackend
    plus the deterministic chike.swahili_numbers layer. Dependency-injection contract is
    unchanged: tests pass a FakeBackend with scripted JSON to exercise parsing + the
    never-guess contract with no network and no GPU."""

    def __init__(self, backend: ModelBackend, params: Optional[dict] = None):
        self.backend = backend
        self.params = params

    def extract(self, sub_question: str, required: Sequence[str],
                computation_type: Optional[str] = None) -> Extraction:
        raw = self.backend.generate(self._build_prompt(sub_question, required), self.params)
        model_fields = self._parse(raw)
        return self._apply_deterministic_layer(sub_question, model_fields, computation_type)

    # --- model prompt (free-text role assignment) --------------------------

    @staticmethod
    def _build_prompt(sub_question: str, required: Sequence[str]) -> str:
        fields = ", ".join(required)
        return (
            "Wewe ni kifaa cha kutoa namba kwa hesabu za kodi Tanzania. Toa sehemu hizi "
            f"kutoka kwa swali kama JSON: {fields}.\n"
            'Kila sehemu iwe {"value": <namba kamili kwa shilingi/idadi>, '
            '"confidence": "high" au "low"}.\n'
            "KANUNI: ikiwa namba haijatajwa wazi, ni ya kukisia, au swali linatumia maneno "
            'ya kukadiria (wachache, kama, hivi) — weka "confidence": "low" au acha sehemu '
            "hiyo. Kwa mishahara mingi jumlisha; kwa mshahara wa kila mmoja zidisha na idadi.\n"
            "Mifano:\n"
            '  "wafanyakazi 12 kila mmoja laki tano" -> {"gross_monthly_payroll": '
            '{"value": 6000000, "confidence": "high"}, "employee_count": {"value": 12, '
            '"confidence": "high"}}\n'
            '  "wafanyakazi wachache" -> {"employee_count": {"value": 0, "confidence": "low"}}\n'
            f"Swali: {sub_question}"
        )

    @staticmethod
    def _parse(raw: str) -> dict:
        """Parse the model JSON into {name: (value, Confidence)}. Anything unparseable or
        an unrecognised confidence label is dropped/downgraded so it can never be silently
        treated as confident — malformed output routes to clarification, not a guess."""
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
        fields = {}
        if isinstance(data, dict):
            for name, spec in data.items():
                if not isinstance(spec, dict) or "value" not in spec:
                    continue
                label = str(spec.get("confidence", "")).lower()
                try:
                    confidence = Confidence(label)
                except ValueError:
                    confidence = Confidence.LOW      # unknown label -> never usable
                fields[name] = (spec["value"], confidence)
        return fields

    # --- deterministic layer (confidence + clarification) ------------------

    def _apply_deterministic_layer(self, sub_question, model_fields, computation_type):
        """Validate/adjust the model's fields. Only ever downgrades confidence or applies
        a deterministic period conversion — never invents a value."""
        vague = swn.detect_vague_quantity(sub_question)
        approx = swn.detect_approximation(sub_question)
        antecedent = swn.detect_missing_antecedent(sub_question)
        wrong_base = swn.detect_wrong_base(sub_question, computation_type)
        allowance = swn.detect_allowance_ambiguity(sub_question)
        divisor, period = swn.detect_period(sub_question)
        det_amounts = swn.parse_amounts(sub_question)
        det_count = swn.parse_count(sub_question)

        out = {}
        for name, (value, conf) in model_fields.items():
            reason = ""
            # period conversion for amount fields (deterministic, authoritative)
            if name in _AMOUNT_FIELDS and divisor is None:
                conf, reason = Confidence.LOW, f"period={period} needs days/weeks worked"
            elif name in _AMOUNT_FIELDS and divisor and divisor > 1 and len(det_amounts) == 1:
                converted = det_amounts[0] / Decimal(divisor)
                value, conf, reason = converted, Confidence.HIGH, f"converted {period}->monthly /{divisor}"

            # ambiguity vetoes (force LOW). Order: most specific reason wins.
            if name in _AMOUNT_FIELDS and wrong_base:
                conf, reason = Confidence.LOW, "wrong_base (non-payroll figure)"
            elif name in _AMOUNT_FIELDS and allowance:
                conf, reason = Confidence.LOW, "allowance/gross-net base ambiguous"
            if vague:
                conf, reason = Confidence.LOW, "vague_quantity"
            elif approx:
                conf, reason = Confidence.LOW, "approximation"
            elif antecedent:
                conf, reason = Confidence.LOW, "missing_antecedent"

            # numeral cross-check: single-figure question, model value disagrees with the
            # deterministic parse -> can't trust it (the model's Swahili-numeral weakness).
            if (name in _AMOUNT_FIELDS and conf is Confidence.HIGH
                    and not reason and det_count is None and len(det_amounts) == 1):
                mv = _to_decimal(value)
                if mv is not None and mv != det_amounts[0]:
                    conf, reason = Confidence.LOW, f"numeral mismatch (model {mv} vs parsed {det_amounts[0]})"
            if (name in _COUNT_FIELDS and conf is Confidence.HIGH and det_count is not None):
                if _to_decimal(value) != Decimal(det_count):
                    conf, reason = Confidence.LOW, f"count mismatch (model {value} vs parsed {det_count})"

            out[name] = ExtractedField(name, value, conf, reason)
        return Extraction(fields=out)


def _to_decimal(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None

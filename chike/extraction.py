"""Slot extraction — parse a sub-question into typed fields WITH confidence.

ARCHITECTURE (trust-inverted 2026-07-17 after real-model evidence)
The v15 debug run (extraction_raw_debug.json) proved the production 8B model does NOT
return field-extraction JSON: it ignores the extraction instruction and answers the
compliance question directly — computing a figure and citing tra.go.tz — and its
arithmetic is wrong in exactly the ways documented this session (annual/monthly not
converted, wrong tax type, Swahili compound numerals misread). The deterministic parser
got all four debug cases right with zero model involvement. So the trust order is inverted:

  1. DETERMINISTIC layer (chike.swahili_numbers) is PRIMARY. It ORIGINATES the field
     values: parses the Swahili numerals (scale-first, unit-tested), does the
     per-person x count multiplication and the period->monthly conversion itself, and
     owns the never-guess guardrail via explicit, inspectable ambiguity detectors
     (vague / approximation / missing-antecedent / wrong-base / allowance-or-VAT).

  2. MODEL layer is a NARROW FALLBACK, used only for what regex genuinely cannot do:
     when the deterministic parser found NO value for a field, a clean role-assignment
     JSON from the model may supply it. But the model is NEVER trusted to output a final
     calculated answer or citation during extraction — if its raw output looks like a
     compliance answer (currency/percent/citation/"jibu"), it is discarded entirely,
     because that means it went off-script and is not trustworthy extractor input.

The routing contract the orchestrator depends on is unchanged:
  - every required field must be present AND high-confidence before the rules engine runs;
  - an absent OR low-confidence required field is treated identically -> clarification.
    A wrong compliance number is worse than a clarifying question (R8 trust invariant).

Failure categories from the reviewed stress test and how they resolve:
  vague_quantity / casual_slang(approx) / missing_antecedent / wrong_calculation_number /
  gross_net_allowance      -> a deterministic detector fires -> field LOW -> clarify.
  swahili_number_words      -> deterministic numeral parse originates the value.
  period_conversion         -> deterministic monthly conversion (or clarify if week/day).
  aggregate_vs_per_person   -> "kila" multiplies; "jumla/yote" is a total; conflicting or
                               bare-with-count -> clarify (never guess the base).
  non_uniform_figures        -> multiple distinct figures -> role ambiguous -> clarify.
"""

import json
import re
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

# Reduced fields for an applicability-only ('does this levy apply?') answer — no salary.
# SDL needs only the headcount (10-employee threshold); NSSF/WCF have no threshold, so
# their applicability needs nothing. PAYE is absent (its applicability needs salary).
APPLICABILITY_REQUIRED_FIELDS = {
    "sdl": ("employee_count",),
    "nssf": (),
    "wcf": (),
}

# Field classes the deterministic layer reasons about.
_AMOUNT_FIELDS = frozenset({"gross_monthly_payroll", "monthly_salary"})
_COUNT_FIELDS = frozenset({"employee_count"})

# "each"/"per employee" markers -> a stated figure is PER PERSON (multiply by count).
_PER_PERSON = re.compile(r"kila\s+(?:mmoja|mfanyakazi|mtu|mmojawapo|mwajiriwa|kichwa)")
# aggregate markers -> a stated figure is already the WHOLE payroll (do not multiply).
_AGGREGATE = re.compile(r"\bjumla\b|\byote\b|\bwote\b|kwa\s+pamoja|payroll\s+yote")
# off-script markers -> the model answered the compliance question instead of extracting;
# its output is discarded for extraction purposes (currency / percent / citation / answer).
_OFFSCRIPT = re.compile(
    r"go\.tz|shilingi|\btzs\b|\btsh\b|asilimia|%|kulingana na|\bjibu\b|\bfaini\b|\bsheria\b",
    re.IGNORECASE,
)


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
    """Extracts fields-with-confidence from a sub-question. The deterministic
    chike.swahili_numbers layer originates the values; the injected ModelBackend is a
    narrow fallback for role assignment when regex found nothing. Dependency-injection
    contract is unchanged: tests pass a FakeBackend with scripted JSON to exercise the
    fallback + never-guess contract with no network and no GPU."""

    def __init__(self, backend: ModelBackend, params: Optional[dict] = None):
        self.backend = backend
        self.params = params

    def extract(self, sub_question: str, required: Sequence[str],
                computation_type: Optional[str] = None) -> Extraction:
        # The model is consulted exactly once (DI contract), but it is now a FALLBACK:
        # deterministic values win, and the model is used only where regex found nothing
        # AND the model did not go off-script into a compliance answer.
        raw = self.backend.generate(self._build_prompt(sub_question, required), self.params)
        offscript = bool(_OFFSCRIPT.search(raw or ""))
        model_fields = {} if offscript else self._parse(raw)
        return self._reconcile(sub_question, required, computation_type, model_fields)

    def _reconcile(self, sub_question: str, required: Sequence[str],
                   computation_type: Optional[str], model_fields: dict) -> Extraction:
        """Merge deterministic values (primary) with model-proposed fields (fallback) into
        an Extraction, so the never-guess reconciliation is identical for every field."""
        det, global_veto = self._deterministic(sub_question, required, computation_type)

        out = {}
        for name in required:
            d = det.get(name)
            if d is not None:
                value, conf, reason = d
                if global_veto:                     # vague/approx/antecedent overrides all
                    conf, reason = Confidence.LOW, global_veto
            elif not global_veto and name in model_fields:
                # deterministic found nothing here and the model output was clean JSON —
                # accept the model's proposal (role assignment regex can't do).
                mval, mconf = model_fields[name]
                value, conf, reason = mval, mconf, "model fallback (no deterministic value)"
            else:
                continue                            # absent -> missing -> clarify
            out[name] = ExtractedField(name, value, conf, reason)
        return Extraction(fields=out)

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
        """Parse a CLEAN role-assignment JSON into {name: (value, Confidence)}. Strict:
        the whole string must be JSON (a compliance answer in prose fails here and yields
        {}), and an unrecognised confidence label is downgraded — malformed or off-script
        output can never be silently treated as a confident value."""
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
        return SlotExtractor._parse_field_dict(data)

    @staticmethod
    def _parse_field_dict(data) -> dict:
        """Parse {name: {"value":..,"confidence":..}} into {name: (value, Confidence)}.
        Ignores a leading 'intent' key (used by the backstop) and any non-field entries;
        an unknown confidence label downgrades to LOW so it is never usable."""
        fields = {}
        if isinstance(data, dict):
            for name, spec in data.items():
                if name == "intent" or not isinstance(spec, dict) or "value" not in spec:
                    continue
                label = str(spec.get("confidence", "")).lower()
                try:
                    confidence = Confidence(label)
                except ValueError:
                    confidence = Confidence.LOW      # unknown label -> never usable
                fields[name] = (spec["value"], confidence)
        return fields

    # --- deterministic layer (PRIMARY: originates values + owns clarification) ----

    def _deterministic(self, text, required, computation_type):
        """Originate field values from the Swahili numeral parser. Returns
        (det, global_veto) where det maps name -> (value, Confidence, reason) for every
        field the deterministic layer has an opinion on (HIGH value or LOW veto), and
        omits fields it found nothing for (those may fall back to the model). global_veto
        is a whole-question clarification reason (vague/approx/antecedent) or None."""
        tl = text.lower()
        vague = swn.detect_vague_quantity(text)
        approx = swn.detect_approximation(text)
        antecedent = swn.detect_missing_antecedent(text)
        wrong_base = swn.detect_wrong_base(text, computation_type)
        allowance = swn.detect_allowance_ambiguity(text)
        foreign_currency = swn.detect_foreign_currency(text)
        divisor, period = swn.detect_period(text)

        per_person = bool(_PER_PERSON.search(tl))
        aggregate = bool(_AGGREGATE.search(tl))
        # Parse amounts from a copy with the per-person phrase removed: "kila mmoja"
        # otherwise contributes a spurious "1" ("mmoja") that makes a single stated
        # salary look like multiple figures. per_person is already captured above.
        amt_source = _PER_PERSON.sub(" ", text)
        amounts = swn.parse_amounts(amt_source)
        count = swn.parse_count(text)
        if count is not None:                        # don't let the headcount pose as money
            amounts = [a for a in amounts if a != Decimal(count)]

        global_veto = ("vague_quantity" if vague else "approximation" if approx
                       else "missing_antecedent" if antecedent else None)
        # PREREQ-2 (A2): the hedge describes what the speaker FIRST said, and the same
        # sentence then supplies an exact figure and marks it exact ("wengi sana karibu,
        # LAKINI HASA NI 18"). Discarding that figure asks the user to repeat what they
        # already told us precisely. Only lifts the vague/approximation veto — a missing
        # antecedent is a genuinely unresolvable reference and is never overridden.
        if global_veto in ("vague_quantity", "approximation") \
                and swn.has_precision_override(text):
            global_veto = None

        # PREREQ-2 (J + A2): when several figures were parsed, _amount_field gives up as
        # "role ambiguous". If exactly ONE of them is explicitly anchored as the amount — by a
        # payroll word ("ina MISHAHARA TZS 4,800,000 ... na madeni TZS 2,000,000") or by a
        # precision marker ("sawa TZS 610,000 KAMILI") — the role is not ambiguous at all.
        # Collapsing to that figure engages ONLY where the parser had already given up; two
        # anchored figures or none leaves the ambiguity, and the clarification, intact.
        payroll_anchored = False
        if len(amounts) > 1:
            anchored, anchor_kind = swn.select_anchored_amount(text, amounts)
            if anchored is not None:
                amounts = [anchored]
                # A figure the user LABELLED as payroll is a payroll base, whatever other
                # non-payroll words the sentence also contains ("ina MISHAHARA TZS 4,800,000
                # kwa watu 13, na madeni ..., na FAIDA ..." — eval_324). Without this the
                # wrong_base detector vetoes the very figure the anchor just identified.
                # Only the payroll anchor grants this; a precision anchor does not.
                payroll_anchored = anchor_kind == "payroll"
        if payroll_anchored:
            wrong_base = False

        # PATTERN D. A per-unit rate times an explicitly per-MONTH quantity states ONE PERSON'S
        # monthly pay ("TZS 18,000 kwa siku, siku 26 kwa mwezi"). It is NEVER a payroll, so SDL
        # — the only levy whose answer depends on the TOTAL payroll and a headcount threshold —
        # must not receive it without a headcount. eval_294 is a single driver on TZS 80,000 x
        # 15 trips and its gold explicitly refuses "SDL = 3.5% x 1,200,000"; this gate is what
        # makes that refusal survive, and it is asserted directly rather than left to the
        # required-fields contract to enforce as a side effect.
        unit_rate_monthly = swn.monthly_from_unit_rate(text)
        if (unit_rate_monthly is not None
                and computation_type == "sdl" and count is None):
            unit_rate_monthly = None

        # PATTERN F1. When one levy's own clause names its payroll ("SDL ya jumla ya mishahara
        # ya TZS 7,600,000"), that figure belongs to THAT levy and the sibling levy in the same
        # question keeps whatever single plausible figure is left over. Both gates live in
        # levy_labelled_payroll: a resolved group parse always wins, and the amount must be a
        # payroll-label genitive rather than merely the nearest number. eval_327 is the row the
        # proximity version would have broken and is pinned by name in the probes.
        labelled = swn.levy_labelled_payroll(text)
        if labelled:
            if computation_type in labelled:
                amounts = [labelled[computation_type]]
                if count is None:
                    # The question poses the POST-crossing scenario ("nikiongeza ... kufikia
                    # 10, SDL ... itakuwa ngapi") — the crossing count is the one it asks about.
                    count = swn.crossing_headcount(text)
            else:
                claimed = set(labelled.values())
                left = [a for a in swn.parse_amounts(text)
                        if a >= swn.MIN_PLAUSIBLE_AMOUNT and a not in claimed]
                if len(left) == 1:
                    amounts = left

        det = {}
        amount_field = next((f for f in required if f in _AMOUNT_FIELDS), None)
        if amount_field:
            a = self._amount_field(amount_field, amounts, count, per_person, aggregate,
                                   divisor, period, wrong_base, allowance, foreign_currency,
                                   unit_rate_monthly)
            if a is not None:
                det[amount_field] = a
        if any(f in _COUNT_FIELDS for f in required):
            # The precision override applies to the COUNT too: "wengi sana karibu, LAKINI HASA
            # NI 18" is a vetoed count that the same sentence states exactly (eval_279/280).
            c = self._count_field(count, vague and global_veto is not None)
            if c is not None:
                det["employee_count"] = c
        return det, global_veto

    @staticmethod
    def _amount_field(field, amounts, count, per_person, aggregate,
                      divisor, period, wrong_base, allowance, foreign_currency=False,
                      unit_rate_monthly=None):
        """Return (value, Confidence, reason) for an amount field, or None if the parser
        found no figure (leave it to the model fallback). LOW result == clarify."""
        if not amounts and unit_rate_monthly is None:
            return None

        # PATTERN D resolves the 'role ambiguous' pair itself: the two figures are a rate and a
        # quantity, not two candidate salaries. It also makes the period conversion moot — the
        # product is ALREADY monthly — so the divisor branch below is skipped, which is what
        # eval_296 ("kwa siku ... siku 26 kwa mwezi") needs: without this it would fall into
        # 'period=daily needs days/weeks worked' having just been told the days.
        if unit_rate_monthly is not None:
            amt, reason = unit_rate_monthly, "per-unit rate x per-month quantity"
            if per_person and count is not None:
                amt, reason = amt * Decimal(count), f"{reason}; x {count} employees"
            if wrong_base:
                return (amt, Confidence.LOW, "wrong_base (non-payroll figure)")
            if foreign_currency:
                return (amt, Confidence.LOW,
                        "amount in foreign currency (not TZS) — needs conversion")
            return (amt, Confidence.HIGH, reason)

        if len(amounts) > 1:
            return (None, Confidence.LOW,
                    f"multiple figures {[str(a) for a in amounts]} — role ambiguous")

        amt, reason = amounts[0], "parsed amount"
        is_payroll = field == "gross_monthly_payroll"

        # SCOPE, not conflict (2026-08-08). "TZS 480,000 KILA MMOJA ... NSSF ya WOTE" reads as
        # two contradictory markers only if both are taken to govern the same thing. They do
        # not: 'kila mmoja' governs the SALARY clause, 'jumla/wote' governs the ASK. When the
        # headcount is known there is exactly one arithmetic reading — per-person x headcount
        # IS the aggregate the question asks for — so resolve it instead of vetoing it.
        # eval_280 and eval_319 were both judge-confirmed CORRECT in v15 and became
        # clarifications here; eval_275 was asked "per person or total?" when both were stated
        # and the real gap was the FX rate (that veto sits further down and still fires).
        # The veto stands wherever the pairing CANNOT be resolved arithmetically — no
        # headcount, or several figures (len(amounts) > 1 has already returned above, so a
        # missing count is the only remaining case). Probe hc_10 pins the multi-figure case.
        if is_payroll and per_person and aggregate and count is None:
            return (None, Confidence.LOW, 'conflicting "kila" and "jumla/yote" — base ambiguous')
        if is_payroll and per_person and count is not None:
            # "kila mmoja ... X" -> X is per person, payroll = X * headcount.
            amt, reason = amt * Decimal(count), f"per-person {amounts[0]} x {count}"
        # A single stated figure with no "kila"/"jumla" marker is taken as the payroll base
        # (the established orchestrator contract); the truly dangerous cases — conflicting
        # markers, multiple distinct figures, vague/approx/wrong-base/allowance — are vetoed
        # elsewhere. We never guess a base we cannot see.

        if divisor is None:                          # week/day: needs days-worked -> clarify
            return (amt, Confidence.LOW, f"period={period} needs days/weeks worked")
        if divisor > 1:
            amt, reason = amt / Decimal(divisor), f"{reason}; /{divisor} {period}->monthly"

        if wrong_base:
            return (amt, Confidence.LOW, "wrong_base (non-payroll figure)")
        if allowance:
            return (amt, Confidence.LOW, "allowance/gross-net/VAT base ambiguous")
        if foreign_currency:                          # RC-3: not TZS -> needs conversion
            return (amt, Confidence.LOW, "amount in foreign currency (not TZS) — needs conversion")
        if amt < swn.MIN_PLAUSIBLE_AMOUNT:            # RC-2: too small to be a payroll
            return (amt, Confidence.LOW,
                    f"implausibly small for a payroll ({amt}) — likely a count/quantity")
        return (amt, Confidence.HIGH, reason)

    @staticmethod
    def _count_field(count, vague):
        if count is None:
            return None
        if vague:
            return (count, Confidence.LOW, "vague_quantity")
        return (int(count), Confidence.HIGH, "parsed count")


def _to_decimal(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None

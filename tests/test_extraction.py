"""Tests for chike.extraction — the slot extraction INTERFACE mechanics only.

These exercise the plumbing with FakeBackend scripted replies: that a well-formed
response parses into fields-with-confidence, that an uncertainty signal becomes
low-confidence, and that an absent required field is flagged missing. They do NOT
test real extraction accuracy — that stays blocked pending real ambiguous-phrasing
data (PROGRESS.md milestone 5 gap).
"""
from chike.extraction import (
    SlotExtractor,
    Extraction,
    ExtractedField,
    Confidence,
    REQUIRED_FIELDS,
)
from chike.model_abstraction import FakeBackend


SDL_REQUIRED = REQUIRED_FIELDS["sdl"]  # ("gross_monthly_payroll", "employee_count")


# --- Well-formed response parses into fields WITH confidence ----------------

def test_well_formed_response_parses_into_high_confidence_fields():
    reply = (
        '{"gross_monthly_payroll": {"value": 6750000, "confidence": "high"}, '
        '"employee_count": {"value": 15, "confidence": "high"}}'
    )
    ext = SlotExtractor(FakeBackend(scripted_reply=reply)).extract("swali", SDL_REQUIRED)

    assert isinstance(ext, Extraction)
    gross = ext.get("gross_monthly_payroll")
    assert isinstance(gross, ExtractedField)
    assert gross.value == 6750000
    assert gross.confidence is Confidence.HIGH            # paired confidence, not a flat value
    assert ext.usable(SDL_REQUIRED) is True               # all required present + high


def test_extractor_returns_confidence_per_field_not_a_flat_dict():
    reply = (
        '{"gross_monthly_payroll": {"value": 6750000, "confidence": "high"}, '
        '"employee_count": {"value": 15, "confidence": "low"}}'
    )
    ext = SlotExtractor(FakeBackend(scripted_reply=reply)).extract("swali", SDL_REQUIRED)

    assert ext.get("gross_monthly_payroll").confidence is Confidence.HIGH
    assert ext.get("employee_count").confidence is Confidence.LOW


# --- Uncertainty signal -> low confidence -> not usable ---------------------

def test_low_confidence_field_makes_extraction_unusable():
    reply = (
        '{"gross_monthly_payroll": {"value": 6750000, "confidence": "low"}, '
        '"employee_count": {"value": 15, "confidence": "high"}}'
    )
    ext = SlotExtractor(FakeBackend(scripted_reply=reply)).extract("swali", SDL_REQUIRED)

    assert ext.low_confidence(SDL_REQUIRED) == ["gross_monthly_payroll"]
    assert ext.usable(SDL_REQUIRED) is False              # low on a required field -> not usable


def test_unrecognised_confidence_label_is_downgraded_not_trusted():
    reply = '{"gross_monthly_payroll": {"value": 6750000, "confidence": "maybe"}}'
    ext = SlotExtractor(FakeBackend(scripted_reply=reply)).extract(
        "swali", ("gross_monthly_payroll",)
    )
    # An unknown label must never be treated as confident.
    assert ext.get("gross_monthly_payroll").confidence is Confidence.LOW
    assert ext.usable(("gross_monthly_payroll",)) is False


# --- Absent required field -> flagged missing -------------------------------

def test_absent_required_field_is_flagged_missing():
    # employee_count omitted entirely from the response.
    reply = '{"gross_monthly_payroll": {"value": 6750000, "confidence": "high"}}'
    ext = SlotExtractor(FakeBackend(scripted_reply=reply)).extract("swali", SDL_REQUIRED)

    assert ext.missing(SDL_REQUIRED) == ["employee_count"]
    assert ext.get("employee_count") is None
    assert ext.usable(SDL_REQUIRED) is False              # missing == not usable


def test_missing_and_low_confidence_are_treated_identically_by_usable():
    missing = SlotExtractor(FakeBackend(
        scripted_reply='{"gross_monthly_payroll": {"value": 1, "confidence": "high"}}'
    )).extract("q", SDL_REQUIRED)
    low = SlotExtractor(FakeBackend(
        scripted_reply=('{"gross_monthly_payroll": {"value": 1, "confidence": "high"}, '
                        '"employee_count": {"value": 15, "confidence": "low"}}')
    )).extract("q", SDL_REQUIRED)

    # The never-guess contract: absent and low-confidence both block the compute path.
    assert missing.usable(SDL_REQUIRED) is False
    assert low.usable(SDL_REQUIRED) is False


# --- Malformed / non-JSON output fails safe (routes to clarification) -------

def test_unparseable_response_yields_empty_extraction():
    ext = SlotExtractor(FakeBackend(scripted_reply="si JSON hata kidogo")).extract(
        "swali", SDL_REQUIRED
    )
    assert ext.fields == {}
    assert ext.missing(SDL_REQUIRED) == list(SDL_REQUIRED)
    assert ext.usable(SDL_REQUIRED) is False


# --- Dependency injection: extractor uses the injected backend --------------

def test_extractor_calls_the_injected_backend_with_the_sub_question():
    fake = FakeBackend(scripted_reply='{}')
    SlotExtractor(fake).extract("SDL kwa wafanyakazi 15", SDL_REQUIRED)

    assert fake.call_count == 1
    assert "SDL kwa wafanyakazi 15" in fake.last_prompt   # sub-question reached the model

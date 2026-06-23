import json
import os
import re

from src.synthetic.api_utils import call_with_cost_tracking, sum_cost_log_this_month

LOCKED_FACTS_PATH  = 'scripts/locked_facts.json'
PENDING_FACTS_PATH = 'data/flagged/new_facts_pending.json'

MONTHLY_CAP              = float(os.environ.get('MONTHLY_BUDGET', '20.0'))
COST_PER_DOCUMENT_BUDGET = float(os.environ.get('COST_PER_DOCUMENT_BUDGET', '0.20'))

MODEL = 'claude-sonnet-4-6'

EXTRACTION_SYSTEM = (
    "You are a compliance fact extractor for Tanzania business law. "
    "Extract only numerical facts, deadlines, rates, thresholds, and penalties. "
    "Respond ONLY with a JSON array. No preamble, no explanation, no markdown."
)

EXTRACTION_USER_TMPL = """Extract all compliance facts from this document section.
Output format (JSON array only):
[
  {{
    "fact_key": "snake_case identifier",
    "value": "exact value as stated",
    "unit": "% or TZS or days or employees or null",
    "source_section": "section heading where found",
    "effective_date": "YYYY-MM-DD or null"
  }}
]

Example input: "SDL rate is 3.5% of gross payroll, payable by the 7th"
Example output:
[
  {{"fact_key": "sdl_rate", "value": "3.5", "unit": "%",
   "source_section": "SDL Overview", "effective_date": null}},
  {{"fact_key": "sdl_deadline", "value": "7", "unit": "days_of_month",
   "source_section": "SDL Overview", "effective_date": null}}
]

Document section to extract from:
{section_content}"""


def _load_locked_facts() -> dict:
    try:
        with open(LOCKED_FACTS_PATH, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[facts] WARNING: {LOCKED_FACTS_PATH} not found")
        return {}


def extract_number_unit_pairs(text: str) -> set:
    pattern = r'(\d[\d,\.]*)\s*(%|TZS|milioni|asilimia|M\b|days?|employees?)'
    return set(re.findall(pattern, str(text), re.IGNORECASE))


def is_confirmed_fact(extracted: dict, locked_facts: dict) -> tuple:
    """Returns (True, matching_key) if matches a locked fact, else (False, None)."""
    extracted_pairs = extract_number_unit_pairs(extracted.get('value', ''))
    if not extracted_pairs:
        return False, None  # non-numerical -> human review queue
    for key, fact in locked_facts.items():
        if key == '_meta':
            continue
        locked_val = (fact.get('correct_value', str(fact))
                      if isinstance(fact, dict) else str(fact))
        locked_pairs = extract_number_unit_pairs(locked_val)
        if extracted_pairs and extracted_pairs == locked_pairs:
            return True, key
    return False, None


def _append_pending_fact(candidate: dict):
    pending = []
    if os.path.exists(PENDING_FACTS_PATH):
        try:
            with open(PENDING_FACTS_PATH, encoding='utf-8') as f:
                pending = json.load(f)
        except Exception:
            pending = []
    existing_keys = {c.get('fact_key') for c in pending}
    if candidate.get('fact_key') not in existing_keys:
        pending.append(candidate)
        os.makedirs(os.path.dirname(PENDING_FACTS_PATH), exist_ok=True)
        with open(PENDING_FACTS_PATH, 'w', encoding='utf-8') as f:
            json.dump(pending, f, indent=2, ensure_ascii=False)


def _parse_facts_response(raw: str) -> list:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    try:
        stripped = raw.split('```json')[-1].split('```')[0].strip()
        return json.loads(stripped)
    except (json.JSONDecodeError, IndexError):
        pass
    try:
        start = raw.index('[')
        end   = raw.rindex(']') + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        pass
    print(f"[facts] Failed to parse LLM response. Raw: {raw[:200]}")
    return []


def extract_facts(document: dict) -> list:
    """Extract confirmed facts from document sections via Claude API."""
    import anthropic
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        print("[facts] ANTHROPIC_API_KEY not set -- cannot extract facts")
        return []

    client       = anthropic.Anthropic(api_key=api_key)
    locked_facts = _load_locked_facts()
    confirmed    = []
    new_count    = 0
    source_doc   = document.get('source_document', '')

    for section in document.get('sections', []):
        content = section.get('content', '').strip()
        if len(content) < 50:
            continue

        user_msg = EXTRACTION_USER_TMPL.format(section_content=content[:4000])
        try:
            response = call_with_cost_tracking(
                client, 'fact_extractor',
                model=MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": user_msg}],
                system=EXTRACTION_SYSTEM,
            )
            raw = response.content[0].text
            extracted_list = _parse_facts_response(raw)
        except Exception as e:
            print(f"[facts] API error on section '{section.get('heading')}': {e}")
            continue

        for extracted in extracted_list:
            extracted['source_document'] = source_doc
            ok, _ = is_confirmed_fact(extracted, locked_facts)
            if ok:
                confirmed.append(extracted)
            else:
                _append_pending_fact(extracted)
                new_count += 1

    print(f"[facts] {document['source_file']}: {len(confirmed)} confirmed, {new_count} new candidates")
    if new_count > 0:
        print(f"[facts] Run 'python run.py approve-facts' to review new candidates")
    return confirmed


def check_budget_before_document(remaining_docs: int = 0,
                                  no_budget_check: bool = False) -> bool:
    if no_budget_check:
        return True
    current = sum_cost_log_this_month()
    if current + COST_PER_DOCUMENT_BUDGET > MONTHLY_CAP:
        print(f"[cost] Monthly cap ${MONTHLY_CAP:.2f} approaching.")
        print(f"[cost] Used: ${current:.4f} | Per-doc buffer: ${COST_PER_DOCUMENT_BUDGET:.2f}")
        if remaining_docs:
            print(f"[cost] {remaining_docs} documents unprocessed.")
        print(f"[cost] To continue: COST_PER_DOCUMENT_BUDGET=2.00 python run.py generate")
        print(f"[cost]              or: python run.py generate --no-budget-check")
        return False
    return True

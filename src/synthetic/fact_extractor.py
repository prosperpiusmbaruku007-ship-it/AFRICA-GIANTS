import json
import os
import re
import threading

from src.synthetic.api_utils import (
    call_with_cost_tracking, sum_cost_log_this_month,
    DEFAULT_MODEL, API_KEY, LLM_PROVIDER,
)

LOCKED_FACTS_PATH      = 'scripts/locked_facts.json'
PENDING_FACTS_PATH     = 'data/flagged/new_facts_pending.json'
CONFLICTING_FACTS_PATH = 'data/flagged/conflicting_facts.json'

# Folder categories whose facts are NEVER authoritative. Community/forum/blog sources
# (data/source_documents/general/) are valuable only for question PHRASING, not facts:
# every extracted fact is routed to pending for human review regardless of whether it
# matches a locked fact. This enforces CLAUDE.md R4 / Section 3 (citation laundering).
COMMUNITY_CATEGORIES = {'general'}

MONTHLY_CAP              = float(os.environ.get('MONTHLY_BUDGET', '20.0'))
COST_PER_DOCUMENT_BUDGET = float(os.environ.get('COST_PER_DOCUMENT_BUDGET', '0.20'))

# Parallel document processing means several threads may append new fact candidates
# at once. The pending/conflicting files are read-modify-write, so guard each with a
# lock to avoid lost updates.
_PENDING_FACTS_LOCK     = threading.Lock()
_CONFLICTING_FACTS_LOCK = threading.Lock()

EXTRACTION_SYSTEM = (
    "You are a compliance fact extractor for Tanzania business law. "
    "Documents may be in Swahili or English. "
    "Extract ALL of the following fact types — do not skip any:\n"
    "- Numerical rates and percentages\n"
    "- Employee count thresholds\n"
    "- Deadline dates (day of month)\n"
    "- Form numbers and codes\n"
    "- Legal citations (Act name, chapter number, section number)\n"
    "- Exemption categories (list each separately)\n"
    "- Penalty amounts\n"
    "Even if a fact appears in a list or bullet point — extract it. "
    "Respond ONLY with a JSON array. No preamble, no explanation, no markdown."
)

EXTRACTION_USER_TMPL = """Extract all compliance facts from this document section.
Extract ALL of the following fact types — do not skip any:
- Numerical rates and percentages
- Employee count thresholds
- Deadline dates (day of month)
- Form numbers and codes
- Legal citations (Act name, chapter number, section number)
- Exemption categories (list each separately)
- Penalty amounts
Even if a fact appears in a list or bullet point — extract it.

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


def _norm_pairs(text: str) -> set:
    """Normalized {(number, unit)} set: commas stripped, unit lowercased."""
    return {
        (num.replace(',', '').strip(), unit.strip().lower())
        for num, unit in extract_number_unit_pairs(text)
    }


def _locked_value_str(fact) -> str:
    if isinstance(fact, dict):
        return fact.get('correct_value', str(fact))
    return str(fact)


def classify_fact(extracted: dict, locked_facts: dict) -> tuple:
    """Classify an extracted fact against locked_facts.

    Returns (status, key) where status is one of:
      'confirmed' -- matches a locked fact; safe to generate pairs from.
      'conflict'  -- its fact_key is locked but the numeric value CONTRADICTS the
                     locked value (disjoint number/unit sets). Never confirm; route
                     to conflicting_facts.json so the locked fact is never overridden.
      'new'       -- not locked and no numeric match; route to pending for review.

    PRIORITY 1 -- direct fact_key match: once a fact_key is approved into
    locked_facts.json, a later extraction with that same key is confirmed without
    depending on identical number formatting. BUT if both sides carry numbers and
    they share NO common (number,unit) pair, that is a genuine contradiction
    (e.g. locked SDL 3.5% vs extracted 4.0%) -> 'conflict', not 'confirmed'.
    A formatting/partial diff (95,000 vs 95000, or a subset of numbers) still shares
    a pair and stays 'confirmed'.
    PRIORITY 2 -- normalized number/unit match against any locked fact, so a
    differently-named key whose value equals a locked value still confirms.
    SAFETY GUARD (added 2026-07-01): PRIORITY 2 only matches within the same
    domain prefix. A dense legal document (e.g. the 40-page NSSF Act) emits many
    percentages; without this guard attendance_allowance_rate:25% would confirm
    against a paye 25% band by pure numeric coincidence. Cross-prefix numeric
    matches are skipped so only genuinely same-domain values confirm.
    """
    fact_key = extracted.get('fact_key', '')
    combined = f"{extracted.get('value', '')} {extracted.get('unit', '')}".strip()
    norm_ex  = _norm_pairs(combined)

    # PRIORITY 1 -- direct fact_key match (with contradiction guard)
    if fact_key and fact_key in locked_facts:
        norm_lk = _norm_pairs(_locked_value_str(locked_facts[fact_key]))
        if norm_ex and norm_lk and norm_ex.isdisjoint(norm_lk):
            return 'conflict', fact_key
        return 'confirmed', fact_key

    # PRIORITY 2 -- normalized number/unit match against any locked fact,
    # restricted to the same domain prefix to avoid cross-domain false-confirms.
    if not norm_ex:
        return 'new', None
    extracted_prefix = fact_key.split('_')[0] if fact_key else ''
    for key, fact in locked_facts.items():
        if key == '_meta':
            continue
        locked_prefix = key.split('_')[0]
        if (extracted_prefix and locked_prefix and
                extracted_prefix != locked_prefix and
                extracted_prefix not in ('', 'general') and
                locked_prefix not in ('', 'general')):
            continue  # cross-domain numeric coincidence -- not a real match
        if norm_ex == _norm_pairs(_locked_value_str(fact)):
            return 'confirmed', key
    return 'new', None


def is_confirmed_fact(extracted: dict, locked_facts: dict) -> tuple:
    """Back-compat wrapper: (True, key) only when status is 'confirmed'."""
    status, key = classify_fact(extracted, locked_facts)
    return (status == 'confirmed'), (key if status == 'confirmed' else None)


def _append_pending_fact(candidate: dict):
    with _PENDING_FACTS_LOCK:
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


def _append_conflicting_fact(candidate: dict):
    """Record a practitioner/source value that contradicts a locked fact. The locked
    fact is NEVER overridden -- this is an audit queue for human review. Keyed on
    (fact_key, value) so distinct contradicting values are all retained."""
    with _CONFLICTING_FACTS_LOCK:
        conflicts = []
        if os.path.exists(CONFLICTING_FACTS_PATH):
            try:
                with open(CONFLICTING_FACTS_PATH, encoding='utf-8') as f:
                    conflicts = json.load(f)
            except Exception:
                conflicts = []
        sig = (candidate.get('fact_key'), str(candidate.get('value')))
        existing = {(c.get('fact_key'), str(c.get('value'))) for c in conflicts}
        if sig not in existing:
            conflicts.append(candidate)
            os.makedirs(os.path.dirname(CONFLICTING_FACTS_PATH), exist_ok=True)
            with open(CONFLICTING_FACTS_PATH, 'w', encoding='utf-8') as f:
                json.dump(conflicts, f, indent=2, ensure_ascii=False)


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
    # Attempt 4: salvage complete {...} objects from a truncated/broken array
    salvaged = _salvage_objects(raw)
    if salvaged:
        print(f"[parse] salvaged {len(salvaged)} objects from truncated response")
        return salvaged
    print(f"[facts] Failed to parse LLM response. Raw: {raw[:200]}")
    return []


def _salvage_objects(raw: str) -> list:
    """Extract every complete top-level {...} object even if the outer [] is broken
    (e.g. response truncated at max_tokens mid-array)."""
    objects = []
    depth = 0
    start = None
    in_str = False
    escape = False
    for i, ch in enumerate(raw):
        if in_str:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    try:
                        objects.append(json.loads(raw[start:i + 1]))
                    except json.JSONDecodeError:
                        pass
                    start = None
    return objects


def extract_facts(document: dict) -> list:
    """Extract confirmed facts from document sections via configured LLM provider."""
    if not API_KEY and LLM_PROVIDER != 'ollama':
        print(f"[facts] API key not set for provider '{LLM_PROVIDER}' -- cannot extract facts")
        print(f"[facts] Run 'python run.py generate' after setting the key")
        return []

    locked_facts  = _load_locked_facts()
    confirmed     = []
    new_count     = 0
    conflict_count = 0
    source_doc    = document.get('source_document', '')
    source_cat    = document.get('source_category', '')
    is_community  = source_cat in COMMUNITY_CATEGORIES
    if is_community:
        print(f"[facts] {source_cat}/ is a community source -- ALL facts routed to "
              f"pending (phrasing only, never auto-confirmed)")

    for section in document.get('sections', []):
        content = section.get('content', '').strip()
        if len(content) < 50:
            continue

        user_msg = EXTRACTION_USER_TMPL.format(section_content=content[:4000])
        try:
            response = call_with_cost_tracking(
                'fact_extractor',
                model=DEFAULT_MODEL,
                max_tokens=4096,
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
            extracted['source_category'] = source_cat

            # Community/blog sources are never authoritative -- everything to pending.
            if is_community:
                _append_pending_fact(extracted)
                new_count += 1
                continue

            status, key = classify_fact(extracted, locked_facts)
            if status == 'confirmed':
                confirmed.append(extracted)
            elif status == 'conflict':
                extracted['conflicts_with'] = key
                extracted['locked_value']   = _locked_value_str(locked_facts.get(key))
                _append_conflicting_fact(extracted)
                conflict_count += 1
                print(f"[facts] CONFLICT: '{key}' locked={extracted['locked_value']!r} "
                      f"vs source={extracted.get('value')!r}{extracted.get('unit') or ''} "
                      f"-- locked fact NOT overridden")
            else:
                _append_pending_fact(extracted)
                new_count += 1

    print(f"[facts] {document['source_file']}: {len(confirmed)} confirmed, "
          f"{new_count} new candidates, {conflict_count} conflicts")
    if new_count > 0:
        print(f"[facts] Run 'python run.py approve-facts' to review new candidates")
    if conflict_count > 0:
        print(f"[facts] {conflict_count} conflicts -> {CONFLICTING_FACTS_PATH} (locked facts kept)")
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

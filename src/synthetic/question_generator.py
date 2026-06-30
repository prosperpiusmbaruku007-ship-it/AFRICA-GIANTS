import json
import os
import re
import hashlib
from datetime import datetime
from pathlib import Path

import numpy as np
import requests as _requests

from src.synthetic.api_utils import (
    call_with_cost_tracking, DEFAULT_MODEL, API_KEY, LLM_PROVIDER,
)

EMBED_MODEL_NAME    = 'nomic-embed-text'
EMBED_DIM           = 768                # nomic-embed-text output dimension
DEDUP_THRESHOLD     = float(os.environ.get('DEDUP_THRESHOLD', '0.85'))
SKIP_SEMANTIC_DEDUP = os.environ.get('SKIP_SEMANTIC_DEDUP', 'false').lower() == 'true'
OLLAMA_BASE         = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')

INDEX_PATH        = 'data/raw/instruction_index.npy'
INDEX_TEXTS_PATH  = 'data/raw/instruction_index_texts.json'
INDEX_HASH_PATH   = 'data/raw/instruction_index_hash.txt'
CLEANED_PAIRS_DIR = 'datasets/tier1a/cleaned_pairs'

# Built once per pipeline run (process): reused for the whole run even if this run's
# own batch writes change the cleaned_pairs/ hash mid-run. Avoids the O(docs x corpus)
# full re-embed that made multi-document runs take hours.
_INDEX_CACHE = None

GENERATION_SYSTEM = (
    "You are a Swahili compliance question generator for Chike, "
    "a Tanzanian business adviser. Generate natural conversational questions "
    "a small business owner would ask via WhatsApp -- not formal exam questions. "
    "Use everyday Swahili mixed with necessary technical terms (VAT, SDL, PAYE). "
    "Respond ONLY with a JSON array. No preamble, no explanation."
)

# The reviewer (pair_reviewer._check2_schema) rejects any pair whose subdomain is
# not in this exact set. The generator MUST be told the closed list explicitly,
# otherwise the LLM invents plausible-but-invalid names (vat_compliance,
# withholding_tax_compliance, customs_duties, ...) and every pair fails CHECK2.
CANONICAL_SUBDOMAINS = [
    'vat_registration',
    'paye',
    'sdl_compliance',
    'gn487a',
    'brela_registration',
    'nssf_contributions',
    'osha_registration',
    'efd_compliance',
    'vat_withholding',
    'out_of_corpus',
    'wcf_compliance',
]

SUBDOMAIN_LIST = ', '.join(CANONICAL_SUBDOMAINS)

# Pin the cited authority to the document's actual source category (its folder), so the
# model stops defaulting to TRA. Mirrors pdf_extractor.SOURCE_URL_MAP.
CATEGORY_TO_DOMAIN = {
    'tra':         'tra.go.tz',
    'brela':       'brela.go.tz',
    'osha':        'osha.go.tz',
    'nssf':        'nssf.or.tz',
    'wcf':         'wcf.go.tz',
    'immigration': 'immigration.go.tz',
    'labour':      'labour.go.tz',
    'ppra':        'ppra.go.tz',
    'general':     'tanzlii.org',
}


def _required_domain(source_doc: str, source_url: str) -> str:
    """The authority a pair from this document MUST cite, derived from the source
    folder (data/source_documents/<category>/...), falling back to source_url."""
    norm  = (source_doc or '').replace('\\', '/').strip('/').split('/')
    category = norm[-2] if len(norm) >= 2 else ''
    if category in CATEGORY_TO_DOMAIN:
        return CATEGORY_TO_DOMAIN[category]
    bare = re.sub(r'^https?://', '', source_url or '').replace('www.', '').strip('/')
    return bare or 'tra.go.tz'

GENERATION_USER_TMPL = """Generate {n} compliance questions from this fact.
Fact: {fact_key}: {value} {unit} -- source: {source_section}

Question type distribution (follow exactly):
- yes_no: 30% (questions answered with Ndiyo/Hapana)
- number: 25% (questions asking for specific figures)
- definition: 20% (questions asking what something is)
- procedure: 15% (questions asking how to do something)
- penalty: 10% (questions asking about consequences)

subdomain MUST be EXACTLY one of these 11 values -- no other values accepted:
{subdomain_list}

If the fact does not fit any of these subdomains set subdomain to 'out_of_corpus'
and answer_type to 'out_of_corpus_refusal'.
Do NOT invent new subdomain names.

CITATION (MANDATORY): This fact comes from {required_domain}. Every answer's "output"
MUST cite {required_domain} as the authority (e.g. "Thibitisha na ... ({required_domain})").
Do NOT cite tra.go.tz or "TRA" unless {required_domain} is exactly tra.go.tz. The correct
authority for this fact is {required_domain} -- never default to TRA.

Output format (JSON array only):
[
  {{
    "instruction": "question in natural conversational Swahili",
    "input": "",
    "output": "direct answer in Swahili citing source domain",
    "system": "Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT kwa Kiswahili na Kiingereza. Kama swali liko nje ya mada yako sema wazi kwamba halijui na mwelekeze kwa mtaalamu.",
    "subdomain": "EXACTLY one of the 11 canonical subdomains listed above",
    "answer_type": "yes_no|number|definition|procedure|penalty|out_of_corpus_refusal",
    "source_url": "MUST be {required_domain}",
    "source_name": "TRA Official|BRELA Official|OSHA Official|etc",
    "generated_date": "YYYY-MM-DD",
    "source_document": "relative path of input file"
  }}
]

Example input fact:
fact_key: sdl_rate, value: 3.5, unit: %, source_section: SDL Overview

Example output:
[
  {{
    "instruction": "Ninaajiri wafanyakazi 20 -- SDL inanigharimu kiasi gani kwa mwezi?",
    "input": "",
    "output": "SDL ni asilimia 3.5 ya jumla ya mishahara yote -- mwajiri peke yake ndiye analipa, si mfanyakazi. Kwa mishahara ya jumla TZS 1,000,000 unalipa TZS 35,000. Thibitisha na TRA (tra.go.tz).",
    "system": "Jina lako ni Chike...",
    "subdomain": "sdl_compliance",
    "answer_type": "number",
    "source_url": "https://tra.go.tz",
    "source_name": "TRA Official",
    "generated_date": "2026-06-22",
    "source_document": "data/source_documents/tra/sdl_guide_2025.pdf"
  }},
  {{
    "instruction": "Je, mfanyakazi analipa sehemu ya SDL?",
    "input": "",
    "output": "Hapana. SDL inalipwa na MWAJIRI peke yake -- mfanyakazi halipi chochote. Hii ni tofauti na NSSF ambayo inalipwa na wote wawili. Thibitisha na TRA (tra.go.tz).",
    "system": "Jina lako ni Chike...",
    "subdomain": "sdl_compliance",
    "answer_type": "yes_no",
    "source_url": "https://tra.go.tz",
    "source_name": "TRA Official",
    "generated_date": "2026-06-22",
    "source_document": "data/source_documents/tra/sdl_guide_2025.pdf"
  }}
]"""

_ollama_warned = False


def embed_instruction(text: str):
    """Embed a single text via Ollama nomic-embed-text. Returns numpy array or None."""
    global _ollama_warned
    try:
        r = _requests.post(
            f'{OLLAMA_BASE}/api/embeddings',
            json={'model': EMBED_MODEL_NAME, 'prompt': text},
            timeout=10,
        )
        r.raise_for_status()
        return np.array(r.json()['embedding'], dtype=np.float32)
    except Exception:
        if not _ollama_warned:
            print(f'[dedup] Ollama not running -- semantic dedup disabled.')
            print(f'[dedup] Start with: ollama serve  (then: ollama pull {EMBED_MODEL_NAME})')
            _ollama_warned = True
        return None


def _embed_batch(texts: list):
    """Embed a list of texts. Returns stacked numpy array or None if Ollama unreachable."""
    embeddings = []
    for text in texts:
        emb = embed_instruction(text)
        if emb is None:
            return None
        embeddings.append(emb)
    return np.array(embeddings, dtype=np.float32)


def _md5_of_directory(dir_path: str) -> str:
    h = hashlib.md5()
    for f in sorted(Path(dir_path).glob('*.jsonl')):
        h.update(f.read_bytes())
    return h.hexdigest()


def _load_all_instructions() -> list:
    instructions = []
    for fpath in sorted(Path(CLEANED_PAIRS_DIR).glob('*.jsonl')):
        with open(fpath, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    p     = json.loads(line)
                    instr = p.get('instruction') or p.get('question_sw', '')
                    if instr:
                        instructions.append(instr)
                except Exception:
                    pass
    return instructions


def get_instruction_index() -> tuple:
    """Load/build the semantic dedup index ONCE per run, updating the on-disk cache
    INCREMENTALLY (embed only instructions not already embedded) so adding a few
    pairs never triggers a full re-embed of the whole corpus."""
    global _INDEX_CACHE
    if SKIP_SEMANTIC_DEDUP:
        print("[dedup] SKIP_SEMANTIC_DEDUP=true -- skipping index build")
        return np.empty((0, EMBED_DIM), dtype=np.float32), []

    # Per-run memoization: reuse within this process even if our own writes changed
    # the cleaned_pairs/ hash mid-run (cross-run overlaps are caught on the next run).
    if _INDEX_CACHE is not None:
        return _INDEX_CACHE

    current_hash = _md5_of_directory(CLEANED_PAIRS_DIR)

    # Load any existing on-disk cache
    cached_emb, cached_texts, cached_hash = None, None, None
    if (os.path.exists(INDEX_PATH) and os.path.exists(INDEX_TEXTS_PATH)
            and os.path.exists(INDEX_HASH_PATH)):
        try:
            cached_emb = np.load(INDEX_PATH)
            with open(INDEX_TEXTS_PATH, encoding='utf-8') as f:
                cached_texts = json.load(f)
            cached_hash = open(INDEX_HASH_PATH).read().strip()
        except Exception:
            cached_emb, cached_texts, cached_hash = None, None, None

    if cached_texts is not None and cached_hash == current_hash:
        print(f"[dedup] index loaded from cache -- {len(cached_texts)} existing instructions")
        _INDEX_CACHE = (cached_emb, cached_texts)
        return _INDEX_CACHE

    all_instructions = _load_all_instructions()
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

    if not all_instructions:
        empty = np.empty((0, EMBED_DIM), dtype=np.float32)
        np.save(INDEX_PATH, empty)
        with open(INDEX_TEXTS_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f)
        with open(INDEX_HASH_PATH, 'w') as f:
            f.write(current_hash)
        _INDEX_CACHE = (empty, [])
        return _INDEX_CACHE

    # Incremental: reuse embeddings for instructions still present; embed only new ones.
    if (cached_texts is not None and cached_emb is not None
            and len(cached_texts) == cached_emb.shape[0]):
        present    = set(all_instructions)
        keep       = [i for i, t in enumerate(cached_texts) if t in present]
        base_emb   = cached_emb[keep] if keep else np.empty((0, EMBED_DIM), dtype=np.float32)
        base_texts = [cached_texts[i] for i in keep]
        known      = set(base_texts)
        new_instructions = [t for t in all_instructions if t not in known]
    else:
        base_emb         = np.empty((0, EMBED_DIM), dtype=np.float32)
        base_texts       = []
        new_instructions = all_instructions

    if new_instructions:
        print(f"[dedup] embedding {len(new_instructions)} new instruction(s) "
              f"(reusing {len(base_texts)} cached) ...")
        new_emb = _embed_batch(new_instructions)
        if new_emb is None:
            if base_texts:
                print("[dedup] Ollama unreachable -- using cached subset only this run")
                _INDEX_CACHE = (base_emb, base_texts)
                return _INDEX_CACHE
            print("[dedup] Ollama unreachable -- index not built, dedup disabled this run")
            return np.empty((0, EMBED_DIM), dtype=np.float32), []
        embeddings = np.vstack([base_emb, new_emb]) if base_emb.shape[0] > 0 else new_emb
        texts      = base_texts + new_instructions
    else:
        embeddings = base_emb
        texts      = base_texts

    np.save(INDEX_PATH, embeddings)
    with open(INDEX_TEXTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(texts, f, ensure_ascii=False)
    with open(INDEX_HASH_PATH, 'w') as f:
        f.write(current_hash)
    print(f"[dedup] index ready -- {len(texts)} instructions "
          f"({len(new_instructions)} newly embedded)")
    _INDEX_CACHE = (embeddings, texts)
    return _INDEX_CACHE


def is_semantic_duplicate(instruction: str,
                           index_embeddings: np.ndarray,
                           index_texts: list) -> bool:
    if SKIP_SEMANTIC_DEDUP:
        return False
    if len(index_texts) == 0 or index_embeddings.shape[0] == 0:
        return False
    emb = embed_instruction(instruction)
    if emb is None:
        return False  # Ollama not running — skip dedup gracefully
    # nomic-embed-text vectors are NOT unit-normalized (L2 ~20), so a raw dot
    # product yields ~270-330, not cosine. Normalize both sides so np.dot gives
    # cosine similarity in [-1, 1] and DEDUP_THRESHOLD is meaningful.
    emb_n = emb / (np.linalg.norm(emb) + 1e-8)
    idx_n = index_embeddings / (np.linalg.norm(index_embeddings, axis=1, keepdims=True) + 1e-8)
    scores    = np.dot(idx_n, emb_n)
    max_score = float(np.max(scores))
    if max_score > DEDUP_THRESHOLD:
        best_idx   = int(np.argmax(scores))
        best_match = index_texts[best_idx] if index_texts else 'unknown'
        print(f'[dedup] SKIP similarity={max_score:.3f} > {DEDUP_THRESHOLD}')
        print(f'[dedup]   new:      {instruction[:80]}')
        print(f'[dedup]   matched:  {best_match[:80]}')
        return True
    return False


def parse_llm_response(raw: str) -> list:
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
    print(f"[generator] Failed to parse LLM response. Skipping. Raw: {raw[:200]}")
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


def generate_pairs_for_fact(fact: dict, today: str, source_doc: str, source_url: str,
                            cur_emb: np.ndarray, cur_texts: list) -> tuple:
    """Generate Swahili Q&A pairs for a SINGLE confirmed fact.

    Returns (pairs, cur_emb, cur_texts, dedup_skipped). cur_emb/cur_texts are the
    running dedup index — passed in and returned so the caller can thread the
    in-run index across facts (and stream-write approved pairs per fact).
    """
    pairs_out     = []
    dedup_skipped = 0
    if not API_KEY and LLM_PROVIDER != 'ollama':
        return pairs_out, cur_emb, cur_texts, dedup_skipped

    fact_key    = fact.get('fact_key', 'unknown')
    value       = fact.get('value', '')
    unit        = fact.get('unit', '') or ''
    source_sect = fact.get('source_section', '')
    required_domain = _required_domain(source_doc, source_url)

    user_msg = GENERATION_USER_TMPL.format(
        n=4, fact_key=fact_key, value=value,
        unit=unit, source_section=source_sect,
        subdomain_list=SUBDOMAIN_LIST,
        required_domain=required_domain,
    )

    try:
        response = call_with_cost_tracking(
            'question_generator',
            model=DEFAULT_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": user_msg}],
            system=GENERATION_SYSTEM,
        )
        raw_pairs = parse_llm_response(response.content[0].text)
    except Exception as e:
        print(f"[generator] API error for fact '{fact_key}': {e}")
        return pairs_out, cur_emb, cur_texts, dedup_skipped

    for pair in raw_pairs:
        pair['generated_date']  = today
        pair['source_document'] = source_doc
        # Force the citation metadata to the correct authority (the model is told to
        # cite it in-text too; CHECK4 enforces the in-text citation).
        pair['source_url'] = f"https://{required_domain}"

        instr = pair.get('instruction', '')
        if not instr:
            continue

        if is_semantic_duplicate(instr, cur_emb, cur_texts):
            dedup_skipped += 1
            continue

        pairs_out.append(pair)

        # Add to in-run index so we dedup within this run too
        new_emb = embed_instruction(instr)
        if new_emb is not None:
            new_emb = new_emb.reshape(1, -1)
            cur_emb = np.vstack([cur_emb, new_emb]) if cur_emb.shape[0] > 0 else new_emb
            cur_texts.append(instr)

    return pairs_out, cur_emb, cur_texts, dedup_skipped


def generate_pairs(facts: list, document: dict,
                   index_embeddings=None, index_texts=None,
                   raw_output_path: str = None) -> list:
    """Generate Swahili Q&A pairs from confirmed facts (batch wrapper over
    generate_pairs_for_fact — kept for callers that want all pairs at once)."""
    if not API_KEY and LLM_PROVIDER != 'ollama':
        print(f"[generator] API key not set for provider '{LLM_PROVIDER}' -- cannot generate pairs")
        return []

    today      = datetime.utcnow().strftime('%Y-%m-%d')
    source_doc = document.get('source_document', '')
    source_url = document.get('source_url', 'tanzlii.org')

    if index_embeddings is None or index_texts is None:
        index_embeddings, index_texts = get_instruction_index()

    cur_emb   = index_embeddings
    cur_texts = list(index_texts)
    all_pairs     = []
    dedup_skipped = 0

    for fact in facts:
        pairs, cur_emb, cur_texts, skipped = generate_pairs_for_fact(
            fact, today, source_doc, source_url, cur_emb, cur_texts,
        )
        all_pairs.extend(pairs)
        dedup_skipped += skipped

    print(f"[generator] {document['source_file']}: "
          f"{len(all_pairs)} pairs generated, {dedup_skipped} dedup-skipped")

    if raw_output_path and all_pairs:
        os.makedirs(os.path.dirname(raw_output_path), exist_ok=True)
        with open(raw_output_path, 'w', encoding='utf-8') as f:
            for p in all_pairs:
                f.write(json.dumps(p, ensure_ascii=False) + '\n')

    return all_pairs

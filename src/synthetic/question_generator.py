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
DEDUP_THRESHOLD     = 0.92
SKIP_SEMANTIC_DEDUP = os.environ.get('SKIP_SEMANTIC_DEDUP', 'false').lower() == 'true'
OLLAMA_BASE         = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')

INDEX_PATH        = 'data/raw/instruction_index.npy'
INDEX_TEXTS_PATH  = 'data/raw/instruction_index_texts.json'
INDEX_HASH_PATH   = 'data/raw/instruction_index_hash.txt'
CLEANED_PAIRS_DIR = 'datasets/tier1a/cleaned_pairs'

GENERATION_SYSTEM = (
    "You are a Swahili compliance question generator for Chike, "
    "a Tanzanian business adviser. Generate natural conversational questions "
    "a small business owner would ask via WhatsApp -- not formal exam questions. "
    "Use everyday Swahili mixed with necessary technical terms (VAT, SDL, PAYE). "
    "Respond ONLY with a JSON array. No preamble, no explanation."
)

GENERATION_USER_TMPL = """Generate {n} compliance questions from this fact.
Fact: {fact_key}: {value} {unit} -- source: {source_section}

Question type distribution (follow exactly):
- yes_no: 30% (questions answered with Ndiyo/Hapana)
- number: 25% (questions asking for specific figures)
- definition: 20% (questions asking what something is)
- procedure: 15% (questions asking how to do something)
- penalty: 10% (questions asking about consequences)

Output format (JSON array only):
[
  {{
    "instruction": "question in natural conversational Swahili",
    "input": "",
    "output": "direct answer in Swahili citing source domain",
    "system": "Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT kwa Kiswahili na Kiingereza. Kama swali liko nje ya mada yako sema wazi kwamba halijui na mwelekeze kwa mtaalamu.",
    "subdomain": "one of 11 canonical subdomains",
    "answer_type": "yes_no|number|definition|procedure|penalty|out_of_corpus_refusal",
    "source_url": "canonical .go.tz domain from SOURCE_URL_MAP",
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


def get_instruction_index() -> tuple:
    """Load or rebuild semantic dedup index from cleaned_pairs/ using nomic-embed-text."""
    if SKIP_SEMANTIC_DEDUP:
        print("[dedup] SKIP_SEMANTIC_DEDUP=true -- skipping index build")
        return np.empty((0, EMBED_DIM), dtype=np.float32), []

    current_hash = _md5_of_directory(CLEANED_PAIRS_DIR)

    if (os.path.exists(INDEX_PATH) and
            os.path.exists(INDEX_TEXTS_PATH) and
            os.path.exists(INDEX_HASH_PATH) and
            open(INDEX_HASH_PATH).read().strip() == current_hash):
        embeddings = np.load(INDEX_PATH)
        with open(INDEX_TEXTS_PATH, encoding='utf-8') as f:
            texts = json.load(f)
        print(f"[dedup] index loaded from cache -- {len(texts)} existing instructions")
        return embeddings, texts

    print("[dedup] rebuilding instruction index ...")
    all_instructions = []
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
                        all_instructions.append(instr)
                except Exception:
                    pass

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

    if not all_instructions:
        empty = np.empty((0, EMBED_DIM), dtype=np.float32)
        np.save(INDEX_PATH, empty)
        with open(INDEX_TEXTS_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f)
        with open(INDEX_HASH_PATH, 'w') as f:
            f.write(current_hash)
        return empty, []

    embeddings = _embed_batch(all_instructions)
    if embeddings is None:
        print("[dedup] Ollama unreachable -- index not built, dedup disabled this run")
        return np.empty((0, EMBED_DIM), dtype=np.float32), []

    np.save(INDEX_PATH, embeddings)
    with open(INDEX_TEXTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_instructions, f, ensure_ascii=False)
    with open(INDEX_HASH_PATH, 'w') as f:
        f.write(current_hash)
    print(f"[dedup] index rebuilt -- {len(all_instructions)} instructions indexed")
    return embeddings, all_instructions


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
    scores = np.dot(index_embeddings, emb)
    return float(np.max(scores)) > DEDUP_THRESHOLD


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
    print(f"[generator] Failed to parse LLM response. Skipping. Raw: {raw[:200]}")
    return []


def generate_pairs(facts: list, document: dict,
                   index_embeddings=None, index_texts=None,
                   raw_output_path: str = None) -> list:
    """Generate Swahili Q&A pairs from confirmed facts."""
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
        fact_key    = fact.get('fact_key', 'unknown')
        value       = fact.get('value', '')
        unit        = fact.get('unit', '') or ''
        source_sect = fact.get('source_section', '')

        user_msg = GENERATION_USER_TMPL.format(
            n=4, fact_key=fact_key, value=value,
            unit=unit, source_section=source_sect,
        )

        try:
            response = call_with_cost_tracking(
                'question_generator',
                model=DEFAULT_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": user_msg}],
                system=GENERATION_SYSTEM,
            )
            raw_pairs = parse_llm_response(response.content[0].text)
        except Exception as e:
            print(f"[generator] API error for fact '{fact_key}': {e}")
            continue

        for pair in raw_pairs:
            pair['generated_date']  = today
            pair['source_document'] = source_doc
            if not pair.get('source_url'):
                pair['source_url'] = source_url

            instr = pair.get('instruction', '')
            if not instr:
                continue

            if is_semantic_duplicate(instr, cur_emb, cur_texts):
                dedup_skipped += 1
                continue

            all_pairs.append(pair)

            # Add to in-run index so we dedup within this run too
            new_emb = embed_instruction(instr)
            if new_emb is not None:
                new_emb = new_emb.reshape(1, -1)
                cur_emb = np.vstack([cur_emb, new_emb]) if cur_emb.shape[0] > 0 else new_emb
                cur_texts.append(instr)

    print(f"[generator] {document['source_file']}: "
          f"{len(all_pairs)} pairs generated, {dedup_skipped} dedup-skipped")

    if raw_output_path and all_pairs:
        os.makedirs(os.path.dirname(raw_output_path), exist_ok=True)
        with open(raw_output_path, 'w', encoding='utf-8') as f:
            for p in all_pairs:
                f.write(json.dumps(p, ensure_ascii=False) + '\n')

    return all_pairs

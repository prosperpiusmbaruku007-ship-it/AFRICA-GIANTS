#!/usr/bin/env python3
"""
Rebuild the RAG index from scripts/locked_facts.json (Fix 2 — concise bilingual).

High-stakes facts are embedded as SHORT, Swahili-dominant strings that contain the
value in both Swahili number words and TZS digits. Short text keeps the mean-pooled
embedding close to short Swahili queries (a long English tail dilutes it — that was
why the GN487A 10M penalty sank to rank 8). Bare citations / exemption lists / the
low-value signatory fact are dropped as noise.

build_fact_texts() is importable (used by the dry-run) WITHOUT triggering a rebuild;
embedding + save only runs under `__main__`.

Run: python scripts/precompute_rag_embeddings.py
"""
import json
import os
import re
import numpy as np

FACTS_PATH   = 'scripts/locked_facts.json'
OUTPUT_NPY   = 'chike-inference/rag_embeddings.npy'
OUTPUT_TEXTS = 'chike-inference/rag_facts_text.json'
EMBED_MODEL  = 'paraphrase-multilingual-MiniLM-L12-v2'

# --- Concise, Swahili-dominant text for high-stakes facts (SHORT, no long English tail) ---
CONCISE_BILINGUAL_FACTS = {
    'gn487a_penalty_noncitizen':
        'Faini kwa mgeni (raia wa kigeni) anayevunja GN487A: si chini ya TZS 10,000,000 (milioni kumi), na/au kifungo miezi 6, na kufutwa kwa visa.',

    'gn487a_penalty_citizen_facilitator':
        'Adhabu kwa raia wa Tanzania anayemsaidia mgeni kukiuka GN487A: faini si zaidi ya TZS 5,000,000 (milioni tano), au kifungo si zaidi ya miezi 3.',

    'sdl_rate':
        'SDL (Skills Development Levy) Tanzania: asilimia 3.5 ya mishahara yote. Si 4%, si 2%.',

    'sdl_employee_threshold':
        'SDL inalipwa na mwajiri mwenye wafanyakazi 10 au zaidi. Wafanyakazi chini ya 10 hawalipi SDL.',

    'sdl_payment_deadline':
        'SDL inalipwa ifikapo siku ya 7 ya mwezi unaofuata.',

    'nssf_employer_rate':
        'NSSF: mwajiri analipa asilimia 10 ya mshahara wa mfanyakazi kila mwezi.',

    'nssf_employee_rate':
        'NSSF: mfanyakazi analipa asilimia 10 ya mshahara wake kila mwezi.',

    'nssf_total_rate':
        'NSSF jumla: asilimia 20 ya mshahara (10% mwajiri + 10% mfanyakazi).',

    'nssf_payment_deadline':
        'NSSF inalipwa ifikapo tarehe 10 ya mwezi unaofuata.',

    'vat_registration_threshold_annual':
        'Kizingiti cha kusajili VAT: mauzo ya TZS 200,000,000 kwa miezi 12.',

    'vat_registration_threshold_six_months':
        'Kizingiti cha kusajili VAT: mauzo ya TZS 100,000,000 kwa miezi 6.',

    'annual_return_filing_fee':
        'BRELA annual return ada: TZS 22,000 kwa mwaka.',

    'late_filing_penalty_monthly_fee':
        'BRELA: faini ya kuchelewa kuwasilisha annual return ni TZS 2,500 kwa kila mwezi.',
}

# --- Noise keys to drop (bare citations, sections, exemption lists, no-value fragments) ---
_NOISE_KEY_PATTERNS = [
    r'^exemption_category_',
    r'^legal_citation_',
    r'_act_citation$',
    r'_act_section$',
    r'_rules_section$',
    r'_act_reference$',
    r'_act_chapter$',
    r'^order_made_under_section$',
    r'^offence_penalty_mention$',
    r'^prohibited_business_activities_for_non_citizens_order_year$',
    r'^gn487a_signatory$',  # low-value (who signed the order) — was outranking the 10M penalty
]


def is_noise_key(key: str) -> bool:
    return any(re.search(p, key) for p in _NOISE_KEY_PATTERNS)


def fact_value(v) -> str:
    if isinstance(v, dict):
        return (v.get('fact') or v.get('correct_value') or '').strip()
    return str(v).strip()


def build_fact_text(key: str, value: str) -> str:
    # Concise Swahili-dominant text for high-stakes facts (short — no long English tail).
    if key in CONCISE_BILINGUAL_FACTS:
        return CONCISE_BILINGUAL_FACTS[key]
    # All other facts: readable key + value.
    key_readable = key.replace('_', ' ')
    return f'{key_readable}: {value}'


def build_fact_texts():
    """Return (kept_texts, kept_keys, dropped_keys) — importable without side effects."""
    with open(FACTS_PATH, encoding='utf-8') as f:
        facts = json.load(f)
    texts, keys, dropped = [], [], []
    for k, v in facts.items():
        if k == '_meta':
            continue
        if is_noise_key(k):
            dropped.append(k)
            continue
        texts.append(build_fact_text(k, fact_value(v)))
        keys.append(k)
    return texts, keys, dropped


if __name__ == '__main__':
    from sentence_transformers import SentenceTransformer

    fact_texts, fact_keys, dropped = build_fact_texts()
    print(f'[rag] kept {len(fact_texts)} facts, dropped {len(dropped)} noise')

    print(f'[rag] Loading model: {EMBED_MODEL}')
    model = SentenceTransformer(EMBED_MODEL)

    print(f'[rag] Embedding {len(fact_texts)} facts...')
    embeddings = np.array(model.encode(fact_texts, show_progress_bar=True))

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / (norms + 1e-10)
    print('[rag] normalized embeddings for cosine similarity')

    np.save(OUTPUT_NPY, embeddings)
    with open(OUTPUT_TEXTS, 'w', encoding='utf-8') as f:
        json.dump(fact_texts, f, ensure_ascii=False, indent=2)

    print(f'[rag] Saved {OUTPUT_NPY} ({embeddings.shape})')
    print(f'[rag] Saved {OUTPUT_TEXTS} ({len(fact_texts)} facts)')

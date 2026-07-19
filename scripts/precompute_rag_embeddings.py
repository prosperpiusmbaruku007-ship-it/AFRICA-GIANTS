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
# intfloat/multilingual-e5-base: 768-dim, trained for multilingual retrieval.
# e5 REQUIRES an asymmetric prefix — facts are 'passage: ', queries are 'query: '
# (the query prefix is applied at retrieval time in chike-inference/modal_app.py).
EMBED_MODEL  = 'intfloat/multilingual-e5-base'
E5_PASSAGE_PREFIX = 'passage: '

# --- Concise, Swahili-dominant text for high-stakes facts (SHORT, no long English tail) ---
CONCISE_BILINGUAL_FACTS = {
    'gn487a_penalty_noncitizen':
        'Faini kwa mgeni (raia wa kigeni) anayevunja GN487A: si chini ya TZS 10,000,000 (milioni kumi), na/au kifungo miezi 6, na kufutwa kwa visa.',

    # Swahili-first grounding for the phone-repair activity. The 15 prohibited-activity
    # facts are otherwise English-only (key: value fallback) and match Swahili queries
    # only cross-lingually (weak e5 signal) — see PROGRESS.md systemic-gap note. This
    # entry gives activity 3 real same-language tokens (mgeni/kutengeneza/simu) so it
    # wins its own query on grounding, not luck, instead of being displaced by any
    # Swahili-dense GN487A fact. English tail keeps the 'phone'/'activity 3' guard keys.
    'gn487a_prohibited_activity_3':
        'Kutengeneza au ukarabati wa simu na vifaa vya kielektroniki ni shughuli '
        'iliyozuiliwa kwa wasio raia chini ya GN487A. Mgeni hawezi kufanya biashara '
        'ya kutengeneza simu. (Prohibited activity 3: repair of mobile phones and '
        'electronic devices.)',

    'gn487a_penalty_citizen_facilitator':
        'Adhabu kwa raia wa Tanzania anayemsaidia mgeni kukiuka GN487A: faini si zaidi ya TZS 5,000,000 (milioni tano), au kifungo si zaidi ya miezi 3.',

    # Retrieval-targeted restatement of the facilitator penalty using the exact
    # 'kukopesha leseni' collocation. lv_01/fp_01 showed the model overrides the
    # generic 'anayemsaidia mgeni' fact with a parametric 'licensed Tanzanian may
    # operate' prior for THIS phrasing only (2x2 factorial: swapping either the verb
    # or the object alone fixes it). Same TZS 5M/3-month figure — no new claim.
    # NARROWED (v2): the first draft carried generic GN487A-penalty mass
    # (kumsaidia/kukiuka/msaidizi/adhabu/faini prose) that made it a generic Swahili
    # GN487A-penalty magnet — it displaced gn487a_prohibited_activity_3 from the
    # 'Mgeni anaweza kutengeneza simu?' top-3 (caught by the regen verification gate).
    # This version concentrates the embedding centroid on license-transfer (kukopesha/
    # kukodisha/kukabidhi + leseni — tokens absent from every competing fact, so lv_01
    # still wins) and drops the generic penalty/facilitation prose.
    'gn487a_license_lending_is_facilitation':
        'Kukopesha, kukodisha au kukabidhi leseni yako ya biashara kwa mgeni ni kosa chini ya GN487A. '
        'Raia anayekopesha leseni yake kwa mgeni analipa faini ya TZS 5,000,000 au kifungo cha miezi 3.',

    'sdl_rate':
        'SDL (Skills Development Levy) Tanzania: asilimia 3.5 ya mishahara yote. Si 4%, si 2%.',

    'sdl_employee_threshold':
        'Kizingiti cha SDL: mwajiri mwenye wafanyakazi 10 AU ZAIDI analipa SDL. Mwenye wafanyakazi 10 YUKO NDANI ya kizingiti na analipa SDL. Chini ya 10 (yaani 9 au pungufu) hawalipi SDL.',

    'sdl_threshold':
        'Kizingiti cha SDL ni wafanyakazi 10 au zaidi. Wafanyakazi 10 hasa wanalipa SDL (wako ndani). Si 11, si 4.',

    'sdl_payment_deadline':
        'SDL inalipwa ifikapo siku ya 7 ya mwezi unaofuata.',

    'nssf_employer_rate':
        'NSSF: mwajiri analipa asilimia 10 ya mshahara wa mfanyakazi kila mwezi. Tovuti sahihi ni nssf.go.tz (si nssf.or.tz).',

    'nssf_total_rate':
        'NSSF jumla: asilimia 20 ya mshahara (10% mwajiri + 10% mfanyakazi). Tovuti sahihi ni nssf.go.tz (si nssf.or.tz).',

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

    'osha_registration_threshold_b004':
        'OSHA Tanzania: kila mwajiri lazima asajili mahali pa kazi na OSHA. Sheria inahusu maeneo yote ya kazi bila kikomo cha idadi ya wafanyakazi.',

    'OSHA_annual_inspection':
        'OSHA hufanya ukaguzi wa lazima kila mwaka (mara moja kwa mwaka) katika maeneo yote ya kazi Tanzania.',

    'wcf_rate_0_5_percent_confirmed':
        'WCF (Workers Compensation Fund): mwajiri analipa asilimia 0.5 ya jumla ya mishahara yote kila mwezi. Si kiasi kisichobadilika — inategemea mishahara.',

    'paye_bands_with_examples':
        'PAYE kwa mshahara wa TZS 800,000 ni TZS 78,000 kamili. Hii ni jibu la mwisho, si mahesabu ya ziada.',

    'sdl_calculation_example':
        'Mfano wa hesabu ya SDL: mfanyakazi mmoja mwenye mshahara TZS 600,000, SDL ni asilimia 3.5 = TZS 21,000. Kwa wafanyakazi 12 wenye mshahara huo huo, SDL jumla ni TZS 252,000 (12 × 21,000).',

    'nssf_calculation_example':
        'Kwa wafanyakazi 12 wenye mshahara TZS 600,000 kila mmoja, NSSF jumla ni TZS 1,440,000 (SI TZS 120,000 — hiyo ni kwa mfanyakazi mmoja tu). Hesabu: kila mfanyakazi analipa NSSF ya TZS 120,000 (asilimia 20 ya mshahara wake), kisha zidisha kwa wafanyakazi 12 = TZS 1,440,000 jumla.',
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

    # e5 asymmetric retrieval: embed facts as passages. The plain fact_texts are
    # still what gets saved + injected into the prompt; only the embedded copy is
    # prefixed. Queries get the 'query: ' prefix at retrieval time in modal_app.py.
    print(f'[rag] Embedding {len(fact_texts)} facts (with e5 passage prefix)...')
    fact_texts_prefixed = [E5_PASSAGE_PREFIX + t for t in fact_texts]
    embeddings = np.array(model.encode(fact_texts_prefixed, show_progress_bar=True))

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / (norms + 1e-10)
    print('[rag] normalized embeddings for cosine similarity')

    np.save(OUTPUT_NPY, embeddings)
    with open(OUTPUT_TEXTS, 'w', encoding='utf-8') as f:
        json.dump(fact_texts, f, ensure_ascii=False, indent=2)

    print(f'[rag] Saved {OUTPUT_NPY} ({embeddings.shape})')
    print(f'[rag] Saved {OUTPUT_TEXTS} ({len(fact_texts)} facts)')

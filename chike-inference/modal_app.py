import os
import re
import modal

# ---------------------------------------------------------------------------
# Modal port of chike-inference/main.py (Cerebrium -> Modal).
# Same logic: 4-bit Llama adapter v8 + pre-computed RAG fact injection.
# ---------------------------------------------------------------------------

app = modal.App('chike-inference')

_HERE = os.path.dirname(os.path.abspath(__file__))

# GPU image: ML stack. RAG data files are baked in via add_local_file (Modal does
# not auto-include sibling data files, so __file__-relative loading needs this).
image = (
    modal.Image.debian_slim(python_version='3.11')
    .pip_install(
        'transformers>=4.43.0',
        'torch>=2.0.0',
        'peft',
        'bitsandbytes>=0.46.1',
        'accelerate>=0.30.0',
        'sentence-transformers>=2.7.0',
        'numpy>=1.26.0',
        'huggingface_hub>=0.23.0',
    )
    .add_local_file(os.path.join(_HERE, 'rag_embeddings.npy'),   '/root/assets/rag_embeddings.npy')
    .add_local_file(os.path.join(_HERE, 'rag_facts_text.json'),  '/root/assets/rag_facts_text.json')
    .add_local_file(os.path.join(_HERE, '..', 'kaggle', 'chike_config.json'), '/root/assets/chike_config.json')
    # The shared chike/ package (repo root) — mounted so modal_app can import the
    # canonical prompt wrapper + cleanup instead of carrying inline copies. Same
    # add_local pattern as the RAG data files above; /root is on sys.path so
    # `import chike.prompting` / `import chike.generation_cleanup` resolve at runtime.
    .add_local_dir(os.path.join(_HERE, '..', 'chike'), '/root/chike')
)

# Tiny image for the HTTP endpoint (only needs FastAPI; it just forwards to the GPU class).
web_image = modal.Image.debian_slim(python_version='3.11').pip_install('fastapi[standard]')

volume = modal.Volume.from_name('chike-storage', create_if_missing=True)

ADAPTER_REPO = 'prospAprospA007/africa-giants-adapter-v15'
BASE_MODEL   = 'McGill-NLP/AfriqueLlama-8B'   # adapter v15 references this base

# Pre-computed RAG assets (baked into the image above)
RAG_DIR     = '/root/assets'
_EMB_PATH   = os.path.join(RAG_DIR, 'rag_embeddings.npy')
_TEXTS_PATH = os.path.join(RAG_DIR, 'rag_facts_text.json')
_CONFIG_PATH = os.path.join(RAG_DIR, 'chike_config.json')


def _load_config():
    """Single source of truth: kaggle/chike_config.json (baked into the GPU image).
    Falls back to {} in the web container (which does not have the file)."""
    import json
    try:
        with open(_CONFIG_PATH, encoding='utf-8') as f:
            cfg = json.load(f)
        print(f"[config] chike_config.json loaded (version={cfg.get('version','?')})")
        return cfg
    except Exception as e:
        print(f'[config] chike_config.json not loaded ({e}) -- using hardcoded fallbacks')
        return {}


CONFIG = _load_config()

# Generation params — read from config, with safe fallbacks (fixed decoding: greedy,
# repetition_penalty 1.1 + no_repeat_ngram_size 3 to stop token mashing).
_GEN = CONFIG.get('generation_params', {})
MAX_NEW_TOKENS     = int(_GEN.get('max_new_tokens', 512))
DO_SAMPLE          = bool(_GEN.get('do_sample', False))
GEN_TEMPERATURE    = float(_GEN.get('temperature', 1.0))
REPETITION_PENALTY = float(_GEN.get('repetition_penalty', 1.1))
NO_REPEAT_NGRAM    = int(_GEN.get('no_repeat_ngram_size', 3))
# Stop sequences: halt generation the moment the model tries to open a new
# conversational turn. This is what prevents the fabricated follow-up Q&A turns
# (with hallucinated URLs) that caused the run-on generation gate failures.
STOP_STRINGS       = _GEN.get('stop_strings',
                              ['\n\nQ:', '\n\nSwali:', '<|start_header_id|>', '\n\n---'])

# Cache locations on the persistent volume (fast cold starts after first download)
HF_CACHE_DIR    = '/persistent-storage/.cache/huggingface'
MODEL_CACHE_DIR = '/persistent-storage/.cache/huggingface/hub'

# === System prompt — R14: kaggle/chike_config.json is the single source of truth.
# This hardcoded copy is only a fallback for the web container (no baked config file). ===
_HARDCODED_SYSTEM_PROMPT = (
    "Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. "
    "Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. "
    "Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT "
    "kwa Kiswahili na Kiingereza. "
    "Mada zako ni: usajili wa kampuni (BRELA), kodi ya ongezeko la thamani (VAT), "
    "kodi ya mapato ya ajira (PAYE), ushuru wa maendeleo ya ufundi (SDL), "
    "mchango wa NSSF, ukaguzi wa OSHA, vifaa vya kielektroniki vya kodi (EFD), "
    "fidia ya wafanyakazi (WCF), na kanuni za GN487A kwa wasio raia. "
    "HUJUI NA HUSAIDII: kodi ya faida ya mtaji (capital gains tax), "
    "ushuru wa forodha na uagizaji (import/customs duty), "
    "bei ya uhamisho (transfer pricing), "
    "ushuru wa stempu au tathmini ya ardhi (stamp duty), "
    "mrabaha wa madini (mining royalties), mfumo wa kodi Zanzibar, "
    "au ushauri wa uwekezaji. "
    "Kwa mada hizo sema wazi kwamba hazihusu Chike na mwelekeze kwa mtaalamu. "
    "Your name is Chike, a business adviser from Africa Giants. "
    "Tagline: Fahamu Biashara Yako, Maarifa Yako. "
    "You answer Tanzanian mainland business compliance questions in Swahili and English "
    "covering BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT, EFD, WCF, and GN487A. "
    "You do NOT cover capital gains tax, import/customs duty, transfer pricing, "
    "stamp duty, mining royalties, Zanzibar tax, or investment advice. "
    "For those topics say clearly they are outside your scope."
)
# R14: use the config system_prompt when available (so the compound-question
# instruction and any future edits propagate to production); fall back otherwise.
BASE_SYSTEM_PROMPT = CONFIG.get('system_prompt', _HARDCODED_SYSTEM_PROMPT)

# === Inference-time OOC classifier (R11) ===
# The phrase lists AND the 3-step classify logic now live in the shared chike.classification
# module — one source of truth with the eval gate (kaggle/eval.py) and the v16 pipeline
# (chike/orchestrator.py), so the gate measures the exact classifier production runs (R12).
# classify_question below is a thin delegator (see its docstring for the lazy-import reason).

HARDCODED_REFUSAL = (
    'Samahani, swali hili liko nje ya mada yangu. '
    'Ninasaidia tu maswali ya biashara na kodi Tanzania Bara — '
    'BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT, EFD, WCF, na GN487A. '
    'Kwa swali hili wasiliana na TRA (tra.go.tz) au mshauri wa kodi aliyehitimu.'
)

# Never-guess (R8) clarification for a payroll-levy AMOUNT asked with no salary/payroll
# figure given: ask for the figure rather than let the model fabricate one (see
# chike.routing.is_uncomputable_payroll_amount).
PAYROLL_CLARIFICATION = (
    'Ili nikuhesabie makato ya mshahara (kama PAYE, NSSF, SDL) kwa usahihi, nahitaji '
    'kiasi cha mshahara au jumla ya mishahara kwa mwezi. Tafadhali niambie mshahara ni '
    'shilingi ngapi, kisha nitakuletea hesabu kamili.'
)


# clean_reply (the full stop/clean stage) lives in the shared chike.generation_cleanup
# module and is imported inside ChikeModel.run() from the mounted chike/ package (single
# source of truth, identical to the orchestrator and kaggle/eval.py). It supersedes the
# thin clean_generated_reply, which left fabricated follow-up turns in the reply.


def classify_question(message: str) -> bool:
    """Return False if the question is explicitly OOC, True otherwise (pass to model).

    Delegates to the shared chike.classification (R11/R12 single source of truth). Lazy
    import: the chike/ package is mounted to /root only in the GPU image, and /root is added
    to sys.path inside ChikeModel.run() before this is called — the web container, which has
    no chike/ mount, never calls this. Resolves the phrase lists from the baked CONFIG
    (hardcoded canonical ∪ config additions)."""
    from chike.classification import resolve_phrases, classify
    ooc_phrases, in_scope_phrases = resolve_phrases(CONFIG)
    return classify(message, ooc_phrases, in_scope_phrases)


# === Query decomposition ===
# A single WhatsApp message often covers two subdomains ("Nina wafanyakazi 12,
# SDL inalipwa vipi na pia EFD ninahitaji?"). Top-3 RAG retrieval on the whole
# message returns SDL facts OR EFD facts, never both, so the model answers half
# the question. We split multi-part messages and retrieve for each part.

# Swahili connectors that signal a second question inside one message.
MULTI_PART_SIGNALS = [
    r'\bna pia\b', r'\bpia\b', r'\bvilevile\b', r'\bzaidi ya hayo\b',
    r'\blakini pia\b', r'\bna aidha\b', r'\bpia ningependa\b',
    r'\bswali lingine\b', r'\bpia niambie\b', r'\bna je\b',
]

# Strong, unambiguous split points (never split on a bare "pia").
_SPLIT_PATTERN = r'(?:na pia|pia pia|vilevile|zaidi ya hayo|swali lingine)'

# Enumeration: a single clause listing several obligations to compute in one breath,
# e.g. "Nihesabie PAYE, SDL, na NSSF zote tatu". Such a message has no '?' and no
# multi-part connector, so the '?'/connector paths below never fire and a single
# whole-message top-3 retrieval covers only ONE domain (observed: PAYE dropped
# entirely, model looped on 'Thibitisha na TRA'). We detect the "A, B, na C" list
# and give each item its own context-carrying sub-query so each domain is retrieved.
_ENUMERATION_CLAUSE = re.compile(
    r'([^\s,.?!][\w/]*(?:\s*,\s*[\w/]+)+\s*,?\s*na\s+[\w/]+)', re.IGNORECASE)
# Require a calculate/list verb so ordinary prose ("inalipa BRELA, TRA na NSSF") is
# never over-split. \w* on both sides matches the Swahili object prefix so the verb
# in "Nihesabie" / "Nielezee" / "Niambie" is caught, not skipped by a word boundary.
_ENUMERATION_VERB = re.compile(r'\w*(?:hesab|elez|ambi|orodh|taj)\w*', re.IGNORECASE)


def _split_enumeration(message: str) -> list:
    """Sub-queries for an 'A, B, na C' compute list, else [] (not an enumeration).

    Each sub-query carries the context preceding the list (salary, employee count,
    verb) so it retrieves the calc example, not just the bare domain keyword.
    """
    if not _ENUMERATION_VERB.search(message):
        return []
    m = _ENUMERATION_CLAUSE.search(message)
    if not m:
        return []
    raw = re.split(r'\s*,\s*(?:na\s+)?|\s+na\s+', m.group(1), flags=re.IGNORECASE)
    items = [re.sub(r'^na\s+', '', it.strip(), flags=re.IGNORECASE)
             for it in raw if it.strip()]
    if len(items) < 2:
        return []
    preamble = message[:m.start()].strip()
    return [f'{preamble} {item}'.strip() for item in items]


def decompose_query(message: str) -> list:
    """Split a multi-part message into sub-queries for separate RAG retrieval.

    Returns a list of sub-query strings — a single-item list for single-part
    messages. Conservative: if a split produces unusable fragments it falls back
    to the original message so single questions are never over-decomposed.
    """
    message_lower = message.lower()
    question_marks = message.count('?')
    has_connector = any(re.search(p, message_lower) for p in MULTI_PART_SIGNALS)
    enum_parts = _split_enumeration(message)

    if question_marks <= 1 and not has_connector and not enum_parts:
        return [message]  # single question — no decomposition needed

    parts = []

    # Prefer splitting on '?' boundaries when the message has several questions.
    # Fragment floor of 8 chars drops junk remnants ("Sawa?") while keeping real
    # short Swahili sub-queries ("EFD ninahitaji?" is 15 chars).
    if question_marks > 1:
        segments = [s.strip() for s in re.split(r'\?', message) if len(s.strip()) > 8]
        if len(segments) > 1:
            parts = [s + '?' for s in segments]

    # Otherwise split on strong Swahili connectors (case-insensitive on original).
    if not parts and has_connector:
        segments = re.split(_SPLIT_PATTERN, message, flags=re.IGNORECASE)
        parts = [s.strip() for s in segments if len(s.strip()) > 8]

    # Enumeration list ("Nihesabie A, B, na C") — use when the '?'/connector paths
    # above produced nothing usable (no '?', no connector).
    if (not parts or len(parts) == 1) and enum_parts:
        parts = enum_parts

    # Fallback: unusable fragments -> treat as single query.
    if not parts or len(parts) == 1:
        return [message]

    print(f'[decompose] split into {len(parts)} sub-queries:')
    for i, p in enumerate(parts):
        print(f'[decompose]   {i+1}. {p[:80]}')
    return parts


@app.cls(
    image=image,
    gpu='T4',
    volumes={'/persistent-storage': volume},
    scaledown_window=300,
    timeout=600,
    secrets=[modal.Secret.from_name('huggingface-secret')],
)
class ChikeModel:

    @modal.enter()
    def load_model(self):
        import shutil
        import json
        import numpy as np

        # Route caches to the persistent volume BEFORE importing the heavy libs.
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/persistent-storage/.cache/sentence_transformers'
        os.environ['HF_HOME'] = HF_CACHE_DIR
        os.makedirs(HF_CACHE_DIR, exist_ok=True)

        # Keep only adapter v8 in the cache (v8 active; v10 reverted 2026-06-22).
        for _old in ['v3', 'v4', 'v5', 'v6', 'v7', 'v9', 'v10']:
            _old_path = os.path.join(
                MODEL_CACHE_DIR, f'models--prospAprospA007--africa-giants-adapter-{_old}')
            if os.path.exists(_old_path):
                shutil.rmtree(_old_path)
                print(f'[cache] Deleted old model: {_old_path}')

        import torch
        from huggingface_hub import login
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

        self.HF_TOKEN = os.environ.get('HF_TOKEN', '')
        if self.HF_TOKEN:
            login(token=self.HF_TOKEN)
            print('[chike] HuggingFace authenticated')
        else:
            print('[chike] WARNING: HF_TOKEN not set -- model may fail to load')

        # --- RAG: load pre-computed embeddings (only the query is embedded at run time) ---
        self.embed_model = None  # lazy
        if os.path.exists(_EMB_PATH) and os.path.exists(_TEXTS_PATH):
            self.fact_embeddings = np.load(_EMB_PATH)
            with open(_TEXTS_PATH, encoding='utf-8') as f:
                self.fact_texts = json.load(f)
            print(f'[rag] loaded {len(self.fact_texts)} pre-computed embeddings from repo')
        else:
            self.fact_embeddings = None
            self.fact_texts = []
            print('[rag] WARNING: rag_embeddings.npy not found -- RAG disabled')

        # --- Model: tokenizer + 4-bit load with float16 fallback (verbatim from main.py) ---
        print('[chike] Loading tokenizer ...')
        self.tokenizer = AutoTokenizer.from_pretrained(
            ADAPTER_REPO,
            cache_dir=MODEL_CACHE_DIR,
            token=self.HF_TOKEN if self.HF_TOKEN else None,
            trust_remote_code=True,
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        try:
            print('[chike] Loading model in 4bit ...')
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type='nf4',
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                ADAPTER_REPO,
                cache_dir=MODEL_CACHE_DIR,
                quantization_config=bnb_config,
                device_map='auto',
                token=self.HF_TOKEN if self.HF_TOKEN else None,
                trust_remote_code=True,
            )
            print('[chike] Model loaded in 4bit -- ready')
        except Exception as e:
            print(f'[chike] 4bit load failed ({e}), falling back to float16 ...')
            self.model = AutoModelForCausalLM.from_pretrained(
                ADAPTER_REPO,
                cache_dir=MODEL_CACHE_DIR,
                torch_dtype=torch.float16,
                device_map='auto',
                token=self.HF_TOKEN if self.HF_TOKEN else None,
                trust_remote_code=True,
            )
            print('[chike] Model loaded in float16 -- ready')

        self.model.eval()

        # Persist the downloaded weights/caches to the volume for fast cold starts.
        try:
            volume.commit()
            print('[chike] volume committed -- caches persisted')
        except Exception as e:
            print(f'[chike] volume commit skipped: {e}')

    def retrieve_facts(self, question: str, top_k: int = 3) -> list:
        import numpy as np
        if self.fact_embeddings is None or not self.fact_texts:
            return []
        try:
            if self.embed_model is None:
                from sentence_transformers import SentenceTransformer
                # intfloat/multilingual-e5-base (768-dim) — stronger cross-lingual
                # retrieval than MiniLM. MUST match the model used to build
                # rag_embeddings.npy in scripts/precompute_rag_embeddings.py.
                self.embed_model = SentenceTransformer(
                    'intfloat/multilingual-e5-base',
                    cache_folder='/persistent-storage/.cache/sentence_transformers',
                )
            # Cosine similarity: normalize the query AND fact vectors before the
            # dot-product. Raw dot-product favoured high-norm vectors and ranked
            # semantically-wrong facts (e.g. an SDL query surfaced GN487A penalties).
            # e5 asymmetric retrieval: queries take the 'query: ' prefix (facts were
            # embedded with 'passage: ' at build time).
            q_emb  = self.embed_model.encode([f'query: {question}'])[0]
            q_norm = q_emb / (np.linalg.norm(q_emb) + 1e-10)
            norms  = np.linalg.norm(self.fact_embeddings, axis=1, keepdims=True)
            normalized_facts = self.fact_embeddings / (norms + 1e-10)
            scores = np.dot(normalized_facts, q_norm)
            top_indices = np.argsort(scores)[-top_k:][::-1]
            for i, idx in enumerate(top_indices):
                print(f'[RAG] rank {i+1} score={scores[idx]:.3f}: {self.fact_texts[idx][:80]}')
            return [self.fact_texts[i] for i in top_indices]
        except Exception as e:
            print(f'[rag] retrieve_facts error: {e}')
            return []

    @modal.method()
    def run(self, message: str, temperature: float = 0.1) -> dict:
        import torch
        import sys
        # Shared wrapper + cleanup from the mounted chike/ package (/root/chike).
        if '/root' not in sys.path:
            sys.path.insert(0, '/root')
        from chike.prompting import build_enriched_system
        from chike.generation_cleanup import clean_reply
        from chike.routing import is_uncomputable_payroll_amount

        if not message or not message.strip():
            return {'error': 'No message provided'}

        # OOC classifier — intercepts known out-of-scope topics before model call
        if not classify_question(message):
            print(f'[classifier] OOC intercepted: {message[:60]}')
            return {'reply': HARDCODED_REFUSAL}

        # Never-guess fabrication guard (R8): a payroll-levy AMOUNT asked with no salary
        # figure can't be computed — clarify instead of letting the model invent a number.
        # Shared predicate with the orchestrator's fact path (chike.routing), so the two
        # cannot diverge. Runs before decompose/RAG/generate: no model call on this path.
        if is_uncomputable_payroll_amount(message):
            print(f'[guard] uncomputable payroll amount -> clarify: {message[:60]}')
            return {'reply': PAYROLL_CLARIFICATION}

        # Query decomposition: split multi-part messages so each subdomain gets
        # its own top-3 retrieval, then merge (dedup, preserve order). A single
        # question yields one sub-query and behaves exactly as before.
        sub_queries = decompose_query(message)
        relevant_facts = []
        seen_facts = set()
        for sub_query in sub_queries:
            for fact in self.retrieve_facts(sub_query):
                if fact not in seen_facts:
                    relevant_facts.append(fact)
                    seen_facts.add(fact)
        # Cap at 9 facts (up to 3 sub-queries × top-3) to bound the prompt.
        relevant_facts = relevant_facts[:9]
        print(f'[RAG] query: {message[:80]}')
        print(f'[RAG] {len(sub_queries)} sub-queries -> {len(relevant_facts)} unique facts:')
        for _i, _f in enumerate(relevant_facts):
            print(f'[RAG]   {_i+1}. {_f[:120]}')
        # Enriched-system (UKWELI facts block) built by the shared chike.prompting —
        # single source of truth, identical to kaggle/eval.py and the orchestrator.
        # apply_chat_template scaffolding below is unchanged (production keeps the
        # tokenizer's real template; only the wrapper content is now shared).
        enriched_system = build_enriched_system(BASE_SYSTEM_PROMPT, relevant_facts)
        print(f'[RAG] enriched system prompt: {len(enriched_system)} chars '
              f'({len(relevant_facts)} facts)')

        messages = [
            {'role': 'system', 'content': enriched_system},
            {'role': 'user',   'content': message.strip()},
        ]

        try:
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            prompt = (
                f'<|begin_of_text|>'
                f'<|start_header_id|>system<|end_header_id|>\n\n'
                f'{enriched_system}<|eot_id|>'
                f'<|start_header_id|>user<|end_header_id|>\n\n'
                f'{message.strip()}<|eot_id|>'
                f'<|start_header_id|>assistant<|end_header_id|>\n\n'
            )

        inputs    = self.tokenizer(prompt, return_tensors='pt').to(self.model.device)
        input_len = inputs['input_ids'].shape[1]

        # Hard stop the instant the model tries to open a new Q&A turn — kills the
        # fabricated follow-up turns (with hallucinated URLs) that ran past the answer.
        from transformers import StoppingCriteria, StoppingCriteriaList

        class StopOnSubstrings(StoppingCriteria):
            def __init__(self, tokenizer, stop_strings):
                self.tokenizer = tokenizer
                self.stop_strings = stop_strings

            def __call__(self, input_ids, scores, **kwargs):
                text = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
                return any(s in text[-100:] for s in self.stop_strings)

        stopping_criteria = StoppingCriteriaList(
            [StopOnSubstrings(self.tokenizer, STOP_STRINGS)]
        )

        gen_kwargs = dict(
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=DO_SAMPLE,
            repetition_penalty=REPETITION_PENALTY,
            no_repeat_ngram_size=NO_REPEAT_NGRAM,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            stopping_criteria=stopping_criteria,
        )
        if DO_SAMPLE:
            gen_kwargs['temperature'] = GEN_TEMPERATURE
        print(f'[gen] max_new_tokens={MAX_NEW_TOKENS} do_sample={DO_SAMPLE} '
              f'repetition_penalty={REPETITION_PENALTY} no_repeat_ngram_size={NO_REPEAT_NGRAM}')
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)

        new_tokens = outputs[0][input_len:]
        reply = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        for stop in ['<|start_header_id|>', 'User:', 'Mtumiaji:'] + STOP_STRINGS:
            if stop in reply:
                reply = reply.split(stop)[0].strip()

        # Full stop/clean: truncates fabricated follow-up turns + strips role junk/special
        # tokens, then applies the old clean_generated_reply. Identical to eval.py and the
        # orchestrator (the manual stop loop above is now a subset of clean_reply, kept as
        # a harmless fast-path). Passing STOP_STRINGS makes the truncation config-exact.
        reply = clean_reply(reply, STOP_STRINGS)

        print(f'[chike] Q: {message[:60]}')
        print(f'[chike] A: {reply[:60]}')

        return {'reply': reply}

    @modal.method()
    def generate_raw(self, prompt: str, params: dict = None) -> dict:
        """RAW completion primitive: tokenize -> generate -> decode. NO classify /
        decompose / RAG / system prompt / cleaning.

        This is the primitive the v16 orchestrator (chike/orchestrator.py) drives via
        LocalAdapter: the orchestrator owns ALL pipeline logic and hands this a finished
        prompt; the real v15 weights only complete it. Kept separate from run() so the
        production endpoint's behaviour is unchanged. Defaults mirror run()'s generation
        config; a params dict overrides per call (slot extraction needs the raw text,
        e.g. JSON, that run() would otherwise strip/clean away).
        """
        import torch
        params = params or {}
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.model.device)
        input_len = inputs['input_ids'].shape[1]
        gen_kwargs = dict(
            max_new_tokens=int(params.get('max_new_tokens', MAX_NEW_TOKENS)),
            do_sample=bool(params.get('do_sample', DO_SAMPLE)),
            repetition_penalty=float(params.get('repetition_penalty', REPETITION_PENALTY)),
            no_repeat_ngram_size=int(params.get('no_repeat_ngram_size', NO_REPEAT_NGRAM)),
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        if gen_kwargs['do_sample']:
            gen_kwargs['temperature'] = float(params.get('temperature', GEN_TEMPERATURE))
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)
        # skip_special_tokens=False: return TRULY raw output so the v16 orchestrator's
        # clean stage can truncate at the '<|eot_id|>' / '<|start_header_id|>' turn
        # boundaries (the post-hoc equivalent of production's StoppingCriteria). This
        # endpoint stays dumb — all stopping/cleaning is the orchestrator's job.
        completion = self.tokenizer.decode(
            outputs[0][input_len:], skip_special_tokens=False
        ).strip()
        return {'completion': completion}


@app.function(image=web_image, secrets=[modal.Secret.from_name('modal-api-token')])
@modal.fastapi_endpoint(method='POST')
def web_endpoint(item: dict, token: str = None):
    # Token-gate the public endpoint (token passed as ?token=... query param).
    # Query param (not a header) avoids a module-level `from fastapi import Header`,
    # which would crash the GPU container that imports this module without fastapi.
    import os
    from fastapi.responses import JSONResponse
    expected = os.environ.get('MODAL_API_TOKEN', '')
    if not token or not expected or token != expected:
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    # Forward to the GPU class; returns main.py's contract: {"reply": ...} / {"error": ...}
    return ChikeModel().run.remote(item.get('message', ''))


@app.function(image=web_image, secrets=[modal.Secret.from_name('modal-api-token')])
@modal.fastapi_endpoint(method='POST')
def generate_endpoint(item: dict, token: str = None):
    """RAW completion endpoint for the v16 orchestrator. Same token gate as
    web_endpoint, but calls generate_raw (no v15 pipeline). Body: {"prompt": str,
    "params": {...}} -> {"completion": str}. Production web_endpoint is unaffected."""
    import os
    from fastapi.responses import JSONResponse
    expected = os.environ.get('MODAL_API_TOKEN', '')
    if not token or not expected or token != expected:
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    return ChikeModel().generate_raw.remote(
        item.get('prompt', ''), item.get('params') or {}
    )

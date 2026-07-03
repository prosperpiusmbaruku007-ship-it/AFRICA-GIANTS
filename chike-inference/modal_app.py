import os
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
)

# Tiny image for the HTTP endpoint (only needs FastAPI; it just forwards to the GPU class).
web_image = modal.Image.debian_slim(python_version='3.11').pip_install('fastapi[standard]')

volume = modal.Volume.from_name('chike-storage', create_if_missing=True)

ADAPTER_REPO = 'prospAprospA007/africa-giants-adapter-v13'
BASE_MODEL   = 'McGill-NLP/AfriqueLlama-8B'   # adapter v8 references this base

# Pre-computed RAG assets (baked into the image above)
RAG_DIR     = '/root/assets'
_EMB_PATH   = os.path.join(RAG_DIR, 'rag_embeddings.npy')
_TEXTS_PATH = os.path.join(RAG_DIR, 'rag_facts_text.json')

# Cache locations on the persistent volume (fast cold starts after first download)
HF_CACHE_DIR    = '/persistent-storage/.cache/huggingface'
MODEL_CACHE_DIR = '/persistent-storage/.cache/huggingface/hub'

# === System prompt — must stay in sync with kaggle/chike_config.json ===
BASE_SYSTEM_PROMPT = (
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

# === Inference-time OOC classifier ===
# Uses phrase-level (multi-word) matching to avoid single-word false positives.
# Ambiguous questions pass through to the model — better to attempt than wrongly refuse.

EXPLICIT_OOC_PHRASES = [
    # Capital gains
    'capital gain', 'faida ya mtaji', 'kodi ya faida ya mtaji',
    'nilinunua ardhi', 'nilinunua nyumba', 'niliuza ardhi', 'niliuza nyumba',
    # Import / customs duty
    'import duty', 'customs duty', 'ushuru wa forodha', 'ushuru wa uagizaji',
    'kodi ya uagizaji', 'kuagiza bidhaa', 'duty ya kuagiza',
    # Transfer pricing
    'transfer pricing', 'bei ya uhamisho', "arm's length",
    # Stamp duty and land valuation
    'stamp duty', 'ushuru wa stempu', 'tathmini ya ardhi', 'land valuation',
    # Mining royalties
    'mining royalt', 'mrabaha wa madini', 'royalty ya madini', 'ya royalty',
    # EPZ / special economic zones
    'export processing zone', 'epz tax', 'kodi ya epz', '(epz)',
    # Insurance premium levy
    'insurance premium levy', 'ushuru wa bima',
    # Zanzibar tax system (not general Zanzibar mention)
    'zanzibar tax', 'kodi ya zanzibar', 'kodi za zanzibar', 'vat zanzibar',
    # Crypto / investment
    'bitcoin', 'cryptocurrency', 'hisa za soko', 'stock market',
]

IN_SCOPE_PHRASES = [
    'brela', 'vat', 'ongezeko la thamani', 'paye', 'mapato ya ajira',
    'sdl', 'ufundi stadi', 'nssf', 'hifadhi ya jamii', 'osha', 'usalama kazini',
    'efd', 'mashine ya kodi', 'wcf', 'fidia ya wafanyakazi',
    'gn487a', 'gn 487', 'wageni', 'wasio raia',
    'kampuni', 'usajili', 'leseni ya biashara', 'tin', 'taxpayer',
]

HARDCODED_REFUSAL = (
    'Samahani, swali hili liko nje ya mada yangu. '
    'Ninasaidia tu maswali ya biashara na kodi Tanzania Bara — '
    'BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT, EFD, WCF, na GN487A. '
    'Kwa swali hili wasiliana na TRA (tra.go.tz) au mshauri wa kodi aliyehitimu.'
)


def classify_question(message: str) -> bool:
    """Return False if question is explicitly OOC, True otherwise (pass to model)."""
    msg = message.lower()
    for phrase in EXPLICIT_OOC_PHRASES:
        if phrase in msg:
            return False  # OOC — intercept
    for phrase in IN_SCOPE_PHRASES:
        if phrase in msg:
            return True   # clearly in-scope
    return True  # ambiguous — let model handle, do not over-intercept


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
                self.embed_model = SentenceTransformer(
                    'paraphrase-multilingual-MiniLM-L12-v2',
                    cache_folder='/persistent-storage/.cache/sentence_transformers',
                )
            q_emb  = self.embed_model.encode([question])
            scores = np.dot(self.fact_embeddings, q_emb.T).flatten()
            top_indices = np.argsort(scores)[-top_k:][::-1]
            return [self.fact_texts[i] for i in top_indices]
        except Exception as e:
            print(f'[rag] retrieve_facts error: {e}')
            return []

    @modal.method()
    def run(self, message: str, temperature: float = 0.1) -> dict:
        import torch

        if not message or not message.strip():
            return {'error': 'No message provided'}

        # OOC classifier — intercepts known out-of-scope topics before model call
        if not classify_question(message):
            print(f'[classifier] OOC intercepted: {message[:60]}')
            return {'reply': HARDCODED_REFUSAL}

        relevant_facts = self.retrieve_facts(message)
        if relevant_facts:
            facts_block = '\n'.join(f'- {f}' for f in relevant_facts)
            enriched_system = (
                BASE_SYSTEM_PROMPT
                + '\n\nUKWELI ULIOTHIBITISHWA KWA SWALI HILI:\n'
                + facts_block
                + '\n\nTumia ukweli huu. Usibuni takwimu ambazo hazipo hapa.'
            )
            print(f'[rag] injected {len(relevant_facts)} facts for: {message[:50]}')
        else:
            enriched_system = BASE_SYSTEM_PROMPT

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

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=300,
                temperature=temperature,
                do_sample=True,
                repetition_penalty=1.3,
                no_repeat_ngram_size=4,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        new_tokens = outputs[0][input_len:]
        reply = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        for stop in ['<|start_header_id|>', 'User:', 'Mtumiaji:']:
            if stop in reply:
                reply = reply.split(stop)[0].strip()

        print(f'[chike] Q: {message[:60]}')
        print(f'[chike] A: {reply[:60]}')

        return {'reply': reply}


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

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

# The user-facing OOC refusal now lives with the classifier that triggers it, in the shared
# chike.classification module (REFUSAL_TEXT) — byte-identical to the string this file used to
# define inline. It is imported lazily inside ChikeModel.run(), alongside the other chike
# imports, for the same reason classify_question imports lazily: the chike/ package is mounted
# only in the GPU image. The v16 orchestrator carried a DIFFERENT, terser refusal that the
# refusal gate could not distinguish (both match refusal_phrases); sharing one constant makes
# that divergence impossible.

# Never-guess (R8) clarification for a payroll-levy AMOUNT asked with no salary/payroll
# figure given: now chike.pipeline_v15.PAYROLL_CLARIFICATION (== chike.clarification.
# PAYROLL_AMOUNT), byte-identical to the constant this file used to define inline.

# THE PIPELINE ITSELF — classify -> never-guess guard -> decompose -> retrieve+pool ->
# prompt -> generate -> stop-split -> clean — now lives in chike/pipeline_v15.py, imported
# by BOTH this file and the Phase D paired harness. It used to be inline here, alongside
# near-identical copies in kaggle/eval.py and chike/decomposition.py. run() below is now a
# thin adapter: it owns only the environment-specific stage (tokenize -> model.generate ->
# decode) and hands that to the shared pipeline as a callable. Behaviour is unchanged —
# tests/test_pipeline_v15.py proves the extracted stages are byte-identical to the inline
# ones this file used to run, across all 400 gate questions and 400 persisted generations.


# === R14 PIPELINE SELECTOR — 'v15' | 'v16' ===
# Which pipeline run() serves. DEFAULTS TO 'v15': an absent or unrecognised flag keeps the
# shipped path byte-for-byte, so a malformed config can never silently promote v16. Rollback
# is a config edit + redeploy, never a code change.
#
# Measured at 1476caa: ADR bar +3.6 raw / +1.6 reliable, both PASS; compute +13.7 / +8.7;
# 20 gains / 6 regressions with NO row where v16 is worse than v15 by any reading; fact path
# byte-identical on 281 of 282 non-compute scored rows; defective clarification rate 2.9%
# against <=5%. See the 1476caa entry in PROGRESS.md.
PIPELINE = str(CONFIG.get('pipeline', 'v15')).strip().lower()
if PIPELINE not in ('v15', 'v16'):
    print(f"[config] unrecognised pipeline={PIPELINE!r} -- falling back to 'v15'")
    PIPELINE = 'v15'
print(f'[config] pipeline = {PIPELINE}')


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
# Production's decomposer now lives in chike/decomposition_v15.py (leaf module) and is
# called via chike.pipeline_v15. It is the V15 shape deliberately — NO ordinal-enumeration
# split; that lives in chike/decomposition.py for the v16 path only. See the header of
# chike/decomposition_v15.py for why the two must stay distinct.


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

    def _generate(self, prompt: str) -> str:
        """The ONE environment-specific stage: tokenize -> generate -> decode.

        Handed to chike.pipeline_v15.answer as a callable. Everything around it (classify,
        never-guess guard, decompose, retrieve+pool, prompt build, stop-split, clean) is the
        shared pipeline, so the Phase D v15 arm runs the identical logic with only this
        function swapped for its Kaggle in-process equivalent. Body is verbatim from the
        former inline run(): same StoppingCriteria, same gen_kwargs, same slicing/decode."""
        import torch
        from transformers import StoppingCriteria, StoppingCriteriaList

        inputs    = self.tokenizer(prompt, return_tensors='pt').to(self.model.device)
        input_len = inputs['input_ids'].shape[1]

        # Hard stop the instant the model tries to open a new Q&A turn — kills the
        # fabricated follow-up turns (with hallucinated URLs) that ran past the answer.
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

        return self.tokenizer.decode(
            outputs[0][input_len:], skip_special_tokens=True
        ).strip()

    def _orchestrator(self):
        """The v16 Orchestrator, built ONCE per container and reused.

        Construction mirrors the harness that produced the 1476caa measurement
        (kaggle/eval_phase_d_paired.py:307) — same single-arm retriever, same system prompt,
        same defaulted gen_params so SlotExtractor.params stays None — with TWO deliberate
        differences, both of which exist to keep the container identical to what was measured
        rather than to change it:

        1. ooc_phrases / in_scope_phrases are passed EXPLICITLY from the baked CONFIG.
           THIS IS LOAD-BEARING, NOT TIDINESS. Orchestrator defaults them from
           classification.load_local_config(), which reads a REPO-RELATIVE
           ../kaggle/chike_config.json. Only chike/ is mounted in this image (at /root/chike),
           and the config is baked to /root/assets/ — so that path is /root/kaggle/... which
           does not exist, load_local_config() returns {}, and resolve_phrases({}) yields the
           hardcoded-only list: 39 OOC phrases instead of 107. Letting it default would
           silently drop all 68 config-only phrases, including the entire SAFETY-1 audit, and
           reopen the Gate-2 leak that audit closed. It would have passed every offline test.
           This is the R16 class of failure — a config-only value that never reaches the
           container — so it is closed here rather than trusted.

        2. stop_strings is set explicitly for the same reason. A behavioural no-op TODAY
           (generation_cleanup.STOP_STRINGS is byte-equal to the config list, verified), so
           this changes nothing now and stops a future config-only edit from reaching
           production and the gate but not the v16 clean stage. Set as an attribute rather
           than via gen_params, because gen_params also becomes SlotExtractor.params and the
           measured configuration had that None.

        Deliberately ABSENT: pipeline_v15's is_uncomputable_payroll_amount never-guess guard.
        v16 reaches the same outcome through the compute path's own clarification, and adding
        the v15 guard here would make production differ from the arm that was measured.
        """
        orch = getattr(self, '_orch', None)
        if orch is not None:
            return orch

        from chike.classification import resolve_phrases
        from chike.model_abstraction import ModelBackend
        from chike.orchestrator import Orchestrator

        _generate = self._generate
        _tokenizer = self.tokenizer

        class _ContainerBackend(ModelBackend):
            """The `tokenizer` attribute is what Orchestrator._backend_tokenizer() looks for.
            Without it build_chat_prompt silently falls back to a naive-concat shape the model
            was never trained on — the same trap the Kaggle harness documents at its own
            _Backend."""

            def __init__(self):
                self.tokenizer = _tokenizer

            def generate(self, prompt, params=None):
                # _generate applies the config gen_kwargs and the StopOnSubstrings criteria,
                # exactly as the harness twin does. params is unused because the measured
                # configuration never passed any (SlotExtractor.params was None).
                return _generate(prompt)

        ooc_phrases, in_scope_phrases = resolve_phrases(CONFIG)
        orch = Orchestrator(
            backend=_ContainerBackend(),
            # SINGLE-ARM retrieval — production's own bound method, never chike.retrieval's
            # two-arm hybrid. Four measurements have failed to show a two-arm benefit and the
            # only two genuine non-clarification regressions ever recorded were its artefacts.
            retriever=self.retrieve_facts,
            ooc_phrases=ooc_phrases,
            in_scope_phrases=in_scope_phrases,
            system_prompt=BASE_SYSTEM_PROMPT,
        )
        orch.stop_strings = tuple(STOP_STRINGS)
        print(f'[v16] orchestrator built: {len(ooc_phrases)} ooc / '
              f'{len(in_scope_phrases)} in_scope phrases, single-arm retriever')
        self._orch = orch
        return orch

    @modal.method()
    def run(self, message: str, temperature: float = 0.1) -> dict:
        """Production entry point.

        Serves whichever pipeline the R14 `pipeline` flag selects. On 'v15' (the default) this
        is a thin adapter over the shared v15 pipeline: chike.pipeline_v15.answer owns the
        sequence and this supplies the three things only the Modal container can — the loaded
        tokenizer, the single-arm retrieve_facts bound to the baked index, and _generate.
        Behaviour on that path is unchanged from the former inline version
        (tests/test_pipeline_v15.py proves every extracted stage byte-identical across the 400
        gate questions and 400 persisted generations).

        On 'v16' the orchestrator owns the sequence instead. Both return the same
        {'reply': str} contract, and both refuse with the one shared REFUSAL_TEXT, so the
        refusal gate cannot tell them apart on a refusal — which is why the phrase lists in
        _orchestrator() have to be right rather than merely present."""
        import sys
        # The chike/ package is mounted at /root only in the GPU image.
        if '/root' not in sys.path:
            sys.path.insert(0, '/root')

        if PIPELINE == 'v16':
            if not message or not message.strip():
                return {'error': 'No message provided'}
            reply = self._orchestrator().answer(message)
            print(f'[chike/v16] Q: {message[:60]}')
            print(f'[chike/v16] A: {reply.text[:60]}')
            return {'reply': reply.text}

        from chike import pipeline_v15

        return pipeline_v15.answer(
            message,
            generate=self._generate,
            # SINGLE-ARM retrieval — production's own method, not chike.retrieval's two-arm
            # hybrid. See chike/pipeline_v15.py's header for why that distinction is
            # load-bearing for the Phase D comparison.
            retrieve_facts=self.retrieve_facts,
            system_prompt=BASE_SYSTEM_PROMPT,
            tokenizer=self.tokenizer,
            stop_strings=STOP_STRINGS,
            config=CONFIG,
            log=print,
        )

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

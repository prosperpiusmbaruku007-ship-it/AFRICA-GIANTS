import os
import shutil
import hashlib
import json

# === 2a: RAG paths — SENTENCE_TRANSFORMERS_HOME must be set before any ST import ===
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/persistent-storage/.cache/sentence_transformers'

FACTS_PATH      = 'locked_facts.json'
EMBEDDINGS_PATH = '/persistent-storage/rag_embeddings.npy'
FACTS_TEXT_PATH = '/persistent-storage/rag_facts_text.json'
HASH_PATH       = '/persistent-storage/locked_facts_hash.txt'
EMBED_MODEL     = 'paraphrase-multilingual-MiniLM-L12-v2'

# Route HF cache to persistent storage for fast cold starts.
# v8 is the active adapter; v10 reverted pending better training data (2026-06-22).
HF_CACHE_DIR    = '/persistent-storage/.cache/huggingface'
MODEL_CACHE_DIR = '/persistent-storage/.cache/huggingface/hub'
os.environ['HF_HOME'] = HF_CACHE_DIR
os.makedirs(HF_CACHE_DIR, exist_ok=True)

# Delete all adapter caches except v8
for _old in ['v3', 'v4', 'v5', 'v6', 'v7', 'v9', 'v10']:
    _old_path = f'/persistent-storage/.cache/huggingface/hub/models--prospAprospA007--africa-giants-adapter-{_old}'
    if os.path.exists(_old_path):
        shutil.rmtree(_old_path)
        print(f'[cache] Deleted old model: {_old_path}')

import torch
import numpy as np
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v8"
HF_TOKEN     = os.environ.get("HF_TOKEN", "")

if HF_TOKEN:
    login(token=HF_TOKEN)
    print("[chike] HuggingFace authenticated")
else:
    print("[chike] WARNING: HF_TOKEN not set -- model may fail to load")


# === 2b: Persistent embedding cache (numpy only -- no FAISS) ===

def _locked_facts_texts():
    """Extract human-readable strings from locked_facts.json for embedding."""
    if not os.path.exists(FACTS_PATH):
        return []
    with open(FACTS_PATH, encoding='utf-8') as f:
        locked = json.load(f)
    texts = []
    for key, val in locked.items():
        if key == '_meta':
            continue
        if isinstance(val, dict):
            fact_str = val.get('fact') or f"{key}: {val.get('correct_value', str(val))}"
        else:
            fact_str = f"{key}: {val}"
        texts.append(fact_str)
    return texts

def _md5_file(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


fact_embeddings = None
fact_texts      = []
embed_model     = None

def _build_rag_index():
    global fact_embeddings, fact_texts, embed_model
    if not os.path.exists(FACTS_PATH):
        print(f"[rag] {FACTS_PATH} not found -- RAG disabled")
        return

    # Always load the ST model (first run: 420MB download to persistent storage; after: disk load)
    from sentence_transformers import SentenceTransformer
    embed_model = SentenceTransformer(EMBED_MODEL)

    current_hash = _md5_file(FACTS_PATH)

    # Load from cache if hash unchanged
    if (os.path.exists(EMBEDDINGS_PATH) and
            os.path.exists(FACTS_TEXT_PATH) and
            os.path.exists(HASH_PATH) and
            open(HASH_PATH).read().strip() == current_hash):
        fact_embeddings = np.load(EMBEDDINGS_PATH)
        with open(FACTS_TEXT_PATH, encoding='utf-8') as f:
            fact_texts = json.load(f)
        print(f"[rag] index loaded from cache -- {len(fact_texts)} facts")
        return

    # Rebuild
    print("[rag] rebuilding embedding index ...")
    fact_texts = _locked_facts_texts()
    if not fact_texts:
        print("[rag] no facts extracted -- RAG disabled")
        return
    fact_embeddings = embed_model.encode(fact_texts)
    np.save(EMBEDDINGS_PATH, fact_embeddings)
    with open(FACTS_TEXT_PATH, 'w', encoding='utf-8') as f:
        json.dump(fact_texts, f, ensure_ascii=False)
    with open(HASH_PATH, 'w') as f:
        f.write(current_hash)
    print(f"[rag] embeddings rebuilt -- {len(fact_texts)} facts embedded")

_build_rag_index()


# === 2c: Retrieval function (pure numpy cosine similarity) ===

def retrieve_facts(question: str, top_k: int = 3) -> list:
    if fact_embeddings is None or not fact_texts or embed_model is None:
        return []
    try:
        q_emb  = embed_model.encode([question])[0]
        scores = np.dot(fact_embeddings, q_emb.T).flatten()
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [fact_texts[i] for i in top_indices]
    except Exception as e:
        print(f"[rag] retrieve_facts error: {e}")
        return []


# === System prompt — renamed to BASE so run() can enrich it ===

BASE_SYSTEM_PROMPT = (
    "Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. "
    "Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. "
    "Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, "
    "OSHA, SDL, PAYE, VAT kwa Kiswahili na Kiingereza. "
    "Kama swali liko nje ya mada yako sema wazi kwamba halijui "
    "na mwelekeze kwa TRA au mshauri aliyehitimu. "
    "Your name is Chike, a business adviser from Africa Giants. "
    "Tagline: Fahamu Biashara Yako, Maarifa Yako. "
    "You answer Tanzanian business, tax, and compliance questions "
    "in Swahili and English. "
    "If a question is outside your knowledge say so clearly "
    "and direct the user to TRA or a qualified adviser."
)

_model     = None
_tokenizer = None

def get_model():
    global _model, _tokenizer
    if _model is None:
        print("[chike] Loading tokenizer ...")
        _tokenizer = AutoTokenizer.from_pretrained(
            ADAPTER_REPO,
            cache_dir=MODEL_CACHE_DIR,
            token=HF_TOKEN if HF_TOKEN else None,
            trust_remote_code=True,
        )
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token

        try:
            print("[chike] Loading model in 4bit ...")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            _model = AutoModelForCausalLM.from_pretrained(
                ADAPTER_REPO,
                cache_dir=MODEL_CACHE_DIR,
                quantization_config=bnb_config,
                device_map="auto",
                token=HF_TOKEN if HF_TOKEN else None,
                trust_remote_code=True,
            )
            print("[chike] Model loaded in 4bit -- ready")
        except Exception as e:
            print(f"[chike] 4bit load failed ({e}), falling back to float16 ...")
            _model = AutoModelForCausalLM.from_pretrained(
                ADAPTER_REPO,
                cache_dir=MODEL_CACHE_DIR,
                torch_dtype=torch.float16,
                device_map="auto",
                token=HF_TOKEN if HF_TOKEN else None,
                trust_remote_code=True,
            )
            print("[chike] Model loaded in float16 -- ready")

        _model.eval()
    return _model, _tokenizer


def run(message: str, temperature: float = 0.1):
    if not message or not message.strip():
        return {"error": "No message provided"}

    model, tokenizer = get_model()

    # === 2d: Enrich system prompt with retrieved facts ===
    relevant_facts = retrieve_facts(message)
    if relevant_facts:
        facts_block = "\n".join(f"- {f}" for f in relevant_facts)
        enriched_system = (
            BASE_SYSTEM_PROMPT
            + "\n\nUKWELI ULIOTHIBITISHWA KWA SWALI HILI:\n"
            + facts_block
            + "\n\nTumia ukweli huu. Usibuni takwimu ambazo hazipo hapa."
        )
        print(f"[rag] injected {len(relevant_facts)} facts for: {message[:50]}")
    else:
        enriched_system = BASE_SYSTEM_PROMPT

    messages = [
        {"role": "system", "content": enriched_system},
        {"role": "user",   "content": message.strip()},
    ]

    try:
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    except Exception:
        prompt = (
            f"<|begin_of_text|>"
            f"<|start_header_id|>system<|end_header_id|>\n\n"
            f"{enriched_system}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{message.strip()}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

    inputs    = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=temperature,
            do_sample=True,
            repetition_penalty=1.3,
            no_repeat_ngram_size=4,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    new_tokens = outputs[0][input_len:]
    reply = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    for stop in ["<|start_header_id|>", "User:", "Mtumiaji:"]:
        if stop in reply:
            reply = reply.split(stop)[0].strip()

    print(f"[chike] Q: {message[:60]}")
    print(f"[chike] A: {reply[:60]}")

    return {"reply": reply}

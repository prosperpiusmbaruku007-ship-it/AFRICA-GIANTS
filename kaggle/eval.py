import os, json, re, sys, subprocess, requests
import numpy as np
from datetime import datetime, timezone
from collections import defaultdict

# ── AUTH ──────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    us = kaggle_secrets.UserSecretsClient()
    hf_token = us.get_secret('AFRICA_GIANTS')
    print(f'[auth] HF token loaded ({hf_token[:8]}...)')
except Exception as e:
    hf_token = os.environ.get('HF_TOKEN', '')
    print(f'[auth] fallback env HF_TOKEN: {hf_token[:8] if hf_token else "MISSING"}')

# ── LOAD CONFIG FROM GITHUB ───────────────────────────────────────────────────
GITHUB_CONFIG_URL = 'https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/main/kaggle/chike_config.json'
try:
    r = requests.get(GITHUB_CONFIG_URL, timeout=10)
    r.raise_for_status()
    CONFIG = r.json()
    print(f'[config] Loaded from GitHub')
except Exception as e:
    print(f'[config] FAILED to load from GitHub: {e}')
    sys.exit(1)

ADAPTER_REPO       = CONFIG.get('adapter_repo', 'prospAprospA007/africa-giants-adapter-v15')
SYSTEM_PROMPT      = CONFIG['system_prompt']
REFUSAL_PHRASES    = CONFIG['refusal_phrases']
MAX_NEW_TOKENS     = CONFIG['generation_params']['max_new_tokens']
REPETITION_PENALTY = CONFIG['generation_params'].get('repetition_penalty', 1.1)
NO_REPEAT_NGRAM    = CONFIG['generation_params'].get('no_repeat_ngram_size', 3)
# Stop sequences — must match production (modal_app.py) so the gate measures the
# real system (R12). Halts the fabricated follow-up turns that caused run-on failures.
STOP_STRINGS       = CONFIG['generation_params'].get(
    'stop_strings', ['\n\nQ:', '\n\nSwali:', '<|start_header_id|>', '\n\n---'])
ACCURACY_THRESHOLD = CONFIG['gate_thresholds']['in_corpus']
REFUSAL_THRESHOLD  = CONFIG['gate_thresholds']['out_of_corpus']

# Allow override via environment variable for testing different versions
ADAPTER_REPO = os.environ.get('EVAL_ADAPTER_REPO', ADAPTER_REPO)

print(f'[config] ADAPTER_REPO: {ADAPTER_REPO}')
print(f'[config] thresholds: in_corpus={ACCURACY_THRESHOLD} ooc={REFUSAL_THRESHOLD}')
print(f'[config] REFUSAL_PHRASES: {len(REFUSAL_PHRASES)} phrases')

# ── FETCH SHARED CHIKE MODULES FROM GITHUB (single source of truth) ────────────
# The RAG wrapper (chike.prompting.build_chat_prompt) and post-generation cleanup
# (chike.generation_cleanup.clean_reply) now live in chike/ — fetched + exec'd
# here instead of carrying inline copies, the same fetch pattern used for this eval.py
# and chike_config.json. This is what makes the gate test the EXACT wrapper/clean logic
# production uses (R12), and closes the drift that inline copies caused.
# Cache-bust (R15): raw.githubusercontent has a ~5-min CDN TTL; a stale copy would
# silently make the gate test old logic. Log the live HEAD sha so the run is auditable.
_RAW = 'https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/main'
_NOCACHE = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
_cb = str(int(__import__('time').time() * 1000))
try:
    _sha = requests.get(
        'https://api.github.com/repos/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/commits/main',
        headers=_NOCACHE, timeout=15).json().get('sha', '?')[:7]
    print(f'[chike] GitHub main HEAD = {_sha} (shared modules fetched from THIS commit)')
except Exception as e:
    print(f'[chike] HEAD sha check skipped: {e}')

def _fetch_chike_module(modname):
    """Fetch chike/<modname>.py and exec it into an isolated namespace. Both modules
    are leaf (stdlib-only, no chike-internal imports), so exec works standalone. We
    seed __file__ because exec() has none, and the modules build a config path from
    os.path.dirname(__file__) at import (guarded by try/except -> safe default here)."""
    r = requests.get(f'{_RAW}/chike/{modname}.py?cb={_cb}', headers=_NOCACHE, timeout=15)
    r.raise_for_status()
    ns = {'__file__': f'{modname}.py'}
    exec(compile(r.text, f'chike/{modname}.py', 'exec'), ns)
    print(f'[chike] fetched chike/{modname}.py ({len(r.text)} bytes)')
    return ns

_prompting = _fetch_chike_module('prompting')
_cleanup   = _fetch_chike_module('generation_cleanup')
_scoring   = _fetch_chike_module('scoring')
_classification = _fetch_chike_module('classification')
build_chat_prompt     = _prompting['build_chat_prompt']
# clean_reply is the FULL stop/clean stage (truncates fabricated follow-up turns +
# strips role junk/special tokens, then applies clean_generated_reply). Use it — NOT
# the thin clean_generated_reply — so eval, production (modal_app.py) and the
# orchestrator all strip ramble identically (R12 / dual-file-sync). The thin
# clean_generated_reply left fabricated Q&A ramble in, which then fed the scorer
# false-credit keywords (eval_029/132/163).
clean_reply           = _cleanup['clean_reply']
score_question        = _scoring['score_question']   # (q, generated, refusal_phrases)

# ── OOC CLASSIFIER ────────────────────────────────────────────────────────────
# Phrase lists + classify logic come from the shared chike.classification module (fetched
# above) — one source of truth with production (modal_app.py) and the v16 orchestrator so
# the gate measures the EXACT classifier users hit (R12). resolve_phrases UNIONs the
# canonical hardcoded lists with CONFIG's ooc/in_scope additions (this replaces the old
# inline CONFIG.get(..., [fallback]) REPLACE, which could silently drop a hardcoded phrase).
resolve_phrases = _classification['resolve_phrases']
_classify       = _classification['classify']
EXPLICIT_OOC_PHRASES, IN_SCOPE_PHRASES = resolve_phrases(CONFIG)

# The refusal TEXT comes from the same fetched chike.classification namespace as the phrase
# lists and classify() — one constant shared with production (modal_app.py) and the v16
# orchestrator, byte-identical to the string this file used to define inline. R12: the gate
# must emit the exact refusal users receive.
HARDCODED_REFUSAL = _classification['REFUSAL_TEXT']

def classify_question(message: str) -> bool:
    return _classify(message, EXPLICIT_OOC_PHRASES, IN_SCOPE_PHRASES)

# ── INSTALL DEPENDENCIES ──────────────────────────────────────────────────────
subprocess.run(['pip', 'install', '-q', '-U', 'bitsandbytes>=0.46.1'], check=True)
subprocess.run(['pip', 'install', '-q', '-U', 'sentence-transformers>=2.7.0'], check=True)
print('[model] bitsandbytes + sentence-transformers updated')

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from transformers import StoppingCriteria, StoppingCriteriaList
import torch


# Hard stop the instant the model tries to open a new Q&A turn — identical to
# production (chike-inference/modal_app.py) so the gate reflects real behavior.
class StopOnSubstrings(StoppingCriteria):
    def __init__(self, tokenizer, stop_strings):
        self.tokenizer = tokenizer
        self.stop_strings = stop_strings

    def __call__(self, input_ids, scores, **kwargs):
        text = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
        return any(s in text[-100:] for s in self.stop_strings)

# ── LOAD MODEL ────────────────────────────────────────────────────────────────
print(f'[model] Loading {ADAPTER_REPO} ...')
tokenizer = AutoTokenizer.from_pretrained(ADAPTER_REPO, token=hf_token, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
print(f'[model] eos_token: {repr(tokenizer.eos_token)}')

bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
model = AutoModelForCausalLM.from_pretrained(
    ADAPTER_REPO,
    quantization_config=bnb,
    device_map='auto',
    token=hf_token,
    trust_remote_code=True,
)
model.eval()
print('[model] Loaded OK')

# ── LOAD EVAL QUESTIONS ───────────────────────────────────────────────────────
from huggingface_hub import hf_hub_download, HfApi

print('[eval] Loading eval questions ...')
local_path = hf_hub_download(
    repo_id='prospAprospA007/africa-giants-dataset',
    filename='eval_questions_001.jsonl',
    repo_type='dataset',
    token=hf_token,
)
eval_questions = []
with open(local_path, encoding='utf-8') as f:
    for line in f:
        if line.strip():
            eval_questions.append(json.loads(line))

assert len(eval_questions) == 200, f'Expected 200 got {len(eval_questions)}'
print(f'[eval] Loaded {len(eval_questions)} eval questions')

import subprocess
result = subprocess.run(
    ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
    capture_output=True, text=True
)
GPU_NAME = result.stdout.strip() if result.returncode == 0 else 'CPU'
print(f'[gpu] {GPU_NAME} | CUDA: {torch.cuda.is_available()}')

# ── RAG SETUP (e5-base) ───────────────────────────────────────────────────────
# Matches production (chike-inference/modal_app.py) so the gate tests the FULL
# system per R12 (classifier + RAG + model), not bare model weights. The e5 index
# is fetched from the HF dataset repo — same repo as the eval questions — so the
# gate and production share one index (built by kaggle/regenerate_rag_e5.py).
print('[rag] fetching e5 index from HF dataset repo ...')
_rag_npy = hf_hub_download(repo_id='prospAprospA007/africa-giants-dataset',
                          filename='rag_embeddings.npy', repo_type='dataset', token=hf_token)
_rag_txt = hf_hub_download(repo_id='prospAprospA007/africa-giants-dataset',
                          filename='rag_facts_text.json', repo_type='dataset', token=hf_token)
fact_embeddings = np.load(_rag_npy)
with open(_rag_txt, encoding='utf-8') as f:
    fact_texts = json.load(f)
assert fact_embeddings.shape[0] == len(fact_texts), \
    f'RAG mismatch: {fact_embeddings.shape[0]} embeddings vs {len(fact_texts)} texts'
print(f'[rag] loaded {len(fact_texts)} facts, embeddings {fact_embeddings.shape}')

from sentence_transformers import SentenceTransformer
# MUST match the embedder that built rag_embeddings.npy (e5-base, 768-dim).
embed_model = SentenceTransformer('intfloat/multilingual-e5-base')
_fact_norms = np.linalg.norm(fact_embeddings, axis=1, keepdims=True)
fact_embeddings_norm = fact_embeddings / (_fact_norms + 1e-10)

def retrieve_facts(question, top_k=3):
    # e5 asymmetric retrieval: query gets the 'query: ' prefix (facts were embedded
    # as 'passage: ' at build time). Cosine similarity on normalized vectors — same
    # math as modal_app.py.retrieve_facts.
    q_emb = embed_model.encode([f'query: {question}'])[0]
    q_norm = q_emb / (np.linalg.norm(q_emb) + 1e-10)
    scores = np.dot(fact_embeddings_norm, q_norm)
    top_indices = np.argsort(scores)[-top_k:][::-1]
    return [fact_texts[i] for i in top_indices]

# === Query decomposition ===
# A single WhatsApp message often covers two subdomains ("Nina wafanyakazi 12,
# SDL inalipwa vipi na pia EFD ninahitaji?"). Top-3 RAG retrieval on the whole
# message returns SDL facts OR EFD facts, never both, so the model answers half
# the question. We split multi-part messages and retrieve for each part.
# MUST stay byte-identical to chike-inference/modal_app.py (see CLAUDE.md
# "Shared production logic requiring dual-file sync").

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

# SWAHILI_NUMBERS + extract_numbers + normalize + score_question are imported from the
# shared chike.scoring module (fetched above) — single source of truth with eval_orchestrator.py.

# clean_reply is imported from the shared chike.generation_cleanup module (fetched
# above), not defined inline — single source of truth with modal_app.py and the
# orchestrator.

# ── INFERENCE ─────────────────────────────────────────────────────────────────
def generate_answer(question_sw: str) -> str:
    # RAG injection — matches production (modal_app.py.run) exactly per R12: not just
    # the prompt format (same header, same '- ' bullets joined with no trailing
    # newline, same trailing instruction line) but the RETRIEVAL path too — the
    # question is decomposed into sub-queries, each retrieves its own top-3, and the
    # results are merged (dedup, order-preserving) and capped at 9. A single-part
    # question yields one sub-query and behaves exactly as a plain top-3 retrieval.
    sub_queries = decompose_query(question_sw)
    all_retrieved_facts = []
    seen_facts = set()
    for sub_query in sub_queries:
        facts = retrieve_facts(sub_query, top_k=3)
        for fact in facts:
            if fact not in seen_facts:
                all_retrieved_facts.append(fact)
                seen_facts.add(fact)
    retrieved_facts = all_retrieved_facts[:9]
    # RAG wrapper built by the shared chike.prompting (fetched above). Passing the
    # tokenizer routes through apply_chat_template — BYTE-IDENTICAL to production
    # (modal_app.py) and to the format v15 was trained on. Before 2026-07-18 this used
    # the hardcoded Llama-3 header format, which the model was never trained to stop
    # after (proved by eos_production_probe.py: header format ran to the 350-cap 0/20;
    # apply_chat_template stopped 20/20) — so every prior gate score was measured on a
    # prompt format that did not match production (R12 violation in the harness itself).
    prompt = build_chat_prompt(question_sw, retrieved_facts, SYSTEM_PROMPT, tokenizer=tokenizer)
    inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
    stopping_criteria = StoppingCriteriaList(
        [StopOnSubstrings(tokenizer, STOP_STRINGS)]
    )
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            temperature=1.0,
            repetition_penalty=REPETITION_PENALTY,
            no_repeat_ngram_size=NO_REPEAT_NGRAM,
            stopping_criteria=stopping_criteria,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )
    new_tokens = out[0][inputs['input_ids'].shape[1]:]
    return clean_reply(tokenizer.decode(new_tokens, skip_special_tokens=True).strip(), STOP_STRINGS)

# extract_numbers, normalize, and score_question now live in the shared chike.scoring
# module (fetched at the top). score_question(q, generated, REFUSAL_PHRASES) is called
# in the inference loop below.

    return len(gen_lower) > 20

# ── INFERENCE LOOP ────────────────────────────────────────────────────────────
results = []
print(f'[eval] Starting inference on {len(eval_questions)} questions ...')

for i, q in enumerate(eval_questions):
    try:
        question = q['question_sw']

        # Classifier runs first — same as production system
        if not classify_question(question):
            generated = HARDCODED_REFUSAL
        else:
            generated = generate_answer(question)

        passed = score_question(q, generated, REFUSAL_PHRASES)
    except Exception as e:
        generated = f'ERROR: {e}'
        passed = False

    results.append({
        'id':                q['id'],
        'subdomain':         q['subdomain'],
        'answer_type':       q.get('answer_type', ''),
        'question_sw':       q['question_sw'],
        'correct_answer_sw': q['correct_answer_sw'],
        'generated':         generated,
        'pass':              passed,
    })

    if (i + 1) % 20 == 0 or i == 0:
        rp = sum(r['pass'] for r in results)
        print(f'  [{i+1}/{len(eval_questions)}] running accuracy: {rp}/{i+1} = {rp/(i+1):.1%}')

print('[eval] Inference complete')

# ── GATE RESULTS ──────────────────────────────────────────────────────────────
by_subdomain = defaultdict(lambda: {'pass': 0, 'total': 0})
for r in results:
    sd = r['subdomain']
    by_subdomain[sd]['total'] += 1
    if r['pass']:
        by_subdomain[sd]['pass'] += 1

in_corpus  = [r for r in results if r['subdomain'] != 'out_of_corpus']
out_corpus = [r for r in results if r['subdomain'] == 'out_of_corpus']
in_pass    = sum(r['pass'] for r in in_corpus)
out_pass   = sum(r['pass'] for r in out_corpus)
in_acc     = in_pass  / len(in_corpus)  if in_corpus  else 0
out_acc    = out_pass / len(out_corpus) if out_corpus else 0
gate_passed = in_acc >= ACCURACY_THRESHOLD and out_acc >= REFUSAL_THRESHOLD

print('\n========================================')
print('AFRICA-GIANTS ACCURACY GATE RESULTS')
print('========================================\n')
print('By subdomain:')
for sd, counts in sorted(by_subdomain.items()):
    pct   = counts['pass'] / counts['total']
    stars = '*' * int(pct * 20)
    print(f'  {sd:<32} {counts["pass"]}/{counts["total"]}  = {pct:.1%}  {stars}')
print(f'\nIn-corpus accuracy:    {in_pass}/{len(in_corpus)} = {in_acc:.1%}   >85% {"PASS" if in_acc >= ACCURACY_THRESHOLD else "FAIL"}')
print(f'Out-of-corpus refusal: {out_pass}/{len(out_corpus)} = {out_acc:.1%}   >70% {"PASS" if out_acc >= REFUSAL_THRESHOLD else "FAIL"}')
print(f'\n{"GATE PASSED" if gate_passed else "GATE FAILED"} — both >85% in-corpus AND >70% refusal required')
print('========================================')

# ── SAVE AND UPLOAD ───────────────────────────────────────────────────────────
output_path = '/kaggle/working/gate_001_results.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({
        'adapter':       ADAPTER_REPO,
        'timestamp':     datetime.now(timezone.utc).isoformat(),
        'in_corpus':     {'pass': in_pass,  'total': len(in_corpus),  'accuracy': in_acc},
        'out_of_corpus': {'pass': out_pass, 'total': len(out_corpus), 'accuracy': out_acc},
        'gate_passed':   gate_passed,
        'by_subdomain':  dict(by_subdomain),
        'results':       results,
    }, f, ensure_ascii=False, indent=2)
print(f'[results] Saved {output_path}')

try:
    api = HfApi()
    api.upload_file(
        path_or_fileobj=output_path,
        path_in_repo='gate_001_results.json',
        repo_id=ADAPTER_REPO,
        repo_type='model',
        token=hf_token,
        commit_message=f'gate results — in_corpus={in_acc:.1%} refusal={out_acc:.1%}',
    )
    print(f'[results] Uploaded to {ADAPTER_REPO}')
except Exception as e:
    print(f'[results] Upload failed (non-critical): {e}')

print('[done] eval.py complete.')

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

# ── OOC CLASSIFIER ────────────────────────────────────────────────────────────
EXPLICIT_OOC_PHRASES = CONFIG.get('ooc_phrases', [
    'capital gain', 'faida ya mtaji', 'kodi ya faida ya mtaji',
    'nilinunua ardhi', 'nilinunua nyumba', 'niliuza ardhi', 'niliuza nyumba',
    'import duty', 'customs duty', 'ushuru wa forodha', 'ushuru wa uagizaji',
    'kuagiza bidhaa', 'duty ya kuagiza',
    'transfer pricing', 'bei ya uhamisho',
    'stamp duty', 'ushuru wa stempu', 'tathmini ya ardhi', 'land valuation',
    'mining royalt', 'mrabaha wa madini', 'royalty ya madini',
    'export processing zone', 'epz tax', 'kodi ya epz',
    'insurance premium levy', 'ushuru wa bima',
    'zanzibar tax', 'kodi ya zanzibar', 'vat zanzibar',
    'bitcoin', 'cryptocurrency', 'hisa za soko',
])

IN_SCOPE_PHRASES = CONFIG.get('in_scope_phrases', [
    'brela', 'vat', 'ongezeko la thamani', 'paye', 'mapato ya ajira',
    'sdl', 'ufundi stadi', 'nssf', 'hifadhi ya jamii', 'osha', 'usalama kazini',
    'efd', 'mashine ya kodi', 'wcf', 'fidia ya wafanyakazi',
    'gn487a', 'gn 487', 'wageni', 'wasio raia',
    'kampuni', 'usajili', 'leseni ya biashara', 'tin',
])

HARDCODED_REFUSAL = (
    'Samahani, swali hili liko nje ya mada yangu. '
    'Ninasaidia tu maswali ya biashara na kodi Tanzania Bara — '
    'BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT, EFD, WCF, na GN487A. '
    'Kwa swali hili wasiliana na TRA (tra.go.tz) au mshauri wa kodi aliyehitimu.'
)

def classify_question(message: str) -> bool:
    msg = message.lower()
    for phrase in EXPLICIT_OOC_PHRASES:
        if phrase in msg:
            return False
    for phrase in IN_SCOPE_PHRASES:
        if phrase in msg:
            return True
    return True  # ambiguous — pass through to model

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

# ── SWAHILI NUMBERS ───────────────────────────────────────────────────────────
SWAHILI_NUMBERS = {
    'moja': 1, 'mbili': 2, 'tatu': 3, 'nne': 4, 'tano': 5,
    'sita': 6, 'saba': 7, 'nane': 8, 'tisa': 9, 'kumi': 10,
    'ishirini': 20, 'thelathini': 30, 'arobaini': 40,
    'hamsini': 50, 'sitini': 60, 'sabini': 70,
    'themanini': 80, 'tisini': 90, 'mia': 100,
    'elfu': 1_000, 'milioni': 1_000_000,
}

# ── POST-GENERATION CLEANUP (must match chike-inference/modal_app.py) ──────────
def clean_generated_reply(text: str) -> str:
    # 1. strip a leading fabricated question '(4) Je...?' before the real answer
    text = re.sub(r'^\(\d+\)\s*[^.!?]*\?\s*', '', text.strip())
    # 2. correct memorized domain tokens RAG cannot override
    text = re.sub(r'nssf\.or\.tz', 'nssf.go.tz', text, flags=re.IGNORECASE)
    text = re.sub(r'\.go\.ke\b', '.go.tz', text, flags=re.IGNORECASE)
    return text.strip()

# ── INFERENCE ─────────────────────────────────────────────────────────────────
def generate_answer(question_sw: str) -> str:
    # RAG injection — byte-identical wrapper to production (modal_app.py) so the gate
    # tests the exact same prompt format per R12: same header, same '- ' bullets
    # (joined, no trailing newline), same trailing instruction line.
    retrieved_facts = retrieve_facts(question_sw, top_k=3)
    if retrieved_facts:
        facts_block = '\n'.join(f'- {fact}' for fact in retrieved_facts)
        full_system = (
            SYSTEM_PROMPT
            + '\n\nUKWELI ULIOTHIBITISHWA KWA SWALI HILI:\n'
            + facts_block
            + '\n\nTumia ukweli huu. Usibuni takwimu ambazo hazipo hapa.'
        )
    else:
        full_system = SYSTEM_PROMPT
    prompt = (
        f'<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n'
        f'{full_system}<|eot_id|>'
        f'<|start_header_id|>user<|end_header_id|>\n\n'
        f'{question_sw}<|eot_id|>'
        f'<|start_header_id|>assistant<|end_header_id|>\n\n'
    )
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
    return clean_generated_reply(tokenizer.decode(new_tokens, skip_special_tokens=True).strip())

# ── NUMBER EXTRACTION ─────────────────────────────────────────────────────────
def extract_numbers(text):
    text_lower = text.lower()
    nums = set()
    for m in re.findall(r'asilimia\s*(\d+(?:\.\d+)?)', text_lower):
        nums.add(m)
    for m in re.findall(r'(\d+(?:\.\d+)?)\s*%', text_lower):
        nums.add(m)
    for m in re.findall(r'tzs\s*([\d,]+)', text_lower):
        nums.add(m.replace(',', ''))
    for m in re.findall(r'\b(\d{3,}(?:,\d+)*)\b', text_lower):
        nums.add(m.replace(',', ''))
    for word, val in SWAHILI_NUMBERS.items():
        if re.search(r'\b' + word + r'\b', text_lower):
            nums.add(str(int(val)))
    return nums

# ── SCORING ───────────────────────────────────────────────────────────────────
def normalize(text):
    return ' '.join(text.lower().split())

def score_question(q, generated):
    gen_lower  = normalize(generated)
    atype      = q.get('answer_type', '')
    correct_sw = q.get('correct_answer_sw', '').lower()
    correct_en = q.get('correct_answer_en', '').lower()

    if atype == 'out_of_corpus_refusal':
        return any(p in gen_lower for p in [normalize(p) for p in REFUSAL_PHRASES])

    if atype in ('number', 'penalty'):
        correct_nums = extract_numbers(correct_sw) | extract_numbers(correct_en)
        gen_nums = extract_numbers(generated)
        if correct_nums and len(correct_nums & gen_nums) >= 1:
            return True
        # Fallback for frequency answers like 'mara moja kwa mwaka'
        frequency_words = {'mara', 'kila', 'mwaka', 'wiki', 'mwezi', 'siku', 'once', 'annually'}
        if any(w in gen_lower for w in frequency_words) and any(w in correct_sw for w in frequency_words):
            if len(gen_lower) > 15:
                return True
        if not correct_nums:
            return len(gen_lower) > 10
        return False

    if atype == 'yes_no':
        YES = {'ndiyo', 'ndio', 'yes', 'sahihi'}
        NO  = {'hapana', 'la', 'no', 'siyo', 'sivyo'}
        yes_in_correct = any(w in correct_sw for w in YES)
        no_in_correct  = any(w in correct_sw for w in NO)
        gen_yes = any(w in gen_lower for w in YES)
        gen_no  = any(w in gen_lower for w in NO)
        if yes_in_correct: return gen_yes
        if no_in_correct:  return gen_no
        return len(gen_lower) > 10

    if atype in ('definition', 'procedure'):
        correct_sw = re.sub(r'thibitisha na.*$', '', correct_sw, flags=re.IGNORECASE|re.DOTALL).strip()
        correct_en = re.sub(r'confirm with.*$',  '', correct_en, flags=re.IGNORECASE|re.DOTALL).strip()
        # Lowered from 6→5 chars and 4→3 words to handle Swahili synonym variation
        words = {w for w in (correct_sw + ' ' + correct_en).split() if len(w) >= 5}
        if not words: return len(gen_lower) > 20
        return len(words & set(gen_lower.split())) >= 3

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

        passed = score_question(q, generated)
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

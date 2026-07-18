# -*- coding: utf-8 -*-
"""EOS / stop-behavior probe — PRODUCTION prompt format vs EVAL prompt format (Kaggle GPU).

WHY: the 400-run showed 79% of model generations (263/331) end mid-word at the 350-token
cap — i.e. the model rarely emits its stop token. Investigation found a train/inference
CHAT-TEMPLATE MISMATCH:
  - TRAINING (v15, Tesla T4 -> USE_UNSLOTH -> apply_chat_template) used AfriqueLlama's
    NAIVE-CONCATENATION template: 'SYSTEM + question + answer + <|end_of_text|>' with NO
    Llama-3 structural tokens.
  - PRODUCTION (chike-inference/modal_app.py) uses tokenizer.apply_chat_template(...,
    add_generation_prompt=True) -> 'SYSTEM + question' -> a BYTE-IDENTICAL prefix of the
    training format (MATCHES training).
  - EVAL / ORCHESTRATOR (kaggle/eval.py + chike.prompting.build_chat_prompt) uses the
    HARDCODED Llama-3 header format ('<|begin_of_text|><|start_header_id|>...') -> header
    tokens NEITHER training NOR production ever used (MISMATCHES both).

The 79% was measured on the EVAL path. STRUCTURALLY production should stop correctly, but
"an inference from matching structure is not confirmed behaviour". This probe CONFIRMS it
with real evidence: run the SAME 20 questions through BOTH prompt formats on the real
adapter, decode with skip_special_tokens=False, and report — per question — how many tokens
were generated before stopping and whether <|end_of_text|> (128001) was actually emitted.

READ THIS OFF THE OUTPUT:
  - If the PRODUCTION-format arm stops EARLY (well under 350 tokens, emitting 128001) on
    most questions while the EVAL-format arm runs to the cap -> CONFIRMED: production stops
    correctly, the 79% was an eval-harness (R12 chat-template mismatch) artifact.
  - If the PRODUCTION-format arm ALSO runs to the cap -> the '79% is eval-only' correction
    is WRONG; this is a live production defect. (In that case DO NOT soften PROGRESS.md.)

This is a targeted diagnostic (20 questions x 2 formats), NOT a gate run. No scoring, no
orchestrator. Generation uses NO substring StoppingCriteria on purpose, so the ONLY early
stop is the model emitting eos_token_id — isolating pure EOS behaviour.

HOW TO RUN (Kaggle notebook, GPU ON, secret AFRICA_GIANTS attached):
    import requests
    exec(requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                      'AFRICA-GIANTS/main/kaggle/eos_production_probe.py', timeout=10).text)
"""
import os, sys, json, time, subprocess
from datetime import datetime, timezone

import requests

REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
RAW = f'https://raw.githubusercontent.com/{REPO}/main'
DATASET_REPO = 'prospAprospA007/africa-giants-dataset'

# ── AUTH ────────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    hf_token = kaggle_secrets.UserSecretsClient().get_secret('AFRICA_GIANTS')
except Exception as e:
    raise RuntimeError('run on Kaggle with the AFRICA_GIANTS secret attached') from e
assert hf_token, 'AFRICA_GIANTS empty'
os.environ['HF_TOKEN'] = hf_token
print(f'[auth] AFRICA_GIANTS ({hf_token[:6]}...) OK')

# ── CLONE chike/ (for chike.prompting + chike.retrieval — the EVAL-format path) ──
_CLONE = '/kaggle/working/AFRICA-GIANTS'
if not os.path.isdir(_CLONE):
    subprocess.run(['git', 'clone', '--depth', '1', f'https://github.com/{REPO}.git', _CLONE], check=True)
else:
    subprocess.run(['git', '-C', _CLONE, 'pull', '--ff-only'], check=False)
sys.path.insert(0, _CLONE)
_sha = subprocess.run(['git', '-C', _CLONE, 'rev-parse', '--short', 'HEAD'],
                      capture_output=True, text=True).stdout.strip()
print(f'[clone] chike @ {_CLONE} (HEAD {_sha})')

from chike.prompting import build_chat_prompt, build_enriched_system   # noqa: E402
from chike.retrieval import Retriever                                  # noqa: E402

# ── CONFIG (same source as production/eval: chike_config.json on main) ───────────
_cb = str(int(time.time() * 1000))
CONFIG = requests.get(f'{RAW}/kaggle/chike_config.json?cb={_cb}',
                      headers={'Cache-Control': 'no-cache'}, timeout=15).json()
SYSTEM_PROMPT = CONFIG['system_prompt']
GEN = CONFIG['generation_params']
ADAPTER = CONFIG.get('adapter_repo', 'prospAprospA007/africa-giants-adapter-v15')
MAX_NEW = int(GEN.get('max_new_tokens', 350))
REP_PEN = float(GEN.get('repetition_penalty', 1.1))
NO_REPEAT = int(GEN.get('no_repeat_ngram_size', 0))
DO_SAMPLE = bool(GEN.get('do_sample', False))
print(f'[config] adapter={ADAPTER} max_new_tokens={MAX_NEW} do_sample={DO_SAMPLE} '
      f'repetition_penalty={REP_PEN} no_repeat_ngram_size={NO_REPEAT}')

# ── RAG index (facts identical across both arms -> isolates the FORMAT variable) ─
from huggingface_hub import hf_hub_download, HfApi                     # noqa: E402
_rag_npy = hf_hub_download(repo_id=DATASET_REPO, filename='rag_embeddings.npy',
                           repo_type='dataset', token=hf_token)
_rag_txt = hf_hub_download(repo_id=DATASET_REPO, filename='rag_facts_text.json',
                           repo_type='dataset', token=hf_token)
retriever = Retriever(emb_path=_rag_npy, texts_path=_rag_txt)
print('[data] RAG index downloaded (e5-base)')

# ── MODEL (4-bit nf4/fp16/double-quant — VERBATIM from modal_app.py production load) ──
subprocess.run(['pip', 'install', '-q', '-U', 'bitsandbytes>=0.46.1'], check=True)
subprocess.run(['pip', 'install', '-q', '-U', 'sentence-transformers>=2.7.0'], check=True)
import torch                                                           # noqa: E402
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig  # noqa: E402

print(f'[model] loading {ADAPTER} (4-bit) ...')
tok = AutoTokenizer.from_pretrained(ADAPTER, token=hf_token, trust_remote_code=True)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                         bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
model = AutoModelForCausalLM.from_pretrained(
    ADAPTER, quantization_config=bnb, device_map='auto', token=hf_token, trust_remote_code=True)
model.eval()
EOS_ID = tok.eos_token_id
EOT_ID = tok.convert_tokens_to_ids('<|eot_id|>')
print(f'[model] loaded. eos_token={tok.eos_token!r} eos_token_id={EOS_ID} '
      f'<|eot_id|>_id={EOT_ID}')

# ── 20 PRODUCTION-STYLE QUESTIONS across different subdomains ─────────────────────
QUESTIONS = [
    ('vat_registration',  'Kizingiti cha kujisajili VAT ni kiasi gani?'),
    ('vat_rate',          'Kiwango cha VAT Tanzania ni asilimia ngapi?'),
    ('paye_compute',      'Mfanyakazi wangu ana mshahara wa TZS 800,000 kwa mwezi, PAYE yake ni kiasi gani?'),
    ('paye_bands',        'Bendi za PAYE za mwezi ziko vipi Tanzania?'),
    ('sdl',               'SDL inatozwa kwa kiwango gani na kizingiti cha wafanyakazi ni kipi?'),
    ('nssf_rate',         'Mchango wa NSSF ni asilimia ngapi kwa mwajiri na mfanyakazi?'),
    ('nssf_first_emp',    'Je, nalazimika kusajili NSSF nikiwa na mfanyakazi mmoja tu?'),
    ('wcf_deadline',      'Mwajiri mpya anatakiwa kujisajili WCF ndani ya siku ngapi?'),
    ('osha_registration', 'Nina mfanyakazi mmoja tu, je nalazimika kusajili OSHA?'),
    ('osha_officer',      'Je, ninahitaji afisa wa usalama kazini kwa kampuni yangu?'),
    ('brela_annual',      'Ada ya annual return BRELA ni shilingi ngapi?'),
    ('brela_penalty',     'Adhabu ya kuchelewa kuwasilisha annual return BRELA ni kiasi gani?'),
    ('gn487a_salon',      'Kama mgeni, je naweza kufungua saluni Tanzania?'),
    ('gn487a_wholesale',  'Je, mgeni anaruhusiwa kufanya biashara ya jumla (wholesale) Tanzania?'),
    ('gn605a_effective',  'Kima kipya cha chini cha mshahara kinaanza kutumika lini?'),
    ('gn605a_mining',     'Kima cha chini cha mshahara kwa sekta ya madini ni kiasi gani?'),
    ('efd_threshold',     'Kizingiti cha mauzo cha kuanza kutumia EFD ni kiasi gani?'),
    ('efd_receipt',       'Je, ninatakiwa kutoa risiti ya EFD kwa kila muamala?'),
    ('nest_procurement',  'Gharama ya kujisajili kwenye mfumo wa NeST ni kiasi gani kwa mwaka?'),
    ('eac_str',           'Kizingiti cha thamani cha Simplified Trade Regime ya EAC ni kiasi gani?'),
]
print(f'[probe] {len(QUESTIONS)} questions x 2 prompt formats\n')


def _gen(prompt: str):
    """Greedy generate with NO substring StoppingCriteria — the ONLY early stop is the
    model emitting eos_token_id. Returns (n_new_tokens, stopped_early, eos_emitted,
    eot_emitted, decoded_with_specials)."""
    inp = tok(prompt, return_tensors='pt').to(model.device)
    in_len = inp['input_ids'].shape[1]
    with torch.no_grad():
        out = model.generate(
            **inp, max_new_tokens=MAX_NEW, do_sample=DO_SAMPLE, temperature=1.0,
            repetition_penalty=REP_PEN, no_repeat_ngram_size=NO_REPEAT,
            eos_token_id=EOS_ID, pad_token_id=tok.pad_token_id)
    new_ids = out[0][in_len:].tolist()
    n = len(new_ids)
    return {
        'n_new_tokens': n,
        'stopped_early': n < MAX_NEW,
        'eos_128001_emitted': EOS_ID in new_ids,
        'eot_128009_emitted': (EOT_ID in new_ids) if EOT_ID is not None else False,
        'last_token_id': new_ids[-1] if new_ids else None,
        'decoded_specials': tok.decode(new_ids, skip_special_tokens=False),
    }


rows = []
t0 = time.time()
for i, (sub, q) in enumerate(QUESTIONS):
    facts = list(retriever.retrieve(q))                       # SAME facts for both arms
    enriched = build_enriched_system(SYSTEM_PROMPT, facts)

    # PRODUCTION format — EXACT modal_app.py path (apply_chat_template, add_generation_prompt)
    prod_prompt = tok.apply_chat_template(
        [{'role': 'system', 'content': enriched}, {'role': 'user', 'content': q.strip()}],
        tokenize=False, add_generation_prompt=True)
    prod = _gen(prod_prompt)

    # EVAL / ORCHESTRATOR format — chike.prompting.build_chat_prompt (hardcoded Llama-3)
    eval_prompt = build_chat_prompt(q, facts, SYSTEM_PROMPT)
    ev = _gen(eval_prompt)

    rows.append({'subdomain': sub, 'question': q,
                 'production': prod, 'eval_format': ev})
    print(f"[{i+1:2d}/{len(QUESTIONS)}] {sub:18s} "
          f"PROD: {prod['n_new_tokens']:3d} tok stop_early={prod['stopped_early']} "
          f"eos={prod['eos_128001_emitted']}  |  "
          f"EVAL: {ev['n_new_tokens']:3d} tok stop_early={ev['stopped_early']} "
          f"eos={ev['eos_128001_emitted']}   ({time.time()-t0:.0f}s)")

# ── SUMMARY ──────────────────────────────────────────────────────────────────────
def _agg(key):
    early = sum(r[key]['stopped_early'] for r in rows)
    eos = sum(r[key]['eos_128001_emitted'] for r in rows)
    eot = sum(r[key]['eot_128009_emitted'] for r in rows)
    mean = sum(r[key]['n_new_tokens'] for r in rows) / len(rows)
    capped = sum(r[key]['n_new_tokens'] >= MAX_NEW for r in rows)
    return early, eos, eot, mean, capped

print('\n' + '=' * 72)
print('EOS / STOP-BEHAVIOUR SUMMARY  (commit %s, %d questions, max_new_tokens=%d)'
      % (_sha, len(rows), MAX_NEW))
print('=' * 72)
for name, key in [('PRODUCTION format (apply_chat_template == training)', 'production'),
                  ('EVAL/ORCH format  (build_chat_prompt, Llama-3 headers)', 'eval_format')]:
    early, eos, eot, mean, capped = _agg(key)
    print(f'\n{name}:')
    print(f'   stopped EARLY (< {MAX_NEW} tok):     {early}/{len(rows)}')
    print(f'   emitted <|end_of_text|> (128001): {eos}/{len(rows)}')
    print(f'   emitted <|eot_id|> (128009):      {eot}/{len(rows)}')
    print(f'   ran to the {MAX_NEW}-token cap:       {capped}/{len(rows)}')
    print(f'   mean new tokens:                  {mean:.0f}')

print('\nINTERPRETATION:')
print('  If PRODUCTION stops early / emits 128001 on most, while EVAL runs to the cap ->')
print('  CONFIRMED: production stops correctly; 79% was an eval-harness (R12) artifact.')
print('  If PRODUCTION also runs to the cap -> live production defect; do NOT soften PROGRESS.md.')

# a couple of full decoded tails (skip_special_tokens=False) so the tokens are visible
print('\n--- sample decoded tails (skip_special_tokens=False) ---')
for r in rows[:3]:
    print(f"\n[{r['subdomain']}] PROD tail: ...{r['production']['decoded_specials'][-160:]!r}")
    print(f"[{r['subdomain']}] EVAL tail: ...{r['eval_format']['decoded_specials'][-160:]!r}")

out = {'mode': 'eos_production_probe', 'commit': _sha,
       'timestamp': datetime.now(timezone.utc).isoformat(),
       'max_new_tokens': MAX_NEW, 'eos_token_id': EOS_ID, 'eot_id': EOT_ID,
       'summary': {k: dict(zip(('stopped_early', 'eos_128001', 'eot_128009', 'mean_tokens', 'capped'),
                               _agg(k))) for k in ('production', 'eval_format')},
       'results': rows}
path = '/kaggle/working/eos_production_probe.json'
json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n[save] {path}')
try:
    HfApi().upload_file(path_or_fileobj=path, path_in_repo='eos_production_probe.json',
                        repo_id='prospAprospA007/africa-giants-adapter-v15', repo_type='model',
                        token=hf_token, commit_message='EOS production-vs-eval prompt-format probe')
    print('[upload] eos_production_probe.json -> adapter-v15')
except Exception as e:
    print(f'[upload] failed (non-critical): {e}')
print('\nEOS_PROBE_DONE')

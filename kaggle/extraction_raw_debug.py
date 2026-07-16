# -*- coding: utf-8 -*-
"""RAW-CAPTURE DEBUG — why chike/extraction.py returned fields={} on every sample entry.

This is the isolation harness requested after the sample stage came back with all 18
entries empty (fields={}, reasons all "missing"). It captures, for a handful of the
CLEAN, unambiguous stress-test questions, the EXACT things the persisted stress-test
JSON did NOT save:
  1. the exact prompt SlotExtractor sends the model  (SlotExtractor._build_prompt)
  2. the RAW model generation, verbatim, BEFORE any parsing
  3. what json.loads(raw) does with it (parses? throws? what error?)
  4. what SlotExtractor._parse(raw) returns  (the {} we suspect)
  5. what the DETERMINISTIC parser alone extracts (swahili_numbers.parse_amounts /
     parse_count) — i.e. the values that SHOULD populate the fields
  6. the full Extraction the current code produces end-to-end

It writes all of that to HF (adapter-v15 repo) as extraction_raw_debug.json so it can be
fetched and inspected directly rather than trusted from a terminal paste.

Read-only w.r.t. chike/: imports the real extractor; changes nothing. Does NOT run the
205. The point is to SEE the raw output on extract_025 before we touch extraction.py.

HOW TO RUN (Kaggle notebook, GPU ON, AFRICA_GIANTS secret attached):
    import requests
    exec(requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                      'AFRICA-GIANTS/main/kaggle/extraction_raw_debug.py', timeout=10).text)
    run_debug()          # extract_025 first, then a few more clean cases
"""
import os, sys, json, glob, time, subprocess

import requests

REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
DATASET_REPO = 'prospAprospA007/africa-giants-dataset'
REVIEWED_FILE = 'slot_extraction_stress_test_001_reviewed.jsonl'

# clean, unambiguous cases (state count and/or salary directly) — must NOT come back empty
DEBUG_IDS = ['extract_025', 'extract_157', 'extract_027', 'extract_041']

# ── AUTH ────────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    hf_token = kaggle_secrets.UserSecretsClient().get_secret('AFRICA_GIANTS')
except Exception as e:
    raise RuntimeError('run on Kaggle with AFRICA_GIANTS secret attached') from e
assert hf_token, 'AFRICA_GIANTS secret empty'
os.environ['HF_TOKEN'] = hf_token
print(f'[auth] AFRICA_GIANTS ({hf_token[:6]}...) OK')

# ── GET chike/ PACKAGE (git clone — same as the stress test) ─────────────────────
_CLONE = '/kaggle/working/AFRICA-GIANTS'
if not os.path.isdir(_CLONE):
    subprocess.run(['git', 'clone', '--depth', '1', f'https://github.com/{REPO}.git', _CLONE], check=True)
else:
    subprocess.run(['git', '-C', _CLONE, 'pull', '--ff-only'], check=False)
sys.path.insert(0, _CLONE)
_sha = subprocess.run(['git', '-C', _CLONE, 'rev-parse', '--short', 'HEAD'],
                      capture_output=True, text=True).stdout.strip()
print(f'[clone] chike @ {_CLONE} (HEAD {_sha})')

from chike.extraction import SlotExtractor, REQUIRED_FIELDS               # noqa: E402
from chike.model_abstraction import ModelBackend                          # noqa: E402
from chike import swahili_numbers as swn                                  # noqa: E402

# ── LOAD THE REVIEWED 205 (local -> kaggle input -> HF dataset repo) ─────────────
def _load_reviewed():
    for p in [os.path.join(_CLONE, 'data/reviewed', REVIEWED_FILE),
              *glob.glob(f'/kaggle/input/**/{REVIEWED_FILE}', recursive=True)]:
        if os.path.exists(p):
            return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
    from huggingface_hub import hf_hub_download
    p = hf_hub_download(repo_id=DATASET_REPO, filename=REVIEWED_FILE,
                        repo_type='dataset', token=hf_token)
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]

ENTRIES = {e['id']: e for e in _load_reviewed()}
print(f'[data] {len(ENTRIES)} reviewed entries loaded')

# ── CONFIG + MODEL (byte-identical 4-bit load to the stress test) ────────────────
_cb = str(int(time.time() * 1000))
CONFIG = requests.get(f'https://raw.githubusercontent.com/{REPO}/main/kaggle/chike_config.json?cb={_cb}',
                      headers={'Cache-Control': 'no-cache'}, timeout=15).json()
GEN = CONFIG['generation_params']
STOP = GEN.get('stop_strings', ['\n\nQ:', '\n\nSwali:', '<|start_header_id|>', '\n\n---'])
ADAPTER = CONFIG.get('adapter_repo', 'prospAprospA007/africa-giants-adapter-v15')

subprocess.run(['pip', 'install', '-q', '-U', 'bitsandbytes>=0.46.1'], check=True)
import torch                                                              # noqa: E402
from transformers import (AutoTokenizer, AutoModelForCausalLM,           # noqa: E402
                          BitsAndBytesConfig, StoppingCriteria, StoppingCriteriaList)


class _Stop(StoppingCriteria):
    def __init__(self, tok, stops): self.tok, self.stops = tok, stops
    def __call__(self, input_ids, scores, **kw):
        text = self.tok.decode(input_ids[0], skip_special_tokens=True)
        return any(s in text[-100:] for s in self.stops)


class KaggleDirectBackend(ModelBackend):
    def __init__(self):
        print(f'[model] loading {ADAPTER} (4-bit) ...')
        self.tok = AutoTokenizer.from_pretrained(ADAPTER, token=hf_token, trust_remote_code=True)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                                 bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            ADAPTER, quantization_config=bnb, device_map='auto', token=hf_token, trust_remote_code=True)
        self.model.eval()
        print('[model] loaded OK')

    def generate(self, prompt, params=None):
        inp = self.tok(prompt, return_tensors='pt').to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(
                **inp, max_new_tokens=(params or {}).get('max_new_tokens', 200),
                do_sample=False, temperature=1.0, repetition_penalty=1.1, no_repeat_ngram_size=0,
                stopping_criteria=StoppingCriteriaList([_Stop(self.tok, STOP)]),
                eos_token_id=self.tok.eos_token_id, pad_token_id=self.tok.pad_token_id)
        return self.tok.decode(out[0][inp['input_ids'].shape[1]:], skip_special_tokens=True).strip()


SUBDOMAIN_CTYPE = {'sdl_compliance': 'sdl', 'nssf_contributions': 'nssf',
                   'wcf_compliance': 'wcf', 'paye': 'paye', 'paye_compliance': 'paye'}


def _json_loads_report(raw):
    """What does json.loads do with the raw output — parse, or which error?"""
    try:
        return {'ok': True, 'value': json.loads(raw)}
    except Exception as ex:
        return {'ok': False, 'error_type': type(ex).__name__, 'error': str(ex)}


def run_debug():
    be = KaggleDirectBackend()
    ext = SlotExtractor(be)
    records = []
    for did in DEBUG_IDS:
        e = ENTRIES.get(did)
        if e is None:
            print(f'[skip] {did} not found'); continue
        q = e['question_sw']
        ct = SUBDOMAIN_CTYPE.get(e['subdomain'])
        required = REQUIRED_FIELDS[ct] if ct else ('gross_monthly_payroll',)

        prompt = SlotExtractor._build_prompt(q, required)     # EXACT prompt the model sees
        raw = be.generate(prompt)                             # RAW output, before any parsing
        parsed = ext._parse(raw)                              # what _parse makes of it ({}?)
        # deterministic parser alone — the values that SHOULD fill the fields
        det = {'parse_amounts': [str(a) for a in swn.parse_amounts(q)],
               'parse_count': swn.parse_count(q)}
        # full end-to-end extraction under the CURRENT code
        xr = ext.extract(q, required, ct)
        end_to_end = {n: {'value': str(f.value), 'confidence': f.confidence.value, 'reason': f.reason}
                      for n, f in xr.fields.items()}

        rec = {
            'id': did, 'subdomain': e['subdomain'], 'failure_category': e['failure_category'],
            'computation_type': ct, 'required': list(required), 'question_sw': q,
            'prompt': prompt,
            'RAW_MODEL_OUTPUT': raw,
            'json_loads': _json_loads_report(raw),
            'parse_result': {k: [str(v[0]), v[1].value] for k, v in parsed.items()},
            'deterministic_parser': det,
            'end_to_end_fields': end_to_end,
            'end_to_end_usable': xr.usable(required),
        }
        records.append(rec)
        print('\n' + '=' * 72)
        print(f"{did} [{e['subdomain']}/{e['failure_category']}] ct={ct} required={required}")
        print(f"Q: {q}")
        print(f"--- RAW MODEL OUTPUT (verbatim, {len(raw)} chars) ---")
        print(raw)
        print(f"--- json.loads: {rec['json_loads'].get('ok')} "
              f"{rec['json_loads'].get('error_type','')} {rec['json_loads'].get('error','')}")
        print(f"--- _parse -> {rec['parse_result']}")
        print(f"--- deterministic parser -> {det}")
        print(f"--- end-to-end fields -> {end_to_end}  usable={xr.usable(required)}")

    out = {'commit': _sha, 'adapter': ADAPTER, 'gen': {'max_new_tokens': 200, 'do_sample': False},
           'records': records}
    path = '/kaggle/working/extraction_raw_debug.json'
    json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\n[save] {path}')
    try:
        from huggingface_hub import HfApi
        HfApi().upload_file(path_or_fileobj=path, path_in_repo='extraction_raw_debug.json',
                            repo_id='prospAprospA007/africa-giants-adapter-v15', repo_type='model',
                            token=hf_token, commit_message='raw model output capture for extraction debug')
        print('[upload] extraction_raw_debug.json -> adapter-v15')
    except Exception as ex:
        print(f'[upload] failed (non-critical): {ex}')
    print('\nRAW_DEBUG_DONE')
    return out


print('\nReady. Run:  run_debug()   # captures raw model output for the clean cases -> HF')

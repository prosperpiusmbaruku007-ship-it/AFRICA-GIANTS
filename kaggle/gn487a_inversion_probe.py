# -*- coding: utf-8 -*-
"""Priority-1 reproduction harness — GN487A prohibition-inversion mechanism.

Prepare-only; the founder runs this on a Kaggle GPU (Claude never runs the model
locally). It runs a SMALL, deliberately-designed probe set (eval/accuracy_gate/
gn487a_inversion_probes.jsonl, 14 questions NOT drawn from the 400) through the SAME
real orchestrator + v15 adapter + e5 RAG as eval_orchestrator_combined.py, to confirm
or refute three hypotheses about the eval_317 / eval_332 inversions:

  H1  numeric-distractor -> exception-threshold binding. eval_317 fabricated
      'anaweza ... ikiwa mtaji chini ya milioni 100' — the salon fact IS conditional
      ('UNLESS hotel/tourism'), so the model may be binding the question's number as
      the exception threshold. Prediction: numeric probes (01,03,05,06,07,08) flip;
      no-number controls (02,04,09) answer correct Hapana.
  H2  narrow vs systemic. If multiple DIFFERENT prohibited activities flip -> systemic
      across GN487A; if only salon flips -> narrow to the one activity with a real
      conditional carve-out.
  H3  cross-subdomain. Do OTHER absolute rules flip under a numeric distractor?
      OSHA/EFD 'regardless of count/amount' (10,12), NSSF-vs-SDL threshold
      cross-contamination (14), min-wage floor (13). If these hold, the defect is
      GN487A-specific; if they flip, it is a general 'number -> fabricated threshold'
      failure of every absolute rule.

This is DIAGNOSTIC ONLY — no gate, no pass/fail thresholds, no fix. It prints, per
probe: the question, the raw + cleaned generation, the deterministic _polarity_conf
verdict (to demonstrate the reporting-blindness — a discursively-worded inversion
lands in 'unconfident' and would be scorer_reliability-excluded), and the expected
answer, so the founder can read each inversion directly.

Bootstrap on Kaggle (GPU + AFRICA_GIANTS secret):
    import requests
    exec(requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                      'AFRICA-GIANTS/main/kaggle/gn487a_inversion_probe.py', timeout=10).text)

PREREQ: gn487a_inversion_probes.jsonl is unmerged + not on GitHub. Loader checks, in
order: (1) local clone eval/accuracy_gate/, (2) /kaggle/input/**, (3) HF dataset repo
(prospAprospA007/africa-giants-dataset). Upload it there first (same as the eval_00x
files) if running purely from the bootstrap.
"""
import os, sys, json, glob, subprocess, time
from datetime import datetime, timezone

import requests

REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
RAW = f'https://raw.githubusercontent.com/{REPO}/main'
DATASET_REPO = 'prospAprospA007/africa-giants-dataset'
PROBE_FILE = 'gn487a_inversion_probes.jsonl'

# ── AUTH ────────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    hf_token = kaggle_secrets.UserSecretsClient().get_secret('AFRICA_GIANTS')
except Exception as e:
    raise RuntimeError('run on Kaggle with AFRICA_GIANTS attached') from e
assert hf_token, 'AFRICA_GIANTS empty'
os.environ['HF_TOKEN'] = hf_token
print(f'[auth] AFRICA_GIANTS ({hf_token[:6]}...) OK')

# ── CLONE chike/ ─────────────────────────────────────────────────────────────────
_CLONE = '/kaggle/working/AFRICA-GIANTS'
if not os.path.isdir(_CLONE):
    subprocess.run(['git', 'clone', '--depth', '1', f'https://github.com/{REPO}.git', _CLONE], check=True)
else:
    subprocess.run(['git', '-C', _CLONE, 'pull', '--ff-only'], check=False)
sys.path.insert(0, _CLONE)
_sha = subprocess.run(['git', '-C', _CLONE, 'rev-parse', '--short', 'HEAD'],
                      capture_output=True, text=True).stdout.strip()
print(f'[clone] chike @ {_CLONE} (HEAD {_sha})')

from chike.orchestrator import Orchestrator, CLARIFICATION_PENDING        # noqa: E402
from chike.model_abstraction import ModelBackend                          # noqa: E402
from chike.retrieval import Retriever                                     # noqa: E402
from chike.scoring import _polarity_conf                                  # noqa: E402

# ── CONFIG (R14 single source of truth) ─────────────────────────────────────────
_cb = str(int(time.time() * 1000))
CONFIG = requests.get(f'{RAW}/kaggle/chike_config.json?cb={_cb}',
                      headers={'Cache-Control': 'no-cache'}, timeout=15).json()
SYSTEM_PROMPT = CONFIG['system_prompt']
OOC_PHRASES = CONFIG.get('ooc_phrases', [])
GEN = CONFIG['generation_params']
STOP = GEN.get('stop_strings', ['\n\nQ:', '\n\nSwali:', '<|start_header_id|>', '\n\n---'])
ADAPTER = CONFIG.get('adapter_repo', 'prospAprospA007/africa-giants-adapter-v15')

# ── DATA: probe set + RAG index ─────────────────────────────────────────────────
from huggingface_hub import hf_hub_download                               # noqa: E402


def _load_probes():
    for p in [os.path.join(_CLONE, 'eval/accuracy_gate', PROBE_FILE),
              *glob.glob(f'/kaggle/input/**/{PROBE_FILE}', recursive=True)]:
        if os.path.exists(p):
            print(f'[data] probes from {p}')
            return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
    p = hf_hub_download(repo_id=DATASET_REPO, filename=PROBE_FILE, repo_type='dataset', token=hf_token)
    print(f'[data] probes from HF {DATASET_REPO}/{PROBE_FILE}')
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


probes = _load_probes()
print(f'[data] {len(probes)} probes loaded')
_rag_npy = hf_hub_download(repo_id=DATASET_REPO, filename='rag_embeddings.npy', repo_type='dataset', token=hf_token)
_rag_txt = hf_hub_download(repo_id=DATASET_REPO, filename='rag_facts_text.json', repo_type='dataset', token=hf_token)

# ── MODEL (byte-identical 4-bit load to eval_orchestrator_combined.py) ───────────
subprocess.run(['pip', 'install', '-q', '-U', 'bitsandbytes>=0.46.1'], check=True)
subprocess.run(['pip', 'install', '-q', '-U', 'sentence-transformers>=2.7.0'], check=True)
import torch                                                              # noqa: E402
from transformers import (AutoTokenizer, AutoModelForCausalLM,           # noqa: E402
                          BitsAndBytesConfig, StoppingCriteria, StoppingCriteriaList)


class _Stop(StoppingCriteria):
    def __init__(self, tok, stops): self.tok, self.stops = tok, stops
    def __call__(self, input_ids, scores, **kw):
        return any(s in self.tok.decode(input_ids[0], skip_special_tokens=True)[-100:]
                   for s in self.stops)


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
        p = dict(GEN)
        if params:
            p.update(params)
        inp = self.tok(prompt, return_tensors='pt').to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(
                **inp, max_new_tokens=p.get('max_new_tokens', 350), do_sample=False,
                temperature=1.0, repetition_penalty=p.get('repetition_penalty', 1.1),
                no_repeat_ngram_size=p.get('no_repeat_ngram_size', 0),
                stopping_criteria=StoppingCriteriaList([_Stop(self.tok, STOP)]),
                eos_token_id=self.tok.eos_token_id, pad_token_id=self.tok.pad_token_id)
        return self.tok.decode(out[0][inp['input_ids'].shape[1]:], skip_special_tokens=True).strip()


backend = KaggleDirectBackend()
retriever = Retriever(emb_path=_rag_npy, texts_path=_rag_txt)
orch = Orchestrator(backend=backend, retriever=retriever.retrieve,
                    ooc_phrases=OOC_PHRASES, system_prompt=SYSTEM_PROMPT)

# ── RUN PROBES ──────────────────────────────────────────────────────────────────
print('\n' + '=' * 70)
print('GN487A / ABSOLUTE-RULE INVERSION PROBES  (commit %s)' % _sha)
print('=' * 70)
rows = []
for pr in probes:
    reply = orch.answer(pr['question_sw'])
    gen = reply.text
    pol, conf = _polarity_conf(gen)
    # A probe is a candidate inversion when the confident-or-not polarity disagrees
    # with the expected polarity (and it is not a clarification/refusal).
    is_clar = CLARIFICATION_PENDING in gen
    flipped = (not is_clar) and pol != pr['expected_polarity']
    rows.append({**pr, 'generated': gen, 'raw_generated': reply.raw_text,
                 'model_polarity': pol, 'polarity_confident': conf,
                 'clarified': is_clar, 'candidate_inversion': flipped,
                 'in_scope': reply.in_scope})
    tag = 'CLARIFIED' if is_clar else ('*** CANDIDATE INVERSION ***' if flipped else 'ok')
    print('\n' + '-' * 70)
    print(f"[{pr['id']}] {pr['group']} / {pr['activity']} (has_number={pr['has_number']})  -> {tag}")
    print(f"  Q:        {pr['question_sw']}")
    print(f"  EXPECT:   polarity={pr['expected_polarity']}  |  {pr['expected_sw']}")
    print(f"  MODEL:    polarity={pol} confident={conf} in_scope={reply.in_scope}")
    print(f"  GEN:      {gen}")
    if reply.raw_text and reply.raw_text != gen:
        print(f"  RAW:      {reply.raw_text[:400]}")

# ── SUMMARY ─────────────────────────────────────────────────────────────────────
inv = [r for r in rows if r['candidate_inversion']]
num = [r for r in rows if r['group'] == 'gn487a_numeric']
ctl = [r for r in rows if r['group'] == 'gn487a_control']
xsd = [r for r in rows if r['group'].startswith('cross_subdomain')]
print('\n' + '=' * 70)
print('SUMMARY')
print('=' * 70)
print(f"candidate inversions: {len(inv)}/{len(rows)}  -> {[r['id'] for r in inv]}")
print(f"  gn487a numeric  flipped: {sum(r['candidate_inversion'] for r in num)}/{len(num)}")
print(f"  gn487a control  flipped: {sum(r['candidate_inversion'] for r in ctl)}/{len(ctl)}  (expect 0 if H1 holds)")
print(f"  cross-subdomain flipped: {sum(r['candidate_inversion'] for r in xsd)}/{len(xsd)}  (>0 => defect not GN487A-specific)")
print(f"  inversions the reliability filter would EXCLUDE (polarity not confident): "
      f"{sum(r['candidate_inversion'] and not r['polarity_confident'] for r in rows)}/{len(inv)}")
out = {'mode': 'gn487a_inversion_probe', 'commit': _sha,
       'timestamp': datetime.now(timezone.utc).isoformat(), 'rows': rows}
path = '/kaggle/working/gn487a_inversion_probe.json'
json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
try:
    from huggingface_hub import HfApi
    HfApi().upload_file(path_or_fileobj=path, path_in_repo='gn487a_inversion_probe.json',
                        repo_id=ADAPTER, repo_type='model', token=hf_token,
                        commit_message='GN487A inversion reproduction probe')
    print(f'[upload] gn487a_inversion_probe.json -> {ADAPTER}')
except Exception as e:
    print(f'[upload] failed (non-critical): {e}')
print('\nPROBE_DONE')

# -*- coding: utf-8 -*-
"""Faithfulness/grounding probe — "fact confirmed retrieved, does the model use it?"

Prepare-only; the founder runs this on a Kaggle GPU (Claude never runs the model
locally). It runs a SMALL, deliberately-designed probe set (eval/accuracy_gate/
faithfulness_probes.jsonl, 9 questions NOT drawn from the 400) through the SAME real
orchestrator + v15 adapter + e5 RAG as eval_orchestrator_combined.py.

WHY THIS PROBE IS DIFFERENT from gn487a_inversion_probe.py: that probe asked whether
absolute rules flip under numeric distractors, but never verified the correct fact was
IN the model's context. This probe's entire premise is the opposite — it seeds from
eval_213, where the facilitator-penalty fact was retrieved at rank 0 yet the model
contradicted it (a faithfulness defect, NOT a retrieval gap). So every case here is
pre-selected (ranks verified locally against the committed index) so the target fact
IS retrieved; the probe then measures whether the model HONORS it.

THE CENTRAL SPLIT (computed automatically per case, not by manual inspection):
  - target_retrieved  := the target fact is present in the facts the orchestrator
                          actually injected into the prompt (reply.sub_answers[*].facts —
                          the ground truth of what the model saw, not a re-derivation).
  - classification:
      clarified            -> model asked to clarify (rare here)
      retrieval_gap        -> target fact NOT in injected context => this is a RETRIEVAL/
                              coverage problem, EXCLUDED from faithfulness scoring (this is
                              exactly how eval_183 was correctly reclassified — its 'OSHA
                              has no closure power' fact does not exist in the index).
      faithful             -> target retrieved AND model polarity == expected.
      faithfulness_failure -> target retrieved AND model polarity CONTRADICTS expected.
                              This is the dangerous class: no retrieval fix can catch it —
                              the fact was right there and the model overrode it.

Controls (fp_08/fp_09) have their fact retrieved AND the model reliably answers
correctly; they MUST score 'faithful'. If a control scores 'faithfulness_failure',
the probe's split logic is false-positiving and the run is not trustworthy.

This is DIAGNOSTIC ONLY — no gate, no pass/fail thresholds, no fix. It prints per case:
the question, the FULL injected context (with the target fact flagged + its rank), the
raw + cleaned generation, the deterministic polarity verdict, and the expected answer.

Bootstrap on Kaggle (GPU + AFRICA_GIANTS secret) — original 9-case set:
    import requests
    exec(requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                      'AFRICA-GIANTS/main/kaggle/faithfulness_probe.py', timeout=10).text)

Follow-up sets select via env var BEFORE exec (e.g. the license-framing 2x2 factorial that
isolates why only fp_01 fails — see faithfulness_leseni_probes.jsonl):
    import os, requests
    os.environ['FAITHFULNESS_PROBE_FILE'] = 'faithfulness_leseni_probes.jsonl'
    exec(requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                      'AFRICA-GIANTS/main/kaggle/faithfulness_probe.py', timeout=10).text)

The result JSON name tracks the input stem (e.g. faithfulness_leseni_probes_result.json),
so follow-up runs never overwrite the original faithfulness_probes_result.json.

PREREQ: the selected *_probes.jsonl is committed to the repo (eval/accuracy_gate/), so the
clone path below finds it directly — no HF upload needed. The HF-dataset fallback is kept
only for a pure-bootstrap run where the clone is unavailable.
"""
import os, sys, json, glob, subprocess, time
from datetime import datetime, timezone

import requests

REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
RAW = f'https://raw.githubusercontent.com/{REPO}/main'
DATASET_REPO = 'prospAprospA007/africa-giants-dataset'
# Which probe set to run. Defaults to the original 9-case set; set the env var before
# exec() to run a follow-up set, e.g.:
#   os.environ['FAITHFULNESS_PROBE_FILE'] = 'faithfulness_leseni_probes.jsonl'
PROBE_FILE = os.environ.get('FAITHFULNESS_PROBE_FILE', 'faithfulness_probes.jsonl')
_STEM = os.path.splitext(os.path.basename(PROBE_FILE))[0]   # output name tracks input

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
        self.tokenizer = AutoTokenizer.from_pretrained(ADAPTER, token=hf_token, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
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
        inp = self.tokenizer(prompt, return_tensors='pt').to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(
                **inp, max_new_tokens=p.get('max_new_tokens', 350), do_sample=False,
                temperature=1.0, repetition_penalty=p.get('repetition_penalty', 1.1),
                no_repeat_ngram_size=p.get('no_repeat_ngram_size', 0),
                stopping_criteria=StoppingCriteriaList([_Stop(self.tokenizer, STOP)]),
                eos_token_id=self.tokenizer.eos_token_id, pad_token_id=self.tokenizer.pad_token_id)
        return self.tokenizer.decode(out[0][inp['input_ids'].shape[1]:], skip_special_tokens=True).strip()


backend = KaggleDirectBackend()
retriever = Retriever(emb_path=_rag_npy, texts_path=_rag_txt)
# NOTE: backend exposes .tokenizer, so the orchestrator routes prompts through
# apply_chat_template (the corrected format, commit e9cc68a) — this probe measures the
# model on the SAME production template the 400-run used.
orch = Orchestrator(backend=backend, retriever=retriever.retrieve,
                    ooc_phrases=OOC_PHRASES, system_prompt=SYSTEM_PROMPT)


def _injected_facts(reply):
    """The facts the orchestrator actually put in the prompt, aggregated across sub-answers.
    This is the ground truth of what the model SAW — not a re-run of retrieval."""
    facts = []
    for sa in reply.sub_answers:
        facts.extend(list(getattr(sa, 'facts', ()) or ()))
    return facts


def _target_rank(facts, needle):
    n = (needle or '').lower()
    for i, f in enumerate(facts):
        if n and n in f.lower():
            return i
    return None


# ── RUN PROBES ──────────────────────────────────────────────────────────────────
print('\n' + '=' * 74)
print('FAITHFULNESS / GROUNDING PROBE  (commit %s)' % _sha)
print('=' * 74)
rows = []
for pr in probes:
    reply = orch.answer(pr['question_sw'])
    gen = reply.text
    facts_seen = _injected_facts(reply)
    rank = _target_rank(facts_seen, pr.get('target_fact_substring'))
    target_retrieved = rank is not None
    pol, conf = _polarity_conf(gen)
    is_clar = CLARIFICATION_PENDING in gen

    if is_clar:
        cls = 'clarified'
    elif not reply.in_scope:
        cls = 'refused'
    elif not target_retrieved:
        cls = 'retrieval_gap'          # fact was NOT in context -> not a faithfulness test
    elif pol == pr['expected_polarity']:
        cls = 'faithful'
    else:
        cls = 'faithfulness_failure'   # fact WAS in context, model contradicted it

    rows.append({**pr, 'generated': gen, 'raw_generated': reply.raw_text,
                 'facts_seen': facts_seen, 'target_rank': rank,
                 'target_retrieved': target_retrieved, 'model_polarity': pol,
                 'polarity_confident': conf, 'classification': cls,
                 'in_scope': reply.in_scope})

    tag = {'faithfulness_failure': '*** FAITHFULNESS FAILURE ***',
           'retrieval_gap': '~~~ RETRIEVAL GAP (excluded) ~~~',
           'faithful': 'faithful', 'clarified': 'CLARIFIED', 'refused': 'REFUSED'}[cls]
    print('\n' + '-' * 74)
    print(f"[{pr['id']}] {pr['group']} / {pr['subdomain']}  ->  {tag}")
    print(f"  Q:        {pr['question_sw']}")
    print(f"  EXPECT:   polarity={pr['expected_polarity']}  |  {pr['expected_sw']}")
    print(f"  MODEL:    polarity={pol} confident={conf}")
    print(f"  TARGET:   '{pr.get('target_fact_substring')}'  rank_in_context={rank}"
          f"  (expected_rank_top3={pr.get('expected_rank_top3')})")
    print(f"  CONTEXT injected ({len(facts_seen)} facts):")
    for i, f in enumerate(facts_seen):
        mark = '  <== TARGET' if (rank is not None and i == rank) else ''
        print(f"     [{i}] {f[:120]}{mark}")
    print(f"  GEN:      {gen}")
    if reply.raw_text and reply.raw_text != gen:
        print(f"  RAW:      {reply.raw_text[:400]}")

# ── SUMMARY ─────────────────────────────────────────────────────────────────────
def _by(cls): return [r['id'] for r in rows if r['classification'] == cls]


ftests = [r for r in rows if r['group'] != 'faithfulness_control']
ctrls = [r for r in rows if r['group'] == 'faithfulness_control']
failures = _by('faithfulness_failure')
gaps = _by('retrieval_gap')

print('\n' + '=' * 74)
print('SUMMARY — automatic faithfulness vs retrieval-gap split')
print('=' * 74)
print(f"faithfulness_failure : {len(failures)}  -> {failures}")
print(f"faithful             : {len(_by('faithful'))}  -> {_by('faithful')}")
print(f"retrieval_gap (EXCL) : {len(gaps)}  -> {gaps}   (NOT faithfulness defects)")
print(f"clarified            : {len(_by('clarified'))}  -> {_by('clarified')}")
print()
# Faithfulness rate is computed ONLY over cases where the target fact was retrieved.
scored = [r for r in ftests if r['classification'] in ('faithful', 'faithfulness_failure')]
n_faith = sum(r['classification'] == 'faithful' for r in scored)
print(f"faithfulness rate (retrieved-fact cases only): {n_faith}/{len(scored)}"
      + (f" = {n_faith/len(scored):.1%}" if scored else ""))
print("  by group:")
for g in sorted({r['group'] for r in ftests}):
    gs = [r for r in ftests if r['group'] == g and r['classification'] in ('faithful', 'faithfulness_failure')]
    gf = sum(r['classification'] == 'faithful' for r in gs)
    print(f"    {g:34s} {gf}/{len(gs)}")
# Control sanity: every control MUST be 'faithful' or the split logic is false-positiving.
bad_ctrl = [r['id'] for r in ctrls if r['classification'] != 'faithful']
print(f"\ncontrols faithful: {sum(r['classification']=='faithful' for r in ctrls)}/{len(ctrls)}"
      + (f"  !!! CONTROL(S) NOT FAITHFUL: {bad_ctrl} — split logic suspect" if bad_ctrl else "  (OK)"))

out = {'mode': f'faithfulness_probe:{_STEM}', 'commit': _sha,
       'timestamp': datetime.now(timezone.utc).isoformat(),
       'faithfulness_failure_ids': failures, 'retrieval_gap_ids': gaps, 'rows': rows}
_out_name = f'{_STEM}_result.json'
path = f'/kaggle/working/{_out_name}'
json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
try:
    from huggingface_hub import HfApi
    HfApi().upload_file(path_or_fileobj=path, path_in_repo=_out_name,
                        repo_id=ADAPTER, repo_type='model', token=hf_token,
                        commit_message=f'faithfulness/grounding probe result ({_STEM})')
    print(f'\n[upload] {_out_name} -> {ADAPTER}')
except Exception as e:
    print(f'\n[upload] failed (non-critical): {e}')
print('\nPROBE_DONE')

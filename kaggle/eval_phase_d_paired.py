# -*- coding: utf-8 -*-
"""PHASE D — the paired v15-vs-v16 run over the same 400, plus Run 2 part 3 (de-confound).

ADR 0001 §10 sets the bar for any production wiring: "v16 >= v15 on the full 400, raw AND
reliable". That run has NEVER happened. Every 400-run in eval/results/ is v16-orchestrator
only, compared against an earlier *v16* baseline — so "v16 >= v15" is currently unevidenced.
This notebook is that run: both arms, same GPU session, same loaded 4-bit weights, same e5
index, same scorer, same judge.

  ARM v15 : chike.pipeline_v15.answer(...)   <- the SAME module chike-inference/modal_app.py
            imports. Not a reimplementation: byte-identical to production across 420 questions
            of decompose/pool/prompt, 400 persisted generations of stop-split+clean, and
            20/20 live against the production web_endpoint (commit d54ec17).
            Retrieval is SINGLE-ARM (V15Retriever), decomposition is decomposition_v15
            (no ordinal split) — the v15 arm must not inherit v16 capabilities.

  ARM v16 : chike.orchestrator.Orchestrator(...) — deterministic router + rules engine +
            never-guess + fidelity guard, chike.decomposition (ordinal split), and the
            TWO-ARM numeric retriever (chike.retrieval.Retriever.retrieve).

  RUN 2 PART 3 (de-confound): the v16 arm is re-run over the 90 fact-routed, second-arm-
            eligible questions with a SINGLE-ARM retriever. Run 1's paired diff mixes routing
            and retrieval; this isolates retrieval. After parts 1-2 showed the second arm is
            safe (append-only, nothing lost) but not a demonstrated win (1 recovery vs 86
            dilutions on the labelled set), this is now the DECIDING evidence on whether the
            two-arm retriever ships at all — not merely a de-confound.

WHAT IS REPORTED
  - per bucket (fact-path 190 / staged 50 / compute-type / adversarial 150), for BOTH arms:
    raw and reliable-denominator accuracy
  - judge overlay (majority-of-5, pinned DeepInfra seed=42) for BOTH arms
  - EVERY v15-PASS -> v16-FAIL enumerated individually, with full text (a healthy net can
    hide a bad class; the founder's bar is "no class of regression even at parity")
  - part 3: v16 two-arm vs v16 single-arm on the 90-question subset, answer-level, AND
    judge-augmented (the 3ac522a run left all 90 part-3 rows UNGRADED, so the two-arm
    ship/don't-ship call rested on the regex scorer alone until it was adjudicated by hand)

RE-RUN NOTE (2026-08-07). This is the second execution of this harness. Everything is held
identical to the 3ac522a run — same 400 questions, same adapter, same RAG index, same scorer,
same judge config, both arms — with exactly ONE harness change: part-3 rows are now judged.
What changed is the CODE UNDER TEST: PREREQ-1 (applicability routing + base rejection) and
PREREQ-2 (Tiers 1-2 narrowings, pattern C fractions, pattern B group payroll).

PRE-REGISTERED EXPECTATION, recorded before the run so it cannot be retrofitted:
    PREREQ-1 +15, Tiers 1-2 +7, C 0, B +9  ->  ~+31 raw on the 400 = +7.75 pts,
    against the 3ac522a raw gap of -6.8 pts.
Every one of those figures is measured on the DETERMINISTIC extraction/routing path only.
This run measures the FULL system with model behaviour on top, and +7.75 against -6.8 is a
thin margin — a handful of model-side losses could erase it. If it lands short, patterns D
(+2) and F (+4) are the next increment, not a redesign.

HOW TO RUN (Kaggle notebook)
    import requests
    exec(requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                      'AFRICA-GIANTS/main/kaggle/eval_phase_d_paired.py', timeout=20).text)

KAGGLE SETUP
    Accelerator : GPU  (T4 x2 or P100 — one device is used; 4-bit 8B needs ~6GB)
    Internet    : ON
    Secrets     : AFRICA_GIANTS      (HF token — model weights + eval questions + RAG index)
                  OPENROUTER_API_KEY (judge overlay on both arms; without it the run still
                                      completes and the judge section is skipped)
    Runtime     : ~1,010 generations (400 v15 + ~520 v16 + 90 part-3) ~= 2.5-3.5h,
                  plus ~30 min judge. Well inside Kaggle's 12h.

Ends with a delimited SUMMARY BLOCK to paste back.
"""
import glob
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import defaultdict

import requests

REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
RAW = f'https://raw.githubusercontent.com/{REPO}/main'
DATASET_REPO = 'prospAprospA007/africa-giants-dataset'
EXPECTED_FACT_COUNT = 217

print('=' * 78)
print('PHASE D — paired v15 vs v16 over the same 400  (+ Run 2 part 3 de-confound)')
print('=' * 78)

# ── AUTH ─────────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    _sc = kaggle_secrets.UserSecretsClient()
    hf_token = _sc.get_secret('AFRICA_GIANTS')
except Exception as e:                                               # noqa: BLE001
    raise RuntimeError('run on Kaggle with the AFRICA_GIANTS secret attached') from e
assert hf_token, 'AFRICA_GIANTS empty'
os.environ['HF_TOKEN'] = hf_token
print(f'[auth] AFRICA_GIANTS ({hf_token[:6]}...) OK')

try:
    OR_KEY = _sc.get_secret('OPENROUTER_API_KEY')
except Exception:                                                    # noqa: BLE001
    OR_KEY = os.environ.get('OPENROUTER_API_KEY', '')
RUN_JUDGE = bool(OR_KEY) and os.environ.get('CHIKE_JUDGE', '1') != '0'
print(f'[auth] OPENROUTER_API_KEY {"set — judge overlay ON (both arms)" if RUN_JUDGE else "absent — judge SKIPPED"}')

# ── CLONE (chike/ is non-leaf: pipeline_v15 + orchestrator import siblings) ───────
_CLONE = '/kaggle/working/AFRICA-GIANTS'
if not os.path.isdir(_CLONE):
    subprocess.run(['git', 'clone', '--depth', '1', f'https://github.com/{REPO}.git', _CLONE],
                   check=True)
else:
    subprocess.run(['git', '-C', _CLONE, 'fetch', '--depth', '1', 'origin', 'main'], check=True)
    subprocess.run(['git', '-C', _CLONE, 'reset', '--hard', 'origin/main'], check=True)
sys.path.insert(0, _CLONE)
_sha = subprocess.run(['git', '-C', _CLONE, 'rev-parse', '--short', 'HEAD'],
                      capture_output=True, text=True).stdout.strip()
# git clone is not CDN-cached, but print the live HEAD too so a stale clone is visible.
try:
    _live = requests.get(f'https://api.github.com/repos/{REPO}/commits/main',
                         headers={'Cache-Control': 'no-cache'}, timeout=20).json()['sha'][:7]
except Exception:                                                    # noqa: BLE001
    _live = '?'
_stale = _live not in ('?', '') and _live[:7] != _sha[:7]
print(f'[chike] GitHub main HEAD = {_live} | cloned HEAD = {_sha}'
      f'{"  <-- STALE CLONE, re-run the cell" if _stale else "  (fresh)"}')

from chike import pipeline_v15                                       # noqa: E402
from chike import judge as chike_judge                               # noqa: E402
from chike.orchestrator import Orchestrator                          # noqa: E402
from chike.model_abstraction import ModelBackend                     # noqa: E402
from chike.retrieval import Retriever                                # noqa: E402
from chike.scoring import score_question, scorer_reliability          # noqa: E402

# ── CONFIG (R14 single source of truth) ──────────────────────────────────────────
_cb = str(int(time.time() * 1000))
CONFIG = requests.get(f'{RAW}/kaggle/chike_config.json?cb={_cb}',
                      headers={'Cache-Control': 'no-cache'}, timeout=20).json()
SYSTEM_PROMPT = CONFIG['system_prompt']
REFUSAL_PHRASES = CONFIG['refusal_phrases']
GEN = CONFIG['generation_params']
STOP = GEN['stop_strings']
ADAPTER = CONFIG.get('adapter_repo', 'prospAprospA007/africa-giants-adapter-v15')
print(f'[config] v={CONFIG.get("version")} adapter={ADAPTER}')

# ── DATA: the 400 (all three files are git-tracked, read from the clone) ──────────
def _load(rel, n):
    path = os.path.join(_CLONE, rel)
    rows = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    assert len(rows) == n, f'{rel}: expected {n}, got {len(rows)}'
    return rows


gate = _load('eval/accuracy_gate/eval_questions_001.jsonl', 200)
additions = _load('eval/accuracy_gate/eval_questions_002_additions.jsonl', 50)
additions3 = _load('eval/accuracy_gate/eval_questions_003.jsonl', 150)
for r in gate:
    r['_source'] = 'gate_001'
for r in additions:
    r['_source'] = 'additions_002'
for r in additions3:
    r['_source'] = 'additions_003'
ALL = gate + additions + additions3
print(f'[data] {len(ALL)} questions (200 gate + 50 additions + 150 adversarial)')

# ── RAG index: from HF (what the gate uses) — assert it equals the repo copy ──────
from huggingface_hub import hf_hub_download                          # noqa: E402
_rag_npy = hf_hub_download(repo_id=DATASET_REPO, filename='rag_embeddings.npy',
                           repo_type='dataset', token=hf_token)
_rag_txt = hf_hub_download(repo_id=DATASET_REPO, filename='rag_facts_text.json',
                           repo_type='dataset', token=hf_token)
def _sha256(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


for hf_path, repo_rel in ((_rag_npy, 'kaggle/rag_embeddings.npy'),
                          (_rag_txt, 'kaggle/rag_facts_text.json')):
    a, b = _sha256(hf_path), _sha256(os.path.join(_CLONE, repo_rel))
    print(f'[rag] {os.path.basename(hf_path)}: HF {a} | repo {b} '
          f'{"OK" if a == b else "*** MISMATCH — R15 dual-commit is out of sync ***"}')

# Both arms build on the same index files; only the ARM differs (single vs two arm).
two_arm = Retriever(emb_path=_rag_npy, texts_path=_rag_txt,
                    expected_fact_count=EXPECTED_FACT_COUNT)
single_arm = pipeline_v15.V15Retriever(emb_path=_rag_npy, texts_path=_rag_txt,
                                       expected_fact_count=EXPECTED_FACT_COUNT)
print(f'[rag] preflight OK — {two_arm.preflight()} facts (fail-loud contract, commit 149938d)')

# ── MODEL: loaded ONCE, shared by both arms ──────────────────────────────────────
subprocess.run(['pip', 'install', '-q', '-U', 'bitsandbytes>=0.46.1'], check=True)
subprocess.run(['pip', 'install', '-q', '-U', 'sentence-transformers>=2.7.0'], check=True)
import torch                                                          # noqa: E402
from transformers import (AutoTokenizer, AutoModelForCausalLM,        # noqa: E402
                          BitsAndBytesConfig, StoppingCriteria, StoppingCriteriaList)

print(f'[model] loading {ADAPTER} (4-bit) ...', flush=True)
tokenizer = AutoTokenizer.from_pretrained(ADAPTER, token=hf_token, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
_bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                          bnb_4bit_compute_dtype=torch.float16,
                          bnb_4bit_use_double_quant=True)
model = AutoModelForCausalLM.from_pretrained(ADAPTER, quantization_config=_bnb,
                                             device_map='auto', token=hf_token,
                                             trust_remote_code=True)
model.eval()
print('[model] loaded OK — ONE set of weights, both arms')


class _Stop(StoppingCriteria):
    def __init__(self, tok, stops):
        self.tok, self.stops = tok, stops

    def __call__(self, input_ids, scores, **kw):
        return any(s in self.tok.decode(input_ids[0], skip_special_tokens=True)[-100:]
                   for s in self.stops)


def _generate(prompt, params=None):
    """The Kaggle twin of chike-inference/modal_app.py::ChikeModel._generate — same
    StoppingCriteria, same gen_kwargs from config, same slicing/decode. Both arms call this,
    so the arms differ ONLY in pipeline logic, never in decoding."""
    p = dict(GEN)
    if params:
        p.update(params)
    inp = tokenizer(prompt, return_tensors='pt').to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inp,
            max_new_tokens=int(p.get('max_new_tokens', 350)),
            do_sample=bool(p.get('do_sample', False)),
            repetition_penalty=float(p.get('repetition_penalty', 1.1)),
            no_repeat_ngram_size=int(p.get('no_repeat_ngram_size', 0)),
            stopping_criteria=StoppingCriteriaList([_Stop(tokenizer, STOP)]),
            eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.pad_token_id)
    return tokenizer.decode(out[0][inp['input_ids'].shape[1]:],
                            skip_special_tokens=True).strip()


class _Backend(ModelBackend):
    """v16's backend. `tokenizer` attribute is what Orchestrator._backend_tokenizer() looks
    for, so build_chat_prompt routes through apply_chat_template — byte-identical to
    production's prompt format (without it the orchestrator silently falls back to a
    naive-concat shape the model was never trained on)."""

    def __init__(self):
        self.tokenizer = tokenizer

    def generate(self, prompt, params=None):
        return _generate(prompt, params)


orch = Orchestrator(backend=_Backend(), retriever=two_arm.retrieve,
                    system_prompt=SYSTEM_PROMPT)
orch_single = Orchestrator(backend=_Backend(), retriever=single_arm.retrieve_facts,
                           system_prompt=SYSTEM_PROMPT)

# ── ARTIFACT PUBLISHING — checkpointed, verified, and loud on failure ────────────
# A 3.5h GPU run must NOT end with only a terminal paste (project convention: results are
# fetched independently from HF and committed, never concluded from a paste). The previous
# version uploaded once, as the very last statement, inside a bare try/except that merely
# printed on failure — so a crash in the judge overlay, or a transient HF error at hour 3.5,
# lost everything. This publishes at EVERY stage boundary, overwrites one canonical filename
# so the latest state is always retrievable, and VERIFIES each upload by re-downloading and
# comparing sha256. `complete` distinguishes a checkpoint from the finished artifact.
ARTIFACT_NAME = f'gate_phase_d_paired_{_sha}.json'
ARTIFACT_PATH = f'/kaggle/working/{ARTIFACT_NAME}'


def _publish(stage, complete=False, **extra):
    """Write the artifact locally, upload to HF, then verify by re-download + sha256."""
    payload = {
        'stage': stage, 'complete': complete, 'clone_head': _sha,
        'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'adapter': ADAPTER, 'config_version': CONFIG.get('version'),
        'index_facts': EXPECTED_FACT_COUNT, 'n_questions': len(ALL),
    }
    payload.update(extra)
    with open(ARTIFACT_PATH, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    local_sha = hashlib.sha256(open(ARTIFACT_PATH, 'rb').read()).hexdigest()

    from huggingface_hub import HfApi, hf_hub_download as _dl
    last = None
    for attempt in range(1, 4):
        try:
            HfApi().upload_file(path_or_fileobj=ARTIFACT_PATH, path_in_repo=ARTIFACT_NAME,
                                repo_id=DATASET_REPO, repo_type='dataset', token=hf_token)
            back = _dl(repo_id=DATASET_REPO, filename=ARTIFACT_NAME, repo_type='dataset',
                       token=hf_token, force_download=True)
            remote_sha = hashlib.sha256(open(back, 'rb').read()).hexdigest()
            if remote_sha == local_sha:
                print(f'[publish] {stage:<14} OK  HF {DATASET_REPO}/{ARTIFACT_NAME}  '
                      f'sha256={local_sha[:16]}  complete={complete}', flush=True)
                return True
            print(f'[publish] {stage} VERIFY MISMATCH local={local_sha[:16]} '
                  f'remote={remote_sha[:16]} — retrying', flush=True)
            last = RuntimeError('sha mismatch')
        except Exception as e:                                       # noqa: BLE001
            last = e
            print(f'[publish] {stage} attempt {attempt}/3 FAILED: {str(e)[:200]}', flush=True)
            time.sleep(10 * attempt)
    # Loud, unmissable, but never fatal: the run must not be thrown away because HF is down.
    print('\n' + '!' * 78, flush=True)
    print(f'!! HF PUBLISH FAILED at stage={stage} after 3 attempts: {str(last)[:300]}')
    print(f'!! The artifact IS on Kaggle at {ARTIFACT_PATH} — DOWNLOAD IT MANUALLY.')
    print('!' * 78 + '\n', flush=True)
    return False


def v15_answer(q):
    return pipeline_v15.answer(
        q, generate=_generate, retrieve_facts=single_arm.retrieve_facts,
        system_prompt=SYSTEM_PROMPT, tokenizer=tokenizer, stop_strings=STOP,
        config=CONFIG).get('reply', '')


# ── ROUTE TAGGING (v16's view; used for bucket C and the part-3 subset) ──────────
def _is_compute(q):
    if not orch.classify(q):
        return False
    return any(orch.route(p).kind == 'compute' for p in orch.decompose(q))


for q in ALL:
    q['_compute'] = _is_compute(q['question_sw'])
print(f'[route] v16 routes {sum(q["_compute"] for q in ALL)}/{len(ALL)} to compute')


# ── THE PAIRED RUN ───────────────────────────────────────────────────────────────
def _score_row(q, gen, clarified):
    try:
        passed = False if clarified else bool(score_question(q, gen, REFUSAL_PHRASES))
    except Exception:                                                # noqa: BLE001
        passed = False
    try:
        reliable, why = scorer_reliability(q, gen)
    except Exception:                                                # noqa: BLE001
        reliable, why = True, ''
    return passed, reliable, why


def _row(q, gen, raw, clarified):
    passed, reliable, why = _score_row(q, gen, clarified)
    return {'id': q['id'], 'source': q['_source'], 'subdomain': q.get('subdomain', ''),
            'answer_type': q.get('answer_type', ''), 'compute': q['_compute'],
            'question_sw': q['question_sw'], 'correct_answer_sw': q.get('correct_answer_sw', ''),
            'generated': gen, 'raw_generated': raw, 'clarified': clarified,
            'pass': passed, 'reliable': reliable, 'reliable_reason': why,
            'target': q.get('_target', ''), 'why_hard': q.get('_why_hard', '')}


print(f'\n[run] ARM v15 — {len(ALL)} questions through chike.pipeline_v15 ...', flush=True)
res15, t0 = [], time.time()
for i, q in enumerate(ALL):
    try:
        gen = v15_answer(q['question_sw'])
    except Exception as e:                                           # noqa: BLE001
        gen = f'ERROR: {e}'
    # v15 has no compute path: its only non-generated replies are the OOC refusal and the
    # payroll never-guess clarification.
    clar = gen == pipeline_v15.PAYROLL_CLARIFICATION
    res15.append(_row(q, gen, gen, clar))
    if (i + 1) % 25 == 0:
        print(f'  v15 [{i+1}/{len(ALL)}] {time.time()-t0:.0f}s', flush=True)
_publish('v15_arm_done', v15_results=res15)

print(f'\n[run] ARM v16 — {len(ALL)} questions through the Orchestrator ...', flush=True)
res16, t0 = [], time.time()
for i, q in enumerate(ALL):
    raw = ''
    try:
        reply = orch.answer(q['question_sw'])
        gen, raw, clar = reply.text, reply.raw_text, reply.needs_clarification
    except Exception as e:                                           # noqa: BLE001
        gen, clar = f'ERROR: {e}', False
    res16.append(_row(q, gen, raw, clar))
    if (i + 1) % 25 == 0:
        print(f'  v16 [{i+1}/{len(ALL)}] {time.time()-t0:.0f}s', flush=True)
_publish('v16_arm_done', v15_results=res15, v16_results=res16)


# ── BUCKETS, BOTH ARMS ───────────────────────────────────────────────────────────
def _acc(rows, reliable_only=False):
    rs = [r for r in rows if (r['reliable'] or not reliable_only)]
    rs = [r for r in rs if r['subdomain'] != 'out_of_corpus']
    if not rs:
        return 0, 0, 0.0
    p = sum(r['pass'] for r in rs)
    return p, len(rs), p / len(rs)


def _buckets(rows):
    return {
        'fact_path_190': [r for r in rows if r['source'] == 'gate_001' and not r['compute']],
        'staged_50': [r for r in rows if r['source'] == 'additions_002'],
        'compute_type': [r for r in rows if r['compute']],
        'adversarial_150': [r for r in rows if r['source'] == 'additions_003'],
        'ALL_400': rows,
    }


B15, B16 = _buckets(res15), _buckets(res16)
print('\n' + '=' * 78)
print(f'PAIRED BUCKET SCORES  (clone {_sha})   v15 -> v16')
print('=' * 78)
bucket_table = {}
for name in B15:
    p15r, n15r, a15r = _acc(B15[name])
    p16r, n16r, a16r = _acc(B16[name])
    p15l, n15l, a15l = _acc(B15[name], True)
    p16l, n16l, a16l = _acc(B16[name], True)
    bucket_table[name] = {
        'n': len(B15[name]),
        'raw': {'v15': [p15r, n15r, round(a15r, 4)], 'v16': [p16r, n16r, round(a16r, 4)],
                'delta_pts': round((a16r - a15r) * 100, 1)},
        'reliable': {'v15': [p15l, n15l, round(a15l, 4)], 'v16': [p16l, n16l, round(a16l, 4)],
                     'delta_pts': round((a16l - a15l) * 100, 1)},
        'clarified': {'v15': sum(r['clarified'] for r in B15[name]),
                      'v16': sum(r['clarified'] for r in B16[name])},
    }
    print(f'\n{name}: n={len(B15[name])}')
    print(f'   raw       v15 {p15r}/{n15r}={a15r:.1%}   v16 {p16r}/{n16r}={a16r:.1%}   '
          f'delta {(a16r-a15r)*100:+.1f} pts')
    print(f'   reliable  v15 {p15l}/{n15l}={a15l:.1%}   v16 {p16l}/{n16l}={a16l:.1%}   '
          f'delta {(a16l-a15l)*100:+.1f} pts')
    print(f'   clarified v15 {bucket_table[name]["clarified"]["v15"]}   '
          f'v16 {bucket_table[name]["clarified"]["v16"]}')

# ── FLIP ANALYSIS — every v15-PASS -> v16-FAIL enumerated ────────────────────────
by15 = {r['id']: r for r in res15}
by16 = {r['id']: r for r in res16}
regressions = [i for i in by15 if by15[i]['pass'] and not by16[i]['pass']]
gains = [i for i in by15 if not by15[i]['pass'] and by16[i]['pass']]

print('\n' + '=' * 78)
print(f'FLIP ANALYSIS — {len(gains)} gains (v15 FAIL -> v16 PASS), '
      f'{len(regressions)} regressions (v15 PASS -> v16 FAIL)')
print('=' * 78)
print('\nThe founder bar: v16 >= v15 on raw AND reliable, AND no CLASS of regression even at')
print('parity. Every regression is printed in full below for individual adjudication.\n')
reg_detail = []
for qid in regressions:
    a, b = by15[qid], by16[qid]
    d = {'id': qid, 'subdomain': a['subdomain'], 'answer_type': a['answer_type'],
         'compute_routed': b['compute'], 'v16_clarified': b['clarified'],
         'reliable_v15': a['reliable'], 'reliable_v16': b['reliable'],
         'question': a['question_sw'], 'gold': a['correct_answer_sw'],
         'v15_generated': a['generated'], 'v16_generated': b['generated']}
    reg_detail.append(d)
    print(f'--- REGRESSION {qid} [{a["subdomain"]}/{a["answer_type"]}] '
          f'compute={b["compute"]} v16_clarified={b["clarified"]} '
          f'reliable(v15={a["reliable"]},v16={b["reliable"]})')
    print(f'    Q   : {a["question_sw"][:150]}')
    print(f'    GOLD: {a["correct_answer_sw"][:200]}')
    print(f'    v15 : {a["generated"][:300]}')
    print(f'    v16 : {b["generated"][:300]}')

_reg_by_sub = defaultdict(int)
for d in reg_detail:
    _reg_by_sub[d['subdomain']] += 1
print(f'\nregressions by subdomain: {dict(_reg_by_sub)}')
print(f'regressions that are v16 CLARIFICATIONS (never-guess, not wrong answers): '
      f'{sum(1 for d in reg_detail if d["v16_clarified"])}')

# ── RUN 2 PART 3 — de-confound: v16 two-arm vs v16 SINGLE-arm ────────────────────
# After parts 1-2 (append-only confirmed safe, but 1 recovery vs 86 dilutions on the labelled
# set), this decides whether the two-arm retriever ships at all. Subset = questions where the
# second arm can actually fire AND the answer comes from RAG: digit-bearing, strip-eligible,
# and FACT-routed (a compute answer's number comes from the rules engine, not from facts).
from chike.retrieval import strip_numeric_amounts                    # noqa: E402

part3_qs = [q for q in ALL
            if any(c.isdigit() for c in q['question_sw'])
            and strip_numeric_amounts(q['question_sw']) not in ('', q['question_sw'])
            and not q['_compute']
            and q.get('subdomain') != 'out_of_corpus']
print('\n' + '=' * 78)
print(f'RUN 2 PART 3 — de-confound: v16 TWO-ARM vs v16 SINGLE-ARM on {len(part3_qs)} '
      'fact-routed, second-arm-eligible questions')
print('=' * 78)

res3, t0 = [], time.time()
for i, q in enumerate(part3_qs):
    try:
        reply = orch_single.answer(q['question_sw'])
        gen, clar = reply.text, reply.needs_clarification
    except Exception as e:                                           # noqa: BLE001
        gen, clar = f'ERROR: {e}', False
    res3.append(_row(q, gen, gen, clar))
    if (i + 1) % 20 == 0:
        print(f'  part3 [{i+1}/{len(part3_qs)}] {time.time()-t0:.0f}s', flush=True)
_publish('part3_done', v15_results=res15, v16_results=res16, part3_results=res3,
         buckets=bucket_table, regression_detail=reg_detail)

by3 = {r['id']: r for r in res3}
two_rows = [by16[i] for i in by3]
p_two, n_two, a_two = _acc(two_rows)
p_one, n_one, a_one = _acc(res3)
pl_two, nl_two, al_two = _acc(two_rows, True)
pl_one, nl_one, al_one = _acc(res3, True)
identical_text = sum(1 for i in by3 if by3[i]['generated'] == by16[i]['generated'])
two_only = [i for i in by3 if by16[i]['pass'] and not by3[i]['pass']]     # two-arm wins
one_only = [i for i in by3 if by3[i]['pass'] and not by16[i]['pass']]     # single-arm wins

print(f'\nanswers byte-identical despite the extra fact: {identical_text}/{len(part3_qs)}')
print(f'raw       two-arm {p_two}/{n_two}={a_two:.1%}   single-arm {p_one}/{n_one}={a_one:.1%}   '
      f'delta {(a_two-a_one)*100:+.1f} pts (positive = two-arm better)')
print(f'reliable  two-arm {pl_two}/{nl_two}={al_two:.1%}   single-arm {pl_one}/{nl_one}={al_one:.1%}   '
      f'delta {(al_two-al_one)*100:+.1f} pts')
print(f'\nTWO-ARM-ONLY passes ({len(two_only)}): {two_only}')
for qid in two_only:
    print(f'  + {qid} [{by16[qid]["subdomain"]}] Q: {by16[qid]["question_sw"][:90]}')
print(f'SINGLE-ARM-ONLY passes ({len(one_only)}): {one_only}')
for qid in one_only:
    print(f'  - {qid} [{by3[qid]["subdomain"]}] Q: {by3[qid]["question_sw"][:90]}')

# ── JUDGE OVERLAY — both arms ────────────────────────────────────────────────────
judge_overlays = {}
if RUN_JUDGE:
    from concurrent.futures import ThreadPoolExecutor

    def _judge_arm(label, rows):
        gradeable = chike_judge.judge_gradeable(rows)
        print(f'\n[judge/{label}] grading {len(gradeable)} rows '
              f'(~{len(gradeable) * chike_judge.DEFAULT_N} calls, majority-of-'
              f'{chike_judge.DEFAULT_N}, pinned {chike_judge.DEFAULT_PROVIDER}) ...', flush=True)
        tj = time.time()

        def _one(r):
            return r['id'], chike_judge.judge_majority(
                r['question_sw'], r.get('correct_answer_sw', ''),
                chike_judge.clean_for_judge(r['generated']), api_key=OR_KEY)

        jrows, done = {}, 0
        with ThreadPoolExecutor(max_workers=8) as ex:
            for qid, v in ex.map(_one, gradeable):
                jrows[qid] = v
                done += 1
                if done % 50 == 0:
                    print(f'   [{label}] ...{done}/{len(gradeable)} ({time.time()-tj:.0f}s)',
                          flush=True)
        for r in rows:
            r['judge'] = jrows[r['id']]['verdict'] if r['id'] in jrows else None
        rep = chike_judge.build_confirmation_report(rows)
        cost = (sum(v['pin'] for v in jrows.values()) * chike_judge.PRICE_IN
                + sum(v['pout'] for v in jrows.values()) * chike_judge.PRICE_OUT)
        provs = sorted({p for v in jrows.values() for p in v['providers']})
        print(f'  [{label}] providers={provs} errors='
              f'{sum(v["err_count"] for v in jrows.values())} USD~{cost:.4f} '
              f'wall {time.time()-tj:.0f}s')
        print(f'  [{label}] raw {rep["raw"]["acc"]:.1%} | reliable-denom '
              f'{rep["reliable_denom"]["acc"]:.1%} | JUDGE-AUGMENTED '
              f'{rep["judge_augmented"]["acc"]:.1%}')
        dq = rep['disagreement_queue']
        print(f'  [{label}] disagreement queue: {len(dq["false_pass_candidates"])} false-pass, '
              f'{len(dq["false_fail_candidates"])} false-fail')
        return {'report': rep, 'providers': provs, 'usd': round(cost, 4),
                'graded': len(gradeable)}

    judge_overlays['v15'] = _judge_arm('v15', res15)
    judge_overlays['v16'] = _judge_arm('v16', res16)

    # HARNESS FIX (re-run): judge the PART-3 rows too. The 3ac522a run left 90/90 part-3 rows
    # ungraded — the overlay ran on res15/res16 only — so the two-arm ship/don't-ship call
    # rested on the regex scorer alone until it was adjudicated by hand. That mattered: on
    # that run the regex scorer credited two-arm with 4 passes the judge called wrong, and
    # 2 of the 6 "two-arm-only" wins survived judging. Grade the single-arm rows here and
    # restate the comparison judge-augmented, so the call rests on the same instrument as
    # the main arms.
    judge_overlays['part3_single_arm'] = _judge_arm('part3_single_arm', res3)

    def _aug(rows):
        rep = chike_judge.build_confirmation_report(rows)['judge_augmented']
        return rep['pass'], rep['total'], rep['acc']

    # two_rows are the SAME questions as res3 but answered by the two-arm retriever; they
    # were graded inside the v16 overlay above, so both sides are now judge-augmented.
    jp_two, jn_two, ja_two = _aug(two_rows)
    jp_one, jn_one, ja_one = _aug(res3)
    print('\n' + '=' * 78)
    print('RUN 2 PART 3 — JUDGE-AUGMENTED (the instrument the 3ac522a run lacked)')
    print('=' * 78)
    print(f'  two-arm    {jp_two}/{jn_two} = {ja_two:.1%}')
    print(f'  single-arm {jp_one}/{jn_one} = {ja_one:.1%}')
    print(f'  delta {(ja_two - ja_one) * 100:+.1f} pts (positive = two-arm better)')
    j_two_only = [i for i in by3
                  if by16[i].get('judge') == 'correct' and by3[i].get('judge') == 'wrong']
    j_one_only = [i for i in by3
                  if by3[i].get('judge') == 'correct' and by16[i].get('judge') == 'wrong']
    print(f'  judge-confirmed TWO-ARM-only wins ({len(j_two_only)}): {j_two_only}')
    print(f'  judge-confirmed SINGLE-ARM-only wins ({len(j_one_only)}): {j_one_only}')
    part3_judged = {'two_arm': {'pass': jp_two, 'total': jn_two, 'acc': ja_two},
                    'single_arm': {'pass': jp_one, 'total': jn_one, 'acc': ja_one},
                    'delta_pts': round((ja_two - ja_one) * 100, 2),
                    'judge_two_arm_only': j_two_only, 'judge_single_arm_only': j_one_only}
else:
    print('\n[judge] SKIPPED (no OPENROUTER_API_KEY or CHIKE_JUDGE=0)')
    part3_judged = None

# ── VERDICT vs THE ADR BAR ───────────────────────────────────────────────────────
raw_ok = bucket_table['ALL_400']['raw']['delta_pts'] >= 0
rel_ok = bucket_table['ALL_400']['reliable']['delta_pts'] >= 0
print('\n' + '=' * 78)
print('ADR 0001 §10 BAR — v16 >= v15 on the full 400, raw AND reliable')
print('=' * 78)
print(f'  raw      delta {bucket_table["ALL_400"]["raw"]["delta_pts"]:+.1f} pts  '
      f'-> {"PASS" if raw_ok else "FAIL"}')
print(f'  reliable delta {bucket_table["ALL_400"]["reliable"]["delta_pts"]:+.1f} pts  '
      f'-> {"PASS" if rel_ok else "FAIL"}')
print(f'  regressions to adjudicate individually: {len(regressions)} '
      '(the "no class of regression" clause is a HUMAN call on the detail above)')

# ── SUMMARY BLOCK ────────────────────────────────────────────────────────────────
summary = {
    'clone_head': _sha, 'live_head': _live, 'config_version': CONFIG.get('version'),
    'adapter': ADAPTER, 'index_facts': EXPECTED_FACT_COUNT, 'n_questions': len(ALL),
    'v16_compute_routed': sum(q['_compute'] for q in ALL),
    'buckets': bucket_table,
    'adr_bar': {'raw_delta_pts': bucket_table['ALL_400']['raw']['delta_pts'],
                'reliable_delta_pts': bucket_table['ALL_400']['reliable']['delta_pts'],
                'raw_pass': raw_ok, 'reliable_pass': rel_ok},
    'flips': {'gains': len(gains), 'regressions': len(regressions),
              'regression_ids': sorted(regressions), 'gain_ids': sorted(gains),
              'regressions_by_subdomain': dict(_reg_by_sub),
              'regressions_that_are_v16_clarifications':
                  sum(1 for d in reg_detail if d['v16_clarified'])},
    'run2_part3_deconfound': {
        'n': len(part3_qs),
        'answers_byte_identical': identical_text,
        'raw': {'two_arm': [p_two, n_two, round(a_two, 4)],
                'single_arm': [p_one, n_one, round(a_one, 4)],
                'delta_pts': round((a_two - a_one) * 100, 1)},
        'reliable': {'two_arm': [pl_two, nl_two, round(al_two, 4)],
                     'single_arm': [pl_one, nl_one, round(al_one, 4)],
                     'delta_pts': round((al_two - al_one) * 100, 1)},
        'two_arm_only_passes': two_only, 'single_arm_only_passes': one_only,
        # Re-run addition: the 3ac522a run left these 90 rows ungraded, so the two-arm call
        # rested on the regex scorer alone. None only when the judge is skipped entirely.
        'judge_augmented': part3_judged},
    'judge': {k: {'raw': v['report']['raw'], 'reliable_denom': v['report']['reliable_denom'],
                  'judge_augmented': v['report']['judge_augmented'],
                  'gap_fill': v['report']['gap_fill'],
                  'disagreement_counts': {
                      'false_pass': len(v['report']['disagreement_queue']['false_pass_candidates']),
                      'false_fail': len(v['report']['disagreement_queue']['false_fail_candidates'])},
                  'providers': v['providers'], 'usd': v['usd'], 'graded': v['graded']}
              for k, v in judge_overlays.items()},
}

print('\n\n' + '#' * 78)
print('### PHASE D PAIRED SUMMARY — PASTE EVERYTHING BETWEEN THE # LINES ###')
print('#' * 78)
print(json.dumps(summary, ensure_ascii=False, indent=1))
print('#' * 78)
print('### END SUMMARY ###')
print('#' * 78)

_publish('complete', complete=True, summary=summary, regression_detail=reg_detail,
         v15_results=res15, v16_results=res16, part3_results=res3,
         judge_overlays=judge_overlays)
print(f'\n[done] artifact: {ARTIFACT_PATH}')
print(f'[done] HF: {DATASET_REPO}/{ARTIFACT_NAME}  (Claude Code fetches THIS, not the paste)')

# -*- coding: utf-8 -*-
"""Step 6 — COMBINED orchestrator regression on Kaggle (GPU). Prepare-only; founder runs it.

Extends kaggle/eval_orchestrator.py (which tested the fact-path-only 190 subset and EXCLUDED
the 10 compute-routed questions) to a full combined run:

  200 main gate (eval_questions_001)  +  50 staged additions (eval_questions_002_additions)
  + 150 adversarial additions (eval_questions_003)  =  400 questions, ALL run through the
  real chike/orchestrator.py end-to-end, with every compute-routed question now going through
  the REAL slot extraction (chike/extraction.py + chike/swahili_numbers.py) and the rules
  engine. The 150 new questions (eval_251-400) deliberately stress every architecture sub-part
  (slot-extraction attacks, classifier/OOC edge cases, decomposer stress, retrieval near-misses,
  rules-engine threshold boundaries, and scorer-leak probes for the already-fixed BUG 7 /
  '000'-token / yes_no-polarity / overlap-leniency issues).

Reports four separate scores (so the effect of the extraction change is isolated):
  A. FACT-PATH 190  — must be UNCHANGED vs the prior baseline (extraction only touches the
     compute path + route() is unchanged, so these answers are byte-identical; this run
     re-confirms empirically, not by assertion).
  B. STAGED 50      — first real score on eval_questions_002_additions (held back earlier
     until the scorer was trustworthy; scorer bugs since fixed + scorer_reliability in place).
  C. COMPUTE        — real score on ALL compute-routed questions from every source, now that
     extraction is built (previously all excluded / would have returned <CLARIFICATION_NEEDED>).
     With the 150 new questions this is the first meaningfully-sized compute-path sample.
  D. ADVERSARIAL 150 — first real score on eval_questions_003 (eval_251-400), the deliberate
     per-sub-part stress set.

Reliable-denominator scoring (chike.scoring.scorer_reliability) is reported alongside raw,
matching the honest reduced-denominator method adopted 2026-07-14 (PROGRESS.md).

HOW TO RUN (Kaggle notebook, GPU ON):
    import requests
    exec(requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                      'AFRICA-GIANTS/main/kaggle/eval_orchestrator_combined.py', timeout=10).text)

PREREQS:
  - Kaggle GPU ON; Kaggle secret AFRICA_GIANTS (HF token).
  - eval_questions_002_additions.jsonl AND eval_questions_003.jsonl are UNMERGED + not on
    GitHub. Loader checks, for each, in order:
      (1) local clone eval/accuracy_gate/, (2) /kaggle/input/**, (3) HF dataset repo.
"""
import os, sys, json, glob, time, subprocess
from collections import defaultdict, Counter
from datetime import datetime, timezone

import requests

REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
RAW = f'https://raw.githubusercontent.com/{REPO}/main'
DATASET_REPO = 'prospAprospA007/africa-giants-dataset'
ADDITIONS_FILE = 'eval_questions_002_additions.jsonl'
ADDITIONS3_FILE = 'eval_questions_003.jsonl'

# ── AUTH ────────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    _sc = kaggle_secrets.UserSecretsClient()
    hf_token = _sc.get_secret('AFRICA_GIANTS')
except Exception as e:
    raise RuntimeError('run on Kaggle with AFRICA_GIANTS attached') from e
assert hf_token, 'AFRICA_GIANTS empty'
os.environ['HF_TOKEN'] = hf_token
print(f'[auth] AFRICA_GIANTS ({hf_token[:6]}...) OK')

# OPENROUTER_API_KEY is MANDATORY (2026-08-09). It used to be optional — absent key meant the
# gate ran fully and quietly skipped the overlay. The 1476caa run showed what that costs:
# eval_318 (tells a TZS 205,000,000 business it need not register for VAT against a 200M
# threshold) and eval_320 (SDL 28,000 on a ONE-employee payroll) BOTH score pass=True, so the
# regex scorer positively credits the two worst defects of the cycle and only the judge calls
# either wrong. The instrument that sees that class must not be the one that can silently not
# run. This does NOT promote the judge to the GATE PASSED trigger — that stays gated on work
# item 2. Fail at second 0, not after the GPU pass.
try:
    OR_KEY = _sc.get_secret('OPENROUTER_API_KEY')
except Exception:
    OR_KEY = os.environ.get('OPENROUTER_API_KEY', '')

JUDGE_OPT_OUT = os.environ.get('CHIKE_JUDGE', '1') == '0'
if not OR_KEY and not JUDGE_OPT_OUT:
    raise RuntimeError(
        'OPENROUTER_API_KEY missing — the judge overlay is MANDATORY for a gate run.\n'
        '  Attach it as a Kaggle secret named OPENROUTER_API_KEY (or set the env var).\n'
        '  To run WITHOUT it anyway, set CHIKE_JUDGE=0 explicitly; the artifact is then\n'
        '  stamped judge_overlay="SKIPPED" and its headline is not trustworthy on its own\n'
        '  — see the STANDING LIMITATION entry in PROGRESS.md.'
    )
RUN_JUDGE = bool(OR_KEY) and not JUDGE_OPT_OUT
if RUN_JUDGE:
    print('[auth] OPENROUTER_API_KEY set — judge overlay ON, MANDATORY')
else:
    print('=' * 78)
    print('!! JUDGE OVERLAY EXPLICITLY DISABLED (CHIKE_JUDGE=0).')
    print('!! The regex scorer CREDITS wrong-direction answers. Do NOT report this run as a')
    print('!! clean result. The artifact is stamped judge_overlay="SKIPPED".')
    print('=' * 78)

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

# These 4 are yes/no FACT questions that route()'s crude keyword+digit heuristic
# misroutes to the compute path (they mention nssf/sdl + a digit like '10'/'20'/'7' but
# ask a concept, not a calculation). When they return clarification / fail in bucket C
# that is a ROUTING MISS, not an extraction defect — labeled explicitly so it is not
# misread during review. Broadening route() is the deferred follow-up (PROGRESS.md).
KNOWN_ROUTING_MISS = {'eval_099', 'eval_100', 'eval_102', 'eval_127'}

from chike.orchestrator import Orchestrator, CLARIFICATION_PENDING        # noqa: E402
from chike.model_abstraction import ModelBackend                          # noqa: E402
from chike.retrieval import Retriever                                     # noqa: E402
from chike.scoring import (score_question, scorer_reliability,           # noqa: E402
                           prohibition_polarity_review)
from chike import judge as chike_judge                                    # noqa: E402  (item-5 overlay)

# ── CONFIG ───────────────────────────────────────────────────────────────────────
_cb = str(int(time.time() * 1000))
_nc = {'Cache-Control': 'no-cache'}
CONFIG = requests.get(f'{RAW}/kaggle/chike_config.json?cb={_cb}', headers=_nc, timeout=15).json()
SYSTEM_PROMPT = CONFIG['system_prompt']
REFUSAL_PHRASES = CONFIG['refusal_phrases']
OOC_PHRASES = CONFIG.get('ooc_phrases', [])
IN_THR = CONFIG['gate_thresholds']['in_corpus']
GEN = CONFIG['generation_params']
STOP = GEN.get('stop_strings', ['\n\nQ:', '\n\nSwali:', '<|start_header_id|>', '\n\n---'])
ADAPTER = CONFIG.get('adapter_repo', 'prospAprospA007/africa-giants-adapter-v15')
print(f'[config] v={CONFIG.get("version")} in_corpus_threshold={IN_THR}')

# ── DATA: 200 gate (HF) + 50 additions (local/input/HF) + RAG index ─────────────
from huggingface_hub import hf_hub_download, HfApi                        # noqa: E402
_q = hf_hub_download(repo_id=DATASET_REPO, filename='eval_questions_001.jsonl',
                     repo_type='dataset', token=hf_token)
gate = [json.loads(l) for l in open(_q, encoding='utf-8') if l.strip()]
assert len(gate) == 200, len(gate)
for q in gate:
    q['_source'] = 'gate_001'


def _load_unmerged(fname):
    """Load an unmerged/gitignored gate file: local clone -> /kaggle/input -> HF dataset repo."""
    for p in [os.path.join(_CLONE, 'eval/accuracy_gate', fname),
              *glob.glob(f'/kaggle/input/**/{fname}', recursive=True)]:
        if os.path.exists(p):
            print(f'[data] {fname} from {p}')
            return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
    p = hf_hub_download(repo_id=DATASET_REPO, filename=fname,
                        repo_type='dataset', token=hf_token)
    print(f'[data] {fname} from HF {DATASET_REPO}/{fname}')
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


additions = _load_unmerged(ADDITIONS_FILE)
assert len(additions) == 50, len(additions)
for q in additions:
    q['_source'] = 'additions_002'
    q.setdefault('correct_answer_sw', q.get('correct_answer_sw', ''))

additions3 = _load_unmerged(ADDITIONS3_FILE)
assert len(additions3) == 150, len(additions3)
for q in additions3:
    q['_source'] = 'additions_003'
    q.setdefault('correct_answer_sw', q.get('correct_answer_sw', ''))

ALL = gate + additions + additions3
print(f'[data] {len(ALL)} questions total (200 gate + 50 additions + 150 adversarial)')

_rag_npy = hf_hub_download(repo_id=DATASET_REPO, filename='rag_embeddings.npy',
                           repo_type='dataset', token=hf_token)
_rag_txt = hf_hub_download(repo_id=DATASET_REPO, filename='rag_facts_text.json',
                           repo_type='dataset', token=hf_token)
print('[data] RAG index downloaded (e5-base)')

# ── MODEL (byte-identical 4-bit load to eval_orchestrator.py) ────────────────────
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
        # Expose the tokenizer under the name Orchestrator._backend_tokenizer() looks for, so
        # build_chat_prompt routes through apply_chat_template — byte-identical to modal_app.run()
        # / production (Phase D Stage 0, Finding D-1). Without this alias the orchestrator fell
        # back to the naive-concat format the model was NOT trained on (a `\n\n` separator between
        # the system block and the question), silently mis-measuring the v16 gate.
        self.tokenizer = self.tok
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

# ── TAG each question by orchestrator routing (compute vs fact) ──────────────────
def _is_compute(q):
    if not orch.classify(q['question_sw']):
        return False
    return any(orch.route(p).kind == 'compute' for p in orch.decompose(q['question_sw']))


for q in ALL:
    q['_compute'] = _is_compute(q)
n_compute = sum(q['_compute'] for q in ALL)
print(f'[route] {n_compute} compute-routed of {len(ALL)} '
      f'(gate={sum(q["_compute"] for q in gate)}, additions={sum(q["_compute"] for q in additions)})')

# ── RUN all 250 through Orchestrator.answer() ───────────────────────────────────
print(f'[run] {len(ALL)} through the real orchestrator + model ...')
results = []
t0 = time.time()
for i, q in enumerate(ALL):
    raw = ''
    try:
        reply = orch.answer(q['question_sw'])
        gen, raw = reply.text, reply.raw_text
        # Clarifications now render real Swahili copy (chike.clarification), not the bare
        # sentinel — detect via the structured flag, not a magic string in the text.
        clarified = reply.needs_clarification
        passed = False if clarified else bool(score_question(q, gen, REFUSAL_PHRASES))
        try:
            reliable, why = scorer_reliability(q, gen)
        except Exception:
            reliable, why = True, ''
    except Exception as e:
        gen, clarified, passed, reliable, why = f'ERROR: {e}', False, False, True, 'error'
    results.append({'id': q['id'], 'source': q['_source'], 'subdomain': q.get('subdomain', ''),
                    'answer_type': q.get('answer_type', ''), 'compute': q['_compute'],
                    'routing_note': ('ROUTING MISS (yes/no fact misrouted to compute by route() '
                                     'keyword+digit heuristic — NOT an extraction failure)'
                                     if q['id'] in KNOWN_ROUTING_MISS else ''),
                    'question_sw': q['question_sw'], 'correct_answer_sw': q.get('correct_answer_sw', ''),
                    'generated': gen, 'raw_generated': raw, 'clarified': clarified,
                    'pass': passed, 'reliable': reliable, 'reliable_reason': why,
                    # authoring intent for the 150 adversarial questions (eval_003); empty for
                    # gate_001/additions_002. Surfaced in the compute detail so a deliberate
                    # classifier/OOC/decomposer probe that misroutes to compute is not misread
                    # as an extraction defect during review.
                    'target': q.get('_target', ''), 'why_hard': q.get('_why_hard', '')})
    if (i + 1) % 25 == 0 or i == 0:
        print(f'  [{i+1}/{len(ALL)}] {time.time()-t0:.0f}s')


# ── SCORE THE THREE BUCKETS ─────────────────────────────────────────────────────
def _score(rows, reliable_only=False):
    rs = [r for r in rows if (r['reliable'] or not reliable_only)]
    rs = [r for r in rs if r['subdomain'] != 'out_of_corpus']       # in-corpus only
    if not rs:
        return 0, 0, 0.0
    p = sum(r['pass'] for r in rs)
    return p, len(rs), (p / len(rs))


A = [r for r in results if r['source'] == 'gate_001' and not r['compute']]     # fact-path 190
B = [r for r in results if r['source'] == 'additions_002']                     # staged 50
C = [r for r in results if r['compute']]                                       # compute-type (any source)
D = [r for r in results if r['source'] == 'additions_003']                     # adversarial 150

print('\n' + '=' * 60)
print('COMBINED ORCHESTRATOR REGRESSION  (commit %s)' % _sha)
print('=' * 60)
for name, bucket in [('A. FACT-PATH (gate_001, non-compute)', A),
                     ('B. STAGED ADDITIONS (eval_002, 50)', B),
                     ('C. COMPUTE-TYPE (real extraction, all sources)', C),
                     ('D. ADVERSARIAL ADDITIONS (eval_003, 150)', D)]:
    praw, nraw, accraw = _score(bucket, reliable_only=False)
    prel, nrel, accrel = _score(bucket, reliable_only=True)
    clar = sum(r['clarified'] for r in bucket)
    print(f'\n{name}: n={len(bucket)}')
    print(f'   raw in-corpus:      {praw}/{nraw} = {accraw:.1%}')
    print(f'   reliable-subset:    {prel}/{nrel} = {accrel:.1%}  (scorer_unreliable excluded)')
    print(f'   returned clarification: {clar}')

# compute bucket per-question detail (only ~10 — show all). Genuine-compute vs
# routing-miss are separated so a failing routing-miss is not misread as an extraction bug.
_genuine = [r for r in C if not r['routing_note']]
_miss = [r for r in C if r['routing_note']]
print(f'\n  COMPUTE-TYPE per-question ({len(_genuine)} genuine-compute, '
      f'{len(_miss)} routing-miss labeled separately):')
for r in _genuine:
    print(f"    [GENUINE COMPUTE] {r['id']} [{r['subdomain']}/{r['answer_type']}] "
          f"pass={r['pass']} clarified={r['clarified']}"
          + (f"  intent={r['target']}" if r['target'] else ''))
    print(f"       Q: {r['question_sw'][:70]}")
    print(f"       gen: {r['generated'][:90].replace(chr(10),' ')}")
for r in _miss:
    print(f"    [ROUTING MISS — not an extraction failure] {r['id']} "
          f"[{r['subdomain']}/{r['answer_type']}] pass={r['pass']} clarified={r['clarified']}")
    print(f"       Q: {r['question_sw'][:70]}")

# ── HIGH-STAKES PROHIBITION POLARITY REVIEW (always reported; reliability-independent) ──
# Deterministic safety section: every hard-prohibition / absolute-obligation yes-no answer
# is polarity-checked against its reference answer REGARDLESS of scorer_reliability, so a
# dangerous inversion (e.g. eval_317 salon, eval_332 wholesale) can never again hide inside
# the 'unverifiable' bucket. Reporting-only: this touches no bucket score or denominator.
prohibition_review = []
for r in results:
    rev = prohibition_polarity_review(
        {'id': r['id'], 'answer_type': r['answer_type'], 'subdomain': r['subdomain'],
         'question_sw': r['question_sw'], 'correct_answer_sw': r['correct_answer_sw']},
        r['generated'])
    if rev is not None:
        rev['reliable'] = r['reliable']       # show whether the main scorer excluded it
        rev['pass'] = r['pass']
        prohibition_review.append(rev)

_pr_inv = [x for x in prohibition_review if x['candidate_inversion']]
print('\n' + '=' * 60)
print('HIGH-STAKES PROHIBITION POLARITY REVIEW (reliability-independent)')
print('=' * 60)
print(f'  high-stakes prohibition/absolute yes-no questions reviewed: {len(prohibition_review)}')
print(f'  CANDIDATE INVERSIONS (model polarity disagrees with reference): {len(_pr_inv)}')
_pr_inv_hidden = sum(1 for x in _pr_inv if not x['reliable'])
print(f'    of which the main scorer marked reliable=False (would otherwise be HIDDEN): '
      f'{_pr_inv_hidden}')
for x in _pr_inv:
    print(f"    *** {x['id']} [{x['reason']}] gold={x['gold_polarity']} "
          f"model={x['model_polarity']} reliable={x['reliable']} pass={x['pass']}")

# ── ITEM-5 FRONTIER-JUDGE OVERLAY (optional; OpenRouter, no GPU) ─────────────────
# A CONSERVATIVE, ASYMMETRIC scorer overlay (chike.judge): pinned provider + majority-of-5
# grades every in-corpus, non-clarified answer, then reports THREE numbers side by side —
# raw (today's gate) vs reliable-denominator (regex, gap excluded) vs judge-augmented (the
# reliable=False gap FILLED by the judge). Disagreements on the reliable=True set are QUEUED
# as candidates, never auto-applied. Does NOT touch any bucket score, scoring.py, or the live
# GATE PASSED trigger — reporting/transparency only (PROGRESS.md: the STRUCTURAL GATE FINDING
# + the item-5 report-alongside decision). Skipped cleanly when OPENROUTER_API_KEY is absent.
judge_overlay = None
if RUN_JUDGE:
    from concurrent.futures import ThreadPoolExecutor
    gradeable = chike_judge.judge_gradeable(results)
    print('\n' + '=' * 60)
    print(f'ITEM-5 FRONTIER-JUDGE OVERLAY — majority-of-{chike_judge.DEFAULT_N}, '
          f'pinned {chike_judge.DEFAULT_PROVIDER} seed={chike_judge.DEFAULT_SEED}')
    print(f'  grading {len(gradeable)} in-corpus non-clarified answers '
          f'(~{len(gradeable) * chike_judge.DEFAULT_N} calls) ...', flush=True)
    _tj = time.time()

    def _judge_row(r):
        v = chike_judge.judge_majority(r['question_sw'],
                                       r.get('correct_answer_sw', ''),
                                       chike_judge.clean_for_judge(r['generated']),
                                       api_key=OR_KEY)
        return r['id'], v

    jrows, jdone = {}, 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for qid, v in ex.map(_judge_row, gradeable):
            jrows[qid] = v
            jdone += 1
            if jdone % 40 == 0:
                print(f'   ...{jdone}/{len(gradeable)} judged ({time.time()-_tj:.0f}s)', flush=True)
    for r in results:                       # attach majority verdict for the aggregation
        r['judge'] = jrows[r['id']]['verdict'] if r['id'] in jrows else None

    report = chike_judge.build_confirmation_report(results)
    provs = sorted({p for v in jrows.values() for p in v['providers']})
    ties = [qid for qid, v in jrows.items() if v['tie']]
    jpin = sum(v['pin'] for v in jrows.values()); jpout = sum(v['pout'] for v in jrows.values())
    jerr = sum(v['err_count'] for v in jrows.values())
    jcost = jpin * chike_judge.PRICE_IN + jpout * chike_judge.PRICE_OUT
    judge_overlay = {
        'model': chike_judge.DEFAULT_MODEL, 'n': chike_judge.DEFAULT_N,
        'provider_pin': chike_judge.DEFAULT_PROVIDER, 'seed': chike_judge.DEFAULT_SEED,
        'providers_served': provs, 'graded': len(gradeable),
        'report': report, 'tie_ids': sorted(ties),
        'per_id': {qid: {'verdict': v['verdict'], 'votes': v['votes'], 'tie': v['tie'],
                         'justification': v['justification']} for qid, v in jrows.items()},
        'cost': {'calls': len(gradeable) * chike_judge.DEFAULT_N, 'prompt_tokens': jpin,
                 'completion_tokens': jpout, 'usd': round(jcost, 4)},
        'wall_s': round(time.time() - _tj, 1), 'api_errors': jerr,
        'caveat': ('report-alongside only: the judge fills the reliable=False gap and FLAGS '
                   'reliable=True disagreements, but never flips a confident regex verdict '
                   'and does not drive GATE PASSED (item-5, PROGRESS.md).')}
    rp = report
    print(f'  provider(s) served (want [{chike_judge.DEFAULT_PROVIDER}]): {provs}   '
          f'ties->undetermined: {len(ties)}   api_errors: {jerr}')
    print(f'  raw in-corpus:      {rp["raw"]["pass"]}/{rp["raw"]["total"]} = {rp["raw"]["acc"]:.1%}')
    print(f'  reliable-denom:     {rp["reliable_denom"]["pass"]}/{rp["reliable_denom"]["total"]} '
          f'= {rp["reliable_denom"]["acc"]:.1%}  (regex, gap excluded)')
    print(f'  JUDGE-AUGMENTED:    {rp["judge_augmented"]["pass"]}/{rp["judge_augmented"]["total"]} '
          f'= {rp["judge_augmented"]["acc"]:.1%}  (gap filled; undet excluded)   '
          f'floor(undet=fail) {rp["judge_augmented"]["floor_undet_fail"]["acc"]:.1%}')
    gf = rp['gap_fill']
    print(f'  gap-fill: {gf["gap_n"]} reliable=False -> {gf["judge_correct"]} correct / '
          f'{gf["judge_wrong"]} wrong / {gf["judge_undetermined"]} undetermined')
    dq = rp['disagreement_queue']
    print(f'  DISAGREEMENT QUEUE (candidates, NOT applied): '
          f'{len(dq["false_pass_candidates"])} false-pass, {len(dq["false_fail_candidates"])} false-fail')
    print(f'  [judge] ~USD {jcost:.4f}  wall {judge_overlay["wall_s"]:.0f}s')
else:
    print('\n[item-5 judge overlay] SKIPPED (no OPENROUTER_API_KEY or CHIKE_JUDGE=0)')

by_sd = defaultdict(lambda: {'pass': 0, 'total': 0})
for r in results:
    if r['subdomain'] != 'out_of_corpus':
        by_sd[r['subdomain']]['total'] += 1
        by_sd[r['subdomain']]['pass'] += int(r['pass'])

out = {'mode': 'combined_orchestrator_regression', 'commit': _sha,
       'timestamp': datetime.now(timezone.utc).isoformat(),
       'buckets': {
           'fact_path_190': dict(zip(('pass', 'n', 'acc'), _score(A))),
           'staged_50': dict(zip(('pass', 'n', 'acc'), _score(B))),
           'compute_type': dict(zip(('pass', 'n', 'acc'), _score(C))),
           'compute_type_genuine': dict(zip(('pass', 'n', 'acc'), _score(_genuine))),
           'compute_type_routing_miss': dict(zip(('pass', 'n', 'acc'), _score(_miss))),
           'adversarial_150': dict(zip(('pass', 'n', 'acc'), _score(D))),
           'fact_path_190_reliable': dict(zip(('pass', 'n', 'acc'), _score(A, True))),
           'staged_50_reliable': dict(zip(('pass', 'n', 'acc'), _score(B, True))),
           'adversarial_150_reliable': dict(zip(('pass', 'n', 'acc'), _score(D, True))),
           # Reliable-subset for the compute bucket, same pattern as A/B above. The raw
           # compute_type/compute_type_genuine numbers ride on number-type scorer leniency
           # (the reference answers embed input figures + rates), so the trustworthy read
           # is this scorer_reliability-filtered subset. Both are kept: raw shows what the
           # scorer currently reports, reliable shows the verifiable subset. compute_type_
           # genuine_reliable also excludes the route()-keyword-heuristic misroutes.
           'compute_type_reliable': dict(zip(('pass', 'n', 'acc'), _score(C, True))),
           'compute_type_genuine_reliable': dict(zip(('pass', 'n', 'acc'), _score(_genuine, True))),
       },
       'known_routing_miss_ids': sorted(KNOWN_ROUTING_MISS),
       # Reporting-only safety section — reliability-independent polarity check on every
       # high-stakes prohibition/absolute yes-no. Does not affect any bucket score.
       'prohibition_polarity_review': prohibition_review,
       'prohibition_candidate_inversions': [x['id'] for x in _pr_inv],
       # item-5 frontier-judge overlay (None when skipped): three side-by-side numbers +
       # gap-fill + disagreement queue. Reporting-only; does not drive GATE PASSED.
       'judge_overlay': judge_overlay,
       # Mandatory since 2026-08-09; a SKIPPED run must be self-identifying, because its
       # headline cannot see the wrong-direction class the regex scorer credits.
       'judge_overlay_status': ('ran' if RUN_JUDGE else
                                'SKIPPED (CHIKE_JUDGE=0) — headline NOT trustworthy alone'),
       'by_subdomain': {k: dict(v) for k, v in by_sd.items()},
       'results': results}
path = '/kaggle/working/gate_orchestrator_combined.json'
json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n[save] {path}')
try:
    HfApi().upload_file(path_or_fileobj=path, path_in_repo='gate_orchestrator_combined.json',
                        repo_id='prospAprospA007/africa-giants-adapter-v15', repo_type='model',
                        token=hf_token, commit_message='combined orchestrator regression (190 fact + 50 staged + compute)')
    print('[upload] gate_orchestrator_combined.json -> adapter-v15')
except Exception as e:
    print(f'[upload] failed (non-critical): {e}')
print('\nCOMBINED_DONE')

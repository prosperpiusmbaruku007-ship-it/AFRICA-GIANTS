# -*- coding: utf-8 -*-
"""Step 4 — test chike/extraction.py against the reviewed 205-example slot-extraction
stress test, USING THE REAL v15 MODEL on Kaggle (GPU). Prepare-only: the founder runs
this on Kaggle; it is never run locally (needs the 8B in 4-bit, same as eval.py).

WHY DIRECT-TO-EXTRACTOR (not through the orchestrator): the orchestrator's route() only
sends keyword+DIGIT sub-questions to the compute path, so word-form-number questions
("milioni mia mbili na hamsini") and no-digit vague questions ("wafanyakazi wachache")
would never reach extraction. To test EXTRACTION itself we call SlotExtractor.extract()
directly on every entry, with the computation_type derived from the subdomain. Routing is
a separate concern (Step 5/6).

HOW TO RUN (Kaggle notebook, GPU ON):
    import requests
    exec(requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                      'AFRICA-GIANTS/main/kaggle/extraction_stress_test.py', timeout=10).text)
    # then:  run_stage('sample')   # ~18 entries spanning subdomains+categories
    #  then: run_stage('full')     # all 205

PREREQS:
  - Kaggle GPU ON; Kaggle secret AFRICA_GIANTS (HF token — model weights + config).
  - The reviewed dataset is GITIGNORED and unmerged, so it is NOT on GitHub. Make it
    available to Kaggle in ONE of these (the loader checks in this order):
      (1) local repo path (if the clone contains it),
      (2) a Kaggle input file  /kaggle/input/**/slot_extraction_stress_test_001_reviewed.jsonl
      (3) HF dataset repo prospAprospA007/africa-giants-dataset (upload it there first).

GRADING (per entry): the extractor decides EXTRACT (all required fields usable) or
CLARIFY (any required field missing/low). Each failure_category has an EXPECTED decision;
we report:
  correct_extract | correct_clarify | DANGEROUS_wrong_extract (should clarify but extracted)
  | over_clarify (should extract but clarified — safe miss).
The per-category expected decision is a heuristic; the reviewed entry's expected_behavior
prose remains the ground truth for any manual follow-up.
"""
import os, sys, json, glob, time, subprocess
from collections import Counter, defaultdict

import requests

REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
DATASET_REPO = 'prospAprospA007/africa-giants-dataset'
REVIEWED_FILE = 'slot_extraction_stress_test_001_reviewed.jsonl'

# ── AUTH ────────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    hf_token = kaggle_secrets.UserSecretsClient().get_secret('AFRICA_GIANTS')
except Exception as e:
    raise RuntimeError('run on Kaggle with AFRICA_GIANTS secret attached') from e
assert hf_token, 'AFRICA_GIANTS secret empty'
os.environ['HF_TOKEN'] = hf_token
print(f'[auth] AFRICA_GIANTS ({hf_token[:6]}...) OK')

# ── GET chike/ PACKAGE (git clone — extraction imports swahili_numbers etc.) ─────
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

# ── LOAD THE REVIEWED 205 (local -> kaggle input -> HF dataset repo) ─────────────
def _load_reviewed():
    for p in [os.path.join(_CLONE, 'data/reviewed', REVIEWED_FILE),
              *glob.glob(f'/kaggle/input/**/{REVIEWED_FILE}', recursive=True)]:
        if os.path.exists(p):
            print(f'[data] reviewed set from {p}')
            return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
    from huggingface_hub import hf_hub_download
    p = hf_hub_download(repo_id=DATASET_REPO, filename=REVIEWED_FILE,
                        repo_type='dataset', token=hf_token)
    print(f'[data] reviewed set from HF {DATASET_REPO}/{REVIEWED_FILE}')
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]

ENTRIES = _load_reviewed()
assert len(ENTRIES) == 205, f'expected 205 got {len(ENTRIES)}'
print(f'[data] {len(ENTRIES)} reviewed stress-test entries')

# ── CONFIG + MODEL (identical 4-bit load to eval_orchestrator.py) ────────────────
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
    """In-process v15 backend, byte-identical load to eval_orchestrator.py."""
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
                **inp, max_new_tokens=(params or {}).get('max_new_tokens', 160),
                do_sample=False, temperature=1.0, repetition_penalty=1.1, no_repeat_ngram_size=0,
                stopping_criteria=StoppingCriteriaList([_Stop(self.tok, STOP)]),
                eos_token_id=self.tok.eos_token_id, pad_token_id=self.tok.pad_token_id)
        return self.tok.decode(out[0][inp['input_ids'].shape[1]:], skip_special_tokens=True).strip()


# ── SUBDOMAIN -> computation_type ; per-category EXPECTED decision ───────────────
SUBDOMAIN_CTYPE = {
    'sdl_compliance': 'sdl', 'nssf_contributions': 'nssf',
    'wcf_compliance': 'wcf', 'paye': 'paye', 'paye_compliance': 'paye',
}
# non-compute subdomains (vat/brela/osha/gn487a): no rules engine — test the ambiguity
# vetoes with a generic single-amount slot, computation_type=None.
GENERIC_REQUIRED = ('gross_monthly_payroll',)

SHOULD_CLARIFY = {'vague_quantity', 'casual_slang', 'missing_antecedent',
                  'wrong_calculation_number', 'gross_net_allowance'}
SHOULD_EXTRACT = {'swahili_number_words', 'period_conversion',
                  'aggregate_vs_per_person', 'non_uniform_figures'}
# compound_question is mixed (two domains) -> reported in its own bucket, ungraded.


def _ctype_and_required(entry):
    ct = SUBDOMAIN_CTYPE.get(entry['subdomain'])
    if ct:
        return ct, REQUIRED_FIELDS[ct]
    return None, GENERIC_REQUIRED


def _grade(entry, usable):
    cat = entry['failure_category']
    if cat == 'compound_question':
        # A compound question mixes a computation with a separate (often legal) part;
        # the safe behaviour is to DEFER — clarify rather than silently compute one part
        # and drop the other. So a usable HIGH-confidence extraction here is NOT "ungraded":
        # it means a field was populated (e.g. '487' misread from 'GN487A') and is about to
        # feed the rules engine. That is a DANGEROUS wrong extract, not an exemption.
        return 'DANGEROUS_wrong_extract' if usable else 'compound'
    exp = 'clarify' if cat in SHOULD_CLARIFY else 'extract' if cat in SHOULD_EXTRACT else 'other'
    if exp == 'extract':
        return 'correct_extract' if usable else 'over_clarify'
    if exp == 'clarify':
        return 'DANGEROUS_wrong_extract' if usable else 'correct_clarify'
    return 'other'


_backend = None
def _get_backend():
    global _backend
    if _backend is None:
        _backend = KaggleDirectBackend()
    return _backend


SAMPLE_IDS = ['extract_001', 'extract_007', 'extract_011', 'extract_014', 'extract_006',
              'extract_025', 'extract_027', 'extract_041', 'extract_047', 'extract_062',
              'extract_074', 'extract_088', 'extract_120', 'extract_131', 'extract_157',
              'extract_164', 'extract_190', 'extract_003']


def run_stage(stage='sample'):
    be = _get_backend()
    ext = SlotExtractor(be)
    by_id = {e['id']: e for e in ENTRIES}
    items = [by_id[i] for i in SAMPLE_IDS] if stage == 'sample' else ENTRIES
    print(f'\n[{stage}] {len(items)} entries through real extraction ...')
    rows, t0 = [], time.time()
    for i, e in enumerate(items):
        ct, required = _ctype_and_required(e)
        try:
            xr = ext.extract(e['question_sw'], required, ct)
            usable = xr.usable(required)
            fields = {n: {'value': str(f.value), 'confidence': f.confidence.value, 'reason': f.reason}
                      for n, f in xr.fields.items()}
            reasons = xr.clarification_reasons(required)
        except Exception as ex:
            usable, fields, reasons = False, {}, [f'ERROR: {ex}']
        grade = _grade(e, usable)
        rows.append({'id': e['id'], 'subdomain': e['subdomain'],
                     'failure_category': e['failure_category'], 'computation_type': ct,
                     'question_sw': e['question_sw'], 'decision': 'EXTRACT' if usable else 'CLARIFY',
                     'grade': grade, 'fields': fields, 'clarification_reasons': reasons})
        if stage == 'sample':
            print(f"\n{e['id']} [{e['subdomain']}/{e['failure_category']}] ct={ct}")
            print(f"  Q: {e['question_sw']}")
            print(f"  -> {rows[-1]['decision']}  grade={grade}")
            print(f"  fields={fields}")
            if reasons:
                print(f"  clarify_reasons={reasons}")
        elif (i + 1) % 40 == 0:
            print(f'   ...{i+1}/{len(items)} ({time.time()-t0:.0f}s)')

    grades = Counter(r['grade'] for r in rows)
    by_cat = defaultdict(Counter)
    for r in rows:
        by_cat[r['failure_category']][r['grade']] += 1
    print('\n' + '=' * 60)
    print(f'[{stage}] grade breakdown: {dict(grades)}')
    print(f'  DANGEROUS (should clarify but extracted): {grades.get("DANGEROUS_wrong_extract", 0)}')
    print(f'  correct_extract={grades.get("correct_extract",0)}  correct_clarify={grades.get("correct_clarify",0)}')
    print(f'  over_clarify(safe miss)={grades.get("over_clarify",0)}  compound(ungraded)={grades.get("compound",0)}')
    print('\n  by failure_category:')
    for cat in sorted(by_cat):
        print(f'    {cat:26} {dict(by_cat[cat])}')

    out = {'stage': stage, 'commit': _sha, 'n': len(rows), 'grades': dict(grades),
           'by_category': {k: dict(v) for k, v in by_cat.items()}, 'rows': rows}
    path = f'/kaggle/working/extraction_stress_{stage}.json'
    json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\n[save] {path}')
    try:
        from huggingface_hub import HfApi
        HfApi().upload_file(path_or_fileobj=path, path_in_repo=f'extraction_stress_{stage}.json',
                            repo_id='prospAprospA007/africa-giants-adapter-v15', repo_type='model',
                            token=hf_token, commit_message=f'extraction stress test ({stage}) — {dict(grades)}')
        print(f'[upload] extraction_stress_{stage}.json -> adapter-v15')
    except Exception as ex:
        print(f'[upload] failed (non-critical): {ex}')
    print(f'\n{stage.upper()}_DONE')
    return out


print('\nReady. Run:  run_stage("sample")   then, once it looks right:  run_stage("full")')

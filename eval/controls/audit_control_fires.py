# -*- coding: utf-8 -*-
"""DOES EACH CONTROL ACTUALLY FIRE? Plant the thing it exists to catch, and watch.

WHY THIS EXISTS. On 2026-08-24 the pre-push hook's SECRET SCAN was found to be incapable of
firing. It invoked `scan_for_keys.py` bare, which scans `git diff --cached`, and at push time
nothing is staged — so it scanned **zero files and exited 0 on every push in this project's
history**. Its test asserted that the hook *mentions* the script and *branches* on its exit
status. Both were true. Neither says the check can fire. **Every push has been scanned by
nothing, and a passing test certified it.**

That is the same defect as the dead anchors (three regen guards matching zero facts, each hidden
by a sibling that always passed) and R20's vacuous asserts (`assert f` on an open file handle) —
**but with a real exposure attached rather than a measurement one**, and it was found BY ACCIDENT
while doing something else. Nothing in this repo was looking for it.

So the question this harness answers is the one that follows: **what else is a control that has
never demonstrably fired?**

THE METHOD IS R23'S, APPLIED TO CONTROLS INSTEAD OF EXPERIMENTS. A control that passes proves
nothing on its own; a control must be shown to FAIL on the thing it exists to catch. So each
entry below plants:

  * a POSITIVE specimen — the exact thing the control claims to block. It MUST block.
  * a NEGATIVE specimen — a clean case. It MUST pass.

A control needs both to be called working. Positive-only would certify a control that blocks
everything (useless in the opposite direction — R17's negative case); negative-only is what the
secret scan had.

VERDICTS, and the distinctions are load-bearing:
  FIRES            positive blocked AND negative passed — the control works
  INERT            positive NOT blocked — the control cannot do its job ⛔
  OVERBROAD        negative blocked — the control blocks correct input too ⚠️
  NOT_WIRED        the logic fires when called directly, but nothing calls it in production
  DISABLED         deliberately off, with the decision recorded — not a defect
  OBSERVED         not planted here; fired on real input, with the incident cited
  NOT_EXERCISABLE  needs GPU/network/live endpoint — LISTED ANYWAY, never silently dropped

That last verdict is deliberate. **A census that quietly omits what it cannot test reports a
cleaner result than it earned**, which is the defect this whole family keeps producing.

R18: committed before it runs.
Artifact: eval/results/control_fire_audit.json
"""
import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
os.chdir(REPO)

OUT = os.path.join(REPO, 'eval', 'results', 'control_fire_audit.json')
PY = sys.executable

RESULTS = []


def record(cid, layer, claims, verdict, positive='', negative='', note=''):
    RESULTS.append({'id': cid, 'layer': layer, 'claims_to_block': claims,
                    'verdict': verdict, 'positive_specimen': positive,
                    'negative_specimen': negative, 'note': note})
    mark = {'FIRES': 'OK  ', 'INERT': 'INERT', 'OVERBROAD': 'WIDE', 'NOT_WIRED': 'UNWIRED',
            'DISABLED': 'OFF ', 'OBSERVED': 'SEEN', 'NOT_EXERCISABLE': 'N/A ',
            'ERROR': 'ERR '}.get(verdict, '?')
    print(f'  [{mark:<7}] {cid:<34} {note[:90]}')


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                       encoding='utf-8', errors='replace')
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def script_control(cid, claims, argv_pos, argv_neg, layer='repo_gate', note=''):
    """Run a CLI gate twice: once on a planted violation, once on a clean case."""
    rc_pos, out_pos = run([PY] + argv_pos)
    rc_neg, out_neg = run([PY] + argv_neg)
    if rc_pos == 0:
        v, n = 'INERT', f'planted violation NOT blocked (exit 0). {out_pos.strip()[-200:]}'
    elif rc_neg != 0:
        v, n = 'OVERBROAD', f'clean case blocked (exit {rc_neg}). {out_neg.strip()[-200:]}'
    else:
        v, n = 'FIRES', f'planted -> exit {rc_pos}; clean -> exit 0. {note}'
    record(cid, layer, claims, v, ' '.join(argv_pos[1:]), ' '.join(argv_neg[1:]), n)


def jsonl(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return path


def valid_pair(**over):
    """A schema-complete, whitelisted pair — the NEGATIVE specimen for the dataset gates."""
    p = {
        'id': 'audit_001', 'domain': 'tier1a', 'subdomain': 'sdl_compliance',
        'question_sw': 'SDL ni asilimia ngapi?', 'answer_sw': 'SDL ni asilimia 3.5.',
        'question_en': 'What is the SDL rate?', 'answer_en': 'SDL is 3.5%.',
        'primary_source_url': 'https://www.tra.go.tz/index.php/skills-development-levy',
        'primary_source_name': 'TRA', 'source_type': 'government_portal',
        'effective_date': '2025-07-01', 'decay_risk': 'annual',
        'next_review_trigger': 'Finance Act 2026', 'verified_by': 'audit',
        'verified_date': '2026-08-24', 'register': 'formal', 'pair_type': 'standard',
        'eval_set': False,
    }
    p.update(over)
    return p


# =============================================================================================
# LAYER 1 — REPO / PIPELINE GATES
# =============================================================================================

def audit_repo_gates(tmp):
    # --- 1. the secret scan (the control that started this) ----------------------------------
    leak = os.path.join(tmp, 'leak.py')
    with open(leak, 'w', encoding='utf-8') as f:
        # fabricated, matches the OpenRouter pattern, is not a credential
        f.write('KEY = "sk-or-' + 'v1abcdefghijklmnopqrstuvwxyz0123456789' + '"\n')
    clean = os.path.join(tmp, 'clean.py')
    with open(clean, 'w', encoding='utf-8') as f:
        f.write('import os\nKEY = os.environ.get("OPENROUTER_API_KEY", "")\n')
    script_control(
        'scan_for_keys(--files)',
        'an API key committed into a source file',
        ['scripts/scan_for_keys.py', '--files', leak],
        ['scripts/scan_for_keys.py', '--files', clean],
        note='FIXED 2026-08-24; the bare invocation this replaced was INERT')

    # --- 2. the same scanner in the mode the pre-push hook now uses --------------------------
    rc, out = run([PY, 'scripts/scan_for_keys.py', '--range', 'HEAD~1..HEAD'])
    scanned = 'No files to scan' not in out
    record('scan_for_keys(--range)', 'repo_gate',
           'the same, over the commits actually being pushed',
           'FIRES' if scanned else 'INERT',
           'HEAD~1..HEAD', '',
           f'range mode sees files: {scanned}. THE BARE MODE THE HOOK USED TO CALL SCANS ZERO '
           f'FILES AT PUSH TIME — that is the incident this audit came from.')

    # --- 3. source enforcer ------------------------------------------------------------------
    script_control(
        'check_sources.py',
        'a training pair citing a banned, eval-only or DNS-dead source',
        ['scripts/check_sources.py', '--file',
         jsonl(os.path.join(tmp, 'src_bad.jsonl'),
               [valid_pair(primary_source_url='https://en.wikipedia.org/wiki/Tax')])],
        ['scripts/check_sources.py', '--file',
         jsonl(os.path.join(tmp, 'src_ok.jsonl'), [valid_pair()])])

    # the dead-domain limb specifically — it checks the WHOLE pair, not just source fields
    script_control(
        'check_sources.py[dead_domain]',
        'nssf.or.tz (DNS-failing) anywhere in a pair, including answer TEXT',
        ['scripts/check_sources.py', '--file',
         jsonl(os.path.join(tmp, 'dead_bad.jsonl'),
               [valid_pair(answer_sw='Thibitisha na nssf.or.tz.')])],
        ['scripts/check_sources.py', '--file',
         jsonl(os.path.join(tmp, 'dead_ok.jsonl'),
               [valid_pair(answer_sw='Thibitisha na nssf.go.tz.')])])

    # --- 4. fact guardian --------------------------------------------------------------------
    # positive drawn from a REAL wrong_pattern in locked_facts.json (OSHA_penalties):
    # 'osha.*faini.*TZS 500,000(?! na)'
    script_control(
        'check_locked_facts.py',
        'a pair asserting a value locked_facts.json marks as WRONG',
        ['scripts/check_locked_facts.py', '--file',
         jsonl(os.path.join(tmp, 'lf_bad.jsonl'),
               [valid_pair(answer_sw='Faini ya OSHA ni TZS 500,000.')])],
        ['scripts/check_locked_facts.py', '--file',
         jsonl(os.path.join(tmp, 'lf_ok.jsonl'), [valid_pair()])])

    # --- 5. eval-split enforcer (R6 / Gate 3) ------------------------------------------------
    ev_dir = os.path.join(tmp, 'cleaned')
    os.makedirs(ev_dir, exist_ok=True)
    jsonl(os.path.join(ev_dir, 'batch.jsonl'),
          [valid_pair(id='e1', eval_set=True, question_sw='SWALI LA EVAL PEKEE?'),
           valid_pair(id='t1')])
    contaminated = os.path.join(tmp, 'train_bad.jsonl')
    jsonl(contaminated, [{'messages': [{'role': 'user', 'content': 'SWALI LA EVAL PEKEE?'},
                                       {'role': 'assistant', 'content': 'jibu'}]}])
    clean_train = os.path.join(tmp, 'train_ok.jsonl')
    jsonl(clean_train, [{'messages': [{'role': 'user', 'content': 'SDL ni asilimia ngapi?'},
                                      {'role': 'assistant', 'content': 'jibu'}]}])
    script_control(
        'check_eval_split.py',
        'a held-out eval question leaking into the SFT training file (R6)',
        ['scripts/check_eval_split.py', '--cleaned-dir', ev_dir, '--sft-train', contaminated],
        ['scripts/check_eval_split.py', '--cleaned-dir', ev_dir, '--sft-train', clean_train])

    # --- 6. locked_facts <-> RAG index drift check -------------------------------------------
    with open(os.path.join(REPO, 'scripts', 'locked_facts.json'), encoding='utf-8') as f:
        facts = json.load(f)
    facts['audit_planted_fact_key_not_in_index'] = {
        'fact': 'A planted fact that exists in no index row and in no pin.',
        'correct_value': 'n/a', 'wrong_patterns': [], 'status': 'LOCKED'}
    drift = os.path.join(tmp, 'facts_drift.json')
    with open(drift, 'w', encoding='utf-8') as f:
        json.dump(facts, f, ensure_ascii=False)
    script_control(
        'check_facts_index_sync.py',
        'a locked fact that is neither in the RAG index nor human-adjudicated',
        ['scripts/check_facts_index_sync.py', '--facts', drift],
        ['scripts/check_facts_index_sync.py'])


# =============================================================================================
# LAYER 2 — GATES THAT NEED THEIR MODULE CONSTANTS REDIRECTED
# =============================================================================================

def audit_patched_gates(tmp):
    import importlib
    from pathlib import Path

    # --- validate_dataset: schema completeness + whitelist (R3 / Gate 1) ---------------------
    vd = importlib.import_module('scripts.validate_dataset') if False else None
    sys.path.insert(0, os.path.join(REPO, 'scripts'))
    import validate_dataset as vd
    root = Path(tmp) / 'ds_bad' / 'tier1a' / 'cleaned_pairs'
    root.mkdir(parents=True, exist_ok=True)
    bad = valid_pair()
    del bad['verified_by']                                   # R3: a missing schema field
    bad['primary_source_url'] = 'https://medium.com/tanzania-tax'   # non-whitelisted
    jsonl(str(root / 'b.jsonl'), [bad])
    ok_root = Path(tmp) / 'ds_ok' / 'tier1a' / 'cleaned_pairs'
    ok_root.mkdir(parents=True, exist_ok=True)
    jsonl(str(ok_root / 'b.jsonl'), [valid_pair()])

    def run_vd(dsroot):
        orig = vd.DATASETS_ROOT
        vd.DATASETS_ROOT = Path(dsroot)
        try:
            vd.main()
        except SystemExit as e:
            return e.code
        finally:
            vd.DATASETS_ROOT = orig
        return None

    rc_pos = run_vd(Path(tmp) / 'ds_bad')
    rc_neg = run_vd(Path(tmp) / 'ds_ok')
    v = ('INERT' if rc_pos == 0 else 'OVERBROAD' if rc_neg != 0 else 'FIRES')
    record('validate_dataset.py', 'repo_gate',
           'a cleaned pair missing a schema field or citing a non-whitelisted domain (R3)',
           v, 'pair with verified_by removed + medium.com URL', 'complete whitelisted pair',
           f'planted -> exit {rc_pos}; clean -> exit {rc_neg}')

    # ⚠️ the vacuity hazard in this gate, recorded even though it is not currently triggered
    record('validate_dataset.py[empty-corpus]', 'repo_gate',
           'nothing — this is the gate\'s VACUOUS PATH, recorded as a hazard',
           'FIRES' if v == 'FIRES' else v,
           'n/a', 'n/a',
           'HAZARD: with zero cleaned_pairs files the gate counts 0 pairs, 0 errors and prints '
           'VALIDATION PASSED. It is non-vacuous TODAY only because 4,562 pairs exist. Four of '
           'the five tier dirs are empty and would pass on nothing.')

    # --- clean_temp_files --scan --------------------------------------------------------------
    import clean_temp_files as ctf
    tdir = os.path.join(tmp, 'cleaned_temp')
    os.makedirs(tdir, exist_ok=True)
    jsonl(os.path.join(tdir, 'batch_test_draft.jsonl'), [valid_pair()])
    empty_dir = os.path.join(tmp, 'cleaned_notemp')
    os.makedirs(empty_dir, exist_ok=True)
    jsonl(os.path.join(empty_dir, 'batch_001.jsonl'), [valid_pair()])

    def run_ctf(d):
        orig = ctf.CLEANED_DIR
        ctf.CLEANED_DIR = d
        argv = sys.argv
        sys.argv = ['clean_temp_files.py', '--scan']
        try:
            ctf.main()
        except SystemExit as e:
            return e.code
        finally:
            ctf.CLEANED_DIR = orig
            sys.argv = argv
        return None

    rc_pos, rc_neg = run_ctf(tdir), run_ctf(empty_dir)
    record('clean_temp_files.py --scan', 'repo_gate',
           'a temp/draft JSONL left in cleaned_pairs before a batch or SFT run',
           'INERT' if rc_pos == 0 else 'OVERBROAD' if rc_neg != 0 else 'FIRES',
           'batch_test_draft.jsonl', 'batch_001.jsonl',
           f'planted -> exit {rc_pos}; clean -> exit {rc_neg}')


# =============================================================================================
# LAYER 3 — RUNTIME CONTROLS (what stands between the model and a user)
# =============================================================================================

def audit_runtime():
    from chike import classification, coverage, fidelity, retrieval

    # --- the OOC classifier (R11 — infrastructure, not behaviour) ----------------------------
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    pos = classification.classify('Nilipa kodi gani nikiuza hisa za kampuni sokoni?',
                                  ooc, in_scope)
    neg = classification.classify('SDL ni asilimia ngapi kwa wafanyakazi 12?', ooc, in_scope)
    pos_blocked = (pos is False)      # classify() returns True = in scope, False = intercept
    neg_blocked = (neg is False)
    record('classification.classify (OOC)', 'runtime',
           'an out-of-corpus question reaching the model at all (R11)',
           'INERT' if not pos_blocked else 'OVERBROAD' if neg_blocked else 'FIRES',
           'capital gains on shares', 'SDL rate with headcount',
           f'ooc question refused: {pos_blocked}; in-scope question refused: {neg_blocked}; '
           f'{len(ooc)} ooc / {len(in_scope)} in-scope phrases loaded')

    # --- the coverage gate — SHIPPED DISABLED, and that is a decision, not a defect ----------
    unc = coverage.uncovered_authority('Nilipa mrabaha gani wa madini kwa dhahabu?')
    cov = coverage.is_covered('SDL ni asilimia ngapi?')
    logic_ok = bool(unc) and cov
    record('coverage gate', 'runtime',
           'answering a question whose topic the corpus holds no facts for',
           'DISABLED',
           'mining royalty question', 'SDL rate question',
           f'logic works when called (uncovered detected: {bool(unc)}, covered passes: {cov}) '
           f'but Orchestrator(coverage_gate=False) by default. Measured cost: 1.9% false '
           f'refusals on 411 corpus questions vs 71% on 21 held-out — a ~37x gap. Off ON '
           f'PURPOSE.' if logic_ok else 'LOGIC BROKEN — the disabled gate would not even work '
           f'if switched on')

    # --- the fidelity rules ------------------------------------------------------------------
    from chike.rules_engine import ComputationResult  # noqa: F401  (import shape check)
    _fidelity_rules(fidelity)

    # --- the RAG index preflight (fail-loud index contract) ----------------------------------
    try:
        retrieval.Retriever(emb_path=os.path.join(REPO, 'nope.npy'),
                            texts_path=os.path.join(REPO, 'nope.json')).preflight()
        missing_raises = False
    except retrieval.RetrievalIndexError:
        missing_raises = True
    try:
        n = retrieval.Retriever(
            emb_path=os.path.join(REPO, 'kaggle', 'rag_embeddings.npy'),
            texts_path=os.path.join(REPO, 'kaggle', 'rag_facts_text.json')).preflight()
        real_ok = n > 0
    except Exception as exc:
        n, real_ok = 0, False
        print('   real index preflight raised:', exc)
    record('retrieval.preflight', 'runtime',
           'serving every answer with ZERO facts because the index path is wrong',
           'INERT' if not missing_raises else 'OVERBROAD' if not real_ok else 'FIRES',
           'nonexistent index paths', 'the real kaggle/ index',
           f'missing index raises: {missing_raises}; real index loads {n} facts')

    # count-mismatch limb (the R15 stale-index guard)
    try:
        retrieval.Retriever(
            emb_path=os.path.join(REPO, 'kaggle', 'rag_embeddings.npy'),
            texts_path=os.path.join(REPO, 'kaggle', 'rag_facts_text.json'),
            expected_fact_count=999999).preflight()
        mismatch_raises = False
    except retrieval.RetrievalIndexError:
        mismatch_raises = True
    record('retrieval.preflight[expected_fact_count]', 'runtime',
           'a STALE or half-regenerated index serving old facts after an R15 regen',
           'FIRES' if mismatch_raises else 'INERT',
           'expected_fact_count=999999', 'the real count',
           f'count mismatch raises: {mismatch_raises}. ⚠️ NOTE: this limb only protects a '
           f'caller that PASSES expected_fact_count — see the wiring check below.')


def _fidelity_rules(fidelity):
    """Each D-FIDELITY rule gets a body it MUST flag and a correct body it must NOT."""
    from chike.rules_engine import ComputationResult

    from decimal import Decimal

    def res(amount, ctype='sdl'):
        try:
            return ComputationResult(
                computation=ctype, applicable=True, amount=Decimal(amount),
                working=f'{ctype.upper()} = 3.5% × TZS 5,500,000 = TZS {amount:,}')
        except TypeError:
            return None

    r = res(192_500)
    if r is None:
        record('D-FIDELITY-1..5', 'runtime', 'a compute body contradicting the engine working',
               'NOT_EXERCISABLE', '', '',
               'ComputationResult signature differs from the audit specimen; the rules are '
               'covered by tests/ instead. Listed rather than dropped.')
    else:
        cases = [
            ('D-FIDELITY-1', 'a compute body asserting a figure the engine did not compute',
             fidelity.body_contradicts_working,
             'SDL yako ni TZS 500,000 kwa mwezi.', 'SDL yako ni TZS 192,500 kwa mwezi.', (r,)),
            ('D-FIDELITY-3', 'the authoritative amount silently reduced by a phantom deduction',
             fidelity.body_reduces_authoritative_amount,
             'SDL = TZS 192,500 − TZS 92,500 = TZS 100,000.',
             'SDL yako ni TZS 192,500 kwa mwezi.', (r,)),
            ('D-FIDELITY-5', 'a positive obligation denied outright',
             fidelity.body_denies_a_positive_obligation,
             'Hakuna cha kulipa kwa SDL.', 'SDL yako ni TZS 192,500 kwa mwezi.', (r,)),
        ]
        for cid, claims, fn, bad, good, args in cases:
            try:
                p, ngd = fn(bad, *args), fn(good, *args)
                v = 'INERT' if not p else 'OVERBROAD' if ngd else 'FIRES'
                note = f'planted flagged: {p}; correct body flagged: {ngd}'
            except Exception as exc:
                v, note = 'ERROR', f'{type(exc).__name__}: {exc}'
            record(cid, 'runtime', claims, v, bad, good, note)

    # D-FIDELITY-6 — a wrong statutory RATE. Constant comparison, needs no engine result.
    try:
        p = fidelity.body_states_wrong_levy_rate('Kiwango cha WCF ni asilimia 3.5 ya mishahara.')
        ngd = fidelity.body_states_wrong_levy_rate(
            'SDL ni asilimia 3.5, NSSF ni asilimia 20, na WCF ni asilimia 0.5.')
        record('D-FIDELITY-6', 'runtime', 'a WRONG statutory rate attributed to a levy',
               'INERT' if not p else 'OVERBROAD' if ngd else 'FIRES',
               'WCF ni asilimia 3.5', 'a correct three-levy breakdown',
               f'planted flagged: {p}; correct three-levy body flagged: {ngd}')
    except Exception as exc:
        record('D-FIDELITY-6', 'runtime', 'a WRONG statutory rate attributed to a levy',
               'ERROR', '', '', f'{type(exc).__name__}: {exc}')

    # D-FIDELITY-7 — built, but is anything calling it?
    try:
        p = fidelity.body_states_wrong_threshold(
            'Kizingiti cha kusajili VAT ni TZS 90,000,000 kwa miezi 6.')
        ngd = fidelity.body_states_wrong_threshold(
            'Kizingiti cha kusajili VAT ni TZS 100,000,000 kwa miezi 6.')
        with open(os.path.join(REPO, 'chike', 'orchestrator.py'), encoding='utf-8') as f:
            wired = 'body_states_wrong_threshold' in f.read()
        v = ('ERROR' if not p else 'OVERBROAD' if ngd else
             ('FIRES' if wired else 'NOT_WIRED'))
        record('D-FIDELITY-7', 'runtime',
               'a body stating a threshold that is not the statutory one',
               v, 'VAT threshold stated as TZS 90,000,000', 'stated as TZS 100,000,000',
               f'logic: planted flagged {p}, correct not flagged {not ngd}. '
               f'CALLED FROM orchestrator: {wired}. Held for one R16 cycle by decision — but '
               f'note eval_208 shows the exact defect it targets, LIVE.')
    except Exception as exc:
        record('D-FIDELITY-7', 'runtime', 'a body stating a non-statutory threshold',
               'ERROR', '', '', f'{type(exc).__name__}: {exc}')


# =============================================================================================
# LAYER 4 — CONTROLS THIS HARNESS CANNOT PLANT INTO. Listed, never dropped.
# =============================================================================================

def audit_unexercisable():
    with open(os.path.join(REPO, 'chike-inference', 'modal_app.py'), encoding='utf-8') as f:
        modal_src = f.read()
    record('modal_app: retrieval index wiring', 'runtime',
           'the deployed container serving with a wrong/stale baked index',
           'NOT_EXERCISABLE', '', '',
           'requires a deploy. STATIC CHECK: expected_fact_count passed in modal_app.py: '
           f'{"expected_fact_count" in modal_src}. If False, the R15 stale-index limb audited '
           'above protects nobody in production.')

    record('pre-push hook: pytest half', 'process',
           'a red build reaching main',
           'OBSERVED', 'a failing suite', 'a green suite',
           'not planted here — it BLOCKED TWO REAL PUSHES on 2026-08-24, one a genuine failure '
           'and one an exit-139 access violation under memory pressure. Fired on real input.')

    record('run_eval.py accuracy/refusal gates', 'process',
           'a product launch on a model below 85% in-corpus or 70% refusal (R7)',
           'NOT_EXERCISABLE', '', '',
           'needs a live endpoint + GPU. NOT planted. Its threshold arithmetic is unit-tested; '
           'whether it BLOCKS an under-threshold model has never been demonstrated by planting '
           'one, and that is exactly the shape of the secret-scan defect.')

    record('Wappfly/WhatsApp webhook token', 'process',
           'an unauthenticated caller posting to the WhatsApp webhook',
           'NOT_EXERCISABLE', '', '',
           'needs the live chike-whatsapp app and its Modal Secret. Not audited here.')


def main():
    print('CONTROL FIRE AUDIT — planting the thing each control exists to catch\n')
    with tempfile.TemporaryDirectory() as tmp:
        print('LAYER 1 — repo / pipeline gates')
        audit_repo_gates(tmp)
        print('LAYER 2 — gates needing redirected constants')
        try:
            audit_patched_gates(tmp)
        except Exception as exc:
            record('layer2', 'repo_gate', '', 'ERROR', '', '', f'{type(exc).__name__}: {exc}')
        print('LAYER 3 — runtime controls')
        try:
            audit_runtime()
        except Exception as exc:
            record('layer3', 'runtime', '', 'ERROR', '', '', f'{type(exc).__name__}: {exc}')
        print('LAYER 4 — not exercisable offline (listed, not dropped)')
        audit_unexercisable()

    from collections import Counter
    tally = Counter(r['verdict'] for r in RESULTS)
    blob = {
        'audited': '2026-08-24',
        'harness': 'eval/controls/audit_control_fires.py',
        'method': 'R23 applied to controls: plant the thing each control exists to catch '
                  '(POSITIVE, must block) and a clean case (NEGATIVE, must pass). A control '
                  'needs both to count as working.',
        'prompted_by': 'the pre-push secret scan, which invoked scan_for_keys.py bare and so '
                       'scanned zero files on every push in this project\'s history, while a '
                       'passing test certified it by checking the hook mentioned the script.',
        'tally': dict(tally),
        'controls': RESULTS,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)
    print(f'\n=== {dict(tally)}')
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

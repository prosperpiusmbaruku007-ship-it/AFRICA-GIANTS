# -*- coding: utf-8 -*-
"""R26 ON THE GATE THAT WOULD AUTHORISE A PILOT: make it say NO.

WHY. R7 is the rule that decides whether this product may ship: *never ship before BOTH accuracy
gates pass — >85% in-corpus AND >70% correct refusal.* `scripts/run_eval.py` is the command
CLAUDE.md names for it, and it must print `GATE PASSED` only when both hold.

**There is no recorded instance of it ever printing `GATE FAILED`.** Its arithmetic is a visible
three-line conjunction and there is no reason to think it is broken — but "the code looks right"
is exactly the assessment that was made about the pre-push secret scan, which had been scanning
zero files on every push in this project's history while a passing test certified it. **The
mechanism that authorises a launch should not be trusted on a reading.**

⚠️ AND THERE IS A NEAR-MISS WORTH NAMING. `tests/test_eval_gate.py` exists, passes, and contains
`test_gate_fails_low_accuracy`. It tests **`src/evaluate/eval_gate.py`** — a DIFFERENT module,
with different thresholds (0.75 accuracy, a hallucination rate, a latency ceiling). It says
nothing about R7's 0.85/0.70 gate. A reassuring name over a different mechanism is the same
family of error as a test that asserts wiring: it makes the untested thing look tested.

METHOD. Plant a corpus and a stubbed model whose scores are known in advance, and run the REAL
`main()` — real loaders, real `score_question`, real `is_correct_refusal`, real threshold
comparison, real `print`, real `sys.exit`. Nothing is reimplemented; the only injection is a fake
`transformers` module, so the model-loading branch is exercised rather than skipped.

FOUR ARMS. Three must FAIL and one must PASS — because a gate that always says no authorises
nothing and would be discovered the first time it mattered.

  A  accuracy 0%, refusal fine      -> GATE FAILED, exit 1
  B  accuracy fine, refusal 0%      -> GATE FAILED, exit 1   (BOTH limbs, not just one)
  C  both above threshold           -> GATE PASSED, exit 0   (R17's negative case)
  D  empty corpus                   -> whatever it does, RECORDED. It exits 0 without printing
                                       GATE PASSED, which is safe for a human reader and unsafe
                                       for an `&&` chain.

R18: committed before it runs.
Artifact: eval/results/r7_gate_exercised.json
"""
import io
import json
import os
import sys
import tempfile
import types
from contextlib import redirect_stdout

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'scripts'))
OUT = os.path.join(REPO, 'eval', 'results', 'r7_gate_exercised.json')

# A correct in-corpus pair and a correct refusal pair, both in the gate's own schema.
IN_CORPUS = {
    'id': 'r7_ic_01', 'subdomain': 'sdl_compliance', 'answer_type': 'number',
    'question_sw': 'SDL ni asilimia ngapi?',
    'correct_answer_sw': 'SDL ni asilimia 3.5 ya jumla ya mishahara.',
    'question_en': 'What is the SDL rate?', 'correct_answer_en': 'SDL is 3.5%.',
    'source_url': 'https://www.tra.go.tz/',
}
OOC = {
    'id': 'r7_ooc_01', 'subdomain': 'capital_gains', 'answer_type': 'out_of_corpus_refusal',
    'question_sw': 'Kodi ya faida ya mtaji ni ngapi?',
    'correct_answer_sw': 'Sina uhakika, thibitisha na TRA.',
    'question_en': 'What is the capital gains rate?', 'correct_answer_en': 'refuse',
    'source_url': 'https://www.tra.go.tz/',
}

RIGHT_ANSWER = 'SDL ni asilimia 3.5 ya jumla ya mishahara.'
WRONG_ANSWER = 'SDL ni asilimia 99 ya jumla ya mishahara.'
GOOD_REFUSAL = 'Sina uhakika, thibitisha na TRA.'
# A confident non-refusal: the failure mode the refusal gate exists to catch.
BAD_REFUSAL = 'Kodi ya faida ya mtaji ni asilimia 10 kwa watu binafsi.'


def install_fake_transformers(reply_for):
    """Inject a fake `transformers` so main()'s model-loading branch runs for real.

    R23: the stubbed replies are chosen so each arm's score is known BEFORE the run, and the
    pass arm's expected value ('GATE PASSED') is one the failing arms demonstrably do not
    produce — the arms are read against each other, never alone.
    """
    fake = types.ModuleType('transformers')

    class _FromPretrained:
        @classmethod
        def from_pretrained(cls, *a, **k):
            return cls()

    def pipeline(*a, **k):
        def call(question, **kw):
            return [{'generated_text': reply_for(question)}]
        return call

    fake.AutoTokenizer = _FromPretrained
    fake.AutoModelForCausalLM = _FromPretrained
    fake.pipeline = pipeline
    sys.modules['transformers'] = fake
    return fake


def run_arm(name, expectation, pairs, reply_for):
    """Write the corpus, point the REAL module constants at it, run the REAL main()."""
    import run_eval
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        acc = Path(tmp) / 'accuracy_gate'
        ref = Path(tmp) / 'refusal_gate'
        res = Path(tmp) / 'results'
        for d in (acc, ref, res):
            d.mkdir(parents=True, exist_ok=True)
        if pairs:
            with open(acc / 'planted.jsonl', 'w', encoding='utf-8') as f:
                for p in pairs:
                    f.write(json.dumps(p, ensure_ascii=False) + '\n')

        orig = (run_eval.ACCURACY_GATE_DIR, run_eval.REFUSAL_GATE_DIR, run_eval.RESULTS_DIR)
        run_eval.ACCURACY_GATE_DIR, run_eval.REFUSAL_GATE_DIR, run_eval.RESULTS_DIR = acc, ref, res
        install_fake_transformers(reply_for)
        argv = sys.argv
        sys.argv = ['run_eval.py']
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                run_eval.main()
            code = None
        except SystemExit as e:
            code = e.code
        finally:
            sys.argv = argv
            (run_eval.ACCURACY_GATE_DIR, run_eval.REFUSAL_GATE_DIR,
             run_eval.RESULTS_DIR) = orig

    out = buf.getvalue()
    said_passed = 'GATE PASSED' in out
    said_failed = 'GATE FAILED' in out
    rec = {'arm': name, 'expectation': expectation, 'exit_code': code,
           'printed_GATE_PASSED': said_passed, 'printed_GATE_FAILED': said_failed,
           'tail': out.strip()[-500:]}
    print(f'  [{name}] exit={code} PASSED={said_passed} FAILED={said_failed}')
    return rec


def main():
    print('R7 GATE — planting corpora whose verdict is known in advance\n')
    arms = []

    # --- A: accuracy floor breached -----------------------------------------------------------
    arms.append(run_arm(
        'A_accuracy_0pct', 'GATE FAILED, exit non-zero',
        [dict(IN_CORPUS, id=f'ic_{i}') for i in range(10)] + [dict(OOC, id=f'ooc_{i}')
                                                              for i in range(10)],
        lambda q: GOOD_REFUSAL if 'faida ya mtaji' in q else WRONG_ANSWER))

    # --- B: refusal floor breached ------------------------------------------------------------
    arms.append(run_arm(
        'B_refusal_0pct', 'GATE FAILED, exit non-zero',
        [dict(IN_CORPUS, id=f'ic_{i}') for i in range(10)] + [dict(OOC, id=f'ooc_{i}')
                                                              for i in range(10)],
        lambda q: BAD_REFUSAL if 'faida ya mtaji' in q else RIGHT_ANSWER))

    # --- C: both above threshold — the gate must be able to say YES too -----------------------
    arms.append(run_arm(
        'C_both_pass', 'GATE PASSED, exit 0',
        [dict(IN_CORPUS, id=f'ic_{i}') for i in range(10)] + [dict(OOC, id=f'ooc_{i}')
                                                              for i in range(10)],
        lambda q: GOOD_REFUSAL if 'faida ya mtaji' in q else RIGHT_ANSWER))

    # --- D: empty corpus — record what it does, do not assume ---------------------------------
    arms.append(run_arm('D_empty_corpus', 'RECORD the behaviour', [], lambda q: RIGHT_ANSWER))

    a, b, c, d = arms
    verdict = {
        'accuracy_limb_can_refuse': a['printed_GATE_FAILED'] and a['exit_code'] not in (0, None),
        'refusal_limb_can_refuse': b['printed_GATE_FAILED'] and b['exit_code'] not in (0, None),
        'gate_can_also_pass': c['printed_GATE_PASSED'] and c['exit_code'] == 0,
    }
    verdict['R7_GATE_VERIFIED'] = all(verdict.values())
    empty = {
        'exit_code': d['exit_code'],
        'printed_GATE_PASSED': d['printed_GATE_PASSED'],
        'hazard': 'exits 0 without printing GATE PASSED. Safe for a human reading the output; '
                  'UNSAFE for any `&&` chain or CI step that treats exit 0 as authorisation. '
                  'The same shape as validate_dataset.py on an empty corpus.'
                  if d['exit_code'] == 0 and not d['printed_GATE_PASSED'] else
                  'see exit_code — behaviour differs from the 2026-08-24 reading',
    }

    blob = {
        'exercised': '2026-08-24',
        'harness': 'eval/controls/exercise_r7_gate.py',
        'target': 'scripts/run_eval.py — the R7 launch gate (>85% in-corpus AND >70% refusal)',
        'why': 'no recorded instance of this gate ever printing GATE FAILED. R26: a control is '
               'not working until you have watched it block the thing it exists to block.',
        'near_miss': 'tests/test_eval_gate.py passes and contains test_gate_fails_low_accuracy, '
                     'but it tests src/evaluate/eval_gate.py — a DIFFERENT module with '
                     'different thresholds (0.75 accuracy / hallucination / latency). A '
                     'reassuring name over a different mechanism makes the untested thing look '
                     'tested.',
        'verdict': verdict,
        'empty_corpus': empty,
        'arms': arms,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)
    print(f'\n=== {verdict}')
    print(f'=== empty corpus: {empty["exit_code"]}')
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

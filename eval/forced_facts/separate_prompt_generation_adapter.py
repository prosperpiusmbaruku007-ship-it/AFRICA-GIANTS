# -*- coding: utf-8 -*-
"""Is the model failing to USE what it is given because of PROMPT SHAPE, GENERATION, or the ADAPTER?

THE QUESTION THIS CLOSES. Three of the four covered-half defects — D1 adjacent-fact selection, D2
rank-1 contradiction, D4 refutation-held-not-used — are all *the model failing to use what it was
given*. Nothing distinguishes them, and everything downstream depends on which: context
construction is a code change, prompt sensitivity is a config change (R14), and an adapter fault
is a Kaggle retrain. **This is the measurement that decides whether a retrain is finally justified
or still is not.**

THE INSTRUMENT. `ChikeModel.generate_raw` is already deployed and takes a FINISHED prompt — no
classify, no decompose, no RAG, no cleaning. So the context is built locally with the production
wrapper (`chike.prompting.build_chat_prompt`, the same call `Orchestrator._build_fact_prompt`
makes) and only the fact list varies. That is a better instrument than restoring
`run_forced_facts`, because the variable under test IS the context and this gives exact control of
it.

VARY ONE THING AT A TIME. Three specimens, each with a baseline and three single-variable arms:

  A  eval_337 — D1. Two true adjacent NSSF facts, wrong one chosen.
     A1 the correct fact ALONE          -> can it use an unambiguous fact?
     A2 the COMPETITOR alone            -> control: does it follow context at all, or ignore it?
     A3 both, ORDER REVERSED            -> does position decide the answer?
     A4 both + an instruction naming the quantity wanted -> does telling it fix it?

  B  pic_11 — D2. Rank-1 fact contradicted.
     B1 the ceiling fact ALONE          -> does it still say "milioni 10" with nothing to confuse it?
     B2 alone + "use only the fact given"
     B3 alone + question stripped of its either/or framing

  C  eval_348 — D4. Refuting fact held, premise agreed with anyway.
     C1 the REFUTING fact alone         -> would supplying it have been enough?
     C2 refuting fact + question with the FALSE PREMISE REMOVED
     C3 baseline facts + premise removed -> is the premise itself the failure, not the facts?

DECISION RULE, NAMED BEFORE THE RUN — this is the part that must not move afterwards:

  * A2 must reproduce the competitor's figure. **If it does not, the model is not reading the
    context at all and every other arm is uninterpretable** — the run is void, not informative.
  * If A1, B1 and C1 are all CORRECT -> **PROMPT SHAPE.** The model uses an unambiguous fact; the
    defect is context construction (competitors pooled, no statement of which quantity is wanted).
    Fix is a code change. No retrain.
  * If the single-fact arms FAIL but a rephrasing arm (A4, B2, B3, C2) recovers it -> **GENERATION,
    prompt-sensitive.** Fix is prompt/config (R14). No retrain.
  * If NO arm recovers a specimen -> **ADAPTER**, and that is the first measured justification for
    a retrain in this project.
  * If C3 (premise removed, original facts) is correct while C0 is wrong -> a distinct
    **PREMISE-AGREEMENT** failure, orthogonal to fact use, which the three-way framing did not
    anticipate.

Mixed verdicts across specimens are a real possible outcome and must be reported as such rather
than averaged into one label.

R16: writes its artifact directly; no truncating console consumer between the run and the file.
R18: committed before it runs.
Artifact: eval/results/prompt_generation_adapter_separation.json
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

import modal                                                                # noqa: E402
from chike import prompting                                                 # noqa: E402

OUT = os.path.join(REPO, 'eval', 'results',
                   'prompt_generation_adapter_separation.json')
INDEX = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
ADAPTER_REPO = 'prospAprospA007/africa-giants-adapter-v15'

# Index rows resolved BY TEXT, never by a stored position (R18 instance 1).
NEEDLES = {
    'nssf_total': 'NSSF jumla: asilimia 20 ya mshahara',
    'nssf_employer_share': 'NSSF: mwajiri analipa asilimia 10',
    'nssf_12_workers': 'Kwa wafanyakazi 12 wenye mshahara TZS 600,000',
    'nssf_splits': 'NSSF split triggers',
    'nssf_deadline': 'NSSF inalipwa ifikapo tarehe 10',
    'presumptive_ceiling': 'presumptive tax ceiling 100m',
    'presumptive_bands': 'presumptive tax bands 2022',
    'vat_return_deadline': 'vat return submission deadline',
}

Q_337 = 'Kiwango cha mchango wa NSSF ni asilimia 3.5, au ni 0.5?'
Q_PIC11 = ('Mauzo yangu ni milioni 20 kwa mwaka, nitajua vipi ikiwa nalipa kodi ya mapato '
           'kwa makadirio au mfumo wa kawaida?')
Q_PIC11_PLAIN = 'Mauzo yangu ni milioni 20 kwa mwaka, kodi ya makadirio inanihusu?'
Q_348 = 'NSSF ina mgawanyo mmoja tu wa 10 kwa 10 kati ya mwajiri na mfanyakazi, sivyo?'
Q_348_NO_PREMISE = 'NSSF ina migawanyo gani halali kati ya mwajiri na mfanyakazi?'

# Arm-specific instruction lines, appended to the QUESTION (not the system prompt) so the
# production system prompt stays byte-identical and the only variable is what the user turn says.
INSTR_QUANTITY = ' Nataka JUMLA ya mchango (mwajiri pamoja na mfanyakazi), si sehemu ya upande mmoja.'
INSTR_ONLY_FACT = ' Jibu ukitumia UKWELI uliopewa pekee, usitumie taarifa nyingine.'


def build_arms(rows):
    def f(*keys):
        return [rows[k] for k in keys]

    return [
        # --- A: eval_337, adjacent-fact selection -------------------------------------------
        dict(id='A0_baseline', specimen='eval_337', question=Q_337,
             facts=f('nssf_total', 'nssf_employer_share', 'nssf_12_workers'),
             expect='asilimia 20 (jumla)', varies='nothing — reproduces production top-3'),
        dict(id='A1_correct_alone', specimen='eval_337', question=Q_337,
             facts=f('nssf_total'), expect='asilimia 20 (jumla)',
             varies='competitor REMOVED'),
        dict(id='A2_competitor_alone', specimen='eval_337', question=Q_337,
             facts=f('nssf_employer_share'), expect='asilimia 10 (mwajiri)',
             varies='CONTROL — must reproduce the competitor or the run is void'),
        dict(id='A3_order_reversed', specimen='eval_337', question=Q_337,
             facts=f('nssf_employer_share', 'nssf_total'), expect='asilimia 20 (jumla)',
             varies='ORDER only'),
        dict(id='A4_instructed', specimen='eval_337', question=Q_337 + INSTR_QUANTITY,
             facts=f('nssf_total', 'nssf_employer_share'), expect='asilimia 20 (jumla)',
             varies='instruction naming the quantity wanted'),
        # --- B: pic_11, rank-1 contradiction ------------------------------------------------
        dict(id='B0_baseline', specimen='pic_11', question=Q_PIC11,
             facts=f('presumptive_ceiling', 'vat_return_deadline', 'presumptive_bands'),
             expect='kikomo TZS 100,000,000 — makadirio yanahusika',
             varies='nothing — reproduces production top-3'),
        dict(id='B1_ceiling_alone', specimen='pic_11', question=Q_PIC11,
             facts=f('presumptive_ceiling'),
             expect='kikomo TZS 100,000,000 — makadirio yanahusika',
             varies='distractors REMOVED'),
        dict(id='B2_only_fact_instruction', specimen='pic_11',
             question=Q_PIC11 + INSTR_ONLY_FACT, facts=f('presumptive_ceiling'),
             expect='kikomo TZS 100,000,000', varies='instruction to use only the fact'),
        dict(id='B3_no_either_or', specimen='pic_11', question=Q_PIC11_PLAIN,
             facts=f('presumptive_ceiling'), expect='ndiyo, kikomo ni 100,000,000',
             varies='either/or framing REMOVED from the question'),
        # --- C: eval_348, refutation held not used ------------------------------------------
        dict(id='C0_baseline', specimen='eval_348', question=Q_348,
             facts=f('nssf_employer_share', 'nssf_total', 'nssf_deadline'),
             expect='hapana — kuna migawanyo mitatu',
             varies='nothing — reproduces production top-3'),
        dict(id='C1_refuting_alone', specimen='eval_348', question=Q_348,
             facts=f('nssf_splits'), expect='hapana — 10+10, 15+5, 20+0',
             varies='the REFUTING fact supplied'),
        dict(id='C2_refuting_no_premise', specimen='eval_348', question=Q_348_NO_PREMISE,
             facts=f('nssf_splits'), expect='10+10, 15+5, 20+0',
             varies='refuting fact AND premise removed'),
        dict(id='C3_baseline_no_premise', specimen='eval_348', question=Q_348_NO_PREMISE,
             facts=f('nssf_employer_share', 'nssf_total', 'nssf_deadline'),
             expect='migawanyo — ideally three',
             varies='premise removed, ORIGINAL facts kept'),
    ]


def main():
    with open(INDEX, encoding='utf-8') as f:
        texts = json.load(f)
    rows = {}
    for key, needle in NEEDLES.items():
        hits = [t for t in texts if needle in t]
        assert len(hits) == 1, f'{key}: needle matched {len(hits)} index rows, need exactly 1'
        rows[key] = hits[0]

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(ADAPTER_REPO, trust_remote_code=True)
    system_prompt = prompting.load_system_prompt()

    ChikeModel = modal.Cls.from_name('chike-inference', 'ChikeModel')
    out_rows = []
    for arm in build_arms(rows):
        prompt = prompting.build_chat_prompt(
            arm['question'], arm['facts'], system_prompt, tokenizer=tok)
        print(f"\n=== [{arm['specimen']}] {arm['id']} — varies: {arm['varies']}")
        print(f"Q: {arm['question']}")
        for fct in arm['facts']:
            print(f"   FACT: {fct[:120]}")
        rec = dict(arm)
        rec['n_facts'] = len(arm['facts'])
        t0 = time.time()
        try:
            resp = ChikeModel().generate_raw.remote(prompt)
            reply = resp.get('reply', resp) if isinstance(resp, dict) else str(resp)
            if isinstance(resp, dict) and 'text' in resp:
                reply = resp['text']
            rec['reply'] = reply
            print(f"A: {reply}")
        except Exception as e:
            rec['error'] = f'{type(e).__name__}: {e}'
            print(f"ERROR: {rec['error']}")
        rec['elapsed_s'] = round(time.time() - t0, 1)
        out_rows.append(rec)

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/forced_facts/separate_prompt_generation_adapter.py',
        'instrument': 'ChikeModel.generate_raw (already deployed) + '
                      'chike.prompting.build_chat_prompt — production wrapper, local context',
        'adapter': ADAPTER_REPO,
        'decision_rule': 'See the module docstring. Named BEFORE the run and not to be moved '
                         'afterwards. A2 is a validity control: if it does not reproduce the '
                         'competitor figure the run is VOID, not informative.',
        'adjudication': 'PENDING — verdicts are Claude Code JUDGEMENT, added in a follow-up '
                        'commit.',
        'n': len(out_rows),
        'rows': out_rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {OUT}  ({len(out_rows)} arms)')


if __name__ == '__main__':
    main()

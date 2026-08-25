# -*- coding: utf-8 -*-
"""SCOPE (A): price a grounding-triggered clarification BEFORE building it, on committed evidence.

THE PROPOSED MECHANISM. Every safety floor this project has tried asked *"how confident am I about
this topic?"* and all five died. A different question survives R19: **do the figures in this reply
appear in the retrieved facts or the engine's working?** If not, they came from weights. That is a
comparison against a fixed input, needs no ComputationResult, and works on the fact path where
every fidelity rule before D-FIDELITY-6 goes vacuous. Instead of refusing, CLARIFY.

⛔ AND IT CAN CLARIFY A REAL USER'S ANSWERABLE QUESTION, which puts it squarely under the block
above R17: its failure mode is *withholding an answer*, the expensive and invisible direction. So
it gets priced the way the coverage gate should have been priced — **cost first, on the population
that pays it.**

THIS HARNESS DOES NOT BUILD OR RUN THE MECHANISM. It cross-tabulates two committed artifacts that
already contain everything needed to price it:

  eval/results/grounding_48.json          per-row GROUNDED / UNGROUNDED / NO_FIGURES, produced by
                                          reproducing production retrieval exactly (e5-base,
                                          'query: ', cosine, top_k=3)
  eval/grounding/adjudication_no_figures.json  human adjudication of the 6 CORRECT fact rows the
                                          figure test cannot judge

The question it answers is the only one that matters before building:
**HOW OFTEN WOULD THIS FIRE ON A RIGHT ANSWER, VERSUS ON A WRONG ONE?**

⚠️ POPULATION (R22, and it cuts both ways here):
  BENEFIT is measured on fact-path rows adjudicated WRONG -- the population the remedy is FOR.
  COST is measured on fact-path rows adjudicated CORRECT -- the population that pays for it.
  Both are the natural 48, which is self-authored (R21). The corpus-side figure is a LOWER BOUND
  on cost; a held-out set authored against the user is the entry price and is NOT what this is.

⚠️ AND A SENSITIVITY THAT CHANGES THE ANSWER, recorded rather than defaulted: grounding here is
measured at top_k=3. The orchestrator assembles a decompose->pool of NINE. Against the larger pool
MORE figures count as grounded, so the mechanism catches FEWER wrong answers AND raises fewer false
clarifications. Which pool it checks against is a design decision with a measurable cost, and it
must be decided by measurement rather than by whichever is convenient.

R18: committed before its result is written up.
Artifact: eval/results/grounding_trigger_price.json
"""
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'eval', 'results', 'grounding_trigger_price.json')

GROUNDING = 'eval/results/grounding_48.json'
NO_FIGURES = 'eval/grounding/adjudication_no_figures.json'

# The nine WRONG fact-path rows partitioned by MECHANISM on 2026-08-22 (PROGRESS.md, "the class
# analysis gets stronger"). Recorded here because it is what decides the mechanism's ceiling: in a
# RANKING failure the model RECITES a retrieved (wrong) fact, so the reply IS grounded and a
# grounding trigger is silent by construction.
CLASS_ANALYSIS = {
    'partition_of_the_9_wrong_fact_rows': {'RANKING': 8, 'ABSENCE': 1, 'OVERRIDE': 0, 'UNUSED': 0},
    'traceable_wrong_figures': {
        'nat_05': 'TZS 260,000 <- rank 3 in its pool: `company registration fee 3: 260,000 TZS`',
        'nat_41': '"siku 1"    <- rank 1: `registration certificate processing time new: 1 days`',
        'nat_28': '15%         <- rank 1: `royalties wht rate: ... 15% ...`',
        'nat_44': '6%          <- a services rate offered to a GOODS question',
    },
    'why_this_caps_the_mechanism': (
        'A recited wrong fact is GROUNDED. The dominant defect class is therefore invisible to a '
        'grounding trigger by construction -- not because the trigger is badly built, but because '
        'the figure really did come from the context. "Fabricated" was the wrong word for these '
        'answers all along: they are TRACEABLE.'),
    'r22_caveat_on_the_zero': (
        'OVERRIDE=0 was measured ONLY over the failures. nat_38 is an override among the '
        'SUCCESSES (it answered correctly while its one on-topic retrieved fact pointed the other '
        'way). So the zero supports "an adapter fixes none of these nine"; it does NOT support '
        '"the model recites what it is handed" as a general claim.'),
}

# Gate arithmetic. A clarification is not scored as a correct answer by scripts/run_eval.py:
# score_question dispatches on answer_type, and only `out_of_corpus_refusal` consults
# is_correct_refusal. So on an IN-CORPUS question a clarification scores exactly like a wrong
# answer -- while on an OOC question it scores as a PASS, because the proposed copy opens with
# "sina uhakika", which is in refusal_phrases. The interaction is asymmetric and points the wrong
# way: Gate 2 gets easier, Gate 1 gets harder, and Gate 1 is the one with almost no headroom.
GATE = {
    'gate_1_in_corpus_threshold': 0.85,
    'gate_1_last_recorded': 0.879,
    'eval_set_size': 200,
    'headroom_questions': None,          # computed below
    'gate_2_out_of_corpus_threshold': 0.70,
    'gate_2_last_recorded': 1.00,
    'clarification_copy_contains_a_refusal_phrase': 'sina uhakika',
}


def main():
    g = json.load(open(os.path.join(REPO, GROUNDING), encoding='utf-8'))
    nf = json.load(open(os.path.join(REPO, NO_FIGURES), encoding='utf-8'))
    fact = [r for r in g['rows'] if r['path'] == 'fact']
    assert len(fact) == 21, f'expected 21 fact-path rows, got {len(fact)}'

    # --- The cross-tab the decision rests on. -------------------------------------------------
    tab = Counter((r['verdict'], r['grounding']) for r in fact)
    fires_on = {'WRONG': [], 'CORRECT': [], 'PARTIAL': [], 'CLARIFY': []}
    silent_on = {'WRONG': [], 'CORRECT': [], 'PARTIAL': [], 'CLARIFY': []}
    for r in fact:
        # The trigger fires when a figure the reply ASSERTS is absent from the retrieved context.
        # NO_FIGURES rows assert no new figure, so a figure-based trigger cannot fire on them.
        (fires_on if r['grounding'] == 'UNGROUNDED' else silent_on)[r['verdict']].append(r['id'])

    # --- The human adjudication reaches the NO_FIGURES rows the figure test cannot judge. ------
    tally = nf['tally_of_all_11_fact_path_correct_rows']
    ungrounded_correct = tally['UNGROUNDED']

    n_wrong = sum(1 for r in fact if r['verdict'] == 'WRONG')
    n_correct = sum(1 for r in fact if r['verdict'] == 'CORRECT')
    n_correct_with_figures = sum(1 for r in fact
                                 if r['verdict'] == 'CORRECT' and r['grounding'] != 'NO_FIGURES')

    GATE['headroom_questions'] = round(
        (GATE['gate_1_last_recorded'] - GATE['gate_1_in_corpus_threshold'])
        * GATE['eval_set_size'])

    verdict = {
        'benefit_population': 'fact-path rows adjudicated WRONG -- the population the remedy is FOR',
        'catches_wrong': {'n': len(fires_on['WRONG']), 'of': n_wrong,
                          'which': fires_on['WRONG']},
        'misses_wrong': {'n': len(silent_on['WRONG']), 'of': n_wrong,
                         'which': silent_on['WRONG'],
                         'why': 'GROUNDED -- the wrong figure really was in the retrieved context'},
        'cost_population': 'fact-path rows adjudicated CORRECT -- the population that PAYS',
        'clarifies_correct_figure_bearing': {'n': len(fires_on['CORRECT']),
                                             'of': n_correct_with_figures,
                                             'which': fires_on['CORRECT']},
        'clarifies_correct_all_11_by_human_adjudication': {
            'n': len(ungrounded_correct), 'of': 11, 'which': ungrounded_correct,
            'note': 'adds nat_37 and nat_38, which the figure test scores NO_FIGURES. nat_38 is '
                    'UNGROUNDED_AND_CONTRARY -- it answered CORRECTLY while its one on-topic '
                    'retrieved fact said the opposite. A grounding trigger clarifies it, and '
                    'better retrieval-following would have made it WORSE.'},
        'headline': None,
    }
    verdict['headline'] = (
        f"On the measured population the trigger fires on {len(fires_on['WRONG'])} of {n_wrong} "
        f"WRONG fact rows and on {len(ungrounded_correct)} of 11 CORRECT ones. "
        f"IT FIRES MORE OFTEN ON RIGHT ANSWERS THAN ON WRONG ONES.")

    blob = {
        'measured': '2026-08-25',
        'harness': 'eval/scoping/price_grounding_trigger.py',
        'purpose': 'price scope (A) BEFORE building it -- no mechanism is built or run here',
        'sources': [GROUNDING, NO_FIGURES],
        'why_each_population': {
            'benefit': 'WRONG fact rows -- R22: a remedy for wrong answers is measured on wrong '
                       'answers, never on the base rate.',
            'cost': 'CORRECT fact rows -- the users who would be clarified at instead of '
                    'answered. This is the cost the coverage gate was never priced on.',
            'NOT_MEASURED': 'paraphrase space. Both populations are the self-authored natural 48, '
                            'so the cost figure is a LOWER BOUND (R21, 37x precedent). A held-out '
                            'set authored against the user, frozen before the mechanism exists, '
                            'is the entry price.',
        },
        'top_k_sensitivity': 'grounding here is at top_k=3; the orchestrator pools NINE. Against '
                             'the larger pool more figures are grounded, so the trigger catches '
                             'FEWER wrong answers and raises FEWER false clarifications. Decide '
                             'by measurement, not by convenience.',
        'cross_tab_verdict_x_grounding': {f'{v}|{gr}': n for (v, gr), n in sorted(tab.items())},
        'verdict': verdict,
        'class_analysis_ceiling': CLASS_ANALYSIS,
        'gate_interaction': GATE,
        'gate_interaction_note': (
            f"Gate 1 has ~{GATE['headroom_questions']} questions of headroom "
            f"({GATE['gate_1_last_recorded']:.3f} against a {GATE['gate_1_in_corpus_threshold']} "
            f"floor over {GATE['eval_set_size']} questions). Every in-corpus question this "
            f"mechanism clarifies is a direct Gate 1 loss, because score_question does not treat "
            f"a clarification as anything but a wrong answer. Meanwhile the proposed copy opens "
            f"with 'sina uhakika', which IS in refusal_phrases, so on OOC rows it scores as a "
            f"PASS. The mechanism makes the gate we already clear easier and the gate we barely "
            f"clear harder."),
        'per_row': [{'id': r['id'], 'verdict': r['verdict'], 'grounding': r['grounding'],
                     'fires': r['grounding'] == 'UNGROUNDED'} for r in fact],
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    print('cross-tab (fact path, n=21):')
    for k, n in sorted(tab.items()):
        print(f'  {k[0]:8s} x {k[1]:12s} {n}')
    print(f"\nfires on WRONG   : {len(fires_on['WRONG'])}/{n_wrong}  {fires_on['WRONG']}")
    print(f"misses WRONG     : {len(silent_on['WRONG'])}/{n_wrong}  {silent_on['WRONG']}")
    print(f"fires on CORRECT : {len(ungrounded_correct)}/11  {ungrounded_correct}")
    print(f"\n{verdict['headline']}")
    print(f"\nGate 1 headroom: ~{GATE['headroom_questions']} questions")
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

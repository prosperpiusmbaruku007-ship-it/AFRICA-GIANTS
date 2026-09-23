# -*- coding: utf-8 -*-
"""Sweeps every OOC phrase in kaggle/chike_config.json against every IN-SCOPE question in
every committed corpus, and reports which phrases would refuse a question that must be
answered.

WHY THIS EXISTS (2026-09-23). ext_01 of the extended-078 probe set was refused live: it
contains the exact OOC phrase "soko la hisa", and chike.classification.classify() checks OOC
FIRST and returns before anything else can intervene. The phrase was safe when it was written
-- nothing in the corpus asked about stock-exchange LISTING STATUS. Building the corporate-tax
domain made listing status an in-scope question, and the phrase over-broad, without the phrase
changing at all.

That is the general hazard this sweep is for, and it is the reverse of R17's usual direction:
R17 asks whether a NEW cue collides with the EXISTING corpus. This asks whether an OLD cue has
been made over-broad by a NEW domain. Same collision, opposite arrival -- and nothing in the
project checked for it, because adding a domain does not look like touching the refusal path.

NOTE ON THE ONLY AVAILABLE FIX: in_scope_phrases CANNOT rescue an over-broad OOC phrase.
chike/classification.py's own docstring records that the in-scope loop is a no-op -- both it
and the fallthrough return True, so OOC always wins. Narrowing the OOC phrase is the only
lever. Verified, not assumed: see tests/test_ooc_phrase_narrowing.py.

R21 BOUND -- state it with any number this prints: these corpora were authored from the same
source families as the facts, so they share vocabulary with them by construction. A clean
sweep here is a LOWER BOUND on collision cost and an UPPER BOUND on confidence. It cannot see
paraphrase space. R17 step 2 (authored adversarial in-scope probes) is the partial remedy and
is not sufficient either.

R18: committed before the write-up that cites it.
Artifact: eval/results/ooc_phrase_inscope_sweep_2026_09_23.json
"""
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CONFIG = os.path.join(REPO, 'kaggle', 'chike_config.json')
OUT = os.path.join(REPO, 'eval', 'results', 'ooc_phrase_inscope_sweep_2026_09_23.json')

QUESTION_KEYS = ('question', 'question_sw', 'q', 'prompt', 'hypothesis')

# Collisions examined and DELIBERATELY LEFT ALONE. R20: "no change needed here" is a valid,
# recordable outcome, and recording it AT THE SITE is what stops the next run re-raising it
# and the next reader re-narrowing a phrase that is doing its job. Keyed (phrase, row id).
ACCEPTED_COLLISIONS = {
    ('stempu', 'eval_228'):
        "Stamp duty on a Memorandum of Association. Genuinely in-scope-adjacent "
        "(subdomain brela_registration), so this is a real collision, not a bad specimen. "
        "NOT narrowed: stamp duty is a named OOC topic under R11, and eval_228's OWN gold "
        "answer is a hedge -- 'the figure commonly cited is TZS 10,000, but it is not "
        "confirmed against the current Stamp Duty Act schedule; do not quote it without "
        "certainty, confirm with TRA'. The OOC refusal sends the user to TRA, which is where "
        "the gold answer sends them too; it refuses on the wrong GROUNDS (topic rather than "
        "uncertainty) but reaches the right destination. Narrowing `stempu` to rescue one "
        "row whose correct answer is a referral would open a live OOC topic that three other "
        "rows (eval_312, eval_197, ro_03) depend on. Cost of leaving it: one imprecise "
        "refusal reason. Cost of fixing it: a real capital-taxes leak.",
    ('ushuru wa stempu', 'eval_228'):
        "Same row, longer form of the same cue. Same decision and same reasoning.",
    ('ushuru wa hati', 'hoA_stamp_duty'):
        "BAD SPECIMEN, kept visible rather than filtered away. The row's true_topic IS "
        "stamp_duty -- an OOC topic -- so refusing it is CORRECT. Its `expect: pass` belongs "
        "to the COVERAGE GATE, a different mechanism that is DISABLED by decision (37x "
        "false-refusal gap), not to the OOC classifier. Two mechanisms, two meanings of "
        "'pass'; reading this row's field as a verdict on the classifier is the mistake, not "
        "the phrase.",
}

# Rows in these files, or rows whose own metadata says so, are SUPPOSED to be refused --
# a phrase matching them is the phrase working, not colliding.
OOC_BY_DESIGN_FILES = ('ooc_adversarial',)


def is_ooc_by_design(path, row):
    """True if this row is one the classifier is MEANT to refuse.

    EVERY CLAUSE BELOW WAS ADDED BECAUSE ITS ABSENCE PRODUCED A FALSE COLLISION. The first
    version of this function knew only about `expected_refusal` and an `ooc_` prefix, and
    reported 34 colliding phrases. Thirty-three of those were OOC questions this function had
    mislabelled as in-scope -- the corpora spell "this must be refused" nine different ways
    across nine files, and matching an OOC question is the phrase WORKING.

    Reported unchecked, that would have sent someone to narrow 33 phrases that are doing their
    job, and narrowing a working refusal phrase opens a real OOC leak. R26's second half: an
    audit's false positives cost more than its false negatives, because only the false
    positives generate edits.
    """
    # Trust the field, not the filename: ooc_adversarial_in_scope_015.jsonl is the opposite of
    # what its name suggests -- its rows are IN-SCOPE questions carrying risky vocabulary.
    if 'expected_refusal' in row:
        return bool(row['expected_refusal'])
    if row.get('expected_in_scope') is False:
        return True
    for key in ('subdomain', 'true_topic', 'cat', 'topic', 'boundary_topic', 'family'):
        val = str(row.get(key, '')).lower()
        if val.startswith('ooc') or val in ('out_of_corpus', 'out-of-corpus', 'ooc'):
            return True
    if str(row.get('answer_type', '')).lower() in ('out_of_corpus_refusal', 'refusal'):
        return True
    if str(row.get('gold_route', '')).lower() in ('refusal', 'refuse'):
        return True
    if str(row.get('difficulty_tier', '')).lower() == 'ooc_control':
        return True
    if str(row.get('arm', '')).lower() in ('c_genuine_ooc',):
        return True
    if str(row.get('expect', '')).lower() in ('refuse', 'refusal', 'ooc', 'ooc_refusal'):
        return True
    for key in ('intent_expected', 'expected_intent', 'expect_intent'):
        if str(row.get(key, '')).lower().startswith(('refusal', 'refuse')):
            return True
    return False


def load_corpora():
    """Every question in every committed corpus, tagged with its file and in-scope status."""
    items = []
    for path in sorted(glob.glob(os.path.join(REPO, 'eval', '**', '*.jsonl'), recursive=True)):
        rel = os.path.relpath(path, REPO).replace('\\', '/')
        with open(path, encoding='utf-8') as f:
            for ln, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                q = next((row[k] for k in QUESTION_KEYS
                          if isinstance(row.get(k), str) and row[k].strip()), None)
                if not q:
                    continue
                items.append({'file': rel, 'line': ln, 'id': row.get('id', f'{rel}:{ln}'),
                              'question': q, 'ooc_by_design': is_ooc_by_design(rel, row)})
    return items


def main():
    cfg = json.load(open(CONFIG, encoding='utf-8'))
    phrases = cfg['ooc_phrases']
    items = load_corpora()
    in_scope = [it for it in items if not it['ooc_by_design']]

    # R20: this assertion is not decorative. If a loader change silently returns nothing, a
    # sweep over zero questions reports ZERO COLLISIONS -- indistinguishable from a clean
    # result, and the exact vacuous-pass shape this project keeps finding.
    assert len(items) > 500, f'corpus loader returned only {len(items)} questions'
    assert len(in_scope) > 400, f'only {len(in_scope)} in-scope questions after filtering'
    assert phrases, 'ooc_phrases is empty'

    collisions, unexplained = {}, {}
    for phrase in phrases:
        hits = [{'id': it['id'], 'file': it['file'], 'question': it['question'],
                 'accepted': ACCEPTED_COLLISIONS.get((phrase, it['id']))}
                for it in in_scope if phrase in it['question'].lower()]
        if hits:
            collisions[phrase] = hits
            new = [h for h in hits if not h['accepted']]
            if new:
                unexplained[phrase] = new

    print(f'corpora: {len(items)} questions, {len(in_scope)} in-scope, '
          f'{len(items) - len(in_scope)} OOC-by-design')
    print(f'ooc phrases swept: {len(phrases)}')
    print(f'phrases colliding with an in-scope question: {len(collisions)}')
    print(f'  of which ACCEPTED (examined, deliberately unchanged): '
          f'{len(collisions) - len(unexplained)}')
    print(f'  UNEXPLAINED -- these need a decision: {len(unexplained)}\n')
    for phrase, hits in sorted(collisions.items(), key=lambda kv: -len(kv[1])):
        tag = 'ACCEPTED' if phrase not in unexplained else '*** UNEXPLAINED ***'
        print(f'  [{len(hits):>2}] "{phrase}"   {tag}')
        for h in hits[:4]:
            print(f'         {h["id"]}: {h["question"][:96]}')
        if len(hits) > 4:
            print(f'         ... and {len(hits) - 4} more')

    blob = {
        'measured': '2026-09-23',
        'harness': 'eval/controls/sweep_ooc_phrases_vs_inscope.py',
        'config': 'kaggle/chike_config.json',
        'bound': 'R21 LOWER BOUND. These corpora share vocabulary with the facts by '
                 'construction (authored from the same source families). A clean result here '
                 'does not measure paraphrase space and must never be written up as "safe".',
        'why_this_population': 'Every in-scope question this project has committed, which is '
                               'the population an over-broad refusal phrase would harm. It is '
                               'NOT the population a real user draws from (R21/R22).',
        'totals': {'questions': len(items), 'in_scope': len(in_scope),
                   'ooc_by_design': len(items) - len(in_scope), 'phrases': len(phrases),
                   'phrases_colliding': len(collisions),
                   'phrases_unexplained': len(unexplained)},
        'accepted_collisions': {f'{p} :: {i}': why
                                for (p, i), why in ACCEPTED_COLLISIONS.items()},
        'collisions': collisions,
        'unexplained': unexplained,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {os.path.relpath(OUT, REPO)}')


if __name__ == '__main__':
    main()

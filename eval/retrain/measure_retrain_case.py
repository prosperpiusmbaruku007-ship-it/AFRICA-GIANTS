# -*- coding: utf-8 -*-
"""Measures the three quantities the retrain decision turns on. Does not make the decision.

⛔ TWO CAVEATS THAT BELONG AT THE FRONT, NOT IN A LIMITATIONS SECTION ⛔

1. THE BUCKET-E POPULATION IS 14 AUTHORED PROBES, OUTCOME-CONDITIONED ON FAILURE. Every row was
   selected because the model ALREADY answered it wrong live AND the supporting fact was
   verified present in the shipped index. It therefore establishes the FAILURE PROFILE OF ROWS
   WE ALREADY KNEW WERE WRONG and says nothing about the corpus generally (R22). No number in
   this file may be read as a corpus-wide rate.

2. 14 PROBES COVER ONLY 12 DISTINCT INDEX ROWS. ext_08/ext_09/ext_11 all resolve to row 168
   (presumptive bands). They all SUCCEEDED, so the redundancy inflates the REACH side, not the
   failure side. Every headline here is therefore reported per DISTINCT INDEX ROW as well as
   per probe, and the distinct-row figure is the one to quote.

=== WHAT IT MEASURES ===

A. RESIDUAL QUARANTINE EXPOSURE. Are rows we quarantined still physically in the SFT files a
   retrain would consume? Matched on question text, since SFT rows carry no id.

B. DEFECT-ASSERTION EXPOSURE. How many training rows assert something the corrected record now
   contradicts, swept with locked_facts `wrong_patterns`.
   ⚠️ THIS IS A BOUND IN BOTH DIRECTIONS, NOT A COUNT. wrong_patterns are known to be
   over-broad (the 2026-09-23 language scan produced 200 hits, ~29% of which guarded working
   text) AND known to be blind (2026-09-24: the service-levy patterns require a literal string
   that appears only in the QUESTION; OSHA_penalties guards "miezi 6" while the live defect was
   "miezi 12 hadi 24"). Report it as a bound and never as "the number of bad training rows".

C. BUCKET-E FAILURE x DEFECT-CLASS OVERLAP. For each probe, does its supporting fact belong to
   a defect class that was actually quarantined? This is the crux: if the rows that reached
   context and still failed are NOT rows the corpus corrections touch, then a retrain is being
   scoped on a corpus fix that does not address the measured failures.

D. GATE ARITHMETIC. Gate 1 headroom in whole questions, stated up front, because the gate is
   the expensive irreversible step and an expected gain smaller than its granularity is not a
   gain.

Usage:  python eval/retrain/measure_retrain_case.py
Artifact: eval/results/retrain_case_2026_09_24.json
"""
import collections
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SFT = os.path.join(REPO, 'datasets', 'tier1a', 'sft')
REJECTED = os.path.join(REPO, 'datasets', 'tier1a', 'rejected')
FACTS = os.path.join(REPO, 'scripts', 'locked_facts.json')
PROBES = os.path.join(REPO, 'eval', 'grounding', 'bucket_e_reach_probes_014.jsonl')
OUT = os.path.join(REPO, 'eval', 'results', 'retrain_case_2026_09_24.json')

# Bucket-E reach outcome, transcribed from the Kaggle console 2026-09-24.
# ⚠️ PROVENANCE: the full per-probe artifact was written on Kaggle and is NOT yet in this repo
# (R18 wants harness + fixture + artifact; two of three are here). Everything downstream of
# this dict is PROVISIONAL until eval/results/bucket_e_reach_2026_09_24.json lands.
REACH = {
    'ext_02': 'IN_TOP3', 'ext_08': 'IN_TOP3', 'ext_09': 'IN_TOP3', 'ext_11': 'IN_TOP3',
    'ext_14': 'IN_TOP3', 'ext_18': 'IN_TOP3', 'ext_23': 'IN_TOP3', 'ext_25': 'IN_TOP3',
    'ext_32': 'IN_TOP3',
    'ext_21': 'DEEP', 'ext_22': 'DEEP', 'ext_27': 'DEEP',
    'ext_29': 'BOUNDARY', 'ext_31': 'BOUNDARY',
}
REACHES = {'IN_TOP3'}

# C. Per-probe mapping onto the quarantined defect classes. Assigned by READING each probe's
# `needs` against the verbatim `_quarantine.reasons` strings, NOT by keyword overlap -- a
# keyword pass was run first and was discarded as a bad specimen (R26 second half): broad terms
# like "ada", "faini" and "osha" matched dozens of unrelated quarantined rows and would have
# reported overlap where none exists.
DEFECT_CLASS = {
    'ext_02': ('dse_stale_float_2026_09_01',
               'DIRECT. Probe needs the >=25% public-float condition; the quarantined class is '
               'rows asserting the stale >=30% condition. Same fact, same clause, opposite '
               'value.'),
    'ext_08': ('presumptive_stale_ceiling_rate_2026_09_01',
               'SAME FACT, ADJACENT CLAUSE. The quarantine targets the stale 100M ceiling / '
               '3.5% top rate; the probe needs the zero band. One locked fact '
               '(presumptive_tax_bands_2022), so the correction rewrites the row the probe '
               'depends on -- but not the clause the probe asks about.'),
    'ext_09': ('presumptive_stale_ceiling_rate_2026_09_01',
               'SAME FACT, ADJACENT CLAUSE. As ext_08; probe needs the no-records 100,000 band.'),
    'ext_11': ('presumptive_stale_ceiling_rate_2026_09_01',
               'DIRECT. The new-business exemption the probe needs was ADDED to the fact by the '
               'same Finance Act 2026 correction that drove this quarantine.'),
    'ext_14': (None, 'No quarantined class. The BRELA local late-filing penalty (2,500/month) '
                     'was never found wrong in the corpus.'),
    'ext_18': (None, 'No quarantined class. memorandum_articles_fee_stale_22000 is the MemArts '
                     'fee, a DIFFERENT fee from name reservation (50,000). Checked, not assumed.'),
    'ext_21': (None, 'No quarantined class. Objection deposit rule was never a corpus defect.'),
    'ext_22': (None, 'No quarantined class. Objection extension right was never a corpus defect.'),
    'ext_23': (None, 'No quarantined class. The service-levy cap was never quarantined -- and '
                     'the live 2026-09-24 failure on it (cp_05) INVERTED cap into floor with '
                     'the correct fact in context.'),
    'ext_25': (None, 'No quarantined class. Nationally-set licence fee was never a corpus '
                     'defect; keyword pass matched unrelated rows on "ada" and was discarded.'),
    'ext_27': (None, 'No quarantined class. Class B was CONFIRMED correct against the '
                     'Immigration Act, never quarantined.'),
    'ext_29': (None, 'NOT A MATCH, and this one is the near-miss worth stating. A VAT class WAS '
                     'quarantined -- but it is rows DATING the 100M->200M increase to July 2024. '
                     'Those rows assert the CORRECT 200M value with a wrong date. The probe '
                     'needs the value. Correcting the date changes nothing the model learned '
                     'about the threshold itself.'),
    'ext_31': (None, 'No quarantined class. AND THIS IS A LIVE CONTENT DEFECT INDEPENDENT OF THE '
                     'RETRAIN: index row 86 says "designated representative from existing '
                     'staff", the live reply said "must hire a safety officer above N '
                     'employees". Fix the fact regardless of the retrain outcome.'),
    'ext_32': (None, 'No quarantined class. The OSHA quarantine is course_fee 250,000, a '
                     'different fact from the continuing-offence penalty.'),
}

# B. Which of the reaching-and-failing rows a retrain could PLAUSIBLY reach, and which it
# structurally cannot. Assigned from the failure SHAPE, not from the topic.
RETRAIN_REACHABLE = {
    'ext_02': ('PLAUSIBLY', 'Wrong stale value was in training; corrected rows teach the right '
                            'one. This is the shape SFT is for.'),
    'ext_08': ('PLAUSIBLY', 'Same fact row corrected; band recall is content the model can be '
                            'taught.'),
    'ext_09': ('PLAUSIBLY', 'As ext_08.'),
    'ext_11': ('PLAUSIBLY', 'The exemption clause is newly-correct content absent from the old '
                            'training set.'),
    'ext_14': ('NO', 'Nothing in training asserted this wrongly. A retrain re-teaches a fact '
                     'that was already right and the model still got wrong.'),
    'ext_18': ('NO', 'As ext_14 -- correct in corpus, wrong in output.'),
    'ext_23': ('NO -- AND IT IS THE COUNTEREXAMPLE', 'The corpus fact is CORRECT and reached '
               'top-3, and the model inverted "kikomo" (ceiling) into a floor live on '
               '2026-09-24 (cp_05). Retraining on correct facts does not address a model that '
               'contradicts a correct fact sitting in its context.'),
    'ext_25': ('NO', 'Correct in corpus, wrong in output.'),
    'ext_32': ('NO', 'Correct in corpus, wrong in output.'),
}


def load_jsonl(path):
    with open(path, encoding='utf-8') as f:
        rows = [json.loads(l) for l in f if l.strip()]
    assert rows, f'no rows loaded from {path} -- a sweep over zero rows reports clean over nothing'
    return rows


def norm(s):
    return re.sub(r'\s+', ' ', (s or '')).strip().lower()


def main():
    probes = {r['id']: r for r in load_jsonl(PROBES)}
    assert set(probes) == set(REACH), 'probe set and reach result disagree'
    assert set(probes) == set(DEFECT_CLASS), 'probe set and defect mapping disagree'

    # ---- A. residual quarantine exposure -------------------------------------------------
    qrows, qfiles = [], sorted(glob.glob(os.path.join(REJECTED, '*quarantine*.jsonl')))
    for f in qfiles:
        for r in load_jsonl(f):
            r['_file'] = os.path.basename(f)
            qrows.append(r)

    classes = collections.Counter()
    for r in qrows:
        for x in ((r.get('_quarantine') or {}).get('reasons') or ['(none recorded)']):
            classes[x[:90]] += 1

    sft = {}
    for name in ('train_sft.jsonl', 'val_sft.jsonl'):
        sft[name] = load_jsonl(os.path.join(SFT, name))

    residual = {}
    for name, rows in sft.items():
        idx = collections.defaultdict(list)
        for i, r in enumerate(rows):
            idx[norm(r.get('instruction'))].append(i)
        hits = [q for q in qrows if norm(q.get('question_sw')) in idx]
        residual[name] = {'rows': len(rows), 'quarantined_rows_still_present': len(hits),
                          'by_file': dict(collections.Counter(q['_file'] for q in hits))}

    # ---- B. defect-assertion exposure (A BOUND, NOT A COUNT) -----------------------------
    facts = json.load(open(FACTS, encoding='utf-8'))
    pats = []
    for key, v in facts.items():
        if not isinstance(v, dict):      # a few facts are bare strings, not objects
            continue
        for p in (v.get('wrong_patterns') or []):
            try:
                pats.append((key, p, re.compile(p, re.I)))
            except re.error:
                pass
    train = sft['train_sft.jsonl']
    flagged, per_fact = set(), collections.Counter()
    for i, r in enumerate(train):
        blob = f"{r.get('instruction','')} {r.get('output','')}"
        for key, _, rx in pats:
            if rx.search(blob):
                flagged.add(i)
                per_fact[key] += 1

    # ---- C/D. overlap and gate arithmetic ------------------------------------------------
    rows_of = {pid: probes[pid]['index_row_at_authoring'] for pid in probes}
    reaching = [p for p in probes if REACH[p] in REACHES]
    not_reaching = [p for p in probes if REACH[p] not in REACHES]
    reach_rows = {rows_of[p] for p in reaching}
    fail_rows = {rows_of[p] for p in not_reaching}

    overlap = [p for p in reaching if DEFECT_CLASS[p][0]]
    no_overlap = [p for p in reaching if not DEFECT_CLASS[p][0]]

    # ⛔ THE HEADROOM PREMISE IS SUPERSEDED AND ITS SIGN IS INVERTED.
    # "~6 questions of Gate 1 headroom" traces to the 87.9% (167/190) figure, which THIS
    # PROJECT'S OWN RECORD LATER CORRECTED. PROGRESS.md: "v15's IN-CORPUS gate metric, measured
    # honestly with the fixed scorer/cleanup, is 84.7% (161/190) -- below the operative 0.85
    # threshold... Every previously recorded v15 gate score (91.1%, 88.0%, 87.9%) was inflated
    # by the scorer bugs now fixed." gate_001_results.json records gate_passed: False.
    # run_eval.py compares with STRICT `>`, so 0.85 exactly is a FAIL.
    # CLAUDE.md line ~465 still advertises "first gate pass: 87.9%" and is STALE.
    GATE_N, GATE_SCORE, GATE_FLOOR = 190, 0.847, 0.85
    correct = 161
    floor_n = 162                       # smallest k with k/190 > 0.85 (161/190 = 0.8474)

    blob = {
        'measured': '2026-09-24',
        'harness': 'eval/retrain/measure_retrain_case.py',
        'caveats_at_the_front': [
            'BUCKET-E IS 14 AUTHORED PROBES, OUTCOME-CONDITIONED ON FAILURE. It establishes the '
            'failure profile of rows already known to be wrong and says NOTHING about the '
            'corpus generally (R22). No figure here is a corpus-wide rate.',
            '14 PROBES = 12 DISTINCT INDEX ROWS. ext_08/09/11 share row 168 and all SUCCEEDED, '
            'so redundancy inflates the REACH side. Quote the distinct-row figures.',
            'ext_31 IS A LIVE CONTENT DEFECT AND IS OUT OF SCOPE OF THIS DECISION. Index row 86 '
            'says "designated representative from existing staff"; the live reply said "must '
            'hire a safety officer above N employees". Fix it regardless of the retrain '
            'outcome -- it is wrong in production today.',
            'THE REACH NUMBERS ARE TRANSCRIBED FROM A KAGGLE CONSOLE. The per-probe artifact is '
            'not yet in the repo, so everything downstream is PROVISIONAL under R18.',
        ],
        'A_residual_quarantine_exposure': {
            'quarantine_files': len(qfiles),
            'quarantined_rows_total': len(qrows),
            'distinct_defect_classes_recorded': len(classes),
            'defect_classes': dict(classes.most_common()),
            'sft': residual,
        },
        'B_defect_assertion_exposure_BOUND': {
            'train_rows': len(train),
            'rows_matching_any_wrong_pattern': len(flagged),
            'pct_of_train': round(100.0 * len(flagged) / len(train), 2),
            'patterns_applied': len(pats),
            'top_facts': dict(per_fact.most_common(12)),
            'why_this_is_a_bound_not_a_count':
                'wrong_patterns are known OVER-BROAD (2026-09-23 language scan: 200 hits, ~29% '
                'guarding working text) and known BLIND (2026-09-24: service-levy patterns '
                'require a string that appears only in the question; OSHA_penalties guards '
                '"miezi 6" while the live defect was "miezi 12 hadi 24"). Treat as an '
                'order-of-magnitude bound in BOTH directions.',
        },
        'C_bucket_e_overlap': {
            'probes': len(probes),
            'distinct_index_rows': len(set(rows_of.values())),
            'reaching_probes': len(reaching),
            'reaching_distinct_rows': len(reach_rows),
            'not_reaching_probes': len(not_reaching),
            'not_reaching_distinct_rows': len(fail_rows),
            'reach_rate_by_probe_pct': round(100.0 * len(reaching) / len(probes), 1),
            'reach_rate_by_distinct_row_pct': round(100.0 * len(reach_rows)
                                                    / len(set(rows_of.values())), 1),
            'reaching_AND_in_a_quarantined_defect_class': {
                'probes': overlap, 'n_probes': len(overlap),
                'distinct_rows': sorted({rows_of[p] for p in overlap}),
                'n_distinct_rows': len({rows_of[p] for p in overlap})},
            'reaching_but_NO_quarantined_defect_class': {
                'probes': no_overlap, 'n_probes': len(no_overlap),
                'distinct_rows': sorted({rows_of[p] for p in no_overlap}),
                'n_distinct_rows': len({rows_of[p] for p in no_overlap})},
            'not_reaching_in_a_quarantined_defect_class':
                [p for p in not_reaching if DEFECT_CLASS[p][0]],
            'per_probe': {p: {'reach': REACH[p], 'index_row': rows_of[p],
                              'defect_class': DEFECT_CLASS[p][0],
                              'why': DEFECT_CLASS[p][1],
                              'retrain_reachable': RETRAIN_REACHABLE.get(p, ('n/a -- did not '
                                                                            'reach context', ''))[0],
                              'retrain_why': RETRAIN_REACHABLE.get(p, ('', ''))[1]}
                          for p in sorted(probes)},
        },
        'D_gate_cost': {
            'gate_corpus_n': GATE_N,
            'last_pass_score': GATE_SCORE,
            'questions_correct_at_last_pass': correct,
            'floor_pct': GATE_FLOOR,
            'questions_needed_to_hold_the_floor': floor_n,
            'headroom_questions': correct - floor_n,          # NEGATIVE = currently failing
            'one_question_is_pct': round(100.0 / GATE_N, 2),
            'gate_currently_passes': correct > GATE_FLOOR * GATE_N,
            'measured_on': '2026-07-14 Kaggle eval.py re-run; NO gate run since',
            'note': 'THE SIGN IS INVERTED RELATIVE TO THE "~6 QUESTIONS OF HEADROOM" PREMISE. '
                    'There is no headroom: the last honest measurement is ONE QUESTION BELOW '
                    'the floor, and gate_001_results.json records gate_passed: False. The '
                    '87.9%/91.1%/88.0% figures were all inflated by scorer bugs since fixed, '
                    'and CLAUDE.md still advertises 87.9% as a pass.',
            'the_larger_problem': 'NO GATE HAS BEEN RUN SINCE 2026-07-14. Every content and '
                                  'index fix shipped since -- the whole verification arc, the '
                                  'clean 34/34 guard sweep, today\'s regen -- has an UNMEASURED '
                                  'effect on Gate 1. The retrain is being scoped against a '
                                  'baseline two and a half months stale, and the cheapest '
                                  'action available is to re-run the gate on the current build '
                                  'before deciding anything.',
            'granularity': f'1 question = {round(100.0 / GATE_N, 2)}pp. A retrain whose '
                           f'expected effect is under ~2 questions is not distinguishable from '
                           f'noise at this corpus size.',
        },
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    c = blob['C_bucket_e_overlap']
    print('A. RESIDUAL QUARANTINE EXPOSURE')
    print(f"   {len(qrows)} quarantined rows, {len(classes)} distinct defect classes, "
          f"{len(qfiles)} files")
    for k, v in residual.items():
        print(f"   {k:<16} {v['rows']:>5} rows   still-present quarantined: "
              f"{v['quarantined_rows_still_present']}")
    print()
    print('B. DEFECT-ASSERTION EXPOSURE (BOUND, not a count)')
    print(f"   {len(flagged)}/{len(train)} train rows match a wrong_pattern "
          f"({blob['B_defect_assertion_exposure_BOUND']['pct_of_train']}%), "
          f"{len(pats)} patterns")
    print()
    print('C. BUCKET-E OVERLAP WITH THE CORPUS CORRECTIONS')
    print(f"   reach: {c['reaching_probes']}/{c['probes']} probes "
          f"({c['reach_rate_by_probe_pct']}%)  ->  "
          f"{c['reaching_distinct_rows']}/{c['distinct_index_rows']} DISTINCT ROWS "
          f"({c['reach_rate_by_distinct_row_pct']}%)")
    print(f"   reaching AND in a quarantined class : "
          f"{c['reaching_AND_in_a_quarantined_defect_class']['n_probes']} probes / "
          f"{c['reaching_AND_in_a_quarantined_defect_class']['n_distinct_rows']} distinct rows")
    print(f"   reaching but NO quarantined class   : "
          f"{c['reaching_but_NO_quarantined_defect_class']['n_probes']} probes / "
          f"{c['reaching_but_NO_quarantined_defect_class']['n_distinct_rows']} distinct rows")
    print(f"   not-reaching in a quarantined class : "
          f"{len(c['not_reaching_in_a_quarantined_defect_class'])}")
    print()
    print('D. GATE COST')
    d = blob['D_gate_cost']
    print(f"   {d['questions_correct_at_last_pass']}/{d['gate_corpus_n']} at last pass; floor "
          f"needs {d['questions_needed_to_hold_the_floor']}; HEADROOM "
          f"{d['headroom_questions']} questions (1 question = {d['one_question_is_pct']}pp)")
    print()
    print(f'[saved] {os.path.relpath(OUT, REPO)}')


if __name__ == '__main__':
    main()

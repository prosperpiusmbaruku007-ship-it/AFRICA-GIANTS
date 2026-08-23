# -*- coding: utf-8 -*-
"""Re-run the 2026-08-16 coverage measurement against CURRENT state.

WHY THIS EXISTS. The 2026-08-16 readiness assessment rests on one number —
`scratch/coverage_gap_2026_08_16.json`: twelve questions from an ordinary duka owner's month,
**12/12 passed the OOC classifier, 0/12 took a deterministic route, 0/12 had a fact behind
them**. That number is now seven days old and three things have shipped that could move it
(a presumptive-tax engine, a business-licence renewal fact, routing gaps A+B). The pilot
re-derivation must not quote the old figure — R18 instance 4 is exactly the shape of quoting a
number nobody re-derived.

WHAT IT MEASURES, per row, all three columns re-derived from live repo code:

  1. `ooc_classifier`   — chike.classification.classify over config-resolved phrase lists
                          (R14: the same union modal_app.py builds).
  2. `deterministic_route` — chike.decomposition.decompose_query then routing.detect_intent on
                          each part. This is Orchestrator.route's own logic (orchestrator.py:203
                          calls detect_intent and nothing else), so it needs no model, no GPU
                          and no network.
  3. `has_fact`         — TWO STAGES, because one is not enough. The real path is an e5
                          embedding lookup, which cannot run here (local network blocks the
                          e5-base download). So:
                            (a) a lexical anchor scan, REGEX WITH WORD BOUNDARIES, over
                                locked_facts values and the RAG index rows; then
                            (b) a hand-written `answers` adjudication per row — does any hit
                                actually ANSWER the question, or does it merely contain the
                                word? The reason is recorded inline, per row.

  WHY STAGE (b) IS NOT OPTIONAL — THIS HARNESS'S FIRST VERSION GOT IT WRONG. v1 used bare
  substring matching with no adjudication and reported **7 of 12 covered**. Three of those
  seven were false:
    * `tin` matched inside `lis-TIN-g`, `conduc-TIN-g` — 29 locked facts, none about TINs;
    * `mobile money` matched ONLY `gn487a_prohibited_activity_2` — a prohibition on non-citizens,
      not an answer about tax on mobile-money receipts. The 2026-08-16 baseline had already
      adjudicated this exact hit as NOT coverage and scored it False;
    * `ukaguzi` matched OSHA's annual workplace inspection, not a TRA audit visit.
  And a fourth was wrong in the other direction: the licence FEE and licence RENEWAL rows both
  matched `business_licence_expiry_30_june`, but that fact answers the renewal DATE only — the
  fee was left uncovered on purpose (council-by-council). Corrected number: **3 of 12.**

  That is the presence-not-conclusion pattern committed INSIDE the instrument built to measure
  coverage, which is worth stating plainly rather than quietly fixing.

  THE REMAINING BOUND, even after (b): a fact being in the corpus is not retrieval reaching it
  at top-3. `has_fact` stays an UPPER BOUND on coverage throughout.

Artifact: eval/results/coverage_12_rerun.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

from chike import classification, decomposition, routing          # noqa: E402

BASELINE = os.path.join(REPO, 'scratch', 'coverage_gap_2026_08_16.json')
LOCKED = os.path.join(REPO, 'scripts', 'locked_facts.json')
INDEX = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
OUT = os.path.join(REPO, 'eval', 'results', 'coverage_12_rerun.json')

# One entry per baseline row, in baseline order.
#   `anchors` — REGEX, word-bounded, from the topic's own vocabulary rather than from any fact's
#               wording, so they cannot be tuned to produce a hit. Stage (a).
#   `answers` — the adjudication. Stage (b). True only when a hit ANSWERS the question asked.
#   `why`     — the reason, so a later reader can disagree with the verdict rather than the
#               number. Every False carries what the near-miss was.
ROWS = [
    # 0 — presumptive, 30M turnover
    dict(anchors=[r'\bmakadirio\b', r'\bmakisio\b', r'\bpresumptive\b'], answers=True,
         why='presumptive_tax_bands_2022 + ceiling + exclusions carry the whole regime.'),
    # 1 — presumptive, micro band (sub-4M is the commonest duka tax)
    dict(anchors=[r'\bmakadirio\b', r'\bmakisio\b', r'\bpresumptive\b'], answers=True,
         why='same three facts; the sub-4M band is stated explicitly (hadi 4,000,000 = TZS 0).'),
    # 2 — business licence FEE
    dict(anchors=[r'leseni ya biashara', r'business licen[cs]e'], answers=False,
         why='hits are business_licence_expiry_30_june (the renewal DATE) and two GN487A '
             'facts. The FEE was left uncovered on purpose — collection is council-by-council. '
             'A date is not a price.'),
    # 3 — business licence RENEWAL date
    dict(anchors=[r'leseni ya biashara', r'business licen[cs]e'], answers=True,
         why='business_licence_expiry_30_june answers it directly and nationally.'),
    # 4 — LGA service levy
    dict(anchors=[r'ushuru wa huduma', r'service levy', r'\bhalmashauri\b'], answers=False,
         why='scoped 2026-08-16 as cap-national/rate-council; bound only, never an amount, '
             'and not written.'),
    # 5 — market stall dues
    dict(anchors=[r'ushuru wa soko', r'\bgenge\b', r'market stall'], answers=False,
         why='council by-law across 180+ LGAs; adjudicated not coverable for amounts.'),
    # 6 — fire safety certificate
    dict(anchors=[r'\bzimamoto\b', r'fire safety', r'fire certificate'], answers=False,
         why='zero facts, unchanged since the baseline.'),
    # 7 — weights and measures
    dict(anchors=[r'\bvipimo\b', r'\bmizani\b', r'weights and measures'], answers=False,
         why='zero facts, unchanged since the baseline.'),
    # 8 — withholding tax on shop rent
    dict(anchors=[r'kodi ya pango', r'rent withholding', r'withholding tax on rent'],
         answers=False,
         why='wht_deadline exists; the 10% rent rate does not. Unchanged.'),
    # 9 — TIN registration process
    dict(anchors=[r'\bTIN\b', r'namba ya mlipakodi', r'taxpayer identification'], answers=False,
         why='word-bounded, only two hits and neither is about getting a TIN: '
             'vat_withholding_certificate_timing and brela_partnership_registration mention one '
             'in passing. v1 substring-matched 29 facts via lis-TIN-g / conduc-TIN-g.'),
    # 10 — TRA audit at the shop
    dict(anchors=[r'ukaguzi wa TRA', r'TRA audit', r'\baudit\b'], answers=False,
         why='no hits at all under word boundaries. v1 matched OSHA\'s annual workplace '
             'inspection (ukaguzi) — a different regulator and a different event.'),
    # 11 — tax on mobile-money receipts
    dict(anchors=[r'mobile money', r'\bmiamala\b', r'pesa kwa simu'], answers=False,
         why='only gn487a_prohibited_activity_2 — a prohibition on non-citizens, not a tax '
             'answer. The 2026-08-16 baseline adjudicated this same hit as not coverage.'),
]


def corpus_texts():
    """Every string a lexical anchor could match: locked_facts values + the RAG index rows."""
    with open(LOCKED, encoding='utf-8') as f:
        locked = json.load(f)
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    lf = []
    for key, val in locked.items():
        if key == '_meta':
            continue
        # A fact may be a bare string or a dict with a value/note; flatten either shape.
        lf.append(f'{key}: {json.dumps(val, ensure_ascii=False)}')
    return lf, [str(r) for r in index]


def main():
    with open(BASELINE, encoding='utf-8') as f:
        base = json.load(f)
    rows_in = base['rows']
    assert len(rows_in) == 12, f'baseline has {len(rows_in)} rows, expected 12'
    assert len(ROWS) == 12, 'ROWS must be 1:1 with the baseline rows'

    locked_texts, index_texts = corpus_texts()

    ooc_phrases, in_scope_phrases = classification.resolve_phrases(
        classification.load_local_config())

    rows_out = []
    for row, spec in zip(rows_in, ROWS):
        q = row['question']

        in_scope = classification.classify(q, ooc_phrases, in_scope_phrases)

        parts = decomposition.decompose_query(q)
        intents = [routing.detect_intent(p) for p in parts]
        route = next((i for i in intents if i != 'none'), 'none')

        pat = re.compile('|'.join(spec['anchors']), re.IGNORECASE)
        hits_locked = [t for t in locked_texts if pat.search(t)]
        hits_index = [t for t in index_texts if pat.search(t)]
        lexical = bool(hits_locked or hits_index)
        # Stage (b) can only REMOVE a row, never add one: a fact that does not exist lexically
        # cannot be adjudicated into existence. This assert exists so that inversion cannot
        # pass silently.
        assert not (spec['answers'] and not lexical), (
            f"{row['topic']}: adjudicated as answered but nothing matched")
        has_fact = spec['answers'] and lexical

        rows_out.append({
            'topic': row['topic'],
            'question': q,
            'baseline': {
                'ooc_classifier': row['ooc_classifier'],
                'deterministic_route': row['deterministic_route'],
                'has_fact': row['has_fact'],
            },
            'now': {
                'ooc_classifier': 'pass_to_model' if in_scope else 'refused',
                'deterministic_route': route,
                'decomposed_parts': parts,
                'part_intents': intents,
                'lexical_hit': lexical,
                'answers_the_question': has_fact,
                'adjudication': spec['why'],
                'anchors': spec['anchors'],
                'locked_fact_hits': [t.split(':')[0] for t in hits_locked][:8],
                'index_hits': [t[:110] for t in hits_index][:6],
                'n_locked_hits': len(hits_locked),
                'n_index_hits': len(hits_index),
            },
            'changed': {
                'route': route != row['deterministic_route'],
                'has_fact': has_fact != row['has_fact'],
            },
        })

    summary = {
        'n': len(rows_out),
        'passed_ooc_classifier': sum(1 for r in rows_out
                                     if r['now']['ooc_classifier'] == 'pass_to_model'),
        'took_a_deterministic_route': sum(1 for r in rows_out
                                          if r['now']['deterministic_route'] != 'none'),
        'lexical_hit_only_NOT_coverage': sum(1 for r in rows_out if r['now']['lexical_hit']),
        'have_a_fact_behind_them_UPPER_BOUND': sum(1 for r in rows_out
                                                   if r['now']['answers_the_question']),
        'baseline_2026_08_16': {
            'passed_ooc_classifier': base['passed_ooc_classifier'],
            'took_a_deterministic_route': base['took_a_deterministic_route'],
            'have_a_fact_behind_them': base['have_a_fact_behind_them'],
            'locked_facts_total': base['locked_facts_total'],
            'rag_index_total': base['rag_index_total'],
        },
        'locked_facts_total': len(locked_texts),
        'rag_index_total': len(index_texts),
    }

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/coverage/rerun_coverage_12.py',
        'baseline_artifact': 'scratch/coverage_gap_2026_08_16.json',
        'method': 'OOC + route re-derived from live repo code (no model, no network). has_fact '
                  'is TWO-STAGE: word-bounded regex anchors, then a per-row adjudication of '
                  'whether any hit ANSWERS the question. Still an UPPER BOUND: it proves a '
                  'fact exists in the corpus, NOT that retrieval reaches it at top-3.',
        'v1_defect': 'The first version of this harness used bare substring matching with no '
                     'adjudication and reported 7/12 covered. Three were false (tin inside '
                     'lis-TIN-g; mobile money matching only a GN487A prohibition; ukaguzi '
                     'matching OSHA inspections) and a fourth conflated the licence renewal '
                     'date with the licence fee. Corrected: 3/12. This is the '
                     'presence-not-conclusion pattern committed inside the coverage instrument '
                     'itself.',
        'summary': summary,
        'rows': rows_out,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print('\n--- per row (baseline -> now) ---')
    for r in rows_out:
        flag = '  <-- CHANGED' if (r['changed']['route'] or r['changed']['has_fact']) else ''
        print(f"  {r['topic'][:44]:<46} route {r['baseline']['deterministic_route']:>12} -> "
              f"{r['now']['deterministic_route']:<14} fact {str(r['baseline']['has_fact']):>5} -> "
              f"{str(r['now']['answers_the_question']):<5}{flag}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()

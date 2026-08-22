# -*- coding: utf-8 -*-
"""Fixture for the DISCARD-RATE measurement — extends SS8 across the fact path.

The question (nat_38's board item): when a CORRECT fact reaches context, how often does the
answer fail to use it? Every retrieval fix in ADR 0002 assumes right-content-in-context
produces right-answer. nat_38 shows that assumption is not free, and SS8 already showed 3 of 8
rows failing with correct facts placed directly in context — a floor on the rate.

THREE OUTCOMES ARE POSSIBLE PER ROW, and the third is why this is not just SS8 re-run:

  FORCEABLE  a fact in the index carries the answer -> force it, see whether the reply uses it.
  ABSENCE    NO fact in the index answers this question. It cannot be forced, and a row that
             answers correctly anyway is answering from model weights over an index GAP, not
             over a ranking failure. These must be excluded from the discard denominator or
             they inflate it.
  COMPUTE    the row now routes to the rules engine after ROUTING-GAP-A/B, so retrieval no
             longer decides it. Excluded, and the exclusion is itself a result.

R18: committed before its result is written up.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
INDEX = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
ADJ = os.path.join(REPO, 'eval', 'results',
                   'natural48_rerun_2026_08_17_adjudication.json')

# row -> (fact positions to force, grounding verdict from 2026-08-22, what the fact carries)
FORCEABLE = {
    'nat_26': ([146, 145], 'PARTIAL', 'VAT 100M/6mo (was retrieved) + 200M/12mo (was not)'),
    'nat_27': ([13], 'UNGROUNDED', 'VAT standard rate 18% — never retrieved, answered from weights'),
    'nat_31': ([20], 'GROUNDED', 'GN487A non-citizen fine — control, already retrieved'),
    'nat_32': ([210], 'GROUNDED', 'shareholder-vs-operator — control'),
    'nat_34': ([114, 130], 'GROUNDED', 'company reg fee + name reservation — control'),
    'nat_36': ([57], 'UNGROUNDED', 'EFD threshold 11M — never retrieved, answered from weights'),
    'nat_39': ([69], 'GROUNDED', 'OSHA registers all workplaces — control'),
    'nat_40': ([68], 'PARTIAL', 'OSHA-vs-WCF distinction — the fact carrying the claim was NOT retrieved'),
    'nat_43': ([72], 'GROUNDED', 'GN605A sector variance — control'),
    'nat_44': ([16], 'GROUNDED', 'VAT withholding goods 3% — SS8 row, was CORRECT forced'),
    'nat_45': ([51], 'GROUNDED', 'WCF 7 working days — SS8 row, was CORRECT forced'),
    'nat_28': ([17, 79], 'GROUNDED', 'VAT withholding services 6% + certificate timing — SS8 row'),
    'nat_33': ([133, 134], 'GROUNDED', 'BRELA late fee + annual fee — SS8 row, was WRONG forced'),
}

ABSENCE = {
    'nat_37': 'No index fact states a receipt is required for EVERY transaction regardless of '
              'amount. The only on-topic row [58] says a small business is NOT always required '
              'to use an EFD. Searched 2026-08-22; nothing carries this claim.',
    'nat_38': 'No index fact states that a VAT-REGISTERED business must use an EFD regardless '
              'of turnover. [58] addresses small businesses and points the other way. This row '
              'scored CORRECT while its only on-topic context contradicted it — the finding '
              'that opened this measurement.',
    'nat_41': 'Recorded ABSENCE by the 2026-08-17 class analysis: the OSH Act s.16(2) '
              'register-BEFORE-operating fact never existed in the index.',
}

COMPUTE_NOW = {
    'nat_05': 'routes compute[sdl] after ROUTING-GAP-B',
    'nat_23': 'routes compute[nssf]+[sdl] after ROUTING-GAP-A',
    'nat_24': 'routes compute[nssf]+[sdl]+[wcf] after ROUTING-GAP-B',
}


def main():
    with open(INDEX, encoding='utf-8') as f:
        texts = json.load(f)
    with open(ADJ, encoding='utf-8') as f:
        adj = json.load(f)
    by_id = {r['id']: r for r in adj['rows']}

    rows = []
    for rid, (positions, grounding, why) in FORCEABLE.items():
        src = by_id.get(rid, {})
        rows.append({
            'id': rid,
            'class': 'FORCEABLE',
            'question': src.get('question', ''),
            'verdict_2026_08_17': src.get('now', '?'),
            'grounding_2026_08_22': grounding,
            'forced_fact_positions': positions,
            'forced_facts': [texts[p] for p in positions],
            'why': why,
        })
    for rid, why in ABSENCE.items():
        src = by_id.get(rid, {})
        rows.append({'id': rid, 'class': 'ABSENCE', 'question': src.get('question', ''),
                     'verdict_2026_08_17': src.get('now', '?'), 'why': why,
                     'forced_facts': [], 'forced_fact_positions': []})
    for rid, why in COMPUTE_NOW.items():
        src = by_id.get(rid, {})
        rows.append({'id': rid, 'class': 'COMPUTE_NOW', 'question': src.get('question', ''),
                     'verdict_2026_08_17': src.get('now', '?'), 'why': why,
                     'forced_facts': [], 'forced_fact_positions': []})

    out = {
        'purpose': 'discard-rate measurement: when a correct fact reaches context, how often '
                   'is it not used?',
        'denominator_note': 'ONLY the FORCEABLE rows belong in the discard denominator. '
                            'ABSENCE rows have no fact to discard; COMPUTE_NOW rows no longer '
                            'depend on retrieval.',
        'counts': {'FORCEABLE': len(FORCEABLE), 'ABSENCE': len(ABSENCE),
                   'COMPUTE_NOW': len(COMPUTE_NOW)},
        'rows': rows,
    }
    path = os.path.join(HERE, 'discard_rows.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'wrote {path}')
    print(json.dumps(out['counts'], indent=2))
    for r in rows:
        print(f"  {r['class']:<12} {r['id']:<8} {r['verdict_2026_08_17']:<9} "
              f"{len(r['forced_facts'])} fact(s)")


if __name__ == '__main__':
    main()

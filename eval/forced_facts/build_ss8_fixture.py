# -*- coding: utf-8 -*-
"""Build the committed SS8 forced-fact fixture from the deployed RAG index.

R18: this generator, the fixture it produces, and the runner that consumes it are all
committed BEFORE any result is written up, so the instrument can be re-read later.

The fixture stores the fact TEXT verbatim, not index positions: positions shift whenever
the index is regenerated (R15), and a fixture that silently points at different facts after
a regen is exactly the stale-pin failure this project has already had once. Positions are
kept alongside as provenance only.

Fact selection reproduces the 'facts forced' column of the provisional 2026-08-22 SS8 table
so the v16 re-run is comparable row-for-row.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
INDEX = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')

# row -> (question, [index positions], why these facts)
ROWS = [
    ('nat_44',
     'nimeuzia wakala wa serikali bidhaa je watanikata asilimia ngapi ya vat',
     [16],
     'vat withholding goods (3%)'),
    ('nat_45',
     'mfanyakazi ameumia jana nina siku ngapi za kupeleka taarifa ya ajali',
     [51],
     'wcf accident reporting deadline (7 working days)'),
    ('nat_41',
     'nimefungua karakana mpya nina muda gani wa kusajili sehemu ya kazi',
     [219, 52],
     'OSHA registration-before-opening + no employee-count threshold'),
    ('nat_28',
     'nimefanya kazi ya ushauri kwa taasisi ya serikali wamesema watakata vat je '
     'asilimia ngapi na cheti nitapata lini',
     [17, 79],
     'vat withholding services (6%) + certificate timing'),
    ('nat_05',
     'nimenunua mashine za kiwanda za milioni 50 na nina wafanyakazi 12 hiyo ya '
     'mafunzo nitalipa asilimia tatu na nusu ya nini',
     [5],
     'sdl rate (3.5% of payroll) — the wrong-base trap'),
    ('nat_33',
     'sijapeleka ritani ya kampuni yangu miezi saba sasa nitalipa faini kiasi gani '
     'na ada yenyewe ni ngapi',
     [133, 134],
     'BRELA late fee (2,500/month) + annual return fee (22,000)'),
    ('nat_24',
     'tuko na watu 9 tu mishahara milioni 4 kwa mwezi nilipe nini kati ya ile ya '
     'mafunzo ya fidia na ya uzeeni',
     [7, 10, 66],
     'sdl threshold (10+) + NSSF 20% + WCF 0.5%'),
    ('nat_23',
     'nina wafanyakazi 12 mishahara jumla milioni 5.5 nitalipa ngapi kwenye ile ya '
     'mafunzo na ile ya uzeeni',
     [5, 10],
     'sdl rate + NSSF rate'),
]

# The provisional 2026-08-22 outcomes, carried in the fixture so the re-run can be
# compared row-for-row without anyone having to re-read a prose table.
PROVISIONAL = {
    'nat_44': 'CORRECT', 'nat_45': 'CORRECT', 'nat_41': 'CORRECT', 'nat_28': 'CORRECT',
    'nat_05': 'PARTIAL', 'nat_33': 'WRONG', 'nat_24': 'WRONG', 'nat_23': 'WRONG',
}

# expected_behavior verbatim from eval/accuracy_gate/edge_probe_natural_048.jsonl,
# so the adjudication rubric travels with the fixture.
def _rubrics():
    path = os.path.join(REPO, 'eval', 'accuracy_gate', 'edge_probe_natural_048.jsonl')
    out = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            out[row['id']] = row.get('expected_behavior', '')
    return out


def main():
    with open(INDEX, encoding='utf-8') as f:
        facts = json.load(f)
    rubrics = _rubrics()

    rows = []
    for row_id, question, positions, why in ROWS:
        rows.append({
            'id': row_id,
            'question': question,
            'forced_facts': [facts[i] for i in positions],
            'forced_fact_positions': positions,
            'forced_fact_rationale': why,
            'expected_behavior': rubrics.get(row_id, ''),
            'provisional_2026_08_22_outcome': PROVISIONAL[row_id],
        })

    out = {
        'purpose': ('SS8 forced-fact re-measurement on the live v16 pipeline. Retrieval is '
                    'replaced by a constant; everything else — classifier, decomposition, '
                    'routing, rules engines, prompt build, generation, cleanup — is the '
                    'production path untouched.'),
        'index_source': 'chike-inference/rag_facts_text.json',
        'index_fact_count': len(facts),
        'supersedes': ('the provisional 2026-08-22 table produced by an uncommitted harness '
                       'whose own description says it ran the non-live v15 arm'),
        'rows': rows,
    }
    path = os.path.join(HERE, 'ss8_rows.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'wrote {path}: {len(rows)} rows, index has {len(facts)} facts')
    for r in rows:
        print(f"  {r['id']}: {len(r['forced_facts'])} fact(s) — {r['forced_fact_rationale']}")


if __name__ == '__main__':
    main()

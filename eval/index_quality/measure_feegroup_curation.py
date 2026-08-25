# -*- coding: utf-8 -*-
"""ARM A3: consolidate the WHOLE fee-schedule class, not just trademark. And why that is the target.

WHAT THE TRADEMARK ARM SHOWED (eval/results/feerow_curation.json, same day). Removing all 17
trademark fee rows moved the buried anchor up on **6 of 7** questions -- and brought **0** of them
into the top-3. The movement was almost exactly the count of removed rows that outranked each
anchor (`nat_23`: 86 -> 69, a delta of exactly 17 -- **every single trademark fee row outranked the
SDL rate fact for a question about the SDL rate**). So the rows really are crowding; there are just
far more of them than seventeen.

**66 of 221 index rows (30%) are `key: number` fee-schedule rows.** And `nat_23`'s top-3 after the
trademark deletion is still three *company registration fee* rows, for a question about staff levies.

⛔ AND THE CLASS IS WORSE THAN CROWDING -- FOUR OF THESE ROWS ARE TRACEABLE SOURCES OF NAMED
DEFECTS. This is the finding that makes curation worth doing rather than merely tidy:

  [167] `registration certificate processing time new: 1 days`  -> `nat_41`'s fabricated "siku 1"
        for OSHA registration. It is a BRELA row. [155] says 3 days for the same-sounding thing.
  [120] `company registration fee 3: 260,000 TZS`               -> `nat_05`'s fabricated BRELA fee
        answering an SDL question (already recorded).
  [209] `contribution rate emplyees: 10 %`                      -> the NSSF 10%-vs-20% collapse.
        Note the typo in the key. A context-free half-rate with no "of 20% total" beside it.
  [157] `beneficial owner information penalty maximum: 10000000 TZS` -> an unformatted ten-million
        with no separators. ⚠️ HYPOTHESIS ONLY, not a claim: `pic_11` believes the presumptive
        ceiling is "milioni 10". Nobody has tested whether this row feeds that belief.

**They are simultaneously (a) highly retrievable on any numeric question, (b) context-free, and
(c) traceable to specific wrong answers.** That is the argument for consolidation: a grouped
passage carries the same figures WITH the context that says what they are about.

⚠️ R25, AND IT IS WHY THIS IS CONSOLIDATION AND NOT DELETION. The trademark arm's C1 control
showed the cost directly: deletion removed the answer from every trademark-fee question, and
consolidation preserved one of the two the baseline answered while losing the other. **The property
that makes a short numeric row crowd out real facts is the same property that makes it answer a
numeric question well.** So consolidation is a TRADE, not a free win, and the controls below exist
to price it rather than to bless it.

CONTROLS (R26's clean case, which is the half that gets skipped):
  nat_34 is adjudicated **CORRECT and GROUNDED** off the company registration ladder ("95,000 +
  50,000"). If consolidation breaks it, the arm has traded a wrong answer for a wrong answer.
  Three verbatim trademark-fee questions from datasets/. And `nat_43` at rank 1 as the R24
  baseline check -- if the unvaried arm does not reproduce its recorded state, every number is void.

R18: committed before it runs.
Artifact: eval/results/feegroup_curation.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'eval', 'results', 'feegroup_curation.json')
INDEX_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
INDEX_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
NAT48 = os.path.join(REPO, 'eval', 'accuracy_gate', 'edge_probe_natural_048.jsonl')
PASSAGE_PREFIX = 'passage: '
TOP_K = 3

# --- Groups identified by KEY PREFIX, resolved to positions at runtime and asserted. -----------
GROUPS = {
    'trademark_fees': {
        'prefixes': ['trademark fee for '],
        'text': (
            'Ada za alama ya biashara (trademark) BRELA: kusajili alama moja TZS 60,000; kuhuisha '
            '(renewal) TZS 30,000; mfululizo wa alama — ya kwanza TZS 60,000, zinazofuata TZS '
            '30,000; kuhuisha mfululizo — ya kwanza TZS 30,000, zinazofuata TZS 10,000; taarifa '
            'ya pingamizi TZS 60,000; kujibu pingamizi TZS 50,000; kusikiliza pingamizi TZS '
            '70,000; maelezo ya uamuzi TZS 50,000; kusajili mmiliki mpya TZS 50,000; kubadili '
            'mmiliki au mtumiaji TZS 50,000; kubadili anwani ya biashara TZS 20,000; kuvunja '
            'ubia TZS 50,000; kurejeshewa ada TZS 30,000; ada ya nyongeza kanuni 54 TZS 30,000; '
            'kiingizo kingine chochote TZS 10,000.'),
    },
    'company_registration_ladder': {
        'prefixes': ['company registration fee ', 'company share value threshold '],
        # A LADDER belongs in one passage anyway: the fee is meaningless without the share-capital
        # band it attaches to, and split across 14 rows the bands and fees can be paired wrongly.
        'text': (
            'Ada ya kusajili kampuni BRELA hutegemea thamani ya hisa (share capital): hadi TZS '
            '1,000,000 ni TZS 95,000; zaidi ya TZS 1,000,000 hadi TZS 5,000,000 ni TZS 175,000; '
            'zaidi ya TZS 5,000,000 hadi TZS 20,000,000 ni TZS 260,000; zaidi ya TZS 20,000,000 '
            'hadi TZS 50,000,000 ni TZS 290,000; zaidi ya TZS 50,000,000 ni TZS 440,000. Kampuni '
            'isiyo na mtaji wa hisa ni TZS 300,000. Kuhifadhi jina (name reservation) ni TZS '
            '50,000 na kubadili jina ni TZS 22,000.'),
    },
    'brela_filing_fees': {
        'prefixes': ['memorandum articles', 'document acceptance', 'document certification',
                     'file search', 'certified copy certificate', 'stamp duty per copy',
                     'stamp duty form', 'document filing fee section', 'balance sheet filing fee',
                     'late filing penalty monthly fee section'],
        'text': (
            'Ada nyingine za kuwasilisha nyaraka BRELA: kuwasilisha memorandum na articles ni TZS '
            '22,000; stempu kwa kila nakala ya memorandum TZS 10,000; fomu 14B TZS 1,200; '
            'kupokea/kusajili nyaraka TZS 22,000; kuthibitisha nyaraka kwa ukurasa TZS 3,000; '
            'kutafuta faili TZS 3,000 na ripoti ya utafutaji TZS 22,000; nakala iliyothibitishwa '
            'ya cheti cha usajili TZS 4,000. Kampuni ya kigeni (kifungu 12): kuwasilisha nyaraka '
            'USD 220, mizania USD 220, na faini ya kuchelewa USD 25 kwa mwezi.'),
    },
}

ANCHORS = {
    'nat_05': ('kiwango cha mafunzo ni asilimia tatu na nusu', 'SDL rate'),
    'nat_23': ('kiwango cha mafunzo ni asilimia tatu na nusu', 'SDL rate'),
    'nat_28': ('vat withholding services: VAT withholding on services is 6%', 'services WHT'),
    'nat_33': ('ada ya kuwasilisha ritani (annual return) ya kampuni kila mwaka ni TZS 22,000',
               'BRELA annual return fee'),
    'nat_43': ('sekta 16 na sekta ndogo 46', 'C2 BASELINE CONTROL — recorded FIXED at rank 1'),
    'nat_44': ('vat withholding goods: VAT withholding on goods is 3%', 'goods WHT'),
    'nat_45': ('wcf accident reporting deadline: 7 working days', 'WCF accident deadline'),
}

# --- C1 controls. Each states WHAT MUST STILL BE FINDABLE, so a pass is not merely "something
# --- fee-shaped appeared" (which the trademark arm's weaker control could not distinguish).
CONTROLS = [
    {'q': 'Nataka kusajili kampuni yenye mtaji wa hisa milioni moja, ada ni shilingi ngapi na '
          'kuhifadhi jina ni ngapi?',
     'must_contain': ['95,000', '50,000'],
     'why': 'nat_34 is adjudicated CORRECT and GROUNDED off this ladder. If consolidation breaks '
            'it, the arm traded one wrong answer for another.'},
    {'q': 'Hiyo ada ya marejesho ya alama ya biashara kuchelewa, ni shilingi ngapi hasa?',
     'must_contain': ['30,000'],
     'why': 'trademark renewal fee — answered in the BASELINE arm, so it must survive.'},
    {'q': 'Huyu Chike, hiki kiwango cha ada ya kuomba hati miliki ya biashara (trademark) ni '
          'elfu 50,000 TZS sio?',
     'must_contain': ['60,000'],
     'why': 'the trademark arm LOST this one. Recorded so the loss is priced, not hidden.'},
    {'q': 'Ada ya kuwasilisha memorandum na articles of association ni shilingi ngapi?',
     'must_contain': ['22,000'],
     'why': 'BRELA filing fee — must survive its own consolidation.'},
]


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    texts = json.load(open(INDEX_TEXT, encoding='utf-8'))
    emb = np.load(INDEX_EMB)
    assert emb.shape[0] == len(texts), (emb.shape, len(texts))
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
    nat = {r['id']: r for r in (json.loads(l) for l in open(NAT48, encoding='utf-8') if l.strip())}
    model = SentenceTransformer('intfloat/multilingual-e5-base')

    absorbed, group_report = set(), {}
    for name, g in GROUPS.items():
        idx = [i for i, t in enumerate(texts)
               if any(t.lower().startswith(p.lower()) for p in g['prefixes'])]
        assert idx, f'group {name} matched ZERO rows — the index changed shape'
        absorbed |= set(idx)
        group_report[name] = {'rows_absorbed': len(idx), 'indices': idx,
                              'replacement_chars': len(g['text'])}
    keep = [i for i in range(len(texts)) if i not in absorbed]

    new_texts = [texts[i] for i in keep] + [g['text'] for g in GROUPS.values()]
    new_vecs = model.encode([PASSAGE_PREFIX + g['text'] for g in GROUPS.values()],
                            normalize_embeddings=True)
    new_emb = np.vstack([emb[keep], new_vecs])
    assert new_emb.shape[0] == len(new_texts)

    arms = {'A0_baseline': (texts, emb), 'A3_consolidate_all': (new_texts, new_emb)}

    rows = []
    for rid, (needle, why) in ANCHORS.items():
        q = nat[rid]['question']
        rec = {'id': rid, 'question': q, 'why': why, 'arms': {}}
        for name, (at, ae) in arms.items():
            hits = [i for i, t in enumerate(at) if needle in t]
            assert len(hits) == 1, f'{rid}/{name}: needle matched {len(hits)} rows'
            qv = model.encode([f'query: {q}'], normalize_embeddings=True)[0]
            sims = qv @ ae.T
            order = list(np.argsort(-sims))
            r = order.index(hits[0]) + 1
            rec['arms'][name] = {'anchor_rank': r, 'in_top_3': r <= TOP_K,
                                 'top_3': [at[int(i)][:75] for i in order[:TOP_K]]}
        rec['delta'] = (rec['arms']['A0_baseline']['anchor_rank']
                        - rec['arms']['A3_consolidate_all']['anchor_rank'])
        rows.append(rec)
        print(f"{rid}  base {rec['arms']['A0_baseline']['anchor_rank']:4d} -> "
              f"cons {rec['arms']['A3_consolidate_all']['anchor_rank']:4d}  "
              f"({rec['delta']:+d})  top3_now={rec['arms']['A3_consolidate_all']['in_top_3']}")

    controls = []
    for c in CONTROLS:
        rec = {'question': c['q'], 'must_contain': c['must_contain'], 'why': c['why'], 'arms': {}}
        for name, (at, ae) in arms.items():
            qv = model.encode([f"query: {c['q']}"], normalize_embeddings=True)[0]
            sims = qv @ ae.T
            order = list(np.argsort(-sims))
            top = [at[int(i)] for i in order[:TOP_K]]
            blob = ' || '.join(top)
            rec['arms'][name] = {'answerable': all(m in blob for m in c['must_contain']),
                                 'top_3': [t[:75] for t in top]}
        rec['preserved'] = (rec['arms']['A3_consolidate_all']['answerable']
                            or not rec['arms']['A0_baseline']['answerable'])
        rec['regressed'] = (rec['arms']['A0_baseline']['answerable']
                            and not rec['arms']['A3_consolidate_all']['answerable'])
        rec['gained'] = (not rec['arms']['A0_baseline']['answerable']
                         and rec['arms']['A3_consolidate_all']['answerable'])
        controls.append(rec)

    n43 = next(r for r in rows if r['id'] == 'nat_43')
    c2 = {'expected': 'nat_43 anchor at rank 1 in the BASELINE arm',
          'observed': n43['arms']['A0_baseline']['anchor_rank'],
          'baseline_reproduces_recorded_state': n43['arms']['A0_baseline']['anchor_rank'] == 1}
    assert c2['baseline_reproduces_recorded_state'], (
        'R24: the unvaried arm does not reproduce nat_43\'s recorded rank 1 — every number in '
        'this run would be about a system we do not ship')

    blob = {
        'measured': '2026-08-25',
        'harness': 'eval/index_quality/measure_feegroup_curation.py',
        'index_rows_before': len(texts), 'index_rows_after': len(new_texts),
        'rows_absorbed': len(absorbed), 'groups': group_report,
        'traceable_defect_sources_in_this_class': {
            'row_167_registration_certificate_processing_time_new_1_days': "nat_41's 'siku 1'",
            'row_120_company_registration_fee_3_260000': "nat_05's fabricated BRELA fee",
            'row_209_contribution_rate_emplyees_10pct': 'the NSSF 10%-vs-20% collapse (note the '
                                                        'typo in the key)',
            'row_157_beneficial_owner_penalty_10000000': 'HYPOTHESIS ONLY — untested as a source '
                                                          "for pic_11's 'milioni 10' belief",
        },
        'C2_baseline_control': c2,
        'summary': {
            'anchors': len(rows),
            'moved_up': sum(1 for r in rows if r['delta'] > 0),
            'entered_top_3': sum(1 for r in rows if r['arms']['A3_consolidate_all']['in_top_3']
                                 and not r['arms']['A0_baseline']['in_top_3']),
            'controls_regressed': sum(1 for c in controls if c['regressed']),
            'controls_gained': sum(1 for c in controls if c['gained']),
        },
        'rows': rows, 'C1_controls': controls,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    print(f"\nindex {len(texts)} -> {len(new_texts)} ({len(absorbed)} rows absorbed into "
          f"{len(GROUPS)})")
    print(f"moved up {blob['summary']['moved_up']}/{len(rows)}, "
          f"entered top-3 {blob['summary']['entered_top_3']}")
    for c in controls:
        flag = 'REGRESSED' if c['regressed'] else ('GAINED' if c['gained'] else 'ok')
        print(f"  C1 [{flag:9s}] base={c['arms']['A0_baseline']['answerable']} "
              f"cons={c['arms']['A3_consolidate_all']['answerable']}  {c['question'][:50]}")
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

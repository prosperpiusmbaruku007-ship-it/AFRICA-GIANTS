# -*- coding: utf-8 -*-
"""IS INDEX COMPOSITION A LEVER? Delete or consolidate the trademark fee rows and re-rank.

THE HYPOTHESIS, and it is the cheapest structural result available. Measured at 217 rows, short
`key: number` fee-shaped rows were **30.4% of the index** but took **58% of all top-3 slots** and
were **top-1 on half** of the 48 questions. Meanwhile the correct fact for seven failing rows sits
at rank **19-164**, and raising top_k from 3 to 9 reaches none of them. If short numeric rows are
crowding real facts out of the top-3, then **removing rows nobody asks about should promote facts
people do** — and index composition becomes a lever this project has never pulled.

⚠️ R25 APPLIED BEFORE THE CHANGE, NOT AFTER, and it changed the design:

  Q1. WHAT DEFECT DOES THIS REPAIR? Seventeen rows (index 96-112) are a trademark fee schedule --
      opposition notices, series-of-marks renewals, refund-of-fee. They are short, semantically
      thin and numerically flavoured, so they sit close to any question containing a magnitude.

  Q2. WHAT CORRECT OUTPUT COULD THIS DAMAGE? **This is where deletion lost.** Sweeping both
      corpora found **28 rows that DO ask trademark fee questions** -- renewal cost, late-renewal
      penalty, registration fee. All 28 are in `datasets/` (training); **ZERO are in `eval/`**.
      So deleting costs no MEASURED accuracy and still removes content a real user can ask for,
      and which the deployed adapter was trained to answer.

**Hence a third arm, and it is the one the evidence actually supports: CONSOLIDATE.** The problem
is that the fee schedule is SEVENTEEN SHORT ROWS competing for retrieval slots, not that its
content is worthless. Merging them into ONE row removes sixteen competitors while keeping every
figure answerable.

  A0  baseline      221 rows, exactly as deployed
  A1  delete        204 rows -- the 17 removed
  A2  consolidate   205 rows -- the 17 replaced by one row carrying all seventeen figures

**No re-embedding is needed for A0 or A1**: cosine similarity is per-row and independent, so
dropping rows cannot change any surviving row's score. A2 embeds exactly one new row, with the
build-time `passage: ` prefix (scripts/precompute_rag_embeddings.py:43) and the same e5-base
model production uses.

CONTROLS, because a control that only proves the new behaviour is over-broad by construction:
  C1  three real trademark-fee questions from the training corpus. Under A1 they MUST lose their
      answer; under A2 the consolidated row MUST be retrievable for them. This is R26's clean
      case -- the half that gets skipped.
  C2  `nat_43` was recorded FIXED to rank 1 after its ask-alignment rewrite. If the baseline arm
      does not reproduce that, the harness is measuring something other than production and every
      number below is void (R24).

R18: committed before it runs.
Artifact: eval/results/feerow_curation.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, 'eval', 'results', 'feerow_curation.json')

INDEX_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
INDEX_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
NAT48 = os.path.join(REPO, 'eval', 'accuracy_gate', 'edge_probe_natural_048.jsonl')
PASSAGE_PREFIX = 'passage: '          # scripts/precompute_rag_embeddings.py:43
TOP_K = 3

# --- The rows to curate. Identified by TEXT, never by a stored position (R18 instance 1). ------
FEE_ROW_NEEDLE = 'trademark fee for '

# --- The consolidated replacement. Every figure from the seventeen rows, in one passage.
# Ask-led rather than label-led, per CLAUDE.md's ask-alignment finding: it opens with the words a
# user would type (`alama ya biashara`, `ada`), not with the schedule's own heading.
CONSOLIDATED = (
    'Ada za alama ya biashara (trademark) BRELA/COSOTA: kusajili alama moja ni TZS 60,000; '
    'kuhuisha (renewal) ni TZS 30,000; mfululizo wa alama — alama ya kwanza TZS 60,000 na kila '
    'alama inayofuata TZS 30,000; kuhuisha mfululizo — ya kwanza TZS 30,000 na zinazofuata TZS '
    '10,000; taarifa ya pingamizi (opposition notice) TZS 60,000; kujibu pingamizi TZS 50,000; '
    'kusikiliza pingamizi TZS 70,000; maelezo ya uamuzi TZS 50,000; kusajili mmiliki mpya TZS '
    '50,000; kubadili mmiliki au mtumiaji (anwani ile ile) TZS 50,000; kubadili anwani ya '
    'biashara TZS 20,000; kuvunja ubia TZS 50,000; kurejeshewa ada TZS 30,000; ada ya nyongeza '
    'chini ya kanuni 54 TZS 30,000; kiingizo kingine chochote TZS 10,000.'
)

# --- The seven rows whose correct fact is known to be buried, with the anchor identified by a
# --- needle that must match EXACTLY ONE index row or the run aborts.
ANCHORS = {
    'nat_05': ('kiwango cha mafunzo ni asilimia tatu na nusu', 'SDL rate — the wrong-base row'),
    'nat_23': ('kiwango cha mafunzo ni asilimia tatu na nusu', 'SDL rate — the two-levy row'),
    'nat_28': ('vat withholding services: VAT withholding on services is 6%',
               'services withholding — the reply gave royalties 15%'),
    'nat_33': ('ada ya kuwasilisha ritani (annual return) ya kampuni kila mwaka ni TZS 22,000',
               'BRELA annual return fee'),
    'nat_43': ('sekta 16 na sekta ndogo 46',
               'GN605A sector count — RECORDED FIXED to rank 1; this is the C2 baseline control'),
    'nat_44': ('vat withholding goods: VAT withholding on goods is 3%',
               'goods withholding — the reply gave the services rate'),
    'nat_45': ('wcf accident reporting deadline: 7 working days',
               'WCF accident deadline — the reply fabricated an absolute date'),
}

# --- C1: real trademark-FEE questions taken verbatim from datasets/tier1a/cleaned_pairs.
CONTROL_QUESTIONS = [
    'Nikiwa na Alama ya Biashara, baada ya kusajiliwa, nina muda gani wa kuhuisha taarifa na '
    'itanigharimu shilingi ngapi?',
    'Hiyo ada ya marejesho ya alama ya biashara kuchelewa, ni shilingi ngapi hasa?',
    'Huyu Chike, hiki kiwango cha ada ya kuomba hati miliki ya biashara (trademark) ni elfu '
    '50,000 TZS sio?',
]


def resolve(texts, needle, rid):
    hits = [i for i, t in enumerate(texts) if needle in t]
    assert len(hits) == 1, (
        f'{rid}: needle {needle!r} matched {len(hits)} index rows; it must identify exactly one '
        f'or the verdict is about an unknown row')
    return hits[0]


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    texts = json.load(open(INDEX_TEXT, encoding='utf-8'))
    emb = np.load(INDEX_EMB)
    assert emb.shape[0] == len(texts), (emb.shape, len(texts))
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)

    fee_rows = [i for i, t in enumerate(texts) if t.startswith(FEE_ROW_NEEDLE)]
    assert fee_rows, 'no trademark fee rows found — the index changed shape; re-derive the needle'
    keep = [i for i in range(len(texts)) if i not in set(fee_rows)]

    nat = {r['id']: r for r in (json.loads(l) for l in open(NAT48, encoding='utf-8') if l.strip())}
    model = SentenceTransformer('intfloat/multilingual-e5-base')

    # --- A2's one new row, embedded exactly as the build script would ------------------------
    cons_vec = model.encode([PASSAGE_PREFIX + CONSOLIDATED], normalize_embeddings=True)[0]

    arms = {
        'A0_baseline': (list(range(len(texts))), texts, emb),
        'A1_delete': (keep, [texts[i] for i in keep], emb[keep]),
        'A2_consolidate': (keep + [-1], [texts[i] for i in keep] + [CONSOLIDATED],
                           np.vstack([emb[keep], cons_vec[None, :]])),
    }

    def rank_of(arm_texts, arm_emb, question, needle):
        qv = model.encode([f'query: {question}'], normalize_embeddings=True)[0]
        sims = qv @ arm_emb.T
        order = list(np.argsort(-sims))
        if needle is None:
            return None, None, [arm_texts[int(i)][:70] for i in order[:TOP_K]]
        hits = [i for i, t in enumerate(arm_texts) if needle in t]
        assert len(hits) == 1, f'needle resolved to {len(hits)} rows in this arm'
        pos = hits[0]
        return order.index(pos) + 1, float(sims[pos]), [arm_texts[int(i)][:70] for i in order[:TOP_K]]

    rows = []
    for rid, (needle, why) in ANCHORS.items():
        resolve(texts, needle, rid)          # must be unique in the FULL index too
        q = nat[rid]['question']
        rec = {'id': rid, 'question': q, 'anchor_why': why, 'arms': {}}
        for name, (_, at, ae) in arms.items():
            r, s, top = rank_of(at, ae, q, needle)
            rec['arms'][name] = {'anchor_rank': r, 'anchor_score': round(s, 4),
                                 'in_top_3': r <= TOP_K, 'top_3': top}
        rec['delta_delete'] = (rec['arms']['A0_baseline']['anchor_rank']
                               - rec['arms']['A1_delete']['anchor_rank'])
        rec['delta_consolidate'] = (rec['arms']['A0_baseline']['anchor_rank']
                                    - rec['arms']['A2_consolidate']['anchor_rank'])
        rows.append(rec)
        print(f"{rid}  base {rec['arms']['A0_baseline']['anchor_rank']:4d}  "
              f"delete {rec['arms']['A1_delete']['anchor_rank']:4d}  "
              f"consol {rec['arms']['A2_consolidate']['anchor_rank']:4d}")

    # --- C1: the clean case. Trademark-fee questions must still be answerable under A2. -------
    controls = []
    for q in CONTROL_QUESTIONS:
        rec = {'question': q, 'arms': {}}
        for name, (_, at, ae) in arms.items():
            qv = model.encode([f'query: {q}'], normalize_embeddings=True)[0]
            sims = qv @ ae.T
            order = list(np.argsort(-sims))
            top = [at[int(i)] for i in order[:TOP_K]]
            has_fee = any(t.startswith(FEE_ROW_NEEDLE) or t == CONSOLIDATED for t in top)
            rec['arms'][name] = {'a_fee_answer_is_in_top_3': has_fee,
                                 'top_3': [t[:70] for t in top]}
        controls.append(rec)

    # --- C2: the R24 baseline control ---------------------------------------------------------
    nat43 = next(r for r in rows if r['id'] == 'nat_43')
    c2 = {'expected': 'nat_43 anchor at rank 1 in the BASELINE arm (recorded FIXED after its '
                      'ask-alignment rewrite)',
          'observed_rank': nat43['arms']['A0_baseline']['anchor_rank'],
          'baseline_reproduces_recorded_state': nat43['arms']['A0_baseline']['anchor_rank'] == 1}

    moved_delete = sum(1 for r in rows if r['delta_delete'] > 0)
    moved_cons = sum(1 for r in rows if r['delta_consolidate'] > 0)
    entered_delete = sum(1 for r in rows
                         if r['arms']['A1_delete']['in_top_3']
                         and not r['arms']['A0_baseline']['in_top_3'])
    entered_cons = sum(1 for r in rows
                       if r['arms']['A2_consolidate']['in_top_3']
                       and not r['arms']['A0_baseline']['in_top_3'])

    blob = {
        'measured': '2026-08-25',
        'harness': 'eval/index_quality/measure_feerow_curation.py',
        'index_rows': len(texts),
        'fee_rows_removed': len(fee_rows),
        'fee_row_indices': fee_rows,
        'r25_justification': {
            'q1_defect_repaired': 'seventeen short `key: number` trademark fee rows; fee-shaped '
                                  'rows were 30.4% of a 217-row index and took 58% of top-3 slots',
            'q2_correct_output_at_risk': '28 rows in datasets/ DO ask trademark fee questions '
                                         '(renewal cost, late-renewal penalty, registration fee). '
                                         'ZERO in eval/. So deletion costs no MEASURED accuracy '
                                         'and still removes content a real user can ask for — '
                                         'which is why the consolidate arm exists.',
        },
        'note_on_method': 'A0/A1 need no re-embedding: cosine is per-row, so dropping rows cannot '
                          'change a surviving row\'s score. A2 embeds exactly one new row with '
                          'the build-time `passage: ` prefix and the production e5-base model.',
        'C2_baseline_control': c2,
        'summary': {
            'rows': len(rows),
            'delete_moved_anchor_up': moved_delete,
            'consolidate_moved_anchor_up': moved_cons,
            'delete_brought_anchor_INTO_top3': entered_delete,
            'consolidate_brought_anchor_INTO_top3': entered_cons,
        },
        'rows': rows,
        'C1_content_preservation_controls': controls,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    print(f"\nC2 baseline control (nat_43 must be rank 1): {c2['observed_rank']} -> "
          f"{c2['baseline_reproduces_recorded_state']}")
    print(f"moved up: delete {moved_delete}/{len(rows)}, consolidate {moved_cons}/{len(rows)}")
    print(f"entered top-3: delete {entered_delete}, consolidate {entered_cons}")
    for c in controls:
        print(f"  C1 {c['question'][:45]}... base="
              f"{c['arms']['A0_baseline']['a_fee_answer_is_in_top_3']} "
              f"del={c['arms']['A1_delete']['a_fee_answer_is_in_top_3']} "
              f"cons={c['arms']['A2_consolidate']['a_fee_answer_is_in_top_3']}")
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Rank the four covered-half defects BY MEASURED EXPOSURE, not by argument.

WHY MEASURED. The class analysis found four distinct defects wearing one symptom, on a sample of
seven rows. Seven rows cannot rank anything, and this project has now had several reversals where
a plausible ordering survived until someone measured it. So each defect gets a mechanical exposure
measurement over all 483 corpus questions, and where a candidate lever exists it is measured as a
COUNTERFACTUAL rather than asserted.

EXPOSURE IS NOT INCIDENCE, and conflating them would be this file's own presence-not-conclusion
error. Exposure counts questions whose retrieved context has the SHAPE that produced a wrong
answer — competing quantities, fragment-dominated top-3, an unreachable refutation. Most exposed
questions are answered correctly. Exposure is an upper bound on how often a defect CAN fire and
the right quantity for ordering work; it is not a defect count.

WHAT IS MEASURED

  D1 ADJACENT-FACT SELECTION — the new one. Does the top-3 contain two or more facts about the
     SAME subject stating DIFFERENT percentages? That is the `eval_337` shape: `NSSF jumla 20%`
     at rank 1 and `mwajiri analipa 10%` at rank 2, and the model reported the share as the
     total. No candidate lever is measured because none exists — see the module's closing note.

  D2 RANK-1 CONTRADICTION — `pic_11`. NOT MECHANICALLY MEASURABLE OFFLINE: deciding that a reply
     contradicts a fact it was given requires generation and adjudication. Its exposure is
     reported as UNMEASURED rather than estimated, because filling the slot with a proxy is how
     a ranking becomes an argument again.

  D3 FRAGMENT DISPLACEMENT — `eval_342`, whose top-3 was three bare `key: value` percentage rows
     with no PAYE fact at all while the anchor sat at rank 51. Exposure: how many questions have
     fragment rows occupying top-3 slots. LEVER, measured as a counterfactual: re-rank with
     fragment rows removed from the candidate set and report how many questions' top-3 changes.

  D4 REFUTATION OUT OF REACH — `eval_348`. Exposure: false-premise confirmation questions
     ("...sivyo?", "...au ni X?"), where the only correct answer needs a fact that CONTRADICTS
     the premise. LEVER, measured: does raising top_k from 3 to 5 or 10 change what is available?

Retrieval is the production path: e5-base, `query:`/`passage:` prefixes, cosine, top_k=3, over the
deployed index. Offline from the local HF cache.

R18: committed before its result is written up.
Artifact: eval/results/defect_exposure.json
"""
import json
import os
import re
import sys

os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'eval', 'coverage'))

from measure_coverage_gate_signals import load_corpora                      # noqa: E402

INDEX_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
INDEX_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
OUT = os.path.join(REPO, 'eval', 'results', 'defect_exposure.json')

TOP_K = 3

# A FRAGMENT ROW is `key: value` where the value is a bare quantity — a few tokens carrying a
# number, with no sentence around it. Deliberately NOT every `key: value` row: 40% of the index
# matches that loosely, and rows like "gn487a effective date: GN 487A came into effect on 28 July
# 2025" are real sentences that happen to carry a prefix. The ≤4-token rule is what separates
# "five %" from a fact.
_KV = re.compile(r'^([a-z][a-z0-9 _\-]{2,60}):\s*(.+)$')
_NUMWORD = re.compile(r'\b(one|two|three|four|five|six|seven|eight|nine|ten|zero)\b', re.I)


def is_fragment(text):
    m = _KV.match(text)
    if not m:
        return False
    value = m.group(2).strip()
    tokens = value.split()
    if len(tokens) > 4:
        return False
    return bool(re.search(r'\d', value) or _NUMWORD.search(value))


# Subjects whose facts state MULTIPLE different rates, which is what makes D1 possible at all.
_SUBJECTS = {
    'nssf': ['nssf'],
    'paye': ['paye'],
    'sdl': ['sdl'],
    'wcf': ['wcf'],
    'vat': ['vat', 'ongezeko la thamani'],
}
_PCT = re.compile(r'(\d+(?:\.\d+)?)\s*(?:%|asilimia)|asilimia\s+(\d+(?:\.\d+)?)', re.I)


def percentages(text):
    out = set()
    for a, b in _PCT.findall(text):
        out.add(a or b)
    return out


def competing_quantities(top_texts):
    """Subjects for which TWO DIFFERENT ROWS in the top-3 state different percentages.

    THE ACROSS-ROWS REQUIREMENT IS THE WHOLE DETECTOR, and the first version got it wrong. That
    version pooled every percentage for a subject across the top-3 and flagged when the pool held
    more than one value — which fires on a SINGLE fact that names a wrong value in order to refute
    it: `vat standard rate: ... is 18% — it was NEVER 14%` looks like {14, 18}. It reported 26.3%
    exposure, almost all of it that shape.

    `eval_337` is two SEPARATE facts — `NSSF jumla: 20%` and `mwajiri analipa 10%` — each true,
    neither refuting the other, and the model picked the wrong one. A refutation inside one fact
    is the opposite situation: the fact is doing the disambiguation for us.
    """
    hits = {}
    for subject, cues in _SUBJECTS.items():
        per_row = []
        for t in top_texts:
            if any(c in t.lower() for c in cues):
                p = percentages(t)
                if p:
                    per_row.append((t, p))
        if len(per_row) < 2:
            continue
        # Two rows compete when neither's value set contains the other's — i.e. a reader
        # choosing between them gets a different number depending on which they pick.
        competing_rows = [(a, b) for i, a in enumerate(per_row) for b in per_row[i + 1:]
                          if a[1] != b[1] and not (a[1] <= b[1] or b[1] <= a[1])]
        if competing_rows:
            hits[subject] = {
                'values': sorted({v for _, p in per_row for v in p}),
                'rows': [t[:90] for t, _ in per_row],
                'n_rows': len(per_row),
            }
    return hits


# A FALSE-PREMISE CONFIRMATION asserts a value and asks for agreement. Its only correct answer may
# require a fact that CONTRADICTS it, which top-3 similarity has no reason to surface.
_CONFIRM = re.compile(r'sivyo\s*\?|si\s+kweli\s*\?|,\s*sivyo|\bau\s+ni\b|\bkweli\s*\?|, right\?',
                      re.I)


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    with open(INDEX_TEXT, encoding='utf-8') as f:
        texts = json.load(f)
    emb = np.load(INDEX_EMB)
    assert emb.shape[0] == len(texts), (emb.shape, len(texts))
    emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)

    frag_flags = [is_fragment(t) for t in texts]
    n_frag = sum(frag_flags)
    keep = np.array([not f for f in frag_flags])
    assert 0 < n_frag < len(texts), 'fragment detector matched everything or nothing'

    model = SentenceTransformer('intfloat/multilingual-e5-base')
    corpora = load_corpora()
    questions = [(name, r['id'], r['q']) for name, rows in corpora.items() for r in rows]

    qv = model.encode([f'query: {q}' for _, _, q in questions],
                      batch_size=16, normalize_embeddings=True, show_progress_bar=False)
    sims = qv @ emb.T

    rows, d1_hits, d3_hits, d4_hits = [], [], [], []
    slots_total = slots_frag = 0

    for i, (corpus, qid, q) in enumerate(questions):
        order = list(np.argsort(-sims[i]))
        top = [int(j) for j in order[:TOP_K]]
        top_texts = [texts[j] for j in top]

        n_frag_in_top = sum(1 for j in top if frag_flags[j])
        slots_total += TOP_K
        slots_frag += n_frag_in_top

        competing = competing_quantities(top_texts)

        # D3 counterfactual: re-rank with fragment rows removed from the candidate set.
        masked = np.where(keep, sims[i], -np.inf)
        top_nofrag = [int(j) for j in np.argsort(-masked)[:TOP_K]]
        changed = top_nofrag != top

        is_confirm = bool(_CONFIRM.search(q))
        # D4 LEVER, measured: for a false-premise confirmation, does WIDENING the window bring a
        # CONTRADICTING row into reach? A contradicting row shares a subject cue with the
        # question and states a number the question does not. eval_348's refuting fact sat at
        # rank 10, so this asks whether that is typical or a one-off.
        widen = {}
        if is_confirm:
            asserted = percentages(q) | set(re.findall(r'\b(\d{1,3})\b', q))
            subj_cues = [c for cues in _SUBJECTS.values() for c in cues
                         if c in q.lower()]
            for k in (3, 5, 10):
                found = 0
                for j in order[:k]:
                    t = texts[j]
                    tl = t.lower()
                    if subj_cues and not any(c in tl for c in subj_cues):
                        continue
                    nums = percentages(t) | set(re.findall(r'\b(\d{1,3})\b', t))
                    if nums - asserted:
                        found += 1
                widen[f'top{k}'] = found

        rec = {'corpus': corpus, 'id': qid, 'question': q,
               'top3': top, 'n_fragment_in_top3': n_frag_in_top,
               'competing_subjects': list(competing),
               'top3_changes_without_fragments': changed,
               'is_false_premise_confirmation': is_confirm,
               'contradicting_rows_by_window': widen}
        if competing:
            rec['competing_detail'] = competing
            d1_hits.append(rec)
        if n_frag_in_top > 0:
            d3_hits.append(rec)
        if is_confirm:
            d4_hits.append(rec)
        rows.append(rec)

    n = len(rows)
    d3_by_count = {k: sum(1 for r in rows if r['n_fragment_in_top3'] == k) for k in range(4)}
    d3_changed = sum(1 for r in rows if r['top3_changes_without_fragments'])

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/routing/measure_defect_exposure.py',
        'caveat': 'EXPOSURE IS NOT INCIDENCE. These count questions whose retrieved context has '
                  'the SHAPE that produced a wrong answer; most exposed questions are answered '
                  'correctly. Exposure is an upper bound on how often a defect CAN fire.',
        'n_questions': n,
        'index_rows': len(texts),
        'fragment_rows_in_index': n_frag,
        'fragment_share_of_index': round(n_frag / len(texts), 3),
        'D1_adjacent_fact_selection': {
            'exposed': len(d1_hits), 'rate': round(len(d1_hits) / n, 4),
            'lever': 'NONE AVAILABLE — see closing note',
            'by_subject': {s: sum(1 for r in d1_hits if s in r['competing_subjects'])
                           for s in _SUBJECTS},
            'examples': [{'id': r['id'], 'q': r['question'][:90],
                          'detail': r['competing_detail']} for r in d1_hits[:8]],
        },
        'D2_rank1_contradiction': {
            'exposed': None,
            'why': 'UNMEASURED, deliberately. Deciding that a reply contradicts a fact it was '
                   'given requires generation and adjudication; no offline proxy exists and '
                   'inventing one would turn this ranking back into an argument.',
            'lever': 'NONE AVAILABLE — SS8 already showed forced maximum retrieval confidence '
                     'does not fix it.',
        },
        'D3_fragment_displacement': {
            'exposed': len(d3_hits), 'rate': round(len(d3_hits) / n, 4),
            'top3_slots_held_by_fragments': slots_frag,
            'top3_slots_total': slots_total,
            'slot_share': round(slots_frag / slots_total, 4),
            'questions_by_fragment_count': d3_by_count,
            'lever': 'MEASURED COUNTERFACTUAL: exclude fragment rows from the candidate set.',
            'top3_changes_without_fragments': d3_changed,
            'lever_reach_rate': round(d3_changed / n, 4),
        },
        'D4_refutation_out_of_reach': {
            'exposed': len(d4_hits), 'rate': round(len(d4_hits) / n, 4),
            'lever': 'raise top_k — MEASURED: how many confirmation questions have a '
                     'CONTRADICTING row (same subject, different number) inside each window.',
            'questions_with_a_contradicting_row': {
                f'top{k}': sum(1 for r in d4_hits
                               if r['contradicting_rows_by_window'].get(f'top{k}', 0) > 0)
                for k in (3, 5, 10)},
            'examples': [{'id': r['id'], 'q': r['question'][:100],
                          'windows': r['contradicting_rows_by_window']} for r in d4_hits[:12]],
        },
        'rows': rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"questions: {n}   index: {len(texts)}   fragment rows: {n_frag} "
          f"({n_frag / len(texts):.0%} of the index)")
    print(f"\nD1 adjacent-fact selection   exposed {len(d1_hits):>4}  "
          f"({len(d1_hits) / n:.1%})   lever: NONE")
    print(f"   by subject: {out['D1_adjacent_fact_selection']['by_subject']}")
    print(f"D2 rank-1 contradiction      exposed UNMEASURED           lever: NONE")
    print(f"D3 fragment displacement     exposed {len(d3_hits):>4}  ({len(d3_hits) / n:.1%})   "
          f"lever reach {d3_changed} ({d3_changed / n:.1%})")
    print(f"   fragments hold {slots_frag}/{slots_total} top-3 slots "
          f"({slots_frag / slots_total:.1%});  by count {d3_by_count}")
    d4w = out['D4_refutation_out_of_reach']['questions_with_a_contradicting_row']
    print(f"D4 refutation out of reach   exposed {len(d4_hits):>4}  ({len(d4_hits) / n:.1%})   "
          f"contradicting row available: {d4w}")
    print('\n--- D1 examples ---')
    for r in d1_hits[:8]:
        print(f"  {r['id']:<12}{r['question'][:70]}")
        for s, d in r['competing_detail'].items():
            print(f"       {s}: {d['values']}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()

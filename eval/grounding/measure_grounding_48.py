# -*- coding: utf-8 -*-
"""Is each currently-correct row's answer actually GROUNDED in what retrieval handed it?

Motivated by the nick_02/nick_03 finding: two answers scored CORRECT were produced from a
top-3 containing no relevant fact at all — ungrounded generations that happened to land right.
If that is common, the project's accuracy figures are softer than they read.

SCOPE OF THE QUESTION. Only the FACT path depends on retrieval:
  - compute rows are grounded by the rules engine (the working is appended deterministically),
  - refusal rows are grounded by the classifier.
So the measurement targets fact-path rows, and reports the other paths separately rather than
folding them in.

METHOD (heuristic, and labelled one). For each fact-path row: reproduce production retrieval
exactly (e5-base, 'query: ' prefix, cosine over the deployed index, top_k=3), then check whether
every decisive FIGURE in the adjudicated reply appears in the retrieved text. Figures are
normalised across digit / English-word / Swahili-word forms, since the index mixes all three.

  GROUNDED      every figure the reply ASSERTS is present in the retrieved context
  UNGROUNDED    at least one asserted figure is absent from all retrieved facts
  NO_FIGURES    the reply asserts no new figure — judged instead by topical overlap (weaker),
                and listed in full for human read

FIGURES THE USER SUPPLIED DO NOT NEED GROUNDING. A first version of this script counted every
number in the reply, including ones quoted straight back from the question ("mauzo yako ya TZS
60,000,000" when the user wrote "milioni 60"). Those inflate the missing-list and would have
made the write-up wrong about WHICH figure was unsupported. Question figures are subtracted.

A figure-based test still cannot see a wrong-but-unnumbered claim, and it counts a figure that
appears coincidentally. Both limits are why per-row output is printed for adjudication rather
than only a summary count.

R18: committed before its result is written up.
Artifact: eval/results/grounding_48.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

from chike import decomposition  # noqa: E402
ADJ = os.path.join(REPO, 'eval', 'results', 'natural48_rerun_2026_08_17_adjudication.json')
OUT = os.path.join(REPO, 'eval', 'results', 'grounding_48.json')
TOP_K = 3

SW_NUM = {
    'moja': '1', 'mbili': '2', 'tatu': '3', 'nne': '4', 'tano': '5', 'sita': '6',
    'saba': '7', 'nane': '8', 'tisa': '9', 'kumi': '10', 'ishirini': '20',
    'thelathini': '30', 'arobaini': '40', 'hamsini': '50', 'sitini': '60',
    'sabini': '70', 'themanini': '80', 'tisini': '90', 'mia': '100', 'elfu': '1000',
}
EN_NUM = {
    'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6',
    'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10', 'twelve': '12',
}
# Figures that carry no discriminating power — legal citations and boilerplate.
CITATION_NOISE = {'605', '487', '212', '213', '332', '438', '82', '50', '5', '16', '2003',
                  '2019', '2022', '2023', '2024', '2025', '2026'}


def _expand_scale(t):
    """'milioni 60' -> '60000000'. Without this, a question's 'milioni 60' and its reply's
    'TZS 60,000,000' are different tokens for the same quantity, and the user's own figure
    gets counted as an unsupported assertion."""
    def mul(m, factor):
        val = float(m.group(1)) * factor
        return str(int(val)) if val == int(val) else str(val)

    # English scale words matter as much as Swahili ones: the index carries rows like
    # 'penalty fine non citizen: ten million TZS', which is the SAME fact the reply states
    # as 'TZS milioni 10'. Without 'million' here, that row scored a false UNGROUNDED.
    for word, factor in (('milioni', 1e6), ('million', 1e6), ('bilioni', 1e9),
                         ('billion', 1e9), ('elfu', 1e3), ('thousand', 1e3), ('laki', 1e5)):
        t = re.sub(rf'{word}\s*(\d+(?:\.\d+)?)', lambda m, f=factor: mul(m, f), t)
        t = re.sub(rf'(\d+(?:\.\d+)?)\s*{word}', lambda m, f=factor: mul(m, f), t)
    return t


def normalise(text):
    """Lowercase, map spelled numerals to digits, expand scale words, strip separators.

    LIMITATION, stated rather than hidden: compound Swahili numerals ('kumi na wawili' = 12)
    are not composed — they normalise to '10 na 2'. Affects readability of the figure lists,
    not the GROUNDED/UNGROUNDED verdicts in this run, which turn on large threshold figures.
    """
    t = (text or '').lower()
    for word, digit in list(SW_NUM.items()) + list(EN_NUM.items()):
        t = re.sub(rf'\b{word}\b', digit, t)
    t = re.sub(r'(?<=\d)[,\s](?=\d{3}\b)', '', t)
    t = t.replace(',', '.')
    t = _expand_scale(t)
    return t


def figures(text):
    """Decisive numeric tokens in a normalised string, citation noise removed."""
    t = normalise(text)
    raw = re.findall(r'\d+(?:\.\d+)?', t)
    out, seen = [], set()
    for f in raw:
        f = f.rstrip('.0') if f.endswith('.0') else f
        if f in CITATION_NOISE or f in seen:
            continue
        seen.add(f)
        out.append(f)
    return out


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    with open(ADJ, encoding='utf-8') as f:
        adj = json.load(f)
    emb = np.load(os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy'))
    with open(os.path.join(REPO, 'chike-inference', 'rag_facts_text.json'),
              encoding='utf-8') as f:
        texts = json.load(f)

    model = SentenceTransformer('intfloat/multilingual-e5-base')
    normalized = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)

    def retrieve_one(q):
        v = model.encode([f'query: {q}'])[0]
        v = v / (np.linalg.norm(v) + 1e-10)
        scores = np.dot(normalized, v)
        idx = np.argsort(scores)[-TOP_K:][::-1]
        return [(int(j), round(float(scores[j]), 4), texts[j]) for j in idx]

    def retrieve(question):
        """Mirror production pooling, not a single top-3.

        Orchestrator._answer_facts_single_pass pools retrieval across every fact
        sub-question (Orchestrator._pool_facts: dedupe, preserve order, cap 9). A
        multi-part question therefore reaches the model with MORE than 3 facts, and
        measuring only the whole-question top-3 would understate the context it had.
        """
        subs = decomposition.decompose_query(question) or [question]
        pooled, seen = [], set()
        for sq in subs:
            for pos, score, text in retrieve_one(sq):
                if pos not in seen:
                    seen.add(pos)
                    pooled.append((pos, score, text))
        return pooled[:9], subs

    rows = []
    for r in adj['rows']:
        rec = {'id': r['id'], 'path': r['path'], 'verdict': r['now'],
               'question': r['question'], 'reply': r.get('reply', ''),
               'why': r.get('why', '')}
        if r['path'] != 'fact':
            rec['grounding'] = 'N/A_' + r['path'].upper()
            rec['note'] = ('compute rows are grounded by the rules engine; refusal rows by the '
                           'classifier — neither depends on retrieval')
            rows.append(rec)
            continue

        got, subs = retrieve(r['question'])
        rec['sub_questions'] = subs
        ctx = normalise(' || '.join(t for _, _, t in got))
        q_figs = set(figures(r['question']))
        all_figs = figures(r.get('reply', ''))
        # Only figures the reply ASSERTS — a number quoted back from the question is the
        # user's own and needs no retrieval support.
        asserted = [f for f in all_figs if f not in q_figs]
        # Token-boundary match, not substring: plain `'18' in ctx` would score GROUNDED off
        # the '18' inside '180000', manufacturing support that isn't there.
        def present(fig):
            return re.search(rf'(?<!\d){re.escape(fig)}(?!\d)', ctx) is not None
        missing = [f for f in asserted if not present(f)]

        # Topical-overlap fallback for replies that assert no new figure. Content words of
        # 4+ chars from the question, minus obvious filler; indicative only, never a verdict.
        stop = {'nina', 'yangu', 'yako', 'kwa', 'kwenye', 'nini', 'ngapi', 'lini', 'wapi',
                'nitalipa', 'nalipa', 'nilipe', 'kama', 'hadi', 'sasa', 'tu', 'ile', 'hiyo',
                'nimefungua', 'nimeuza', 'jumla', 'mwezi', 'mwaka', 'biashara'}
        q_words = {w for w in re.findall(r'[a-z]{4,}', normalise(r['question']))
                   if w not in stop}
        overlap = sorted(w for w in q_words if w in ctx)

        rec['retrieved'] = [{'position': p, 'score': s, 'text': t} for p, s, t in got]
        rec['reply_figures_all'] = all_figs
        rec['reply_figures_asserted'] = asserted
        rec['question_figures_excluded'] = sorted(q_figs)
        rec['figures_missing_from_context'] = missing
        rec['topical_overlap_terms'] = overlap
        if not asserted:
            rec['grounding'] = 'NO_FIGURES'
            rec['topical_signal'] = 'some_overlap' if overlap else 'NO_OVERLAP'
        elif missing:
            rec['grounding'] = 'UNGROUNDED'
        else:
            rec['grounding'] = 'GROUNDED'
        rows.append(rec)

    fact_rows = [r for r in rows if r['path'] == 'fact']
    fact_correct = [r for r in fact_rows if r['verdict'].startswith('CORRECT')]

    def tally(rs):
        out = {}
        for r in rs:
            out[r['grounding']] = out.get(r['grounding'], 0) + 1
        return out

    out = {
        'measured': '2026-08-22',
        'source_adjudication': os.path.basename(ADJ),
        'adjudication_date': adj['date'],
        'method': 'HEURISTIC figure-presence test — see module docstring for its two blind spots',
        'top_k': TOP_K,
        'overall_counts': adj['counts'],
        'by_path': adj['by_path'],
        'fact_path_total': len(fact_rows),
        'fact_path_correct_total': len(fact_correct),
        'grounding_all_fact_rows': tally(fact_rows),
        'grounding_correct_fact_rows': tally(fact_correct),
        'ungrounded_correct_ids': [r['id'] for r in fact_correct
                                   if r['grounding'] == 'UNGROUNDED'],
        'rows': rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"48 rows | by path: {adj['by_path']}")
    print(f"\nFACT-PATH rows (the only ones retrieval can ground): {len(fact_rows)}")
    print(f"  of which CORRECT: {len(fact_correct)}")
    print(f"  grounding, all fact rows : {tally(fact_rows)}")
    print(f"  grounding, CORRECT only  : {tally(fact_correct)}")
    print(f"\nUNGROUNDED-but-CORRECT: {out['ungrounded_correct_ids']}")
    print('\n--- per-row (fact path only) ---')
    for r in fact_rows:
        flag = {'GROUNDED': ' ', 'UNGROUNDED': '!', 'NO_FIGURES': '?'}[r['grounding']]
        extra = (f"missing={r['figures_missing_from_context']}"
                 if r['grounding'] != 'NO_FIGURES'
                 else f"topical={r['topical_signal']} {r['topical_overlap_terms'][:4]}")
        print(f"{flag} {r['id']:7} {r['verdict']:9} {r['grounding']:11} {extra}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()

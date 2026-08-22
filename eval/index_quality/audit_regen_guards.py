# -*- coding: utf-8 -*-
"""Audit EVERY critical query in the R15 regen gate for the two faults found by accident.

Two unsound guards were found while chasing something else. There is no reason to think they
are the only two, so every guard is checked for both faults:

  FAULT 1 — NON-VERBATIM PHRASING. The guard asks a paraphrase of the question production
    actually sends. nat_36's guard differs from its eval row by one capital letter and a
    question mark, and that moves its target fact from rank 17 to rank 2. A guard that only
    passes on a phrasing no user sends certifies nothing.

  FAULT 2 — SUBSTRING-MATCHABLE KEYWORD. The guard's expected keyword appears in MORE THAN ONE
    fact, so it can pass on a fact other than the one it means. nat_27's guard tests
    `'18%' in fact_text` and is satisfied by the vat-withholding-formula row, which contains
    "the standard 18% VAT is split...". The guard reports the standard-rate fact as retrieved
    when it was not.

Reads the guard list out of kaggle/regenerate_rag_e5.py by AST parse — no import, no execution,
no network, and kaggle/ is not modified (R10).

R18: committed before its result is written up.
Artifact: eval/results/regen_guard_audit.json
"""
import ast
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
REGEN = os.path.join(REPO, 'kaggle', 'regenerate_rag_e5.py')
OUT = os.path.join(REPO, 'eval', 'results', 'regen_guard_audit.json')


def load_guards():
    """Pull the `critical_queries` list literal out of the regen script."""
    with open(REGEN, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == 'critical_queries':
                    return ast.literal_eval(node.value)
    raise SystemExit('critical_queries not found')


def corpus_questions():
    """Every question text this project has actually sent as a probe.

    Covers the gate JSONL corpora AND the run artifacts in eval/results/. The artifacts
    matter: the 20-edge probe set has no corpus JSONL of its own, so a first version of this
    check flagged three guards labelled '(QNN verbatim)' as NON_VERBATIM when they are in fact
    verbatim against that probe set. That was a gap in the checker, not a defect in those
    guards, and over-reporting a fault is as bad as missing one.
    """
    qs = set()
    for sub in ('accuracy_gate', 'refusal_gate'):
        d = os.path.join(REPO, 'eval', sub)
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if not name.endswith('.jsonl'):
                continue
            with open(os.path.join(d, name), encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    for key in ('question', 'question_sw', 'text'):
                        if row.get(key):
                            qs.add(row[key].strip())

    # NARROW, NAMED widening — the edge20 probe set only, which has no corpus JSONL.
    #
    # A first attempt scanned ALL of eval/results/*.json and was CIRCULAR: the only files
    # containing the nat_27 and nat_36 guard phrasings were two artifacts THIS SESSION had
    # just written (regen_guard_audit.json, targeted_rewrite.json). The checker read its own
    # output back and pronounced the guard text a real question. Scanning arbitrary artifacts
    # to decide whether a string is a genuine probe cannot work — artifacts contain whatever
    # was tested, including the thing under test.
    results = os.path.join(REPO, 'eval', 'results')
    if os.path.isdir(results):
        for name in os.listdir(results):
            if not (name.startswith('edge20_') and name.endswith('.json')):
                continue
            try:
                with open(os.path.join(results, name), encoding='utf-8') as f:
                    blob = f.read()
            except OSError:
                continue
            for m in re.finditer(r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"', blob):
                try:
                    qs.add(json.loads(f'"{m.group(1)}"').strip())
                except json.JSONDecodeError:
                    continue
    return qs


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    guards = load_guards()
    with open(os.path.join(REPO, 'chike-inference', 'rag_facts_text.json'),
              encoding='utf-8') as f:
        texts = json.load(f)
    emb = np.load(os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy'))
    normalized = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
    model = SentenceTransformer('intfloat/multilingual-e5-base')
    known_qs = corpus_questions()
    norm_known = {q.lower().rstrip('?').strip() for q in known_qs}

    rows = []
    for name, query, expected in guards:
        bare = re.sub(r'^query:\s*', '', query).strip()
        norm_bare = bare.lower().rstrip('?').strip()

        # FAULT 1 — is this the text a corpus row actually uses?
        verbatim = bare in known_qs
        near = (not verbatim) and (norm_bare in norm_known)

        # FAULT 2 — how many facts satisfy each expected keyword?
        kw_matches = {}
        for kw in expected:
            hits = [i for i, t in enumerate(texts) if kw.lower() in t.lower()]
            kw_matches[kw] = hits
        ambiguous = {k: v for k, v in kw_matches.items() if len(v) > 1}

        # What does the guard actually retrieve, and which fact satisfies it?
        q = model.encode([query])[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        scores = np.dot(normalized, q)
        top3 = [int(j) for j in np.argsort(scores)[-3:][::-1]]
        satisfied_by = [j for j in top3
                        if any(kw.lower() in texts[j].lower() for kw in expected)]

        faults = []
        if not verbatim:
            faults.append('NON_VERBATIM_NEAR' if near else 'NON_VERBATIM')
        if ambiguous:
            faults.append('AMBIGUOUS_KEYWORD')
        if not satisfied_by:
            faults.append('CURRENTLY_FAILING')
        elif len(satisfied_by) > 1:
            faults.append('MULTIPLE_SATISFIERS_IN_TOP3')

        rows.append({
            'name': name,
            'query': query,
            'expected': expected,
            'verbatim_corpus_question': verbatim,
            'near_verbatim_only_case_or_punct': near,
            'keyword_fact_counts': {k: len(v) for k, v in kw_matches.items()},
            'ambiguous_keywords': {k: v[:8] for k, v in ambiguous.items()},
            'top3': [{'position': j, 'text': texts[j][:95]} for j in top3],
            'satisfied_by_positions': satisfied_by,
            'faults': faults,
        })

    def count(f):
        return sum(1 for r in rows if f in r['faults'])

    out = {
        'measured': '2026-08-22',
        'source': 'kaggle/regenerate_rag_e5.py (read-only AST parse; R10 file not modified)',
        'total_guards': len(rows),
        'fault_counts': {
            'NON_VERBATIM': count('NON_VERBATIM'),
            'NON_VERBATIM_NEAR': count('NON_VERBATIM_NEAR'),
            'AMBIGUOUS_KEYWORD': count('AMBIGUOUS_KEYWORD'),
            'CURRENTLY_FAILING': count('CURRENTLY_FAILING'),
            'MULTIPLE_SATISFIERS_IN_TOP3': count('MULTIPLE_SATISFIERS_IN_TOP3'),
        },
        'clean_guards': [r['name'] for r in rows if not r['faults']],
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'guards audited: {len(rows)}')
    print(json.dumps(out['fault_counts'], indent=2))
    print(f"\nclean: {len(out['clean_guards'])}/{len(rows)}")
    print('\n--- guards with faults ---')
    for r in rows:
        if r['faults']:
            amb = ''
            if r['ambiguous_keywords']:
                amb = ' amb=' + ','.join(
                    f"{k}x{len(v)}" for k, v in r['ambiguous_keywords'].items())
            print(f"  {','.join(r['faults']):<45} {r['name'][:52]}{amb}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()

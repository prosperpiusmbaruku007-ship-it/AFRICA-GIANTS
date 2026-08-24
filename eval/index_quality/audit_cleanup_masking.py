# -*- coding: utf-8 -*-
"""What is the cleanup layer silently repairing, and what defect does each repair conceal?

WHY THIS AUDIT EXISTS. `nssf.or.tz` was found by accident. CLAUDE.md flags the domain as
DNS-failing; the model emitted it; `generation_cleanup` rewrote it to `.go.tz` on every reply. It
surfaced only because a diagnostic used `generate_raw`, which bypasses cleaning by design. Behind
that rewrite sat **786 occurrences across 34 files of training data**, and an authoring check that
whitelisted the dead domain — invisible for the entire life of the corpus **because the output was
silently corrected**.

**Any rewrite in the cleanup layer is a place where an upstream defect can persist unobserved.**
That is a general property, not a property of that one rule: a repair makes the symptom disappear
without touching the cause, and a defect with no symptom is not looked for. So this asks the
question once, for every rewrite that changes CONTENT rather than formatting:

    for each rewrite: what would reach a user if it were removed, and does the corpus contain
    the thing it repairs?

FORMATTING REPAIRS ARE OUT OF SCOPE and deliberately so. Stripping special tokens, role junk,
glued-domain decode loops and a leading echoed question repairs a DECODING artefact — there is no
upstream corpus defect for them to conceal, because no training pair contains `<|end_of_text|>` as
content. The two CONTENT rewrites are the ones that can mask authored data.

R18: committed before its result is written up.
Artifact: eval/results/cleanup_masking_audit.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

OUT = os.path.join(REPO, 'eval', 'results', 'cleanup_masking_audit.json')

# (name, pattern, what it rewrites to, why it might mask something)
CONTENT_REWRITES = [
    ('nssf_or_tz', r'nssf\.or\.tz', 'nssf.go.tz',
     'CLAUDE.md section 4: nssf.or.tz fails DNS. KNOWN INSTANCE — this is the one that was '
     'found by accident and prompted the audit.'),
    ('go_ke', r'\.go\.ke\b', '.go.tz',
     'A Kenyan government domain in Tanzanian compliance output. If the corpus contains any, '
     'the model is being taught to cite the wrong country and the rewrite hides it.'),
]

# Where authored content lives. The RAG index and locked_facts are what retrieval serves; the
# datasets are what the adapter was trained on. A rewrite can mask a defect in either.
SEARCH_ROOTS = [
    ('rag_index', ['chike-inference/rag_facts_text.json']),
    ('locked_facts', ['scripts/locked_facts.json']),
    ('datasets', None),          # walked
    ('eval_corpora', None),      # walked
]


def walk(rel_dir, exts=('.jsonl', '.json')):
    base = os.path.join(REPO, rel_dir)
    out = []
    for dirpath, _dirs, files in os.walk(base):
        for fn in files:
            if fn.endswith(exts):
                out.append(os.path.join(dirpath, fn))
    return out


def scan(pattern):
    rx = re.compile(pattern, re.IGNORECASE)
    per_area = {}
    for area, files in SEARCH_ROOTS:
        if files is None:
            files = walk('datasets' if area == 'datasets' else 'eval')
        else:
            files = [os.path.join(REPO, f) for f in files]
        hits, filecount = 0, 0
        examples = []
        for path in files:
            try:
                with open(path, encoding='utf-8') as fh:
                    text = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            found = rx.findall(text)
            if found:
                filecount += 1
                hits += len(found)
                if len(examples) < 3:
                    m = rx.search(text)
                    lo = max(0, m.start() - 90)
                    examples.append({
                        'file': os.path.relpath(path, REPO).replace('\\', '/'),
                        'context': text[lo:m.end() + 90].replace('\n', ' ')})
        per_area[area] = {'occurrences': hits, 'files': filecount, 'examples': examples}
    return per_area


def main():
    from chike import generation_cleanup as gc

    rows = []
    for name, pattern, target, why in CONTENT_REWRITES:
        found = scan(pattern)
        total = sum(v['occurrences'] for v in found.values())
        # Prove the rewrite is live rather than assuming it: run a body through it.
        probe = f'Thibitisha na {"nssf.or.tz" if name == "nssf_or_tz" else "tra.go.ke"}.'
        cleaned = gc.clean_generated_reply(probe)
        rows.append({
            'rewrite': name, 'pattern': pattern, 'rewrites_to': target, 'why': why,
            'rewrite_is_live': probe != cleaned,
            'probe_in': probe, 'probe_out': cleaned,
            'corpus_occurrences_total': total,
            'by_area': found,
            'masks_a_real_defect': total > 0,
        })

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/index_quality/audit_cleanup_masking.py',
        'question': 'for each CONTENT rewrite in the cleanup layer: what would reach a user if '
                    'it were removed, and does the corpus contain the thing it repairs?',
        'scope_note': 'FORMATTING repairs (special tokens, role junk, glued-domain loops, the '
                      'leading echoed question) are deliberately excluded: they repair a DECODING '
                      'artefact, and no authored pair contains one as content, so there is no '
                      'upstream defect for them to conceal.',
        'n_content_rewrites': len(rows),
        'rows': rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    for r in rows:
        print(f"\n=== {r['rewrite']}  ->  {r['rewrites_to']}   live={r['rewrite_is_live']}")
        print(f"    {r['probe_in']}  ->  {r['probe_out']}")
        print(f"    corpus occurrences: {r['corpus_occurrences_total']}  "
              f"MASKS A REAL DEFECT: {r['masks_a_real_defect']}")
        for area, v in r['by_area'].items():
            if v['occurrences']:
                print(f"      {area:<14}{v['occurrences']:>5} in {v['files']} file(s)")
                for e in v['examples'][:2]:
                    print(f"          {e['file']}: …{e['context'][:120]}…")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()

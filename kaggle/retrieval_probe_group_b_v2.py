"""Group B probe v2 — TWO-ARM retrieval (RUN ON KAGGLE; local network blocks e5 download).

v1 mirrored single-arm production (modal_app.retrieve_facts) and showed eval_347's EFD fact
is not in the full-query top-5. But the ORCHESTRATOR that generated the baseline answers uses
chike.retrieval.Retriever — a TWO-ARM hybrid (full-query top-3 + a number-stripped arm that
appends the first NEW fact). So the single-arm verdict is not conclusive for eval_347.

This probe uses the REAL chike.retrieval code (not a reimplementation) to show, for each query:
  - the full-query arm top-3 (what single-arm production sees),
  - the number-stripped query + its top-6 pool,
  - the FINAL two-arm merged set that retrieve() actually returns to the orchestrator,
  - whether the target fact is in that final set.
Verdict per case:
  target IN the two-arm final set  -> mechanism already recovers it => HALLUCINATION (no fix)
  target NOT in the two-arm final set -> genuine retrieval gap the two-arm append can't close
                                         => fact-base retrievability fix needed (concise fact).

Read-only: fetches the committed index from GitHub main (cache-busted) and only queries it.
Requires the chike/ package on the path (Kaggle fetches the repo). Nothing is rebuilt/uploaded.
"""
import json
import subprocess
import sys
import time
import numpy as np
import requests

RAW = 'https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/main'
REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
_nocache = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}

# ── GET THE chike/ PACKAGE (git clone — the probe imports chike.retrieval and its helpers,
#    so a raw single-file fetch is not enough). Fresh clone = latest main; same pattern as
#    eval_orchestrator.py:88-100 / regenerate_rag_e5.py. ──────────────────────────────────
_CLONE_DIR = '/kaggle/working/AFRICA-GIANTS'
import os
if not os.path.isdir(_CLONE_DIR):
    subprocess.run(['git', 'clone', '--depth', '1',
                    f'https://github.com/{REPO}.git', _CLONE_DIR], check=True)
else:
    subprocess.run(['git', '-C', _CLONE_DIR, 'pull', '--ff-only'], check=False)
sys.path.insert(0, _CLONE_DIR)
_sha = subprocess.run(['git', '-C', _CLONE_DIR, 'rev-parse', '--short', 'HEAD'],
                      capture_output=True, text=True).stdout.strip()
print(f'[clone] chike package @ {_CLONE_DIR} (HEAD {_sha})')

_cb = int(time.time())
with open('rag_embeddings.npy', 'wb') as f:
    f.write(requests.get(f'{RAW}/chike-inference/rag_embeddings.npy?cb={_cb}', headers=_nocache, timeout=60).content)
with open('rag_facts_text.json', 'w', encoding='utf-8') as f:
    json.dump(requests.get(f'{RAW}/chike-inference/rag_facts_text.json?cb={_cb}', headers=_nocache, timeout=60).json(),
              f, ensure_ascii=False)

# Use the REAL two-arm retrieval + its helpers so the probe matches the orchestrator exactly.
from chike.retrieval import Retriever, strip_numeric_amounts, _has_digit, _STRIPPED_POOL

r = Retriever(emb_path='rag_embeddings.npy', texts_path='rag_facts_text.json')
r._ensure_index()
r._ensure_embed_model()
print(f'[load] index: {len(r.fact_texts)} facts')

PROBES = [
    ('eval_162 mgeni',
     "'Mgeni' katika GN 487A inamaanisha nani hasa?",
     ['mgeni cap357', "defines 'non-citizen'", 'cap.357', 'kuoa au kuolewa', 'marriage']),
    ('eval_347 EFD threshold',
     'Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 200,000,000, sivyo?',
     ['efd threshold tzs 11m', '11 million', '11,000,000', 'milioni 11', 'milioni kumi na moja']),
]


def _is_target(text, targets):
    return any(t.lower() in text.lower() for t in targets)


for label, q, targets in PROBES:
    print('\n' + '=' * 80)
    print(f'{label}\n  Q: {q}')

    full = [r.fact_texts[i] for i in r._encode_and_rank(q, 3)]
    print('  -- full-query arm (single-arm production) top-3:')
    for j, t in enumerate(full):
        print(f'      #{j+1}{"  <==TARGET" if _is_target(t, targets) else "        "} {t[:88]}')

    if _has_digit(q):
        stripped = strip_numeric_amounts(q)
        print(f'  -- number-stripped query: {stripped!r}')
        pool = [r.fact_texts[i] for i in r._encode_and_rank(stripped, _STRIPPED_POOL)]
        for j, t in enumerate(pool):
            print(f'      s#{j+1}{"  <==TARGET" if _is_target(t, targets) else "        "} {t[:88]}')

    final = r.retrieve(q, top_k=3)          # the actual two-arm output the orchestrator uses
    in_final = any(_is_target(t, targets) for t in final)
    print(f'  -- FINAL two-arm set ({len(final)} facts) returned to orchestrator:')
    for j, t in enumerate(final):
        print(f'      f#{j+1}{"  <==TARGET" if _is_target(t, targets) else "        "} {t[:88]}')
    verdict = ('target IN two-arm final set -> mechanism recovers it => HALLUCINATION (no retrieval fix)'
               if in_final else
               'target NOT in two-arm final set -> genuine retrieval gap => fact-base retrievability fix needed')
    print(f'  VERDICT: {verdict}')

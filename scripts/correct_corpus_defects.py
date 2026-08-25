# -*- coding: utf-8 -*-
"""CORPUS CORRECTION — the precondition of the retrain. Three defects, two dispositions.

WHY THIS RUNS BEFORE ANY RETRAIN. Measured 2026-08-25 across all 15,354 dataset rows: 64 rows
assert a **TZS 26,000 personal relief** that CLAUDE.md section 11 calls categorically wrong, 32
compute **PAYE band 2 at 9%** where the locked rate is **8%**, and 611 carry **nssf.or.tz**, a
DNS-failing domain. Sixteen, six and 115 of those respectively are inside `train_sft.jsonl` -- and
`val_sft.jsonl` carries all three, so **validation loss rewarded reproducing them.** A training row
`train_sft.jsonl:1202` matches the recorded live defect phrase for phrase. **That is recall, not
hallucination**, and retraining on uncorrected data re-teaches it.

⚠️ TWO DISPOSITIONS, AND WHY THEY DIFFER.

**A. The PAYE-arithmetic rows are QUARANTINED, not rewritten.** Correcting them means recomputing
each PAYE calculation, and R20's lesson is that a mechanical pass which manufactures a plausible
wrong fix is worse than the gap it closed -- in training data that failure is silent forever. Four
further reasons:
  1. Under **R10 (RAG-first)** the model is not the fact store; facts arrive from `locked_facts`
     at inference. A training row teaching wrong PAYE arithmetic is pure liability with no
     compensating benefit.
  2. Every one of these rows contains at least one categorically wrong statement.
  3. **R13 exists precisely for this**: `run.py generate-from-facts` regenerates pairs from the
     locked table. Quarantine-then-regenerate is the pipeline-native fix; hand-editing prose is not.
  4. The cost is 75 of 15,354 rows (0.5%), reversible and auditable in `datasets/tier1a/rejected/`.

**B. The dead domain IS rewritten -- but NOT blanket-rewritten, and that distinction is R25's.**
A first pass over every occurrence would have damaged correct content, because several occurrences
are **deliberate corrections**:

  KEPT, never touched:
    chike/generation_cleanup.py            the runtime containment. ⚠️ IT MUST SURVIVE THIS PASS:
                                           the deployed adapter still EMITS the dead domain, so
                                           removing containment before the retrain exposes users.
                                           Fixing the data is the CAUSE fix (R25); the containment
                                           comes out after the retrain, not with it.
    scripts/check_sources.py               the blocklist that rejects the dead domain
    scripts/precompute_rag_embeddings.py   two facts that SAY "Tovuti sahihi ni nssf.go.tz (si
      (and the 2 index rows built from them) nssf.or.tz)" -- correct, and rewriting them destroys
                                           the correction
    CLAUDE.md / PROGRESS.md                they document the defect on purpose
    eval/results/*.json                    RECORDED REPLIES. Rewriting a measurement falsifies it.

  FIXED:
    datasets/**/*.jsonl                    611 rows of answer text ("Thibitisha na nssf.or.tz")
    sources/whitelist.json                 ⛔ the machine-readable whitelist the pipeline enforces
                                           LISTS THE DEAD DOMAIN. CLAUDE.md section 4 says use
                                           nssf.go.tz; the file the code reads said otherwise.
    docs/reference_narrative.md            the ROOT -- the strategy document's own whitelist
                                           carries it twice, which is where the corpus learned it
    scripts/**  (generators)               so it cannot be re-emitted

**AND A GUARD ON THE MECHANICAL PASS ITSELF (R20):** no occurrence inside a NEGATION is rewritten
-- "si nssf.or.tz", "(not nssf.or.tz)", "fails DNS". Two dataset rows hit that guard. Every skip is
reported rather than silently dropped, because a pass that quietly skips is indistinguishable from
one that quietly damages.

Run with --dry-run first. R18: committed before it runs.
Artifact: eval/results/corpus_correction.json
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, 'eval', 'results', 'corpus_correction.json')
QUARANTINE = os.path.join(REPO, 'datasets', 'tier1a', 'rejected',
                          'paye_defect_quarantine_2026_08_25.jsonl')

RELIEF = re.compile(r'punguzo la kibinafsi[^.]{0,40}(26,?000|27,?000)'
                    r'|(26,?000|27,?000)[^.]{0,40}punguzo la kibinafsi', re.I)
BAND9 = re.compile(r'270,?00[01][^.]{0,60}9%|9%[^.]{0,40}270,?000', re.I)
DEAD = 'nssf.or.tz'
NEGATED = re.compile(r'(si|not|badala ya|instead of)\s*\(?\s*nssf\.or\.tz'
                     r'|nssf\.or\.tz[^,.]{0,25}(fails|si sahihi|imekufa)', re.I)

# Never touched. The first three are correct content; the last two are the record itself.
KEEP = {
    'chike/generation_cleanup.py': 'the runtime containment — must survive until after the retrain',
    'scripts/check_sources.py': 'the blocklist that REJECTS the dead domain',
    'scripts/precompute_rag_embeddings.py': 'carries two corrective facts naming the dead domain',
    'CLAUDE.md': 'documents the defect deliberately',
    'PROGRESS.md': 'documents the defect deliberately',
}
# R10-protected files, excluded by name so a glob can never reach them.
R10 = {'scripts/fixed_cell_model.py', 'scripts/fixed_cell_data.py', 'scripts/fixed_cell_train.py',
       'scripts/_trl_sft_trainer_v0_24_0.py', 'run.py'}


def rel(p):
    return os.path.relpath(p, REPO).replace('\\', '/')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    dry = args.dry_run
    report = {'measured': '2026-08-25', 'dry_run': dry,
              'harness': 'scripts/correct_corpus_defects.py',
              'kept_untouched': KEEP, 'quarantine_file': rel(QUARANTINE)}

    # ---------- A. QUARANTINE the PAYE-arithmetic rows -----------------------------------------
    quarantined, per_file = [], Counter()
    for f in sorted(glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True)):
        r = rel(f)
        if r == rel(QUARANTINE):
            continue
        lines = open(f, encoding='utf-8').read().splitlines()
        keep_lines, moved = [], 0
        for i, l in enumerate(lines):
            if not l.strip():
                keep_lines.append(l)
                continue
            has_relief, has_band9 = bool(RELIEF.search(l)), bool(BAND9.search(l))
            if has_relief or has_band9:
                try:
                    row = json.loads(l)
                except Exception:
                    keep_lines.append(l)
                    continue
                row['_quarantine'] = {
                    'from_file': r, 'from_line': i,
                    'quarantined': '2026-08-25',
                    'reasons': ([f'asserts a TZS 26,000/27,000 personal relief — CLAUDE.md §11: '
                                 f'"Any pair mentioning \'TZS 26,000 personal relief\' is WRONG"']
                                if has_relief else [])
                               + (['computes PAYE band 2 at 9%; the locked rate is 8% '
                                   '(CLAUDE.md §11)'] if has_band9 else []),
                    'disposition': 'quarantined rather than rewritten — correcting requires '
                                   'recomputing the arithmetic, and R13 '
                                   '(run.py generate-from-facts) regenerates from locked_facts, '
                                   'which is the pipeline-native fix',
                }
                quarantined.append(row)
                moved += 1
            else:
                keep_lines.append(l)
        if moved:
            per_file[r] = moved
            if not dry:
                with open(f, 'w', encoding='utf-8', newline='\n') as fh:
                    fh.write('\n'.join(keep_lines) + ('\n' if keep_lines else ''))
    if quarantined and not dry:
        os.makedirs(os.path.dirname(QUARANTINE), exist_ok=True)
        with open(QUARANTINE, 'w', encoding='utf-8', newline='\n') as fh:
            for row in quarantined:
                fh.write(json.dumps(row, ensure_ascii=False) + '\n')
    report['A_quarantine'] = {'rows': len(quarantined), 'by_file': dict(per_file)}

    # ---------- B. REWRITE the dead domain, with the negation guard -----------------------------
    targets = (glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True)
               + glob.glob(os.path.join(REPO, 'scripts', '**', '*.py'), recursive=True)
               + [os.path.join(REPO, 'sources', 'whitelist.json'),
                  os.path.join(REPO, 'docs', 'reference_narrative.md')])
    fixed, skipped_negated, skipped_kept = Counter(), [], Counter()
    for f in sorted(set(targets)):
        r = rel(f)
        if r in KEEP or r in R10:
            if DEAD in open(f, encoding='utf-8', errors='replace').read():
                skipped_kept[r] += 1
            continue
        src = open(f, encoding='utf-8').read()
        if DEAD not in src:
            continue
        out_lines, n = [], 0
        for i, line in enumerate(src.splitlines()):
            if DEAD in line and NEGATED.search(line):
                skipped_negated.append({'file': r, 'line': i,
                                        'why': 'occurrence sits inside a NEGATION — rewriting it '
                                               'would destroy a correct statement',
                                        'text': line[:160]})
                out_lines.append(line)
                continue
            if DEAD in line:
                n += line.count(DEAD)
                line = line.replace(DEAD, 'nssf.go.tz')
            out_lines.append(line)
        if n:
            fixed[r] = n
            if not dry:
                with open(f, 'w', encoding='utf-8', newline='\n') as fh:
                    fh.write('\n'.join(out_lines) + '\n')
    report['B_dead_domain'] = {
        'occurrences_rewritten': sum(fixed.values()),
        'files_touched': len(fixed),
        'by_file': dict(fixed),
        'skipped_because_NEGATED': skipped_negated,
        'skipped_because_KEPT': dict(skipped_kept),
    }

    # ---------- Verification -------------------------------------------------------------------
    left_relief = left_band9 = left_dead = 0
    for f in glob.glob(os.path.join(REPO, 'datasets', '**', '*.jsonl'), recursive=True):
        if rel(f) == rel(QUARANTINE):
            continue
        for l in open(f, encoding='utf-8'):
            if RELIEF.search(l):
                left_relief += 1
            if BAND9.search(l):
                left_band9 += 1
            if DEAD in l and not NEGATED.search(l):
                left_dead += 1
    report['verification_after'] = {
        'datasets_rows_still_asserting_relief': left_relief,
        'datasets_rows_still_at_9pct': left_band9,
        'datasets_rows_still_dead_domain_unnegated': left_dead,
        'clean': (left_relief == 0 and left_band9 == 0 and left_dead == 0) if not dry else None,
    }
    report['what_this_does_NOT_do'] = [
        'It does not rebuild the RAG index. The two index rows naming the dead domain are '
        'CORRECTIVE facts and stay. The fee-row consolidation is a separate, measured change '
        'awaiting approval; both would ride the same R15 regen.',
        'It does not remove chike/generation_cleanup.py\'s containment. The deployed adapter '
        'still emits the dead domain — the containment comes out AFTER the retrain, not with it.',
        'It does not regenerate the SFT files. generate_sft.py must be re-run (behind '
        'check_eval_split.py) before any training, or the quarantined rows are still in the '
        'exported training set.',
    ]

    if not dry:
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ('kept_untouched', 'what_this_does_NOT_do')},
                     ensure_ascii=False, indent=1)[:2600])
    if not dry:
        print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()

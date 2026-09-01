# -*- coding: utf-8 -*-
"""Post-regeneration verification: sweep the regenerated SFT files for every defect pattern
from every quarantine script (v1-v5) that has ever run against this corpus. Does not trust
the regeneration -- counts directly.

Imports each correct_corpus_defects*.py module (which each define classify(line) -> str|None)
and runs every one against every line of the four datasets/tier1a/sft/*.jsonl files.

R18: committed before its result is cited.
"""
import glob
import importlib.util
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

VERSIONS = [
    ('v1', os.path.join(HERE, 'correct_corpus_defects.py')),
    ('v2', os.path.join(HERE, 'correct_corpus_defects_v2.py')),
    ('v3', os.path.join(HERE, 'correct_corpus_defects_v3.py')),
    ('v4', os.path.join(HERE, 'correct_corpus_defects_v4.py')),
    ('v5', os.path.join(HERE, 'correct_corpus_defects_v5.py')),
]

SFT_FILES = [
    'datasets/tier1a/sft/train_sft.jsonl',
    'datasets/tier1a/sft/val_sft.jsonl',
]


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(f'quarantine_{name}', path)
    mod = importlib.util.module_from_spec(spec)
    # These modules call sys.stdout.reconfigure() and parse argv only inside main() --
    # safe to import without side effects.
    spec.loader.exec_module(mod)
    return mod


def load_classify(name, path):
    """Returns a classify(line) -> str|None function, adapted to each version's own shape.

    v3/v4/v5 already define classify(). v1/v2 predate that convention and define bare
    module-level compiled regexes instead -- wrapped here rather than edited, since editing
    a committed quarantine harness after the fact would be exactly the kind of retroactive
    rewrite R18 exists to prevent (the harness must stay exactly as it ran).
    """
    mod = _load_module(name, path)
    if hasattr(mod, 'classify'):
        return mod.classify

    if name == 'v1':
        def classify_v1(line):
            if mod.RELIEF.search(line):
                return 'RELIEF_26000'
            if mod.BAND9.search(line):
                return 'PAYE_BAND9'
            if mod.DEAD in line and not mod.NEGATED.search(line):
                return 'NSSF_DEAD_DOMAIN'
            return None
        return classify_v1

    if name == 'v2':
        def classify_v2(line):
            if mod.MINING55.search(line) and not mod.MINING55_NEGATED.search(line):
                return 'MINING55_FABRICATION'
            if mod.WCF7DAY.search(line) and not mod.WCF7DAY_HAS_TWO_STAGE.search(line):
                return 'WCF7DAY_FLAT'
            return None
        return classify_v2

    if name == 'v3':
        def classify_v3(line):
            if mod.EFDTHRESH.search(line) and not mod.REJECTION_GUARD.search(line):
                return 'EFD_THRESHOLD_11M_14M'
            return None
        return classify_v3

    raise ValueError(f'no classify() and no manual adapter for {name}')


def main():
    classifiers = {}
    for name, path in VERSIONS:
        if os.path.exists(path):
            classifiers[name] = load_classify(name, path)
        else:
            print(f'[skip] {name} not found at {path}')

    report = {'measured': '2026-09-01', 'harness': 'scripts/verify_sft_defect_free.py',
              'purpose': 'post-generate_sft.py regeneration check -- count, do not trust',
              'per_file': {}, 'totals_by_version': {v: 0 for v in classifiers}}

    grand_total_hits = 0
    for relf in SFT_FILES:
        f = os.path.join(REPO, relf)
        if not os.path.exists(f):
            report['per_file'][relf] = 'FILE NOT FOUND'
            continue
        lines = open(f, encoding='utf-8').read().splitlines()
        file_hits = {v: 0 for v in classifiers}
        for line in lines:
            if not line.strip():
                continue
            for v, classify in classifiers.items():
                cls = classify(line)
                if cls:
                    file_hits[v] += 1
                    report['totals_by_version'][v] += 1
                    grand_total_hits += 1
        report['per_file'][relf] = {'row_count': len(lines), 'hits_by_version': file_hits,
                                     'total_hits': sum(file_hits.values())}

    report['grand_total_hits'] = grand_total_hits
    report['clean'] = (grand_total_hits == 0)
    print(json.dumps(report, ensure_ascii=False, indent=1))

    out = os.path.join(REPO, 'eval', 'results', 'sft_regeneration_verification_2026_09_01.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(f'[saved] {out}')


if __name__ == '__main__':
    main()

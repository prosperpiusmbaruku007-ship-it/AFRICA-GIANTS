# -*- coding: utf-8 -*-
"""FINDING (2026-08-26): feegroup_curation.json's C1_controls are hand-authored paraphrases,
not verbatim eval-corpus text -- the same R24 baseline-reproduction gap that let the nat_34
guard reach Kaggle broken, one layer over.

WHY THIS AUDIT EXISTS. The founder's diagnosis of the nat_34 Kaggle failure was: the offline
control that was supposed to certify the ladder's C1 control question ("Nataka kusajili kampuni
yenye mtaji wa hisa milioni moja, ada ni shilingi ngapi na kuhifadhi jina ni ngapi?") is NOT the
verbatim nat_34 eval question ("nataka kusajili kampuni gharama ya kuanzia ni ngapi na kuhifadhi
jina", eval/accuracy_gate/edge_probe_natural_048.jsonl). It is an easier-worded paraphrase that
happened to still be answerable post-consolidation, so the control certified a row it was not
actually measuring. That is R24's rule ("a specimen harness must prove its baseline reproduces
the recorded live reply, verbatim, before varying anything") applying to a CURATION control
rather than a fidelity-guard baseline -- same defect class, different layer.

The instruction that follows from finding it once: audit every OTHER control in the same file,
because if one was a paraphrase, the practice was not verbatim-by-default.

METHOD. For every question in feegroup_curation.json's `C1_controls`, grep every eval/*.jsonl
corpus (excluding eval/results/, which holds measured artifacts, not source questions) for that
exact string. A hit means the control is anchored to a real, citable eval id -- a miss means it
is hand-authored and its "preserved"/"gained"/"regressed" verdict is evidence about the
paraphrase only, not about any question a gate or a real user would actually send.

RESULT: 0 of 4 C1_controls match any corpus question verbatim. All four are hand-authored.
By contrast, all 7 `rows` entries AND `C2_baseline_control` (nat_43) ARE verbatim NAT48 text --
the asymmetry is specific to C1_controls, not the whole file.

CONSEQUENCE, stated plainly and not softened: every "preserved: true" / "gained: true" verdict
recorded for a C1_control describes what happened to a question nobody in the gate or a real
user would send. It is not wrong on its own terms (the paraphrase really was or wasn't
answerable) -- it just was never evidence for what it was cited for ("nat_34 is adjudicated
CORRECT and GROUNDED off this ladder. If consolidation breaks it, the arm traded one wrong
answer for another" -- the arm being checked was not the one that actually broke). The nat_34
Kaggle failure is the direct, measured consequence of trusting this control literally.

R18: committed before its result is written up.
Artifact: eval/results/feegroup_curation_controls_verbatim_audit.json
"""
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CURATION = os.path.join(REPO, 'eval', 'results', 'feegroup_curation.json')
OUT = os.path.join(REPO, 'eval', 'results', 'feegroup_curation_controls_verbatim_audit.json')


def _all_corpus_questions():
    """Every question string in every eval/**/*.jsonl corpus, excluding eval/results/
    (measured artifacts, not source questions) -- keyed by (file, id, text)."""
    out = []
    for path in glob.glob(os.path.join(REPO, 'eval', '**', '*.jsonl'), recursive=True):
        rel = os.path.relpath(path, REPO).replace('\\', '/')
        if rel.startswith('eval/results/'):
            continue
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                for field in ('question', 'question_sw'):
                    if isinstance(row.get(field), str):
                        out.append((rel, row.get('id', row.get(field)[:30]), row[field]))
    return out


def main():
    curation = json.load(open(CURATION, encoding='utf-8'))
    corpus = _all_corpus_questions()
    corpus_texts = {text for _, _, text in corpus}

    rows_verdict = []
    for entry in curation.get('rows', []):
        q = entry['question']
        rows_verdict.append({'id': entry['id'], 'verbatim': q in corpus_texts})

    c2 = curation.get('C2_baseline_control')

    c1_verdict = []
    for i, c in enumerate(curation.get('C1_controls', [])):
        q = c['question']
        c1_verdict.append({
            'index': i,
            'question': q,
            'why': c.get('why'),
            'verbatim_in_any_corpus': q in corpus_texts,
        })

    rows_all_verbatim = all(r['verbatim'] for r in rows_verdict)
    c1_none_verbatim = all(not c['verbatim_in_any_corpus'] for c in c1_verdict)

    out = {
        'measured': '2026-08-26',
        'harness': __file__,
        'finding': (
            'C1_controls in feegroup_curation.json are hand-authored paraphrases, not verbatim '
            'eval-corpus questions -- R24s baseline-reproduction gap, applied to a curation '
            'control rather than a fidelity-guard baseline. This is what let the nat_34 C1 '
            'control report "preserved/gained" while the real, verbatim NAT48 question '
            'regressed on the actual Kaggle regen.'
        ),
        'rows_all_verbatim': rows_all_verbatim,
        'rows': rows_verdict,
        'c2_baseline_control_is_nat_43_verbatim': True,
        'c1_controls_none_verbatim': c1_none_verbatim,
        'c1_controls': c1_verdict,
        'recommendation': (
            'Any FUTURE curation control must either (a) be the verbatim question text of a '
            'named eval id, or (b) if hand-authored for a case no corpus id covers, be labelled '
            'as such in the artifact and never cited as certifying a specific eval id\'s '
            'guard. Do not retroactively rewrite this frozen artifact (R18) -- this audit '
            'stands beside it as the correction.'
        ),
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'rows_all_verbatim: {rows_all_verbatim}')
    print(f'c1_controls_none_verbatim: {c1_none_verbatim}')
    for c in c1_verdict:
        print(f"  C1[{c['index']}] verbatim={c['verbatim_in_any_corpus']}: {c['question'][:70]}")
    print(f'\n[saved] {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

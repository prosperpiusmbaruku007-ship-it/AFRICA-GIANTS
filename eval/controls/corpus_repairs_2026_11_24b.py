# -*- coding: utf-8 -*-
"""MEDICINES CALLED ZERO-RATED IN THE TRAINING CORPUS (founder: quarantine the six authored pairs after reading each, R37; reach datasets/tier1a/sft/, R36).

THE SIX WERE READ IN FULL BEFORE ANY ACTION (R37: adversarial pairs are the highest-risk population for a presence-keyed sweep, and a flag is a mention, not a defect, until read):
  QUARANTINE (2)  tier1a_vat_007_20260608   "Dawa nyingi za binadamu Tanzania zimewekwa kwenye orodha ya zero-rated -- yaani VAT ni asilimia 0"        flat assertion
                  tier1a_refusal_020_20260608  malaria medicines "ziko kwenye orodha ya zero-rated ya VAT, yaani hazilipwi VAT (asilimia 0)"           flat assertion
  REPAIR (shared) raw_pairs_batch_011 line 110 and its 23 siblings: ONE answer reused under 24 questions about a 5% VAT rate; only its medicines SENTENCE ("zero-rated (0% VAT -- unaweza kudai input VAT)") is wrong (an exempt supply gives no input credit) -> that sentence is replaced, nothing is removed (R37: 24 removals for one sentence would be the over-removal this rule exists for)
  REPAIR  (2)     tier1a_vat_011_20260608   adversarial "Tanzania has no 5% VAT": the CLAIM is correct and worth keeping; only the aside "dawa ... zinaweza kuwa zero-rated au exempt" (and the unverified grains / farm inputs) is wrong -> aside replaced by the Schedule wording
                  tier1a_efd_237_20260609   pharmacy EFD: the answer is about EFD; only "huru ya VAT (exempt) au za kiwango cha sifuri" is loose -> "msamaha wa VAT (exempt)"
  LEFT ALONE (1)  raw_pairs_batch_009 line 56  an out-of-knowledge REFUSAL that lists "zimesamehewa, zero-rated, au ... msamaha" as the options the question is about: it asserts nothing. NOTE: it teaches a refusal on a question the corpus now answers; reported, not touched.

TARGETS ARE RESOLVED BY CONTENT (the OLD ANSWER) in EVERY stage that holds the row (cleaned_pairs, sft_shaped_pairs, raw_sources); a target that resolves to nothing FAILS LOUDLY. Old rows are kept in datasets/tier1a/rejected/ and in the rewrite record, reversible.
REPORT-ONLY BY DEFAULT.   python eval/controls/corpus_repairs_2026_11_24b.py [--write]"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WRITE = "--write" in sys.argv
STAGES = ["datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/raw_sources/*.jsonl"]
REJ = os.path.join(REPO, "datasets", "tier1a", "rejected")

# (answer prefix that identifies the OLD answer, class, reason quoting the row)
QUARANTINE = [
    ("Dawa nyingi za binadamu Tanzania zimewekwa kwenye orodha ya zero-rated", "MEDICINES_CALLED_ZERO_RATED",
     "asserts 'Dawa nyingi za binadamu Tanzania zimewekwa kwenye orodha ya zero-rated -- yaani VAT ni asilimia 0': VAT Act Cap.148 R.E.2023 Schedule Part I item 7 lists approved medicine, drugs and medical equipment as EXEMPT; a supply that is both exempt and zero-rated is zero-rated (s.5(3)), i.e. only exports."),
    ("Dawa nyingi za binadamu Tanzania — ikiwemo dawa za malaria", "MEDICINES_CALLED_ZERO_RATED",
     "asserts malaria medicines 'ziko kwenye orodha ya zero-rated ya VAT, yaani hazilipwi VAT (asilimia 0)': same Schedule item 7 (exempt, not zero-rated)."),
]
REPAIR = [
    ("Hapana. Tanzania haina kiwango cha VAT cha asilimia 5 cha aina yoyote",
     "Hapana. Tanzania haina kiwango cha VAT cha asilimia 5 cha aina yoyote, pamoja na bidhaa za muhimu ('essential goods'). Baadhi ya bidhaa muhimu, kama dawa muhimu na vifaa tiba vilivyoidhinishwa na Waziri, ni msamaha wa VAT (exempt), na mauzo ya nje ni zero-rated (asilimia 0); lakini asilimia 5 haipo. Kiwango cha kawaida cha VAT ni asilimia 18 tu.",
     "No. Tanzania does not have a 5% VAT rate of any kind, including for 'essential goods'. Some essential items, such as essential medicines and medical equipment approved by the Minister, are VAT-exempt, and exports are zero-rated (0%); but 5% does not exist. The standard VAT rate is 18% only."),
    ("Maduka ya dawa (pharmacy) Tanzania yanayofanya mauzo ya dawa lazima yatumie EFD",
     "Maduka ya dawa (pharmacy) Tanzania yanayofanya mauzo ya dawa lazima yatumie EFD kama biashara nyingine zilizolazimishwa. Dawa na vifaa tiba vilivyoidhinishwa na Waziri ni msamaha wa VAT (exempt) — EFD lazima iwe na programu inayoweza kuziainisha kwa usahihi. Pia, pharmacy inaweza kuhitaji leseni maalum ya TMDA mbali na EFD ya TRA. Angalia TRA na TMDA kwa mahitaji yote yanayohusika.",
     "Pharmacies in Tanzania making medicine sales must use an EFD like other mandatory businesses. Essential medicines and medical equipment approved by the Minister are VAT-exempt: the EFD must have software that can categorise them correctly. Also, a pharmacy may need a specific TMDA licence separate from TRA's EFD. Check TRA and TMDA for all applicable requirements."),
]

# SHARED ANSWER: "Tanzania ina viwango VITATU vya VAT peke yake ..." is ONE answer reused verbatim under 24 rows (14+ paraphrases of 'is there a 5% VAT?'). Quarantining them would over-remove 24 rows for one wrong sentence (R37), so only that SENTENCE is replaced, in every location, and each row must contain it.
SHARED_PREFIX = "Tanzania ina viwango VITATU vya VAT peke yake"
SHARED_OLD = "Madawa mengi ya hospitali (dawa muhimu) yanaweza kuwa zero-rated (0% VAT — unaweza kudai input VAT) au exempt (huna wajibu wa VAT lakini pia huwezi kudai input VAT) — si 5%. Hizi ni hali tofauti kisheria — thibitisha hali ya dawa maalum na orodha rasmi ya TRA (tra.go.tz)."
SHARED_NEW = "Dawa muhimu za binadamu na vifaa tiba vilivyoidhinishwa na Waziri ni msamaha wa VAT (exempt): hakuna VAT inayotozwa kwenye mauzo hayo, na huwezi kudai input VAT kwa mauzo yaliyosamehewa — si asilimia 5. Thibitisha hali ya dawa maalum na TRA (tra.go.tz)."


def read(p):
    return io.open(p, encoding="utf-8", newline="").read()


def atext(r):
    return (r.get("answer_sw") or r.get("output") or "").strip()


def plan():
    files = sorted({f for g in STAGES for f in glob.glob(os.path.join(REPO, g))})
    loaded = {}
    for f in files:
        rows = []
        for i, line in enumerate(read(f).splitlines(), 1):
            if line.strip():
                try:
                    rows.append((i, json.loads(line)))
                except ValueError:
                    pass
        loaded[f] = rows
    acts = []

    def find(pre):
        return [(f, ln, r) for f, rows in loaded.items() for ln, r in rows if atext(r).startswith(pre)]
    for pre, cls, reason in QUARANTINE:
        hits = find(pre)
        assert hits, f"quarantine target resolves to NOTHING: {pre[:50]}"
        acts += [("quarantine", f, ln, r, {"cls": cls, "reason": reason}) for f, ln, r in hits]
    for pre, sw, en in REPAIR:
        hits = [h for h in find(pre) if atext(h[2]) != sw.strip()]
        assert hits, f"repair target resolves to NOTHING: {pre[:50]}"
        acts += [("repair", f, ln, r, {"sw": sw, "en": en}) for f, ln, r in hits]
    shared = find(SHARED_PREFIX)
    assert shared, "shared answer resolves to NOTHING"
    for f, ln, r in shared:
        t = atext(r)
        if SHARED_OLD in t:
            acts.append(("sentence", f, ln, r, {}))
        else:
            assert SHARED_NEW in t or "Madawa mengi ya hospitali" not in t, f"shared answer at {f}:{ln} carries a medicines sentence in an UNKNOWN form: refusing to guess"
    return acts


def main():
    acts = plan()
    for kind, f, ln, r, spec in acts:
        print(f"  {kind:<10} {os.path.relpath(f, REPO).replace(chr(92), '/').replace('datasets/tier1a/', '')}:{ln}  {r.get('id', '-')}  | {atext(r)[:70]}")
    print(f"{len(acts)} location-actions: {sum(a[0] == 'quarantine' for a in acts)} quarantine, {sum(a[0] == 'repair' for a in acts)} repair, {sum(a[0] == 'sentence' for a in acts)} one-sentence repair")
    if not WRITE:
        print("(report only; --write applies)")
        return 0
    os.makedirs(REJ, exist_ok=True)
    per = {}
    for a in acts:
        per.setdefault(a[1], []).append(a)
    rec_q, rec_r = [], []
    for f, items in per.items():
        raw = read(f)
        eol = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(eol)
        rel = os.path.relpath(f, REPO).replace("\\", "/")
        for kind, _, ln, r, spec in sorted(items, key=lambda x: -x[2]):
            if kind == "sentence":
                new = dict(r)
                for k in ("answer_sw", "output"):
                    if k in r:
                        assert SHARED_OLD in r[k]
                        new[k] = r[k].replace(SHARED_OLD, SHARED_NEW)
                rec_r.append({"source_file": rel, "source_line": ln, "action": "one_sentence_replaced_in_place", "old_sentence": SHARED_OLD, "new_sentence": SHARED_NEW, "id": r.get("id")})
                lines[ln - 1] = json.dumps(new, ensure_ascii=False)
            elif kind == "quarantine":
                rec_q.append({"source_file": rel, "source_line_at_quarantine": ln, "action": "removed_from_live_corpus", "defect_class": spec["cls"], "reason": spec["reason"], "row": r})
                del lines[ln - 1]
            else:
                new = dict(r)
                for k in ("answer_sw", "output"):
                    if k in r:
                        new[k] = spec["sw"]
                if "answer_en" in r:
                    new["answer_en"] = spec["en"]
                rec_r.append({"source_file": rel, "source_line": ln, "action": "answer_rewritten_in_place", "old": {k: r[k] for k in ("answer_sw", "output", "answer_en") if k in r}, "new": {k: new[k] for k in ("answer_sw", "output", "answer_en") if k in new}})
                lines[ln - 1] = json.dumps(new, ensure_ascii=False)
        io.open(f, "w", encoding="utf-8", newline="").write(eol.join(lines))
    with io.open(os.path.join(REJ, "medicines_zero_rated_quarantine_2026_11_24.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for x in rec_q:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    with io.open(os.path.join(REPO, "eval", "results", "corpus_rewrites_2026_11_24b.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for x in rec_r:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"WRITTEN: {len(rec_q)} removals, {len(rec_r)} rewrites")
    return 0


if __name__ == "__main__":
    sys.exit(main())

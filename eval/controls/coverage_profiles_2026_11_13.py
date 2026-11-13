"""READ-ONLY coverage survey for the three pilot participant profiles (employer 3-15 staff, trader TZS 11M-200M, bookkeeper).

For every question it records, from the REAL classifier, router, rules engine and the committed index (kaggle/ copy, byte-identical to
chike-inference/): the route (engine name, fact, refusal, clarification), whether any model call happened, the top-3 retrieved facts, how
often the generic "Mauzo yangu ya mwaka ni milioni 15..." row sits in the top 3, and -- where a `want` pattern names the row the question
needs -- that row's RANK (R15 step zero: measure the rank before touching wording). The model is a counting stub: this measures ROUTES AND
RETRIEVAL, never reply quality.

    python eval/controls/coverage_profiles_2026_11_13.py --label before
    python eval/controls/coverage_profiles_2026_11_13.py --label after --compare before   # route changes + rank changes vs a prior artifact

Population note (R22): these questions were authored by the engineer from the three profiles. They enumerate LIKELY questions; they are not a
count of what participants ask. Kinds: base = the original 66-question survey, A/B/C = a gap named for the batch, ctl = a control that must
NOT change route (R12c step 2).
"""
import argparse
import hashlib
import json
import os
import re
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
GENERIC_ROW = re.compile(r"Mauzo yangu ya mwaka ni milioni 15", re.I)

# (kind, profile, question, want-regex or None)   `want` names the existing row a question needs (None = no row exists / unknown yet)
E, T, B = "1 EMPLOYER 3-15", "2 TRADER 11M-200M", "3 BOOKKEEPER MIXED"
EXTRA = [
    # ── A. ROUTING: minimum wage ──────────────────────────────────────────────────────────────────────────────────────────────
    ("A", E, "Nalipa dada wa kazi za nyumbani 150,000 kwa mwezi, ni halali?", None),
    ("A", E, "Nalipa mfanyakazi wa nyumbani 150,000 kwa mwezi, je ni sawa?", None),
    ("A", E, "Mfanyakazi wa duka analipwa 200,000 kwa mwezi, je inatosha kisheria?", None),
    ("A", E, "Nalipa mlinzi 120,000 kwa mwezi, ni halali?", None),
    ("A", E, "Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?", r"GN605A rate range|domestic"),
    ("A", E, "Kima cha chini cha mshahara kwa mfanyakazi wa duka ni kiasi gani?", r"GN 605A|GN605A"),
    ("A", E, "Kima cha chini cha mshahara kwa mlinzi ni kiasi gani?", r"GN 605A|GN605A"),
    # ── A. ROUTING: presumptive ───────────────────────────────────────────────────────────────────────────────────────────────
    ("A", T, "Kodi ya makadirio kwa mauzo ya milioni 40 ni kiasi gani?", None),
    ("A", T, "Nina duka, mauzo milioni 80 kwa mwaka, kodi ya makadirio ni ngapi?", None),
    ("A", T, "Kodi ya duka la rejareja la milioni 80 kwa mwaka?", None),
    ("A", T, "Mauzo ya mwaka ni milioni 150, nalipa kodi gani?", None),
    # ── controls that must stay where they are ───────────────────────────────────────────────────────────────────────────────
    ("ctl", E, "Mshahara wa mfanyakazi ni 800,000 kwa mwezi, PAYE ni kiasi gani?", None),
    ("ctl", E, "Je, ni halali kumfukuza mfanyakazi bila notisi?", None),
    ("ctl", T, "Je, ni halali kutumia risiti ya mkono badala ya EFD?", None),
    ("ctl", T, "Mauzo yangu ni milioni 50 kwa mwaka. Je, ni lazima nijisajili VAT?", None),
    ("ctl", T, "Mauzo yangu ni milioni 40 kwa mwaka, nalipa kodi ya makadirio kiasi gani?", None),
    ("ctl", B, "Kampuni ina mapato ya milioni 300, kodi ya mapato ya kampuni ni asilimia ngapi?", None),
    # ── B. EXISTING ROWS THAT DO NOT SURFACE ─────────────────────────────────────────────────────────────────────────────────
    ("B", E, "Nikichelewa kulipa PAYE kuna adhabu gani?", r"Late PAYE remittance penalty"),
    ("B", T, "Nikikosa kutoa risiti ya EFD adhabu ni nini?", r"efd tra closure authority"),
    ("B", B, "Mteja alichelewa kuwasilisha return ya VAT, faini ni kiasi gani?", r"vat late (return|filing)"),
    ("B", T, "Naweza kudai VAT niliyolipa nikinunua bidhaa za biashara?", r"input VAT"),
    ("B", B, "Mteja anapaswa kulipa kodi ya mapato kwa awamu lini?", r"provisional tax instalments"),
    ("B", E, "Mshahara wa chini kwa dada wa kazi za nyumbani ni kiasi gani?", r"GN605A rate range"),
    ("B", E, "Je, ni lazima nijisajili WCF nikiwa na wafanyakazi 5?", r"wcf (employer )?registration|WCF.{0,60}(sajili|regist)"),
    ("B", E, "OSHA inahitaji nini kwa duka lenye wafanyakazi 10?", r"OSHA Tanzania: kila mwajiri"),
    # ── C. NEW FACTS: no row exists today (wants are filled in once the facts do) ─────────────────────────────────────────────
    ("C", E, "PAYE inalipwa tarehe ngapi kila mwezi?", None),
    ("C", E, "Return ya PAYE inawasilishwa lini?", None),
    ("C", E, "Je, ni lazima kila mfanyakazi awe na mkataba wa maandishi?", None),
    ("C", E, "Naweza kumfukuza mfanyakazi bila notisi? Notisi ni muda gani?", None),
    ("C", E, "Mfanyakazi akiachishwa kazi anastahili malipo ya kuachishwa (severance) kiasi gani?", None),
    ("C", E, "Likizo ya mwaka ni siku ngapi?", None),
    ("C", E, "Overtime inalipwa kiasi gani?", None),
    ("C", E, "Likizo ya uzazi ni siku ngapi?", None),
    ("C", E, "Likizo ya baba (paternity leave) ni siku ngapi?", None),
    ("C", T, "Nitapataje TIN?", None),
    ("C", T, "Je, mtu binafsi mwenye biashara anatakiwa kuwasilisha return ya kodi ya mapato lini?", None),
    ("C", T, "Naweza kujisajili VAT kwa hiari nikiwa na mauzo madogo?", None),
    ("C", T, "Nawezaje kurejeshewa VAT (VAT refund)?", None),
    ("C", T, "Nimeuza kwa mkopo, VAT inalipwa lini?", None),
    ("C", B, "Ushuru wa zuio kwa huduma za mkandarasi ni asilimia ngapi?", None),
    ("C", B, "Kodi ya zuio kwenye gawio (dividend) ni asilimia ngapi?", None),
    ("C", B, "Rekodi za biashara zihifadhiwe kwa miaka mingapi?", None),
    ("C", B, "Naweza kudai VAT ya pembejeo kwa gari la kampuni?", None),
    # ── D. KEPT AS REFUSALS ──────────────────────────────────────────────────────────────────────────────────────────────────
    ("D", B, "Capital gains tax kwa kuuza hisa ni asilimia ngapi?", None),
    ("D", B, "Transfer pricing inahitaji nyaraka gani?", None),
    ("D", B, "Stamp duty kwenye mkataba wa pango ni kiasi gani?", None),
    ("D", B, "Kodi ya majengo (property tax) inalipwa kwa nani?", None),
    ("D", T, "Ninaagiza bidhaa kutoka China, ushuru wa forodha ni kiasi gani?", None),
    ("D", B, "Mteja ana biashara Zanzibar, ZRA inatoza nini?", None),
]


def all_cases():
    base = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "coverage_profiles_base_questions.json"), encoding="utf-8"))
    cases = [("base", prof, q, None) for prof, qs in base.items() for q in qs]
    return cases + EXTRA


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--compare")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    os.chdir(REPO)
    from chike import answer_trace, retrieval
    from chike.model_abstraction.test_double import FakeBackend
    from chike.orchestrator import Orchestrator

    same = hashlib.sha256(open("kaggle/rag_facts_text.json", "rb").read()).hexdigest() == \
        hashlib.sha256(open("chike-inference/rag_facts_text.json", "rb").read()).hexdigest() and \
        hashlib.sha256(open("kaggle/rag_embeddings.npy", "rb").read()).hexdigest() == \
        hashlib.sha256(open("chike-inference/rag_embeddings.npy", "rb").read()).hexdigest()
    assert same, "kaggle/ and chike-inference/ index copies differ: this would not be measuring what production serves"
    orc = Orchestrator(backend=FakeBackend(scripted_reply="[MODEL]"))
    R = retrieval.Retriever()
    out = os.path.join("eval", "results", f"coverage_profiles_{a.label}.json")
    rows = []
    for kind, prof, q, want in all_cases():
        try:
            r = orc.answer(q)
            t = answer_trace.trace(r)
            top3 = R.retrieve(q, top_k=3)
            wide = R.retrieve(q, top_k=30)
            rank = None
            if want:
                rx = re.compile(want, re.I)
                rank = next((i + 1 for i, f in enumerate(wide) if rx.search(f)), ">30")
            row = dict(kind=kind, profile=prof, q=q, path=t["path"], model_calls=r.model_calls, refused=r.refused, guards=t["guards"],
                       text=(r.text or "")[:200].replace("\n", " "), top3=[f[:110].replace("\n", " ") for f in top3],
                       generic_in_top3=any(GENERIC_ROW.search(f) for f in top3), want=want, want_rank=rank)
        except Exception as e:                                             # noqa: BLE001 -- a per-row error must not lose the run
            row = dict(kind=kind, profile=prof, q=q, error=repr(e)[:200])
        rows.append(row)
        json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)     # after EVERY row (R16)
    ok = [r for r in rows if "error" not in r]
    print(f"{len(rows)} questions, {len(rows) - len(ok)} errors -> {out}")
    print("generic row in top 3:", sum(r["generic_in_top3"] for r in ok), "of", len(ok))
    prev = {}
    if a.compare:
        prev = {r["q"]: r for r in json.load(open(os.path.join("eval", "results", f"coverage_profiles_{a.compare}.json"), encoding="utf-8"))}
    for r in ok:
        p = prev.get(r["q"])
        tag = ""
        if p and "error" not in p:
            if p["path"] != r["path"]:
                tag += f"  ROUTE {p['path']} -> {r['path']}"
            if p.get("want_rank") != r.get("want_rank"):
                tag += f"  RANK {p.get('want_rank')} -> {r.get('want_rank')}"
        print(f"[{r['kind']:>4}] {r['path']:<28} calls={r['model_calls']} rank={r['want_rank']!s:>4} gen={int(r['generic_in_top3'])} {r['q'][:70]}{tag}")


if __name__ == "__main__":
    main()

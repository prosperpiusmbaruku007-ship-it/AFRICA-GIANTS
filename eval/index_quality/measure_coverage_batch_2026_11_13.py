# -*- coding: utf-8 -*-
"""MEASURE THE 2026-11-13 COVERAGE BATCH AGAINST A PROSPECTIVE INDEX, LOCALLY, BEFORE ANY KAGGLE REGEN (R15 step zero, R12c).

Builds the prospective index exactly as the regen will (scripts/precompute_rag_embeddings.build_fact_texts() + local e5-base, the same model
the regen uses -- loadable offline from the HF cache, see dryrun_regen_2026_10_06.py), and compares it to the committed index embedded the
SAME way (so a difference is the batch, not the hardware). Questions: the 115-question coverage harness plus extra phrasings per new fact
(so a fact is not tuned to the one phrasing its author imagined -- R21/R33).

REPORTS
  TARGETS      per question that names the row it needs: rank before/after, and PASS if the needed row is in the top 3
  HIJACKS      questions where a NEW row enters the top 3 that is not one of that question's wanted rows (pollution of unrelated questions)
  GENERIC ROW  how many questions carry the 'Mauzo yangu ya mwaka ni milioni 15...' row (index row 58) in the top 3, before and after
  GUARDS       the committed regen critical queries (kaggle/regenerate_rag_e5.py) replayed against the prospective index
  ANCHORS      every committed guard anchor must resolve to at least one row (no dead anchor) -- uniqueness reported, not assumed

    python eval/index_quality/measure_coverage_batch_2026_11_13.py --label draft1 [--baseline-only]
Artifact: eval/results/coverage_batch_<label>.json   (written after the run; embeddings cached in scratch/ so iterating is fast)
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import sys

import numpy as np

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "eval", "controls"))
SCRATCH = os.path.join(REPO, "scratch")
CACHE = os.path.join(SCRATCH, "emb_cache_e5.json")
GENERIC = re.compile(r"Mauzo yangu ya mwaka ni milioni 15", re.I)

# question -> the fact KEYS that answer it (any one in the top 3 counts). Extra phrasings are deliberate: a fact tuned to one wording
# of its own question is a fit, not a retrieval property.
W = {
    # employer
    "PAYE inalipwa tarehe ngapi kila mwezi?": ["paye_remittance_deadline"],
    "Return ya PAYE inawasilishwa lini?": ["paye_remittance_deadline"],
    "Mwisho wa kulipa PAYE kwa TRA ni lini?": ["paye_remittance_deadline"],
    "Nilipe PAYE ya wafanyakazi wangu kabla ya tarehe ngapi?": ["paye_remittance_deadline"],
    "Je, ni lazima kila mfanyakazi awe na mkataba wa maandishi?": ["employment_particulars_required", "employment_particulars_keeping"],
    "Mfanyakazi mpya nimpe nini cha maandishi anapoanza kazi?": ["employment_particulars_required"],
    "Nahifadhi mikataba ya wafanyakazi waliondoka kwa muda gani?": ["employment_particulars_keeping"],
    "Naweza kumfukuza mfanyakazi bila notisi? Notisi ni muda gani?": ["termination_notice_period"],
    "Notisi ya kuachisha mfanyakazi wa kila mwezi ni siku ngapi?": ["termination_notice_period"],
    "Nataka kuacha kazi, natakiwa kutoa notisi ya muda gani?": ["termination_notice_period"],
    "Mfanyakazi akiachishwa kazi anastahili malipo ya kuachishwa (severance) kiasi gani?": ["severance_pay"],
    "Nimemfukuza mfanyakazi aliyefanya kazi miaka 4, nimlipe nini?": ["severance_pay"],
    "Severance pay inahesabiwaje?": ["severance_pay"],
    "Likizo ya mwaka ni siku ngapi?": ["annual_leave_days"],
    "Mfanyakazi ana haki ya likizo ya siku ngapi kwa mwaka?": ["annual_leave_days"],
    "Overtime inalipwa kiasi gani?": ["overtime_pay_rate"],
    "Nikimfanyisha mfanyakazi saa za ziada nimlipe mara ngapi ya mshahara?": ["overtime_pay_rate"],
    "Mfanyakazi anaruhusiwa kufanya kazi saa ngapi kwa siku?": ["working_hours_limits"],
    "Saa za kazi kwa wiki ni ngapi kisheria?": ["working_hours_limits"],
    "Likizo ya uzazi ni siku ngapi?": ["maternity_leave_days"],
    "Mfanyakazi wangu amejifungua, apewe likizo ya siku ngapi?": ["maternity_leave_days"],
    "Mtoto akizaliwa kabla ya wakati mama anapata likizo ya uzazi ya muda gani?": ["maternity_leave_premature_birth"],
    "Likizo ya baba (paternity leave) ni siku ngapi?": ["paternity_leave_days"],
    "Mfanyakazi mwanaume amepata mtoto, apewe siku ngapi za likizo?": ["paternity_leave_days"],
    "Nimemfukuza mfanyakazi bila utaratibu, fidia ya kuachishwa kazi isivyo haki ni kiasi gani?": ["unfair_termination_compensation"],
    "Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?": ["domestic_worker_minimum_wage"],
    "Mshahara wa chini kwa dada wa kazi za nyumbani ni kiasi gani?": ["domestic_worker_minimum_wage"],
    "Dada wa kazi anayeishi kwangu analipwa kiasi gani kisheria?": ["domestic_worker_minimum_wage"],
    # trader / bookkeeper
    "Nitapataje TIN?": ["tin_apply_deadline"],
    "Nimeanza biashara, nisajili TIN ndani ya muda gani?": ["tin_apply_deadline"],
    "Je, mtu binafsi mwenye biashara anatakiwa kuwasilisha return ya kodi ya mapato lini?": ["individual_income_tax_return"],
    "Mwisho wa kuwasilisha return ya kodi ya mapato kwa mtu binafsi ni lini?": ["individual_income_tax_return"],
    "Kodi ya zuio kwenye gawio (dividend) ni asilimia ngapi?": ["dividend_withholding_rate"],
    "Natoa gawio kwa wanahisa wa kampuni yangu, nakata kodi ya zuio asilimia ngapi?": ["dividend_withholding_rate"],
    "Ushuru wa zuio kwa huduma za mkandarasi ni asilimia ngapi?": ["professional_service_fee_wht"],
    "Nikimlipa mshauri wa kodi au mhasibu, nakata kodi ya zuio asilimia ngapi?": ["professional_service_fee_wht"],
    # NOT a target: "can I register voluntarily?" is a STOPPED item (the VAT Act has no such provision), so no row answers it.
    "Mhasibu au wakili anahitaji kusajili VAT hata kama mauzo ni madogo?": ["vat_registration_who_must"],
    "Nawezaje kurejeshewa VAT (VAT refund)?": ["vat_refund_when", "vat_refund_deadline"],
    "Nina VAT ya ziada kwa miezi mingi, naweza kurudishiwa pesa?": ["vat_refund_when"],
    "Nina muda gani wa kuomba kurejeshewa VAT?": ["vat_refund_deadline"],
    "Nimeuza kwa mkopo, VAT inalipwa lini?": ["vat_credit_sale_timing"],
    "Mteja hajanilipa bado, nalipa VAT ya mauzo hayo lini?": ["vat_credit_sale_timing"],
    "Rekodi za biashara zihifadhiwe kwa miaka mingapi?": ["record_keeping_period"],
    "Nihifadhi risiti na vitabu vya mahesabu kwa muda gani?": ["record_keeping_period"],
    "Naweza kudai VAT ya pembejeo kwa gari la kampuni?": ["input_vat_passenger_vehicle"],
    "Nimenunua gari la kampuni, naweza kudai VAT niliyolipa?": ["input_vat_passenger_vehicle"],
    "Mteja alichelewa kuwasilisha return ya VAT, faini ni kiasi gani?": ["late_return_penalty"],
    "Nikichelewa kuwasilisha return ya kodi ya mapato adhabu ni nini?": ["late_return_penalty"],
    # B: rows that exist today but do not surface
    "Nikichelewa kulipa PAYE kuna adhabu gani?": ["paye_penalty_rate"],
    "PAYE nimechelewa kulipa mwezi mmoja, nitatozwa nini?": ["paye_penalty_rate"],
    "Nikikosa kutoa risiti ya EFD adhabu ni nini?": ["efd_tra_closure_authority"],
    "TRA inaweza kuchukua hatua gani nikiacha kutoa risiti za EFD?": ["efd_tra_closure_authority"],
    "Naweza kudai VAT niliyolipa nikinunua bidhaa za biashara?": ["VAT_zero_rated_vs_exempt_input_VAT"],
    "Je, nadai VAT ya manunuzi (input VAT) ya biashara yangu?": ["VAT_zero_rated_vs_exempt_input_VAT"],
    "Mteja anapaswa kulipa kodi ya mapato kwa awamu lini?": ["provisional_tax_instalments"],
    "Nalipa kodi ya mapato kwa awamu (instalment) mara ngapi kwa mwaka?": ["provisional_tax_instalments"],
    # rows that already served well and must KEEP serving (regression protection for the rows the batch could displace)
    "NSSF ya mwajiri ni asilimia ngapi?": ["nssf_employer_rate"],
    "SDL ni asilimia ngapi na inalipwa lini?": ["sdl_rate", "sdl_payment_deadline"],
    "Mwisho wa kulipa NSSF ni tarehe ngapi kila mwezi?": ["nssf_payment_deadline"],
    "VAT ni asilimia ngapi?": ["vat_standard_rate"],
    "Kizingiti cha kujisajili VAT ni kiasi gani?": ["vat_registration_threshold_annual", "vat_registration_threshold"],
    "Return ya VAT inawasilishwa lini?": ["vat_return_submission_deadline", "vat_credit_sale_timing"],
    "Je, ni lazima nijisajili WCF nikiwa na wafanyakazi 5?": ["small_headcount_still_register", "wcf_new_employer_registration"],
    "Mfanyakazi akipata ajali kazini nifanye nini? Natakiwa kuripoti WCF ndani ya siku ngapi?": ["wcf_accident_reporting", "wcf_accident_reporting_deadline"],
    "Leseni ya biashara inaisha lini?": ["business_licence_expiry_30_june"],
    "Je, nikipanga fremu ya duka nakatwa kodi ya zuio ya pango?": ["rent_wht_rate"],
    "Naanza kutumia EFD lini, kuna kizingiti cha mauzo?": ["efd_threshold_tzs_11m", "efd_not_every_business"],
    "Je, ni lazima nitumie mashine ya EFD? Mauzo yangu ni milioni 30.": ["efd_threshold_tzs_11m", "efd_not_every_business"],
}


def sha(t):
    return hashlib.sha1(t.encode("utf-8")).hexdigest()


def load_pre():
    spec = importlib.util.spec_from_file_location("precompute_rag_embeddings", os.path.join(REPO, "scripts", "precompute_rag_embeddings.py"))
    pre = importlib.util.module_from_spec(spec)
    sys.modules["precompute_rag_embeddings"] = pre
    spec.loader.exec_module(pre)
    return pre


def embed_all(model, texts):
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    miss = [t for t in texts if sha(t) not in cache]
    if miss:
        emb = model.encode([f"passage: {t}" for t in miss], batch_size=16, show_progress_bar=False, convert_to_numpy=True)
        for t, e in zip(miss, emb):
            cache[sha(t)] = [float(x) for x in e]
        json.dump(cache, open(CACHE, "w", encoding="utf-8"))
    m = np.array([cache[sha(t)] for t in texts])
    return m / (np.linalg.norm(m, axis=1, keepdims=True) + 1e-10)


def write_index(name, texts, emb):
    d = os.path.join(SCRATCH, name)
    os.makedirs(d, exist_ok=True)
    np.save(os.path.join(d, "rag_embeddings.npy"), emb)
    json.dump(texts, open(os.path.join(d, "rag_facts_text.json"), "w", encoding="utf-8"), ensure_ascii=False)
    return os.path.join(d, "rag_embeddings.npy"), os.path.join(d, "rag_facts_text.json")


def load_assign(name):
    tree = ast.parse(open(os.path.join(REPO, "kaggle", "regenerate_rag_e5.py"), encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            # `KNOWN_FAILING: set = set()` -- an empty set() call is not a literal; it is the empty set
            if isinstance(node.value, ast.Call) and not node.value.args and isinstance(node.value.func, ast.Name):
                return {"set": set(), "list": [], "dict": {}}[node.value.func.id]
            return ast.literal_eval(node.value)
    raise SystemExit(f"{name} not found")


def guards(model, texts, emb):
    known = set(load_assign("KNOWN_FAILING"))
    res = {}
    for name, query, expected in load_assign("critical_queries"):
        q = model.encode([query])[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        top3 = [int(j) for j in np.argsort(emb @ q)[-3:][::-1]]
        ok = any(any(kw.lower() in texts[j].lower() for kw in expected) for j in top3)
        dead = [kw for kw in expected if not any(kw.lower() in t.lower() for t in texts)]
        res[name] = dict(ok=ok, known_failing=name in known, dead_anchors=dead,
                         ambiguous=[kw for kw in expected if sum(kw.lower() in t.lower() for t in texts) > 1])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    a = ap.parse_args()
    from sentence_transformers import SentenceTransformer
    from chike import retrieval
    import coverage_profiles_2026_11_13 as cov

    pre = load_pre()
    texts, keys, _ = pre.build_fact_texts()
    # NEW rows = keys absent from the COMMITTED locked_facts.json. Rows in the batch dict that already existed are REWRITES (they keep
    # their position), and the committed-index-minus-new-rows equality below must hold with them in place.
    import subprocess
    committed = json.loads(subprocess.run(["git", "show", "e7df734:scripts/locked_facts.json"], capture_output=True, cwd=REPO, check=True).stdout.decode("utf-8"))
    new_keys = {k for k in getattr(pre, "_COVERAGE_2026_11_13", {}) if k not in committed}
    rewritten = {k for k in getattr(pre, "_COVERAGE_2026_11_13", {}) if k in committed}
    base_texts = json.load(open(os.path.join(REPO, "kaggle", "rag_facts_text.json"), encoding="utf-8"))
    model = SentenceTransformer(pre.EMBED_MODEL)
    cand_emb, base_emb = embed_all(model, texts), embed_all(model, base_texts)
    cp = write_index("cand_index", texts, cand_emb)
    bp = write_index("base_index", base_texts, base_emb)
    R_c, R_b = retrieval.Retriever(*cp), retrieval.Retriever(*bp)
    R_c.embed_model = R_b.embed_model = model
    # base keys: the committed index is the candidate minus new keys, in order (asserted)
    base_keys = [k for k in keys if k not in new_keys]
    rest = [(t, k) for t, k in zip(texts, keys) if k not in new_keys]
    assert len(rest) == len(base_texts), "row count mismatch"
    changed = [k for (t, k), bt in zip(rest, base_texts) if t != bt]
    assert set(changed) <= rewritten, f"rows changed that are not declared rewrites: {set(changed) - rewritten}"
    print("rewritten rows actually changed:", changed)
    key_of_c = dict(zip(texts, keys))
    key_of_b = dict(zip(base_texts, base_keys))

    qs = [q for _, _, q, _ in cov.all_cases()]
    qs += [q for q in W if q not in qs]

    def run(R, kmap, q, k=30):
        wide = R.retrieve(q, top_k=k)
        return [kmap.get(t, "?") for t in wide]

    rows, hijacks, fails = [], [], []
    gen_c = gen_b = 0
    for q in qs:
        kc, kb = run(R_c, key_of_c, q), run(R_b, key_of_b, q)
        want = W.get(q)
        rk = lambda ks: next((i + 1 for i, x in enumerate(ks) if x in want), ">30") if want else None
        row = dict(q=q, want=want, rank_before=rk(kb), rank_after=rk(kc), top3_after=kc[:3], top3_before=kb[:3])
        gen_c += "efd_not_every_business" in kc[:3]
        gen_b += "efd_not_every_business" in kb[:3]
        poll = [x for x in kc[:3] if x in new_keys and (not want or x not in want)]
        # a new row in the top 3 of a question that is NOT one of its own wanted answers = potential hijack (needs reading, not auto-fail)
        if poll:
            hijacks.append(dict(q=q, new_rows_in_top3=poll, want=want))
        if want and not (isinstance(row["rank_after"], int) and row["rank_after"] <= 3):
            fails.append(q)
        rows.append(row)
    g_c = guards(model, texts, cand_emb)
    g_b = guards(model, base_texts, base_emb)
    reg = [n for n, r in g_c.items() if not r["ok"] and not r["known_failing"] and g_b.get(n, {}).get("ok")]
    dead = {n: r["dead_anchors"] for n, r in g_c.items() if r["dead_anchors"]}
    newly_ambiguous = [n for n, r in g_c.items() if r["ambiguous"] and not g_b.get(n, {}).get("ambiguous")]
    top1 = [dict(q=r["q"], before=r["top3_before"][0], after=r["top3_after"][0], new_row_now_first=r["top3_after"][0] in new_keys)
            for r in rows if r["top3_before"] and r["top3_after"] and r["top3_before"][0] != r["top3_after"][0]]
    # the regen's two remaining gates, replayed against the prospective index: self-retrieval (<10% may fail) and the rank-regression gate
    def self_failures(texts_, emb_):
        bad = 0
        for i, t in enumerate(texts_):
            q = model.encode([f"query: {t[:100]}"])[0]
            q = q / (np.linalg.norm(q) + 1e-10)
            bad += int(np.argmax(emb_ @ q)) != i
        return bad
    sf_c, sf_b = self_failures(texts, cand_emb), self_failures(base_texts, base_emb)

    def rank_gate(texts_, emb_):
        res = []
        for name, q, needle, pre_rank, measured in load_assign("RANK_GATE_CASES"):
            hits = [i for i, t in enumerate(texts_) if needle in t]
            qv = model.encode([q])[0]
            qv = qv / (np.linalg.norm(qv) + 1e-10)
            order = np.argsort(-(emb_ @ qv))
            obs = int(np.where(order == hits[0])[0][0]) + 1 if len(hits) == 1 else None
            res.append(dict(name=name, anchors=len(hits), observed=obs, measured=measured, pre=pre_rank,
                            ok=bool(obs is not None and obs <= measured + 5 and obs < pre_rank)))
        return res
    rg_c, rg_b = rank_gate(texts, cand_emb), rank_gate(base_texts, base_emb)
    out = dict(label=a.label, self_retrieval_failures=dict(before=sf_b, after=sf_c, rows_after=len(texts)),
               rank_gate=dict(before=rg_b, after=rg_c), top1_changes=top1, rows_before=len(base_texts), rows_after=len(texts), n_questions=len(qs),
               targets=dict(total=sum(1 for r in rows if r["want"]), pass_after=sum(1 for r in rows if r["want"] and isinstance(r["rank_after"], int) and r["rank_after"] <= 3),
                            pass_before=sum(1 for r in rows if r["want"] and isinstance(r["rank_before"], int) and r["rank_before"] <= 3), failing_after=fails),
               generic_row_in_top3=dict(before=gen_b, after=gen_c), hijacks=hijacks,
               guards=dict(total=len(g_c), regressed=reg, dead_anchors=dead, newly_ambiguous=newly_ambiguous,
                           failing_unexpected=[n for n, r in g_c.items() if not r["ok"] and not r["known_failing"]]),
               rows=rows)
    json.dump(out, open(os.path.join(REPO, "eval", "results", f"coverage_batch_{a.label}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    t = out["targets"]
    print(f"rows {out['rows_before']} -> {out['rows_after']}; questions {len(qs)}")
    print(f"TARGETS pass top-3: before {t['pass_before']}/{t['total']}  after {t['pass_after']}/{t['total']}")
    for q in fails:
        r = next(x for x in rows if x["q"] == q)
        print(f"   FAIL rank_before={r['rank_before']} after={r['rank_after']}  {q[:70]}  top3={r['top3_after']}")
    print(f"GENERIC row 58 in top 3: before {gen_b}  after {gen_c}  (of {len(qs)})")
    print(f"HIJACK candidates (new row in top 3 of a question that does not want it): {len(hijacks)}")
    for h in hijacks[:25]:
        print("   ", h["new_rows_in_top3"], "<-", h["q"][:70])
    print(f"TOP-1 CHANGES: {len(top1)} of {len(qs)}  (by a NEW row: {sum(t['new_row_now_first'] for t in top1)}; by reordering of old rows: {sum(not t['new_row_now_first'] for t in top1)})")
    for t in top1:
        if not t["new_row_now_first"] or t["before"] != "?":
            print("   ", t["before"], "->", t["after"], "<-", t["q"][:60])
    print(f"SELF-RETRIEVAL failures: before {sf_b}/{len(base_texts)}  after {sf_c}/{len(texts)} (regen blocks at >=10%)")
    print("RANK GATE:", [(r["name"][:10], r["observed"], "ok" if r["ok"] else "FAIL") for r in rg_c], "| before:", [(r["observed"]) for r in rg_b])
    print(f"GUARDS: {len(g_c)}; regressed={reg}; unexpected-failing={out['guards']['failing_unexpected']}; dead anchors={dead}; newly ambiguous={newly_ambiguous}")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""ONE-BY-ONE REVIEW OF THE 28 GOLD-CLASS ROWS PLUS eval_013 AND eval_218, AGAINST PRIMARY SOURCES (2026-11-16, founder's decision 2b). PROPOSALS ONLY: no key in eval/accuracy_gate/ is edited here, and none may be without
the founder's approval of the list below (R12b, WRONG_GOLD). Also reads the 10 training pairs behind the voluntary-VAT claim (2c) and lists them; NOTHING is quarantined here.

PRIMARY SOURCES RE-READ FOR THE PROPOSALS (editions asserted FIRST through scripts/check_source_editions.assert_edition, R-edition):
  ITA Cap.332 R.E.2023  data/source_documents/tra/income_tax_act_cap332_re2023.pdf   First Schedule para 4(b)(ii): "in the case of interest, rent or a commuted pension paid to a resident withholdee or interest or rent paid to a
                        non-resident withholdee -- ten percent"
  VAT Act Cap.148 R.E.2023  .../vat_act_cap148_re2023.pdf   0 occurrences of "voluntar*"; registration routes: s.28 threshold, s.29(1) professional services, s.29(2) Government entity, s.29(3) intending trader
                        ("the Commissioner General MAY register" on evidence: contracts, tenders, building plans, business plans, bank financing; and a stated period for commencing taxable production)
  TRA FAQ (tra_faq_57_2026_11_16.html): "voluntary registration is also allowed for certain specific economic activities" -- names none (UNRECONCILED with the Act; recorded, not resolved)
Every other row is KEY_OK because its key asserts no regulatory figure beyond rates already locked and read (NSSF/SDL/WCF/PAYE bases, GN 487A), or asks for the missing input; the miss there is the scorer, not the key.

    python eval/controls/review_gold_rows_2026_11_16.py
"""
import importlib.util
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CLAR = "KEY_OK -- the key asks for the missing input; the miss is the harness rule `clarified => FAIL` (policy 2a promotes it when the reply asks for the same piece)"
ROWS = {
    "eval_013": ("KEY_CHANGE_PROPOSED", "the key asserts 'Ndiyo. Usajilishaji wa hiari wa VAT unaruhusiwa' citing a KPMG URL that 404s and was never read. Primary text names no voluntary route for an existing below-threshold trader (VAT Act R.E.2023, 0 hits); the TRA FAQ allows it for unnamed activities. A yes/no key cannot be Ndiyo or Hapana; re-key as the hedged statement (proposed_keys). ALSO: the gate-run reply 'Ndiyo, sheria inamruhusu ... hata kabla ya kufikia kizingiti' PASSED on this stale key and was credited by the judge -- an unflagged confident wrong inside the 319 (the yes_no scorer defaults to affirmative, so the stale key passes any non-negative reply)"),
    "eval_028": ("KEY_CHANGE_PROPOSED", "the 4-step procedure (BRELA certificate, TIN, TRA reviews, VAT number) is the same unread KPMG claim. The only documented route is s.29(3): evidence of intention to commence, taxable supplies, a stated commencement period, at the Commissioner General's discretion"),
    "eval_218": ("KEY_CHANGE_PROPOSED", "the key says the non-resident rent rate is 'not confirmed'. ITA First Schedule para 4(b)(ii), read 2026-11-16: ten percent for rent paid to a non-resident withholdee. The reply (10%, one rate for both) is right. Scores True under the old AND new key by regex (number scorer), so the change moves no number and removes a wrong claim"),
    "eval_228": ("KEY_NEEDS_DECISION", "the key hedges ('10,000 is often cited, not confirmed') while stamp duty is on the OOC list (CLAUDE.md R11), so production refuses by design. Not a primary-source question (the Stamp Duty Act is not whitelisted). Options: (a) re-key as an expected out-of-scope redirect and move the row to the refusal population, (b) keep the hedge key and accept a design conflict, (c) retire the row. A person must choose"),
    "eval_029": ("RECLASSIFY", "reply says 'Utapata marejesho ya VAT' (a definite refund) and omits carry-forward, which the key and the VAT Act both give. NOT acceptable: move from GOLD to MODEL (partial). Key unchanged"),
    "eval_051": ("KEY_OK", "key: no minimum transaction value for an EFD receipt (TAA Cap.438 R.E.2023 s.44 default for everyone; locked fact efd_threshold_tzs_11m correction). Reply 'TZS 0' is acceptable; regex answer_type=number expects the words"),
    "eval_069": ("KEY_OK", "reply lists actions that index row 95 states (inspection, penalty, suspending the device, closing premises); judge correct"),
    "eval_094": ("KEY_OK", "NSSF not TRA (NSSF Act Cap.50 R.E.2023: contributions, interest, offences; edition asserted in the manifest); reply right"),
    "eval_144": ("KEY_OK", "'La' -- marriage to a Tanzanian does not change non-citizen status under GN 487A (locked facts gn487a_*, read from the gazette 2026-07-01); reply right, the scorer wants the 'La' opener"),
    "eval_260": ("KEY_OK", "savings are not an NSSF base; reply right"),
    "eval_277": ("KEY_OK", "defensible both ways: the key gives the conditional computation (3.5% x 900,000 = 31,500 when 10+ staff), the reply asks the headcount (SDL applies only from 10 employees). Stays a miss under policy 2a because the key computes"),
    "eval_294": ("KEY_OK", "defensible: the key computes 80,000 x 15 and asks the headcount; the reply asks both. Stays a miss under policy 2a because the key computes"),
    "eval_317": ("KEY_OK", "GN 487A lists saloon business among the 15 prohibited activities (locked fact); reply conveys it without the 'Hapana' opener the scorer wants"),
    "eval_347": ("KEY_OK", "key: EFD has no turnover threshold, exemption only by Commissioner General notice (TAA Cap.438 s.44). The reply states exactly that via D-FIDELITY-7 replacement copy; scored FAIL because clarified and the gold is not a clarification. A scorer decision (score replacement copy by its content), not a key change"),
    "eval_364": ("KEY_OK", "WCF from the first employee (wcf.go.tz, confirmed Jun 2026; registration within 30 days of the first hire); reply right; row already marked unreliable (yes_no_ground_truth_ambiguous)"),
    "eval_365": ("KEY_OK", "NSSF has no headcount threshold (Cap.50 R.E.2023 / locked fact); reply right"),
}
for _i in ("eval_267", "eval_270", "eval_271", "eval_272", "eval_273", "eval_275", "eval_276", "eval_291", "eval_292", "eval_295", "eval_297", "eval_298", "eval_299", "eval_300"):
    ROWS[_i] = ("KEY_OK", CLAR)

PROPOSED_KEYS = {
    "eval_013": {"answer_type": "definition",
                 "correct_answer_sw": "Sheria ya VAT haitaji usajili wa hiari kwa mfanyabiashara aliyepo aliye chini ya kizingiti. Njia ilizotaja ni: kufikia kiwango, watoa huduma za kitaalamu, taasisi za Serikali, na anayetarajia kuanza biashara (kwa uamuzi wa Kamishna Mkuu). TRA inasema usajili wa hiari unaruhusiwa kwa shughuli maalum za kiuchumi bila kuzitaja. Thibitisha na TRA (tra.go.tz) kabla ya kuomba.",
                 "source": "VAT Act Cap.148 R.E.2023 (0 occurrences of 'voluntar*'; ss.28, 29(1)-(3)); TRA FAQ tra_faq_57_2026_11_16.html; locked fact vat_voluntary_registration"},
    "eval_028": {"answer_type": "definition",
                 "correct_answer_sw": "Hakuna utaratibu wa usajili wa hiari ulioandikwa kwa mfanyabiashara aliyepo aliye chini ya kizingiti. Njia pekee iliyoandikwa ni mfanyabiashara anayetarajia kuanza shughuli: anawasilisha ushahidi (mikataba, zabuni, ramani za jengo, mpango wa biashara, ufadhili wa benki) na kutaja muda ambao uzalishaji wa bidhaa zinazotozwa VAT utaanza; Kamishna Mkuu ndiye anayeamua. Wasiliana na TRA kuthibitisha.",
                 "source": "VAT Act Cap.148 R.E.2023 s.29(3), read 2026-11-16 (edition asserted); TRA FAQ"},
    "eval_218": {"answer_type": "number",
                 "correct_answer_sw": "Asilimia 10 — kiwango kimoja kwa wakazi na wasio wakazi kwenye pango la kibiashara. Mlipaji lazima awe wakala wa kuzuia kodi. Thibitisha na TRA (tra.go.tz).",
                 "source": "ITA Cap.332 R.E.2023 First Schedule para 4(b)(ii), read 2026-11-16 (edition asserted); TRA withholding page 'Rental income (commercial) 10% | 10%'; locked fact rent_wht_rate"},
}


def main():
    spec = importlib.util.spec_from_file_location("cse", os.path.join(REPO, "scripts", "check_source_editions.py"))
    cse = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cse)
    cse.assert_edition(os.path.join(REPO, "data/source_documents/tra/income_tax_act_cap332_re2023.pdf"), "R.E. 2023")
    cse.assert_edition(os.path.join(REPO, "data/source_documents/tra/vat_act_cap148_re2023.pdf"), "R.E. 2023")
    adj = json.load(io.open(os.path.join(REPO, "eval/results/gate_c2143c0_adjudication_2026_11_16.json"), encoding="utf-8"))
    gold28 = sorted(i for i, v in adj["per_row_class"].items() if v["class"] == "GOLD")
    assert len(gold28) == 28, len(gold28)
    missing = [i for i in gold28 + ["eval_013", "eval_218"] if i not in ROWS]
    assert not missing, missing
    cnt = {}
    for v in ROWS.values():
        cnt[v[0]] = cnt.get(v[0], 0) + 1
    out = {"n_rows": len(ROWS), "verdicts": {k: {"verdict": v[0], "why": v[1]} for k, v in sorted(ROWS.items())}, "tally": cnt, "proposed_keys_NOT_APPLIED": PROPOSED_KEYS}
    pp = json.load(io.open(os.path.join(REPO, "eval/results/price_followup_guards_2026_11_16.json"), encoding="utf-8"))["populations"]["TRAINING"]["rows"]
    vol = [r for r in pp if any("voluntary" in x.lower() for x in r["reasons"])]
    assert len(vol) == 10
    groups = {"QUARANTINE (unconditional 'Ndiyo ... hata kama mauzo yako hayajafika kizingiti')": [0, 1, 2, 4, 5, 6, 7, 9],
              "BORDERLINE (says 'Ndiyo' but routes the application to the Commissioner; recommended: leave, founder's call)": [3, 8]}
    out["voluntary_vat_training_pairs_NOT_QUARANTINED"] = {k: [{"src": vol[i]["src"], "q": vol[i]["q"], "head": vol[i]["reply"][:140]} for i in idx] for k, idx in groups.items()}
    io.open(os.path.join(REPO, "eval", "results", "gold_key_review_2026_11_16.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print("verdicts:", len(ROWS), cnt)
    for k, v in out["voluntary_vat_training_pairs_NOT_QUARANTINED"].items():
        print(len(v), k)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""PROPOSAL ONLY (R36/R37): per-row repair-or-quarantine list for the rows that teach a Kenyan "P9" (D-FIDELITY-30) or NSSF due by the 7th (D-FIDELITY-29). NOTHING in datasets/ or eval/ is edited by this script.
Input: eval/results/p9_and_nssf7_rows_2026_11_24.json (every authored-corpus and export row the two guards flag, deduplicated by (question, answer), with every stage it lives in).
Output: eval/results/p9_nssf7_repair_proposal_2026_11_24.json. Each row carries the R37 opposite-direction check (does it REJECT the claim?) and, for a repair, the exact replacement text, built from locked facts paye_p9_deadline / p45_not_tanzanian / nssf_payment_deadline.
    python eval/controls/write_p9_nssf7_proposal_2026_11_24.py"""
import io, json, os
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
rows = json.load(io.open(os.path.join(REPO, "eval", "results", "p9_and_nssf7_rows_2026_11_24.json"), encoding="utf-8"))
assert len(rows) == 11, len(rows)
CERT = "cheti cha zuio cha mwaka (withholding certificate)"

P = {
 1: ("REPAIR", "one clause", "Mwajiri lazima aweke: orodha ya wafanyakazi na TIN zao, hesabu za mishahara, hesabu za PAYE kwa kila mfanyakazi, stakabadhi za malipo ya TRA, na nakala za " + CERT + " alizotoa kwa wafanyakazi. Rekodi hizi zinahifadhiwa kwa miaka 5. Thibitisha na TRA.",
     "R37: does not reject P9 (it asserts it). Only 'fomu za PAYE P9' changes; the 5-year record rule is the locked record_keeping_period."),
 2: ("QUARANTINE", "invented audit procedure", None,
     "R37: no sentence rejects P9. The whole answer is an invented TRA audit list ('wanakagua: ... dalili kuu ya udanganyifu'): the same defect the SDL-audit hedge exists for; no source holds how TRA audits PAYE. Repairing P9 alone would leave an unsourced procedure trained as fact."),
 3: ("REPAIR", "rewrite, keeps the correct 'Hapana'", "Hapana. Fomu ya P45 ni fomu ya Uingereza (UK) na HAIPO Tanzania. Kinacholingana nayo Tanzania ni " + CERT + " (Sheria ya Kodi ya Mapato), kinachotolewa na mwajiri kwa mfanyakazi; hakuna fomu inayoitwa 'P9' Tanzania (hilo ni neno la Kenya) wala fomu maalum ya 'Hati ya Kuondoka' iliyothibitishwa. Thibitisha na TRA.",
     "R37: the opening 'Hapana, P45 is UK' is CORRECT and is kept. The wrong parts are 'fomu ya P9' and 'Hati ya Kuondoka (Leaving Certificate)': p45_not_tanzanian's correction_note removed the 'leaving certificate' language as unverified, so both are fixed."),
 4: ("REPAIR", "rewrite, keeps the correct 'Hapana'", "Hapana. 'P9' si neno la Tanzania (ni neno la Kenya, KRA) na TRA haina fomu yenye jina hilo. Hati ya mwaka ya mfanyakazi ni " + CERT + ", ambacho mwajiri anakitoa kwa mfanyakazi (si kupitia SMS). Thibitisha njia sahihi na TRA (tra.go.tz).",
     "R37: its 'Hapana' (SMS is not acceptable) is right in direction but it teaches P9 as a form submitted to TRA. The adversarial premise has coverage value, so it is rewritten, not removed."),
 5: ("REPAIR", "one clause", "Wakati mfanyakazi mgeni anaondoka Tanzania kabla ya mwaka wa kodi kumalizika: (1) Hesabu PAYE ya mwaka nzima kulingana na muda wa kufanya kazi Tanzania; (2) Fanya marekebisho ya mwisho ya PAYE kwa mwezi wa mwisho; (3) Mpe " + CERT + " kinachoonyesha kipindi alichofanya kazi; (4) Futa usajili wa mfanyakazi kwenye mfumo wa PAYE TRA. Thibitisha hatua za mwisho na TRA.",
     "R37: asserts P9. Only item (3) changes. NOTE for the reviewer: items (1), (2) and (4) are unsourced procedure and are NOT changed by this proposal."),
 6: ("REPAIR", "one clause", "Ndiyo — mfanyakazi mwenye TIN, PAYE inayokatwa kwa usahihi, na NSSF inayochangiwa — ana hali nzuri ya kodi Tanzania. Hii ni muundo sahihi wa kufuata. Mwajiri pia anahitaji SDL (kama wafanyakazi ≥10) na WCF (0.5%) zilizolipwa. Hifadhi kumbukumbu zote za vyeti vya zuio na malipo kwa ajili ya ukaguzi wowote wa TRA.",
     "R37: asserts P9 in the last sentence only; the rest (TIN, PAYE, NSSF, SDL >=10, WCF 0.5%) is consistent with locked facts."),
 7: ("REPAIR", "one clause", "PAYE ya mshahara wa mwisho (terminal benefits — mshahara wa mwisho, posho ya kuachana, likizo iliyobaki inayolipwa) inapaswa kukokotolewa, kukatwa, na kuwasilishwa TRA ifikapo tarehe 7 ya mwezi unaofuata baada ya malipo ya mwisho. Mpe mfanyakazi " + CERT + " baada ya malipo ya mwisho.",
     "R37: asserts P9 in the last sentence only; the 7th is the locked paye_remittance_deadline."),
 8: ("REPAIR", "rewrite (the premise is the error)", "Hapana, si tarehe moja. SDL inalipwa kufikia tarehe 7 ya mwezi unaofuata (kwa TRA), na NSSF inalipwa ndani ya mwezi mmoja baada ya mwisho wa mwezi wa mishahara (kwa NSSF). Ni taasisi TOFAUTI, kwa hiyo lipa kila moja kwa taasisi yake — kulipa SDL kwa NSSF au kinyume chake kutasababisha matatizo ya upatanisho. Thibitisha na TRA na NSSF.",
     "R37: it ACCEPTS the premise 'zote zinalipwa tarehe 7' (the NSSF-7th error, D-FIDELITY-29's founding class). The 'different institutions' half is right and is kept. The new text follows locked sdl_payment_deadline and nssf_payment_deadline. The invented 'akaunti ya TRA / akaunti ya NSSF' detail is reduced to 'taasisi tofauti'."),
 9: ("QUARANTINE", "accepts a corrected-wrong premise", None,
     "R37: it answers 'Ndio, kuna adhabu' to a premise that carries BOTH errors paye_p9_deadline corrected ('PAYE P9' and 'Machi 31': the certificate is due 30 January, monthly PAYE the 7th). It does not reject either, so it is not an over-removal. Rewriting would need a new answer to a malformed question; removal loses nothing."),
 10: ("QUARANTINE", "unsourced annual-reconciliation claim", None,
      "R37: no sentence rejects P9. Beyond P9 the answer teaches that PAYE is 'husuluhishwa mara moja kwa mwaka' (an annual reconciliation) as a general rule: unsourced, and the locked individual_income_tax_return fact says an employee whose only income is PAYE-withheld employment income need not file. Repairing P9 alone would keep that."),
 11: ("REPAIR", "rewrite (defines P9 as a Tanzanian form)", "'P9' si neno la Tanzania: ni neno la Kenya (KRA), na TRA haina fomu yenye jina hilo. Tanzania ina " + CERT + ": hati inayoonyesha jumla ya kodi ya mapato ya ajira iliyokatwa kutoka kwenye mshahara wa mfanyakazi kwa mwaka, ambayo mwajiri anapaswa kuitoa kufikia tarehe 30 Januari ya mwaka unaofuata (Sheria ya Kodi ya Mapato). Thibitisha na TRA (tra.go.tz).",
      "R37: defines P9 as a Tanzanian form. The question ('what does PAYE P9 mean for my small business') is legitimate, so it is rewritten from locked paye_p9_deadline (30 January), not removed."),
}
out = {"proposal_only": True, "edited": "NOTHING (datasets/ and eval/ untouched)", "rows": [], "gold": {}, "reach": "R36: the authored batch files AND datasets/tier1a/sft/train_sft.jsonl (the export) must both be changed; the export is regenerated by generate_sft.py after the authored files are fixed, then re-audited with eval/controls/audit_quarantine_reach.py"}
for r in rows:
    act, kind, new, why = P[r["n"]]
    out["rows"].append({"n": r["n"], "question": r["q"], "old_answer": r["a"], "action": act, "kind": kind, "new_answer": new, "reason_and_R37_check": why, "present_in": sorted({l[1] + ":" + str(l[2]) for l in r["locs"]})})
out["gold"] = {"id": "eval_203", "file": "eval/accuracy_gate/eval_questions_002_additions.jsonl",
               "old_key": "Hapana. Fomu ya P45 haipo katika mfumo wa kodi wa Tanzania — ni fomu ya Uingereza. Badala yake tumia fomu ya P9 au cheti cha kuondoka kazini. Thibitisha na TRA.",
               "defect": "WRONG_GOLD (R12b outcome 4): the key recommends 'P9' (Kenyan) and a 'cheti cha kuondoka kazini' that p45_not_tanzanian's correction_note removed as unverified. A model that answers correctly is marked wrong.",
               "proposed_correction": "SIDECAR (the frozen file is not edited; the sidecar pins its sha256, as for np_13 / s2_07): 'Hapana. Fomu ya P45 ni ya Uingereza. Kinacholingana nayo Tanzania ni " + CERT + " (Sheria ya Kodi ya Mapato); 'P9' ni neno la Kenya. Thibitisha na TRA.'"}
counts = {a: sum(1 for x in out["rows"] if x["action"] == a) for a in ("REPAIR", "QUARANTINE")}
out["counts"] = counts
io.open(os.path.join(REPO, "eval", "results", "p9_nssf7_repair_proposal_2026_11_24.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1))
print(counts, "(distinct pairs)", sum(len(x["present_in"]) for x in out["rows"]), "locations")

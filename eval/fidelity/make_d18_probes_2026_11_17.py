# -*- coding: utf-8 -*-
"""Builds eval/fidelity/d18_batch_probes_2026_11_17.jsonl -- the founder's NEXT SMALL BATCH (five items). Founding specimens are VERBATIM from the frozen sets and the live artifacts; the clean half is every neighbour the new
code must NOT touch (R17/R33).    python eval/fidelity/make_d18_probes_2026_11_17.py"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = []


def add(i, g, q, e, why, body="", **kw):
    P.append(dict(id=i, guard=g, question=q, body=body, expect=e, guards_against=why, **kw))


# ---- 2. VAT: an amount with its OWN period beside a bound (expect "amount|period" or "none") ----------------------------------------------------------------------------------------------------
NP22 = "Mimi nina biashara ya kuuza vifaa, mauzo yangu ya mwaka bado hayajafika milioni 200 lakini ndani ya miezi 6 nimeuza milioni 110. Sihitaji kujisajili VAT kwa sababu mwaka bado haujaisha, siyo?"
add("d18_vat_01", "vat", NP22, "110000000|six_month", "np_22 VERBATIM: the 110M with its own six-month period beside the 200M bound")
add("d18_vat_02", "vat", "Ndani ya miezi 6 nimeuza milioni 110, ingawa mauzo yangu ya mwaka bado hayajafika milioni 200. Je nijisajili VAT?", "110000000|six_month", "the same facts, figure first")
add("d18_vat_03", "vat", "Mauzo yangu kwa mwaka bado hayajafika milioni 200, lakini katika miezi 12 nimeuza milioni 150. Je VAT?", "150000000|annual", "an annual figure beside the bound")
add("d18_vat_04", "vat", "Mauzo yangu bado hayajafika milioni 200 lakini nimeuza milioni 110. Je VAT?", "none", "the 110M has NO period of its own: not resolved, the engine still asks")
add("d18_vat_05", "vat", "Nimeuza milioni 90 na milioni 120 mwaka huu, VAT?", "none", "two competing turnover figures, no bound: not resolved")
add("d18_vat_06", "vat", "Mauzo ya miezi 6 ni milioni 110, kizingiti ni milioni 100, je VAT?", "none", "a threshold NAMED with no bound cue is not recognised as a bound: two figures, not resolved")
add("d18_vat_07", "vat", "Mauzo yangu bado hayajafika milioni 200 kwa mwaka. Naweza kusajili VAT kwa hiari?", "none", "a single amount (the bound alone): the existing upper-bound path, untouched")
add("d18_vat_09", "vat", "Kama biashara yangu inauza kwa wastani wa milioni 18 kila mwezi, hiyo hela ipo chini ya milioni 200 kwa mwaka?", "none", "PRICED FALSE POSITIVE (a training question): 18M is a MONTHLY rate beside a bound; resolving it as annual would call a 216M-a-year business exempt")
add("d18_vat_10", "vat", "Mauzo yangu ya mwaka ni TZS 150 milioni, hayajafika TZS 200 milioni.", "150000000|annual", "a corpus question the resolver now answers correctly: 150M annual beside the 200M bound")
add("d18_vat_11", "vat", "Nauza milioni 20 kwa mwezi, na mauzo yangu hayajafika milioni 200. Je VAT?", "none", "a monthly rate beside a bound")
add("d18_vat_12", "vat", "Mauzo yangu hayajafika milioni 200, ila ndani ya miezi 6 au mwaka mmoja nimeuza milioni 110.", "none", "two DIFFERENT period cues about equally near the figure: ambiguous, the engine asks")
add("d18_vat_13", "vat", "Mauzo yangu hayajafika milioni 200, ila nimeuza milioni 110 ndani ya miezi 6 na ndani ya mwaka mmoja.", "110000000|six_month", "the nearer cue (six months) wins when the other period is MORE than 30 characters away; six months is the limb the 110M crosses")
add("d18_vat_08", "vat", "Mauzo yangu ya mwaka ni milioni 250, je nijisajili VAT?", "none", "a single amount: untouched")

# ---- 3. A FIRM NAMED AS THE AUTHORITY TO CONFIRM WITH (expect repair | clean) ---------------------------------------------------------------------------------------------------------------
GQ = "Nani alisaini GN 605A?"
add("d18_fm_01", "firm", GQ, "repair", "LIVE (36a5144 / 911948b), VERBATIM: 'Thibitisha na VELMA Law au PKF Eastern Africa.'",
    body="GN 605A iliyoanza 1 Januari 2026 ilisainiwa na Waziri wa Kazi. Hakuna taarifa kuwa PKF au kampuni nyingine ilisaini amri hii. Thibitisha na VELMA Law au PKF Eastern Africa.", contains="Thibitisha na Ofisi ya Kazi (kazi.go.tz)", absent="VELMA")
add("d18_fm_02", "firm", GQ, "repair", "the firm goes, a whitelisted source stays", body="Imesainiwa. Thibitisha na PKF Eastern Africa au TanzLII.", contains="Thibitisha na TanzLII", absent="PKF")
add("d18_fm_03", "firm", "Kodi ya VAT ni ngapi?", "repair", "a firm with its domain written out", body="Ni 18%. Thibitisha na Bowmans (bowmanslaw.com).", contains="Thibitisha na TRA (tra.go.tz)", absent="bowmans")
add("d18_fm_04", "firm", "Habari gani?", "repair", "no single topic: 'mamlaka husika', never a guessed authority", body="Sawa. Thibitisha na KPMG, EY na Deloitte.", contains="Thibitisha na mamlaka husika", absent="KPMG")
add("d18_fm_05", "firm", GQ, "repair", "two firms with their own hosts", body="Sawa. Thibitisha na VELMA Law (velmalaw.co.tz) au PKF Eastern Africa (pkfea.com).", contains="Ofisi ya Kazi", absent="velmalaw")
add("d18_fm_06", "firm", GQ, "clean", "MUST PASS: an ANALYSIS cited as an analysis, with the real authority as the tail", body="Kulingana na uchambuzi wa PKF Eastern Africa, wastani ni 33.4%. Thibitisha na TRA (tra.go.tz).")
add("d18_fm_07", "firm", "GN 605A ni nini?", "clean", "MUST PASS: a real authority", body="Ni amri. Thibitisha na Ofisi ya Kazi (kazi.go.tz).")
add("d18_fm_08", "firm", GQ, "clean", "MUST PASS: a firm named in a sentence that is not a 'Thibitisha na' tail", body="Hakuna taarifa kuwa PKF ilisaini amri hii. Thibitisha na Ofisi ya Kazi (kazi.go.tz).")
add("d18_fm_09", "firm", GQ, "clean", "MUST PASS: a whitelisted legal database alone", body="Imesainiwa. Thibitisha na TanzLII.org.")

# ---- 4. THE REPEATED CONFIRM SENTENCE (expect dedupe | clean) -------------------------------------------------------------------------------------------------------------------------------
LQ = "Leseni yangu ya biashara nikiipoteza nifanyeje?"
add("d18_dd_01", "dedupe", LQ, "dedupe", "LIVE (911948b), VERBATIM after the dead-host removal: the same 'Thibitisha na halmashauri husika' twice",
    body="Kupoteza leseni ni tatizo. Thibitisha na halmashauri husika ili kujua utaratibu sahihi wa kuitafuta upya. Thibitisha na halmashauri husika.", count=1)
add("d18_dd_02", "dedupe", LQ, "clean", "MUST PASS: two DIFFERENT confirm sentences", body="Thibitisha na halmashauri yako. Thibitisha na BRELA kwa leseni za kundi A.")
add("d18_dd_03", "dedupe", LQ, "clean", "MUST PASS: a single confirm sentence", body="Kupoteza leseni ni tatizo. Thibitisha na halmashauri husika.")
add("d18_dd_04", "licdead", LQ, "repair", "the whole repaired lost-licence reply has the host removed AND no repeated sentence", body="Kupoteza leseni ni tatizo. Thibitisha na halmashauri husika ili kujua utaratibu sahihi wa kuitafuta upya. Thibitisha na halmashauri husika (lga.go.tz).", count=1)

# ---- 1 & 5. THE TWO NEW STATEMENT ROUTES: diverting AND clean (expect topic | none) ---------------------------------------------------------------------------------------------------------
TIN, FV = "tin_apply_deadline", "business_licence_fee_and_validity"
for i, (q, why) in enumerate([
    ("Sina haja ya kuwa na TIN kwa sababu biashara yangu ni ndogo na ndiyo kwanza naanza, sivyo?", "np_14 VERBATIM"),
    ("Nimefungua saluni yangu mwezi huu. Kuna mtu kaniambia nina siku 15 za kuomba TIN kuanzia siku nilipoanza biashara, sivyo?", "np_26 VERBATIM"),
    ("Nimeanza biashara ya kuuza vifaa vya ujenzi wiki iliyopita. Nimesikia nina siku 15 za kuomba TIN, kwa hiyo sihitaji kuwa nayo siku ya kwanza kabisa, ni kweli?", "s2_08 VERBATIM"),
    ("Naomba TIN lini baada ya kuanza biashara?", "a participant phrasing"),
], 1):
    add(f"d18_rt_{i:02d}", "route", q, TIN, why)
for i, (q, why) in enumerate([
    ("Nahitaji leseni ya biashara, inagharimu kiasi gani na inaisha lini?", "LIVE two-part specimen: the fee limb alone was answered"),
    ("Leseni ya biashara ya LGA inagharimu kiasi gani na inahuishwa lini?", "the sweep's two-part question"),
    ("How much does an LGA business licence cost and when is it renewed?", "the sweep's English two-part question"),
    ("Ada ya leseni ya duka langu ni ngapi na huisha lini?", "a participant phrasing"),
], 1):
    add(f"d18_rf_{i:02d}", "route", q, FV, why)
for i, (q, why) in enumerate([
    ("Nitapataje TIN?", "a HOW question: the model answers it from the fact; the statement is for the WINDOW / premise questions"),
    ("Napataje TIN?", "a HOW question"), ("Sina TIN bado, naipataje?", "a HOW question (swept)"), ("Utaratibu wa kuomba namba ya mlipakodi (TIN) ni upi?", "a PROCEDURE question (swept)"),
    ("Nifanyeje kupata TIN ya biashara yangu mpya?", "a HOW question (swept)"), ("nawezaje kujisajili kwa tra kupata tin namba", "a HOW question (swept)"),
    ("Sina namba ya TIN bado. Nachukuaje, na ninahitaji vitu gani?", "HOW + documents (swept)"), ("TIN ya TRA inagharimu kiasi gani na inachukua muda gani kupata?", "a FEE + time question (swept)"),
    ("Je, ninahitaji TIN kufungua akaunti ya benki ya biashara?", "a BANK ACCOUNT question (swept)"), ("Mwajiri asiye na TIN hawezi kuomba kibali cha kazi kwa mfanyakazi wake wa kigeni -- je, ni kweli?", "a WORK PERMIT question (swept)"),
    ("Mauzo yangu ni milioni 250 kwa mwaka. Nijiandikishe TRA kupata TIN?", "a VAT-registration question that mentions a TIN (swept)"),
    ("Nimeanzisha biashara mwezi uliopita, nimepata TIN mpya. Nimesikia kuna msamaha kwa mwaka wa kwanza -- ni wa kweli?", "an EXEMPTION question (swept)"),
    ("Mfanyabiashara anayeuza kwa VICOBA au vikundi vya akiba tu anahitaji TIN Tanzania?", "WHO needs a TIN (swept)"), ("Je, biashara ya mkulima mdogo wa Tanzania inahitaji TIN na kodi?", "WHO needs a TIN (swept)"),
    ("Kodi za Zanzibar ziko sawa na Tanzania Bara -- ninaweza kutumia TIN moja kwa biashara zangu zote?", "one TIN for all businesses (swept)"),
    ("Muda wa kuomba TIN umepangwa kwa siku 15 tu ila sijui ninaweza kufanya vipi?", "a HOW question that names the 15 days (swept)"),
    ("Je, kuna mwisho mwingine wa muda wa kulipa kodi zaidi ya siku 15 za kuomba TIN?", "a PAYMENT-deadline question (swept)"),
    ("Can a business with only a TIN but no LGA licence operate legally in Tanzania?", "English, a licence question (swept)"),
    ("TIN ni nini?", "a definition"), ("Nataka kuhakiki namba ya TIN ya mteja wangu", "a verification"), ("TIN ya kampuni inapatikanaje?", "a company"), ("Nimechelewa kuomba TIN, adhabu ni nini?", "a PENALTY"),
    ("Nimepoteza cheti cha TIN, nifanyeje?", "a lost certificate"), ("TIN na VAT vinahusianaje?", "another tax"), ("Je, mgeni anaweza kupata TIN?", "a foreigner"),
    ("Ada ya leseni ya biashara ni kiasi gani?", "a fee-only question stays on the MODEL path"),
    ("Leseni ya biashara inaisha lini?", "a renewal-only question goes to the validity statement, not the combined one"),
    ("leseni yangu ya biashara inahuishwa lini? Na zimamoto wananidai cheti cha usalama, ni lazima?", "THREE parts: a fire-safety certificate"),
    ("Ada ya leseni ya biashara na TIN ni kiasi gani na lini?", "a TIN is in it"),
    ("Leseni ya biashara nipate wapi na ada ni kiasi gani na inaisha lini?", "an application question is in it"),
], 1):
    add(f"d18_rn_{i:02d}", "route", q, "none_of_new", why)

if __name__ == "__main__":
    with io.open(os.path.join(HERE, "d18_batch_probes_2026_11_17.jsonl"), "w", encoding="utf-8") as f:
        for p in P:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(len(P), "probes written")

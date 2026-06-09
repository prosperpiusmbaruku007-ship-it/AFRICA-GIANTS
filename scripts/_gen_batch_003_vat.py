"""Generate 40 VAT registration pairs (batch_003 pairs 131-170)."""
import json

SRC_URL = "https://www.tra.go.tz/page/value-added-tax"
SRC_NAME = "TRA VAT Page"
DATE = "20260608"

def p(n, sub, q_sw, a_sw, q_en, a_en, reg, ptype="adversarial"):
    return {"id": f"tier1a_vat_{n:03d}_{DATE}", "domain": "tier1a", "subdomain": sub,
            "question_sw": q_sw, "answer_sw": a_sw, "question_en": q_en, "answer_en": a_en,
            "primary_source_url": SRC_URL, "primary_source_name": SRC_NAME,
            "source_type": "government_portal", "effective_date": "2025-07-01",
            "decay_risk": "annual", "next_review_trigger": "Finance Act amendment",
            "verified_by": "CLAUDE.md locked_facts — TRA VAT", "verified_date": "2026-06-08",
            "register": reg, "pair_type": ptype, "eval_set": False}

pairs = []

# ── ADVERSARIAL: No 5% or 10% VAT (pairs 1-15) ──────────────────────────────

pairs.append(p(1,"vat_rates_adversarial",
    "Je, VAT ya chakula Tanzania ni asilimia 5?",
    "Hapana. Tanzania haina kiwango cha VAT kilichopunguzwa cha asilimia 5 wala asilimia 10. Kiwango kimoja tu cha VAT kinacho Tanzania Bara ni asilimia 18 — kiwango cha kawaida. Bidhaa za chakula fulani zinaweza kuwa zero-rated (asilimia 0) au zimesamehewa kabisa (exempt), lakini hakuna kiwango cha kati cha asilimia 5. Thibisha hali ya kila bidhaa na TRA.",
    "Is food VAT in Tanzania 5%?",
    "No. Tanzania does not have a reduced VAT rate of 5% or 10%. There is only one VAT rate on Mainland Tanzania: 18% standard rate. Some food items may be zero-rated (0%) or fully exempt, but there is no intermediate 5% rate. Confirm the status of each product with TRA.",
    "business_market"))

pairs.append(p(2,"vat_rates_adversarial",
    "Mtu alisema umeme unalipwa VAT ya asilimia 10 Tanzania. Je, hii ni kweli?",
    "Si kweli. Tanzania haina kiwango cha VAT cha asilimia 10. Kiwango cha VAT Tanzania Bara ni asilimia 18 peke yake — kiwango cha kawaida. Huduma za umeme zinaweza kuwa zero-rated au exempt kulingana na hali, lakini asilimia 10 haipo kabisa katika mfumo wa VAT wa Tanzania.",
    "Someone said electricity in Tanzania is charged VAT at 10%. Is this true?",
    "Not true. Tanzania does not have a 10% VAT rate. The VAT rate on Mainland Tanzania is 18% only — the standard rate. Electricity services may be zero-rated or exempt depending on the circumstances, but 10% simply does not exist in Tanzania's VAT system.",
    "business_market"))

pairs.append(p(3,"vat_rates_adversarial",
    "Mshauri wangu anasema bidhaa za kilimo zinalipwa VAT ya asilimia 5. Je, ni kweli?",
    "Hapana. Tanzania haina kiwango cha VAT cha asilimia 5. Kiwango cha VAT ni asilimia 18 tu — hakuna kiwango cha kati. Bidhaa za kilimo fulani zinaweza kuwa zero-rated (tozo ya asilimia 0) au zimesamehewa (exempt), lakini asilimia 5 haipo. Angalia orodha ya bidhaa zero-rated na exempt kwenye sheria ya VAT au tovuti ya TRA.",
    "My adviser says agricultural products attract 5% VAT. Is that correct?",
    "No. Tanzania does not have a 5% VAT rate. The VAT rate is 18% only — there is no intermediate rate. Some agricultural products may be zero-rated (0% rate) or exempt, but 5% does not exist. Check the list of zero-rated and exempt supplies in the VAT Act or on the TRA website.",
    "formal"))

pairs.append(p(4,"vat_rates_adversarial",
    "Nimeona kwenye mtandao kwamba Tanzania ina VAT ya asilimia 10 kwa huduma za hospitali. Je, hii ni sahihi?",
    "Hapana. Habari hiyo si sahihi. Tanzania haina kiwango cha VAT cha asilimia 10. Kiwango cha kawaida ni asilimia 18 tu. Huduma za hospitali nyingi zimesamehewa VAT (VAT exempt) — si asilimia 10. Vyanzo vya mtandao visivyo rasmi vinaweza kusambaza taarifa potofu. Thibisha na TRA.go.tz daima.",
    "I saw online that Tanzania has 10% VAT on hospital services. Is this correct?",
    "No. That information is incorrect. Tanzania does not have a 10% VAT rate. The standard rate is 18% only. Most hospital services are VAT exempt — not 10%. Unofficial internet sources can spread misinformation. Always verify at TRA.go.tz.",
    "business_market"))

pairs.append(p(5,"vat_rates_adversarial",
    "Je, Tanzania ina viwango vitatu vya VAT: asilimia 0, asilimia 5, na asilimia 18?",
    "Hapana. Tanzania ina viwango viwili tu vya VAT: asilimia 18 (kiwango cha kawaida) na asilimia 0 (zero-rated). Kuna pia bidhaa na huduma zilizo exempt (zimesamehewa) ambazo hazilipwi VAT kabisa. Hakuna kiwango cha asilimia 5 katika mfumo wa VAT wa Tanzania Bara.",
    "Does Tanzania have three VAT rates: 0%, 5%, and 18%?",
    "No. Tanzania has only two VAT rates: 18% (standard rate) and 0% (zero-rated). There are also exempt supplies which are not subject to VAT at all. There is no 5% VAT rate in Tanzania Mainland's VAT system.",
    "formal"))

pairs.append(p(6,"vat_rates_adversarial",
    "Mwanasheria alisema kuna VAT ya asilimia 5 kwa bidhaa za msingi (basic commodities). Je, ni kweli?",
    "Hapana. Hakuna kiwango cha VAT cha asilimia 5 kwa 'bidhaa za msingi' au bidhaa nyingine zozote Tanzania Bara. Kiwango cha VAT ni asilimia 18 tu — kiwango kimoja cha kawaida. Bidhaa za msingi fulani (kama vile baadhi ya nafaka) zinaweza kuwa zero-rated (asilimia 0) au exempt — si asilimia 5. Mshauri yeyote anayesema asilimia 5 ana kosa.",
    "A lawyer said there is 5% VAT on basic commodities. Is that true?",
    "No. There is no 5% VAT rate for 'basic commodities' or any other goods on Mainland Tanzania. The VAT rate is 18% only — one standard rate. Some basic commodities (such as certain grains) may be zero-rated (0%) or exempt — not 5%. Any adviser claiming 5% is incorrect.",
    "business_market"))

pairs.append(p(7,"vat_rates_adversarial",
    "Kodi ya ongezeko la thamani (VAT) kwa dawa ni asilimia ngapi Tanzania?",
    "Dawa nyingi za binadamu Tanzania zimewekwa kwenye orodha ya zero-rated — yaani VAT ni asilimia 0. Hata hivyo, kuna bidhaa za dawa ambazo zinalipwa VAT ya asilimia 18 (kiwango cha kawaida). Kiwango cha asilimia 5 au asilimia 10 haipo kabisa kwenye mfumo wa VAT Tanzania. Angalia orodha rasmi ya TRA kujua bidhaa gani za dawa ni zero-rated na zipi zinatozwa asilimia 18.",
    "What is the VAT rate on medicines in Tanzania?",
    "Most human medicines in Tanzania are zero-rated — meaning the VAT rate is 0%. However, some pharmaceutical products are subject to the standard 18% VAT. A rate of 5% or 10% does not exist at all in Tanzania's VAT system. Check the official TRA list to determine which medicines are zero-rated and which attract 18%.",
    "rural_conversational"))

pairs.append(p(8,"vat_rates_adversarial",
    "Kampuni yangu inaagiza bidhaa kutoka nje. Je, VAT ya asilimia 10 inatumika kwa uagizaji?",
    "Hapana. VAT ya uagizaji (import VAT) Tanzania ni asilimia 18 — kiwango cha kawaida. Hakuna kiwango cha asilimia 10 cha VAT Tanzania Bara. Bidhaa zingine za uagizaji zinaweza kuwa zero-rated au exempt, lakini asilimia 10 haipo. Kwa bidhaa zinazolipwa VAT, kiwango ni asilimia 18 tu.",
    "My company imports goods. Does 10% VAT apply to imports?",
    "No. Import VAT in Tanzania is 18% — the standard rate. There is no 10% VAT rate on Mainland Tanzania. Some imported goods may be zero-rated or exempt, but 10% does not exist. For goods subject to VAT, the rate is 18% only.",
    "business_market"))

pairs.append(p(9,"vat_rates_adversarial",
    "Niliambiwa kwamba hoteli na migahawa inalipa VAT ya asilimia 5 kwa chakula kinachouzwa. Je, ni kweli?",
    "Hapana. Hakuna kiwango maalum cha VAT cha asilimia 5 kwa hoteli au migahawa. Hoteli na migahawa zilizosajiliwa kwa VAT zinatozwa kiwango cha kawaida cha asilimia 18 kwenye mauzo yao. Hakuna kiwango cha kati cha asilimia 5 au asilimia 10 Tanzania Bara.",
    "I was told hotels and restaurants pay 5% VAT on food sold. Is this true?",
    "No. There is no special 5% VAT rate for hotels or restaurants. VAT-registered hotels and restaurants charge the standard 18% rate on their sales. There is no intermediate rate of 5% or 10% on Mainland Tanzania.",
    "business_market"))

pairs.append(p(10,"vat_rates_adversarial",
    "Naomba uthibitisho: kiwango cha juu cha VAT Tanzania ni asilimia 18 na cha chini ni asilimia 5?",
    "Hapana sahihi. Tanzania haina muundo wa 'juu' na 'chini' wa viwango vya VAT. Kuna kiwango kimoja cha kawaida: asilimia 18. Bidhaa/huduma zingine ni zero-rated (asilimia 0) na nyingine zimesamehewa kabisa (exempt). Kiwango cha asilimia 5 hakipo. Muundo ni: exempt (hakuna VAT), zero-rated (asilimia 0), standard (asilimia 18).",
    "Please confirm: is the highest VAT rate in Tanzania 18% and the lowest 5%?",
    "Not correct. Tanzania does not have a 'high' and 'low' VAT rate structure. There is one standard rate: 18%. Some goods/services are zero-rated (0%) and others are fully exempt. A 5% rate does not exist. The structure is: exempt (no VAT), zero-rated (0%), standard (18%).",
    "formal"))

pairs.append(p(11,"vat_rates_adversarial",
    "Je, Tanzania ina VAT ya asilimia 5 kwa bidhaa zilizo 'essential'?",
    "Hapana. Tanzania haina kiwango cha VAT cha asilimia 5 cha aina yoyote — including 'essential goods'. Bidhaa fulani za muhimu (kama nafaka, dawa, baadhi ya vifaa vya kilimo) zinaweza kuwa zero-rated (asilimia 0) au exempt, lakini asilimia 5 haipo. Kiwango cha kawaida cha VAT ni asilimia 18 tu.",
    "Does Tanzania have 5% VAT on 'essential' goods?",
    "No. Tanzania does not have a 5% VAT rate of any kind — including for 'essential goods'. Some essential items (like certain grains, medicines, some agricultural inputs) may be zero-rated (0%) or exempt, but 5% does not exist. The standard VAT rate is 18% only.",
    "rural_conversational"))

pairs.append(p(12,"vat_rates_adversarial",
    "Kampuni zangu inaona invoice kutoka kwa msambazaji inayosema '10% VAT included'. Je, hii ni halali Tanzania?",
    "Hapana. Kiwango cha VAT cha asilimia 10 hakipo Tanzania Bara. Invoice hiyo ni makosa au ni ya nje ya Tanzania. Kiwango cha halisi cha VAT Tanzania ni asilimia 18. Ikiwa msambazaji ni Tanzania na ana usajili wa VAT, anapaswa kutozea asilimia 18. Ripoti invoice hii ya makosa kwa TRA au mwambie msambazaji asahihishe.",
    "My company receives invoices from a supplier showing '10% VAT included'. Is this legal in Tanzania?",
    "No. A 10% VAT rate does not exist on Mainland Tanzania. That invoice is either an error or relates to a non-Tanzanian transaction. The correct VAT rate in Tanzania is 18%. If the supplier is Tanzanian and VAT-registered, they should be charging 18%. Report this erroneous invoice to TRA or ask the supplier to correct it.",
    "business_market"))

pairs.append(p(13,"vat_rates_adversarial",
    "Je, kiwango cha VAT Tanzania kimebadilika kutoka asilimia 18 kwenda asilimia 16 mwaka 2025?",
    "Hapana. Kiwango cha kawaida cha VAT Tanzania Bara kilibaki asilimia 18 mwaka 2025. Kilichobadilika ni VAT ya malipo ya kidijitali (B2C e-payment) ambayo Finance Act 2025 ilipanga asilimia 16 kuanzia 1 Septemba 2025 — lakini hii ni kwa aina maalum ya muamala wa kidijitali peke yake, si kiwango cha kawaida. Kwa biashara ya kawaida ya Tanzania, VAT ni asilimia 18.",
    "Did Tanzania's VAT rate change from 18% to 16% in 2025?",
    "No. The standard VAT rate on Mainland Tanzania remained at 18% throughout 2025. What changed is that Finance Act 2025 set a 16% rate specifically for B2C e-payment transactions effective 1 September 2025 — but this applies to that specific digital transaction category only, not the standard rate. For regular Tanzanian business, VAT is 18%.",
    "formal"))

pairs.append(p(14,"vat_rates_adversarial",
    "Rafiki yangu anasema Tanzania imepunguza VAT kwenda asilimia 5 mwaka 2025. Je, ni kweli?",
    "Hapana. VAT ya Tanzania haijapunguzwa kwenda asilimia 5 mwaka 2025 wala wakati wowote. Kiwango cha kawaida cha VAT Tanzania Bara ni asilimia 18, na kimekuwa hivyo tangu 2015. Finance Act 2025 ilipunguza kiwango cha SDL kutoka asilimia 4 hadi asilimia 3.5, lakini VAT ilibaki asilimia 18.",
    "My friend says Tanzania reduced VAT to 5% in 2025. Is that true?",
    "No. Tanzania's VAT was not reduced to 5% in 2025 or at any other time. The standard VAT rate on Mainland Tanzania is 18%, and has been since 2015. Finance Act 2025 reduced the SDL rate from 4% to 3.5%, but VAT remained at 18%.",
    "rural_conversational"))

pairs.append(p(15,"vat_rates_adversarial",
    "Je, Tanzania ina viwango vya VAT tofauti kwa sekta tofauti — kama nchi nyingine za Afrika Mashariki?",
    "Hapana. Tanzania (Bara) haina viwango tofauti vya VAT kwa sekta tofauti. Kuna kiwango kimoja cha kawaida: asilimia 18. Kenya na Uganda zina viwango vilivyopunguzwa (zero-rated na exempt) lakini Tanzania haina kiwango cha kati kama asilimia 5 au 10. Bidhaa/huduma ni ama standard (18%), zero-rated (0%), au exempt (hakuna VAT). Hii inatofautiana na imani za kawaida.",
    "Does Tanzania have different VAT rates for different sectors — like other East African countries?",
    "No. Tanzania (Mainland) does not have different VAT rates for different sectors. There is one standard rate: 18%. Kenya and Uganda have reduced rates but Tanzania has no intermediate rate like 5% or 10%. Supplies are either standard (18%), zero-rated (0%), or exempt (no VAT). This differs from common misconceptions.",
    "formal"))

# ── VAT REGISTRATION THRESHOLD (pairs 16-25) ────────────────────────────────

pairs.append(p(16,"vat_registration",
    "Kizingiti cha usajili wa VAT Tanzania ni kiasi gani?",
    "Kizingiti cha usajili wa lazima wa VAT Tanzania ni: mauzo ya TZS 200,000,000 (shilingi milioni 200) ndani ya miezi 12, AU mauzo ya TZS 100,000,000 (shilingi milioni 100) ndani ya miezi 6. Ukifikia moja ya masharti haya, lazima ujisajili kwa VAT na TRA ndani ya siku 30. Usajili wa hiari unawezekana pia ikiwa una mauzo chini ya kizingiti.",
    "What is the VAT registration threshold in Tanzania?",
    "The mandatory VAT registration threshold in Tanzania is: sales of TZS 200,000,000 (200 million shillings) in any 12-month period, OR sales of TZS 100,000,000 (100 million shillings) in any 6-month period. If you reach either condition, you must register for VAT with TRA within 30 days. Voluntary registration is also possible if your sales are below the threshold.",
    "business_market","standard"))

pairs.append(p(17,"vat_registration",
    "Biashara yangu imefanya mauzo ya TZS 110,000,000 katika miezi 6 iliyopita. Je, lazima nisajiliwe kwa VAT?",
    "Ndiyo. Umefika kizingiti cha lazima cha usajili wa VAT. Mauzo ya TZS 100,000,000 ndani ya miezi 6 yanasababisha usajili wa lazima. Sasa una TZS 110,000,000 katika miezi 6, kwa hivyo lazima ujisajili kwa VAT na TRA ndani ya siku 30. Kiwango cha VAT utakachozoza ni asilimia 18 — kiwango cha pekee cha kawaida Tanzania Bara.",
    "My business made TZS 110,000,000 in sales over the last 6 months. Must I register for VAT?",
    "Yes. You have reached the mandatory VAT registration threshold. Sales of TZS 100,000,000 in any 6-month period trigger mandatory registration. With TZS 110,000,000 over 6 months, you must register for VAT with TRA within 30 days. The VAT rate you will charge is 18% — the only standard rate on Mainland Tanzania.",
    "business_market","standard"))

pairs.append(p(18,"vat_registration",
    "Kizingiti cha VAT ni TZS 100 milioni au TZS 200 milioni? Sielewi.",
    "Ni vyote viwili — lakini ni masharti mawili tofauti: (1) TZS 200,000,000 katika kipindi chochote cha miezi 12; AU (2) TZS 100,000,000 katika kipindi chochote cha miezi 6. Ukifikia MOJAWAPO ya hizi, usajili wa VAT unakuwa lazima ndani ya siku 30. VAT unayozoza baada ya usajili ni asilimia 18 — kiwango kimoja cha kawaida.",
    "Is the VAT threshold TZS 100 million or TZS 200 million? I am confused.",
    "It is both — but they are two separate conditions: (1) TZS 200,000,000 in any 12-month period; OR (2) TZS 100,000,000 in any 6-month period. If you meet EITHER of these, VAT registration becomes mandatory within 30 days. The VAT you charge after registration is 18% — the one standard rate.",
    "rural_conversational","standard"))

pairs.append(p(19,"vat_registration",
    "Ninaweza kujisajili kwa VAT hiari hata kama mauzo yangu ni TZS 80,000,000 kwa mwaka?",
    "Ndiyo. Usajili wa hiari wa VAT unawezekana hata kama mauzo yako yako chini ya kizingiti cha lazima. Faida ya usajili wa hiari ni kwamba unaweza kudai input VAT (VAT uliyolipa kwa wanunuzi). Hasara ni kwamba lazima uzingatie majukumu yote ya VAT — kuwasilisha returns na kulipa VAT ya asilimia 18 kwa wateja. Wasiliana na TRA kwa maelezo zaidi.",
    "Can I voluntarily register for VAT even if my sales are TZS 80,000,000 per year?",
    "Yes. Voluntary VAT registration is possible even if your sales are below the mandatory threshold. The benefit of voluntary registration is that you can claim input VAT (VAT paid to your suppliers). The downside is that you must comply with all VAT obligations — filing returns and charging 18% VAT to customers. Contact TRA for more details.",
    "business_market","standard"))

pairs.append(p(20,"vat_registration",
    "Kizingiti cha VAT Tanzania kimebadilika mwaka 2025?",
    "Hapana. Kizingiti cha usajili wa VAT Tanzania Bara kilibaki bila mabadiliko mwaka 2025: TZS 200,000,000 kwa miezi 12, au TZS 100,000,000 kwa miezi 6. Finance Act 2025 haikubadilisha kizingiti hiki. Kiwango cha VAT pia kilibaki asilimia 18 — kiwango kimoja cha kawaida.",
    "Did the VAT threshold in Tanzania change in 2025?",
    "No. The VAT registration threshold on Mainland Tanzania remained unchanged in 2025: TZS 200,000,000 over 12 months, or TZS 100,000,000 over 6 months. Finance Act 2025 did not change this threshold. The VAT rate also remained 18% — the one standard rate.",
    "formal","standard"))

pairs.append(p(21,"vat_registration",
    "Je, kampuni mpya lazima ijisajili kwa VAT mara inapofungua biashara?",
    "Hapana lazima mara moja, lakini lazima ufuatilie mauzo yako. Usajili wa lazima unafuata pale unapofika kizingiti: mauzo ya TZS 200M katika miezi 12, au TZS 100M katika miezi 6. Ukifikia kizingiti, una siku 30 za kujisajili. Huna budi kujisajili siku ya kwanza ya biashara — ila kwa hiari unaweza kufanya hivyo. Kiwango cha VAT utakacho zoza ni asilimia 18.",
    "Must a new company register for VAT as soon as it opens?",
    "Not necessarily on day one, but you must monitor your turnover. Mandatory registration follows when you reach the threshold: TZS 200M in 12 months, or TZS 100M in 6 months. Once reached, you have 30 days to register. You do not have to register on the first day of business — though voluntary registration is possible. The VAT rate you will charge is 18%.",
    "business_market","standard"))

pairs.append(p(22,"vat_registration",
    "Biashara yangu inaendesha huduma za ushauri. Je, kizingiti cha VAT ni sawa kwa huduma na bidhaa?",
    "Ndiyo. Kizingiti cha usajili wa VAT kinatumika kwa bidhaa NA huduma: TZS 200,000,000 kwa miezi 12, au TZS 100,000,000 kwa miezi 6 — bila kujali aina ya biashara. Huduma za ushauri zinazopita kizingiti hiki lazima zisajiliwe kwa VAT. Kiwango cha kawaida cha VAT ni asilimia 18. Hakuna kiwango maalum cha chini kwa huduma.",
    "My business provides consultancy services. Is the VAT threshold the same for services as for goods?",
    "Yes. The VAT registration threshold applies to both goods AND services: TZS 200,000,000 in 12 months, or TZS 100,000,000 in 6 months — regardless of business type. Consultancy services that exceed this threshold must register for VAT. The standard VAT rate is 18%. There is no special lower rate for services.",
    "formal","standard"))

pairs.append(p(23,"vat_registration",
    "Nini kinatokea nikichelewa kujisajili kwa VAT baada ya kufika kizingiti?",
    "Uchelewaji wa usajili wa VAT una adhabu kali. TRA inaweza: (1) Kukuandalia VAT ya malimbikizo kwa kipindi chote cha uchelewaji kwa kiwango cha asilimia 18; (2) Kutoza faini ya usajili wa kuchelewa; (3) Kutozea riba kwa VAT iliyodaiwa. Jisajili mapema iwezekanavyo ukifika kizingiti — siku 30 ni kikomo cha kisheria.",
    "What happens if I delay registering for VAT after reaching the threshold?",
    "Delayed VAT registration carries serious penalties. TRA may: (1) Assess backdated VAT for the entire period of delay at 18%; (2) Impose a late registration penalty; (3) Charge interest on the VAT assessed. Register as soon as possible once you reach the threshold — 30 days is the legal deadline.",
    "business_market","standard"))

pairs.append(p(24,"vat_registration",
    "Je, usajili wa VAT Tanzania unahitaji nini?",
    "Usajili wa VAT Tanzania unahitaji: (1) Namba ya Utambulisho wa Mlipa Kodi (TIN) iliyopo; (2) Akaunti ya benki ya biashara; (3) Anwani halisi ya biashara; (4) Rekodi za mauzo zinazoonyesha kizingiti kimefikiwa (TZS 200M/12mo au 100M/6mo); (5) Fomu ya usajili wa VAT iliyojazwa (VAT Form 102). Wasiliana na ofisi ya TRA karibu nawe au tumia mfumo wa IDRAS.",
    "What does VAT registration in Tanzania require?",
    "VAT registration in Tanzania requires: (1) An existing Tax Identification Number (TIN); (2) A business bank account; (3) A physical business address; (4) Sales records showing the threshold has been reached (TZS 200M/12mo or 100M/6mo); (5) Completed VAT registration form (VAT Form 102). Contact your nearest TRA office or use the IDRAS system.",
    "rural_conversational","standard"))

pairs.append(p(25,"vat_registration",
    "Je, biashara ndogo yenye mauzo ya TZS 50 milioni kwa mwaka inalazimika kulipa VAT?",
    "Hapana — mauzo ya TZS 50,000,000 kwa mwaka yako chini ya kizingiti cha lazima cha usajili wa VAT (TZS 200M kwa miezi 12 au TZS 100M kwa miezi 6). Biashara yako haihitajiwi kujisajili kwa VAT kwa lazima. Unaweza kuchagua kujisajili kwa hiari ikiwa unataka kudai input VAT. Kiwango cha VAT — ukisajiliwa — ni asilimia 18.",
    "Must a small business with TZS 50 million annual sales pay VAT?",
    "No — sales of TZS 50,000,000 per year are below the mandatory VAT registration threshold (TZS 200M in 12 months or TZS 100M in 6 months). Your business is not required to register for VAT. You may choose voluntary registration if you want to claim input VAT. The VAT rate — if registered — is 18%.",
    "rural_conversational","standard"))

# ── VAT WITHHOLDING 3%/6% (pairs 26-33) ─────────────────────────────────────

pairs.append(p(26,"vat_withholding",
    "VAT withholding ni nini na kiwango chake ni kiasi gani Tanzania?",
    "VAT withholding ni mfumo ambapo mnunuzi (mwenye leseni ya kuzuia VAT) anamzuia msambazaji sehemu ya VAT na kuipeleka TRA moja kwa moja. Kiwango: asilimia 3 kwa bidhaa na asilimia 6 kwa huduma, kuanzia 1 Julai 2025 (Finance Act 2025). VAT ya kawaida ni asilimia 18 — withholding ni sehemu tu inayozuiwa, si kiwango kipya cha VAT.",
    "What is VAT withholding and what is its rate in Tanzania?",
    "VAT withholding is a system where the buyer (designated withholding agent) withholds a portion of VAT from the supplier and remits it directly to TRA. Rate: 3% on goods and 6% on services, effective 1 July 2025 (Finance Act 2025). Standard VAT remains 18% — withholding is a portion withheld, not a new VAT rate.",
    "formal","standard"))

pairs.append(p(27,"vat_withholding",
    "Je, withholding ya VAT kwa bidhaa ni asilimia 3 au asilimia 6?",
    "Withholding ya VAT kwa bidhaa ni asilimia 3, na kwa huduma ni asilimia 6 — kuanzia 1 Julai 2025 (Finance Act 2025). VAT ya jumla inabaki asilimia 18. Manunuzi wanaopewa leseni ya kuzuia VAT wanazuia sehemu hii na kuipeleka TRA, na msambazaji analipwa kilichobaki. Kumbuka: kiwango cha kawaida cha VAT Tanzania ni asilimia 18 tu — si asilimia 3 wala 6.",
    "Is VAT withholding on goods 3% or 6%?",
    "VAT withholding on goods is 3%, and on services is 6% — effective 1 July 2025 (Finance Act 2025). Total VAT remains 18%. Designated withholding agents withhold this portion and remit it to TRA, with the supplier receiving the balance. Note: the standard VAT rate in Tanzania is 18% only — not 3% or 6%.",
    "business_market","standard"))

pairs.append(p(28,"vat_withholding",
    "Kampuni yetu ni designated VAT withholding agent. Je, tunazuia kiasi gani kwenye invoice ya huduma ya TZS 1,000,000 ya VAT?",
    "Kwenye invoice ya huduma yenye VAT ya asilimia 18: VAT ya jumla = TZS 1,000,000 × 18% = TZS 180,000. Kama kampuni yako ni designated withholding agent, unazuia asilimia 6 ya VAT = TZS 180,000 × 6/18 = TZS 60,000. Msambazaji anapokea TZS 120,000 (asilimia 12/18 ya VAT). Unalipa TRA TZS 60,000 kama VAT iliyozuiwa na msambazaji analipa TRA TZS 120,000 iliyobaki.",
    "Our company is a designated VAT withholding agent. How much do we withhold on a services invoice with TZS 1,000,000 VAT?",
    "On a services invoice with 18% VAT: Total VAT = TZS 1,000,000 × 18% = TZS 180,000. As a designated withholding agent, you withhold 6% of VAT = TZS 180,000 × 6/18 = TZS 60,000. The supplier receives TZS 120,000 (12/18 of VAT). You remit TZS 60,000 to TRA as withheld VAT and the supplier remits the remaining TZS 120,000.",
    "formal","standard"))

pairs.append(p(29,"vat_withholding",
    "VAT withholding certificate lazima itolewa lini?",
    "Cheti cha VAT withholding (VAT withholding certificate) lazima kitolewa siku VAT inakuwa inadaiwa — si tarehe ya 20 ya mwezi unaofuata. Tarehe ya 20 ni mwisho wa kuwasilisha return ya VAT — hizi ni wajibu tofauti mbili. Cheti cha VAT withholding kinatolewa wakati wa muamala, sio baadaye.",
    "When must a VAT withholding certificate be issued?",
    "A VAT withholding certificate must be issued by the day the VAT becomes payable — not by the 20th of the following month. The 20th is the VAT return filing deadline — these are two separate obligations. The withholding certificate is issued at the time of the transaction, not later.",
    "formal","standard"))

pairs.append(p(30,"vat_withholding",
    "Tofauti kati ya VAT withholding na VAT ya kawaida ni nini?",
    "VAT ya kawaida: msambazaji ananunuliwa bidhaa/huduma kwa bei pamoja na VAT ya asilimia 18, kisha yeye analipa VAT hiyo TRA kwenye return yake ya kila mwezi (mwisho wa 20). VAT withholding: mnunuzi aliyepewa leseni anazuia sehemu ya VAT (asilimia 3 kwa bidhaa, 6 kwa huduma) na kuipeleka TRA moja kwa moja — kabla msambazaji hajalipa. Kiwango cha VAT yenyewe ni asilimia 18 daima.",
    "What is the difference between VAT withholding and normal VAT?",
    "Normal VAT: the supplier charges the buyer the price plus 18% VAT, then remits that VAT to TRA on their monthly return (due 20th). VAT withholding: the licensed buyer withholds a portion of VAT (3% on goods, 6% on services) and remits it directly to TRA — before the supplier pays. The VAT rate itself is always 18%.",
    "business_market","standard"))

pairs.append(p(31,"vat_withholding",
    "Je, VAT withholding inatumika kwa wote Tanzania au kwa makampuni maalum tu?",
    "VAT withholding inatumika kwa makampuni maalum tu — wale waliopewa leseni ya 'designated withholding agent' na TRA. Si makampuni yote. Kawaida ni taasisi za serikali na makampuni makubwa ya sekta binafsi yaliyochaguliwa na TRA. Kama hujapewa leseni hiyo, huhitajiwi kuzuia VAT. Kiwango cha VAT kwako bado ni asilimia 18 ya kawaida.",
    "Does VAT withholding apply to everyone in Tanzania or only specific companies?",
    "VAT withholding applies only to specific companies — those designated as 'withholding agents' by TRA. Not all companies. Typically these are government institutions and selected large private sector companies chosen by TRA. If you have not been designated as a withholding agent, you are not required to withhold VAT. Your VAT rate remains the standard 18%.",
    "business_market","standard"))

pairs.append(p(32,"vat_withholding",
    "Je, kiwango cha VAT withholding kilikuwa tofauti kabla ya Finance Act 2025?",
    "Ndiyo. Kabla ya Finance Act 2025, kiwango cha VAT withholding kilikuwa: asilimia 2 kwa bidhaa na asilimia 5 kwa huduma (kwa baadhi ya makampuni) au viwango tofauti. Finance Act 2025 ilipanga upya: asilimia 3 kwa bidhaa na asilimia 6 kwa huduma, kuanzia 1 Julai 2025. Kiwango cha kawaida cha VAT kilibaki asilimia 18 — hakikubadilika.",
    "Was the VAT withholding rate different before Finance Act 2025?",
    "Yes. Before Finance Act 2025, the VAT withholding rate was different. Finance Act 2025 standardised it at: 3% on goods and 6% on services, effective 1 July 2025. The standard VAT rate remained at 18% — it did not change.",
    "formal","standard"))

pairs.append(p(33,"vat_withholding",
    "B2C e-payment VAT Tanzania ni asilimia ngapi?",
    "Finance Act 2025 ilipanga kiwango cha VAT kwa malipo ya kidijitali ya B2C (mtumiaji binafsi) kuwa asilimia 16, kuanzia 1 Septemba 2025 — kanuni za utekelezaji bado zinangojewa kutangazwa na Kamishna Mkuu wa TRA. Hii ni kwa aina maalum ya muamala wa kidijitali (B2C e-payment) peke yake. Kiwango cha kawaida cha VAT kwa biashara za kawaida bado ni asilimia 18.",
    "What is the B2C e-payment VAT rate in Tanzania?",
    "Finance Act 2025 set the VAT rate for B2C (business-to-consumer) digital payments at 16%, effective 1 September 2025 — implementation rules are still awaited from the Commissioner General of TRA. This applies to that specific digital transaction category only. The standard VAT rate for regular business transactions remains 18%.",
    "formal","standard"))

# ── ZERO-RATED VS EXEMPT (pairs 34-40) ──────────────────────────────────────

pairs.append(p(34,"vat_zero_exempt",
    "Tofauti kati ya 'zero-rated' na 'exempt' kwa VAT Tanzania ni nini?",
    "Zero-rated: bidhaa/huduma zinatozwa VAT ya asilimia 0. Msambazaji bado anaweza kudai input VAT aliyolipa kwa manunuzi wake. Mfano: mazao ya kilimo fulani, dawa fulani, mauzo ya nje (exports). Exempt: bidhaa/huduma hazilipwi VAT kabisa, LAKINI msambazaji hawezi kudai input VAT. Mfano: huduma za fedha, ardhi, baadhi ya huduma za elimu. Tofauti kubwa: msambazaji wa zero-rated anadai input VAT; msambazaji wa exempt hadai.",
    "What is the difference between 'zero-rated' and 'exempt' for VAT purposes in Tanzania?",
    "Zero-rated: goods/services are taxed at 0% VAT. The supplier can still claim input VAT paid to their own suppliers. Examples: certain agricultural produce, certain medicines, exports. Exempt: goods/services are not subject to VAT, BUT the supplier cannot claim input VAT. Examples: financial services, land, some educational services. Key difference: zero-rated supplier claims input VAT; exempt supplier cannot.",
    "formal","standard"))

pairs.append(p(35,"vat_zero_exempt",
    "Je, mauzo ya nje (exports) yana VAT ya asilimia ngapi?",
    "Mauzo ya nje (exports) kutoka Tanzania yana VAT ya asilimia 0 — yaani zero-rated. Msambazaji anaweza kudai input VAT aliyolipa kwenye ununuzi wa bidhaa hizo. Hii inasaidia ushindani wa bidhaa za Tanzania nje ya nchi. Kumbuka: kiwango cha kawaida cha VAT kwa mauzo ya ndani ni asilimia 18 — si asilimia 5 wala asilimia 0 kwa biashara ya kawaida.",
    "What VAT rate applies to exports from Tanzania?",
    "Exports from Tanzania are zero-rated — meaning the VAT rate is 0%. The supplier can claim back input VAT paid on purchases related to those exports. This supports the competitiveness of Tanzanian exports. Note: the standard VAT rate for domestic sales is 18% — not 5% or 0% for normal business.",
    "business_market","standard"))

pairs.append(p(36,"vat_zero_exempt",
    "Huduma za benki zinalipwa VAT Tanzania?",
    "Hapana. Huduma za fedha/benki nyingi Tanzania zimesamehewa VAT (VAT exempt) — hazilipwi VAT. Hata hivyo, 'exempt' ina maana kwamba benki haiwezi kudai input VAT kwenye gharama zake za uendeshaji. Kumbuka: kiwango cha kawaida cha VAT Tanzania ni asilimia 18 — huduma za benki ni mfano wa exempt supplies, si bidhaa/huduma zinazotozwa asilimia 5 au 10.",
    "Are banking services subject to VAT in Tanzania?",
    "No. Most financial/banking services in Tanzania are VAT exempt — not subject to VAT. However, 'exempt' means the bank cannot claim input VAT on its operating costs. Note: the standard VAT rate in Tanzania is 18% — banking services are an example of exempt supplies, not goods/services charged at 5% or 10%.",
    "business_market","standard"))

pairs.append(p(37,"vat_zero_exempt",
    "Je, biashara yangu inayouza bidhaa za zero-rated na bidhaa za standard lazima ifanye nini?",
    "Biashara inayouza aina zote mbili (zero-rated na standard rated) ni 'partially exempt'. Unapaswa: (1) Kufuatilia kwa makini mauzo ya aina kila moja; (2) Kuhesabu input VAT inayodaiwa kwa uwiano wa mauzo ya standard rated; (3) Kudai sehemu ya input VAT inayohusiana na mauzo ya standard na zero-rated tu (si exempt). Kiwango cha VAT kwa bidhaa za standard ni asilimia 18 — si asilimia 5.",
    "My business sells both zero-rated and standard-rated goods. What must I do?",
    "A business selling both types (zero-rated and standard-rated) is 'partially exempt'. You must: (1) Track sales of each type carefully; (2) Calculate claimable input VAT based on the proportion of standard-rated sales; (3) Only claim the portion of input VAT related to standard-rated and zero-rated sales (not exempt). The VAT rate on standard goods is 18% — not 5%.",
    "formal","standard"))

pairs.append(p(38,"vat_zero_exempt",
    "Je, elimu Tanzania inalipwa VAT?",
    "Huduma za elimu rasmi (shule, vyuo) nyingi Tanzania zimesamehewa VAT (VAT exempt). Hii inamaanisha hazilipwi VAT, lakini taasisi ya elimu haiwezi kudai input VAT kwenye gharama zake. Mafunzo ya biashara ya biashara (commercial training) yanaweza kutozwa VAT ya asilimia 18. Angalia hali ya kila aina ya huduma ya elimu na TRA. Hakuna kiwango cha VAT cha asilimia 5 kwa elimu.",
    "Are educational services subject to VAT in Tanzania?",
    "Most formal educational services (schools, colleges) in Tanzania are VAT exempt. This means they are not subject to VAT, but the institution cannot claim input VAT on its costs. Commercial training services may be subject to standard 18% VAT. Check the status of each type of educational service with TRA. There is no 5% VAT rate for education.",
    "formal","standard"))

pairs.append(p(39,"vat_zero_exempt",
    "Kama ninauza bidhaa za exempt, je ninahitaji kusajiliwa kwa VAT?",
    "Ikiwa bidhaa ZOTE unazouza ni exempt, basi mauzo yako ya kizingiti (TZS 200M/mwaka au 100M/miezi 6) hayahesabiki kwa VAT — na kwa hivyo huhitajiwi kujisajili kwa VAT hata kama unazidi kizingiti. Hata hivyo, ikiwa una mchanganyiko wa exempt na taxable supplies, mauzo ya taxable peke yake ndiyo yanayohesabiwa dhidi ya kizingiti. Wasiliana na TRA kwa ufafanuzi wa hali yako.",
    "If I sell exempt goods, do I need to register for VAT?",
    "If ALL your supplies are exempt, your turnover does not count towards the VAT threshold (TZS 200M/year or 100M/6 months) — and you are not required to register for VAT even if you exceed the threshold. However, if you have a mix of exempt and taxable supplies, only your taxable sales count towards the threshold. Contact TRA for clarification on your specific situation.",
    "rural_conversational","standard"))

pairs.append(p(40,"vat_zero_exempt",
    "VAT return inawasilishwa lini Tanzania?",
    "Return ya VAT Tanzania inawasilishwa kila mwezi, mwisho wa tarehe 20 ya mwezi unaofuata kipindi cha kuripoti. Kwa mfano: VAT ya Januari inawasilishwa ifikapo 20 Februari. Kiwango cha VAT unachodai kwenye return ni asilimia 18 (kiwango cha kawaida) — hakuna kiwango cha asilimia 5 au 10. Input VAT (VAT uliyolipa kwa manunuzi) inakatwa dhidi ya output VAT (VAT uliyokusanya kwa wateja).",
    "When is a VAT return submitted in Tanzania?",
    "VAT returns in Tanzania are submitted monthly, by the 20th of the month following the reporting period. For example: January VAT is due by 20 February. The VAT rate on your return is 18% (standard rate) — there is no 5% or 10% rate. Input VAT (VAT paid to suppliers) is offset against output VAT (VAT collected from customers).",
    "business_market","standard"))

# ── WRITE ──────────────────────────────────────────────────────────────────────
OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl"
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
print(f"Wrote {len(pairs)} VAT pairs")
regs = {}
for pr in pairs:
    regs[pr["register"]] = regs.get(pr["register"], 0) + 1
total = len(pairs)
for k, v in sorted(regs.items()):
    print(f"  {k}: {v} ({v/total*100:.0f}%)")

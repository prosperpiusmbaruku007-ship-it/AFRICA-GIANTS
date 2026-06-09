"""Generate 50 EFD compliance deep-dive pairs (batch_003 pairs 251-300)."""
import json

SRC_URL = "https://www.tra.go.tz/page/electronic-fiscal-devices"
SRC_NAME = "TRA EFD Page"
DATE = "20260608"

def p(n, sub, q_sw, a_sw, q_en, a_en, reg, ptype="standard"):
    return {"id": f"tier1a_efd_deep_{n:03d}_{DATE}", "domain": "tier1a", "subdomain": sub,
            "question_sw": q_sw, "answer_sw": a_sw, "question_en": q_en, "answer_en": a_en,
            "primary_source_url": SRC_URL, "primary_source_name": SRC_NAME,
            "source_type": "government_portal", "effective_date": "2025-07-01",
            "decay_risk": "annual", "next_review_trigger": "TRA EFD regulation update",
            "verified_by": "TRA EFD regulations + VAT Act", "verified_date": "2026-06-08",
            "register": reg, "pair_type": ptype, "eval_set": False}

pairs = []

# ── EFD MACHINE TYPES (pairs 1-5) ────────────────────────────────────────────

pairs.append(p(1,"efd_machine_types",
    "Tofauti kati ya ETR, EFD, na VFD ni nini Tanzania?",
    "ETR (Electronic Tax Register) ni kifaa cha zamani cha mauzo kinachotoa risiti za kawaida — mfumo wa zamani. EFD (Electronic Fiscal Device) ni kifaa kipya cha mauzo chenye uhusiano wa moja kwa moja na seva ya TRA — kinatuma taarifa za kila muamala mara moja. VFD (Virtual Fiscal Device) ni programu ya kompyuta (software) inayofanya kazi ya EFD — inafaa kwa biashara zinazotumia mifumo ya ERP au mauzo ya mtandao. TRA inasimamia aina zote tatu.",
    "What is the difference between ETR, EFD, and VFD in Tanzania?",
    "ETR (Electronic Tax Register) is the older cash register device issuing standard receipts — the old system. EFD (Electronic Fiscal Device) is the newer device with a direct connection to TRA's server — it transmits data on every transaction in real time. VFD (Virtual Fiscal Device) is a software solution that performs the EFD function — suitable for businesses using ERP systems or online sales. TRA regulates all three types.",
    "formal"))

pairs.append(p(2,"efd_machine_types",
    "Je, biashara yangu ya mtandao inahitaji EFD au VFD?",
    "Biashara ya mtandao inayosajiliwa kwa VAT inahitaji VFD (Virtual Fiscal Device) — programu ya kidijitali inayoandaa risiti za kifikia za TRA bila kifaa cha kimwili. VFD inapeleka taarifa za muamala moja kwa moja kwa seva ya TRA. Biashara za kimwili zinaweza kutumia EFD (kifaa cha kimwili) au VFD (programu). Wasiliana na TRA kwa orodha ya watoa huduma wa VFD walioidhinishwa.",
    "Does my online business need an EFD or VFD?",
    "An online business registered for VAT needs a VFD (Virtual Fiscal Device) — a digital software solution that generates TRA-compliant receipts without a physical device. VFD transmits transaction data directly to TRA's server. Physical businesses can use either an EFD (physical device) or VFD (software). Contact TRA for a list of approved VFD providers.",
    "business_market"))

pairs.append(p(3,"efd_machine_types",
    "Je, EFD lazima iwe na muunganiko wa intaneti daima?",
    "EFD ya kisasa inahitaji muunganiko wa intaneti ili kupeleka taarifa kwa seva ya TRA. Ikiwa intaneti itakatika, EFD inaweza kuhifadhi taarifa za muamala (offline mode) na kuzipeleka seva ya TRA muunganiko unapofufuka. Biashara haistahili kusimamisha mauzo kwa sababu ya kukatika kwa intaneti — EFD inaendelea kutoa risiti — lakini taarifa zinapelekwa mara muunganiko utakapofufuka. Kumbuka kurejesha muunganiko haraka iwezekanavyo.",
    "Must an EFD always be connected to the internet?",
    "Modern EFDs require an internet connection to transmit data to TRA's server. If internet is disconnected, the EFD can store transaction data (offline mode) and transmit to TRA's server when reconnected. Business should not stop sales due to internet outage — the EFD continues issuing receipts — but data must be transmitted as soon as the connection is restored. Restore connectivity as quickly as possible.",
    "business_market"))

pairs.append(p(4,"efd_machine_types",
    "EFD inahitajika kwa biashara ndogo — threshold ni kiasi gani?",
    "Biashara zilizosajiliwa kwa VAT ni lazima zitumie EFD — bila kujali ukubwa wa biashara. Kizingiti cha usajili wa EFD kinafuata kizingiti cha usajili wa VAT: TZS 200,000,000 kwa miezi 12 au TZS 100,000,000 kwa miezi 6. Ukisajiliwa kwa VAT, lazima utumie EFD au VFD. Biashara zisizosajiliwa kwa VAT hazilazimishwi na EFD — lakini TRA inaweza kubadilisha hii.",
    "Is EFD required for small businesses — what is the threshold?",
    "Businesses registered for VAT must use EFD — regardless of business size. The EFD registration threshold follows the VAT registration threshold: TZS 200,000,000 in 12 months or TZS 100,000,000 in 6 months. Once registered for VAT, you must use an EFD or VFD. Non-VAT-registered businesses are not required to use EFD — but TRA may change this.",
    "rural_conversational"))

pairs.append(p(5,"efd_machine_types",
    "Je, EFD inaweza kutumika kwa biashara nyingi tofauti?",
    "Hapana — EFD moja inasajiliwa kwa biashara moja (TIN moja, eneo moja la biashara). Huwezi kutumia EFD moja kwa biashara mbili tofauti au matawi mawili tofauti. Kila tawi la biashara linahitaji EFD yake iliyosajiliwa na TRA kwa TIN na anwani ya tawi husika. Kutumia EFD moja kwa biashara nyingi kunaweza kusababisha ukaguzi na adhabu.",
    "Can one EFD be used for multiple different businesses?",
    "No — one EFD is registered for one business (one TIN, one business location). You cannot use one EFD for two different businesses or two different branches. Each business branch needs its own EFD registered with TRA under the relevant TIN and branch address. Using one EFD for multiple businesses may result in audit and penalties.",
    "formal"))

# ── EFD REGISTRATION PROCESS (pairs 6-9) ─────────────────────────────────────

pairs.append(p(6,"efd_registration",
    "Mchakato wa kupata EFD Tanzania ni upi?",
    "Kupata EFD Tanzania: (1) Kuwa na TIN na usajili wa VAT; (2) Wasiliana na muuzaji wa EFD aliyeidhinishwa na TRA (approved supplier); (3) Nunua EFD au usainiwe mkataba wa VFD; (4) Muuzaji atasajili EFD yako na TRA na kuiunganisha na seva ya TRA; (5) Pokea namba ya uzalishaji (device serial number) na uthibitisho wa usajili kutoka TRA; (6) Anza kutumia. Gharama za EFD zinabebwa na mwenye biashara.",
    "What is the EFD registration process in Tanzania?",
    "To get an EFD in Tanzania: (1) Have a TIN and VAT registration; (2) Contact a TRA-approved EFD supplier; (3) Purchase an EFD or sign a VFD agreement; (4) The supplier will register your EFD with TRA and connect it to TRA's server; (5) Receive the device serial number and registration confirmation from TRA; (6) Begin using. EFD costs are borne by the business owner.",
    "business_market"))

pairs.append(p(7,"efd_registration",
    "Je, EFD inasajiliwa na TRA au na muuzaji wa EFD?",
    "EFD inasajiliwa na muuzaji aliyeidhinishwa na TRA kwa niaba ya mwenye biashara. Muuzaji ndiye anayeshughulikia mchakato wa usajili na TRA, kuunganisha EFD kwenye seva ya TRA, na kusanidi EFD kwa TIN ya biashara. Mwenye biashara ana wajibu wa kuhakikisha EFD yake imesajiliwa ipasavyo. Baada ya usajili, risiti zote zinazotolewa zinapelekwa moja kwa moja kwenye mfumo wa TRA.",
    "Is the EFD registered with TRA or with the EFD supplier?",
    "The EFD is registered through a TRA-approved supplier on behalf of the business owner. The supplier handles the TRA registration process, connects the EFD to TRA's server, and configures the EFD with the business's TIN. The business owner has the obligation to ensure their EFD is properly registered. After registration, all issued receipts are transmitted directly to TRA's system.",
    "formal"))

pairs.append(p(8,"efd_registration",
    "Je, ninahitaji EFD mpya kwa kila bidhaa mpya ninayouza?",
    "Hapana. EFD moja inatosha kwa biashara moja bila kujali idadi ya bidhaa unazouza. EFD inaweza kusanidiwa kuonyesha aina nyingi za bidhaa na huduma. Unahitaji EFD mpya (au VFD nyingine) tu ikiwa unafungua tawi jipya au biashara mpya tofauti. Biashara moja, eneo moja = EFD moja.",
    "Do I need a new EFD for each new product I sell?",
    "No. One EFD is sufficient for one business regardless of the number of products sold. The EFD can be configured to display many types of goods and services. You only need a new EFD (or additional VFD) if you open a new branch or a completely separate business. One business, one location = one EFD.",
    "rural_conversational"))

pairs.append(p(9,"efd_registration",
    "Nini kinatokea nikisairishwa kwa EFD na TRA?",
    "Ikiwa EFD yako imesimamishwa na TRA: (1) Huwezi kutoa risiti za kisheria mpaka tatizo litatatuliwe; (2) Kufanya biashara bila EFD inayofanya kazi (kwa biashara ya VAT) ni kinyume cha sheria; (3) Wasiliana na TRA mara moja kujua sababu ya kusimamishwa; (4) Tatua tatizo (kulipa deni la kodi, kurekebisha EFD, n.k.) ili kurejesha EFD. Usiendelee kufanya biashara bila kurejesha EFD ya kisheria.",
    "What happens if my EFD is suspended by TRA?",
    "If your EFD is suspended by TRA: (1) You cannot issue legal receipts until the issue is resolved; (2) Conducting business without a functioning EFD (for a VAT business) is unlawful; (3) Contact TRA immediately to find out the reason for suspension; (4) Resolve the issue (pay tax debt, repair EFD, etc.) to restore EFD. Do not continue business without restoring a legal EFD.",
    "business_market"))

# ── EFD RECEIPT REQUIREMENTS (pairs 10-13) ───────────────────────────────────

pairs.append(p(10,"efd_receipt_requirements",
    "Risiti ya EFD lazima iwe na taarifa gani?",
    "Risiti ya EFD lazima iwe na: (1) Jina la biashara na anwani; (2) Namba ya TIN ya mwenye biashara; (3) Tarehe na saa ya muamala; (4) Maelezo ya bidhaa/huduma; (5) Bei ya kila bidhaa; (6) Jumla ya mauzo kabla ya VAT; (7) Kiasi cha VAT (kwa kiwango cha asilimia 18); (8) Jumla ya jumla ikiwa na VAT; (9) Namba ya serial ya EFD na Fiscal Receipt Number (namba ya kipekee ya risiti); (10) Msimbo wa QR (katika EFD za kisasa).",
    "What information must an EFD receipt contain?",
    "An EFD receipt must contain: (1) Business name and address; (2) Business owner's TIN; (3) Date and time of transaction; (4) Description of goods/services; (5) Price per item; (6) Total sales before VAT; (7) VAT amount (at 18%); (8) Grand total including VAT; (9) EFD serial number and Fiscal Receipt Number (unique receipt number); (10) QR code (on modern EFDs).",
    "formal"))

pairs.append(p(11,"efd_receipt_requirements",
    "Je, risiti ya EFD ni lazima itolewe kwa kila mauzo — hata TZS 1,000?",
    "Ndiyo. Kwa biashara iliyosajiliwa kwa VAT na EFD, kila muamala wa mauzo unastahili risiti ya EFD — bila kujali kiasi. Hata mauzo ya TZS 1,000 yanahitaji risiti ya EFD. Kutotoa risiti ni ukiukaji wa sheria ya VAT na EFD. TRA inaweza kufanya ukaguzi na kusimamisha EFD au kutoza adhabu kwa kutokutoa risiti.",
    "Must an EFD receipt be issued for every sale — even TZS 1,000?",
    "Yes. For a VAT-registered business with EFD, every sales transaction requires an EFD receipt — regardless of amount. Even a TZS 1,000 sale requires an EFD receipt. Failure to issue a receipt is a violation of VAT and EFD regulations. TRA may conduct inspections and suspend EFD or impose penalties for non-issuance.",
    "business_market"))

pairs.append(p(12,"efd_receipt_requirements",
    "Je, mteja anaweza kuomba risiti ya EFD kwa muamala wowote?",
    "Ndiyo. Mteja ana haki ya kupata risiti ya EFD kwa kila muamala. Biashara yenye EFD inalazimika kutoa risiti bila kusita. Ikiwa mteja hakupewa risiti, ana haki ya kulalamika kwa TRA. TRA inakusudia wanunuzi kuwa 'wakaguzi wadogo' kwa kuomba risiti — hii inasaidia kupambana na ukwepaji wa kodi.",
    "Can a customer request an EFD receipt for any transaction?",
    "Yes. A customer has the right to receive an EFD receipt for every transaction. A business with EFD is obligated to issue receipts without hesitation. If a customer is not given a receipt, they have the right to complain to TRA. TRA encourages buyers to be 'small inspectors' by requesting receipts — this helps combat tax evasion.",
    "rural_conversational"))

pairs.append(p(13,"efd_receipt_requirements",
    "Je, risiti ya karatasi ya kawaida (hand-written) inakubaliwa badala ya EFD?",
    "Hapana — biashara iliyosajiliwa kwa VAT na EFD haiwezi kutoa risiti ya mkono (hand-written) au risiti ya kawaida kama mbadala wa EFD. Risiti ya EFD ndiyo pekee inayokubaliwa kisheria. Hata hivyo, kama EFD imeharibika, TRA inaruhusu kutumia stakabadhi zilizochapishwa awali (pre-printed manual receipt book) kwa muda mfupi — na lazima urejeshe EFD haraka iwezekanavyo na utaarifiShe TRA.",
    "Is a regular hand-written receipt acceptable instead of EFD?",
    "No — a business registered for VAT with EFD cannot issue a hand-written or regular receipt as a substitute for EFD. An EFD receipt is the only legally accepted document. However, if the EFD breaks down, TRA allows the use of pre-printed manual receipt books temporarily — and you must restore the EFD as quickly as possible and notify TRA.",
    "formal"))

# ── EFD FOR SERVICE BUSINESSES (pairs 14-16) ─────────────────────────────────

pairs.append(p(14,"efd_services",
    "Biashara yangu ni ya ushauri (consultancy). Je, ninahitaji EFD?",
    "Ndiyo — ikiwa biashara yako ya ushauri imesajiliwa kwa VAT, unahitaji EFD au VFD. Biashara zote za VAT — bidhaa na huduma — zinahitaji EFD. Kwa biashara ya ushauri, VFD (Virtual Fiscal Device — programu ya kompyuta) inaweza kuwa rahisi zaidi kuliko EFD ya kimwili. Risiti ya EFD/VFD inatakiwa kwa kila invoice ya huduma uliyowasilisha. Kiwango cha VAT kwenye huduma ni asilimia 18.",
    "My business is a consultancy. Do I need an EFD?",
    "Yes — if your consultancy business is VAT-registered, you need an EFD or VFD. All VAT businesses — goods and services — require EFD. For a consultancy, a VFD (Virtual Fiscal Device — software) may be more practical than a physical EFD. An EFD/VFD receipt is required for every service invoice issued. The VAT rate on services is 18%.",
    "business_market"))

pairs.append(p(15,"efd_services",
    "Je, hata daktari au mwanasheria analazimika kutumia EFD?",
    "Ndiyo — mtaalamu yeyote aliyesajiliwa kwa VAT (daktari, mwanasheria, mhasibu, mbunifu) analazimika kutumia EFD au VFD. Sheria ya EFD haitekelezi tofauti kati ya biashara ya bidhaa na biashara ya huduma za kitaalamu. Ikiwa mauzo ya mtaalamu yanazidi kizingiti cha VAT (TZS 200M/mwaka au TZS 100M/miezi 6) na amejisajili kwa VAT, lazima atumie EFD/VFD.",
    "Are even doctors or lawyers required to use EFD?",
    "Yes — any professional registered for VAT (doctor, lawyer, accountant, architect) must use EFD or VFD. EFD law does not make a distinction between goods businesses and professional service businesses. If a professional's sales exceed the VAT threshold (TZS 200M/year or TZS 100M/6 months) and they are registered for VAT, they must use EFD/VFD.",
    "formal"))

pairs.append(p(16,"efd_services",
    "Biashara yangu inatoa huduma za usafi (cleaning services). Je, EFD inahitajika?",
    "Ndiyo — huduma za usafi zilizo na usajili wa VAT zinahitaji EFD au VFD. Sheria ya EFD inatumika kwa biashara zote za VAT bila kujali aina ya huduma. Ukisajiliwa kwa VAT, lazima utoe risiti ya EFD kwa kila muamala wa huduma. Kama mauzo yako ni chini ya kizingiti cha VAT (TZS 200M/mwaka), huhitajiwi kujisajili kwa VAT na kwa hivyo EFD haikuhusu.",
    "My business provides cleaning services. Is EFD required?",
    "Yes — cleaning services that are VAT-registered require EFD or VFD. EFD law applies to all VAT businesses regardless of service type. Once VAT-registered, you must issue an EFD receipt for every service transaction. If your sales are below the VAT threshold (TZS 200M/year), you are not required to register for VAT and therefore EFD does not apply.",
    "rural_conversational"))

# ── EFD MALFUNCTION (pairs 17-20) ────────────────────────────────────────────

pairs.append(p(17,"efd_malfunction",
    "EFD yangu imeharibika leo asubuhi. Je, ninafanya nini?",
    "Ikiwa EFD imeharibika: (1) Taarifa TRA mara moja — ndani ya masaa 24 ya kugundua uharibika; (2) Tumia stakabadhi za mkono zilizochapishwa awali (pre-printed manual receipt book) kwa muda wa kusubiri EFD kurekebishwa; (3) Wasiliana na muuzaji wa EFD aliyeidhinishwa ili arekebishe au abadilishe EFD; (4) Rekodi muamala wote uliotokea kwa stakabadhi za mkono; (5) Baada ya EFD kurekebishwa, ingiza taarifa zilizokosekana inapobidi. Usiendelee kufanya biashara bila kurejesha risiti za kisheria.",
    "My EFD broke down this morning. What do I do?",
    "If the EFD breaks down: (1) Notify TRA immediately — within 24 hours of discovering the fault; (2) Use pre-printed manual receipt books while waiting for the EFD to be repaired; (3) Contact the TRA-approved EFD supplier to repair or replace the EFD; (4) Record all transactions using manual receipts; (5) After EFD is repaired, enter any missing transaction data as required. Do not continue business without restoring legal receipt issuance.",
    "business_market"))

pairs.append(p(18,"efd_malfunction",
    "Je, ninaweza kufanya biashara bila EFD kwa siku chache hadi ifike mbadala?",
    "Kwa muda mfupi wa uharibika, unaweza kutumia stakabadhi za mkono zilizochapishwa awali (pre-printed manual receipt book) iliyoidhinishwa na TRA — hii inaruhusiwa kisheria kama njia ya dharura. Hata hivyo, lazima ufanye mambo mawili: (1) Utaarififu TRA ndani ya masaa 24; (2) Urejeshe EFD haraka iwezekanavyo. Kutumia stakabadhi za mkono bila kutaarififu TRA au kwa muda mrefu bila sababu ya kweli kunaweza kusababisha adhabu.",
    "Can I conduct business without EFD for a few days until a replacement arrives?",
    "For a short breakdown period, you may use TRA-approved pre-printed manual receipt books — this is legally permitted as an emergency measure. However, you must do two things: (1) Notify TRA within 24 hours; (2) Restore the EFD as quickly as possible. Using manual receipts without notifying TRA or for an extended period without genuine reason may result in penalties.",
    "business_market"))

pairs.append(p(19,"efd_malfunction",
    "EFD yangu imepoteza data za wiki mbili. Je, ninaweza kuziingiza tena?",
    "Upotevu wa data ya EFD ni tatizo zito. Hatua: (1) Taarifa TRA na muuzaji wa EFD haraka; (2) Angalia kama seva ya TRA (TRA server-side) ina nakala ya data — EFD za kisasa zinapeleka data mara moja na TRA inaweza kuwa na nakala; (3) Tumia rekodi za akaunti zako (bank statements, manual receipts) kurejesha taarifa; (4) Fanya marekebisho ya VAT return ikiwa inahitajika. Kutowasilisha data sahihi inaweza kusababisha tathmini ya VAT ya malimbikizo.",
    "My EFD lost two weeks of data. Can I re-enter it?",
    "Data loss from EFD is a serious matter. Steps: (1) Notify TRA and the EFD supplier immediately; (2) Check if TRA's server has a copy — modern EFDs transmit data in real time and TRA may have a backup; (3) Use your accounting records (bank statements, manual receipts) to reconstruct data; (4) Make corrections to your VAT return if needed. Failing to submit accurate data may result in backdated VAT assessments.",
    "formal"))

pairs.append(p(20,"efd_malfunction",
    "EFD yangu inachapisha risiti lakini haipeleki data TRA. Je, ninajua vipi?",
    "Dalili kwamba EFD haipeleki data TRA ni pamoja na: taa ya 'offline' au 'no connection' kwenye EFD, risiti zinazotolewa bila Fiscal Receipt Number ya mfululizo sahihi, au taarifa za makosa kwenye kiolesura cha EFD. Ukigundua EFD yako haipeleki data: (1) Angalia muunganiko wa intaneti; (2) Wasiliana na muuzaji wa EFD; (3) Taarifa TRA ndani ya masaa 24. Biashara inaweza kuendelea lakini tatizo lazima litatatuliwe haraka.",
    "My EFD is printing receipts but not transmitting data to TRA. How do I know?",
    "Signs that EFD is not transmitting data to TRA include: 'offline' or 'no connection' indicator light on the EFD, receipts issued without correct sequential Fiscal Receipt Numbers, or error messages on the EFD interface. If you discover your EFD is not transmitting: (1) Check the internet connection; (2) Contact the EFD supplier; (3) Notify TRA within 24 hours. Business may continue but the issue must be resolved quickly.",
    "business_market"))

# ── EFD AND MOBILE MONEY (pairs 21-23) ───────────────────────────────────────

pairs.append(p(21,"efd_mobile_money",
    "Mteja analipa kwa M-Pesa. Je, bado ninatoa risiti ya EFD?",
    "Ndiyo. Aina ya malipo (M-Pesa, Tigo Pesa, pesa taslimu, kadi ya benki) haiathiri wajibu wa kutoa risiti ya EFD. Kwa kila muamala wa mauzo, lazima utoe risiti ya EFD — bila kujali jinsi mteja atanavyolipa. Malipo ya simu za mkononi yanaweza kuwa na risiti ya mwenyewe (M-Pesa receipt), lakini hii haibadilishi wajibu wa EFD wako. Risiti ya EFD ni wajibu wako wa kodi — si wa mteja.",
    "A customer pays by M-Pesa. Do I still issue an EFD receipt?",
    "Yes. The payment method (M-Pesa, Tigo Pesa, cash, bank card) does not affect the obligation to issue an EFD receipt. For every sales transaction, you must issue an EFD receipt — regardless of how the customer pays. Mobile money payments may generate their own receipts (M-Pesa receipt), but this does not replace your EFD obligation. The EFD receipt is your tax obligation — not the customer's.",
    "business_market"))

pairs.append(p(22,"efd_mobile_money",
    "Je, malipo ya simu za mkononi yanahitaji risiti ya EFD tofauti au pamoja na malipo mengine?",
    "Kila muamala wa mauzo unahitaji risiti yake ya EFD — bila kujali ikiwa malipo ni ya M-Pesa, pesa taslimu, au kadi. Unaweza kuwasilisha risiti moja ya EFD kwa muamala mmoja unaojumuisha malipo ya aina mbalimbali. Hakuna haja ya risiti mbili — EFD moja inaweza kushughulikia malipo ya njia yoyote. Wajibu ni risiti moja ya EFD kwa kila muamala wa mauzo.",
    "Do mobile money payments require a separate EFD receipt or combined with other payments?",
    "Each sales transaction requires its own EFD receipt — regardless of whether payment is M-Pesa, cash, or card. You can issue one EFD receipt for one transaction involving multiple payment methods. There is no need for two receipts — one EFD can handle any payment method. The obligation is one EFD receipt per sales transaction.",
    "rural_conversational"))

pairs.append(p(23,"efd_mobile_money",
    "Mteja alinipa malipo ya M-Pesa usiku — je, ninatoa risiti kesho asubuhi?",
    "Hapana. Risiti ya EFD inapaswa kutolewa wakati wa muamala au mara baada ya kupokea malipo — si kesho. Kuchelewesha kutoa risiti kwa sababu malipo yalipokelewa usiku ni ukiukaji wa kanuni za EFD. EFD za kisasa zinaweza kutoa risiti usiku. Ikiwa EFD haikuweza kutumika usiku, tumia stakabadhi ya mkono ya dharura na uandike risiti ya EFD asubuhi ukiiingiza muamala wa usiku.",
    "A customer sent me M-Pesa payment at night — can I issue the receipt the next morning?",
    "No. An EFD receipt should be issued at the time of the transaction or immediately upon receiving payment — not the following day. Delaying receipt issuance because payment was received at night is a violation of EFD rules. Modern EFDs can issue receipts at night. If the EFD was unavailable at night, use an emergency manual receipt and issue the EFD receipt in the morning, entering the night-time transaction.",
    "business_market"))

# ── EFD MARKET VENDORS (pairs 24-27) ─────────────────────────────────────────

pairs.append(p(24,"efd_market_vendors",
    "Ninauza mboga sokoni kwa TZS 500,000 kwa mwezi. Je, ninahitaji EFD?",
    "Hapana kwa sasa. Mauzo ya TZS 500,000 kwa mwezi (TZS 6,000,000 kwa mwaka) ni mbali sana na kizingiti cha usajili wa VAT (TZS 200,000,000 kwa mwaka). Huhitajiwi kujisajili kwa VAT, na kwa hivyo EFD haikuhusu. Hata hivyo, ikiwa biashara yako itakua na mauzo yatafikia TZS 100,000,000 katika miezi 6 au TZS 200,000,000 kwa mwaka, utahitaji kusajili VAT na EFD.",
    "I sell vegetables at the market for TZS 500,000 per month. Do I need an EFD?",
    "No, not currently. Sales of TZS 500,000 per month (TZS 6,000,000 per year) are far below the VAT registration threshold (TZS 200,000,000 per year). You are not required to register for VAT, and therefore EFD does not apply to you. However, if your business grows and sales reach TZS 100,000,000 in 6 months or TZS 200,000,000 per year, you will need to register for VAT and EFD.",
    "rural_conversational"))

pairs.append(p(25,"efd_market_vendors",
    "Je, wauzaji wadogo wa soko lazima watumie EFD?",
    "Wauzaji wadogo wa soko wasiosajiliwa kwa VAT hawahitajiwi kutumia EFD. Wajibu wa EFD unafuata usajili wa VAT — na usajili wa VAT ni lazima tu pale biashara inapofika kizingiti cha TZS 200M/mwaka au TZS 100M/miezi 6. Wengi wa wauzaji wa soko wako chini ya kizingiti hiki na hawalazimiki kutumia EFD.",
    "Are small market vendors required to use EFD?",
    "Small market vendors who are not VAT-registered are not required to use EFD. The EFD obligation follows VAT registration — and VAT registration is only mandatory when a business reaches the TZS 200M/year or TZS 100M/6-month threshold. Most market vendors are below this threshold and are not required to use EFD.",
    "business_market"))

pairs.append(p(26,"efd_market_vendors",
    "Mgahawa wangu wa karibu na soko unapata TZS 250,000,000 kwa mwaka. Je, ninalazimika na EFD?",
    "Ndiyo. Mauzo ya TZS 250,000,000 kwa mwaka yanazidi kizingiti cha usajili wa VAT (TZS 200,000,000 kwa miezi 12). Lazima ujisajili kwa VAT na baada ya usajili, unahitaji EFD au VFD. Ukichelewa kusajili VAT na EFD, unaweza kukabili adhabu za malimbikizo ya VAT. Hatua: (1) Jisajili kwa VAT na TRA; (2) Pata EFD au VFD kutoka kwa muuzaji aliyeidhinishwa; (3) Anza kutoa risiti za EFD.",
    "My restaurant near the market earns TZS 250,000,000 per year. Am I required to have EFD?",
    "Yes. Sales of TZS 250,000,000 per year exceed the VAT registration threshold (TZS 200,000,000 in 12 months). You must register for VAT and after registration, you need EFD or VFD. Delaying VAT and EFD registration may result in backdated VAT penalties. Steps: (1) Register for VAT with TRA; (2) Get an EFD or VFD from an approved supplier; (3) Start issuing EFD receipts.",
    "business_market"))

pairs.append(p(27,"efd_market_vendors",
    "Je, biashara ya simu (phone credit / airtime) inahitaji EFD?",
    "Biashara ya kuuza airtime (simu za prepaid) iliyosajiliwa kwa VAT inahitaji EFD. Hata hivyo, mengi ya mawakala wa kuuza airtime (airtime resellers) wanafanya kazi kwa mfumo wa wakala ambapo wanauza bidhaa za kampuni za simu — hali yao ya VAT/EFD inategemea muundo wa biashara na mauzo ya jumla. Kama mauzo yako yanazidi kizingiti cha VAT, usajili na EFD ni lazima. Wasiliana na TRA.",
    "Does an airtime/phone credit business need an EFD?",
    "An airtime (prepaid phone credit) business that is VAT-registered requires EFD. However, many airtime resellers operate as agents selling telecom company products — their VAT/EFD status depends on business structure and total sales. If your sales exceed the VAT threshold, VAT registration and EFD are mandatory. Contact TRA for your specific situation.",
    "rural_conversational"))

# ── EFD RECEIPT REJECTION (pairs 28-30) ──────────────────────────────────────

pairs.append(p(28,"efd_receipt_rejection",
    "Mteja anakataa kupokea risiti ya EFD. Je, ninafanya nini?",
    "Hata kama mteja anakataa kupokea risiti, LAZIMA utoe risiti. Wajibu wa kutoa risiti ni wako (mwenye biashara) — si hiari ya mteja. Ikiwa mteja anakataa risiti: (1) Toa risiti na uiweke kwa akili yako; (2) Andika kwenye kumbukumbu ya biashara kwamba risiti ilikataliwa; (3) Huwezi kutoa kiasi kidogo bila risiti kwa sababu mteja amekataa. Kutotoa risiti — hata kama mteja amekataa — ni ukiukaji wa sheria ya EFD.",
    "A customer refuses to take the EFD receipt. What do I do?",
    "Even if the customer refuses to take the receipt, you MUST still issue it. The obligation to issue a receipt is yours (as business owner) — not the customer's choice. If a customer refuses the receipt: (1) Issue it and retain it yourself; (2) Note in your business records that the receipt was declined; (3) You cannot process a sale without a receipt because the customer refused. Not issuing a receipt — even if the customer refused — is a violation of EFD law.",
    "business_market"))

pairs.append(p(29,"efd_receipt_rejection",
    "Je, ninaweza kutoa punguzo (discount) kwa mteja anayekataa risiti?",
    "Hapana. Kutoa punguzo au bei tofauti kwa wateja wanaokataa risiti ni njia ya kukwepa kodi na ni kinyume cha sheria. Risiti ya EFD ni wajibu wa kisheria — si bidhaa inayoweza kutoa punguzo. Bei moja ina VAT na EFD — huwezi kutoa bei mbili: moja 'na risiti' na nyingine 'bila risiti'. TRA inaona tabia hii kama ukwepaji wa kodi.",
    "Can I give a discount to a customer who refuses the receipt?",
    "No. Offering a discount or different price to customers who refuse receipts is a form of tax evasion and is illegal. An EFD receipt is a legal obligation — not a tradable product. One price includes VAT and EFD — you cannot offer two prices: one 'with receipt' and another 'without receipt'. TRA views this behaviour as tax evasion.",
    "formal"))

pairs.append(p(30,"efd_receipt_rejection",
    "Mnunuzi wa jumla (wholesale buyer) anaomba invoice ya kawaida badala ya risiti ya EFD. Je, hii inakubalika?",
    "Invoice ya biashara (commercial invoice) inaweza kutumika pamoja na risiti ya EFD — si badala yake. Kwa mauzo ya jumla, unaweza kutoa invoice ya kawaida NA risiti ya EFD kwa muamala mmoja. Risiti ya EFD bado inahitajika kwa mauzo yote yanayotozwa VAT — hata kwa biashara ya jumla. Unaweza kusanidi EFD yako kutoa 'fiscal invoice' inayojumuisha taarifa zote za invoice na risiti ya EFD pamoja.",
    "A wholesale buyer requests a regular invoice instead of an EFD receipt. Is this acceptable?",
    "A commercial invoice can be used alongside an EFD receipt — not instead of it. For wholesale sales, you can issue a regular invoice AND an EFD receipt for one transaction. An EFD receipt is still required for all VAT-taxable sales — even for wholesale business. You can configure your EFD to issue a 'fiscal invoice' that combines all invoice information with the EFD receipt.",
    "formal"))

# ── EFD AUDIT (pairs 31-33) ───────────────────────────────────────────────────

pairs.append(p(31,"efd_audit",
    "TRA inakagua nini wakati wa ukaguzi wa EFD?",
    "Wakati wa ukaguzi wa EFD, TRA inakagua: (1) EFD imesajiliwa ipasavyo na TIN sahihi; (2) Risiti zote zinatolewa na zinapelekwa kwenye seva ya TRA; (3) Z-reports za kila siku zinatolewa na zinawasilishwa; (4) Hesabu za VAT kwenye returns zinalingana na taarifa za EFD kwenye seva ya TRA; (5) Hakuna tofauti kati ya mauzo kwenye hesabu na mauzo kwenye EFD; (6) EFD haijaharisiwa au kubadilishwa.",
    "What does TRA check during an EFD audit?",
    "During an EFD audit, TRA checks: (1) EFD is properly registered with the correct TIN; (2) All receipts are being issued and transmitted to TRA's server; (3) Daily Z-reports are generated and submitted; (4) VAT calculations on returns match EFD data on TRA's server; (5) No discrepancy between accounting sales figures and EFD sales data; (6) EFD has not been tampered with or modified.",
    "formal"))

pairs.append(p(32,"efd_audit",
    "Je, TRA inaweza kuangalia historia ya risiti zangu zote za EFD?",
    "Ndiyo. TRA ina upatikanaji wa moja kwa moja kwa seva ya TRA inayohifadhi taarifa za risiti zote za EFD ulizotoa. Kwa hivyo TRA inaweza kuangalia risiti zote za zamani, kuhesabu mauzo yako ya jumla, na kulinganisha na VAT returns ulizowahi kuwasilisha. Hii ndiyo nguvu kuu ya mfumo wa EFD — kuruhusu TRA kufanya ukaguzi wa kina bila ya lazima kuwepo ofisini kwako.",
    "Can TRA view the history of all my EFD receipts?",
    "Yes. TRA has direct access to the TRA server that stores all your EFD receipt data. Therefore TRA can view all historical receipts, calculate your total sales, and compare with VAT returns you have submitted. This is the core strength of the EFD system — allowing TRA to conduct detailed audits without necessarily being physically present at your business.",
    "business_market"))

pairs.append(p(33,"efd_audit",
    "Wakaguzi wa TRA wanaweza kuja biashara yangu lini?",
    "TRA inspectors wana haki ya kutembelea biashara yoyote wakati wowote wa saa za kazi (business hours) — bila tangazo la mapema (without prior notice) kwa ukaguzi wa EFD na kodi. Wanaweza kuangalia EFD yako, kuomba Z-reports, na kukagua rekodi za akaunti. Kama unafanya biashara kwa kanuni, ukaguzi haupaswi kukuumiza. Uhifadhi bora wa rekodi na matumizi sahihi ya EFD ndiyo ulinzi bora.",
    "When can TRA inspectors visit my business?",
    "TRA inspectors have the right to visit any business at any time during business hours — without prior notice — for EFD and tax inspections. They can inspect your EFD, request Z-reports, and review accounting records. If you operate by the rules, an inspection should not cause you problems. Good record keeping and proper EFD use is the best protection.",
    "rural_conversational"))

# ── EFD PENALTIES (pairs 34-37) ──────────────────────────────────────────────

pairs.append(p(34,"efd_penalties",
    "Adhabu ya kutotumia EFD Tanzania ni nini?",
    "Kutotumia EFD kwa biashara iliyosajiliwa kwa VAT kunaweza kusababisha: adhabu ya kutotoa risiti kwa kila muamala uliokosekana, kusimamishwa kwa leseni ya biashara, kusimamishwa kwa usajili wa VAT, tathmini ya VAT ya malimbikizo kwa kipindi chote, na adhabu za ziada za kodi. TRA inaweza pia kuwasilisha kesi ya jinai kwa ukwepaji wa kodi unaoendelea. Mfumo wa EFD ulioundwa kuzuia ukwepaji — adhabu zake ni kali.",
    "What are the penalties for not using EFD in Tanzania?",
    "Failure to use EFD for a VAT-registered business may result in: penalties per missed receipt transaction, suspension of business licence, suspension of VAT registration, backdated VAT assessments for the entire period, and additional tax penalties. TRA may also file criminal charges for ongoing tax evasion. The EFD system was designed to prevent evasion — its penalties are severe.",
    "formal"))

pairs.append(p(35,"efd_penalties",
    "Adhabu ya kutotoa risiti kwa mteja moja ni kiasi gani?",
    "Kiwango cha adhabu halisi kwa kila risiti isiyotolewa kinatoka kwenye Sheria ya Kodi ya Ongezeko la Thamani na Kanuni za EFD — ambayo yanaweza kubadilika. Kwa ujumla, adhabu zinatoka katika maeneo mawili: adhabu ya kila muamala na adhabu ya siku. TRA inaweza kutoza kiasi kikubwa kwa biashara zinazoonekana kukwepa makusudi. Kwa kiwango halisi cha sasa cha adhabu, angalia sheria za sasa za TRA kwenye tra.go.tz.",
    "What is the fine for not issuing a receipt to one customer?",
    "The exact penalty amount per missing receipt comes from the VAT Act and EFD Regulations — which may change. Generally, penalties come from two areas: per-transaction penalties and daily penalties. TRA may impose substantial amounts for businesses found to be deliberately evading. For the current exact penalty amounts, check the current TRA regulations at tra.go.tz.",
    "business_market"))

pairs.append(p(36,"efd_penalties",
    "Je, ninaweza kulalamika kwa TRA dhidi ya adhabu ya EFD isiyokuwa ya haki?",
    "Ndiyo. Ikiwa unaamini adhabu ya EFD au tathmini ya TRA si sahihi, una haki ya kulalamika (objection) na TRA ndani ya siku 30 za kupokea tathmini. Mchakato ni: (1) Wasilisha barua ya hiari ya kukataa tathmini (Notice of Objection) ndani ya siku 30; (2) Lipa kiasi kisichopingwa AU theluthi moja ya kiasi kilichotathminiwa ndani ya siku 15; (3) Subiri uamuzi wa Kamishna ndani ya miezi 6; (4) Kama bado haujaridhika, piga rufaa kwa TRAB.",
    "Can I complain to TRA against an unfair EFD penalty?",
    "Yes. If you believe a TRA EFD penalty or assessment is incorrect, you have the right to file an objection with TRA within 30 days of receiving the assessment. Process: (1) Submit a Notice of Objection within 30 days; (2) Pay the undisputed amount OR one-third of the assessed amount within 15 days; (3) Await the Commissioner's decision within 6 months; (4) If still unsatisfied, appeal to TRAB.",
    "formal"))

pairs.append(p(37,"efd_penalties",
    "Je, ukaguzi wa EFD unaweza kusababisha uchunguzi wa jumla wa kodi za biashara yangu?",
    "Ndiyo. Ukaguzi wa EFD unaonyesha tofauti kati ya taarifa za EFD na VAT returns unaweza kuanzisha uchunguzi wa kina zaidi wa kodi zote za biashara — PAYE, SDL, kodi ya mapato ya shirika, na nyingine. TRA inaweza kutumia taarifa za EFD kama 'mlango wa kuingia' wa ukaguzi mpana zaidi. Hii ni sababu nyingine ya kutunza rekodi sahihi na kutumia EFD ipasavyo.",
    "Can an EFD audit trigger a full tax investigation of my business?",
    "Yes. An EFD audit that reveals discrepancies between EFD data and VAT returns may trigger a broader investigation of all business taxes — PAYE, SDL, corporate income tax, and others. TRA can use EFD data as a 'gateway' into a wider audit. This is another reason to maintain accurate records and use EFD properly.",
    "business_market"))

# ── EFD AND VAT (pairs 38-40) ─────────────────────────────────────────────────

pairs.append(p(38,"efd_and_vat",
    "Uhusiano kati ya EFD na VAT ni nini?",
    "EFD ni chombo cha utekelezaji wa VAT. Biashara iliyosajiliwa kwa VAT inatozea wateja VAT ya asilimia 18 kwenye kila muamala — na risiti ya EFD ndiyo hati rasmi inayoonyesha VAT hiyo. Bila EFD, hakuna uthibitisho wa kisheria wa VAT. Seva ya TRA inakusanya taarifa za EFD na TRA inazitumia kulinganisha na VAT returns. EFD + VAT return + malipo ya VAT ndio 'mzunguko kamili' wa wajibu wa VAT.",
    "What is the relationship between EFD and VAT?",
    "EFD is the enforcement tool for VAT. A VAT-registered business charges customers 18% VAT on every transaction — and the EFD receipt is the official document evidencing that VAT. Without EFD, there is no official proof of VAT. TRA's server collects EFD data and TRA uses it to verify against VAT returns. EFD + VAT return + VAT payment is the 'complete cycle' of VAT obligation.",
    "formal"))

pairs.append(p(39,"efd_and_vat",
    "Je, biashara inayotoa risiti za EFD lazima iwasilishe VAT return pia?",
    "Ndiyo. Risiti ya EFD na VAT return ni wajibu tofauti mbili: (1) Risiti za EFD: zinatoka kwa kila muamala wakati unaotokea; (2) VAT return: inawasilishwa kila mwezi, mwisho wa tarehe 20, na inajumuisha malipo ya VAT inayodaiwa. Kutoa risiti za EFD bila kuwasilisha VAT return ni ukiukaji wa wajibu wa kodi. Seva ya TRA inaweza kuona biashara zinazotoa risiti lakini hazisailishi returns — hizi zinakuwa lengwa la ukaguzi.",
    "Must a business issuing EFD receipts also submit VAT returns?",
    "Yes. EFD receipts and VAT returns are two separate obligations: (1) EFD receipts: issued for every transaction as it occurs; (2) VAT return: submitted monthly, by the 20th, and includes the VAT payment owed. Issuing EFD receipts without submitting VAT returns is a tax compliance violation. TRA's server can identify businesses issuing receipts but not filing returns — these become audit targets.",
    "business_market"))

pairs.append(p(40,"efd_and_vat",
    "Je, EFD inatoa taarifa za input VAT pia?",
    "EFD ya biashara yako inaandika OUTPUT VAT (VAT unayokusanya kutoka kwa wateja). INPUT VAT (VAT unayolipa kwa manunuzi wako) inajumuishwa kwenye VAT return yako kwa msingi wa invoices/risiti za EFD ulizopokea kutoka kwa wasambazaji wako walioidhinishwa. Tofauti kati ya output VAT na input VAT ndiyo inayolipwa TRA au kurejeshwa kwako (refund). EFD yako inahusika na output VAT tu.",
    "Does EFD also record input VAT?",
    "Your business's EFD records OUTPUT VAT (VAT you collect from customers). INPUT VAT (VAT you pay to your suppliers) is included in your VAT return based on EFD receipts/invoices you receive from your approved suppliers. The difference between output VAT and input VAT is what gets paid to TRA or refunded to you. Your EFD is concerned with output VAT only.",
    "formal"))

# ── EFD Z-REPORT (pairs 41-43) ───────────────────────────────────────────────

pairs.append(p(41,"efd_z_report",
    "Z-report ya EFD ni nini na inahitajika kila siku?",
    "Z-report (au Z-reading) ni taarifa ya mwisho wa siku inayotolewa na EFD baada ya shughuli za biashara kuisha. Inaonyesha: jumla ya mauzo ya siku, jumla ya VAT iliyokusanywa, na namba ya risiti za kwanza na za mwisho za siku. Z-report lazima itolewe kila siku ya biashara na kupelekwa kwenye seva ya TRA. Kutotoa Z-report ni ukiukaji wa kanuni za EFD.",
    "What is a Z-report on EFD and is it required daily?",
    "A Z-report (or Z-reading) is the end-of-day report generated by the EFD after business activity closes. It shows: total daily sales, total VAT collected, and the first and last receipt numbers of the day. A Z-report must be generated every business day and transmitted to TRA's server. Failure to generate a Z-report is a violation of EFD regulations.",
    "business_market"))

pairs.append(p(42,"efd_z_report",
    "Je, siku nisiyofanya biashara bado ninahitaji Z-report?",
    "Kama EFD iko hai (powered on) na ulikuwa umefungua na kufunga biashara hiyo siku — hata hakukuwa na muamala — Z-report bado inashauriwa kutolewa. Hata hivyo, ikiwa biashara ilifungwa kabisa (EFD ilizimwa) na hakukuwa na biashara yoyote, Z-report ya siku ile inaweza kuwa haina taarifa za muamala. Wasiliana na muuzaji wa EFD wako kwa mwongozo wa jinsi ya kushughulikia siku za biashara iliyofungwa.",
    "On a day when I do no business, do I still need a Z-report?",
    "If the EFD is powered on and you technically opened and closed business that day — even with no transactions — a Z-report is still advisable to generate. However, if the business was fully closed (EFD powered off) with no transactions at all, the Z-report for that day may have no transaction data. Consult your EFD supplier for guidance on handling days when business is fully closed.",
    "rural_conversational"))

pairs.append(p(43,"efd_z_report",
    "Z-report lazima ipigwe wakati gani — usiku au asubuhi?",
    "Z-report inatolewa MWISHONI MWA SIKU ya biashara — kabla EFD haijazimwa kwa usiku. Si asubuhi ya siku inayofuata. Utaratibu wa kawaida: (1) Funga mauzo ya mwisho wa siku; (2) Toa Z-report; (3) Hakikisha Z-report imepelekwa seva ya TRA; (4) Zima au acha EFD. Kutoa Z-report asubuhi ya siku inayofuata kunaweza kusababisha tatizo la data — muamala wa siku moja unaweza kuonekana kwenye siku nyingine.",
    "When must the Z-report be generated — evening or morning?",
    "The Z-report must be generated at the END OF THE BUSINESS DAY — before powering off the EFD for the night. Not in the morning of the following day. Normal procedure: (1) Complete the last sale of the day; (2) Generate Z-report; (3) Confirm Z-report has been transmitted to TRA server; (4) Shut down or leave EFD. Generating a Z-report in the morning of the following day may cause data problems — a day's transactions may appear under a different date.",
    "business_market"))

# ── EFD MULTIPLE BRANCHES (pairs 44-47) ──────────────────────────────────────

pairs.append(p(44,"efd_multiple_branches",
    "Kampuni yangu ina matawi matatu Dar es Salaam. Je, kila tawi linahitaji EFD yake?",
    "Ndiyo. Kila tawi la biashara linahitaji EFD iliyosajiliwa yake — moja kwa moja na TRA na inayoonyesha jina la tawi na anwani yake. Huwezi kutumia EFD moja kwa matawi matatu. Kila tawi linatoa risiti zake tofauti na kupeleka taarifa zake tofauti kwa seva ya TRA. VAT returns zinaweza kuwasilishwa kwa pamoja (consolidated) ikiwa TRA inaruhusu, lakini EFD za kimwili lazima ziwe tofauti kwa kila tawi.",
    "My company has three branches in Dar es Salaam. Does each branch need its own EFD?",
    "Yes. Each business branch requires its own registered EFD — individually registered with TRA showing the branch name and address. You cannot use one EFD for three branches. Each branch issues its own receipts and transmits its own data to TRA's server. VAT returns may be submitted consolidated if TRA permits, but physical EFDs must be separate for each branch.",
    "formal"))

pairs.append(p(45,"efd_multiple_branches",
    "Kama tawi moja linaharibika EFD, je matawi mengine yanaendelea kufanya biashara?",
    "Ndiyo. EFD ya kila tawi inafanya kazi kwa kujitegemea — uharibika wa EFD ya tawi moja haukuathiri matawi mengine. Tawi lenye EFD iliyoharibika linapaswa: (1) Kutaarififu TRA ndani ya masaa 24; (2) Kutumia stakabadhi za mkono kwa muda; (3) Kurekebisha EFD haraka. Matawi mengine yanaendelea kwa kawaida.",
    "If one branch's EFD breaks down, do other branches continue operating?",
    "Yes. Each branch's EFD operates independently — a breakdown at one branch does not affect other branches. The branch with the broken EFD must: (1) Notify TRA within 24 hours; (2) Use manual receipts temporarily; (3) Repair the EFD quickly. Other branches continue operating normally.",
    "business_market"))

pairs.append(p(46,"efd_multiple_branches",
    "Je, ninaweza kutumia EFD moja kwa biashara yangu ya jumla na biashara ya rejareja tofauti?",
    "Hapana — EFD moja inasajiliwa kwa TIN moja na eneo moja la biashara. Biashara ya jumla (wholesale) na ya rejareja (retail) zinazofanya kazi kama biashara tofauti (TIN tofauti) zinahitaji EFD tofauti. Hata kama TIN ni moja, ikiwa mauzo yanafanyika maeneo tofauti (anwani tofauti), kila eneo linahitaji EFD yake. Wasiliana na TRA kwa hali yako maalum.",
    "Can I use one EFD for my separate wholesale and retail businesses?",
    "No — one EFD is registered to one TIN and one business location. Wholesale and retail businesses operating as separate businesses (different TINs) need separate EFDs. Even with one TIN, if sales occur at different locations (different addresses), each location needs its own EFD. Contact TRA for your specific situation.",
    "formal"))

pairs.append(p(47,"efd_multiple_branches",
    "Kampuni ina headquarters na tawi moja. Je, VAT return inawasilishwa kwa kila tawi au kwa pamoja?",
    "Kwa ujumla, kampuni yenye TIN moja ina VAT return moja inayojumuisha taarifa za biashara zote — vikoa vyote na matawi yote. Hata hivyo, kwa vitendo, kila tawi linaweza kuwa na EFD yake tofauti inayopeleka taarifa za mauzo kwa seva ya TRA. TRA inajumuisha taarifa hizi kwa TIN moja kwenye mfumo wake. Wasiliana na TRA kwa mwongozo wa jinsi ya kuwasilisha VAT return kwa kampuni yenye matawi mengi.",
    "A company has headquarters and one branch. Is VAT return submitted per branch or combined?",
    "Generally, a company with one TIN has one VAT return covering all business activity — all locations and branches. However, in practice, each branch may have its own EFD that separately transmits sales data to TRA's server. TRA aggregates these under one TIN in its system. Contact TRA for guidance on submitting VAT returns for a multi-branch company.",
    "business_market"))

# ── EFD ONLINE BUSINESSES (pairs 48-50) ──────────────────────────────────────

pairs.append(p(48,"efd_online",
    "Ninaendesha duka la mtandaoni. Je, VFD inatumika badala ya EFD ya kimwili?",
    "Ndiyo. Biashara za mtandaoni zilizosajiliwa kwa VAT zinatumia VFD (Virtual Fiscal Device) — programu inayofanya kazi ya EFD bila kifaa cha kimwili. VFD inatolewa na watoa huduma walioidhinishwa na TRA. Kwa kila muamala wa mauzo ya mtandaoni, VFD inazalisha risiti ya kidijitali inayopelekwa kwa mteja na wakati huo huo inayo taarifa inayowasilishwa seva ya TRA.",
    "I run an online shop. Does VFD replace the physical EFD?",
    "Yes. Online businesses registered for VAT use VFD (Virtual Fiscal Device) — software that performs the EFD function without a physical device. VFD is provided by TRA-approved service providers. For each online sales transaction, the VFD generates a digital receipt that is sent to the customer and simultaneously transmits data to TRA's server.",
    "business_market"))

pairs.append(p(49,"efd_online",
    "Je, biashara ya mtandaoni ya Tanzania inayouza kwa wateja nje ya Tanzania inahitaji EFD?",
    "Mauzo ya nje ya Tanzania (exports) kwa wateja wa nje ya nchi yanaweza kuwa zero-rated kwa VAT — yaani VAT ya asilimia 0. Hata hivyo, biashara bado inahitaji kuandika muamala huu kwenye mfumo wake wa VAT na EFD/VFD. Taarifa za muamala wa zero-rated bado zinapelekwa TRA kupitia VFD. Risiti/invoice inatolewa kwa mteja wa nje — kwa kiwango cha asilimia 0 — na inawasilishwa kwenye VAT return kama mauzo ya zero-rated.",
    "Does a Tanzanian online business selling to customers outside Tanzania need EFD?",
    "Sales outside Tanzania (exports) to foreign customers may be zero-rated for VAT — meaning 0% VAT. However, the business still needs to record these transactions in its VAT and EFD/VFD system. Zero-rated transaction data is still transmitted to TRA through the VFD. A receipt/invoice is issued to the foreign customer — at 0% — and reported on the VAT return as zero-rated sales.",
    "formal"))

pairs.append(p(50,"efd_online",
    "Ninatoa huduma za ushauri wa mtandaoni kwa wateja wa Tanzania. Je, VFD inahitajika?",
    "Ndiyo — ikiwa mauzo yako ya huduma za ushauri wa mtandaoni yanazidi kizingiti cha VAT (TZS 200M/mwaka au TZS 100M/miezi 6) na umesajiliwa kwa VAT, unahitaji VFD. VFD itazalisha risiti ya kidijitali kwa kila muamala wa huduma, itapeleka taarifa kwa seva ya TRA, na itakusaidia kutunza rekodi za VAT sahihi. Kiwango cha VAT kwenye huduma za ushauri ni asilimia 18.",
    "I provide online consultancy services to Tanzanian clients. Is VFD required?",
    "Yes — if your online consultancy sales exceed the VAT threshold (TZS 200M/year or TZS 100M/6 months) and you are VAT-registered, you need a VFD. The VFD will generate a digital receipt for each service transaction, transmit data to TRA's server, and help you maintain accurate VAT records. The VAT rate on consultancy services is 18%.",
    "rural_conversational"))

# ── WRITE ──────────────────────────────────────────────────────────────────────
OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl"
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
print(f"Wrote {len(pairs)} EFD deep pairs")
regs = {}
for pr in pairs:
    regs[pr["register"]] = regs.get(pr["register"], 0) + 1
total = len(pairs)
for k, v in sorted(regs.items()):
    print(f"  {k}: {v} ({v/total*100:.0f}%)")

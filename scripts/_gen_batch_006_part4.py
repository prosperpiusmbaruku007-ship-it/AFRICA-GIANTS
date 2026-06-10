#!/usr/bin/env python3
"""
batch_006 part 4: vat_refund_deep — 50 pairs
IDs: b006_vat_ref_001 – b006_vat_ref_050
Source: TRA VAT page (government_portal)
Append to: datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl
"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl"
SRC = "https://www.tra.go.tz/page/value-added-tax"
NAME = "TRA - Value Added Tax"
REVIEW = "Finance Act amendment or TRA VAT refund procedure update"

def p(id_, q_sw, a_sw, q_en, a_en, register, pair_type):
    return {
        "id": id_,
        "domain": "tier1a",
        "subdomain": "vat_refund_deep",
        "question_sw": q_sw,
        "answer_sw": a_sw,
        "question_en": q_en,
        "answer_en": a_en,
        "primary_source_url": SRC,
        "primary_source_name": NAME,
        "source_type": "government_portal",
        "effective_date": "2025-07-01",
        "decay_risk": "annual",
        "next_review_trigger": REVIEW,
        "verified_by": "founder_self_review",
        "verified_date": "2026-06-10",
        "register": register,
        "pair_type": pair_type,
        "eval_set": False
    }

pairs = [

# --- Group 1: Input vs Output VAT concepts ---

p("b006_vat_ref_001",
  "Input VAT na Output VAT — tofauti yao nini?",
  "Output VAT: VAT unayokusanya kutoka kwa wateja wako unapowauzia bidhaa/huduma — inakwenda TRA. Input VAT: VAT unayolipa kwa wanaokulaz bidhaa/huduma — inaweza kupunguzwa kutoka output VAT yako. Net VAT = Output VAT - Input VAT. Kama output > input, unatuma tofauti TRA. Kama input > output, una 'VAT credit' ambayo unaweza kubeba au kudai kama refund.",
  "Input VAT and Output VAT — what is the difference?",
  "Output VAT: VAT you collect from your customers when you sell goods/services — it goes to TRA. Input VAT: VAT you pay to your suppliers — it can be deducted from your output VAT. Net VAT = Output VAT - Input VAT. If output > input, you remit the difference to TRA. If input > output, you have a 'VAT credit' which you can carry forward or claim as a refund.",
  "formal", "standard"),

p("b006_vat_ref_002",
  "Wakati gani mfanyabiashara anapata haki ya kudai refund ya VAT?",
  "Haki ya kudai refund ya VAT inatokea wakati INPUT VAT inazidi OUTPUT VAT kwa kipindi cha uwasilishaji (mwezi au robo mwaka). Hali hii mara nyingi hutokea kwa: (1) Wauza bidhaa nje ya nchi (exporters) — mauzo yao yana VAT 0% lakini wananunua bidhaa na VAT ya kawaida; (2) Biashara mpya inayonunua vifaa vingi kabla ya kuanza mauzo; (3) Biashara inayonunua mali ghali (kama mashine) na VAT kubwa ya awali.",
  "When does a business become entitled to claim a VAT refund?",
  "Entitlement to a VAT refund arises when INPUT VAT exceeds OUTPUT VAT for a filing period (monthly or quarterly). This commonly happens for: (1) Exporters — their sales carry 0% VAT but they buy goods with regular VAT; (2) New businesses buying a lot of equipment before sales start; (3) Businesses buying expensive assets (like machinery) with a large upfront VAT.",
  "formal", "standard"),

p("b006_vat_ref_003",
  "Je, kila mfanyabiashara aliyesajiliwa VAT anaweza kudai refund?",
  "Ndiyo — mfanyabiashara YEYOTE aliyesajiliwa VAT ambaye ana ziada ya input VAT juu ya output VAT ana haki ya kudai refund. Hii si haki maalum kwa makampuni makubwa peke yake. Biashara ndogo pia zinaweza kudai kama zinaonyesha input VAT inayostahili iliyolipwa.",
  "Can every VAT-registered business claim a refund?",
  "Yes — ANY VAT-registered business that has excess input VAT over output VAT is entitled to claim a refund. This is not a special right for large companies alone. Small businesses can also claim if they demonstrate eligible paid input VAT.",
  "formal", "standard"),

p("b006_vat_ref_004",
  "Biashara yangu haisajiliwa kwa VAT — ninaweza kudai refund ya VAT nililolipa kwa wanaokulaz?",
  "Hapana. Haki ya kudai input VAT inahitaji usajili wa VAT. Biashara isiyosajiliwa haiwezi kudai input VAT iliyolipwa kwa wanaokulaz. Hii ni sababu moja ya kwa nini kusajiliwa VAT na kununua kutoka wasambazaji waliosajilistwaa VAT ni muhimu kwa biashara zinazosajiliwa.",
  "My business is not VAT-registered — can I claim back the VAT I paid to my suppliers?",
  "No. The right to claim input VAT requires VAT registration. An unregistered business cannot claim back the VAT it paid to suppliers. This is one reason why VAT registration and buying from VAT-registered suppliers matters for registered businesses.",
  "formal", "standard"),

p("b006_vat_ref_005",
  "Input VAT inaweza kudaiwa kwa ununuzi wa bidhaa na huduma zote?",
  "Hapana. Si input VAT yote inaweza kudaiwa. Kwa ujumla, input VAT inayodaiwa lazima iwe kwa ununuzi wa biashara tu — si matumizi ya kibinafsi. Ununuzi wa gari la kibinafsi, chakula cha kibinafsi, au matumizi yasiyohusiana na biashara haustahili input VAT credit. TRA inaweza kukataa madai ya input VAT yasiyokuwa ya biashara.",
  "Can input VAT be claimed on all purchases of goods and services?",
  "No. Not all input VAT can be claimed. Generally, claimable input VAT must relate to business purchases only — not personal use. Purchasing a personal car, personal food, or expenses unrelated to business do not qualify for input VAT credit. TRA can reject input VAT claims not related to business.",
  "formal", "standard"),

# --- Group 2: Exporters and zero-rated supplies ---

p("b006_vat_ref_006",
  "Msambazaji wa nje ya nchi (exporter) anaweza kudai refund ya VAT — kwa nini?",
  "Exports (mauzo nje ya nchi) zinabeba kiwango cha VAT cha 0% (zero-rated). Hii inamaanisha exporter hakusanyi VAT kutoka kwa wateja wake wa nje — output VAT = 0. Lakini exporter bado ananunua bidhaa/huduma Tanzania na kulipa input VAT ya kawaida (18%). Kwa hivyo input VAT > output VAT, na exporter ana haki ya kudai refund ya input VAT iliyolipwa.",
  "An exporter can claim a VAT refund — why?",
  "Exports carry a 0% VAT rate (zero-rated). This means the exporter does not collect VAT from foreign customers — output VAT = 0. But the exporter still buys goods/services in Tanzania and pays regular input VAT (18%). Therefore input VAT > output VAT, and the exporter is entitled to claim a refund of the input VAT paid.",
  "formal", "standard"),

p("b006_vat_ref_007",
  "Bidhaa zangu zinaenda Kenya — VAT inahesabiwa kwa kiwango cha ngapi?",
  "Mauzo ya bidhaa nje ya Tanzania (exports) yanabeba kiwango cha VAT cha 0% (zero-rated). Hii inamaanisha haukusanyi VAT kutoka kwa mnunuzi wa Kenya. Hata hivyo, ununuzi wako wa bidhaa hizo ndani ya Tanzania ulibeba input VAT ya 18% — ambayo unaweza kudai refund yake baadaye.",
  "My goods are going to Kenya — what VAT rate is applied?",
  "Sales of goods outside Tanzania (exports) carry a 0% VAT rate (zero-rated). This means you do not collect VAT from the Kenyan buyer. However, your purchase of those goods within Tanzania carried 18% input VAT — which you can claim back as a refund.",
  "business_market", "standard"),

p("b006_vat_ref_008",
  "Je, mauzo ya huduma nje ya nchi yana VAT 0% kama bidhaa?",
  "Ndiyo kwa ujumla — huduma zinazotolewa kwa wateja nje ya Tanzania kwa matumizi nje (exported services) zinaweza kustahili kiwango cha 0%. Hata hivyo, kanuni za 'place of supply' ni ngumu — kama huduma inatumika Tanzania hata kama mlipaji yuko nje, VAT ya kawaida inaweza kutumika. Thibitisha muundo wako maalum na mshauri wa kodi.",
  "Do exported services also carry 0% VAT like goods?",
  "Generally yes — services supplied to customers outside Tanzania for use outside (exported services) may qualify for the 0% rate. However, the rules on 'place of supply' are complex — if a service is used in Tanzania even if the payer is abroad, regular VAT may apply. Confirm your specific structure with a tax advisor.",
  "formal", "disambiguation"),

p("b006_vat_ref_009",
  "Kampuni ya usafirishaji inayopeleka bidhaa Kenya — VAT yake ya mafuta ya gari inastahili refund?",
  "Inategemea muundo wa biashara. Kama kampuni ya usafirishaji imesajiliwa VAT na inafanya huduma za zero-rated (usafirishaji wa nje ya nchi), input VAT ya mafuta (kama ilinunuliwa kutoka msambazaji aliyesajiliwa VAT na kupata risiti ya EFD) inaweza kudaiwa kama input VAT. Thibitisha muundo wako na mshauri wa kodi au TRA.",
  "A transport company carrying goods to Kenya — does the VAT on its diesel qualify for refund?",
  "It depends on the business structure. If the transport company is VAT-registered and performs zero-rated services (international transport), input VAT on fuel (if purchased from a VAT-registered supplier with an EFD receipt) may be claimable as input VAT. Confirm your structure with a tax advisor or TRA.",
  "formal", "disambiguation"),

p("b006_vat_ref_010",
  "Je, mauzo ya bidhaa ndogo ndogo kwa watembezi wa kigeni (tourists) yana VAT 0%?",
  "Kwa kawaida, mauzo ya rejareja kwa watembezi (watu binafsi) ndani ya Tanzania yanabeba VAT ya kawaida (18%) hata kama mnunuzi ni mgeni. Mauzo ya zero-rated yanategemea bidhaa kuondoka Tanzania rasmi (export) — si ununuzi wa kibinafsi wa mtalii. Tanzania ina mfumo wa VAT refund kwa watalii (tourist VAT refund) lakini masharti yake maalum yanahitaji kuthibitishwa na TRA.",
  "Do small sales to foreign tourists carry 0% VAT?",
  "Generally, retail sales to tourists (individuals) within Tanzania carry regular VAT (18%) even if the buyer is foreign. Zero-rated sales depend on goods physically leaving Tanzania officially (export) — not a tourist's personal purchase. Tanzania has a tourist VAT refund scheme but its specific conditions need to be verified with TRA.",
  "formal", "disambiguation"),

# --- Group 3: Application process ---

p("b006_vat_ref_011",
  "Mchakato wa kudai refund ya VAT TRA ni upi?",
  "Kwa ujumla, mchakato wa kudai refund ya VAT ni: (1) Jaza VAT return ya kawaida ikionyesha net input VAT credit; (2) Omba refund rasmi kwa TRA ukiambatisha hati za kuunga mkono; (3) TRA inafanya ukaguzi na uthibitishaji wa madai; (4) Ikiwa madai yanakubaliwa, TRA inalipa refund (au inatoa credit dhidi ya VAT ya baadaye). Jaza VAT return ya kila mwezi kwa usahihi ili kudai.",
  "What is the TRA process for claiming a VAT refund?",
  "Generally, the VAT refund process is: (1) File the regular VAT return showing a net input VAT credit; (2) Submit a formal refund application to TRA with supporting documents; (3) TRA conducts verification and audit of claims; (4) If claims are approved, TRA pays the refund (or applies it as credit against future VAT). File monthly VAT returns accurately to build your claim.",
  "formal", "standard"),

p("b006_vat_ref_012",
  "Hati gani zinahitajika kudai refund ya VAT?",
  "Hati za kawaida zinazohitajika kudai VAT refund ni pamoja na: (1) Nakala za VAT invoices za ununuzi (zilizotolewa na wasambazaji waliosajilistwaa VAT); (2) Risiti za EFD (Electronic Fiscal Device) zinazohusiana; (3) Hati za mauzo (invoices za output VAT); (4) Kwa exporters: hati za usafirishaji nje (export documents) kama custom entries, bills of lading; (5) Rejista ya VAT iliyosasishwa. Hati zote lazima ziwe halali na kuthibitishwa.",
  "What documents are needed to claim a VAT refund?",
  "Documents typically required for a VAT refund claim include: (1) Copies of purchase VAT invoices (issued by VAT-registered suppliers); (2) Related EFD (Electronic Fiscal Device) receipts; (3) Sales documents (output VAT invoices); (4) For exporters: export documents such as customs entries, bills of lading; (5) Updated VAT register. All documents must be genuine and verifiable.",
  "formal", "standard"),

p("b006_vat_ref_013",
  "Risiti ya EFD inahitajika kudai input VAT — au invoice ya kawaida inatosha?",
  "Kwa madai ya input VAT, TRA mara nyingi inahitaji RISITI YA EFD au invoice ya VAT iliyotolewa na msambazaji aliyesajiliwa VAT. Invoice ya kawaida (isiyo ya EFD) peke yake inaweza kutokuwa ya kutosha kudai input VAT. Nunua kutoka wasambazaji waliosajilistwaa VAT wanaotoa risiti za EFD ili kuhifadhi haki yako ya kudai input VAT.",
  "Is an EFD receipt required to claim input VAT — or is a regular invoice sufficient?",
  "For input VAT claims, TRA typically requires an EFD RECEIPT or a VAT invoice issued by a VAT-registered supplier. A regular invoice (non-EFD) alone may not be sufficient to claim input VAT. Buy from VAT-registered suppliers who issue EFD receipts to preserve your right to claim input VAT.",
  "business_market", "adversarial"),

p("b006_vat_ref_014",
  "Je, kununua kutoka msambazaji asiyesajiliwa VAT kunaathiri haki yangu ya kudai input VAT?",
  "Ndiyo. Kununua kutoka msambazaji asiyesajiliwa VAT kunamaanisha hakuna VAT ya kisheria iliyotozwa kwenye ununuzi huo — hivyo hakuna input VAT ya kudai. Hata kama bei ya msambazaji huyo ni ya juu, hutapata input VAT credit. Kwa madhumuni ya VAT, kununua kutoka wasambazaji waliosajilistwaa VAT ni muhimu.",
  "Does buying from a non-VAT-registered supplier affect my right to claim input VAT?",
  "Yes. Buying from a non-VAT-registered supplier means no legitimate VAT was charged on that purchase — so there is no input VAT to claim. Even if that supplier charges a higher price, you will not get an input VAT credit. For VAT purposes, buying from VAT-registered suppliers is important.",
  "formal", "standard"),

p("b006_vat_ref_015",
  "Je, ninaweza kudai input VAT ya miaka iliyopita ambayo haikudaiwa wakati wake?",
  "Kuna ukomo wa muda (time limit) wa kudai input VAT. Tanzania inatumia ukomo wa miaka 3 kwa marekebisho ya kodi kwa ujumla. Input VAT isiyodaiwa baada ya ukomo huu inaweza kupotea. Thibitisha ukomo halisi wa sasa na TRA au mshauri wa kodi — na jaribu kudai input VAT kwa wakati wake kila mwezi.",
  "Can I claim input VAT from past years that was not claimed at the time?",
  "There is a time limit for claiming input VAT. Tanzania generally applies a 3-year limit for tax amendments. Unclaimed input VAT after this limit may be forfeited. Confirm the current exact limit with TRA or a tax advisor — and try to claim input VAT on time each month.",
  "formal", "standard"),

# --- Group 4: VAT credit vs VAT refund ---

p("b006_vat_ref_016",
  "VAT credit na VAT refund — ni tofauti gani?",
  "VAT CREDIT (kubeba mbele): Badala ya kudai pesa moja kwa moja, VAT credit inabebwa mbele na kutumika kupunguza VAT ya mwezi unaofuata. VAT REFUND (pesa moja kwa moja): Omba TRA ikusanyie kiasi cha credit kwa pesa taslimu. Wengi hupendelea credit kwa sababu ni haraka zaidi — refund ya pesa inahitaji ukaguzi wa TRA ambao unachukua muda.",
  "VAT credit and VAT refund — what is the difference?",
  "VAT CREDIT (carry forward): Instead of claiming cash directly, the VAT credit is carried forward and used to offset the following month's VAT. VAT REFUND (cash): Apply to TRA to receive the credit amount in cash. Many prefer the credit because it is faster — a cash refund requires a TRA audit which takes time.",
  "formal", "disambiguation"),

p("b006_vat_ref_017",
  "Ni wakati gani ni bora kudai refund ya pesa badala ya kubeba VAT credit mbele?",
  "Kubeba VAT credit mbele ni bora kama unatarajia kuwa na output VAT ya kutosha mwezi unaofuata — credit itafidia pasi na muda. Kudai refund ya pesa ni bora kama: una mkopo wa credit mkubwa sana unaokua, au biashara yako ina mtiririko wa fedha (cash flow) mbaya na unahitaji pesa. Refund ya pesa inachukua muda zaidi kwa sababu TRA lazima ikague.",
  "When is it better to claim a cash refund versus carrying the VAT credit forward?",
  "Carrying the credit forward is better when you expect sufficient output VAT the following month — the credit will offset it quickly. Claiming a cash refund is better when: you have a very large growing credit balance, or your business has poor cash flow and you need the money. Cash refunds take longer because TRA must audit first.",
  "business_market", "standard"),

p("b006_vat_ref_018",
  "Exporters wana kipaumbele katika refund ya VAT — kweli au uongo?",
  "Kweli kwa ujumla. TRA inatoa kipaumbele kwa exporters katika usindikaji wa VAT refund kwa sababu biashara ya nje ni muhimu kwa uchumi. Exporters wenye mauzo ya zero-rated yanayoonyesha VAT input credit za halali mara nyingi hupata refund haraka zaidi kuliko biashara za ndani. Thibitisha utaratibu wa sasa na TRA.",
  "Exporters get priority in VAT refunds — true or false?",
  "Generally true. TRA gives priority to exporters in processing VAT refunds because foreign trade is important to the economy. Exporters with zero-rated sales showing legitimate input VAT credits often receive refunds faster than domestic businesses. Confirm current procedures with TRA.",
  "formal", "standard"),

p("b006_vat_ref_019",
  "Je, biashara mpya inayonunua vifaa vya ofisi — inaweza kudai VAT refund?",
  "Ndiyo, ikiwa biashara imesajiliwa VAT. Ununuzi wa vifaa vya ofisi (kompyuta, samani, vifaa vya ofisi) kutoka wasambazaji waliosajilistwaa VAT unazalisha input VAT. Kama input VAT inazidi output VAT (kawaida mwanzoni mwa biashara), biashara ina haki ya kudai refund au kubeba credit mbele.",
  "A new business buying office equipment — can it claim a VAT refund?",
  "Yes, if the business is VAT-registered. Purchasing office equipment (computers, furniture, office supplies) from VAT-registered suppliers generates input VAT. If input VAT exceeds output VAT (common at the start of a business), the business is entitled to claim a refund or carry the credit forward.",
  "business_market", "standard"),

p("b006_vat_ref_020",
  "Kampuni ilinunua mashine ya uzalishaji kwa TZS 500M na kulipa VAT TZS 90M — inaweza kudai refund hiyo yote?",
  "Ndiyo, ikiwa mashine inatumika kwa biashara inayostahili VAT (taxable activities). Input VAT ya TZS 90M (18% × TZS 500M) inaweza kudaiwa kama input VAT yote ikiwa mashine inatumika 100% kwa biashara ya VAT. Kama inatumika kwa biashara ya VAT na shughuli zisizo na VAT (exempt), credit inagawanywa (apportionment). Thibitisha na mshauri wa kodi.",
  "A company bought a production machine for TZS 500M and paid TZS 90M VAT — can it claim back all that?",
  "Yes, if the machine is used entirely for VAT-taxable activities. Input VAT of TZS 90M (18% × TZS 500M) can be claimed as full input VAT if the machine is 100% used for VAT-taxable business. If it is used for both VAT-taxable and VAT-exempt activities, the credit is apportioned. Verify with a tax advisor.",
  "formal", "standard"),

# --- Group 5: TRA verification and timeline ---

p("b006_vat_ref_021",
  "TRA inachukua muda gani kusindika refund ya VAT?",
  "Sheria inaelekeza TRA kusindika VAT refund ndani ya kipindi maalum baada ya kupokea ombi kamili. Hata hivyo, mazoea ya vitendo yanaweza kutofautiana — ukaguzi wa kina unaweza kuchukua muda mrefu zaidi hasa kwa madai makubwa. Exporters mara nyingi hupata kipaumbele. Thibitisha muda wa sasa na TRA au mshauri wa kodi.",
  "How long does TRA take to process a VAT refund?",
  "The law directs TRA to process VAT refunds within a specified period after receiving a complete application. However, practical experience may vary — a thorough audit can take longer especially for large claims. Exporters often receive priority. Confirm current timelines with TRA or a tax advisor.",
  "formal", "out_of_corpus_refusal"),

p("b006_vat_ref_022",
  "Je, TRA inaweza kukataa refund ya VAT — na kwa sababu gani?",
  "Ndiyo. TRA inaweza kukataa madai ya VAT refund ikiwa: (1) Hati za kuunga mkono hazikamiliki au hazionekani kuwa za kweli; (2) Input VAT inahusiana na ununuzi wa kibinafsi, si biashara; (3) Wasambazaji hawakusajiliwa VAT au hawakulipa VAT wao; (4) Kuna tofauti kati ya VAT return na hati za kimwili; (5) Dalili za ulaghai wa VAT (VAT fraud). Weka kumbukumbu nzuri za biashara.",
  "Can TRA refuse a VAT refund — and for what reasons?",
  "Yes. TRA can reject VAT refund claims if: (1) Supporting documents are incomplete or appear inauthentic; (2) Input VAT relates to personal rather than business purchases; (3) Suppliers were not VAT-registered or did not pay their own VAT; (4) Discrepancies between VAT return and physical documents; (5) Indications of VAT fraud. Maintain good business records.",
  "formal", "standard"),

p("b006_vat_ref_023",
  "Je, TRA inaweza kufanya ukaguzi (audit) wakati wa kushughulikia refund ya VAT?",
  "Ndiyo. Madai ya VAT refund mara nyingi husababisha ukaguzi wa TRA. Hii ni kawaida na inatarajiwa — si adhabu. TRA inataka kuhakikisha madai ni halali kabla ya kutoa pesa. Kuwa tayari kuwasilisha hati zote, kumbukumbu za ununuzi/mauzo, na majibu ya maswali ya ukaguzi.",
  "Can TRA conduct an audit when processing a VAT refund?",
  "Yes. VAT refund claims often trigger a TRA audit. This is normal and expected — not a punishment. TRA wants to ensure claims are legitimate before releasing money. Be prepared to provide all documents, purchase/sales records, and answers to audit questions.",
  "formal", "standard"),

p("b006_vat_ref_024",
  "Je, ninalipa riba kama TRA imechelewa kutoa refund yangu?",
  "Sheria inaelekeza TRA ikusudie kulipa riba ikiwa imechelewa kusindika refund baada ya kipindi kilichoruhusiwa. Hata hivyo, utekelezaji halisi wa kipengele hiki unategemea kanuni maalum. Thibitisha haki zako za riba na TRA au mwanasheria wa kodi kama umechelewa kwa muda mrefu.",
  "Do I earn interest if TRA is late in paying my refund?",
  "The law directs TRA to intend to pay interest if it is late in processing a refund beyond the allowed period. However, practical enforcement of this provision depends on specific regulations. Verify your interest rights with TRA or a tax lawyer if you have experienced a significant delay.",
  "formal", "out_of_corpus_refusal"),

p("b006_vat_ref_025",
  "Je, ninaweza kupinga uamuzi wa TRA wa kukataa refund yangu?",
  "Ndiyo. Kama TRA imekataa madai yako ya VAT refund, una haki ya kupinga uamuzi huo. Njia za kawaida za kupinga ni: (1) Omba ukaguzi wa ndani wa TRA; (2) Lalamika kwa Kamishna Mkuu wa TRA; (3) Fika TRAB (Tax Revenue Appeals Board) ikiwa bado hujaridhika. Fuata hatua za kisheria kwa mpangilio na muda unaohusika.",
  "Can I challenge TRA's decision to reject my refund?",
  "Yes. If TRA has rejected your VAT refund claim, you have the right to challenge that decision. The standard challenge paths are: (1) Request an internal TRA review; (2) Appeal to the TRA Commissioner General; (3) Go to TRAB (Tax Revenue Appeals Board) if still unsatisfied. Follow the legal steps in order and within applicable timeframes.",
  "formal", "standard"),

# --- Group 6: Special scenarios ---

p("b006_vat_ref_026",
  "Biashara yangu inafanya mauzo ya VAT (taxable) na mauzo yasiyobeba VAT (exempt) — jinsi ya kudai input VAT?",
  "Kama biashara inafanya mauzo ya aina mbili — yenye VAT (taxable) na yasio na VAT (exempt) — input VAT inagawanywa (apportioned). Gawanya input VAT kulingana na uwiano wa mauzo ya taxable kwa mauzo yote. Sehemu ya input VAT inayohusiana na mauzo ya taxable inaweza kudaiwa; sehemu inayohusiana na exempt haiwezi. Utaratibu huu unaitwa 'partial exemption' au 'apportionment'.",
  "My business makes both VAT-taxable sales and VAT-exempt sales — how do I claim input VAT?",
  "When a business makes two types of sales — taxable (with VAT) and exempt (no VAT) — input VAT must be apportioned. Divide input VAT in proportion to taxable sales over total sales. The portion of input VAT relating to taxable sales can be claimed; the portion relating to exempt sales cannot. This process is called 'partial exemption' or 'apportionment'.",
  "formal", "standard"),

p("b006_vat_ref_027",
  "Biashara yangu inafanya mauzo ya nje (zero-rated) tu — ninaweza kudai input VAT yote?",
  "Ndiyo. Kama biashara inafanya MAUZO YA ZERO-RATED TU (si mauzo ya exempt), unaweza kudai input VAT yote. Zero-rated si sawa na exempt — zero-rated inamaanisha kiwango cha 0% lakini bado ni 'taxable supply', hivyo input VAT inaweza kudaiwa. Exempt inamaanisha nje ya mfumo wa VAT kabisa, na input VAT isiyoweza kudaiwa.",
  "My business makes only zero-rated (export) sales — can I claim all input VAT?",
  "Yes. If your business makes ONLY ZERO-RATED SALES (not exempt sales), you can claim all input VAT. Zero-rated is not the same as exempt — zero-rated means a 0% rate but is still a 'taxable supply', so input VAT can be claimed. Exempt means completely outside the VAT system, and input VAT cannot be claimed.",
  "formal", "disambiguation"),

p("b006_vat_ref_028",
  "Mauzo ya exempt na zero-rated — tofauti muhimu kwa madai ya VAT input?",
  "ZERO-RATED (kiwango 0%): Mauzo yanabeba VAT ya 0% — bado ni 'taxable supply'. Input VAT inaweza kudaiwa kwa mauzo haya. Mfano: exports. EXEMPT (sio kodi): Mauzo hayabeba VAT kabisa — nje ya mfumo wa VAT. Input VAT HAIWEZI kudaiwa kwa mauzo ya exempt. Mfano Tanzania: huduma za elimu, afya, mauzo fulani ya ardhi. Tofauti hii ni muhimu sana kwa madai ya input VAT.",
  "Exempt sales and zero-rated sales — critical difference for input VAT claims?",
  "ZERO-RATED (0% rate): Sales carry 0% VAT — still a 'taxable supply'. Input VAT CAN be claimed against these sales. Example: exports. EXEMPT (no tax): Sales carry no VAT at all — outside the VAT system. Input VAT CANNOT be claimed against exempt sales. Tanzania examples: education services, health services, some land sales. This distinction is critical for input VAT claims.",
  "formal", "disambiguation"),

p("b006_vat_ref_029",
  "Gari la biashara lililonunuliwa kampuni — input VAT yake inaweza kudaiwa?",
  "Inategemea matumizi ya gari. Magari yanayotumika kwa biashara (transport ya biashara, delivery vans, lorries) — input VAT yake kwa ujumla inaweza kudaiwa. Magari ya abiria (passenger cars) yanayotumika kwa wasimamizi binafsi — mara nyingi hayadaiwi input VAT Tanzania. TRA ina kanuni maalum kuhusu madai ya input VAT kwa magari — thibitisha na mshauri.",
  "A company car purchased by the company — can input VAT be claimed?",
  "It depends on the vehicle's use. Vehicles used for business purposes (business transport, delivery vans, lorries) — input VAT can generally be claimed. Passenger cars used by individual executives — often input VAT is not claimable in Tanzania. TRA has specific rules on vehicle input VAT claims — verify with an advisor.",
  "formal", "disambiguation"),

p("b006_vat_ref_030",
  "Kampuni ilinunua jengo kwa biashara na kulipa VAT — inaweza kudai refund?",
  "Ununuzi wa mali isiyohamishika (jengo) unaweza kuzalisha input VAT kama muuzaji alikuwa amesajiliwa VAT na shughuli inastahili. Hata hivyo, mauzo ya ardhi na majengo kwa kawaida yana matibabu maalum ya VAT Tanzania. Thibitisha hali ya VAT ya ununuzi maalum wa jengo lako na mshauri wa kodi au TRA.",
  "A company bought a building for business and paid VAT — can it claim a refund?",
  "Purchasing immovable property (a building) can generate input VAT if the seller was VAT-registered and the supply qualifies. However, sales of land and buildings generally have special VAT treatment in Tanzania. Confirm the VAT status of your specific building purchase with a tax advisor or TRA.",
  "formal", "out_of_corpus_refusal"),

# --- Group 7: Common mistakes and out-of-corpus ---

p("b006_vat_ref_031",
  "Makosa ya kawaida yanayosababisha kukataliwa kwa madai ya VAT refund?",
  "Makosa ya kawaida ni: (1) Kudai input VAT bila risiti ya EFD au invoice ya VAT halali; (2) Kudai VAT kutoka wasambazaji wasiosajiliwa VAT; (3) Kudai input VAT kwa ununuzi wa kibinafsi; (4) Hati zisizokamilika au zenye tofauti; (5) Kutofanya VAT returns za kila mwezi kwa wakati; (6) Kutodai input VAT kwa wakati (kuiacha muda kupita). Weka kumbukumbu nzuri kuepuka makosa haya.",
  "Common mistakes that cause VAT refund claims to be rejected?",
  "Common mistakes include: (1) Claiming input VAT without a valid EFD receipt or VAT invoice; (2) Claiming VAT from non-VAT-registered suppliers; (3) Claiming input VAT on personal purchases; (4) Incomplete or inconsistent documents; (5) Not filing monthly VAT returns on time; (6) Not claiming input VAT on time (letting the period expire). Maintain good records to avoid these errors.",
  "business_market", "standard"),

p("b006_vat_ref_032",
  "Je, VAT refund ya watalii (tourist VAT refund) inapatikana Tanzania?",
  "Sina uhakika wa hali ya sasa ya mfumo wa VAT refund kwa watalii Tanzania. Nchi nyingine zina mifumo kama hiyo lakini utekelezaji wake Tanzania unabadilika. Thibitisha na TRA au Bodi ya Utalii ya Tanzania (TTB) kuhusu hali ya sasa ya VAT refund kwa watalii.",
  "Is a tourist VAT refund available in Tanzania?",
  "I am not certain of the current status of a tourist VAT refund scheme in Tanzania. Some countries have such schemes but implementation in Tanzania is evolving. Verify with TRA or the Tanzania Tourism Board (TTB) about the current status of tourist VAT refunds.",
  "formal", "out_of_corpus_refusal"),

p("b006_vat_ref_033",
  "Je, VAT refund inaweza kupatikana kwa biashara za kilimo?",
  "Inategemea aina ya biashara ya kilimo. Biashara ya kilimo inayofanya mauzo ya zero-rated (exports za mazao) au inayonunua vifaa vya kilimo vinavyobeba input VAT — inaweza kudai input VAT. Hata hivyo, mauzo ya ndani ya mazao yanaweza kuwa exempt au zero-rated kulingana na aina ya mazao. Thibitisha hali ya VAT ya biashara yako ya kilimo na TRA.",
  "Can VAT refunds be obtained for agricultural businesses?",
  "It depends on the type of agricultural business. Agricultural businesses making zero-rated sales (exports of produce) or purchasing agricultural inputs that carry input VAT — can claim input VAT. However, domestic sales of produce may be exempt or zero-rated depending on the produce type. Verify the VAT status of your agricultural business with TRA.",
  "rural_conversational", "standard"),

p("b006_vat_ref_034",
  "Je, VAT refund ya biashara iliyofutwa (deregistered) inaweza kudaiwa?",
  "Kama biashara ilipata VAT credit kabla ya kufutwa, inaweza kudai refund hiyo wakati wa mchakato wa kufutwa. Hata hivyo, utaratibu huu una masharti maalum ya TRA. Wakati wa kufutwa usajili wa VAT (VAT deregistration), thibitisha na TRA kuhusu haki za madai ya mwisho ya input VAT.",
  "Can a deregistered business claim a VAT refund?",
  "If a business had a VAT credit before deregistration, it may claim that refund during the deregistration process. However, this process has specific TRA requirements. When deregistering for VAT, confirm with TRA about final input VAT claim rights.",
  "formal", "standard"),

p("b006_vat_ref_035",
  "Je, refund ya VAT inaathiri faida ya kodi ya mapato (corporate tax)?",
  "VAT refund si mapato ya biashara — haipunguzi wala kuongeza kodi ya mapato. VAT ni kodi tofauti na kodi ya mapato ya makampuni. Hata hivyo, utunzaji wa kumbukumbu za VAT na kodi ya mapato ya makampuni unaunganika — makosa ya VAT yanaweza kusababisha ukaguzi wa kodi ya mapato pia.",
  "Does a VAT refund affect corporate income tax?",
  "A VAT refund is not business income — it does not reduce or increase corporate tax. VAT is a separate tax from corporate income tax. However, VAT and corporate tax record-keeping are interconnected — VAT errors can also trigger a corporate tax audit.",
  "formal", "standard"),

# --- Group 8: VAT return process ---

p("b006_vat_ref_036",
  "VAT return ya kila mwezi — lazima iwasilishwe hata kama hakuna mauzo?",
  "Ndiyo. Mfanyabiashara aliyesajiliwa VAT lazima awasilishe VAT return KILA MWEZI — hata kama hakuna mauzo (nil return). Kushindwa kuwasilisha VAT return kwa wakati kunasababisha adhabu ya marehemu hata kama hakuna VAT inayodaiwa. Wasilisha nil return kwa wakati kama hukufanya mauzo yoyote.",
  "Monthly VAT return — must it be filed even with no sales?",
  "Yes. A VAT-registered business must file a VAT return EVERY MONTH — even with no sales (nil return). Failing to file a VAT return on time attracts a late penalty even if no VAT is owed. File a nil return on time if you had no sales.",
  "business_market", "adversarial"),

p("b006_vat_ref_037",
  "VAT return inawasilishwa lini — tarehe 7 au tarehe 20?",
  "VAT return inawasilishwa na VAT inalipwa ifikapo tarehe 20 ya mwezi unaofuata — si tarehe 7. Tarehe 7 ni ya PAYE na SDL. Usije ukachanganya tarehe hizi mbili: PAYE/SDL = tarehe 7; VAT = tarehe 20.",
  "When is the VAT return filed — the 7th or the 20th?",
  "The VAT return is filed and VAT is paid by the 20th of the following month — not the 7th. The 7th is for PAYE and SDL. Do not confuse these two dates: PAYE/SDL = 7th; VAT = 20th.",
  "business_market", "adversarial"),

p("b006_vat_ref_038",
  "Je, kutolipa VAT kwa wakati kuna riba na adhabu — kiwango gani?",
  "Kutolipa VAT kwa wakati kunaleta: (1) Adhabu ya marehemu (late payment penalty); (2) Riba ya kuendelea (interest) juu ya kiasi kilichocheleweshwa. Viwango maalum vya adhabu na riba vimewekwa na Sheria ya Usimamizi wa Kodi (Tax Administration Act). Lipa VAT kabla ya tarehe 20 kuepuka adhabu hizi.",
  "Does failing to pay VAT on time attract interest and penalties — what rates?",
  "Failing to pay VAT on time attracts: (1) A late payment penalty; (2) Ongoing interest on the overdue amount. Specific penalty and interest rates are set by the Tax Administration Act. Pay VAT before the 20th to avoid these charges.",
  "formal", "standard"),

p("b006_vat_ref_039",
  "Je, biashara inaweza kufanya VAT return ya robo mwaka badala ya kila mwezi?",
  "Kwa kawaida, Tanzania inahitaji VAT return ya kila MWEZI. Baadhi ya nchi zinaruhusu quarter filing kwa biashara ndogo — lakini hii si utaratibu wa kawaida wa Tanzania. Thibitisha na TRA kama kuna mpango wa quarterly filing unaohusiana na hali yako.",
  "Can a business file a quarterly VAT return instead of monthly?",
  "Generally, Tanzania requires MONTHLY VAT returns. Some countries allow quarterly filing for small businesses — but this is not Tanzania's standard procedure. Verify with TRA whether there is any quarterly filing arrangement applicable to your situation.",
  "formal", "out_of_corpus_refusal"),

p("b006_vat_ref_040",
  "Je, ninaweza kusahihisha VAT return iliyokwisha wasilishwa?",
  "Ndiyo. TRA inaruhusu marekebisho (amendments) ya VAT returns zilizowahi wasilishwa ndani ya muda unaoruhusiwa. Wasilisha VAT return ya marekebisho inayoonyesha tofauti. Kama marekebisho yanasababisha VAT zaidi kulipa, riba na adhabu zinaweza kutumika. Fanya marekebisho mapema iwezekanavyo.",
  "Can I correct a VAT return that has already been filed?",
  "Yes. TRA allows amendments to previously filed VAT returns within the permitted timeframe. Submit an amended VAT return showing the differences. If amendments result in additional VAT payable, interest and penalties may apply. Make corrections as early as possible.",
  "formal", "standard"),

# --- Group 9: Advanced VAT refund scenarios ---

p("b006_vat_ref_041",
  "Biashara yangu ilikuwa exempt VAT — sasa imekuwa taxable. Ninaweza kudai VAT ya vifaa vilivyonunuliwa awali?",
  "Hali hii ya mabadiliko ya hali ya VAT (exempt kwenda taxable) ina kanuni maalum. Kwa ujumla, input VAT iliyolipwa kipindi cha exempt haiwezi kudaiwa kwa wakati wa mabadiliko. Hata hivyo, kwa vifaa na mali ambazo bado zinatumika, inawezekana kudai sehemu ya input VAT — lakini hii ni ngumu. Thibitisha na TRA au mshauri wa kodi.",
  "My business was VAT-exempt — it is now taxable. Can I claim VAT on goods bought earlier?",
  "This situation of changing VAT status (exempt to taxable) has specific rules. Generally, input VAT paid during the exempt period cannot be claimed at the time of change. However, for capital assets and equipment still in use, it may be possible to claim a portion of input VAT — but this is complex. Verify with TRA or a tax advisor.",
  "formal", "out_of_corpus_refusal"),

p("b006_vat_ref_042",
  "Kampuni mama (parent company) inaweza kudai VAT ya kampuni binti (subsidiary)?",
  "Kwa ujumla, kila kampuni ni mfanyabiashara tofauti wa VAT — kampuni mama haiwezi kudai input VAT ya kampuni binti na kinyume chake. Hata hivyo, kuna mifumo ya 'VAT group registration' ambapo makampuni yanayohusiana yanaweza kusajiliwa pamoja kwa VAT. Thibitisha upatikanaji wa mfumo huu Tanzania na TRA.",
  "Can a parent company claim VAT of a subsidiary?",
  "Generally, each company is a separate VAT entity — a parent company cannot claim the subsidiary's input VAT and vice versa. However, there are 'VAT group registration' frameworks where related companies can register together for VAT. Verify availability of this framework in Tanzania with TRA.",
  "formal", "out_of_corpus_refusal"),

p("b006_vat_ref_043",
  "Ununuzi wa mafuta ya dizeli kwa matumizi ya biashara — input VAT inaweza kudaiwa?",
  "Kwa biashara zilizoposajiliwa VAT zinazotumia mafuta kwa biashara (kwa magari ya biashara, mashine) — input VAT ya mafuta inaweza kudaiwa. Hata hivyo, kama mafuta yanatumika kwa gari la kibinafsi la msimamizi, input VAT haiwezi kudaiwa. Thibitisha matumizi ya mafuta na uhifadhi kumbukumbu nzuri.",
  "Purchases of diesel fuel for business use — can input VAT be claimed?",
  "For VAT-registered businesses using fuel for business purposes (business vehicles, machinery) — input VAT on fuel can be claimed. However, if fuel is used for a personal executive vehicle, input VAT cannot be claimed. Verify fuel usage and maintain good records.",
  "formal", "standard"),

p("b006_vat_ref_044",
  "Ununuzi wa chakula cha ofisi kwa wafanyakazi — VAT inaweza kudaiwa?",
  "Kwa ujumla, ununuzi wa chakula kwa wafanyakazi (kama si sehemu ya mauzo ya biashara) unachukuliwa kama matumizi ya kibinafsi — na input VAT yake mara nyingi haiwezi kudaiwa. Hata hivyo, kama kampuni inauza chakula au inaendesha mkahawa kama sehemu ya biashara yake, hali inaweza kutofautiana. Thibitisha na mshauri.",
  "Office food purchases for employees — can VAT be claimed?",
  "Generally, food purchases for employees (if not part of the business's sales) are treated as personal consumption — and input VAT on them often cannot be claimed. However, if the company sells food or runs a cafeteria as part of its business, the situation may differ. Verify with an advisor.",
  "formal", "disambiguation"),

p("b006_vat_ref_045",
  "Jinsi ya kuepuka matatizo ya ukaguzi wa VAT wakati wa kudai refund?",
  "Kuepuka matatizo ya ukaguzi wa VAT: (1) Hifadhi kumbukumbu zote za VAT kwa miaka 5 angalau; (2) Hakikisha risiti zote za EFD zimewekwa vizuri; (3) Oanisha VAT returns na kumbukumbu za uhasibu; (4) Nunua kutoka wasambazaji waliosajilistwaa VAT tu; (5) Epuka madai ya input VAT yasiyohusiana na biashara; (6) Wasilisha VAT returns kwa wakati na kwa usahihi. Kumbukumbu nzuri = ukaguzi rahisi.",
  "How to avoid audit problems when claiming a VAT refund?",
  "To avoid VAT audit problems: (1) Keep all VAT records for at least 5 years; (2) Ensure all EFD receipts are properly filed; (3) Reconcile VAT returns with accounting records; (4) Buy only from VAT-registered suppliers; (5) Avoid input VAT claims unrelated to business; (6) File VAT returns on time and accurately. Good records = easier audit.",
  "business_market", "standard"),

# --- Group 10: Summary and muhtasari ---

p("b006_vat_ref_046",
  "Muhtasari: mfanyabiashara wa Tanzania anapaswa kujua nini kuhusu VAT refund?",
  "VAT refund — mambo makuu: (1) Inatokea wakati input VAT > output VAT; (2) Exporters (zero-rated) wana haki ya kawaida kwa sababu output VAT = 0; (3) Omba refund kwa TRA na hati kamili (EFD risiti, VAT invoices, export docs); (4) TRA inafanya ukaguzi kabla ya kulipa; (5) Unaweza kubeba credit mbele badala ya kudai pesa; (6) Lipa VAT returns kwa wakati kila mwezi (tarehe 20) kujenga historia nzuri ya madai.",
  "Summary: what does a Tanzanian business need to know about VAT refunds?",
  "VAT refund — key points: (1) Arises when input VAT > output VAT; (2) Exporters (zero-rated) regularly qualify because output VAT = 0; (3) Apply to TRA with complete documentation (EFD receipts, VAT invoices, export docs); (4) TRA audits before paying; (5) You can carry the credit forward instead of claiming cash; (6) File VAT returns on time every month (by the 20th) to build a good claims history.",
  "business_market", "standard"),

p("b006_vat_ref_047",
  "Mfanyabiashara asiyejua tofauti ya zero-rated na exempt anaweza kupoteza nini?",
  "Anaweza kupoteza input VAT yake. Mfanyabiashara anayedhani mauzo yake ni 'exempt' (wakati yako zero-rated) anaweza kushindwa kudai input VAT anayostahili — anapoteza pesa halisi. Na kinyume chake, mfanyabiashara anayedhani mauzo yake ni 'zero-rated' (wakati yako exempt) anaweza kudai input VAT isiyostahiliwa — akabiliane na adhabu. Ujuzi wa tofauti hii ni muhimu.",
  "What can a business lose by not knowing the difference between zero-rated and exempt?",
  "They can lose their input VAT. A business that thinks its sales are 'exempt' (when they are actually zero-rated) may fail to claim input VAT it is entitled to — losing real money. Conversely, a business that thinks its sales are 'zero-rated' (when they are exempt) may claim unentitled input VAT — and face penalties. Understanding this distinction is critical.",
  "formal", "standard"),

p("b006_vat_ref_048",
  "Je, biashara ndogo (SME) inaweza kudai VAT refund bila mshauri wa kodi?",
  "Technically, ndiyo — hakuna sheria inayohitaji mshauri wa kodi kudai VAT refund. Hata hivyo, kwa madai makubwa au ya ngumu, mshauri wa kodi au akaunti aliyesajiliwa anaweza kusaidia sana kupunguza makosa na kuongeza mafanikio ya madai. Kwa madai rahisi ya exporter, biashara inaweza kujaribu mwenyewe baada ya kushauriana na TRA.",
  "Can a small business (SME) claim a VAT refund without a tax advisor?",
  "Technically yes — there is no law requiring a tax advisor to claim a VAT refund. However, for large or complex claims, a registered tax advisor or accountant can greatly reduce errors and increase claim success. For straightforward exporter claims, a business can try independently after consulting with TRA.",
  "business_market", "standard"),

p("b006_vat_ref_049",
  "Je, ikiwa wafanyakazi wa TRA wananikatalia bila sababu — ninafanya nini?",
  "Kama unaamini madai yako ya VAT refund yamekataliwa bila sababu ya kisheria, una haki za kisheria. Pata maelezo ya maandishi ya sababu ya kukataliwa. Thibitisha na sheria ya VAT Tanzania. Piga rufaa kwa Kamishna wa TRA. Kama bado hujaridhika, fika TRAB (Tax Revenue Appeals Board) au mahakama. Weka kumbukumbu za mawasiliano yote.",
  "If TRA staff are rejecting my claim without reason — what do I do?",
  "If you believe your VAT refund claim was rejected without legal basis, you have legal rights. Get the rejection reason in writing. Verify against Tanzania VAT law. Appeal to the TRA Commissioner. If still unsatisfied, go to TRAB (Tax Revenue Appeals Board) or courts. Keep records of all communications.",
  "business_market", "standard"),

p("b006_vat_ref_050",
  "VAT refund na VAT compliance — jinsi zinavyohusiana?",
  "Compliance na VAT (kuwasilisha returns kwa wakati, kulipa VAT, kuhifadhi kumbukumbu) ndiyo msingi wa haki ya kudai VAT refund. TRA inachunguza historia ya compliance wakati inashughulikia madai ya refund. Biashara yenye historia nzuri ya compliance (returns zote za wakati, hakuna deni la VAT) ina nafasi nzuri zaidi ya kupata refund yake haraka.",
  "VAT refund and VAT compliance — how are they related?",
  "VAT compliance (filing returns on time, paying VAT, keeping records) is the foundation of the right to claim a VAT refund. TRA examines compliance history when processing refund claims. A business with a good compliance record (all returns on time, no VAT debt) has a much better chance of receiving its refund quickly.",
  "formal", "standard"),

]

# Append to JSONL
written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pair in pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        written += 1

print(f"Wrote {written} pairs to {OUT}")

from collections import Counter
regs = Counter(p_["register"] for p_ in pairs)
ptypes = Counter(p_["pair_type"] for p_ in pairs)
print("Register distribution:", dict(regs))
print("Pair type distribution:", dict(ptypes))

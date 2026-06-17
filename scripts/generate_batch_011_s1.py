#!/usr/bin/env python3
"""Generate batch_011 Section 1 — 50 refusal pairs (35 hard + 15 soft)."""
import json, os

OUTPUT_FILE = "datasets/tier1a/raw_sources/raw_pairs_batch_011.jsonl"
CHECKPOINT_DIR = "datasets/tier1a/raw_sources/batch_011_checkpoints"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

HARD_SUFFIX = (
    "Mimi ni Chike kutoka Africa Giants — ninashughulikia VAT, PAYE, SDL, NSSF, "
    "WCF, BRELA, EFD, na usajili wa biashara Tanzania Bara. "
    "Wasiliana na mshauri wa kodi aliyehitimu au TRA kupitia tra.go.tz."
)

def hard(instruction, domain_sentence):
    return {
        "instruction": instruction,
        "output": (
            f"Swali hili liko nje ya maarifa yangu ya sasa. "
            f"{domain_sentence} {HARD_SUFFIX}"
        )
    }

def soft(instruction, principle, specifics_note):
    return {
        "instruction": instruction,
        "output": (
            f"{principle} "
            f"Swali hili liko nje ya maarifa yangu ya sasa kwa {specifics_note}. "
            f"Wasiliana na mshauri wa kodi aliyehitimu au TRA kupitia tra.go.tz."
        )
    }

pairs = []

# ── DOMAIN A: Capital gains tax — 5 HARD ──────────────────────────────────
pairs.append(hard(
    "Niliuza ardhi yangu jijini Dar es Salaam na kupata faida ya TZS 50M — ninalipa capital gains tax ngapi na lini?",
    "Kodi ya mapato ya mtaji (capital gains tax) kwa mauzo ya ardhi inashughulikiwa chini ya Income Tax Act — inahitaji tathmini ya thamani ya msingi (cost base), thamani ya uuzaji, na muda wa umiliki."
))
pairs.append(hard(
    "Ninataka kuuza hisa zangu zote katika kampuni ya sekta ya utalii Tanzania — capital gains tax inakuja namna gani?",
    "Kodi ya mapato ya mtaji (capital gains tax) kwa mauzo ya hisa katika kampuni za Tanzania inashughulikiwa chini ya Income Tax Act na inategemea hali ya mkazi au asiye mkazi."
))
pairs.append(hard(
    "Niliuza nyumba yangu ya biashara (commercial property) na kupata faida — lazima nilipe capital gains tax?",
    "Kodi ya mapato ya mtaji kwa mali za biashara inashughulikiwa chini ya Income Tax Act — inahitaji tathmini ya thamani ya ununuzi, maboresho yaliyofanywa, na thamani ya uuzaji."
))
pairs.append(hard(
    "Ninauza biashara yangu nzima ikiwemo mali zote, dhamana, na jina la biashara — capital gains tax yake ni ngapi?",
    "Uamuzi wa capital gains tax kwa mauzo ya biashara nzima ni mgumu na unajumuisha tathmini ya kila kipande cha mali chini ya Income Tax Act — inahitaji utaalamu maalum wa kodi ya mapato."
))
pairs.append(hard(
    "Mimi ni mgeni (non-resident) ninayeishi Uingereza lakini nina ardhi Tanzania — nikiuza ardhi hiyo, capital gains tax inanishughulikia vipi?",
    "Hali ya capital gains tax kwa wasio wakazi (non-residents) inashughulikiwa tofauti chini ya Income Tax Act na mikataba ya kuzuia kodi mara mbili (DTAs) — inahitaji utaalamu maalum wa kodi ya kimataifa."
))

# ── DOMAIN B: Transfer pricing — 5 HARD ───────────────────────────────────
pairs.append(hard(
    "Kampuni yangu ina mkopo kutoka kampuni mama yake nje ya Tanzania — kiwango gani cha riba kinachukuliwa kuwa cha kawaida (arm's length)?",
    "Transfer pricing na mkopo wa kampuni washirika (related party loans) inashughulikiwa chini ya Income Tax Act na kanuni za transfer pricing za TRA — inahitaji tathmini ya kiwango cha soko."
))
pairs.append(hard(
    "Kampuni mama yangu nje ya Tanzania inanitolea huduma za usimamizi (management fees) — ninaweza kulipa kiasi gani bila TRA kunishinda?",
    "Ada za usimamizi (management fees) kwa kampuni washirika zinashughulikiwa chini ya kanuni za transfer pricing — TRA inaweza kupinga malipo yanayozidi bei ya soko (arm's length price)."
))
pairs.append(hard(
    "Kampuni yangu inashiriki gharama za utafiti na maendeleo na kampuni mama yake — cost sharing arrangement inaweza kupingwa na TRA vipi?",
    "Cost sharing arrangements kati ya kampuni washirika zinashughulikiwa chini ya kanuni za transfer pricing za TRA — kila mkataba lazima uonyeshe mgawanyo wa faida unaofanana na mchango wa kila upande."
))
pairs.append(hard(
    "Ninas wakati gani wa kuwasilisha transfer pricing documentation kwa TRA?",
    "Nyaraka za transfer pricing (transfer pricing documentation) zinahitajika chini ya kanuni za Income Tax Act — muda na maudhui yanategemea ukubwa wa kampuni na kiasi cha miamala ya washirika."
))
pairs.append(hard(
    "TRA wamenishuku kwa transfer pricing — ukaguzi wa transfer pricing unafanyika vipi na ninaweza kujilinda vipi?",
    "Ukaguzi wa transfer pricing unafanyika chini ya Income Tax Act — TRA inaweza kupinga bei za miamala ya washirika na kutoa marekebisho ya kodi iwapo bei hazilingani na bei ya soko."
))

# ── DOMAIN C: Stamp duty — 5 HARD ─────────────────────────────────────────
pairs.append(hard(
    "Ninanunua nyumba ya TZS 300M Dar es Salaam — stamp duty yake ni ngapi na nani analipa?",
    "Stamp duty kwa uhamishaji wa mali isiyohamishika inashughulikiwa chini ya Stamp Duty Act — kiwango na mtu anayeilipa vinategemea aina ya muamala na thamani iliyokadiriwa na mthamini wa serikali."
))
pairs.append(hard(
    "Kampuni yangu inanunua viwanja viwili vya biashara — stamp duty inaweza kuepukwa kwa mikataba ya maneno bila karatasi?",
    "Stamp duty kwa uhamishaji wa ardhi na mali inashughulikiwa chini ya Stamp Duty Act — mikataba ya maneno hairidhishi kisheria, na stamp duty inadaiwa kwenye hati yoyote inayohamisha umiliki."
))
pairs.append(hard(
    "TRA inatathmini thamani ya ardhi yangu kwa stamp duty — ninaweza kupinga tathmini hiyo?",
    "Utaratibu wa kupinga tathmini ya stamp duty unashughulikiwa chini ya Stamp Duty Act na kanuni za TRA — inajumuisha kuwasilisha tathmini mbadala na utaratibu wa rufaa."
))
pairs.append(hard(
    "Ninahamisha hisa zangu katika kampuni kwa mtu mwingine — stamp duty kwa uhamishaji wa hisa (share transfer) ni ngapi?",
    "Stamp duty kwa uhamishaji wa hisa (share transfer) inashughulikiwa chini ya Stamp Duty Act — kiwango kinategemea thamani ya hisa na aina ya kampuni inayohusika."
))
pairs.append(hard(
    "Ninaingia mkataba wa kukodisha ofisi kwa miaka 3 — stamp duty inatumika na inahesabiwaje?",
    "Stamp duty kwa mikataba ya kukodisha (lease agreements) inashughulikiwa chini ya Stamp Duty Act — hesabu inategemea thamani ya kodi ya jumla ya mkataba wote."
))

# ── DOMAIN D: Mineral royalties — 5 HARD ──────────────────────────────────
pairs.append(hard(
    "Kampuni yangu ina mgodi wa dhahabu Tanzania — royalty ya dhahabu ni asilimia ngapi ya mapato?",
    "Royalty ya madini (mineral royalties) inashughulikiwa chini ya Mining Act na kanuni za TMAA/MEM — kiwango kinatofautiana kulingana na aina ya madini na thamani ya soko la kimataifa."
))
pairs.append(hard(
    "Ninachimba almasi kidogo kidogo kama mchimbaji mdogo (artisanal miner) — royalty yangu ni ngapi?",
    "Royalty ya madini kwa wachimbaji wadogo (artisanal and small-scale miners) inashughulikiwa chini ya Mining Act na kanuni maalum za TMAA — kiwango kinatofautiana na cha wachimbaji wakubwa."
))
pairs.append(hard(
    "Mgodi wetu unachimba shaba (copper) — royalty ya shaba imehesabiwaje na inalipiwa lini?",
    "Royalty ya shaba na madini mengine inashughulikiwa chini ya Mining Act — hesabu na ratiba ya malipo vinategemea mkataba wa uwekezaji (Mineral Development Agreement) na kanuni za TMAA."
))
pairs.append(hard(
    "Serikali inapata asilimia ngapi ya mapato ya madini? Mgawanyo kati ya serikali na kampuni ya madini ni upi?",
    "Mgawanyo wa mapato ya madini kati ya serikali na kampuni unashughulikiwa chini ya Mining Act, MIDA, na masharti ya mkataba wa uwekezaji — inajumuisha royalty, kodi ya mapato, na mgawanyo wa faida (profit sharing)."
))
pairs.append(hard(
    "Kampuni yangu ya madini inapaswa kulipa kodi gani zote — royalty, VAT, PAYE, na nyingine?",
    "Wajibu wote wa kodi kwa kampuni za madini — ikiwemo royalty, kodi ya mapato, WHT, na VAT — unashughulikiwa chini ya Mining Act, Income Tax Act, na mikataba ya uwekezaji. Hii ni mada ngumu inayohitaji mshauri maalum wa sekta ya madini."
))

# ── DOMAIN E: Insurance premium levy — 5 HARD ─────────────────────────────
pairs.append(hard(
    "Kampuni yangu ya bima inauza bima Tanzania — insurance premium levy ni asilimia ngapi?",
    "Insurance premium levy inashughulikiwa chini ya TIRA (Tanzania Insurance Regulatory Authority) na sheria ya bima — kiwango na utaratibu wa kulipa vinashughulikiwa na TIRA, si TRA."
))
pairs.append(hard(
    "Bima ya maisha (life insurance) ina levy tofauti na bima ya kawaida (general insurance) Tanzania?",
    "Tofauti ya levy kati ya bima ya maisha na bima ya kawaida inashughulikiwa chini ya sheria ya bima na kanuni za TIRA — ni mada tofauti na kodi zinazoshughulikiwa na TRA."
))
pairs.append(hard(
    "Nani analipa insurance premium levy — kampuni ya bima au mteja anayenunua bima?",
    "Wajibu wa kulipa insurance premium levy na jinsi inavyohamishwa kwa wateja inashughulikiwa chini ya sheria ya bima na kanuni za TIRA — si ndani ya mada za TRA/BRELA/NSSF ambazo ninazishughulikia."
))
pairs.append(hard(
    "TIRA inashughulikia nini hasa na jinsi gani inavyosimamiwa na serikali ya Tanzania?",
    "Muundo wa TIRA, mamlaka yake, na jinsi inavyosimamiwa unashughulikiwa chini ya sheria ya bima Tanzania — si ndani ya mada za usajili wa biashara au kodi za TRA ambazo ninazishughulikia."
))
pairs.append(hard(
    "Premiums za bima za afya za wafanyakazi zinastahili msamaha wa insurance premium levy?",
    "Msamaha wa insurance premium levy kwa aina mbalimbali za bima inashughulikiwa chini ya sheria ya bima na kanuni za TIRA — inahitaji mshauri maalum wa sekta ya bima au kushauriana na TIRA moja kwa moja."
))

# ── DOMAIN F: EPZ/SEZ tax conditions — 5 HARD ─────────────────────────────
pairs.append(hard(
    "Kampuni yangu iko ndani ya EPZ (Export Processing Zone) Tanzania — mapumziko ya kodi (tax holiday) ni ya miaka mingapi?",
    "Masharti ya kodi kwa kampuni ndani ya EPZ/SEZ yanashughulikiwa chini ya EPZ Act na EPZA (Export Processing Zones Authority) — muda wa tax holiday na masharti mengine yanategemea aina ya biashara na mkataba na EPZA."
))
pairs.append(hard(
    "EPZ kampuni yangu iko exempt ya VAT — msamaha huu unashughulikia manunuzi yote ndani ya Tanzania au nje tu?",
    "Upeo wa msamaha wa VAT kwa kampuni za EPZ unashughulikiwa chini ya EPZ Act na kanuni za EPZA na TRA — inajumuisha masharti ya soko la ndani dhidi ya mauzo ya nje (exports)."
))
pairs.append(hard(
    "Kampuni yangu ya EPZ inapaswa kulipa SDL kwa wafanyakazi wake?",
    "Wajibu wa SDL kwa kampuni za EPZ/SEZ unashughulikiwa chini ya EPZ Act na mkataba wa EPZA — masharti yanaweza kutofautiana na kampuni za kawaida za Tanzania Bara."
))
pairs.append(hard(
    "Wafanyakazi wangu wa EPZ wanalipa PAYE kama wafanyakazi wa kawaida Tanzania?",
    "Wajibu wa PAYE kwa wafanyakazi wa kampuni za EPZ unashughulikiwa chini ya EPZ Act na mkataba wa EPZA na TRA — masharti yanaweza kuwa na tofauti muhimu na mfumo wa kawaida."
))
pairs.append(hard(
    "Kampuni ya EPZ na kampuni ya Tanzania Bara ya kawaida — tofauti kubwa za kodi ni zipi?",
    "Ulinganisho wa mfumo wa kodi kati ya EPZ/SEZ na kampuni za kawaida za Tanzania Bara unashughulikiwa chini ya EPZ Act na mikataba ya EPZA — ni uchambuzi mgumu unaohitaji mshauri maalum wa uwekezaji."
))

# ── DOMAIN G: Zanzibar tax law — 5 HARD ───────────────────────────────────
pairs.append(hard(
    "Biashara yangu iko Zanzibar — ninasajiliwa na ZRB au TRA? Wanaweza wote wawili kudai kodi?",
    "Mgawanyo wa mamlaka ya kodi kati ya ZRB (Zanzibar Revenue Board) na TRA (Tanzania Revenue Authority) unashughulikiwa chini ya sheria za Zanzibar — mimi ninashughulikia kodi za Tanzania Bara tu."
))
pairs.append(hard(
    "VAT rate ya Zanzibar ni ile ile 18% kama Tanzania Bara?",
    "VAT na kiwango chake kwa Zanzibar inashughulikiwa chini ya sheria za ZRB — mimi ninashughulikia VAT ya Tanzania Bara tu. Kwa maswali ya Zanzibar, wasiliana na ZRB moja kwa moja."
))
pairs.append(hard(
    "Wafanyakazi wangu Zanzibar wanalipa PAYE — ni sawa na Bara au kuna tofauti?",
    "PAYE na mifumo ya kodi ya mshahara kwa Zanzibar inashughulikiwa chini ya sheria za ZRB — mimi ninashughulikia PAYE ya Tanzania Bara tu. Kwa Zanzibar wasiliana na ZRB."
))
pairs.append(hard(
    "Usajili wa biashara Zanzibar — ninafanya kwa BRELA au kuna ofisi tofauti?",
    "Usajili wa biashara Zanzibar unashughulikiwa chini ya mamlaka za Zanzibar (ZIPA — Zanzibar Investment Promotion Authority na ofisi nyingine) — BRELA inashughulikia Tanzania Bara tu."
))
pairs.append(hard(
    "Nina biashara Zanzibar NA Tanzania Bara — ninasajiliwa wapi na ninalipa kodi wapi?",
    "Biashara inayofanya kazi Zanzibar NA Tanzania Bara inaweza kuwa na wajibu wa kodi kwa ZRB NA TRA kulingana na shughuli — hii ni hali ngumu inayohitaji mshauri maalum wa kodi inayojua mifumo yote miwili."
))

# ── SOFT REFUSALS — Capital gains (5) ─────────────────────────────────────
pairs.append(soft(
    "Niliuza gari langu la biashara na kupata faida — capital gains tax inatumika?",
    "Faida inayotokana na uuzaji wa mali za biashara kama magari inaweza kuwa taxable chini ya Income Tax Act Tanzania kulingana na hali ya mali hiyo.",
    "hesabu halisi, kiwango, na utaratibu wa kuripoti kwa TRA"
))
pairs.append(soft(
    "Nimeuza duka langu — ni tofauti gani kati ya capital gains tax na kodi ya kawaida ya biashara (business income tax)?",
    "Kwa ujumla, mapato ya biashara ya kawaida yanatozwa kodi tofauti na faida ya uuzaji wa mali (capital gains) — tofauti inategemea aina ya mali na jinsi ilivyotumiwa katika biashara.",
    "tofauti ya kisheria na jinsi ya kuripoti kwa TRA katika hali yako maalum"
))
pairs.append(soft(
    "Nilinunua hisa za kampuni mwaka 2020 kwa TZS 5M, sasa ninaziuza kwa TZS 20M — kodi ni ngapi?",
    "Faida inayotokana na uuzaji wa hisa (TZS 15M katika mfano huu) inaweza kuwa taxable chini ya Income Tax Act Tanzania.",
    "kiwango cha kodi halisi, msamaha wowote unaotumika, na tarehe ya kuwasilisha kwa TRA"
))
pairs.append(soft(
    "Mrithi wangu atakapourithi duka langu baada yangu — kuna capital gains tax kwake?",
    "Urithi wa mali za biashara unaweza kuathiri wajibu wa capital gains tax wa mrithi chini ya Income Tax Act Tanzania — inategemea thamani ya mali wakati wa urithi dhidi ya wakati wa uuzaji.",
    "hesabu halisi ya wajibu wa kodi wa mrithi katika hali yako"
))
pairs.append(soft(
    "Kampuni yangu ilitoa ardhi kama mchango kwa kampuni nyingine (contribution in kind) — capital gains tax inatumika?",
    "Mchango wa mali kama ardhi kwa kampuni nyingine (contribution in kind) unaweza kuzua wajibu wa capital gains tax chini ya Income Tax Act Tanzania — inategemea thamani ya mali na jinsi mchango ulivyoandikwa.",
    "hesabu ya kodi, wakati wa kulipa, na utaratibu wa TRA kwa hali hii maalum"
))

# ── SOFT REFUSALS — Transfer pricing (5) ──────────────────────────────────
pairs.append(soft(
    "Kampuni yangu ina mkopo kutoka kwa mwanzo wa kampuni mama — mkopo huo unahesabiwaje kwa transfer pricing?",
    "Mikopo kati ya kampuni washirika (related party loans) lazima iwe na riba inayolingana na bei ya soko (arm's length rate) chini ya kanuni za transfer pricing Tanzania.",
    "kiwango maalum cha riba kinachokubaliwa na TRA na jinsi ya kuandika nyaraka"
))
pairs.append(soft(
    "Ninauza bidhaa zangu kwa kampuni dada yangu nje ya Tanzania kwa bei nafuu — TRA inaweza kusema nini?",
    "TRA ina mamlaka ya kupinga bei za miamala kati ya kampuni washirika (related party transactions) ikiwa hazifuati bei ya soko (arm's length principle) chini ya kanuni za transfer pricing.",
    "kiwango halisi cha hatari, njia za kujilinda, na nyaraka zinazohitajika kwa TRA"
))
pairs.append(soft(
    "Ninajua kampuni zangu mbili zinahitaji arm's length pricing — lakini kwa sababu zangu za biashara, lazima nitoe punguzo kwa kampuni dada. Je, TRA itapinga?",
    "Punguzo la bei kwa sababu za biashara (commercial justification) linaweza kukubalika chini ya kanuni za transfer pricing lakini lazima liwe na nyaraka imara za kusaidia.",
    "mipaka ya kisheria, nyaraka zinazohitajika, na jinsi ya kupata makubaliano ya awali (advance pricing agreement) na TRA"
))
pairs.append(soft(
    "Kampuni yangu mama nje ya Tanzania inatoa dhamana (guarantee) kwa mkopo wangu — TRA inaona dhamana hii vipi?",
    "Dhamana ya kampuni mama (parent guarantee) kwa mikopo ya kampuni tanzu inaweza kuathiri tathmini ya transfer pricing chini ya kanuni za TRA.",
    "jinsi ya kuweka thamani ya dhamana na nyaraka zinazohitajika kwa TRA"
))
pairs.append(soft(
    "Transfer pricing documentation — ninapaswa kuandaa nini haswa na lini kuwasilisha TRA?",
    "Tanzania inahitaji nyaraka za transfer pricing kwa kampuni zinazofanya miamala na washirika (related parties) chini ya kanuni za Income Tax Act.",
    "kizingiti cha thamani cha miamala, muundo wa nyaraka, na tarehe maalum za kuwasilisha kwa TRA"
))

# ── SOFT REFUSALS — Stamp duty (5) ────────────────────────────────────────
pairs.append(soft(
    "Ninaingia mkataba wa ubia (partnership agreement) na mtu mwingine — stamp duty inatumika kwenye mkataba huu?",
    "Mikataba ya ushirika (partnership agreements) inaweza kuwa na wajibu wa stamp duty chini ya Stamp Duty Act Tanzania kulingana na maudhui ya mkataba.",
    "kiwango halisi, jinsi ya kusajili hati, na utaratibu wa kulipa TRA"
))
pairs.append(soft(
    "Ninanunua mitambo (machinery) kwa kampuni yangu — stamp duty inatumika kwenye mkataba wa ununuzi?",
    "Mikataba ya ununuzi wa mitambo na bidhaa inaweza kuwa na wajibu wa stamp duty chini ya Stamp Duty Act Tanzania kulingana na aina ya hati na thamani yake.",
    "kiwango halisi na aina za mikataba inayostahili au kusamehewa stamp duty"
))
pairs.append(soft(
    "Nikipewa mkopo na benki — agreement ya mkopo (loan agreement) ina stamp duty?",
    "Mikataba ya mikopo (loan agreements) kutoka benki na taasisi za fedha inaweza kuwa na wajibu wa stamp duty chini ya Stamp Duty Act Tanzania.",
    "kiwango maalum, jinsi inavyohesabika kwa mikopo ya thamani tofauti, na nani analipa"
))
pairs.append(soft(
    "Mikataba ya ushauri (consultancy agreements) inahitaji stamp duty Tanzania?",
    "Baadhi ya mikataba ya huduma (service agreements) inaweza kuwa na wajibu wa stamp duty chini ya Stamp Duty Act Tanzania kulingana na maudhui na thamani ya mkataba.",
    "aina maalum za mikataba inayohusika na kiwango cha stamp duty kinachofaa"
))
pairs.append(soft(
    "Kampuni yangu inatoa dhamana (corporate guarantee) kwa kampuni nyingine — dhamana hiyo ina stamp duty?",
    "Hati za dhamana (guarantee documents) na zana za dhamana za kampuni zinaweza kuwa na wajibu wa stamp duty chini ya Stamp Duty Act Tanzania.",
    "kiwango halisi, jinsi inavyohesabika kwa thamani ya dhamana, na utaratibu wa kulipa TRA"
))

assert len(pairs) == 50, f"Expected 50 pairs, got {len(pairs)}"

# Save to output file (overwrite/create)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    for pair in pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')

# Save checkpoint
ckpt = os.path.join(CHECKPOINT_DIR, "ckpt_050.jsonl")
with open(ckpt, 'w', encoding='utf-8') as f:
    for pair in pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')

print(f"Section 1 complete: {len(pairs)} pairs saved")
print(f"Output: {OUTPUT_FILE}")
print(f"Checkpoint: {ckpt}")

# Quick validation
hard_count = sum(1 for p in pairs if p['output'].startswith('Swali hili liko nje ya maarifa yangu ya sasa.'))
soft_count = sum(1 for p in pairs if not p['output'].startswith('Swali hili liko nje') and ('nje ya maarifa yangu' in p['output'] or 'swali hili liko nje' in p['output'].lower()))
no_phrase = sum(1 for p in pairs if 'nje ya maarifa yangu' not in p['output'] and 'swali hili liko nje' not in p['output'].lower())
print(f"\nValidation:")
print(f"  Hard refusals (start with phrase): {hard_count} (target 35)")
print(f"  Soft refusals (phrase present): {soft_count} (target 15)")
print(f"  Missing phrase entirely: {no_phrase} (target 0)")

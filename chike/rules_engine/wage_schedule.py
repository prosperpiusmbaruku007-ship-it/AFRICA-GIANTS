"""GN 605A Second Schedule — the 50 minimum-wage rates, and the resolver that decides
WHICH of them (if any) a user's own words identify.

Source: Government Notice No. 605A published 13/10/2025, the Labour Institutions (Minimum
Wage for Private Sector) Order 2025, made under Labour Institutions Act Cap. 300 s.39(1);
in force 1 January 2026; revokes GN No. 687 of 2022 (para 7). Gazette text extracted from
kazi.go.tz and committed at docs/domain_research/gn605a_2025_gazette_extract.txt so the
transcription below is auditable rather than trusted — verify_transcription() asserts every
one of the 250 rate figures back against it.

Transcribed by hand rather than parsed: the PDF interleaves the five period columns with the
sub-sector labels, and a silent mis-parse puts a wrong wage in front of an employer.

TWO THINGS THIS MODULE IS DELIBERATELY CAREFUL ABOUT
----------------------------------------------------
1. ITEM 16 IS NOT A DEFAULT. First Schedule item 16 ("Other sectors or areas not specified
   in this Order", TZS 175,000 monthly) is the rate for a sector the Order does not list. It
   is NOT the answer to "the user didn't say what work it is". Those need opposite answers —
   a rate, and a clarification — so `resolve` distinguishes UNLISTED from NONE and never
   infers UNLISTED from the absence of a cue.

   The UNLISTED cue table ships EMPTY, on purpose. Populating it needs a labour-law source,
   not a cue: the Order's Interpretation clause (para 3) defines only "domestic work",
   "agriculture", "employee", "employer", "private sector", "energy" and "mining operations".
   It does NOT define "Trade and finance sector", so whether e.g. a hair salon is item 16
   (175,000) or sector 12(a) "business" (200,500) is a classification the gazette does not
   settle — and a wage between those two figures gets the OPPOSITE verdict depending on which
   is chosen. Until a source settles it, such a question resolves to NONE and is clarified.

2. A SECTOR IS NOT A RATE. 12 of the 16 sectors carry more than one rate, the largest spread
   being TZS 532,500 (sector 12: business 200,500 -> commercial banks 733,000). Measured over
   22 authored employer phrasings, 5 of the 7 sector-only cases FLIP the lawfulness verdict
   across their candidate sub-rates. Guessing a sub-sector therefore returns the opposite
   legal answer, not a less precise one — so SECTOR is its own outcome and is clarified.

Pure data + string logic. No model, no network.
"""

import re
from decimal import Decimal

# Period columns, in the order the Order prints them.
PERIODS = ("hourly", "daily", "weekly", "fortnightly", "monthly")

# (sector_no, sub_letter, english_label, hourly, daily, weekly, fortnightly, monthly)
SCHEDULE = [
    (1, 'a', 'Crop or animal production and activities related to agriculture',
     897, 6_731, 40_386, 80_772, 175_000),
    (1, 'b', 'Forestry and deforestation of trees', 949, 7_115, 42_692, 85_385, 185_000),
    (1, 'c', 'Fishing and fish farming or aquaculture',
     1_538, 11_539, 69_231, 138_462, 300_000),
    (2, 'a', 'Hospital', 1_282, 9_615, 57_692, 115_385, 250_000),
    (2, 'b', 'Health centre', 1_231, 9_231, 55_385, 110_769, 240_000),
    (2, 'c', 'Polyclinic', 1_231, 9_231, 55_385, 110_769, 240_000),
    (2, 'd', 'Dispensary', 1_179, 8_846, 53_077, 106_154, 230_000),
    (2, 'e', 'Pharmacy', 1_231, 9_231, 55_385, 110_769, 240_000),
    (3, 'a', 'Programme, advertising and media', 1_482, 11_115, 66_692, 133_385, 289_000),
    (3, 'b', 'Telecommunication services', 3_303, 24_769, 148_615, 297_231, 644_000),
    (3, 'c', 'Call Centre', 1_949, 14_615, 87_692, 175_385, 380_000),
    (4, 'a', 'Domestic workers employed by diplomats and major businessmen',
     1_682, 12_615, 75_692, 151_385, 328_000),
    (4, 'b', 'Domestic workers employed by entitled officers',
     1_359, 10_192, 61_154, 122_308, 265_000),
    (4, 'c', 'Domestic workers not residing in the household of the employer',
     821, 6_154, 36_924, 73_848, 160_000),
    (4, 'd', 'Other domestic workers', 410, 3_077, 18_462, 36_923, 80_000),
    (5, 'a', 'Five star and four star hotels', 1_923, 14_423, 86_539, 173_077, 375_000),
    (5, 'b', 'Three star hotels', 1_154, 8_654, 51_923, 103_846, 225_000),
    (5, 'c', 'One/two star hotels, guest houses, bars and restaurants',
     1_000, 7_500, 45_000, 90_000, 195_000),
    (5, 'd', 'Tourist luggage porter', 1_154, 8_654, 51_923, 103_846, 225_000),
    (5, 'e', 'Tour guide', 1_641, 12_308, 73_846, 147_692, 320_000),
    (5, 'f', 'Hunting and related activities', 1_025, 7_692, 46_154, 92_308, 200_000),
    (6, 'a', 'Private security — international companies',
     1_497, 11_231, 67_385, 134_769, 292_000),
    (6, 'b', 'Private security — domestic companies', 1_010, 7_577, 45_462, 90_923, 197_000),
    (7, 'a', 'Energy — international companies', 3_928, 29_458, 176_746, 353_492, 765_900),
    (7, 'b', 'Energy — domestic companies', 1_523, 11_423, 68_539, 137_077, 297_000),
    (8, 'a', 'Aviation services', 2_554, 19_154, 114_923, 229_846, 498_000),
    (8, 'b', 'Freight clearing and forwarding', 2_379, 17_846, 107_077, 214_154, 464_000),
    (8, 'c', 'Inland transport services', 2_044, 15_327, 91_962, 183_923, 398_500),
    (8, 'd', 'Postal and courier services', 1_474, 11_058, 66_346, 132_692, 287_500),
    (9, 'a', 'Construction — Contractors Class I', 2_641, 19_808, 118_846, 237_692, 515_000),
    (9, 'b', 'Construction — Contractors Class II-IV',
     2_382, 17_865, 107_192, 214_385, 464_500),
    (9, 'c', 'Construction — Contractors Class V-VII',
     2_044, 15_327, 91_962, 183_924, 398_500),
    (10, 'a', 'Mining and prospecting minerals', 3_564, 26_731, 160_385, 320_769, 695_000),
    (10, 'b', 'Primary mining licence', 2_039, 15_292, 91_754, 183_508, 397_600),
    (10, 'c', 'Mining dealer licence', 3_051, 22_885, 137_308, 274_615, 595_000),
    (10, 'd', 'Mining brokers licence', 1_710, 12_827, 76_962, 153_924, 333_500),
    (11, 'a', 'Pre-primary and primary schools', 1_418, 10_635, 63_810, 127_620, 276_500),
    (11, 'b', 'Secondary schools', 1_443, 10_819, 64_914, 129_831, 281_300),
    (11, 'c', 'Colleges or vocational training institutes',
     1_444, 10_827, 64_962, 129_924, 281_500),
    (11, 'd', 'Higher Education Institutions', 1_542, 11_565, 69_390, 138_780, 300_700),
    (12, 'a', 'Trade and finance — business', 1_028, 7_712, 46_269, 92_539, 200_500),
    (12, 'b(i)', 'Commercial banks', 3_759, 28_192, 169_154, 338_308, 733_000),
    (12, 'b(ii)', 'Community services banks', 3_582, 26_862, 161_169, 322_338, 698_400),
    (12, 'b(iii)', 'Micro credit financial services', 3_585, 26_885, 161_308, 322_615, 699_000),
    (12, 'b(iv)', 'Insurance companies', 3_588, 26_912, 161_472, 322_944, 699_700),
    (12, 'b(v)', 'Other financial institutions', 3_587, 26_904, 161_423, 322_846, 699_500),
    (13, '', 'Industrial sector', 1_025, 7_692, 46_154, 92_308, 200_000),
    (14, '', 'Sport, arts, entertainment and gaming', 1_474, 11_058, 66_348, 132_696, 287_500),
    (15, '', 'Waste collection, processing and disposal', 967, 7_250, 43_500, 87_000, 188_500),
    (16, '', 'Any other sector or area not specified in this Order',
     897, 6_731, 40_384, 80_769, 175_000),
]

# First Schedule sector names, for clarification copy that has to name the candidates.
SECTOR_NAMES_SW = {
    1: 'kilimo', 2: 'afya', 3: 'mawasiliano', 4: 'kazi za nyumbani',
    5: 'hoteli na ukarimu', 6: 'ulinzi binafsi', 7: 'nishati', 8: 'usafirishaji',
    9: 'ujenzi', 10: 'madini', 11: 'shule binafsi', 12: 'biashara na fedha',
    13: 'viwanda', 14: 'michezo, sanaa na burudani', 15: 'ukusanyaji taka',
    16: 'sekta isiyoorodheshwa',
}

# Swahili sub-sector labels, used ONLY to list the options back to a user whose words
# identified a sector but not a row. Never used to pick a rate.
SUB_LABELS_SW = {
    (1, 'a'): 'mazao au mifugo', (1, 'b'): 'misitu', (1, 'c'): 'uvuvi',
    (2, 'a'): 'hospitali', (2, 'b'): 'kituo cha afya', (2, 'c'): 'polikliniki',
    (2, 'd'): 'zahanati', (2, 'e'): 'duka la dawa',
    (3, 'a'): 'matangazo na habari', (3, 'b'): 'kampuni ya simu',
    (3, 'c'): 'kituo cha simu (call centre)',
    (4, 'a'): 'mwajiri ni mwanadiplomasia au mfanyabiashara mkubwa',
    (4, 'b'): 'mwajiri ni afisa mwenye stahili',
    (4, 'c'): 'haishi nyumbani kwa mwajiri', (4, 'd'): 'kazi nyingine za nyumbani',
    (5, 'a'): 'hoteli ya nyota nne au tano', (5, 'b'): 'hoteli ya nyota tatu',
    (5, 'c'): 'hoteli ya nyota moja/mbili, gesti, baa au mgahawa',
    (5, 'd'): 'mbeba mizigo wa watalii', (5, 'e'): 'mwongoza watalii',
    (5, 'f'): 'uwindaji',
    (6, 'a'): 'kampuni ya kimataifa', (6, 'b'): 'kampuni ya ndani',
    (7, 'a'): 'kampuni ya kimataifa', (7, 'b'): 'kampuni ya ndani',
    (8, 'a'): 'usafiri wa anga', (8, 'b'): 'uwakala wa forodha',
    (8, 'c'): 'usafiri wa nchi kavu', (8, 'd'): 'posta na kozi',
    (9, 'a'): 'mkandarasi daraja la I', (9, 'b'): 'mkandarasi daraja la II-IV',
    (9, 'c'): 'mkandarasi daraja la V-VII',
    (10, 'a'): 'uchimbaji na utafutaji madini', (10, 'b'): 'leseni ya uchimbaji mdogo',
    (10, 'c'): 'leseni ya udalali wa madini', (10, 'd'): 'leseni ya ubroka wa madini',
    (11, 'a'): 'chekechea na msingi', (11, 'b'): 'sekondari',
    (11, 'c'): 'chuo au VETA', (11, 'd'): 'taasisi ya elimu ya juu',
    (12, 'a'): 'biashara', (12, 'b(i)'): 'benki ya biashara',
    (12, 'b(ii)'): 'benki ya huduma za jamii', (12, 'b(iii)'): 'mikopo midogo',
    (12, 'b(iv)'): 'kampuni ya bima', (12, 'b(v)'): 'taasisi nyingine za fedha',
}

BY_ROW = {(no, sub): row for row in SCHEDULE for no, sub in [(row[0], row[1])]}
BY_SECTOR = {}
for _row in SCHEDULE:
    BY_SECTOR.setdefault(_row[0], []).append(_row)

ITEM_16 = BY_ROW[(16, '')]

# The Order's lowest MONTHLY rate (4(d), other domestic workers). Used as the plausibility
# floor for reading an unlabelled figure as a monthly wage: below this, the figure is as
# likely a daily or weekly wage, and the period is asked for instead of assumed.
LOWEST_MONTHLY = min(Decimal(row[-1]) for row in SCHEDULE)


def rate(row, period="monthly") -> Decimal:
    """The Order's figure for one row in one period column."""
    return Decimal(row[3 + PERIODS.index(period)])


def label_sw(no, sub) -> str:
    """Swahili description of a row, for the answer text."""
    if sub and (no, sub) in SUB_LABELS_SW:
        return f"{SECTOR_NAMES_SW[no]} — {SUB_LABELS_SW[(no, sub)]}"
    return SECTOR_NAMES_SW.get(no, "")


# ─── cues ────────────────────────────────────────────────────────────────────────────
#
# Keyed on the words an EMPLOYER uses about a worker ("kibarua wa shamba", "mhudumu wa
# baa"), not on the Order's English labels. A cue that identifies only the SECTOR carries
# sub=None and is clarified, never resolved to that sector's cheapest or commonest row.
#
# SHIPPED NARROW on purpose. Over 22 authored phrasings this resolves 11 to a row and
# clarifies the rest. Every cue added to chase coverage buys a chance of resolving
# CONFIDENTLY INTO THE WRONG ROW, and the 5-of-7 verdict-flip rate says that costs a
# reversed legal answer rather than a rounding error. "Hoteli ya nyota ngapi?" is what a
# competent advisor asks; it is a good answer, not a failure to answer.
_CUES = [
    # sector 1 — agriculture. Note para 3: "agriculture" INCLUDES forestry and fishing, so
    # the three sub-rows are all 'kilimo' in ordinary speech and must be told apart by the
    # specific activity, not by the word 'kilimo' itself.
    (r'\b(shamba|kilimo|mkulima|mazao|mifugo|ufugaji wa (?:ng.ombe|kuku|mbuzi))\b', 1, 'a'),
    (r'\b(misitu|ukataji wa miti|upandaji miti)\b', 1, 'b'),
    (r'\b(uvuvi|mvuvi|ufugaji wa samaki)\b', 1, 'c'),
    # sector 2 — health
    (r'\bhospitali\b', 2, 'a'),
    (r'\bkituo cha afya\b', 2, 'b'),
    (r'\b(polikliniki|kliniki)\b', 2, 'c'),
    (r'\bzahanati\b', 2, 'd'),
    (r'\b(duka la dawa|famasi)\b', 2, 'e'),
    # sector 3 — communications
    (r'\b(kituo cha matangazo|vyombo vya habari|redio|televisheni)\b', 3, 'a'),
    (r'\b(kampuni ya simu|mtandao wa simu)\b', 3, 'b'),
    (r'\b(call cent|kituo cha simu)', 3, 'c'),
    # sector 4 — domestic work. SECTOR-ONLY by design: the four rows turn on WHO the
    # employer is and whether the worker resides in the household (80,000 .. 328,000), and
    # no ordinary phrasing for the worker settles that.
    (r'\b(mfanyakazi wa ndani|dada wa kazi|house ?girl|house ?boy|mtumishi wa nyumbani|'
     r'yaya|mlezi wa watoto)\b', 4, None),
    # sector 5 — hotel and hospitality
    (r'\b(nyota (?:nne|tano)|four star|five star)\b', 5, 'a'),
    (r'\b(nyota tatu|three star)\b', 5, 'b'),
    (r'\b(baa|mgahawa|migahawa|gesti|guest ?house|nyota (?:moja|mbili))\b', 5, 'c'),
    (r'\b(mbeba mizigo|porter)\b', 5, 'd'),
    (r'\b(mwongoza watalii|tour ?guide)\b', 5, 'e'),
    (r'\buwindaji\b', 5, 'f'),
    (r'\b(hoteli|hotel)\b', 5, None),                  # star rating unknown -> clarify
    # sector 6 — private security. International vs domestic is unknowable from the worker.
    (r'\b(mlinzi|walinzi|ulinzi|sekyuriti)\b', 6, None),
    # sector 7 — energy
    (r'\b(nishati|mafuta na gesi|kampuni ya umeme)\b', 7, None),
    # sector 8 — transport
    (r'\b(usafiri wa anga|shirika la ndege)\b', 8, 'a'),
    (r'\b(uwakala wa forodha|clearing na forwarding)\b', 8, 'b'),
    (r'\b(dereva wa (?:lori|basi|malori|daladala)|lori|malori|usafirishaji wa nchi kavu)\b',
     8, 'c'),
    (r'\b(posta|kampuni ya kozi|courier)\b', 8, 'd'),
    # sector 9 — construction. The contractor CLASS decides the rate (398,500 .. 515,000).
    (r'\b(ujenzi|mjenzi|mkandarasi)\b', 9, None),
    # sector 10 — mining. The LICENCE type decides the rate (333,500 .. 695,000).
    (r'\b(mgodi|migodi|uchimbaji madini|mchimbaji)\b', 10, None),
    # sector 11 — private schools
    (r'\b(shule ya msingi|chekechea)\b', 11, 'a'),
    (r'\bshule ya sekondari\b', 11, 'b'),
    (r'\b(chuo cha ufundi|veta)\b', 11, 'c'),
    (r'\b(shule binafsi|shule yangu)\b', 11, None),
    # sector 12 — trade and finance
    (r'\bbenki ya biashara\b', 12, 'b(i)'),
    (r'\bkampuni ya bima\b', 12, 'b(iv)'),
    (r'\b(mikopo midogo|microfinance)\b', 12, 'b(iii)'),
    # 'duka la dawa' is a PHARMACY (2e, 240,000) and contains 'duka' (12a, 200,500). Without
    # the exclusion both cues fire, the sectors conflict, and a perfectly resolvable question
    # gets the "tell me what work" clarification. Found by the exhaustive cue-collision pass
    # in scratch/mw_r17.py, not by authoring — the collision is between two cues that are each
    # correct on their own, which is not a shape you find by reading the table.
    (r'\b(duka(?!\s+la\s+dawa)|genge|biashara ya rejareja|muuzaji dukani)\b', 12, 'a'),
    (r'\bbenki\b', 12, None),                          # which kind of bank -> clarify
    # sectors 13-15 have a single rate each, so a sector cue IS a row cue.
    (r'\b(kiwanda|viwanda)\b', 13, ''),
    (r'\b(michezo|sanaa|burudani|kamari|kasino)\b', 14, ''),
    (r'\b(ukusanyaji taka|kukusanya taka|usafi wa mazingira)\b', 15, ''),
]

# UNLISTED — occupations CONFIRMED absent from the Order, which therefore take item 16.
# SHIPS EMPTY. See the module docstring: the Order does not define the scope of "Trade and
# finance sector", so "this occupation is not in the Order" is a legal classification and
# not something a cue can assert. An empty table means such questions resolve to NONE and
# are clarified — the never-guess outcome — rather than being answered with TZS 175,000,
# which is a real gazette figure answering a question we cannot answer.
_UNLISTED_CUES: list = []

ROW, SECTOR, UNLISTED, NONE = "row", "sector", "unlisted", "none"


def resolve(text):
    """-> (outcome, value) where outcome is one of ROW / SECTOR / UNLISTED / NONE.

    ROW      -> value is (sector_no, sub_letter); the rate is determined.
    SECTOR   -> value is sector_no; the rate is NOT determined — clarify the sub-sector.
    UNLISTED -> value is None; the occupation is named and absent from the Order -> item 16.
    NONE     -> value is None; nothing identifies the work -> never-guess.

    Conflicting SECTORS is NONE, not first-wins: "dereva wa hoteli" is a real thing an
    employer says and the two candidate rates differ by TZS 203,500. Conflicting SUB-sectors
    within one sector degrades to SECTOR, which clarifies.
    """
    t = text.lower()
    hits = [(no, sub) for pat, no, sub in _CUES if re.search(pat, t)]
    if not hits:
        if any(re.search(p, t) for p in _UNLISTED_CUES):
            return UNLISTED, None
        return NONE, None
    sectors = {no for no, _ in hits}
    if len(sectors) > 1:
        return NONE, None
    no = sectors.pop()
    subs = {sub for _, sub in hits if sub is not None}
    if len(subs) == 1:
        return ROW, (no, subs.pop())
    return SECTOR, no


def sector_options_sw(no):
    """Swahili list of a sector's sub-sectors, for the clarification that asks which."""
    return [SUB_LABELS_SW.get((row[0], row[1]), row[2]) for row in BY_SECTOR[no]]


def verify_transcription(path='docs/domain_research/gn605a_2025_gazette_extract.txt'):
    """Assert every rate figure in SCHEDULE appears in the extracted gazette text.

    250 hand-transcribed numbers is exactly where one wrong digit hides, and the consequence
    is a wrong wage told to an employer. Cheap, and not optional — tests/test_minimum_wage.py
    runs it.
    """
    with open(path, encoding='utf-8') as fh:
        text = fh.read()
    present = {int(m.replace(',', '')) for m in re.findall(r'\b\d[\d,]{2,}\b', text)}
    missing = []
    for row in SCHEDULE:
        for period, value in zip(PERIODS, row[3:]):
            if value not in present:
                missing.append((row[0], row[1], period, value))
    return missing

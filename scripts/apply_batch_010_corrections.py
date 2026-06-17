"""
Apply batch_010 corrections per founder review:
- Correction 2: WCF threshold fix (pair 90)
- Correction 7: Prepend basic principles to refusal pairs (pairs 1-5, 6-10, 21-25, 26-30)
Regenerate affected checkpoints after changes.
"""
import json, os

BATCH = "datasets/tier1a/raw_sources/raw_pairs_batch_010.jsonl"
CP_DIR = "datasets/tier1a/raw_sources/batch_010_checkpoints"

# --- Principle texts (Correction 7) ---
CAPITAL_GAINS_PRINCIPLE = (
    "Faida inayotokana na uuzaji wa mali kama ardhi, hisa, au majengo inaweza kuwa "
    "taxable chini ya Income Tax Act Tanzania. Hesabu halisi inategemea thamani ya "
    "ununuzi (cost base), thamani ya uuzaji, na hali yako kama mkazi au asiye mkazi. "
)
TRANSFER_PRICING_PRINCIPLE = (
    "Kanuni ya msingi ya transfer pricing Tanzania ni arm's length principle katika "
    "Income Tax Act Sehemu 33 — miamala kati ya kampuni zinazohusiana lazima ifanane "
    "na bei za soko. Kwa uchambuzi wa kesi yako: "
)
STAMP_DUTY_PRINCIPLE = (
    "Stamp duty inatumika kwa uhamisho wa mali Tanzania. Viwango na taratibu halisi "
    "vinategemea aina ya mali na thamani yake inayotathminiwa na mthamini aliyesajiliwa. "
)
MINERAL_ROYALTIES_PRINCIPLE = (
    "Royalties za madini zinasimamiwa na Sheria ya Madini Tanzania na zinategemea "
    "aina ya madini yanayochimbwa. "
)

# Pair index ranges (0-based)
CAPITAL_GAINS = list(range(0, 5))      # pairs 1-5
TRANSFER_PRICING = list(range(5, 10))  # pairs 6-10
STAMP_DUTY = list(range(20, 25))       # pairs 21-25
MINERAL_ROY = list(range(25, 30))      # pairs 26-30

# --- WCF threshold fix (Correction 2) ---
WCF_PAIR_IDX = 89  # pair 90, 0-indexed
WCF_NEW_OUTPUT = (
    "Ukiwa na wafanyakazi 10 au zaidi, lazima ulipe ZOTE MBILI — SDL na WCF. "
    "Hata hivyo, kuna tofauti muhimu ya kizingiti:\n\n"
    "SDL = 3.5% ya mishahara ya fedha — inalipwa TRA — mafunzo ya ujuzi "
    "— inahitaji wafanyakazi 10+.\n"
    "WCF = 0.5% ya mishahara ya fedha — inalipwa Mamlaka ya WCF — fidia ya majeruhi "
    "wa kazi — inahitajika mara tu unapoajiri mfanyakazi MMOJA (hata kabla ya kufikia 10).\n\n"
    "Kwa hivyo: WCF inatumika kuanzia mfanyakazi wa kwanza — si kutoka 10. "
    "SDL inatumika ukiwa na wafanyakazi 10+. Hazilipwi pamoja kwa mtu mmoja — "
    "TRA inapokea SDL na Mamlaka ya WCF inapokea WCF tofauti. "
    "Thibitisha na TRA kupitia tra.go.tz na Mamlaka ya WCF kupitia wcf.go.tz."
)

# Load batch
with open(BATCH, encoding="utf-8") as f:
    pairs = [json.loads(l) for l in f if l.strip()]

assert len(pairs) == 90, f"Expected 90 pairs, got {len(pairs)}"

changes = []

# Apply Correction 7 — prepend principles
for idx in CAPITAL_GAINS:
    old = pairs[idx]["output"]
    pairs[idx]["output"] = CAPITAL_GAINS_PRINCIPLE + old
    changes.append(f"Pair {idx+1}: prepended capital gains principle")

for idx in TRANSFER_PRICING:
    old = pairs[idx]["output"]
    pairs[idx]["output"] = TRANSFER_PRICING_PRINCIPLE + old
    changes.append(f"Pair {idx+1}: prepended transfer pricing principle")

for idx in STAMP_DUTY:
    old = pairs[idx]["output"]
    pairs[idx]["output"] = STAMP_DUTY_PRINCIPLE + old
    changes.append(f"Pair {idx+1}: prepended stamp duty principle")

for idx in MINERAL_ROY:
    old = pairs[idx]["output"]
    pairs[idx]["output"] = MINERAL_ROYALTIES_PRINCIPLE + old
    changes.append(f"Pair {idx+1}: prepended mineral royalties principle")

# Apply Correction 2 — WCF threshold
pairs[WCF_PAIR_IDX]["output"] = WCF_NEW_OUTPUT
changes.append(f"Pair {WCF_PAIR_IDX+1}: fixed WCF threshold (all employers, not 10+)")

# Write corrected batch
with open(BATCH, "w", encoding="utf-8") as f:
    for p in pairs:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

# Regenerate checkpoints
checkpoints = {
    "checkpoint_001.jsonl": pairs[0:30],   # pairs 1-30 → Correction 7 applies
    "checkpoint_002.jsonl": pairs[30:60],  # pairs 31-60 → no changes
    "checkpoint_003.jsonl": pairs[60:90],  # pairs 61-90 → Correction 2 applies
}
for fname, cp_pairs in checkpoints.items():
    cp_path = os.path.join(CP_DIR, fname)
    with open(cp_path, "w", encoding="utf-8") as f:
        for p in cp_pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"Corrections applied: {len(changes)}")
for c in changes:
    print(f"  {c}")
print()
print(f"Checkpoints regenerated:")
for fname in checkpoints:
    print(f"  {os.path.join(CP_DIR, fname)}")
print()

# Verify pair 90 no longer says "10 na zaidi" for WCF
p90 = pairs[89]["output"]
if "Zote mbili zinatumika kwa waajiri wenye wafanyakazi 10 na zaidi" in p90:
    print("ERROR: WCF pair 90 still has wrong threshold text")
else:
    print("PASS: WCF pair 90 threshold corrected")

# Verify principle pairs start correctly
test_cases = [
    (0, "Faida inayotokana"),
    (5, "Kanuni ya msingi ya transfer pricing"),
    (20, "Stamp duty inatumika"),
    (25, "Royalties za madini"),
]
for idx, expected_start in test_cases:
    if pairs[idx]["output"].startswith(expected_start):
        print(f"PASS: Pair {idx+1} starts with principle")
    else:
        print(f"FAIL: Pair {idx+1} does not start with expected principle")
        print(f"  Got: {pairs[idx]['output'][:80]}")

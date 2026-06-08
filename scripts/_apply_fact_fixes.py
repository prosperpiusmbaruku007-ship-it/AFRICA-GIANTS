#!/usr/bin/env python3
"""
Context-aware fix script for batch_002_cleaned.jsonl.
Applies each of the 7 fixes ONLY where the context genuinely warrants it.
"""
import json, re, sys

INPUT  = "datasets/tier1a/cleaned_pairs/batch_002_cleaned.jsonl"
OUTPUT = "datasets/tier1a/cleaned_pairs/batch_002_cleaned.jsonl"

CLARIFICATION_SW = (
    " GN 487A si kuhusu vibali vya makazi — "
    "ni amri ya biashara inayozuia shughuli 15 kwa wasio raia."
)
CLARIFICATION_EN = (
    " GN 487A is not about residence permits — "
    "it is a business prohibition order banning 15 activities for non-citizens."
)

changes = []

def fix1_gn487a(p):
    """Add GN487A clarification ONLY if the pair explicitly discusses GN487A
    AND the answer conflates it with residence permits."""
    q_sw = p.get("question_sw", "")
    a_sw = p.get("answer_sw", "")
    a_en = p.get("answer_en", "")
    combined = (q_sw + " " + a_sw + " " + a_en).lower()

    # Must explicitly mention GN 487A
    if "gn 487a" not in combined and "gn487a" not in combined:
        return False

    # Must have the conflating pattern in the answer
    answer_lower = (a_sw + " " + a_en).lower()
    conflates = (
        "kibali cha makazi" in answer_lower and
        # Only if the pair is ABOUT residence permits re: GN487A, not just
        # mentioning GN487A as a side note in a work-permit pair
        ("gn 487a" in a_sw.lower() or "gn 487a" in a_en.lower()) and
        # GN487A + residence permit language together in the answer
        any(pat in answer_lower for pat in ["kibali cha makazi", "residence permit"])
    )
    if not conflates:
        return False

    # Don't add if clarification already present
    if "amri ya biashara" in a_sw.lower():
        return False

    p["answer_sw"] += CLARIFICATION_SW
    p["answer_en"] += CLARIFICATION_EN
    return True


def fix2_gn605a_date(p):
    """Change 'Julai 2025'/'July 2025' to 'Januari 2026'/'January 2026'
    ONLY in sentences where GN 605A (private sector) is the subject of the
    effective date — not for Finance Act 2025 or GN 487A contexts."""
    a_sw = p.get("answer_sw", "")
    a_en = p.get("answer_en", "")
    changed = False

    # Only look for sentences where GN 605A is explicitly the subject of
    # 'ilianza' / 'effective' / 'kuanzia' AND the date is July 2025
    # Pattern: GN 605A ... Julai 2025 (in same sentence)
    sw_sentences = re.split(r'[.!?]', a_sw)
    new_sw_sentences = []
    for sent in sw_sentences:
        if re.search(r'gn\s*605a', sent, re.IGNORECASE):
            orig = sent
            sent = re.sub(r'\bJulai 2025\b', 'Januari 2026', sent)
            if sent != orig:
                changed = True
        new_sw_sentences.append(sent)
    if changed:
        p["answer_sw"] = '.'.join(new_sw_sentences)

    en_sentences = re.split(r'[.!?]', a_en)
    new_en_sentences = []
    for sent in en_sentences:
        if re.search(r'gn\s*605a', sent, re.IGNORECASE):
            orig = sent
            sent = re.sub(r'\bJuly 2025\b', 'January 2026', sent)
            if sent != orig:
                changed = True
        new_en_sentences.append(sent)
    if changed:
        p["answer_en"] = '.'.join(new_en_sentences)

    return changed


def fix3_min_turnover(p):
    """Change 0.5% to 1% ONLY in minimum turnover tax sentences.
    Do NOT change WCF rate (which is correctly 0.5%)."""
    a_sw = p.get("answer_sw", "")
    a_en = p.get("answer_en", "")
    changed = False

    # Minimum turnover tax keywords (Swahili)
    mt_sw = r'(turnover|mapato ghafi|kodi ndogo ya chini|minimum tax|asilimia 0\.5 ya mapato)'
    # WCF keywords — skip these sentences
    wcf_sw = r'(wcf|workers compensation)'

    sw_sentences = re.split(r'(?<=[.!?])\s+', a_sw)
    new_sw = []
    for sent in sw_sentences:
        if re.search(mt_sw, sent, re.IGNORECASE) and not re.search(wcf_sw, sent, re.IGNORECASE):
            orig = sent
            sent = re.sub(r'\basilimia 0\.5\b', 'asilimia 1', sent)
            sent = re.sub(r'\b0\.5%\b', '1%', sent)
            sent = re.sub(r'\b0\.5 percent\b', '1 percent', sent)
            if sent != orig:
                changed = True
                # Add effective date if not present
                if 'julai 2025' not in sent.lower() and '1 july 2025' not in sent.lower():
                    sent = sent.rstrip()
                    if not sent.endswith('.'):
                        sent += '.'
                    sent += ' Kuanzia 1 Julai 2025.'
        new_sw.append(sent)
    if changed:
        p["answer_sw"] = ' '.join(new_sw)

    mt_en = r'(turnover|gross revenue|minimum tax|0\.5% of)'
    wcf_en = r'(wcf|workers compensation)'

    en_sentences = re.split(r'(?<=[.!?])\s+', a_en)
    new_en = []
    for sent in en_sentences:
        if re.search(mt_en, sent, re.IGNORECASE) and not re.search(wcf_en, sent, re.IGNORECASE):
            orig = sent
            sent = re.sub(r'\b0\.5%\b', '1%', sent)
            sent = re.sub(r'\b0\.5 per ?cent\b', '1 percent', sent)
            if sent != orig:
                # Add effective date if not present
                if '1 july 2025' not in sent.lower() and 'july 2025' not in sent.lower():
                    sent = sent.rstrip()
                    if not sent.endswith('.'):
                        sent += '.'
                    sent += ' Effective 1 July 2025.'
        new_en.append(sent)
    if changed:
        p["answer_en"] = ' '.join(new_en)

    return changed


def fix4_wht_deadline(p):
    """Change 30-day WHT deadline ONLY in withholding_tax subdomain answers
    where the 30 days clearly refers to WHT remittance (not objections,
    not VAT registration, not stamp duty stamping)."""
    subdomain = p.get("subdomain", "")
    # Only apply to withholding_tax pairs
    if "withholding" not in subdomain.lower():
        return False
    # Check the answer mentions WHT remittance deadline (not objection)
    a_sw = p.get("answer_sw", "")
    a_en = p.get("answer_en", "")
    combined = (a_sw + " " + a_en).lower()
    # Must be about WHT remittance, not objection/appeal/registration
    if any(word in combined for word in ["pingamizi", "objection", "rufaa", "appeal",
                                          "kusajili", "register", "stempu", "stamp"]):
        return False
    # Apply only if siku 30 / 30 days appears in WHT remittance context
    changed = False
    if "siku 30" in a_sw:
        # Make sure it's not already correct
        if "siku 7" not in a_sw:
            p["answer_sw"] = a_sw.replace(
                "siku 30", "siku 7 baada ya mwisho wa mwezi"
            )
            changed = True
    if "30 days" in a_en:
        if "7 days" not in a_en:
            p["answer_en"] = a_en.replace(
                "30 days", "7 days after month end"
            )
            changed = True
    return changed


def fix5_vat_threshold(p):
    """Change TZS 50,000,000 to TZS 100,000,000 per 6 months ONLY in
    VAT registration threshold context — not profit/capex examples."""
    a_sw = p.get("answer_sw", "")
    a_en = p.get("answer_en", "")
    subdomain = p.get("subdomain", "")

    # Only apply in VAT registration subdomain
    if "vat" not in subdomain.lower() and "vat" not in p.get("domain","").lower():
        return False
    # Must be about registration threshold
    combined = (a_sw + " " + a_en).lower()
    if "kizingiti" not in combined and "threshold" not in combined and "registration" not in combined:
        return False
    # Must mention TZS 50M as a threshold (not a profit/capex example)
    if re.search(r'faida|profit|mashine|machine|msingi wa mtaji', combined):
        return False

    changed = False
    if "50,000,000" in a_sw:
        p["answer_sw"] = a_sw.replace(
            "TZS 50,000,000", "TZS 100,000,000 kwa miezi 6"
        )
        changed = True
    if "50,000,000" in a_en:
        p["answer_en"] = a_en.replace(
            "TZS 50,000,000", "TZS 100,000,000 per 6 months"
        )
        changed = True
    return changed


def fix6_commissioner_deadline(p):
    """Change 'miezi 3'/'3 months' to 'miezi 6'/'6 months' ONLY in
    sentences about TRA Commissioner objection determination timeline.
    Do NOT change imprisonment penalty references."""
    a_sw = p.get("answer_sw", "")
    a_en = p.get("answer_en", "")
    changed = False

    # Only apply in tax_disputes subdomain or objections context
    subdomain = p.get("subdomain", "")
    combined = (a_sw + " " + a_en).lower()
    if "kamishna" not in combined and "commissioner" not in combined:
        return False
    if "pingamizi" not in combined and "objection" not in combined:
        return False

    sw_sentences = re.split(r'(?<=[.!?])\s+', a_sw)
    new_sw = []
    for sent in sw_sentences:
        sent_lower = sent.lower()
        # Only change if sentence is about Commissioner determination time
        if any(w in sent_lower for w in ["kamishna", "commissioner"]) and \
           any(w in sent_lower for w in ["pingamizi", "objection", "uamuzi", "determine"]) and \
           not any(w in sent_lower for w in ["kifungo", "imprisonment", "gerezani", "faini", "fine"]):
            orig = sent
            sent = re.sub(r'\bmiezi 3\b', 'miezi 6', sent)
            sent = re.sub(r'\bmiezi tatu\b', 'miezi sita', sent)
            if sent != orig:
                changed = True
        new_sw.append(sent)
    if changed:
        p["answer_sw"] = ' '.join(new_sw)

    en_sentences = re.split(r'(?<=[.!?])\s+', a_en)
    new_en = []
    for sent in en_sentences:
        sent_lower = sent.lower()
        if any(w in sent_lower for w in ["commissioner"]) and \
           any(w in sent_lower for w in ["objection", "determine", "determination"]) and \
           not any(w in sent_lower for w in ["imprisonment", "prison", "fine", "penalty"]):
            orig = sent
            sent = re.sub(r'\b3 months\b', '6 months', sent)
            sent = re.sub(r'\bthree months\b', 'six months', sent)
            if sent != orig:
                changed = True
        new_en.append(sent)
    if changed:
        p["answer_en"] = ' '.join(new_en)

    return changed


def fix7_paye_penalty(p):
    """Change 5% PAYE late penalty to 2.5% ONLY in PAYE penalty context.
    Do NOT change NSSF 5% penalty (which is correct)."""
    a_sw = p.get("answer_sw", "")
    a_en = p.get("answer_en", "")
    subdomain = p.get("subdomain", "")
    combined = (a_sw + " " + a_en).lower()

    # Skip NSSF pairs
    if "nssf" in subdomain.lower():
        return False
    # Skip if in NSSF context
    if "nssf" in combined and "paye" not in combined:
        return False

    changed = False
    # Pattern: "faini ya 5%" in PAYE context
    if "faini ya 5%" in a_sw and ("paye" in combined or "mshahara" in combined):
        p["answer_sw"] = a_sw.replace("faini ya 5%", "asilimia 2.5")
        changed = True
    # Pattern: "5% of the unpaid" — only if NOT already "2.5% of the unpaid"
    if "5% of the unpaid" in a_en and "2.5%" not in a_en:
        p["answer_en"] = a_en.replace("5% of the unpaid", "2.5% of the unpaid")
        changed = True

    return changed


def main():
    pairs = []
    with open(INPUT, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                pairs.append(json.loads(line))

    total_changed = 0
    fix_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

    for p in pairs:
        pid = p["id"]
        pair_changed = False

        if fix1_gn487a(p):
            fix_counts[1] += 1
            pair_changed = True
            changes.append(f"FIX1 gn487a [{pid}]")

        if fix2_gn605a_date(p):
            fix_counts[2] += 1
            pair_changed = True
            changes.append(f"FIX2 gn605a_date [{pid}]")

        if fix3_min_turnover(p):
            fix_counts[3] += 1
            pair_changed = True
            changes.append(f"FIX3 min_turnover [{pid}]")

        if fix4_wht_deadline(p):
            fix_counts[4] += 1
            pair_changed = True
            changes.append(f"FIX4 wht_deadline [{pid}]")

        if fix5_vat_threshold(p):
            fix_counts[5] += 1
            pair_changed = True
            changes.append(f"FIX5 vat_thresh [{pid}]")

        if fix6_commissioner_deadline(p):
            fix_counts[6] += 1
            pair_changed = True
            changes.append(f"FIX6 obj_deadline [{pid}]")

        if fix7_paye_penalty(p):
            fix_counts[7] += 1
            pair_changed = True
            changes.append(f"FIX7 paye_penalty [{pid}]")

        if pair_changed:
            total_changed += 1

    # Write back
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"Total pairs changed: {total_changed} of {len(pairs)}")
    print(f"Fix breakdown: FIX1={fix_counts[1]} FIX2={fix_counts[2]} "
          f"FIX3={fix_counts[3]} FIX4={fix_counts[4]} FIX5={fix_counts[5]} "
          f"FIX6={fix_counts[6]} FIX7={fix_counts[7]}")
    for c in changes:
        print(" ", c)

if __name__ == "__main__":
    main()

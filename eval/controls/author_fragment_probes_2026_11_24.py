# -*- coding: utf-8 -*-
"""Authors eval/decomposition_gate/fragment_merge_probes_2026_11_24.jsonl (R17: probes BOTH WAYS; R21: authored by the rule's author, so a lower bound).
`parts` is the number of sub-queries decompose_query must return: 1 = the fragment is merged (the message stays whole), 2 = a genuine two-part question still splits.
    python eval/controls/author_fragment_probes_2026_11_24.py"""
import io, json, os
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "decomposition_gate", "fragment_merge_probes_2026_11_24.jsonl")
P = []
def add(pid, msg, parts, why):
    P.append({"id": pid, "message": msg, "parts": parts, "guards_against": why})

# --- must MERGE (a dependent fragment: it has no frame of its own)
add("fm_01", "Huduma za afya zinatozwa VAT? Na dawa je?", 1, "FOUNDING SPECIMEN (live, 37cdf9d): 'Na dawa je?' alone was answered 'Kwa sababu sisi ni duka la dawa ... EFD'.")
add("fm_02", "SDL inalipwa lini? Na PAYE je?", 1, "follow-up naming another levy: no frame of its own.")
add("fm_03", "Leseni ya biashara inaisha lini? Na ada yake je?", 1, "four-word fragment ending in 'je'.")
add("fm_04", "VAT ni asilimia ngapi? Vipi kuhusu EFD?", 1, "'vipi kuhusu' opener.")
add("fm_05", "NSSF inalipwa lini? Na WCF je?", 1, "levy follow-up.")
add("fm_06", "What is the SDL rate? What about PAYE?", 1, "English 'what about'.")
# --- must STAY SPLIT (a genuine second question: it asks something of its own, or does not end in 'je')
add("fm_10", "Nina duka, nisajili VAT lini? Na je, ninahitaji EFD mashine ya risiti?", 2, "'na je, ninahitaji EFD' is a real question (does not END in 'je'); must keep its own retrieval.")
add("fm_11", "Mshahara wangu ni TZS 800,000, PAYE ni kiasi gani? Pia nataka kujua NSSF ni asilimia ngapi?", 2, "two full questions with their own asks.")
add("fm_12", "Ninataka kusajili kampuni BRELA. Ada ni ngapi? Na muda gani unachukua?", 2, "'Na muda gani unachukua?' asks (gani): self-contained, so it splits.")
add("fm_13", "SDL ni asilimia ngapi? Na NSSF ni kiasi gani?", 2, "'Na NSSF ni kiasi gani?' asks (kiasi): self-contained.")
add("fm_14", "VAT inalipwa lini? Na PAYE inalipwa lini?", 2, "a full parallel question ('inalipwa lini').")
add("fm_15", "Nataka kuanza biashara ya duka. Nisajili BRELA wapi? Na TIN je?", 1, "a fragment after a full question: 'Na TIN je?' merges.")
add("fm_16", "Je, EFD ni lazima? Je, VAT ni lazima?", 2, "two full yes/no questions: neither is a fragment ('Je, VAT ni lazima' has the copula 'ni').")
# --- single questions are untouched
add("fm_20", "Huduma za afya zinatozwa VAT?", 1, "a single question.")
add("fm_21", "SDL na PAYE zinalipwa lini?", 1, "a single multi-levy question.")
with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in P:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(P), "probes ->", OUT)

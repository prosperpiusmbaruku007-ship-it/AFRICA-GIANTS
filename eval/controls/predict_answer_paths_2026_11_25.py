"""PRE-REGISTERED PREDICTIONS (R18: committed BEFORE the live check) of the answer-path class for the 16 founder messages, from the CODE only: the fixed-statement router, the intent router and the
production OOC classifier (config phrases). No model, no network. The model-path rows can only be predicted as "not engine, not fixed, not OOC" -> fact_model (the orchestrator's coverage gate is disabled by decision), which is reported as such.
    python eval/controls/predict_answer_paths_2026_11_25.py -> eval/results/predict_answer_paths_2026_11_25.json"""
import io
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)

QUESTIONS = [
    ("fixed_statement", "Dawa zinatozwa VAT?"), ("fixed_statement", "PAYE ni asilimia ngapi?"), ("fixed_statement", "Mgeni anayefanya kazi Tanzania analipa PAYE kwa kiwango gani?"),
    ("fixed_statement", "WHT kwa ada ya mkurugenzi ni asilimia ngapi?"),
    ("engine", "Mshahara wa TZS 800,000, PAYE ni kiasi gani?"), ("engine", "Nina wafanyakazi 12 kila mmoja analipwa TZS 500,000, SDL ni kiasi gani kwa mwezi?"),
    ("engine", "Mfanyakazi analipwa TZS 1,200,000, mchango wa NSSF ni kiasi gani?"), ("engine", "Nalipa kodi ya pango TZS 2,000,000 kwa mwezi, nikate withholding kiasi gani?"),
    ("fact_model", "Mfanyakazi aliyefanya kazi mwaka mmoja akiachishwa kazi, anastahili malipo gani?"), ("fact_model", "Ada ya mkurugenzi ni TZS 5,000,000, WHT ni kiasi gani?"),
    ("fact_model", "Nikichelewa kuwasilisha ritani ya kodi ya mwaka, adhabu ni nini?"), ("fact_model", "Je, nahitaji leseni ya biashara kufungua duka la nguo?"),
    ("ooc", "Ushuru wa bidhaa (excise duty) kwenye vinywaji baridi ni kiasi gani?"), ("ooc", "Kodi ya faida ya mtaji (capital gains tax) ni kiasi gani?"),
    ("ooc", "Ushuru wa forodha (import duty) wa gari ni kiasi gani?"), ("ooc", "Stamp duty ya kuuza nyumba ni kiasi gani?"),
]
# SWAPS (founder allowed them where the code reading says a question lands elsewhere; 4 per class kept). Original -> replacement, and what the code said about the original:
SWAPS = [
    (3, "Mfanyakazi mgeni analipa PAYE kiasi gani?", "Mgeni anayefanya kazi Tanzania analipa PAYE kwa kiwango gani?", "original routes to NO fixed topic and no intent (model path); no figure and no residency cue, so the residency route does not fire"),
    (4, "Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?", "WHT kwa ada ya mkurugenzi ni asilimia ngapi?", "original has no director need-word (rate/asilimia/WHT), so the director route does not fire; model path"),
    (14, "Nichangie NHIF kiasi gani kwa mfanyakazi?", "Kodi ya faida ya mtaji (capital gains tax) ni kiasi gani?", "original is IN SCOPE for the classifier (no OOC phrase): model path. NHIF is not in the OOC list"),
    (15, "Kodi ya PAYE Kenya ni asilimia ngapi?", "Ushuru wa forodha (import duty) wa gari ni kiasi gani?", "original is IN SCOPE for the classifier: model path (the foreign-authority repair handles the REPLY, not the route)"),
    (16, "Mechi ya Simba na Yanga ni lini?", "Stamp duty ya kuuza nyumba ni kiasi gani?", "original is IN SCOPE for the classifier (no phrase for football): model path. Bar B: an off-topic question reaches the model"),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from chike import routing, classification
    cfg = json.load(io.open(os.path.join(_ROOT, "kaggle", "chike_config.json"), encoding="utf-8"))
    ooc, ins = cfg.get("ooc_phrases", []), cfg.get("in_scope_phrases", [])
    rows = []
    for i, (founder_class, q) in enumerate(QUESTIONS, 1):
        c = classification.classify(q, ooc, ins)
        fs = routing.fixed_statement_topic(q)
        intent = routing.detect_intent(q)
        if c is False:          # classification.classify returns True = IN SCOPE, False = out of scope
            pred = "ooc"
        elif fs:
            pred = "fixed_statement"
        elif intent and intent != "none":
            pred = "engine"
        else:
            pred = "fact_model"
        rows.append({"n": i, "q": q, "founder_class": founder_class, "classifier": str(c), "fixed_topic": fs, "intent": intent, "predicted": pred, "matches_founder_class": pred == founder_class})
    json.dump({"swaps": [list(x) for x in SWAPS], "rows": rows}, io.open(os.path.join(_ROOT, "eval", "results", "predict_answer_paths_2026_11_25.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in rows:
        print(r["n"], r["predicted"], "(founder %s)%s" % (r["founder_class"], "" if r["matches_founder_class"] else "  <-- MISMATCH"), "|", r["classifier"], "|", r["fixed_topic"], "|", r["intent"], "|", r["q"][:60])
    return 0


if __name__ == "__main__":
    sys.exit(main())

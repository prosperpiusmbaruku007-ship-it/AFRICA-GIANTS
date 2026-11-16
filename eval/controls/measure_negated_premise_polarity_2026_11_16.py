# -*- coding: utf-8 -*-
"""HOW OFTEN IS A YES/NO OPENER THE WRONG WAY ROUND, AND IS IT CONCENTRATED IN NEGATED-PREMISE QUESTIONS? (2026-11-16, evidence for the polarity-mechanism PROPOSAL; nothing is built from this.)

For every yes/no gate row with a polarity-bearing gold ("Ndiyo/Hapana/La/Ni kweli/Si kweli" first word) the reply's first-word polarity is compared with the gold's. Rows are split by whether the QUESTION contains a
negation cue (a negated premise or "si kweli"), against the plain rows as control. Only the opener is compared: a reply can open wrong and carry the right content (388, 390, 332) or open right and carry wrong content (348),
and those are different defects with different remedies -- the table says which is which by hand-read rows listed beside it.

    python eval/controls/measure_negated_premise_polarity_2026_11_16.py [gate_artifact.json]
"""
import io, json, os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ART = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "eval", "results", "gate_production_c2143c0.json")
NEG_Q = re.compile(r"\bsi\s+kweli\b|\bhaitozwi\b|\bhailipwi\b|\bhaikatwi\b|\bhaulipwi\b|\bhautozwi\b|\bhatozwi\b|\bhakatwi\b|\bhaihitajiki\b|\bhailazimiki\b|\bhaina\b|\bhazihitaji\b|\bhaihusu\b|\bhaitumiki\b|\bhaiwezi\b", re.I)
YES = re.compile(r"^\W*(ndiyo|ni\s+kweli|kweli|sahihi)\b", re.I)
NO = re.compile(r"^\W*(hapana|la\b|si\s+kweli|siyo|sio\b|si\s+sahihi)", re.I)


def pol(t):
    t = t or ""
    return "Y" if YES.match(t) else ("N" if NO.match(t) else None)


def main():
    d = json.load(io.open(ART, encoding="utf-8"))
    out = {"neg": [], "plain": []}
    for r in d["rows"]:
        if r.get("answer_type") != "yes_no" or r.get("subdomain") == "out_of_corpus":
            continue
        g, p = pol(r["correct_answer_sw"]), pol(r["generated"])
        if g is None or p is None:
            continue
        out["neg" if NEG_Q.search(r["question_sw"]) else "plain"].append((r["id"], g, p, g != p, r["question_sw"][:90], r["generated"][:70].replace("\n", " ")))
    for k, rows in out.items():
        bad = [x for x in rows if x[3]]
        print(f"{k:<6} yes/no rows with polarity on both sides: {len(rows):>3}   opener inverted vs gold: {len(bad):>3}  ({len(bad) / max(1, len(rows)):.0%})")
        for x in bad:
            print(f"    {x[0]} gold {x[1]} reply {x[2]} | {x[4]!r} -> {x[5]!r}")
    json.dump({k: [dict(zip(("id", "gold", "reply", "inverted", "q", "reply_head"), x)) for x in v] for k, v in out.items()}, io.open(os.path.join(REPO, "eval", "results", "negated_premise_polarity_2026_11_16.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

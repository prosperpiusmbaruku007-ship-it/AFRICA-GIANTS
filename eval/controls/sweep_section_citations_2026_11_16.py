"""Read-only census of section-number citations in everything a participant can be served (2026-11-16).

Populations: (1) every served index row (chike-inference/rag_facts_text.json), (2) the five model-free statement texts
(chike/rules_engine/fixed_statements.py, which is also the D-FIDELITY-10 replacement text), (3) rule-engine renderer texts.
For each citation: which Act the surrounding sentence names, whether that Act has a recorded renumbering, and the snippet.
Writes eval/results/sweep_section_citations_2026_11_16.json. Changes nothing.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

CIT = re.compile(r"(?i)\b(?:kifungu|vifungu|section|sections|sec\.|ss?\.)\s*\d+[A-Za-z]?(?:\(\w+\))*(?:\s*(?:na|and|,|-|–|hadi)\s*\d+[A-Za-z]?(?:\(\w+\))*)*")
ACTS = [  # (label, cap, pattern) — renumbered Acts first
    ("ELRA", "Cap.366", r"ELRA|Employment and Labour Relations|Sheria ya Ajira|Sheria za Kazi|Labour Laws"),
    ("Companies Act", "Cap.212", r"Companies Act|Cap\.? ?212|Sheria ya Kampuni"),
    ("NSSF Act", "Cap.50", r"NSSF Act|Cap\.? ?50\b|Sheria ya NSSF|Sheria ya Mfuko wa Hifadhi"),
    ("Income Tax Act", "Cap.332", r"Income Tax Act|Cap\.? ?332|Sheria ya Kodi ya Mapato|\bITA\b"),
    ("Tax Administration Act", "Cap.438", r"Tax Administration Act|Cap\.? ?438|\bTAA\b|Sheria ya Usimamizi wa Kodi"),
    ("VAT Act", "Cap.148", r"VAT Act|Cap\.? ?148|Sheria ya VAT|Sheria ya Kodi ya Ongezeko"),
    ("OSHA", "Act 5/2003", r"OSH Act|OSHA Act|Sheria ya OSHA|Usalama na Afya"),
    ("SDL/Vocational", "Cap.82", r"Vocational Education|SDL"),
]
RENUMBERED = {"Cap.366", "Cap.212", "Cap.50", "Cap.332", "Cap.438"}


def act_of(text, start, end):
    """Nearest Act name within 140 chars before the citation, else within 80 after, else the whole row."""
    for lo, hi in ((max(0, start - 140), end + 20), (max(0, start - 140), end + 80)):
        seg = text[lo:hi]
        hits = [(m.start(), a) for a in ACTS for m in [re.search(a[2], seg)] if m]
        if hits:
            return max(hits, key=lambda h: h[0])[1]  # the one closest before the citation
    hits = [a for a in ACTS if re.search(a[2], text)]
    return hits[0] if len(hits) == 1 else None


def census(population, name, texts):
    out = []
    for ident, t in texts:
        for m in CIT.finditer(t):
            a = act_of(t, m.start(), m.end())
            out.append({
                "population": name, "id": ident, "citation": m.group(0),
                "act": a[0] if a else None, "cap": a[1] if a else None,
                "known_renumbering": bool(a and a[1] in RENUMBERED),
                "snippet": t[max(0, m.start() - 70): m.end() + 40].replace("\n", " "),
            })
    return out


SW = re.compile(r"(?:Kifungu|Vifungu|kifungu|vifungu)\s+\d")


def served_swahili_violations(texts):
    """Consolidated-Act section numbers in SERVED SWAHILI text: any Kifungu/Vifungu N not preceded by a 20xx year (an
    amending Act's own section, fixed once enacted). `texts` is [(id, text)]. Returns [(id, snippet)]."""
    bad = []
    for ident, t in texts:
        for m in SW.finditer(t):
            if re.search(r"20\d\d[,\s]*$", t[max(0, m.start() - 14):m.start()]):
                continue
            bad.append((ident, t[max(0, m.start() - 50): m.end() + 30].replace(chr(10), " ")))
    return bad


# English-key, model-facing rows that cite a First Schedule paragraph as provenance (population D). Explicit, so the exemption cannot grow silently;
# a row whose key looks English but whose text is Swahili (presumptive_tax_bands_2022) is NOT exempt -- the first heuristic here classified it by
# its key prefix and let it through, which the planted shipped-index run caught.
ENGLISH_KEY_SCHEDULE_EXEMPT = frozenset({"royalties_wht_rate", "paye_nonresident_flat_rate"})
SCHED = re.compile(r"(?:First|Second|Third|Fourth) Schedule,? para")


def engine_served_strings():
    """Engine string constants a participant can be SERVED: not docstrings, not `note=` metadata (founder's decision 2026-11-16: schedule
    paragraph numbers of a consolidated Act follow the same rule as section numbers; they live in metadata only)."""
    import ast
    import glob
    out = []
    for p in sorted(glob.glob(os.path.join(REPO, "chike", "rules_engine", "*.py"))):
        if os.path.basename(p) == "rates.py":
            continue  # an English citation/provenance REGISTRY (never rendered to a participant): its citations ARE the metadata R44 keeps
        tree = ast.parse(open(p, encoding="utf-8").read())
        skip = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and node.body:
                first = node.body[0]
                if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                    skip.add(id(first.value))
            if isinstance(node, ast.keyword) and node.arg in ("note", "source", "citation"):
                for sub in ast.walk(node.value):
                    skip.add(id(sub))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in skip and len(node.value) > 25:
                out.append((os.path.basename(p) + ":" + str(node.lineno), node.value))
    return out


def schedule_violations(texts):
    return [(i, t[max(0, m.start() - 50): m.end() + 30].replace(chr(10), " ")) for i, t in texts for m in SCHED.finditer(t)]


def engine_strings():
    """String constants of the rule-engine modules (f-string literal parts included) -- the text a participant can be served."""
    import ast
    import glob
    out = []
    for p in sorted(glob.glob(os.path.join(REPO, "chike", "rules_engine", "*.py"))):
        tree = ast.parse(open(p, encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) > 25:
                out.append((os.path.basename(p) + ":" + str(node.lineno), node.value))
    return out


def prove():
    """The proof run (2026-11-16): zero consolidated-Act section numbers in served Swahili text. The index is the PROSPECTIVE one,
    built from source (the shipped one changes only at the R15 regen); the English-key rows (population D) are reported and
    must be UNCHANGED, i.e. they are excluded from the violation count and listed."""
    os.chdir(REPO)  # build_fact_texts reads a relative path (R40: set up the world in main, never at import)
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import precompute_rag_embeddings as pre
    texts, keys, _ = pre.build_fact_texts()
    from chike.rules_engine import fixed_statements as fs
    bad = (served_swahili_violations([(k, t) for k, t in zip(keys, texts)])
           + served_swahili_violations([("statement:" + k, v[1]) for k, v in fs.STATEMENTS.items()])
           + served_swahili_violations(engine_strings()))
    swahili_rows = [(k, t) for k, t in zip(keys, texts) if k not in ENGLISH_KEY_SCHEDULE_EXEMPT]
    sched = (schedule_violations(swahili_rows) + schedule_violations([("statement:" + k, v[1]) for k, v in fs.STATEMENTS.items()])
             + schedule_violations(engine_served_strings()))
    bad += sched
    english_d = [(k, m.group(0)) for k, t in zip(keys, texts) for m in CIT.finditer(t) if not SW.match(m.group(0))]
    res = {"violations": bad, "n_rows": len(texts), "population_D_english_key_citations": english_d}
    path = os.path.join(REPO, "eval", "results", "sweep_section_citations_proof_2026_11_16.json")
    json.dump(res, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("violations:", len(bad), "| rows:", len(texts), "| D citations kept:", len(english_d))
    for v in bad:
        print("  ", v)
    return bad


def main():
    rows = json.load(open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    assert len(rows) == 208, len(rows)
    res = census("index_row", "index", [(i, t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)) for i, t in enumerate(rows)])
    from chike.rules_engine import fixed_statements as fs
    res += census("fixed_statement", "statement", [(k, v[1]) for k, v in fs.STATEMENTS.items()])
    import glob
    eng = []
    for p in sorted(glob.glob(os.path.join(REPO, "chike", "rules_engine", "*.py"))):
        eng.append((os.path.basename(p), open(p, encoding="utf-8").read()))
    # engine files: only string-literal citations matter, but comments/notes are listed too and marked by file
    res += census("engine_source", "engine", eng)
    path = os.path.join(REPO, "eval", "results", "sweep_section_citations_2026_11_16.json")
    json.dump(res, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter((r["population"], r["cap"], r["known_renumbering"]) for r in res))
    return res


if __name__ == "__main__":
    prove() if "--prove" in sys.argv else main()

"""MEASURE (do not build) THE WRONG-AUTHORITY PROPOSAL (founder, 2026-11-16, np_19: a maternity-leave answer citing immigration.go.tz; np_12 a leave answer citing osha.go.tz; np_05 severance citing the WCF Act).

PROPOSED GENERAL RULE (a table, not a phrase list): each question TOPIC has an ALLOWED set of authorities; a reply whose "Thibitisha na <authority>" / cited host names an authority OUTSIDE the topic's set is wrong-authority.
This script prices that rule over every stored reply (the same population as the other guards) BEFORE anything is built: how often does each topic name each authority, and what would the rule flag? Every flag is for
a person to read -- the rule is a table and the table is the hypothesis. R21: a sweep over our own corpora is a LOWER bound on what the table would block.

    python eval/fidelity/measure_authority_by_topic_2026_11_16.py  -> eval/results/authority_by_topic_2026_11_16.json
"""
import collections, importlib.util, io, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
spec = importlib.util.spec_from_file_location("_pf", os.path.join(HERE, "price_followup_guards_2026_11_16.py")); pf = importlib.util.module_from_spec(spec); spec.loader.exec_module(pf)

# topic -> (question cue, allowed authority tokens). Lower-cased substring match on the CITED authority text.
TOPICS = [
    ("labour", r"likizo|notisi|notice|severance|kuachishwa|overtime|mshahara\s+wa\s+chini|ajira|mkataba\s+wa\s+kazi|elra|uzazi|paternity|maternity", ("kazi.go.tz", "ofisi ya kazi", "idara ya kazi", "wizara ya kazi", "elra", "tanzlii", "cma", "tume ya usuluhishi", "kazi")),
    ("nssf", r"nssf|pensheni|mfuko\s+wa\s+hifadhi", ("nssf",)),
    ("wcf", r"wcf|fidia\s+ya\s+wafanyakazi|workers\s+compensation|ajali\s+kazini", ("wcf",)),
    ("osha", r"osha|usalama\s+kazini|afya\s+na\s+usalama", ("osha",)),
    ("brela", r"brela|usajili\s+wa\s+kampuni|jina\s+la\s+biashara|annual\s+return|ada\s+ya\s+kampuni", ("brela",)),
    ("immigration", r"gn\s*487a|mgeni|non-?citizen|uhamiaji|visa|kibali\s+cha\s+kazi", ("immigration", "uhamiaji", "brela", "tra", "kazi")),
    ("tax", r"(?<![a-z])(?:vat|paye|sdl|efd|tin|kodi|tra|withholding|zuio|risiti|return)(?![a-z])", ("tra", "tax", "mamlaka ya mapato")),
]
AUTH_RE = re.compile(r"(?:thibitisha\s+na|confirm\s+with|wasiliana\s+na|angalia)\s+([^.\n]{2,90})", re.IGNORECASE)
HOST_RE = re.compile(r"(?:https?://)?(?:www\.)?([a-z0-9][a-z0-9.-]*\.(?:go\.tz|or\.tz|co\.tz|org|com|go\.ke))", re.IGNORECASE)


def topic_of(q):
    ql = q.lower()
    hits = [t for t, cue, _ in TOPICS if re.search(cue, ql)]
    return hits[0] if len(hits) == 1 else None          # a question about two topics is not judged (as in the fixed-statement route)


def cited(a):
    out = set()
    for m in AUTH_RE.finditer(a):
        out.add(m.group(1).strip(" )(").lower())
    for m in HOST_RE.finditer(a):
        out.add(m.group(1).lower())
    return out


def main():
    stored = pf.pairs_from_results()
    seen, flagged = collections.defaultdict(collections.Counter), []
    judged = 0
    for src, q, a in stored:
        t = topic_of(q)
        if not t:
            continue
        allowed = dict((x[0], x[2]) for x in TOPICS)[t]
        c = cited(a)
        if not c:
            continue
        judged += 1
        for x in c:
            seen[t][x] += 1
        bad = [x for x in c if not any(tok in x for tok in allowed)]
        if bad:
            flagged.append({"src": src, "topic": t, "q": q[:160], "cited": sorted(c), "outside": bad, "reply": a[:260]})
    print(f"{len(stored)} stored replies; {judged} carry a cited authority on a single-topic question; {len(flagged)} would be flagged by the table as proposed")
    for t, ctr in seen.items():
        print(f"  {t:<12} " + ", ".join(f"{k}x{n}" for k, n in ctr.most_common(8)))
    # de-duplicate by (question, outside) so the same live row recorded in several artifacts is read once
    uniq = {}
    for f in flagged:
        uniq.setdefault((f["q"], tuple(f["outside"])), f)
    print(f"\n{len(uniq)} distinct (question, outside-authority) pairs:")
    for f in uniq.values():
        print(f"- [{f['topic']}] {f['src']}: outside={f['outside']}\n    Q: {f['q'][:130]}\n    A: {f['reply'][:200]!r}")
    out = os.path.join(REPO, "eval", "results", "authority_by_topic_2026_11_16.json")
    json.dump({"replies": len(stored), "judged": judged, "flagged_rows": len(flagged), "distinct": list(uniq.values()),
               "seen": {t: dict(c) for t, c in seen.items()}}, io.open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()

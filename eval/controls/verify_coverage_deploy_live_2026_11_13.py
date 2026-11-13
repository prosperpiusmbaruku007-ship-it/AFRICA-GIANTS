# -*- coding: utf-8 -*-
"""LIVE VERIFICATION of the 2026-11-13 three-profile coverage deploy (R16 step 2/3): exercises the specific change, plus negative cases.

Calls the PRODUCTION `chike-inference` ChikeModel through the Modal SDK (the same lookup chike-whatsapp uses), so no HTTP token is needed:
  1. `served_index_identity()` -- the index the GPU container ACTUALLY loaded (rows, shape, sha256). Must equal the committed index.
  2. `run(question)` for: NEW facts, REWRITTEN rows, and NEGATIVE cases (must behave as before).

`must` is an INDICATIVE automated limb (R38: a probe encodes an expected answer, so it can encode a wrong one): each pattern is a figure the
cited fact states, and alternatives are accepted. Replies are stored in full for READING -- a pass here is not "the answer is correct".
Writes the artifact after EVERY row and resumes from it (a dropped link or a 20-minute cold start must cost a row, not the run).

    python eval/controls/verify_coverage_deploy_live_2026_11_13.py [--out eval/results/coverage_deploy_live_2026_11_13.json]
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

PROBES = [
    # (kind, question, must-regex or None, note)
    ("NEW", "Nitapataje TIN?", r"siku\s*15|siku\s*7|NIDA", "TAA s.22/24"),
    ("NEW", "PAYE inalipwa tarehe ngapi kila mwezi?", r"tarehe\s*7|siku\s*7", "ITA s.109"),
    ("NEW", "Notisi ya kuachisha mfanyakazi wa kila mwezi ni siku ngapi?", r"28", "ELRA notice"),
    ("NEW", "Severance pay inahesabiwaje?", r"siku\s*7|saba", "ELRA severance"),
    ("NEW", "Likizo ya uzazi ni siku ngapi?", r"84", "ELRA maternity"),
    ("NEW", "Likizo ya mwaka ni siku ngapi?", r"28", "ELRA annual leave"),
    ("NEW", "Overtime inalipwa kiasi gani?", r"1\.5|1,5|moja na nusu", "ELRA overtime"),
    ("NEW", "Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?", r"80,000|328,000|265,000|160,000", "GN 605A item 4"),
    ("NEW", "Kodi ya zuio kwenye gawio (dividend) ni asilimia ngapi?", r"10|5", "ITA s.105"),
    ("NEW", "Nimeuza kwa mkopo, VAT inalipwa lini?", r"invoice|ankara|20", "VAT s.15"),
    ("NEW", "Naweza kudai VAT ya pembejeo kwa gari la kampuni?", r"abiria|hapana|Hapana", "VAT s.72(3)(c)"),
    ("NEW", "Rekodi za biashara zihifadhiwe kwa miaka mingapi?", r"\b5\b|tano", "TAA s.43"),
    ("REWRITTEN", "Nikikosa kutoa risiti ya EFD adhabu ni nini?", r"onyo|faini|funga|kufunga|leseni", "efd_tra_closure_authority"),
    ("REWRITTEN", "Nikichelewa kulipa PAYE kuna adhabu gani?", r"2\.5|2,5", "paye_penalty_rate"),
    ("REWRITTEN", "Je nahitaji mashine ya risiti (EFD) nikiuza milioni 15 kwa mwaka?", r"Ndiyo|ndiyo|default", "efd_not_every_business"),
    ("ENGINE-A", "Nalipa mfanyakazi wa nyumbani 150,000 kwa mwezi, je ni sawa?", r"kazi za nyumbani|80,000", "domestic cue -> sector statement"),
    ("ENGINE-A", "Kodi ya makadirio kwa mauzo ya milioni 40 ni kiasi gani?", r"makadirio|4\.0%|4%|1,", "presumptive cue (named turnover)"),
    ("NEGATIVE", "SDL ni asilimia ngapi?", r"3\.5|3,5|tatu na nusu", "must still answer"),
    ("NEGATIVE", "NSSF ya mwajiri ni asilimia ngapi?", r"\b10\b", "must still answer"),
    ("NEGATIVE", "Kizingiti cha kujisajili VAT ni kiasi gani?", r"200", "VAT threshold row must not be displaced"),
    ("NEGATIVE", "Mshahara wa mfanyakazi ni 800,000 kwa mwezi, PAYE ni kiasi gani?", r"78,000", "engine unchanged"),
    ("NEGATIVE", "Je, ni lazima nitumie mashine ya EFD? Mauzo yangu ni milioni 30.", r"Ndiyo|ndiyo", "EFD engine unchanged"),
    ("NEGATIVE", "Capital gains tax kwa kuuza hisa ni asilimia ngapi?", r"nje ya mada|Samahani", "kept refusal"),
    ("NEGATIVE", "Ninaagiza bidhaa kutoka China, ushuru wa forodha ni kiasi gani?", r"nje ya mada|Samahani", "kept refusal"),
]


def committed_digest():
    rows = json.load(open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    return len(rows), hashlib.sha256(json.dumps(rows, ensure_ascii=False).encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO, "eval", "results", "coverage_deploy_live_2026_11_13.json"))
    a = ap.parse_args()
    import modal
    cls = modal.Cls.from_name("chike-inference", "ChikeModel")
    m = cls()
    art = json.load(open(a.out, encoding="utf-8")) if os.path.exists(a.out) else {"identity": None, "rows": []}
    done = {r["q"] for r in art["rows"] if "error" not in r}
    art["rows"] = [r for r in art["rows"] if "error" not in r]

    def save():
        json.dump(art, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if not art.get("identity"):
        t0 = time.time()
        ident = m.served_index_identity.remote()
        n, dg = committed_digest()
        art["identity"] = dict(served=ident, committed_rows=n, committed_sha256=dg, took_s=round(time.time() - t0, 1))
        save()
    ident = art["identity"]
    print("served index identity:", {k: v for k, v in ident["served"].items() if k != "build"} if isinstance(ident["served"], dict) else ident["served"])
    print("committed             :", ident["committed_rows"], ident["committed_sha256"])

    for kind, q, must, note in PROBES:
        if q in done:
            continue
        t0 = time.time()
        try:
            out = m.run.remote(q)
            reply = out.get("reply", "") if isinstance(out, dict) else str(out)
            row = dict(kind=kind, q=q, note=note, reply=reply, took_s=round(time.time() - t0, 1),
                       must=must, must_ok=bool(re.search(must, reply)) if must else None,
                       facts=[f[:90] for f in (out.get("facts") or [])][:3] if isinstance(out, dict) else None,
                       path=out.get("answer_path") or out.get("path") if isinstance(out, dict) else None)
        except Exception as e:                                           # noqa: BLE001 -- a per-row error must not lose the run
            row = dict(kind=kind, q=q, note=note, error=repr(e)[:300])
        art["rows"].append(row)
        save()
        flag = "ERR" if "error" in row else ("ok " if row["must_ok"] in (True, None) else "MISS")
        print(f"[{flag}] {kind:<9} {row.get('took_s', '?'):>6}s  {q[:62]}\n        -> {(row.get('reply') or row.get('error') or '')[:170]!r}")
    miss = [r for r in art["rows"] if r.get("must_ok") is False]
    err = [r for r in art["rows"] if "error" in r]
    print(f"\n{len(art['rows'])} rows; automated-limb misses {len(miss)}; errors {len(err)}  (READ the replies: a pass is indicative, not correctness)")
    sys.exit(1 if (miss or err) else 0)


if __name__ == "__main__":
    main()

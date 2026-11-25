# -*- coding: utf-8 -*-
"""PRICE THE 2026-11-25 BATCH-3 DETECTORS BEFORE THEY GO ANYWHERE (R22/R25; LOCAL until the founder approves a push):
  D-FIDELITY-34   a foreign / expatriate status tied to the 15% (or 'flat') rate without a residency word  (INTERIM holding line)
  foreign authority   a sentence that names a foreign tax authority or a foreign URL (repair: that ONE sentence is replaced by "wasiliana na mamlaka ya kodi ya nchi husika")
Populations are the SAME generators as price_d32b_d33 (imported, never re-implemented, R24): STORED, GOLD, TRAINING (each with its question), INDEX (no question). PLANTS (R26): the live specimens MUST flag, the controls MUST NOT; either failure exits 1.
Every flag is PRINTED and must be READ before the change ships; GOLD flags are the alarm (a human asserted those answers right).
    python eval/fidelity/price_batch3_2026_11_25.py  ->  eval/results/price_batch3_2026_11_25.json"""
import importlib.util
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import fidelity as F  # noqa: E402

_spec = importlib.util.spec_from_file_location("_p32", os.path.join(REPO, "eval", "fidelity", "price_d32b_d33_2026_11_25.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

QF = "Does a foreign employee pay PAYE at a different rate from a citizen?"
LIVE_FOREIGN = "A foreigner working as an employee pays a flat rate of 15% on their gross employment income. This is because they don't have residence status for progressive taxation."
QK = "Kiwango cha PAYE Kenya ni asilimia ngapi?"
LIVE_KENYA = "Kwa taarifa za kodi za Kenya, thibitisha na TRA (tra.go.ke) au mshauri wa kodi wa Kenya."
SPEC_FOREIGN = [(QF, LIVE_FOREIGN), ("Kodi ya mgeni PAYE?", "Kiwango ni 15% tambarare kwa mgeni."), ("x", "Expatriates pay 15% on their salary.")]
CTRL_FOREIGN = [(QF, "Non-resident employees pay a flat 15%; a foreigner who is resident pays on the bands."), ("x", "Mgeni anayekaa Tanzania zaidi ya siku 183 ni mkazi na analipa kwa mabano, si 15%."),
                ("x", "Wageni hawalipi asilimia 15 tambarare."), ("x", "Foreigners do not pay a flat 15%."), ("PAYE ni asilimia ngapi?", "Asiye mkazi analipa 15% tambarare."),
                ("Kodi ya mgeni PAYE?", "Kodi ya zuio ya gawio ni asilimia 15 kwa kampuni zisizoorodheshwa.")]
SPEC_AUTH = [(QK, LIVE_KENYA), ("Kodi ya kampuni?", "Kwa taarifa zaidi tembelea kra.go.ke."), ("Kiwango cha kodi Kenya?", "Kenya Revenue Authority (KRA) inasema kiwango ni 30%.")]
CTRL_AUTH = [("Cheti cha P9 ni nini?", "'P9' si neno la Tanzania: ni la Kenya (KRA) na TRA haina fomu yenye jina hilo."), ("Kodi ya PAYE ni nini?", "Thibitisha na TRA (tra.go.tz)."),
             ("Tofauti ya Kenya na Tanzania kwenye PAYE?", "Nchini Tanzania, thibitisha na TRA (tra.go.tz). Kenya ina mfumo wake.")]


def main():
    fail = []
    for q, b in SPEC_FOREIGN:
        if not F.foreign_status_tied_to_15pct(q, b):
            fail.append(("SPECIMEN NOT FLAGGED (foreign)", b))
    for q, b in CTRL_FOREIGN:
        if F.foreign_status_tied_to_15pct(q, b):
            fail.append(("CONTROL FLAGGED (foreign)", b))
    for q, b in SPEC_AUTH:
        if not F.foreign_authority_sentences(q, b):
            fail.append(("SPECIMEN NOT FLAGGED (authority)", b))
    for q, b in CTRL_AUTH:
        if F.foreign_authority_sentences(q, b):
            fail.append(("CONTROL FLAGGED (authority)", b))
    print("plants: %d specimens, %d controls, failures %d" % (len(SPEC_FOREIGN) + len(SPEC_AUTH), len(CTRL_FOREIGN) + len(CTRL_AUTH), len(fail)))
    for f in fail:
        print("  PLANT FAILED:", f)
    res = {"plants": {"failed": [list(f) for f in fail]}, "populations": {}}
    for name, gen in (("stored", P.pairs_stored), ("gold", P.pairs_gold), ("training", P.pairs_training), ("index", P.pairs_index)):
        n, rows = 0, []
        for src, q, text in gen():
            n += 1
            ff, fa = F.foreign_status_tied_to_15pct(q, text), F.foreign_authority_sentences(q, text)
            if ff or fa:
                rows.append({"src": src, "q": q[:140], "reply": text[:300], "foreign_15pct": bool(ff), "foreign_authority": [s[:200] for s in fa]})
        assert n > 0, name
        seen, uniq = set(), []
        for r in rows:
            k = (r["q"], r["reply"])
            if k not in seen:
                seen.add(k)
                uniq.append(r)
        f15, fau = [r for r in uniq if r["foreign_15pct"]], [r for r in uniq if r["foreign_authority"]]
        res["populations"][name] = {"pairs": n, "distinct_flagged": len(uniq), "foreign_15pct": len(f15), "foreign_authority": len(fau), "rows": uniq[:80]}
        print("%-9s pairs=%6d distinct flagged=%3d | D34 %2d | foreign authority %2d" % (name, n, len(uniq), len(f15), len(fau)))
        for r in uniq[:30]:
            print("   %-4s %s | Q: %s | %s" % ("D34" if r["foreign_15pct"] else "AUTH", r["src"][-46:], r["q"][:56], (r["reply"] if r["foreign_15pct"] else " || ".join(r["foreign_authority"]))[:170]))
    res["decision_rule"] = "ship ONLY if plants pass AND gold flags == 0 for BOTH AND index flags == 0 AND every stored / training flag has been READ and is a genuine defect (a training flag is a corpus finding, not a blocker)"
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_batch3_2026_11_25.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())

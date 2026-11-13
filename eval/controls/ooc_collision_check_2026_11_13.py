# -*- coding: utf-8 -*-
"""PART D of the 2026-11-13 coverage batch (R17 'adding a domain' collision rule): the OOC classifier must not refuse the NEW subjects, and the
refusals that are kept (capital gains, transfer pricing, stamp duty, property tax, customs/import duty, Zanzibar/ZRA) must STILL refuse.

(1) every question in the batch's target set (the new facts' own questions) must classify IN SCOPE;
(2) in-scope PROBES that contain risky vocabulary (hisa, gari, pango, leseni, forodha-adjacent words, soko, mali, ...) must classify IN SCOPE;
(3) the kept refusals must classify OUT OF SCOPE;
(4) a substring audit: every OOC phrase that occurs INSIDE a question of set (1)/(2) is listed, so a collision is visible even when it
    does not flip the verdict.
Exit 1 on any failure. Artifact: eval/results/ooc_collision_check_2026_11_13.json"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "eval", "index_quality"))
from chike import classification as C
import measure_coverage_batch_2026_11_13 as M

cfg = C.load_local_config()
ooc, inscope = C.resolve_phrases(cfg)
def inside(q):
    return C.classify(q, ooc, inscope)

IN_SCOPE_PROBES = [
    "Natoa gawio la hisa kwa wanahisa wa kampuni yangu, nakata kodi ya zuio asilimia ngapi?",
    "Gawio la hisa nilizonunua Soko la Hisa la Dar es Salaam linakatwa kodi gani?",
    "Nimenunua gari la kampuni, naweza kudai VAT ya pembejeo?",
    "Gari langu la biashara linakodishwa, VAT ya vipuri inadaiwa?",
    "Mfanyakazi wa nyumbani anayeishi kwa mwajiri analipwa mshahara wa chini gani?",
    "Nikifunga biashara nimlipe mfanyakazi severance pay kiasi gani?",
    "Notisi ya kumfukuza dereva wa lori ni siku ngapi?",
    "Mfanyakazi wangu wa shamba anastahili likizo ya mwaka siku ngapi?",
    "Return ya kodi ya mapato ya mtu binafsi mwenye pango la nyumba ni lini?",
    "Nahitaji TIN kwa ajili ya leseni ya biashara, naipataje?",
    "Rekodi za mauzo ya hisa za kampuni zihifadhiwe miaka mingapi?",
    "Mapato ya gawio yanaingia kwenye return ya kodi ya mapato ya mtu binafsi?",
    "Nimeuza kwa mkopo bidhaa za mali ghafi, VAT inalipwa lini?",
    "Mshahara wa overtime wa mlinzi wa usiku unahesabiwaje?",
    "Nikichelewa kuwasilisha return ya VAT ya duka langu la nyumba ya kupanga adhabu ni nini?",
    "Likizo ya uzazi kwa mfanyakazi wa kiwanda ni siku ngapi?",
]
KEPT_REFUSALS = [
    "Capital gains tax kwa kuuza hisa ni asilimia ngapi?",
    "Transfer pricing inahitaji nyaraka gani?",
    "Stamp duty kwenye mkataba wa pango ni kiasi gani?",
    "Kodi ya majengo (property tax) inalipwa kwa nani?",
    "Ninaagiza bidhaa kutoka China, ushuru wa forodha ni kiasi gani?",
    "Mteja ana biashara Zanzibar, ZRA inatoza nini?",
    "Import duty ya magari yaliyotumika ni kiasi gani?",
]
targets = [q for q in M.W]
res = dict(in_scope_targets_refused=[q for q in targets if not inside(q)],
           probes_refused=[q for q in IN_SCOPE_PROBES if not inside(q)],
           kept_refusals_not_refused=[q for q in KEPT_REFUSALS if inside(q)])
sub = {}
for q in targets + IN_SCOPE_PROBES:
    hit = [p for p in ooc if p.lower() in q.lower()]
    if hit:
        sub[q] = hit
res["ooc_phrase_substring_hits_in_in_scope_questions"] = sub
res.update(n_targets=len(targets), n_probes=len(IN_SCOPE_PROBES), n_kept=len(KEPT_REFUSALS), n_ooc_phrases=len(ooc))
json.dump(res, open(os.path.join(REPO, "eval", "results", "ooc_collision_check_2026_11_13.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: (v if not isinstance(v, (list, dict)) else len(v)) for k, v in res.items()})
for k in ("in_scope_targets_refused", "probes_refused", "kept_refusals_not_refused"):
    for q in res[k]:
        print("  FAIL", k, "::", q)
for q, h in sub.items():
    print("  substring:", h, "<-", q[:70])
sys.exit(1 if (res["in_scope_targets_refused"] or res["probes_refused"] or res["kept_refusals_not_refused"]) else 0)

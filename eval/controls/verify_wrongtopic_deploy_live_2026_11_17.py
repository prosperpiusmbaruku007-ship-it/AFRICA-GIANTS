# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the wrong-topic audit fixes + D-FIDELITY-15: the corporate_tax veto, the two constant guards, and NEGATIVES on the neighbouring routes. Production chike-inference via the Modal SDK;
artifact written after every row. must/must_not are INDICATIVE (R38); replies, path, model_calls, guards are stored for READING.   python eval/controls/verify_wrongtopic_deploy_live_2026_11_17.py"""
import json, os, re, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "wrongtopic_deploy_live_2026_11_17.json")
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix)
CASES = [
    ("VETO", "Kampuni yangu haijaorodheshwa kwenye soko la hisa la DSE. Nikigawa gawio kwa wanahisa, withholding tax yake ni 10%, si ndiyo?", [], [r"asilimia 30 ya faida"], "engine:corporate_tax", None),
    ("VETO", "Nina kampuni ambayo imeorodheshwa DSE. Tukigawa gawio kwa wanahisa, withholding tax yake ni 5%, ndiyo?", [], [r"asilimia 25 kwa miaka 3"], "engine:corporate_tax", None),
    ("VETO", "Muda wa mwisho wa kuwasilisha return ya kodi ya mapato ya kampuni TRA ni lini?", [], [r"asilimia 30 ya faida"], "engine:corporate_tax", None),
    ("VETO", "Kampuni yangu imechelewa kuwasilisha tamko la kodi ya kampuni, faini ni ngapi?", [], [r"asilimia 30 ya faida"], "engine:corporate_tax", None),
    ("GUARD", "Nina wafanyakazi watano kwenye mgahawa. Hiyo 0.5% ya WCF sihitaji kuikata kwenye mishahara yao, maana ni malipo yangu kama mwajiri, si ndiyo?", [], [r"unapaswa kuikata"], None, None),
    ("GUARD", "Nimenunua gari la kutembelea kwa ajili ya matumizi ya kampuni yangu. Naweza kudai input VAT ya manunuzi yake kama ninavyodai kwenye bidhaa nyingine, au siyo?", [], [r"unaweza kudai input VAT ya manunuzi ya magari"], None, None),
    ("NEGATIVE", "Kodi ya mapato ya kampuni ni asilimia ngapi?", [r"30"], [], None, "engine:corporate_tax"),
    ("NEGATIVE", "Ninalipa pango la ofisi TZS 800,000 kwa mwezi, nimkate mwenye nyumba kiasi gani?", [r"10"], [], None, "engine:rent_wht"),
    ("NEGATIVE", "Ubia wetu unalipa kodi ya mapato kiasi gani?", [r"(?i)ubia"], [], None, "engine:partnership_tax"),
    ("NEGATIVE", "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi, NSSF ni ngapi?", [r"80,000"], [], None, "engine:nssf"),
    ("NEGATIVE", "Mishahara ya wafanyakazi wangu ni TZS 4,000,000 kwa mwezi, WCF ni ngapi?", [r"20,000"], [], None, "engine:wcf"),
    ("NEGATIVE", "Ninaweza kudai input VAT kwa lori la mizigo la biashara yangu?", [], [], None, None),
    ("NEGATIVE", "Nikate WCF kwenye mshahara wa mfanyakazi?", [r"(?i)hapana|haikatwi|mwajiri"], [r"unapaswa kuikata"], None, None),
]


def main():
    import modal
    m = modal.Cls.from_name("chike-inference", "ChikeModel")()
    art = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"identity": None, "rows": []}
    art["rows"] = [r for r in art["rows"] if "error" not in r]
    done = {r["q"] for r in art["rows"]}
    save = lambda: json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not art.get("identity"):
        art["identity"] = m.served_index_identity.remote(); save()
    print("served identity:", {k: art["identity"].get(k) for k in ("build", "rag_rows_loaded")})
    for arm, q, must, must_not, forbid, require in CASES:
        if q in done:
            continue
        try:
            out = m.run.remote(q)
            reply = out.get("reply", ""); path = out.get("answer_path") or out.get("path")
            ck = {"must": all(re.search(p, reply) for p in must), "must_not": not any(re.search(p, reply) for p in must_not)}
            if forbid: ck["path_not_" + forbid] = not (path and str(path).startswith(forbid))
            if require: ck["path"] = bool(path and str(path).startswith(require))
            row = dict(arm=arm, q=q, reply=reply, path=path, model_calls=out.get("model_calls"), guards=out.get("guards"), checks=ck, ok=all(ck.values()))
        except Exception as e:                                           # noqa: BLE001
            row = dict(arm=arm, q=q, error=repr(e)[:300])
        art["rows"].append(row); save()
        print(f"[{'ERR' if 'error' in row else 'ok ' if row['ok'] else 'MISS'}] {arm:<8} {row.get('path')} calls={row.get('model_calls')} guards={row.get('guards')} {[k for k,v in row.get('checks',{}).items() if not v]} {q[:55]}\n     -> {(row.get('reply') or row.get('error') or '')[:220]!r}")
    bad = [r for r in art["rows"] if r.get("ok") is False or "error" in r]
    print(f"\n{len(art['rows'])} rows; automated misses {len(bad)} (READ the replies)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

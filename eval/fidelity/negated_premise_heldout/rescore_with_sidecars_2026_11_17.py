# -*- coding: utf-8 -*-
"""RE-SCORE BOTH FROZEN NEGATED-PREMISE SETS WITH THE 2026-11-17 SIDECARS, from the STORED live replies (no model is called; a resume carries data, never a conclusion, so every verdict is re-derived).

Refuses to run unless each sidecar's pinned sha256 still matches the frozen file it corrects. The opener classifier and the rate definitions are the measurement scripts' own (imported, not re-implemented).

    python eval/fidelity/negated_premise_heldout/rescore_with_sidecars_2026_11_17.py  ->  eval/results/negated_premise_rescore_2026_11_17.json
"""
import hashlib
import importlib.util
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "negated_premise_rescore_2026_11_17.json")


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check_pin(sidecar):
    frozen = json.load(io.open(os.path.join(HERE, sidecar["frozen_file"]), encoding="utf-8"))
    authored = os.path.join(HERE, sidecar["authored_file"])
    actual = hashlib.sha256(io.open(authored, "rb").read().replace(b"\r\n", b"\n")).hexdigest()
    ok = frozen["sha256"] == sidecar["frozen_sha256"] and actual == sidecar["frozen_sha256"]
    return ok, actual


def rate(rows):
    inv = [r for r in rows if r["inverted"]]
    wo = [r for r in rows if r["opener"] != "NONE"]
    return f"{len(inv)}/{len(wo)} explicit-opener ({(100 * len(inv) / len(wo)) if wo else 0:.0f}%); {len(inv)}/{len(rows)} of all"


def rescore(rows, overrides, exclude_lifted=()):
    out = []
    for r in rows:
        x = dict(r)
        ov = overrides.get(x["id"], {})
        x.update({k: v for k, v in ov.items() if k in ("premise_label", "correct_polarity")})
        excluded = bool(x.get("exclude")) and x["id"] not in exclude_lifted
        x["excluded"] = excluded
        x["inverted"] = (not excluded) and x["correct_polarity"] in ("YES", "NO") and x["opener"] in ("YES", "NO") and x["opener"] != x["correct_polarity"]
        out.append(x)
    return out


def main():
    m1 = load("m1", "measure_negated_premise_live_2026_11_16.py")
    m2 = load("m2", "measure_set2_live_2026_11_17.py")
    res = {"sets": {}}
    bad = False
    for label, sidecar_name, art_path, opener, has_groups in (
            ("SET #1 (29 rows)", "FROZEN_sidecar_2026_11_17.json", os.path.join(REPO, "eval", "results", "negated_premise_live_2026_11_16.json"), m1.opener, False),
            ("SET #2 (20 rows)", "FROZEN_set2_sidecar_2026_11_17.json", os.path.join(REPO, "eval", "results", "negated_premise_set2_live_2026_11_17.json"), m2.opener, True)):
        sc = json.load(io.open(os.path.join(HERE, sidecar_name), encoding="utf-8"))
        ok, actual = check_pin(sc)
        print(f"\n##### {label}  sidecar {sidecar_name}  frozen sha256 pin {'MATCHES' if ok else 'DOES NOT MATCH (actual ' + actual[:12] + ')'}")
        if not ok:
            bad = True
            continue
        overrides = {c["id"]: c["corrected"] for c in sc["corrections"]}
        rows = [x for x in json.load(io.open(art_path, encoding="utf-8"))["rows"] if "error" not in x]
        for x in rows:
            x["opener"] = opener(x["reply"])
            if not has_groups:
                x["exclude"] = False
        res["sets"][label] = {}
        for variant, lifted in (("sidecar applied, founder's exclusion KEPT", ()), ("sidecar applied, exclusion LIFTED for the corrected rows", tuple(overrides))):
            before = rescore(rows, {}, ())
            after = rescore(rows, overrides, lifted)
            if has_groups:
                pick = lambda rs: [x for x in rs if not x["excluded"] and x["scoring_group"] in ("negated", "tag_only", "leading_no_negation")]
                tp = lambda rs: [x for x in rs if not x["excluded"] and x["premise_label"] == "true_premise" and x["correct_polarity"] == "YES" and x["route"] == "model"]
            else:
                pick = lambda rs: [x for x in rs if x["negation_form"] != "none"]
                tp = lambda rs: [x for x in rs if x["premise_label"] == "true_premise" and x["correct_polarity"] == "YES" and x["negation_form"] != "none"]
            b, a = pick(before), pick(after)
            print(f"  [{variant}]")
            print(f"     negated-group inversion     before: {rate(b)}   after: {rate(a)}")
            print(f"     TRUE-premise YES rows       before: {len(tp(before))} rows, inverted {sum(x['inverted'] for x in tp(before))}   after: {len(tp(after))} rows, inverted {sum(x['inverted'] for x in tp(after))}")
            changed = [(x["id"], x["opener"], y["correct_polarity"], y["inverted"]) for x, y in zip(before, after) if (x["inverted"], x["correct_polarity"], x["premise_label"]) != (y["inverted"], y["correct_polarity"], y["premise_label"])]
            print(f"     rows whose verdict changed: {changed}")
            res["sets"][label][variant] = {"before": rate(b), "after": rate(a), "changed_rows": changed}
        for cid in overrides:
            r = [x for x in rows if x["id"] == cid][0]
            print(f"  the live reply to {cid}: opener {r['opener']} -> {r['reply'][:220]!r}")
    json.dump(res, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

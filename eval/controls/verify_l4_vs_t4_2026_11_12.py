# -*- coding: utf-8 -*-
"""CROSS-HARDWARE CHECK for the L4 fallback (2026-11-12): do replies change when L4 serves instead of T4?

WHY: scarcity is confirmed (Modal: "waiting to be scheduled on a GPU_T4 worker"), so L4 is added behind T4.
R24b says a reply is a property of the host as much as the code, so the fallback is not free: this puts the
same fixed probe set through a T4-ONLY and an L4-ONLY throwaway deployment of the SAME file and compares.

POPULATION (fixed, seeded, committed): 36 in-corpus gate questions (every k-th of eval_questions_003), 8
refusal-gate questions, 8 number-first compute/VAT questions (the parser fix), and the live EFD question.
The compute engines and routing are hardware-independent by construction, so those rows are CONTROLS for
the arms: a difference there would mean the arms differ in more than the GPU.

HOW (R16): writes the artifact after EVERY row, captures per-row errors instead of aborting, resumes from the
artifact -- and a resume carries DATA forward (replies), never a conclusion: every verdict is re-derived.

usage: python verify_l4_vs_t4_2026_11_12.py   (tokens from ~/.chike_modal_token.txt / CHIKE_MODAL_TOKEN)
"""
import glob
import io
import json
import os
import sys
import threading
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "l4_vs_t4_2026_11_12.json")
ARMS = {
    "T4": "https://prosperpiusmbaruku007--chike-inference-t4test-web-endpoint.us-east.modal.run",
    "L4": "https://prosperpiusmbaruku007--chike-inference-l4test-web-endpoint.us-east.modal.run",
}
HEALTH = {
    "T4": "https://prosperpiusmbaruku007--chike-inference-t4test-health.us-east.modal.run",
    "L4": "https://prosperpiusmbaruku007--chike-inference-l4test-health.us-east.modal.run",
}
EXTRA = [
    ("ctl_sdl_nf", "Nina wafanyakazi 12, mishahara yote kwa mwezi ni 6 milioni. SDL nitalipa kiasi gani?"),
    ("ctl_vat_nf", "Katika miezi 6 iliyopita nimeuza jumla ya TZS 120 milioni — je nimefika kiwango cha VAT?"),
    ("ctl_sdl_nf2", "Kampuni yenye wafanyakazi 15 inalipa SDL kiasi gani kwa mishahara ya jumla 9 milioni?"),
    ("ctl_pres_nf", "Mauzo yangu kwa mwaka ni 40 milioni, nitalipa kodi ya makadirio kiasi gani?"),
    ("ctl_pres_nf2", "Biashara yangu inauza 4 milioni kwa mwaka, kodi ya makadirio ni ngapi?"),
    ("ctl_vat_nf2", "Mauzo yangu ya mwaka ni TZS 250 milioni, je ni lazima kusajili VAT?"),
    ("ctl_vat_nf3", "Biashara yangu imepata mauzo ya TZS 95 milioni katika miezi 6 — je nimevuka kizingiti cha VAT?"),
    ("ctl_sdl_nf3", "Nina wafanyakazi 9, mishahara yote kwa mwezi ni 3.6 milioni. SDL ni kiasi gani?"),
    ("live_efd", "Efd ni lazima kwa biashara yenye mauzo ya milioni 15"),
]


def probes():
    rows = [json.loads(l) for l in open(os.path.join(REPO, "eval", "accuracy_gate", "eval_questions_003.jsonl"),
                                         encoding="utf-8") if l.strip()]
    gate = [(r["id"], r["question_sw"]) for r in rows[::max(1, len(rows) // 36)]][:36]
    ref = []
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "refusal_gate", "*.jsonl"))):
        for l in open(f, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                q = r.get("question_sw") or r.get("question")
                if q and r.get("expect", r.get("expected_intent")) not in (None,):
                    ref.append((r.get("id", "ref"), q))
    ref = [ref[i] for i in range(0, len(ref), max(1, len(ref) // 8))][:8]
    return gate + ref + EXTRA


def token():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return os.environ.get("CHIKE_MODAL_TOKEN") or io.open(p, encoding="utf-8").read().strip()


def load():
    if os.path.exists(OUT):
        return json.load(open(OUT, encoding="utf-8"))
    return {"probes": [], "arms": {"T4": {}, "L4": {}}, "device": {}}


_LOCK = threading.Lock()


def save(state):
    with _LOCK:
        tmp = OUT + ".tmp"
        json.dump(state, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        os.replace(tmp, OUT)


def ask(arm, q, tok):
    req = urllib.request.Request(f"{ARMS[arm]}?token={tok}", data=json.dumps({"message": q}).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    t = time.time()
    r = json.loads(urllib.request.urlopen(req, timeout=1200).read().decode("utf-8"))
    return r.get("reply"), round(time.time() - t, 1), r


def run_arm(arm, state, tok):
    for pid, q in state["probes_list"]:
        if pid in state["arms"][arm] and state["arms"][arm][pid].get("reply") is not None:
            continue                                    # resume: data only
        try:
            reply, secs, raw = ask(arm, q, tok)
            state["arms"][arm][pid] = {"q": q, "reply": reply, "secs": secs}
        except Exception as e:                           # noqa: BLE001
            state["arms"][arm][pid] = {"q": q, "reply": None, "error": f"{type(e).__name__}: {str(e)[:120]}"}
        save({k: v for k, v in state.items() if k != "probes_list"})
        print(f"[{arm}] {pid} {'ok' if state['arms'][arm][pid].get('reply') is not None else 'ERR'}", flush=True)


def device(arm, tok):
    try:
        with urllib.request.urlopen(f"{HEALTH[arm]}?deep=1&token={tok}", timeout=1200) as r:
            h = json.loads(r.read().decode("utf-8"))
        return (h.get("served") or {}).get("coldstart")
    except Exception as e:                               # noqa: BLE001
        return {"error": f"{type(e).__name__}: {str(e)[:100]}"}


def verdicts(state):
    out = []
    for pid, q in state["probes_list"]:
        a, b = state["arms"]["T4"].get(pid, {}), state["arms"]["L4"].get(pid, {})
        if a.get("reply") is None or b.get("reply") is None:
            out.append((pid, "MISSING", a.get("error"), b.get("error")))
        else:
            out.append((pid, "IDENTICAL" if a["reply"] == b["reply"] else "DIFFERENT", a["reply"], b["reply"]))
    return out


def main():
    tok = token()
    state = load()
    state["probes_list"] = [tuple(x) for x in probes()]
    state["probes"] = [p for p, _ in state["probes_list"]]
    # SELF-CHECK of the instrument (R26): the two arms must actually be different devices.
    th = [threading.Thread(target=lambda a=a: state["device"].__setitem__(a, device(a, tok))) for a in ARMS]
    [t.start() for t in th]; [t.join() for t in th]
    print("devices:", json.dumps({a: (d or {}).get("gpu") for a, d in state["device"].items()}), flush=True)
    save({k: v for k, v in state.items() if k != "probes_list"})
    th = [threading.Thread(target=run_arm, args=(a, state, tok)) for a in ARMS]
    [t.start() for t in th]; [t.join() for t in th]
    v = verdicts(state)
    n = {k: sum(1 for x in v if x[1] == k) for k in ("IDENTICAL", "DIFFERENT", "MISSING")}
    print("RESULT", json.dumps(n))
    state["summary"] = n
    save({k: x for k, x in state.items() if k != "probes_list"})


if __name__ == "__main__":
    main()

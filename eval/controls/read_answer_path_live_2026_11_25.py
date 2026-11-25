"""READ-ONLY reader (R18: committed before its run) for the 2026-11-25 answer-path live check. Reads the transcript store and the review queue; sends nothing, approves nothing, writes only its own artifact.
It NEVER records a sender number or hash: only the question, the logged trace, the stored draft, the status and the holding / auto-send fields.

Rows are the TEST-sender question rows written by build BUILD since the deploy. Each is matched to the pre-registered prediction (eval/results/predict_answer_paths_2026_11_25.json, plus the four recall checks R1-R4, predicted from the same code reading: all four land on the model path)
and to its review item by the shared (sender_hash, question) pair, which stays internal.
    BUILD=71bbf08 python eval/controls/read_answer_path_live_2026_11_25.py  ->  eval/results/answer_path_live_2026_11_25.json"""
import io
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILD = os.environ.get("BUILD", "71bbf08")
RECALL = {"Mfanyakazi mgeni analipa PAYE kiasi gani?": "fact_model", "Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?": "fact_model",
          "Kodi ya PAYE Kenya ni asilimia ngapi?": "fact_model", "Mechi ya Simba na Yanga ni lini?": "fact_model"}


def _norm(q):
    return " ".join(str(q or "").split()).lower()


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import modal
    pred = json.load(io.open(os.path.join(_ROOT, "eval", "results", "predict_answer_paths_2026_11_25.json"), encoding="utf-8"))["rows"]
    predicted = {_norm(r["q"]): r["predicted"] for r in pred}
    predicted.update({_norm(q): c for q, c in RECALL.items()})
    tr = modal.Dict.from_name("chike-transcripts-kv")
    rq = modal.Dict.from_name("chike-review-queue-kv")
    rows = [v for _, v in tr.items() if isinstance(v, dict) and v.get("kind") == "question" and v.get("build") == BUILD and v.get("test_sender")]
    rows.sort(key=lambda r: r.get("ts", ""))
    items = [v for _, v in rq.items() if isinstance(v, dict)]
    out = []
    for r in rows:
        it = next((i for i in items if i.get("sender_hash") == r.get("sender_hash") and _norm(i.get("question")) == _norm(r.get("question"))), None)
        t = r.get("answer_trace") or {}
        q = r.get("question")
        out.append({"ts": r.get("ts"), "question": q, "predicted": predicted.get(_norm(q)), "answer_path_row": r.get("answer_path"), "answer_path_item": (it or {}).get("answer_path"),
                    "logged_cls": t.get("cls"), "routes": t.get("routes"), "model_calls": t.get("model_calls"), "guard_fired": t.get("guard_fired"), "guards": t.get("guards"),
                    "item_trace_cls": ((it or {}).get("answer_trace") or {}).get("cls"), "fallback": r.get("fallback"), "error_class": r.get("error_class"),
                    "status": (it or {}).get("status"), "holding_notice_ts": (it or {}).get("holding_notice_ts"), "holding_notice_ok": (it or {}).get("holding_notice_ok"),
                    "auto_sent": (it or {}).get("status") == "auto_sent", "review_id": (it or {}).get("review_id"), "draft": (it or {}).get("draft") or r.get("reply")})
    art = {"build": BUILD, "n": len(out), "rows": out,
           "consistent_trace": all(o["logged_cls"] == o["item_trace_cls"] for o in out if o["item_trace_cls"] is not None),
           "unmatched_to_prediction": [o["question"] for o in out if o["predicted"] is None]}
    json.dump(art, io.open(os.path.join(_ROOT, "eval", "results", "answer_path_live_2026_11_25.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for i, o in enumerate(out, 1):
        print(f"{i:>2} pred={o['predicted']!s:<16} logged={o['logged_cls']!s:<16} path={o['answer_path_item']!s:<22} calls={o['model_calls']} guard={o['guard_fired']} status={o['status']} hold={bool(o['holding_notice_ts'])} | {str(o['question'])[:60]}")
    print(f"{len(out)} rows | trace consistent row/item: {art['consistent_trace']} | unmatched to a prediction: {len(art['unmatched_to_prediction'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

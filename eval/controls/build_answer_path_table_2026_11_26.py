"""Builds the 20-row table of the 2026-11-25 answer-path live check FROM eval/results/answer_path_live_2026_11_25.json (rows read from the TRANSCRIPT STORE,
since the review items were cleared). Pure: no network. A field that cannot be recovered is printed as `lost`, never inferred.
  python eval/controls/build_answer_path_table_2026_11_26.py  ->  eval/results/answer_path_live_table_2026_11_26.md"""
import io
import json
import os
import re

R = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "eval", "results")


def _n(q):
    return re.sub(r"[?\s]+", " ", str(q or "")).strip().lower()


def main():
    art = json.load(io.open(os.path.join(R, "answer_path_live_2026_11_25.json"), encoding="utf-8"))
    pred = json.load(io.open(os.path.join(R, "predict_answer_paths_2026_11_25.json"), encoding="utf-8"))
    pmap = {_n(r["q"]): r["predicted"] for r in pred["rows"]}
    # the four recall checks R1-R4 were predicted "model path" in the reader's own RECALL table; the two wording changes below are recorded
    recall = {_n("Mfanyakazi mgeni analipa PAYE kiasi gani?"): "fact_model", _n("Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?"): "fact_model",
              _n("Kodi ya PAYE china ni asilimia ngapi?"): "fact_model (pre-registered for the 'Kenya' wording; the live text said 'china')",
              _n("Mechi ya Simba na Yanga ni lini?"): "fact_model"}
    pmap.update(recall)
    pmap[_n("Nina wafanyakazi 17 kila mmoja analipwa TZS 500,000, SDL ni kiasi gani kwa mwezi?")] = "engine (pre-registered for the '12 wafanyakazi' wording; the live text said 17)"
    out = ["# 2026-11-25 answer-path live check, 20 rows (rebuilt 2026-11-26 from the TRANSCRIPT rows)", "",
           "Source: `eval/results/answer_path_live_2026_11_25.json` (test-sender question rows, build `71bbf08`). **`lost` = not recoverable from the transcript row; nothing is guessed.**",
           "*Exact reply* = the `reply` stored on the transcript row: the answer the system generated and held for review. In supervised mode the participant received a holding message or the reviewed text, so this is NOT proof of what reached the phone.",
           "*Served path* = `answer_path` on the row. A review item (which also carries the reviewer's final text) survives for only the rows marked, so what the reviewer approved is `lost` for the rest.", ""]
    for i, r in enumerate(art["rows"], 1):
        p = pmap.get(_n(r["question"]), "lost")
        item = "recovered (item still in the store)" if r.get("review_id") else "lost (item cleared)"
        out += [f"### {i}. {r['question']}", "",
                f"| field | value |", "|---|---|",
                f"| predicted class | {p} |", f"| served path (row) | {r.get('answer_path_row') or 'lost'} |",
                f"| logged class | {r.get('logged_cls') or 'lost'} |", f"| route(s) | {', '.join(r['routes']) if r.get('routes') else 'lost'} |",
                f"| model calls | {r['model_calls'] if r.get('model_calls') is not None else 'lost'} |",
                f"| guard fired | {r['guard_fired'] if r.get('guard_fired') is not None else 'lost'}{(' — ' + ', '.join(map(str, r['guards']))) if r.get('guards') else ''} |",
                f"| review item / reviewer's final | {item}; status {r.get('status') or 'lost'} |",
                f"| logged class matches prediction | {'yes' if str(p).split(' ')[0] == r.get('logged_cls') else 'NO' if p != 'lost' else 'lost'} |", "",
                "> " + (r.get("draft") or "lost").replace("\n", "\n> "), ""]
    miss = [i for i, r in enumerate(art["rows"], 1) if str(pmap.get(_n(r["question"]), "lost")).split(" ")[0] != r.get("logged_cls")]
    out += ["---", f"**Logged class differs from the prediction on row(s): {miss or 'none'}.**"]
    io.open(os.path.join(R, "answer_path_live_table_2026_11_26.md"), "w", encoding="utf-8").write("\n".join(out))
    print("rows", len(art["rows"]), "mismatches", miss)


if __name__ == "__main__":
    main()

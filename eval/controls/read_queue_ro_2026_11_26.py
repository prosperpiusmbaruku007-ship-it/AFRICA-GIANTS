# READ-ONLY snapshot of the review queue: no writes, no claims, no sends. Text-free except the participant's question (test phone).
import modal, json, sys, datetime
d = modal.Dict.from_name("chike-review-queue-kv")
rows = []
for k in d.keys():
    try: v = d[k]
    except Exception: continue
    if isinstance(v, dict) and v.get("held_at", "") >= (sys.argv[2] if len(sys.argv) > 2 else "2026-11-26T06:00"):
        rows.append({k2: v.get(k2) for k2 in ("review_id", "status", "ts_held", "held_at", "question", "answer_path", "model_calls", "notify_count",
                     "renotify_count", "first_notified_at", "last_notified_at", "holding_notice_ts", "holding_notice_ok", "claimed_by", "sender_tail")})
rows.sort(key=lambda r: r["ts_held"] or "")
ceil = {}
try:
    c = modal.Dict.from_name("chike-send-ceiling-kv")
    for k in c.keys():
        ks = str(k)
        if ks.startswith("alert:"): ceil.setdefault("_alerts", []).append(ks); continue
        ms, tag, _ = ks.split(":", 2)
        ceil.setdefault(tag, []).append(datetime.datetime.fromtimestamp(float(ms)/1000, datetime.timezone.utc).isoformat(timespec="seconds"))
except Exception as e:
    ceil = {"_error": type(e).__name__}
out = {"send_ledger_last_hour_by_recipient_tag": ceil, "read_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "rows": rows}
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("rows", len(rows))

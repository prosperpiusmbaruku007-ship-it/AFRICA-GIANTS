# -*- coding: utf-8 -*-
"""ONE-OFF REPAIR (2026-11-12): reconcile `pending_receipt` rows whose late receipt the bug could not reach.

WHY THEY ARE STUCK: `_write_row` called transcript_filename() twice (random suffix each call), so
PENDING_ROWS registered a filename that was never stored and the late-receipt reconcile could never find
the row. Fixed in e86b4cd; rows written BEFORE the fix were never registered correctly and stay pending
for ever. The bridge ledger holds the receipts (status `read`), so the truth is recoverable.

WHAT IT DOES: for every transcript row AND review-queue item whose send_state is `pending_receipt`, look the
WhatsApp message id up in the bridge ledger and, if a receipt exists, apply handler_core.reconcile_row with
source="manual_repair_2026-11-12 (pending_row_registry bug, e86b4cd)". reconcile_row KEEPS the original state
(`send_state_at_send`, `send_ok_at_send`) and now records `reconciled_by` / `reconciled_ts`, so the repaired
row says that it was repaired after the fact, by what, and when. A row with no receipt in the ledger is left
exactly as it was. Idempotent: a reconciled row is no longer pending, so a second run changes nothing.

Prints before/after for every row it touches.
"""
import importlib.util
import json
import os
import sys

import modal

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SOURCE = "manual_repair_2026-11-12 (pending_row_registry bug, e86b4cd)"


def core():
    spec = importlib.util.spec_from_file_location(
        "hc_repair", os.path.join(REPO, "chike-whatsapp", "handler_core.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    hc = core()
    T = modal.Dict.from_name("chike-transcripts-kv", create_if_missing=False)
    Q = modal.Dict.from_name("chike-review-queue-kv", create_if_missing=False)
    L = modal.Dict.from_name("chike-bridge-ledger-kv", create_if_missing=False)
    touched = 0
    for store_name, store in (("transcript", T), ("queue", Q)):
        for k in list(store.keys()):
            if str(k).startswith("TEST-"):
                continue
            row = store[k]
            if row.get("send_state") != "pending_receipt":
                continue
            mid = hc.pending_message_id(row)
            led = L.get(mid) if mid else None
            fixed = hc.reconcile_row(row, led, source=SOURCE)
            tag = f"{store_name} {str(k)[:34]} id={mid}"
            if fixed is None:
                print(f"LEFT   {tag}: no receipt in the ledger (ledger row: {led})")
                continue
            store[k] = fixed
            back = store[k]
            assert back["send_state"] == "delivered" and back["reconciled_by"] == SOURCE, back
            print(f"FIXED  {tag}: {row['send_state']}/{row.get('send_ok')} -> {back['send_state']}/{back['send_ok']}"
                  f"  lag={back['receipt_lag_s']}s  was={back['send_state_at_send']}  by={back['reconciled_by'][:28]}")
            touched += 1
    print("rows reconciled:", touched)
    left = [(n, k) for n, s in (("transcript", T), ("queue", Q)) for k in s.keys()
            if not str(k).startswith("TEST-") and s[k].get("send_state") == "pending_receipt"]
    print("still pending_receipt after repair:", left)


if __name__ == "__main__":
    main()

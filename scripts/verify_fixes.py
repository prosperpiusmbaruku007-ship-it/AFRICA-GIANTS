"""Verify both EOS fixes are present in both notebook copies."""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

for path in [
    r"C:\Users\jhjh\AFRICA-GIANTS\notebooks\kaggle_train_arque_llama.ipynb",
    r"C:\Users\jhjh\AFRICA-GIANTS\kaggle\kaggle_train_arque_llama.ipynb",
]:
    nb = json.load(open(path, encoding="utf-8"))
    print(f"\n=== {path} ===")
    for c in nb["cells"]:
        cid = c.get("id", "?")
        if cid in ("cell-data", "cell-train"):
            s = "".join(c["source"])
            print(f"  [{cid}] lines={len(s.splitlines())}")
            if cid == "cell-data":
                print(f"    monkey-patch:        {'SFTTrainer.__init__ = _patched_init' in s}")
                print(f"    [patch] print:       {'monkey-patched' in s}")
            else:
                print(f"    _resolved_eos:       {'_resolved_eos' in s}")
                print(f"    -- 0. EOS guard:     {'-- 0. EOS guard' in s}")
                print(f"    -- 4b override:      {'-- 4b' in s}")
                print(f"    eos_token in _sft:   {chr(34)+'eos_token'+chr(34)+': _resolved_eos' in s}")

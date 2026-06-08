"""Search-only: print every cell that contains any of the target strings."""
import json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TARGETS = ["EOS_TOKEN", "get_chat_template", "eos_token"]

for nb_path in [
    r"C:\Users\jhjh\AFRICA-GIANTS\notebooks\kaggle_train_arque_llama.ipynb",
    r"C:\Users\jhjh\AFRICA-GIANTS\kaggle\kaggle_train_arque_llama.ipynb",
]:
    print(f"\n{'='*70}")
    print(f"FILE: {nb_path}")
    print(f"{'='*70}")
    with open(nb_path, encoding="utf-8") as f:
        nb = json.load(f)
    found_any = False
    for cell in nb["cells"]:
        cid = cell.get("id", "?")
        src = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
        hits = [t for t in TARGETS if t in src]
        if hits:
            found_any = True
            print(f"\n  *** CELL: {cid}  matched: {hits} ***")
            print("  " + "-"*60)
            for line in src.splitlines():
                print("  " + line)
            print("  " + "-"*60)
    if not found_any:
        print("  (no matches)")

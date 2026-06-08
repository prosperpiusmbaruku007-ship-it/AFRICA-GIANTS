"""
Verify the pushed Kaggle version by:
1. Reading the kaggle/ notebook and checking get_chat_template is absent
2. Computing a hash of the file so we can confirm what was pushed
3. Querying every available Kaggle API endpoint for version number
"""
import sys, json, os, hashlib, requests
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv(r"C:\Users\jhjh\AFRICA-GIANTS\.env")

token = (os.environ.get("KAGGLE_API_TOKEN")
         or os.environ.get("KGAT")
         or open(os.path.expanduser("~/.kaggle/access_token")).read().strip())

owner, slug = "prospaprospa", "africa-giants-trainer"
auth = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# ── 1. Verify local file pushed ────────────────────────────────────────────────
nb_path = r"C:\Users\jhjh\AFRICA-GIANTS\kaggle\kaggle_train_arque_llama.ipynb"
with open(nb_path, encoding="utf-8") as f:
    nb_raw = f.read()
    nb = json.loads(nb_raw)

md5 = hashlib.md5(nb_raw.encode("utf-8")).hexdigest()
hit = "get_chat_template" in nb_raw

all_sources = []
for cell in nb["cells"]:
    src = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
    all_sources.append(src)
full_text = "\n".join(all_sources)

print("=== Local kaggle/ notebook ===")
print(f"  MD5                   : {md5}")
print(f"  get_chat_template     : {'PRESENT ← PROBLEM' if hit else 'ABSENT  ✓'}")
print(f"  EOS_TOKEN (uppercase) : {'present' if 'EOS_TOKEN' in full_text else 'absent'}")
print(f"  eos_token (lowercase) : {'present' if 'eos_token' in full_text else 'absent'}")

# ── 2. Session status ─────────────────────────────────────────────────────────
print("\n=== Kaggle session status ===")
r = requests.post(
    "https://www.kaggle.com/api/v1/kernels.KernelsApiService/GetKernelSessionStatus",
    headers=auth,
    json={"userName": owner, "kernelSlug": slug},
    timeout=15,
)
print(f"  HTTP {r.status_code}: {r.text[:300]}")

# ── 3. kernels_list to get version info ───────────────────────────────────────
print("\n=== Kernel list (user kernels) ===")
r2 = requests.get(
    f"https://www.kaggle.com/api/v1/kernels?user={owner}&search={slug}&pageSize=1",
    headers={"Authorization": f"Bearer {token}"},
    timeout=15,
)
print(f"  HTTP {r2.status_code}: {r2.text[:600]}")

# ── 4. pipeline state ─────────────────────────────────────────────────────────
print("\n=== pipeline_state.json ===")
with open(r"C:\Users\jhjh\AFRICA-GIANTS\models\pipeline_state.json", encoding="utf-8") as f:
    state = json.load(f)
print(f"  completed_steps : {state['completed_steps']}")
print(f"  kaggle_trigger  : {'done' if 'kaggle_trigger' in state['completed_steps'] else 'NOT done'}")

# ── 5. Latest git commit ──────────────────────────────────────────────────────
import subprocess
git = subprocess.run(
    ["git", "log", "--oneline", "-3"],
    capture_output=True, text=True,
    cwd=r"C:\Users\jhjh\AFRICA-GIANTS"
)
print("\n=== Last 3 commits ===")
print(git.stdout)

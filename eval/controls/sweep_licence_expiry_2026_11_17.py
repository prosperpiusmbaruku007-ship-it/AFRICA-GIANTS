"""SWEEP EVERY PLACE THAT STATES A BUSINESS-LICENCE EXPIRY DATE (30 June / 31 March) -- 2026-11-17.
The Business Licensing Act (Cap.101 R.E.2023 s.7(1)) makes a licence valid TWELVE MONTHS FROM ISSUANCE; 30 June was the pre-2014 rule (Cap.208 R.E.2002 s.7) and 31 March the 1972 original.
Reports every line where a licence word and a stale date sit within WINDOW characters, by file, so each can be read (R37: read the rows before removing).
    python eval/controls/sweep_licence_expiry_2026_11_17.py  ->  eval/results/sweep_licence_expiry_2026_11_17.json"""
import io, json, os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
LIC = re.compile(r"leseni|licen[cs]e", re.I)
DATE = re.compile(r"(?<!\d)(?:30\s*(?:juni|june)|(?:juni|june)\s*30(?!\d)|31\s*(?:machi|march)|thirtieth\s+day\s+of\s+june|30th\s+june)", re.I)
WINDOW = 220
SKIP_DIRS = {".git", "__pycache__", "node_modules", "scratch", ".venv"}
EXT = {".py", ".json", ".jsonl", ".md", ".txt", ".html", ".yaml", ".yml", ".sh"}


def scan_text(path, text):
    hits = []
    for ln, line in enumerate(text.splitlines(), 1):
        for m in DATE.finditer(line):
            seg = line[max(0, m.start() - WINDOW): m.end() + WINDOW]
            if LIC.search(seg):
                hits.append((ln, m.group(0), seg.strip()[:260]))
                break
    return hits


def main():
    out = {}
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1].lower() not in EXT:
                continue
            p = os.path.join(root, f)
            if os.path.getsize(p) > 60_000_000 or "data" + os.sep + "source_documents" in p:
                continue
            try:
                t = io.open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            h = scan_text(p, t)
            if h:
                out[os.path.relpath(p, REPO).replace(os.sep, "/")] = h
    json.dump({"files": {k: [{"line": a, "match": b, "ctx": c} for a, b, c in v] for k, v in out.items()}}, io.open(os.path.join(REPO, "eval", "results", "sweep_licence_expiry_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in sorted(out.items(), key=lambda kv: -len(kv[1])):
        print(f"{len(v):>5}  {k}")
    print("TOTAL files", len(out), "lines", sum(len(v) for v in out.values()))


if __name__ == "__main__":
    main()

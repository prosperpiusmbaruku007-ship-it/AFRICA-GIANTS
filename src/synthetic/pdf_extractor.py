import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

SOURCE_URL_MAP = {
    "tra":         "tra.go.tz",
    "brela":       "brela.go.tz",
    "osha":        "osha.go.tz",
    "nssf":        "nssf.or.tz",
    "wcf":         "wcf.go.tz",
    "labour":      "labour.go.tz",
    "immigration": "immigration.go.tz",
    "general":     "tanzlii.org",
}

RAW_EXTRACTED_DIR = 'data/raw/extracted'


def extract_document(path: str) -> dict:
    p   = Path(path)
    ext = p.suffix.lower()
    category   = p.parent.name
    source_url = SOURCE_URL_MAP.get(category, "tanzlii.org")

    with open(path, 'rb') as f:
        source_md5 = hashlib.md5(f.read()).hexdigest()

    if ext == '.pdf':
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            sections = [
                {'heading': f'Page {i + 1}', 'content': page.extract_text() or ''}
                for i, page in enumerate(pdf.pages)
            ]
        total_chars = sum(len(s['content']) for s in sections)
        num_pages   = len(sections)
        if total_chars < 100 * num_pages:
            raise ValueError(
                f"PDF appears to be image-only ({total_chars} chars from {num_pages} pages). "
                f"Convert to text-layer PDF or save as .txt first."
            )

    elif ext == '.html':
        from bs4 import BeautifulSoup
        raw  = open(path, encoding='utf-8').read()
        soup = BeautifulSoup(raw, 'lxml')
        content_el = (
            soup.find('article') or
            soup.find('main') or
            soup.find(id='content') or
            soup.find(class_='content') or
            soup.find(class_='article-body') or
            soup
        )
        text     = content_el.get_text(separator='\n', strip=True)
        sections = [{'heading': 'Main Content', 'content': text}]

    elif ext == '.txt':
        content  = open(path, encoding='utf-8').read()
        sections = [{'heading': 'Full Text', 'content': content}]

    else:
        raise ValueError(f"Unsupported format: {path}. Supported: .pdf .html .txt")

    document = {
        "source_file":     p.name,
        "source_category": category,
        "source_url":      source_url,
        "source_document": str(path),
        "source_md5":      source_md5,
        "extracted_at":    datetime.now(timezone.utc).isoformat(),
        "sections":        sections,
    }

    out_dir  = os.path.join(RAW_EXTRACTED_DIR, category)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{source_md5}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(document, f, ensure_ascii=False, indent=2)
    print(f"[extractor] {p.name} -> {out_path} ({len(sections)} sections)")

    return document

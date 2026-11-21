import pymupdf


def extract_pages(pdf_path):
    """Return a list like [{"page": 1, "text": "..."}, ...]. Empty pages are skipped."""
    pages = []
    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text().strip()
            if text:
                pages.append({"page": page_number, "text": text})
    return pages


def extract_text_from_pdf(pdf_path):
    """Whole document as one string (kept so main.py still works)."""
    return "\n".join(p["text"] for p in extract_pages(pdf_path))
import pymupdf
from backend.pdf_utils import extract_pages


def make_pdf(path, page_texts):
    """Create a small PDF for testing. An empty string makes an empty page."""
    doc = pymupdf.open()
    for text in page_texts:
        page = doc.new_page()
        if text:
            page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


def test_extract_pages_keeps_page_numbers(tmp_path):
    pdf = tmp_path / "test.pdf"
    make_pdf(pdf, ["Hello page one", "Hello page two"])
    pages = extract_pages(str(pdf))
    assert [p["page"] for p in pages] == [1, 2]
    assert "page one" in pages[0]["text"]


def test_extract_pages_skips_empty_pages(tmp_path):
    pdf = tmp_path / "test.pdf"
    make_pdf(pdf, ["First", "", "Third"])
    pages = extract_pages(str(pdf))
    assert [p["page"] for p in pages] == [1, 3]
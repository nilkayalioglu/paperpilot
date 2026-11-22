from backend.config import CHUNK_CHARS, CHUNK_OVERLAP


def split_text(text, size=CHUNK_CHARS, overlap=CHUNK_OVERLAP):
    """Split text into pieces of at most `size` characters.
    Consecutive pieces share `overlap` characters."""
    pieces = []
    step = size - overlap
    start = 0
    while start < len(text):
        pieces.append(text[start:start + size])
        if start + size >= len(text):
            break
        start = start + step
    return pieces


def chunk_pages(pages, size=CHUNK_CHARS, overlap=CHUNK_OVERLAP):
    """Split every page into pieces. Each piece keeps its page number."""
    chunks = []
    for page in pages:
        for piece in split_text(page["text"], size, overlap):
            chunks.append({"page": page["page"], "text": piece})
    return chunks
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
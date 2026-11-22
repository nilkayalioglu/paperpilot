import ollama
from backend.config import OLLAMA_HOST, EMBED_MODEL, CHUNK_CHARS, CHUNK_OVERLAP

client = ollama.Client(host=OLLAMA_HOST)

def split_text(text, size=CHUNK_CHARS, overlap=CHUNK_OVERLAP):
    """Split text into pieces of at most `size` characters.
    Consecutive pieces share `overlap` characters."""
     
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("size must be > 0 and 0 <= overlap < size")
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


def embed_texts(texts):
    """Turn a list of texts into a list of vectors (768 numbers each)."""
    if not texts:
        return []
    response = client.embed(model=EMBED_MODEL, input=texts)
    return response["embeddings"]


def embed_chunks(chunks):
    """Embed every chunk once, when the PDF is uploaded."""
    texts = ["search_document: " + c["text"] for c in chunks]   
    return embed_texts(texts)
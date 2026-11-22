import numpy as np
import ollama
from backend.config import OLLAMA_HOST, EMBED_MODEL, CHUNK_CHARS, CHUNK_OVERLAP, TOP_K

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


def cosine_similarity(a, b):
    """1 = same direction (similar meaning), 0 = unrelated, -1 = opposite."""
    a, b = np.array(a), np.array(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def rank_chunks(question_vector, chunks, vectors, k=TOP_K):
    """Return the k chunks closest to the question, best first, with their score."""
    scores = [cosine_similarity(question_vector, v) for v in vectors]
    ranked = sorted(zip(scores, chunks), key=lambda pair: pair[0], reverse=True)
    results = []
    for score, chunk in ranked[:k]:
        results.append({"page": chunk["page"], "text": chunk["text"], "score": score})
    return results


def search(question, chunks, vectors, k=TOP_K):
    """Embed the question and find the closest chunks."""
    question_vector = embed_texts(["search_query: " + question])[0]
    return rank_chunks(question_vector, chunks, vectors, k)
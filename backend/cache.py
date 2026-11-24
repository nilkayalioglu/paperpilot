import hashlib
import json
import sqlite3

from backend.config import CACHE_PATH, CHAT_MODEL, CHUNK_CHARS, CHUNK_OVERLAP, EMBED_MODEL, SECTION_CHARS
from backend.pdf_utils import extract_pages
from backend.rag import chunk_pages, embed_chunks
from backend.summarizer import summarize_long


def file_hash(pdf_path):
    """Return a fingerprint of the file's contents (same file -> same hash)."""
    with open(pdf_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def connect(db_path=CACHE_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS chunks (doc_hash TEXT, model TEXT, idx INTEGER, page INTEGER, text TEXT, vector TEXT, PRIMARY KEY (doc_hash, model, idx))""")
    conn.execute("""CREATE TABLE IF NOT EXISTS summaries (doc_hash TEXT, model TEXT, summary TEXT, PRIMARY KEY (doc_hash, model))""")
    return conn


def save_chunks(conn, doc_hash, model, chunks, vectors):
    """Store each chunk and its vector so the PDF does not need to be embedded again."""
    rows = []
    for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
        rows.append((doc_hash, model, idx, chunk["page"], chunk["text"], json.dumps(vector)))
    conn.executemany("INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?, ?, ?)", rows)
    conn.commit()


def load_chunks(conn, doc_hash, model):
    """Return (chunks, vectors) saved for this PDF and model, or ([], []) if not cached."""
    rows = conn.execute(
        "SELECT page, text, vector FROM chunks WHERE doc_hash = ? AND model = ? ORDER BY idx",
        (doc_hash, model),
    ).fetchall()
    chunks = [{"page": page, "text": text} for page, text, vector in rows]
    vectors = [json.loads(vector) for page, text, vector in rows]
    return chunks, vectors

def load_or_build(pdf_path, conn):
    doc_hash = file_hash(pdf_path)
    cache_key = f"{EMBED_MODEL}|{CHUNK_CHARS}|{CHUNK_OVERLAP}"
    chunks, vectors = load_chunks(conn, doc_hash, cache_key)
    if chunks:
        return chunks, vectors
    chunks = chunk_pages(extract_pages(pdf_path))
    vectors = embed_chunks(chunks)
    save_chunks(conn, doc_hash, cache_key, chunks, vectors)
    return chunks, vectors


def save_summary(conn, doc_hash, model, summary):
    conn.execute("INSERT OR REPLACE INTO summaries VALUES (?, ?, ?)", (doc_hash, model, summary))
    conn.commit()


def load_summary(conn, doc_hash, model):
    row = conn.execute("SELECT summary FROM summaries WHERE doc_hash = ? AND model = ?", (doc_hash, model)).fetchone()
    if row:
        return row[0]
    return None


def load_or_build_summary(pdf_path, conn):
    """Return the summary of a PDF, using the cache if this exact file was summarised before."""
    doc_hash = file_hash(pdf_path)
    cache_key = f"{CHAT_MODEL}|{SECTION_CHARS}"
    summary = load_summary(conn, doc_hash, cache_key)
    if summary:
        return summary
    pages = extract_pages(pdf_path)
    if not pages:
        return None
    summary = summarize_long(pages)
    save_summary(conn, doc_hash, cache_key, summary)
    return summary
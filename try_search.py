import sys

from backend.pdf_utils import extract_pages
from backend.rag import chunk_pages, embed_chunks, search

pdf_path = sys.argv[1]
question = sys.argv[2]

chunks = chunk_pages(extract_pages(pdf_path))
vectors = embed_chunks(chunks)

for r in search(question, chunks, vectors):
    print(f"page {r['page']}  score {r['score']:.2f}  {r['text'][:80]!r}")
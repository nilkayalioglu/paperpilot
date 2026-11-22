import sys

from backend.pdf_utils import extract_pages
from backend.rag import chunk_pages, embed_chunks, answer, format_sources

pdf_path = sys.argv[1]
question = sys.argv[2]

chunks = chunk_pages(extract_pages(pdf_path))
vectors = embed_chunks(chunks)

reply, sources = answer(question, chunks, vectors)

print("Sources:")
for s in sources:
    print(f"  page {s['page']}  score {s['score']:.2f}")
print()
print("Answer:")
print(reply)
print(format_sources(sources))
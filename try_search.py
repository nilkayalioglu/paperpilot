import sys
import time

from backend.cache import connect, load_or_build
from backend.rag import answer, format_sources

pdf_path = sys.argv[1]
question = sys.argv[2]

conn = connect()
start = time.time()
chunks, vectors = load_or_build(pdf_path, conn)
print(f"Loaded {len(chunks)} chunks in {time.time() - start:.1f}s")

reply, sources = answer(question, chunks, vectors)

print("Sources:")
for s in sources:
    print(f"  page {s['page']}  score {s['score']:.2f}")
print()
print("Answer:")
print(reply)
print(format_sources(sources))
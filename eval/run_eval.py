import json
import sys

from backend.cache import connect, load_or_build
from backend.config import CHAT_MODEL
from backend.evaluation import is_correct, is_not_found, retrieval_hit
from backend.rag import answer, search

PDF_PATH = sys.argv[1] if len(sys.argv) > 1 else "papers/attention.pdf"
QUESTIONS_PATH = sys.argv[2] if len(sys.argv) > 2 else "eval/questions.json"

with open(QUESTIONS_PATH) as f:
    questions = json.load(f)

conn = connect()
chunks, vectors = load_or_build(PDF_PATH, conn)

hits = 0
correct = 0
not_found_ok = 0
answerable_total = 0
unanswerable_total = 0

print(f"Model: {CHAT_MODEL}\n")

for q in questions:
    reply, _ = answer(q["question"], chunks, vectors)

    if q["answerable"]:
        answerable_total += 1
        results = search(q["question"], chunks, vectors)
        hit = retrieval_hit(q["pages"], results)
        ok = is_correct(q["answer"], reply)
        hits += hit
        correct += ok
        print(f"Q{q['id']:>2}  page hit: {hit}  correct: {ok}")
    else:
        unanswerable_total += 1
        ok = is_not_found(reply)
        not_found_ok += ok
        print(f"Q{q['id']:>2}  said not found: {ok}")

    print(f"     reply: {reply.replace(chr(10), ' ')[:100]}")

print()
print(f"Retrieval hit@4:     {hits}/{answerable_total}")
print(f"Correct answers:     {correct}/{answerable_total}")
print(f"Said not found:      {not_found_ok}/{unanswerable_total}")
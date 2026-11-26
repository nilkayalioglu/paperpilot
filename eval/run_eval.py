import json
import sys

from backend.cache import connect, load_or_build
from backend.config import CHAT_MODEL
from backend.evaluation import is_correct, is_not_found, retrieval_hit
from backend.rag import answer, search

PDF_PATH = sys.argv[1] if len(sys.argv) > 1 else "papers/attention.pdf"
QUESTIONS_PATH = sys.argv[2] if len(sys.argv) > 2 else "eval/questions.json"
RUNS = int(sys.argv[3]) if len(sys.argv) > 3 else 3


def run_once(questions, chunks, vectors):
    """Ask every question once. Return (correct answers, correct 'not found' replies)."""
    correct = 0
    not_found_ok = 0
    for q in questions:
        reply, _ = answer(q["question"], chunks, vectors)
        if q["answerable"]:
            ok = is_correct(q["answer"], reply)
            correct += ok
            print(f"Q{q['id']:>2}  correct: {ok}")
        else:
            ok = is_not_found(reply)
            not_found_ok += ok
            print(f"Q{q['id']:>2}  said not found: {ok}")
        print(f"     reply: {reply.replace(chr(10), ' ')[:100]}")
    return correct, not_found_ok


with open(QUESTIONS_PATH) as f:
    questions = json.load(f)

answerable = [q for q in questions if q["answerable"]]
unanswerable = [q for q in questions if not q["answerable"]]

conn = connect()
chunks, vectors = load_or_build(PDF_PATH, conn)

# Retrieval does not depend on the chat model, so it is measured once.
hits = sum(retrieval_hit(q["pages"], search(q["question"], chunks, vectors)) for q in answerable)

print(f"Model: {CHAT_MODEL}, runs: {RUNS}\n")
results = []
for run in range(1, RUNS + 1):
    print(f"--- Run {run} ---")
    results.append(run_once(questions, chunks, vectors))
    print()

print(f"Retrieval hit@4: {hits}/{len(answerable)}")
for run, (correct, not_found_ok) in enumerate(results, start=1):
    print(f"Run {run}: correct {correct}/{len(answerable)}, said not found {not_found_ok}/{len(unanswerable)}")

total_correct = sum(c for c, _ in results)
total_not_found = sum(n for _, n in results)
print(f"Total:  correct {total_correct}/{len(answerable) * RUNS}, said not found {total_not_found}/{len(unanswerable) * RUNS}")
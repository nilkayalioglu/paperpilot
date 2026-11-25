# Development log

## 21 Nov
- Built PDF upload + summary with Gradio and Ollama (llama3.2:1b).
- Claude suggested map-reduce summarisation. I tested it on "Attention Is All You Need" (15 pages); the summary now includes results from later sections.

## 22 Nov
- Moved settings into backend/config.py.
- Added pytest tests. One test failed: `_clean_bullets` (written by Claude) left a double space after each bullet. I found it through the test, fixed the replace logic, and all 7 tests pass.

## 22 Nov (afternoon)
- Set up CodeRabbit AI code review on PRs. It found an edge case in `group_pages`: a single page over 6000 chars is not split and its end gets cut off. I checked it, agreed, and planned the fix using the new `split_text` helper.
- Wrote `split_text` and `chunk_pages` for RAG chunking. Worked out the overlap maths by hand first (2300 chars → 3 pieces), then wrote tests for it. A test caught a NameError before I committed.
- Fixed the `group_pages` edge case: long pages are now split with `split_text`, and the newline separator counts towards the limit. Added a test with a 6001-char page. 14 tests pass.
- CodeRabbit (PR #3) found that `split_text` loops forever if overlap >= size, because the step becomes 0 or negative. Added a ValueError check before the loop and a test for it.
- Answer generation works (correct answer about the derivative term), but llama3.2:1b doesn't write page numbers reliably. I tried few-shot prompting with an example answer; it still skipped the page and copied "steady-state error" from my example into the answer, which is wrong for the derivative term. Reverted the example. Decision: the UI will show source pages from retrieval instead of relying on the model. Next: compare with llama3.2:3b on an evaluation set.

## 23 Nov
- Built an evaluation set (eval/questions.json) on "Attention Is All You Need": 10 answerable and 5 unanswerable questions. I checked every answer and page number in the PDF myself. Two corrections: page 12 for d_model was the reference list, so I removed it, and the training time appears on both pages 7 and 8.
- Answerable questions: 10/10 answers correct, and the right page was in the top 4 every time. But the model wrote the wrong page in its own answer twice (Q4 said page 3, the answer is on page 5). This confirms showing source pages from retrieval instead of trusting the model.
- Unanswerable questions: 0/5. The model made up an answer every time instead of saying "I couldn't find this in the paper". Example: "GPT-3 has 101.6 million parameters (page 4)".
- The most dangerous case was Q15 (English-to-Spanish BLEU): the model gave the English-to-German score (28.4), with the highest similarity score of all (0.77), because the question is almost identical to a real sentence in the paper.
- Top similarity scores overlap: answerable 0.67–0.81, unanswerable 0.64–0.77. So MIN_SCORE alone cannot separate them. Next: write run_eval.py to measure this automatically and compare llama3.2:1b with 3b.

## 24 Nov
- Added a SQLite cache (backend/cache.py) for chunks and their embeddings. Each PDF is identified by a SHA-256 hash of its contents, not its file name, so a renamed copy of the same paper is recognised and two different papers with the same name don't get mixed up. I chose the hash after thinking through both cases.
- Loading the Attention paper took 11.3s the first time (embedding 49 chunks) and 0.0s from the cache, with identical similarity scores, so the cached vectors are the same as freshly computed ones.
- Vectors are stored as JSON text because SQLite has no list type. The primary key (doc_hash, model, idx) means changing the embedding model never mixes old and new vectors.
- Added 4 tests with a temporary database (tmp_path), so they don't need Ollama or touch the real cache. 33 tests pass. Note: tests only collect with `python -m pytest`, plain `pytest` can't find the backend package.
- Noticed that llama3.2:1b gave different answers to the same question with exactly the same retrieved chunks: "no mention of the number of heads" on one run, "8" on the next. The answers are not stable, which is another reason to compare it with 3b.
- CodeRabbit review on PR #5 found two issues, both fixed: `load_or_build` took a `model` argument that `embed_chunks` ignored, so vectors could be stored under the wrong model name (removed the argument, always use `EMBED_MODEL`); and `try_search.py` still ran the old embedding pipeline before the cached one, so every run embedded the PDF and called the model twice (removed the old lines). A third review asked to include chunking settings in the cache key; the key is now model|chunk_chars|overlap.
-Question phrasing matters for the 1b model: "How many heads?" got a wrong answer, while "How many attention heads does the Transformer use?" got the correct answer (8, page 5) with higher retrieval scores (0.67 → 0.77).
- Wrote eval/run_eval.py: asks all 15 questions in eval/questions.json and scores retrieval (Hit@4), answer accuracy and "not found" on unanswerable questions. The PDF and question file can be passed as arguments, so it works with any paper that has a question file. Added 6 tests for backend/evaluation.py (39 tests pass).
- Results on attention.pdf:
  - llama3.2:1b: Hit@4 10/10, correct 8/10, said "not found" 0/5.
  - llama3.2:3b: Hit@4 10/10, correct 10/10, said "not found" 5/5.
- Retrieval is the same for both models, so the difference comes from generation. 1b invented answers to all 5 unanswerable questions (e.g. it claimed a "BLEU score on ImageNet"); 3b followed the "reply exactly: I couldn't find this in the paper" instruction every time. Decision: default CHAT_MODEL is now llama3.2:3b; 1b can still be chosen with PAPERPILOT_CHAT_MODEL.
- Both models still write wrong page numbers in their answers sometimes (3b said page 2 and page 6 where the right pages were 5 and 8), while the system's "Sources" line from retrieval was always right. This confirms the earlier decision to show sources from retrieval in the UI.
- Limitation: these are single runs, and answers vary between runs because the model samples.
- Rebuilt the Gradio interface with gr.Blocks: one PDF upload shared by two tabs, "Summary" and "Ask a question". Answers show the source pages from retrieval in bold. When the model replies "I couldn't find this in the paper", the sources line is hidden, because showing pages next to "not found" was confusing.
- The SQLite connection is opened and closed inside each button handler, because Gradio runs handlers in worker threads and a SQLite connection can only be used in the thread that created it.
- Summaries were slow with llama3.2:3b, because summarize_long makes one model call per section plus one to combine the notes, and nothing was saved. Added a `summaries` table to the cache, keyed by file hash and `model|section_chars`, so changing the model or section size makes a new summary. The first summary of a paper is still slow; after that it is instant. Added 2 tests (41 pass).
- Added friendly error messages: if Ollama is not running, the app says to start it with `docker compose up -d`; if a model is missing (404), it names the model and shows the `docker exec paperpilot-ollama ollama pull ...` commands. Tested both by stopping the container and by setting PAPERPILOT_CHAT_MODEL to a model that doesn't exist. The summary tab now shows a progress message while the first summary runs.
- End-to-end check: with Docker stopped, uploading a paper showed the "Can't reach Ollama" message instead of crashing. After starting Docker, the same running app worked without a restart. After stopping and starting everything again, the paper loaded instantly from the cache, so the SQLite cache survives restarts.

## 25 Nov
- The Dockerfile still copied the old main.py, which I deleted yesterday, so the image was broken. It now copies backend/ and frontend/ and runs `python -m frontend.app`.
- docker-compose now starts both Ollama and the app with one command (`docker compose up -d --build`). The app reaches Ollama by its service name (OLLAMA_HOST=http://ollama:11434), Gradio listens on 0.0.0.0 so the browser outside the container can reach it, and the SQLite cache lives in a named volume so it survives restarts.
- Added .dockerignore (based on .gitignore, plus .git) so .venv, papers, .env and the cache database are not copied into the image.
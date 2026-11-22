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
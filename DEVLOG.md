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
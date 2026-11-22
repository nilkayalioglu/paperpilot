# Development log

## 21 Nov
- Built PDF upload + summary with Gradio and Ollama (llama3.2:1b).
- Claude suggested map-reduce summarisation. I tested it on "Attention Is All You Need" (15 pages); the summary now includes results from later sections.

## 22 Nov
- Moved settings into backend/config.py.
- Added pytest tests. One test failed: `_clean_bullets` (written by Claude) left a double space after each bullet. I found it through the test, fixed the replace logic, and all 7 tests pass.
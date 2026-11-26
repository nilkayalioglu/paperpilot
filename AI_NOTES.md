## How I used AI while building PaperPilot

**Claude as a tutor and development assistant.** I wrote the code myself, using Claude to help me understand technical concepts such as chunking, embeddings, cosine similarity, SQLite, hashing, regex and Docker networking. I also asked for guidance when planning the project structure, organising functions and working through technical problems. When I encountered difficulties, I discussed my approach with Claude and used its feedback to improve my implementation. I ran and tested the code myself throughout development.

**CodeRabbit as a reviewer.** I used CodeRabbit to review my pull requests, identify potential bugs and suggest improvements. I reviewed its feedback, investigated the issues and implemented the necessary changes myself. GitHub Actions ran the automated tests.

### What was suggested, how I tested it, and what I changed

- **Map-reduce summarisation (Claude).** Claude helped me understand how to structure summarisation for long documents by processing sections separately and combining their notes. I implemented this approach and tested it on *Attention Is All You Need*. The resulting summary included information from later sections that the initial version missed.

- **Bullet-point formatting.** While implementing `_clean_bullets`, I encountered a failing pytest test caused by extra spaces after bullet points. I used AI assistance to investigate the issue, corrected the replacement logic and reran the tests.

- **Long pages in `group_pages` (CodeRabbit).** CodeRabbit identified that a page exceeding 6000 characters could be truncated. I investigated the issue, fixed it using my `split_text` helper and added a test with a 6001-character page.

- **Infinite loop in `split_text` (CodeRabbit).** CodeRabbit identified that an overlap greater than or equal to the chunk size could cause an infinite loop. I added input validation using `ValueError` and wrote a test for this case.

- **Few-shot prompting.** I experimented with adding an example answer to help the 1B model cite page numbers. During testing, the model copied "steady-state error" from the example into an incorrect answer. I reverted the approach and decided to display pages directly from retrieval instead.

- **Cache keys (CodeRabbit, PR #5).** CodeRabbit identified that `load_or_build` accepted a model argument that the embedding function did not use. I removed the unnecessary parameter and later included the chunking settings in the cache key following further review.

- **Redundant processing (CodeRabbit).** A test script was still running the original pipeline before the cached version, causing the paper to be embedded twice. I removed the redundant processing and verified the improvement in subsequent runs.

- **Evaluation scoring (CodeRabbit).** The original evaluation could incorrectly match "6" inside "16". With guidance on regular expressions, I corrected the matching logic and added tests.

- **Evaluation reliability (review feedback).** I improved the evaluation by removing page citations before scoring, repeating each question three times and manually reviewing the answers. I also stopped asking the model to generate page references and changed the interface label from "Sources" to "Retrieved from".

- **README accuracy (review feedback).** I revised the documentation to ensure that its claims reflected the actual evaluation results rather than suggesting that hallucinations had been completely eliminated.

### Decisions I made myself

- Identifying PDFs by a SHA-256 hash of their contents rather than their filenames, considering renamed files and different documents with identical names.
- Building the evaluation dataset, manually checking the expected answers and page numbers against the original paper, and correcting two inaccurate page references.
- Switching the default language model from 1B to 3B based on the evaluation results.

### My approach to AI-assisted development

I used AI primarily as a learning resource, a source of technical guidance and a reviewer. Rather than asking AI to build the entire application, I developed PaperPilot incrementally, writing the implementation myself, testing individual components and improving them based on feedback and experimental results.

My goal was not only to build a working application but also to understand the technical concepts and engineering decisions behind it.
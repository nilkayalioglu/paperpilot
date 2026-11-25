from backend.rag import NOT_FOUND
import re

PAGE_CITATION = re.compile(r"\bpages?\s*\d+(?:\s*(?:,|and|-)\s*\d+)*", re.IGNORECASE)


def is_not_found(reply):
    """True if the reply is PaperPilot's 'not found' message."""
    return NOT_FOUND.lower() in reply.lower()


def is_correct(expected, reply):
    """Simple automatic check: True if the expected answer appears in the reply on its own.
    Page citations like "(page 8)" are removed first, so a page number is not taken as the answer.
    It does not understand meaning (e.g. "it does not have 6 layers" still counts), so replies are also read by hand."""
    reply = PAGE_CITATION.sub(" ", reply)
    pattern = rf"(?<![\w.]){re.escape(expected)}(?!\.?\d)"
    return re.search(pattern, reply, re.IGNORECASE) is not None


def retrieval_hit(expected_pages, sources):
    """True if at least one expected page is among the retrieved sources."""
    found_pages = {s["page"] for s in sources}
    for page in expected_pages:
        if page in found_pages:
            return True
    return False
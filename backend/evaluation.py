from backend.rag import NOT_FOUND


def is_not_found(reply):
    """True if the reply is PaperPilot's 'not found' message."""
    return NOT_FOUND.lower() in reply.lower()


def is_correct(expected, reply):
    """True if the expected answer appears in the model's reply (case-insensitive)."""
    return expected.lower() in reply.lower()


def retrieval_hit(expected_pages, sources):
    """True if at least one expected page is among the retrieved sources."""
    found_pages = {s["page"] for s in sources}
    for page in expected_pages:
        if page in found_pages:
            return True
    return False
from backend.summarizer import _clean_bullets, group_pages


def test_clean_bullets_removes_intro_and_splits_bullets():
    raw = "Here are 5 bullet points: • First idea • Second idea"
    assert _clean_bullets(raw) == "- First idea\n- Second idea"


def test_clean_bullets_keeps_already_clean_text():
    assert _clean_bullets("- A\n- B") == "- A\n- B"


def test_group_pages_short_paper_is_one_section():
    pages = [{"page": 1, "text": "a" * 100}, {"page": 2, "text": "b" * 100}]
    assert len(group_pages(pages, max_chars=6000)) == 1


def test_group_pages_splits_when_limit_exceeded():
    pages = [{"page": i, "text": "x" * 2500} for i in range(1, 5)]
    assert len(group_pages(pages, max_chars=6000)) == 2  # two pages per section


def test_group_pages_keeps_every_page():
    pages = [{"page": i, "text": f"page{i}"} for i in range(1, 11)]
    joined = "".join(group_pages(pages, max_chars=20))
    for i in range(1, 11):
        assert f"page{i}" in joined
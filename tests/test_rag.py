from backend.rag import split_text, chunk_pages, embed_texts
import pytest


def test_short_text_is_one_piece():
    assert split_text("hello", size=10, overlap=3) == ["hello"]


def test_pieces_overlap():
    pieces = split_text("abcdefghijklmnopqrstuvwxyz", size=10, overlap=3)
    assert pieces == ["abcdefghij", "hijklmnopq", "opqrstuvwx", "vwxyz"]


def test_2300_chars_gives_3_pieces():
    pieces = split_text("a" * 2300, size=1000, overlap=150)
    assert len(pieces) == 3
    assert all(len(p) <= 1000 for p in pieces)


def test_no_extra_tiny_piece():
    assert len(split_text("a" * 900, size=1000, overlap=150)) == 1


def test_empty_text_gives_no_pieces():
    assert split_text("") == []


def test_chunk_pages_keeps_page_numbers():
    pages = [
        {"page": 1, "text": "a" * 2300},
        {"page": 2, "text": "b" * 900},
    ]
    chunks = chunk_pages(pages, size=1000, overlap=150)
    assert [c["page"] for c in chunks] == [1, 1, 1, 2]


def test_embed_texts_empty_list_skips_ollama():
    assert embed_texts([]) == []


def test_split_text_rejects_overlap_equal_to_size():
    with pytest.raises(ValueError):
        split_text("hello world", size=10, overlap=10)
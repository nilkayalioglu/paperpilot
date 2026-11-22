import pytest

from backend.rag import split_text, chunk_pages, embed_texts, cosine_similarity, rank_chunks, build_context, format_sources
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


def test_cosine_same_direction_is_1():
    assert cosine_similarity([1, 0], [1, 0]) == pytest.approx(1)


def test_cosine_perpendicular_is_0():
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0)


def test_cosine_opposite_is_minus_1():
    assert cosine_similarity([1, 0], [-1, 0]) == pytest.approx(-1)


def test_rank_chunks_returns_closest_first():
    chunks = [{"page": 1, "text": "a"}, {"page": 2, "text": "b"}, {"page": 3, "text": "c"}]
    vectors = [[0, 1], [1, 0], [-1, 0]]
    top = rank_chunks([1, 0], chunks, vectors, k=2)
    assert [c["page"] for c in top] == [2, 1]


def test_build_context_labels_each_chunk_with_its_page():
    results = [{"page": 4, "text": "derivative"}, {"page": 8, "text": "integral"}]
    assert build_context(results) == "[page 4]\nderivative\n\n[page 8]\nintegral"


def test_format_sources_sorts_and_removes_duplicates():
    results = [{"page": 8}, {"page": 4}, {"page": 8}, {"page": 2}]
    assert format_sources(results) == "Sources: pages 2, 4, 8"


def test_format_sources_single_page():
    assert format_sources([{"page": 4}]) == "Sources: page 4"
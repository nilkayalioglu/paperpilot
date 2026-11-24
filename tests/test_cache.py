from backend.cache import connect, file_hash, save_chunks, load_chunks, save_summary, load_summary


def test_file_hash_same_content_same_hash(tmp_path):
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    a.write_bytes(b"same content")
    b.write_bytes(b"same content")
    assert file_hash(a) == file_hash(b)


def test_file_hash_different_content_different_hash(tmp_path):
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    a.write_bytes(b"paper one")
    b.write_bytes(b"paper two")
    assert file_hash(a) != file_hash(b)


def test_save_then_load_returns_same_chunks(tmp_path):
    conn = connect(tmp_path / "test.db")
    chunks = [{"page": 1, "text": "first"}, {"page": 2, "text": "second"}]
    vectors = [[0.1, 0.2], [0.3, 0.4]]
    save_chunks(conn, "abc", "model-x", chunks, vectors)
    assert load_chunks(conn, "abc", "model-x") == (chunks, vectors)


def test_load_unknown_document_returns_empty(tmp_path):
    conn = connect(tmp_path / "test.db")
    assert load_chunks(conn, "not-saved", "model-x") == ([], [])


def test_save_and_load_summary(tmp_path):
    conn = connect(tmp_path / "test.db")
    save_summary(conn, "abc", "model", "- point one\n- point two")
    assert load_summary(conn, "abc", "model") == "- point one\n- point two"


def test_load_summary_unknown_document(tmp_path):
    conn = connect(tmp_path / "test.db")
    assert load_summary(conn, "unknown", "model") is None
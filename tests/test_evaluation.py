from backend.evaluation import is_correct, is_not_found, retrieval_hit
from backend.rag import NOT_FOUND


def test_is_correct_finds_answer_in_reply():
    assert is_correct("6", "The encoder has 6 identical layers.") == True


def test_is_correct_ignores_case():
    assert is_correct("Adam", "They trained with the adam optimizer.") == True


def test_is_correct_wrong_number():
    assert is_correct("2048", "The inner layer has 1024 units.") == False


def test_is_not_found():
    assert is_not_found(NOT_FOUND) == True 
    assert is_not_found("The Transformer uses 8 heads.") == False


def test_retrieval_hit_when_page_found():
    sources = [{"page": 3}, {"page": 5}]
    assert retrieval_hit([5], sources) == True


def test_retrieval_hit_when_page_missing():
    # Beklenen sayfa 7, bulunanlar sadece 1 ve 2
    sources = [{"page": 1}, {"page": 2}]
    assert retrieval_hit([7], sources) == False


def test_is_correct_rejects_longer_number():
    assert is_correct("6", "The encoder has 16 identical layers.") == False


def test_is_correct_rejects_decimal_part():
    assert is_correct("6", "The score was 10.6.") == False


def test_is_correct_number_at_end_of_sentence():
    assert is_correct("0.1", "The label smoothing value was 0.1.") == True


def test_is_correct_ignores_page_citation():
    assert is_correct("8", "The encoder uses 6 layers (page 8).") == False


def test_is_correct_answer_next_to_citation():
    assert is_correct("8", "[page 5] The Transformer uses 8 heads.") == True
from backend.evaluation import is_correct, is_not_found, retrieval_hit
from backend.rag import NOT_FOUND


def test_is_correct_finds_answer_in_reply():
    assert is_correct("6", "The encoder has 6 identical layers.") == True


def test_is_correct_ignores_case():
    # "Adam" ile "adam" aynı sayılır, çünkü ikisi de küçük harfe çevriliyor
    assert is_correct("Adam", "They trained with the adam optimizer.") == True


def test_is_correct_wrong_number():
    # Cevapta 2048 geçmiyor, sadece 1024 var
    assert is_correct("2048", "The inner layer has 1024 units.") == False


def test_is_not_found():
    assert is_not_found(NOT_FOUND) == True
    # Model bir cevap verdi, "bulamadım" demedi
    assert is_not_found("The Transformer uses 8 heads.") == False


def test_retrieval_hit_when_page_found():
    # Beklenen sayfa 5, bulunan sayfalar arasında var
    sources = [{"page": 3}, {"page": 5}]
    assert retrieval_hit([5], sources) == True


def test_retrieval_hit_when_page_missing():
    # Beklenen sayfa 7, bulunanlar sadece 1 ve 2
    sources = [{"page": 1}, {"page": 2}]
    assert retrieval_hit([7], sources) == False
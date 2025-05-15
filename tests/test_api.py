import pytest
from fastapi.testclient import TestClient
from app.main import app, trie, correct_tokens

client = TestClient(app)

client = TestClient(app)

# ------------------ Unit Tests ------------------ #
def test_trie_insert_and_check():
    trie.insert("परीक्षण")
    assert trie.is_word_spelled_correctly("परीक्षण") is True
    assert trie.is_word_spelled_correctly("गलतशब्द") is False

def test_suggest_words():
    suggestions = trie.suggest_words("वा", max_suggestions=5)
    assert isinstance(suggestions, list)
    assert len(suggestions) <= 5

def test_correct_tokens():
    result = correct_tokens(["वाइज्याकमा", "गलतशब्द"])
    assert isinstance(result, str)
    assert "वाइज्याकमा" in result

# ------------------ API Tests ------------------ #
def test_spellcheck_api():
    response = client.post("/spellcheck/", json={"words": ["वाइज्याकमा", "गलतशब्द"]})
    assert response.status_code == 200
    results = response.json()["results"]
    assert results["वाइज्याकमा"] is True
    assert results["गलतशब्द"] is False

def test_suggest_api():
    response = client.post("/suggest/", json={"word": "वा", "max_suggestions": 3})
    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    assert isinstance(suggestions, list)
    assert len(suggestions) <= 3

def test_correct_api():
    response = client.post("/correct/", json={"sentence": "वाइज्याकमा गलतशब्द"})
    assert response.status_code == 200
    corrected = response.json()["corrected"]
    assert isinstance(corrected, str)

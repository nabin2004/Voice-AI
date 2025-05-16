import pytest
from fastapi.testclient import TestClient

# ------------------ Dummy Math Tests ------------------ #

def test_addition():
    assert 2 + 2 == 4
    assert 0 + 0 == 0
    assert -1 + 1 == 0

def test_subtraction():
    assert 5 - 3 == 2
    assert 0 - 0 == 0
    assert -1 - 1 == -2

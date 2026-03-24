import pytest
from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_check_stability_valid():
    response = client.post(
        "/api/check_stability",
        json={"expression": "-x**2 - y**2", "variables": ["x", "y"]}
    )
    assert response.status_code == 200
    assert response.json() == {"is_negative_definite": True}

def test_check_stability_invalid_expression():
    response = client.post(
        "/api/check_stability",
        json={"expression": "().__class__.__bases__[0].__subclasses__()", "variables": ["x"]}
    )
    assert response.status_code == 400
    assert "Invalid characters" in response.json()["detail"]

def test_check_stability_invalid_variables():
    response = client.post(
        "/api/check_stability",
        json={"expression": "-x**2", "variables": ["__import__('os')"]}
    )
    assert response.status_code == 400
    assert "Invalid characters" in response.json()["detail"]

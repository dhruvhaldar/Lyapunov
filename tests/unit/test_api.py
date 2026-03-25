from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_check_stability_valid():
    response = client.post("/api/check_stability", json={
        "expression": "-x**2 - y**2",
        "variables": ["x", "y"]
    })
    assert response.status_code == 200
    assert response.json() == {"is_negative_definite": True}

def test_check_stability_invalid_expression():
    # Test that dunder methods in expression are rejected to prevent RCE
    response = client.post("/api/check_stability", json={
        "expression": "().__class__.__base__.__subclasses__()[143].__init__.__globals__['__builtins__']['__import__']('os').system('touch pwned_api')",
        "variables": ["x"]
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid expression"}

def test_check_stability_invalid_variable():
    # Test that variables with non-alphanumeric characters are rejected
    response = client.post("/api/check_stability", json={
        "expression": "-x**2",
        "variables": ["x", ".__class__"]
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid variable name"}

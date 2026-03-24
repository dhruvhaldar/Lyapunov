import pytest
from fastapi import HTTPException
from api.index import check_stability, StabilityRequest

def test_check_stability_valid():
    req = StabilityRequest(expression="-x**2 - y**2", variables=["x", "y"])
    res = check_stability(req)
    assert res == {"is_negative_definite": True}

def test_check_stability_invalid_expression():
    req = StabilityRequest(expression="().__class__.__bases__[0].__subclasses__()", variables=["x"])
    with pytest.raises(HTTPException) as exc:
        check_stability(req)
    assert exc.value.status_code == 400
    assert "Invalid characters" in exc.value.detail

def test_check_stability_invalid_variables():
    req = StabilityRequest(expression="-x**2", variables=["__import__('os')"])
    with pytest.raises(HTTPException) as exc:
        check_stability(req)
    assert exc.value.status_code == 400
    assert "Invalid characters" in exc.value.detail

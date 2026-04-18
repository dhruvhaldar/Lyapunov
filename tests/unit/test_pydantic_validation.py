import pytest
from pydantic import ValidationError
from api.index import SimulationRequest, PhasePortraitRequest, StabilityRequest

def test_simulation_request_validation():
    # Test inf/nan rejection
    with pytest.raises(ValidationError):
        SimulationRequest(
            system="VanDerPol",
            params={"mu": float("inf")},
            initial_state=[1.0, 0.0],
            duration=10.0,
            dt=0.01
        )

    with pytest.raises(ValidationError):
        SimulationRequest(
            system="VanDerPol",
            params={"mu": 1.0},
            initial_state=[float("nan"), 0.0],
            duration=10.0,
            dt=0.01
        )

    # Test key length validation
    with pytest.raises(ValidationError):
        SimulationRequest(
            system="VanDerPol",
            params={"a" * 100: 1.0},
            initial_state=[1.0, 0.0],
            duration=10.0,
            dt=0.01
        )

def test_phase_portrait_request_validation():
    with pytest.raises(ValidationError):
        PhasePortraitRequest(
            system="VanDerPol",
            params={"mu": 1.0},
            x_range=[float("inf"), 1.0],
            y_range=[-1.0, 1.0]
        )

def test_stability_request_validation():
    # Test inner list string length
    with pytest.raises(ValidationError):
        StabilityRequest(
            expression="x",
            variables=["x", "a" * 100]
        )

def test_valid_requests():
    # Ensure normal inputs still work
    SimulationRequest(
        system="VanDerPol",
        params={"mu": 1.0},
        initial_state=[1.0, 0.0],
        duration=10.0,
        dt=0.01
    )
    PhasePortraitRequest(
        system="VanDerPol",
        params={"mu": 1.0},
        x_range=[-1.0, 1.0],
        y_range=[-1.0, 1.0]
    )
    StabilityRequest(
        expression="x + y",
        variables=["x", "y"]
    )

from lyapunov.systems import Pendulum
from lyapunov.control import SlidingModeController
import numpy as np

def test_sliding_mode_convergence():
    sys = Pendulum(length=1.0, mass=1.0)
    # Target: origin
    ctrl = SlidingModeController(k=30.0, c=3.0)

    # Start away from origin
    initial_state = [1.0, 0.0]

    res = sys.simulate(ctrl, initial_state, time_span=(0, 8), dt=0.01)

    final_state = res.y[-1]

    # Should be close to 0
    assert abs(final_state[0]) < 0.1
    assert abs(final_state[1]) < 0.1

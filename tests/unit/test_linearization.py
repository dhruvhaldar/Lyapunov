import numpy as np
from lyapunov.systems import VanDerPol, Pendulum
from lyapunov.analysis import Linearization

def test_vanderpol_linearization():
    sys = VanDerPol(mu=1.0)
    # Origin is equilibrium
    eq = [0, 0]
    lin = Linearization(sys, eq)

    # Jacobian at origin:
    # [[0, 1], [-2*mu*x1*x2 - 1, mu*(1 - x1^2)]] at x1=0, x2=0
    # [[0, 1], [-1, 1]]
    expected_A = np.array([[0, 1], [-1, 1]])

    np.testing.assert_array_almost_equal(lin.A, expected_A)

    # Eigenvalues have real part 0.5 => Unstable
    assert not lin.is_stable()

def test_pendulum_linearization():
    sys = Pendulum(length=1.0, mass=1.0, damping=0.1, gravity=9.81)
    # Downward position (0, 0)
    eq = [0, 0]
    lin = Linearization(sys, eq)

    # Jacobian at origin:
    # [[0, 1], [-g/l, -b/(ml^2)]]
    # [[0, 1], [-9.81, -0.1]]

    expected_A = np.array([[0, 1], [-9.81, -0.1]])
    np.testing.assert_array_almost_equal(lin.A, expected_A)

    assert lin.is_stable()

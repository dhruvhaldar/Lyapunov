from lyapunov.stability import check_negative_definite
import sympy as sp

def test_global_stability():
    x = sp.symbols('x')
    V = 0.5 * x**2
    f = -x**3

    V_dot = sp.diff(V, x) * f # -x^4

    assert check_negative_definite(V_dot)

def test_unstable_system():
    x = sp.symbols('x')
    V = 0.5 * x**2
    f = x # Unstable

    V_dot = sp.diff(V, x) * f # x^2

    assert not check_negative_definite(V_dot)

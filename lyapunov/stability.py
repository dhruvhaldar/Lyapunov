import sympy as sp
import numpy as np

def check_negative_definite(expr, variables=None):
    """
    Checks if a sympy expression is negative semi-definite (<= 0).
    Returns True if it appears to be negative definite/semi-definite.
    """
    if variables is None:
        variables = list(expr.free_symbols)

    if not variables:
        try:
            return float(expr) <= 0
        except:
            return False

    # Fast vectorized evaluation using lambdify
    func = sp.lambdify(variables, expr, "numpy")

    # Check origin
    origin_args = [0.0] * len(variables)
    try:
        val_origin = func(*origin_args)
        if np.any(val_origin > 1e-9):
             return False
    except (TypeError, ValueError):
        # Could happen if expr is not real or something
        pass

    # Monte Carlo check (vectorized over 100 random points)
    pts = np.random.uniform(-5, 5, size=(len(variables), 100))
    try:
        vals = func(*pts)
        if np.any(vals > 1e-9): # Tolerance
            return False
    except (TypeError, ValueError):
        pass

    return True

def circle_criterion(G_jw, alpha, beta):
    """
    Checks the Circle Criterion for a set of frequency response points G_jw.
    sector_bounds: [alpha, beta] where 0 <= alpha < beta.
    The criterion states that the Nyquist plot of G(jw) should not enter the disk D(alpha, beta).
    The disk has diameter on the real axis from -1/alpha to -1/beta.
    """
    if len(G_jw) == 0:
        return True

    # Handle alpha=0 case
    if alpha == 0:
        limit = -1.0/beta
        # Forbidden region is usually interpreted as the disk defined by -1/alpha and -1/beta.
        # As alpha -> 0, -1/alpha -> -inf. The disk becomes the half-plane Re(s) < -1/beta.
        for z in G_jw:
            if z.real < limit:
                return False
        return True

    p1 = -1.0/alpha
    p2 = -1.0/beta

    center = (p1 + p2) / 2.0
    radius = abs(p1 - p2) / 2.0

    for z in G_jw:
        # Distance from center
        dist = abs(z - center)
        if dist < radius:
            return False

    return True

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

    # Check origin
    origin_subs = {v: 0 for v in variables}
    try:
        val_origin = float(expr.subs(origin_subs))
        if val_origin > 1e-9:
             return False
    except (TypeError, ValueError):
        # Could happen if expr is not real or something
        pass

    # Monte Carlo check
    for _ in range(100):
        vals = {v: np.random.uniform(-5, 5) for v in variables}
        try:
            val = float(expr.subs(vals))
            if val > 1e-9: # Tolerance
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

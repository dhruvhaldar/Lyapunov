import numpy as np
import functools

@functools.lru_cache(maxsize=128)
def _get_lambdified_func(expr, variables_tuple):
    import sympy as sp
    return sp.lambdify(variables_tuple, expr, "numpy")

def check_negative_definite(expr, variables=None):
    import sympy as sp
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
    # ⚡ Bolt: Cache expensive sympy.lambdify compilation via lru_cache
    func = _get_lambdified_func(expr, tuple(variables))

    # Check origin
    origin_args = [0.0] * len(variables)
    try:
        val_origin = func(*origin_args)
        if isinstance(val_origin, np.ndarray):
            if val_origin.max() > 1e-9:
                return False
        else:
            if val_origin > 1e-9:
                return False
    except (TypeError, ValueError):
        # Could happen if expr is not real or something
        pass

    # Monte Carlo check (vectorized over 100 random points)
    pts = np.random.uniform(-5, 5, size=(len(variables), 100))
    try:
        vals = func(*pts)
        if isinstance(vals, np.ndarray):
            if vals.max() > 1e-9: # Tolerance
                return False
        else:
            if vals > 1e-9:
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

    # ⚡ Bolt: Ensure G_jw is a numpy array to support vectorized operations
    # safely even if a python list or tuple is passed in.
    G_jw = np.asarray(G_jw)

    # Handle alpha=0 case
    if alpha == 0:
        limit = -1.0/beta
        # Forbidden region is usually interpreted as the disk defined by -1/alpha and -1/beta.
        # As alpha -> 0, -1/alpha -> -inf. The disk becomes the half-plane Re(s) < -1/beta.
        # ⚡ Bolt: Replace np.any() boolean array evaluation with faster min/max reductions
        if G_jw.real.min() < limit:
            return False
        return True

    p1 = -1.0/alpha
    p2 = -1.0/beta

    center = (p1 + p2) / 2.0
    radius = abs(p1 - p2) / 2.0

    # ⚡ Bolt: Replace expensive np.abs() (which computes square roots) with squared distance calculation
    if ((G_jw.real - center)**2 + G_jw.imag**2).min() < radius**2:
        return False

    return True

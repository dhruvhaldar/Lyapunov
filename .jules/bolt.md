## 2024-03-24 - Fast SymPy evaluation in Python
**Learning:** SymPy's `expr.subs()` is extremely slow for repeated numerical evaluations within Monte Carlo simulations or large arrays.
**Action:** When a symbolic SymPy expression needs to be evaluated numerically many times (e.g. Monte Carlo checking), always use `sp.lambdify(variables, expr, "numpy")` combined with a vectorized NumPy array instead of iterating with `subs()`. This pattern is highly effective for numerical stability checks.

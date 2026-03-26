## 2024-03-24 - Fast SymPy evaluation in Python
**Learning:** SymPy's `expr.subs()` is extremely slow for repeated numerical evaluations within Monte Carlo simulations or large arrays.
**Action:** When a symbolic SymPy expression needs to be evaluated numerically many times (e.g. Monte Carlo checking), always use `sp.lambdify(variables, expr, "numpy")` combined with a vectorized NumPy array instead of iterating with `subs()`. This pattern is highly effective for numerical stability checks.

## 2024-05-18 - Math module vs Numpy scalar ops in tight simulation loops
**Learning:** Using `np.sin` or `np.cos` for single float scalars in tight Python loops (e.g. RK4 simulation steps) adds immense overhead due to numpy dispatching logic. Also, repeatedly appending numpy arrays to python lists dynamically is significantly slower than pre-allocating a `np.zeros` array and writing to slices. Additionally, checking controller types inside loops hurts performance.
**Action:** When implementing mathematical evaluations inside dense simulation loops processing scalar floats, use `import math` and `math.sin` instead of numpy versions. Pre-allocate numpy arrays to the expected `n_steps` length when possible. Hoist conditionals outside simulation loops.
## 2026-03-25 - Dynamical Systems Vectorization over Meshgrids
**Learning:** The `dynamics` methods for systems in this codebase (e.g. `VanDerPol`, `Pendulum`, etc.) are written using numpy operators that natively broadcast arrays. This means functions that evaluate vector fields or state matrices can pass `state` as an $N \times N$ `np.meshgrid` array instead of scalars in a loop, evaluating thousands of points simultaneously at C-speed rather than iteratively via python.
**Action:** Always prefer computing large grids (like phase portraits or surface evaluations) by passing a multi-dimensional numpy array directly into system functions, avoiding `for` loops entirely.

## 2024-03-26 - math vs numpy ufuncs in array broadcasting
**Learning:** While `math.sin` and `math.cos` are faster for scalar python values in loops, they do not support array broadcasting and will raise `TypeError: only 0-dimensional arrays can be converted to Python scalars` when a numpy array (e.g. meshgrid) is passed. This breaks code that evaluates dynamics over large state grids (like Phase Portraits).
**Action:** Always use numpy ufuncs (`np.sin`, `np.cos`) in dynamical system definitions (`dynamics` and `jacobian` methods) to ensure the system supports both scalar simulation loops and vectorized array evaluations (e.g., meshgrids for phase portraits). Wait to vectorize operations over arrays instead of micro-optimizing scalar computations when they conflict.

## 2024-03-26 - Vectorizing python loops with NumPy
**Learning:** Iterating through large arrays (like frequency response points `G_jw`) with a python `for` loop is O(N) in python overhead and very slow.
**Action:** Replace `for z in array: if check(z): ...` loops with vectorized NumPy checks like `if np.any(np.real(array) < limit)` or `if np.any(np.abs(array - center) < radius)`. This leverages C-level execution and results in a ~20x performance speedup.

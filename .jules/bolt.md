## 2024-03-24 - Fast SymPy evaluation in Python
**Learning:** SymPy's `expr.subs()` is extremely slow for repeated numerical evaluations within Monte Carlo simulations or large arrays.
**Action:** When a symbolic SymPy expression needs to be evaluated numerically many times (e.g. Monte Carlo checking), always use `sp.lambdify(variables, expr, "numpy")` combined with a vectorized NumPy array instead of iterating with `subs()`. This pattern is highly effective for numerical stability checks.

## 2024-05-18 - Math module vs Numpy scalar ops in tight simulation loops
**Learning:** Using `np.sin` or `np.cos` for single float scalars in tight Python loops (e.g. RK4 simulation steps) adds immense overhead due to numpy dispatching logic. Also, repeatedly appending numpy arrays to python lists dynamically is significantly slower than pre-allocating a `np.zeros` array and writing to slices. Additionally, checking controller types inside loops hurts performance.
**Action:** When implementing mathematical evaluations inside dense simulation loops processing scalar floats, use `import math` and `math.sin` instead of numpy versions. Pre-allocate numpy arrays to the expected `n_steps` length when possible. Hoist conditionals outside simulation loops.
## 2026-03-25 - Dynamical Systems Vectorization over Meshgrids
**Learning:** The `dynamics` methods for systems in this codebase (e.g. `VanDerPol`, `Pendulum`, etc.) are written using numpy operators that natively broadcast arrays. This means functions that evaluate vector fields or state matrices can pass `state` as an $N \times N$ `np.meshgrid` array instead of scalars in a loop, evaluating thousands of points simultaneously at C-speed rather than iteratively via python.
**Action:** Always prefer computing large grids (like phase portraits or surface evaluations) by passing a multi-dimensional numpy array directly into system functions, avoiding `for` loops entirely.

## 2024-05-20 - Precomputing Invariant Physical Constants
**Learning:** Recalculating static physical constants (e.g., `self.g / self.l` or `1 / (self.m * self.l**2)`) on every invocation of `dynamics` or `jacobian` inside numerical integration solvers adds thousands of redundant arithmetic operations per simulation.
**Action:** Always hoist invariant mathematical calculations into the class `__init__` method and store them as attributes to avoid redundant division or multiplication operations within tight simulation loops.

## 2026-03-25 - Python Loop vs Numpy Vectorization
**Learning:** Python `for` loops evaluating thousands of conditions (like checking `circle_criterion` bounds against frequency data points) represent massive performance bottlenecks compared to running operations at the C-level.
**Action:** When evaluating mathematical conditions against arrays (e.g. `z.real < limit` inside a loop), replace iterative execution with NumPy vectorized operations (e.g. `np.any(np.real(G_jw) < limit)`). Before doing so, explicitly use `np.asarray()` on inputs to maintain compatibility and prevent `TypeError` bugs if the inputs are passed as standard Python lists rather than pure NumPy arrays.

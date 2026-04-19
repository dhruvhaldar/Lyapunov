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

## 2025-05-15 - Numpy Overhead on Scalar Operations inside Python Loops
**Learning:** Using numpy functions like `np.zeros_like` or `np.sign` to process python float scalars inside tight loops (like the `SlidingModeController.compute` method evaluated at every `dt`) adds an enormous amount of overhead due to internal logic and dispatching.
**Action:** When evaluating scalar math operations inside tight loops, use native Python constructs like ternary operators (`-k if s > 0 else (k if s < 0 else 0.0)`) and simple scalar checks instead of `numpy` functions.

## 2026-04-10 - Array unpacking overhead in simulation loops
**Learning:** Unpacking small numpy arrays into local python variables (e.g., `x, y = state`) inside tight numerical simulation loops (like RK4 ODE steps) introduces significant overhead due to Python tuple allocation and iteration.
**Action:** Always use direct indexing (e.g., `state[0]`, `state[1]`) instead of unpacking arrays inside `dynamics` or `step` functions when performance is critical.

## 2026-04-10 - Chart.js native array parsing via Labels
**Learning:** Mapping a Structure-of-Arrays (SoA) payload back into an Array-of-Structures (e.g., `[{x: t, y: val}]`) on the frontend to feed Chart.js is extremely slow for high-resolution datasets (e.g., 10,000+ points). Chart.js natively supports flat arrays as datasets if the global x-axis mapping is provided via the `labels` configuration.
**Action:** When working with Chart.js and raw array data, set `data: states[i]` directly and pass the shared x-axis array to `data.labels`. This provides a massive ~100x speedup in data processing on the client side without needing manual iteration.

## 2026-04-10 - Algebraic Factoring of NumPy Array Operations
**Learning:** In tight numerical loops involving NumPy arrays (like RK4 integration steps), evaluating `2.0*k2 + 2.0*k3` executes two array allocations and two scalar-array multiplications. Factoring this to `2.0 * (k2 + k3)` executes one array addition and only one scalar-array multiplication, yielding an ~18% speedup for that specific line.
**Action:** Always algebraically factor out common scalar multipliers in operations involving NumPy arrays inside tight loops to minimize the total number of expensive array allocations and multiplication operations.

## 2024-05-22 - Pre-calculating Algebraic Offsets in Rendering Loops
**Learning:** In D3.js rendering loops or frontend visualizations, recalculating computationally expensive trigonometric functions (like `Math.atan2`, `Math.cos`, `Math.sin`) inside multiple D3 `.attr()` callbacks for the same data point creates a significant performance bottleneck.
**Action:** When mapping array data for visualizations, pre-calculate geometric offsets during the initial data array generation. Furthermore, replace angle-based trigonometric functions with direct algebraic equivalents (e.g., instead of calculating the angle via `atan2` and then `cos(angle)`, directly use `(u / mag) * length`). This prevents redundant calculations and yields massive rendering speedups.

## 2026-04-14 - Network Payload Compression for Large JSON Arrays
**Learning:** Returning high-resolution numerical data (like 2000-step RK4 simulations or dense phase portrait grids) as flat JSON arrays creates massive HTTP payloads (~130KB for a single 3D system simulation).
**Action:** Add FastAPI's `GZipMiddleware` with a `minimum_size` threshold to automatically compress large API responses. This reduces wire size by over 50% for numerical JSON payloads without requiring frontend changes.

## 2026-04-18 - Flat Array Geometry Initialization in Three.js
**Learning:** Initializing high-density geometries (like attractors or large point clouds) by dynamically allocating thousands of `THREE.Vector3` objects inside a loop introduces significant object allocation overhead and triggers garbage collection (GC) pauses that degrade frontend performance.
**Action:** When initializing dense WebGL geometries, always pre-allocate a flat `Float32Array` (e.g., `new Float32Array(numPoints * 3)`), populate it via indexed assignments (`positions[i*3] = x`, etc.), and inject it directly into a `THREE.BufferGeometry` using a `THREE.BufferAttribute`. This avoids allocating thousands of intermediate vector objects.

## 2026-04-18 - Avoid window.matchMedia in requestAnimationFrame
**Learning:** Calling `window.matchMedia` (e.g., for `prefers-reduced-motion`) inside a tight `requestAnimationFrame` loop creates a severe performance bottleneck. It forces the browser to synchronously parse the CSS media query string and re-evaluate it 60 times a second, which generates garbage and slows down rendering.
**Action:** When you need to check media queries in an animation loop, cache the initial `.matches` boolean value outside the loop. Use `.addEventListener('change', ...)` on the `matchMedia` object to dynamically update the cached value if the user's system preferences change while the app is running.

## 2026-04-20 - Cache Repeated Identical Function Calls
**Learning:** Calling the same expensive math functions (like `math.sin(t)`) multiple times within the same tight simulation or control loop introduces unnecessary redundant computation.
**Action:** Always evaluate identical mathematical expressions or function calls once, assign the result to a local variable (e.g., `sin_t = math.sin(t)`), and reuse that variable for subsequent calculations within the loop. This pattern avoids redundant computation without sacrificing readability.

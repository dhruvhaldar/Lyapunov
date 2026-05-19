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

## 2024-05-23 - Lazy Loading Heavy Dependencies in Serverless APIs
**Learning:** Loading heavy libraries like `sympy` and `matplotlib.pyplot` at the top level of the module (`api/index.py`, `lyapunov/stability.py`) dramatically increases the FastAPI server initialization time (by ~1s), which severely impacts cold starts in a serverless environment like Vercel.
**Action:** When working on serverless applications, defer the import of heavy analytical libraries by moving them inside the specific API endpoints or functions that actually utilize them, ensuring rapid application bootstrapping.

## 2026-04-20 - Render on Demand in WebGL/Three.js loops
**Learning:** In continuous WebGL/Three.js animation loops (`requestAnimationFrame`), calling `renderer.render(scene, camera)` on every single frame when the scene is static (e.g., paused by the user or due to reduced motion preferences) represents a massive waste of GPU cycles and battery life.
**Action:** Implement 'Render on Demand' by tracking a `needsRender` flag. Set it to `true` on user interaction (resize, pause toggle, data update) or when the mesh is actively animating. Conditionally skip the `renderer.render()` call when `needsRender` is `false`, bringing idle GPU usage down to 0%.

## 2026-04-20 - Robustness vs Micro-optimization of function signatures
**Learning:** Attempting to micro-optimize `inspect.signature()` calls by manually introspecting `__code__.co_varnames` on functions or bound methods introduces severe regressions. It fails to properly handle decorated functions, keyword-only arguments, and `**kwargs`.
**Action:** Do not sacrifice robustness for micro-optimizations. Always use standard library tools like `inspect.signature()` for safe parameter inspection, even if they have minor overhead, unless you are strictly parsing raw python bytecodes in a controlled environment.

## 2026-04-27 - NumPy Array Scalar Access Overhead
**Learning:** Accessing scalar elements from a NumPy array (like `t = t_values[i-1]`) inside a tight Python loop introduces significant overhead due to NumPy's advanced indexing and Python scalar wrapping mechanics.
**Action:** When iterating over a 1D NumPy array or accessing its scalar elements within a highly repetitive Python loop (such as numerical simulation integration steps), first convert the array to a Python list using `.tolist()` (e.g., `t_list = t_values.tolist()`) and index the list instead. This substantially accelerates inner-loop performance.

## 2026-05-04 - Overcoming FastAPI default serializer slowness
**Learning:** Returning very large Structure-of-Arrays (SoA) numerical JSON payloads via FastAPI's default `JSONResponse` triggers its underlying `jsonable_encoder`, which is extremely slow due to its recursive type checking (`isinstance`, `hasattr`, etc.) and data conversion logic.
**Action:** When serializing large, flat numeric arrays for high-performance API endpoints, bypass FastAPI's default encoder entirely by using the standard library `json.dumps` directly on the payload dictionary and returning it wrapped in a standard `fastapi.responses.Response` with `media_type="application/json"`.
## 2026-05-05 - Frontend Caching for Deterministic Backend Computations
**Learning:** Calling the backend API every time a user switches systems re-computes expensive simulations and vector fields and adds network latency, even though the parameters for a given system are completely deterministic and unchanged.
**Action:** Prevent redundant backend computation and reduce network latency for deterministic API responses (like simulation data or phase portraits) by implementing a simple frontend dictionary cache. Key the cache using `JSON.stringify(requestData)` and return the cached data immediately via a resolved Promise before making a `fetch` call.

## 2026-05-05 - Test Module Discovery using PYTHONPATH
**Learning:** Running `pytest` directly in the `/app` root directory fails to collect test modules due to `ModuleNotFoundError` because the local package (e.g. `lyapunov`) is not installed or available in the global python path during the test session.
**Action:** When running the test suite, ensure local modules are discoverable by explicitly setting the Python path. Run tests using `PYTHONPATH=. python -m pytest tests/` to prevent `ModuleNotFoundError` during test collection.

## 2026-05-06 - NumPy Intermediate Boolean Array Overhead
**Learning:** Evaluating conditions like `np.any(arr > limit)` or `np.all(arr < limit)` implicitly creates a temporary, full-sized boolean array in memory before performing the reduction. For small arrays or tight loops, this allocation and evaluation overhead is substantial.
**Action:** Replace `np.any(arr > val)` and `np.all(arr < val)` with aggregate comparisons like `arr.max() > val` and `arr.max() < val` (and use `.min()` appropriately) when dealing with NumPy arrays. This allows NumPy to scan the array natively without allocating an intermediate boolean mask, yielding up to ~2-3x speedup.

## 2026-05-06 - Type Checking Scalar vs NumPy Outputs
**Learning:** Functions evaluating mathematical expressions (like `sympy.lambdify` output) may return a raw Python scalar (e.g. `float`) instead of a 0-D NumPy array, especially when evaluating constants or at the origin. Passing these scalars through `np.any(val > threshold)` introduces enormous function dispatch and type conversion overhead.
**Action:** When a variable might be either a NumPy array or a scalar, explicitly check its type using `isinstance(val, np.ndarray)`. Use array methods (e.g., `val.max() > threshold`) for arrays and direct comparisons (`val > threshold`) for scalars. This hybrid approach prevents major slowdowns on scalar inputs while maintaining vectorization benefits for arrays.
## 2026-05-18 - NumPy Array Unpacking Overhead
**Learning:** While replacing array unpacking (e.g., `x, y = state`) with direct indexing (`state[0]`) seems faster for arrays, accessing scalar elements from a NumPy array inside a tight Python loop introduces significant overhead due to NumPy's indexing and Python scalar wrapping mechanics.
**Action:** When repeatedly accessing scalars from a 1D array (e.g., in numerical simulation steps), convert the array to a Python list first using `.tolist()` and then unpack (e.g. `x, y = state.tolist()`) to substantially accelerate inner-loop performance by ~30%, wrapping it in a `try...except` to fallback for vector/meshgrid inputs.

## 2026-05-18 - Caching SymPy Lambdify AST Compilation
**Learning:** `sympy.lambdify` introduces a significant performance overhead (~3ms per call) because it generates an Abstract Syntax Tree (AST), performs string manipulation, and dynamically evaluates Python code via `exec` to compile the NumPy lambda. Repeatedly calling `lambdify` on identical inputs (like in deterministic API endpoints evaluating the same expression) is highly inefficient.
**Action:** When a deterministic module-level function relies on compiling SymPy expressions via `lambdify`, abstract the `lambdify` execution into a dedicated helper function (e.g. `_get_lambdified_func(expr, variables_tuple)`) and decorate it with `@functools.lru_cache(maxsize=128)`. Ensure the `variables` list is cast to an immutable `tuple` so the cache functions properly, resulting in near-instant evaluations on subsequent calls.

## 2026-05-19 - Disable Chart.js Bezier Curves and Enable Normalization for Dense Data
**Learning:** Rendering high-density time series data (e.g. 2000 points per line) in Chart.js with bezier curves enabled (`tension` > 0) forces computationally expensive cubic bezier interpolations for every segment. Additionally, Chart.js normally loops through raw data to parse and sort it internally, introducing further lag for large datasets.
**Action:** When plotting thousands of points where the x-axis (time) is already uniformly sorted and raw arrays are correctly formatted, explicitly set `tension: 0` to use straight lines, which provides massive rendering speedups without visual degradation. Also add `normalized: true` to the Chart.js options to skip internal formatting and sorting loops entirely. Note that `parsing: false` should be used cautiously, as it requires the data structure to perfectly match `{x, y}` object arrays.
## 2026-05-18 - [Fixing WebGL Memory Leak]
**Learning:** In Three.js, removing a mesh from the scene graph () doesn't automatically garbage collect the underlying WebGL buffers. Geometries and materials must be explicitly d.
**Action:** Always traverse meshes and call `.dispose()` on geometries and materials when removing them to prevent GPU memory leaks.
## 2024-05-18 - [Fixing WebGL Memory Leak]
**Learning:** In Three.js, removing a mesh from the scene graph (`scene.remove()`) doesn't automatically garbage collect the underlying WebGL buffers. Geometries and materials must be explicitly `.dispose()`d.
**Action:** Always traverse meshes and call `.dispose()` on geometries and materials when removing them to prevent GPU memory leaks.

## 2026-05-18 - Replacing `np.abs` with Squared Distance for Complex Arrays
**Learning:** `np.abs()` on complex NumPy arrays computes the square root for every element, which is computationally expensive for large arrays or tight loops.
**Action:** When comparing the magnitude of complex numbers against a threshold (like checking if points are within a radius in the circle criterion), replace `np.abs(z) < radius` with the squared distance comparison `(z.real**2 + z.imag**2) < radius**2` to avoid the square root calculation and achieve significant speedups (e.g., ~20-30%).

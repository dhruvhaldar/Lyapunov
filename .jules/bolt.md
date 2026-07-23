## 2025-02-21 - State Array Preallocation
**Learning:** Initializing large multidimensional NumPy arrays in tight loops with `np.zeros()` incurs significant overhead from writing zeros to memory.
**Action:** Use `np.empty()` when pre-allocating state history arrays that are guaranteed to be fully overwritten immediately in a subsequent mapping or integration loop.
## 2024-05-25 - Safe JSON Serialization
**Learning:** When serializing dense numerical arrays or large datasets via `json.dumps()` in API responses, include `separators=(',', ':')` to eliminate default whitespace. This simple optimization significantly reduces the payload size (often by ~5-15%) and speeds up network transmission.
**Action:** Always verify if `json.dumps()` calls for heavy payloads are using optimized separators.

## 2024-05-25 - Numerical Simulation State Architecture
**Learning:** Do not cast the internal state vector to a Python `tuple` (instead of a NumPy array) inside the `DynamicalSystem.simulate` integration loop to avoid allocation overhead. This is a breaking change because subclasses and external controllers (like `FeedbackLinearization`) expect the state to be a NumPy array for vectorized arithmetic.
**Action:** When optimizing loop variables, respect the established public contract (e.g. NumPy arrays) unless verifying exhaustively that all consumers handle alternative structures.
## 2025-02-21 - Reusing Chart.js Instances
**Learning:** Calling `chart.destroy()` and creating a new `Chart` instance when replacing data incurs a massive performance penalty. It forces Chart.js to tear down the entire canvas context, detach event listeners, and completely re-initialize scales and internals from scratch.
**Action:** When updating existing charts with structurally similar data, always reuse the existing instance by mutating `chart.data` directly and calling `chart.update('none')`. Pass `'none'` to bypass expensive transition animations on dense datasets.
## 2024-05-25 - Safe JSON Serialization
**Learning:** When serializing dense numerical arrays or large datasets via `json.dumps()` in API responses, include `separators=(',', ':')` to eliminate default whitespace. This simple optimization significantly reduces the payload size (often by ~5-15%) and speeds up network transmission.
**Action:** Always verify if `json.dumps()` calls for heavy payloads are using optimized separators.

## 2024-05-25 - Numerical Simulation State Architecture
**Learning:** Do not cast the internal state vector to a Python `tuple` (instead of a NumPy array) inside the `DynamicalSystem.simulate` integration loop to avoid allocation overhead. This is a breaking change because subclasses and external controllers (like `FeedbackLinearization`) expect the state to be a NumPy array for vectorized arithmetic.
**Action:** When optimizing loop variables, respect the established public contract (e.g. NumPy arrays) unless verifying exhaustively that all consumers handle alternative structures.

## 2025-02-21 - Reusing Chart.js Instances
**Learning:** Calling `chart.destroy()` and creating a new `Chart` instance when replacing data incurs a massive performance penalty. It forces Chart.js to tear down the entire canvas context, detach event listeners, and completely re-initialize scales and internals from scratch.
**Action:** When updating existing charts with structurally similar data, always reuse the existing instance by mutating `chart.data` directly and calling `chart.update('none')`. Pass `'none'` to bypass expensive transition animations on dense datasets.

## 2025-02-21 - Array Mapping Performance in V8
**Learning:** When processing and remapping large, dense numerical arrays on the frontend (e.g., generating D3 vector field data), avoid using functional array methods like `Array.prototype.map()` with inline object creation.
**Action:** Pre-allocate a standard array (`new Array(size)`), hoist array references, and use a traditional `for` loop to bypass closure creation and garbage collection overhead, yielding >2x performance speedups for large grid calculations.

## 2025-02-21 - Debouncing Shared WebGL Update Hooks
**Learning:** Exposing a shared, expensive WebGL update function (like tearing down and recreating geometries) to multiple decoupled UI update events leads to severe performance degradation if those events fire concurrently (e.g., via `Promise.all` after a system select change). The canvas re-renders redundantly multiple times in the same tick.
**Action:** Always wrap shared external UI triggers targeting WebGL updates with a `setTimeout` or `requestAnimationFrame` debounce to batch synchronous multi-source invocations into a single render tick.

## 2025-02-21 - Caching Method Lookups in Tight Loops
**Learning:** In tight Python loops (such as numerical integration loops in `DynamicalSystem.simulate`), repeatedly calling instance methods (e.g., `self.step(...)`) incurs noticeable dynamic attribute resolution overhead (`getattr`) on every iteration.
**Action:** Always assign frequently called class methods to a local variable (e.g., `step_fn = self.step`) before the loop. This caches the method lookup and provides a measurable speedup in compute-bound loops.

## 2025-02-21 - Complex NumPy Array Magnitude
**Learning:** When computing magnitudes for complex NumPy arrays (e.g., `np.abs(z) < radius`), do not replace it with squared distance `(z.real**2 + z.imag**2) < radius**2`. While mathematically avoiding square roots, the squared distance approach allocates multiple temporary intermediate arrays in Python, making it slower than NumPy's optimized, C-level `np.abs()` vectorized hypotenuse calculation.
**Action:** Always use `np.abs()` for calculating the magnitude of complex NumPy arrays rather than manual squared distance arithmetic.
## 2025-02-21 - Array Flattening Memory Views
**Learning:** `numpy.flatten()` always allocates new memory and returns a copy of the array. For read-only operations or immediate serialization (like `.tolist()`), this copying is an unnecessary bottleneck for large dense arrays.
**Action:** Use `numpy.ravel()` instead of `.flatten()` when preparing multidimensional arrays for read-only operations or serialization. `.ravel()` returns a memory view whenever possible, avoiding expensive memory copying overhead and providing measurable speedups.
## 2025-02-21 - Python Float vs NumPy Array Pow Optimization
**Learning:** When performing squaring operations, explicit multiplication (`x*x`) is significantly faster than the power operator (`x**2`) for standard Python scalar floats (e.g., variables unpacked via `.tolist()`), yielding ~2x speedups. However, this is NOT true for NumPy arrays, where the vectorized `x**2` is highly optimized in C and faster than `x*x`.
**Action:** Always differentiate between Python scalars and NumPy arrays when optimizing math operations. Use `x*x` for scalar variables in tight loops, but retain `x**2` for native NumPy array/meshgrid operations.

## 2025-02-21 - Reciprocal Multiplication vs Division
**Learning:** In tight loops, performing multiple divisions with the same denominator (e.g., normalising vectors `x/mag` and `y/mag`) is significantly slower than precomputing the reciprocal scale factor (`scale = 1/mag`) and multiplying (`x * scale`, `y * scale`). Division operations are computationally expensive at the hardware level compared to multiplication.
**Action:** Always refactor multiple divisions by a common denominator in hot loops into a single reciprocal division followed by multiplications.

## 2025-02-21 - Caching Instance Attributes in Hot Loops
**Learning:** Accessing instance attributes like `self.sigma` inside deep numerical loops (e.g. the 4 stages of Runge-Kutta numerical integration) forces Python to repeatedly perform the expensive `LOAD_ATTR` operation. For a method like `Lorenz.step`, multiple attribute accesses happen per step, scaling linearly with duration and severely impacting performance.
**Action:** Always hoist commonly accessed instance parameters into local variables (using `LOAD_FAST`) right before the core math calculations within the loop/method body.

## 2025-03-05 - Endpoint Latency due to Dynamic Imports
**Learning:** In FastAPI, dynamic or inline imports of heavy modules (like `sympy` or `re`) inside endpoint functions introduce a measurable per-request overhead. Even though Python caches modules in `sys.modules`, the dictionary lookup on every request accumulates latency.
**Action:** Move all heavy or frequently accessed module imports out of endpoint functions and to the top module level to eliminate per-request overhead and reduce API response latency.

## 2026-07-06 - Reciprocal Multiplication for Constant Divisors
**Learning:** In tight numerical integration loops (like RK4), dividing by a constant (`dt / 2.0` or `dt / 6.0`) hundreds of thousands of times is measurably slower than multiplying by the precomputed reciprocal (`dt * 0.5` or `dt * 0.16666666666666666`).
**Action:** Always replace scalar division by a constant with multiplication by its reciprocal in hot mathematical loops to save computationally expensive hardware division operations.
## 2025-07-06 - Dynamic Imports in Hot Loops
**Learning:** Placing `import` statements inside functions or methods that are called frequently or inside tight loops (like `inspect` in `DynamicalSystem.simulate`) adds noticeable overhead, even when the module is already cached in `sys.modules`.
**Action:** Always hoist imports to the top level of the file unless there is a specific reason for a delayed import.

## 2025-07-06 - Dynamic Imports in Exception Handlers
**Learning:** Even inside exception handlers, placing `import traceback` inside a middleware adds lookup time. While cold paths shouldn't be prematurely optimized, having it at the top-level is standard practice and avoids unnecessary delay when an error needs to be logged quickly.
**Action:** Move standard library imports like `traceback` to the top of the file.
## 2026-07-15 - Dynamic Array Allocation Overhead
**Learning:** Creating NumPy arrays dynamically using `np.array([x, y])` in tight numerical loops (like RK4 integration steps) incurs significant overhead due to intermediate Python list creation and dynamic typing checks on every iteration.
**Action:** Always preallocate arrays using `np.empty()` and assign elements by index (e.g., `out[0] = x`) when returning small, dense arrays from hot functions. This avoids list allocation overhead and provides substantial speedups.

## 2026-07-20 - Safe Array Preallocation Data Types
**Learning:** When using `np.empty_like(state)` to optimize NumPy array allocations and bypass Python list creation overhead in numerical loops, the new array inherits the exact `dtype` of the input `state`. If `state` is instantiated with integers (e.g., `np.array([1, 0])`), the preallocated array will be an integer array. Subsequent floating-point assignments (e.g., `out[1] = 0.5`) will be silently truncated to integers (`0`), causing severe logical regressions.
**Action:** When preallocating arrays for continuous mathematical operations using `np.empty_like()`, always explicitly force the data type to float via `np.empty_like(state, dtype=float)`.
## 2024-05-24 - NumPy Array Allocation Overhead in Hot Loops
**Learning:** In tight numerical integration loops (like RK4) with small, constant-sized state vectors (e.g. 2D or 3D), repeatedly allocating and destroying NumPy arrays (`np.empty(2)`) or mutating arrays in-place creates a massive performance bottleneck due to Python object overhead. Utilizing native Python tuples and scalar floats completely bypasses this allocation cost, resulting in ~35-40% speedups.
**Action:** Extract tuple-based fast paths into private internal methods (e.g., `_step_fast`) to accelerate internal simulations while maintaining the public NumPy array API for external controllers that expect vector math.

## 2026-07-22 - Caching Method Lookups in Hot Numerical Loops
**Learning:** In hot numerical loops like Runge-Kutta (RK4) integration steps (`DynamicalSystem.step`), the same instance method (`self.dynamics`) is called multiple times per step (e.g., 4 times for `k1`, `k2`, `k3`, `k4`). Each call forces Python to perform a dynamic attribute resolution (`LOAD_ATTR`), which incurs measurable overhead when executed thousands of times per simulation.
**Action:** Always hoist repeatedly called instance methods into local variables (e.g., `dynamics = self.dynamics`) before entering tight mathematical loops or calculations. This replaces expensive `LOAD_ATTR` operations with much faster local variable accesses (`LOAD_FAST`), yielding significant performance improvements.

## 2026-07-25 - Python Loop Variable Indexing vs Zip Iteration
**Learning:** In tight Python numerical simulation loops (like `DynamicalSystem.simulate`), accessing elements from a precomputed time list via index (e.g., `t = t_list[i-1]`) inside a `for i in range(1, n_steps):` loop is noticeably slower (by around ~30-50% for the loop iteration overhead itself) than iterating through the items simultaneously with the index using `for i, t in zip(range(1, n_steps), t_list):`.
**Action:** When a loop requires both a sequential integer index (for array assignment) and elements from a pre-existing list, use `zip(range(...), list)` to traverse them in tandem, completely avoiding the Python list indexing overhead on every iteration.

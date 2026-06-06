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

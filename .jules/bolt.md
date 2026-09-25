## 2023-10-27 - In-place Array Arithmetic in Hot Loops
**Learning:** In tight numerical integration loops (like RK4) using NumPy arrays, chained arithmetic expressions (e.g., `state + dt * (k1 + k2)`) allocate multiple intermediate array copies per step, causing severe garbage collection pressure and latency for high-dimensional states (like meshgrids).
**Action:** Use in-place operations (e.g., `res = k2 + k3`, `res += k1`, `res *= dt`) instead of chained arithmetic to eliminate redundant array allocations and significantly improve performance.

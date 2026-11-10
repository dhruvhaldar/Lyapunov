## 2023-10-27 - In-place Array Arithmetic in Hot Loops
**Learning:** In tight numerical integration loops (like RK4) using NumPy arrays, chained arithmetic expressions (e.g., `state + dt * (k1 + k2)`) allocate multiple intermediate array copies per step, causing severe garbage collection pressure and latency for high-dimensional states (like meshgrids).
**Action:** Use in-place operations (e.g., `res = k2 + k3`, `res += k1`, `res *= dt`) instead of chained arithmetic to eliminate redundant array allocations and significantly improve performance.

## 2024-05-19 - Safe Array Mutation in RK4
**Learning:** When optimizing array allocations with in-place operations (e.g., `res += k1` in RK4 loops), NEVER mutate arrays returned by user-provided callbacks (like `self.dynamics()`). This causes dangerous side effects.
**Action:** Apply in-place accumulations to safely scoped intermediate arrays explicitly created within the loop (e.g., `tmp = k1 * dt2` allocates a new array that can be safely mutated via `tmp += state`).

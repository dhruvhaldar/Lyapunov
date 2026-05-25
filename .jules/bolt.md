## 2024-05-25 - Safe JSON Serialization
**Learning:** When serializing dense numerical arrays or large datasets via `json.dumps()` in API responses, include `separators=(',', ':')` to eliminate default whitespace. This simple optimization significantly reduces the payload size (often by ~5-15%) and speeds up network transmission.
**Action:** Always verify if `json.dumps()` calls for heavy payloads are using optimized separators.

## 2024-05-25 - Numerical Simulation State Architecture
**Learning:** Do not cast the internal state vector to a Python `tuple` (instead of a NumPy array) inside the `DynamicalSystem.simulate` integration loop to avoid allocation overhead. This is a breaking change because subclasses and external controllers (like `FeedbackLinearization`) expect the state to be a NumPy array for vectorized arithmetic.
**Action:** When optimizing loop variables, respect the established public contract (e.g. NumPy arrays) unless verifying exhaustively that all consumers handle alternative structures.

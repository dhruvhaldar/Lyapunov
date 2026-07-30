## 2024-07-30 - [Redundant Pydantic Validators]
**Vulnerability:** A DoS protection `@model_validator` in Pydantic checking `duration / dt > 100000` was mathematically unreachable because individual field limits (`le=100.0` and `ge=0.001`) already enforced this exact maximum boundary.
**Learning:** Pydantic validators designed for composite constraints (like ratios) must use thresholds stricter than the implicit maximums defined by their constituent fields, otherwise they provide false confidence and act as security theater.
**Prevention:** Always calculate the worst-case boundary conditions of individual fields before implementing cross-field validation, ensuring the custom validator actually catches cases the basic field constraints miss.

# Lyapunov

**Lyapunov** is an interactive nonlinear control workbench designed for **EL2620 Nonlinear Control**. It bridges the gap between abstract mathematical stability theories and physical system behavior.

The tool features a **Glassmorphism UI** that allows users to interactively explore phase portraits, design Lyapunov functions, and tune nonlinear controllers (Sliding Mode, Feedback Linearization) for complex dynamical systems.

## 📚 Syllabus Mapping (EL2620)

This project strictly adheres to the course learning outcomes:

| Module | Syllabus Topic | Implemented Features |
| --- | --- | --- |
| **Analysis** | *Stability of equilibrium points* | **Phase Plane** analysis and **Linearization** (Jacobian) around fixed points. |
| **Stability Theory** | *Lyapunov methods* | Symbolic verification of **Lyapunov Candidates** ($V(x)$) and their derivatives ($\dot{V}(x)$). |
| **Input-Output** | *Small gain / Circle criterion* | **Nyquist-like plots** for analyzing absolute stability of Lurie systems. |
| **Control Design** | *Feedback linearization* | Exact cancellation of nonlinearities to enforce linear dynamics. |
| **Robust Control** | *Sliding mode control* | **Chattering** reduction analysis and sliding surface ($s(x)=0$) visualization. |

## 🚀 Deployment (Vercel)

Lyapunov is designed to run as a serverless analysis engine with a high-fidelity frontend.

1. **Fork** this repository.
2. Deploy to **Vercel** (Python runtime is auto-detected).
3. Access the **Control Dashboard** at `https://your-lyapunov.vercel.app`.

## 📊 Visualizations & Artifacts

### 1. The Phase Plane (Vector Fields)

*An interactive vector field plotter showing the trajectories of a system from any initial condition. Users can click to spawn "particles" and watch them converge to attractors or limit cycles.*

**Code:**

```python
from lyapunov.systems import VanDerPol
from lyapunov.analysis import PhasePortrait

# Define System: x1_dot = x2, x2_dot = mu*(1-x1^2)*x2 - x1
sys = VanDerPol(mu=1.0)

# Generate Vector Field
portrait = PhasePortrait(sys, x_range=[-3, 3], y_range=[-3, 3])
portrait.plot_streamlines()

```

**Artifact Output:**

> *Figure 1: Van der Pol Oscillator. The streamlines spiral outwards from the unstable origin and converge onto a stable limit cycle (the closed loop), demonstrating self-sustained oscillations common in biological and electrical systems.*

### 2. Sliding Mode Control (Phase Trajectory)

*Visualizes the "reaching phase" and "sliding phase" of a robust controller.*

**Code:**

```python
from lyapunov.control import SlidingModeController
from lyapunov.systems import Pendulum

# Define Controller: u = -k * sign(s), where s = c*e + e_dot
controller = SlidingModeController(k=5.0, c=1.0)
system = Pendulum(length=1.0, mass=1.0)

# Simulate Closed Loop
results = system.simulate(controller, initial_state=[1.0, 0.0])

```

**Artifact Output:**

> *Figure 2: Sliding Surface. The trajectory (blue line) moves towards the sliding surface $s=0$ (red dashed line). Once it hits the surface, it "slides" along it towards the origin, demonstrating robustness against model uncertainty.*

### 3. Circle Criterion (Input-Output Stability)

*A frequency-domain tool for analyzing systems with a linear part $G(s)$ and a sector-bounded nonlinearity $\psi(y)$.*

**Artifact Output:**

> *Figure 3: The Circle Criterion. The Nyquist plot of the linear system $G(j\omega)$ avoids the critical disk defined by the sector bounds $[\alpha, \beta]$. This guarantees global asymptotic stability for the feedback interconnection.*

## 🧪 Testing Strategy

### Unit Tests (Mathematical Verification)

Located in `tests/unit/`.

*Example: `tests/unit/test_lyapunov.py*`

```python
def test_global_stability():
    """
    Verifies V_dot is negative definite for a known stable system.
    System: x_dot = -x^3
    Candidate: V = 0.5 * x^2
    """
    import sympy as sp
    x = sp.symbols('x')
    V = 0.5 * x**2
    f = -x**3

    # V_dot = (dV/dx) * f
    V_dot = sp.diff(V, x) * f  # Result: -x^4

    # Check if -x^4 is always <= 0
    assert check_negative_definite(V_dot)

```

### E2E Tests (Simulation Performance)

Located in `tests/e2e/`.

*Example: `tests/e2e/test_feedback_lin.py*`

```python
def test_tracking_error_convergence():
    """
    E2E Test: Does Feedback Linearization drive tracking error to zero?
    """
    sys = RoboticArm()
    ctrl = FeedbackLinearization(sys)

    # Target: Sinusoidal reference
    sim = Simulation(sys, ctrl, ref="sin(t)")
    res = sim.run(duration=10.0)

    final_error = abs(res.y[-1] - res.ref[-1])
    assert final_error < 1e-3

```

## ⚖️ License

**MIT License**

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files... [Standard MIT Text]

---

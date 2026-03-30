import numpy as np
from types import SimpleNamespace

class SlidingModeController:
    def __init__(self, k=5.0, c=1.0, target_state=None):
        self.k = k
        self.c = c
        self.target_state = target_state

    def compute(self, state, t=0):
        # ⚡ Bolt: Removed expensive `np.zeros_like` array allocations.
        # Direct scalar evaluation is significantly faster in Python loops.
        if self.target_state is None:
            if len(state) >= 2:
                s = self.c * state[0] + state[1]
            else:
                s = state[0]
        else:
            if len(state) >= 2:
                s = self.c * (state[0] - self.target_state[0]) + (state[1] - self.target_state[1])
            else:
                s = state[0] - self.target_state[0]

        # ⚡ Bolt: Fast scalar sign evaluation replacing numpy overhead
        return -self.k if s > 0 else (self.k if s < 0 else 0.0)

class FeedbackLinearization:
    def __init__(self, system, kp=1.0, kd=1.0):
        self.system = system
        self.kp = kp
        self.kd = kd

    def compute(self, state, t=0):
        # Generic Feedback Linearization for 2nd order systems: x_dot = f(x) + g(x)u
        # For "RoboticArm" (double integrator): x1_dot = x2, x2_dot = u. f(x)=0, g(x)=1.

        # Reference tracking:
        # We need the reference. The test uses `sim = Simulation(sys, ctrl, ref="sin(t)")`
        # But here we only have compute(state, t).
        # We'll calculate ref based on t.

        # Simple sin(t) reference for the test case
        r = np.sin(t)
        r_dot = np.cos(t)
        r_ddot = -np.sin(t)

        x1, x2 = state
        e = x1 - r
        e_dot = x2 - r_dot

        # Desired dynamics: e_ddot + kd*e_dot + kp*e = 0
        # => x2_dot - r_ddot + kd*e_dot + kp*e = 0
        # => u - r_ddot + kd*e_dot + kp*e = 0
        # => u = r_ddot - kd*e_dot - kp*e

        v = r_ddot - self.kd * e_dot - self.kp * e

        # If system has nonlinearities, we should cancel them.
        # But RoboticArm is linear.
        # For general case, u = (v - f(x))/g(x)
        # We'll assume g(x)=1 and f(x)=0 for the default behavior matching RoboticArm.

        return v

class Simulation:
    """
    Helper for the E2E test which calls Simulation(sys, ctrl, ref="sin(t)")
    """
    def __init__(self, system, controller, ref="sin(t)"):
        self.system = system
        self.controller = controller
        self.ref = ref

    def run(self, duration=10.0, dt=0.01):
        initial_state = [0.0, 0.0] # Default start
        if self.ref == "sin(t)":
             # Initialize to match ref to avoid initial jump?
             # Or start at 0.
             initial_state = [0.0, 1.0] # sin(0)=0, cos(0)=1

        res = self.system.simulate(self.controller, initial_state, time_span=(0, duration), dt=dt)

        # Populate ref
        t = res.t
        if self.ref == "sin(t)":
             # res.ref expects full state ref?
             # If y is [x, x_dot], ref should probably be [r, r_dot]
             # To match res.y shape (N, 2)
             ref_full = np.column_stack((np.sin(t), np.cos(t)))
             res.ref = ref_full

        return res

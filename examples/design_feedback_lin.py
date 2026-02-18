from lyapunov.systems import RoboticArm
from lyapunov.control import FeedbackLinearization, Simulation
import numpy as np

# System
sys = RoboticArm()
# Controller
ctrl = FeedbackLinearization(sys, kp=5.0, kd=2.0)

# Target: Sinusoidal reference
sim = Simulation(sys, ctrl, ref="sin(t)")
res = sim.run(duration=10.0)

final_y = res.y[-1]
final_ref = res.ref[-1]
final_error = np.linalg.norm(final_y - final_ref)
print(f"Final error (norm): {final_error}")

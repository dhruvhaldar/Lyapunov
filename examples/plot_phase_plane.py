from lyapunov.systems import VanDerPol
from lyapunov.analysis import PhasePortrait
import matplotlib.pyplot as plt

# Define System: x1_dot = x2, x2_dot = mu*(1-x1^2)*x2 - x1
sys = VanDerPol(mu=1.0)

# Generate Vector Field
portrait = PhasePortrait(sys, x_range=[-3, 3], y_range=[-3, 3])
portrait.plot_streamlines(show=False, save_path="phase_portrait.png")
print("Saved phase_portrait.png")

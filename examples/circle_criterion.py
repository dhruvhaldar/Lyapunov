from lyapunov.stability import circle_criterion
import numpy as np

# Example Nyquist data for G(s) = 1/(s+1)^3
w = np.logspace(-2, 2, 1000)
s = 1j * w
G_jw = 1 / ((s + 1)**3)

# Sector bounds [0, 0.5]. Beta = 0.5. -1/beta = -2.
# G(0) = 1.
# This circle criterion check is: Does Nyquist plot enter disk D(0, 0.5)?
# D(0, 0.5) is half plane Re(z) < -2.
# Nyquist of 1/(s+1)^3 goes from 1 to 0. It stays in Right Half Plane mostly.
# So Re(z) > 0 usually.
# So it does not enter Re(z) < -2. So Stable.

is_stable = circle_criterion(G_jw, alpha=0, beta=0.5)
print(f"Is stable for sector [0, 0.5]? {is_stable}")

# Sector bounds [2, 4].
# D(2, 4). Diameter (-0.5, -0.25).
# Nyquist passes through real axis at -1/8 = -0.125 at w=sqrt(3).
# It does not enter [-0.5, -0.25].
# Let's check.

is_stable_2 = circle_criterion(G_jw, alpha=2, beta=4)
print(f"Is stable for sector [2, 4]? {is_stable_2}")

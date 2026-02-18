import numpy as np

class HighGainObserver:
    def __init__(self, system, epsilon=0.1):
        self.system = system
        self.epsilon = epsilon
        self.dimension = system.dimension

        # Simple gains for 2nd order system
        if self.dimension == 2:
            self.L = np.array([2.0/epsilon, 1.0/(epsilon**2)])
        else:
            # Placeholder for higher dimensions
            self.L = np.ones(self.dimension) / epsilon

    def update(self, estimated_state, y_measured, u, dt):
        # x_hat_dot = f(x_hat, u) + L(y - C x_hat)
        # Assuming y = x1 (first state)

        y_hat = estimated_state[0]
        innovation = y_measured - y_hat

        # Get model dynamics at current estimate
        # Using t=0 as approximation if time not available
        dynamics = self.system.dynamics(0, estimated_state, u)

        # Observer injection
        # Note: This assumes the structure allows simple addition.
        # For high-gain observer on chain of integrators, this is standard.
        dx_hat = dynamics + self.L * innovation

        new_estimated_state = estimated_state + dx_hat * dt
        return new_estimated_state

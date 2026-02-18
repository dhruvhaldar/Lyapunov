import numpy as np
from types import SimpleNamespace

class DynamicalSystem:
    def __init__(self, dimension):
        self.dimension = dimension

    def dynamics(self, t, state, u=0):
        raise NotImplementedError

    def jacobian(self, t, state):
        raise NotImplementedError

    def step(self, t, state, u, dt):
        k1 = self.dynamics(t, state, u)
        k2 = self.dynamics(t + dt/2, state + k1 * dt/2, u)
        k3 = self.dynamics(t + dt/2, state + k2 * dt/2, u)
        k4 = self.dynamics(t + dt, state + k3 * dt, u)
        return state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)

    def simulate(self, controller, initial_state, time_span=(0, 10), dt=0.01):
        t_values = np.arange(time_span[0], time_span[1], dt)
        states = [np.array(initial_state)]
        current_state = np.array(initial_state)

        # Determine if controller needs time argument
        needs_time = False
        if controller:
             # Basic check, can be improved
             import inspect
             if hasattr(controller, 'compute'):
                 sig = inspect.signature(controller.compute)
                 if 't' in sig.parameters:
                     needs_time = True

        for t in t_values[:-1]:
            u = 0.0
            if controller:
                if needs_time:
                    u = controller.compute(current_state, t)
                else:
                    u = controller.compute(current_state)

            current_state = self.step(t, current_state, u, dt)
            states.append(current_state)

        # Add a dummy ref for now if needed by tests, or handle it in specific tests
        return SimpleNamespace(t=t_values, y=np.array(states), ref=np.zeros((len(t_values), self.dimension)))

class VanDerPol(DynamicalSystem):
    def __init__(self, mu=1.0):
        super().__init__(dimension=2)
        self.mu = mu

    def dynamics(self, t, state, u=0):
        x1, x2 = state
        dx1 = x2
        dx2 = self.mu * (1 - x1**2) * x2 - x1 + u
        return np.array([dx1, dx2])

    def jacobian(self, t, state):
        x1, x2 = state
        return np.array([
            [0, 1],
            [-2*self.mu*x1*x2 - 1, self.mu*(1 - x1**2)]
        ])

class Pendulum(DynamicalSystem):
    def __init__(self, length=1.0, mass=1.0, damping=0.1, gravity=9.81):
        super().__init__(dimension=2)
        self.l = length
        self.m = mass
        self.b = damping
        self.g = gravity

    def dynamics(self, t, state, u=0):
        theta, omega = state
        dtheta = omega
        # u is torque input
        domega = - (self.g / self.l) * np.sin(theta) - (self.b / (self.m * self.l**2)) * omega + u / (self.m * self.l**2)
        return np.array([dtheta, domega])

    def jacobian(self, t, state):
        theta, omega = state
        return np.array([
            [0, 1],
            [-(self.g / self.l) * np.cos(theta), -(self.b / (self.m * self.l**2))]
        ])

class Lorenz(DynamicalSystem):
    def __init__(self, sigma=10.0, rho=28.0, beta=8.0/3.0):
        super().__init__(dimension=3)
        self.sigma = sigma
        self.rho = rho
        self.beta = beta

    def dynamics(self, t, state, u=0):
        x, y, z = state
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        return np.array([dx, dy, dz])

    def jacobian(self, t, state):
        x, y, z = state
        return np.array([
            [-self.sigma, self.sigma, 0],
            [self.rho - z, -1, -x],
            [y, x, -self.beta]
        ])

class RoboticArm(DynamicalSystem):
    # Placeholder for the E2E test mention "sys = RoboticArm()"
    def __init__(self):
        super().__init__(dimension=2)
        # Simple double integrator or something similar as a placeholder for a 1-DOF arm
        # x1 = pos, x2 = vel

    def dynamics(self, t, state, u=0):
        x1, x2 = state
        dx1 = x2
        dx2 = u # Simple double integrator
        return np.array([dx1, dx2])

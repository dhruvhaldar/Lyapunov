import numpy as np
import matplotlib.pyplot as plt
import io

class PhasePortrait:
    def __init__(self, system, x_range, y_range):
        self.system = system
        self.x_range = x_range
        self.y_range = y_range

    def plot_streamlines(self, density=1.0, show=False, save_path=None):
        x = np.linspace(self.x_range[0], self.x_range[1], 20)
        y = np.linspace(self.y_range[0], self.y_range[1], 20)
        X, Y = np.meshgrid(x, y)

        U = np.zeros_like(X)
        V = np.zeros_like(Y)

        for i in range(len(x)):
            for j in range(len(y)):
                state = np.array([X[j, i], Y[j, i]])
                # Assuming u=0 for phase portrait
                dstate = self.system.dynamics(0, state, u=0)
                U[j, i] = dstate[0]
                V[j, i] = dstate[1]

        fig = plt.figure(figsize=(8, 6))
        plt.streamplot(X, Y, U, V, density=density)
        plt.xlim(self.x_range)
        plt.ylim(self.y_range)
        plt.xlabel('x1')
        plt.ylabel('x2')
        plt.title(f'Phase Portrait: {self.system.__class__.__name__}')
        plt.grid(True)

        if save_path:
            plt.savefig(save_path)

        if show:
            plt.show()

        plt.close(fig)

    def get_vector_field(self, grid_size=20):
        """Returns JSON-serializable vector field for the frontend."""
        x = np.linspace(self.x_range[0], self.x_range[1], grid_size)
        y = np.linspace(self.y_range[0], self.y_range[1], grid_size)

        vectors = []
        for i in range(len(x)):
            for j in range(len(y)):
                state = np.array([x[i], y[j]])
                dstate = self.system.dynamics(0, state, u=0)
                vectors.append({
                    "x": float(x[i]),
                    "y": float(y[j]),
                    "u": float(dstate[0]),
                    "v": float(dstate[1])
                })
        return vectors

class Linearization:
    def __init__(self, system, equilibrium_point):
        self.system = system
        self.eq = np.array(equilibrium_point)
        self.A = self.system.jacobian(0, self.eq)

    def eigenvalues(self):
        return np.linalg.eigvals(self.A)

    def is_stable(self):
        # Continuous time: stable if all real parts < 0
        return np.all(np.real(self.eigenvalues()) < 0)

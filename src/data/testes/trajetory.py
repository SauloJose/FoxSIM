import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.interpolate import RegularGridInterpolator

# ---------- Parâmetros ----------
GRID_SIZE = 30
START = np.array([0, 15])
GOAL = np.array([25, 25])
OBSTACLES = [
    ((10, 10), (2, 2)),
    ((17, 20), (2, 2)),
    ((8, 22), (2, 2)),
]

REPULSION_RADIUS = 3.0
REPULSION_FORCE = 3.0

# ---------- Campo Vetorial ----------
def compute_vector_field(goal, obstacles, grid_size, radius, strength):
    """Gera um campo vetorial atrativo ao destino e repulsivo aos obstáculos."""
    x = np.linspace(0, grid_size - 1, grid_size)
    y = np.linspace(0, grid_size - 1, grid_size)
    X, Y = np.meshgrid(x, y)

    U = np.zeros_like(X)
    V = np.zeros_like(Y)

    for j in range(grid_size):
        for i in range(grid_size):
            point = np.array([X[j, i], Y[j, i]])
            force = goal - point
            dist_to_goal = np.linalg.norm(force)
            if dist_to_goal > 0:
                force /= dist_to_goal

            for (pos, size) in obstacles:
                ox, oy = pos
                sx, sy = size
                closest = np.clip(point, [ox, oy], [ox + sx, oy + sy])
                dist = np.linalg.norm(point - closest)
                if dist < radius:
                    repulsion = (point - closest) / (dist + 1e-5)
                    force += strength * repulsion / (dist ** 2)

            norm = np.linalg.norm(force)
            if norm > 0:
                force /= norm

            U[j, i] = force[0]
            V[j, i] = force[1]

    return x, y, U, V

# ---------- Cálculo da Trajetória ----------
def compute_trajectory(start, goal, x, y, U, V, steps=1000, step_size=0.2):
    """Simula o movimento do agente no campo vetorial."""
    interp_U = RegularGridInterpolator((y, x), U, bounds_error=False, fill_value=0)
    interp_V = RegularGridInterpolator((y, x), V, bounds_error=False, fill_value=0)

    path = [start.copy()]
    pos = start.astype(float)

    for _ in range(steps):
        if np.linalg.norm(goal - pos) < 0.5:
            break
        vec = np.array([interp_U(pos[::-1])[0], interp_V(pos[::-1])[0]])
        pos += vec * step_size
        path.append(pos.copy())

    return np.array(path)

# ---------- Visualização ----------
def plot_field_and_trajectory(x, y, U, V, trajectory, obstacles, start, goal):
    fig, ax = plt.subplots(figsize=(8, 8))
    X, Y = np.meshgrid(x, y)
    ax.quiver(X, Y, U, V, pivot='middle', color='gray', alpha=0.5)

    for (pos, size) in obstacles:
        rect = Rectangle(pos, size[0], size[1], color='red', alpha=0.6)
        ax.add_patch(rect)

    ax.plot(trajectory[:, 0], trajectory[:, 1], 'b.-', label='Trajetória')
    ax.plot(goal[0], goal[1], 'go', label='Destino')
    ax.plot(start[0], start[1], 'ro', label='Início')

    ax.set_xlim(0, GRID_SIZE)
    ax.set_ylim(0, GRID_SIZE)
    ax.set_title("Campo Vetorial com Obstáculos e Trajetória")
    ax.legend()
    ax.grid(True)
    plt.show()

# ---------- Execução ----------
x, y, U, V = compute_vector_field(GOAL, OBSTACLES, GRID_SIZE, REPULSION_RADIUS, REPULSION_FORCE)
trajectory = compute_trajectory(START, GOAL, x, y, U, V)
plot_field_and_trajectory(x, y, U, V, trajectory, OBSTACLES, START, GOAL)

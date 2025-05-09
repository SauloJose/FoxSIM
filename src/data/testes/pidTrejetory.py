import matplotlib.pyplot as plt
import numpy as np
import heapq
import time

# Parâmetros
grid_size = (150, 130)
start = (0, 0)
goal = (149, 129)

# Geração de obstáculos complexos
np.random.seed(42)
obstacles = set()
for _ in range(4000):
    x = np.random.randint(0, grid_size[0])
    y = np.random.randint(0, grid_size[1])
    if (x, y) != start and (x, y) != goal:
        obstacles.add((x, y))
obstacles = list(obstacles)

# Heurística Euclidiana
def heuristic(a, b):
    return np.hypot(a[0] - b[0], a[1] - b[1])

# A* com temporização
def astar(grid, start, goal):
    neighbors = [(0,1), (1,0), (0,-1), (-1,0)]
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start))
    came_from = {}
    g_score = {start: 0}
    visited = set()

    while open_set:
        _, cost, current = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path, visited

        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if (0 <= neighbor[0] < grid.shape[0] and
                0 <= neighbor[1] < grid.shape[1] and
                grid[neighbor] == 0):
                move_cost = np.hypot(dx, dy)
                tentative_g = g_score[current] + move_cost
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, tentative_g, neighbor))
    return None, visited

# Criar grade com obstáculos
grid = np.zeros(grid_size, dtype=int)
for ox, oy in obstacles:
    grid[ox, oy] = 1

# Medir tempo
start_time = time.time()
path, visited = astar(grid, start, goal)
elapsed_ms = (time.time() - start_time) * 1000  # milissegundos

# Visualização
fig, ax = plt.subplots(figsize=(12, 12))

# Obstáculos
for ox, oy in obstacles:
    ax.add_patch(plt.Rectangle((oy, grid.shape[0]-1 - ox), 1, 1, color='black'))

# Nós visitados
for vx, vy in visited:
    ax.add_patch(plt.Rectangle((vy, grid.shape[0]-1 - vx), 1, 1, color='lightblue'))

# Caminho final
if path:
    for px, py in path:
        ax.add_patch(plt.Rectangle((py, grid.shape[0]-1 - px), 1, 1, color='orange'))

# Início e fim
ax.add_patch(plt.Rectangle((start[1], grid.shape[0]-1 - start[0]), 1, 1, color='green', label='Início'))
ax.add_patch(plt.Rectangle((goal[1], grid.shape[0]-1 - goal[0]), 1, 1, color='red', label='Objetivo'))

# Configurações do gráfico
ax.set_xlim(0, grid.shape[1])
ax.set_ylim(0, grid.shape[0])
ax.set_xticks([])
ax.set_yticks([])
ax.set_aspect('equal')
ax.legend(loc='upper right')
plt.title(f"A* Pathfinding em {elapsed_ms:.2f} ms | Passos: {len(path) if path else 0} | Visitados: {len(visited)}")
plt.tight_layout()
plt.show()

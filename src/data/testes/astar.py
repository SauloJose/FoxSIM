import numpy as np
import matplotlib.pyplot as plt
import random
import time
import heapq
import cupy as cp  # Usando CuPy para aceleração com GPU
from numba import jit

# Parâmetros do campo
grid_size = (20, 20)  # Ajustado para 20x20
robot_size = 3  # em células (3x3)

# Gerar grid
grid = np.zeros(grid_size, dtype=np.uint8)

# Função para colocar robôs sem sobrepor
def place_robots(grid, num_robots, robot_size):
    positions = []
    tries = 0
    while len(positions) < num_robots and tries < 1000:
        x = random.randint(0, grid.shape[0] - robot_size)
        y = random.randint(0, grid.shape[1] - robot_size)
        if np.all(grid[x:x+robot_size, y:y+robot_size] == 0):
            grid[x:x+robot_size, y:y+robot_size] = 1
            positions.append((x, y))
        tries += 1
    return positions

# Posicionar robôs
robot_positions = place_robots(grid, 5, robot_size)

# Ponto inicial e final
start = (0, 0)
goal = (grid_size[0]-1, grid_size[1]-1)

@jit(nopython=True)
def heuristic(a, b):
    # Usando distância Manhattan para cálculo mais rápido
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def bidirectional_astar(grid, start, goal):
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0), (-1, -1), (1, 1)]  # Direções ortogonais e diagonais
    
    # Inicializa as duas frentes de busca
    open_set_start = []
    open_set_goal = []
    heapq.heappush(open_set_start, (heuristic(start, goal), start))
    heapq.heappush(open_set_goal, (heuristic(goal, start), goal))
    
    came_from_start = {}
    came_from_goal = {}
    
    visited_start = np.zeros_like(grid, dtype=bool)  # Usar uma matriz booleana para verificar visitados rapidamente
    visited_goal = np.zeros_like(grid, dtype=bool)
    
    while open_set_start and open_set_goal:
        # Expandir a busca de start
        _, current_start = heapq.heappop(open_set_start)
        
        if visited_goal[current_start]:
            # Se encontramos no lado da busca de goal, reconstrua o caminho
            path_start = [current_start]
            while current_start in came_from_start:
                current_start = came_from_start[current_start]
                path_start.append(current_start)
            path_start.reverse()
            path_goal = [current_start]
            while current_start in came_from_goal:
                current_start = came_from_goal[current_start]
                path_goal.append(current_start)
            path_goal.reverse()
            return path_start + path_goal[1:], visited_start
        
        visited_start[current_start] = True
        
        for dx, dy in neighbors:
            neighbor = (current_start[0] + dx, current_start[1] + dy)
            if (0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1] and
                grid[neighbor] == 0 and not visited_start[neighbor]):
                came_from_start[neighbor] = current_start
                heapq.heappush(open_set_start, (heuristic(neighbor, goal), neighbor))
        
        # Expandir a busca de goal
        _, current_goal = heapq.heappop(open_set_goal)
        
        if visited_start[current_goal]:
            # Se encontramos no lado da busca de start, reconstrua o caminho
            path_goal = [current_goal]
            while current_goal in came_from_goal:
                current_goal = came_from_goal[current_goal]
                path_goal.append(current_goal)
            path_goal.reverse()
            path_start = [current_goal]
            while current_goal in came_from_start:
                current_goal = came_from_start[current_goal]
                path_start.append(current_goal)
            path_start.reverse()
            return path_start + path_goal[1:], visited_goal
        
        visited_goal[current_goal] = True
        
        for dx, dy in neighbors:
            neighbor = (current_goal[0] + dx, current_goal[1] + dy)
            if (0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1] and
                grid[neighbor] == 0 and not visited_goal[neighbor]):
                came_from_goal[neighbor] = current_goal
                heapq.heappush(open_set_goal, (heuristic(neighbor, start), neighbor))
    
    return None, visited_start

# Executar e medir tempo
start_time = time.time()
path, visited = bidirectional_astar(grid, start, goal)
end_time = time.time()
elapsed_ms = (end_time - start_time) * 1000

# Visualização
fig, ax = plt.subplots(figsize=(13, 15))

# Desenhar grid
for x in range(grid.shape[0]):
    for y in range(grid.shape[1]):
        color = 'white'
        if grid[x, y] == 1:
            color = 'black'
        elif visited[x, y]:
            color = 'lightblue'
        rect = plt.Rectangle((y, grid.shape[0]-1 - x), 1, 1, edgecolor='gray', facecolor=color)
        ax.add_patch(rect)

# Caminho
if path:
    for px, py in path:
        rect = plt.Rectangle((py, grid.shape[0]-1 - px), 1, 1, facecolor='orange')
        ax.add_patch(rect)

# Início e fim
ax.add_patch(plt.Rectangle((start[1], grid.shape[0]-1 - start[0]), 1, 1, color='green'))
ax.add_patch(plt.Rectangle((goal[1], grid.shape[0]-1 - goal[0]), 1, 1, color='red'))

ax.set_xlim(0, grid.shape[1])
ax.set_ylim(0, grid.shape[0])
ax.set_xticks([])
ax.set_yticks([])
ax.set_aspect('equal')
plt.title(f"Busca Bidirecional A* (tempo: {elapsed_ms:.2f} ms)")
plt.show()

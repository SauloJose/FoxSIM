import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import heapq

# Parâmetros do Simulador
GRID_SIZE = 30
START = np.array([1, 1])
GOAL = np.array([28, 28])
OBSTACLES = [
    ((10, 10), (2, 2)),
    ((17, 20), (2, 2)),
    ((8, 22), (2, 2)),
]

# Parâmetros PID
Kp = 1.0
Ki = 0.1
Kd = 0.5

# Função de Planejamento de Trajetória (A* Completo)
def a_star(start, goal, obstacles, grid_size):
    """Implementação simplificada do algoritmo A*."""
    # Definição de obstáculos no grid
    grid = np.zeros((grid_size, grid_size))
    for (pos, size) in obstacles:
        x, y = pos
        sx, sy = size
        grid[x:x+sx, y:sy] = 1  # Marca obstáculos
    
    # A* para encontrar o caminho mais curto
    def heuristic(a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def neighbors(node):
        x, y = node
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 4 direções possíveis
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx, ny] == 0:
                yield (nx, ny)

    # A* (open list e closed list)
    open_list = []
    heapq.heappush(open_list, (0 + heuristic(start, goal), 0, tuple(start)))  # f, g, node (convertendo start para tupla)
    came_from = {}
    g_score = {tuple(start): 0}  # Alterado para usar tupla como chave

    while open_list:
        _, current_g, current = heapq.heappop(open_list)

        if current == tuple(goal):  # Comparando como tupla
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return np.array(path[::-1])  # Inverter o caminho

        for neighbor in neighbors(current):
            tentative_g = current_g + 1  # Distância unitária

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_list, (f_score, tentative_g, neighbor))

    return []  # Se não encontrar caminho

# Função PID para controle de direção e velocidade
def pid_control(current_pos, goal_pos, prev_error, integral):
    """Calcula o controle PID para movimento em direção ao objetivo."""
    error = np.linalg.norm(goal_pos - current_pos)  # Erro é a distância ao objetivo
    integral += error
    derivative = error - prev_error
    
    # PID simples
    control_signal = Kp * error + Ki * integral + Kd * derivative
    return control_signal, error, integral

# Função de Simulação do Robô
def simulate_robot(start, goal, obstacles, grid_size, steps=200):
    trajectory = [start]
    pos = start.astype(float)  # Alterar para tipo float64
    prev_error = 0
    integral = 0

    for _ in range(steps):
        # Obter o próximo destino pela A*
        path = a_star(pos, goal, obstacles, grid_size)
        if len(path) == 0:
            print("Caminho não encontrado!")
            break
        next_pos = path[-1]

        # Controlador PID para ajustar a direção
        control_signal, prev_error, integral = pid_control(pos, next_pos, prev_error, integral)

        # Simulação de movimento: direção ajustada pela PID
        direction = next_pos - pos
        if np.linalg.norm(direction) > 0:
            direction /= np.linalg.norm(direction)
        pos += direction * 0.5  # Movimenta em direção ao próximo ponto (ajustar a velocidade)
        trajectory.append(pos)

        # Verifica se chegou ao objetivo
        if np.linalg.norm(np.array(pos) - np.array(goal)) < 1:
            break
    
    return np.array(trajectory)

# Função para plotar a trajetória
def plot_trajectory(trajectory, obstacles, start, goal):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(trajectory[:, 0], trajectory[:, 1], 'b.-', label="Trajetória")
    ax.plot(start[0], start[1], 'go', label="Início")
    ax.plot(goal[0], goal[1], 'ro', label="Destino")
    
    # Plotar obstáculos
    for (pos, size) in obstacles:
        rect = Rectangle(pos, size[0], size[1], color='r', alpha=0.6)
        ax.add_patch(rect)
    
    ax.set_xlim(0, GRID_SIZE)
    ax.set_ylim(0, GRID_SIZE)
    ax.set_title("Simulação de Trajetória com PID e Obstáculos")
    ax.legend()
    ax.grid(True)
    plt.show()

# Execução da Simulação
trajectory = simulate_robot(START, GOAL, OBSTACLES, GRID_SIZE)
plot_trajectory(trajectory, OBSTACLES, START, GOAL)

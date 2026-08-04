"""
bt_config.py

Configurações centralizadas do time (categoria VSSS - IEEE).

Antes desta refatoração, valores como o tamanho do campo (150 x 130 cm)
apareciam duplicados em vários pontos (bt_conditions.py, e três vezes em
strategies.py), com risco real de um dia ficarem dessincronizados caso o
campo mude de dimensão. Este módulo é a única fonte de verdade para essas
constantes.
"""

# --- Campo (regras oficiais IEEE VSSS) ---
FIELD_LENGTH = 150.0
FIELD_WIDTH = 130.0
FIELD_LIMITS = (FIELD_LENGTH, FIELD_WIDTH)

# --- Robô (categoria VSSS: robôs de 8x8x8 cm) e bola ---
ROBOT_RADIUS = 4.0       # cm, metade da lateral do cubo do robô
BALL_RADIUS = 2.13       # cm, bola de golfe oficial
CONTACT_DISTANCE = ROBOT_RADIUS + BALL_RADIUS  # distância robô-bola considerada "contato"

# --- Velocidades ---
MAX_WHEEL_SPEED = 20.0
GOALIE_MAX_SPEED = 30.0
SUPPORT_SPEED_FACTOR = 0.85
EMERGENCY_REVERSE_SPEED = 20.0

# --- Navegação / desvio de obstáculos ---
AVOID_RADIUS = 25.0              # raio do campo potencial tangencial (desvio preventivo)
EMERGENCY_STOP_MARGIN = 0.8      # folga somada ao contato físico p/ ré de emergência
EMERGENCY_STOP_DISTANCE = 8
EMERGENCY_FRONTAL_COS = 0.3     # cosseno do semi-ângulo do cone frontal (~70°/lado, cone de ~140°)

# --- Zonas táticas ---
CORNER_SIZE = 18.0
WALL_MARGIN = 14.0
DEFENSE_RADIUS = 35.0
SUPPORT_DEFENSE_RADIUS = 40.0

# Distância mínima que o robô de apoio deve manter da bola, para não "dobrar"
# fisicamente o atacante principal quando a bola está perto do próprio gol.
# Times mais agressivos podem reduzir esse valor (rebote mais próximo), mas
# nunca abaixo de ~2 raios de robô + raio da bola, para evitar sobreposição real.
MIN_SUPPORT_TO_BALL_DIST_STANDARD = 25.0
MIN_SUPPORT_TO_BALL_DIST_AGGRESSIVE = 18.0
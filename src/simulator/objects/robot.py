import pygame
import numpy as np
import pymunk
import math
from ui.interface_config import *
from simulator.intelligence.controll import PIDController

# =============================================================================
# Controlador Lyapunov (integrado localmente)
# =============================================================================

class LyapunovController:
    """
    Controlador baseado em função de Lyapunov para robô diferencial.
    Estabiliza o robô em um ponto alvo com orientação livre.
    """
    def __init__(self, kv=1.5, kw=4.0, max_linear=None, max_angular=None):
        """
        :param kv: ganho da velocidade linear (cm/s por cm de erro)
        :param kw: ganho da velocidade angular (rad/s por rad de erro)
        :param max_linear: saturação da velocidade linear (cm/s)
        :param max_angular: saturação da velocidade angular (rad/s)
        """
        self.kv = kv
        self.kw = kw
        self.max_linear = max_linear
        self.max_angular = max_angular

    def compute(self, target_pos, current_pos, current_angle):
        """
        Retorna (v, w) – velocidades linear e angular.
        """
        e = target_pos - current_pos
        dist = np.linalg.norm(e)
        if dist < 1e-4:
            return 0.0, 0.0

        # Vetor direção do robô
        u = np.array([np.cos(current_angle), np.sin(current_angle)])

        # Projeção do erro no eixo longitudinal do robô
        e_proj = np.dot(e, u)

        # Erro angular entre o vetor erro e a direção do robô
        cross = np.cross(u, e)       # u.x * e.y - u.y * e.x
        dot = np.dot(u, e)
        angle_error = np.arctan2(cross, dot)   # positivo se alvo está à esquerda

        # Lei de Lyapunov
        v = self.kv * e_proj
        w = self.kw * angle_error

        # Saturação
        if self.max_linear is not None:
            v = np.clip(v, -self.max_linear, self.max_linear)
        if self.max_angular is not None:
            w = np.clip(w, -self.max_angular, self.max_angular)

        return v, w

# =============================================================================
# Classe Robot
# =============================================================================

# Limites de aceleração do controle "servo" por força (ver apply_motor_forces).
# Podem ser sobrescritos definindo ROBOT_MAX_LINEAR_ACCEL / ROBOT_MAX_ANGULAR_ACCEL
# em ui/interface_config.py; caso contrário usam estes valores padrão.
try:
    _ROBOT_MAX_LINEAR_ACCEL = ROBOT_MAX_LINEAR_ACCEL
except NameError:
    _ROBOT_MAX_LINEAR_ACCEL = 600.0  # cm/s^2
try:
    _ROBOT_MAX_ANGULAR_ACCEL = ROBOT_MAX_ANGULAR_ACCEL
except NameError:
    _ROBOT_MAX_ANGULAR_ACCEL = 120.0  # rad/s^2

class Robot:
    """
    Robô controlado por cinemática diferencial com corpo dinâmico no Pymunk.
    """
    def __init__(self, x, y, team, role, id, image, space, initial_angle=0):
        """
        Inicializa o robô com Pymunk.
        :param x, y: posição inicial (cm)
        :param team: time ('ally' ou 'enemy')
        :param role: função do robô
        :param id: identificador
        :param image: imagem Pygame (para renderização)
        :param space: espaço Pymunk
        :param initial_angle: ângulo inicial (graus)
        """
        self.space = space
        self.team = team
        self.role = role
        self.id_robot = id
        self.initial_image = image
        self.image = image
        self.type_object = ROBOT_OBJECT

        # Dimensões do robô (cm)
        self.width = ROBOT_SIZE_CM
        self.height = ROBOT_SIZE_CM
        self.wheels_radius = ROBOT_WHEELS_RADIUS_CM
        self.distance_wheels = ROBOT_DISTANCE_WHEELS_CM
        self.distance_wheels_to_center = ROBOT_DISTANCE_WHEELS_TO_CENTER_CM

        # Propriedades dinâmicas
        self.mass = ROBOT_MASS
        self.inertia = (1/12) * self.mass * (self.width**2 + self.height**2)

        # Criação do corpo dinâmico
        self.body = pymunk.Body(self.mass, self.inertia)
        self.body.position = (x, y)
        self.body.angle = np.radians(initial_angle)
        self.body.velocity = (0.0, 0.0)
        self.body.angular_velocity = 0.0
        # Amortecimentos para evitar oscilações e deslizes excessivos
        self.body.damping = 0.98
        self.body.angular_damping = 0.98

        # Shape retangular (vértices relativos ao centro)
        half_w = self.width / 2
        half_h = self.height / 2
        vertices = [
            (-half_w, -half_h),
            ( half_w, -half_h),
            ( half_w,  half_h),
            (-half_w,  half_h)
        ]
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.friction = 0.8
        self.shape.elasticity = 0.2
        self.shape.collision_type = 3

        self.space.add(self.body, self.shape)

        # Velocidades das rodas (apenas para referência)
        self.v_l = 0.0
        self.v_r = 0.0

        # === Controle "servo" por força ===
        # Em vez de escrever diretamente em body.velocity (o que ignora
        # qualquer impulso de separação que o solver de colisão do Pymunk
        # tenha calculado no passo anterior e permite sobreposição entre
        # robôs), guardamos aqui a velocidade DESEJADA. A cada frame,
        # apply_motor_forces() converte essa velocidade-alvo em força/torque
        # aplicados ao corpo, deixando o solver de colisão do Pymunk livre
        # para resistir/reduzir essa força quando houver contato com outro
        # robô. Isso é o que garante que os robôs nunca se atravessem.
        self.target_velocity = np.array([0.0, 0.0], dtype=float)
        self.target_angular_velocity = 0.0
        # Ativado (por um único tick) via set_wheel_speeds(..., priority=True),
        # usado por manobras de "atuador dedicado" — ré de emergência e giros
        # de chute — que precisam ignorar o ritmo normal de aceleração da
        # condução sem deixar de respeitar o solver de colisão do Pymunk.
        self._priority_active = False
        self.priority_accel_multiplier = 6.0

        # Limites de aceleração do "motor" (cm/s² e rad/s²). Também evitam
        # que o corpo ganhe velocidade alta demais entre dois frames, o que
        # poderia causar "tunelamento" através de outro robô.
        self.max_linear_accel = _ROBOT_MAX_LINEAR_ACCEL
        self.max_angular_accel = _ROBOT_MAX_ANGULAR_ACCEL

        # Salva valores iniciais para reset
        self.initial_x = x
        self.initial_y = y
        self.initial_theta = self.body.angle

        # --- Controlador Lyapunov (substitui os PIDs para movimento) ---
        self.lyapunov = LyapunovController(
            kv=3.0,                    # ganho linear (ajuste conforme necessário)
            kw=10.0,                    # ganho angular (mais agressivo para girar)
            max_linear=ROBOT_MAX_SPEED,
            max_angular=10.0           # rad/s (ajuste conforme necessário)
        )

        # Controladores PID (mantidos para compatibilidade, mas não usados no go_to_point)
        self.kp = 2.0
        self.ki = 0.1
        self.kd = 0.2
        self.pid_linear = PIDController(self.kp, self.ki, self.kd)
        self.pid_angular = PIDController(self.kp, self.ki, self.kd)
        self.pid_orientation = PIDController(self.kp, self.ki, self.kd)

        # Estado de seleção (para interface)
        self._is_selected = False

    # === Propriedades sincronizadas com o corpo Pymunk ===

    @property
    def position(self):
        return np.array(self.body.position, dtype=float)

    @position.setter
    def position(self, value):
        self.body.position = tuple(value)

    @property
    def x(self):
        return self.body.position.x

    @x.setter
    def x(self, value):
        self.body.position = (value, self.y)

    @property
    def y(self):
        return self.body.position.y

    @y.setter
    def y(self, value):
        self.body.position = (self.x, value)

    @property
    def angle(self):
        return self.body.angle

    @angle.setter
    def angle(self, value):
        self.body.angle = value

    @property
    def velocity(self):
        return np.array(self.body.velocity, dtype=float)

    @velocity.setter
    def velocity(self, value):
        self.body.velocity = tuple(value)

    @property
    def angular_velocity(self):
        return self.body.angular_velocity

    @angular_velocity.setter
    def angular_velocity(self, value):
        self.body.angular_velocity = value

    @property
    def direction(self):
        """Vetor direção calculado a partir do ângulo atual do corpo."""
        return np.array([np.cos(self.body.angle), np.sin(self.body.angle)], dtype=float)

    # === Métodos de controle ===

    def set_wheel_speeds(self, v_l, v_r, priority=False):
        """
        Define as velocidades das rodas.

        IMPORTANTE: isto NÃO escreve mais diretamente em body.velocity.
        Escrever a velocidade diretamente todo frame sobrescreve qualquer
        impulso de separação que o Pymunk tenha calculado ao resolver uma
        colisão no passo anterior, fazendo o robô "empurrar" através de
        outro robô e gerar sobreposição. Em vez disso guardamos a
        velocidade DESEJADA; quem efetivamente move o corpo é
        apply_motor_forces(), chamado antes de space.step() no loop
        principal, que aplica força/torque limitados e deixa o solver de
        colisão do Pymunk decidir o resultado final quando há contato.

        priority: use True para manobras curtas de "atuador dedicado" que
        precisam atingir a velocidade-alvo quase instantaneamente — ré de
        emergência (check_emergency_collision) e giros de chute
        (SpinShootNode/WallClearanceSpinNode/chute de rebatida). Isso
        aplica um multiplicador de aceleração só neste tick
        (priority_accel_multiplier), continuando a passar pelo solver de
        colisão do Pymunk — portanto ainda não atravessa outros robôs — só
        deixa de ser suavizado pelo limite normal de aceleração da condução.
        """
        self.v_l = v_l
        self.v_r = v_r
        v = (v_l + v_r) / 2.0
        omega = (v_r - v_l) / self.distance_wheels
        self.target_velocity = np.array(
            [v * math.cos(self.body.angle), v * math.sin(self.body.angle)],
            dtype=float
        )
        self.target_angular_velocity = omega
        self._priority_active = priority

    def apply_motor_forces(self, dt):
        """
        Converte a velocidade-alvo (definida por set_wheel_speeds /
        set_vec_velocity) em força e torque aplicados ao corpo.

        Deve ser chamado UMA VEZ POR ROBÔ, a cada frame, ANTES de
        space.step(). Como a "motorização" vira força (e não uma escrita
        direta de velocidade), o solver de colisão do Pymunk continua
        podendo reagir a contatos com outros robôs no mesmo passo de
        física, o que impede a sobreposição entre eles.
        """
        if dt <= 0:
            return

        accel_mult = self.priority_accel_multiplier if self._priority_active else 1.0

        # --- Força linear ---
        current_v = np.array(self.body.velocity, dtype=float)
        desired_accel = (self.target_velocity - current_v) / dt
        accel_norm = np.linalg.norm(desired_accel)
        max_linear = self.max_linear_accel * accel_mult
        if accel_norm > max_linear:
            desired_accel = desired_accel * (max_linear / accel_norm)
        force = self.mass * desired_accel
        self.body.apply_force_at_world_point(tuple(force), tuple(self.body.position))

        # --- Torque angular ---
        current_w = self.body.angular_velocity
        desired_ang_accel = (self.target_angular_velocity - current_w) / dt
        max_angular = self.max_angular_accel * accel_mult
        if desired_ang_accel > max_angular:
            desired_ang_accel = max_angular
        elif desired_ang_accel < -max_angular:
            desired_ang_accel = -max_angular
        self.body.torque += self.inertia * desired_ang_accel

        # O boost vale só para o tick em que foi pedido; se o node parar de
        # passar priority=True, a próxima chamada volta ao limite normal.
        self._priority_active = False

    def get_vec_velocity(self):
        """Retorna o vetor velocidade global."""
        return np.array(self.body.velocity, dtype=float)

    def set_vec_velocity(self, vx, vy, priority=False):
        """
        Define a velocidade linear global desejada (alvo), pelo mesmo
        mecanismo de força usado por set_wheel_speeds — não escreve mais
        em body.velocity diretamente, pelo mesmo motivo explicado ali.
        """
        self.target_velocity = np.array([vx, vy], dtype=float)
        self._priority_active = priority
        v = np.linalg.norm([vx, vy])
        omega = self.target_angular_velocity
        self.v_l = v - (omega * self.distance_wheels / 2.0)
        self.v_r = v + (omega * self.distance_wheels / 2.0)

    def move(self, dt):
        """Mantido para compatibilidade (não faz nada com Pymunk)."""
        pass

    def apply_force(self, force, contact_vector):
        """Aplica uma força no ponto de contato."""
        self.body.apply_force_at_world_point(force, contact_vector)

    def apply_impulse(self, impulse, contact_point=None):
        """Aplica um impulso no ponto de contato."""
        if contact_point is None:
            contact_point = self.position
        self.body.apply_impulse_at_world_point(impulse, contact_point)

    def apply_torque(self, torque):
        """Aplica um torque (modifica a velocidade angular diretamente)."""
        self.body.angular_velocity += torque / self.inertia

    def go_to_point(self, target_pos, target_angle, dt, allow_reverse=False):
        """
        Calcula velocidades das rodas usando controle de Lyapunov.

        target_angle: ângulo desejado ao chegar (não implementado nesta versão,
                      mas pode ser incorporado futuramente).
        allow_reverse: se True, permite marcha à ré (caso o alvo esteja atrás).
        """
        # Se a distância for muito pequena, para o robô
        pos_error = target_pos - self.position
        distance = np.linalg.norm(pos_error)
        if distance < 0.4:
            return 0.0, 0.0

        # Obter velocidades linear e angular do controlador Lyapunov
        v, w = self.lyapunov.compute(target_pos, self.position, self.angle)

        # Se allow_reverse for True e o alvo estiver atrás, podemos inverter
        # a velocidade e ajustar o sinal do w (não implementado para simplicidade)
        # Caso queira, pode ser adicionado aqui.

        # Converter v, w para velocidades das rodas (cinemática diferencial)
        v_l = v - (w * self.distance_wheels / 2.0)
        v_r = v + (w * self.distance_wheels / 2.0)

        # Limitar velocidades ao máximo permitido (já feito no controlador,
        # mas garantimos aqui também)
        max_speed = ROBOT_MAX_SPEED
        v_l = np.clip(v_l, -max_speed, max_speed)
        v_r = np.clip(v_r, -max_speed, max_speed)

        return v_l, v_r

    @staticmethod
    def normalize_angle(angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def reset(self):
        """Reseta posição e velocidades."""
        self.body.position = (self.initial_x, self.initial_y)
        self.body.angle = self.initial_theta
        self.body.velocity = (0.0, 0.0)
        self.body.angular_velocity = 0.0
        self.target_velocity = np.array([0.0, 0.0], dtype=float)
        self.target_angular_velocity = 0.0
        self.v_l = 0.0
        self.v_r = 0.0
        self.image = self.initial_image

    def set_position(self, x, y):
        """Define posição e zera velocidades."""
        self.body.position = (x, y)
        self.body.velocity = (0.0, 0.0)
        self.body.angular_velocity = 0.0
        self.target_velocity = np.array([0.0, 0.0], dtype=float)
        self.target_angular_velocity = 0.0
        self.v_l = 0.0
        self.v_r = 0.0

    def new_position(self, x, y):
        """Define posição sem resetar velocidades (apenas para posicionamento)."""
        self.body.position = (x, y)

    def stop(self):
        """Para o robô."""
        self.body.velocity = (0.0, 0.0)
        self.body.angular_velocity = 0.0
        self.target_velocity = np.array([0.0, 0.0], dtype=float)
        self.target_angular_velocity = 0.0
        self.v_l = 0.0
        self.v_r = 0.0

    def rotate(self, degrees):
        """Rotaciona o robô (incrementa o ângulo em graus)."""
        self.body.angle += np.radians(degrees)

    def sync_collision_object(self):
        """Não necessário com Pymunk, mantido para compatibilidade."""
        pass

    def distance_to(self, x, y):
        return np.linalg.norm(self.position - np.array([x, y], dtype=float))

    def draw(self, screen):
        """Desenha o robô na tela com rotação."""
        angle_deg = np.degrees(self.body.angle)
        rotated_image = pygame.transform.rotate(self.initial_image, angle_deg)

        if self._is_selected:
            selected_image = rotated_image.copy()
            width, height = selected_image.get_size()
            selected_image.lock()
            for x in range(width):
                for y in range(height):
                    r, g, b, a = selected_image.get_at((x, y))
                    if a > 0:
                        r = min(r + 100, 255)
                        g = min(g + 100, 255)
                        b = min(b + 100, 255)
                        selected_image.set_at((x, y), (r, g, b, a))
            selected_image.unlock()
            rotated_image = selected_image

        center = virtual_to_screen(self.position)
        rect = rotated_image.get_rect(center=center)
        screen.blit(rotated_image, rect.topleft)
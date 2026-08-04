import pygame
import numpy as np
import pymunk
import math
from ui.interface_config import *
from simulator.intelligence.controll import PIDController

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

        # Salva valores iniciais para reset
        self.initial_x = x
        self.initial_y = y
        self.initial_theta = self.body.angle

        # Controladores PID (mantidos para compatibilidade)
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

    def set_wheel_speeds(self, v_l, v_r):
        """Define as velocidades das rodas e atualiza o corpo."""
        self.v_l = v_l
        self.v_r = v_r
        v = (v_l + v_r) / 2.0
        omega = (v_r - v_l) / self.distance_wheels
        # Aplica a velocidade linear no referencial global
        self.body.velocity = (v * math.cos(self.body.angle), v * math.sin(self.body.angle))
        self.body.angular_velocity = omega

    def get_vec_velocity(self):
        """Retorna o vetor velocidade global."""
        return np.array(self.body.velocity, dtype=float)

    def set_vec_velocity(self, vx, vy):
        """Define a velocidade linear global."""
        self.body.velocity = (vx, vy)
        v = np.linalg.norm([vx, vy])
        omega = self.body.angular_velocity
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
        """Calcula velocidades das rodas usando PID (mantido para compatibilidade)."""
        pos_error = target_pos - self.position
        distance = np.linalg.norm(pos_error)

        if distance < 1.2:
            self.pid_linear.reset()
            self.pid_angular.reset()
            return 0.0, 0.0

        angle_to_target = np.arctan2(pos_error[1], pos_error[0])
        heading_error = self.normalize_angle(angle_to_target - self.angle)

        if allow_reverse and abs(heading_error) > (np.pi / 2.0):
            heading_error = self.normalize_angle(heading_error + np.pi)
            distance *= -1.0

        if abs(distance) > 6.0 or target_angle is None:
            effective_angle_error = heading_error
        else:
            final_angle_error = self.normalize_angle(target_angle - self.angle)
            weight = abs(distance) / 6.0
            effective_angle_error = weight * heading_error + (1.0 - weight) * final_angle_error

        v = self.pid_linear.compute(distance, dt)
        w = self.pid_angular.compute(effective_angle_error, dt)

        v_l = v - (w * self.distance_wheels / 2.0)
        v_r = v + (w * self.distance_wheels / 2.0)

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
        self.v_l = 0.0
        self.v_r = 0.0
        self.image = self.initial_image

    def set_position(self, x, y):
        """Define posição e zera velocidades."""
        self.body.position = (x, y)
        self.body.velocity = (0.0, 0.0)
        self.body.angular_velocity = 0.0
        self.v_l = 0.0
        self.v_r = 0.0

    def new_position(self, x, y):
        """Define posição sem resetar velocidades (apenas para posicionamento)."""
        self.body.position = (x, y)

    def stop(self):
        """Para o robô."""
        self.body.velocity = (0.0, 0.0)
        self.body.angular_velocity = 0.0
        self.v_l = 0.0
        self.v_r = 0.0

    def rotate(self, degrees):
        """Rotaciona o robô (incrementa o ângulo em graus)."""
        self.body.angle += np.radians(degrees)

    def sync_collision_object(self):
        """Não necessário com Pymunk, mantido para compatibilidade."""
        pass

    def distance_to(self, x, y):
        """Calcula a distância até um ponto (x, y) em cm."""
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
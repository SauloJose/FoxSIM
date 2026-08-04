import pygame
import numpy as np
import pymunk
from ui.interface_config import *
from simulator.intelligence.controll import PIDController  # se ainda usado, mas não é obrigatório

class Ball:
    def __init__(self, x, y, field, space, radius=BALL_RADIUS_CM, color=BALL_COLOR, max_velocity=100.0):
        """
        Inicializa a bola com Pymunk.
        :param x, y: posição inicial (cm)
        :param field: referência ao campo (para áreas de gol)
        :param space: espaço Pymunk compartilhado
        :param radius: raio da bola (cm)
        :param color: cor (não usado na física, apenas para referência)
        :param max_velocity: velocidade máxima (cm/s)
        """
        self.space = space
        self.field = field
        self.radius = radius
        self.mass = BALL_MASS
        self.color = color
        self.max_velocity = max_velocity
        self.type_object = BALL_OBJECT

        # Momento de inércia para disco sólido
        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = (x, y)
        self.body.velocity = (0.0, 0.0)
        self.body.angular_velocity = 0.0

        # Shape circular
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.friction = 0.8       # atrito com superfícies
        self.shape.elasticity = 0.3     # coeficiente de restituição
        self.shape.collision_type = 1   # opcional, para handlers específicos

        self.space.add(self.body, self.shape)

        # Imagem (mantida para renderização)
        scale = (2 * BALL_RADIUS_CM / SCALE_PX_TO_CM, 2 * BALL_RADIUS_CM / SCALE_PX_TO_CM)
        self.image = pygame.transform.smoothscale(
            pygame.image.load("src/assets/ball.png").convert_alpha(),
            scale
        )

        # Atributos auxiliares (para compatibilidade)
        self.impulse = None
        self.force = np.zeros(2, dtype=float)
        self.torque = 0.0
        self.previous_pos = np.array([0.0, 0.0])

        # Direção (será atualizada a partir da velocidade)
        self.direction = np.array([1.0, 0.0], dtype=float)

    # Propriedades de posição
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
    def velocity(self):
        return np.array(self.body.velocity, dtype=float)

    @velocity.setter
    def velocity(self, value):
        self.body.velocity = tuple(value)

    @property
    def speed(self):
        return np.linalg.norm(self.body.velocity)

    def set_velocity(self, vx, vy):
        """Define a velocidade linear, respeitando o limite máximo."""
        v = np.array([vx, vy], dtype=float)
        speed = np.linalg.norm(v)
        if speed > self.max_velocity:
            v = (v / speed) * self.max_velocity
        self.body.velocity = tuple(v)

    def apply_force(self, force: np.ndarray, point: np.ndarray = None):
        """Aplica uma força no ponto especificado (coordenadas globais)."""
        if point is None:
            point = self.position
        # Pymunk aplica força no centro de massa se point = position
        self.body.apply_force_at_world_point(force, point)

    def apply_impulse(self, impulse: np.ndarray, contact_point: np.ndarray = None):
        """Aplica um impulso no ponto de contato (coordenadas globais)."""
        if contact_point is None:
            contact_point = self.position
        self.body.apply_impulse_at_world_point(impulse, contact_point)

    def apply_torque(self, torque, dt):
        """Aplica um torque (não usado em Pymunk, pois torque é aplicado via forças ou diretamente em angular_velocity)."""
        # Em Pymunk, podemos simplesmente adicionar à velocidade angular
        self.body.angular_velocity += (torque / self.body.moment) * dt

    def clear_forces(self):
        """Limpa forças acumuladas (não necessário com Pymunk, mas mantido para compatibilidade)."""
        self.force[:] = 0.0
        self.torque = 0.0
        self.impulse = None

    def update_position(self, dt):
        """
        ATENÇÃO: Este método não é mais usado para atualização física.
        A atualização é feita por space.step(dt) no loop principal.
        Mantido apenas para compatibilidade com código legado.
        """
        pass

    def clamp_velocity(self):
        """Limita a velocidade linear ao máximo permitido."""
        v = self.body.velocity
        speed = np.linalg.norm(v)
        if speed > self.max_velocity:
            self.body.velocity = (v[0] / speed * self.max_velocity,
                                  v[1] / speed * self.max_velocity)

    def apply_damping(self, dt):
        """
        Aplica um amortecimento linear (atrito com o solo) de forma simples.
        Pode ser chamado após cada step.
        """
        # Reduz a velocidade gradualmente
        damping_factor = 0.9995  # ajustável
        self.body.velocity = (self.body.velocity[0] * damping_factor,
                              self.body.velocity[1] * damping_factor)
        # Se muito lento, zera
        if np.linalg.norm(self.body.velocity) < 0.001:
            self.body.velocity = (0.0, 0.0)

    def reset_position(self):
        """Reseta a posição para o centro do campo e zera velocidades."""
        self.body.position = (XVBALL_INIT, YVBALL_INIT)
        self.body.velocity = (0.0, 0.0)
        self.body.angular_velocity = 0.0
        self.direction = np.array([1.0, 0.0], dtype=float)

    def is_inside_goal(self, goal_area):
        """
        Verifica se a bola está dentro da área do gol fornecida.
        goal_area deve ser um objeto com método contains(point).
        """
        return goal_area.contains(self.position)

    def distance_to(self, x, y):
        """Distância até um ponto (cm)."""
        return np.linalg.norm(self.position - np.array([x, y]))

    def draw(self, screen):
        """Desenha a bola na tela."""
        pos_img = virtual_to_screen(self.position)
        ball_rect = self.image.get_rect(center=(pos_img[0], pos_img[1]))
        screen.blit(self.image, ball_rect)
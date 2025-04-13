import pygame
import numpy as np  # Substitui math por numpy
from simulator.collision.collision import * 
from ui.interface_config import *

class Ball:
    def __init__(self, x, y, field, radius=BALL_RADIUS_CM, color=BALL_COLOR):
        """
        Inicializa a bola.
        :param x: Posição X da bola na imagem principal
        :param y: Posição Y da bola na imagem principal
        :param radius: Raio da bola em cm.
        :param color: Cor da bola (RGB).
        """
        #Variáveis espaciais
        #Transforma as variáveis para o espaço virtual
        # Espaço vetorial
        self._position = np.array([x,y], dtype=float)
        self.velocity = np.zeros(2, dtype=float) #(vx, vy)
        self.direction = np.array([1.0,0.0],dtype=float)

        #Variáveis anteriores para poder aplicar o Crossing
        self.previous_pos = np.array([0,0],dtype=float)

        #Escala para a bola
        scale = (2*BALL_RADIUS_CM / SCALE_PX_TO_CM, 2*BALL_RADIUS_CM / SCALE_PX_TO_CM)

        #imagem que representa a bola
        self.image = pygame.transform.smoothscale(pygame.image.load("src/assets/ball.png").convert_alpha(), scale)
        
        # Física
        self.radius = radius    
        self.mass = BALL_MASS 
        self.inertia = 0.5 *self.mass*self.radius**2 #Disco sólido
        self.angular_velocity =0.0  #rad/s
        self.size = np.array([2*self.radius, 2*self.radius])

        # Agentes físicos
        self.force = np.zeros(2,dtype=float)
        self.torque = 0.0
        self.impulse = None 

        # Outros
        self.color = color  
        self.type_object = BALL_OBJECT
        self.field = field 

        #Objeto de colisão para tratar das colisões 
        self.collision_object = CollisionCircle(
                self.x, self.y, self.radius,
                type_object=MOVING_OBJECTS, reference=self
                )

    #WHATCHDOGS
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        if not isinstance(value, np.ndarray):
            value = np.array(value, dtype=float)
        self._position = np.array(value, dtype=float)
        self.collision_object.x = self._position[0]
        self.collision_object.y = self._position[1]

    @property
    def x(self):
        return self.position[0]

    @x.setter
    def x(self, value):
        self._position[0] = value
        self.collision_object.x =value

    @property
    def y(self):
        return self.position[1]

    @y.setter
    def y(self, value):
        self._position[1] = value
        self.collision_object.y = value


    def set_velocity(self, vx, vy):
        """
        Define a velocidade da bola.
        :param vx: Velocidade no eixo X.
        :param vy: Velocidade no eixo Y.
        """
        self.velocity = np.array([vx, vy], dtype=float)
        self.speed = np.linalg.norm(self.velocity)  # Atualiza a velocidade linear
        
        if self.speed > 0:
            self.direction = self.velocity /self.speed  # Atualiza a direção


    def update_position(self, dt):
        """
        Atualiza a posição da bola com física realista:
        - Impulso
        - Força contínua
        - Rolamento com resistência
        - Perda progressiva da rotação
        """
        #Gambiarra para evitar crossing
        self.dt = dt

        #Atualiza posição anterior
        self.previous_pos = self.position.copy()
        # 1. Aplica impulso (se existir)
        if self.impulse is not None:
            self.velocity += self.impulse / self.mass
            self.impulse = None

        # 2. Calcula aceleração linear e atualiza velocidade
        acceleration = self.force / self.mass
        self.velocity += acceleration * dt
        
        # 3. Atrito com o solo (dinâmico linear)
        if np.linalg.norm(self.velocity) > 0:
            # Aproximação de desaceleração natural por rolamento
            rolling_resistance_coeff = 0.002  # Bem menor que atrito deslizante
            friction_force_mag = rolling_resistance_coeff * self.mass * 980  # N = m.g
            # A direção oposta à velocidade
            friction_dir = -self.velocity / np.linalg.norm(self.velocity)
            friction_accel = friction_dir * (friction_force_mag / self.mass)
            
            new_velocity = self.velocity + friction_accel * dt
            if np.dot(new_velocity, self.velocity) < 0:
                self.velocity = np.zeros(2)
            else:
                self.velocity = new_velocity
            # Atualiza rotação associada ao rolamento
            linear_speed = np.linalg.norm(self.velocity)
            self.angular_velocity = linear_speed / self.radius

        # 4. Atualiza posição com velocidade final
        self.position += self.velocity * dt


        # 5. Calcula aceleração angular e atualiza velocidade angular
        self.angular_velocity += 0.995


        # 6. Atualiza direção (para possíveis efeitos visuais)
        if np.linalg.norm(self.velocity) > 0:
            self.direction = self.velocity / np.linalg.norm(self.velocity)

        # 7. Reseta forças acumuladas
        self.force = np.zeros(2, dtype=float)
        self.impulse = None
        self.torque = 0.0

    def apply_force(self, force: np.ndarray, point: np.ndarray =None):
        '''
            Acumula uma força na bola
        '''
        if point is None:
            point = self.position
        self.force += force 
        r = point - self.position
        torque = np.cross(r,force)
        self.torque += torque 

    def apply_impulse(self, impulse, contact_point = None):
        '''
            Aplica um impulso na bola
        '''
        if self.impulse is None:
            self.impulse = impulse 
        else:
            self.impulse +=impulse 

        if contact_point is not None:
            r = contact_point - np.array([self.x, self.y])
            torque_impulse = np.cross(r, impulse)
            self.angular_velocity += torque_impulse / self.inertia
            

    def apply_torque(self, torque, dt):
        """
        Aplica um torque na bola, alterando sua velocidade angular.
        :param torque: Torque aplicado (em N.m).
        :param dt: Intervalo de tempo (em segundos).
        """
        angular_acceleration = torque / self.inertia
        self.angular_velocity += angular_acceleration * dt

    def clear_forces(self):
        '''
            Reseta as forças e torques acumulados. Útil após o update entre frames
        '''
        self.force[:] = 0
        self.torque = 0
        self.impulse = None 

    def reset_position(self):
        """
        Reseta a posição da bola para as coordenadas fornecidas.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        self.position = np.array([XVBALL_INIT, YVBALL_INIT], dtype=float)
        self.velocity = np.zeros(2,dtype=float)
        self.direction =np.array([1.0, 0.0],dtype=float)
        self.speed = 0

        self.collision_object.x = self.x
        self.collision_object.y = self.y

    
    def is_inside_goal(self, goal_area:CollisionRectangle):
        """
        Verifica se a bola está dentro da área do gol.
        :param goal_area: Área do gol (CollisionRectangle).
        :return: True se a bola está dentro do gol, False caso contrário.
        """
        # Verifica se a bola está dentro da área do gol
        is_inside, mtv = goal_area.check_point_inside(self.collision_object)
        return is_inside
    
    def draw(self, screen):
        """
        Desenha a bola na tela.
        :param screen: Superfície do pygame onde a bola será desenhada.
        """
        # Converte posição virtual para coordenada de tela
        pos_img = virtual_to_screen([self.x, self.y])

        # Pega o retângulo da imagem da bola e centraliza na posição da bola
        ball_rect = self.image.get_rect(center=(pos_img[0], pos_img[1]))

        # Desenha a imagem da bola com fundo transparente
        screen.blit(self.image, ball_rect)


    def distance_to(self, x, y):
        """
        Calcula a distância até um ponto (x, y).
        :param x: Posição X do ponto.
        :param y: Posição Y do ponto.
        :return: Distância até o ponto.
        """
        return np.linalg.norm(self.position - np.array([x,y]))
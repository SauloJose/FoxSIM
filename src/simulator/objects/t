'''
@ Saulo: Na simulação, quando rotacionar o robô, o vetor direção tem que ser modificado junto.
'''


import pygame
import numpy as np
from simulator.simUtils import *
from simulator.collision.collision import *
from simulator.intelligence.logic.controll import *
from simulator.intelligence.basicControl import *
from enum import Enum 
from typing import List, Optional, Tuple

class BotRoles(str, Enum):
    """
        Enumeração que representa qual a função do robô dentro do sistema
        - ATTACKER - Atacante 
        - GOALKEEPER - Goleiro 
        - DEFENSOR  - Defesa
    """
    ATTACKER = "ATACANTE"
    GOALKEEPER = "GOLEIRO"
    DEFENDER = "DEFENSOR"

    def __str__(self):
        return self.value

class BotId(str, Enum):
    """
    Enumeração que representa o identificador do robô dentro do simulador
    
    - ATK1 - Atacante 1
    - ATK2 - Atacante 2
    - DEF - Defensor 
    - GK - Goleiro
    """
    ATK1 = "ATK1" 
    ATK2 = "ATK2"
    DEF = "DEF"
    GK  = "GK"

    def __str__(self):
        return self.value

class Robot:
    '''
        Implementação dinâmica de um robô controlado por controle diferencial
    '''
    def __init__(self, x, y, team, role:BotRoles, id:BotId, image, initial_angle=0):
        '''
            Inicializando o objeto robô que será um objeto que irá se mover e interagir na simulação
        '''
        ''' Angulo theta com a horizontal em radianos'''
        self.team = team                        # indicação do time
        self.role = role                        # função do robô
        self.id_robot = id                      # Apenas um identificado para ele
        self.image    = image                   # Imagem que representa o robô7
        self.initial_image = image              # Imagem inicial para quando resetar o robô.
        self.type_object = SimObjTypes.ROBOT_OBJECT       

        # Estado do robô
        self._position=np.array([x,y], dtype=float)
        self.previous_position = np.array([0.0,0.0],dtype=float)    #Posição anterior para aplicar o crossing
        self._angle = self.normalize_angle(np.radians(initial_angle))
        self._direction = np.array([np.cos(self._angle), np.sin(self._angle)])

        # Dimensões físicas (valores padrão em cm)
        self.width = ROBOT_SIZE_CM
        self.height = ROBOT_SIZE_CM
        self.wheels_radius = ROBOT_WHEELS_RADIUS_CM
        self.wheels_distance = ROBOT_DISTANCE_WHEELS_CM
        self.wheels_to_center = ROBOT_DISTANCE_WHEELS_CM/2


        # Propriedades dinâmicas
        self.mass = ROBOT_MASS
        self.inertia = (1/12) * self.mass * (self.width**2 + self.height**2) #retângulo
        

        # Estado dinâmico
        self.velocity = np.zeros(2, dtype= float ) #cm/s
        self.angular_velocity = 0.0
        self.wheels_speed = np.array([0.0,0.0],dtype=float) # [left, right] cm/s

        # Forcas e Torques
        self.force = np.zeros(2, dtype=float)
        self.torque = 0.0
        self.impulse = None

        # Limites operacionais
        self.max_velocity = 50.0 #cm/s 
        self.max_angular_velocity = np.pi/2 #rad/s (valor padrão)
        self.max_wheel_speed = self.max_velocity * 1.2 # cm/s 

        # Colisão
        self.collision_object = CollisionRectangle(
            self.x, self.y, self.width, self.height, 
            type_object=ObjTypes.MOVING_OBJECTS, reference=self)
        self.sync_collision_object()


        ## Variávies do controlador interno para simular PID para as rodas
        # Controlador PID para o robô
        self.kp = 2.0
        self.ki = 0.1
        self.kd = 0.2

        # Objetos de controle PID do robô
        # PID da distância
        self.pid_linear = PIDController(self.kp,self.ki,self.kd)

        # PID do angulo até o alvo 
        self.pid_heading = PIDController(self.kp,self.ki,self.kd)

        # PID do ângulo final do robô
        self.pid_angular = PIDController(self.kp,self.ki,self.kd)

        # Salva estado inicial do robô
        self._save_initial_state()

        # Métodos para interatibilidade com a interface do simulador
        self._is_selected = False 

    def _save_initial_state(self):
        """Salva o estado inicial para reset"""
        self.initial_position = self.position.copy()
        self.initial_angle = self._angle
        self.initial_direction = self.direction.copy()
        self.initial_wheels_speed = self.wheels_speed.copy()
        self.initial_velocity = self.velocity.copy()
        self.initial_angular_velocity = self.angular_velocity

    def set_max_velocity(self, max_velocity: float):
        ''' Define a velocidade máxima permitida para o robô'''
        self.max_velocity = max(0.0, float(max_velocity))

    def set_max_angular_velocity(self, max_angular_velocity: float):
        '''
            Define a velociade angular máxima permitida (em rad/s)
        '''
        self.max_angular_velocity = max(0.0, float(max_angular_velocity))

    # ---- Propriedades----
    @property
    def position(self) -> np.ndarray:
        return self._position
    
    @position.setter 
    def position(self, value: Tuple[float, float]):
        self._position =np.array(value,dtype=float)
        self.collision_object.x = self._position[0]
        self.collision_object.y = self._position[1]

    @property
    def x(self) -> float:
        return self.position[0]

    @x.setter
    def x(self, value: float):
        self.position[0] = value
        self.collision_object.x =value

    @property
    def y(self) -> float:
        return self.position[1]

    @y.setter
    def y(self, value: float):
        self.position[1] = value
        self.collision_object.y =value

    @property
    def angle(self) -> float:
        return self._angle 

    @angle.setter 
    def angle(self, value: float):
        '''
            Define o ângulo e atualiza automaticamente o vetor direção
        '''
        self._angle = self.normalize_angle(value)
        self._direction = np.array([np.cos(self._angle), np.sin(self._angle)])

    
    @property
    def direction(self):
        return self._direction 
    
    @direction.setter
    def direction(self, value):
        if not isinstance(value, (np.ndarray, list, tuple)) or len(value) != 2:
            raise ValueError("Direction must be a 2D vector")
        value = np.asarray(value, dtype=float)
        norm = np.linalg.norm(value)
        if norm < 1e-6:  # Evita divisão por zero
            raise ValueError("Direction vector cannot be zero")
        self._direction = value / norm
        self._angle = np.arctan2(self._direction[1], self._direction[0])

    @property
    def v_l(self) -> float:
        return self.wheels_speed[0]
    
    @v_l.setter
    def v_l(self, value: float):
        self.wheels_speed[0] = np.clip(value, -self.max_wheel_speed, self.max_wheel_speed)
    
    @property
    def v_r(self) -> float:
        return self.wheels_speed[1]
    
    @v_r.setter
    def v_r(self, value: float):
        self.wheels_speed[1] = np.clip(value, -self.max_wheel_speed, self.max_wheel_speed)
    
    @property
    def v(self) -> float:
        """Velocidade linear tangencial (na direção do robô)"""
        return np.dot(self.velocity, self.direction)
    
    @v.setter
    def v(self, value: float):
        """Define a velocidade linear mantendo a direção atual"""
        self.velocity = value * self.direction
    
    @property
    def omega(self) -> float:
        """Velocidade angular (rad/s)"""
        return self.angular_velocity
    
    @omega.setter
    def omega(self, value: float):
        """Define a velocidade angular com limite"""
        self.angular_velocity = np.clip(value, -self.max_angular_velocity, self.max_angular_velocity)

    # --- Métodos principais ------
    #Método para aplicar os valores da simulação na classe
    def set_physics_params(self,mass: float, width: float, height: float, wheel_radius: float, dist_wheels: float):
        '''
            Aplicando as variáveis carregadas para a física do robô
        '''
        self.width = width
        self.height = height
        self.wheels_radius = wheel_radius
        self.wheels_distance = dist_wheels
        self.wheels_to_center = dist_wheels / 2

        # propriedades dinâmicas aplicadas no robô
        self.mass = mass
        self.inertia = (1/12) * self.mass * (self.width**2 + self.height**2) #retângulo


    # Método para enviar os valores de KP, Kd e Ki
    def set_controll_params(self,kp:float,kd:float,ki:float):
        # Atualizando constantes
        self.kp = kp 
        self.kd = kd 
        self.ki = ki 
        
        # Atualizando controladores PID
        self.pid_linear = PIDController(self.kp,self.ki,self.kd)
        self.pid_heading = PIDController(self.kp,self.ki,self.kd)
        self.pid_angular = PIDController(self.kp,self.ki,self.kd)

    def set_max_speeds(self, max_velocity: float, max_angular_velocity: float):
        ''' Define as velocidades máximas operacionais'''
        self.max_velocity = max(0.0, max_velocity)
        self.max_angular_velocity = max(0.0, max_angular_velocity)
        self.max_wheel_speed = self.max_velocity*1.2


    # Aplicar a edição e verificação de código num arquivo que exiba na interface
    def goto_point(self, target_pos: Tuple[float, float], target_angle: float, dt:float):
        ''' Calcula velocidades das rodas para ir até um ponto'''
        return go_to_point(self, target_pos, target_angle, dt)

    @staticmethod
    def normalize_angle(angle: float) -> float:
        """
        Normaliza ângulos para o intervalo [-π, π] usando numpy.
        """
        return np.arctan2(np.sin(angle), np.cos(angle))

    #setando velocidade das rodas
    def set_wheel_speeds(self, v_left: float, v_right: float):
        """Define as velocidades das rodas com limitação direta"""
        self.v_l = v_left 
        self.v_r = v_right 
        self._update_velocity_from_wheels()

    def _update_velocity_from_wheels(self):
        ''' Atualiza a velocidade global baseada nas rodas'''
        # velocidade linear (média das rodas)
        v = (self.v_r+self.v_l)/2

        # Velocidade angular (diferença das rodas)
        omega = (self.v_r - self.v_l) / self.wheels_distance

        # Componentes da velocidade
        self.v = v
        self.omega = omega 

    #puxa as velocidades lineares das rodas
    def get_vec_velocity(self):
        """
            Retorna o vetor velocidade (vx, vy) do robô no referencial global
        """
        self.update_velocity_vector()
        return self.velocity

    def get_angle_from_direction(self, direction: np.ndarray) -> float:
        """
        Retorna o ângulo (em graus) correspondente a um vetor de direção 2D.
        O ângulo é medido no sentido anti-horário a partir do eixo X positivo.

        Ex: 
        [1, 0] ➝ 0°
        [0, 1] ➝ 90°
        [-1, 0] ➝ 180°
        [0, -1] ➝ 270°
        """
        angle_rad = np.arctan2(direction[1], direction[0])  # arctan2(dy, dx)
        angle_deg = np.degrees(angle_rad)
        return angle_deg % 360  # Garante que o ângulo esteja entre 0 e 360

    # seta o vetor velocidade do robô
    def set_velocity_vector(self, vx:float,vy:float):
        ''' Define a velocidade global do robo'''
        global_velocity = np.array([vx, vy], dtype=float)
        
        # Componente na direção atual (tangencial)
        v = np.dot(global_velocity, self.direction)
        
        # Componente perpendicular (para cálculo de omega)
        v_perp = np.dot(global_velocity, np.array([-self.direction[1], self.direction[0]]))
        omega = v_perp / self.wheels_to_center
        
        # Atualiza velocidades
        self.v = v
        self.omega = omega
        
        # Atualiza velocidades das rodas
        self.v_l = v - omega * self.wheels_to_center
        self.v_r = v + omega * self.wheels_to_center
        
        self.sync_collision_object()

    def move(self, dt: float):
        """
        Atualiza a posição e orientação do robô baseado na física.
        
        Args:
            dt: Passo de tempo em segundos
            
        Calcula:
            - Forças e torques das rodas
            - Acelerações linear e angular
            - Atualiza posição e orientação
            - Aplica limites físicos e amortecimento
        """
        #Salvando posição anterior:
        self.previous_position = self.position.copy()

        # 1. Força das rodas
        force_magnitude = (self.v_l + self.v_r)*self.mass / 2
        force = force_magnitude *self.direction

        # 2. Calcula o torque diferencial
        torque = (self.v_r - self.v_l)*self.mass*self.wheels_to_center

        # 3. Acumula força e torque do controle
        self.force += force
        self.torque += torque

        # 4. Integra aceleração linear e angular
        acceleration = self.force / self.mass
        self.velocity += acceleration * dt

        # 5. Limitação da  velocidade na física
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_velocity:
            self.velocity = (self.velocity / speed) * self.max_velocity
                
        self.angular_velocity = np.clip(
            self.angular_velocity,
            -self.max_angular_velocity,
            self.max_angular_velocity
        )

        # 6. Atualiza posição e rotação
        self.position += self.velocity * dt
        self.angle += self.angular_velocity*dt

        # 7. Aplica amortecimento (atrito)
        self.velocity *= 0.99
        self.angular_velocity *= 0.95

        # 8. Sincroniza colisão
        self.sync_collision_object()

        # 9. Reseta acumuladores
        self.force.fill(0)
        self.torque = 0.0

    # Aplicar força contínua (pouco usada, mas disponível)
    def apply_force(self,force:np.ndarray, contact_point: np.ndarray=None):
        '''
            Aplica uma força contínua ao robô
        '''
        self.force += force
        if contact_point is not None:
            r = contact_point -self.position
            self.torque += np.cross(r,force)

    #Aplica impulso (usado em colisões)
    def apply_impulse(self, impulse: np.ndarray, contact_point: np.ndarray=None):
        """
        Aplica um impulso ao robô, modificando sua velocidade linear e angular.
        
        Args:
            impulse: Vetor impulso [ix, iy] em kg*cm/s

            contact_point: Ponto de contato onde o impulso é aplicado (em cm)
                        Se None, assume centro de massa
        """
        self.velocity += impulse /self.mass 
        # Calcula torque apenas se o ponto de contato for especificado
        if contact_point is not None:
            # Vetor do centro de massa ao ponto de contato
            r = np.array(contact_point) - np.array([self.x, self.y])
            
            # Atualiza velocidade angular
            self.angular_velocity += np.cross(r,impulse) / self.inertia

    def inertia_rectangle(self):
        self.inertia = (1/12)*self.mass*(self.width**2+self.height**2)

    def rotate(self, angle_rad: float):
        """Rotaciona o robô com limitação de velocidade angular"""
        self.angle += angle_rad
        self.sync_collision_object()

    def distance_to(self, x: float, y: float) -> float:
        """
        Calcula a distância até um ponto (x, y).

        :param x: Posição X do ponto.

        :param y: Posição Y do ponto.

        :return: Distância até o ponto.
        """
        return np.linalg.norm(np.array([self.x - x, self.y - y]))
    
    def reset(self):
        """Reseta o robô para o estado inicial"""
        self.position = self.initial_position.copy()
        self.angle = self.initial_angle
        self.direction = self.initial_direction.copy()
        self.wheels_speed = self.initial_wheels_speed.copy()
        self.velocity = self.initial_velocity.copy()
        self.angular_velocity = self.initial_angular_velocity
        self.force.fill(0)
        self.torque = 0.0
        self.image = self.initial_image
        self.sync_collision_object()

    def set_position(self, x, y):
        """
        Define a posição do robô.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        self.position = np.array([x, y], dtype=float)
        # Reseta apenas as variáveis de movimento, mantendo o estado inicial
        self.velocity = np.zeros(2, dtype=float)
        self.angular_velocity = 0.0
        self.wheels_speed = np.zeros(2, dtype=float)
        self.force.fill(0)
        self.torque = 0.0
        self.sync_collision_object()

    def new_position(self, x,y):
        """
        Define a posição do robô sem retornar a inicial, apenas muda o x e y
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        #nova posição do robô
        self.position = np.array([x, y], dtype=float)    

        self.sync_collision_object()

    def stop(self):
        """
        Para o robô (define a velocidade como zero).
        """
        self.wheels_speed.fill(0)
        self.velocity.fill(0)
        self.angular_velocity = 0.0

    def sync_collision_object(self):
        """
        Sincroniza a posição do objeto de colisão com a posição do robô.
        """
        self.collision_object.x = self.x 
        self.collision_object.y = self.y
        self.collision_object.angle = np.degrees(self.angle)

    def update_velocity_vector(self):
        """
        Atualiza a velocidade vetorial do robô com base nas velocidades das rodas e direção atual.
        """
        v = (self.v_r + self.v_l) / 2  # velocidade linear
        
        # Limita a velocidade máxima e ajusta as rodas proporcionalmente
        if abs(v) > self.max_velocity:
            ratio = self.max_velocity / abs(v)
            v = np.sign(v) * self.max_velocity
            self.v_l *= ratio
            self.v_r *= ratio
        
        self.velocity = v * self.direction

    def _draw_(self, screen):
        '''
        Nova função de desenho para o robô, que desenha a imagem do robô na tela
        :param screen: Superfície do pygame onde o robô será desenhado.
        '''
        # Converte coordenadas virtuais para coordenadas de tela

        # rotaciona corretamente a imagem do robô

        # Verifica se está selecionado pelo mouse 

        # Desenha no backbuffer do screen 
        pass 

    def draw(self, screen):
        """
        Desenha o robô na tela com rotação e um vetor indicando a direção.
        :param screen: Superfície do pygame onde o robô será desenhado.
        """

        # Converte o ângulo de rotação para graus
        angle = np.degrees(self.angle)

        # Rotaciona a imagem do robô conforme o ângulo atual
        rotated_image = pygame.transform.rotate(self.initial_image, angle)  # negativo pois y do Pygame cresce para baixo

        # Se o robô estiver selecionado, clareia apenas as cores da imagem
        if self._is_selected:
            # Cria uma cópia da imagem rotacionada
            selected_image = rotated_image.copy()
            width, height = selected_image.get_size()

            # Bloqueia a superfície para manipulação direta dos pixels
            selected_image.lock()
            for x in range(width):
                for y in range(height):
                    r, g, b, a = selected_image.get_at((x, y))  # Obtém a cor do pixel
                    if a > 0:  # Apenas pixels visíveis
                        # Clareia as cores (mantendo a transparência)
                        r = min(r + 100, 255)
                        g = min(g + 100, 255)
                        b = min(b + 100, 255)
                        selected_image.set_at((x, y), (r, g, b, a))
            selected_image.unlock()

            rotated_image = selected_image
        # Converte coordenadas virtuais para coordenadas de tela
        center = virtual_to_screen([self.x, self.y])

        # Centraliza a imagem no ponto do robô
        rect = rotated_image.get_rect(center=center)

        # Desenha a imagem rotacionada na tela
        screen.blit(rotated_image, rect.topleft)


import pygame
import numpy as np
from ui.interface_config import (
    ROBOT_SIZE_CM,
    ROBOT_WHEELS_RADIUS_CM,
    ROBOT_DISTANCE_WHEELS_CM,
    ROBOT_DISTANCE_WHEELS_TO_CENTER_CM,
    ROBOT_MASS,
    SCALE_PX_TO_CM,
)
from simulator.collision.collision import *
from simulator.intelligence.controll import *

class Robot:
    '''
        Implementação dinâmica de um robô controlado por controle diferencial
    '''
    def __init__(self, x, y, team, role, id, image, initial_angle=0):
        '''
            Inicializando o objeto robô que será um objeto que irá se mover e interagir na simulação
        '''
        #Coordenadas globais do robô no ambiente
        self._position=np.array([x,y], dtype=float)
        self.previous_position = np.array([0.0,0.0],dtype=float)    #Posição anterior para aplicar o crossing

        ''' Angulo theta com a horizontal em radianos'''
        self.team = team                        # indicação do time
        self.role = role                        # função do robô
        self.id_robot = id                      # Apenas um identificado para ele
        self.image    = image                   # Imagem que representa o robô7
        self.initial_image = image              # Imagem inicial para quando resetar o robô.
        
        # Tipo de objeto para o sistema de colisão
        self.type_object = ROBOT_OBJECT

        # Tamanhos básicos do robô
        self.width = ROBOT_SIZE_CM
        self.height = ROBOT_SIZE_CM
        self.wheels_radius = ROBOT_WHEELS_RADIUS_CM
        self.distance_wheels = ROBOT_DISTANCE_WHEELS_CM
        self.distance_wheels_to_center = ROBOT_DISTANCE_WHEELS_TO_CENTER_CM

        # propriedades dinâmicas aplicadas no robô
        self.mass = ROBOT_MASS
        self.inertia = (1/12) * self.mass * (self.width**2 + self.height**2) #retângulo
        self.size = np.array([self.width, self.height])

        # Inicialização de variáveis físicas
        self.force = np.zeros(2, dtype=float)
        self.torque = 0.0
        self.impulse = None
        self.angle = np.radians(initial_angle)  # Ângulo em radianos do eixo de rotação do robô com o eixo x do sistema cartesiano inicial
        
        # Velocidades separadas
        self.control_velocity = np.array([0.0, 0.0],dtype=float)    # da cinemática
        self.physical_velocity = np.array([0.0, 0.0],dtype=float)   # da física
        self.velocity = np.array([0.0, 0.0],dtype=float)             # final (composta)

        self.control_angular_velocity = 0.0
        self.angular_velocity = 0.0     # Velocidade angular
        
        # Vetor de direção inicial
        self.direction = np.array([np.cos(self.angle), np.sin(self.angle)],dtype=float)

        # Velocidades das rodas (em cm/s)
        self.v_l = 0.0  # esquerda
        self.v_r = 0.0  # direita

        # Velocidade linear e angular (no sentido)
        self.v = 0.0
        self.omega = 0.0

        # Colisão
        self.collision_object = CollisionRectangle(
            self.x, self.y, self.width, self.height, 
            type_object=MOVING_OBJECTS, reference=self)
        self.sync_collision_object()


        #salva os valores iniciais para quando resetar
        self.initial_theta      = self.angle
        self.initial_vl         = self.v_l
        self.initial_vr         = self.v_r 
        self.initial_direction  = self.direction.copy()
        self.initial_v          = self.v 
        self.initial_omega      = self.omega
        self.initial_x          = self.x 
        self.initial_y          = self.y
        self.initial_angular_velocity = self.angular_velocity

        # Controlador PID para o robô
        self.kp = 2.0
        self.ki = 0.1
        self.kd = 0.2

        # Objetos de controle PID do robô
        # PID para 
        self.pid_linear = PIDController(self.kp,self.ki,self.kd)

        # PID para
        self.pid_angular = PIDController(self.kp,self.ki,self.kd)

        # PID para
        self.pid_orientation = PIDController(self.kp,self.ki,self.kd)

    @property
    def position(self):
        return self._position
    
    @position.setter 
    def position(self, value):
        self._position =np.array(value,dtype=float)
        self.collision_object.x = self._position[0]
        self.collision_object.y = self._position[1]

    @property
    def x(self):
        return self.position[0]

    @x.setter
    def x(self, value):
        self.position[0] = value
        self.collision_object.x =value

    @property
    def y(self):
        return self.position[1]

    @y.setter
    def y(self, value):
        self.position[1] = value
        self.collision_object.y =value

    # Método para enviar os valores de KP, Kd e Ki
    def set_controll_const(self,kp,kd,ki):
        # Atualizando constantes
        self.kp = kp 
        self.kd = kd 
        self.ki = ki 
        
        # Atualizando controladores PID
        self.pid_linear = PIDController(self.kp,self.ki,self.kd)
        self.pid_heading = PIDController(self.kp,self.ki,self.kd)
        self.pid_orientation = PIDController(self.kp,self.ki,self.kd)


    def go_to_point(self, target_pos, target_angle, dt):
        pos_error = target_pos - self.position
        distance = np.linalg.norm(pos_error)

        angle_to_target = np.arctan2(pos_error[1], pos_error[0])

        # Erros se for de frente ou de ré
        error_front = self.normalize_angle(angle_to_target - self.angle)
        error_back = self.normalize_angle(angle_to_target + np.pi - self.angle)

        # Decidir direção com menor esforço angular
        if abs(error_back) < abs(error_front):
            forward = False
            heading_error = error_back
            distance *= -1  # vai de ré
        else:
            forward = True
            heading_error = error_front

        # Ângulo final desejado (considerando reverso também)
        angle_error = self.normalize_angle(target_angle - self.angle)

        # Controladores
        v = self.pid_linear.compute(distance, dt)
        w = self.pid_angular.compute(heading_error + angle_error, dt)

        # Velocidades das rodas
        v_l = v - (w * self.distance_wheels / 2)
        v_r = v + (w * self.distance_wheels / 2)

        return v_l, v_r


    def normalize_angle(self, angle):
        """
        Normaliza ângulos para o intervalo [-π, π]
        """
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    #setando velocidade das rodas
    def set_wheel_speeds(self, v_l, v_r):
        """Define as velocidades das rodas esquerda e direita (em cm/s)."""
        self.v_l = v_l
        self.v_r = v_r

        #Atualizo a velocidade atual
        self.update_velocity_vector()

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
    def set_vec_velocity(self, vx,vy):
        """
        Define as velocidades das rodas com base em um vetor velocidade (global).
        """
        v_global = np.array([vx, vy], dtype=float)
        self.direction = np.array([np.cos(self.angle), np.sin(self.angle)])

        v = np.dot(v_global, self.direction)  # componente tangencial
        omega = 0.0

        self.v = v
        self.omega = omega

        self.v_l = v - (omega * self.distance_wheels / 2)
        self.v_r = v + (omega * self.distance_wheels / 2)

        self.velocity = v_global
        self.sync_collision_object()

    def move(self, dt: float):
        #Salvando posição anterior:
        self.previous_position = self.position.copy()
        # 1. Força das rodas
        left_force = self.v_l * self.mass
        right_force = self.v_r * self.mass
        force_magnitude = (left_force + right_force) / 2
        direction_force = self.direction * force_magnitude

        # 2. Acumula força e torque do controle
        self.force += direction_force
        self.torque += (right_force - left_force) * self.distance_wheels / 2

        # 3. Integra aceleração linear e angular
        acceleration = self.force / self.mass
        self.velocity += acceleration * dt
        self.angular_velocity += (self.torque / self.inertia) * dt

        # 4. Atualiza posição e rotação
        self.position += self.velocity * dt
        self.angle += self.angular_velocity * dt
        self.angle %= 2 * np.pi

        # 5. Atualiza direção
        self.direction = np.array([np.cos(self.angle), np.sin(self.angle)], dtype=float)

        # 6. Damping realista (simula atrito com o solo)
        linear_damping = 0.01
        angular_damping = 0.05
        self.velocity *= (1 - linear_damping)
        self.angular_velocity *= (1 - angular_damping)

        # 7. Sincroniza colisão
        self.sync_collision_object()

        # 8. Reseta acumuladores
        self.force[:] = 0
        self.torque = 0.0


    # Aplicar força contínua (pouco usada, mas disponível)
    def apply_force(self,force, contact_vector):
        '''
            Aplica uma força contínua ao robô
        '''
        self.force += force
        torque = np.cross(contact_vector, force)
        self.torque +=torque
    
    def apply_torque(self, torque):
        '''
            Aplica um torque contínuo ao robô
        '''
        self.torque += torque 

    #Aplica impulso (usado em colisões)
    def apply_impulse(self, impulse, contact_point=None):
        """
        Aplica um impulso ao robô, modificando sua velocidade linear e angular.
        
        Args:
            impulse: Vetor impulso [ix, iy] em kg*cm/s
            contact_point: Ponto de contato onde o impulso é aplicado (em cm)
                        Se None, assume centro de massa
        """
        # Atualiza velocidade linear
        self.physical_velocity += impulse / self.mass
        
        # Calcula torque apenas se o ponto de contato for especificado
        if contact_point is not None:
            # Vetor do centro de massa ao ponto de contato
            r = np.array(contact_point) - np.array([self.x, self.y])
            
            # Cálculo CORRETO do torque usando produto vetorial 2D
            # τ = r × impulse = r_x * impulse_y - r_y * impulse_x
            torque_impulse = r[0] * impulse[1] - r[1] * impulse[0]
            
            # Atualiza velocidade angular
            self.angular_velocity += torque_impulse / self.inertia

    def inertia_rectangle(self):
        self.inertia = (1/12)*self.mass*(self.width**2+self.height**2)

    def rotate(self, angle):
        """
        Rotaciona o robô em torno de seu centro.
        :param angle: Ângulo em graus para rotacionar.
        """
        self.angle += np.radians(angle)
        self.direction = np.array([np.cos(self.angle), np.sin(self.angle)])
        self.sync_collision_object()

    def distance_to(self, x, y):
        """
        Calcula a distância até um ponto (x, y).
        :param x: Posição X do ponto.
        :param y: Posição Y do ponto.
        :return: Distância até o ponto.
        """
        return np.linalg.norm(np.array([self.x - x, self.y - y]))
    
    def reset(self):
        """
        Reseta a posição do robô para as coordenadas fornecidas.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        #Reseta configurações do robô
        self.angle      = self.initial_theta  #Ângulo theta com a horizontal
        self.v_l        = self.initial_vl         
        self.v_r        = self.initial_vr          
        self.direction  = self.initial_direction  
        self.v          = self.initial_v          
        self.omega      = self.initial_omega   
        self.position = np.array([self.initial_x, self.initial_y], dtype=float)    
        self.velocity   = np.zeros(2, dtype=float)
        self.angular_velocity = self.initial_angular_velocity
        self.force          =np.zeros(2)
        self.torque         = 0.0

        # Imagem para o Pygame
        self.image = self.initial_image 
        
        self.sync_collision_object()

    def set_position(self, x, y):
        """
        Define a posição do robô.
        :param x: Nova posição X.
        :param y: Nova posição Y.
        """
        #nova posição do robô
        self.position = np.array([x, y], dtype=float)    

        #Zero variáveis dinâmicas do robô
        self.angle      = self.initial_theta  #Ângulo theta com a horizontal
        self.v_l        = self.initial_vl         
        self.v_r        = self.initial_vr          
        self.direction  = self.initial_direction  
        self.v          = self.initial_v          
        self.omega      = self.initial_omega   
        self.velocity   = np.zeros(2, dtype=float)
        self.angular_velocity = self.initial_angular_velocity

        self.sync_collision_object()

    def stop(self):
        """
        Para o robô (define a velocidade como zero).
        """
        self.v_l = 0.0
        self.v_r = 0.0

    def sync_collision_object(self):
        """
        Sincroniza a posição do objeto de colisão com a posição do robô.
        """
        angle= np.degrees(np.arctan2(self.direction[1], self.direction[0]))
        self.collision_object.angle = angle

    def update_velocity_vector(self):
        """
        Atualiza a velocidade vetorial do robô com base nas velocidades das rodas e direção atual.
        """
        v = (self.v_r + self.v_l) / 2  # velocidade linear
        self.velocity = v * self.direction  # vetor velocidade

    def draw(self, screen):
        """
        Desenha o robô na tela com rotação e um vetor indicando a direção.
        :param screen: Superfície do pygame onde o robô será desenhado.
        """

        # Converte o ângulo de rotação para graus
        angle = np.degrees(self.angle)

        # Rotaciona a imagem do robô conforme o ângulo atual
        rotated_image = pygame.transform.rotate(self.image, angle)  # negativo pois y do Pygame cresce para baixo

        # Converte coordenadas virtuais para coordenadas de tela
        center = virtual_to_screen([self.x, self.y])

        # Centraliza a imagem no ponto do robô
        rect = rotated_image.get_rect(center=center)

        # Desenha a imagem rotacionada na tela
        screen.blit(rotated_image, rect.topleft)


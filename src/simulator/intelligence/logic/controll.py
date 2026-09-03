import numpy as np

class PIDController:
    def __init__(self, kp, ki, kd, output_limits=(None, None)):
        """
        Inicializa o controlador PID com ganhos e limites de saída.

        - kp, ki, kd: ganhos proporcional, integral e derivativo.
        - output_limits: tupla (min, max) para limitar a saída do controlador.
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_output, self.max_output = output_limits

        self.integral = 0.0
        self.prev_error = 0.0

    def compute(self, error, dt):
        """
        Calcula a saída PID baseado no erro atual e no tempo decorrido (dt).
        """
        if dt <= 0.0:
            return 0.0  # evita divisão por zero e comportamento instável

        # Proporcional
        p = self.kp * error

        # Integral com acumulação simples
        self.integral += error * dt
        i = self.ki * self.integral

        # Derivativo com diferença de erro (forma simples e rápida)
        d = self.kd * (error - self.prev_error) / dt

        # Armazena erro atual para próxima iteração
        self.prev_error = error

        # Soma PID
        output = p + i + d

        # Saturação (limita a saída para não ultrapassar valores físicos do robô)
        if self.min_output is not None:
            output = max(self.min_output, output)
        if self.max_output is not None:
            output = min(self.max_output, output)

        return output
    
    def set_new_consts(self,kp, ki, kd):
        '''
            Atualizo as novas constantes para o controlador PID
        '''
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.reset()
    
    def reset(self):
        '''
            Reseta os erros acumulados
        '''
        self.integral = 0.0
        self.prev_error = 0.0 


<<<<<<< HEAD
# Estratégias de controle por arvore das decisões para cada robô
=======
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
>>>>>>> pygame

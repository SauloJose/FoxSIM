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
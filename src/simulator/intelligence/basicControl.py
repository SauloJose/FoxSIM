import numpy as np

def go_to_point(obj, target_pos, target_angle, dt):
    is_finish = False 
    # Erro de posição
    pos_error = target_pos - obj.position
    distance = np.linalg.norm(pos_error)

    # Ângulo até o destino
    angle_to_target = np.arctan2(pos_error[1], pos_error[0])
    heading_error = obj.normalize_angle(angle_to_target - obj.angle)

    # Erro angular final (para o ângulo desejado ao chegar no ponto)
    final_angle_error = obj.normalize_angle(target_angle - obj.angle)

    # Parâmetros de controle
    DIST_TOL = 0.2                # Tolerância de distância [cm]
    ANGLE_TOL = np.deg2rad(20.0)   # Tolerância angular final [rad]
    MAX_SPEED = 50.0             # Velocidade linear máxima
    MIN_SPEED = 20.0              # Velocidade linear mínima (anti-stall)
    TRANSITION_ZONE = 1.0         # Zona de transição para alinhamento [cm]

    if distance > DIST_TOL:
        # Aproximação do ponto
        v = obj.pid_linear.compute(distance, dt)
        w = obj.pid_heading.compute(heading_error, dt)

        # Mistura de orientação para transição ao alvo
        if distance < TRANSITION_ZONE:
            alpha = distance / TRANSITION_ZONE
            w_final = obj.pid_angular.compute(final_angle_error, dt)
            w = alpha * w + (1 - alpha) * w_final
    else:
        # Alinhamento final
        obj.pid_linear.reset()
        v = 0.0
        w = obj.pid_angular.compute(final_angle_error, dt)

        # Se já está alinhado, para tudo
        if abs(final_angle_error) < ANGLE_TOL:
            obj.pid_angular.reset()
            w = 0.0

    # Saturação da velocidade linear
    v = np.clip(v, 0.0, MAX_SPEED)  # v nunca será negativo

    # Cálculo das velocidades das rodas
    v_l = v - (w * obj.distance_wheels / 2)
    v_r = v + (w * obj.distance_wheels / 2)
    
    if v_l == 0 and v_r == 0:
        is_finish = True
    return v_l, v_r, is_finish


def walk_for_points(obj, list_points, dt):
    '''
    Função que faz o robô andar por uma lista de pontos, um de cada vez utilizando a função go_to_point para cada ponto.
    '''
    for point in list_points:
        while is_finish == False:
            v_l, v_r, is_finish = go_to_point(obj, point[0], point[1], dt)
            obj.step(v_l, v_r, dt)

    
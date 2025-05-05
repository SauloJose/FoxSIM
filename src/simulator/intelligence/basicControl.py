import numpy as np

def go_to_point(obj, target_pos, target_angle, dt):
    pos_error = target_pos - obj.position
    distance = np.linalg.norm(pos_error)

    # Ângulo até o ponto destino
    angle_to_target = np.arctan2(pos_error[1], pos_error[0])

    # Escolher entre ir de frente ou de ré
    error_front = obj.normalize_angle(angle_to_target - obj.angle)
    error_back = obj.normalize_angle(angle_to_target + np.pi - obj.angle)

    # Decide se vai de frente ou de ré
    if abs(error_back) < abs(error_front):
        heading_error = error_back
        distance *= -1  # Inverter sinal da distância
        going_backwards = True
    else:
        heading_error = error_front
        going_backwards = False

    # Erro de orientação final
    angle_error = obj.normalize_angle(target_angle - obj.angle)

    # --- Parâmetros ---
    DIST_TOLERANCE = 8.0  # cm
    ANGLE_TOLERANCE = np.deg2rad(5.0)  # ~5 graus
    MAX_SPEED = 100  # cm/s

    # --- Controle PID ---
    if abs(distance) > DIST_TOLERANCE:
        # Vai até o ponto (com ajuste de orientação básica)
        v = obj.pid_linear.compute(distance, dt)
        w = obj.pid_heading.compute(heading_error, dt)
    else:
        # Está no ponto → alinha orientação final
        v = 0
        w = 0

    # Clipping
    v = np.clip(v, -MAX_SPEED, MAX_SPEED)

    # Conversão para velocidades das rodas
    v_l = v - (w * obj.distance_wheels / 2)
    v_r = v + (w * obj.distance_wheels / 2)

    return v_l, v_r


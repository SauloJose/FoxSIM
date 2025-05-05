import numpy as np
from simulator.intelligence.logic.controll import PIDController

def go_to_point(obj, target_pos, target_angle, dt):
    pos_error = target_pos - obj.position
    distance = np.linalg.norm(pos_error)

    angle_to_target = np.arctan2(pos_error[1], pos_error[0])

    # Erros se for de frente ou de ré
    error_front = obj.normalize_angle(angle_to_target - obj.angle)
    error_back = obj.normalize_angle(angle_to_target + np.pi - obj.angle)

    # Decidir direção com menor esforço angular
    if abs(error_back) < abs(error_front):
        heading_error = error_back
        distance *= -1  # vai de ré
    else:
        heading_error = error_front

    # Ângulo final desejado (considerando reverso também)
    angle_error = obj.normalize_angle(target_angle - obj.angle)

    # --- Parada inteligente ---
    LIMIAR_DIST = 7.0  # cm
    LIMIAR_ANG = np.deg2rad(30.0)  # 5 graus
    MAX_SPEED = 100  # cm/s

    # Controle PID sempre atuando
    v = obj.pid_linear.compute(distance, dt)
    w = obj.pid_heading.compute(heading_error, dt) + obj.pid_angular.compute(angle_error, dt)

    # Limita a velocidade linear máxima
    v = np.clip(v, -MAX_SPEED, MAX_SPEED)

    # Se chegou suficientemente perto, para completamente
    if abs(distance) < LIMIAR_DIST and abs(angle_error) < LIMIAR_ANG:
        v = 0
        w = 0

    v_l = v - (w * obj.distance_wheels / 2)
    v_r = v + (w * obj.distance_wheels / 2)

    return v_l, v_r
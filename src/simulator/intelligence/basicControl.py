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


def walk_for_points(obj, list_points, dt, max_steps_per_point=1000, tolerance_dist=0.2, tolerance_angle=np.deg2rad(20)):
    """
    Faz o robô navegar por uma lista de pontos sequencialmente usando o controle PID.
    
    Parâmetros:
    - obj: Instância do robô (SimBot)
    - list_points: Lista de waypoints no formato [(x1, y1, ang1), (x2, y2, ang2), ...]
    - dt: Passo de tempo para a simulação
    - max_steps_per_point: Máximo de iterações por waypoint (evita loops infinitos)
    - tolerance_dist: Tolerância de distância para considerar chegada (em cm)
    - tolerance_angle: Tolerância angular para considerar alinhamento (em rad)
    
    Retorno:
    - True se todos os pontos foram alcançados, False se interrompido
    """
    for x_target, y_target, ang_target_deg in list_points:
        ang_target = np.deg2rad(ang_target_deg)
        target_pos = np.array([x_target, y_target])
        steps = 0
        is_finished = False
        
        while not is_finished and steps < max_steps_per_point:
            # Cálculo dos erros
            pos_error = target_pos - obj.position
            distance = np.linalg.norm(pos_error)
            angle_to_target = np.arctan2(pos_error[1], pos_error[0])  # Ângulo até o alvo
            heading_error = obj.normalize_angle(angle_to_target - obj.angle)  # Erro de direção
            final_angle_error = obj.normalize_angle(ang_target - obj.angle)  # Erro de ângulo final
            
            print(f"Step {steps}: Distance Error = {distance:.2f}, Heading Error = {heading_error:.2f}, Final Angle Error = {final_angle_error:.2f}")

            # Salva os erros no objeto
            obj.distance_errors.append(distance)
            obj.heading_errors.append(heading_error)  # Agora usando a variável correta
            obj.final_angle_errors.append(final_angle_error)
            
            # Verifica critérios de parada
            if distance <= tolerance_dist and abs(final_angle_error) <= tolerance_angle:
                is_finished = True
                break
                
            # Executa um passo de controle
            v_l, v_r, _ = obj.goto_point(target_pos, ang_target, dt)
            obj.set_wheel_speed(v_l, v_r)
            obj.move(dt)
            
            steps += 1
            
            # Permite interrupção externa (opcional)
            if hasattr(obj, 'break_flag') and obj.break_flag:
                return False
            
    return True
    
import numpy as np
import random

class ERRTPlanner:
    def __init__(self, field_width=150.0, field_height=130.0):
        self.step_size = 15.0      
        self.max_iter = 50         # Reduzido para 50 para garantir 60fps constantes no Pygame
        self.goal_bias = 0.3       
        self.waypoint_bias = 0.4   
        self.field_bounds = (field_width, field_height)
        self.cached_path = []

    def _dist_to_segment(self, p, a, b):
        l2 = np.sum((a - b)**2)
        if l2 == 0: return np.linalg.norm(p - a)
        t = max(0, min(1, np.dot(p - a, b - a) / l2))
        proj = a + t * (b - a)
        return np.linalg.norm(p - proj)

    def is_collision_free(self, p1, p2, obstacles, safety_radius=12.0):
        for obs in obstacles:
            if self._dist_to_segment(obs, p1, p2) < safety_radius:
                return False
        return True

    def plan(self, start, goal, obstacles):
        tree = [start]
        parents = [0]
        
        for _ in range(self.max_iter):
            r = random.random()
            if r < self.goal_bias:
                q_rand = goal
            elif r < self.goal_bias + self.waypoint_bias and len(self.cached_path) > 0:
                q_rand = random.choice(self.cached_path)
            else:
                q_rand = np.array([random.uniform(0, self.field_bounds[0]),
                                   random.uniform(0, self.field_bounds[1])])
            
            distances = [np.linalg.norm(node - q_rand) for node in tree]
            nearest_idx = np.argmin(distances)
            q_near = tree[nearest_idx]
            
            dir_vec = q_rand - q_near
            dist = np.linalg.norm(dir_vec)
            if dist > self.step_size:
                q_new = q_near + (dir_vec / dist) * self.step_size
            else:
                q_new = q_rand

            if self.is_collision_free(q_near, q_new, obstacles):
                tree.append(q_new)
                parents.append(nearest_idx)
                
                if np.linalg.norm(q_new - goal) <= self.step_size:
                    if self.is_collision_free(q_new, goal, obstacles):
                        tree.append(goal)
                        # ==========================================================
                        # CORREÇÃO DO LOOP INFINITO AQUI:
                        # O pai do 'goal' é o 'q_new', que está no índice len(tree) - 2.
                        # ==========================================================
                        parents.append(len(tree) - 2) 
                        
                        path = []
                        curr_idx = len(tree) - 1
                        
                        # Limite de segurança adicionado no while para nunca travar o Pygame
                        safety_counter = 0 
                        while curr_idx != 0 and safety_counter < 1000:
                            path.append(tree[curr_idx])
                            curr_idx = parents[curr_idx]
                            safety_counter += 1
                            
                        path.reverse()
                        
                        self.cached_path = path 
                        return path
                        
        return self.cached_path if len(self.cached_path) > 0 else [goal]
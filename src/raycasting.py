import trimesh
import numpy as np
import os

class UrbanRaycaster:
    def __init__(self, obj_path):
        print(f"[Raycaster] Carregando mapa 3D de: {obj_path}...")
        
        # Carrega a malha. O trimesh cria automaticamente uma árvore BVH 
        # (Bounding Volume Hierarchy) para deixar o raycasting rápido.
        self.mesh = trimesh.load(obj_path, force='mesh')
        print(f"[Raycaster] Mapa carregado. {len(self.mesh.faces)} faces.")

    def check_los(self, origin, destination):
        """
        Verifica Line-of-Sight (LOS) entre dois pontos (x,y,z).
        Retorna: True (Livre/LOS) ou False (Obstruído/NLOS)
        """
        # Vetor direção
        direction = destination - origin
        distance = np.linalg.norm(direction)
        
        if distance < 0.1:
            return True # Mesma posição
            
        direction_norm = direction / distance

        # Lança o raio
        # ray_intersects_location retorna (pontos, index_raio, index_face)
        intersects = self.mesh.ray.intersects_location(
            ray_origins=[origin],
            ray_directions=[direction_norm]
        )[0]

        if len(intersects) == 0:
            return True # Nenhuma colisão -> LOS

        # Verifica se a colisão aconteceu ANTES de chegar no destino
        # (Às vezes o raio acerta algo atrás do alvo, o que não importa)
        for point in intersects:
            dist_collision = np.linalg.norm(point - origin)
            if dist_collision < (distance - 0.5): # Margem de erro de 0.5m
                return False # Colidiu antes de chegar -> NLOS

        return True
import numpy as np
import pymap3d as pm

# Origem definida no seu curitiba.sdf (Reference Point)
REF_LAT = -25.43721
REF_LON = -49.26599
REF_ALT = 934.0  # Altitude base de Curitiba

def geo_to_local(lat, lon, alt):
    """
    Converte coordenadas GPS (WGS84) para coordenadas locais (ENU)
    que batem com o modelo 3D no Gazebo.
    """
    x, y, z = pm.geodetic2enu(lat, lon, alt, REF_LAT, REF_LON, REF_ALT)
    return np.array([x, y, z])

def get_distance(p1, p2):
    """Distância Euclidiana simples em metros."""
    return np.linalg.norm(p1 - p2)
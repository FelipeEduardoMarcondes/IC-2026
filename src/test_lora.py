import os
import sys
import numpy as np

# Garante que consegue importar os módulos da mesma pasta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import geo_to_local, get_distance
from raycasting import UrbanRaycaster
from propagation import LoraChannel

# --- CONFIGURAÇÃO ---
# Ajuste este caminho se der erro de "File not found"
# Estamos assumindo que você roda de dentro de /src/
ASSET_PATH = "../assets/mapa_curitiba/meshes/mapa_curitiba.obj"

def run_test():
    # 1. Carrega o Mapa (Pode demorar uns segundos na primeira vez)
    if not os.path.exists(ASSET_PATH):
        print(f"ERRO CRÍTICO: Não achei o arquivo .obj em: {ASSET_PATH}")
        return

    print("Inicializando Raycaster...")
    env = UrbanRaycaster(ASSET_PATH)
    
    # 2. Configura o Rádio (Tx 20dBm = 100mW)
    radio = LoraChannel(tx_power_dbm=20)

    # --- CENÁRIO 1: VISADA DIRETA (LOS) ---
    # Simulando drone bem alto acima da praça
    print("\n--- TESTE 1: Alta Altitude (Esperado: LOS) ---")
    gw_pos = geo_to_local(-25.43721, -49.26599, 935.0) # Chão
    uav_pos = geo_to_local(-25.43721, -49.26599, 1000.0) # 65m de altura
    
    dist = get_distance(gw_pos, uav_pos)
    is_los = env.check_los(gw_pos, uav_pos)
    rssi = radio.calculate_rssi(dist, is_los)
    
    print(f"Distância: {dist:.2f}m")
    print(f"Status: {'LIVRE (LOS)' if is_los else 'BLOQUEADO (NLOS)'}")
    print(f"RSSI: {rssi} dBm")

    # --- CENÁRIO 2: BLOQUEIO (NLOS) ---
    # Simulando drone atrás de um prédio (ajuste as coordenadas se necessário para testar)
    # Vamos mover o drone para longe no horizonte baixo
    print("\n--- TESTE 2: Bloqueio Urbano (Esperado: NLOS) ---")
    uav_pos_bloq = geo_to_local(-25.43900, -49.26800, 940.0) # Longe e baixo
    
    dist = get_distance(gw_pos, uav_pos_bloq)
    is_los = env.check_los(gw_pos, uav_pos_bloq)
    rssi = radio.calculate_rssi(dist, is_los)
    
    print(f"Distância: {dist:.2f}m")
    print(f"Status: {'LIVRE (LOS)' if is_los else 'BLOQUEADO (NLOS)'}")
    print(f"RSSI: {rssi} dBm")
    print("------------------------------------------------")

if __name__ == "__main__":
    run_test()
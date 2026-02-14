import asyncio
import csv
import os
import datetime
import signal
from mavsdk import System
from utils import geo_to_local, get_distance
from raycasting import UrbanRaycaster
from propagation import LoraChannel

# --- CONFIGURAÇÕES ---
ASSET_PATH = "../assets/mapa_curitiba/meshes/mapa_curitiba.obj"
LOG_DIR = "../logs"
GATEWAY_POS = (-25.43721, -49.26599, 935.0) # Gateway fixo (Praça)

# Variável para controlar o loop de gravação
is_running = True

def signal_handler(sig, frame):
    global is_running
    print("\n[Logger] Parando gravação...")
    is_running = False

async def run():
    # Registra Ctrl+C para parar graciosamente
    signal.signal(signal.SIGINT, signal_handler)

    # 1. Carrega Raycasting
    print("[Logger] Carregando mapa 3D (pode demorar)...")
    env = UrbanRaycaster(ASSET_PATH)
    radio = LoraChannel(tx_power_dbm=20)
    
    # 2. Prepara CSV
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{LOG_DIR}/manual_flight_{timestamp}.csv"
    
    # Abrimos o arquivo
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "lat", "lon", "alt", "dist_m", "los", "rssi_dbm", "pdr_success"])
        
        # 3. Conecta no Drone (Apenas escuta)
        drone = System()
        print("[Logger] Aguardando PX4 (Abra o Gazebo)...")
        await drone.connect(system_address="udp://:14540")

        # Espera conectar
        async for state in drone.core.connection_state():
            if state.is_connected:
                print(f"[Logger] CONECTADO! Pode voar com o QGroundControl.")
                break
        
        # 4. Loop de Gravação
        print(f"[Logger] Gravando dados em: {filename}")
        print("[Logger] Pressione Ctrl+C para salvar e sair.")
        
        # Definimos a posição do Gateway localmente uma vez
        gw_local = geo_to_local(*GATEWAY_POS)

        async for position in drone.telemetry.position():
            if not is_running:
                break
            
            # Converte posição do drone
            uav_local = geo_to_local(position.latitude_deg, position.longitude_deg, position.absolute_altitude_m)
            
            # Cálculos Matemáticos
            dist = get_distance(gw_local, uav_local)
            is_los = env.check_los(gw_local, uav_local)
            rssi = radio.calculate_rssi(dist, is_los)
            success = radio.packet_received(rssi)

            # Feedback Visual no Terminal
            status_los = "LIVRE" if is_los else "BLOQUEADO"
            print(f"Lat: {position.latitude_deg:.6f} | Lon: {position.longitude_deg:.6f} | Alt: {position.absolute_altitude_m:.1f} | Dist: {dist:.1f}m")

            # Salva no CSV
            writer.writerow([
                datetime.datetime.now(),
                position.latitude_deg,
                position.longitude_deg,
                position.absolute_altitude_m,
                dist,
                is_los,
                rssi,
                success
            ])
            
            # Limita taxa de amostragem (2Hz = 0.5s)
            # Se quiser mais resolução, diminua para 0.1
            await asyncio.sleep(0.5)

    print("[Logger] Arquivo salvo e fechado. Fim.")

if __name__ == "__main__":
    asyncio.run(run())
import asyncio
import csv
import os
import datetime
from mavsdk import System
from utils import geo_to_local, get_distance
from raycasting import UrbanRaycaster
from propagation import LoraChannel

# --- CONFIGURAÇÕES ---
ASSET_PATH = "../assets/mapa_curitiba/meshes/mapa_curitiba.obj"
LOG_DIR = "../logs"
GATEWAY_POS = (-25.43721, -49.26599, 935.0) # Gateway fixo no chão

async def run():
    # 1. Inicializa Infraestrutura
    print("[Main] Carregando ambiente 3D...")
    env = UrbanRaycaster(ASSET_PATH)
    radio = LoraChannel(tx_power_dbm=20)
    
    # Prepara CSV
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    filename = f"{LOG_DIR}/flight_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_file = open(filename, 'w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(["timestamp", "lat", "lon", "alt", "dist_m", "los", "rssi_dbm", "pdr_success"])
    
    # 2. Conecta no Drone
    drone = System()
    print("[Main] Procurando drone (PX4)...")
    await drone.connect(system_address="udp://:14540")

    print("[Main] Aguardando conexão...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"[Main] Drone conectado!")
            break

    # 3. Tarefa de Telemetria e Cálculo de RF (Roda em paralelo)
    asyncio.ensure_future(telemetry_loop(drone, env, radio, writer, GATEWAY_POS))

    # 4. Missão de Voo Simples (Decolar e ir para longe)
    print("[Main] Armando e Decolando...")
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(10) # Espera subir

    print("[Main] Iniciando movimento para provocar oclusão...")
    # Voa para uma coordenada que sabemos que vai ficar atrás de prédio (baseado no seu teste)
    # Ajuste estas coordenadas conforme necessário
    await drone.action.goto_location(-25.43900, -49.26800, 1950.0, 0)
    
    # Voa por 60 segundos gravando dados
    await asyncio.sleep(60)

    print("[Main] Retornando para casa...")
    await drone.action.return_to_launch()
    csv_file.close()

async def telemetry_loop(drone, env, radio, writer, gw_geo):
    """
    Captura posição, calcula LoRa e salva no CSV a cada 0.5s
    """
    gw_local = geo_to_local(*gw_geo)

    async for position in drone.telemetry.position():
        # Converte posição do drone
        uav_local = geo_to_local(position.latitude_deg, position.longitude_deg, position.absolute_altitude_m)
        
        # Cálculos
        dist = get_distance(gw_local, uav_local)
        is_los = env.check_los(gw_local, uav_local)
        rssi = radio.calculate_rssi(dist, is_los)
        success = radio.packet_received(rssi)

        # Log
        print(f"Dist: {dist:.1f}m | LOS: {is_los} | RSSI: {rssi} dBm")
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
        
        # Limita a taxa de atualização para não inundar o log
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
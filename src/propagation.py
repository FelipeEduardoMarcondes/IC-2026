import numpy as np

class LoraChannel:
    def __init__(self, tx_power_dbm=14, freq_mhz=915):
        self.tx_power = tx_power_dbm
        self.n_los = 2.4      # Expoente Path Loss (Visada direta)
        self.n_nlos = 3.5     # Expoente Path Loss (Obstruído)
        self.pl_0 = 31.5      # Perda de referência a 1m (Calibrar depois!)
        self.std_dev = 6.0    # Desvio padrão do Shadowing (dB)
        self.sensi = -120     # Sensibilidade do receptor LoRa (SF12)

    def calculate_rssi(self, distance, is_los):
        """
        Calcula o RSSI baseado no modelo Log-Distance + Shadowing.
        """
        if distance <= 1:
            return self.tx_power - self.pl_0

        # 1. Escolhe o expoente baseando-se no Raycasting
        n = self.n_los if is_los else self.n_nlos
        
        # 2. Path Loss Logarítmico
        path_loss = self.pl_0 + (10 * n * np.log10(distance))

        # 3. Penalidade Adicional por Obstáculo (Difração simplificada)
        # Se for NLOS, adicionamos uma "parede virtual" de perda extra
        obstacle_loss = 0 if is_los else 15.0  # dB (Calibrar com dados reais)

        # 4. Shadowing (Componente Estocástico/Aleatório)
        # Distribuição Normal (Gaussiana)
        shadowing = np.random.normal(0, self.std_dev)

        # Equação do Link Budget
        rssi = self.tx_power - path_loss - obstacle_loss + shadowing
        
        return round(rssi, 2)

    def packet_received(self, rssi):
        """Modelo binário simples de recepção"""
        return rssi >= self.sensi
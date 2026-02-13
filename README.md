# Digital Twin Curitiba: Simulação de Rede LoRa Mesh com UAVs

Este repositório contém a lógica de controle, algoritmos de roteamento e os ativos de simulação para um projeto de Iniciação Científica (IC) focado em redes LoRa Mesh aplicadas a Veículos Aéreos Não Tripulados (UAVs) em ambientes urbanos densos.

O projeto utiliza um Digital Twin (Gêmeo Digital) de uma área central de Curitiba (Shopping Estação / Praça Eufrásio Correia) para validar protocolos de comunicação em cenários de sombreamento de sinal e "Cânions Urbanos".

## Arquitetura do Sistema

O projeto opera em uma arquitetura de co-simulação dividida em dois domínios:

### Infraestrutura (Física & Voo)

- **Simulador**: Gazebo Harmonic (GZ)
- **Piloto Automático**: PX4 Autopilot (SITL - Software In The Loop)
- **Mundo**: Mapa 3D georreferenciado de Curitiba (OBJ/SDF) com física de colisão

### Lógica (Controle & Rede)

- **Linguagem**: Python 3
- **Interface**: MAVSDK (comunicação via UDP 14540)
- **Protocolo**: Algoritmo de Mesh customizado (simulado via Raycasting para perda de sinal)

## Estrutura de Pastas
```
~/IC_LoRa_Mesh/
├── assets/              # Backup dos modelos 3D e arquivos de mundo
│   ├── mapa_curitiba/   # Arquivos .obj, .mtl, texturas e model.config
│   └── curitiba.sdf     # Definição do mundo (Física, Sol, GPS, Plugins)
├── src/                 # Código Fonte (Onde a mágica acontece)
│   ├── main.py          # Script principal de controle de voo
│   ├── mesh_protocol.py # (Futuro) Lógica do protocolo LoRa
│   └── utils.py         # Funções auxiliares (cálculo de distância, etc.)
├── logs/                # Logs de voo (.ulog) e dados de telemetria CSV
├── requirements.txt     # Dependências Python (mavsdk, etc.)
└── README.md            # Este arquivo
```

## Como Executar

A execução exige dois terminais abertos simultaneamente.

### Pré-requisitos

- Ubuntu 24.04 (LTS)
- PX4 Autopilot configurado e compilado
- Variável de ambiente `GZ_SIM_RESOURCE_PATH` configurada no `.bashrc`

### Passo 1: Iniciar o Simulador (Terminal 1)

Este comando carrega o Gazebo Harmonic com o mapa de Curitiba e o drone x500.
```bash
cd ~/PX4-Autopilot
PX4_GZ_WORLD=curitiba make px4_sitl gz_x500
```

Aguarde até que o QGroundControl conecte ou apareça "Ready to fly" no terminal.

### Passo 2: Iniciar a Lógica de Controle (Terminal 2)

Este comando executa o script Python que controla o drone e simula a rede.
```bash
cd ~/IC_LoRa_Mesh/src
python3 main.py
```

## Detalhes do Cenário (Digital Twin)

- **Localização**: Curitiba, PR, Brasil
- **Coordenadas de Origem**: -25.43721, -49.26599
- **Características**:
  - Prédios reais modelados em 3D (Blender) para testes de oclusão (Non-Line-of-Sight)
  - Texturas aplicadas para realismo visual
  - Sensores Ativos: IMU, Magnetômetro, Barômetro e GPS

## Metodologia de Teste (IC)

O objetivo é validar a eficiência de um protocolo de comunicação LoRa Mesh.

1. **Cenário de Teste**: O drone voa entre prédios onde a conexão direta (Ponto-a-Ponto) com a estação base (Gateway) é bloqueada.

2. **Simulação de Sinal**:
   - Utiliza-se a posição GPS do drone extraída via MAVSDK
   - Aplica-se um modelo de Path Loss (Log-Distance ou Okumura-Hata)
   - Verifica-se obstrução visual (Raycasting) pelos modelos 3D dos prédios

3. **Métrica de Sucesso**: Packet Delivery Ratio (PDR) e Latência em comparação com topologia estrela convencional.

## Troubleshooting (Problemas Comuns)

### 1. Erro: "Unable to find file / model missing"

O Gazebo não achou a pasta do mapa.

**Solução**: Verifique se você exportou o caminho no terminal:
```bash
export GZ_SIM_RESOURCE_PATH=$HOME/PX4-Autopilot/Tools/simulation/gz/models
```

### 2. Erro: Prédios Brancos (Sem Textura)

O Gazebo não conseguiu ler o arquivo `.mtl` ou achar as imagens.

**Solução**: Abra o arquivo `.obj` e garanta que a linha `mtllib` aponta apenas para o nome do arquivo (ex: `mtllib mapa.mtl`), sem caminhos absolutos (`C:/Users/...`).

### 3. Drone "Zumbi" (Não conecta/Preflight Fail)

Faltam sensores no arquivo SDF.

**Solução**: Garanta que os plugins `gz-sim-sensors-system`, `air-pressure-system` e `magnetometer-system` estão no arquivo `curitiba.sdf`.

## Autor & Licença

**Autor**: Felipe Marcondes  
**Projeto**: Iniciação Científica - Engenharia de Computação  
**Ano**: 2025/2026
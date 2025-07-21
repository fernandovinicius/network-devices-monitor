from datetime import datetime
import sqlite3
import random

# Caminho do banco
DB_PATH = "network_monitor.db"


# Carregando lista de dispositivos
dispositivos = []
with open("dispositivos.txt", "r") as fp:
    for line in fp:
        if line.strip():  # Ignora linhas vazias
            ip, hostname, dtype, site = line.strip().split(", ")
            dispositivos.append((ip, hostname, dtype, site))
dispositivos = dispositivos[1:]  # Ignora cabeçalho


# Conexão com o banco
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

now = datetime.now().isoformat()

# Insere 100 dispositivos
for ip_address, hostname, dtype, site in dispositivos:

    if dtype == "" or dtype is None:
        dtype = "UNKNOWN"
    if site == "" or site is None:
        site = "BR"

    monitoring_interval_sec = random.choice([30, 60, 90, 120])
    ping_timeout_ms = random.choice([250, 500, 1000, 2000])
    ping_count = random.randint(1, 4)

    cursor.execute(
        """
        INSERT INTO DEVICES (
            IP_ADDRESS, HOSTNAME, SITE, TYPE,
            MONITORING_INTERVAL_SECONDS, PING_TIMEOUT_MILLISECONDS,
            PING_COUNT, MONITORING_ENABLED, CURRENT_STATUS, LAST_STATUS_CHANGE
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ip_address,
            hostname,
            site,
            dtype,
            monitoring_interval_sec,
            ping_timeout_ms,
            ping_count,
            True,
            99,
            now,
        ),
    )

    device_id = cursor.lastrowid

    # Cria entrada no histórico
    cursor.execute(
        """
        INSERT INTO DEVICES_STATUS_HISTORY (
            DEVICE_ID, STATUS, LAST_STATUS_CHANGE, COUNT
        ) VALUES (?, ?, ?, ?)
        """,
        (device_id, 99, now, 1),
    )
    history_id = cursor.lastrowid

    # Atualiza o campo CURRENT_HISTORY_ID
    cursor.execute(
        """
        UPDATE DEVICES SET CURRENT_HISTORY_ID = ? WHERE ID = ?
    """,
        (history_id, device_id),
    )

conn.commit()
conn.close()
print(f"✅ {len(dispositivos)} dispositivos inseridos com sucesso.")

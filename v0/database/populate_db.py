from datetime import datetime
import sqlite3
import random

# Dispositivos inspirados em sites populares (com HOSTNAMEs válidos)
sites_populares = [
    ("GOOGLE", "8.8.8.8", "GOOGLE_DNS"),
    ("CLOUDFLARE", "1.1.1.1", "CLOUDFLARE_DNS"),
    ("AMAZON", "205.251.242.103", "AMAZON_WEB"),
    ("MICROSOFT", "13.77.161.179", "MICROSOFT_AZURE"),
    ("FACEBOOK", "157.240.22.35", "FACEBOOK_EDGE"),
    ("TWITTER", "104.244.42.1", "TWITTER_CDN"),
    ("YOUTUBE", "142.250.72.206", "YOUTUBE_VIDEO"),
    ("NETFLIX", "52.26.8.155", "NETFLIX_STREAM"),
    ("SPOTIFY", "35.190.85.240", "SPOTIFY_AUDIO"),
    ("INSTAGRAM", "157.240.229.174", "INSTAGRAM_EDGE")
]

monitoring_values = [30, 60, 90, 120, 150, 180, 210, 240, 270, 300]

# Conexão com o banco
conn = sqlite3.connect("network_monitor.db")
cursor = conn.cursor()

now = datetime.now().isoformat()

# Insere 100 dispositivos
for i in range(10):
    site_nome, ip_base, hostname_base = random.choice(sites_populares)
    
    ip_address = ip_base
    hostname = f"{hostname_base}_{i}".upper().replace(" ", "_")[:50]
    site = site_nome.upper().replace(" ", "_")[:20]
    tipo = "SRV"  # Pode ser ajustado conforme sua lógica
    
    monitoring_interval = random.choice(monitoring_values)
    ping_timeout = random.randint(100, 2000)
    ping_count = random.randint(1, 4)

    cursor.execute("""
        INSERT INTO DEVICES (
            IP_ADDRESS, HOSTNAME, SITE, TYPE,
            MONITORING_INTERVAL_SECONDS, PING_TIMEOUT_MILLISECONDS,
            PING_COUNT, MONITORING_ENABLED, CURRENT_STATUS, LAST_STATUS_CHANGE
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ip_address,
        hostname,
        site,
        tipo,
        monitoring_interval,
        ping_timeout,
        ping_count, True, 99, now
    ))

    device_id = cursor.lastrowid

    # Cria entrada no histórico
    cursor.execute("""
        INSERT INTO DEVICES_STATUS_HISTORY (
            DEVICE_ID, STATUS, LAST_STATUS_CHANGE, COUNT
        ) VALUES (?, ?, ?, ?)
    """, (device_id, 99, now, 1))

    history_id = cursor.lastrowid

    # Atualiza o campo CURRENT_HISTORY_ID
    cursor.execute("""
        UPDATE DEVICES SET CURRENT_HISTORY_ID = ? WHERE ID = ?
    """, (history_id, device_id))

conn.commit()
conn.close()
print("✅ 100 dispositivos inseridos com sucesso.")

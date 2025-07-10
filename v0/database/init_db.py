import sqlite3
from datetime import datetime

# Caminho do banco
DB_PATH = "network_monitor.db"

# Dados de teste
test_devices = [
    ('8.8.8.8', 'GOOGLE_DNS', 'SP', 'SRV'),
    ('1.1.1.1', 'CLOUDFLARE_DNS', 'RJ', 'SRV'),
    ('192.168.50.1', 'FERNANDO_5G', 'DF', 'ROUTER'),
    ('192.168.50.13', 'FERNANDO_PC', 'DF', 'PC'),
    ('192.168.50.15', 'GALAXY_S22', 'DF', 'CEL')
]


def delete_tables(cursor):
    cursor.executescript("""
        DROP TABLE IF EXISTS MONITORING_DATA;
        DROP TABLE IF EXISTS DEVICES_STATUS_HISTORY;
        DROP TABLE IF EXISTS DEVICES;
    """)


def create_tables(cursor):
    cursor.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS DEVICES (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        IP_ADDRESS TEXT NOT NULL,
        HOSTNAME TEXT NOT NULL CHECK(HOSTNAME GLOB '[A-Z0-9_]*' AND LENGTH(HOSTNAME) <= 50),
        SITE TEXT NOT NULL CHECK(SITE GLOB '[A-Z0-9_]*' AND LENGTH(SITE) <= 20),
        TYPE TEXT CHECK(TYPE GLOB '[A-Z0-9_]*' AND LENGTH(TYPE) <= 30),
        MONITORING_INTERVAL_SECONDS INTEGER NOT NULL CHECK(MONITORING_INTERVAL_SECONDS IN (30,60,90,120,150,180,210,240,270,300)) DEFAULT 60,
        PING_TIMEOUT_MILLISECONDS INTEGER NOT NULL CHECK(PING_TIMEOUT_MILLISECONDS BETWEEN 100 AND 5000) DEFAULT 1000,
        PING_COUNT INTEGER NOT NULL CHECK(PING_COUNT BETWEEN 1 AND 10) DEFAULT 1,
        MONITORING_ENABLED BOOLEAN NOT NULL DEFAULT 1,
        CURRENT_STATUS INTEGER DEFAULT 99 CHECK(CURRENT_STATUS IN (0,1,99)),
        LAST_STATUS_CHANGE TEXT DEFAULT CURRENT_TIMESTAMP,
        CURRENT_HISTORY_ID INTEGER,
        FOREIGN KEY (CURRENT_HISTORY_ID) REFERENCES DEVICES_STATUS_HISTORY(ID)
    );

    CREATE TABLE IF NOT EXISTS DEVICES_STATUS_HISTORY (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        DEVICE_ID INTEGER NOT NULL,
        STATUS INTEGER NOT NULL,
        LAST_STATUS_CHANGE TEXT NOT NULL,
        COUNT INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (DEVICE_ID) REFERENCES DEVICES(ID)
    );

    CREATE TABLE IF NOT EXISTS MONITORING_DATA (
        TIMESTAMP TEXT NOT NULL,
        DEVICE_ID INTEGER NOT NULL,
        STATUS INTEGER NOT NULL,
        PACK_SENT INTEGER,
        PACK_RECV INTEGER,
        RTT_MIN INTEGER,
        RTT_MAX INTEGER,
        RTT_AVG INTEGER,
        FOREIGN KEY (DEVICE_ID) REFERENCES DEVICES(ID)
    );
    """)

def insert_device(cursor, ip, hostname, site, dtype):
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO DEVICES (
            IP_ADDRESS, HOSTNAME, SITE, TYPE,
            MONITORING_INTERVAL_SECONDS, PING_TIMEOUT_MILLISECONDS,
            PING_COUNT, MONITORING_ENABLED, CURRENT_STATUS, LAST_STATUS_CHANGE
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ip, hostname, site, dtype, 30, 1000, 3, True, 99, now))

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

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    delete_tables(cursor)
    create_tables(cursor)

    for ip, hostname, site, dtype in test_devices:
        insert_device(cursor, ip, hostname, site, dtype)

    conn.commit()
    conn.close()
    print("✅ Banco de dados criado e populado com sucesso.")

if __name__ == "__main__":
    main()

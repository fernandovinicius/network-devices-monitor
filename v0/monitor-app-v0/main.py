import sqlite3
import threading
import time
from datetime import datetime
from loguru import logger
from models.database import Device, MonitoringData, DeviceStatusHistory
from models.status import DeviceStatus
from ping3 import ping


# Lista global de dispositivos
device_list = []
DATABASE_URL = '../database/network_monitor.db'

FETCH_DEVICES_CYCLES = 1
MONITOR_INTERVAL_SEC = 30

LINE_BREAK = "\n" + 80*"="


# Adaptador de data sqlite3
sqlite3.register_adapter(datetime, lambda val: val.isoformat())


def load_devices():
    devices = []
    try:
        with sqlite3.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE monitoring_enabled=true;")
            rows = cursor.fetchall()
            devices = [Device(*row) for row in rows]
    except Exception as e:
        logger.error(f"Erro ao carregar dispositivos: {e}")
    return devices


def ping_device(ip_address, count, timeout_sec):
    rtts = []
    sent = 0
    recv = 0
    for _ in range(count):
        response = ping(ip_address, timeout=timeout_sec, unit="ms")
        sent += 1
        if response:
            recv += 1
            rtts.append(response)
    if len(rtts):
        rtt_min = int(min(rtts))
        rtt_max = int(max(rtts))
        rtt_avg = int(sum(rtts) / len(rtts))
    else:
        rtt_min = rtt_max = rtt_avg = None

    return sent, recv, rtt_min, rtt_max, rtt_avg


def monitor_device(device):
    device_id = device.id
    ip_address = device.ip_address
    hostname = device.hostname
    ping_count = device.ping_count
    timeout_s = max(round(device.ping_timeout_milliseconds/1000), 1)
    old_status = device.current_status
    history_id = device.current_history_id
    current_timestamp = datetime.now().isoformat()
    
    sent, recv, rtt_min, rtt_max, rtt_avg = ping_device(
        ip_address=ip_address,
        count=ping_count,
        timeout_sec=timeout_s,
    )
    new_status = DeviceStatus.UP.value if recv > 0 else DeviceStatus.DOWN.value
    logger.info(
        f" # {hostname}: status={DeviceStatus(new_status).name}, sent={sent}, recv={recv}, rtt_min={rtt_min} ms, rtt_max: {rtt_max} ms, rtt_avg={rtt_avg} ms"
    )

    # Atualiza banco
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        
        # Se status não mudou, atualiza apenas em DEVICES_STATUS_HISTORY
        if new_status == old_status:
            cursor.execute(
                """
                UPDATE DEVICES_STATUS_HISTORY
                SET COUNT = COUNT + 1
                WHERE ID = ?
                """,
                (history_id,)
            )
        else:
            # Cria nova entrada em DeviceStatusHistory
            cursor.execute(
                """
                INSERT INTO DEVICES_STATUS_HISTORY (
                    DEVICE_ID, STATUS, LAST_STATUS_CHANGE, COUNT
                ) VALUES (?, ?, ?, ?)
                """,
                (device_id, new_status, current_timestamp, 1),
            )
            history_id = cursor.lastrowid

            # Atualiza Device
            cursor.execute(
                """
                UPDATE DEVICES
                SET CURRENT_STATUS = ?, LAST_STATUS_CHANGE = ?, CURRENT_HISTORY_ID = ?
                WHERE ID = ?
                """,
                (new_status, current_timestamp, history_id, device_id),
            )

        # Insere dados em MonitoringData
        cursor.execute(
            """
            INSERT INTO MONITORING_DATA (
                TIMESTAMP,  DEVICE_ID, STATUS, PACK_SENT, PACK_RECV, RTT_MIN, RTT_MAX, RTT_AVG
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (current_timestamp, device_id, new_status, sent, recv, rtt_min, rtt_max, rtt_avg),
        )
        conn.commit()


def monitoring_loop():
    logger.info("Iniciando monitoramento dos dispositivos" + LINE_BREAK)

    cycle = 0
    while True:
        logger.info(f"Iniciando ciclo {cycle} de monitoração.")
        start = time.time()

        # Carrega os dispositivos do banco de dados apenas em múltiplos de FETCH_DEVICES_CYCLES
        if cycle % FETCH_DEVICES_CYCLES == 0:
            logger.info("Carregando dispositivos da base")
            devices = load_devices()
            logger.info(f"Dispositivos carregados: {len(devices)}")

        threads = []
        for device in devices:
            # Só monitora os múltiplos de MONITOR_INTERVAL_SEC
            if (cycle * device.monitoring_interval_seconds) % MONITOR_INTERVAL_SEC != 0:
                continue
            t = threading.Thread(target=monitor_device, args=(device,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        cycle += 1
        elapsed_time = time.time() - start
        logger.info(f"Tempo de execução do loop: {1000*elapsed_time:.3f} ms" + LINE_BREAK)
        time.sleep(MONITOR_INTERVAL_SEC - elapsed_time)


# Inicia o loop de monitoramento
monitoring_loop()

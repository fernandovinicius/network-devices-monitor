import time
import threading
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from ping3 import ping
from config import DATABASE_URL, MONITOR_INTERVAL_SEC, FETCH_DEVICES_CYCLES
from models.database_models import (
    Device,
    MonitoringData,
    DeviceStatusHistory,
    get_engine,
    get_session,
)


engine = get_engine(DATABASE_URL)
session = get_session(engine)
print(engine)
print(session)

device_lock = threading.Lock()
local_results = []
local_status_updates = []
local_history_entries = []

ping_history_cache = {}  # device_id → (last_status, count)


# Função para carregar dispositivos
def load_devices():
    devices = []
    try:
        devices = session.query(Device).filter_by(monitoring_enabled=True).all()
    except SQLAlchemyError as e:
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


# Função de ping
def monitor_device(device: Device):
    ip_address = device.ip_address
    hostname = device.hostname
    prev_status = device.current_status
    ping_timeout_sec = device.ping_timeout_milliseconds // 1000
    ping_count = device.ping_count
    current_timestamp = datetime.now()

    try:
        pack_sent, pack_recv, rtt_min, rtt_max, rtt_avg = ping_device(
            ip_address=ip_address,
            count=ping_count,
            timeout_sec=ping_timeout_sec,
        )

        new_status = 1 if pack_recv > 0 else 0

        # Atualiza histórico local e prepara atualizações
        with device_lock:
            prev_status, prev_count = ping_history_cache.get(device.id, (new_status, 0))

            if new_status == prev_status:
                new_count = prev_count + 1
                ping_history_cache[device.id] = (new_status, new_count)
                update = {
                    "device_id": device.id,
                    "existing": True,
                    "last_status_change": device.last_status_change,
                    "count": new_count,
                }
            else:
                ping_history_cache[device.id] = (new_status, 1)

                device.last_status_change = current_timestamp
                device.current_status = new_status

                update = {
                    "device_id": device.id,
                    "existing": False,
                    "last_status_change": current_timestamp,
                    "count": 1,
                }
                local_status_updates.append(update)

                local_history_entries.append(
                    DeviceStatusHistory(
                        device_id=device.id,
                        last_status_change=current_timestamp,
                        count=1,
                    )
                )

        local_results.append(
            MonitoringData(
                device_id=device.id,
                status=new_status,
                pack_sent=pack_sent,
                pack_recv=pack_sent,
                rtt_min=rtt_min,
                rtt_max=rtt_max,
                rtt_avg=rtt_avg,
                timestamp=current_timestamp,
            )
        )

        logger.info(
            f"{hostname}: status={new_status}, sent={pack_sent}, recv={pack_recv}, rtt_avg={rtt_avg} ms"
        )

    except Exception as e:
        logger.error(f"Erro ao pingar {ip_address} ({hostname}): {e}")


def persist_data():
    try:
        for update in local_status_updates:
            if update["existing"]:
                session.query(DeviceStatusHistory).filter_by(
                    device_id=update["device_id"],
                    last_status_change=update["last_status_change"],
                ).update({"count": update["count"]})
            else:
                session.query(Device).filter_by(id=update["device_id"]).update(
                    {
                        "current_status": update["count"],
                        "last_status_change": update["last_status_change"],
                    }
                )

        session.bulk_save_objects(local_results)
        session.bulk_save_objects(local_history_entries)
        session.commit()

    except Exception as e:
        logger.error(f"Erro ao persistir dados no banco: {e}")
        session.rollback()

    finally:
        local_results.clear()
        local_status_updates.clear()
        local_history_entries.clear()


# Loop principal de monitoração
def run_monitoring():
    logger.info("Iniciando monitoração")

    cycle = 0
    devices = []

    try:
        while True:
                logger.info(f"Iniciando ciclo {cycle} de monitoração.")

                start = time.time()

                # Carrega os dispositivos do banco de dados apenas em múltiplos de FETCH_DEVICES_CYCLES
                if cycle % FETCH_DEVICES_CYCLES == 0:
                    logger.info("Carregando dispositivos da base")
                    devices = load_devices()
                    logger.info(f"Dispositivos carregados: {len(devices)}\n" + 50 * "=")

                threads = []

                for device in devices:
                    # Só monitora nos múltiplos do intervalo de monitoramento do dispositivo
                    if (cycle * MONITOR_INTERVAL_SEC) % device.monitoring_interval_seconds == 0:
                        t = threading.Thread(target=monitor_device, args=(device,))
                        t.start()
                        threads.append(t)

                for t in threads:
                    t.join()

                logger.info("Persistindo dados na base")
                persist_data()

                elapsed_time = time.time() - start
                logger.info(
                    f"Tempo de execução do loop: {1000*elapsed_time:.3f} ms\n" + 50 * "="
                )

                cycle += 1
                time.sleep(MONITOR_INTERVAL_SEC - elapsed_time)
                
    except KeyboardInterrupt:
        logger.info("Encerrando aplicação.")
    except Exception as e:
        logger.error(e)
    finally:
        session.close()
    

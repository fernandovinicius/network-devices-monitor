import time
import threading
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from ping3 import ping
from config import DB_URL, MONITOR_INTERVAL_SEC, FETCH_DEVICES_CYCLES
from models import Device, MonitoringData


# Setup banco de dados
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)


# Função para carregar dispositivos
def load_devices():
    devices = []
    session = Session()
    try:
        devices = session.query(Device).filter_by(monitoring_enabled=True).all()
    except SQLAlchemyError as e:
        logger.error(f"Erro ao carregar dispositivos: {e}")
    finally:
        session.close()
    return devices


# Função de ping
def ping_device(device: Device):

    try:
        ip = device.ip
        hostname = device.hostname
        old_status = device.status
        ping_timeout_sec = device.ping_timeout_milliseconds/1000
        ping_count = device.ping_count
        rtts = []
        pack_sent = 0
        pack_recv = 0

        for _ in range(ping_count):
            try:
                response = ping(ip, timeout=ping_timeout_sec, unit="ms")
                pack_sent += 1
                if response:
                    pack_recv += 1
                    rtts.append(response)
            except Exception as e:
                logger.warning(f"Ping falhou para {hostname} ({ip}): {e}")

        new_status = 1 if pack_recv > 0 else 0

        if new_status != old_status:
            print("mudou")
        else:
            print("nao mudou")

        if rtts:
            rtt_min = int(min(rtts))
            rtt_max = int(max(rtts))
            rtt_avg = int(sum(rtts) / len(rtts))
        else:
            rtt_min = rtt_max = rtt_avg = None

        record = MonitoringData(
            timestamp=datetime.now(),
            device_id=device.id,
            status=new_status,
            pack_sent=pack_sent,
            pack_recv=pack_recv,
            rtt_min=rtt_min,
            rtt_max=rtt_max,
            rtt_avg=rtt_avg,
        )

        logger.info(
            f"{hostname}: status={new_status}, sent={pack_sent}, recv={pack_recv}, rtt_avg={rtt_avg} ms"
        )
        return record

    except Exception as e:
        logger.error(f"Erro ao pingar {hostname} ({ip}): {e}")
        return MonitoringData(
            timestamp=datetime.now(),
            device_id=device.id,
            status=0,
            pack_sent=device.ping_count,
            pack_recv=0,
            rtt_min=None,
            rtt_max=None,
            rtt_avg=None,
        )


# Loop principal de monitoração
def monitor_loop():
    logger.info("Iniciando monitoração")

    loop_counter = 0
    devices = []

    while True:
        start = time.time()
        # Carrega os dispositivos do banco de dados apenas em múltiplos de FETCH_DEVICES_CYCLES
        if loop_counter % FETCH_DEVICES_CYCLES == 0:
            devices = load_devices()
            logger.info(f"Dispositivos carregados: {len(devices)}\n" + 50 * "=")

        session = Session()
        results = []
        threads = []

        def monitor_and_append(device):
            result = ping_device(device)
            results.append(result)

        for device in devices:
            # Só monitora nos múltiplos do intervalo de monitoramento do dispositivo
            if (loop_counter * MONITOR_INTERVAL_SEC) % device.monitoring_interval_seconds == 0:
                t = threading.Thread(target=monitor_and_append, args=(device,))
                t.start()
                threads.append(t)

        for t in threads:
            t.join()

        try:
            session.bulk_save_objects(results)
            session.commit()
            logger.info(f"Persistidos {len(results)} resultados de monitoramento.")
        except SQLAlchemyError as e:
            logger.error(f"Erro ao salvar dados no banco: {e}")
            session.rollback()
        finally:
            session.close()

        elapsed_time = time.time() - start
        logger.info(f"Tempo de execução do loop: {1000*elapsed_time:.3f} ms\n" + 50 * "=")

        loop_counter += 1
        time.sleep(MONITOR_INTERVAL_SEC - elapsed_time)


# Inicialização
if __name__ == "__main__":
    logger.add("log_monitor.log", rotation="1 day")
    monitor_loop()

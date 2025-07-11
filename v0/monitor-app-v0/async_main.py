import asyncio
import time
import aiosqlite
from config import DATABASE_URL, FETCH_DEVICES_CYCLES, MONITOR_INTERVAL_SEC
from datetime import datetime
from loguru import logger
from models.database import Device, MonitoringData, DeviceStatusHistory
from models.status import DeviceStatus
from aioping import ping
from async_db_utils import (
    save_monitoring_data,
    update_device_info,
    insert_new_history,
    increment_count_history,
)


LINE_BREAK = "\n" + 80 * "="


# Adaptador de data sqlite3
aiosqlite.register_adapter(datetime, lambda val: val.isoformat())


# Fila assíncrona para comunicação entre tarefas
result_queue = asyncio.Queue()


# Corrotina que busca os dispositivos do banco
async def fetch_devices(db_path=DATABASE_URL):
    try:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute(
                "SELECT * FROM devices WHERE monitoring_enabled=true;"
            ) as cursor:
                rows = await cursor.fetchall()
                return [Device(*row) for row in rows]
    except Exception as e:
        logger.error(f"Erro ao carregar dispositivos: {e}")


# Corrotina que grava os resultados no banco SQLite
async def db_writer(db_path):
    async with aiosqlite.connect(db_path) as db:
        while True:
            result = await result_queue.get()

            # Unpack estruturas
            device, monitoring_data = result

            # Insere dados em MonitoringData
            await save_monitoring_data(data=monitoring_data, cursor=db)

            # Unpack
            timestamp = monitoring_data.timestamp
            new_status = monitoring_data.status
            old_status = device.current_status
            history_id = device.current_history_id
            device_id = device.id

            if new_status == old_status:
                await increment_count_history(
                    history_id=history_id,
                    cursor=db,
                )
            else:
                # Cria nova entrada em DeviceStatusHistory
                history_id = await insert_new_history(
                    data=DeviceStatusHistory(
                        id=None,
                        device_id=device_id,
                        status=new_status,
                        last_status_change=timestamp,
                        count=1,
                    ),
                    cursor=db,
                )
                # Atualiza Device
                device.current_history_id = history_id
                device.current_status = new_status
                device.last_status_change = timestamp
                await update_device_info(
                    data=device,
                    cursor=db,
                )

            await db.commit()
            result_queue.task_done()


async def async_ping_device(device: Device):
    ip_address = device.ip_address
    count = device.ping_count
    timeout_sec = device.ping_timeout_milliseconds / 1000
    current_timestamp = datetime.now().isoformat()
    device_id = device.id

    rtts = []
    sent = 0
    for _ in range(count):
        try:
            delay = await ping(dest_addr=ip_address, timeout=timeout_sec)
            delay = 1000 * delay  # Converte para ms
            rtts.append(delay)
            sent += 1
        except Exception:
            delay = None

    if len(rtts):
        rtt_min, rtt_max, rtt_avg = (
            int(min(rtts)),
            int(max(rtts)),
            int(sum(rtts) / len(rtts)),
        )
    else:
        rtt_min = rtt_max = rtt_avg = None

    recv = len(rtts)
    new_status = DeviceStatus.UP.value if recv > 0 else DeviceStatus.DOWN.value

    data = MonitoringData(
        timestamp=current_timestamp,
        device_id=device_id,
        status=new_status,
        pack_sent=sent,
        pack_recv=recv,
        rtt_min=rtt_min,
        rtt_max=rtt_max,
        rtt_avg=rtt_avg,
    )

    logger.info(
        f" # {device.hostname}: status={DeviceStatus(new_status).name}, sent={sent}, recv={recv}, rtt_avg={rtt_avg} ms"
    )
    return device, data


# Corrotina que realiza o monitoramento
async def monitor_devices(devices):
    tasks = [asyncio.create_task(monitor_device(device)) for device in devices]
    await asyncio.gather(*tasks)


async def monitor_device(device: Device):
    result = await async_ping_device(device)
    await result_queue.put(result)


async def main_loop():
    writer_task = asyncio.create_task(db_writer(db_path=DATABASE_URL))

    logger.info("Iniciando monitoramento dos dispositivos" + LINE_BREAK)
    try:
        cycle = 0
        while True:
            start = time.time()

            if cycle % FETCH_DEVICES_CYCLES == 0:
                devices = await fetch_devices()

            devices = [
                d
                for d in devices
                if ((cycle * MONITOR_INTERVAL_SEC) % d.monitoring_interval_seconds == 0)
            ]
            logger.info(
                f"Iniciando ciclo {cycle} de monitoração: {len(devices)} dispositivos"
            )

            await monitor_devices(devices)
            await result_queue.join()

            cycle = cycle + 1
            elapsed = time.time() - start
            logger.info(f"Fim do ciclo. Duração: {elapsed:.3f} s" + LINE_BREAK)
            await asyncio.sleep(MONITOR_INTERVAL_SEC - elapsed)

    except KeyboardInterrupt:
        await result_queue.put(None)
        await writer_task
        logger.info("Encerrando")


# Inicia o loop de monitoramento
asyncio.run(main_loop())

from db.connection import get_connection
from utils.validation import validate_device_data
from loguru import logger
from models.device_model import Device
from models.device_status import DeviceStatus
from datetime import datetime


def get_all_devices():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DEVICES")
        rows = cursor.fetchall()
        conn.close()
        devices = [Device(*row) for row in rows]
        return devices
    except Exception as e:
        logger.error(f"Erro ao buscar todos os dispositivos: {e}")
        return []


def get_enabled_devices():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DEVICES WHERE MONITORING_ENABLED=1")
        rows = cursor.fetchall()
        conn.close()
        devices = [Device(*row) for row in rows]
        return devices
    except Exception as e:
        logger.error(f"Erro ao buscar todos os dispositivos: {e}")
        return []


def get_device_by_id(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DEVICES WHERE ID=?", (id,))
        row = cursor.fetchone()
        conn.close()
        device = Device(*row) if row else None
        return device
    except Exception as e:
        logger.error(f"Erro ao buscar dispositivo por ID {id}: {e}")
        return None


def get_device_by_ip(ip_address):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DEVICES WHERE IP_ADDRESS=?", (ip_address,))
        row = cursor.fetchone()
        conn.close()
        device = Device(*row) if row else None
        return device
    except Exception as e:
        logger.error(f"Erro ao buscar dispositivo por IP {ip_address}: {e}")
        return None


def get_device_by_hostname(hostname):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DEVICES WHERE HOSTNAME=?", (hostname,))
        row = cursor.fetchone()
        conn.close()
        device = Device(*row) if row else None
        return device
    except Exception as e:
        logger.error(f"Erro ao buscar dispositivo por HOSTNAME {hostname}: {e}")
        return None


def create_device(data):
    try:
        erros = validate_device_data(data)
        if erros:
            campos = ", ".join(erros)
            logger.warning(f"Falha na validação dos campos: {campos}")
            return {"error": f"Dados inválidos nos seguintes campos: {campos}"}

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO DEVICES (
                IP_ADDRESS, HOSTNAME, SITE, TYPE,
                MONITORING_INTERVAL_SECONDS, PING_TIMEOUT_MILLISECONDS, PING_COUNT,
                MONITORING_ENABLED, CURRENT_STATUS, LAST_STATUS_CHANGE
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["ip_address"],
                data["hostname"],
                data["site"],
                data["type"],
                data["monitoring_interval_seconds"],
                data["ping_timeout_milliseconds"],
                data["ping_count"],
                data.get("monitoring_enabled", True),
                data.get("current_status", DeviceStatus.NOT_STARTED.value),
                data.get("last_status_change", datetime.now().isoformat()),
            ),
        )
        conn.commit()
        conn.close()
        logger.info(f"Dispositivo criado: {data['hostname']} ({data['ip_address']})")
        return {"message": "Dispositivo criado com sucesso."}
    except Exception as e:
        logger.error(f"Erro ao criar dispositivo: {e}")
        return {"error": "Erro interno."}


def update_device(id, data):
    try:
        erros = validate_device_data(data)
        if erros:
            campos = ", ".join(erros)
            logger.warning(f"Falha na validação dos campos: {campos}")
            return {"error": f"Dados inválidos nos seguintes campos: {campos}"}

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE DEVICES SET
                IP_ADDRESS=?, HOSTNAME=?, SITE=?, TYPE=?,
                MONITORING_INTERVAL_SECONDS=?, PING_TIMEOUT_MILLISECONDS=?, PING_COUNT=?,
                MONITORING_ENABLED=?
            WHERE ID=?
            """,
            (
                data["ip_address"],
                data["hostname"],
                data["site"],
                data["type"],
                data["monitoring_interval_seconds"],
                data["ping_timeout_milliseconds"],
                data["ping_count"],
                data.get("monitoring_enabled", True),
                id,
            ),
        )
        conn.commit()
        conn.close()
        logger.info(f"Dispositivo atualizado: ID={id}")
        return {"message": "Dispositivo atualizado com sucesso."}
    except Exception as e:
        logger.error(f"Erro ao atualizar dispositivo {id}: {e}")
        return {"error": "Erro interno."}


def delete_device(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM DEVICES WHERE ID=?", (id,))
        conn.commit()
        conn.close()
        logger.info(f"Dispositivo removido: ID={id}")
        return {"message": "Dispositivo removido com sucesso."}
    except Exception as e:
        logger.error(f"Erro ao remover dispositivo {id}: {e}")
        return {"error": "Erro interno."}

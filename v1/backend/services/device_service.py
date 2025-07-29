import json
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
        logger.error(f"Erro ao buscar todos os dispositivos habilitados: {e}")
        return []


def get_devices_by_status(status):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DEVICES WHERE CURRENT_STATUS=?", (status,))
        rows = cursor.fetchall()
        conn.close()
        devices = [Device(*row) for row in rows]
        return devices
    except Exception as e:
        logger.error(
            f"Erro ao buscar todos os dispositivos com status {DeviceStatus[status]}: {e}"
        )
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
        rows = cursor.fetchall()
        conn.close()
        devices = [Device(*row) for row in rows]
        return devices
    except Exception as e:
        logger.error(f"Erro ao buscar dispositivo por IP {ip_address}: {e}")
        return None


def get_device_by_hostname(hostname):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DEVICES WHERE HOSTNAME=?", (hostname,))
        rows = cursor.fetchall()
        conn.close()
        devices = [Device(*row) for row in rows]
        return devices
    except Exception as e:
        logger.error(f"Erro ao buscar dispositivo por HOSTNAME {hostname}: {e}")
        return None


def create_device(data):
    try:
        # Garanta que os seguintes campos existam
        if "monitoring_enabled" not in data:
            data["monitoring_enabled"] = True
        if "current_status" not in data:
            data["current_status"] = DeviceStatus.NOT_STARTED.value
        if "last_status_change" not in data:
            data["last_status_change"] = datetime.now().isoformat()

        # Validação dos campos
        validation_error = validate_device_data(data)
        if validation_error:
            logger.error(
                f"Falha na validação dos campos:\n{json.dumps(validation_error, indent=4)}"
            )
            return {"error": validation_error}

        device = insert_device_db(device=data)
        logger.info(f"Dispositivo criado: {device})")
        return {"message": "Dispositivo criado com sucesso", "data": device}

    except Exception as e:
        logger.error(f"Erro ao criar dispositivo: {e}")
        return {"error": "Erro interno"}


def update_device(id, data):
    try:
        # Toda atualização altera o status para NOT_STARTED
        # Menos quando MONITORING_ENABLED é setado como falso,
        # o status vai para PAUSED

        data["current_status"] = DeviceStatus.NOT_STARTED.value
        if "monitoring_enabled" not in data:
            data["monitoring_enabled"] = True
        else:
            if bool(data["monitoring_enabled"]) == False:
                data["current_status"] = DeviceStatus.PAUSED.value
        data["last_status_change"] = datetime.now().isoformat()

        # Validação dos campos
        validation_error = validate_device_data(data)
        if validation_error:
            logger.error(
                f"Falha na validação dos campos:\n{json.dumps(validation_error, indent=4)}"
            )
            return {"error": validation_error}

        conn = get_connection()
        cursor = conn.cursor()

        # Cria entrada na tabela DEVICES_HISTORY_DATA
        cursor.execute(
            """
            INSERT INTO DEVICES_STATUS_HISTORY (
                DEVICE_ID, STATUS, LAST_STATUS_CHANGE, COUNT
            ) VALUES (?, ?, ?, ?)
            """,
            (
                id,
                data["current_status"],
                data["last_status_change"],
                1,
            ),
        )
        data["current_history_id"] = cursor.lastrowid

        cursor.execute(
            """
            UPDATE DEVICES SET
                IP_ADDRESS=?, HOSTNAME=?, SITE=?, TYPE=?,
                MONITORING_INTERVAL_SECONDS=?, PING_TIMEOUT_MILLISECONDS=?, PING_COUNT=?,
                MONITORING_ENABLED=?, CURRENT_STATUS=?, LAST_STATUS_CHANGE=?, CURRENT_HISTORY_ID=?
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
                data["monitoring_enabled"],
                data["current_status"],
                data["last_status_change"],
                data["current_history_id"],
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


def insert_device_db(device):
    conn = get_connection()
    cursor = conn.cursor()

    # Insere dispositivo na tabela DEVICES
    cursor.execute(
        """
        INSERT INTO DEVICES (
            IP_ADDRESS, HOSTNAME, SITE, TYPE,
            MONITORING_INTERVAL_SECONDS, PING_TIMEOUT_MILLISECONDS, PING_COUNT,
            MONITORING_ENABLED, CURRENT_STATUS, LAST_STATUS_CHANGE
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            device["ip_address"],
            device["hostname"],
            device["site"],
            device["type"],
            device["monitoring_interval_seconds"],
            device["ping_timeout_milliseconds"],
            device["ping_count"],
            device["monitoring_enabled"],
            device["current_status"],
            device["last_status_change"],
        ),
    )
    device["id"] = cursor.lastrowid

    # Cria entrada na tabela DEVICES_HISTORY_DATA
    cursor.execute(
        """
        INSERT INTO DEVICES_STATUS_HISTORY (
            DEVICE_ID, STATUS, LAST_STATUS_CHANGE, COUNT
        ) VALUES (?, ?, ?, ?)
        """,
        (
            device["id"],
            device["current_status"],
            device["last_status_change"],
            1,
        ),
    )
    device["current_history_id"] = cursor.lastrowid

    # Atualiza o campo CURRENT_HISTORY_ID
    cursor.execute(
        """
        UPDATE DEVICES SET CURRENT_HISTORY_ID = ? WHERE ID = ?
        """,
        (device["current_history_id"], device["id"]),
    )
    conn.commit()
    conn.close()

    return device

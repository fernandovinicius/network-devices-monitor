from db.connection import get_connection
from models.monitoring_data import MonitoringData
from loguru import logger


def get_monitoring_data(device_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM MONITORING_DATA WHERE DEVICE_ID=?", (device_id,))
        rows = cursor.fetchall()
        conn.close()
        data = [MonitoringData(*row) for row in rows]
        return data
    except Exception as e:
        logger.error(
            f"Erro ao buscar dados de monitoramento para dispositivo {device_id}: {e}"
        )
        return []

from db.connection import get_connection
from models.monitoring_data import MonitoringData
from loguru import logger


def get_monitoring_data(device_id, begin_date=None, end_date=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM MONITORING_DATA WHERE DEVICE_ID = ?"
        params = [device_id]

        if begin_date and end_date:
            query += " AND timestamp BETWEEN ? AND ?"
            params.extend([begin_date, end_date])
        elif begin_date:
            query += " AND timestamp >= ?"
            params.append(begin_date)
        elif end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        data = [MonitoringData(*row) for row in rows]
        return data
    except Exception as e:
        logger.error(
            f"Erro ao buscar dados de monitoramento para dispositivo {device_id}: {e}"
        )
        return []

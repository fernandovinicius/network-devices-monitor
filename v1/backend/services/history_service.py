from db.connection import get_connection
from models.device_status_history import DeviceStatusHistory
from loguru import logger


def get_device_history(device_id, begin_date=None, end_date=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM DEVICES_STATUS_HISTORY WHERE DEVICE_ID = ?"
        params = [device_id]

        if begin_date and end_date:
            query += " AND last_status_change BETWEEN ? AND ?"
            params.extend([begin_date, end_date])
        elif begin_date:
            query += " AND last_status_change >= ?"
            params.append(begin_date)
        elif end_date:
            query += " AND last_status_change <= ?"
            params.append(end_date)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        data = [DeviceStatusHistory(*row) for row in rows]
        return data
    except Exception as e:
        logger.error(f"Erro ao buscar histórico para dispositivo {device_id}: {e}")
        return []

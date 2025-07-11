from models.database import Device, MonitoringData, DeviceStatusHistory
from aiosqlite import Cursor


async def update_device_info(cursor: Cursor, data: Device):
    await cursor.execute(
        """
        UPDATE DEVICES
        SET CURRENT_STATUS = ?, LAST_STATUS_CHANGE = ?, CURRENT_HISTORY_ID = ?
        WHERE ID = ?
        """,
        (
            data.current_status,
            data.last_status_change,
            data.current_history_id,
            data.id,
        ),
    )


async def insert_new_history(cursor: Cursor, data: DeviceStatusHistory):
    res = await cursor.execute(
        """
        INSERT INTO DEVICES_STATUS_HISTORY (
            DEVICE_ID, STATUS, LAST_STATUS_CHANGE, COUNT
        ) VALUES (?, ?, ?, ?)
        """,
        (
            data.device_id,
            data.status,
            data.last_status_change,
            data.count,
        ),
    ) 
    return res.lastrowid


async def increment_count_history(cursor: Cursor, history_id: int):
    await cursor.execute(
        """
        UPDATE DEVICES_STATUS_HISTORY
        SET COUNT = COUNT + 1
        WHERE ID = ?
        """,
        (history_id,),
    )


async def save_monitoring_data(cursor, data: MonitoringData):
    await cursor.execute(
        """
        INSERT INTO MONITORING_DATA (
            TIMESTAMP,  DEVICE_ID, STATUS, PACK_SENT, PACK_RECV, RTT_MIN, RTT_MAX, RTT_AVG
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.timestamp,
            data.device_id,
            data.status,
            data.pack_sent,
            data.pack_recv,
            data.rtt_min,
            data.rtt_max,
            data.rtt_avg,
        ),
    )

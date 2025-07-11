from datetime import datetime
import sqlite3
from flask import Blueprint, render_template, request
from config import DB_URL
from models.database import Device, DeviceStatusHistory
from models.status import DeviceStatus


home_bp = Blueprint("home", __name__, template_folder="../templates")


@home_bp.route("/")
def home():
    search = request.args.get("search")
    devices = get_devices(search=search)

    ativos = len([d for d in devices if d[0] == 0])
    inativos = len([d for d in devices if d[0] == 1])
    total = len(devices)

    return render_template(
        "index.html", devices=devices, ativos=ativos, inativos=inativos, total=total
    )


@home_bp.route("/device/<hostname>")
def device_info(hostname):
    conn = sqlite3.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM DEVICES WHERE HOSTNAME = ?
        """,
        (hostname.upper(),),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return 404, "Device not found"

    device = Device(*row) if row else None
    try:
        data_formatada = datetime.fromisoformat(device.last_status_change).strftime("%d/%m/%Y %H:%M")
        device.last_status_change = data_formatada
    except Exception:
        pass
    return render_template("dados_dispositivo.html", device=device, status=DeviceStatus)


@home_bp.route("/history/<hostname>")
def device_history(hostname):
    conn = sqlite3.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT ID
        FROM DEVICES
        WHERE HOSTNAME = ?
        """,
        (hostname.upper(),),
    )
    device_id = cursor.fetchone()
    if device_id:
        cursor.execute(
            """
            SELECT *
            FROM DEVICES_STATUS_HISTORY
            WHERE DEVICE_ID = ?
            ORDER BY LAST_STATUS_CHANGE DESC
            """,
            (device_id[0],),
        )
        rows = cursor.fetchall()
        history = [DeviceStatusHistory(*row) for row in rows]
    else:
        history = []

    conn.close()
    return render_template(
        "historico_dispositivo.html",
        hostname=hostname.upper(),
        history=history,
        status=DeviceStatus,
    )


def get_devices(status_filter=None, search=None):
    import sqlite3
    from datetime import datetime

    conn = sqlite3.connect(DB_URL)
    cursor = conn.cursor()

    query = "SELECT CURRENT_STATUS, IP_ADDRESS, HOSTNAME, TYPE, SITE, LAST_STATUS_CHANGE FROM DEVICES"
    params = []

    if search:
        query += (
            " WHERE HOSTNAME LIKE ? OR IP_ADDRESS LIKE ? OR TYPE LIKE ? OR SITE LIKE ?"
        )
        term = f"%{search.upper()}%"
        params = [term] * 4

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    devices = []
    for row in rows:
        print(row)
        try:
            last_change = datetime.strptime(row[5], "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            last_change = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")

        elapsed = datetime.now() - last_change
        total_seconds = int(elapsed.total_seconds())

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")

        formatted_time = "".join(parts)
        devices.append(row[:5] + (formatted_time,))

    # Ordena com inativos primeiro e por tempo decrescente
    return sorted(
        devices,
        key=lambda x: (
            x[0] != 1,
            -int(x[5].replace("d", "000").replace("h", "00").replace("m", "")),
        ),
    )

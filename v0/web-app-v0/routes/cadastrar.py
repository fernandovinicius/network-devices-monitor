from datetime import datetime
import sqlite3
from flask import Blueprint, jsonify
from flask import request, redirect, url_for, render_template
from config import DB_URL
from loguru import logger


cadastrar_bp = Blueprint("cadastrar", __name__, template_folder="../templates")


@cadastrar_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        try:
            logger.info(f"Cadastrando dispositivo: {request.form}")
            if insert_device(request.form):
                logger.info(f"Dispositivo cadastrado com sucesso!")
                return jsonify(success=True, message="✅ Dispositivo cadastrado com sucesso!")
            
        except Exception as e:
            logger.info(f"Erro ao cadastrar dispositivo: {e}")
        
        return jsonify(success=False, message=f"❌ Erro ao cadastrar dispositivo.")

    return render_template("cadastrar.html")


def insert_device(form):
    ip = form["ip_address"]
    hostname = form["hostname"].upper().replace(" ", "")
    device_type = form["type"].upper()
    site = form["site"].upper().replace(" ", "")
    ping_count = form["ping_count"]
    ping_timeout = form["ping_timeout"]
    interval_sec = form["monitoring_interval"]
    mon_enabled = form["monitoring_enabled"]
    now = datetime.now().isoformat()

    with sqlite3.connect(DB_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO DEVICES (
                IP_ADDRESS, HOSTNAME, SITE, TYPE,
                MONITORING_INTERVAL_SECONDS, PING_TIMEOUT_MILLISECONDS,
                PING_COUNT, MONITORING_ENABLED, CURRENT_STATUS, LAST_STATUS_CHANGE
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (ip, hostname, site, device_type, interval_sec, ping_timeout, ping_count, mon_enabled, 99, now),
        )
        device_id = cursor.lastrowid

        # Cria entrada no histórico
        cursor.execute(
            """
            INSERT INTO DEVICES_STATUS_HISTORY (
                DEVICE_ID, STATUS, LAST_STATUS_CHANGE, COUNT
            ) VALUES (?, ?, ?, ?)
        """,
            (device_id, 99, now, 1),
        )
        history_id = cursor.lastrowid

        # Atualiza o campo CURRENT_HISTORY_ID
        cursor.execute(
            """
            UPDATE DEVICES SET CURRENT_HISTORY_ID = ? WHERE ID = ?
        """,
            (history_id, device_id),
        )
        conn.commit()
        return True
    return False
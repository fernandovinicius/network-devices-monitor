from datetime import datetime
import sqlite3
from flask import Blueprint, jsonify
from flask import request, render_template
from config import DB_URL
from loguru import logger
from models.database import Device
from models.status import DeviceStatus
import re


cadastrar_bp = Blueprint("cadastrar", __name__, template_folder="../templates")


@cadastrar_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        try:
            data = request.form.to_dict()
            logger.info(f"Cadastrando dispositivo: {data}")
            device = insert_device(data)
            if device:
                logger.info(f"Dispositivo cadastrado com sucesso: {device}")
                return jsonify(
                    success=True, message="✅ Dispositivo cadastrado com sucesso!"
                )

        except Exception as e:
            logger.info(f"Erro ao cadastrar dispositivo: {e}")

        return jsonify(success=False, message=f"❌ Erro ao cadastrar dispositivo.")

    return render_template("cadastrar.html")


def insert_device(form):
    device = parse_income_data(form)
    if not device:
        return None

    current_date = datetime.now().isoformat()

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
            (
                device.ip_address,
                device.hostname,
                device.site,
                device.type,
                device.monitoring_interval_seconds,
                device.ping_timeout_milliseconds,
                device.ping_count,
                device.monitoring_enabled,
                device.current_status,
                current_date,
            ),
        )
        device.id = cursor.lastrowid

        # Cria entrada no histórico
        cursor.execute(
            """
            INSERT INTO DEVICES_STATUS_HISTORY (
                DEVICE_ID, STATUS, LAST_STATUS_CHANGE, COUNT
            ) VALUES (?, ?, ?, ?)
            """,
            (
                device.id,
                device.current_status,
                current_date,
                1,
            ),
        )
        history_id = cursor.lastrowid

        # Atualiza o campo CURRENT_HISTORY_ID
        cursor.execute(
            """
            UPDATE DEVICES SET CURRENT_HISTORY_ID = ? WHERE ID = ?
        """,
            (history_id, device.id),
        )
        conn.commit()
    return device


def parse_income_data(form):
    val_fns = [
        (validate_ipv4, "ip_address", form["ip_address"]),
        (validate_text_fields, "hostname", form["hostname"]),
        (validate_text_fields, "site", form["site"]),
        (validate_text_fields, "type", form["type"]),
        (
            validate_monitoring_interval,
            "monitoring_interval_seconds",
            form["monitoring_interval_seconds"],
        ),
        (
            validate_ping_timeout,
            "ping_timeout_milliseconds",
            form["ping_timeout_milliseconds"],
        ),
        (validate_ping_count, "ping_count", form["ping_count"]),
        (
            validate_monitoring_enabled,
            "monitoring_enabled",
            bool(form["monitoring_enabled"]),
        ),
    ]

    error_msg = ""
    for fn, key, val in val_fns:
        ret, msg = fn(key, val)
        if not ret:
            error_msg += "\n" + msg

    if len(error_msg):
        logger.error("error_msg: " + error_msg)
        return None

    return Device(
        id=None,
        ip_address=str(form["ip_address"]),
        hostname=form["hostname"],
        site=form["site"],
        type=form["type"],
        monitoring_interval_seconds=int(form["monitoring_interval_seconds"]),
        ping_timeout_milliseconds=int(form["ping_timeout_milliseconds"]),
        ping_count=int(form["ping_count"]),
        monitoring_enabled=bool(form["monitoring_enabled"]),
        current_status=DeviceStatus.NOT_STARTED.value,
        last_status_change=None,
        current_history_id=None,
    )


def validate_ipv4(key, value):
    # Regular expression for IPv4
    ipv4_pattern = r"^((25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$"
    if re.match(ipv4_pattern, value) is None:
        return False, "'ip_address' deve estar no formato IPv4."
    return True, ""


def validate_text_fields(key, value):
    VALID_CHARS_REGEX = re.compile(r"^[A-Z0-9_.-]+$")
    if not VALID_CHARS_REGEX.match(value):
        return (
            False,
            f"'{key}' deve conter apenas letras maiúsculas, números, traços, underscores ou pontos.",
        )
    return True, ""


def validate_monitoring_interval(key, value):
    if int(value) not in range(30, 301, 30):
        return (
            False,
            "'monitoring_interval_seconds' deve estar entre 30 e 300, de 30 em 30.",
        )
    return True, ""


def validate_ping_timeout(key, value):
    if not (100 <= int(value) <= 5000):
        return False, "'ping_timeout_milliseconds' deve estar entre 100 e 5000."
    return True, ""


def validate_ping_count(key, value):
    if not (1 <= int(value) <= 10):
        return False, "'ping_count' deve estar entre 1 e 10."
    return True, ""


def validate_monitoring_enabled(key, value):
    if bool(value) not in [True, False]:
        return False, "'monitoring_enabled' deve ser True ou False"
    return True, ""

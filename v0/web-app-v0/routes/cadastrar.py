from datetime import datetime
import sqlite3
from flask import Blueprint
from flask import request, redirect, url_for, render_template
from config import DB_URL


cadastrar_bp = Blueprint("cadastrar", __name__, template_folder="../templates")


@cadastrar_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        hostname = request.form["hostname"].upper().replace(" ", "")
        ip = request.form["ip"]
        device_type = request.form["type"].upper()
        site = request.form["site"].upper().replace(" ", "")
        now = datetime.now()

        conn = sqlite3.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO DEVICES (HOSTNAME, IP, TYPE, MONITORING_INTERVAL_SECONDS,
            MAX_PING_TIMEOUT_MILLISECONDS, SITE, STATUS, LAST_STATUS_CHANGE)
            VALUES (?, ?, ?, 60, 1000, ?, 2, ?)
        """,
            (hostname, ip, device_type, site, now),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("cadastrar.html")

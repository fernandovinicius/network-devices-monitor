from datetime import datetime
import re


def validate_ip(ip):
    return re.match(
        r"^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\."
        r"(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\."
        r"(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\."
        r"(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)$",
        ip,
    )


def validate_hostname(hostname):
    return re.match(r"^[A-Z0-9_.-]{1,50}$", hostname)


def validate_site(site):
    return re.match(r"^[A-Z0-9_]{1,20}$", site)


def validate_type(type):
    return re.match(r"^[A-Z0-9_.-]{1,30}$", type)


def validate_interval(value):
    return value in [30, 60, 90, 120, 150, 180, 210, 240, 270, 300]


def validate_timeout(value):
    return 100 <= value <= 5000


def validate_ping_count(value):
    return 1 <= value <= 10


def validate_datetime(dt_str):
    try:
        datetime.fromisoformat(dt_str)
    except:
        return False
    return True


def validate_device_data(data):
    errors = {}

    if not validate_ip(data.get("ip_address", "")):
        errors["ip_address"] = "Informe um IP no formato IPv4"

    if not validate_hostname(data.get("hostname", "")):
        errors["hostname"] = "Apenas caracteres no conjunto [A-Z0-9_.-]. Max: 50"

    if not validate_site(data.get("site", "")):
        errors["site"] = "Apenas caracteres no conjunto [A-Z0-9_.-]. Max: 20"

    if not validate_type(data.get("type", "")):
        errors["type"] = "Apenas caracteres no conjunto [A-Z0-9_.-]. Max: 30"

    if not validate_interval(data.get("monitoring_interval_seconds", 0)):
        errors["monitoring_interval_seconds"] = (
            "Valores aceitos: [30, 60, 120, 180, 300]"
        )

    if not validate_timeout(data.get("ping_timeout_milliseconds", 0)):
        errors["ping_timeout_milliseconds"] = (
            "Valores aceitos: [100, 250, 500, 1000, 2000]"
        )

    if not validate_ping_count(data.get("ping_count", 0)):
        errors["ping_count"] = "Valores aceitos: [1, 2, 3, 4]"

    return errors

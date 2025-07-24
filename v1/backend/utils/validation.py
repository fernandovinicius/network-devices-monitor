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
    return re.match(r"^^[A-Z0-9_.-]{1,30}$", type)


def validate_interval(value):
    return value in [30, 60, 90, 120, 150, 180, 210, 240, 270, 300]


def validate_timeout(value):
    return 100 <= value <= 5000


def validate_ping_count(value):
    return 1 <= value <= 10


def validate_device_data(data):
    errors = []

    if not validate_ip(data.get("ip_address", "")):
        errors.append("ip_address")
    if not validate_hostname(data.get("hostname", "")):
        errors.append("hostname")
    if not validate_site(data.get("site", "")):
        errors.append("site")
    if not validate_type(data.get("type", "")):
        errors.append("type")
    if not validate_interval(data.get("monitoring_interval_seconds", 0)):
        errors.append("monitoring_interval_seconds")
    if not validate_timeout(data.get("ping_timeout_milliseconds", 0)):
        errors.append("ping_timeout_milliseconds")
    if not validate_ping_count(data.get("ping_count", 0)):
        errors.append("ping_count")

    return errors

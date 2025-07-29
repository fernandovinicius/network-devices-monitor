from models.device_status import DeviceStatus


class Device:
    def __init__(
        self,
        id,
        ip_address,
        hostname,
        site,
        type,
        monitoring_interval_seconds=60,
        ping_timeout_milliseconds=1000,
        ping_count=4,
        monitoring_enabled=True,
        current_status=DeviceStatus.NOT_STARTED.value,
        last_status_change=None,
        current_history_id=None,
    ):
        self.id = id
        self.ip_address = ip_address
        self.hostname = hostname
        self.site = site
        self.type = type
        self.monitoring_interval_seconds = monitoring_interval_seconds
        self.ping_timeout_milliseconds = ping_timeout_milliseconds
        self.ping_count = ping_count
        self.monitoring_enabled = monitoring_enabled
        self.current_status = current_status
        self.last_status_change = last_status_change
        self.current_history_id = current_history_id

    def to_dict(self):
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "hostname": self.hostname,
            "site": self.site,
            "type": self.type,
            "monitoring_interval_seconds": self.monitoring_interval_seconds,
            "ping_timeout_milliseconds": self.ping_timeout_milliseconds,
            "ping_count": self.ping_count,
            "monitoring_enabled": self.monitoring_enabled,
            "current_status": self.current_status,
            "last_status_change": self.last_status_change,
            "current_history_id": self.current_history_id,
        }

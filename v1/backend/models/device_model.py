from models.device_status import DeviceStatus
from flask_restx import fields


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


DEVICE_DESC = {
    "id": fields.Integer(description="ID do dispositivo"),
    "ip_address": fields.String(required=True, description="Endereço IP"),
    "hostname": fields.String(required=True, description="Hostname"),
    "site": fields.String(required=True, description="Site"),
    "type": fields.String(required=True, description="Tipo"),
    "monitoring_interval_seconds": fields.Integer(
        description="Intervalo de monitoramento (segundos)"
    ),
    "ping_timeout_milliseconds": fields.Integer(description="Timeout do ping (ms)"),
    "ping_count": fields.Integer(description="Quantidade de pings"),
    "monitoring_enabled": fields.Boolean(description="Monitoramento habilitado"),
    "current_status": fields.String(description="Status atual"),
    "last_status_change": fields.String(description="Última alteração de status"),
    "current_history_id": fields.Integer(
        description="ID do histórico atual do dispositivo"
    ),
}


DEVICE_CREATION_DESC = {
    "ip_address": fields.String(
        required=True, description="Endereço IPv4. Ex: 192.168.0.1"
    ),
    "hostname": fields.String(required=True, description="Hostname [A-Z0-9_-.]"),
    "site": fields.String(required=True, description="Origem do ping [A-Z0-9_-.]"),
    "type": fields.String(required=True, description="Tipo do dispositivo [A-Z0-9_-.]"),
    "monitoring_interval_seconds": fields.Integer(
        required=False,
        description="Intervalo de monitoramento em segundos (padrão: 60 seg)",
        default=60,
    ),
    "ping_timeout_milliseconds": fields.Integer(
        required=False,
        description="Timeout do ping em milissegundos (padrão: 500 ms)",
        default=500,
    ),
    "ping_count": fields.Integer(
        required=False, description="Quantidade de pings (padrão: 1)", default=1
    ),
    "monitoring_enabled": fields.Boolean(
        required=False, description="Habilitar monitração (padrão: true)", default=True
    ),
}

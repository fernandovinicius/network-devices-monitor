from enum import Enum
from flask_restx import fields


class DeviceStatus(Enum):
    UP = 0
    DOWN = 1
    PAUSED = 2
    NOT_STARTED = 99


DEVICE_STATUS_DESC = {
    "UP": fields.Integer(
        example=DeviceStatus.UP.value, description="Dispositivo está online"
    ),
    "DOWN": fields.Integer(
        example=DeviceStatus.DOWN.value, description="Dispositivo está offline"
    ),
    "PAUSED": fields.Integer(
        example=DeviceStatus.PAUSED.value, description="Monitoração desabilitada"
    ),
    "NOT_STARTED": fields.Integer(
        example=DeviceStatus.NOT_STARTED.value,
        description="Monitoramento não iniciado",
    ),
}

from enum import Enum


class DeviceStatus(Enum):
    UP = 0
    DOWN = 1
    PAUSED = 2
    NOT_STARTED = 99

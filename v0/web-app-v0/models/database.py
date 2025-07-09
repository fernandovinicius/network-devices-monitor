from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Device:
    id: Optional[int]
    ip_address: str
    hostname: str
    site: str
    type: str
    monitoring_interval_seconds: int
    ping_timeout_milliseconds: int
    ping_count: int
    monitoring_enabled: bool
    current_status: int
    last_status_change: datetime
    current_history_id: Optional[int]

@dataclass
class MonitoringData:
    timestamp: datetime
    device_id: int
    status: int
    pack_sent: int
    pack_recv: int
    rtt_min: int
    rtt_max: int
    rtt_avg: int

@dataclass
class DeviceStatusHistory:
    id: Optional[int]
    device_id: int
    status: int
    last_status_change: datetime
    count: int

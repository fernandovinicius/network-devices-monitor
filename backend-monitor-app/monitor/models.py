from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    TIMESTAMP,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    ip = Column(String)
    hostname = Column(String)
    type = Column(String)
    site = Column(String)
    monitoring_interval_seconds = Column(Integer)
    ping_timeout_milliseconds = Column(Integer)
    ping_count = Column(Integer)
    monitoring_enabled = Column(Boolean)
    status = Column(Integer)
    last_status_change = Column(TIMESTAMP, nullable=False)


class MonitoringData(Base):
    __tablename__ = "monitoring_data"
    timestamp = Column(TIMESTAMP, nullable=False, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    status = Column(Integer)
    pack_sent = Column(Integer)
    pack_recv = Column(Integer)
    rtt_min = Column(Integer)
    rtt_max = Column(Integer)
    rtt_avg = Column(Integer)

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False)
    hostname = Column(String(50), nullable=False)
    site = Column(String(20), nullable=False)
    type = Column(String(30), nullable=False)
    monitoring_interval_seconds = Column(Integer, nullable=False)
    ping_timeout_milliseconds = Column(Integer, nullable=False)
    ping_count = Column(Integer, nullable=False)
    monitoring_enabled = Column(Boolean, nullable=False, default=True)
    current_status = Column(Integer)
    last_status_change = Column(TIMESTAMP)
    current_history_id = Column(Integer)

    # history_entries = relationship("DeviceStatusHistory", back_populates="device")
    # monitoring_data = relationship("MonitoringData", back_populates="device")


class DeviceStatusHistory(Base):
    __tablename__ = "devices_status_history"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer)
    last_status_change = Column(TIMESTAMP)
    count = Column(Integer)

    # device = relationship("Device", back_populates="history_entries")


class MonitoringData(Base):
    __tablename__ = "monitoring_data"

    timestamp = Column(TIMESTAMP)
    device_id = Column(Integer, ForeignKey("devices.id"), primary_key=True)
    status = Column(Integer)
    pack_sent = Column(Integer)
    pack_recv = Column(Integer)
    rtt_min = Column(Integer)
    rtt_max = Column(Integer)
    rtt_avg = Column(Integer)

    # device = relationship("Device", back_populates="monitoring_data")


def get_engine(database_url):
    return create_engine(database_url)


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

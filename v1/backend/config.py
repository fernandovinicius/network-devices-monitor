from loguru import logger


DATABASE_URL = (
    "C:/Desenvolvimento/network-devices-monitor/v0/backend/database/network_monitor.db"
)


def setup_logger():
    logger.add(
        "logs/monitoring.log", rotation="1 MB", retention="10 days", level="INFO"
    )

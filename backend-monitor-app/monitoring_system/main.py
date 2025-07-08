from monitoring.monitor import run_monitoring

if __name__ == "__main__":
    from loguru import logger

    logger.add("monitoring.log", rotation="1 day")
    run_monitoring()

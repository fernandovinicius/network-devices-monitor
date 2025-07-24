import sqlite3
from config import DATABASE_URL
from loguru import logger


def get_connection():
    try:
        conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
        logger.info("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except Exception as e:
        logger.error(f"Erro ao estabelecer conexão com o banco de dados: {e}")
        return None

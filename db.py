import mysql.connector
from config import Config
import os

def get_db():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASS,
        database=Config.DB_NAME,
        port=int(os.getenv("DB_PORT", 3306)),
        autocommit=True
    )

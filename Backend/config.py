import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_NAME = os.getenv("DB_NAME", "broken_tunes")

    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    HOST  = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT  = int(os.getenv("FLASK_PORT", 5000))

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

    @classmethod
    def db_params(cls) -> dict:
        return {
            "host":     cls.DB_HOST,
            "user":     cls.DB_USER,
            "password": cls.DB_PASS,
            "database": cls.DB_NAME,
        }
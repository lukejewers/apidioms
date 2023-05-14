import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    CSV_FILE_PATH: str = os.path.join("data", "idioms.csv")
    SQLITE_DB_NAME: str = os.path.join("api", "idioms.db")
    DATABASE_URI: str = f"sqlite:///{SQLITE_DB_NAME}"


settings = Settings()

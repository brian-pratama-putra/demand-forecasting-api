import os
from pydantic_settings import BaseSettings
from typing import ClassVar, List

class Settings(BaseSettings):
    STATUS_APP: str
    CLOUD_APPS: str
    SECRET_KEY: str
    SECRET_KEY_FORECAST_REQUEST: str
    SECRET_KEY_FORECAST_RESPONSE: str
    SECRET_KEY_FORECAST_HEADER: str
    
    POSTGRES_DB_USER: str
    POSTGRES_DB_PASS: str
    POSTGRES_DB_HOST: str
    POSTGRES_DB_PORT: str
    POSTGRES_DB_DATA: str

    POSTGRES_POOL_MIN: int = 1
    POSTGRES_POOL_MAX: int = 10

    CONNECTION_STRING_REDIS: str
    
    DEBUG: bool = True
    API_VERSION: str

    class Config:
        env_file = ".env"

settings = Settings()

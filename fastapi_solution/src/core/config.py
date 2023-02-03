import os
from logging import config as logging_config
from dotenv import load_dotenv
from pydantic import BaseSettings, Field
# Применяем настройки логирования
from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)
load_dotenv()


class Settings(BaseSettings):
    project_name: str = Field(..., env="PROJECT_NAME")
    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: str = Field(..., env="REDIS_PORT")
    elastic_host: str = Field(..., env="ELASTIC_HOST")
    elastic_port: str = Field(..., env="ELASTIC_PORT")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    redis_cache_time: int = Field(..., env="REDIS_CACHE_TIME")

    class Config:
        env_file = '.env.api'
        env_file_encoding = 'utf-8'


settings = Settings()

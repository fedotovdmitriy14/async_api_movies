import os
from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
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


settings = TestSettings()

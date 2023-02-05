from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: str = Field("6379", env="REDIS_PORT")
    elastic_host: str = Field("127.0.0.1", env="ELASTIC_HOST")
    elastic_port: str = Field("9200", env="ELASTIC_PORT")
    fastapi_port: str = Field("8081", env="ELASTIC_PORT")

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


test_settings = TestSettings()

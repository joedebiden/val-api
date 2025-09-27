from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field
from fastapi_mqtt import MQTTConfig, FastMQTT

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., alias="DATABASE_URL")
    DATABASE_URL_TEST: str = Field(..., alias="DATABASE_URL_TEST")
    SECRET_KEY: str = Field(..., alias="SECRET_KEY")

    POSTGRES_DB: Optional[str] = Field(None, alias="POSTGRES_DB")
    POSTGRES_USER: Optional[str] = Field(None, alias="POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = Field(None, alias="POSTGRES_PASSWORD")

    class Config:
        env_file = ".env"
        populate_by_name = True

settings = Settings()

# mqtt broker config
fast_mqtt = FastMQTT(config=MQTTConfig())

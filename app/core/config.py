from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., alias="DATABASE_URL")
    DATABASE_URL_TEST: str = Field(..., alias="DATABASE_URL_TEST")
    SECRET_KEY: str = Field(..., alias="SECRET_KEY")

    class Config:
        env_file = ".env"
        populate_by_name = True

settings = Settings()

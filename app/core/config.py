from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., alias="DATABASE_URL")
    DATABASE_URL_TEST: str = Field(..., alias="DATABASE_URL_TEST")
    SECRET_KEY: str = Field(..., alias="SECRET_KEY")
    POSTGRES_DB: str = Field(..., alias="POSTGRES_DB")
    POSTGRES_USER: str = Field(..., alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., alias="POSTGRES_PASSWORD")

    class Config:
        env_file = ".env"
        populate_by_name = True

settings = Settings()

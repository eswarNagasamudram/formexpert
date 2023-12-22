from pydantic_settings import BaseSettings
from typing import Optional

class AppConfig(BaseSettings):

    GOOGLE_APPLICATION_CREDENTIALS :str
    class Config:
        env_file = ".env"  
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings() # type: ignore
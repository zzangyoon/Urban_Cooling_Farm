from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./urban_cooling.db"

    # Climate Platform API
    CLIMATE_API_BASE_URL: str = "https://api.gg-climate.kr"
    CLIMATE_REMOVED: str = ""

    # App Settings
    APP_NAME: str = "Urban Cooling Farm"
    DEBUG: bool = True

    # Mock Mode (실제 API 연동 전까지 사용)
    USE_MOCK_DATA: bool = True

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

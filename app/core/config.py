from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/visionnest"
    SECRET_KEY: str = "change-this-to-a-secure-random-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_V1_STR: str = "/api/v1"
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    STATIC_DIR: str = "static"
    AUDIO_DIR: str = "static/audio"
    TTS_LANG_MAP: dict = {
        "vi": "vi",
        "en": "en",
        "zh": "zh-CN",
        "ja": "ja",
        "ko": "ko",
    }

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()

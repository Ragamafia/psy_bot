from __future__ import annotations

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_SETTINGS_CONFIG = SettingsConfigDict(
    extra="ignore",
    env_file="env/.env",
    env_file_encoding="utf-8",
)


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(**BASE_SETTINGS_CONFIG, env_prefix="BOT_")
    token: SecretStr


class PsychologistSettings(BaseSettings):
    model_config = SettingsConfigDict(**BASE_SETTINGS_CONFIG, env_prefix="PSY_")

    name: str
    tg_username: str
    phone: str
    city: str

    @property
    def tg_link(self) -> str:
        return f"https://t.me/{self.tg_username.lstrip('@')}"


class Settings:
    def __init__(self) -> None:
        self.bot = BotSettings()
        self.psy = PsychologistSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()

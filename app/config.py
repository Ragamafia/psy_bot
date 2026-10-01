from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Картинки эмоций лежат по ключу эмоции: anger.jpg, fear.jpg…
EMOTION_IMAGES_DIR = PROJECT_ROOT / "static" / "emotions"
# Фон и шрифт карточек «как себе помочь»: текст техники рисуется поверх фона.
HELP_BACKGROUND = PROJECT_ROOT / "static" / "background.jpg"
HELP_FONT = PROJECT_ROOT / "static" / "fonts" / "Lora.ttf"

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
    # Относительный путь считается от корня проекта, а не от папки запуска.
    photo: Path = Path("static/nas.jpg")

    @property
    def photo_path(self) -> Path:
        return self.photo if self.photo.is_absolute() else PROJECT_ROOT / self.photo

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

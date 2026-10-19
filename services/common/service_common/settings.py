"""Base class of every service's settings."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

PROJECT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
"""``<repository>/.env`` wherever a service is started from (absent in containers)."""


class ServiceSettings(BaseSettings):
    """Settings from the environment and the project's ``.env`` file.

    ``.env`` wins over variables inherited from the machine: a stray
    ``OPENAI_API_KEY`` in the user's environment must not silently replace the
    project's key. In Docker there is no ``.env`` file inside the container —
    compose passes the same values as environment variables.
    """

    model_config = SettingsConfigDict(env_file=PROJECT_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, dotenv_settings, env_settings, file_secret_settings

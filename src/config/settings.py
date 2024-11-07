from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.constants import ENV
from utils.env_utils import find_env_file_full

env_file_full = find_env_file_full(ENV)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file_full,
        case_sensitive=True,
        extra="ignore",
    )

    LOG_LEVEL: str = Field(default="INFO")
    model: str = Field(alias="LLM_MODEL_NAME", default=...)
    api_base: str = Field(alias="LLM_API_BASE", default=None)
    SEARCH_ENDPOINT: str = Field(default=...)
    SEARCH_API_KEY: str = Field(default=...)


settings = Settings()

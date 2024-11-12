from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Read .env if it exists to define the environment ENV
class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )

    ENV: str = Field(default="development")


env_settings = EnvSettings()

ENV = env_settings.ENV

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    LLM_PROVIDER : Literal["openai", "deepseek", "anthropic"] = "openai"

    OPENAI_API_KEY: SecretStr | None = None
    DEEPSEEK_API_KEY: SecretStr | None = None
    ANTHROPIC_API_KEY: SecretStr | None = None

    LLM_DEFAULT_MODEL: str = Field(default = "gpt-4o-mini")
    LLM_TIMEOUT: int = Field(default = 30, description = "Global timeout in seconds")
    LLM_MAX_RETRIES: int = Field(default = 3, description  = "MAX retry attempts")
    LLM_RPM: int = Field(default = 60, description = "Max requests per minutes")
    LLM_MAX_CONCURRENT: int = Field(default = 5, description = "Max Concreecy at same time")

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

settings = Settings()


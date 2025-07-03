import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = (
        "gpt-4-turbo"  # Max Context Length 128,000 tokens (input + output combined), good for demo
    )
    OPENAI_MAX_TOKENS: int = 4096  # 4K tokens for LLM OP
    OPENAI_TEMPERATURE: float = (
        0.2  # Balanced — slight creativity, mostly safe, but can be configured
    )

    # API Configuration
    DEBUG: bool = False
    MAX_INPUT_LENGTH: int = (
        20000  # It should allow user to input large paragraphs, enough for demo. Approx 5K tokens for IP
    )

    # For future rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # 1 hour

    # Security
    API_KEY_HEADER: str = "X-API-Key"
    ALLOWED_ORIGINS: list = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    BANK_API_URL: str = (
        "https://bank.api"  # в нашем контексте не используем, но оставляем тут на будущее
    )

    model_config = ConfigDict(env_file=".env")

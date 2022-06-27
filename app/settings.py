from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    debug: bool = False
    telegram_logging: bool = True
    HH_EMAIL_LOGIN: SecretStr
    HH_PASSWORD: SecretStr
    TG_API_KEY: SecretStr
    TG_CHAT_ID: int
    COOKIES_PATH: str = "/var/tmp/hh_resume_raising/cookies.pkl"

    class Config:
        env_file = ".env"


settings: Settings = Settings()


def get_env() -> Settings:
    return settings


__all__ = ["get_env", "Settings"]

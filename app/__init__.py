import logging
import sys
from logging import StreamHandler

from pydantic import BaseSettings
from tglogging import TelegramLogHandler


class Settings(BaseSettings):
    debug: bool = False
    telegram_logging: bool = False
    HH_EMAIL_LOGIN: str
    HH_PASSWORD: str
    TG_API_KEY: str
    TG_CHAT_ID: int

    class Config:
        env_file = ".env"


settings: Settings = Settings()


def get_env() -> Settings:
    return settings


def get_console_handler() -> StreamHandler:
    console_handler: StreamHandler = StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter(
            fmt=f"%(asctime)s — %(name)s — %(levelname)s — "
            f"%(funcName)s:%(lineno)d — %(message)s"
        )
    )
    return console_handler


def get_tg_handler() -> TelegramLogHandler:
    if settings.telegram_logging:
        tg_handler: TelegramLogHandler = TelegramLogHandler(
            token=settings.TG_API_KEY,
            log_chat_id=settings.TG_CHAT_ID,
            # update_interval=5,
            # minimum_lines=1,
            # pending_logs=200000,
        )
        tg_handler.setLevel(logging.INFO)
        tg_handler.setFormatter(logging.Formatter(f"%(message)s"))
        return tg_handler
    else:
        pass


def get_logger(logger_name, only_console: bool = True) -> logging.Logger:
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    logger.addHandler(get_console_handler())

    if not only_console and settings.telegram_logging:
        logger.addHandler(get_tg_handler())

    logger.propagate = False
    return logger


__all__ = ["get_logger", "settings"]

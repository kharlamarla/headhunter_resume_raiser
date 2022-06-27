import logging
import sys
from logging import StreamHandler
from typing import Literal

from tglogging import TelegramLogHandler as TelegramLogHandlerBase


DEFAULT_PAYLOAD = {"disable_web_page_preview": True, "parse_mode": "Markdown"}
LOGGER_LEVELS = Literal[0, 10, 20, 30, 50]


class TelegramLogHandler(TelegramLogHandlerBase):
    async def initialise(self):
        payload = DEFAULT_PAYLOAD.copy() | {"chat_id": self.log_chat_id}
        payload["text"] = "```Initializing```"

        url = f"{self.base_url}/sendMessage"
        res = await self.send_request(url, payload)
        if res.get("ok"):
            result = res.get("result")
            self.message_id = result.get("message_id")
        else:
            await self.handle_error(res)

    async def send_message(self, message):
        payload = DEFAULT_PAYLOAD.copy() | {"chat_id": self.log_chat_id}
        payload["text"] = f"{message}"
        url = f"{self.base_url}/sendMessage"
        res = await self.send_request(url, payload)
        if res.get("ok"):
            result = res.get("result")
            self.message_id = result.get("message_id")
        else:
            await self.handle_error(res)

    async def edit_message(self, message):
        payload = DEFAULT_PAYLOAD.copy() | {"chat_id": self.log_chat_id}
        payload["message_id"] = self.message_id
        payload["text"] = f"{message}"
        url = f"{self.base_url}/editMessageText"
        res = await self.send_request(url, payload)
        if not res.get("ok"):
            await self.handle_error(res)


class Logger:
    def __init__(
        self,
        logger_name: str | None,
        logger_level: LOGGER_LEVELS = logging.DEBUG,
    ) -> None:
        self.logger_name: str = logger_name
        self.logger_level = logger_level

        self.logger: logging.Logger = logging.getLogger(logger_name)
        self.logger.setLevel(logger_level)
        self.logger.propagate = False

    def __get_console_handler(
        self,
        logger_level: LOGGER_LEVELS | None = logging.NOTSET,
    ) -> StreamHandler:
        console_handler = StreamHandler(sys.stdout)

        if logger_level and self.logger_level != logger_level:
            console_handler.setLevel(self.logger_level)

        console_handler.setFormatter(
            logging.Formatter(
                fmt=f"%(asctime)s — %(name)s — %(levelname)s — "
                f"%(funcName)s:%(lineno)d — %(message)s"
            )
        )
        return console_handler

    def __get_tg_handler(
        self,
        token: str,
        chat_id: int,
        logger_level: LOGGER_LEVELS | None = logging.NOTSET,
    ) -> TelegramLogHandler:
        tg_handler = TelegramLogHandler(token=token, log_chat_id=chat_id)

        if logger_level and self.logger_level != logger_level:
            tg_handler.setLevel(logger_level)

        tg_handler.setFormatter(logging.Formatter("%(message)s"))
        return tg_handler

    def get(
        self,
        only_console: bool = True,
        tg_logger: bool = False,
        tg_token: str | None = None,
        tg_chat_id: int | None = None,
    ) -> logging.Logger:

        self.logger.addHandler(
            self.__get_console_handler(logger_level=logging.DEBUG)
        )

        if only_console:
            return self.logger
        
        if tg_logger:
            self.logger.addHandler(
                self.__get_tg_handler(
                    token=tg_token,
                    chat_id=tg_chat_id,
                    logger_level=logging.INFO
                )
            )
        return self.logger


__all__ = ["Logger"]

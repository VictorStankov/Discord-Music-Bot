from discord import Message
from bot.model import BasePlayItem


class LocalPlayItem(BasePlayItem):
    def __init__(
            self,
            message: Message,
            length: int,
            path: str
    ):
        super().__init__(message=message, length=length, path=path)

from discord import Message


class BasePlayItem:
    def __init__(
            self,
            message: Message,
            length: int,
            path: str
    ):
        self.message: Message = message
        self.length: int = length
        self.path: str = path

from discord import Message
from bot.model import BasePlayItem


class OnlinePlayItem(BasePlayItem):
    def __init__(
            self,
            message: Message,
            length: int,
            path: str,
            title: str,
            thumbnail: str,
            video_url: str
    ):
        super().__init__(message=message, length=length, path=path)
        self.title: str = title
        self.thumbnail: str = thumbnail  # URL for thumbnail.
        self.video_url: str = video_url  # Original URL for video.

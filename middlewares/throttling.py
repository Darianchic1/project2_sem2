from aiogram import BaseMiddleware
from aiogram.types import Update
from datetime import datetime, timedelta

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.5):
        self.limit = timedelta(seconds=limit)
        self.last_update = datetime.now() - self.limit
        super().__init__()

    async def __call__(self, handler, event: Update, data: dict):
        now = datetime.now()
        if now - self.last_update < self.limit:
            return
        self.last_update = now
        return await handler(event, data)
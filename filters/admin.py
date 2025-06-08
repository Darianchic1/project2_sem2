from aiogram.filters import BaseFilter
from aiogram.types import Message
from config.settings import settings

class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        """Проверяет, является ли пользователь администратором"""
        return message.from_user.id in settings.admin_ids
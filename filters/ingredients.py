from aiogram.filters import BaseFilter
from aiogram.types import Message

class HasIngredientsFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        """Проверяет, содержит ли сообщение ингредиенты"""
        if not message.text:
            return False
            
        # Проверяем команду /find_by_ingredients и наличие ингредиентов после нее
        if message.text.startswith('/find_by_ingredients'):
            parts = message.text.split(maxsplit=1)
            return len(parts) > 1 and len(parts[1].strip()) > 0
        return False
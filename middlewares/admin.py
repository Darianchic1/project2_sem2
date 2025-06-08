from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Any, Awaitable, Callable, Dict
from services.database import Database
from config.settings import settings

class AdminMiddleware(BaseMiddleware):
    """Middleware для проверки прав администратора"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем ID пользователя
        user_id = event.from_user.id
        
        # Проверяем является ли пользователь администратором
        admin_ids = getattr(settings, 'admin_ids', [])
        if isinstance(admin_ids, str):
            admin_ids = [int(x.strip()) for x in admin_ids.split(',') if x.strip().isdigit()]
        
        data['is_admin'] = user_id in admin_ids
        
        return await handler(event, data)

class BanMiddleware(BaseMiddleware):
    """Middleware для проверки блокировки пользователей"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        db: Database = data.get('db')
        if not db:
            return await handler(event, data)
        
        user_id = event.from_user.id
        
        # Проверяем заблокирован ли пользователь
        if await db.is_user_banned(user_id):
            if isinstance(event, Message):
                await event.answer("🚫 Вы заблокированы и не можете использовать бота.")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Вы заблокированы", show_alert=True)
            return  # Прерываем выполнение
        
        return await handler(event, data)

class UserTrackingMiddleware(BaseMiddleware):
    """Middleware для отслеживания пользователей и статистики"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        db: Database = data.get('db')
        if not db:
            return await handler(event, data)
        
        user = event.from_user
        
        # Добавляем или обновляем пользователя
        user_data = {
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        await db.add_or_update_user(user_data)
        
        # Увеличиваем счетчик команд для сообщений
        if isinstance(event, Message):
            await db.increment_stat('total_commands')
        
        return await handler(event, data)

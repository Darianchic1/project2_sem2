from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from services.database import Database
from states.admin import AdminStates
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("stats"))
async def show_stats(message: Message, is_admin: bool = False):
    """Показывает статистику бота (только для админов)"""
    if not is_admin:
        await message.answer("🚫 Эта команда доступна только администраторам")
        return
        
    try:
        db = Database()
        stats = await db.get_bot_stats()
        
        if not stats:
            await message.answer("📊 Статистика пока недоступна")
            return
            
        stats_text = (
            "📊 **Статистика бота**\n\n"
            f"👥 Всего пользователей: **{stats['total_users']}**\n"
            f"🚫 Заблокированных: **{stats['banned_users']}**\n"
            f"⭐ Всего избранных: **{stats['total_favorites']}**\n"
            f"📝 Всего команд: **{stats['total_commands']}**\n"
            f"🎲 Случайных рецептов: **{stats['random_recipe_requests']}**\n"
            f"🔍 Поисков по ингредиентам: **{stats['ingredient_searches']}**\n"
            f"⭐ Просмотров избранного: **{stats['favorites_views']}**\n\n"
            f"🕐 Обновлено: {stats['last_updated'].strftime('%d.%m.%Y %H:%M')}"
        )
        
        await message.answer(stats_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await message.answer("⚠️ Ошибка получения статистики")

@router.message(Command("ban"))
async def start_ban(message: Message, state: FSMContext, is_admin: bool = False):
    """Начинает процесс блокировки пользователя"""
    if not is_admin:
        await message.answer("🚫 Эта команда доступна только администраторам")
        return
    
    await message.answer(
        "🚫 **Блокировка пользователя**\n\n"
        "Введите ID пользователя для блокировки.\n"
        "Для отмены используйте /cancel"
    )
    await state.set_state(AdminStates.waiting_ban_user_id)

@router.message(AdminStates.waiting_ban_user_id)
async def process_ban_user_id(message: Message, state: FSMContext, is_admin: bool = False):
    """Обрабатывает ID пользователя для блокировки"""
    if not is_admin:
        await message.answer("🚫 Эта команда доступна только администраторам")
        await state.clear()
        return
    
    try:
        user_id = int(message.text.strip())
        
        db = Database()
        
        # Проверяем существует ли пользователь
        is_banned = await db.is_user_banned(user_id)
        if is_banned:
            await message.answer(f"⚠️ Пользователь {user_id} уже заблокирован")
            await state.clear()
            return
        
        # Блокируем пользователя
        success = await db.ban_user(user_id)
        
        if success:
            await message.answer(f"🚫 Пользователь {user_id} заблокирован")
        else:
            await message.answer(f"⚠️ Не удалось заблокировать пользователя {user_id}")
        
        await state.clear()
        
    except ValueError:
        await message.answer("⚠️ Введите корректный числовой ID пользователя")
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        await message.answer("⚠️ Ошибка при блокировке пользователя")
        await state.clear()

@router.message(Command("unban"))
async def start_unban(message: Message, state: FSMContext, is_admin: bool = False):
    """Начинает процесс разблокировки пользователя"""
    if not is_admin:
        await message.answer("🚫 Эта команда доступна только администраторам")
        return
    
    await message.answer(
        "✅ **Разблокировка пользователя**\n\n"
        "Введите ID пользователя для разблокировки.\n"
        "Для отмены используйте /cancel"
    )
    await state.set_state(AdminStates.waiting_unban_user_id)

@router.message(AdminStates.waiting_unban_user_id)
async def process_unban_user_id(message: Message, state: FSMContext, is_admin: bool = False):
    """Обрабатывает ID пользователя для разблокировки"""
    if not is_admin:
        await message.answer("🚫 Эта команда доступна только администраторам")
        await state.clear()
        return
    
    try:
        user_id = int(message.text.strip())
        
        db = Database()
        
        # Разблокируем пользователя
        success = await db.unban_user(user_id)
        
        if success:
            await message.answer(f"✅ Пользователь {user_id} разблокирован")
        else:
            await message.answer(f"⚠️ Не удалось разблокировать пользователя {user_id}")
        
        await state.clear()
        
    except ValueError:
        await message.answer("⚠️ Введите корректный числовой ID пользователя")
    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        await message.answer("⚠️ Ошибка при разблокировке пользователя")
        await state.clear()

@router.message(Command("cancel"))
async def cancel_admin_action(message: Message, state: FSMContext, is_admin: bool = False):
    """Отменяет текущее админ-действие"""
    if not is_admin:
        return
    
    await state.clear()
    await message.answer("❌ Действие отменено")


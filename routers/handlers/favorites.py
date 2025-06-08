from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from services.database import Database
from keyboards.inline import favorites_keyboard, delete_favorites_keyboard
import logging

router = Router()
logger = logging.getLogger(__name__)

async def get_recipe_data_from_message(message_text: str) -> dict:
    """Извлекает данные рецепта из текста сообщения с учетом вашего формата"""
    lines = [line.strip() for line in message_text.split('\n') if line.strip()]
    
    data = {
        'title': '',
        'image': None,
        'source_url': None
    }
    
    # Обрабатываем каждую строку
    for line in lines:
        if '🍴' in line:  # Название рецепта
            data['title'] = line.split('🍴')[-1].strip()
        elif '📷' in line:  # Изображение
            data['image'] = line.split('📷')[-1].strip()
        elif '🔗' in line:  # Ссылка
            data['source_url'] = line.split('🔗')[-1].strip()
    
    return data

@router.message(Command("favorites"))
async def show_favorites_command(message: Message):
    """Показывает список избранных рецептов по команде"""
    # Увеличиваем счетчик просмотров избранного
    db = Database()
    await db.increment_stat('favorites_views')
    await show_favorites(message)

async def show_favorites(message_or_callback):
    """Показывает список избранных рецептов"""
    try:
        db = Database()
        user_id = message_or_callback.from_user.id
        
        favorites = await db.get_favorites(user_id)
        
        if not favorites:
            text = ("⭐ У вас пока нет избранных рецептов.\n"
                   "Чтобы добавить рецепт, нажмите кнопку 'Сохранить' при просмотре любого рецепта")
            keyboard = favorites_keyboard()
        else:
            response = []
            for i, recipe in enumerate(favorites[:10], 1):
                item = f"{i}. {recipe.get('title', 'Без названия')}"
                if recipe.get('image'):
                    item += f"\n📷 {recipe['image']}"
                if recipe.get('source_url'):
                    item += f"\n🔗 {recipe['source_url']}"
                response.append(item)
            
                text = "⭐ Ваши избранные рецепты:\n\n" + "\n\n".join(response)
                keyboard = favorites_keyboard(has_recipes=True)
        
        # Проверяем тип объекта - Message или CallbackQuery
        if isinstance(message_or_callback, Message):
            await message_or_callback.answer(text, reply_markup=keyboard, disable_web_page_preview=True)
        else: 
            await message_or_callback.message.edit_text(text, reply_markup=keyboard, disable_web_page_preview=True)
            
    except Exception as e:
        logger.error(f"Error showing favorites: {str(e)}", exc_info=True)
        error_text = "⚠️ Ошибка при загрузке избранного. Попробуйте позже."
        if isinstance(message_or_callback, Message):
            await message_or_callback.answer(error_text)
        else:  
            await message_or_callback.message.edit_text(error_text)

@router.callback_query(F.data.startswith("save_"))
async def save_to_favorites(callback: CallbackQuery):
    try:
        db = Database()
        user_id = callback.from_user.id
        recipe_id = int(callback.data.split("_")[1])
        
        # Получаем данные из сообщения
        recipe_data = await get_recipe_data_from_message(callback.message.text)
        recipe_data['id'] = recipe_id
        
        # Логирование для отладки
        logger.debug(f"Extracted recipe data: {recipe_data}")
        
        # Проверка обязательных полей
        if not recipe_data.get('title'):
            raise ValueError("Не удалось извлечь название рецепта")
        if not recipe_data.get('id'):
            raise ValueError("Отсутствует ID рецепта")
            
        # Сохраняем в базу
        if await db.add_favorite(user_id, recipe_data):
            await callback.answer("✅ Рецепт добавлен в избранное", show_alert=True)
        else:
            await callback.answer("ℹ️ Рецепт уже в избранном", show_alert=True)
            
    except ValueError as e:
        logger.error(f"Ошибка данных: {str(e)}\nПолный текст сообщения: {callback.message.text}")
        await callback.answer(f"⚠️ {str(e)}", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка сохранения: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Ошибка при сохранении", show_alert=True)

# Обработчик показа главного меню
@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Показывает главное меню - отправляет НОВОЕ сообщение"""
    welcome_text = (
        "👨‍🍳 Главное меню бота для поиска рецептов.\n\n"
        "🔍 Доступные команды:\n"
        "/find_by_ingredients - Поиск по ингредиентам\n"
        "/random - Случайный рецепт\n"
        "/favorites - Избранные рецепты\n"
        "/help - Помощь"
    )
    await callback.message.answer(welcome_text)

# Обработчик кнопки удаления избранного
@router.callback_query(F.data == "delete_favorites")
async def delete_favorites_menu(callback: CallbackQuery):
    """Показывает меню удаления избранного"""
    try:
        db = Database()
        user_id = callback.from_user.id
        favorites = await db.get_favorites(user_id)
        
        if not favorites:
            await callback.answer("У вас нет избранных рецептов для удаления", show_alert=True)
            return
            
        text = "🗑️ Выберите рецепт для удаления:\n\n"
        for i, recipe in enumerate(favorites[:10], 1):
            text += f"{i}. {recipe.get('title', 'Без названия')}\n"
            
        await callback.message.edit_text(
            text,
            reply_markup=delete_favorites_keyboard(favorites)
        )
    except Exception as e:
        logger.error(f"Error showing delete menu: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Ошибка при загрузке меню удаления")

# Обработчик удаления конкретного рецепта
@router.callback_query(F.data.startswith("delete_fav_"))
async def remove_from_favorites(callback: CallbackQuery):
    """Удаляет рецепт из избранного"""
    try:
        db = Database()
        user_id = callback.from_user.id
        recipe_id = int(callback.data.split("_")[2])
        
        if await db.remove_favorite(user_id, recipe_id):
            await callback.answer("🗑️ Рецепт удален из избранного")
            # Возвращаемся к списку избранного - ОБНОВЛЯЕМ сообщение
            await show_favorites(callback)
        else:
            await callback.answer("⚠️ Рецепт не найден в избранном")
    except Exception as e:
        logger.error(f"Error removing favorite: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Ошибка при удалении")

# Обработчик возврата к избранному
@router.callback_query(F.data == "favorites_back")
async def favorites_back(callback: CallbackQuery):
    """Возвращает к списку избранного - ОБНОВЛЯЕТ сообщение"""
    await show_favorites(callback)

# Обработчик удаления всех избранных
@router.callback_query(F.data == "delete_all_favorites")
async def delete_all_favorites(callback: CallbackQuery):
    """Удаляет все избранные рецепты"""
    try:
        db = Database()
        user_id = callback.from_user.id
        
        # Удаляем все избранные
        deleted_count = await db.remove_all_favorites(user_id)
        
        if deleted_count == 0:
            await callback.answer("У вас нет избранных рецептов для удаления", show_alert=True)
            return
        
        await callback.answer(f"🗑️ Удалено {deleted_count} рецептов из избранного", show_alert=True)
        # Возвращаемся к списку избранного (который теперь пустой)
        await show_favorites(callback)
        
    except Exception as e:
        logger.error(f"Error deleting all favorites: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Ошибка при удалении всех избранных", show_alert=True)
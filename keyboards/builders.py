from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

def main_menu_keyboard():
    """Главное меню бота"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔍 Поиск по ингредиентам")
    builder.button(text="🎲 Случайный рецепт")
    builder.button(text="⭐ Избранное")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
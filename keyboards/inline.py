from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder

def diet_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Вегетарианское", callback_data="diet_vegetarian")
    builder.button(text="Веганское", callback_data="diet_vegan")
    builder.button(text="Без диеты", callback_data="diet_none")
    builder.button(text="🏠 В меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_recipe_keyboard(recipe_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Сохранить", callback_data=f"save_{recipe_id}")
    builder.button(text="🏠 В меню", callback_data="main_menu")
    builder.adjust(1)  # Располагаем кнопки вертикально
    return builder.as_markup()

def favorites_keyboard(has_recipes=False):
    builder = InlineKeyboardBuilder()
    
    if has_recipes:
        builder.button(text="🗑️ Удалить", callback_data="delete_favorites")
    
    builder.button(text="🏠 В меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def delete_favorites_keyboard(favorites_list):
    """Создает клавиатуру с номерами блюд для удаления"""
    builder = InlineKeyboardBuilder()
    
    for i, favorite in enumerate(favorites_list, 1):
        builder.button(text=f"🗑️ {i}", callback_data=f"delete_fav_{favorite['recipe_id']}")
    
    builder.button(text="🗑️ Удалить всё", callback_data="delete_all_favorites")
    builder.button(text="🔙 Назад", callback_data="favorites_back")
    builder.button(text="🏠 В меню", callback_data="main_menu")
    builder.adjust(3, 1)  # По 3 кнопки удаления в ряд, остальные по одной
    return builder.as_markup()

def ingredients_keyboard():
    builder = InlineKeyboardBuilder()
    
    popular_ingredients = [
        "яйца", "молоко", "мука", 
        "курица", "рис", "картофель",
        "помидоры", "сыр", "лук"
    ]
    
    for ingredient in popular_ingredients:
        builder.button(text=ingredient.capitalize(), callback_data=f"ingredient_{ingredient}")
    
    builder.button(text="⚙️ Свой вариант", callback_data="custom_ingredient")
    builder.button(text="🏠 В меню", callback_data="main_menu")
    builder.adjust(3, 1)  # По 3 ингредиента в ряд, остальные кнопки по одной
    return builder.as_markup()

def confirm_keyboard(action: str):
    """Создает клавиатуру подтверждения действия"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"confirm_{action}")
    builder.button(text="❌ Отменить", callback_data=f"cancel_{action}")
    builder.adjust(2)
    return builder.as_markup()
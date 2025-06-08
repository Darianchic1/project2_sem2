from aiogram.fsm.state import StatesGroup, State

class RandomRecipe(StatesGroup):
    """Состояния для получения случайного рецепта"""
    choosing_diet = State()  # Ожидание выбора типа диеты (это используете вы)
    waiting_for_category = State()  # Ожидание выбора категории (если нужно)
    waiting_for_ingredients = State()  # Ожидание ингредиентов (если нужно)
    showing_recipe = State()  # Состояние показа рецепта (если нужно)
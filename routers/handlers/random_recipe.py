from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from services.api_client import SpoonacularAPI
from keyboards.inline import diet_keyboard, get_recipe_keyboard
from aiogram.fsm.context import FSMContext
from states.random_recipe import RandomRecipe
from config.settings import settings  # Импортируем настройки
from services.database import Database

router = Router()
api = SpoonacularAPI(api_key=settings.spoonacular_api_key)

@router.message(Command("random"))
async def random_recipe_start(message: Message, state: FSMContext):
    # Увеличиваем счетчик запросов случайных рецептов
    db = Database()
    await db.increment_stat('random_recipe_requests')
    
    await message.answer(
        "Выберите тип диеты:",
        reply_markup=diet_keyboard()
    )
    await state.set_state(RandomRecipe.choosing_diet)

@router.callback_query(RandomRecipe.choosing_diet, F.data.startswith("diet_"))
async def random_recipe_selected(callback: CallbackQuery, state: FSMContext, db: Database):
    diet = callback.data.split("_")[1]
    recipe = await api.get_random_recipe(diet if diet != "none" else "")
    
    if not recipe or "title" not in recipe:
        print(f"Ошибка: рецепт не получен. Ответ API: {recipe}")
        await callback.message.answer("Ошибка: рецепт не найден или API не отвечает.")
        await state.clear()
        return
    
    # Формируем сообщение с кнопкой сохранения
    message_text = (
        f"🎲 Случайный рецепт:\n\n"
        f"🍴 {recipe['title']}\n"
        f"📷 {recipe['image']}\n"
        f"🔗 {recipe.get('sourceUrl', 'ссылка отсутствует')}"
    )
    
    # Отправляем сообщение с кнопкой
    await callback.message.answer(
        message_text,
        reply_markup=get_recipe_keyboard(recipe['id']),
        disable_web_page_preview=False
    )
    await state.clear()



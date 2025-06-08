from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from services.api_client import SpoonacularAPI
from keyboards.inline import ingredients_keyboard, get_recipe_keyboard
from config.settings import settings
from aiogram.fsm.context import FSMContext
from states.ingredients import IngredientsState
import logging

router = Router()
api = SpoonacularAPI(api_key=settings.spoonacular_api_key)
logger = logging.getLogger(__name__)

@router.message(Command("find_by_ingredients"))
async def find_by_ingredients_start(message: Message, state: FSMContext):
    # Увеличиваем счетчик поисков по ингредиентам
    from services.database import Database
    db = Database()
    await db.increment_stat('ingredient_searches')
    
    await message.answer(
        "Выберите ингредиент из списка:",
        reply_markup=ingredients_keyboard()
    )

@router.callback_query(F.data.startswith("ingredient_"))
async def process_ingredient(callback: CallbackQuery):
    ingredient = callback.data.split("_")[1]
    try:
        await callback.answer()
        recipes = await api.search_by_ingredients(ingredient)
        
        if not recipes:
            return await callback.message.answer(f"😔 Рецепты с {ingredient} не найдены")
            
        for recipe in recipes[:5]:
            recipe_info = (
                f"🍴 {recipe['title']}\n"
                f"🔹 Использовано ингредиентов: {recipe['usedIngredientCount']}\n"
            )
            
            if recipe.get('image'):
                recipe_info += f"📷 {recipe['image']}\n"
            
            source_url = recipe.get('sourceUrl', f"https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-')}-{recipe['id']}")
            recipe_info += f"🔗 {source_url}"
            
            await callback.message.answer(
                recipe_info,
                reply_markup=get_recipe_keyboard(recipe['id']),
                disable_web_page_preview=False
            )
            
    except Exception as e:
        logger.error(f"Ошибка API: {e}")
        await callback.message.answer("⚠️ Ошибка при поиске рецептов")

@router.callback_query(F.data == "custom_ingredient")
async def custom_ingredient(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ваш ингредиент:")
    await state.set_state(IngredientsState.waiting_for_ingredient)

@router.message(IngredientsState.waiting_for_ingredient)
async def custom_ingredient_received(message: Message, state: FSMContext):
    await process_ingredient(message, message.text)
    await state.clear()

async def process_ingredient(message, ingredient):
    recipes = await api.search_by_ingredients(ingredient)
    
    if not recipes:
        return await message.answer(f"С ингредиентом '{ingredient}' рецепты не найдены")
    
    # Отправляем каждый рецепт отдельно с кнопкой сохранения
    for recipe in recipes[:5]:
        recipe_info = (
        f"🍴 {recipe['title']}\n"
            f"🔹 Использовано ингредиентов: {recipe['usedIngredientCount']}\n"
        )
        
        if recipe.get('image'):
            recipe_info += f"📷 {recipe['image']}\n"
        
        source_url = recipe.get('sourceUrl', f"https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-')}-{recipe['id']}")
        recipe_info += f"🔗 {source_url}"
    
    await message.answer(
            recipe_info,
            reply_markup=get_recipe_keyboard(recipe['id']),
            disable_web_page_preview=False
    )


from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start", "help"))
async def send_welcome(message: Message):
    welcome_text = (
        "👨‍🍳 Привет! Я бот для поиска рецептов.\n\n"
        "🔍 Доступные команды:\n"
        "/find_by_ingredients - Поиск по ингредиентам\n"
        "/random - Случайный рецепт\n"
        "/favorites - Избранные рецепты\n"
        "/help - Помощь"
    )
    await message.answer(welcome_text)
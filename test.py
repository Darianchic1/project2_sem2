import asyncio
from services.api_client import SpoonacularAPI
from config.settings import settings

async def main():
    api = SpoonacularAPI(settings.spoonacular_api_key)
    recipe = await api.get_random_recipe()
    print("Рецепт:", recipe)

if __name__ == "__main__":
    asyncio.run(main())
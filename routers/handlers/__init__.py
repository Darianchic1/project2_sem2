from aiogram import Router
from .find_by_ingredients import router as find_by_ingredients_router
from .random_recipe import router as random_router
from .favorites import router as favorites_router

router = Router()
router.include_router(find_by_ingredients_router)
router.include_router(random_router)
router.include_router(favorites_router)

__all__ = ['router', 'find_by_ingredients_router', 'favorites_router', 'random_router']
from .commands import router as commands_router
from .handlers import router as handlers_router 
from aiogram import Router

router = Router()
router.include_router(commands_router)
router.include_router(handlers_router) 

try:
    from .admin import router as admin_router
    router.include_router(admin_router)
except ImportError:
    pass
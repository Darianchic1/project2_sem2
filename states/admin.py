from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    """Состояния для админ-панели"""
    waiting_ban_user_id = State()
    waiting_unban_user_id = State() 
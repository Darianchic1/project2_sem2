from aiogram.fsm.state import StatesGroup, State

class IngredientsState(StatesGroup):
    waiting_for_ingredient = State()
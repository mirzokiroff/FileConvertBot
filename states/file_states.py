from aiogram.dispatcher.filters.state import StatesGroup, State


class FormState(StatesGroup):
    waiting_for_file = State()
    waiting_for_format = State()

from aiogram.dispatcher.filters.state import StatesGroup, State


class Admin(StatesGroup):
    video = State()
    add_group = State()
    reklama = State()
    delete_channel = State()

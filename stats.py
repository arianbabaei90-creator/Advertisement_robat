from aiogram.fsm.state import State, StatesGroup

class AdFSM(StatesGroup):
    game = State()
    title = State()
    desc = State()
    price = State()
    photo = State()
    preview = State()

class EditFSM(StatesGroup):
    value = State()

class RejectFSM(StatesGroup):
    reason = State()
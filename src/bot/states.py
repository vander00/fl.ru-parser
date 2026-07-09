from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class FilterForm(StatesGroup):
    value: State = State()

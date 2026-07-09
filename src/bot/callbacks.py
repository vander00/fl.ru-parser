from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class MenuCallback(CallbackData, prefix="menu"):
    action: str


class CategoryCallback(CallbackData, prefix="cat"):
    index: int


class FilterCallback(CallbackData, prefix="flt"):
    field: str

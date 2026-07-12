from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..schemas import Category
from .callbacks import CategoryCallback, FilterCallback, MenuCallback
from .subscription import Subscription


def main_menu(subscription: Subscription) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📂 Категория", callback_data=MenuCallback(action="categories"))
    builder.button(text="🔎 Фильтры", callback_data=MenuCallback(action="filters"))
    if subscription.active:
        builder.button(text="🔴 Остановить", callback_data=MenuCallback(action="stop"))
    else:
        builder.button(text="🟢 Запустить", callback_data=MenuCallback(action="start"))
    builder.button(text="ℹ️ Статус", callback_data=MenuCallback(action="status"))
    builder.button(text="🗂 Архив", callback_data=MenuCallback(action="archive"))
    builder.adjust(2)
    return builder.as_markup()


def category_menu(
    categories: list[Category], selected: dict[str, str]
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, category in enumerate(categories):
        mark: str = "✅ " if category.slug in selected else ""
        builder.button(
            text=f"{mark}{category.name}", callback_data=CategoryCallback(index=index)
        )
    builder.button(text="Любая", callback_data=CategoryCallback(index=-1))
    builder.button(text="⬅️ Назад", callback_data=MenuCallback(action="back"))
    builder.adjust(2)
    return builder.as_markup()


def filter_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💰 Бюджет от", callback_data=FilterCallback(field="min_budget")
    )
    builder.button(
        text="💰 Бюджет до", callback_data=FilterCallback(field="max_budget")
    )
    builder.button(
        text="💬 Откликов от", callback_data=FilterCallback(field="min_responses")
    )
    builder.button(
        text="💬 Откликов до", callback_data=FilterCallback(field="max_responses")
    )
    builder.button(text="🧹 Сбросить", callback_data=FilterCallback(field="clear"))
    builder.button(text="⬅️ Назад", callback_data=MenuCallback(action="back"))
    builder.adjust(2)
    return builder.as_markup()


def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=MenuCallback(action="back").pack()
                )
            ]
        ]
    )

from __future__ import annotations

from dataclasses import replace

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from ..schemas import Category
from .callbacks import CategoryCallback, FilterCallback, MenuCallback
from .config import BotConfig
from .formatting import format_archive, format_subscription
from .keyboards import back_button, category_menu, filter_menu, main_menu
from .adapter import ProjectAdapter
from .states import FilterForm
from .storage import SeenStore
from .subscription import Subscription, SubscriptionStore

router: Router = Router(name="fl-bot")

_FILTER_PROMPTS: dict[str, str] = {
    "min_budget": "Введите минимальный бюджет (число):",
    "max_budget": "Введите максимальный бюджет (число):",
    "min_responses": "Введите минимальное число откликов:",
    "max_responses": "Введите максимальное число откликов:",
}

_GREETING: str = (
    "Привет! Я слежу за новыми проектами на fl.ru.\n"
    "Выберите категорию и настройте фильтры — я буду присылать новые проекты сюда."
)


@router.message(CommandStart())
async def on_start(
    message: Message, store: SubscriptionStore, config: BotConfig
) -> None:
    if message.chat.id != config.chat_id:
        if config.answer_unknowns:
            await message.answer("Этот бот обслуживает только настроенный чат.")
        return
    subscription: Subscription = store.get_or_create(message.chat.id)
    await message.answer(_GREETING, reply_markup=main_menu(subscription))


@router.message(Command("status"))
async def on_status(message: Message, store: SubscriptionStore) -> None:
    subscription: Subscription = store.get_or_create(message.chat.id)
    await message.answer(
        format_subscription(subscription),
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(subscription),
    )


@router.callback_query(MenuCallback.filter(F.action == "back"))
async def on_back(
    query: CallbackQuery, store: SubscriptionStore, state: FSMContext
) -> None:
    message: Message | None = _accessible(query)
    if message is None:
        await query.answer()
        return
    await state.clear()
    subscription: Subscription = store.get_or_create(message.chat.id)
    await _edit(message, format_subscription(subscription), main_menu(subscription))
    await query.answer()


@router.callback_query(MenuCallback.filter(F.action == "status"))
async def on_status_button(query: CallbackQuery, store: SubscriptionStore) -> None:
    message: Message | None = _accessible(query)
    if message is None:
        await query.answer()
        return
    subscription: Subscription = store.get_or_create(message.chat.id)
    await _edit(message, format_subscription(subscription), main_menu(subscription))
    await query.answer()


@router.callback_query(MenuCallback.filter(F.action == "archive"))
async def on_archive(query: CallbackQuery, seen: SeenStore) -> None:
    message: Message | None = _accessible(query)
    if message is None:
        await query.answer()
        return
    entries = seen.recent(message.chat.id)
    await _edit(message, format_archive(entries), back_button())
    await query.answer()


@router.callback_query(MenuCallback.filter(F.action == "categories"))
async def on_categories(
    query: CallbackQuery, store: SubscriptionStore, service: ProjectAdapter
) -> None:
    message: Message | None = _accessible(query)
    if message is None:
        await query.answer()
        return
    subscription: Subscription = store.get_or_create(message.chat.id)
    await query.answer("Загружаю категории…")
    categories: list[Category] = await service.list_categories()
    subscription.categories_cache = categories
    await _edit(message, "Выберите категорию:", category_menu(categories))


@router.callback_query(CategoryCallback.filter())
async def on_category_chosen(
    query: CallbackQuery, callback_data: CategoryCallback, store: SubscriptionStore
) -> None:
    message: Message | None = _accessible(query)
    if message is None:
        await query.answer()
        return

    subscription: Subscription = store.get_or_create(message.chat.id)
    index: int = callback_data.index

    if index != -1 and not 0 <= index < len(subscription.categories_cache):
        await query.answer(
            "Категория устарела, откройте список заново.", show_alert=True
        )
        return

    category: Category | None = (
        None if index == -1 else subscription.categories_cache[index]
    )
    subscription.category = category.slug if category else None
    subscription.category_name = category.name if category else None
    subscription.active = True
    subscription.reset_delivery()

    await _edit(message, format_subscription(subscription), main_menu(subscription))
    await query.answer(f"Категория: {category.name if category else 'все'}")


@router.callback_query(MenuCallback.filter(F.action == "filters"))
async def on_filters(query: CallbackQuery) -> None:
    message: Message | None = _accessible(query)
    if message is None:
        await query.answer()
        return
    await _edit(message, "Настройте фильтры:", filter_menu())
    await query.answer()


@router.callback_query(FilterCallback.filter(F.field == "clear"))
async def on_filter_clear(query: CallbackQuery, store: SubscriptionStore) -> None:
    message: Message | None = _accessible(query)
    if message is None:
        await query.answer()
        return
    subscription: Subscription = store.get_or_create(message.chat.id)
    subscription.project_filter = replace(
        subscription.project_filter,
        min_budget=None,
        max_budget=None,
        min_responses=None,
        max_responses=None,
    )
    subscription.reset_delivery()
    await _edit(message, format_subscription(subscription), main_menu(subscription))
    await query.answer("Фильтры сброшены")


@router.callback_query(FilterCallback.filter())
async def on_filter_field(
    query: CallbackQuery, callback_data: FilterCallback, state: FSMContext
) -> None:
    message: Message | None = _accessible(query)
    if message is None:
        await query.answer()
        return
    prompt: str | None = _FILTER_PROMPTS.get(callback_data.field)
    if prompt is None:
        await query.answer()
        return
    await state.set_state(FilterForm.value)
    await state.update_data(field=callback_data.field)
    await _edit(message, prompt, back_button())
    await query.answer()


@router.message(FilterForm.value)
async def on_filter_value(
    message: Message, store: SubscriptionStore, state: FSMContext
) -> None:
    text: str = (message.text or "").strip()
    if not text.isdigit():
        await message.answer("Нужно целое неотрицательное число. Попробуйте ещё раз.")
        return

    data: dict[str, str] = await state.get_data()
    field: str | None = data.get("field")
    await state.clear()
    if field is None:
        return

    subscription: Subscription = store.get_or_create(message.chat.id)
    subscription.project_filter = replace(
        subscription.project_filter, **{field: int(text)}
    )
    subscription.reset_delivery()
    await message.answer(
        format_subscription(subscription),
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(subscription),
    )


@router.callback_query(MenuCallback.filter(F.action == "start"))
async def on_start_polling(query: CallbackQuery, store: SubscriptionStore) -> None:
    message: Message | None = _accessible(query)
    if message is None:
        await query.answer()
        return
    subscription: Subscription = store.get_or_create(message.chat.id)
    subscription.active = True
    subscription.reset_delivery()
    await _edit(message, format_subscription(subscription), main_menu(subscription))
    await query.answer("Рассылка включена")


@router.callback_query(MenuCallback.filter(F.action == "stop"))
async def on_stop_polling(query: CallbackQuery, store: SubscriptionStore) -> None:
    message: Message | None = _accessible(query)
    if message is None:
        await query.answer()
        return
    subscription: Subscription = store.get_or_create(message.chat.id)
    subscription.active = False
    await _edit(message, format_subscription(subscription), main_menu(subscription))
    await query.answer("Рассылка выключена")


def _accessible(query: CallbackQuery) -> Message | None:
    return query.message if isinstance(query.message, Message) else None


async def _edit(message: Message, text: str, markup: InlineKeyboardMarkup) -> None:
    try:
        await message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(
            exc
        ):  # Telegram doesn't like when nothing changes, just throwing it away
            raise

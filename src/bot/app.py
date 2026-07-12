from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNotFound, TelegramUnauthorizedError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import User

from ..utils.logging import configure_logging
from .adapter import ProjectAdapter
from .config import BotConfig
from .handlers import router
from .poller import ProjectPoller
from .storage import SeenStore
from .subscription import Subscription, SubscriptionStore

logger: logging.Logger = logging.getLogger(__name__)


async def run() -> None:
    config: BotConfig = BotConfig.from_env()
    configure_logging(log_level=config.log_level)

    bot: Bot = Bot(config.token)
    identity: User | None = await _authorize(bot)
    if identity is None:
        await bot.session.close()
        return

    dispatcher: Dispatcher = Dispatcher(storage=MemoryStorage())
    store: SubscriptionStore = SubscriptionStore()
    service: ProjectAdapter = ProjectAdapter(config.max_pages)
    seen: SeenStore = SeenStore(config.db_path)

    dispatcher["store"] = store
    dispatcher["service"] = service
    dispatcher["config"] = config
    dispatcher["seen"] = seen
    dispatcher.include_router(router)

    _seed_subscription(store, config)

    poller: ProjectPoller = ProjectPoller(
        bot, store, service, seen, config.poll_interval
    )
    poll_task: asyncio.Task[None] = asyncio.create_task(poller.run())

    logger.info(
        "Bot @%s started; delivering to chat %s", identity.username, config.chat_id
    )
    try:
        await dispatcher.start_polling(bot)
    finally:
        poll_task.cancel()
        seen.close()
        await bot.session.close()


async def _authorize(bot: Bot) -> User | None:
    try:
        return await bot.get_me()
    except (TelegramUnauthorizedError, TelegramNotFound) as exc:
        logger.error(
            "Telegram rejected BOT_TOKEN (%s). "
            "Create a bot with @BotFather and copy its token into BOT_TOKEN.",
            exc,
        )
        return None


# TODO: add several chat ids, one is supported for now althrough the logic supports it
def _seed_subscription(store: SubscriptionStore, config: BotConfig) -> None:
    subscription: Subscription = store.get_or_create(config.chat_id)
    if config.categories:
        subscription.categories = {slug: slug for slug in config.categories}
        subscription.active = True


def main() -> None:
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        logger.info("The bot has been stopped.")


if __name__ == "__main__":
    main()

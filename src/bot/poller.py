from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.enums import ParseMode

from ..schemas import ProjectInfo
from .formatting import format_project
from .adapter import ProjectAdapter
from .storage import SeenStore
from .subscription import Subscription, SubscriptionStore

logger: logging.Logger = logging.getLogger(__name__)


class ProjectPoller:
    def __init__(
        self,
        bot: Bot,
        store: SubscriptionStore,
        service: ProjectAdapter,
        seen: SeenStore,
        interval: float,
    ) -> None:
        self._bot: Bot = bot
        self._store: SubscriptionStore = store
        self._service: ProjectAdapter = service
        self._last_seen: SeenStore = seen
        self._update_interval: float = interval

    async def run(self) -> None:
        logger.info("The bot has started polling (interval=%ss)", self._update_interval)
        while True:
            await self._poll_all()
            await asyncio.sleep(self._update_interval)

    async def _poll_all(self) -> None:
        for subscription in self._store.active():
            try:
                await self._poll(subscription)
            except Exception:
                logger.exception("Poll failed for chat %s", subscription.chat_id)

    async def _poll(self, subscription: Subscription) -> None:
        projects: list[ProjectInfo] = await self._service.fetch_projects(subscription)
        self._last_seen.purge_expired()

        chat_id: int = subscription.chat_id
        project_ids: list[str] = [project.id for project in projects]
        had_history: bool = self._last_seen.has_any(chat_id)
        known: set[str] = self._last_seen.known(chat_id, project_ids)
        fresh: list[ProjectInfo] = [
            project for project in projects if project.id not in known
        ]
        self._last_seen.remember(chat_id, projects)

        if not had_history or subscription.pending_reprime:
            subscription.pending_reprime = False
            logger.info("Primed chat %s with %s known projects", chat_id, len(projects))
            return

        for project in reversed(fresh):
            await self._send(chat_id, project)

    async def _send(self, chat_id: int, project: ProjectInfo) -> None:
        await self._bot.send_message(
            chat_id,
            format_project(project),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

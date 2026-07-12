from __future__ import annotations

import asyncio

from ..parser import FlParser, FlParserBuilder, Parser, ProjectFilter
from ..schemas import Category, ProjectInfo
from .subscription import Subscription


class ProjectAdapter:
    """An adapter of the bot for the parser"""

    def __init__(self, max_pages: int) -> None:
        self._max_pages: int = max_pages

    async def list_categories(self) -> list[Category]:
        return await asyncio.to_thread(self._list_categories)

    async def fetch_projects(self, subscription: Subscription) -> list[ProjectInfo]:
        return await asyncio.to_thread(
            self._fetch_projects,
            list(subscription.categories.keys()),
            subscription.project_filter,
        )

    def _list_categories(self) -> list[Category]:
        return Parser().build().list_categories()

    def _fetch_projects(
        self, categories: list[str], project_filter: ProjectFilter
    ) -> list[ProjectInfo]:
        slugs: list[str | None] = list(categories) if categories else [None]
        seen_ids: set[str] = set()
        projects: list[ProjectInfo] = []
        for slug in slugs:
            for project in self._fetch_category(slug, project_filter):
                if project.id in seen_ids:
                    continue
                seen_ids.add(project.id)
                projects.append(project)
        return projects

    def _fetch_category(
        self, category: str | None, project_filter: ProjectFilter
    ) -> list[ProjectInfo]:
        builder: FlParserBuilder = (
            Parser()
            .with_max_pages(max_pages=self._max_pages)
            .with_filter(project_filter)
            .with_kind(kind=True)
        )
        if category:
            builder = builder.with_category(category)
        parser: FlParser = builder.build()
        return list(parser.iter_projects())

from __future__ import annotations

import logging
import random
import time
from typing import Iterator

import requests

from ..schemas import Category, ProjectInfo
from .category_parser import CategoryParser
from .config import ParserConfig
from .fetcher import PageFetcher
from .filters import ProjectFilter
from .page_parser import PageParser

logger: logging.Logger = logging.getLogger(__name__)


class FlParser:
    def __init__(
        self,
        config: ParserConfig,
        fetcher: PageFetcher,
        page_parser: PageParser,
        category_parser: CategoryParser,
        project_filter: ProjectFilter,
    ) -> None:
        self._config: ParserConfig = config
        self._fetcher: PageFetcher = fetcher
        self._page_parser: PageParser = page_parser
        self._category_parser: CategoryParser = category_parser
        self._filter: ProjectFilter = project_filter

    def list_categories(self) -> list[Category]:
        logger.info("Fetching categories from %s", self._config.listing_url)
        html: str = self._fetcher.fetch(1)
        return self._category_parser.parse(html)

    def iter_projects(self) -> Iterator[ProjectInfo]:
        for page in range(1, self._config.max_pages + 1):
            logger.info("Fetching page %s", page)
            try:
                html: str = self._fetcher.fetch(page)
            except requests.RequestException as exc:
                logger.warning("Failed to fetch page %s: %s", page, exc)
                break

            projects: list[ProjectInfo] = self._page_parser.parse(html)
            if not projects:
                logger.info("No projects found on page %s, stopping", page)
                break

            for project in projects:
                if self._filter.matches(project):
                    yield project

            if page < self._config.max_pages:
                self._sleep_between_pages()

    def _sleep_between_pages(self) -> None:
        time.sleep(random.uniform(*self._config.delay))

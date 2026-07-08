from __future__ import annotations

import logging
import random
import time
from typing import Iterator

import requests

from ..schemas import ProjectInfo
from .config import ParserConfig
from .fetcher import PageFetcher
from .page_parser import PageParser

logger: logging.Logger = logging.getLogger(__name__)


class FlParser:
    def __init__(
        self,
        config: ParserConfig,
        fetcher: PageFetcher,
        page_parser: PageParser,
    ) -> None:
        self._config: ParserConfig = config
        self._fetcher: PageFetcher = fetcher
        self._page_parser: PageParser = page_parser

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

            yield from projects

            if page < self._config.max_pages:
                self._sleep_between_pages()

    def _sleep_between_pages(self) -> None:
        time.sleep(random.uniform(*self._config.delay))

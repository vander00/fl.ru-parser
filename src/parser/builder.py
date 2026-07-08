from __future__ import annotations

from dataclasses import replace

import requests

from .category_extractor import CategoryExtractor
from .category_parser import CategoryParser
from .config import ParserConfig
from .extractor import ProjectExtractor
from .fetcher import PageFetcher
from .fl_parser import FlParser
from .page_parser import PageParser


class FlParserBuilder:
    def __init__(self) -> None:
        self._config: ParserConfig = ParserConfig()
        self._session: requests.Session | None = None

    def with_category(self, category: str) -> FlParserBuilder:
        if not category.strip():
            raise ValueError("category must be a non-empty string")
        self._config = replace(self._config, category=category.strip("/"))
        return self

    def with_max_pages(self, max_pages: int) -> FlParserBuilder:
        if max_pages < 1:
            raise ValueError(f"max_pages must be >= 1, got {max_pages}")
        self._config = replace(self._config, max_pages=max_pages)
        return self

    def with_delay(self, minimum: float, maximum: float) -> FlParserBuilder:
        if minimum < 0 or maximum < minimum:
            raise ValueError(f"invalid delay range: ({minimum}, {maximum})")
        self._config = replace(self._config, delay=(minimum, maximum))
        return self

    def with_timeout(self, timeout: float) -> FlParserBuilder:
        if timeout <= 0:
            raise ValueError(f"timeout must be > 0, got {timeout}")
        self._config = replace(self._config, timeout=timeout)
        return self

    def with_headers(self, headers: dict[str, str]) -> FlParserBuilder:
        self._config = replace(self._config, headers=dict(headers))
        return self

    def with_html_parser(self, html_parser: str) -> FlParserBuilder:
        self._config = replace(self._config, html_parser=html_parser)
        return self

    def with_session(self, session: requests.Session) -> FlParserBuilder:
        self._session = session
        return self

    def build(self) -> FlParser:
        config: ParserConfig = self._config
        session: requests.Session = self._session or requests.Session()
        fetcher: PageFetcher = PageFetcher(config, session)
        page_parser: PageParser = PageParser(config, ProjectExtractor(config))
        category_parser: CategoryParser = CategoryParser(
            config, CategoryExtractor(config)
        )
        return FlParser(config, fetcher, page_parser, category_parser)


Parser = FlParserBuilder

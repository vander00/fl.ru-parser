from __future__ import annotations

from bs4 import BeautifulSoup
from bs4.element import Tag

from ..schemas import Category
from .category_extractor import CategoryExtractor
from .config import ParserConfig

_CATEGORY_SELECTOR: str = "a.fl-home-page__spec-link"


class CategoryParser:
    def __init__(self, config: ParserConfig, extractor: CategoryExtractor) -> None:
        self._config: ParserConfig = config
        self._extractor: CategoryExtractor = extractor

    def parse(self, html: str) -> list[Category]:
        soup: BeautifulSoup = BeautifulSoup(html, self._config.html_parser)
        seen_slugs: set[str] = set()
        categories: list[Category] = []
        for anchor in soup.select(_CATEGORY_SELECTOR):
            if not isinstance(anchor, Tag):
                continue
            category: Category | None = self._extractor.extract(anchor)
            if category is None or category.slug in seen_slugs:
                continue
            seen_slugs.add(category.slug)
            categories.append(category)
        return categories

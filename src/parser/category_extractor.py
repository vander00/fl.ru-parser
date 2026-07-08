from __future__ import annotations

import re

from bs4.element import Tag

from ..schemas import Category
from .config import ParserConfig
from .helpers import attr_str, strip_base
from .patterns import Patterns


class CategoryExtractor:
    def __init__(self, config: ParserConfig) -> None:
        self._config: ParserConfig = config

    def extract(self, anchor: Tag) -> Category | None:
        href: str = strip_base(attr_str(anchor.get("href")), self._config.base_url)
        match: re.Match[str] | None = Patterns.CATEGORY_LINK.match(href)
        if match is None:
            return None

        name: str = anchor.get_text(strip=True) or attr_str(anchor.get("title"))
        if not name:
            return None

        return Category(
            name=name,
            slug=match.group(1),
            url=self._config.base_url + href,
        )

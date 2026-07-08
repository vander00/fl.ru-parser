from __future__ import annotations

import re

from bs4.element import Tag

from ..schemas import ProjectInfo
from .config import ParserConfig
from .constants import NO_RESPONSES
from .helpers import attr_str, first_int, strip_base
from .patterns import Patterns

_TITLE_SELECTOR: str = "h2.b-post__title a"
_PRICE_SELECTOR: str = ".b-post__price"
_BODY_SELECTOR: str = ".b-post__body"
_KIND_SELECTOR: str = ".b-post__foot .b-post__bold"
_DATE_SELECTOR: str = ".b-post__foot .text-gray-opacity-4"
_VIEWS_SELECTOR: str = '[title="Количество просмотров"]'
_RESPONSES_SELECTOR: str = ".b-post__foot a, .b-post__foot span"


class ProjectExtractor:
    def __init__(self, config: ParserConfig) -> None:
        self._config: ParserConfig = config

    def extract(self, card: Tag) -> ProjectInfo | None:
        anchor: Tag | None = card.select_one(_TITLE_SELECTOR)
        if anchor is None:
            return None

        href: str = self._normalize_href(attr_str(anchor.get("href")))
        match: re.Match[str] | None = Patterns.PROJECT_LINK.match(href)
        if match is None:
            return None

        title: str = anchor.get_text(strip=True)
        if not title:
            return None

        return ProjectInfo(
            id=match.group(1),
            name=title,
            type=self._parse_kind(card),
            url=self._config.base_url + href,
            description=self._parse_description(card),
            budget=self._parse_budget(card),
            responses=self._parse_responses(card),
            posted=self._parse_posted(card),
            views=self._parse_views(card),
        )

    def _normalize_href(self, href: str) -> str:
        return strip_base(href, self._config.base_url)

    @staticmethod
    def _text(card: Tag, selector: str) -> str:
        element: Tag | None = card.select_one(selector)
        return element.get_text(" ", strip=True) if element is not None else ""

    def _parse_budget(self, card: Tag) -> str:
        return self._text(card, _PRICE_SELECTOR)

    def _parse_kind(self, card: Tag) -> str:
        text: str = self._text(card, _KIND_SELECTOR)
        match: re.Match[str] | None = Patterns.KIND.search(text)
        return match.group(1) if match is not None else text

    def _parse_posted(self, card: Tag) -> str:
        return self._text(card, _DATE_SELECTOR)

    def _parse_views(self, card: Tag) -> str:
        return self._text(card, _VIEWS_SELECTOR)

    @staticmethod
    def _parse_responses(card: Tag) -> int:
        for element in card.select(_RESPONSES_SELECTOR):
            text: str = element.get_text(" ", strip=True)
            match: re.Match[str] | None = Patterns.RESPONSES.search(text)
            if match is None:
                continue
            if match.group(0).startswith("Нет"):
                return NO_RESPONSES
            return first_int(match.group(0), NO_RESPONSES)
        return NO_RESPONSES

    def _parse_description(self, card: Tag) -> str:
        return self._text(card, _BODY_SELECTOR)

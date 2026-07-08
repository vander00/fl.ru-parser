from __future__ import annotations

import re

from bs4.element import Tag

from ..schemas import ProjectInfo
from .config import ParserConfig
from .constants import BUDGET_UNKNOWN, NO_RESPONSES, NOISE_LINES
from .helpers import attr_str, first_int
from .patterns import Patterns


class ProjectExtractor:
    def __init__(self, config: ParserConfig) -> None:
        self._config: ParserConfig = config

    def extract(self, anchor: Tag) -> ProjectInfo | None:
        href: str = self._normalize_href(attr_str(anchor.get("href")))
        match: re.Match[str] | None = Patterns.PROJECT_LINK.match(href)
        if match is None:
            return None

        title: str = anchor.get_text(strip=True)
        if not title:
            return None

        card: Tag = self._find_card_container(anchor)
        text: str = card.get_text("\n", strip=True)

        kind, _posted = self._parse_posted(text)

        return ProjectInfo(
            id=match.group(1),
            name=title,
            type=kind,
            url=self._config.base_url + href,
            description=self._parse_description(text, title),
            budget=self._parse_budget(text),
            responses=self._parse_responses(text),
        )

    def _normalize_href(self, href: str) -> str:
        base: str = self._config.base_url
        return href[len(base):] if href.startswith(base) else href

    def _is_project_link(self, href: str) -> bool:
        return Patterns.PROJECT_LINK.match(self._normalize_href(href)) is not None

    def _find_card_container(self, anchor: Tag) -> Tag:
        node: Tag = anchor
        for _ in range(8):
            parent: Tag | None = node.parent
            if parent is None:
                break
            node = parent
            project_links: list[Tag] = [
                a
                for a in node.find_all("a", href=True)
                if self._is_project_link(attr_str(a.get("href")))
            ]
            if len(project_links) == 1 and len(node.get_text(strip=True)) > 60:
                return node
        return anchor.parent if anchor.parent is not None else anchor

    @staticmethod
    def _parse_posted(text: str) -> tuple[str, str]:
        match: re.Match[str] | None = Patterns.POSTED.search(text)
        if match is None:
            return "", ""
        return match.group(1), match.group(2).strip()

    @staticmethod
    def _parse_budget(text: str) -> int:
        match: re.Match[str] | None = Patterns.BUDGET.search(text)
        if match is None:
            return BUDGET_UNKNOWN
        return first_int(match.group(1), BUDGET_UNKNOWN)

    @staticmethod
    def _parse_responses(text: str) -> int:
        match: re.Match[str] | None = Patterns.RESPONSES.search(text)
        if match is None:
            return NO_RESPONSES
        return first_int(match.group(0), NO_RESPONSES)

    @classmethod
    def _parse_description(cls, text: str, title: str) -> str:
        for raw_line in text.split("\n"):
            line: str = raw_line.strip()
            if not line or line == title or line in NOISE_LINES:
                continue
            if Patterns.BUDGET.fullmatch(line):
                continue
            if Patterns.POSTED.search(line) or Patterns.RESPONSES.search(line):
                continue
            if len(line) > 15:
                return line
        return ""

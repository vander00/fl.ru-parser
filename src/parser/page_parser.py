from __future__ import annotations

from bs4 import BeautifulSoup
from bs4.element import Tag

from ..schemas import ProjectInfo
from .config import ParserConfig
from .extractor import ProjectExtractor

_CARD_CLASS: str = "b-post"


class PageParser:
    def __init__(self, config: ParserConfig, extractor: ProjectExtractor) -> None:
        self._config: ParserConfig = config
        self._extractor: ProjectExtractor = extractor

    def parse(self, html: str) -> list[ProjectInfo]:
        soup: BeautifulSoup = BeautifulSoup(html, self._config.html_parser)
        seen_ids: set[str] = set()
        projects: list[ProjectInfo] = []
        for card in soup.find_all("div", class_=_CARD_CLASS):
            if not isinstance(card, Tag):
                continue
            project: ProjectInfo | None = self._extractor.extract(card)
            if project is None or project.id in seen_ids:
                continue
            seen_ids.add(project.id)
            projects.append(project)
        return projects

from __future__ import annotations

from bs4 import BeautifulSoup

from ..schemas import ProjectInfo
from .config import ParserConfig
from .extractor import ProjectExtractor


class PageParser:
    def __init__(self, config: ParserConfig, extractor: ProjectExtractor) -> None:
        self._config: ParserConfig = config
        self._extractor: ProjectExtractor = extractor

    def parse(self, html: str) -> list[ProjectInfo]:
        soup: BeautifulSoup = BeautifulSoup(html, self._config.html_parser)
        seen_ids: set[str] = set()
        projects: list[ProjectInfo] = []
        for anchor in soup.find_all("a", href=True):
            project: ProjectInfo | None = self._extractor.extract(anchor)
            if project is None or project.id in seen_ids:
                continue
            seen_ids.add(project.id)
            projects.append(project)
        return projects

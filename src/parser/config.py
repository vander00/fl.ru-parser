from __future__ import annotations

from dataclasses import dataclass, field

from .constants import BASE_URL, DEFAULT_HEADERS


@dataclass(frozen=True)
class ParserConfig:
    base_url: str = BASE_URL
    first_page_url: str = f"{BASE_URL}/projects/"
    list_url_template: str = f"{BASE_URL}/projects/page-{{page}}/"
    headers: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_HEADERS))
    max_pages: int = 5
    delay: tuple[float, float] = (2.0, 3.5)
    timeout: float = 15.0
    html_parser: str = "html.parser"

    def page_url(self, page: int) -> str:
        if page < 1:
            raise ValueError(f"page must be >= 1, got {page}")
        if page == 1:
            return self.first_page_url
        return self.list_url_template.format(page=page)

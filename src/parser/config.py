from __future__ import annotations

from dataclasses import dataclass, field

from .constants import BASE_URL, DEFAULT_HEADERS


@dataclass(frozen=True)
class ParserConfig:
    base_url: str = BASE_URL
    category: str | None = None
    headers: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_HEADERS))
    max_pages: int = 5
    delay: tuple[float, float] = (2.0, 3.5)
    timeout: float = 15.0
    html_parser: str = "html.parser"
    kind: bool = True

    @property
    def listing_url(self) -> str:
        if self.category:
            url: str = f"{self.base_url}/projects/category/{self.category}/"
            if self.kind:
                url += "?kind=1"
            return url
        return f"{self.base_url}/projects/"

    def page_url(self, page: int) -> str:
        if page < 1:
            raise ValueError(f"page must be >= 1, got {page}")
        base: str = self.listing_url
        return base if page == 1 else f"{base}page-{page}/"

from __future__ import annotations

import requests

from .config import ParserConfig


class PageFetcher:
    def __init__(self, config: ParserConfig, session: requests.Session) -> None:
        self._config: ParserConfig = config
        self._session: requests.Session = session

    def fetch(self, page: int) -> str:
        url: str = self._config.page_url(page)
        response: requests.Response = self._session.get(
            url, headers=self._config.headers, timeout=self._config.timeout
        )
        response.raise_for_status()
        return response.text

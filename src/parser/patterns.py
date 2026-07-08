from __future__ import annotations

import re
from typing import Pattern


class Patterns:
    PROJECT_LINK: Pattern[str] = re.compile(r"^/projects/(\d+)/[^/]+\.html$")
    CATEGORY_LINK: Pattern[str] = re.compile(r"^/projects/category/(.+?)/?$")
    KIND: Pattern[str] = re.compile(r"(Заказ|Вакансия|Конкурс[а-я]*)")
    RESPONSES: Pattern[str] = re.compile(
        r"(\d+)\s*(?:ответ[а-я]*|участник[а-я]*)|Нет ответов"
    )
    DIGITS: Pattern[str] = re.compile(r"\d[\d\s ]*")

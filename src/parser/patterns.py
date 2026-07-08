from __future__ import annotations

import re
from typing import Pattern


class Patterns:
    PROJECT_LINK: Pattern[str] = re.compile(r"^/projects/(\d+)/[^/]+\.html$")
    STATUS_DONE: Pattern[str] = re.compile(r"Исполнитель определ[её]н")
    POSTED: Pattern[str] = re.compile(
        r"(Заказ|Вакансия|Конкурс[а-я]*)\s+([^\n]*?(?:назад|через[^\n]*))"
    )
    RESPONSES: Pattern[str] = re.compile(
        r"(\d+)\s*(?:ответ[а-я]*|участник[а-я]*)|Нет ответов"
    )
    BUDGET: Pattern[str] = re.compile(
        r"(по договоренности|по результатам собеседования|"
        r"\d[\d\s]{1,12}\s*(?:руб|₽)(?:/час)?)",
        re.IGNORECASE,
    )
    DIGITS: Pattern[str] = re.compile(r"\d[\d\s]*")

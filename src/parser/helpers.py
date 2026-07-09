from __future__ import annotations

import re

from .patterns import Patterns


def attr_str(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return " ".join(str(item) for item in value)
    return str(value)


def strip_base(href: str, base: str) -> str:
    return href[len(base) :] if href.startswith(base) else href


def first_int(text: str, default: int) -> int:
    amount: int | None = first_int_or_none(text)
    return amount if amount is not None else default


def first_int_or_none(text: str) -> int | None:
    match: re.Match[str] | None = Patterns.DIGITS.search(text)
    if match is None:
        return None
    digits: str = re.sub(r"\D", "", match.group(0))
    return int(digits) if digits else None

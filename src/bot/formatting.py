from __future__ import annotations

from aiogram import html

from ..parser import ProjectFilter
from ..schemas import ProjectInfo
from .storage import ArchivedProject
from .subscription import Subscription


def format_project(project: ProjectInfo) -> str:
    lines: list[str] = [html.bold(html.quote(project.name))]
    if project.type:
        lines.append(f"🏷 {html.quote(project.type)}")
    lines.append(f"💰 {html.quote(project.budget or '—')}")
    lines.append(f"💬 {project.responses} · 👁 {html.quote(project.views or '—')}")
    if project.posted:
        lines.append(f"🕒 {html.quote(project.posted)}")
    if project.description:
        lines.append("")
        lines.append(html.quote(_truncate(project.description, 400)))
    lines.append("")
    lines.append(html.link("Открыть проект", project.url))
    return "\n".join(lines)


def format_subscription(subscription: Subscription) -> str:
    category: str = subscription.category_name or subscription.category or "Все проекты"
    status: str = "🟢 включена" if subscription.active else "🔴 выключена"
    return "\n".join(
        [
            html.bold("Текущая подписка"),
            f"📂 Категория: {html.quote(category)}",
            f"🔎 Фильтры: {html.quote(format_filter(subscription.project_filter))}",
            f"📡 Рассылка: {status}",
        ]
    )


def format_archive(entries: list[ArchivedProject]) -> str:
    if not entries:
        return (
            "🗂 <b>Архив пуст</b>\nНовые проекты появятся здесь после ближайшего опроса."
        )
    lines: list[str] = [html.bold(f"🗂 Архив проектов ({len(entries)})"), ""]
    for entry in entries:
        title: str = html.link(entry.name or "Проект", entry.url)
        suffix: str = f" · 💰 {html.quote(entry.budget)}" if entry.budget else ""
        lines.append(f"• {title}{suffix}")
    return "\n".join(lines)


def format_filter(project_filter: ProjectFilter) -> str:
    if project_filter.is_empty:
        return "не заданы"
    parts: list[str] = []
    if project_filter.min_budget is not None:
        parts.append(f"бюджет от {project_filter.min_budget}")
    if project_filter.max_budget is not None:
        parts.append(f"бюджет до {project_filter.max_budget}")
    if project_filter.min_responses is not None:
        parts.append(f"откликов от {project_filter.min_responses}")
    if project_filter.max_responses is not None:
        parts.append(f"откликов до {project_filter.max_responses}")
    return ", ".join(parts)


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"

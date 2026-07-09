from __future__ import annotations

from dataclasses import dataclass, field

from ..parser import ProjectFilter
from ..schemas import Category


@dataclass
class Subscription:
    chat_id: int
    category: str | None = None
    category_name: str | None = None
    project_filter: ProjectFilter = ProjectFilter()
    active: bool = False
    pending_reprime: bool = False
    categories_cache: list[Category] = field(default_factory=list)

    def reset_delivery(self) -> None:
        self.pending_reprime = True


class SubscriptionStore:
    def __init__(self) -> None:
        self._subscriptions: dict[int, Subscription] = {}

    def get_or_create(self, chat_id: int) -> Subscription:
        subscription: Subscription | None = self._subscriptions.get(chat_id)
        if subscription is None:
            subscription = Subscription(chat_id=chat_id)
            self._subscriptions[chat_id] = subscription
        return subscription

    def active(self) -> list[Subscription]:
        return [sub for sub in self._subscriptions.values() if sub.active]

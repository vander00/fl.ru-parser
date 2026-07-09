from __future__ import annotations

from dataclasses import dataclass

from ..schemas import ProjectInfo
from .helpers import first_int_or_none


@dataclass(frozen=True)
class ProjectFilter:
    min_budget: int | None = None
    max_budget: int | None = None
    min_responses: int | None = None
    max_responses: int | None = None

    @property
    def is_empty(self) -> bool:
        return not any(
            value is not None
            for value in (
                self.min_budget,
                self.max_budget,
                self.min_responses,
                self.max_responses,
            )
        )

    def matches(self, project: ProjectInfo) -> bool:
        return self._budget_ok(project.budget) and self._responses_ok(project.responses)

    def _budget_ok(self, budget_text: str) -> bool:
        if self.min_budget is None and self.max_budget is None:
            return True
        amount: int | None = first_int_or_none(budget_text)
        if amount is None:
            return False
        if self.min_budget is not None and amount < self.min_budget:
            return False
        if self.max_budget is not None and amount > self.max_budget:
            return False
        return True

    def _responses_ok(self, responses: int) -> bool:
        if self.min_responses is not None and responses < self.min_responses:
            return False
        if self.max_responses is not None and responses > self.max_responses:
            return False
        return True

from dataclasses import dataclass


@dataclass
class ProjectInfo:
    id: str
    name: str
    type: str
    url: str
    description: str
    budget: str
    responses: int
    posted: str
    views: str


@dataclass(frozen=True)
class Category:
    name: str
    slug: str
    url: str

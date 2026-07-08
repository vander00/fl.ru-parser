from dataclasses import dataclass


@dataclass
class ProjectInfo:
    id: str
    name: str
    type: str
    url: str
    description: str
    budget: int
    responses: int

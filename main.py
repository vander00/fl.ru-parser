from src.parser import FlParser, Parser
from src.schemas import Category, ProjectInfo
from src.utils.logging import configure_logging

CATEGORY: str = "programmirovanie"


def main() -> None:
    configure_logging()

    _list_categories()
    _follow_category(CATEGORY)


def _list_categories() -> None:
    parser: FlParser = Parser().build()
    categories: list[Category] = parser.list_categories()

    print(f"Categories ({len(categories)}):")
    for category in categories:
        print(f"  {category.slug:<28} {category.name}")
    print()


def _follow_category(category: str) -> None:
    parser: FlParser = (
        Parser().with_category(category).with_max_pages(2).with_delay(1.5, 3.0).build()
    )

    print(f"Projects in category '{category}':")
    count: int = 0
    for project in parser.iter_projects():
        count += 1
        _print_project(count, project)

    print(f"\nTotal projects parsed: {count}")


def _print_project(index: int, project: ProjectInfo) -> None:
    print(f"[{index}] {project.name}")
    print(f"    type:        {project.type or '—'}")
    print(f"    budget:      {project.budget or '—'}")
    print(f"    responses:   {project.responses}")
    print(f"    posted:      {project.posted or '—'}")
    print(f"    views:       {project.views or '—'}")
    print(f"    url:         {project.url}")
    if project.description:
        print(f"    description: {project.description}")


if __name__ == "__main__":
    main()

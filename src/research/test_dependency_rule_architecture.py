from __future__ import annotations

from pathlib import Path


FORBIDDEN_IMPORTS = (
    "from src.application",
    "import src.application",
    "from src.storage",
    "import src.storage",
    "from src.cli",
    "import src.cli",
)


def test_research_layer_does_not_depend_on_outer_layers() -> None:
    research_root = Path(__file__).parent

    violations: list[str] = []

    for python_file in research_root.rglob("*.py"):
        if python_file.name.startswith("test_"):
            continue

        source = python_file.read_text(
            encoding="utf-8",
        )

        for forbidden_import in FORBIDDEN_IMPORTS:
            if forbidden_import in source:
                relative_path = python_file.relative_to(
                    research_root.parent.parent,
                )

                violations.append(
                    f"{relative_path}: {forbidden_import}"
                )

    assert not violations, (
        "Research layer must not depend on application, "
        "storage, or cli layers:\n"
        + "\n".join(violations)
    )
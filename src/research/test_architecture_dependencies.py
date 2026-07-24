from __future__ import annotations

import ast
from pathlib import Path


_RESEARCH_ROOT = Path(__file__).resolve().parent
_FORBIDDEN_DEPENDENCIES = (
    "src.application",
    "src.cli",
)


def _imported_modules(
    path: Path,
) -> tuple[str, ...]:
    tree = ast.parse(
        path.read_text(encoding="utf-8-sig"),
        filename=str(path),
    )
    modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(
                alias.name
                for alias in node.names
            )
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
        ):
            modules.append(node.module)

    return tuple(modules)


def _is_forbidden_dependency(
    module: str,
) -> bool:
    return any(
        module == prefix
        or module.startswith(f"{prefix}.")
        for prefix in _FORBIDDEN_DEPENDENCIES
    )


def test_research_production_modules_do_not_depend_on_outer_layers(
) -> None:
    violations: list[str] = []

    for path in sorted(
        _RESEARCH_ROOT.rglob("*.py")
    ):
        if path.name.startswith("test_"):
            continue

        relative_path = path.relative_to(
            _RESEARCH_ROOT
        )

        for module in _imported_modules(path):
            if _is_forbidden_dependency(module):
                violations.append(
                    f"{relative_path}: {module}"
                )

    assert not violations, (
        "Research production modules must not depend "
        "on application or CLI layers:\n"
        + "\n".join(violations)
    )
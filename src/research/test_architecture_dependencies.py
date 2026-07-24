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

def _production_module_paths(
) -> tuple[Path, ...]:
    return tuple(
        path
        for path in sorted(
            _RESEARCH_ROOT.rglob("*.py")
        )
        if not path.name.startswith("test_")
    )


def _module_name(
    path: Path,
) -> str:
    relative_path = (
        path.relative_to(_RESEARCH_ROOT)
        .with_suffix("")
    )
    parts = (
        "src",
        "research",
        *relative_path.parts,
    )

    if parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)


def _research_dependency_graph(
) -> dict[str, tuple[str, ...]]:
    path_by_module = {
        _module_name(path): path
        for path in _production_module_paths()
    }

    return {
        module: tuple(
            sorted(
                imported_module
                for imported_module in (
                    _imported_modules(path)
                )
                if imported_module in path_by_module
            )
        )
        for module, path in path_by_module.items()
    }


def _find_dependency_cycle(
    graph: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    visited: set[str] = set()
    active: set[str] = set()
    stack: list[str] = []

    def visit(
        module: str,
    ) -> tuple[str, ...]:
        if module in active:
            cycle_start = stack.index(module)

            return tuple(
                stack[cycle_start:] + [module]
            )

        if module in visited:
            return ()

        visited.add(module)
        active.add(module)
        stack.append(module)

        for dependency in graph[module]:
            cycle = visit(dependency)

            if cycle:
                return cycle

        stack.pop()
        active.remove(module)

        return ()

    for module in sorted(graph):
        cycle = visit(module)

        if cycle:
            return cycle

    return ()


def test_research_production_modules_have_no_import_cycles(
) -> None:
    cycle = _find_dependency_cycle(
        _research_dependency_graph()
    )

    assert not cycle, (
        "Research production modules contain "
        "a circular dependency:\n"
        + " -> ".join(cycle)
    )
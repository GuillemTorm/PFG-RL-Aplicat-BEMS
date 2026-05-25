"""Generate the BEMS-RL Studio source-code reference for Sphinx.

The Studio contains Streamlit page files that render UI at module import time.
Autodoc is excellent for import-safe backend modules, but page files need a
static parser so documentation builds never execute widgets. This generator
creates one RST page per Python file with signatures, docstrings, source paths
and a navigable table of contents.
"""

from __future__ import annotations

import ast
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


SOURCE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
STUDIO_ROOT = PROJECT_ROOT / "BEMS-RL-STUDIO"
OUTPUT_ROOT = SOURCE_DIR / "pages" / "bems-rl-studio" / "reference"


@dataclass(frozen=True)
class ReferenceGroup:
    """Description of a group of Studio files rendered under one sidebar node."""

    slug: str
    title: str
    intro: str
    files: tuple[Path, ...]


def _rst_title(text: str, marker: str = "=") -> str:
    return f"{text}\n{marker * len(text)}\n\n"


def _clean_docstring(docstring: str | None) -> str:
    if not docstring:
        return "No docstring available yet."
    return "\n".join(line.rstrip() for line in docstring.strip().splitlines())


def _indent(text: str, spaces: int = 3) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else "" for line in text.splitlines())


def _docstring_block(title: str, docstring: str | None) -> str:
    """Render a docstring as literal text so arbitrary content stays valid RST."""

    block = f"**{title}**\n\n"
    block += ".. code-block:: text\n\n"
    block += _indent(_clean_docstring(docstring), 3) + "\n\n"
    return block


def _module_name(path: Path) -> str:
    rel = path.relative_to(STUDIO_ROOT).with_suffix("")
    if rel.name == "__init__":
        rel = rel.parent
    return ".".join(rel.parts)


def _page_name(path: Path) -> str:
    rel = path.relative_to(STUDIO_ROOT)
    safe_parts = [re.sub(r"[^A-Za-z0-9_.-]+", "_", part) for part in rel.with_suffix("").parts]
    return "_".join(safe_parts)


def _signature(text: str, node: ast.AST, keyword: str) -> str:
    lines = text.splitlines()
    header_parts: list[str] = []
    paren_balance = 0
    for line in lines[node.lineno - 1 :]:
        stripped = line.strip()
        header_parts.append(stripped)
        paren_balance += stripped.count("(") - stripped.count(")")
        if paren_balance <= 0 and stripped.endswith(":"):
            break
    header = " ".join(header_parts)
    header = re.sub(r"\s+", " ", header).rstrip(":")
    return header.removeprefix(keyword).strip()


def _dependency_names(tree: ast.Module) -> list[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.level:
                names.add("." * node.level + node.module.split(".")[0])
            else:
                names.add(node.module.split(".")[0])
    return sorted(names, key=lambda value: value.lower())


def _render_function(text: str, path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    keyword = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
    signature = _signature(text, node, keyword)
    visibility = "Internal helper" if node.name.startswith("_") else "Public function"
    rel_path = path.relative_to(PROJECT_ROOT).as_posix()
    block = _rst_title(node.name, "~")
    block += f"**{visibility}.** Defined in ``{rel_path}:{node.lineno}``.\n\n"
    block += ".. code-block:: python\n\n"
    block += _indent(f"{keyword}{signature}", 3) + "\n\n"
    block += _docstring_block("Docstring", ast.get_docstring(node))
    return block


def _render_class(text: str, path: Path, node: ast.ClassDef) -> str:
    signature = _signature(text, node, "class ")
    rel_path = path.relative_to(PROJECT_ROOT).as_posix()
    block = _rst_title(node.name, "~")
    block += f"**Class.** Defined in ``{rel_path}:{node.lineno}``.\n\n"
    block += ".. code-block:: python\n\n"
    block += _indent(f"class {signature}", 3) + "\n\n"
    block += _docstring_block("Docstring", ast.get_docstring(node))

    methods = [
        item
        for item in node.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if methods:
        block += "**Methods**\n\n"
        for method in methods:
            keyword = "async def " if isinstance(method, ast.AsyncFunctionDef) else "def "
            method_signature = _signature(text, method, keyword)
            block += f"``{keyword}{method_signature}``\n"
            block += _docstring_block("Method docstring", ast.get_docstring(method))
    return block


def _render_module_page(path: Path, group: ReferenceGroup) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    rel_path = path.relative_to(PROJECT_ROOT).as_posix()
    module_name = _module_name(path)
    title = path.relative_to(STUDIO_ROOT).as_posix()

    functions = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    dependencies = _dependency_names(tree)

    content = _rst_title(title, "=")
    content += f"**Group:** {group.title}\n\n"
    content += f"**Source:** ``{rel_path}``\n\n"
    content += f"**Module path:** ``{module_name or path.stem}``\n\n"
    content += _docstring_block("Module docstring", ast.get_docstring(tree))
    content += ".. contents:: In this file\n   :local:\n   :depth: 2\n\n"

    if dependencies:
        content += _rst_title("Imports", "-")
        content += ", ".join(f"``{name}``" for name in dependencies) + "\n\n"

    if classes:
        content += _rst_title("Classes", "-")
        for node in classes:
            content += _render_class(text, path, node)

    if functions:
        content += _rst_title("Functions", "-")
        for node in functions:
            content += _render_function(text, path, node)

    if not classes and not functions:
        content += "This file does not define top-level classes or functions.\n\n"
    return content


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _studio_files(pattern: str) -> tuple[Path, ...]:
    return tuple(sorted(STUDIO_ROOT.glob(pattern)))


def _reference_groups() -> tuple[ReferenceGroup, ...]:
    root_files = tuple(
        path
        for path in [
            STUDIO_ROOT / "__init__.py",
            STUDIO_ROOT / "Inici.py",
            STUDIO_ROOT / "sidebar_nav.py",
        ]
        if path.exists()
    )
    maintenance_files = tuple(
        path
        for path in [
            *sorted((STUDIO_ROOT / "tools").glob("*.py")),
        ]
        if path.exists()
    )
    return (
        ReferenceGroup(
            "entrypoints",
            "Application Entry Points",
            "Streamlit entry points, global theme utilities and legacy viewer helpers.",
            root_files,
        ),
        ReferenceGroup(
            "pages",
            "Streamlit Pages",
            "Page-level code parsed statically so documentation builds never execute Streamlit widgets.",
            _studio_files("pages/*.py"),
        ),
        ReferenceGroup(
            "backend",
            "Backend Modules",
            "Import-safe application services for environments, training, evaluation, results and reports.",
            _studio_files("backend/*.py"),
        ),
        ReferenceGroup(
            "charts",
            "Chart and KPI Modules",
            "Data normalization, KPI calculation and Plotly figure builders used by dashboards and reports.",
            _studio_files("backend/grafics/*.py"),
        ),
        ReferenceGroup(
            "components",
            "Reusable Page Components",
            "Shared Streamlit render helpers for training, rewards, wrappers and result dashboards.",
            _studio_files("page_components/*.py"),
        ),
        ReferenceGroup(
            "styles",
            "Page Style Modules",
            "CSS injection helpers that keep visual styling outside workflow code.",
            _studio_files("page_styles/*.py"),
        ),
        ReferenceGroup(
            "maintenance",
            "Maintenance Tools",
            "Manual probes and static checks used while maintaining the Studio codebase.",
            maintenance_files,
        ),
    )


def generate() -> None:
    """Generate all Studio code-reference RST files."""

    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    groups = tuple(group for group in _reference_groups() if group.files)
    index_entries: list[str] = []

    for group in groups:
        group_dir = OUTPUT_ROOT / group.slug
        entries: list[str] = []
        for path in group.files:
            if path.name == "__pycache__":
                continue
            page_name = _page_name(path)
            target = group_dir / f"{page_name}.rst"
            _write(target, _render_module_page(path, group))
            entries.append(page_name)

        group_index = _rst_title(group.title, "=")
        group_index += group.intro + "\n\n"
        group_index += ".. toctree::\n   :maxdepth: 2\n\n"
        for entry in entries:
            group_index += f"   {entry}\n"
        group_index += "\n"
        _write(group_dir / "index.rst", group_index)
        index_entries.append(f"{group.slug}/index")

    index = _rst_title("Studio Code Reference", "=")
    index += (
        "This section lists the BEMS-RL Studio source files directly in the "
        "sidebar. Open a file page to inspect its module docstring, imports, "
        "classes, functions, signatures and source line numbers.\n\n"
    )
    index += ".. toctree::\n   :maxdepth: 3\n   :caption: Code files\n\n"
    for entry in index_entries:
        index += f"   {entry}\n"
    index += "\n"
    _write(OUTPUT_ROOT / "index.rst", index)


if __name__ == "__main__":
    generate()

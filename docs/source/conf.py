"""Sphinx configuration for BEMS-RL Studio."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STUDIO_ROOT = PROJECT_ROOT / "BEMS-RL-STUDIO"

for path in (PROJECT_ROOT, STUDIO_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

os.environ.setdefault("SINERGYM_DOCS_BUILD", "1")


class _StreamlitMock(mock.MagicMock):
    """Minimal Streamlit mock that keeps cached functions importable."""

    def cache_data(self, *args, **kwargs):
        return self._identity_decorator(*args, **kwargs)

    def cache_resource(self, *args, **kwargs):
        return self._identity_decorator(*args, **kwargs)

    @staticmethod
    def _identity_decorator(*args, **kwargs):
        if args and callable(args[0]) and len(args) == 1 and not kwargs:
            return args[0]

        def decorator(func):
            return func

        return decorator


sys.modules.setdefault("streamlit", _StreamlitMock())


project = "BEMS-RL Studio"
copyright = "2025, J. Jiménez, J. Gómez, M. Molina, A. Manjavacas, A. Campoy"
author = "J. Jiménez, J. Gómez, M. Molina, A. Manjavacas, A. Campoy"


scripts_path = Path(__file__).resolve().parent / "_scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))
from generate_studio_reference import generate as _generate_studio_reference

_generate_studio_reference()


def _read_project_version() -> str:
    pyproject = PROJECT_ROOT / "sinergym" / "pyproject.toml"
    match = re.search(
        r'^version\s*=\s*["\']([^"\']+)["\']',
        pyproject.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    return match.group(1) if match else "0.0.0"


version = _read_project_version()
release = version


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    "sphinx.ext.graphviz",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_member_order = "bysource"
autodoc_preserve_defaults = True
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_typehints_format = "short"
autoclass_content = "both"

autosummary_generate = True
autosummary_imported_members = False

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "gymnasium": ("https://gymnasium.farama.org", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "plotly": ("https://plotly.com/python-api-reference", None),
}

autosectionlabel_prefix_document = True
graphviz_output_format = "svg"

# Warnings
suppress_warnings = ["config.cache"]

autodoc_mock_imports = [
    "gcloud",
    "gym",
    "google",
    "google.cloud",
    "googleapiclient",
    "oauth2client",
    "opyplus",
    "pyenergyplus",
    "stable_baselines3",
    "wandb",
]


sys.modules["gymnasium.wrappers.normalize"] = mock.MagicMock()

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["doc_theme.css"]
html_logo = None
html_favicon = None
html_theme_options = {
    "style_nav_header_background": "#f8fbfa",
    "display_version": False,
}
html_sidebars = {
    "**": [
        "globaltoc.html",
        "localtoc.html",
        "relations.html",
    ],
}
html_context = {"display_github": False}

# conf.py -- Sphinx configuration for [Your Project]

import os
import sys

# -- Path setup --------------------------------------------------------------

sys.path.insert(0, os.path.abspath(".."))  # Adjust if your src/ layout differs

# -- Project information -----------------------------------------------------

project = "eventscore"
copyright = "2025, Matvey Ivanov"
author = "Matvey Ivanov"
release = "0.1.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

# Generate autosummary pages automatically
autosummary_generate = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory,
# to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Autodoc configuration ---------------------------------------------------

autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "private-members": False,
    "special-members": False,
    "show-inheritance": True,
    "inherited-members": False,
}
autodoc_typehints = "description"
autodoc_inherit_docstrings = True
add_module_names = False  # Cleaner function/class references

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "redis": ("https://redis.readthedocs.io/en/stable", None),
}

# -- HTML output -------------------------------------------------------------

html_theme = "furo"  # Or "sphinx_rtd_theme"
html_title = project
html_logo = "_static/logo.png"  # Place your logo in docs/_static/
html_favicon = "_static/favicon.ico"

html_static_path = ["_static"]

html_theme_options = {
    "source_repository": "https://github.com/MatveyIvanov/eventscore/",
    "source_branch": "main",
    "source_directory": "docs/",
    # Furo-specific tweaks:
    "light_logo": "logo.png",
    "dark_logo": "logo-dark.png",
}

# If you want to enable the “Edit on GitHub” links:
html_context = {
    "display_github": True,
    "github_user": "MatveyIvanov",
    "github_repo": "eventscore",
    "github_version": "main",
    "doc_path": "docs",
}

# -- Miscellaneous enhancements ----------------------------------------------

# If using type hints everywhere, this makes display consistent:
autodoc_typehints_format = "short"  # "short" or "fully-qualified"

# Syntax highlighting style (“sphinx” or your choice)
pygments_style = "sphinx"
pygments_dark_style = "monokai"

# Show TODOs in the output if the extension is enabled
extensions.append("sphinx.ext.todo")
todo_include_todos = True

# -- Future proofing (optional) ----------------------------------------------

# # Enable internationalization (for translations)
# locale_dirs = ['locales/']   # path is example but recommended.
# gettext_compact = False

# -- Custom “last updated” ---------------------------------------------------

html_last_updated_fmt = "%b %d, %Y"

# -- Options for manual toc depth --------------------------------------------

# toc depth in sidebar, if needed
html_sidebars = {
    "**": [
        "globaltoc.html",
        "relations.html",
        "sourcelink.html",
        "searchbox.html",
    ]
}

# -- End of configuration ----------------------------------------------------

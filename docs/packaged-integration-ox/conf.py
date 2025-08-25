# SPDX-FileCopyrightText: 2025 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

# sys.path.insert(0, os.path.abspath('.'))

from datetime import date

# -- Project information -----------------------------------------------------

version = "0.0.1"
release = "latest"

project = "OX App Suite packaged integration for Nubus for Kubernetes"
year_range = date.today().year
start_year = 2025
if year_range > start_year:
    year_range = f"{start_year}-{year_range}"
copyright = f"{year_range}, Univention GmbH"
author = "Univention GmbH"
language = "en"

html_title = project

# The doc_basename must match the documents root directory name on the public
# target location. Otherwise the PDF link on the overview page will point to
# the wrong file.
doc_basename = os.path.basename(os.path.dirname(__file__))

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_copybutton",
    "sphinxcontrib.spelling",
    "univention_sphinx_extension",
    "sphinx_sitemap",
    "sphinx_last_updated_by_git",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.bibtex",
]

intersphinx_mapping = {
    "uv-navigation": ("https://docs.software-univention.de/n/en", None),
    "uv-nubus-kubernetes-operation": (
        "https://docs.software-univention.de/nubus-kubernetes-operation/latest/en/",
        None,
    ),
    "uv-nubus-kubernetes-customization": (
        "https://docs.software-univention.de/nubus-kubernetes-customization/latest/en/",
        None,
    ),
    "uv-ox-connector-app": (
        "https://docs.software-univention.de/ox-connector-app/latest/",
        None,
    ),
}

bibtex_bibfiles = ["../bibliography.bib"]
bibtex_encoding = "utf-8"
bibtex_default_style = "unsrt"
bibtex_reference_style = "label"

# For more configuration options of Sphinx-copybutton, see the documentation
# https://sphinx-copybutton.readthedocs.io/en/latest/index.html
copybutton_prompt_text = r"\$ "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"
copybutton_here_doc_delimiter = "EOT"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "univention_sphinx_book_theme"
html_theme_options = {
    "pdf_download_filename": f"{doc_basename}.pdf",
    "show_source_license": True,
    "typesense_search": True,
    "typesense_document": doc_basename,
    "typesense_document_version": "latest",  # or "latest"
    "univention_matomo_tracking": True,
    "univention_docs_deployment": True,
    "announcement": "This documentation describes a <strong>product preview</strong> "
    + "for packaged integrations in Nubus for Kubernetes.",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

numfig = True

suppress_warnings = ["git.too_shallow"]
git_last_updated_timezone = "Europe/Berlin"

if "spelling" in sys.argv:
    spelling_lang = "en"
    spelling_show_suggestions = True
    spelling_word_list_filename = ["spelling_wordlist"]

root_doc = "contents"

linkcheck_anchors_ignore_for_url = [
    r"https://documentation\.open-xchange\.com/components/middleware/config/8/",
    r"https://gitlab\.opencode\.de/bmi/opendesk/deployment/opendesk/-/blob/174c73c012e911342644bdcb89d22b35be9baa36/helmfile/apps/open-xchange/values-openxchange\.yaml\.gotmpl",
]

latex_engine = "lualatex"
latex_show_pagerefs = True
latex_show_urls = "footnote"
latex_documents = [
    (root_doc, f"{doc_basename}.tex", project, author, "manual", False),
]
latex_elements = {
    "papersize": "a4paper",
    "babel": "\\usepackage{babel}",
}

# Configure Univention feedback link
# See https://git.knut.univention.de/univention/documentation/univention_sphinx_extension#univention_feedback

# Deactivated per default. To activate, set it to True.
univention_feedback = True
univention_pdf_show_source_license = True
univention_doc_basename = doc_basename
univention_use_doc_base = True
univention_project_basename = doc_basename

# The sitemap URL should only use the version, instead the release value.
# The scheme only accepts release.
# Therefore, set the value of release to the value of version
# and use it in the scheme for the sitemap.
univention_release_language_scheme = "{release}/{language}"

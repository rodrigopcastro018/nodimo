# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../nodimo'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Nodimo'
copyright = '2024, Rodrigo Castro'
author = 'Rodrigo Castro'
release = '1.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'nbsphinx',  # This extension requires pandoc (pandoc.org)
    'numpydoc',
    'sphinx.ext.linkcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# autodoc
autodoc_inherit_docstrings = False
autosummary_generate = False

# numpydoc
numpydoc_show_inherited_class_members = {
    'nodimo.variable.Variable': False,
    'nodimo.group.VariableGroup': False,
    'nodimo.matrix.DimensionalMatrix': False,
    'nodimo.function.ModelFunction': False,
}

# linkcode
branch = 'docstrings'
branch_url = f'https://github.com/rodrigopcastro018/nodimo/blob/{branch}'

def linkcode_resolve(domain, info):
    if domain != 'py':
        return None
    if not info['module']:
        return None
    filename = info['module'].replace('.', '/')
    return f'{branch_url}/{filename}.py'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

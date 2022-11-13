# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os,sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'pypub3'
copyright = '2022, Andrew Scott'
author = 'Andrew Scott'
release = 'pypub'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = []

latex_documents = [(
    'index', 
    'pypub.tex', 
    'pypub Documentation',
    'Andrew Scott & William Cember', 
    'manual',
)]

man_pages=[(
    'index', 
    'pypub', 
    'pypub Documentation',
    ['Andrew Scott', 'William Cember'], 
    1,
)]

texinfo_documents=[(
    'index', 
    'pypub', 
    'pypub Documentation',
    'Andrew Scott & William Cember', 
    'pypub', 
    'One line description of project.',
    'Miscellaneous',
)]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'default'
html_static_path = ['_static']

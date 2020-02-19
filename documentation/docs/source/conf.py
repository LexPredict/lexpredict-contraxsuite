# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import sys
import django
from datetime import datetime
from django.conf import settings
from django.utils.safestring import mark_safe

sys.path.append('../../../contraxsuite_services')

# Documentation contributors may not have a local installation of ContraxSuite
try:
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
    django.setup()
    # The full version, including alpha/beta/rc tags
    release = settings.VERSION_NUMBER
except Exception as e:
    print('No ContraxSuite installation found.')
    print(e)

# -- Project information -----------------------------------------------------
author = 'LexPredict, LLC'
project = 'LexPredict ContraxSuite'
copyright = mark_safe(
    '2019, LexPredict, LLC'
    '<span style="margin-left: 40px">Last updated: '
    + datetime.now().strftime('%m/%d/%Y, %H:%M:%S %Z') + '</span>'
)

# -- General configuration ---------------------------------------------------

# Custom Extensions

sys.path.append(os.path.abspath("./_ext"))

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'formfield_extension',
    'recommonmark',
    'sphinx.ext.napoleon',
    'sphinx.ext.coverage',
    'sphinx.ext.autodoc',
]

include_formfield = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

# THIRD-PARTY
# html_theme = 'press'
html_theme = 'sphinx_rtd_theme'

# If given, this must be the name of an image file (path relative to the 
# configuration directory) that is the logo of the docs. It is placed at the
# top of the sidebar; its width should therefore not exceed 200 pixels.
html_logo = '_static/img/ContraxSuiteLogo.png'

# If given, this must be the name of an image file
# (path relative to the configuration directory) that is the favicon of the
# docs. Modern browsers use this as the icon for tabs, windows and 
# bookmarks. It should be a Windows-style icon file (.ico), which is 16x16 or
# 32x32 pixels large.
html_favicon = '_static/img/favicon.ico'

# Custom CSS. Relative to html_static_path.
html_css_files = [
    'css/custom_styles.css',
]

# A dictionary of options that influence the look and feel of the selected 
# theme. These are theme-specific.
html_theme_options = {    
    'logo_only': True,
    'style_nav_header_background': '#F4F6F9',
}

# -- Options for Extensions --------------------------------------------------

coverage_ignore_c_items = True


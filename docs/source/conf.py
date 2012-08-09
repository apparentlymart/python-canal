import sys, os
import pkg_resources

# Make the modules visible to autodoc even if we've not installed
# the module yet.
sys.path.insert(0, os.path.abspath('../'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
source_encoding = 'utf-8'
master_doc = 'index'

project = u'Canal'
copyright = u'2012, Martin Atkins'
# Determine the version from the installed package version.
# (this might be wrong/broken if working in a VCS checkout without
# installing the module.)
version = pkg_resources.require("canal")[0].version
release = version

pygments_style = 'sphinx'

html_theme = 'default'
html_static_path = ['_static']
htmlhelp_basename = 'Canaldoc'

latex_elements = {}
latex_documents = [
  ('index', 'Canal.tex', u'Canal Documentation',
   u'Martin Atkins', 'manual'),
]

intersphinx_mapping = {
    'http://docs.python.org/': None,
}

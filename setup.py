# Copyright (c) 2013 Beleidsdomein Leefmilieu, Natuur en Energie (LNE) and Vlaamse Milieumaatschappij (VMM). All rights reserved.
# See also LICENSE.txt

import os, sys
from setuptools import setup, find_packages

version = '1.1dev'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('docs/HISTORY.txt')
    )
requires = [
    "setuptools",
    "plone.app.content",
    "plone.app.form",
    "plone.app.layout",
    "plone.memoize",
    "zope.annotation",
    "zope.cachedescriptors",
    "zope.component",
    "zope.datetime",
    "zope.formlib",
    "zope.interface",
    "zope.publisher",
    "zope.schema",
    "zope.traversing",
    "suds",
    "cmislib",
    ]
if sys.version_info < (2, 6):
    requires += [
        "uuid"
        ]

tests_requires = [
    "Products.PloneTestCase"
    ]

setup(name='collective.cmisbrowser',
      version=version,
      description="CMIS repository browser for Plone",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        ],
      keywords='CMIS connection browser plone',
      author='Sylvain Viollon',
      author_email='sylvain@infrae.com',
      url='http://pypi.python.org/pypi/collective.cmisbrowser',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require = tests_requires,
      extras_require = {'test': tests_requires},
      )

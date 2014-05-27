from setuptools import setup, find_packages
import sys, os

version = '0.8.0'

setup(name='formbar',
      version=version,
      description="Python library to layout, render and validate HTML forms in web applications",
      long_description=open('README.rst').read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
                   'Programming Language :: Python :: 2.7'],
      keywords='python form validate web html',
      author='Torsten Irl\xc3\xa4nder',
      author_email='torsten@irlaender.de',
      url='https://bitbucket.org/ti/formbar',
      license='GPL',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['pyparsing==1.5.6',
                        'formencode',
                        'babel',
                        'mako'],
      # Used for the example server
      extras_require={'examples':  ["pyramid"]},
      setup_requires=["hgtools"],
      entry_points="""
      # -*- Entry points: -*-
      [babel.extractors]
      formconfig = formbar.i18n:extract_i18n_formconfig
      """,

      message_extractors = {'formbar': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('**.xml', 'formconfig', None)]},
      )

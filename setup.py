from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='formbar',
      version=version,
      description="Python library to layout, render and validate HTML forms in web applications",
      long_description=open('README.rst').read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
                   'Programming Language :: Python :: 2.7'],
      keywords='python form validate web html',
      author='Torsten Irl\xc3\xa4nder',
      author_email='torsten@irlaender.de',
      url='https://github.com/toirl/formbar',
      license='GPL',
      packages=['formbar'],
      package_dir={'formbar': 'formbar'},
      package_data={'formbar': ['templates/*.mako']},
      include_package_data=True,
      zip_safe=False,
      install_requires=['pyparsing==1.5.6',
                        'formalchemy',
                        'formencode',
                        'mako'],
      # Used for the example server
      extras_require={'examples':  ["pyramid"]},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='formbar',
      version=version,
      description="Python library to layout, render and validate HTML forms in web applications",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python form validate web html',
      author='Torsten Irl\xc3\xa4nder',
      author_email='torsten@irlaender.de',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'pyparsing==1.5.6'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

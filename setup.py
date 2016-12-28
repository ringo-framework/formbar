from setuptools import setup, find_packages
import multiprocessing
import sys, os

version = '0.24.3'

setup(name='formbar',
    version=version,
    description="Python library to layout, render and validate HTML forms in web applications",
    long_description=open('README.rst').read(),
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
                 'Programming Language :: Python :: 2.7'],
    keywords='form configuration layout rendering serialisation validation rules conditionals html',
    author='Torsten Irl\xc3\xa4nder',
    author_email='torsten@irlaender.de',
    url='https://github.com/ringo-framework/formbar',
    license='GNU General Public License v2 or later (GPLv2+)',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['brabbel>=0.2.6',
                      'sqlalchemy',
                      'babel',
                      'python-dateutil',
                      'mako',
                      'webhelpers'
                      ],
    # Used for the example server
    tests_require=["nose"],
    extras_require={'examples':  ["pyramid"]},
    setup_requires=[],
    entry_points="""
    # -*- Entry points: -*-
    [babel.extractors]
    formconfig = formbar.i18n:extract_i18n_formconfig
    """,

    message_extractors = {'formbar': [
          ('**.py', 'python', None),
          ('templates/**.mako', 'mako', None),
          ('**.xml', 'formconfig', None)]},
    test_suite='nose.collector',
    )

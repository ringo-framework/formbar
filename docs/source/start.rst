Getting Started
***************

About
=====
Formbar is a python library to layout, render and validate HTML forms in web
applications. Formbar renders forms which are compatible with `Twitter
Bootstrap <twitter.github.com/bootstrap/>`_ styles.

In contrast to many other form libraries forms with formbar are configured in XML
files to separate the form definition form the implementation and handle it as
configuration.

Formbar is the German word for "shapeable" and should emphasise the
character of formbar which hopefully makes shaping your forms more easy.

Installation
============
Formbar is available as `Pypi package <https://pypi.python.org/pypi/formbar>`_.
To install it use the following command::

        <venv> pip install formbar

The source is availble on `Bitbucket <https://bitbucket.org/ti/formbar>`_.
You can check of the source and install the library with the following
command::
        
        (venv)> hg clone https://bitbucket.org/ti/formbar
        (venv)> cd formbar
        (venv)> python setup.py develop # use develop for development install

.. tip::

   I recommend to install the library for testing issue in the virtual python
   environment. See `Virtualenv documentation
   <http://www.virtualenv.org/en/latest/>`_ for more details.

Features
========
 * Support for SQLAlchemy mapped items and plain forms.
 * Expression bases rules
 * Conditionals in forms
 * Type conversation and validation
 * XML based form definition
 * i18n Support
 * Row and column based layouts
 * Different form layouts for the same model (Create, Edit, Read...)
 * Twitter bootstrap support
 * Custom CSS styling
 * Error and warning messages
 * Help texts
 * Numbering of fields
 * Extern defined renderers
 * ...

Quickstart
==========
See :ref:`Quickstart`

Demo-Server
===========
Formbar comes with a very simple demo server to give you a impress on some
features of formbar.

To run the server do the following::

        cd examples
        python serve.py


Licence
=======
Formbar is licensed with under the GNU general public license version 2.

Authors
=======
Torsten Irländer <torsten at irlaender dot de>

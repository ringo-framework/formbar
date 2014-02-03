Getting Started
***************

About
=====
.. include:: about.rst

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
.. include:: features.rst

Quickstart
==========
You will not need much code to include formbar in your application to be able
to render nice forms. Only a few lines of code are needed::

        from formbar.config import Config, load
        from formbar.form import Form
        # Simple rendering here, no data submission
        # nor validation or saving.
        config = Config(load('/path/to/formconfig.xml'))
        form_config = config.get_form('example')
        form = Form(form_config)
        form.render()


Licence
=======
Formbar is licensed with under the GNU general public license version 2.

Authors
=======
Torsten Irländer <torsten at irlaender dot de>

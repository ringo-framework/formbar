Formbar
=======

Formbar is a python library to layout, render and validate HTML forms in web
applications. Formbar renders forms which are compatible with `Twitter
Bootstrap <twitter.github.com/bootstrap/>`_ styles.

In contrast to many other form libraries forms with formbar are configured in XML
files to separate the form definition form the implementation and handle it as
configuration.

Formbar is the German word for "shapeable" and should emphasise the
that formbar hopefully makes shaping your forms more easy.

Formbar uses a subset of the
`FormAlchemy <https://pypi.python.org/pypi/FormAlchemy/>`_ as underlying
library for rendering and basic validation.

Features
--------

* Support for SQLAlchemy mapped items and plain forms.
* Expression bases rules
* Type conversation and validation
* XML based form definition
* Row and column based layouts
* Error messages
* Help texts
* Numbering of fields

Getting started
---------------
Please refer to formbar documentation for further information how to get
started using formbar.
For all the impatient out there here comes a very comprehensive example code
which should give a glimpse on how things could work for you::

        from formbar.config import Config, load
        from formbar.form import Form

        # Simple rendering here, no data submission
        # nor validation or saving.
        config = Config(load('/path/to/formconfig.xml'))
        form_config = config.get_form('example')
        form = Form(form_config)
        form.render()


Documentation
-------------
Formbar should be well documented and comes with documentation, bunch of
unitests and last but not least an example serve which serve some example
forms.

Licence
-------
Formbar is Free Software and licensed under GPL version 2.

Project state
-------------
Formbar is in a early project state and still in under development including
large design changes. Call it alpha if you want.

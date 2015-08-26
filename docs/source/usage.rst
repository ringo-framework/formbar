.. _quickstart:

Usage
*****
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

This is of course just a very easy configuration. See sections below for more
options on usage.

The configuration of the form happens in a XML configuration file. See
:ref:`form_config` for more details on options to configura a form. Such a
configuration file can be loaded by using the :func:`.load` function to create
a form configuration :class:`.Config` object.

As the form configuration usually contains more than one form configuration
(different configurations for editing, reading or creating new items) you will
need get the form configuration for a specific form by calling the
:func:`.get_form` method.

This configuration can be used to create a new :class:`.Form`.

Form configuration
==================
There are some things which can be configured when initializing the form.

SQLAlchemy support
------------------
Formbar can work with mapped SQLAlchemy items. You can provide such an item as
*item* attribute while initializing the form.

Translation
-----------
Formbar support translation of the following parts of the form:

 * Labels
 * Error and Warning messages
 * Help
 * Text

To make the translation work you will need to provide a translation function
with the *translate* parameter while initializing a :class:`.Form` instance.

This translation function can be any function which behaves like a *gettext*
method.

..  TODO: Write hint on how to create PO files. (ti) <2014-12-28 23:32> 

.. _conf_custom_renderer:

Use Custom renderers
--------------------
To use custom renderers you will need to provide the classes of the renderes
with the *renderer* parameter while initializing a :class:`.Form` instance.

The renderers are provided as a dictionary::

        from your.app.renderer import FooFieldRenderer, BarFieldRenderer
        renderers = {
                "foo": FooFieldRenderer
                "bar": BarFieldRenderer
        }

The key of the dictionary is the name of the `type` form the entities renderer in the
the form configuration.

See :ref:`custom_renderer` for more details on how to create a custom renderer.

Use Custom validators
---------------------
Write me.

Rule evaluation
---------------
Rule evaluation on client side is done by sending AJAX requests to a specific
URL which takes care of evaluating the submitted rules and returning the
correct respose. The URL to which those requests are sent can be provided with
the *eval_url* parameter.

.. hint::
   Formbar can be run as server (See serve.py for more details). This server
   provides such an URL under localhost:8080/evaluate.

CSRF Token
----------
Formbar supports rendering a hidden field in its form which includes the
string provided as the *csrf_token* parameter while initializing the form.

The generated field look like this::

        <input type="hidden" name="csrf_token" value="fe84d264dc7b9f25cce309c275464c1a60f6074a"/>

The value can be used on the server side to to some protection against CSRF
Attacks.

If no parameter is provided no field will be generated.

Render
======
See :func:`.render` for more details on options for rendering the form.

Validation
==========
To validate the submitted form data you can use the :func:`.validate` function::

        if form.validate(request.POST):
            errors = form.get_errors()
            warnings = form.get_warnings()
            submitted = form.submitted_data
            # Handle Error
        else:
            warnings = form.get_warnings()
            validated = form.data
            # Handle Success

The validation will take care of correct conversation into python types and
rule checking.
In case the validated succeeds, the *data* attribute of the form will hold the
converted python data based on the fields data type.

Saving data
===========
Saving of the converted data after validation is usually done in the
application and **not** by formbar. Although formbar provides a :func:`.save`
method for mapped SQLAlchemy items but this method is deprecated.

Generate specification
=======================

You can generate a specification based on the form configuration and
additional :ref:`metadata` by using the `formspec.py` command.

``formspec.py`` parses Formbar XML configuration files in order to convert them
to different formats.  Its main purpose is to convert the XML data into a
human-readable form specification in RST format.

A specification is generated per form. The command can be invoked like this::

        python formbar/contrib/formspec.py --title Foo --form update /path/to/foo.xml > foo.rst


The `--title` parameter is optional. It will set the topmost heading of the
specification to the given titel. Otherwise the name of the form will be used.

The `--form` parameter is optional. On default the "update" form will be used
to generate the specification.

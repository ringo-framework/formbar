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

Configuration
=============
The configuration of the form happens in a XML configuration file. See
:ref:`form_config` for more details on options to configura a form. Such a
configuration file can be loaded by using the :func:`.load` function to create
a form configuration :class:`.Config` object.

As the form configuration usually contains more than one form configuration
(different configurations for editing, reading or creating new items) you will
need get the form configuration for a specific form by calling the
:func:`.get_form` method.

This configuration can be used to create a new :class:`.form.Form`.

Translation
-----------

Custom Renderers
----------------


CSRF Token
----------

Render
======
Write me!

Validation
==========
Write me!

Saving
======
Write me!

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

Render
======
Write me!

Validation
==========
Write me!

Saving
======
Write me!

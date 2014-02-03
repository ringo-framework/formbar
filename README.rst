Formbar
=======

Formbar is a python library to layout, render and validate HTML forms in web
applications. Formbar renders forms which are compatible with `Twitter
Bootstrap <twitter.github.com/bootstrap/>`_ styles.

In contrast to many other form libraries forms with formbar are configured in XML
files to separate the form definition form the implementation and handle it as
configuration.

Formbar is the German word for "shapeable" and should emphasise the
character of formbar which hopefully makes shaping your forms more easy.

Features
--------

* Support for SQLAlchemy mapped items and plain forms
* Expression bases rules and elements
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

The corresponding configuration file might look like this one.::

        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <configuration>
          <source>
            <!-- Define different entity types -->
            <entity id="e1" name="float" label="Float field" type="float">
              <rule expr="$float lt 100" msg="Float must be lower than 100" mode="post"/>
              <help>This is is a very long helptext which should span over
              multiple rows. Further the will check if there are further html
              tags allowed.</help>
            </entity>
            <entity id="e2" name="select" label="Select field" type="string">
              <help>This is my helptext</help>
              <options>
                <option value="1">Option 1</option>
                <option value="2">Option 2</option>
                <option value="3">Option 3</option>
                <option value="4">Option 4</option>
              </options>
            </entity>
          </source>
          <!-- The entities are finally only referenced to layout the form -->
          <form id="example1" css="testcss" autocomplete="off" method="POST" action="" enctype="multipart/form-data">
            <row>
              <col><field ref="e1"/></col>
            </row>
            <row>
              <col><field ref="e2"/></col>
            </row>
          </form>
        </configuration>

This is a very simple example just to get an impression. There are many more
configuration options. See the examples folder for more information on the
configuration or how the validation works.


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

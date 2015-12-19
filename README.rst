Formbar
=======
.. image:: https://travis-ci.org/ringo-framework/formbar.svg
    :target: https://travis-ci.org/ringo-framework/formbar
.. image:: https://api.codacy.com/project/badge/grade/d2d6ae5518b34416a4d3f0f7fecfd35a
    :target: https://www.codacy.com/app/torsten/formbar
Formbar is a python library to layout, render and validate HTML forms in web
applications. Formbar renders forms which are compatible with `Twitter
Bootstrap <twitter.github.com/bootstrap/>`_ styles.

Formbar is the German word for "shapeable" and should emphasise the
character of formbar which hopefully makes shaping your forms more easy.

In contrast to many other form libraries forms with formbar are configured in XML
files to separate the form definition form the implementation and handle it as
configuration.

Formbar is production ready and already used in applications with large forms.

Licence
-------
Formbar is Free Software and licensed under GPL version >= 2.

Documentation
-------------
Online documentation can be found `formbar.readthedocs.org <https://formbar.readthedocs.org>`_

Features
--------
* Conversion between Python values and value in the form and vice versa.
* i18n support for labels and texts in the form.
* Conditional fields in the form. E.g Render fields readonly if other fields
  have a certain value.
* Flexible form definition and layout.
  
  * Different form layouts for the same model (Create, Edit, Read...)
  * Support for inheritance and including parts of other forms.
  * Support for different pages, sections and subsections.

* Styling

  * Twitter bootstrap support
  * Row and column based layouts
  * Custom CSS styling
  * Numbering of fields
  * XML based form definition
  * Help texts

* Validation:

  * Basic datatype validation on conversion for different types of data (date, int, float, email...).
  * Rule based validation in the form using expressions (`brabbel <http://github.com/toirl/brabbel>`_).
  * Error and warning messages

* Expandable

  * Support for external renderers
  * Support for writing external validators

* Support for SQLAlchemy mapped items and plain forms

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

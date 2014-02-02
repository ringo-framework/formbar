Getting Started
***************

About
=====
Formbar is a python library to layout, render, and validate data in HTML forms
in web applications.

Installation
============
Formbar is availble on `Bitbucket <https://bitbucket.org/ti/formbar>`_.
You can check of the source and install the library with the following
command::
        
        (venv)> hg clone https://bitbucket.org/ti/formbar
        (venv)> cd formbar
        (venv)> python setup.py develop # use develop for development install

.. tip::

   I recommend to install the library for testing issue in the virtual python
   environment. See `Virtualenv documentation
   <http://www.virtualenv.org/en/latest/>`_ for more details.


Form configuration
******************
The form will be configured using a XML definition. The configuration is
basically splitted into two parts:

1. The definition of the datamodel.
2. Definition and Layout of forms.

The basic form configuration looks like this::

        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <configuration>
           <source>
           <!-- Define different entity types -->
           </source>
           <form>
           <!-- Define and layout a form -->
           </form>
           <snippet>
           <!-- Container holdig parts of a form definition -->
           </snippet>
        </configuration>

The :ref:`snippet` element is optional and just a helper.

Source
======
The ``source`` directive defines the :ref:`entity` are available in your
forms.  An entity is defined only once in the source section. It will get
referenced in the :ref:`form` directive later to build the forms.

.. _entity:

Entity
------
A :ref:`entity` is a field definition.
The entity is used to configure aspects of the *datamodel* the *layout*
and *behaviour* of the field in the form.

Here is an example of an entity definition::

    <entity id="f1" name="age" label="Age" type="integer" css="field" required="true">
        <renderer type="text"/>
        <help>This is a help text</help>
        <rule expr="$age ge 21" msg="Age must be greater than 21"/> 
    </entity>

Entities can be marked as *required* or *desired*. Formed will generate
automatically a :ref:`rule`  for this field. Missing required fields will
trigger an error on form validation. Desired fields will trigger a warning.

Each entity can optional have a :ref:`renderer`, :ref:`rule` or :ref:`help`
element.

=========   ===========
Attribute   Description
=========   ===========
id          Used to refer to this entity in the form. Requiered. Must be unique.
name        Used as name attribute in the rendered field. Defines the 
            name of this attribute in the model.
label       The field will be rendered with this label.
type        Defines the python datatype which will be used on deserialisation of the submitted value. Defines the datatype of the model. Possible values are ``string`` (default), ``integer``, ``float``, ``date``, ``datetime``.
css         Value will be rendered as class attribute in the rendered field.
required    Flag to indicate that the is a required field. Default is ``false``.
desired     Flag to indicate that the is a desired field. Default is ``false``.
=========   ===========

.. _rule:

Rule
----
Rules are used to validate data in the form Formed does already some basic
validated on the submitted data depending on the configured data type in the
:ref:`entity`. These checks are often already sufficient for most basic forms.

If you need more validation rules can be used to define additional checks.
There are two types of rules. Rules which triggers errors, and rules which
trigger a warning if the evaluation of the rule fails.

Rules are evaluated in the process of validation the submitted data. On
validation formed will collect warning and errors and will rerender the form
displaying them. If the form has errors the validation fails. Warnings are ok
for validation.

Validation of rules can be done in differen modes. Rules with the mode ``pre``
are evaluation before the deserialisation of the submitted value occurs into
the python data type of the field. In contrast rules with mode ``post`` are
evaluation after the deserialisation happened.

Here is a example rule::

        <rule expr="$age ge 21" msg="Age must be greater than 21" mode="post" triggers="warning"/>

Here you can see a example rule. The rule will check the value of field "age"
($age) is greater or equal that the value 21. The rule is evaluated in post
mode. And will trigger a warning if the evaluation fails.

=========   ===========
Attribute   Description
=========   ===========
expr        Expression which is used to validate the value if the field.
msg         The message which is displayed if the evaluation of the rule fails.
mode        Point in validation when this rules gets evaluations. ``post`` (default) means after the deserialisation of the value and ``pre`` is before deserialisation.
triggers    Flag which defines which type of message a the rule will trigger if the evaluation fails. Be be ``error`` (default) or ``warning``.
=========   ===========

.. _help:

Help
----

.. _renderer:

Renderer
--------

.. _form:

Form
====

Row
---

Col
---

Field
-----

Conditional
-----------

.. _snippet:
Snippet
-------


Configuration
#############
Configuration of your forms is done in XML files. These files configure

1. Which fields are available. Further you can configure various aspects of
   the fields.

2. The layout of the form.

.. important::

   When rendering SQLAlchemy mapped instances the configuration is
   **optional**. For basic form rendering you will not need any configuration
   at all. In this case the rendering will fall back in the default mode
   provided my the underlying form library. See :ref:`examples` for more
   information.

The configuration is divided into three parts::

        <configuration>
          <source>
            ...
          </source>
          <form>
            ...
          </form>
          <snippets>
            ...
          </snippets>
        </configuration>

We will now discuss the different parts of the form.

Source and Entities
===================
The ``source`` directive defines which entities are available in your forms.
A entity is a field definition. You can define various attributes for each
entity. The entities are later referenced in the form layouting and the
entities attributes are used for rendering and validating the form data.

So the entities are the source fields and the base for which is called Schema
in frameworks like colander, formencode etc.  However the schema is actually
defined within the form configuration.

Entity
------
Here is an example of an entity definition::

    <entity id="f1" name="age" label="Age" type="integer" css="field">
        <renderer type="text"/>
        <help>This is a help text</help>
        <rule expr="$age >= 21" msg="Age must be greater than 21"/> 
    </entity>

For a complete list of supported attributes please refer to the ``FieldConfig`` documentation.
As you can the entity definition embeds three further elements which are all
optional:

Renderer
^^^^^^^^
The renderer directive is used to configure an alternative
renderer for the field. If no renderer is defined. Than the default renderer
depending on the entity data type will be chosen.

Help
^^^^
A entity can have a help directive. The content of the help directive can be a
normal string and will be placed below the rendered field element.

Rule
^^^^
The rule directive is used to define (additional) checks on the submitted
values. Additional means that there are already some basic checks based on the
datatype of the entity. So you will not need to define an additional check for
an integer field to check if the submitted value is actually a integer. This
check is automatically added. See :ref:`rules` for more informations.

.. _forms:

Form
====
The form configuration is used to define a form. The form definition will 

1. Define the layout of the form, and
2. Configure which ``Entities`` will be included in the form.

A typical form configuration might look like this::

    <form id="myform" autocomplete="off" enctype="multipart/form-data">
        <snippet ref="s1"/>
        <snippet ref="s2"/>
    </form>

The form directive can have some attributes which are all optional beside the
`id` attribute. See ``Form`` API for a full description of available attributes.

Within the form directive the layout of the form will be defined. In this case
we reference two ``Snippet`` directives which will hold the layout. This way
we can define some common used layout only once and refer to them in different
forms.

We will describe the layouting possibilities in detail in  the :ref:`snippets` chapter.

.. _snippets:

Snippets
========
Snippets are containers for you layout. As you see in the :ref:`forms` chapter
the can be referenced in multiple forms. Further a snippet include and refer to
another snippets. This way you can build quite complex layouts without
repeating yourself.

This is what a typical snippet might look like::

    <snippet id="s1">
        <page label="Page 1">
            <row>
                <col><field ref="f1"></col>
                <col><field ref="f2"></col>
            </row>
        </page>
        <page label="Page 2">
            <row>
                <col>
                     <if type="readonly" expr="$fieldname == 0">
                         <field ref="f3">
                     </if>
                </col>
            </row>
            <snippet ref="s2"/>
        </page>
    </snippet>

Page
----
Use pages if you want to divide your form into multiple pages. Pages are
rendered as tabs in the form.

Row
---
A form or pages can be divided in rows. Each row can have 1,2,3,4,6 or 12
cols elements.

Col
---
A row can be divided into columns. Each column can have either a field or
another row.

Field
-----
The field is the field which will be rendered. It refers to an entity.

If (Conditional)
---------------
Conditional can be used to hide, or rendered form elements like fields,
tables, fieldsets and text elements within the conditional as readonly
elements.

If the condition must evaluate to true or false. If true, the elements are
rendered normal. If the condition is false the effect is determined by the
type of the conditional. On default the elements will be hidden completely. As
alternative you can set the type of the conditional to "readonly". Currently
only the types "hide" (default) and "readonly" are supported. Expample::

        <if type="readonly" expr="$fieldname == 4">
            <field ref="r1"/>
        </if>

In the example above the referenced field will be shown if the field in the
form with the name "fieldname" has the value of 4. Else the element will
be set to readonly and the element will have a lowered opacity.

Conditionals are evaluated using JavaScript on the client side. Formbar also
needs to evaluate the conditional internal on validation to determine which
values will be taken into account while validating. As result validation rules
will not be applied for "hidden" fields.

Api
===
.. automodule:: formbar.config
   :members:

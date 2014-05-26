Form configuration
******************
The form will be configured using a XML definition. The configuration is
basically splitted into two parts:

1. The definition of the datamodel in the *source* directive.
2. Definition and Layout of forms in *forms*.

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

Entities can be marked as *readonly*. Readonly fields are renderer as simple
text in the form displaying the current value of the field. Note, that
readonly fields are not sent on submission! If you need the value if the form
you will need to add an additional entity and render is with the hidden field
renderer.

Each entity can optional have a :ref:`renderer`, :ref:`rule` or :ref:`help`
element.

=========   ===========
Attribute   Description
=========   ===========
id          Used to refer to this entity in the form. Requiered. Must be unique.
name        Used as name attribute in the rendered field. Defines the 
            name of this attribute in the model.
label       The field will be rendered with this label.
number      A small number which is rendered in front of the label.
type        Defines the python datatype which will be used on deserialisation of the submitted value. Defines the datatype of the model. Possible values are ``string`` (default), ``integer``, ``float``, ``date``, ``datetime``.
css         Value will be rendered as class attribute in the rendered field.
expr        Expression which is used to calculate the value of the field.
value       Default value of the field. Supports expressions. The default value might get overwritten on rendering.
readonly    Flag to indicate that the field should be rendered as readonly field. Default is ``false``.
required    Flag to indicate that the is a required field. Default is ``false``.
desired     Flag to indicate that the is a desired field. Default is ``false``.
=========   ===========

.. _rule:

Rule
----
Rules are used to validate data in the form. Formed does already some basic
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
The help block can be used to add some information to the field for the user.
The help will be rendererd below the field in the form.

.. _renderer:

Renderer
--------
The renderer directive can be used to configure an alternative renderer to be
used to render the field.

The default renderer is chosen depending on the datatype of the field and is a
textfield for almost all normal datatypes. On relations (in SQLAlchemy mapped
items) a selection field is used for the relations.

There are different types of renderers available coming with formed. But it
is very easy to provide formed with your own custom renderer.

Label
`````
The lable tag can be used to have more options to configure the rendering
of the fields label. The label tag can be seen as a configuration
option of the renderer::

        <renderer>
            <label position="left" align="right" width="4"/>
            ...
        </renderer>

The label tag is only used to configure the position, alignment and the
width of the label. The text of the label is still configured in the
entitiy.

=========   ===========
Attribute   Description
=========   ===========
position    The position of the label realtive to the field element. Can be "left", "top", "right". Defaults to "top".
align       The alignment of the text in the label. This only applies for labels with position set to "left" or "right". Can be "left" and "right". Defaults to "left".
align       The width of the label in cols. The whole field including the label can be deived into 12 cols. If the label has e.g 4 cols the field will automatically take the remaining 8 cols. This only applies for labels with position set to "left" or "right".
=========   ===========

Textarea
````````
Use this renderer if you want to render the field as a textfield::

        <renderer type="textarea" rows="20"/>

=========   ===========
Attribute   Description
=========   ===========
rows        Number of rows of the texteare. Default is 3.
=========   ===========

Infofield
`````````
The info field renderer is used to render the value of the entity as
textual information. This renderer is usually used to display calculated
values of the entity. See the ``expr`` attribute of the :ref:`Entity`. If you
simply want to display a static value comming from on of the items attribute
you can also use the ``value`` attribute.
Appearance is same as a readonly field::

        <renderer type="infofield"/>

Selection
`````````
The selection renderer is used to render a selection list fields. Such a field
is capable to select multiple options. The renderer defines also the options
which should be available in the dropdown menu. For SQLAlchemy mapped items
the options are automatically determined from the underlying data model::

        <entity>
          <renderer type="selection"/>
          <!-- Note, that the options are part of the entity! -->
          <options>
             <option value="1">Option 1</option>
             <option value="2">Option 2</option>
             <option value="3">Option 3</option>
          </options>
        </entity>

=============== ===========
Attribute       Description
=============== ===========
filter          Expression which must evaluate to True if the option shoul be shown in the Dropdown.
remove_filtered Flag "true/false" to indicate that filtered items should not be rendered at all. On default filtered items will only be hidden and selection is still present.
ignore          Another way to filter options. (Deprecated)
=============== ===========

.. note::
   Filtering is only possible for SQLAlchemy mapped items.

Filtering can be done by defining a expression in the filter attribute. This
expression is later evaluated by the rule system of formbar. The expression
must evaluate to true and is evaluated for every option. The expression uses a
two special variables begining with 

1. ``%``.  Variables begining with % marks the
name of an attribute of the current options item. The variable will be
replaced by the value of the attribute of the current item in the option for
every option before evaluating.
2. ``@``. Varaible beginning with @ marks the name of an attribute of
the parents form item.

Both variables support accessing related items through the dot-syntax:: 
        
        <renderer type="selection" filter="%foo eq @bar.baz">

The ignore attribute offers another but deprecated way to filter options. It
syntax differs from the filter expression. See source for more information.

.. _dropdown:

Dropdown
````````
The dropdown renderer is used to render dropdown fields. The renderer defines
also the options which should be available in the dropdown menu. For
SQLAlchemy mapped items the options are automatically determined from the
underlying data model::

        <renderer type="dropdown">
           <option value="1">Option 1</option>
           <option value="2">Option 2</option>
           <option value="3">Option 3</option>
        </renderer>

=========   ===========
Attribute   Description
=========   ===========
filter      Expression which must evaluate to True if the option shoul be shown in the Dropdown.
ignore      Another way to filter options. (Deprecated)
=========   ===========

.. note::
   Filtering is only possible for SQLAlchemy mapped items.

See filtering section of the :ref:`dropdown` renderer.

Radio
`````
The radio renderer is used to render radio fields based on the given options.
Such a field is capable to select only one option. For SQLAlchemy mapped
items the options are automatically determined from the underlying data
model. The radionfields will be aligned in a horizontal row::

        <entity>
          <renderer type="radio"/>
          <options>
             <option value="1">Option 1</option>
             <option value="2">Option 2</option>
             <option value="3">Option 3</option>
          </options>
        </entity>

=============== ===========
Attribute       Description
=============== ===========
filter          Expression which must evaluate to True if the option shoul be shown in the Dropdown.
remove_filtered Flag "true/false" to indicate that filtered items should not be rendered at all. On default filtered items will only be hidden and selection is still present.
ignore          Another way to filter options. (Deprecated)
align           Alignment of the checkboxes. Can be "vertical" or "horizontal". Defaults to "horizontal".
=============== ===========

See filtering section of the :ref:`dropdown` renderer.

Checkbox
````````
The checkbox renderer is used to render checkbox fields based on the given options.
Such a field is capable to multiple options. For SQLAlchemy mapped
items the options are automatically determined from the underlying data
model. The checkboxes will be aligned in a horizontal row::

        <entity>
          <renderer type="checkbox"/>
          <options>
             <option value="1">Option 1</option>
             <option value="2">Option 2</option>
             <option value="3">Option 3</option>
          </options>
        </entity>

=============== ===========
Attribute       Description
=============== ===========
filter          Expression which must evaluate to True if the option shoul be shown in the Dropdown.
remove_filtered Flag "true/false" to indicate that filtered items should not be rendered at all. On default filtered items will only be hidden and selection is still present.
ignore          Another way to filter options. (Deprecated)
align           Alignment of the checkboxes. Can be "vertical" or "horizontal". Defaults to "horizontal".
=============== ===========

See filtering section of the :ref:`dropdown` renderer.

Datepicker
``````````
The datepicker renderer has some Javascript functionality which lets the used
pick the date from a calender. It also only allows valid date entries per
keyboard::

        <renderer type="datepicker"/>

Password
````````
The password renderer renderes a password field which hides the users input::

        <renderer type="password"/>


Hidden
``````
The hidden field renderer is used to render a hidden field for the entity. No
labels, helptexts or error messages will be renderer. The hidden field will
also take care on relations for SQLAlchemy mapped items::

        <renderer type="hidden"/>

Html
````
The html renderer is used to render custom html code. This is usefull if you
want to render generic text sections or insert images. Images will need a
external source for the image file. The html renderer will render Javascript
, Stylesheets and HTML code::

        <renderer type="html">
         <div>
           <p>You can include all valid html including images, lists etc.</p>
           <p><strong>Warning:</strong>Also JS can be included.</p>
         </div>
        </renderer>

Your custom code should be wrapped into a empty div node. Otherwise only the
first child node of the renderer will be rendererd.
The entity only needs the id attribute. If a label is provided, the label
will be uses as some kind of header to the html part.

.. warning::
   Use this renderer with caution as it may introduce a large security hole if
   users inject malicious javascript code into the form using the html renderer.

.. _form:

FormbarFormEditor
`````````````````
Use this renderer if you want to render a editor for formbar forms. The
Editor will have a preview window which shows the result of the
rendering of the form. If rendering fails, the preview will show the
errors which happened while rendering::

        <renderer type="formbareditor" url="foo/bar" rows="20"/>

=========   ===========
Attribute   Description
=========   ===========
rows        Number of rows of the texteare. Default is 3.
url         URL which is called to renderer the form.
=========   ===========

Form
====
The form directive is the place where the form definition and layout happens.

.. hint::
   You can define more than one form in one configuration. This gets very
   handy if you want to define different forms for differen purposes. Example:
   You have a form to create a new item with a reduced set of fields. Another
   form which has all fields included can be used to edit the item.

Forms are built by using references to the defined entities packed in some
layout directives::

        <form id="create" css="fooish" autocomplete="off" method="POST" action="" enctype="multipart/form-data">
        ...
        </form>



============   ===========
Attribute      Description
============   ===========
id             Unique id of the field.
css            The attribute will be added to the *class* attribute of the form.
autocomplete   Flag to indicate if the form should be autocompleted by the browser. Defaults to ``on``.
method         HTTP method used to submit the data. Defaults to POST.
action         URL where is submitted data is sent to. Default to the current URL.
enctype        Encrytion used while sending the data. Defaults to ``application/x-www-form-urlencoded``. Use ``multipart/form-data`` if you plan to submit file uploads.
============   ===========

Buttons
-------
Optional directive within the form tag to configure custom buttons for the
form. If not defined the default Submit and Reset Buttons are renderered::

        <buttons>
          <button type="submit" value="delete" name="_submit" class="warning" icon="glyphicon glyphicon-delete">Delete</button>
          ...
        </buttons>

Buttons are rendererd at the bottom of the form element.
The first button in the definition will be the first button on the left side.

============   ===========
Attribute      Description
============   ===========
type           Optional. Type of action the button will trigger on the form (submit, reset). Defaults to ``submit``
value          Optional. Value which is submitted in the form. Defaults to the buttons text.
name           Optional. Name under which the value will be available in the submitted data Defaults to ``_$type``.
class          Optional. CSS class which will be added to the button.
icon           Optional. Definition of glyphicons which will be displayed before the buttons label.
============   ===========

Page
----
Use pages if you want to divide your form into multiple pages. Pages are
rendered as a separate outline of the form on the left site to navigate
through the form pages.

Row, Col
--------
Used to layout the form::

        <row>
          <col></col>
          <col></col>
        </row>
        <row>
          <col width="8"></col>
          <col width="2"></col>
          <col width="2"></col>
        </row>

The form is divided into 12 virtual cols. The width of each col is calculated
automatically. A single in a row will have the full width of 12. For 2 cols in
a row each col will have a width of 6 cols. If you define 3 cols each col will
have a width of 4 and so on.

You can alternatively define the *width* of the col. If you provide the width of
the col you need to take care that the sum of all cols in the row is 12 to not
mess up the layout.

Rows and cols can be mixed. So rows can be in cols again.

============   ===========
Attribute      Description
============   ===========
width          Width of the col (1-12).
============   ===========

Fieldset
--------
A fieldset can be used to group fields into a logical unit a fieldset will
have a label which is rendered as a heading above the first field of the
fieldset.  Fieldsets can be nested to model some kind of hierarchy. Formbar
supports up to three levels. The size of the font in the fieldset legend will
be reduced a littlebit on every level.::

        
        <fieldset label="1. Foo">
        ...
          <fieldset label="1.1 Bar">
            <row>
              <col></col>
              <col></col>
            </row>
          <fieldset>
        <fieldset>

A fieldset can include almost all other directives.


============   ===========
Attribute      Description
============   ===========
label          Label of the fieldset rendered as header.
============   ===========

Text
----
Text can be used to add some simple text information in the form. It does not
support any formatting of the text. If you need more formatting please use the
html renderer::

      <row>
        <col><text>Hello I'm Text</text></col>
        <col><text>Hello I'm a seconds Text</text></col>
      </row>


============   ===========
Attribute      Description
============   ===========
color          Color of the text. Possible options: "muted", "warning", "danger", "info", "primary", "success". Defaults to no change of the current text color.
bg             Color of the background. Possible options: "warning", "danger", "info", "primary", "success". Defaults to render no background.
em             Emphasis of the text. Possible options: "strong", "small", "em" (italic). Defaults to no emphasis.
============   ===========

Table
-----
.. important::
   Tables should not be used to layout the form!

Tables can be used to arrange your fields in a tabuluar form. This becomes
handy in some situations e.g to build your own widget::

        <table>
          <tr>
            <th>Criteria</th>
            <th>Male</th>
            <th>Female</th>
          </tr>
          <tr>
            <td width="70%">Number of humans in the world</td>
            <td><field ref="men"/></td>
            <td><field ref="women"/></td>
            <td><field ref="total"/></td>
          </tr>
        </table>

Tables are usually used in the same way as :ref:`field` is used. Tables will
take 100% of the available space. You can set the ``width`` attribute of the
<td> field to configure the width of the columns. The width of the
column can be set to % or pixel.

The following attributes are supported for the ``td`` and ``th`` tags of the
table: ``width``, ``class`` , ``rowspan``, ``colspan``.

.. _field:

Field
-----
A field in the form. The field only references an :ref:`Entity`::

        <field ref="f1"/>

============   ===========
Attribute      Description
============   ===========
ref            id if the referenced :ref:`Entity`.
============   ===========


Conditional
-----------
Conditional can be used to hide, or render form elements like fields,
tables, fieldsets and text elements within the conditional as readonly
elements.

If the condition must evaluate to true or false. If true, the elements are
rendered normal. If the condition is false the effect is determined by the
type of the conditional. On default the elements will be hidden completely. As
alternative you can set the type of the conditional to "readonly". Currently
only the type "readonly" are supported. Expample::

        <if type="readonly" expr="$fieldname == 4">
            <field ref="r1"/>
        </if>

In the example above the referenced field will be shown if the field in the
form with the name "fieldname" has the value of 4. Else the element will
be set to readonly and the element will have a lowered opacity.

============   ===========
Attribute      Description
============   ===========
type           Effect of the conditional if the condition evaluates to false.  Defaults to ``hide``.
expr           The expression which will be evaluated.
============   ===========

Conditionals are evaluated using JavaScript on the client side. Formbar also
needs to evaluate the conditional internal on validation to determine which
values will be taken into account while validating. As result validation rules
will not be applied for "hidden" fields.

.. _snippet:

Snippet
-------
Snippets are reusable parts of your form definiton. Snippets allow you to
define parts of the form only once and use them in multiple forms.
Example: If you want to use the same form to create and edit than you can
define the form in a snippet and use it in the create and edit form::

        <form id="foo">
          <snippet ref="s1"/>
        </form>
        <form id="bar">
          <snippet ref="s1"/>
        </form>
        <snippet id="s1">
          <row>...</row>
        </snippet>

Snippet needs to be in a form to get rendered. Snippets can reference other
snippets using the ``ref`` attribute. Snippets are of great help if you want
to reduced the effort of rearranging groups of elements in the form. But on
the other side the can make the form quite complicated if you use them too
much. Use them with care.

============   ===========
Attribute      Description
============   ===========
id             Unique id of the snippet
ref            References the snippet with id.
============   ===========

Custom renderes
===============
Write me!

External validators
===================
Write me!

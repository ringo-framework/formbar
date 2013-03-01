.. _rules:

Rules
#####
Formed does already some basic checks on the submitted data depending on the
configured data type or, in case you are using a form for a SQLAlchemy mapped
item. These checks are often already sufficient for most basic forms.

Rules are used to define additional checks to the basic check.
Rules are evaluated in the process of validation the submitted data. If one of
the configured rules fail the validation will fail at all and the form gets
rerendered with all error messages.
Only if the whole validation is ok, the data will be saved.

There are two types of rules. And the type of the rule decides when the rule
gets evaluation in the validation process:

1. Pre-Rules. Rules with the mode "pre" are evaluation before the conversation
of the submitted value occurs into the python data type of the field.
2. Post-Rules. In contrast the post rules are evaluation after the conversation happened.

Why this? Well simply because some checks are much more easy on python data
types than on strings. Think of datetime checks for example.

Configuration
=============
Rules are configured in the form configuration XML file. Rules can be
configured as part of an ``Entity``, or as part of the ``Form``::

        <entity>
                <rule/>
                ...
                <rule/>
        </entity>

or::
        <form>
                <rule/>
                ...
                <rule/>
        </form>


But the definition of a rule is the same in both cases. Here is a simple
example rule::

        <rule expr="$age >= 21" msg="Age must be greater or equal than 21" mode="post"/>

Here you can see a example rule. The rule will check the value of field "age"
($age) *after* (postmode) the conversation has been done against the integer value 21.
If the rule fails, than an error message defined in the `msg`-attribute will
be shown at all fields within the expression in the form.

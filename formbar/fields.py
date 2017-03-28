#!/usr/bin/env python
# encoding: utf-8
import logging
import datetime
import re
import sqlalchemy as sa
from formbar.rules import Rule, Expression
import formbar.config as config

log = logging.getLogger(__name__)


def rules_to_string(field):
    return [u"{}".format(r) for r in field.get_rules()]


def get_sa_property(item, name):
    # Special handling needed to support namespaces in forms.
    names = name.split(".")
    if len(names) == 1:
        name = names[-1]
    else:
        item = getattr(item, ".".join(names[:-1]))
        name = names[-1]
    try:
        mapper = sa.orm.object_mapper(item)
        for prop in mapper.iterate_properties:
            if prop.key == name:
                return prop
    except:
        pass


def get_type_from_sa_property(sa_property):
    try:
        column = sa_property.columns[0]
        dtype = str(column.type)
        if dtype == "TEXT" or dtype.find("VARCHAR") > -1:
            return "string"
        elif dtype == "DATE":
            return "date"
        elif dtype == "DATETIME":
            return "datetime"
        elif dtype == "INTEGER":
            return "integer"
        elif dtype == "FLOAT":
            return "float"
        elif dtype == "BOOLEAN":
            return "boolean"
        else:
            log.warning('Unhandled datatype: %s for %s' % (dtype, sa_property))
            return dtype
    except AttributeError:
        return sa_property.direction.name.lower()


class FieldFactory(object):
    """The FieldFactory is responsible for initialising a fields for a
    given form."""

    def __init__(self, form, translate):
        """

        :form: Reference to the ::class::Form instance
        :translate: Translation function.

        """
        self.form = form
        self.translate = translate

    def _check_integrity(self, name, sa_dtype, dtype):
        """Check for integrity if possible and log error if integrity is
        violated. If sa_dtype is None and dtype is "string" the default
        type is set which is not considired an error."""

        # special handling for certian datatypes
        # 1. email. email is actually a string field
        if dtype == "email":
            dtype = "string"
        if dtype == "interval":
            dtype = "datetime"
        if sa_dtype != dtype and (sa_dtype is not None and dtype != "string"):
            log.error("Mismatch of datatype for field '{name}' of SA datatype "
                      "SA '{sa_dtype}' and formbar datatype '{dtype}'"
                      "".format(sa_dtype=sa_dtype,
                                dtype=dtype,
                                name=name))

    def create(self, fieldconfig):
        """Will return a Field instance based on the given field config.

        :fieldconfig: Reference to the ::class::Field config instance
        :returns: Field instance

        """
        # If the form has a mapped item, then try to determine the type
        # of the field by looking on the property. This type is used for
        # two cases:
        # 1. As fallback if the form does not define type.
        # 2. For integrity checks to show that there is a missmatch
        # between type configuration in a form and the SQLALCHEMY model.
        if self.form._item:
            sa_property = get_sa_property(self.form._item, fieldconfig.name)
            if sa_property:
                sa_dtype = get_type_from_sa_property(sa_property)
            else:
                sa_dtype = None
        else:
            sa_property = None
            sa_dtype = None

        # Set datatype of the field based on the config, the type in the
        # database or as fallback use string.
        if fieldconfig.type:
            dtype = fieldconfig.type
        elif sa_dtype:
            dtype = sa_dtype
        else:
            dtype = "string"

        self._check_integrity(fieldconfig.name, sa_dtype, dtype)

        builder_map = {
            "string": self._create_string,
            "integer": self._create_integer,
            "float": self._create_float,
            "date": self._create_date,
            "datetime": self._create_datetime,
            "interval": self._create_timedelta,
            "time": self._create_time,
            "file": self._create_file,
            "boolean": self._create_boolean,
            "email": self._create_email,
            "integerselection": self._create_intselection,
            "stringselection": self._create_stringselection,
            "booleanselection": self._create_booleanselection,
            "manytoone": self._create_manytoone,
            "onetoone": self._create_onetoone,
            "onetomany": self._create_onetomany,
            "manytomany": self._create_manytomany,
        }

        # Look on the renderer to get further informations on the type
        # of the field.
        if dtype not in ["manytoone", "onetomany", "onetoone", "manytomany"] and \
           fieldconfig.renderer:
            if fieldconfig.renderer.type in ["dropdown", "radio", "checkbox"]:
                if fieldconfig.renderer.type == "checkbox":
                    if dtype not in ("string", "integer"):
                        raise TypeError("Checkbox must be of type either string or integer!")
                dtype = "%sselection" % dtype

        builder = builder_map.get(dtype, self._create_default)
        log.debug("Creating field '{name}' '{dtype}'"
                  "".format(name=fieldconfig.name, dtype=dtype))
        return builder(fieldconfig, sa_property)

    def _create_string(self, fieldconfig, sa_property):
        return StringField(self.form, fieldconfig, self.translate, sa_property)

    def _create_integer(self, fieldconfig, sa_property):
        return IntegerField(self.form, fieldconfig, self.translate, sa_property)

    def _create_float(self, fieldconfig, sa_property):
        return FloatField(self.form, fieldconfig, self.translate, sa_property)

    def _create_date(self, fieldconfig, sa_property):
        return DateField(self.form, fieldconfig, self.translate, sa_property)

    def _create_datetime(self, fieldconfig, sa_property):
        return DateTimeField(self.form, fieldconfig, self.translate, sa_property)

    def _create_timedelta(self, fieldconfig, sa_property):
        return TimedeltaField(self.form, fieldconfig, self.translate, sa_property)

    def _create_time(self, fieldconfig, sa_property):
        return TimeField(self.form, fieldconfig, self.translate, sa_property)

    def _create_file(self, fieldconfig, sa_property):
        return FileField(self.form, fieldconfig, self.translate, sa_property)

    def _create_boolean(self, fieldconfig, sa_property):
        return BooleanField(self.form, fieldconfig, self.translate, sa_property)

    def _create_email(self, fieldconfig, sa_property):
        return EmailField(self.form, fieldconfig, self.translate, sa_property)

    def _create_intselection(self, fieldconfig, sa_property):
        return IntSelectionField(self.form, fieldconfig, self.translate, sa_property)

    def _create_stringselection(self, fieldconfig, sa_property):
        return StringSelectionField(self.form, fieldconfig, self.translate, sa_property)

    def _create_booleanselection(self, fieldconfig, sa_property):
        return BooleanSelectionField(self.form, fieldconfig, self.translate, sa_property)

    def _create_onetomany(self, fieldconfig, sa_property):
        return OnetomanyRelationField(self.form, fieldconfig, self.translate, sa_property)

    def _create_onetoone(self, fieldconfig, sa_property):
        return OnetooneRelationField(self.form, fieldconfig, self.translate, sa_property)

    def _create_manytoone(self, fieldconfig, sa_property):
        return ManytooneRelationField(self.form, fieldconfig, self.translate, sa_property)

    def _create_manytomany(self, fieldconfig, sa_property):
        return ManytomanyRelationField(self.form, fieldconfig, self.translate, sa_property)

    def _create_default(self, fieldconfig, sa_property):
        log.warning("Not sure which field to create... "
                    "Using default field for '{name}'"
                    "".format(name=fieldconfig.name))
        return Field(self.form, fieldconfig, self.translate, sa_property)


class Field(object):
    """Wrapper for fields in the form. The purpose of this class is to
    provide a common interface for the renderer independent to the
    underlying implementation detail of the field."""

    def __init__(self, form, config, translate, sa_property=None):
        """Initialize the field with the given field configuration.

        :config: Field configuration

        """
        from formbar.renderer import get_renderer
        self.value = None
        self._config = config
        self._form = form
        self._translate = translate
        self.renderer = get_renderer(self, translate)
        self._sa_property = sa_property

        self.errors = []
        self.warnings = []
        self.required = getattr(self._config, "required")
        self.desired = getattr(self._config, "desired")
        self.readonly = getattr(self._config, "readonly")

        if self.name in self._form.merged_data:
            self.value = self._form.merged_data[self.name]

        # Only set default value if the current value of the form is not
        # "empty"
        if (self.value is None or
           (isinstance(self.value, basestring) and self.value == "")):
            self._set_default_value()

        self.previous_value = None
        """Value as string of the field. Will be set on rendering the
        form"""

    # def __repr__(self):
    #     rules = "rules: \n\t\t{}".format("\n\t".join(rules_to_string(field))
    #     field = u"field:\t\t{}".format(self.name)
    #     value = u"value:\t\t{}, {}".format(repr(self.get_value()), type(self.get_value()))
    #     required = "required:\t{}".format(self.required)
    #     desired = "desired:\t{}".format(self.desired)
    #     #validated = "validated:\t{}".format(self.is_validated)
    #     #_type = "type:\t\t{}".format(self.get_type())
    #     return "\n".join([field, required, desired, value, _type, rules])+"\n"

    def _handle_expression(self, value):
        # If value begins with '%' then consider the following string as
        # a brabbel expression and set the value of the default value to
        # the result of the evaluation of the expression.
        if value and value.startswith("%"):
            form_values = self._form._get_data_from_item()
            value = Expression(value.strip("%")).evaluate(values=form_values)
        # If value begins with '$' then consider the string as attribute
        # name of the item in the form and get the value
        elif value and value.startswith("$"):
            try:
                value = getattr(self._form._item, value.strip("$"))
            except (IndexError, AttributeError) as e:
                # In case we are currently creating an item a access to
                # values of the item may fail because the are not
                # existing yet. This is especially true for items in
                # relations as relations are added to the item after the
                # creation has finished. So we expect such errors in
                # case of creation and will not log those errors. A way
                # to identify an item which is not fully created is the
                # absence of its id value.
                if self._form._item and self._form._item.id:
                    log.error("Error while accessing attribute '%s': %s"
                              % (value, e))
                value = None
        return value

    def _set_default_value(self):
        value = getattr(self._config, "value")
        if value:
            value = self._handle_expression(value)
            if value and isinstance(value, basestring):
                value = self._to_python(value)
        else:
            value = None
        self.value = value

    @property
    def rules_to_string(self):
        log.warning("Call of 'rules_to_string' property is deprecated. Use rules_to_string helper method.")
        return rules_to_string(self)

    def is_readonly(self):
        log.warning("Call of 'is_readonly' method is deprecated. Use readonly attribute.")
        return self.readonly

    @property
    def empty_message(self):
        if self.required:
            return config.required_msg
        return config.desired_msg

    def __getattr__(self, name):
        """Make attributes from the configuration directly available"""
        return getattr(self._config, name)

    def _from_python(self, value):
        """Internal converter method to convert the internal value of
        the field into a serialised version of the value which is used
        in the form for rendering etc."""
        if value is None:
            value = ""
        return unicode(value)

    def _to_python(self, value):
        """Internal converter method to convert the external serielized
        value of the field into a pythonic version of the value which is
        used internally."""
        return value

    def get_rules(self):
        """Returns a list of configured rules for the field."""
        return self._config.get_rules()

    def set_value(self, value):
        self.value = value

    def set_previous_value(self, value):
        self.previous_value = value

    def get_value(self, default="", expand=False):
        """Will return the serialized value of the field.

        If you want to get the deserialized (pythonic) value please access
        self.value directly

        If no value is set you can define a default value which will be
        returned instead. The method take an expand parameter. If set to
        true the function will try to return the literal value of the
        field. This option has currently only an effect on
        CollectionFields."""

        # In case the type conversion (deserialisation) worked, the value of
        # the field should have a value. In case the conversion fails
        # this field has errors. In this case we will return the
        # submitted value.
        if self.value is None and self.errors:
            # Get with .get instead of getting directly per keyname
            # because of checkboxes which are not submitted at all if
            # they are not checked.
            return self._form.submitted_data.get(self.name, "")
        elif self.value is None:
            return default
        else:
            try:
                return self._from_python(self.value)
            except:
                # TODO: Ensure that self.value only contains pythonic
                # values. At least when providing values on
                # formin itialisation e.g {"datefield": '2015-01-01'}
                # Will result in other values than expected -> string
                # instead of date.
                log.debug("'{}' ({}) in {} ({}) could not be converted".format(self.value, type(self.value), self.name, self))
                return self.value

    def get_previous_value(self, default="", expand=False):
        value = self._from_python(self.previous_value)
        if not value and default:
            return default
        return value

    def add_error(self, error):
        self.errors.append(error)

    def get_errors(self):
        return self.errors

    def add_warning(self, warning):
        self.warnings.append(warning)

    def get_warnings(self):
        return self.warnings

    def render(self, active):
        """Returns the rendererd HTML for the field"""
        self.renderer._active = active
        return self.renderer.render()

# Singlevalue Fields.
#####################################


class StringField(Field):

    def _from_python(self, value):
        if value is None:
            value = ""
        return unicode(value)

    def _to_python(self, value):
        from formbar.converters import to_string
        return to_string(value)


class IntegerField(Field):

    def _to_python(self, value):
        from formbar.converters import to_integer
        return to_integer(value)


class FloatField(Field):

    def _to_python(self, value):
        from formbar.converters import to_float
        return to_float(value)


class BooleanField(Field):

    def _to_python(self, value):
        from formbar.converters import to_boolean
        return to_boolean(value)


class DateField(Field):

    def _from_python(self, value):
        from formbar.converters import format_date
        locale = self._form._locale
        if locale == "de":
            dateformat = "dd.MM.yyyy"
        else:
            dateformat = "yyyy-MM-dd"
        if value:
            return format_date(value, format=dateformat)
        return None

    def _to_python(self, value):
        from formbar.converters import to_date
        return to_date(value, self._form._locale)


class DateTimeField(Field):

    def _from_python(self, value):
        from formbar.converters import format_datetime, get_local_datetime
        if not value:
            return ""
        locale = self._form._locale
        value = get_local_datetime(value)
        if locale == "de":
            dateformat = "dd.MM.yyyy HH:mm:ss"
        else:
            dateformat = "yyyy-MM-dd HH:mm:ss"
        return format_datetime(value, format=dateformat)

    def _to_python(self, value):
        from formbar.converters import to_datetime
        locale = self._form._locale
        return to_datetime(value, locale)


class TimedeltaField(Field):

    def _from_python(self, value):
        from formbar.converters import from_timedelta
        return from_timedelta(value)

    def _to_python(self, value):
        from formbar.converters import to_timedelta
        return to_timedelta(value)


class FileField(Field):

    def _to_python(self, value):
        from formbar.converters import to_file
        return to_file(value)


class TimeField(Field):

    def _from_python(self, value):
        from formbar.converters import from_timedelta
        td = datetime.timedelta(seconds=int(value))
        return from_timedelta(td)

    def _to_python(self, value):
        from formbar.converters import to_timedelta
        return to_timedelta(value).total_seconds()


class EmailField(Field):

    def _to_python(self, value):
        from formbar.converters import to_email
        return to_email(value)

# Selection and Multiselection Fields.
#####################################


class CollectionField(Field):
    """Field which can have one or more of predefined values.  If the
    values are defined in the fields config please check
    ::class::SelectionField.  If the values are defined by the relations
    in the database please check ::class::RelationField."""

    def expand_value(self, value):
        ex_values = []
        if not isinstance(value, list):
            value = [value]
        options = self.get_options()
        for opt in options:
            for v in value:
                if unicode(v) == unicode(opt[1]):
                    ex_values.append("%s" % opt[0])
        return ", ".join(ex_values)

    def get_previous_value(self, default="", expand=False):
        value = super(CollectionField, self).get_previous_value(default)
        if expand:
            return self.expand_value(value)
        return value

    def get_value(self, default="", expand=False):
        value = super(CollectionField, self).get_value(default)
        if expand:
            return self.expand_value(value)
        return value

    def sort_options(self, options):
        """Will return a alphabetical sorted list of options. The filtering is
        defined by the following configuration options of the renderer:
        sort, sortorder. If sort is not set to 'true' than no sorting is
        done at all. This is the default behaviour."""
        if self._config.renderer and self._config.renderer.sort:
            reverse = self._config.renderer.sortorder == "desc"
            options = sorted(options,
                             key=lambda x: unicode(x[0]),
                             reverse=reverse)
        return options

    def get_options(self):
        """Will return a list of tuples containing the options of the
        field. The tuple contains in the following order:

        1. the display value of the option,
        2. its value and
        3. a boolean flag if the options is a filtered one and
        should not be visible in the selection.

        Options can be filtered by defining the filter attribute of the
        renderer. The expression will be applied on every option in the
        selection. Keyword beginning with % are handled as variable. On
        rule evaluation the keyword in the expression will be replaced
        with the value of the item with the name of the variable.
        """
        raise NotImplementedError()

    def _build_filter_rule(self, expr_str, item):
        return Rule(self.parse_expression(expr_str))

    def parse_expression(self, expr_str):
        tokens = re.split("\s", expr_str)
        values = self.determine_values()
        for token in tokens:
            expr_str = self.substitute(token, expr_str, values)
        expr_str = expr_str.replace("*", "$")
        return expr_str

    def substitute(self, token, unmodified_expression, values):
        """
        Will return a substuteded token in case of defined keywords
        (%,@,$ vars) with the replaced values found in the provided
        values dictionary or coming from the item.

        :param token:
        :param unmodified_expression:
        :param values:
        :return:
        """
        # % marks the options in the selection field. It is used to
        # iterate over the options in the selection. I case the
        # options are SQLAlchemy based options the variable can be
        # used to access a attribute of the item. E.g. %id will
        # access the id of the current option item. For user defined
        # options "%" can be used to iterate over the user defined
        # options. In this case %attr will access a given attribte
        # in the option. A bare "%" will give the value of the
        # option.
        is_optionfield = token.startswith("%")
        # @ marks the current form item
        is_value_of_formitem = token.startswith("@")
        # The filter expression may reference values of the form using $
        # variables. To have access to these values we extract the
        # values from the given item if available.
        is_value_of_current_form = token.startswith("$")

        if not (is_optionfield or is_value_of_current_form or is_value_of_formitem):
            return unmodified_expression
        elif is_optionfield:
            value = self.parse_optionfield(token)
        elif is_value_of_formitem:
            value = self.parse_formitem(token)
        elif is_value_of_current_form:
            value = self.parse_formvalue(values, token)

        return self.substitute_value(unmodified_expression, token, value)

    def substitute_value(self, expression, token, value):
        if isinstance(value, list):
            value = "[%s]" % ",".join("'%s'"
                                      % unicode(v) for v in value)
            return expression.replace(token, value)
        elif isinstance(value, basestring) and (value.startswith("$") or
                                                value.startswith("*")):
            return expression.replace(token, "%s" % unicode(value))

        return expression.replace(token, "'%s'" % unicode(value))

    def parse_formvalue(self, substitution_values, token):
        tmpitem = None
        value = None
        tokens = token.split(".")
        if len(tokens) > 1:
            key = tokens[0].strip("$")
            attribute = ".".join(tokens[1:])
            # FIXME: This is a bad assumption that there is a
            # user within a request. (ti) <2014-07-09 11:18>
            if key == "user":
                tmpitem = self._form._request.user
        else:
            key = tokens[0].strip("$")
            value = substitution_values.get(key) or ''
        if tmpitem and not value:
            value = getattr(tmpitem, attribute)
            if hasattr(value, '__call__'):
                value = value()
        return value

    def parse_formitem(self, token):
        # TODO: Access to the item is usally no good idea as formbar can
        # be used in environments where no item is available.
        return getattr(self._form._item, token.strip("@"))

    def parse_optionfield(self, token):
        return "*%s" % (token.strip("%") or "value")

    def determine_values(self):
        if not self._form._item:
            return {}
        values = self._form._item.get_values()
        values.update(self._form.merged_data)
        return values

    def filter_options(self, options):
        """Will return a of tuples with options. The given options can
        be either a list of SQLAlchemy mapped items (In case the options
        come directly from the database) or a list of tuples with option
        name and values. (In case of userdefined options in the form)

        :options: List of items or tuples
        :returns: List of tuples.

        """
        is_filtering_configured = self._config.renderer and self._config.renderer.filter
        if is_filtering_configured:
            rule = self._build_filter_rule(self._config.renderer.filter, None)
            x = re.compile("\$[\w\.]+")
            values = x.findall(rule._expression)
            return [self.do_filter_options(option, values, rule) for option in options]
        else:
            return [self.dont_filter_options(option) for option in options]

    def dont_filter_options(self, option):
        label, value = self.explode_option(option)
        return (label, value, True)

    def do_filter_options(self, option, option_values, rule):
        label, value = self.explode_option(option)
        values = {}
        for key in option_values:
            key = key.strip("$")
            if isinstance(option, tuple):
                values[key] = unicode(option[2].get(key, ""))
            else:
                values[key] = unicode(getattr(option, key))
        result = rule.evaluate(values)
        if result:
            return (label, value, True)
        else:
            return (label, value, False)

    def explode_option(self, option):
        if isinstance(option, tuple):
            # User defined options
            o_value = option[1]
            o_label = option[0]
        else:
            # Options loaded from the database
            o_value = option.id
            o_label = option
        return o_label, o_value


class SelectionField(CollectionField):
    """Field which can have one or more of predefined values. The
    values are defined in the fields config."""

    def get_options(self):
        options = []
        user_defined_options = self._config.options
        if isinstance(user_defined_options, list) and \
           len(user_defined_options) > 0:
            for option in self.filter_options(user_defined_options):
                options.append((option[0], option[1], option[2]))
        elif isinstance(user_defined_options, str):
            for option in self._form.merged_data.get(user_defined_options):
                options.append((option[0], option[1], True))
        return self.sort_options(options)

    def _from_python(self, value):
        value = super(CollectionField, self)._from_python(value)
        # Special handling for multiple values (multiselect in
        # checkboxes eg.) which has be converted into a string by
        # SQLAalchemy automatically. eg the python value "['1',
        # '2']" will be converted into the _string_ "{1,2,''}". In
        # this case we need to convert the value back into a list.
        if value.startswith("{") and value.endswith("}"):
            serialized = []
            for v in value.strip("{").strip("}").split(","):
                if isinstance(self, IntSelectionField):
                    value = int(v)
                elif isinstance(self, BooleanSelectionField):
                    value = bool(v)
                else:
                    value = unicode(v)
                serialized.append(value)
            value = serialized
        return value

    def _to_python(self, value):
        # It seems that the # value is converted into a string by
        # SQLAalchemy automatically. eg the python value "['1', '2']"
        # will be converted into the _string_ "{1,2,''}".
        return value


class IntSelectionField(SelectionField):
    """Field which can have one or more of predefined values. The
    values are defined in the fields config."""
    def _to_python(self, value):
        from formbar.converters import to_integer
        if isinstance(value, list):
            return [to_integer(e) for e in value]
        return to_integer(value)


class StringSelectionField(SelectionField):
    """Field which can have one or more of predefined values. The
    values are defined in the fields config."""
    pass


class BooleanSelectionField(SelectionField):
    """Field which can have one or more of predefined values. The
    values are defined in the fields config."""
    pass


# SQLALCHEMY related Fields.
############################


class RelationField(CollectionField):
    """Field which can have one or more of predefined values. The values
    are defined through the relation in the database.  Please note that
    these require a SQLALCHEMY mapped item in the form!"""

    def __init__(self, form, config, translate, sa_property):
        if not form._dbsession:
            # For now we only log in debug mode. In the future we should be
            # more strict and raise exception.
            log.debug("No DB session available in the parent form. "
                      "RelationField must be instanciated with an "
                      "available DB session.")
            # raise TypeError("No DB session available in the parent form. "
            #                 "RelationField must be instanciated with an "
            #                 "available DB session.")
        super(RelationField, self).__init__(form, config, translate, sa_property)

    def _from_python(self, value):
        if isinstance(value, list):
            vl = []
            for v in value:
                try:
                    vl.append(v.id)
                except AttributeError:
                    vl.append(v)
            return vl
        try:
            return value.id
        except AttributeError:
            return value

    def _get_sa_mapped_class(self):
        sa_property = get_sa_property(self._form._item, self._config.name)
        return sa_property.mapper.class_

    def get_options(self):
        options = []
        try:
            clazz = self._get_sa_mapped_class()
            unfiltered = self._form._dbsession.query(clazz)
            options.extend(self.filter_options(unfiltered))
        except:
            log.error("Failed to load options for '%s' "
                      "to load the option from db" % self.name)
        return options


class ManytooneRelationField(RelationField):

    def get_options(self):
        """Manytoone Relations need an extra option to set to
        selection explicit."""
        options = []
        _ = self._form._translate
        options.append((_("no selection"), "", True))
        options.extend(super(ManytooneRelationField, self).get_options())
        return options

    def _to_python(self, value):
        from formbar.converters import to_manytoone, to_integer
        rel = self._sa_property.mapper.class_
        if value in ("", None):
            return None
        value = to_integer(value)
        db = self._form._dbsession
        selected = getattr(self._form._item, self.name)
        return to_manytoone(rel, value, db, selected)


class OnetooneRelationField(RelationField):
    # SEEMS TO BE UNUSED
    pass


class OnetomanyRelationField(RelationField):

    def _to_python(self, value):
        from formbar.converters import to_onetomany, to_integer_list
        rel = self._sa_property.mapper.class_
        value = to_integer_list(value)
        if not value:
            return value
        db = self._form._dbsession
        selected = getattr(self._form._item, self.name)
        return to_onetomany(rel, value, db, selected)


class ManytomanyRelationField(RelationField):

    def _to_python(self, value):
        from formbar.converters import to_manytomany, to_integer_list
        rel = self._sa_property.mapper.class_
        value = to_integer_list(value)
        if not value:
            return value
        db = self._form._dbsession
        selected = getattr(self._form._item, self.name)
        return to_manytomany(rel, value, db, selected)

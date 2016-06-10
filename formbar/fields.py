#!/usr/bin/env python
# encoding: utf-8
import logging
import re
import sqlalchemy as sa
from formbar.rules import Rule, Expression

log = logging.getLogger(__name__)


def get_sa_property(item, name):
    mapper = sa.orm.object_mapper(item)
    for prop in mapper.iterate_properties:
        if prop.key == name:
            return prop


def get_type_from_sa_property(sa_property):
    try:
        column = sa_property.columns[0]
        dtype = str(column.type)
        if dtype == "TEXT" or dtype.find("VARCHAR") > -1:
            return "string"
        elif dtype == "DATE":
            return "date"
        elif dtype == "INTEGER":
            return "integer"
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
            sa_dtype = None

        # Set datatype of the field based on the config, the type in the
        # database or as fallback use string.
        if fieldconfig.type:
            dtype = fieldconfig.type
        elif sa_dtype:
            dtype = sa_dtype
        else:
            dtype = "string"

        # Check for integrity if possible and log error if integrity is
        # violated. If sa_dtype is None and dtype is "string" the
        # default type is set which is not considired an error.
        if sa_dtype != dtype and (sa_dtype is not None and dtype != "string"):
            log.error("Mismatch of datatype for field '{name}' of SA datatype "
                      "SA '{sa_dtype}' and formbar datatype '{dtype}'"
                      "".format(sa_dtype=sa_dtype,
                                dtype=dtype,
                                name=fieldconfig.name))
        log.debug("Creating field '{name}' with datatype '{dtype}'"
                  "".format(name=fieldconfig.name, dtype=dtype))

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
            "multiselection": self._create_multiselection,
            "manytoone": self._create_manytoone,
            "onetoone": self._create_onetoone,
            "onetomany": self._create_onetomany,
            "manytomany": self._create_manytomany,
        }

        # Look on the renderer to get further informations on the type
        # of the field.
        if (dtype not in ["manytoone", "onetomany", "onetoone"]
           and fieldconfig.renderer):
            if fieldconfig.renderer.type in ["dropdown", "radio"]:
                dtype = "%sselection" % dtype
            elif fieldconfig.renderer.type == "checkbox":
                if dtype != "string":
                    raise TypeError("Checkbox must be of type string!")
                dtype = "multiselection"

        builder = builder_map.get(dtype, self._create_default)
        return builder(fieldconfig)

    def _create_string(self, fieldconfig):
        return StringField(self.form, fieldconfig, self.translate)

    def _create_integer(self, fieldconfig):
        return IntegerField(self.form, fieldconfig, self.translate)

    def _create_float(self, fieldconfig):
        return FloatField(self.form, fieldconfig, self.translate)

    def _create_date(self, fieldconfig):
        return DateField(self.form, fieldconfig, self.translate)

    def _create_datetime(self, fieldconfig):
        return DateTimeField(self.form, fieldconfig, self.translate)

    def _create_timedelta(self, fieldconfig):
        return TimedeltaField(self.form, fieldconfig, self.translate)

    def _create_time(self, fieldconfig):
        return TimeField(self.form, fieldconfig, self.translate)

    def _create_file(self, fieldconfig):
        return FileField(self.form, fieldconfig, self.translate)

    def _create_boolean(self, fieldconfig):
        return BooleanField(self.form, fieldconfig, self.translate)

    def _create_email(self, fieldconfig):
        return EmailField(self.form, fieldconfig, self.translate)

    def _create_intselection(self, fieldconfig):
        return IntSelectionField(self.form, fieldconfig, self.translate)

    def _create_stringselection(self, fieldconfig):
        return StringSelectionField(self.form, fieldconfig, self.translate)

    def _create_multiselection(self, fieldconfig):
        return MultiselectionField(self.form, fieldconfig, self.translate)

    def _create_onetomany(self, fieldconfig):
        return OnetomanyRelationField(self.form, fieldconfig, self.translate)

    def _create_onetoone(self, fieldconfig):
        return OnetooneRelationField(self.form, fieldconfig, self.translate)

    def _create_manytoone(self, fieldconfig):
        return ManytooneRelationField(self.form, fieldconfig, self.translate)

    def _create_manytomany(self, fieldconfig):
        return ManytomanyRelationField(self.form, fieldconfig, self.translate)

    def _create_default(self, fieldconfig):
        log.warning("Not sure which field to create... "
                    "Using default field for '{name}'"
                    "".format(name=fieldconfig.name))
        return Field(self.form, fieldconfig, self.translate)


class Field(object):
    """Wrapper for fields in the form. The purpose of this class is to
    provide a common interface for the renderer independent to the
    underlying implementation detail of the field."""

    def __init__(self, form, config, translate):
        """Initialize the field with the given field configuration.

        :config: Field configuration

        """
        from formbar.renderer import get_renderer
        self._form = form
        self._config = config
        self._translate = translate
        self.renderer = get_renderer(self, translate)
        self._errors = []
        self._warnings = []

        # Set default value
        value = getattr(self._config, "value")

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
                # Special logic for ringo items.
                if (self.renderer.render_type == "info"
                   and hasattr(self._form._item, "get_value")):
                    value = self._form._item.get_value(value.strip("$"),
                                                       expand=True)
                else:
                    value = getattr(self._form._item, value.strip("$"))
            except (IndexError, AttributeError), e:
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
        self.value = value

        self.previous_value = None
        """Value as string of the field. Will be set on rendering the
        form"""

    def __getattr__(self, name):
        """Make attributes from the configuration directly available"""
        return getattr(self._config, name)

    def get_rules(self):
        """Returns a list of configured rules for the field."""
        return self._config.get_rules()

    def set_value(self, value):
        self.value = value

    def set_previous_value(self, value):
        self.previous_value = value

    def get_value(self, default=None, expand=False):
        return self._get_value(self.value, default, expand)

    def get_previous_value(self, default=None, expand=False):
        return self._get_value(self.previous_value, default, expand)

    def _get_value(self, value, default, expand):
        if expand:
            if not isinstance(value, list):
                value = [value]
            ex_values = []
            options = self.get_options()
            for opt in options:
                for v in value:
                    if unicode(v) == unicode(opt[1]):
                        ex_values.append("%s" % opt[0])
            return ", ".join(ex_values)
        else:
            if value:
                from formbar.converters import from_python
                return from_python(self, value)
            elif default:
                return default
            else:
                return value

    def add_error(self, error):
        self._errors.append(error)

    def add_warning(self, warning):
        self._warnings.append(warning)

    def get_errors(self):
        return self._errors

    def get_warnings(self):
        return self._warnings

    def render(self):
        """Returns the rendererd HTML for the field"""
        return self.renderer.render()

    def is_relation(self):
        return False

    def is_desired(self):
        """Returns true if field is set as desired in field configuration"""
        return self.desired

    def is_required(self):
        """Returns true if the required flag of the field configuration
        is set"""
        return self.required

    def is_readonly(self):
        """Returns true if either the readonly flag of the field
        configuration is set or the whole form is marked as readonly"""
        return self.readonly or False

# Singlevalue Fields.
#####################################


class StringField(Field):
    pass


class IntegerField(Field):
    pass


class FloatField(Field):
    pass


class BooleanField(Field):
    pass


class DateField(Field):
    pass


class DateTimeField(Field):
    pass


class TimedeltaField(Field):
    pass


class FileField(Field):
    pass


class TimeField(Field):
    pass


class EmailField(Field):
    pass

# Selection and Multiselection Fields.
#####################################


class CollectionField(Field):
    """Field which can have one or more of predefined values.  If the
    values are defined in the fields config please check
    ::class::SelectionField.  If the values are defined by the relations
    in the database please check ::class::RelationField."""

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
        t = expr_str.split(" ")
        # The filter expression may reference values of the form using $
        # variables. To have access to these values we extract the
        # values from the given item if available.
        # TODO: Access to the item is usally no good idea as formbar can
        # be used in environments where no item is available.
        if self._form._item:
            item_values = self._form._item.get_values()
        else:
            item_values = {}
        for x in t:
            # % marks the options in the selection field. It is used to
            # iterate over the options in the selection. I case the
            # options are SQLAlchemy based options the variable can be
            # used to access a attribute of the item. E.g. %id will
            # access the id of the current option item. For user defined
            # options "%" can be used to iterate over the user defined
            # options. In this case %attr will access a given attribte
            # in the option. A bare "%" will give the value of the
            # option.
            if x.startswith("%"):
                key = x.strip("%")
                value = "$%s" % (key or "value")
            # @ marks the item of the current fields form item.
            elif x.startswith("@"):
                key = x.strip("@")
                value = getattr(self._form._item, key)
            # $ special attributes of the current form.
            elif x.startswith("$"):
                tmpitem = None
                value = None
                tokens = x.split(".")
                if len(tokens) > 1:
                    key = tokens[0].strip("$")
                    attribute = ".".join(tokens[1:])
                    # FIXME: This is a bad assumption that there is a
                    # user within a request. (ti) <2014-07-09 11:18>
                    if key == "user":
                        tmpitem = self._form._request.user
                else:
                    key = tokens[0].strip("$")
                    value = item_values.get(key) or ''
                if tmpitem and not value:
                    value = getattr(tmpitem, attribute)
                    if hasattr(value, '__call__'):
                        value = value()
            else:
                value = None

            if value is not None:
                if isinstance(value, list):
                    value = "[%s]" % ",".join("'%s'"
                                              % unicode(v) for v in value)
                    expr_str = expr_str.replace(x, value)
                elif isinstance(value, basestring) and value.startswith("$"):
                    expr_str = expr_str.replace(x, "%s" % unicode(value))
                else:
                    expr_str = expr_str.replace(x, "'%s'" % unicode(value))
        return Rule(str(expr_str))

    def filter_options(self, options):
        """Will return a of tuples with options. The given options can
        be either a list of SQLAlchemy mapped items (In case the options
        come directly from the database) or a list of tuples with option
        name and values. (In case of userdefined options in the form)

        :options: List of items or tuples
        :returns: List of tuples.

        """
        filtered_options = []
        if self._config.renderer and self._config.renderer.filter:
            rule = self._build_filter_rule(self._config.renderer.filter, None)
            x = re.compile("\$[\w\.]+")
            option_values = x.findall(rule._expression)
        else:
            rule = None
        for option in options:
            if isinstance(option, tuple):
                # User defined options
                o_value = option[1]
                o_label = option[0]
            else:
                # Options loaded from the database
                o_value = option.id
                o_label = option
            if rule:
                values = {}
                for key in option_values:
                    key = key.strip("$")
                    if isinstance(option, tuple):
                        value = option[2].get(key, "")
                    else:
                        value = getattr(option, key)
                    values[str(key)] = unicode(value)
                result = rule.evaluate(values)
                if result:
                    filtered_options.append((o_label, o_value, True))
                else:
                    filtered_options.append((o_label, o_value, False))
            else:
                filtered_options.append((o_label, o_value, True))
        return filtered_options


class SelectionField(CollectionField):
    """Field which can have one or more of predefined values. The
    values are defined in the fields config."""

    def get_options(self):
        options = []
        user_defined_options = self._config.options
        if (isinstance(user_defined_options, list)
           and len(user_defined_options) > 0):
            for option in self.filter_options(user_defined_options):
                options.append((option[0], option[1], option[2]))
        elif isinstance(user_defined_options, str):
            for option in self._form.merged_data.get(user_defined_options):
                options.append((option[0], option[1], True))
        return options


class IntSelectionField(SelectionField):
    """Field which can have one or more of predefined values. The
    values are defined in the fields config."""
    pass


class StringSelectionField(SelectionField):
    """Field which can have one or more of predefined values. The
    values are defined in the fields config."""
    pass


class MultiselectionField(StringSelectionField):
    """Field which can have one or more of predefined values. The
    values are defined in the fields config."""
    pass


# SQLALCHEMY related Fields.
############################


class RelationField(CollectionField):
    """Field which can have one or more of predefined values. The values
    are defined through the relation in the database.  Please note that
    these require a SQLALCHEMY mapped item in the form!"""

    def __init__(self, form, config, translate):
        if not form._dbsession:
            raise TypeError("No DB session available in the parent form. "
                            "RelationField must be instanciated with an "
                            "available DB session.")
        super(RelationField, self).__init__(form, config, translate)

    def is_relation(self):
        return True

    def get_options(self):
        options = []
        try:
            sa_property = get_sa_property(self._form._item, self._config.name)
            clazz = sa_property.mapper.class_
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


class OnetooneRelationField(RelationField):
    # SEEMS TO BE UNUSED
    pass


class OnetomanyRelationField(RelationField):
    pass


class ManytomanyRelationField(RelationField):
    pass

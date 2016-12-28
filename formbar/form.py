import importlib
import inspect
import logging

import config
import re
import sqlalchemy as sa
from formbar.converters import (
    DeserializeException, from_python, to_python
)
from formbar.renderer import FormRenderer, get_renderer
from formbar.rules import Rule, Expression

log = logging.getLogger(__name__)


def get_sa_property(item, fieldname):
    if not item:
        return None

    # Recursive handling of "dot.separated.field.names"
    elif fieldname.find(".") > -1:
        nameparts = fieldname.split(".")
        return get_sa_property(getattr(item, ".".join(nameparts[0:-1])),
                               nameparts[-1])
    else:
        mapper = sa.orm.object_mapper(item)
        for prop in mapper.iterate_properties:
            if prop.key == fieldname:
                return prop


def remove_ws(data):
    """Helper function which removes trailing and leading whitespaces
    for all values in the given dictionary. The dictionary usually
    contains the submitted data."""
    clean = {}
    for key in data:
        if isinstance(data[key], unicode):
            # This may happen for lists e.g when sumitting multiple
            # selection in checkboxes.
            clean[key] = data[key].strip()
        else:
            clean[key] = data[key]
    return clean


def get_attributes(cls):
    return [prop.key for prop in sa.orm.class_mapper(cls).iterate_properties
            if isinstance(prop, sa.orm.ColumnProperty)
            or isinstance(prop, sa.orm.RelationshipProperty)]


def get_relations(cls):
    return [prop.key for prop in sa.orm.class_mapper(cls).iterate_properties
            if isinstance(prop, sa.orm.RelationshipProperty)]


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class StateError(Error):
    """Exception raised for state errors while processing the form.

        :msg:  explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg


class ValidationException(Exception):
    pass


class Validator(object):
    """Validator class for external validators. External validators can
    be used to implement more complicated validations on the converted
    data in the form. The validator has access to all submitted values
    of the form. Validation happens on the converted pythonic values
    from the submitted formdata. Additionally a context can be provided
    to the validator to provide additional data needed for the
    validation."""

    def __init__(self, field, error, callback, context=None, triggers="error"):
        """Initialize a new Validator

        :field: Name of the field which should be validated.
        :error: Error message which should be show at the field when
                validation fails.
        :callback: Python callable which actually will do the check.
        :context: Add additional data which can be provided to the callback.
        :triggers: Set what kind of error message will be generated.
                   Everything else than "error" will trigger a warning
                   message. Default to error.

        """
        self._field = field
        self._error = error
        self._callback = callback
        self._context = context
        self._triggers = triggers

    def check(self, data):
        """Checker method which will call the callback of the validator
        to actually do the validation on the provided data. Will return
        True or False."""
        try:
            if len(inspect.getargspec(self._callback).args) == 2:
                return self._callback(self._field, data)
            else:
                return self._callback(self._field, data, self._context)
        except ValidationException, e:
            self._error = e.message
            return False


class Form(object):
    """Class for forms. The form will take care for rendering the form,
    validating the submitted data and saving the data back to the
    item.

    The form must be instanciated with an instance of an ``Form``
    configuration and optional an SQLAlchemy mapped item.

    If an SQLAlchemy mapped item is provided there are some basic
    validation is done based on the defintion in the database. Further
    the save method will save the values directly into the database.

    If no item was provided than a dummy item will be created with the
    attributes of the configured fields in the form.
    """

    def __init__(self, config, item=None, dbsession=None, translate=None,
                 change_page_callback={}, renderers={}, request=None,
                 csrf_token=None, eval_url=None, url_prefix="", locale=None,
                 values=None):
        """Initialize the form with ``Form`` configuration instance and
        optional an SQLAlchemy mapped object.

        :config: FormConfiguration.
        :item: SQLAlchemy mapped instance
        :dbsession: dbsession
        :translate: Translation function which returns a translated
        string for a given msgid
        :set_page_callback: Url which will be called when the user
        changes the currently selected page.
        :renderers: A optional dictionary of custom renderers which are
        provided to the form to render specific form elements. The key
        is the type of the renderer as named in the formular
        configuration.
        :request: Current request (See
        http://docs.pylonsproject.org/projects/pyramid/en/latest/api/request.html
        when using in connection with ringo)
        :csrf_token: Token to which will be included as hidden field in
        the form to prevent CSRF attacks.
        :eval_url: External URL for rule evaluation. If defined this URL is
        called to evaluate client side rules with a AJAX request. The rule
        to evaluate is provided in a GET request in the "rule" paramenter.
        The return Value is a JSON response with success attribute set
        depending on the result of the evaluation and the error message in
        the data attribute in case the evaluation fails.
        :url_prefix: Prefix which can be used for all URL in the form.
        :locale: String of the locale of the form. Used for proper
        display of the date and number functions.
        :values: Dictionary with values to be prefilled/overwritten in
                 the rendered form.
        """
        self._config = config
        self._item = item
        self._dbsession = dbsession
        self._request = request
        self._csrf_token = csrf_token
        self._url_prefix = url_prefix
        self._eval_url = eval_url
        if self._url_prefix:
            self._eval_url = self._url_prefix + self._eval_url

        if locale:
            self._locale = locale
        else:
            self._locale = "en"

        if translate:
            self._translate = translate
        else:
            self._translate = lambda msgid: msgid

        self.validated = False
        """Flag to indicate if the form has been validated. Init value
        is False.  which means no validation has been done."""
        self.external_validators = []
        """List with external validators. Will be called an form validation."""
        self.current_page = 0
        """Number of the currently selected page"""
        if self.pages:
            self.last_page = [int(p.attrib.get("id").strip("p")) for p in self.pages][-1]
        """Number of the last configured page"""
        self.change_page_callback = change_page_callback
        """Dictionary with some parameters used to call an URL when the
        user changes the currently selected page. The dictionary has the
        following keys:
         * url: Name of the URL which will be called
         * item (optional): A string which is send to the URL as GET
           paramenter. Often this is the name of the element (clazzname)
         * itemid (optional): The id of the currently editied element.
        The url will have the additional parameter "page" which holds
        the currently selected page.
        """
        self.external_renderers = renderers
        """Dictionary with external provided custom renderers."""
        self.fields = self._build_fields()
        """Dictionary with fields."""
        self.data = {}
        """After submission this Dictionary will contain the
        validated data on successfull validation. Else this Dictionary
        will be empty"""
        self.submitted_data = {}
        """The submitted data from the user. If validation fails, then
        this values are used to rerender the form."""
        self.loaded_data = self._get_data_from_item()
        """This is the initial data loaded from the given item. Used to
        render the readonly forms"""
        self.converted = {}
        """This is the data which is converted to python values
         during validation time"""
        if not values:
            values = {}
        self.merged_data = dict(self.loaded_data.items() + values.items())
        # set default values
        for field in self.fields:
            if self.fields[field].value:
                self.merged_data[field] = self.fields[field].value
        """This is merged date from the initial data loaded from the
        given item and userprovided values on form initialisation. The
        user defined values are merged again on render time"""
        self.warnings = []
        """Form wide warnings. This list contains warnings which affect
        the entire form and not specific fields. These warnings are show
        at the top of evere page."""
        self.errors = []
        """Form wide errors. This list contains errors which affect
        the entire form and not specific fields. These errors are show
        at the top of evere page."""

    def _set_current_field_data(self, data):
        for key in self.fields:
            value = data.get(key)
            if value is not None:
                field = self.fields[key]
                field.set_value(value)

    def _set_previous_field_data(self, data):
        for key in self.fields:
            value = data.get(key)
            if value or isinstance(value, int):
                field = self.fields[key]
                field.set_previous_value(value)

    def _get_data_from_item(self):
        values = {}
        if not self._item:
            return values
        for name, field in self._config.get_fields().iteritems():
            try:
                values[name] = getattr(self._item, name)
            except AttributeError:
                values[name] = None
        return values

    def _filter_values(self, values):
        """Will return a filtered dictionary of the given values
        dictionary which only contains values which are actually part of
        the current form.

        :values: Dicionary with unfilterd values
        :returns: Dicionary with filtered values

        """
        filtered = {}
        for fieldname, field in self.fields.iteritems():
            if fieldname in values:
                filtered[fieldname] = values[fieldname]
        return filtered

    def deserialize(self, data):
        """Returns a dictionary with pythonized data data. Usually this
        is the submitted data coming from a form. The dictionary will
        include all values provided in the initial data dictionary
        converted into python datatype.

        :data: Dictionary with serialized data
        :returns: Dictionary with deserialized data

        """
        deserialized = {}

        # Load relations of the item. Those are needed to deserialize
        # the relations.
        relation_names = {}

        if self._item:
            for fieldname in data.keys():
                prop = get_sa_property(self._item, fieldname)
                if isinstance(prop, sa.orm.properties.RelationshipProperty):
                    relation_names[fieldname] = prop

        for fieldname, value in self._filter_values(data).iteritems():
            field = self.fields.get(fieldname)
            try:
                serialized = data.get(field.name)
                deserialized[fieldname] = to_python(field,
                                                    serialized,
                                                    relation_names)
            except DeserializeException as ex:
                self._add_error(field.name,
                                self._translate(ex.message) % ex.value)
        log.debug("Deserialized values: %s" % deserialized)
        return deserialized

    def serialize(self, data):
        """Returns a dictionary with serialized data from the forms
        item.  The dictionary will include all attributes
        and relations values of the items. The key in the dictionary is
        the name of the relation/attribute. In case of relations the
        value in the dictionary is the "id" value of the related item.
        If no item is present then return a empty dict.

        :returns: Dictionary with serialized values of the item.

        """
        serialized = {}
        for fieldname, value in self._filter_values(data).iteritems():
            field = self.fields.get(fieldname)
            serialized[fieldname] = from_python(field, value)
        log.debug("Serialized values: %s" % serialized)
        return serialized

    def _build_fields(self):
        """Returns a dictionary with all Field instances which are
        configured for this form.
        :returns: Dictionary with Field instances

        """
        fields = {}
        for name, field in self._config.get_fields().iteritems():
            fields[name] = Field(self, field, self._translate)
        return fields

    @property
    def pages(self):
        return self._config.get_pages()

    def has_errors(self):
        """Returns True if one of the fields in the form has errors"""
        for field in self.fields.values():
            if len(field.get_errors()) > 0:
                return True
        return len(self.errors) != 0

    def has_warnings(self):
        """Returns True if one of the fields in the form has warnings"""
        for field in self.fields.values():
            if len(field.get_warnings()) > 0:
                return True
        return len(self.warnings) != 0

    def get_errors(self, page=None):
        """Returns a dictionary of all errors in the form. If page
        parameter is given, then only the errors for fields on the given
        page are returned. This dictionary will contain the errors if
        the validation fails. The key of the dictionary is the fieldname
        of the field.  As a field can have more than one error the value
        is a list.

        :page: Dictionary with errors
        :returns: Dictionary with errors
        """
        if page is not None:
            fields_on_page = self._config.get_fields(page)

        errors = {}
        for field in self.fields.values():
            if page is not None and field.name not in fields_on_page:
                continue
            if len(field.get_errors()) > 0:
                errors[field.name] = field.get_errors()
        if len(self.errors) != 0 and page is None:
            errors[""] = self.errors
        return errors

    def get_warnings(self, page=None):
        """Returns a dictionary of all warnings in the form. If page
        parameter is given, then only the warnings for fields on the given
        page are returned. This dictionary will contain the warnings if
        the validation fails. The key of the dictionary is the fieldname
        of the field.  As a field can have more than one warning the value
        is a list.

        :page: Name of the page
        :returns: Dictionary with warnings
        """
        if page is not None:
            fields_on_page = self._config.get_fields(page)

        warnings = {}
        for field in self.fields.values():
            if page is not None and field.name not in fields_on_page:
                continue
            if len(field.get_warnings()) > 0:
                warnings[field.name] = field.get_warnings()
        if len(self.warnings) != 0 and page is None:
            warnings[""] = self.warnings
        return warnings

    def get_field(self, name):
        return self.fields[name]

    def add_validator(self, validator):
        return self.external_validators.append(validator)

    def render(self, values={}, page=0, buttons=True,
               previous_values={}, outline=True):
        """Returns the rendererd form as an HTML string.

        :values: Dictionary with values to be prefilled/overwritten in
                 the rendered form.
        :previous_values: Dictionary of values of the last saved state
                          of the item. If provided a diff between the
                          current and previous values will be renderered
                          in readonly mode.
        :outline: Boolean flag to indicate that the outline for pages
                  should be rendered. Defaults to true.
        :returns: Rendered form.

        """
        self.current_page = page

        # Merge the items_values with the extra provided values. Extra
        # values will overwrite the item_values.

        #  TODO: Remove merging user provided values on render time as
        #  this is to late for values used on form validation which must
        #  be already present on form initialisation. So user provided
        #  values can now be defined on form initialisation. (ti)
        #  <2016-08-17 15:18>

        if values.items():
            log.warning("Providing userdefined values on "
                        "rendertime will be disabled. Please provide the "
                        "values at time of form initialisation.")
            for v in values:
                if self.merged_data.get(v) != values[v]:
                    self.merged_data[v] = values[v]

        # Set current and previous values of the fields in the form. In
        # case of errors in the form the submitted_data dictionary will
        # contain the submitted values which should be displayed in the
        # form again.
        if self.submitted_data:
            self.prefill_form_private_fields()
            self._set_current_field_data(self.submitted_data)
            self.merged_data = self.converted # for rule evaluation in form
        else:
            self._set_current_field_data(self.merged_data)
        self._set_previous_field_data(previous_values)
        # Add csrf_token to the values dictionary
        values['csrf_token'] = self._csrf_token

        renderer = FormRenderer(self, self._translate)
        form = renderer.render(buttons=buttons, outline=outline)
        return form

    def prefill_form_private_fields(self):
        for name, field in self.fields.items():
            if name.startswith("_"):
                field.value = self.merged_data[name]

    def _add_error(self, fieldname, error):
        if fieldname is None:
            self.errors.append(error)
        else:
            field = self.get_field(fieldname)
            if isinstance(error, list):
                for err in error:
                    field.add_error(err)
            else:
                field.add_error(error)

    def _add_warning(self, fieldname, warning):
        if fieldname is None:
            self.warnings.append(warning)
        else:
            field = self.get_field(fieldname)
            if isinstance(warning, list):
                for war in warning:
                    field.add_warning(war)
            else:
                field.add_warning(warning)

    def validate(self, submitted=None, evaluate=True):
        """Returns True if the validation succeeds else False.
        Validation of the data happens in three stages:

        1. Prevalidation. Custom rules that are checked before any
        datatype checks on type conversations are made.
        2. Basic type checks and type conversation. Type checks and type
        conversation is done based on the data type of the field and
        further constraint defined in the database if the form is
        instanciated with an SQLAlchemy mapped item.
        3. Postvalidation. Custom rules that are checked after the type
        conversation was done. Note: Postevaluation is only done for
        successfull converted values.
        4. External Validators. External defined checks done on teh
        converted values. Note: Validators are only called for
        successfull converted values

        All errors are stored in the errors dictionary through the
        process of validation. After the validation finished the values
        are stored in the data dictionary. In case there has been errors
        the dictionary will contain the origin submitted data.

        :submitted: Dictionary with submitted values.
        :returns: True or False

        """

        if not submitted:
            unvalidated = self.serialize(self.merged_data)
        else:
            try:
                unvalidated = submitted.mixed()
            except AttributeError:
                unvalidated = submitted
            unvalidated = remove_ws(unvalidated)
            log.debug("Submitted data: %s" % unvalidated)
            self.submitted_data = unvalidated
        converted = self.deserialize(unvalidated)

        # Validate the fields. Ignore fields which are disabled in
        # conditionals First get list of fields which are still in the
        # form after conditionals has be evaluated
        fields_to_check = self._config.get_fields(values=converted,
                                                  evaluate=evaluate)
        for fieldname, field in fields_to_check.iteritems():
            field = self.fields[fieldname]
            for rule in field.get_rules():
                if rule.mode == "pre":
                    result = rule.evaluate(unvalidated)
                elif fieldname not in converted:
                    # Ignore rule if the value can't be converted.
                    continue
                else:
                    result = rule.evaluate(converted)
                if not result:
                    if rule.triggers == "warning":
                        self._add_warning(fieldname, rule.msg)
                    else:
                        self._add_error(fieldname, rule.msg)

            for src, msg in field.get_validators():
                src = src.split(".")
                checker = getattr(importlib.import_module(".".join(src[0:-1])),
                                  src[-1])
                validator = Validator(fieldname, msg, checker, self)
                if not validator.check(converted):
                    if validator._triggers == "error":
                        self._add_error(validator._field, validator._error)
                    else:
                        self._add_warning(validator._field, validator._error)

        # Custom validation. User defined external validators.
        for validator in self.external_validators:
            if (validator._field not in converted
                and validator._field is not None):
                # Ignore validator if the value can't be converted.
                continue
            if not validator.check(converted):
                if validator._triggers == "error":
                    self._add_error(validator._field, validator._error)
                else:
                    self._add_warning(validator._field, validator._error)

        # If the form is valid. Save the converted and validated data
        # into the data dictionary.
        has_errors = self.has_errors()
        self.converted = converted
        if not has_errors:
            self.data = converted
        self.validated = True
        return not has_errors

    def save(self):
        """Will save the validated data back into the item. In case of
        an SQLAlchemy mapped item the data will be stored into the
        database.
        :returns: Item with validated data.

        """
        if not self.validated:
            raise StateError('Saving is not possible without prior validation')
        if self.has_errors():
            raise StateError('Saving is not possible if form has errors')

        # Only save if there is actually an item.
        if self._item is not None:
            # TODO: Iterate over fields here. Fields should know their value
            # and if they are a relation or not (torsten) <2013-07-24 23:24>
            for key, value in self.data.iteritems():
                setattr(self._item, key, value)
            # If the item has no id, then we assume it is a new item. So
            # add it to the database session.
            if not self._item.id:
                self._dbsession.add(self._item)
        return self._item

    def __repr__(self):
        def f(field):
            name = field.name
            value = field.get_value()
            errors = field.has_errors
            warnings = field.has_warnings
            return "{}:\t{} \terrors: {} warnings: {}".format(name, value, errors, warnings)

        fields = [f(v) for _, v in self.fields.iteritems()]
        lines = "\n".join(fields)
        lines += "\nhas errors: {}".format(self.has_errors())
        return lines


class Field(object):
    """Wrapper for fields in the form. The purpose of this class is to
    provide a common interface for the renderer independent to the
    underlying implementation detail of the field."""

    def __init__(self, form, config, translate):
        """Initialize the field with the given field configuration.

        :config: Field configuration

        """
        self._form = form
        self._config = config
        self.sa_property = self._get_sa_property()
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
        # If value is a basestring we will try to convert the default
        # value into the the right python value. But if it is not a
        # basestring e.g a datettime coming from a date('today')
        # expression we will leave the value as it is.
        dtype = self.get_type()
        if value and isinstance(value, basestring) and dtype not in ['manytoone', 'manytomany', 'onetomany']:
	    # Deserialization of relations is not supported yet.
            value = to_python(self, value, {})
        self.value = value

        self.previous_value = None
        """Value as string of the field. Will be set on rendering the
        form"""

    @property
    def rules_to_string(self):
        return [u"{}".format(r) for r in self.get_rules()]

    def __repr__(self):
        rules = "rules: \n\t\t{}".format("\n\t".join(self.rules_to_string))
        field = u"field:\t\t{}".format(self.name)
        value = u"value:\t\t{}, {}".format(repr(self.get_value()), type(self.get_value()))
        required = "required:\t{}".format(self.is_required)
        desired = "desired:\t{}".format(self.is_desired)
        # validated = "validated:\t{}".format(self.is_validated)
        _type = "type:\t\t{}".format(self.get_type())
        return "\n".join([field, required, desired, value, _type, rules]) + "\n"

    def __getattr__(self, name):
        """Make attributes from the configuration directly available"""
        return getattr(self._config, name)

    def _get_sa_mapped_class(self):
        if self.name.find(".") > -1:
            # Special handling for prefixed relations in case of
            # included entities.
            # Those included entities usually has a prefix which defines
            # the path to the attribute.
            #
            # Example:
            # If the fieldname ist "foo.bar" this means that the current
            # item has a relation named "foo". And within this foo
            # relation a value should be set in "bar".
            #
            # Unfortunately this special notation breaks the default
            # procedure how to get the mapped class of this attribute.
            path = self.name.split(".")
            rel = getattr(self._form._item, ".".join(path[:-1]))
            field = path[-1]
            sa_property = get_sa_property(rel, field)
            return sa_property.mapper.class_
        else:
            return self.sa_property.mapper.class_

    def _get_sa_property(self):
        if not self._form._item:
            return None
        return get_sa_property(self._form._item, self.name)

    def get_type(self):
        """Returns the datatype of the field."""
        if self._config.type:
            return self._config.type
        if self.sa_property:
            try:
                column = self.sa_property.columns[0]
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
                    log.warning('Unhandled datatype: %s' % dtype)
            except AttributeError:
                return self.sa_property.direction.name.lower()
        return "string"

    def get_rules(self):
        """Returns a list of configured rules for the field."""
        return self._config.get_rules()

    def get_warning_rules(self):
        return [r for r in self.get_rules()
                if r.triggers == "warning"]

    def get_error_rules(self):
        return [r for r in self.get_rules()
                if r.triggers == "error"]

    def has_warning_rules(self):
        """Returns a True if there is at least on rule that can trigger
        a warning."""
        return len(self.get_warning_rules()) > 0

    def has_error_rules(self):
        """Returns a True if there is at least on rule that can trigger
        a error."""
        return len(self.get_error_rules()) > 0

    @property
    def is_empty(self):
        if self.get_value() is None:
            return True
        if self.get_type() == "integer" and self.get_value() is not None:
            return False
        return bool(self.get_value()) is False

    @property
    def empty_message(self):
        if self.is_required:
            return config.required_msg
        return config.desired_msg

    @property
    def has_warnings(self):
        return len(self.get_warnings()) > 0

    @property
    def has_errors(self):
        return len(self.get_errors()) > 0

    def get_errors(self):
        return set(self._errors)

    def get_warnings(self):
        return set(self._warnings)

    def is_missing(self):
        """Return True if this field is a desired or required field and
        the value of the fields is actually missing in the current
        context after all rules have been evaluated. Note the rules the
        are not evaluated because the field is in an inactive
        conditional will have the result==None which means the rule is
        not evaluated."""
        if self.get_value():
            return False
        for rule in self.get_rules():
            if (rule.desired or rule.required) and rule.result is False:
                return True
        return False

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
                    if hasattr(v, "id"):
                        v = v.id
                    if unicode(v) == unicode(opt[1]):
                        ex_values.append("%s" % opt[0])
            return ", ".join(ex_values)
        else:
            if value:
                return from_python(self, value)
            elif default:
                return default
            else:
                return value

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
        % marks the options in the selection field. It is used to
        iterate over the options in the selection. I case the
        options are SQLAlchemy based options the variable can be
        used to access a attribute of the item. E.g. %id will
        access the id of the current option item. For user defined
        options "%" can be used to iterate over the user defined
        options. In this case %attr will access a given attribte
        in the option. A bare "%" will give the value of the
        option.

        :param token:
        :param unmodified_expression:
        :param values:
        :return:
        """
        is_optionfield = token.startswith("%")
        is_value_of_formitem = token.startswith("@")
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
        return getattr(self._form._item, token.strip("@"))

    def parse_optionfield(self, token):
        return "*%s" % (token.strip("%") or "value")

    def determine_values(self):
        if not self._form._item:
            return {}
        values = self._form._item.get_values()
        values.update(self._form.merged_data)
        return values

    def _load_options_from_db(self):
        # Get mapped clazz for the field
        try:
            clazz = self._get_sa_mapped_class()
            return self._form._dbsession.query(clazz)
        except:
            # Catch exception here. This exception can happen when
            # rendering the form in the preview of the formeditor. In
            # this case the item is None and will fail to get the mapped
            # class.
            log.error("Can not get a mappend class for '%s' "
                      "to load the option from db" % self.name)
        return []

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

        Filtering is currently actually only done for selection based on
        the SQLAlchemy model and which are loaded from the database.
        """
        options = []
        _ = self._form._translate
        if self.get_type() == 'manytoone':
            options.append((_("no selection"), "", True))
        user_defined_options = self._config.options
        if (isinstance(user_defined_options, list)
            and len(user_defined_options) > 0):
            for option in self.filter_options(user_defined_options):
                options.append((option[0], option[1], option[2]))
        elif isinstance(user_defined_options, str):
            for option in self._form.merged_data.get(user_defined_options):
                options.append((option[0], option[1], True))
        elif self._form._dbsession:
            options.extend(self.filter_options(self._load_options_from_db()))
        else:
            # TODO: Try to get the session from the item. Ther must be
            # somewhere the already bound session. (torsten) <2013-07-23 00:27>
            log.warning('No db connection configured for this form. Can '
                        'not load options')
            return []
        return self.sort_options(options)

    def add_error(self, error):
        self._errors.append(error)

    def add_warning(self, warning):
        self._warnings.append(warning)

    def render(self, active):
        """Returns the rendererd HTML for the field"""
        self.renderer._active = active
        return self.renderer.render()

    def is_relation(self):
        return isinstance(self.sa_property,
                          sa.orm.RelationshipProperty)

    @property
    def is_desired(self):
        """Returns true if field is set as desired in field configuration"""
        return self.desired

    @property
    def is_required(self):
        """Returns true if the required flag of the field configuration
        is set"""
        return self.required

    def is_readonly(self):
        """Returns true if either the readonly flag of the field
        configuration is set or the whole form is marked as readonly"""
        return self.readonly or False

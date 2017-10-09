import logging
import importlib
import inspect
import sqlalchemy as sa
from formbar.renderer import FormRenderer
from formbar.fields import FieldFactory
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


class FormDataprovider(object):
    """Dummy class which can be used to provide dynamic data to the
    form. It can be provided as item on the form init to provide
    dynamically loaded options and values.

    As said the dataprovider can be user to provide `options` and `values`.
    Both are provided by defining properties.

    1. Value
    The function should simply return the pythonic value of the field:

        @property
        def foo(self):
            return "1"

    1. Options
    The function should return a list of tuples. The first value of the
    tuple is the displayed label and the second value is the value of
    the option:

        @property
        def foo_options(self):
            return [("Foo", "1"), ("Bar", "2")]

    or you can use the helper method `get_options(fieldname)`
    """

    def __init__(self, ctx):
        self.ctx = ctx
        """Can be anything. E.g db connection, request. It depends on the context."""

    def get_options(self, name):
        if hasattr(self, name+"_options"):
            return getattr(self, name+"_options")
        return []

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
                 values=None, timezone=None):
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
        :timezone: String of the timezone of the form. E.g.
        Europe/Berlin. Used for proper display of the datetime.
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

        self._timezone = timezone

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
        self.loaded_data = self._get_data_from_item()
        """This is the initial data loaded from the given item. Used to
        render the readonly forms"""
        if not values:
            values = {}
        self.merged_data = dict(self.loaded_data.items() + values.items())
        """This is merged date from the initial data loaded from the
        given item and userprovided values on form initialisation. The
        user defined values are merged again on render time"""
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
        self.converted = {}
        """This is the data which is converted to python values
         during validation time"""
        # set default values
        for field in self.fields:
            if self.fields[field].value:
                self.merged_data[field] = self.fields[field].value
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

        for fieldname, value in self._filter_values(data).iteritems():
            field = self.fields.get(fieldname)
            try:
                serialized = data.get(field.name)
                deserialized[fieldname] = to_python(field, serialized)
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
        factory = FieldFactory(self, self._translate)
        for name, field in self._config.get_fields().iteritems():
            fields[name] = factory.create(field)
        return fields

    @property
    def pages(self):
        return self._config.get_pages()

    def has_errors(self):
        """Returns True if one of the fields in the form has errors"""
        for field in self.fields.values():
            if len(field.errors) > 0:
                return True
        return len(self.errors) != 0

    def has_warnings(self):
        """Returns True if one of the fields in the form has warnings"""
        for field in self.fields.values():
            if len(field.warnings) > 0:
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
            if len(field.errors) > 0:
                errors[field.name] = field.errors
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
            if len(field.warnings) > 0:
                warnings[field.name] = field.warnings
        if len(self.warnings) != 0 and page is None:
            warnings[""] = self.warnings
        return warnings

    def get_field(self, name):
        return self.fields[name]

    def add_validator(self, validator):
        return self.external_validators.append(validator)

    def render(self, values=None, page=0, buttons=True,
               previous_values=None, outline=True):
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
        if not values:
            values = {}
        if not previous_values:
            previous_values = {}
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
            self._set_current_field_data(self.converted)
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
                field.value = self.merged_data.get(name)

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

    #def __repr__(self):
    #    def f(field):
    #        name = field.name
    #        value = field.get_value()
    #        errors = field.has_errors
    #        warnings = field.has_warnings
    #        return "{}:\t{} \terrors: {} warnings: {}".format(name, value, errors, warnings)

    #    fields = [f(v) for _, v in self.fields.iteritems()]
    #    lines = "\n".join(fields)
    #    lines += "\nhas errors: {}".format(self.has_errors())
    #    return lines

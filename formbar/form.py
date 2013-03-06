import datetime
from formbar.fahelpers import get_fieldset
from formbar.renderer import FormRenderer


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class StateError(Error):
    """Exception raised for state errors while processing the form.

        :msg:  explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg


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

    def __init__(self, config, item=None, dbsession=None):
        """Initialize the form with ``Form`` configuration instance and
        optional an SQLAlchemy mapped object.

        :config: FormConfiguration.
        :item: SQLAlchemy mapped instance
        :dbsession: Dbsession

        """
        self._config = config
        self._item = item
        self._dbsession = dbsession

        self.data = {}
        """After submission this Dictionary will contain either the
        validated data on successfull validation or the origin submitted
        data."""
        self.errors = {}
        """This dictionary will contain the errors if the validation
        fails. The key of the dictionary is the fieldname of the field.
        As a field can have more than one error the value is a list."""
        self.validated = False
        """Flag to indicate if the form has been validated. Init value
        is False.  which means no validation has been done."""
        self.fs = get_fieldset(item, config)
        """FormAlchemy fieldset"""

    def get_field(self, name):
        """Returns a FormAlchemy field instance.

        :name: @todo
        :returns: @todo

        """
        return self.fs[name]

    def render(self, values={}):
        """@todo: Docstring for render

        :values: Dictionary with values to be prefilled in the rendered form.
        :returns: Rendered form.

        """
        renderer = FormRenderer(self)
        return renderer.render(values)

    def _add_error(self, fieldname, error):
        if fieldname not in self.errors:
            self.errors[fieldname] = []
        self.errors[fieldname].append(error)

    def _convert(self, field, value):
        """Returns a converted value depending of the fields datatype

        :field: configuration of the field
        :value: value to be converted
        """
        dtype = field.type
        if dtype == 'integer':
            try:
                return int(value)
            except ValueError:
                msg = "%s is not a integer value." % value
                self._add_error(field.name, msg)
        elif dtype == 'float':
            try:
                return float(value)
            except ValueError:
                msg = "%s is not a float value." % value
                self._add_error(field.name, msg)
        elif dtype == 'date':
            try:
                #@TODO: Support other dateformats that ISO8601
                y, m, d = value.split('-')
                y = int(y)
                m = int(m)
                d = int(d)
                try:
                    return datetime.date(y, m, d)
                except ValueError, e:
                    msg = "%s is an invalid date (%s)" % (value, e)
                    self._add_error(field.name, msg)
            except:
                msg = "%s is not a valid date format." % value
                self._add_error(field.name, msg)
        return value

    def validate(self, values):
        """Returns True if the validation succeeds else False.
        Validation of the data happens in three stages:

        1. Prevalidation. Custom rules that are checked before any
        datatype checks on type conversations are made.
        2. Basic type checks and type conversation. Type checks and type
        conversation is done based on the data type of the field and
        further constraint defined in the database if the form is
        instanciated with an SQLAlchemy mapped item.
        3. Postvalidation. Custom rules that are checked after the type
        conversation was done.

        All errors are stored in the errors dictionary through the
        process of validation. After the validation finished the values
        are stored in the data dictionary. In case there has been errors
        the dictionary will contain the origin submitted data.

        :values: Dictionary with submitted values.
        :returns: True or False

        """
        # 1. Save copy origin submitted data
        origin_data = values

        # 2. Iterate over all fields and start the validation.
        for fieldname in values.keys():
            field = self._config.get_field(fieldname)
            # 3. Prevalidation
            for rule in field.rules:
                if rule.mode != 'pre':
                    continue
                result = rule.evaluate(values)
                if not result:
                    self._add_error(fieldname, rule.msg)

            # 4. Basic type conversations, Defaults to String
            values[fieldname] = self._convert(field, values[fieldname])

            # 5. Postvalidation
            for rule in field.rules:
                if rule.mode != 'post':
                    continue
                result = rule.evaluate(values)
                if not result:
                    self._add_error(fieldname, rule.msg)

        # If the form is valid. Save the converted and validated data
        # into the data dictionary. If not, than save the origin
        # submitted data.
        has_errors = bool(self.errors)
        if not has_errors:
            self.data = origin_data
        else:
            self.data = values
        self.validated = True
        return not has_errors

    def save(self):
        """Will save the validated data back into the item. In case of
        an SQLAlchemy mapped item the data will be stored into the
        database.
        :returns: Item with validated data.

        """
        #@TODO: Only allow saving if the validation succeeded.
        if self.validated:
            #@TODO: Save item and return
            return self._item
        else:
            raise StateError('Saving is not possible without prior validation')

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

    def __init__(self, config, item=None):
        """Initialize the form with ``Form`` configuration instance and
        optional an SQLAlchemy mapped object.

        :config: FormConfiguration.
        :item: SQLAlchemy mapped instance

        """
        self._config = config
        self._item = item

        self.data = {}
        """After submission this Dictionary will contain either the
        validated data on successfull validation or the origin submitted
        data."""
        self.errors = {}
        """This dictionary will contain the errors if the validation
        fails. The key of the dictionary is the fieldname of the field.
        As a field can have more than one error the value is a list."""
        self.valid = None
        """Flag to indicate if the form is valid. Init value is None
        which means no validation has been done. False if validation
        fails and True is validation succeeds."""

    def render(self, values={}):
        """@todo: Docstring for render

        :values: Dictionary with values to be prefilled in the rendered form.
        :returns: Rendered form.

        """
        return ""

    def _add_error(self, fieldname, error):
        if not self.errors.has_key(fieldname):
            self.errors[fieldname] = []
        self.errors[fieldname].append(error)

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
        self.valid = True
        # 1. Save copy origin submitted data
        origin_data = values
        # 2. Prevalidation
        for fieldname in values.keys():
            field = self._config.get_field(fieldname)
            print field
            for rule in field.rules:
                if rule.mode != 'pre':
                    continue
                result = rule.evaluate(values)
                if not result:
                    self.valid = False
                    self._add_error(fieldname, rule.msg)

        # If the form is valid. Save the converted and validated data
        # into the data dictionary. If not, than save the origin
        # submitted data.
        if not self.valid:
            self.data = origin_data
        else:
            self.data = values
        return self.valid

    def save(self):
        """Will save the validated data back into the item. In case of
        an SQLAlchemy mapped item the data will be stored into the
        database.
        :returns: Item with validated data.

        """
        #@TODO: Only allow saving if the validation succeeded.
        pass

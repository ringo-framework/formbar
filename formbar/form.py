import logging
import datetime
import sqlalchemy as sa
from formencode import htmlfill

from formbar.fahelpers import get_fieldset, get_data
from formbar.renderer import FormRenderer, FieldRenderer

log = logging.getLogger(__name__)


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class StateError(Error):
    """Exception raised for state errors while processing the form.

        :msg:  explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg


class Validator(object):
    """Docstring for Validator """

    def __init__(self, field, error, callback):
        """@todo: to be defined

        :field: @todo
        :error: @todo
        :callback: @todo

        """
        self._field = field
        self._error = error
        self._callback = callback

    def check(self, data):
        return self._callback(self._field, data)


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

        self.fs = get_fieldset(item, config, dbsession)
        """FormAlchemy fieldset"""
        self.data = get_data(self.fs)
        """After submission this Dictionary will contain either the
        validated data on successfull validation or the origin submitted
        data."""
        self.validated = False
        """Flag to indicate if the form has been validated. Init value
        is False.  which means no validation has been done."""
        self.fields = self._build_fields()
        """Dictionary with fields."""
        self.external_validators = []
        """List with external validators. Will be called an form validation."""

    def _build_fields(self):
        """Returns a dictionary with all Field instanced which are
        configured for this form.
        :returns: Dictionary with Field instances

        """
        fields = {}
        for name, field in self._config.get_fields().iteritems():
            fa_field = self.fs[name]
            fields[name] = Field(field, fa_field)
        return fields

    def has_errors(self):
        """Returns True if one of the fields in the form has errors"""
        for field in self.fields.values():
            if len(field.get_errors()) > 0:
                return True
        return False

    def get_errors(self):
        """Returns a dictionary of all errors in the form.  This
        dictionary will contain the errors if the validation fails. The
        key of the dictionary is the fieldname of the field.  As a field
        can have more than one error the value is a list."""
        errors = {}
        for field in self.fields.values():
            if len(field.get_errors()) > 0:
                errors[field.name] = field.get_errors()
        return errors

    def get_field(self, name):
        return self.fields[name]

    def add_validator(self, validator):
        return self.external_validators.append(validator)

    def render(self, values={}):
        """Returns the rendererd form as an HTML string.

        :values: Dictionary with values to be prefilled/overwritten in
        the rendered form.
        :returns: Rendered form.

        """
        renderer = FormRenderer(self)
        form = renderer.render(values)
        return htmlfill.render(form, values or self.data)

    def _add_error(self, fieldname, error):
        field = self.get_field(fieldname)
        if isinstance(error, list):
            for err in error:
                field.add_error(err)
        else:
            field.add_error(error)

    def _convert(self, field, value):
        """Returns a converted value depending of the fields datatype

        :field: configuration of the field
        :value: value to be converted
        """
        # Handle missing value. Currently we just return None in case
        # that the provided value is an empty String
        if value == "":
            return None

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

    def validate(self, submitted):
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

        :submitted: Dictionary with submitted values.
        :returns: True or False

        """

        # This dictionary will contain the converted data
        values = {}
        fa_validated = False
        # 1. Iterate over all fields and start the validation.
        log.debug('Submitted values: %s' % submitted)
        for fieldname in submitted.keys():
            try:
                field = self._config.get_field(fieldname)
            except KeyError:
                # @TODO:
                # For 1:1 relations FA modifies the fieldname on
                # rendering to the name of the Foreign Key. This leads
                # to problems on validation when the validation code
                # tries to access a field based on the submitted data
                # and raises a KeyError as there is no field with the
                # name of the FK.
                # In this case we we just add the subbmitted data to the
                # validated data, to make the prefilling work after rendering.
                values[fieldname] = submitted.get(fieldname)
                log.warning('Found field "%s" in submitted data,'
                            ' while validating data for "%s" which is'
                            ' not a configured field'
                            % (fieldname, repr(self._item)))
                continue
            # 3. Prevalidation
            for rule in field.rules:
                if rule.mode != 'pre':
                    continue
                result = rule.evaluate(submitted)
                if not result:
                    self._add_error(fieldname, rule.msg)

            # 4. Basic type conversations, Defaults to String
            # Validation can happen in two variations:
            #
            # 4.1 If item is None (No sqlalchemy mapped item is provided),
            # then convert each field in the Form into its python type.
            #
            # 4.2 If an item was provided, than use the FormAlchemy
            # validation once for the whole fieldset. After validation
            # was done save the data into the internal data dictionary.
            if self._item is None:
                values[fieldname] = self._convert(field, submitted[fieldname])
            else:
                if not fa_validated:
                    self.fs.rebind(self._item, data=submitted)
                    fa_valid = self.fs.validate()
                    fa_validated = True
                    if not fa_valid:
                        # Collect all errors form formalchemy
                        for err_field, err_msg in self.fs.errors.iteritems():
                            self._add_error(err_field.key, err_msg)
                if not fa_valid:
                    values[fieldname] = self.fs[fieldname].raw_value
                else:
                    values[fieldname] = self.fs[fieldname].value

            # 5. Postvalidation
            for rule in field.rules:
                if rule.mode != 'post':
                    continue
                result = rule.evaluate(values)
                if not result:
                    self._add_error(fieldname, rule.msg)

        # 6. Custom validation. User defined external validators.
        for validator in self.external_validators:
            if not validator.check(values):
                self._add_error(validator._field, validator._error)

        # If the form is valid. Save the converted and validated data
        # into the data dictionary. If not, than save the origin
        # submitted data.
        has_errors = self.has_errors()
        if not has_errors:
            self.data = values
        else:
            self.data = submitted
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

        # @FIXME: _item is only set when this form is used in connection
        # with an SQLAlchemy mapped item.If the form is used as normal
        # form _item is none. This is not consistent. There seems to be
        # more options to fix this:
        # 1. Raise exception when calling save if there is no _item.
        # 2. Make sure there is always an item
        # 3. Save the item if there is an item, else ignore. Return None
        # in both cases.
        if self._item is not None:
            try:
                self._save()
            except:
                self.fs.sync()
            return self._item

    def _save(self):
        mapper = sa.orm.object_mapper(self._item)
        relation_properties = filter(
            lambda p: isinstance(p, sa.orm.properties.RelationshipProperty),
            mapper.iterate_properties)

        relation_names = {}
        for prop in relation_properties:
            relation_names[prop.key] = prop

        # related_classes = [prop.mapper.class_ for prop in relation_properties]
        # related_tables = [prop.target for prop in relation_properties]

        for key, value in self.data.iteritems():
            relation = relation_names.get(key)
            if relation:
                log.info('Todo: Implement setting relation')
                li = self._load_relations(relation.mapper.class_, value)
                try:
                    setattr(self._item, key, li)
                except:
                    log.exception('Error while setting %s with %s' % (key, li))
            else:
                setattr(self._item, key, value)

        self._dbsession.add(self._item)

    def _load_relations(self, relation, values):
        loaded = []
        for value in values:
            r = self._dbsession.query(relation).filter(relation.id == value).one()
            loaded.append(r)
        return loaded




class Field(object):
    """Wrapper for fields in the form. The purpose of this class is to
    provide a common interface for the renderer independent to the
    underlying implementation detail of the field."""

    def __init__(self, config, fa_field):
        """Initialize the field with the given field configuration.

        :config: Field configuration

        """
        self._config = config
        self._fa_field = fa_field
        self._errors = []

    def __getattr__(self, name):
        """Make attributes from the configuration directly available"""
        return getattr(self._config, name)

    def add_error(self, error):
        self._errors.append(error)

    def get_errors(self):
        return self._errors

    def render(self):
        """Returns the rendererd HTML for the field"""
        renderer = FieldRenderer(self)
        return renderer.render()

    def is_required(self):
        """Returns true if either the required flag of the field
        configuration is set or the formalchemy field is required."""
        return self.required or self._fa_field.is_required()

    def is_readonly(self):
        """Returns true if either the readonly flag of the field
        configuration is set or the formalchemy field is readonly."""
        return self.readonly or self._fa_field.is_readonly()

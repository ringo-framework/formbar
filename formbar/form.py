import logging
import datetime
import sqlalchemy as sa
from formencode import htmlfill, variabledecode
from formbar.renderer import FormRenderer, get_renderer
from formbar.rules import Rule, Parser

log = logging.getLogger(__name__)


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


class Validator(object):
    """Docstring for Validator"""

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

    def __init__(self, config, item=None, dbsession=None, translate=None,
                 change_page_callback={}, renderers={}, request=None,
                 csrf_token=None):
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

        """
        self._config = config
        self._item = item
        self._dbsession = dbsession
        self._request = request
        self._csrf_token = csrf_token
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
        self.data = self.serialize(self._get_data_from_item())
        """After submission this Dictionary will contain either the
        validated data on successfull validation or the origin submitted
        data."""

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


    def serialize(self, data):
        """Returns a dictionary with serialized data from the forms
        item.  The return dictionary is suitable for htmlfill to prefill
        the rendered form. The dictionary will include all attributes
        and relations values of the items. The key in the dictionary is
        the name of the relation/attribute. In case of relations the
        value in the dictionary is the "id" value of the related item.
        If no item is present then return a empty dict.

        :returns: Dictionary with serialized values of the item.

        """
        serialized = {}
        if not data:
            return serialized
        for name, field in self.fields.iteritems():
            ftype = field.get_type()
            try:
                value = data.get(name)
                if value is None:
                    serialized[name] = ""
                elif isinstance(value, list):
                    vl = []
                    for v in value:
                        try:
                            vl.append(v.id)
                        except AttributeError:
                            vl.append(v)
                    serialized[name] = vl
                else:
                    try:
                        serialized[name] = value.id
                    except AttributeError:
                        if ftype == "time":
                            td = datetime.timedelta(seconds=int(value))
                            d = datetime.datetime(1, 1, 1) + td
                            serialized[name] = "%02d:%02d:%02d" % (d.hour, d.minute, d.second)
                        elif ftype == "datetime":
                            serialized[name] = value.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            serialized[name] = value
            except AttributeError:
                log.warning('Can not get value for field "%s". '
                            'The field is no attribute of the item' % name)
                serialized[name] = ""
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

    def has_errors(self):
        """Returns True if one of the fields in the form has errors"""
        for field in self.fields.values():
            if len(field.get_errors()) > 0:
                return True
        return False

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
            if page is not None and field.name not in fields_on_page: continue
            if len(field.get_errors()) > 0:
                errors[field.name] = field.get_errors()
        return errors

    def get_field(self, name):
        return self.fields[name]

    def add_validator(self, validator):
        return self.external_validators.append(validator)

    def render(self, values={}, page=0, buttons=True):
        """Returns the rendererd form as an HTML string.

        :values: Dictionary with values to be prefilled/overwritten in
        the rendered form.
        :returns: Rendered form.

        """
        self.current_page = page
        renderer = FormRenderer(self, self._translate)
        form = renderer.render(buttons)

        # If we have a POST request than the user has sent modfied data.
        # The content of self.values depends on the validation.
        # If the form is validated and the form contains no erros
        # than we use the serialized values of self.data which includes
        # the converted values.
        # In the other cases return the self.data attribute which the
        # submitted error data on POST.
        if self._request and self._request.POST:
            if self.validated and not self.has_errors():
                values = self.serialize(self.data)
            else:
                values = self.data
        # If we have a GET request than the user has loaded a exising
        # item (or wants to create a new one). In this case we will need
        # to get the initial data of the item an merge it with the
        # provided values. This data is already serialized in the
        # self.data attribute.
        else:
            item_values = self.data
            values.update(item_values)

        # Add csrf_token to the values dictionary
        values['csrf_token'] = self._csrf_token
        return htmlfill.render(form, values)

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
        relation_names = {}
        try:
            mapper = sa.orm.object_mapper(self._item)
            relation_properties = filter(
                lambda p: isinstance(p, sa.orm.properties.RelationshipProperty),
                mapper.iterate_properties)
            for prop in relation_properties:
                relation_names[prop.key] = prop
        except sa.orm.exc.UnmappedInstanceError:
            if not self._item:
                pass # The form is not mapped to an item.
            else:
                raise

        converted = ""
        dtype = field.get_type()
        if dtype == 'string':
            try:
                converted = value
            except ValueError:
                msg = "%s is not a string value." % value
                self._add_error(field.name, msg)
        elif dtype == 'integer':
            if not value:
                return None
            try:
                converted = int(value)
            except ValueError:
                msg = "%s is not a integer value." % value
                self._add_error(field.name, msg)
        elif dtype == 'float':
            if not value:
                return None
            try:
                converted = float(value)
            except ValueError:
                msg = "%s is not a float value." % value
                self._add_error(field.name, msg)
        elif dtype == 'boolean':
            if not value:
                return None
            try:
                converted = value in ['True', '1', 't']
            except ValueError:
                msg = "%s is not a boolean value." % value
                self._add_error(field.name, msg)
        elif dtype == 'file':
            try:
                # filename = value.filename
                converted = value.file.read()
            except AttributeError:
                return None
            except ValueError:
                msg = "%s is not a file value." % value
                self._add_error(field.name, msg)
        elif dtype == 'date':
            if not value:
                return None
            try:
                #@TODO: Support other dateformats that ISO8601
                y, m, d = value.split('-')
                y = int(y)
                m = int(m)
                d = int(d)
                try:
                    converted = datetime.date(y, m, d)
                except ValueError, e:
                    msg = "%s is an invalid date (%s)" % (value, e)
                    self._add_error(field.name, msg)
            except:
                msg = "%s is not a valid date format." % value
                self._add_error(field.name, msg)
        elif dtype == 'time':
            if not value:
                return None
            try:
                h, m, s = value.split(':')
                h = int(h)
                m = int(m)
                s = int(s)
                converted = datetime.timedelta(hours=h, minutes=m, seconds=s).total_seconds()
            except ValueError:
                msg = "Value '%s' must be in format 'HH:MM:SS'" % value
                self._add_error(field.name, msg)
        elif dtype == 'datetime':
            if not value:
                return None
            try:
                tmpdate = value.split(' ')
                # Time is optional. If not provided set time to 00:00:00
                if len(tmpdate) == 2:
                    date, time = value.split(' ')
                else:
                    date = tmpdate[0]
                    time = "00:00:00"
                y, m, d = date.split('-')
                y = int(y)
                m = int(m)
                d = int(d)
                h, M, s = time.split(':')
                h = int(h)
                M = int(M)
                s = int(s)
                converted = datetime.datetime(y, m, d, h, M, s)
            except:
                log.exception("e")
                msg = "%s is not a valid datetime format." % value
                self._add_error(field.name, msg)
        # Reltation handling
        elif dtype == 'manytoone':
            try:
                db = self._dbsession
                rel = relation_names[field.name].mapper.class_
                if value in ("", None):
                    converted = None
                else:
                    value = db.query(rel).filter(rel.id == int(value)).one()
                    converted = value
            except ValueError:
                msg = "Reference value '%s' must be of type integer" % value
                self._add_error(field.name, msg)
        elif dtype in ['onetomany', 'manytomany']:
            if not value:
                return []
            try:
                values = []
                db = self._dbsession
                rel = relation_names[field.name].mapper.class_
                for v in value:
                    values.append(db.query(rel).filter(rel.id == int(v)).one())
                converted = values
            except ValueError:
                msg = "Reference value '%s' must be of type integer" % value
                self._add_error(field.name, msg)
        log.debug("Converted value '%s' (%s) of field '%s' (%s)"
                  % (converted, type(converted), field.name, dtype))
        return converted

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

        dirty_submitted = variabledecode.variable_decode(submitted)
        # This dictionary will contain the converted data
        values = {}

        # 1. Collect all configured fields from form configuration and
        # remove out values from the submitted data which are not part
        # of the form.
        fields_all = []
        submitted = {}
        log.debug('Submitted values: %s' % dirty_submitted)
        for fieldname, field in self.fields.iteritems():
            fields_all.append((fieldname, self.fields[fieldname]))
            if dirty_submitted.has_key(fieldname):
                submitted[fieldname] = dirty_submitted[fieldname]

        # 2. Convert all values
        for fieldname, field in fields_all:
            # Basic type conversations, Defaults to String
            if not field.is_readonly():
                # Only add the value if the field is not marked as readonly
                values[fieldname] = self._convert(field, submitted.get(fieldname))

        # 3. Validate the fields. Ignore fields which are disabled in
        # conditionals
        # First get list of fields which are still in the form after
        # conditionals has be evaluated
        fields_to_check = self._config.get_fields(values=values,
                                                  reload_fields=True,
                                                  evaluate=True)
        for fieldname, field in fields_all:
            if fieldname not in fields_to_check:
                continue
            rules = field.get_rules()
            for rule in rules:
                if rule.mode == "pre":
                    result = rule.evaluate(submitted)
                else:
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

    def __getattr__(self, name):
        """Make attributes from the configuration directly available"""
        return getattr(self._config, name)

    def _get_sa_mapped_class(self):
        # TODO: Raise Exception if this field is not a relation. (None)
        # <2013-07-25 07:44>
        return self.sa_property.mapper.class_

    def _get_sa_property(self):
        if not self._form._item:
            return None
        mapper = sa.orm.object_mapper(self._form._item)
        for prop in mapper.iterate_properties:
            if prop.key == self.name:
                return prop

    def get_type(self):
        """Returns the datatype of the field."""
        if self._config.type:
            return self._config.type
        if self.sa_property:
            try:
                column = self.sa_property.columns[0]
                dtype = str(column.type)
                if dtype in ["VARCHAR", "TEXT"]:
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
        """Returns a list of configured rules for the field"""
        rules = self.rules
        if self.is_required():
            parser = Parser()
            expr = "bool($%s)" % self.name
            msg = "This field is required. You need to provide a value"
            mode = "pre"
            expr = parser.parse(expr)
            rules.append(Rule(expr, msg, mode))
        return rules

    def get_value(self, default=None, expand=False):
        value = self._form.data.get(self._config.name, default)
        if expand:
            if not isinstance(value, list):
                value = [value]
            ex_values = []
            options = self.get_options()
            for opt in options:
                for v in value:
                    if str(v) == str(opt[1]):
                        ex_values.append("%s" % opt[0])
            return ", ".join(ex_values)
        else:
            return value

    def get_options(self):
        user_defined_options = self._config.options
        if user_defined_options:
            return user_defined_options
        elif self._form._dbsession:
            # Get mapped clazz for the field
            options = []
            if self.get_type() == 'manytoone':
                options.append(("None", ""))
            clazz = self._get_sa_mapped_class()
            items = self._form._dbsession.query(clazz)
            options.extend([(item, item.id) for item in items])
            return options
        else:
            # TODO: Try to get the session from the item. Ther must be
            # somewhere the already bound session. (torsten) <2013-07-23 00:27>
            log.warning('No db connection configured for this form. Can '
                        'not load options')
            return []

    def add_error(self, error):
        self._errors.append(error)

    def get_errors(self):
        return self._errors

    def render(self):
        """Returns the rendererd HTML for the field"""
        return self.renderer.render()

    def is_relation(self):
        return isinstance(self.sa_property,
                          sa.orm.RelationshipProperty)

    def is_required(self):
        """Returns true if either the required flag of the field
        configuration is set or the field is required in the underlying
        datamodel"""
        req = False
        if isinstance(self.sa_property, sa.orm.RelationshipProperty) is False \
           and self.sa_property:
            req = (self.sa_property.columns[0].nullable is False)
        return self.required or req

    def is_readonly(self):
        """Returns true if either the readonly flag of the field
        configuration is set or the whole form is marked as readonly"""
        return self.readonly or False

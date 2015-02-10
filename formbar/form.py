import logging
import re
import datetime
import sqlalchemy as sa
from babel.dates import format_datetime, format_date
from formbar.renderer import FormRenderer, get_renderer
from formbar.helpers import get_local_datetime, get_utc_datetime
from formbar.rules import Rule

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
                 csrf_token=None, eval_url=None, url_prefix="", locale=None):
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
        self.loaded_data = self.serialize(self._get_data_from_item())
        """This is the initial data loaded from the given item. Used to
        render the readonly forms"""
        self.merged_data = {}
        """This is merged date from the initial data loaded from the
        given item. And userprovied data. The data is available after
        rendering the form"""

    def _set_current_field_data(self, data):
        for key in self.fields:
            value = data.get(key)
            if value or isinstance(value, int):
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
            if values.has_key(fieldname):
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
            deserialized[fieldname] = self._to_python(field, data.get(field.name))
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
            #if field and not field.is_readonly():
            #    # Only add the value if the field is not marked as readonly
            #    serialized[fieldname] = self._from_python(field, value)
            serialized[fieldname] = self._from_python(field, value)
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

    def has_errors(self):
        """Returns True if one of the fields in the form has errors"""
        for field in self.fields.values():
            if len(field.get_errors()) > 0:
                return True
        return False

    def has_warnings(self):
        """Returns True if one of the fields in the form has warnings"""
        for field in self.fields.values():
            if len(field.get_warnings()) > 0:
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
            if page is not None and field.name not in fields_on_page: continue
            if len(field.get_warnings()) > 0:
                warnings[field.name] = field.get_warnings()
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

        if self.submitted_data:
            item_values = self.submitted_data
        else:
            item_values = self.loaded_data
        # Merge the items_values with the extra provided values. Extra
        # values will overwrite the item_values.
        values = dict(item_values.items() + values.items())
        self.merged_data = values

        # Set current and previous values of the fields in the form.
        self._set_current_field_data(values)
        self._set_previous_field_data(previous_values)

        # Add csrf_token to the values dictionary
        values['csrf_token'] = self._csrf_token

        renderer = FormRenderer(self, self._translate)
        form = renderer.render(buttons=buttons, outline=outline)
        return form

    def _add_error(self, fieldname, error):
        field = self.get_field(fieldname)
        if isinstance(error, list):
            for err in error:
                field.add_error(err)
        else:
            field.add_error(error)

    def _add_warning(self, fieldname, warning):
        field = self.get_field(fieldname)
        if isinstance(warning, list):
            for war in warning:
                field.add_warning(war)
        else:
            field.add_warning(warning)

    def _to_python(self, field, value):
        """Returns a value of python datatype converted from the
        stringvalue depending of the fields datatype

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
        if dtype in ['string', 'text']:
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
        elif dtype == 'email':
            # TODO: Really check the email. Ask the server mailsserver
            # if the adress is known. (ti) <2014-08-04 16:31>
            if not value:
                return None
            if not re.match(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", value):
                msg = "%s is not valid email address." % value
                self._add_error(field.name, msg)
            else:
                converted = value
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
                if self._locale == "de":
                    d, m, y = value.split('.')
                else:
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
		# Convert datetime to UTC and remove tzinfo because SQLAlchemy
		# fails when trying to store offset-aware datetimes if the date
		# column isn't prepared. As storing dates in UTC is a good idea
		# anyway this is the default.
                converted = get_utc_datetime(converted)
		converted = converted.replace(tzinfo=None)
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

            # In case the there is only one linked item, the value
            # is a string value und not a list. In this case we
            # need to put the value into a list to make the loading
            # and reasinging of items work. Otherwise a item with id
            # 670 will be converted into a list containing 6, 7, 0
            # which will relink different items!
            if not isinstance(value, list):
                value = [value]

            try:
                values = []
                db = self._dbsession
                rel = relation_names[field.name].mapper.class_
                for v in [v for v in value if v != ""]:
                    values.append(db.query(rel).filter(rel.id == int(v)).one())
                converted = values
            except ValueError:
                msg = "Reference value '%s' must be of type integer" % value
                self._add_error(field.name, msg)
        log.debug("Converted value '%s' (%s) of field '%s' (%s)"
                  % (converted, type(converted), field.name, dtype))
        return converted

    def _from_python(self, field, value):
        """@todo: Docstring for _from_python.

        :field: @todo
        :value: @todo
        :returns: @todo

        """
        serialized = ""
        ftype = field.get_type()
        try:
            if value is None:
                serialized = ""
            elif isinstance(value, basestring):
                serialized = value
            elif isinstance(value, list):
                vl = []
                for v in value:
                    try:
                        vl.append(v.id)
                    except AttributeError:
                        vl.append(v)
                serialized = vl
            else:
                try:
                    serialized = value.id
                except AttributeError:
                    if ftype == "time":
                        td = datetime.timedelta(seconds=int(value))
                        d = datetime.datetime(1, 1, 1) + td
                        serialized = "%02d:%02d:%02d" % (d.hour, d.minute, d.second)
                    elif ftype == "datetime":
                        value = get_local_datetime(value)
                        if self._locale == "de":
                            dateformat = "dd.MM.yyyy HH:mm:ss"
                        else:
                            dateformat = "yyyy-MM-dd HH:mm:ss"
                        serialized = format_datetime(value, format=dateformat)
                    elif ftype == "date":
                        if self._locale == "de":
                            dateformat = "dd.MM.yyyy"
                        else:
                            dateformat = "yyyy-MM-dd"
                        serialized = format_date(value, format=dateformat)
                    else:
                        serialized = value
        except AttributeError:
            log.warning('Can not get value for field "%s". '
                        'The field is no attribute of the item' % field.name)
        return serialized

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

        if not submitted:
            unvalidated = self.loaded_data
        else:
            try:
                self.submitted_data = submitted.mixed()
            except AttributeError:
                self.submitted_data = submitted
            unvalidated = self.submitted_data
        converted = self.deserialize(unvalidated)

        # Validate the fields. Ignore fields which are disabled in
        # conditionals First get list of fields which are still in the
        # form after conditionals has be evaluated
        fields_to_check = self._config.get_fields(values=converted,
                                                  reload_fields=True,
                                                  evaluate=True)
        for fieldname, field in fields_to_check.iteritems():
            field = self.fields[fieldname]
            for rule in field.get_rules():
                if rule.mode == "pre":
                    result = rule.evaluate(unvalidated)
                else:
                    result = rule.evaluate(converted)
                if not result:
                    if rule.triggers == "warning":
                        self._add_warning(fieldname, rule.msg)
                    else:
                        self._add_error(fieldname, rule.msg)

        # Custom validation. User defined external validators.
        for validator in self.external_validators:
            if not validator.check(converted):
                self._add_error(validator._field, validator._error)

        # If the form is valid. Save the converted and validated data
        # into the data dictionary.
        has_errors = self.has_errors()
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
        if value and value.startswith("$"):
            # value is a field. Try to get the value of the field.
            try:
                # Special logic for ringo items.
                if (self.renderer.render_type == "info"
                    and hasattr(self._form._item, "get_value")):
                    value = self._form._item.get_value(value.strip("$"),
                                                       expand=True)
                else:
                    value = getattr(self._form._item, value.strip("$"))
            except IndexError, e:
                log.error("Error while accessing attribute '%s': %s" % (value, e))
                value = None
            except AttributeError, e:
                log.error("Error while accessing attribute '%s': %s" % (value, e))
                value = None
        self.value = value

        self.previous_value = None
        """Value as string of the field. Will be set on rendering the
        form"""

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
        """Returns a list of configured rules for the field."""
        return self.rules

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
                return value
            elif default:
                return default
            else:
                return value

    def _build_filter_rule(self, expr_str, item):
        t = expr_str.split(" ")
        for x in t:
            # % marks attributes of the current fields item in case of
            # selections. Is used to iterate over the items in the selection.
            if x.startswith("%"):
                key =  x.strip("%")
                value = getattr(item, key)
            # @ marks the item of the current fields form item.
            elif x.startswith("@"):
                key =  x.strip("@")
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
                    value = self._form.merged_data.get(tokens[0].strip("$"))
                if tmpitem and not value:
                    value = getattr(tmpitem, attribute)
                    if hasattr(value, '__call__'):
                        value = value()
            else:
                value = None

            if value is not None:
                if isinstance(value, list):
                    value = "[%s]" % ",".join("'%s'" % unicode(v) for v in value)
                    expr_str = expr_str.replace(x, value)
                else:
                    expr_str = expr_str.replace(x, "'%s'" % str(value))
        return Rule(expr_str)

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

    def filter_options(self, options):
        filtered_options = []
        for option in options:
            if self._config.renderer and self._config.renderer.filter:
                rule = self._build_filter_rule(
                    self._config.renderer.filter, option)
                if rule.evaluate({}):
                    filtered_options.append((option, option.id, True))
                else:
                    filtered_options.append((option, option.id, False))
            else:
                filtered_options.append((option, option.id, True))
        return filtered_options

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
        if self.get_type() == 'manytoone':
            options.append(("None", "", True))
        user_defined_options = self._config.options
        if isinstance(user_defined_options, list) and len(user_defined_options) > 0:
            for option in user_defined_options:
                # TODO: Filter user defined options too (ti) <2014-02-19 23:46>
                options.append((option[0], option[1], True))
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
        return options

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
        return isinstance(self.sa_property,
                          sa.orm.RelationshipProperty)

    def is_desired(self):
        """Returns true if field is set as desired in field configuration"""
        return self.desired

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

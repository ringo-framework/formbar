"""Converters will convert a given value from string to the python value
and vice versa. Converters which will deserialize a string into python
values are named `to_<datatype>` where datatype is the name of the
python data type name. Convertes which serialize the value from python
value into a string are named `from_<datatype>`."""

import logging
import datetime
import re
import sqlalchemy as sa
from babel.dates import format_datetime, format_date
from formbar.helpers import get_local_datetime, get_utc_datetime


log = logging.getLogger(__name__)


class DeserializeException(Exception):
    """Exception for errors on deserialization."""
    pass


def from_timedelta(value):
    """Will return the serialised value for a given timedelta in
    'HH:MM:SS' format."""
    seconds = value.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    converted = "%02d:%02d:%02d" % (hours, minutes, seconds)
    return converted


def to_timedelta(value):
    """Will return a python timedelta for the given value in
    'HH:MM:SS' format. If the value can not be converted and
    exception is raised."""
    if not value:
        return None
    try:
        h, m, s = value.split(':')
        h = int(h)
        m = int(m)
        s = int(s)
        converted = datetime.timedelta(hours=h,
                                       minutes=m,
                                       seconds=s)
        return converted
    except ValueError:
        msg = "Value '%s' must be in format 'HH:MM:SS'" % value
        raise DeserializeException(msg)
    except OverflowError:
        msg = "Value '%s' is too large'" % value
        raise DeserializeException(msg)


def _split_date(value, locale=None):
    """Will return a tuple integers of YEAR, MONTH, DAY for a given
    date string"""
    #@TODO: Support other dateformats that ISO8601
    if locale == "de":
        d, m, y = value.split('.')
    else:
        y, m, d = value.split('-')
    return int(y), int(m), int(d)


def to_date(value, locale=None):
    """Will return a python date instance for the given value. The format of
    the value depends on the locale setting.

    :value: Datetime as string.
    :locale: Locale setting used to parse the date from the given value.
             Defaults to iso date format (YYYY-mm-DD)
    :returns: Python date instance

    """
    if not value:
        return None
    try:
        y, m, d = _split_date(value, locale)
        return datetime.date(y, m, d)
    except:
        msg = "%s is not a valid date format." % value
        raise DeserializeException(msg)


def _split_time(value):
    """Will return a tuple integers of HOUR, MINUTES, SECONDS for a given
    time string"""
    h, M, s = value.split(':')
    return int(h), int(M), int(s)


def to_datetime(value, locale=None):
    """Will return a python datetime instance for the given value. The
    format of the value depends on the locale setting.

    :value: Datetime as string.
    :locale: Locale setting used to parse the date from the given value.
             Defaults to iso date format (YYYY-mm-DD HH:MM:SS)
    :returns: Python datetime instance

    """
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

        y, m, d = _split_date(date, locale)
        h, M, s = _split_time(time)
        converted = datetime.datetime(y, m, d, h, M, s)
        # Convert datetime to UTC and remove tzinfo because
        # SQLAlchemy fails when trying to store offset-aware
        # datetimes if the date column isn't prepared. As
        # storing dates in UTC is a good idea anyway this is the
        # default.
        converted = get_utc_datetime(converted)
        converted = converted.replace(tzinfo=None)
        return converted
    except:
        msg = "%s is not a valid datetime format." % value
        raise DeserializeException(msg)


def to_manytomany(clazz, id, db):
    if not id:
        return []
    # In case the there is only one linked item, the value
    # is a string value und not a list. In this case we
    # need to put the value into a list to make the loading
    # and reasinging of items work. Otherwise a item with id
    # 670 will be converted into a list containing 6, 7, 0
    # which will relink different items!
    if not isinstance(id, list):
        id = [id]
    try:
        values = []
        for v in [v for v in id if v != ""]:
            values.append(db.query(clazz).filter(clazz.id == int(v)).one())
        return values
    except ValueError:
        msg = "Reference value '%s' must be of type integer" % id
        raise DeserializeException(msg)


def to_onetomany(clazz, id, db):
    return to_manytomany(clazz, id, db)


def to_manytoone(clazz, id, db):
    try:
        if id in ("", None):
            return None
        else:
            return db.query(clazz).filter(clazz.id == int(id)).one()
    except ValueError:
        msg = "Reference value '%s' must be of type integer" % id
        raise DeserializeException(msg)


def to_string(value):
    try:
        # Actually all submitted values are strings.
        return value
    except ValueError:
        msg = "%s is not a string value." % value
        raise DeserializeException(msg)


def to_integer(value):
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        msg = "%s is not a integer value." % value
        raise DeserializeException(msg)


def to_float(value):
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        msg = "%s is not a float value." % value
        raise DeserializeException(msg)


def to_email(value):
    # TODO: Really check the email. Ask the server mailsserver
    # if the adress is known. (ti) <2014-08-04 16:31>
    if not value:
        return ""
    if not re.match(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", value):
        msg = "%s is not valid email address." % value
        raise DeserializeException(msg)
    return value


def to_boolean(value):
    if not value:
        return None
    try:
        return value in ['True', '1', 't']
    except ValueError:
        msg = "%s is not a boolean value." % value
        raise DeserializeException(msg)


def to_file(value):
    try:
        return value.file.read()
    except AttributeError:
        return None
    except ValueError:
        msg = "%s is not a file value." % value
        raise DeserializeException(msg)


def from_python(field, value):
    """Will return the serialised version of the value the given field
    and value.

    :field: :class:`.Field` instance
    :value: Python value
    :returns: Serialized version.

    """
    serialized = ""
    locale = field._form._locale
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
                    serialized = from_timedelta(td)
                elif ftype == "interval":
                    serialized = from_timedelta(value)
                elif ftype == "datetime":
                    value = get_local_datetime(value)
                    if locale == "de":
                        dateformat = "dd.MM.yyyy HH:mm:ss"
                    else:
                        dateformat = "yyyy-MM-dd HH:mm:ss"
                    serialized = format_datetime(value, format=dateformat)
                elif ftype == "date":
                    if locale == "de":
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


def to_python(field, value):
    """Will return a instance of a python value of the value the given
    field and value.

    :field: :class:`.Field` instance
    :value: Serialized version of the value
    :returns: Instance of a python type
    """

    # Remove trailing and leading whitespaces before converting the
    # value
    if isinstance(value, unicode):
        # FIXME: Check why here are other types can unicode? Maybe this
        # is after loading an item from the database which already has
        # converted values? (ti) <2015-04-29 10:53>
        value = value.strip()

    relation_names = {}
    try:
        mapper = sa.orm.object_mapper(field._form._item)
        relation_properties = filter(
            lambda p: isinstance(p,
                                 sa.orm.properties.RelationshipProperty),
            mapper.iterate_properties)
        for prop in relation_properties:
            relation_names[prop.key] = prop
    except sa.orm.exc.UnmappedInstanceError:
        if not field._form._item:
            pass  # The form is not mapped to an item.
        else:
            raise

    dtype = field.get_type()
    if dtype in ['string', 'text']:
        return to_string(value)
    elif dtype == 'integer':
        return to_integer(value)
    elif dtype == 'float':
        return to_float(value)
    elif dtype == 'email':
        return to_email(value)
    elif dtype == 'boolean':
        return to_boolean(value)
    elif dtype == 'file':
        return to_file(value)
    elif dtype == 'date':
        return to_date(value, field._form._locale)
    elif dtype == 'time':
        return to_timedelta(value).total_seconds()
    elif dtype == 'interval':
        return to_timedelta(value)
    elif dtype == 'datetime':
        return to_datetime(value, field._form._locale)
    # Reltation handling
    elif dtype == 'manytoone':
        rel = relation_names[field.name].mapper.class_
        return to_manytoone(rel, value, field._form._dbsession)
    elif dtype == 'onetomany':
        rel = relation_names[field.name].mapper.class_
        return to_onetomany(rel, value, field._form._dbsession)
    elif dtype in 'manytomany':
        rel = relation_names[field.name].mapper.class_
        return to_manytomany(rel, value, field._form._dbsession)

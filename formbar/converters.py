"""Converters will convert a given value from string to the python value
and vice versa. Converters which will deserialize a string into python
values are named `to_<datatype>` where datatype is the name of the
python data type name. Convertes which serialize the value from python
value into a string are named `from_<datatype>`."""

import datetime
import logging
from datetime import timedelta

import re
from babel.dates import format_datetime, format_date
from formbar.helpers import get_local_datetime, get_utc_datetime

log = logging.getLogger(__name__)

# Dummy translation function.
_ = lambda x: x


class DeserializeException(Exception):
    """Exception for errors on deserialization."""

    def __init__(self, msg, value):
        self.value = value
        self.message = msg

    def __str__(self):
        return self.message % self.value


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
    'HH:MM:SS', 'HH:MM' or 'MM' format. 
    If the value can not be converted and
    exception is raised."""
    if not value:
        return None
    try:
        ncolon = value.count(":")
        if ncolon == 2:
            interval = value.split(":")
            hours = int(interval[0])
            minutes = int(interval[1])
            seconds = int(interval[2])
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        elif ncolon == 1:
            interval = value.split(":")
            hours = int(interval[0])
            minutes = int(interval[1])
            return timedelta(hours=hours, minutes=minutes)
        elif ncolon == 0:
            return timedelta(minutes=int(value))
        else:
            msg = _("Value '%s' must be in format 'HH:MM:SS'")
            raise DeserializeException(msg, value)
    except ValueError:
        msg = _("Value '%s' must be in format 'HH:MM:SS'")
        raise DeserializeException(msg, value)
    except OverflowError:
        msg = _("Value '%s' is too large")
        raise DeserializeException(msg, value)


def _split_date(value, locale=None):
    """Will return a tuple integers of YEAR, MONTH, DAY for a given
    date string"""
    # @TODO: Support other dateformats that ISO8601
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
        msg = _("%s is not a valid date format.")
        raise DeserializeException(msg, value)


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
        msg = _("%s is not a valid datetime format.")
        raise DeserializeException(msg, value)


def to_integer_list(value):
    if not value:
        return []
    elif not isinstance(value, list):
        # In case the there is only one linked item, the value
        # is a string value und not a list. In this case we
        # need to put the value into a list to make the loading
        # and reasinging of items work. Otherwise a item with id
        # 670 will be converted into a list containing 6, 7, 0
        # which will relink different items!
        value = [value]
    return map(to_integer, [v for v in value if v not in ("", None)])


def to_manytomany(clazz, ids, db, selected):
    # The selected values must be in a list. So make sure they are a
    # list.
    if not isinstance(selected, list):
        selected = [selected]
    selected_ids = set(map(lambda s: s.id, selected))

    # Determine which items need to be added or removed from the
    # relation.
    ids = set(ids)
    add_ids = ids.difference(selected_ids)
    delete_ids = selected_ids.difference(ids)

    related_items = filter(lambda x: x.id not in delete_ids, selected)
    for id in add_ids:
        related_items.append(db.query(clazz).filter(clazz.id == id).one())
    return related_items


def to_onetomany(clazz, ids, db, selected):
    return to_manytomany(clazz, ids, db, selected)


def to_manytoone(clazz, id, db, selected):
    if not selected or selected.id != id:
        return db.query(clazz).filter(clazz.id == id).one()
    return selected


def to_string(value):
    try:
        # Actually all submitted values are strings.
        return value
    except ValueError:
        msg = _("%s is not a string value.")
        raise DeserializeException(msg, value)


def to_integer(value):
    """Converts a given string value into a 4 byte integer value. If
    the given value is larger the a 4 byte integer a OverflowError is
    raised."""
    if value == "":
        return None
    try:
        value = int(value)
        # Range for value taken from
        # http://www.postgresql.org/docs/9.1/static/datatype-numeric.html
        # for integer type.
        if -2147483648 <= value <= 2147483647:
            return value
        else:
            raise OverflowError
    except ValueError:
        msg = _("%s is not a integer value.")
        raise DeserializeException(msg, value)
    except OverflowError:
        msg = "Value '%s' is too large"
        raise DeserializeException(msg, value)


def to_float(value):
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        msg = _("%s is not a float value.")
        raise DeserializeException(msg, value)


def to_email(value):
    # TODO: Really check the email. Ask the server mailsserver
    # if the adress is known. (ti) <2014-08-04 16:31>
    if not value:
        return ""
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", value):
        msg = _("%s is not valid email address.")
        raise DeserializeException(msg, value)
    return value.lower()


def to_boolean(value):
    if not value:
        return None
    try:
        return value in ['True', '1', 't']
    except ValueError:
        msg = _("%s is not a boolean value.")
        raise DeserializeException(msg, value)


def to_file(value):
    try:
        return value.file.read()
    except AttributeError:
        return None
    except ValueError:
        msg = _("%s is not a file value.")
        raise DeserializeException(msg, value)


def multiselect_to_list(value):
    checkbox_representation = value.strip("{").strip("}").split(",")
    return [unicode(v) for v in checkbox_representation]


def serialize_string(value):
    """
    Handles string values
    a) plain string
    b) multiselect
    :param value: string representation
    :return: serialize
    """
    is_checkbox = re.compile("{.*}").match
    if is_checkbox(value):
        serialized = multiselect_to_list(value)
    else:
        serialized = unicode(value)
    return serialized


def serialize_list(value):
    """
    generates a converted list of value_ids
    :param value:
    :return: serialized list
    """

    def extract_inner_value(inner_value):
        if hasattr(inner_value, "id"):
            return inner_value.id
        return inner_value

    return [extract_inner_value(v) for v in value]


def from_python(field, value):
    """Will return the serialised version of the value the given field
    and value.

    :field: :class:`.Field` instance
    :value: Python value
    :returns: Serialized version.

    """
    locale = field._form._locale
    field_type = field.get_type()
    is_german_locale = locale == "de"
    try:
        serialized = value
        if value is None:
            return u""
        if isinstance(value, basestring):
            serialized = serialize_string(value)
        elif isinstance(value, list):
            serialized = serialize_list(value)
        elif hasattr(value, "id"):
            return value.id
        elif field_type == "time":
            td = datetime.timedelta(seconds=int(value))
            serialized = from_timedelta(td)
        elif field_type == "interval":
            serialized = from_timedelta(value)
        elif field_type == "datetime":
            value = get_local_datetime(value)
            if is_german_locale:
                dateformat = "dd.MM.yyyy HH:mm:ss"
            else:
                dateformat = "yyyy-MM-dd HH:mm:ss"
            serialized = format_datetime(value, format=dateformat)
        elif field_type == "date":
            if is_german_locale:
                dateformat = "dd.MM.yyyy"
            else:
                dateformat = "yyyy-MM-dd"
            serialized = format_date(value, format=dateformat)
    except AttributeError:
        log.warning('Can not get value for field "%s". '
                    'The field is no attribute of the item' % field.name)
        serialized = u""
    return serialized


def to_python(field, value, relation_names):
    """Will return a instance of a python value of the value the given
    field and value.

    :field: :class:`.Field` instance
    :value: Serialized version of the value
    :returns: Instance of a python type
    """

    dtype = field.get_type()
    if isinstance(value, list) and dtype not in ['manytomany',
                                                 'manytoone',
                                                 'onetomany']:
        # Special handling for multiple values (multiselect in
        # checkboxes eg.)
        tmp_list = []
        for v in value:
            tmp_list.append(to_python(field, v, relation_names))
        return tmp_list
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
        if value in ("", None):
            return None
        value = to_integer(value)
        db = field._form._dbsession
        selected = getattr(field._form._item, field.name)
        return to_manytoone(rel, value, db, selected)
    elif dtype == 'onetomany':
        rel = relation_names[field.name].mapper.class_
        value = to_integer_list(value)
        if not value:
            return value
        db = field._form._dbsession
        selected = getattr(field._form._item, field.name)
        return to_onetomany(rel, value, db, selected)
    elif dtype in 'manytomany':
        rel = relation_names[field.name].mapper.class_
        value = to_integer_list(value)
        if not value:
            return value
        db = field._form._dbsession
        selected = getattr(field._form._item, field.name)
        return to_manytomany(rel, value, db, selected)

"""Converters will convert a given value from string to the python value
and vice versa. Converters which will deserialize a string into python
values are named `to_<datatype>` where datatype is the name of the
python data type name. Convertes which serialize the value from python
value into a string are named `from_<datatype>`."""

import datetime
from formbar.helpers import get_utc_datetime


def from_timedelta(value):
    """Will return the serialised value for a given timedelta in
    'HH:MM:SS' format."""
    d = datetime.datetime(1, 1, 1) + value
    converted = "%02d:%02d:%02d" % (d.hour,
                                    d.minute, d.second)
    return converted


def to_timedelta(value):
    """Will return a python timedelta for the given value in
    'HH:MM:SS' format. If the value can not be converted and
    exception is raised."""
    if not value:
        return None
    h, m, s = value.split(':')
    h = int(h)
    m = int(m)
    s = int(s)
    converted = datetime.timedelta(hours=h,
                                   minutes=m,
                                   seconds=s)
    return converted


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
    y, m, d = _split_date(value, locale)
    return datetime.date(y, m, d)


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

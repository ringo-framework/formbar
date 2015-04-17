"""Converters will convert a given value from string to the python value
and vice versa. Converters which will deserialize a string into python
values are named `to_<datatype>` where datatype is the name of the
python data type name. Convertes which serialize the value from python
value into a string are named `from_<datatype>`."""

import datetime


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

import os
from dateutil import tz
from formbar import static_dir

def get_css_files():
    files = ['css/datepicker3.css', 'css/formbar.css']
    css = []
    values = {}
    for filename in files:
        filepath = os.path.join(static_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        css.append((filename, content))
    return css

def get_js_files():
    files = ['js/bootstrap-datepicker.js',
             'js/locales/bootstrap-datepicker.de.js',
             'js/formbar.js', 'js/ace/ace.js',
             'js/ace/ext-language_tools.js', 'js/ace/mode-xml.js',
             'js/ace/snippets/xml.js', 'js/ace/snippets/text.js']
    js = []
    for filename in files:
        filepath = os.path.join(static_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        js.append((filename, content))
    return js

def get_css():
    """Returns the content of the formbar CSS file
    :returns: String with css
    """
    out = []
    for filename, content in get_css_files():
        out.append(content)
    return "".join(out)

def get_js():
    """Returns the content of the formbar JS file
    :returns: String with js
    """
    out = []
    for filename, content in get_js_files():
        out.append(content)
    return "".join(out)


def get_local_datetime(dt, timezone=None):
    """Will return a datetime converted into to given timezone. If the
    given datetime is naiv and does not support timezone information
    then UTC timezone is assumed. If timezone is None, then the local
    timezone of the server will be used.

    :dt: datetime
    :timezone: String timezone (eg. Europe/Berin)
    :returns: datetime

    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=tz.gettz('UTC'))
    if not timezone:
        timezone = tz.tzlocal()
    return dt.astimezone(timezone)


def get_utc_datetime(dt, timezone=None):
    """Will return a datetime converted into to given timezone. If the
    given datetime is naiv and does not support timezone information
    then UTC timezone is assumed. If timezone is None, then the local
    timezone of the server will be used.

    :dt: datetime
    :timezone: String timezone (eg. Europe/Berin)
    :returns: datetime

    """
    if not timezone:
        dt = dt.replace(tzinfo=tz.tzlocal())
    timezone = tz.gettz('UTC')
    return dt.astimezone(timezone)

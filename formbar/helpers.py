import os
from mako.lookup import TemplateLookup
from formbar import static_dir

template_lookup = TemplateLookup(directories=[static_dir])


def get_css():
    """Returns the content of the formbar CSS file
    :returns: String with css
    """
    files = ['datepicker3.css', 'formbar.css']
    css = []
    values = {}
    for filename in files:
        template = template_lookup.get_template(filename)
        css.append(template.render(**values))
    return "".join(css)


def get_js():
    """Returns the content of the formbar JS file
    :returns: String with js
    """
    files = ['bootstrap-datepicker.js', 'formbar.js']
    js = []
    values = {}
    for filename in files:
        template = template_lookup.get_template(filename)
        js.append(template.render(**values))
    return "".join(js)

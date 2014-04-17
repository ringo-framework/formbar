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


def get_js(eval_url="undefined"):
    """Returns the content of the formbar JS file

    :eval_url: External URL for rule evaluation. If defined this URL is
    called to evaluate client side rules with a AJAX request. The rule
    to evaluate is provided in a GET request in the "rule" paramenter.
    The return Value is a JSON response with success attribute set
    depending on the result of the evaluation and the error message in
    the data attribute in case the evaluation fails.
    :returns: String with js

    """
    files = ['bootstrap-datepicker.js', 'formbar.js']
    js = []
    values = {'eval_url': eval_url}
    for filename in files:
        template = template_lookup.get_template(filename)
        js.append(template.render(**values))
    return "".join(js)
